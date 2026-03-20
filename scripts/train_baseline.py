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
from models.config import TARGET_CONFIGS
from models.logistic_model import LogisticBaselineModel
from models.rule_baseline import RuleBaselineModel


def main() -> None:
    parser = argparse.ArgumentParser(description="Train stage-four baseline models.")
    parser.add_argument(
        "--db-path",
        default=str(ROOT / "data" / "sqlite" / "fund_data.db"),
        help="SQLite database path.",
    )
    parser.add_argument(
        "--targets",
        nargs="*",
        default=["future_5d_up", "future_20d_relative_strength"],
        help="Targets to train.",
    )
    parser.add_argument(
        "--fit-scope",
        choices=["train", "train_valid"],
        default="train_valid",
        help="Rows used for final model artifacts.",
    )
    args = parser.parse_args()

    dataset = read_sql("SELECT * FROM dataset_training_samples", args.db_path)
    training_splits = ["train"] if args.fit_scope == "train" else ["train", "valid"]
    fit_df = dataset.loc[dataset["dataset_split"].isin(training_splits)].copy()

    artifact_dir = ROOT / "data" / "processed" / "models"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    summary: list[dict[str, object]] = []

    for target_name in args.targets:
        config = TARGET_CONFIGS[target_name]
        label_column = config["label_column"]
        model_df = fit_df.dropna(subset=config["feature_columns"] + [label_column]).copy()

        rule_model = RuleBaselineModel(target_name=target_name).fit(model_df)
        rule_model.save(artifact_dir / f"{target_name}_rule_baseline.json")

        logistic_model = LogisticBaselineModel(target_name=target_name).fit(model_df, label_column)
        logistic_model.save(artifact_dir / f"{target_name}_logistic.joblib")
        logistic_model.coefficient_frame().to_csv(
            artifact_dir / f"{target_name}_logistic_coefficients.csv",
            index=False,
            encoding="utf-8-sig",
        )

        summary.append(
            {
                "target_name": target_name,
                "fit_scope": args.fit_scope,
                "rows": int(len(model_df)),
                "funds": int(model_df["fund_code"].nunique()),
                "feature_count": len(config["feature_columns"]),
                "label_positive_rate": float(model_df[label_column].astype(float).mean()),
                "rule_model_path": str(artifact_dir / f"{target_name}_rule_baseline.json"),
                "logistic_model_path": str(artifact_dir / f"{target_name}_logistic.joblib"),
            }
        )

    (artifact_dir / "training_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
