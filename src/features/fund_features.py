from __future__ import annotations

import numpy as np
import pandas as pd


def build_fund_features(feature_df: pd.DataFrame) -> pd.DataFrame:
    base = feature_df.copy()
    grouped_amount = base.groupby("fund_code")["amount"]
    grouped_turnover = base.groupby("fund_code")["turnover"]

    base["amount_change_1d"] = grouped_amount.pct_change(fill_method=None)
    base["amount_change_5d"] = grouped_amount.pct_change(5, fill_method=None)
    base["amount_ma_gap_5d"] = base["amount"] / grouped_amount.transform(
        lambda series: series.rolling(5, min_periods=5).mean()
    ) - 1
    base["amount_ma_gap_20d"] = base["amount"] / grouped_amount.transform(
        lambda series: series.rolling(20, min_periods=20).mean()
    ) - 1
    base["turnover_avg_5d"] = grouped_turnover.transform(
        lambda series: series.rolling(5, min_periods=5).mean()
    )
    base["turnover_avg_20d"] = grouped_turnover.transform(
        lambda series: series.rolling(20, min_periods=20).mean()
    )
    base["liquidity_feature_ready"] = base["amount"].notna().astype(int)

    # Stage-three scope intentionally excludes historical premium/discount and share/AUM deltas,
    # because stage-two did not persist those time series yet.
    base["premium_discount_rate"] = np.nan
    base["share_change_20d"] = np.nan
    base["aum_change_20d"] = np.nan
    return base
