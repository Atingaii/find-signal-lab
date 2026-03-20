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

from common.db import read_sql, replace_table
from models.config import TARGET_CONFIGS
from models.logistic_model import LogisticBaselineModel
from models.rule_baseline import RuleBaselineModel
from prediction.predict import build_prediction_output, latest_prediction_snapshot


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate latest prediction snapshots.")
    parser.add_argument(
        "--db-path",
        default=str(ROOT / "data" / "sqlite" / "fund_data.db"),
        help="SQLite database path.",
    )
    parser.add_argument(
        "--targets",
        nargs="*",
        default=["future_5d_up", "future_20d_relative_strength"],
        help="Targets to score.",
    )
    args = parser.parse_args()

    feature_df = read_sql("SELECT * FROM feature_fund_daily WHERE is_primary_target = 1", args.db_path)
    feature_df["trade_date"] = pd.to_datetime(feature_df["trade_date"])

    model_dir = ROOT / "data" / "processed" / "models"
    output_dir = ROOT / "data" / "processed" / "predictions"
    output_dir.mkdir(parents=True, exist_ok=True)

    latest_frames: list[pd.DataFrame] = []
    summary: list[dict[str, object]] = []

    for target_name in args.targets:
        config = TARGET_CONFIGS[target_name]
        latest_candidates = feature_df.dropna(subset=config["feature_columns"]).copy()

        rule_model = RuleBaselineModel.load(model_dir / f"{target_name}_rule_baseline.json")
        logistic_model = LogisticBaselineModel.load(model_dir / f"{target_name}_logistic.joblib")

        for model_name, model in [
            ("rule_baseline", rule_model),
            ("logistic_regression", logistic_model),
        ]:
            predicted = model.predict(latest_candidates)
            snapshot = latest_prediction_snapshot(predicted, target_name)
            snapshot = build_prediction_output(snapshot, target_name)
            latest_frames.append(snapshot)

            snapshot.to_csv(
                output_dir / f"{model_name}_{target_name}_latest.csv",
                index=False,
                encoding="utf-8-sig",
            )
            (output_dir / f"{model_name}_{target_name}_latest.json").write_text(
                snapshot.to_json(force_ascii=False, orient="records", indent=2),
                encoding="utf-8",
            )

            summary.append(
                {
                    "target_name": target_name,
                    "model_name": model_name,
                    "prediction_date": snapshot["prediction_date"].iloc[0] if not snapshot.empty else None,
                    "rows": int(len(snapshot)),
                    "top_fund_code": snapshot["fund_code"].iloc[0] if not snapshot.empty else None,
                }
            )

    combined = pd.concat(latest_frames, ignore_index=True) if latest_frames else pd.DataFrame()
    if not combined.empty:
        replace_table("prediction_snapshot_latest", combined, args.db_path)
        explanation_input = combined[
            [
                "fund_code",
                "fund_name",
                "benchmark_family",
                "prediction_date",
                "target_name",
                "prediction_label",
                "prediction_probability",
                "confidence_level",
                "top_feature_contributors",
                "feature_snapshot",
                "risk_snapshot",
                "explanation_input_payload",
                "model_name",
                "model_version",
            ]
        ].copy()
        replace_table("prediction_explanation_input_latest", explanation_input, args.db_path)
        explanation_input.to_csv(
            output_dir / "prediction_explanation_input_latest.csv",
            index=False,
            encoding="utf-8-sig",
        )
        (output_dir / "prediction_explanation_input_latest.json").write_text(
            explanation_input.to_json(force_ascii=False, orient="records", indent=2),
            encoding="utf-8",
        )

    (output_dir / "prediction_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
