"""
Hacker News 数据获取模块 - 使用 Algolia API
https://hn.algolia.com/api
"""
import requests
from typing import Dict, List
from datetime import datetime


class HackerNewsFetcher:
    """Hacker News 数据获取器"""

    BASE_URL = "https://hn.algolia.com/api/v1"

    def __init__(self):
        pass

    def _format_time(self, created_at: str) -> str:
        """格式化时间为 MM-DD HH:MM"""
        try:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            return dt.strftime("%m-%d %H:%M")
        except:
            return datetime.now().strftime("%m-%d")

    def get_front_page(self, limit: int = 10) -> List[Dict]:
        """
        获取 HN 首页热门文章

        Args:
            limit: 返回文章数量，默认 10 条

        Returns:
            新闻列表，每条包含 title, url, source, published, points, comments
        """
        url = f"{self.BASE_URL}/search"
        params = {
            "tags": "front_page",
            "hitsPerPage": limit
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for hit in data.get("hits", []):
                # 构造 HN 讨论链接
                object_id = hit.get("objectID", "")
                hn_url = f"https://news.ycombinator.com/item?id={object_id}"

                # 优先使用外部链接，如果没有则使用 HN 讨论页
                external_url = hit.get("url", "")
                target_url = external_url if external_url else hn_url

                results.append({
                    "title": hit.get("title", "无标题"),
                    "url": target_url,
                    "source": f"HN 🔥 {hit.get('points', 0)} | 💬 {hit.get('num_comments', 0)}",
                    "published": self._format_time(hit.get("created_at", "")),
                    "author": hit.get("author", ""),
                    "points": hit.get("points", 0),
                    "comments": hit.get("num_comments", 0),
                    "hn_url": hn_url,  # 保留 HN 讨论链接
                    "success": True
                })

            return results

        except Exception as e:
            print(f"Hacker News 获取失败: {e}")
            return []

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """
        搜索 HN 文章

        Args:
            query: 搜索关键词
            limit: 返回数量

        Returns:
            搜索结果列表
        """
        url = f"{self.BASE_URL}/search"
        params = {
            "query": query,
            "hitsPerPage": limit,
            "tags": "story"  # 只搜索文章
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for hit in data.get("hits", []):
                object_id = hit.get("objectID", "")
                hn_url = f"https://news.ycombinator.com/item?id={object_id}"
                external_url = hit.get("url", "")
                target_url = external_url if external_url else hn_url

                results.append({{
                    "title": hit.get("title", "无标题"),
                    "url": target_url,
                    "source": f"HN 搜索 | 🔥 {hit.get('points', 0)}",
                    "published": self._format_time(hit.get("created_at", "")),
                    "author": hit.get("author", ""),
                    "points": hit.get("points", 0),
                    "comments": hit.get("num_comments", 0),
                    "success": True
                }})

            return results

        except Exception as e:
            print(f"HN 搜索失败: {e}")
            return []

    def get_tech_news(self, limit: int = 5) -> List[Dict]:
        """
        获取科技相关热门文章（搜索 tech 关键词）
        """
        return self.search("tech programming", limit)

    def get_ai_news(self, limit: int = 5) -> List[Dict]:
        """
        获取 AI 相关热门文章
        """
        return self.search("AI artificial intelligence LLM", limit)
