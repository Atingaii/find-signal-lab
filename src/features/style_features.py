from __future__ import annotations

import pandas as pd


def build_style_features(feature_df: pd.DataFrame) -> pd.DataFrame:
    base = feature_df.copy()

    family_metrics = (
        base.groupby(["trade_date", "benchmark_family"], dropna=False)
        .agg(
            family_peer_count=("fund_code", "nunique"),
            family_return_1d=("daily_return_1d", "median"),
            family_return_5d=("return_5d", "median"),
            family_return_20d=("return_20d", "median"),
        )
        .reset_index()
    )

    style_baseline = (
        family_metrics.groupby("trade_date", dropna=False)
        .agg(
            universe_family_return_5d=("family_return_5d", "median"),
            universe_family_return_20d=("family_return_20d", "median"),
        )
        .reset_index()
    )

    family_metrics = family_metrics.merge(style_baseline, on="trade_date", how="left")
    family_metrics["style_strength_5d"] = (
        family_metrics["family_return_5d"] - family_metrics["universe_family_return_5d"]
    )
    family_metrics["style_strength_20d"] = (
        family_metrics["family_return_20d"] - family_metrics["universe_family_return_20d"]
    )

    base = base.merge(
        family_metrics[
            [
                "trade_date",
                "benchmark_family",
                "family_peer_count",
                "family_return_1d",
                "family_return_5d",
                "family_return_20d",
                "style_strength_5d",
                "style_strength_20d",
            ]
        ],
        on=["trade_date", "benchmark_family"],
        how="left",
    )

    base["excess_return_1d"] = base["daily_return_1d"] - base["family_return_1d"]
    base["excess_return_5d"] = base["return_5d"] - base["family_return_5d"]
    base["excess_return_20d"] = base["return_20d"] - base["family_return_20d"]
    return base

