from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


RETURN_WINDOWS = (1, 5, 10, 20)
VOL_WINDOWS = (5, 10, 20)


@dataclass(frozen=True)
class ReferenceSeriesSchema:
    fund_code: str = "fund_code"
    trade_date: str = "trade_date"
    reference_value: str = "reference_value"
    reference_basis: str = "reference_basis"


def build_reference_frame(
    dim_fund: pd.DataFrame,
    market_daily: pd.DataFrame,
    nav_daily: pd.DataFrame,
) -> pd.DataFrame:
    dim_columns = [
        "fund_code",
        "fund_name",
        "market_type",
        "benchmark_family",
        "benchmark_name",
        "selection_bucket",
    ]
    dim = dim_fund[dim_columns].copy()
    dim["is_primary_target"] = (dim["market_type"] == "ETF").astype(int)

    market = market_daily.copy()
    if not market.empty:
        market["trade_date"] = pd.to_datetime(market["trade_date"])
        market["reference_value"] = pd.to_numeric(market["close"], errors="coerce")
        market["reference_basis"] = "market_close"
        market["unit_nav"] = np.nan
        market["nav_date"] = pd.NaT
        market = market.merge(dim, on="fund_code", how="inner")

    nav = nav_daily.copy()
    if not nav.empty:
        nav["trade_date"] = pd.to_datetime(nav["nav_date"])
        nav["reference_value"] = pd.to_numeric(nav["unit_nav"], errors="coerce")
        nav["reference_basis"] = "unit_nav"
        nav["open"] = np.nan
        nav["close"] = np.nan
        nav["high"] = np.nan
        nav["low"] = np.nan
        nav["volume"] = np.nan
        nav["amount"] = np.nan
        nav["amplitude"] = np.nan
        nav["pct_chg"] = np.nan
        nav["chg"] = np.nan
        nav["turnover"] = np.nan
        nav = nav.merge(dim, on="fund_code", how="inner")

    combined = pd.concat([market, nav], ignore_index=True, sort=False)
    combined = combined.sort_values(["fund_code", "trade_date"]).reset_index(drop=True)
    combined["reference_value"] = pd.to_numeric(combined["reference_value"], errors="coerce")
    combined["daily_return_1d"] = combined.groupby("fund_code")["reference_value"].pct_change()
    combined["series_age_days"] = combined.groupby("fund_code").cumcount() + 1
    return combined


def build_price_features(reference_df: pd.DataFrame) -> pd.DataFrame:
    base = reference_df.copy()
    base = base.sort_values(["fund_code", "trade_date"]).reset_index(drop=True)

    grouped_value = base.groupby("fund_code")["reference_value"]
    grouped_return = base.groupby("fund_code")["daily_return_1d"]

    for window in RETURN_WINDOWS:
        base[f"return_{window}d"] = grouped_value.pct_change(window)
        rolling_mean = grouped_value.transform(lambda series: series.rolling(window, min_periods=window).mean())
        base[f"ma_gap_{window}d"] = base["reference_value"] / rolling_mean - 1

    base["momentum_5_minus_20"] = base["return_5d"] - base["return_20d"]
    base["momentum_10_minus_20"] = base["return_10d"] - base["return_20d"]
    base["up_day_ratio_10d"] = grouped_return.transform(
        lambda series: series.gt(0).rolling(10, min_periods=10).mean()
    )

    for window in VOL_WINDOWS:
        base[f"volatility_{window}d"] = grouped_return.transform(
            lambda series: series.rolling(window, min_periods=window).std()
        )

    base["max_drawdown_20d"] = grouped_value.transform(_rolling_max_drawdown_20d)
    return base


def _rolling_max_drawdown_20d(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")
    result = pd.Series(index=values.index, dtype="float64")
    for end in range(len(values)):
        start = end - 19
        if start < 0:
            result.iloc[end] = np.nan
            continue
        window = values.iloc[start : end + 1]
        if window.isna().any():
            result.iloc[end] = np.nan
            continue
        peaks = window.cummax()
        drawdowns = window / peaks - 1
        result.iloc[end] = drawdowns.min()
    return result
