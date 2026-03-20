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
from datasets.build_training_dataset import assemble_training_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Export stage-three training dataset.")
    parser.add_argument(
        "--db-path",
        default=str(ROOT / "data" / "sqlite" / "fund_data.db"),
        help="SQLite database path.",
    )
    args = parser.parse_args()

    db_path = Path(args.db_path)
    feature_df = read_sql("SELECT * FROM feature_fund_daily", db_path)
    label_df = read_sql("SELECT * FROM label_fund_daily", db_path)
    feature_df["trade_date"] = pd.to_datetime(feature_df["trade_date"])
    label_df["trade_date"] = pd.to_datetime(label_df["trade_date"])

    dataset_df, summary = assemble_training_dataset(feature_df, label_df)
    replace_table("dataset_training_samples", dataset_df, db_path)

    output_dir = ROOT / "data" / "processed" / "datasets"
    output_dir.mkdir(parents=True, exist_ok=True)
    dataset_df.to_csv(output_dir / "training_dataset_v1.csv", index=False, encoding="utf-8-sig")
    for split_name in ("train", "valid", "test"):
        dataset_df.loc[dataset_df["dataset_split"] == split_name].to_csv(
            output_dir / f"training_dataset_v1_{split_name}.csv",
            index=False,
            encoding="utf-8-sig",
        )

    (output_dir / "training_dataset_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
