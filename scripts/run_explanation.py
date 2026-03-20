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
from explain.reason_engine import build_explanations


def main() -> None:
    parser = argparse.ArgumentParser(description="Build deterministic explanations from prediction snapshots.")
    parser.add_argument(
        "--db-path",
        default=str(ROOT / "data" / "sqlite" / "fund_data.db"),
        help="SQLite database path.",
    )
    parser.add_argument(
        "--source-table",
        default="prediction_explanation_input_latest",
        help="Source table produced by stage four.",
    )
    args = parser.parse_args()

    output_dir = ROOT / "data" / "processed" / "explanations"
    output_dir.mkdir(parents=True, exist_ok=True)

    source_df = read_sql(f"SELECT * FROM {args.source_table}", args.db_path)
    explanation_df = build_explanations(source_df)
    replace_table("explanation_result_latest", explanation_df, args.db_path)

    explanation_df.to_csv(
        output_dir / "explanation_result_latest.csv",
        index=False,
        encoding="utf-8-sig",
    )
    (output_dir / "explanation_result_latest.json").write_text(
        explanation_df.to_json(force_ascii=False, orient="records", indent=2),
        encoding="utf-8",
    )

    summary = (
        explanation_df.groupby(["target_name", "model_name"], as_index=False)
        .agg(
            rows=("fund_code", "count"),
            bullish=("direction_conclusion", lambda s: int((s == "偏多").sum())),
            bearish=("direction_conclusion", lambda s: int((s == "偏空").sum())),
            neutral=("direction_conclusion", lambda s: int((s == "中性").sum())),
        )
        .sort_values(["target_name", "model_name"])
    )
    replace_table("explanation_summary_latest", summary, args.db_path)
    summary.to_csv(
        output_dir / "explanation_summary_latest.csv",
        index=False,
        encoding="utf-8-sig",
    )
    (output_dir / "explanation_summary_latest.json").write_text(
        summary.to_json(force_ascii=False, orient="records", indent=2),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "source_rows": int(len(source_df)),
                "explanation_rows": int(len(explanation_df)),
                "targets": sorted(explanation_df["target_name"].unique().tolist()),
                "models": sorted(explanation_df["model_name"].unique().tolist()),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
