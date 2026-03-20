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

from data_sources.akshare_client import AkShareClient
from data_sources.official_client import OfficialClient
from storage.sqlite_store import SQLiteStore
from universe.builder import UniverseBuilder


def row_to_json(row: pd.Series) -> str:
    return json.dumps(row.to_dict(), ensure_ascii=False, default=str)


def normalize_fund_master(frame: pd.DataFrame, snapshot_at: str) -> pd.DataFrame:
    renamed = frame.rename(
        columns={
            "基金代码": "fund_code",
            "基金简称": "fund_name",
            "基金类型": "fund_type",
        }
    ).copy()
    renamed["snapshot_at"] = snapshot_at
    renamed["source"] = "akshare_fund_name_em"
    renamed["raw_payload"] = frame.apply(row_to_json, axis=1)
    return renamed[["snapshot_at", "source", "fund_code", "fund_name", "fund_type", "raw_payload"]]


def normalize_quote_snapshot(
    frame: pd.DataFrame,
    snapshot_at: str,
    source: str,
    market_type: str,
) -> pd.DataFrame:
    renamed = frame.rename(
        columns={
            "基金代码": "fund_code",
            "基金名称": "fund_name",
            "当前-单位净值": "nav_unit",
            "当前-累计净值": "nav_accumulated",
            "前一日-单位净值": "previous_unit_nav",
            "前一日-累计净值": "previous_accumulated_nav",
            "增长值": "growth_value",
            "增长率": "growth_rate",
            "最新-交易日": "latest_trade_date",
            "申购状态": "purchase_status",
            "赎回状态": "redemption_status",
        }
    ).copy()
    renamed["snapshot_at"] = snapshot_at
    renamed["source"] = source
    renamed["market_type"] = market_type
    renamed["raw_payload"] = frame.apply(row_to_json, axis=1)
    return renamed[
        [
            "snapshot_at",
            "source",
            "market_type",
            "fund_code",
            "fund_name",
            "nav_unit",
            "nav_accumulated",
            "previous_unit_nav",
            "previous_accumulated_nav",
            "growth_value",
            "growth_rate",
            "latest_trade_date",
            "purchase_status",
            "redemption_status",
            "raw_payload",
        ]
    ]


def normalize_index_snapshot(frame: pd.DataFrame, snapshot_at: str) -> pd.DataFrame:
    renamed = frame.rename(
        columns={
            "基金代码": "fund_code",
            "基金名称": "fund_name",
            "单位净值": "unit_nav",
            "日期": "nav_date",
            "日增长率": "growth_rate",
            "跟踪方式": "tracking_mode",
            "跟踪标的": "benchmark_scope",
        }
    ).copy()
    renamed = renamed.drop_duplicates(subset=["fund_code"]).copy()
    renamed["snapshot_at"] = snapshot_at
    renamed["source"] = "akshare_fund_info_index_em"
    renamed["raw_payload"] = renamed.apply(row_to_json, axis=1)
    return renamed[
        [
            "snapshot_at",
            "source",
            "fund_code",
            "fund_name",
            "unit_nav",
            "nav_date",
            "growth_rate",
            "tracking_mode",
            "benchmark_scope",
            "raw_payload",
        ]
    ]


def build_dim_fund(universe_df: pd.DataFrame, snapshot_at: str) -> pd.DataFrame:
    dim = universe_df.copy()
    dim["created_at"] = snapshot_at
    dim["updated_at"] = snapshot_at
    return dim[
        [
            "fund_code",
            "fund_name",
            "market_type",
            "is_listed",
            "benchmark_family",
            "benchmark_name",
            "selection_bucket",
            "source_priority",
            "history_source",
            "latest_trade_date",
            "fund_type",
            "tracking_mode",
            "data_status",
            "source_note",
            "created_at",
            "updated_at",
        ]
    ]


def build_universe_membership(universe_df: pd.DataFrame, as_of_date: str) -> pd.DataFrame:
    membership = universe_df.copy()
    membership["as_of_date"] = as_of_date
    return membership[
        [
            "as_of_date",
            "fund_code",
            "fund_name",
            "market_type",
            "benchmark_family",
            "benchmark_name",
            "selection_bucket",
            "source_priority",
            "selected_reason",
            "history_source",
        ]
    ]


