"""
日报生成器
"""
import json
import os
from datetime import datetime
from typing import Dict, List
from jinja2 import Template


class ReportGenerator:
    """日报生成器"""

    def __init__(self, template_dir: str = None):
        self.template_dir = template_dir or os.path.join(os.path.dirname(__file__), "templates")

    def get_weather_icon(self, weather: str) -> str:
        """根据天气返回emoji图标"""
        icon_map = {
            "晴": "☀️",
            "多云": "⛅",
            "阴": "☁️",
            "小雨": "🌧️",
            "中雨": "🌧️",
            "大雨": "⛈️",
            "雪": "❄️",
            "雾": "🌫️",
            "霾": "😷",
        }
        for key, icon in icon_map.items():
            if key in weather:
                return icon
        return "🌤️"

    def get_aqi_color(self, aqi: str) -> str:
        """根据AQI返回颜色等级"""
        try:
            aqi_val = int(aqi)
            if aqi_val <= 50:
                return "🟢"
            elif aqi_val <= 100:
                return "🟡"
            elif aqi_val <= 150:
                return "🟠"
            else:
                return "🔴"
        except:
            return "⚪"

    def get_uv_icon(self, uv_category: str) -> str:
        """根据紫外线返回图标"""
        if "最弱" in uv_category or "弱" in uv_category:
            return "🟢"
        elif "中等" in uv_category:
            return "🟡"
        else:
            return "🔴"

    def format_number(self, num, decimal: int = 2) -> str:
        """格式化数字"""
        if num is None or num == "-":
            return "-"
        try:
            return f"{float(num):.{decimal}f}"
        except:
            return str(num)

    def generate_html(self, data: Dict) -> str:
        """生成HTML日报"""
        template_str = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>每日早报 - {{ date }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px 0;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 0 15px;
        }

        .header {
            text-align: center;
            color: white;
            padding: 30px 0;
        }

        .header h1 {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 8px;
        }

        .header .date {
            font-size: 14px;
            opacity: 0.9;
        }

        .card {
            background: white;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }

        .card-title {
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .card-title .icon {
            font-size: 22px;
        }

        /* 天气样式 */
        .weather-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
        }

        .weather-item {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            padding: 15px;
            color: white;
        }

        .weather-city {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 8px;
        }

        .weather-main {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        }

        .weather-icon {
            font-size: 32px;
        }

        .weather-temp {
            font-size: 24px;
            font-weight: 700;
        }

        .weather-desc {
            font-size: 14px;
            opacity: 0.9;
        }

        .weather-details {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 8px;
            font-size: 12px;
            opacity: 0.9;
        }

        .weather-detail {
            display: flex;
            align-items: center;
            gap: 4px;
        }

        /* 表格样式 */
        .data-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }

        .data-table th {
            background: #f8f9fa;
            padding: 12px 8px;
            text-align: left;
            font-weight: 600;
            color: #666;
            border-bottom: 2px solid #e9ecef;
        }

        .data-table td {
            padding: 12px 8px;
            border-bottom: 1px solid #e9ecef;
        }

        .data-table tr:last-child td {
            border-bottom: none;
        }

        .number {
            font-family: "SF Mono", Monaco, monospace;
            font-weight: 600;
        }

        .up {
            color: #e74c3c;
        }

        .down {
            color: #27ae60;
        }

        .neutral {
            color: #95a5a6;
        }

        /* 新闻样式 */
        .news-list {
            list-style: none;
        }

        .news-item {
            padding: 12px 0;
            border-bottom: 1px solid #e9ecef;
            display: flex;
            gap: 12px;
        }

        .news-item:last-child {
            border-bottom: none;
        }

        .news-time {
            font-size: 12px;
            color: #999;
            white-space: nowrap;
            min-width: 50px;
        }

        .news-content {
            flex: 1;
        }

        .news-title {
            font-size: 14px;
            color: #333;
            line-height: 1.5;
        }

        .news-source {
            font-size: 12px;
            color: #999;
            margin-top: 4px;
        }

        /* 备注 */
        .footer-note {
            text-align: center;
            color: rgba(255,255,255,0.7);
            font-size: 12px;
            padding: 20px 0;
        }

        /* AI 洞察样式 */
        .ai-insight {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .ai-insight .card-title {
            color: white;
        }

        .insight-highlight {
            background: rgba(255,255,255,0.15);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 12px;
            font-size: 14px;
            line-height: 1.5;
        }

        .insight-section {
            margin-bottom: 10px;
            font-size: 13px;
            line-height: 1.5;
        }

        .insight-section:last-child {
            margin-bottom: 0;
        }

        .insight-label {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 2px 8px;
            border-radius: 4px;
            margin-right: 8px;
            font-weight: 500;
        }

        .insight-text {
            opacity: 0.95;
        }

        /* AI 新闻摘要 */
        .news-ai-summary {
            font-size: 12px;
            color: #667eea;
            margin-top: 4px;
            padding: 4px 8px;
            background: #f0f3ff;
            border-radius: 4px;
            line-height: 1.4;
        }

        /* 板块网格 */
        .sector-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 10px;
        }

        .sector-item {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 12px;
            text-align: center;
            border-left: 3px solid #ddd;
        }

        .sector-item.up {
            background: #fff5f5;
            border-left-color: #e74c3c;
        }

        .sector-item.down {
            background: #f0fff4;
            border-left-color: #27ae60;
        }

        .sector-name {
            font-size: 13px;
            font-weight: 600;
            color: #333;
            margin-bottom: 4px;
        }

        .sector-change {
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 4px;
        }

        .sector-item.up .sector-change {
            color: #e74c3c;
        }

        .sector-item.down .sector-change {
            color: #27ae60;
        }

        .sector-leader {
            font-size: 11px;
            color: #999;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        /* 响应式 */
        @media (max-width: 480px) {
            .header h1 {
                font-size: 24px;
            }

            .card {
                padding: 15px;
            }

            .weather-grid {
                grid-template-columns: 1fr;
            }

            .data-table {
                font-size: 12px;
            }

            .data-table th,
            .data-table td {
                padding: 10px 6px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 每日早报</h1>
            <div class="date">{{ date }} {{ weekday }}</div>
        </div>

        <!-- 天气模块 -->
        <div class="card">
            <div class="card-title">
                <span class="icon">🌤️</span>
                <span>重点城市天气</span>
            </div>
            <div class="weather-grid">
                {% for city in weather %}
                {% if city.success %}
                <div class="weather-item">
                    <div class="weather-city">{{ city.name }}</div>
                    <div class="weather-main">
                        <span class="weather-icon">{{ city.weather_icon }}</span>
                        <span class="weather-temp">{{ city.current.temp }}°</span>
                    </div>
                    <div class="weather-desc">{{ city.current.weather }} | {{ city.forecast.temp_min }}°~{{ city.forecast.temp_max }}°</div>
                    <div class="weather-details">
                        <div class="weather-detail">💧 湿度 {{ city.current.humidity }}%</div>
                        <div class="weather-detail">{{ city.aqi_icon }} 空气 {{ city.air.category }}</div>
                        <div class="weather-detail">☀️ 紫外线 {{ city.uv.category }}</div>
                        <div class="weather-detail">🌬️ {{ city.current.wind_dir }}{{ city.current.wind_scale }}级</div>
                    </div>
                </div>
                {% endif %}
                {% endfor %}
            </div>
        </div>

        <!-- 美股 -->
        <div class="card">
            <div class="card-title">
                <span class="icon">🇺🇸</span>
                <span>美股市场（前一交易日）</span>
            </div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>指数</th>
                        <th style="text-align:right">最新价</th>
                        <th style="text-align:right">涨跌</th>
                        <th style="text-align:right">涨跌幅</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in indices.us %}
                    {% if item.success %}
                    <tr>
                        <td>{{ item.name }}</td>
                        <td class="number" style="text-align:right">{{ "%.2f"|format(item.price) }}</td>
                        <td class="number {{ 'up' if item.change > 0 else 'down' if item.change < 0 else 'neutral' }}" style="text-align:right">
                            {{ "+%.2f"|format(item.change) if item.change > 0 else "%.2f"|format(item.change) }}
                        </td>
                        <td class="number {{ 'up' if item.change_pct > 0 else 'down' if item.change_pct < 0 else 'neutral' }}" style="text-align:right">
                            {{ "+%.2f%%"|format(item.change_pct) if item.change_pct > 0 else "%.2f%%"|format(item.change_pct) }}
                        </td>
                    </tr>
                    {% endif %}
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <!-- 亚太市场 -->
        <div class="card">
            <div class="card-title">
                <span class="icon">🌏</span>
                <span>亚太市场</span>
            </div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>指数</th>
                        <th style="text-align:right">最新价</th>
                        <th style="text-align:right">涨跌</th>
                        <th style="text-align:right">涨跌幅</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in indices.hk %}
                    {% if item.success %}
                    <tr>
                        <td>{{ item.name }}</td>
                        <td class="number" style="text-align:right">{{ "%.2f"|format(item.price) }}</td>
                        <td class="number {{ 'up' if item.change > 0 else 'down' if item.change < 0 else 'neutral' }}" style="text-align:right">
                            {{ "+%.2f"|format(item.change) if item.change > 0 else "%.2f"|format(item.change) }}
                        </td>
                        <td class="number {{ 'up' if item.change_pct > 0 else 'down' if item.change_pct < 0 else 'neutral' }}" style="text-align:right">
                            {{ "+%.2f%%"|format(item.change_pct) if item.change_pct > 0 else "%.2f%%"|format(item.change_pct) }}
                        </td>
                    </tr>
                    {% endif %}
                    {% endfor %}
                    {% for item in indices.cn %}
                    {% if item.success %}
                    <tr>
                        <td>{{ item.name }}</td>
                        <td class="number" style="text-align:right">{{ "%.2f"|format(item.price) }}</td>
                        <td class="number {{ 'up' if item.change > 0 else 'down' if item.change < 0 else 'neutral' }}" style="text-align:right">
                            {{ "+%.2f"|format(item.change) if item.change > 0 else "%.2f"|format(item.change) }}
                        </td>
                        <td class="number {{ 'up' if item.change_pct > 0 else 'down' if item.change_pct < 0 else 'neutral' }}" style="text-align:right">
                            {{ "+%.2f%%"|format(item.change_pct) if item.change_pct > 0 else "%.2f%%"|format(item.change_pct) }}
                        </td>
                    </tr>
                    {% endif %}
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <!-- 关注基金 -->
        {% if funds.enabled != False %}
        <div class="card">
            <div class="card-title">
                <span class="icon">📈</span>
                <span>我的关注</span>
            </div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>基金名称</th>
                        <th style="text-align:right">价格</th>
                        <th style="text-align:right">涨跌</th>
                    </tr>
                </thead>
                <tbody>
                    {% for fund in funds.watchlist %}
                    {% if fund.success %}
                    <tr>
                        <td>{{ fund.name }}<br><small style="color:#999">{{ fund.code }}</small></td>
                        <td class="number" style="text-align:right">{{ fund.price }}</td>
                        <td class="number {{ 'up' if fund.change_pct > 0 else 'down' if fund.change_pct < 0 else 'neutral' }}" style="text-align:right">
                            {{ "+%.2f%%"|format(fund.change_pct) if fund.change_pct > 0 else "%.2f%%"|format(fund.change_pct) }}
                        </td>
                    </tr>
                    {% endif %}
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <!-- 热门ETF涨幅榜 -->
        {% if funds.hot_etfs %}
        <div class="card">
            <div class="card-title">
                <span class="icon">🔥</span>
                <span>今日热门ETF</span>
            </div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>基金</th>
                        <th style="text-align:right">涨幅</th>
                    </tr>
                </thead>
                <tbody>
                    {% for fund in funds.hot_etfs %}
                    {% if fund.success %}
                    <tr>
                        <td>{{ fund.name }}<br><small style="color:#999">{{ fund.code }}</small></td>
                        <td class="number {{ 'up' if fund.daily_change > 0 else 'down' }}" style="text-align:right">
                            {{ "+%.2f%%"|format(fund.daily_change) if fund.daily_change > 0 else "%.2f%%"|format(fund.daily_change) }}
                        </td>
                    </tr>
                    {% endif %}
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}

        <!-- 行业板块表现 -->
        {% if funds.sectors %}
        <div class="card">
            <div class="card-title">
                <span class="icon">🏗️</span>
                <span>板块表现</span>
            </div>
            <div class="sector-grid">
                {% for sector_name, sector_data in funds.sectors.items() %}
                <div class="sector-item {{ 'up' if sector_data.avg_change > 0 else 'down' }}">
                    <div class="sector-name">{{ sector_name }}</div>
                    <div class="sector-change">{{ "+%.2f%%"|format(sector_data.avg_change) if sector_data.avg_change > 0 else "%.2f%%"|format(sector_data.avg_change) }}</div>
                    <div class="sector-leader">{{ sector_data.leader.name }}</div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
        {% endif %}

        <!-- AI 洞察 -->
        {% if ai_insights and ai_insights.enabled %}
        <div class="card ai-insight">
            <div class="card-title">
                <span class="icon">🤖</span>
                <span>AI 洞察</span>
            </div>
            {% if ai_insights.highlight %}
            <div class="insight-highlight">💡 {{ ai_insights.highlight }}</div>
            {% endif %}
            {% if ai_insights.market_comment %}
            <div class="insight-section">
                <span class="insight-label">📈 市场</span>
                <span class="insight-text">{{ ai_insights.market_comment }}</span>
            </div>
            {% endif %}
            {% if ai_insights.weather_advice %}
            <div class="insight-section">
                <span class="insight-label">🌤️ 出行</span>
                <span class="insight-text">{{ ai_insights.weather_advice }}</span>
            </div>
            {% endif %}
        </div>
        {% endif %}

        <!-- 热点资讯 -->
        <div class="card">
            <div class="card-title">
                <span class="icon">🔥</span>
                <span>全球热点</span>
            </div>
            <ul class="news-list">
                {% for news in news_list %}
                <li class="news-item">
                    <span class="news-time">{{ news.published }}</span>
                    <div class="news-content">
                        <div class="news-title">{{ news.title }}</div>
                        {% if news.ai_summary %}
                        <div class="news-ai-summary">🤖 {{ news.ai_summary }}</div>
                        {% endif %}
                        <div class="news-source">{{ news.source }}</div>
                    </div>
                </li>
                {% endfor %}
            </ul>
        </div>

        <div class="footer-note">
            <p>数据更新时间：{{ update_time }}</p>
            <p style="margin-top:5px">仅供参考，不构成投资建议</p>
        </div>
    </div>
</body>
</html>
"""

        template = Template(template_str)

        # 处理天气数据
        for city in data.get("weather", []):
            if city.get("success"):
                city["weather_icon"] = self.get_weather_icon(city.get("current", {}).get("weather", ""))
                city["aqi_icon"] = self.get_aqi_color(city.get("air", {}).get("aqi", "-"))

        # 渲染模板
        html = template.render(
            date=data.get("date", datetime.now().strftime("%Y年%m月%d日")),
            weekday=data.get("weekday", ""),
            weather=data.get("weather", []),
            indices=data.get("indices", {"us": [], "hk": [], "cn": []}),
            funds=data.get("funds", []),
            news_list=data.get("news", []),
            ai_insights=data.get("ai_insights", {"enabled": False}),
            update_time=data.get("update_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )

        return html

    def save_report(self, html: str, output_path: str):
        """保存日报到文件"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"日报已保存: {output_path}")
