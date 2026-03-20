from __future__ import annotations

import json

import pandas as pd


EXPLANATION_COLUMNS = [
    "fund_code",
    "fund_name",
    "benchmark_family",
    "prediction_date",
    "target_name",
    "prediction_label",
    "prediction_probability",
    "confidence_level",
    "top_feature_contributors",
    "risk_snapshot",
    "feature_snapshot",
    "explanation_input_payload",
    "model_name",
    "model_version",
]


def build_prediction_output(
    dataframe: pd.DataFrame,
    target_name: str,
) -> pd.DataFrame:
    result = dataframe.copy()
    result["target_name"] = target_name
    result["prediction_date"] = pd.to_datetime(result["trade_date"]).dt.date.astype(str)
    result["confidence_level"] = result["prediction_probability"].map(_confidence_level)
    result["feature_snapshot"] = result.apply(_feature_snapshot_json, axis=1)
    result["risk_snapshot"] = result.apply(_risk_snapshot_json, axis=1)
    result["explanation_input_payload"] = result.apply(_explanation_input_payload_json, axis=1)
    return result


def latest_prediction_snapshot(dataframe: pd.DataFrame, target_name: str) -> pd.DataFrame:
    latest_date = pd.to_datetime(dataframe["trade_date"]).max()
    latest_rows = dataframe.loc[pd.to_datetime(dataframe["trade_date"]) == latest_date].copy()
    latest_rows = latest_rows.sort_values("rank_score", ascending=False).reset_index(drop=True)
    return build_prediction_output(latest_rows, target_name)


def _feature_snapshot_json(row: pd.Series) -> str:
    payload = {
        "return_5d": _to_float(row.get("return_5d")),
        "return_20d": _to_float(row.get("return_20d")),
        "excess_return_5d": _to_float(row.get("excess_return_5d")),
        "excess_return_20d": _to_float(row.get("excess_return_20d")),
        "style_strength_20d": _to_float(row.get("style_strength_20d")),
        "volatility_20d": _to_float(row.get("volatility_20d")),
        "max_drawdown_20d": _to_float(row.get("max_drawdown_20d")),
    }
    return json.dumps(payload, ensure_ascii=False)


def _risk_snapshot_json(row: pd.Series) -> str:
    payload = {
        "volatility_20d": _to_float(row.get("volatility_20d")),
        "max_drawdown_20d": _to_float(row.get("max_drawdown_20d")),
        "market_turnover_5d_avg": _to_float(row.get("market_turnover_5d_avg")),
    }
    return json.dumps(payload, ensure_ascii=False)


def _explanation_input_payload_json(row: pd.Series) -> str:
    payload = {
        "fund_code": row.get("fund_code"),
        "fund_name": row.get("fund_name"),
        "benchmark_family": row.get("benchmark_family"),
        "prediction_date": pd.to_datetime(row.get("trade_date")).date().isoformat()
        if pd.notna(row.get("trade_date"))
        else None,
        "target_name": row.get("target_name"),
        "prediction_label": int(row.get("prediction_label")) if pd.notna(row.get("prediction_label")) else None,
        "prediction_probability": _to_float(row.get("prediction_probability")),
        "confidence_level": _confidence_level(row.get("prediction_probability")),
        "top_feature_contributors": json.loads(row.get("top_feature_contributors", "[]")),
        "feature_snapshot": json.loads(_feature_snapshot_json(row)),
        "risk_snapshot": json.loads(_risk_snapshot_json(row)),
        "model_name": row.get("model_name"),
        "model_version": row.get("model_version"),
    }
    return json.dumps(payload, ensure_ascii=False)


def _confidence_level(probability: object) -> str:
    if probability is None or pd.isna(probability):
        return "unknown"
    gap = abs(float(probability) - 0.5)
    if gap >= 0.25:
        return "high"
    if gap >= 0.10:
        return "medium"
    return "low"


def _to_float(value: object) -> float | None:
    if value is None or pd.isna(value):
        return None
    return float(value)
