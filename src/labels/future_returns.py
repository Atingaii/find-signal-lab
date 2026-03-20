from __future__ import annotations

import pandas as pd


LABEL_HORIZONS = (1, 5, 20)


def build_future_return_labels(reference_df: pd.DataFrame) -> pd.DataFrame:
    base = reference_df.copy()
    base = base.sort_values(["fund_code", "trade_date"]).reset_index(drop=True)

    grouped_value = base.groupby("fund_code")["reference_value"]
    grouped_date = base.groupby("fund_code")["trade_date"]

    for horizon in LABEL_HORIZONS:
        base[f"future_date_{horizon}d"] = grouped_date.shift(-horizon)
        base[f"future_{horizon}d_return"] = grouped_value.shift(-horizon) / base["reference_value"] - 1
        base[f"future_{horizon}d_up"] = (
            base[f"future_{horizon}d_return"].gt(0).where(base[f"future_{horizon}d_return"].notna())
        ).astype("Int64")

    for horizon in (5, 20):
        peer_median = (
            base.groupby(["trade_date", "benchmark_family"], dropna=False)[f"future_{horizon}d_return"]
            .transform("median")
        )
        peer_count = (
            base.groupby(["trade_date", "benchmark_family"], dropna=False)["fund_code"].transform("nunique")
        )
        base[f"future_{horizon}d_peer_median_return"] = peer_median
        base[f"future_{horizon}d_relative_excess"] = (
            base[f"future_{horizon}d_return"] - base[f"future_{horizon}d_peer_median_return"]
        )
        relative_strength = base[f"future_{horizon}d_relative_excess"].gt(0)
        base[f"future_{horizon}d_relative_strength"] = (
            relative_strength.where(
                base[f"future_{horizon}d_relative_excess"].notna() & peer_count.gt(1)
            )
        ).astype("Int64")

    return base[
        [
            "fund_code",
            "trade_date",
            "fund_name",
            "market_type",
            "benchmark_family",
            "benchmark_name",
            "selection_bucket",
            "reference_basis",
            "is_primary_target",
            "future_date_1d",
            "future_date_5d",
            "future_date_20d",
            "future_1d_return",
            "future_5d_return",
            "future_20d_return",
            "future_1d_up",
            "future_5d_up",
            "future_20d_up",
            "future_5d_peer_median_return",
            "future_20d_peer_median_return",
            "future_5d_relative_excess",
            "future_20d_relative_excess",
            "future_5d_relative_strength",
            "future_20d_relative_strength",
        ]
    ].copy()
