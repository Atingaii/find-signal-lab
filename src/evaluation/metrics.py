from __future__ import annotations

import math

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score


def classification_metrics(y_true: pd.Series, y_prob: pd.Series, threshold: float = 0.5) -> dict[str, float]:
    y_true_int = y_true.astype(int)
    y_pred = (y_prob >= threshold).astype(int)
    metrics = {
        "accuracy": float(accuracy_score(y_true_int, y_pred)),
        "precision": float(precision_score(y_true_int, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true_int, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true_int, y_pred, zero_division=0)),
    }
    if y_true_int.nunique() >= 2:
        metrics["auc"] = float(roc_auc_score(y_true_int, y_prob))
    else:
        metrics["auc"] = float("nan")
    return metrics


def top_k_hit_rate(
    dataframe: pd.DataFrame,
    probability_column: str,
    label_column: str,
    k: int = 3,
) -> float:
    hits: list[float] = []
    for _, group in dataframe.groupby("trade_date", sort=True):
        top = group.sort_values(probability_column, ascending=False).head(k)
        if top.empty:
            continue
        hits.append(float(top[label_column].astype(int).mean()))
    return float(np.mean(hits)) if hits else float("nan")


def rank_ic(
    dataframe: pd.DataFrame,
    score_column: str,
    actual_return_column: str,
) -> float:
    correlations: list[float] = []
    for _, group in dataframe.groupby("trade_date", sort=True):
        subset = group[[score_column, actual_return_column]].dropna()
        if len(subset) < 2:
            continue
        correlation = subset[score_column].corr(subset[actual_return_column], method="spearman")
        if pd.notna(correlation):
            correlations.append(float(correlation))
    return float(np.mean(correlations)) if correlations else float("nan")


def grouped_return_spread(
    dataframe: pd.DataFrame,
    score_column: str,
    actual_return_column: str,
    k: int = 3,
) -> float:
    spreads: list[float] = []
    for _, group in dataframe.groupby("trade_date", sort=True):
        ordered = group.sort_values(score_column, ascending=False)
        top = ordered.head(k)[actual_return_column].mean()
        bottom = ordered.tail(k)[actual_return_column].mean()
        if pd.notna(top) and pd.notna(bottom):
            spreads.append(float(top - bottom))
    return float(np.mean(spreads)) if spreads else float("nan")


def safe_round(metrics: dict[str, float], digits: int = 6) -> dict[str, float | None]:
    result: dict[str, float | None] = {}
    for key, value in metrics.items():
        if value is None or (isinstance(value, float) and math.isnan(value)):
            result[key] = None
        else:
            result[key] = round(float(value), digits)
    return result

