from __future__ import annotations

import json
from typing import Any

import pandas as pd

from explain.templates import feature_label


DEFAULT_REPORT_MODEL = "logistic_regression"


def build_daily_summary(
    explanation_df: pd.DataFrame,
    model_name: str = DEFAULT_REPORT_MODEL,
    top_k: int = 5,
) -> dict[str, Any]:
    filtered = explanation_df.loc[explanation_df["model_name"] == model_name].copy()
    if filtered.empty:
        filtered = explanation_df.copy()

    report_date = filtered["report_date"].iloc[0] if not filtered.empty else None
    targets: list[dict[str, Any]] = []
    top_pick_rows: list[dict[str, Any]] = []
    family_rows: list[dict[str, Any]] = []
    risk_rows: list[dict[str, Any]] = []

    for target_name, target_frame in filtered.groupby("target_name"):
        target_frame = target_frame.sort_values("prediction_probability", ascending=False).reset_index(drop=True)
        target_label = target_frame["target_label"].iloc[0]
        top_long = _pick_records(target_frame.head(top_k), "top_long")
        top_short = _pick_records(target_frame.sort_values("prediction_probability").head(top_k), "top_short")
        family_strength = _family_strength(target_frame, target_name, model_name)
        target_risks = _target_risk_digest(pd.concat([target_frame.head(top_k), target_frame.sort_values("prediction_probability").head(top_k)]))

        targets.append(
            {
                "target_name": target_name,
                "target_label": target_label,
                "top_long": top_long,
                "top_short": top_short,
                "family_strength": family_strength,
                "style_summary": _style_summary(top_long, family_strength),
                "risk_digest": target_risks,
            }
        )
        top_pick_rows.extend(_flatten_picks(report_date, target_name, model_name, top_long))
        top_pick_rows.extend(_flatten_picks(report_date, target_name, model_name, top_short))
        family_rows.extend([{**row, "report_date": report_date} for row in family_strength])
        risk_rows.extend([{**row, "target_name": target_name, "model_name": model_name, "report_date": report_date} for row in target_risks])

    return {
        "report_date": report_date,
        "model_name": model_name,
        "targets": targets,
        "top_pick_rows": top_pick_rows,
        "family_rows": family_rows,
        "risk_rows": risk_rows,
    }


def _pick_records(frame: pd.DataFrame, section_name: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for rank, row in enumerate(frame.to_dict(orient="records"), start=1):
        records.append(
            {
                "section_name": section_name,
                "rank": rank,
                "fund_code": row["fund_code"],
                "fund_name": row["fund_name"],
                "benchmark_family": row["benchmark_family"],
                "prediction_probability": float(row["prediction_probability"]),
                "direction_conclusion": row["direction_conclusion"],
                "confidence_level": row["confidence_level"],
                "summary_text": row["summary_text"],
                "risk_flags": json.loads(row["risk_flags"]),
                "primary_reasons": json.loads(row["primary_reasons"]),
            }
        )
    return records


def _family_strength(frame: pd.DataFrame, target_name: str, model_name: str) -> list[dict[str, Any]]:
    grouped = (
        frame.groupby("benchmark_family", as_index=False)["prediction_probability"]
        .mean()
        .sort_values("prediction_probability", ascending=False)
        .reset_index(drop=True)
    )
    rows: list[dict[str, Any]] = []
    for rank, row in enumerate(grouped.to_dict(orient="records"), start=1):
        rows.append(
            {
                "target_name": target_name,
                "model_name": model_name,
                "benchmark_family": row["benchmark_family"],
                "rank": rank,
                "avg_prediction_probability": float(row["prediction_probability"]),
            }
        )
    return rows


def _style_summary(top_long: list[dict[str, Any]], family_strength: list[dict[str, Any]]) -> str:
    top_families = [row["benchmark_family"] for row in family_strength[:3]]
    feature_counter: dict[str, int] = {}
    for row in top_long[:5]:
        for reason in row["primary_reasons"][:2]:
            feature = feature_label(reason["feature_name"])
            feature_counter[feature] = feature_counter.get(feature, 0) + 1
    dominant_features = sorted(feature_counter.items(), key=lambda item: (-item[1], item[0]))[:2]
    family_text = "、".join(top_families) if top_families else "暂无明显集中风格"
    if dominant_features:
        feature_text = "、".join(name for name, _ in dominant_features)
        return f"当前强势家族主要集中在 {family_text}，高频驱动集中在 {feature_text}。"
    return f"当前强势家族主要集中在 {family_text}。"


def _target_risk_digest(frame: pd.DataFrame) -> list[dict[str, Any]]:
    counter: dict[tuple[str, str], int] = {}
    message_map: dict[str, str] = {}
    for risk_payload in frame["risk_flags"]:
        for flag in json.loads(risk_payload):
            key = (flag["flag_code"], flag["severity"])
            counter[key] = counter.get(key, 0) + 1
            message_map[flag["flag_code"]] = flag["message"]
    rows = [
        {
            "flag_code": key[0],
            "severity": key[1],
            "count": count,
            "message": message_map[key[0]],
        }
        for key, count in counter.items()
    ]
    rows.sort(key=lambda item: (-item["count"], item["flag_code"]))
    return rows[:5]


def _flatten_picks(report_date: str | None, target_name: str, model_name: str, picks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in picks:
        rows.append(
            {
                "report_date": report_date,
                "target_name": target_name,
                "model_name": model_name,
                **{key: value for key, value in item.items() if key not in {"risk_flags", "primary_reasons"}},
                "risk_flags": json.dumps(item["risk_flags"], ensure_ascii=False),
                "primary_reasons": json.dumps(item["primary_reasons"], ensure_ascii=False),
            }
        )
    return rows
