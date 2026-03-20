from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS raw_fund_master_snapshot (
    snapshot_at TEXT NOT NULL,
    source TEXT NOT NULL,
    fund_code TEXT NOT NULL,
    fund_name TEXT,
    fund_type TEXT,
    raw_payload TEXT NOT NULL,
    PRIMARY KEY (snapshot_at, source, fund_code)
);

CREATE TABLE IF NOT EXISTS raw_fund_quote_snapshot (
    snapshot_at TEXT NOT NULL,
    source TEXT NOT NULL,
    market_type TEXT NOT NULL,
    fund_code TEXT NOT NULL,
    fund_name TEXT,
    nav_unit REAL,
    nav_accumulated REAL,
    previous_unit_nav REAL,
    previous_accumulated_nav REAL,
    growth_value REAL,
    growth_rate REAL,
    latest_trade_date TEXT,
    purchase_status TEXT,
    redemption_status TEXT,
    raw_payload TEXT NOT NULL,
    PRIMARY KEY (snapshot_at, source, market_type, fund_code)
);

CREATE TABLE IF NOT EXISTS raw_index_fund_snapshot (
    snapshot_at TEXT NOT NULL,
    source TEXT NOT NULL,
    fund_code TEXT NOT NULL,
    fund_name TEXT,
    unit_nav REAL,
    nav_date TEXT,
    growth_rate REAL,
    tracking_mode TEXT,
    benchmark_scope TEXT,
    raw_payload TEXT NOT NULL,
    PRIMARY KEY (snapshot_at, source, fund_code)
);

CREATE TABLE IF NOT EXISTS raw_etf_history (
    source TEXT NOT NULL,
    fund_code TEXT NOT NULL,
    trade_date TEXT NOT NULL,
    open REAL,
    close REAL,
    high REAL,
    low REAL,
    volume REAL,
    amount REAL,
    amplitude REAL,
    pct_chg REAL,
    chg REAL,
    turnover REAL,
    raw_payload TEXT NOT NULL,
    ingested_at TEXT NOT NULL,
    PRIMARY KEY (source, fund_code, trade_date)
);

CREATE TABLE IF NOT EXISTS raw_fund_nav (
    source TEXT NOT NULL,
    fund_code TEXT NOT NULL,
    nav_date TEXT NOT NULL,
    unit_nav REAL,
    accum_nav REAL,
    daily_growth_rate REAL,
    raw_payload TEXT NOT NULL,
    ingested_at TEXT NOT NULL,
    PRIMARY KEY (source, fund_code, nav_date)
);

CREATE TABLE IF NOT EXISTS raw_macro_series (
    source TEXT NOT NULL,
    series_name TEXT NOT NULL,
    observation_date TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL,
    unit TEXT,
    raw_payload TEXT NOT NULL,
    ingested_at TEXT NOT NULL,
    PRIMARY KEY (source, series_name, observation_date, metric_name)
);

CREATE TABLE IF NOT EXISTS dim_fund (
    fund_code TEXT PRIMARY KEY,
    fund_name TEXT NOT NULL,
    market_type TEXT NOT NULL,
    is_listed INTEGER NOT NULL,
    benchmark_family TEXT NOT NULL,
    benchmark_name TEXT NOT NULL,
    selection_bucket TEXT NOT NULL,
    source_priority INTEGER NOT NULL,
    history_source TEXT NOT NULL,
    latest_trade_date TEXT,
    fund_type TEXT,
    tracking_mode TEXT,
    data_status TEXT NOT NULL,
    source_note TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fund_classification_map (
    fund_code TEXT NOT NULL,
    benchmark_family TEXT NOT NULL,
    benchmark_name TEXT NOT NULL,
    market_type TEXT NOT NULL,
    classification_reason TEXT NOT NULL,
    is_v1_core INTEGER NOT NULL,
    source_note TEXT,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (fund_code, benchmark_family)
);

CREATE TABLE IF NOT EXISTS fund_universe_membership (
    as_of_date TEXT NOT NULL,
    fund_code TEXT NOT NULL,
    fund_name TEXT NOT NULL,
    market_type TEXT NOT NULL,
    benchmark_family TEXT NOT NULL,
    benchmark_name TEXT NOT NULL,
    selection_bucket TEXT NOT NULL,
    source_priority INTEGER NOT NULL,
    selected_reason TEXT NOT NULL,
    history_source TEXT NOT NULL,
    PRIMARY KEY (as_of_date, fund_code)
);

CREATE TABLE IF NOT EXISTS fact_fund_market_daily (
    fund_code TEXT NOT NULL,
    trade_date TEXT NOT NULL,
    open REAL,
    close REAL,
    high REAL,
    low REAL,
    volume REAL,
    amount REAL,
    amplitude REAL,
    pct_chg REAL,
    chg REAL,
    turnover REAL,
    source TEXT NOT NULL,
    ingested_at TEXT NOT NULL,
    PRIMARY KEY (fund_code, trade_date)
);

CREATE TABLE IF NOT EXISTS fact_fund_nav_daily (
    fund_code TEXT NOT NULL,
    nav_date TEXT NOT NULL,
    unit_nav REAL,
    accum_nav REAL,
    daily_growth_rate REAL,
    source TEXT NOT NULL,
    ingested_at TEXT NOT NULL,
    PRIMARY KEY (fund_code, nav_date)
);

CREATE TABLE IF NOT EXISTS fact_macro_observation (
    series_name TEXT NOT NULL,
    observation_date TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL,
    unit TEXT,
    source TEXT NOT NULL,
    ingested_at TEXT NOT NULL,
    PRIMARY KEY (series_name, observation_date, metric_name)
);

CREATE TABLE IF NOT EXISTS data_validation_run (
    run_at TEXT PRIMARY KEY,
    universe_count INTEGER NOT NULL,
    etf_history_funds INTEGER NOT NULL,
    nav_history_funds INTEGER NOT NULL,
    macro_series_count INTEGER NOT NULL,
    checks_json TEXT NOT NULL
);
"""


class SQLiteStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def initialize(self) -> None:
        with self.connect() as conn:
            conn.executescript(SCHEMA_SQL)

    def replace_table(self, table_name: str, dataframe: pd.DataFrame) -> None:
        with self.connect() as conn:
            conn.execute(f"DELETE FROM {table_name}")
            if not dataframe.empty:
                dataframe.to_sql(table_name, conn, if_exists="append", index=False)

    def insert_validation(self, summary: dict[str, object]) -> None:
        row = pd.DataFrame(
            [
                {
                    "run_at": summary["run_at"],
                    "universe_count": summary["universe_count"],
                    "etf_history_funds": summary["etf_history_funds"],
                    "nav_history_funds": summary["nav_history_funds"],
                    "macro_series_count": summary["macro_series_count"],
                    "checks_json": json.dumps(summary["checks"], ensure_ascii=False),
                }
            ]
        )
        with self.connect() as conn:
            row.to_sql("data_validation_run", conn, if_exists="append", index=False)
