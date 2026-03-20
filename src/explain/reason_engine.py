from __future__ import annotations

import json
from typing import Any

import pandas as pd

from explain.risk_rules import build_invalidation_conditions, build_risk_flags
from explain.templates import (
    build_llm_surface_prompt,
    chinese_confidence,
    direction_conclusion,
    format_reason_text,
    parse_json,
    target_label,
)


def build_explanations(dataframe: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for row in dataframe.to_dict(orient="records"):
        records.append(_build_row(row))
    return pd.DataFrame(records)


def _build_row(row: dict[str, Any]) -> dict[str, Any]:
    probability = _to_float(row.get("prediction_probability"))
    contributors = parse_json(row.get("top_feature_contributors"), [])
    feature_snapshot = parse_json(row.get("feature_snapshot"), {})
    risk_snapshot = parse_json(row.get("risk_snapshot"), {})
    direction = direction_conclusion(probability)
    risk_flags = build_risk_flags(
        probability=probability,
        confidence_level=str(row.get("confidence_level")),
        feature_snapshot=feature_snapshot,
        risk_snapshot=risk_snapshot,
        prediction_label=_to_int(row.get("prediction_label")),
    )
    primary_reasons = _build_primary_reasons(
        contributors=contributors,
        feature_snapshot=feature_snapshot,
        target_name=str(row.get("target_name")),
    )
    secondary_reasons = _build_secondary_reasons(
        contributors=contributors,
        feature_snapshot=feature_snapshot,
        target_name=str(row.get("target_name")),
        primary_count=len(primary_reasons),
    )
    invalidation_conditions = build_invalidation_conditions(contributors, risk_flags)
    summary_text = _build_summary_text(
        fund_name=str(row.get("fund_name")),
        target_name=str(row.get("target_name")),
        direction=direction,
        probability=probability,
        confidence_level=str(row.get("confidence_level")),
        primary_reasons=primary_reasons,
        risk_flags=risk_flags,
    )

    llm_surface_payload = {
        "fund_code": row.get("fund_code"),
        "fund_name": row.get("fund_name"),
        "target_name": row.get("target_name"),
        "prediction_label": _to_int(row.get("prediction_label")),
        "prediction_probability": probability,
        "confidence_level": row.get("confidence_level"),
        "direction_conclusion": direction,
        "primary_reasons": primary_reasons,
        "secondary_reasons": secondary_reasons,
        "risk_flags": risk_flags,
        "invalidation_conditions": invalidation_conditions,
        "summary_text": summary_text,
        "report_date": row.get("prediction_date"),
    }

    return {
        "fund_code": row.get("fund_code"),
        "fund_name": row.get("fund_name"),
        "benchmark_family": row.get("benchmark_family"),
        "prediction_date": row.get("prediction_date"),
        "report_date": row.get("prediction_date"),
        "target_name": row.get("target_name"),
        "target_label": target_label(str(row.get("target_name"))),
        "prediction_label": _to_int(row.get("prediction_label")),
        "prediction_probability": probability,
        "confidence_level": row.get("confidence_level"),
        "direction_conclusion": direction,
        "model_name": row.get("model_name"),
        "model_version": row.get("model_version"),
        "primary_reasons": _json(primary_reasons),
        "secondary_reasons": _json(secondary_reasons),
        "risk_flags": _json(risk_flags),
        "invalidation_conditions": _json(invalidation_conditions),
        "summary_text": summary_text,
        "top_feature_contributors": _json(contributors),
        "feature_snapshot": _json(feature_snapshot),
        "risk_snapshot": _json(risk_snapshot),
        "source_payload": row.get("explanation_input_payload"),
        "llm_surface_payload": _json(llm_surface_payload),
        "llm_surface_prompt": build_llm_surface_prompt(llm_surface_payload),
    }


def _build_primary_reasons(
    contributors: list[dict[str, Any]],
    feature_snapshot: dict[str, Any],
    target_name: str,
) -> list[dict[str, Any]]:
    reasons: list[dict[str, Any]] = []
    for contributor in contributors[:2]:
        feature_name = str(contributor.get("feature_name"))
        contribution = _to_float(contributor.get("contribution")) or 0.0
        feature_value = _to_float(feature_snapshot.get(feature_name))
        reasons.append(
            {
                "feature_name": feature_name,
                "contribution": contribution,
                "feature_value": feature_value,
                "text": format_reason_text(feature_name, contribution, feature_value, target_name),
            }
        )
    return reasons


def _build_secondary_reasons(
    contributors: list[dict[str, Any]],
    feature_snapshot: dict[str, Any],
    target_name: str,
    primary_count: int,
) -> list[dict[str, Any]]:
    reasons: list[dict[str, Any]] = []
    for contributor in contributors[primary_count:3]:
        feature_name = str(contributor.get("feature_name"))
        contribution = _to_float(contributor.get("contribution")) or 0.0
        feature_value = _to_float(feature_snapshot.get(feature_name))
        reasons.append(
            {
                "feature_name": feature_name,
                "contribution": contribution,
                "feature_value": feature_value,
                "text": format_reason_text(feature_name, contribution, feature_value, target_name),
            }
        )

    if not reasons:
        for feature_name in ("return_20d", "excess_return_20d"):
            if feature_name in feature_snapshot:
                feature_value = _to_float(feature_snapshot.get(feature_name))
                reasons.append(
                    {
                        "feature_name": feature_name,
                        "contribution": None,
                        "feature_value": feature_value,
                        "text": format_reason_text(feature_name, 0.0, feature_value, target_name),
                    }
                )
                break
    return reasons[:2]


def _build_summary_text(
    fund_name: str,
    target_name: str,
    direction: str,
    probability: float | None,
    confidence_level: str,
    primary_reasons: list[dict[str, Any]],
    risk_flags: list[dict[str, Any]],
) -> str:
    probability_text = "缺失" if probability is None else f"{probability * 100:.1f}%"
    reason_text = " ".join(reason["text"] for reason in primary_reasons[:2]) if primary_reasons else "暂无主要驱动因子。"
    risk_text = risk_flags[0]["message"] if risk_flags else "当前未触发额外高优先级风险规则。"
    return (
        f"{fund_name}在{target_label(target_name)}上给出{direction}结论，"
        f"预测概率 {probability_text}，置信度{chinese_confidence(confidence_level)}。"
        f"主要依据：{reason_text} 风险提示：{risk_text}"
    )


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)


def _to_int(value: Any) -> int | None:
    if value is None:
        return None
    return int(value)
