from __future__ import annotations

from typing import Any


def render_markdown(summary: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# 基金方向预测器日报 {summary['report_date']}")
    lines.append("")
    lines.append(f"- 报告模型: `{summary['model_name']}`")
    lines.append(f"- 报告日期: `{summary['report_date']}`")
    lines.append("- 说明: 第五阶段解释层仅整理第四阶段结构化预测结果，不重新训练模型。")
    lines.append("")

    for target in summary["targets"]:
        lines.append(f"## {target['target_label']}")
        lines.append("")
        lines.append("### Top 看多")
        lines.extend(_render_pick_list(target["top_long"]))
        lines.append("")
        lines.append("### Top 看空")
        lines.extend(_render_pick_list(target["top_short"]))
        lines.append("")
        lines.append("### 同类强弱")
        for row in target["family_strength"][:5]:
            probability = row["avg_prediction_probability"] * 100
            lines.append(
                f"- {row['benchmark_family']}: 平均概率 {probability:.1f}%"
            )
        lines.append("")
        lines.append("### 市场风格总结")
        lines.append(f"- {target['style_summary']}")
        lines.append("")
        lines.append("### 风险提示")
        if target["risk_digest"]:
            for risk in target["risk_digest"]:
                lines.append(f"- {risk['message']} (命中 {risk['count']} 次)")
        else:
            lines.append("- 当前未触发集中风险提示。")
        lines.append("")

    lines.append("## 模型与数据说明")
    lines.append("")
    lines.append("- 预测输入来源: `prediction_explanation_input_latest`")
    lines.append("- 解释输出来源: `explanation_result_latest`")
    lines.append("- 当前报告为 deterministic 模板化说明，保留无大模型 fallback。")
    return "\n".join(lines).strip() + "\n"


def _render_pick_list(picks: list[dict[str, Any]]) -> list[str]:
    if not picks:
        return ["- 暂无样本"]
    lines: list[str] = []
    for item in picks:
        probability = item["prediction_probability"] * 100
        lines.append(
            f"- {item['rank']}. {item['fund_name']} ({item['fund_code']}) | "
            f"{item['direction_conclusion']} | 概率 {probability:.1f}% | 置信度 {item['confidence_level']}"
        )
        lines.append(f"  摘要: {item['summary_text']}")
    return lines