def collect_etf_history(
    client: AkShareClient,
    universe_df: pd.DataFrame,
    start_date: str,
    end_date: str,
    ingested_at: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw_rows: list[pd.DataFrame] = []
    fact_rows: list[pd.DataFrame] = []
    etf_codes = universe_df.loc[universe_df["market_type"] == "ETF", "fund_code"].tolist()

    for fund_code in etf_codes:
        try:
            history = client.fetch_etf_history(fund_code, start_date=start_date, end_date=end_date)
        except Exception as exc:
            print(f"WARN: skip ETF history for {fund_code}: {exc}")
            continue
        if history.empty:
            continue

        history = history.rename(
            columns={
                "日期": "trade_date",
                "开盘": "open",
                "收盘": "close",
                "最高": "high",
                "最低": "low",
                "成交量": "volume",
                "成交额": "amount",
                "振幅": "amplitude",
                "涨跌幅": "pct_chg",
                "涨跌额": "chg",
                "换手率": "turnover",
            }
        ).copy()
        history["fund_code"] = fund_code
        history["source"] = history.attrs.get("source", "listed_fund_history")
        history["ingested_at"] = ingested_at
        history["raw_payload"] = history.apply(row_to_json, axis=1)

        raw_rows.append(
            history[
                [
                    "source",
                    "fund_code",
                    "trade_date",
                    "open",
                    "close",
                    "high",
                    "low",
                    "volume",
                    "amount",
                    "amplitude",
                    "pct_chg",
                    "chg",
                    "turnover",
                    "raw_payload",
                    "ingested_at",
                ]
            ]
        )
        fact_rows.append(
            history[
                [
                    "fund_code",
                    "trade_date",
                    "open",
                    "close",
                    "high",
                    "low",
                    "volume",
                    "amount",
                    "amplitude",
                    "pct_chg",
                    "chg",
                    "turnover",
                    "source",
                    "ingested_at",
                ]
            ]
        )

    return concat_frames(raw_rows), concat_frames(fact_rows)


def collect_nav_history(
    client: OfficialClient,
    universe_df: pd.DataFrame,
    ingested_at: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw_rows: list[pd.DataFrame] = []
    fact_rows: list[pd.DataFrame] = []
    nav_codes = universe_df.loc[
        universe_df["history_source"] == "eastmoney_pingzhongdata", "fund_code"
    ].tolist()

    for fund_code in nav_codes:
        _, nav_df = client.fetch_fund_nav_history(fund_code)
        if nav_df.empty:
            continue
        nav_df = nav_df.rename(
            columns={
                "净值日期": "nav_date",
                "单位净值": "unit_nav",
                "累计净值": "accum_nav",
                "日增长率": "daily_growth_rate",
            }
        ).copy()
        nav_df["fund_code"] = fund_code
        nav_df["source"] = "eastmoney_pingzhongdata"
        nav_df["ingested_at"] = ingested_at
        nav_df["raw_payload"] = nav_df.apply(row_to_json, axis=1)

        raw_rows.append(
            nav_df[
                [
                    "source",
                    "fund_code",
                    "nav_date",
                    "unit_nav",
                    "accum_nav",
                    "daily_growth_rate",
                    "raw_payload",
                    "ingested_at",
                ]
            ]
        )
        fact_rows.append(
            nav_df[
                [
                    "fund_code",
                    "nav_date",
                    "unit_nav",
                    "accum_nav",
                    "daily_growth_rate",
                    "source",
                    "ingested_at",
                ]
            ]
        )

    return concat_frames(raw_rows), concat_frames(fact_rows)


def normalize_pmi(frame: pd.DataFrame, ingested_at: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, row in frame.iterrows():
        month_text = str(row["月份"]).replace("年", "-").replace("月份", "-01")
        observation_date = pd.to_datetime(month_text).date().isoformat()
        for metric_name in ["制造业-指数", "制造业-同比增长", "非制造业-指数", "非制造业-同比增长"]:
            rows.append(
                {
                    "series_name": "macro_china_pmi",
                    "observation_date": observation_date,
                    "metric_name": metric_name,
                    "metric_value": row[metric_name],
                    "unit": "pct_or_index",
                    "source": "akshare_macro_china_pmi",
                    "ingested_at": ingested_at,
                    "raw_payload": row_to_json(row),
                }
            )
    return pd.DataFrame(rows)


def normalize_lpr(frame: pd.DataFrame, ingested_at: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, row in frame.iterrows():
        observation_date = pd.to_datetime(row["TRADE_DATE"]).date().isoformat()
        for metric_name in ["LPR1Y", "LPR5Y", "RATE_1", "RATE_2"]:
            rows.append(
                {
                    "series_name": "macro_china_lpr",
                    "observation_date": observation_date,
                    "metric_name": metric_name,
                    "metric_value": row[metric_name],
                    "unit": "pct",
                    "source": "akshare_macro_china_lpr",
                    "ingested_at": ingested_at,
                    "raw_payload": row_to_json(row),
                }
            )
    return pd.DataFrame(rows)


def normalize_sse_summary(frame: pd.DataFrame, ingested_at: str) -> pd.DataFrame:
    report_row = frame.loc[frame["项目"] == "报告时间"]
    observation_date = datetime.now(UTC).date().isoformat()
    if not report_row.empty:
        report_text = str(report_row.iloc[0]["股票"])
        observation_date = pd.to_datetime(report_text).date().isoformat()

    rows: list[dict[str, object]] = []
    for _, row in frame.iterrows():
        item = row["项目"]
        if item == "报告时间":
            continue
        for category in ["股票", "主板", "科创板"]:
            rows.append(
                {
                    "series_name": "sse_market_summary",
                    "observation_date": observation_date,
                    "metric_name": f"{category}_{item}",
                    "metric_value": pd.to_numeric(row[category], errors="coerce"),
                    "unit": "",
                    "source": "akshare_stock_sse_summary",
                    "ingested_at": ingested_at,
                    "raw_payload": row_to_json(row),
                }
            )
    return pd.DataFrame(rows)


def normalize_szse_summary(frame: pd.DataFrame, trade_date: str, ingested_at: str) -> pd.DataFrame:
    observation_date = pd.to_datetime(trade_date).date().isoformat()
    rows: list[dict[str, object]] = []
    for _, row in frame.iterrows():
        category = row["证券类别"]
        for metric_name in ["数量", "成交金额", "总市值", "流通市值"]:
            rows.append(
                {
                    "series_name": "szse_market_summary",
                    "observation_date": observation_date,
                    "metric_name": f"{category}_{metric_name}",
                    "metric_value": pd.to_numeric(row[metric_name], errors="coerce"),
                    "unit": "",
                    "source": "akshare_stock_szse_summary",
                    "ingested_at": ingested_at,
                    "raw_payload": row_to_json(row),
                }
            )
    return pd.DataFrame(rows)


def concat_frames(frames: list[pd.DataFrame]) -> pd.DataFrame:
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def save_reference_pages(client: OfficialClient, trade_date: str) -> None:
    output_dir = ROOT / "data" / "raw" / "official"
    output_dir.mkdir(parents=True, exist_ok=True)
    sse_page = client.fetch_sse_fundlist_page()
    szse_page = client.fetch_szse_lof_reference_page()
    (output_dir / f"sse_fundlist_{trade_date}.html").write_text(sse_page.text, encoding="utf-8")
    (output_dir / f"szse_lof_reference_{trade_date}.html").write_text(
        szse_page.text, encoding="utf-8"
    )


def build_summary(
    run_at: str,
    universe_df: pd.DataFrame,
    market_daily: pd.DataFrame,
    nav_daily: pd.DataFrame,
    macro_fact: pd.DataFrame,
) -> dict[str, object]:
    checks = {
        "universe_count_ge_20": int(len(universe_df) >= 20),
        "etf_history_loaded": int(market_daily["fund_code"].nunique() >= 1) if not market_daily.empty else 0,
        "nav_history_loaded": int(nav_daily["fund_code"].nunique() >= 1) if not nav_daily.empty else 0,
        "macro_loaded": int(macro_fact["series_name"].nunique() >= 1) if not macro_fact.empty else 0,
    }
    return {
        "run_at": run_at,
        "universe_count": int(len(universe_df)),
        "etf_history_funds": int(market_daily["fund_code"].nunique()) if not market_daily.empty else 0,
        "nav_history_funds": int(nav_daily["fund_code"].nunique()) if not nav_daily.empty else 0,
        "macro_series_count": int(macro_fact["series_name"].nunique()) if not macro_fact.empty else 0,
        "checks": checks,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync stage-two fund data into SQLite.")
    parser.add_argument("--start-date", default="20240101", help="ETF history start date in YYYYMMDD.")
    parser.add_argument(
        "--end-date",
        default=datetime.now(UTC).strftime("%Y%m%d"),
        help="ETF history end date in YYYYMMDD.",
    )
    parser.add_argument(
        "--trade-date",
        default=datetime.now(UTC).strftime("%Y%m%d"),
        help="Trade date for daily snapshots and market summary.",
    )
    parser.add_argument(
        "--db-path",
        default=str(ROOT / "data" / "sqlite" / "fund_data.db"),
        help="Target SQLite database path.",
    )
    args = parser.parse_args()

    snapshot_at = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    as_of_date = pd.to_datetime(args.trade_date).date().isoformat()

    ak_client = AkShareClient()
    supplement_client = OfficialClient()
    builder = UniverseBuilder(ROOT / "config" / "fund_pool_v1.yaml")
    store = SQLiteStore(Path(args.db_path))
    store.initialize()

    fund_master = ak_client.fetch_fund_master()
    etf_snapshot = ak_client.fetch_etf_snapshot()
    lof_snapshot = ak_client.fetch_lof_snapshot()
    passive_index_funds = ak_client.fetch_passive_index_funds()

    universe_df = builder.build(fund_master, etf_snapshot, lof_snapshot, passive_index_funds)
    classification_map = builder.build_classification_map(universe_df)

    raw_fund_master = normalize_fund_master(fund_master, snapshot_at)
    raw_etf_snapshot = normalize_quote_snapshot(
        etf_snapshot, snapshot_at, "akshare_fund_etf_category_ths", "ETF"
    )
    raw_lof_snapshot = normalize_quote_snapshot(
        lof_snapshot, snapshot_at, "akshare_fund_etf_category_ths", "LOF"
    )
    raw_index_snapshot = normalize_index_snapshot(passive_index_funds, snapshot_at)

    raw_market_daily, fact_market_daily = collect_etf_history(
        ak_client,
        universe_df,
        start_date=args.start_date,
        end_date=args.end_date,
        ingested_at=snapshot_at,
    )
    raw_nav_daily, fact_nav_daily = collect_nav_history(
        supplement_client, universe_df, ingested_at=snapshot_at
    )

    macro_fact = concat_frames(
        [
            normalize_pmi(ak_client.fetch_macro_pmi(), snapshot_at),
            normalize_lpr(ak_client.fetch_macro_lpr(), snapshot_at),
            normalize_sse_summary(ak_client.fetch_sse_summary(), snapshot_at),
            normalize_szse_summary(ak_client.fetch_szse_summary(args.trade_date), args.trade_date, snapshot_at),
        ]
    )
    raw_macro = macro_fact.copy()

    store.replace_table("raw_fund_master_snapshot", raw_fund_master)
    store.replace_table("raw_fund_quote_snapshot", concat_frames([raw_etf_snapshot, raw_lof_snapshot]))
    store.replace_table("raw_index_fund_snapshot", raw_index_snapshot)
    store.replace_table("raw_etf_history", raw_market_daily)
    store.replace_table("raw_fund_nav", raw_nav_daily)
    store.replace_table(
        "raw_macro_series",
        raw_macro[
            [
                "source",
                "series_name",
                "observation_date",
                "metric_name",
                "metric_value",
                "unit",
                "raw_payload",
                "ingested_at",
            ]
        ],
    )
    store.replace_table("dim_fund", build_dim_fund(universe_df, snapshot_at))
    store.replace_table("fund_classification_map", classification_map)
    store.replace_table("fund_universe_membership", build_universe_membership(universe_df, as_of_date))
    store.replace_table("fact_fund_market_daily", fact_market_daily)
    store.replace_table("fact_fund_nav_daily", fact_nav_daily)
    store.replace_table(
        "fact_macro_observation",
        macro_fact[
            [
                "series_name",
                "observation_date",
                "metric_name",
                "metric_value",
                "unit",
                "source",
                "ingested_at",
            ]
        ],
    )

    save_reference_pages(supplement_client, args.trade_date)

    processed_dir = ROOT / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    universe_df.to_csv(processed_dir / "fund_universe_v1.csv", index=False, encoding="utf-8-sig")
    summary = build_summary(snapshot_at, universe_df, fact_market_daily, fact_nav_daily, macro_fact)
    (processed_dir / "sync_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    store.insert_validation(summary)

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
