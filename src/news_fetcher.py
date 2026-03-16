"""
新闻资讯获取模块
"""
import os
import re
import requests
import feedparser
from typing import Dict, List
from datetime import datetime
from html import unescape


class NewsFetcher:
    """新闻资讯获取器"""

    def __init__(self, api_key: str = None):
        self.newsapi_key = api_key or os.getenv("NEWSAPI_KEY")

    def fetch_from_rss(self, url: str, source_name: str, max_items: int = 3) -> List[Dict]:
        """从RSS源获取新闻"""
        try:
            feed = feedparser.parse(url)
            news_items = []

            for entry in feed.entries[:max_items]:
                # 清理HTML标签
                title = re.sub(r'<[^>]+>', '', entry.get('title', ''))
                title = unescape(title)

                # 获取发布时间
                published = entry.get('published', '')
                if not published:
                    published = datetime.now().strftime("%m-%d")
                else:
                    # 简化日期格式
                    published = self._format_date(published)

                news_items.append({
                    "title": title,
                    "source": source_name,
                    "published": published,
                    "url": entry.get('link', '')
                })

            return news_items
        except Exception as e:
            print(f"RSS获取失败 {source_name}: {e}")
            return []

    def _format_date(self, date_str: str) -> str:
        """格式化日期为 MM-DD"""
        try:
            # 尝试解析常见格式
            for fmt in ["%a, %d %b %Y %H:%M:%S %z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
                try:
                    dt = datetime.strptime(date_str[:19], fmt[:19])
                    return dt.strftime("%m-%d")
                except:
                    continue
            return datetime.now().strftime("%m-%d")
        except:
            return datetime.now().strftime("%m-%d")

    def fetch_cailianshe(self) -> List[Dict]:
        """获取财联社新闻"""
        # 财联社 RSS
        url = "https://www.cls.cn/telegraph"
        # 由于财联社需要JS渲染，这里使用模拟数据或备用源
        return []

    def fetch_wallstreetcn(self) -> List[Dict]:
        """获取华尔街见闻新闻"""
        url = "https://api.wallstreetcn.com/apiv1/content/articles?category=global&limit=5"
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            items = []

            for item in data.get("data", {}).get("items", [])[:3]:
                items.append({
                    "title": item.get("title", ""),
                    "source": "华尔街见闻",
                    "published": datetime.fromtimestamp(item.get("display_time", 0)).strftime("%m-%d %H:%M"),
                    "url": f"https://wallstreetcn.com/articles/{item.get('id', '')}"
                })
            return items
        except Exception as e:
            print(f"华尔街见闻获取失败: {e}")
            return []

    def fetch_36kr(self) -> List[Dict]:
        """获取36氪新闻"""
        url = "https://36kr.com/api/newsflash"
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()
            items = []

            for item in data.get("data", {}).get("items", [])[:3]:
                items.append({
                    "title": item.get("title", ""),
                    "source": "36氪",
                    "published": item.get("published_at", "")[5:10] if item.get("published_at") else "",
                    "url": f"https://36kr.com/newsflashes/{item.get('id', '')}"
                })
            return items
        except Exception as e:
            print(f"36氪获取失败: {e}")
            return []

    def fetch_newsapi(self, query: str = "finance") -> List[Dict]:
        """使用 NewsAPI 获取新闻"""
        if not self.newsapi_key:
            return []

        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "apiKey": self.newsapi_key,
            "category": "business",
            "language": "zh",
            "pageSize": 5
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            items = []

            for article in data.get("articles", [])[:3]:
                items.append({
                    "title": article.get("title", ""),
                    "source": article.get("source", {}).get("name", "NewsAPI"),
                    "published": article.get("publishedAt", "")[5:10] if article.get("publishedAt") else "",
                    "url": article.get("url", "")
                })
            return items
        except Exception as e:
            print(f"NewsAPI获取失败: {e}")
            return []

    def get_all_news(self, max_items: int = 5) -> List[Dict]:
        """获取所有新闻源"""
        all_news = []

        # 尝试多个数据源
        sources = [
            ("wallstreetcn", self.fetch_wallstreetcn),
            ("36kr", self.fetch_36kr),
            ("newsapi", self.fetch_newsapi),
        ]

        for name, fetch_func in sources:
            try:
                news = fetch_func()
                all_news.extend(news)
            except Exception as e:
                print(f"{name} 获取失败: {e}")

        # 去重并限制数量
        seen_titles = set()
        unique_news = []
        for item in all_news:
            if item["title"] not in seen_titles:
                seen_titles.add(item["title"])
                unique_news.append(item)

        return unique_news[:max_items]
