"""
增强版基金数据获取模块 - 基于 AKShare
提供更多维度：行业主题表现
"""
import akshare as ak
from typing import Dict, List
from datetime import datetime, timedelta


class EnhancedFundFetcher:
    """增强版基金数据获取器"""

    def __init__(self):
        pass

    def get_fund_spot(self, fund_code: str) -> Dict:
        """获取ETF实时行情"""
        try:
            df = ak.fund_etf_spot_em()
            fund_row = df[df["代码"] == fund_code]

            if fund_row.empty:
                return {"code": fund_code, "error": "未找到基金", "success": False}

            row = fund_row.iloc[0]
            return {
                "code": fund_code,
                "name": row.get("名称", fund_code),
                "price": row.get("最新价", "-"),
                "change": row.get("涨跌额", "-"),
                "change_pct": row.get("涨跌幅", "-"),
                "volume": row.get("成交量", "-"),
                "turnover": row.get("成交额", "-"),
                "success": True
            }
        except Exception as e:
            return {"code": fund_code, "error": str(e), "success": False}

    def get_fund_info_from_open(self, fund_code: str, fund_name: str) -> Dict:
        """从开放式基金列表获取（兼容原有方式）"""
        try:
            df = ak.fund_open_fund_daily_em()
            fund_row = df[df["基金代码"] == fund_code]

            if fund_row.empty:
                # 尝试用ETF实时接口
                return self.get_fund_spot(fund_code)

            row = fund_row.iloc[0]
            return {
                "code": fund_code,
                "name": fund_name,
                "nav": row.get("单位净值", "-"),
                "daily_change": row.get("日增长率", "-"),
                "success": True
            }
        except Exception as e:
            return {"code": fund_code, "name": fund_name, "error": str(e), "success": False}

    def get_sector_etfs(self) -> Dict[str, Dict]:
        """
        获取行业主题ETF表现
        使用预定义的代表性ETF
        """
        # 行业代表ETF
        sector_etfs = {
            "科技": ["515880", "159995", "512480"],
            "医药": ["512010", "159938", "512170"],
            "新能源": ["515030", "159806", "516160"],
            "消费": ["159928", "515650", "512690"],
            "金融": ["512800", "515290", "510230"],
            "跨境": ["513100", "513300", "513050"],
        }

        results = {}
        for sector, codes in sector_etfs.items():
            sector_funds = []
            for code in codes:
                try:
                    data = self.get_fund_spot(code)
                    if data.get("success"):
                        sector_funds.append(data)
                except:
                    continue

            if sector_funds:
                # 计算平均涨跌幅
                changes = []
                for f in sector_funds:
                    try:
                        chg = float(f.get("change_pct", 0) or 0)
                        changes.append(chg)
                    except:
                        continue

                if changes:
                    avg_change = sum(changes) / len(changes)
                    leader = max(sector_funds, key=lambda x: float(x.get("change_pct", 0) or 0))
                    results[sector] = {
                        "avg_change": round(avg_change, 2),
                        "leader": leader,
                        "count": len(sector_funds)
                    }

        return results

    def get_all_fund_data(self, config: Dict) -> Dict:
        """
        获取完整的基金数据（用于日报）
        """
        result = {
            "enabled": True,
            "watchlist": [],
            "sectors": {},
            "updated_at": datetime.now().strftime("%H:%M")
        }

        # 获取配置
        fund_config = config.get("finance", {}).get("funds", {})
        if isinstance(fund_config, list):
            # 旧格式兼容
            fund_config = {"watchlist": fund_config}

        watchlist = fund_config.get("watchlist", [])

        # 1. 获取关注基金
        for fund in watchlist:
            data = self.get_fund_info_from_open(fund["code"], fund["name"])
            if data.get("success"):
                result["watchlist"].append(data)

        # 2. 获取行业板块表现（如果启用）
        if fund_config.get("show_sectors", True):
            try:
                result["sectors"] = self.get_sector_etfs()
            except Exception as e:
                print(f"板块数据获取失败: {e}")

        return result
