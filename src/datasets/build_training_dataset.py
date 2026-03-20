from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


CORE_FEATURE_COLUMNS = [
    "daily_return_1d",
    "return_5d",
    "return_10d",
    "return_20d",
    "momentum_5_minus_20",
    "momentum_10_minus_20",
    "volatility_20d",
    "max_drawdown_20d",
    "excess_return_5d",
    "excess_return_20d",
    "style_strength_20d",
    "macro_pmi_manufacturing",
    "macro_pmi_non_manufacturing",
    "macro_lpr_1y",
    "macro_lpr_5y",
    "market_turnover_5d_avg",
]

CORE_LABEL_COLUMNS = [
    "future_1d_up",
    "future_5d_up",
    "future_20d_up",
    "future_5d_relative_strength",
    "future_20d_relative_strength",
]


@dataclass(frozen=True)
class SplitConfig:
    train_ratio: float = 0.70
    valid_ratio: float = 0.15
    purge_gap_days: int = 20


def assemble_training_dataset(
    feature_df: pd.DataFrame,
    label_df: pd.DataFrame,
    split_config: SplitConfig | None = None,
) -> tuple[pd.DataFrame, dict[str, object]]:
    config = split_config or SplitConfig()

    dataset = feature_df.merge(
        label_df,
        on=[
            "fund_code",
            "trade_date",
            "fund_name",
            "market_type",
            "benchmark_family",
            "benchmark_name",
            "selection_bucket",
            "reference_basis",
            "is_primary_target",
        ],
        how="inner",
    )
    dataset = dataset.sort_values(["trade_date", "fund_code"]).reset_index(drop=True)
    dataset = dataset.loc[dataset["is_primary_target"] == 1].copy()

    dataset["feature_ready"] = dataset[CORE_FEATURE_COLUMNS].notna().all(axis=1)
    dataset["label_ready"] = dataset[CORE_LABEL_COLUMNS].notna().all(axis=1)
    dataset = dataset.loc[dataset["feature_ready"] & dataset["label_ready"]].copy()
    dataset["dataset_split"] = _assign_time_split(dataset["trade_date"], config)
    dataset = dataset.loc[dataset["dataset_split"].notna()].copy()
    dataset["dataset_version"] = "v1_stage3"

    summary = {
        "rows": int(len(dataset)),
        "funds": int(dataset["fund_code"].nunique()),
        "date_range": [
            dataset["trade_date"].min().date().isoformat() if not dataset.empty else None,
            dataset["trade_date"].max().date().isoformat() if not dataset.empty else None,
        ],
        "split_counts": dataset["dataset_split"].value_counts().sort_index().to_dict(),
        "core_feature_columns": CORE_FEATURE_COLUMNS,
        "core_label_columns": CORE_LABEL_COLUMNS,
    }
    return dataset, summary


def _assign_time_split(trade_dates: pd.Series, config: SplitConfig) -> pd.Series:
    unique_dates = pd.Series(sorted(pd.to_datetime(trade_dates.unique())))
    if unique_dates.empty:
        return pd.Series(dtype="object", index=trade_dates.index)

    train_end_idx = max(int(len(unique_dates) * config.train_ratio) - 1, 0)
    valid_end_idx = max(int(len(unique_dates) * (config.train_ratio + config.valid_ratio)) - 1, train_end_idx)

    train_end_date = unique_dates.iloc[train_end_idx]
    valid_start_idx = min(train_end_idx + config.purge_gap_days + 1, len(unique_dates))
    valid_end_date = unique_dates.iloc[valid_end_idx]
    test_start_idx = min(valid_end_idx + config.purge_gap_days + 1, len(unique_dates))

    split = pd.Series(pd.NA, index=trade_dates.index, dtype="object")
    current_dates = pd.to_datetime(trade_dates)
    split.loc[current_dates <= train_end_date] = "train"

    if valid_start_idx < len(unique_dates):
        valid_start_date = unique_dates.iloc[valid_start_idx]
        split.loc[(current_dates >= valid_start_date) & (current_dates <= valid_end_date)] = "valid"

    if test_start_idx < len(unique_dates):
        test_start_date = unique_dates.iloc[test_start_idx]
        split.loc[current_dates >= test_start_date] = "test"
    return split
