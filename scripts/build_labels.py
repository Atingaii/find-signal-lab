from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from common.db import read_sql, replace_table
from features.price_features import build_reference_frame
from labels.future_returns import build_future_return_labels


def main() -> None:
    parser = argparse.ArgumentParser(description="Build stage-three label table.")
    parser.add_argument(
        "--db-path",
        default=str(ROOT / "data" / "sqlite" / "fund_data.db"),
        help="SQLite database path.",
    )
    args = parser.parse_args()

    db_path = Path(args.db_path)
    dim_fund = read_sql("SELECT * FROM dim_fund", db_path)
    market_daily = read_sql("SELECT * FROM fact_fund_market_daily", db_path)
    nav_daily = read_sql("SELECT * FROM fact_fund_nav_daily", db_path)

    reference_df = build_reference_frame(dim_fund, market_daily, nav_daily)
    label_df = build_future_return_labels(reference_df)
    label_df["trade_date"] = pd.to_datetime(label_df["trade_date"])
    for column in ["future_date_1d", "future_date_5d", "future_date_20d"]:
        label_df[column] = pd.to_datetime(label_df[column])
    label_df["created_at"] = datetime.now(UTC).isoformat().replace("+00:00", "Z")

    replace_table("label_fund_daily", label_df, db_path)

    output_dir = ROOT / "data" / "processed" / "labels"
    output_dir.mkdir(parents=True, exist_ok=True)
    label_df.to_csv(output_dir / "label_fund_daily.csv", index=False, encoding="utf-8-sig")

    summary = {
        "rows": int(len(label_df)),
        "funds": int(label_df["fund_code"].nunique()),
        "primary_target_rows": int(label_df["is_primary_target"].sum()),
        "label_ready_1d": int(label_df["future_1d_up"].notna().sum()),
        "label_ready_5d": int(label_df["future_5d_up"].notna().sum()),
        "label_ready_20d": int(label_df["future_20d_up"].notna().sum()),
    }
    (output_dir / "label_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
