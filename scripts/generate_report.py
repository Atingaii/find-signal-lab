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
from reports.daily_report import render_markdown
from reports.summary_builder import DEFAULT_REPORT_MODEL, build_daily_summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate markdown daily report from explanation results.")
    parser.add_argument(
        "--db-path",
        default=str(ROOT / "data" / "sqlite" / "fund_data.db"),
        help="SQLite database path.",
    )
    parser.add_argument(
        "--source-table",
        default="explanation_result_latest",
        help="Stage five explanation result table.",
    )
    parser.add_argument(
        "--model-name",
        default=DEFAULT_REPORT_MODEL,
        help="Preferred model surface for daily report.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of bullish and bearish funds shown per target.",
    )
    args = parser.parse_args()

    report_dir = ROOT / "reports" / "daily"
    report_dir.mkdir(parents=True, exist_ok=True)
    output_dir = ROOT / "data" / "processed" / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    explanation_df = read_sql(f"SELECT * FROM {args.source_table}", args.db_path)
    summary = build_daily_summary(explanation_df, model_name=args.model_name, top_k=args.top_k)
    markdown = render_markdown(summary)
    report_date = str(summary["report_date"])

    latest_report_path = report_dir / "daily_report_latest.md"
    dated_report_path = report_dir / f"daily_report_{report_date.replace('-', '')}.md"
    latest_report_path.write_text(markdown, encoding="utf-8")
    dated_report_path.write_text(markdown, encoding="utf-8")

    summary_payload = {
        key: value
        for key, value in summary.items()
        if key not in {"top_pick_rows", "family_rows", "risk_rows"}
    }
    (output_dir / "daily_report_summary_latest.json").write_text(
        json.dumps(summary_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    top_pick_rows = pd.DataFrame(summary["top_pick_rows"])
    if not top_pick_rows.empty:
        top_pick_rows["report_date"] = report_date
        replace_table("report_top_picks_latest", top_pick_rows, args.db_path)
        top_pick_rows.to_csv(
            output_dir / "report_top_picks_latest.csv",
            index=False,
            encoding="utf-8-sig",
        )

    family_rows = pd.DataFrame(summary["family_rows"])
    if not family_rows.empty:
        family_rows["report_date"] = report_date
        replace_table("report_family_summary_latest", family_rows, args.db_path)
        family_rows.to_csv(
            output_dir / "report_family_summary_latest.csv",
            index=False,
            encoding="utf-8-sig",
        )

    risk_rows = pd.DataFrame(summary["risk_rows"])
    if not risk_rows.empty:
        risk_rows["report_date"] = report_date
        replace_table("report_risk_digest_latest", risk_rows, args.db_path)
        risk_rows.to_csv(
            output_dir / "report_risk_digest_latest.csv",
            index=False,
            encoding="utf-8-sig",
        )

    report_frame = pd.DataFrame(
        [
            {
                "report_date": report_date,
                "model_name": args.model_name,
                "source_table": args.source_table,
                "report_path": str(latest_report_path.relative_to(ROOT)),
                "markdown_text": markdown,
                "summary_payload": json.dumps(summary_payload, ensure_ascii=False),
            }
        ]
    )
    replace_table("report_daily_latest", report_frame, args.db_path)

    print(
        json.dumps(
            {
                "report_date": report_date,
                "model_name": args.model_name,
                "targets": [item["target_name"] for item in summary["targets"]],
                "report_path": str(latest_report_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
