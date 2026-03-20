from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path


def query_scalar(conn: sqlite3.Connection, sql: str) -> int:
    return int(conn.execute(sql).fetchone()[0])


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate stage-two SQLite data readiness.")
    parser.add_argument(
        "--db-path",
        default="data/sqlite/fund_data.db",
        help="SQLite database path.",
    )
    args = parser.parse_args()

    db_path = Path(args.db_path)
    with sqlite3.connect(db_path) as conn:
        summary = {
            "universe_count": query_scalar(conn, "SELECT COUNT(*) FROM dim_fund"),
            "etf_history_rows": query_scalar(conn, "SELECT COUNT(*) FROM fact_fund_market_daily"),
            "nav_history_rows": query_scalar(conn, "SELECT COUNT(*) FROM fact_fund_nav_daily"),
            "macro_rows": query_scalar(conn, "SELECT COUNT(*) FROM fact_macro_observation"),
            "listed_funds": query_scalar(conn, "SELECT COUNT(*) FROM dim_fund WHERE is_listed = 1"),
            "open_nav_funds": query_scalar(
                conn,
                "SELECT COUNT(DISTINCT fund_code) FROM fact_fund_nav_daily",
            ),
        }

    checks = {
        "universe_count_ge_20": summary["universe_count"] >= 20,
        "etf_history_rows_gt_0": summary["etf_history_rows"] > 0,
        "nav_history_rows_gt_0": summary["nav_history_rows"] > 0,
        "macro_rows_gt_0": summary["macro_rows"] > 0,
    }

    output = {"summary": summary, "checks": checks}
    print(json.dumps(output, ensure_ascii=False, indent=2))
    raise SystemExit(0 if all(checks.values()) else 1)


if __name__ == "__main__":
    main()
