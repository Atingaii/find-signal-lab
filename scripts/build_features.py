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
from features.fund_features import build_fund_features
from features.macro_features import build_macro_features
from features.price_features import build_price_features, build_reference_frame
from features.style_features import build_style_features


def main() -> None:
    parser = argparse.ArgumentParser(description="Build stage-three feature table.")
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
    macro_df = read_sql("SELECT * FROM fact_macro_observation", db_path)

    reference_df = build_reference_frame(dim_fund, market_daily, nav_daily)
    feature_df = build_price_features(reference_df)
    feature_df = build_fund_features(feature_df)
    feature_df = build_style_features(feature_df)
    feature_df = build_macro_features(feature_df, macro_df)
    feature_df["trade_date"] = pd.to_datetime(feature_df["trade_date"])
    feature_df["created_at"] = datetime.now(UTC).isoformat().replace("+00:00", "Z")

    replace_table("feature_fund_reference_daily", reference_df, db_path)
    replace_table("feature_fund_daily", feature_df, db_path)

    output_dir = ROOT / "data" / "processed" / "features"
    output_dir.mkdir(parents=True, exist_ok=True)
    reference_df.to_csv(output_dir / "feature_fund_reference_daily.csv", index=False, encoding="utf-8-sig")
    feature_df.to_csv(output_dir / "feature_fund_daily.csv", index=False, encoding="utf-8-sig")

    summary = {
        "rows": int(len(feature_df)),
        "funds": int(feature_df["fund_code"].nunique()),
        "primary_targets": int(feature_df.loc[feature_df["is_primary_target"] == 1, "fund_code"].nunique()),
        "date_range": [
            feature_df["trade_date"].min().date().isoformat() if not feature_df.empty else None,
            feature_df["trade_date"].max().date().isoformat() if not feature_df.empty else None,
        ],
        "feature_ready_rows": int(
            feature_df[
                [
                    "return_20d",
                    "volatility_20d",
                    "max_drawdown_20d",
                    "style_strength_20d",
                ]
            ]
            .notna()
            .all(axis=1)
            .sum()
        ),
    }
    (output_dir / "feature_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
