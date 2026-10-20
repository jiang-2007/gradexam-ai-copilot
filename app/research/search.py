"""全网搜索封装：支持博查搜索 API（免费额度）"""
import os
import requests
from typing import List, Dict

# 默认接口（可覆盖）
BOCHA_URL = "https://api.bochaai.com/v1/web-search"


class WebSearch:
    """通用联网搜索

    部署时在 .env 配置 BOCHA_API_KEY（在 https://open.bochaai.com 注册，
    新用户有免费额度）。未配置时抛出提示，不会静默返回假数据。
    """

    def __init__(self, api_key: str = "", url: str = ""):
        self.api_key = api_key or os.getenv("BOCHA_API_KEY", "")
        self.url = url or os.getenv("BOCHA_SEARCH_URL", BOCHA_URL)

    def search(self, query: str, count: int = 8, freshness: str = "oneYear") -> List[Dict]:
        """执行搜索，返回文档列表 [{title, url, snippet, publish_time}]"""
        if not self.api_key:
            raise RuntimeError(
                "未配置 BOCHA_API_KEY。请到 https://open.bochaai.com 注册获取（有免费额度），"
                "填入 .env 后重启服务。"
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "query": query,
            "summary": True,
            "count": count,
            "freshness": freshness,
        }
        try:
            resp = requests.post(self.url, headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            raise RuntimeError(f"搜索接口调用失败：{e}")

        pages = data.get("data", {}).get("webPages", {}).get("value", [])
        results = []
        for p in pages:
            results.append({
                "title": p.get("name", ""),
                "url": p.get("url", ""),
                "snippet": p.get("summary", ""),
                "publish_time": p.get("dateLastPublished", ""),
            })
        return results

    def search_text(self, query: str, count: int = 8, freshness: str = "oneYear") -> str:
        """搜索并拼接成纯文本（便于喂给 LLM 提取）"""
        results = self.search(query, count, freshness)
        blocks = []
        for i, r in enumerate(results, 1):
            blocks.append(
                f"[{i}] 标题：{r['title']}\n"
                f"来源：{r['url']}\n"
                f"时间：{r['publish_time']}\n"
                f"内容：{r['snippet']}"
            )
        return "\n\n".join(blocks)


def search_or_hint(query: str, count: int = 8) -> str:
    """搜索；失败时返回配置指引（便于前端展示）"""
    ws = WebSearch()
    try:
        return ws.search_text(query, count)
    except RuntimeError as e:
        return f"【搜索未启用】{e}"
