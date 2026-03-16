#!/usr/bin/env python3
"""
每日早报生成器主程序
"""
import json
import os
import sys
from datetime import datetime
from src.weather_fetcher import WeatherFetcher
from src.finance_fetcher import FinanceFetcher
from src.news_fetcher import NewsFetcher
from src.report_generator import ReportGenerator


def load_config(config_path: str = "config.json") -> dict:
    """加载配置文件"""
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_weekday() -> str:
    """获取中文星期"""
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    return weekdays[datetime.now().weekday()]


def main():
    print("=" * 50)
    print("🚀 开始生成每日早报")
    print("=" * 50)

    # 加载配置
    config = load_config()
    print("✅ 配置加载完成")

    # 初始化数据容器
    report_data = {
        "date": datetime.now().strftime("%Y年%m月%d日"),
        "weekday": get_weekday(),
        "weather": [],
        "indices": {"us": [], "hk": [], "cn": []},
        "funds": [],
        "news": [],
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # 1. 获取天气数据
    print("\n🌤️ 正在获取天气数据...")
    try:
        weather_fetcher = WeatherFetcher()
        cities = config.get("weather", {}).get("cities", [])
        report_data["weather"] = weather_fetcher.get_all_cities_weather(cities)
        success_count = sum(1 for w in report_data["weather"] if w.get("success"))
        print(f"✅ 天气数据获取完成 ({success_count}/{len(cities)})")
        # 打印详细错误信息
        for w in report_data["weather"]:
            if not w.get("success"):
                print(f"   ⚠️ {w['name']}: {w.get('error', '未知错误')}")
    except Exception as e:
        print(f"❌ 天气数据获取失败: {e}")

    # 2. 获取金融数据
    print("\n📈 正在获取金融数据...")
    try:
        finance_fetcher = FinanceFetcher()
        indices = config.get("finance", {}).get("indices", [])
        report_data["indices"] = finance_fetcher.get_all_indices(indices)

        funds = config.get("finance", {}).get("funds", [])
        report_data["funds"] = finance_fetcher.get_all_funds(funds)
        print("✅ 金融数据获取完成")
    except Exception as e:
        print(f"❌ 金融数据获取失败: {e}")

    # 3. 获取新闻资讯
    print("\n📰 正在获取热点资讯...")
    try:
        news_fetcher = NewsFetcher()
        max_news = config.get("news", {}).get("max_items", 5)
        report_data["news"] = news_fetcher.get_all_news(max_items=max_news)
        print(f"✅ 资讯获取完成 ({len(report_data['news'])}条)")
    except Exception as e:
        print(f"❌ 资讯获取失败: {e}")

    # 4. 生成日报
    print("\n📝 正在生成日报...")
    try:
        generator = ReportGenerator()
        html = generator.generate_html(report_data)

        # 保存到 docs 目录（GitHub Pages 源目录）
        output_path = "docs/index.html"
        generator.save_report(html, output_path)

        # 同时保存一份带日期的版本
        dated_path = f"docs/archive/{datetime.now().strftime('%Y%m%d')}.html"
        generator.save_report(html, dated_path)

        print("\n" + "=" * 50)
        print("✨ 日报生成完成!")
        print(f"📄 主页面: {output_path}")
        print(f"📄 归档: {dated_path}")
        print("=" * 50)
    except Exception as e:
        print(f"❌ 日报生成失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
