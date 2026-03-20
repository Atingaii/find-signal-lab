from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from common.db import read_sql
from evaluation.backtest import simulate_top_k_strategy
from evaluation.metrics import classification_metrics, grouped_return_spread, rank_ic, safe_round, top_k_hit_rate
from models.config import TARGET_CONFIGS
from models.logistic_model import LogisticBaselineModel
from models.naive_model import NaiveSignalModel
from models.rule_baseline import RuleBaselineModel
from prediction.predict import build_prediction_output


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate stage-four baseline models.")
    parser.add_argument(
        "--db-path",
        default=str(ROOT / "data" / "sqlite" / "fund_data.db"),
        help="SQLite database path.",
    )
    parser.add_argument(
        "--targets",
        nargs="*",
        default=["future_5d_up", "future_20d_relative_strength"],
        help="Targets to evaluate.",
    )
    args = parser.parse_args()

    dataset = read_sql("SELECT * FROM dataset_training_samples", args.db_path)
    dataset["trade_date"] = pd.to_datetime(dataset["trade_date"])
    report_dir = ROOT / "reports" / "modeling"
    report_dir.mkdir(parents=True, exist_ok=True)

    all_results: list[dict[str, object]] = []
    markdown_lines = ["# 第四阶段评估报告", ""]

    for target_name in args.targets:
        config = TARGET_CONFIGS[target_name]
        label_column = config["label_column"]
        return_column = config["actual_return_column"]
        feature_columns = list(config["feature_columns"])
        train_df = dataset.loc[dataset["dataset_split"] == "train"].dropna(
            subset=feature_columns + [label_column, return_column]
        )
        valid_df = dataset.loc[dataset["dataset_split"] == "valid"].dropna(
            subset=feature_columns + [label_column, return_column]
        )
        test_df = dataset.loc[dataset["dataset_split"] == "test"].dropna(
            subset=feature_columns + [label_column, return_column]
        )

        model_builders = {
            "naive_signal": _build_naive_model(target_name, train_df),
            "rule_baseline": RuleBaselineModel(target_name=target_name).fit(train_df),
            "logistic_regression": LogisticBaselineModel(target_name=target_name).fit(train_df, label_column),
        }

        markdown_lines.extend([f"## {target_name}", ""])

        for model_name, model in model_builders.items():
            split_results: dict[str, dict[str, object]] = {}
            markdown_lines.extend([f"### {model_name}", ""])
            for split_name, split_df in [("valid", valid_df), ("test", test_df)]:
                predicted = model.predict(split_df)
                predicted = build_prediction_output(predicted, target_name)
                metrics = classification_metrics(
                    predicted[label_column].astype(float),
                    predicted["prediction_probability"].astype(float),
                )
                metrics["top_k_hit_rate"] = top_k_hit_rate(
                    predicted,
                    probability_column="prediction_probability",
                    label_column=label_column,
                    k=config["top_k"],
                )
                metrics["rank_ic"] = rank_ic(
                    predicted,
                    score_column="rank_score",
                    actual_return_column=return_column,
                )
                metrics["grouped_return_spread"] = grouped_return_spread(
                    predicted,
                    score_column="rank_score",
                    actual_return_column=return_column,
                    k=config["top_k"],
                )

                backtest_history, backtest_summary = simulate_top_k_strategy(
                    predicted,
                    score_column="rank_score",
                    actual_return_column=return_column,
                    k=config["top_k"],
                )

                failure_samples = _failure_samples(predicted, label_column)
                boundary_samples = _boundary_samples(predicted)
                family_slice = _slice_by_family(
                    predicted,
                    label_column=label_column,
                    return_column=return_column,
                    top_k=config["top_k"],
                )

                predicted.to_csv(
                    report_dir / f"{model_name}_{target_name}_{split_name}_predictions.csv",
                    index=False,
                    encoding="utf-8-sig",
                )
                backtest_history.to_csv(
                    report_dir / f"{model_name}_{target_name}_{split_name}_backtest.csv",
                    index=False,
                    encoding="utf-8-sig",
                )
                failure_samples.to_csv(
                    report_dir / f"{model_name}_{target_name}_{split_name}_failures.csv",
                    index=False,
                    encoding="utf-8-sig",
                )
                boundary_samples.to_csv(
                    report_dir / f"{model_name}_{target_name}_{split_name}_boundary.csv",
                    index=False,
                    encoding="utf-8-sig",
                )
                pd.DataFrame.from_dict(family_slice, orient="index").reset_index().rename(
                    columns={"index": "benchmark_family"}
                ).to_csv(
                    report_dir / f"{model_name}_{target_name}_{split_name}_by_family.csv",
                    index=False,
                    encoding="utf-8-sig",
                )

                split_results[split_name] = {
                    "classification": safe_round(metrics),
                    "backtest": safe_round(backtest_summary),
                    "rows": int(len(predicted)),
                    "failure_samples": int(len(failure_samples)),
                    "boundary_samples": int(len(boundary_samples)),
                    "by_family": family_slice,
                }

                rounded = safe_round(metrics)
                markdown_lines.append(
                    f"- {split_name}: accuracy={rounded['accuracy']}, "
                    f"f1={rounded['f1']}, auc={rounded['auc']}, "
                    f"top_k_hit_rate={rounded['top_k_hit_rate']}, "
                    f"rank_ic={rounded['rank_ic']}, "
                    f"spread={rounded['grouped_return_spread']}"
                )

            if isinstance(model, LogisticBaselineModel):
                model.coefficient_frame().to_csv(
                    report_dir / f"{model_name}_{target_name}_coefficients.csv",
                    index=False,
                    encoding="utf-8-sig",
                )

            model_result = {
                "target_name": target_name,
                "model_name": model_name,
                "results": split_results,
            }
            all_results.append(model_result)
            markdown_lines.append("")

    (report_dir / "evaluation_summary.json").write_text(
        json.dumps(all_results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (report_dir / "evaluation_report.md").write_text("\n".join(markdown_lines), encoding="utf-8")
    print(json.dumps(all_results, ensure_ascii=False, indent=2))


def _failure_samples(predicted: pd.DataFrame, label_column: str, limit: int = 20) -> pd.DataFrame:
    failures = predicted.loc[predicted["prediction_label"] != predicted[label_column].astype(int)].copy()
    failures["confidence_gap"] = (failures["prediction_probability"] - 0.5).abs()
    return failures.sort_values("confidence_gap", ascending=False).head(limit)


def _boundary_samples(predicted: pd.DataFrame, limit: int = 20) -> pd.DataFrame:
    boundary = predicted.copy()
    boundary["boundary_gap"] = (boundary["prediction_probability"] - 0.5).abs()
    return boundary.sort_values("boundary_gap", ascending=True).head(limit)


def _build_naive_model(target_name: str, train_df: pd.DataFrame) -> NaiveSignalModel:
    signal_map = {
        "future_5d_up": "return_5d",
        "future_20d_relative_strength": "excess_return_20d",
    }
    return NaiveSignalModel(target_name=target_name, signal_column=signal_map[target_name]).fit(train_df)


def _slice_by_family(
    predicted: pd.DataFrame,
    label_column: str,
    return_column: str,
    top_k: int,
) -> dict[str, dict[str, float | int | None]]:
    result: dict[str, dict[str, float | int | None]] = {}
    for benchmark_family, family_df in predicted.groupby("benchmark_family", sort=True):
        metrics = classification_metrics(
            family_df[label_column].astype(float),
            family_df["prediction_probability"].astype(float),
        )
        family_top_k = max(1, min(top_k, int(family_df["fund_code"].nunique())))
        metrics["top_k_hit_rate"] = top_k_hit_rate(
            family_df,
            probability_column="prediction_probability",
            label_column=label_column,
            k=family_top_k,
        )
        metrics["rank_ic"] = rank_ic(
            family_df,
            score_column="rank_score",
            actual_return_column=return_column,
        )
        metrics["grouped_return_spread"] = grouped_return_spread(
            family_df,
            score_column="rank_score",
            actual_return_column=return_column,
            k=family_top_k,
        )
        result[str(benchmark_family)] = {
            "rows": int(len(family_df)),
            **safe_round(metrics),
        }
    return result


if __name__ == "__main__":
    main()
