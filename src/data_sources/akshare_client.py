from __future__ import annotations

import requests
import pandas as pd
import akshare as ak


requests.sessions.Session.trust_env = False


class AkShareClient:
    """Thin wrapper around the small AkShare surface used in stage two."""

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.trust_env = False
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/134.0.0.0 Safari/537.36"
                )
            }
        )

    def fetch_fund_master(self) -> pd.DataFrame:
        return ak.fund_name_em().copy()

    def fetch_etf_snapshot(self, trade_date: str = "") -> pd.DataFrame:
        return ak.fund_etf_category_ths(symbol="ETF", date=trade_date).copy()

    def fetch_lof_snapshot(self, trade_date: str = "") -> pd.DataFrame:
        return ak.fund_etf_category_ths(symbol="LOF", date=trade_date).copy()

    def fetch_passive_index_funds(self) -> pd.DataFrame:
        return ak.fund_info_index_em(symbol="全部", indicator="被动指数型").copy()

    def fetch_etf_history(
        self,
        fund_code: str,
        start_date: str,
        end_date: str,
        adjust: str = "qfq",
    ) -> pd.DataFrame:
        try:
            return self._fetch_etf_history_eastmoney(
                fund_code=fund_code,
                start_date=start_date,
                end_date=end_date,
                adjust=adjust,
            )
        except requests.RequestException:
            return self._fetch_etf_history_sina(
                fund_code=fund_code,
                start_date=start_date,
                end_date=end_date,
            )

    def _fetch_etf_history_eastmoney(
        self,
        fund_code: str,
        start_date: str,
        end_date: str,
        adjust: str = "qfq",
    ) -> pd.DataFrame:
        adjust_dict = {"qfq": "1", "hfq": "2", "": "0"}
        url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
        params = {
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f116",
            "ut": "7eea3edcaed734bea9cbfc24409ed989",
            "klt": "101",
            "fqt": adjust_dict[adjust],
            "beg": start_date,
            "end": end_date,
            "secid": f"{self._market_id(fund_code)}.{fund_code}",
        }
        response = self.session.get(url, params=params, timeout=20)
        response.raise_for_status()
        data_json = response.json()
        if not (data_json.get("data") and data_json["data"].get("klines")):
            return pd.DataFrame()

        temp_df = pd.DataFrame([item.split(",") for item in data_json["data"]["klines"]])
        temp_df.columns = [
            "日期",
            "开盘",
            "收盘",
            "最高",
            "最低",
            "成交量",
            "成交额",
            "振幅",
            "涨跌幅",
            "涨跌额",
            "换手率",
        ]
        for column in ["开盘", "收盘", "最高", "最低", "成交量", "成交额", "振幅", "涨跌幅", "涨跌额", "换手率"]:
            temp_df[column] = pd.to_numeric(temp_df[column], errors="coerce")
        temp_df.attrs["source"] = "eastmoney_push2his"
        return temp_df

    def _fetch_etf_history_sina(
        self,
        fund_code: str,
        start_date: str,
        end_date: str,
    ) -> pd.DataFrame:
        symbol = self._sina_symbol(fund_code)
        temp_df = ak.fund_etf_hist_sina(symbol=symbol).copy()
        if temp_df.empty:
            return temp_df

        temp_df["date"] = pd.to_datetime(temp_df["date"], errors="coerce")
        start_ts = pd.to_datetime(start_date)
        end_ts = pd.to_datetime(end_date)
        temp_df = temp_df.loc[temp_df["date"].between(start_ts, end_ts)].copy()
        if "prevclose" not in temp_df.columns:
            temp_df["prevclose"] = temp_df["close"].shift(1)

        temp_df["pct_chg"] = (
            (temp_df["close"] - temp_df["prevclose"]) / temp_df["prevclose"] * 100
        )
        temp_df["chg"] = temp_df["close"] - temp_df["prevclose"]
        temp_df["amplitude"] = (
            (temp_df["high"] - temp_df["low"]) / temp_df["prevclose"] * 100
        )
        temp_df["turnover"] = pd.NA
        temp_df["date"] = temp_df["date"].dt.date

        temp_df = temp_df.rename(
            columns={
                "date": "日期",
                "open": "开盘",
                "close": "收盘",
                "high": "最高",
                "low": "最低",
                "volume": "成交量",
                "amount": "成交额",
                "amplitude": "振幅",
                "pct_chg": "涨跌幅",
                "chg": "涨跌额",
                "turnover": "换手率",
            }
        )[
            ["日期", "开盘", "收盘", "最高", "最低", "成交量", "成交额", "振幅", "涨跌幅", "涨跌额", "换手率"]
        ]
        temp_df.attrs["source"] = "sina_finance_etf_klc2"
        return temp_df

    def fetch_macro_pmi(self) -> pd.DataFrame:
        return ak.macro_china_pmi().copy()

    def fetch_macro_lpr(self) -> pd.DataFrame:
        return ak.macro_china_lpr().copy()

    def fetch_sse_summary(self) -> pd.DataFrame:
        return ak.stock_sse_summary().copy()

    def fetch_szse_summary(self, trade_date: str) -> pd.DataFrame:
        return ak.stock_szse_summary(date=trade_date).copy()

    @staticmethod
    def _market_id(fund_code: str) -> int:
        return 1 if fund_code.startswith(("5", "6", "9")) else 0

    @staticmethod
    def _sina_symbol(fund_code: str) -> str:
        prefix = "sh" if fund_code.startswith(("5", "6", "9")) else "sz"
        return f"{prefix}{fund_code}"
