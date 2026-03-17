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

    def fetch_hackernews(self) -> List[Dict]:
        """获取 Hacker News 热门文章"""
        try:
            from src.hackernews_fetcher import HackerNewsFetcher
            hn_fetcher = HackerNewsFetcher()
            news = hn_fetcher.get_front_page(limit=5)
            # 转换格式以兼容
            return [{
                "title": n["title"],
                "source": n["source"],
                "published": n["published"],
                "url": n["url"],
                "points": n.get("points", 0)
            } for n in news]
        except Exception as e:
            print(f"Hacker News 获取失败: {e}")
            return []

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
        """获取财联社新闻 - 使用 RSSHub 或备用源"""
        urls = [
            "https://rsshub.app/cls/telegraph",
            "https://rsshub.rssforever.com/cls/telegraph",
            "https://rss.shab.fun/cls/telegraph",
        ]
        for url in urls:
            result = self.fetch_from_rss(url, "财联社", max_items=3)
            if result:
                return result
        return []

    def fetch_techcrunch(self) -> List[Dict]:
        """获取 TechCrunch 科技新闻"""
        url = "https://techcrunch.com/feed/"
        return self.fetch_from_rss(url, "TechCrunch", max_items=2)

    def fetch_the_verge(self) -> List[Dict]:
        """获取 The Verge 科技新闻"""
        url = "https://www.theverge.com/rss/index.xml"
        return self.fetch_from_rss(url, "The Verge", max_items=2)

    def fetch_wallstreetcn(self) -> List[Dict]:
        """获取华尔街见闻新闻 - 使用 RSS 源"""
        urls = [
            "https://rsshub.app/wallstreetcn/live",
            "https://rsshub.rssforever.com/wallstreetcn/live",
            "https://rss.shab.fun/wallstreetcn/live",
        ]
        for url in urls:
            result = self.fetch_from_rss(url, "华尔街见闻", max_items=3)
            if result:
                return result
        return []

    def fetch_36kr(self) -> List[Dict]:
        """获取36氪新闻 - 使用 RSSHub 或备用源"""
        urls = [
            "https://rsshub.app/36kr/newsflashes",
            "https://rsshub.rssforever.com/36kr/newsflashes",
            "https://rss.shab.fun/36kr/newsflashes",
        ]
        for url in urls:
            result = self.fetch_from_rss(url, "36氪", max_items=3)
            if result:
                return result
        return []

    def fetch_solidot(self) -> List[Dict]:
        """获取 Solidot 科技新闻"""
        url = "https://www.solidot.org/index.rss"
        return self.fetch_from_rss(url, "Solidot", max_items=3)

    def fetch_ithome(self) -> List[Dict]:
        """获取 IT之家新闻"""
        urls = [
            "https://rsshub.app/ithome/ranking/24h",
            "https://rsshub.rssforever.com/ithome/ranking/24h",
        ]
        for url in urls:
            result = self.fetch_from_rss(url, "IT之家", max_items=3)
            if result:
                return result
        return []

    def fetch_newsapi(self, query: str = "finance") -> List[Dict]:
        """使用 NewsAPI 获取新闻"""
        if not self.newsapi_key:
            return []

        # 获取科技和商业新闻
        categories = ["technology", "business"]
        all_items = []

        for category in categories:
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                "apiKey": self.newsapi_key,
                "category": category,
                "language": "en",
                "pageSize": 3
            }

            try:
                response = requests.get(url, params=params, timeout=10)
                data = response.json()

                for article in data.get("articles", []):
                    all_items.append({
                        "title": article.get("title", ""),
                        "source": f"NewsAPI | {article.get('source', {}).get('name', 'Unknown')}",
                        "published": article.get("publishedAt", "")[5:10] if article.get("publishedAt") else "",
                        "url": article.get("url", "")
                    })
            except Exception as e:
                print(f"NewsAPI {category} 获取失败: {e}")

        return all_items[:5]

    def fetch_reuters(self) -> List[Dict]:
        """获取 Reuters 新闻 - 使用 RSSHub"""
        urls = [
            "https://rsshub.app/reuters/business/finance",
            "https://rsshub.rssforever.com/reuters/business/finance",
        ]
        for url in urls:
            result = self.fetch_from_rss(url, "Reuters", max_items=3)
            if result:
                return result
        return []

    def fetch_bloomberg(self) -> List[Dict]:
        """获取 Bloomberg 新闻 - 使用 RSSHub"""
        urls = [
            "https://rsshub.app/bloomberg/latest",
            "https://rsshub.rssforever.com/bloomberg/latest",
        ]
        for url in urls:
            result = self.fetch_from_rss(url, "Bloomberg", max_items=3)
            if result:
                return result
        return []

    def fetch_arstechnica(self) -> List[Dict]:
        """获取 Ars Technica 科技新闻"""
        url = "https://feeds.arstechnica.com/arstechnica/index"
        return self.fetch_from_rss(url, "Ars Technica", max_items=3)

    def fetch_wired(self) -> List[Dict]:
        """获取 Wired 科技新闻"""
        url = "https://www.wired.com/feed/rss"
        return self.fetch_from_rss(url, "Wired", max_items=3)

    def fetch_ft(self) -> List[Dict]:
        """获取 Financial Times 新闻"""
        urls = [
            "https://rsshub.app/ft/chinese",
            "https://rsshub.rssforever.com/ft/chinese",
        ]
        for url in urls:
            result = self.fetch_from_rss(url, "FT中文网", max_items=3)
            if result:
                return result
        return []

    def fetch_nyt(self) -> List[Dict]:
        """获取 New York Times 新闻"""
        url = "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"
        return self.fetch_from_rss(url, "NYT", max_items=3)

    def fetch_guardian(self) -> List[Dict]:
        """获取 The Guardian 新闻"""
        url = "https://www.theguardian.com/technology/rss"
        return self.fetch_from_rss(url, "The Guardian", max_items=3)

    def fetch_engadget(self) -> List[Dict]:
        """获取 Engadget 科技新闻"""
        url = "https://www.engadget.com/rss.xml"
        return self.fetch_from_rss(url, "Engadget", max_items=3)

    def fetch_verge_ai(self) -> List[Dict]:
        """获取 The Verge AI 新闻"""
        url = "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"
        return self.fetch_from_rss(url, "The Verge AI", max_items=3)

    def get_all_news(self, max_items: int = 5) -> List[Dict]:
        """获取所有新闻源"""
        all_news = []

        # 尝试多个数据源（按优先级排序）
        sources = [
            # 中文新闻源
            ("财联社", self.fetch_cailianshe),
            ("华尔街见闻", self.fetch_wallstreetcn),
            ("36氪", self.fetch_36kr),
            ("Solidot", self.fetch_solidot),
            ("IT之家", self.fetch_ithome),
            ("FT中文网", self.fetch_ft),
            # 国际新闻源
            ("Hacker News", self.fetch_hackernews),
            ("Reuters", self.fetch_reuters),
            ("Bloomberg", self.fetch_bloomberg),
            ("NewsAPI", self.fetch_newsapi),
            ("Ars Technica", self.fetch_arstechnica),
            ("Wired", self.fetch_wired),
            ("TechCrunch", self.fetch_techcrunch),
            ("The Verge", self.fetch_the_verge),
            ("NYT", self.fetch_nyt),
            ("The Guardian", self.fetch_guardian),
            ("Engadget", self.fetch_engadget),
            ("The Verge AI", self.fetch_verge_ai),
        ]

        for name, fetch_func in sources:
            try:
                news = fetch_func()
                if news:
                    print(f"  ✅ {name}: {len(news)}条")
                    all_news.extend(news)
                else:
                    print(f"  ⚠️ {name}: 无数据")
            except Exception as e:
                print(f"  ❌ {name}: {e}")

        # 去重并限制数量
        seen_titles = set()
        unique_news = []
        for item in all_news:
            title = item.get("title", "").strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_news.append(item)

        return unique_news[:max_items]
