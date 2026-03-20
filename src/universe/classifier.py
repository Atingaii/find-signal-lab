from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BenchmarkRule:
    family_code: str
    family_name: str
    include_keywords: tuple[str, ...]
    exclude_keywords: tuple[str, ...] = ()


BENCHMARK_RULES: tuple[BenchmarkRule, ...] = (
    BenchmarkRule("DIVIDEND_LOW_VOL", "红利低波", ("红利低波", "低波红利")),
    BenchmarkRule("CHINEXT50", "创业板50", ("创业板50",)),
    BenchmarkRule("CSIA500", "中证A500", ("中证A500", "A500")),
    BenchmarkRule("CSI1000", "中证1000", ("中证1000",)),
    BenchmarkRule("CSI500", "中证500", ("中证500",)),
    BenchmarkRule("CSI300", "沪深300", ("沪深300",)),
    BenchmarkRule("SSE50", "上证50", ("上证50",)),
    BenchmarkRule("STAR50", "科创50", ("科创50",)),
    BenchmarkRule("CHINEXT", "创业板指", ("创业板指", "创业板ETF", "创业板指数")),
    BenchmarkRule("DIVIDEND", "中证红利", ("中证红利", "红利ETF", "红利指数")),
)

GLOBAL_EXCLUDE_KEYWORDS: tuple[str, ...] = (
    "QDII",
    "港股",
    "标普",
    "纳斯达克",
    "商品",
    "黄金",
    "原油",
    "REIT",
    "联接",
)


def normalize_fund_code(value: object) -> str:
    text = str(value).strip()
    return text.zfill(6)


def normalize_fund_name(value: object) -> str:
    return str(value).strip().replace("（", "(").replace("）", ")")


def is_excluded_name(name: str) -> bool:
    return any(keyword in name for keyword in GLOBAL_EXCLUDE_KEYWORDS)


def classify_benchmark_family(name: str) -> tuple[str | None, str | None]:
    normalized_name = normalize_fund_name(name)
    if is_excluded_name(normalized_name):
        return None, None

    for rule in BENCHMARK_RULES:
        if all(keyword not in normalized_name for keyword in rule.include_keywords):
            continue
        if any(keyword in normalized_name for keyword in rule.exclude_keywords):
            continue
        return rule.family_code, rule.family_name
    return None, None


def share_class_priority(name: str) -> int:
    normalized_name = normalize_fund_name(name)
    if normalized_name.endswith("A"):
        return 0
    if normalized_name.endswith("C") or normalized_name.endswith("E") or normalized_name.endswith("Y"):
        return 2
    if normalized_name.endswith("B"):
        return 3
    return 1
