from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from universe.classifier import (
    classify_benchmark_family,
    normalize_fund_code,
    normalize_fund_name,
)


class UniverseBuilder:
    def __init__(self, config_path: Path) -> None:
        with config_path.open("r", encoding="utf-8") as file:
            self.config = yaml.safe_load(file)

    def build(
        self,
        fund_master: pd.DataFrame,
        etf_snapshot: pd.DataFrame,
        lof_snapshot: pd.DataFrame,
        passive_index_funds: pd.DataFrame,
    ) -> pd.DataFrame:
        master_lookup = self._prepare_lookup(fund_master, "基金代码", "基金简称")
        etf_lookup = self._prepare_lookup(etf_snapshot, "基金代码", "基金名称")
        lof_lookup = self._prepare_lookup(lof_snapshot, "基金代码", "基金名称")
        index_lookup = self._prepare_lookup(passive_index_funds, "基金代码", "基金名称")

        records: list[dict[str, object]] = []
        for spec in self.config["funds"]:
            fund_code = normalize_fund_code(spec["fund_code"])
            source_note: list[str] = []
            resolved_name = normalize_fund_name(spec["fund_name_hint"])

            for source_row in [master_lookup, etf_lookup, lof_lookup, index_lookup]:
                if fund_code not in source_row.index:
                    continue
                row = source_row.loc[fund_code]
                if not resolved_name:
                    resolved_name = normalize_fund_name(row["fund_name"])
                source_note.append(str(row["source_label"]))

            family_code, family_name = classify_benchmark_family(resolved_name)
            if not family_code:
                family_code = spec["benchmark_family"]
                family_name = spec["benchmark_name"]

            master_row = master_lookup.loc[fund_code] if fund_code in master_lookup.index else None
            index_row = index_lookup.loc[fund_code] if fund_code in index_lookup.index else None
            latest_trade_date = None
            if spec["market_type"] == "ETF" and fund_code in etf_lookup.index:
                latest_trade_date = etf_lookup.loc[fund_code]["latest_trade_date"]
            if spec["market_type"] == "LOF" and fund_code in lof_lookup.index:
                latest_trade_date = lof_lookup.loc[fund_code]["latest_trade_date"]

            records.append(
                {
                    "fund_code": fund_code,
                    "fund_name": resolved_name,
                    "market_type": spec["market_type"],
                    "is_listed": int(spec["market_type"] in {"ETF", "LOF"}),
                    "benchmark_family": family_code,
                    "benchmark_name": family_name,
                    "selection_bucket": spec["selection_bucket"],
                    "source_priority": spec["source_priority"],
                    "history_source": spec["history_source"],
                    "selected_reason": spec["selected_reason"],
                    "fund_type": self._extract_value(master_row, "fund_type"),
                    "tracking_mode": self._extract_value(index_row, "tracking_mode"),
                    "latest_trade_date": latest_trade_date,
                    "data_status": "verified" if source_note else "hint_only",
                    "source_note": ",".join(source_note) if source_note else "config_only",
                }
            )

        return pd.DataFrame(records).sort_values(
            ["source_priority", "benchmark_family", "market_type", "fund_code"]
        ).reset_index(drop=True)

    def build_classification_map(self, universe_df: pd.DataFrame) -> pd.DataFrame:
        result = universe_df[
            [
                "fund_code",
                "benchmark_family",
                "benchmark_name",
                "market_type",
                "selected_reason",
                "source_note",
            ]
        ].copy()
        result["classification_reason"] = (
            result["benchmark_name"] + " family inferred from curated V1 pool"
        )
        result["is_v1_core"] = result["market_type"].isin(["ETF"]).astype(int)
        result["updated_at"] = pd.Timestamp.utcnow().isoformat()
        return result[
            [
                "fund_code",
                "benchmark_family",
                "benchmark_name",
                "market_type",
                "classification_reason",
                "is_v1_core",
                "source_note",
                "updated_at",
            ]
        ]

    @staticmethod
    def _extract_value(row: pd.Series | None, key: str) -> str | None:
        if row is None:
            return None
        value = row.get(key)
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @staticmethod
    def _prepare_lookup(df: pd.DataFrame, code_col: str, name_col: str) -> pd.DataFrame:
        prepared = df.copy()
        prepared = prepared.rename(columns={code_col: "fund_code", name_col: "fund_name"})
        prepared["fund_code"] = prepared["fund_code"].map(normalize_fund_code)
        prepared["fund_name"] = prepared["fund_name"].map(normalize_fund_name)

        if "基金类型" in prepared.columns:
            prepared = prepared.rename(columns={"基金类型": "fund_type"})
        if "跟踪方式" in prepared.columns:
            prepared = prepared.rename(columns={"跟踪方式": "tracking_mode"})
        if "最新-交易日" in prepared.columns:
            prepared = prepared.rename(columns={"最新-交易日": "latest_trade_date"})

        prepared["source_label"] = name_col
        return prepared.drop_duplicates("fund_code").set_index("fund_code", drop=False)
