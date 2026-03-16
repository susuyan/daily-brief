"""
金融数据获取模块
"""
import yfinance as yf
import akshare as ak
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class FinanceFetcher:
    """金融数据获取器"""

    def __init__(self):
        self.cn_market_open = self._check_cn_market_open()

    def _check_cn_market_open(self) -> bool:
        """检查A股是否开盘（简化判断）"""
        now = datetime.now()
        weekday = now.weekday()
        if weekday >= 5:  # 周末
            return False
        return True

    def get_us_index(self, symbol: str, name: str) -> Dict:
        """获取美股指数"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")

            if len(hist) < 2:
                return {"name": name, "error": "无数据", "success": False}

            latest = hist.iloc[-1]
            prev = hist.iloc[-2]

            current = latest["Close"]
            prev_close = prev["Close"]
            change = current - prev_close
            change_pct = (change / prev_close) * 100

            return {
                "name": name,
                "symbol": symbol,
                "price": round(current, 2),
                "change": round(change, 2),
                "change_pct": round(change_pct, 2),
                "success": True
            }
        except Exception as e:
            return {"name": name, "error": str(e), "success": False}

    def get_hk_index(self, symbol: str, name: str) -> Dict:
        """获取港股指数"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")

            if len(hist) < 1:
                return {"name": name, "error": "无数据", "success": False}

            latest = hist.iloc[-1]
            prev = hist.iloc[-2] if len(hist) >= 2 else latest

            current = latest["Close"]
            prev_close = prev["Close"]
            change = current - prev_close
            change_pct = (change / prev_close) * 100 if prev_close > 0 else 0

            return {
                "name": name,
                "symbol": symbol,
                "price": round(current, 2),
                "change": round(change, 2),
                "change_pct": round(change_pct, 2),
                "success": True
            }
        except Exception as e:
            return {"name": name, "error": str(e), "success": False}

    def get_cn_index(self, symbol: str, name: str) -> Dict:
        """获取A股指数"""
        try:
            # 使用 akshare 获取中证500等指数
            if symbol == "000905.SS":
                # 中证500
                df = ak.index_zh_a_hist(symbol="000905", period="daily", start_date=(datetime.now() - timedelta(days=7)).strftime("%Y%m%d"), end_date=datetime.now().strftime("%Y%m%d"))
            elif symbol == "000001.SS":
                # 上证指数
                df = ak.index_zh_a_hist(symbol="000001", period="daily", start_date=(datetime.now() - timedelta(days=7)).strftime("%Y%m%d"), end_date=datetime.now().strftime("%Y%m%d"))
            else:
                # 其他指数使用 yfinance
                return self.get_us_index(symbol, name)

            if df is None or len(df) < 1:
                return {"name": name, "error": "无数据", "success": False}

            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) >= 2 else latest

            current = float(latest["收盘"])
            prev_close = float(prev["收盘"])
            change = current - prev_close
            change_pct = (change / prev_close) * 100

            return {
                "name": name,
                "symbol": symbol,
                "price": round(current, 2),
                "change": round(change, 2),
                "change_pct": round(change_pct, 2),
                "success": True
            }
        except Exception as e:
            # 降级到 yfinance
            return self.get_us_index(symbol, name)

    def get_fund_info(self, fund_code: str, fund_name: str) -> Dict:
        """获取基金信息"""
        try:
            # 使用 akshare 获取基金净值
            df = ak.fund_open_fund_daily_em()
            fund_row = df[df["基金代码"] == fund_code]

            if fund_row.empty:
                return {"name": fund_name, "code": fund_code, "error": "未找到基金", "success": False}

            row = fund_row.iloc[0]
            nav = row.get("单位净值", "-")
            daily_change = row.get("日增长率", "-")

            return {
                "name": fund_name,
                "code": fund_code,
                "nav": nav,
                "daily_change": daily_change,
                "success": True
            }
        except Exception as e:
            return {"name": fund_name, "code": fund_code, "error": str(e), "success": False}

    def get_all_indices(self, indices: List[Dict]) -> Dict[str, List[Dict]]:
        """获取所有指数数据"""
        results = {
            "us": [],
            "hk": [],
            "cn": []
        }

        for idx in indices:
            market = idx.get("market", "us")
            symbol = idx["symbol"]
            name = idx["name"]

            if market == "us":
                data = self.get_us_index(symbol, name)
                results["us"].append(data)
            elif market == "hk":
                data = self.get_hk_index(symbol, name)
                results["hk"].append(data)
            elif market == "cn":
                data = self.get_cn_index(symbol, name)
                results["cn"].append(data)

        return results

    def get_all_funds(self, funds: List[Dict]) -> List[Dict]:
        """获取所有基金数据"""
        results = []
        for fund in funds:
            data = self.get_fund_info(fund["code"], fund["name"])
            results.append(data)
        return results
