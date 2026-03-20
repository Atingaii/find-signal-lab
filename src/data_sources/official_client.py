from __future__ import annotations

import json
import re
from dataclasses import dataclass

import pandas as pd
import requests


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/134.0.0.0 Safari/537.36"
)


@dataclass(frozen=True)
class PageSnapshot:
    url: str
    text: str


class OfficialClient:
    """Official and public-web supplement client used to fill AkShare gaps."""

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.trust_env = False
        self.session.headers.update({"User-Agent": USER_AGENT})

    def fetch_sse_fundlist_page(self) -> PageSnapshot:
        url = "https://etf.sse.com.cn/fundlist/"
        response = self.session.get(url, timeout=20)
        response.raise_for_status()
        return PageSnapshot(url=url, text=response.text)

    def fetch_szse_lof_reference_page(self) -> PageSnapshot:
        url = "https://www.szse.cn/www/investor/knowledge/fund/lof/t20161123_538832.html"
        response = self.session.get(url, timeout=20)
        response.raise_for_status()
        return PageSnapshot(url=url, text=response.text)

    def fetch_pingzhongdata_text(self, fund_code: str) -> str:
        url = f"http://fund.eastmoney.com/pingzhongdata/{fund_code}.js"
        response = self.session.get(url, timeout=20)
        response.raise_for_status()
        return response.text

    def fetch_fund_nav_history(self, fund_code: str) -> tuple[dict[str, str], pd.DataFrame]:
        text = self.fetch_pingzhongdata_text(fund_code)
        meta = {
            "fund_code": fund_code,
            "fund_name": self._extract_string(text, "fS_name"),
            "source_url": f"http://fund.eastmoney.com/pingzhongdata/{fund_code}.js",
        }

        unit_nav = pd.DataFrame(self._extract_json(text, "Data_netWorthTrend"))
        accum_nav = pd.DataFrame(self._extract_json(text, "Data_ACWorthTrend"), columns=["x", "累计净值"])

        if unit_nav.empty:
            return meta, pd.DataFrame(
                columns=["净值日期", "单位净值", "累计净值", "日增长率"]
            )

        unit_nav["净值日期"] = pd.to_datetime(unit_nav["x"], unit="ms", utc=True).dt.tz_convert(
            "Asia/Shanghai"
        )
        unit_nav["净值日期"] = unit_nav["净值日期"].dt.date
        unit_nav = unit_nav.rename(columns={"y": "单位净值", "equityReturn": "日增长率"})
        unit_nav = unit_nav[["净值日期", "单位净值", "日增长率"]]

        if not accum_nav.empty:
            accum_nav["净值日期"] = pd.to_datetime(
                accum_nav["x"], unit="ms", utc=True
            ).dt.tz_convert("Asia/Shanghai")
            accum_nav["净值日期"] = accum_nav["净值日期"].dt.date
            accum_nav = accum_nav[["净值日期", "累计净值"]]

        merged = unit_nav.merge(accum_nav, on="净值日期", how="left")
        merged["单位净值"] = pd.to_numeric(merged["单位净值"], errors="coerce")
        merged["累计净值"] = pd.to_numeric(merged["累计净值"], errors="coerce")
        merged["日增长率"] = pd.to_numeric(merged["日增长率"], errors="coerce")
        merged = merged.sort_values("净值日期").reset_index(drop=True)
        return meta, merged

    @staticmethod
    def _extract_string(text: str, variable: str) -> str:
        match = re.search(rf'var\s+{variable}\s*=\s*"([^"]*)";', text)
        return match.group(1) if match else ""

    @staticmethod
    def _extract_json(text: str, variable: str) -> list[object]:
        match = re.search(rf"var\s+{variable}\s*=\s*(.+?);", text, re.S)
        if not match:
            return []
        return json.loads(match.group(1))
