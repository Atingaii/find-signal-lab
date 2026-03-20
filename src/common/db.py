from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


DEFAULT_DB_PATH = Path("data/sqlite/fund_data.db")


def resolve_db_path(db_path: str | Path | None = None) -> Path:
    return Path(db_path) if db_path else DEFAULT_DB_PATH


def read_sql(query: str, db_path: str | Path | None = None) -> pd.DataFrame:
    path = resolve_db_path(db_path)
    with sqlite3.connect(path) as conn:
        return pd.read_sql_query(query, conn)


def replace_table(
    table_name: str,
    dataframe: pd.DataFrame,
    db_path: str | Path | None = None,
) -> None:
    path = resolve_db_path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        dataframe.to_sql(table_name, conn, if_exists="replace", index=False)

