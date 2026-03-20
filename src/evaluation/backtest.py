from __future__ import annotations

import pandas as pd


def simulate_top_k_strategy(
    dataframe: pd.DataFrame,
    score_column: str,
    actual_return_column: str,
    k: int = 3,
) -> tuple[pd.DataFrame, dict[str, float | int | None]]:
    rows: list[dict[str, object]] = []
    for trade_date, group in dataframe.groupby("trade_date", sort=True):
        ordered = group.sort_values(score_column, ascending=False)
        top = ordered.head(k)
        bottom = ordered.tail(k)
        top_return = top[actual_return_column].mean()
        bottom_return = bottom[actual_return_column].mean()
        spread = top_return - bottom_return if pd.notna(top_return) and pd.notna(bottom_return) else None
        rows.append(
            {
                "trade_date": trade_date,
                "top_k_return": top_return,
                "bottom_k_return": bottom_return,
                "top_bottom_spread": spread,
            }
        )

    history = pd.DataFrame(rows).sort_values("trade_date").reset_index(drop=True)
    history["top_k_equity"] = (1 + history["top_k_return"].fillna(0.0)).cumprod()
    history["top_bottom_equity"] = (1 + history["top_bottom_spread"].fillna(0.0)).cumprod()
    history["top_k_drawdown"] = history["top_k_equity"] / history["top_k_equity"].cummax() - 1
    history["top_bottom_drawdown"] = (
        history["top_bottom_equity"] / history["top_bottom_equity"].cummax() - 1
    )

    summary = {
        "periods": int(len(history)),
        "top_k_mean_return": float(history["top_k_return"].mean()) if not history.empty else None,
        "top_bottom_mean_spread": float(history["top_bottom_spread"].mean()) if not history.empty else None,
        "top_k_max_drawdown": float(history["top_k_drawdown"].min()) if not history.empty else None,
        "top_bottom_max_drawdown": float(history["top_bottom_drawdown"].min()) if not history.empty else None,
    }
    return history, summary

