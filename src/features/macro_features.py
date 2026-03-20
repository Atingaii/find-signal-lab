from __future__ import annotations

import pandas as pd


MACRO_FIELD_MAP = {
    ("macro_china_pmi", "制造业-指数"): "macro_pmi_manufacturing",
    ("macro_china_pmi", "非制造业-指数"): "macro_pmi_non_manufacturing",
    ("macro_china_lpr", "LPR1Y"): "macro_lpr_1y",
    ("macro_china_lpr", "LPR5Y"): "macro_lpr_5y",
}


def build_macro_features(feature_df: pd.DataFrame, macro_df: pd.DataFrame) -> pd.DataFrame:
    base = feature_df.copy().sort_values("trade_date").reset_index(drop=True)
    base["trade_date"] = pd.to_datetime(base["trade_date"])

    macro = macro_df.copy()
    macro["observation_date"] = pd.to_datetime(macro["observation_date"])
    macro["feature_name"] = macro.apply(
        lambda row: MACRO_FIELD_MAP.get((row["series_name"], row["metric_name"])),
        axis=1,
    )
    macro = macro.loc[macro["feature_name"].notna()].copy()
    macro_wide = (
        macro.pivot_table(
            index="observation_date",
            columns="feature_name",
            values="metric_value",
            aggfunc="last",
        )
        .reset_index()
        .sort_values("observation_date")
    )
    if not macro_wide.empty:
        macro_wide = macro_wide.ffill()
        calendar = pd.date_range(
            start=macro_wide["observation_date"].min(),
            end=base["trade_date"].max(),
            freq="D",
        )
        macro_wide = (
            macro_wide.set_index("observation_date")
            .reindex(calendar)
            .ffill()
            .rename_axis("macro_snapshot_date")
            .reset_index()
        )

    market_turnover = (
        base.loc[base["amount"].notna(), ["trade_date", "amount"]]
        .groupby("trade_date", as_index=False)["amount"]
        .sum()
        .rename(columns={"amount": "market_turnover_total"})
        .sort_values("trade_date")
    )
    market_turnover["market_turnover_5d_avg"] = market_turnover["market_turnover_total"].rolling(
        5, min_periods=5
    ).mean()

    if not macro_wide.empty:
        base = base.merge(macro_wide, left_on="trade_date", right_on="macro_snapshot_date", how="left")
    else:
        base["macro_snapshot_date"] = pd.NaT

    base = base.merge(market_turnover, on="trade_date", how="left")
    return base
