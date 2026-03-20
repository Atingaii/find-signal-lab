from __future__ import annotations

from typing import Any

from explain.templates import feature_label, format_percent


def build_risk_flags(
    probability: float | None,
    confidence_level: str,
    feature_snapshot: dict[str, Any],
    risk_snapshot: dict[str, Any],
    prediction_label: int | None,
) -> list[dict[str, Any]]:
    flags: list[dict[str, Any]] = []
    volatility = _to_float(risk_snapshot.get("volatility_20d"))
    drawdown = _to_float(risk_snapshot.get("max_drawdown_20d"))
    return_20d = _to_float(feature_snapshot.get("return_20d"))
    excess_return_20d = _to_float(feature_snapshot.get("excess_return_20d"))

    if confidence_level == "low":
        flags.append(
            {
                "flag_code": "low_confidence",
                "severity": "medium",
                "message": "当前样本靠近决策边界，方向结论稳定性一般。",
            }
        )

    if volatility is not None and volatility >= 0.015:
        flags.append(
            {
                "flag_code": "high_volatility_20d",
                "severity": "high",
                "message": f"近20日波动率为 {format_percent(volatility)}，短期波动风险偏高。",
            }
        )

    if drawdown is not None and drawdown <= -0.05:
        flags.append(
            {
                "flag_code": "deep_drawdown_20d",
                "severity": "high",
                "message": f"近20日最大回撤为 {format_percent(drawdown)}，回撤修复尚未确认。",
            }
        )

    if prediction_label == 1 and return_20d is not None and return_20d < 0:
        flags.append(
            {
                "flag_code": "trend_conflict",
                "severity": "medium",
                "message": "模型偏多，但近20日收益仍为负，趋势一致性不足。",
            }
        )

    if prediction_label == 0 and excess_return_20d is not None and excess_return_20d > 0:
        flags.append(
            {
                "flag_code": "relative_strength_conflict",
                "severity": "medium",
                "message": "模型偏空，但近20日超额收益仍为正，弱势信号未完全确认。",
            }
        )

    if probability is not None and abs(probability - 0.5) < 0.05:
        flags.append(
            {
                "flag_code": "near_boundary",
                "severity": "medium",
                "message": "预测概率贴近 0.5，结论容易随单日波动翻转。",
            }
        )

    return _dedupe(flags)


def build_invalidation_conditions(
    top_contributors: list[dict[str, Any]],
    risk_flags: list[dict[str, Any]],
) -> list[str]:
    conditions: list[str] = []
    for contributor in top_contributors[:2]:
        feature_name = str(contributor.get("feature_name", ""))
        contribution = _to_float(contributor.get("contribution")) or 0.0
        conditions.append(_feature_invalidation_text(feature_name, contribution))

    for flag in risk_flags:
        if flag["flag_code"] == "high_volatility_20d":
            conditions.append("若近20日波动率继续上行，当前结论的可交易性会下降。")
        if flag["flag_code"] == "deep_drawdown_20d":
            conditions.append("若近20日最大回撤继续扩大，当前信号可能失效。")

    return _dedupe_text(conditions)[:3]


def _feature_invalidation_text(feature_name: str, contribution: float) -> str:
    if contribution >= 0:
        mapping = {
            "amount_change_1d": "若近1日成交额变化回落并失去放量支撑，现有判断会被削弱。",
            "daily_return_1d": "若近1日收益回落并失去短线支撑，现有判断会被削弱。",
            "return_5d": "若近5日收益回落并转负，现有判断会被削弱。",
            "return_20d": "若近20日收益持续下滑，现有判断会被削弱。",
            "excess_return_5d": "若近5日超额收益转负，现有判断会被削弱。",
            "excess_return_20d": "若近20日超额收益转负，现有判断会被削弱。",
            "style_strength_20d": "若近20日风格强弱回落，现有判断会被削弱。",
            "volatility_20d": "若近20日波动率继续抬升，现有判断会被削弱。",
            "max_drawdown_20d": "若近20日最大回撤继续扩大，现有判断会被削弱。",
            "momentum_5_minus_20": "若5日-20日动量差继续恶化，现有判断会被削弱。",
            "momentum_10_minus_20": "若10日-20日动量差继续恶化，现有判断会被削弱。",
        }
    else:
        mapping = {
            "amount_change_1d": "若近1日成交额变化重新走强，现有判断会被推翻。",
            "daily_return_1d": "若近1日收益快速修复，现有判断会被推翻。",
            "return_5d": "若近5日收益修复并转正，现有判断会被推翻。",
            "return_20d": "若近20日收益重新转强，现有判断会被推翻。",
            "excess_return_5d": "若近5日超额收益重新转正，现有判断会被推翻。",
            "excess_return_20d": "若近20日超额收益重新转正，现有判断会被推翻。",
            "style_strength_20d": "若近20日风格强弱重新走强，现有判断会被推翻。",
            "volatility_20d": "若近20日波动率显著回落，现有判断会被推翻。",
            "max_drawdown_20d": "若近20日最大回撤明显修复，现有判断会被推翻。",
            "momentum_5_minus_20": "若5日-20日动量差重新转强，现有判断会被推翻。",
            "momentum_10_minus_20": "若10日-20日动量差重新转强，现有判断会被推翻。",
        }
    return mapping.get(feature_name, f"若{feature_label(feature_name)}的当前贡献方向被扭转，现有判断会失效。")


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)


def _dedupe(flags: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for flag in flags:
        code = flag["flag_code"]
        if code in seen:
            continue
        seen.add(code)
        result.append(flag)
    return result


def _dedupe_text(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
