from __future__ import annotations

import json
from typing import Any


TARGET_LABELS = {
    "future_5d_up": "未来5个交易日上涨",
    "future_20d_relative_strength": "未来20个交易日相对同类更强",
}

FEATURE_LABELS = {
    "amount_change_1d": "近1日成交额变化",
    "daily_return_1d": "近1日收益",
    "return_5d": "近5日收益",
    "return_20d": "近20日收益",
    "excess_return_5d": "近5日超额收益",
    "excess_return_20d": "近20日超额收益",
    "style_strength_20d": "近20日风格强弱",
    "volatility_20d": "近20日波动率",
    "max_drawdown_20d": "近20日最大回撤",
    "momentum_5_minus_20": "5日-20日动量差",
    "momentum_10_minus_20": "10日-20日动量差",
    "market_turnover_5d_avg": "近5日市场成交额均值",
}

LLM_OUTPUT_SCHEMA = {
    "fund_code": "string",
    "fund_name": "string",
    "target_name": "string",
    "prediction_label": "integer",
    "prediction_probability": "float",
    "confidence_level": "string",
    "direction_conclusion": "string",
    "primary_reasons": "array<object>",
    "secondary_reasons": "array<object>",
    "risk_flags": "array<object>",
    "invalidation_conditions": "array<string>",
    "summary_text": "string",
    "report_date": "string",
}


def target_label(target_name: str) -> str:
    return TARGET_LABELS.get(target_name, target_name)


def feature_label(feature_name: str) -> str:
    return FEATURE_LABELS.get(feature_name, feature_name)


def chinese_confidence(confidence_level: str) -> str:
    mapping = {
        "high": "高",
        "medium": "中",
        "low": "低",
        "unknown": "未知",
    }
    return mapping.get(confidence_level, confidence_level)


def direction_conclusion(probability: float | None) -> str:
    if probability is None:
        return "中性"
    if probability >= 0.58:
        return "偏多"
    if probability <= 0.42:
        return "偏空"
    return "中性"


def format_percent(value: float | None) -> str:
    if value is None:
        return "缺失"
    return f"{value * 100:.2f}%"


def format_number(value: float | None) -> str:
    if value is None:
        return "缺失"
    return f"{value:.4f}"


def parse_json(value: Any, fallback: Any) -> Any:
    if value is None:
        return fallback
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        if not value.strip():
            return fallback
        return json.loads(value)
    return fallback


def format_reason_text(
    feature_name: str,
    contribution: float,
    feature_value: float | None,
    target_name: str,
) -> str:
    label = feature_label(feature_name)
    polarity = "正向贡献" if contribution >= 0 else "负向贡献"
    if feature_value is None:
        return f"{label}当前未在解释快照中单独透出数值，但该因子在当前模型中对{target_label(target_name)}形成{polarity}。"
    value_text = format_feature_value(feature_name, feature_value)
    return f"{label}为 {value_text}，在当前模型中对{target_label(target_name)}形成{polarity}。"


def format_feature_value(feature_name: str, value: float | None) -> str:
    if feature_name in {
        "amount_change_1d",
        "daily_return_1d",
        "return_5d",
        "return_20d",
        "excess_return_5d",
        "excess_return_20d",
        "style_strength_20d",
        "volatility_20d",
        "max_drawdown_20d",
        "momentum_5_minus_20",
        "momentum_10_minus_20",
    }:
        return format_percent(value)
    if feature_name == "market_turnover_5d_avg":
        if value is None:
            return "缺失"
        return f"{value / 100000000:.2f} 亿"
    return format_number(value)


def build_llm_surface_prompt(payload: dict[str, Any]) -> str:
    return (
        "你是基金方向预测器的解释整理层，只能润色结构化解释，不能新增事实。\n"
        "输入字段必须原样保留其含义，只能做压缩、排序和中文润色。\n"
        f"输出 JSON schema: {json.dumps(LLM_OUTPUT_SCHEMA, ensure_ascii=False)}\n"
        f"输入 payload: {json.dumps(payload, ensure_ascii=False)}"
    )
