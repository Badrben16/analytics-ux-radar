from __future__ import annotations

import html
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import quote_plus, urlparse

import feedparser
import requests
from dateutil import parser as date_parser

from config import KEYWORDS, OFFICIAL_FEEDS, TOPICS, google_news_urls

DATA_PATH = Path("data/news.json")
USER_AGENT = "AnalyticsUXRadar/1.0 (+https://github.com/Badrben16/analytics-ux-radar)"


def _clean_html(value: str | None) -> str:
    if not value:
        return ""
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def _parse_date(value: str | None) -> str:
    if not value:
        return datetime.now(timezone.utc).isoformat()
    try:
        dt = date_parser.parse(value)
        if not dt.tzinfo:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat()
    except Exception:
        return datetime.now(timezone.utc).isoformat()


def _domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""


def classify(text: str, hinted_category: str | None = None) -> tuple[list[str], dict[str, int]]:
    haystack = f" {text.lower()} "
    scores: dict[str, int] = {}
    for category, words in KEYWORDS.items():
        score = sum(1 for word in words if word.lower() in haystack)
        if score:
            scores[category] = score
    if hinted_category:
        scores[hinted_category] = scores.get(hinted_category, 0) + 2
    categories = [name for name, score in sorted(scores.items(), key=lambda x: x[1], reverse=True) if score > 0]
    return categories[:4] or ([hinted_category] if hinted_category else ["Autre"]), scores


def relevance_score(item: dict) -> int:
    text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
    categories, scores = classify(text, item.get("seed_category"))
    base = min(5, 1 + sum(scores.values()))

    # Bonus pour les signaux de convergence UX × Analytics / expérimentation.
    if any(k in text for k in ("a/b", "experimentation", "contentsquare", "product analytics", "cro")):
        base += 1
    if len(categories) >= 2:
        base += 1
    if item.get("source_type") == "official":
        base += 1
    return max(1, min(5, base))


def _entry_to_item(entry, source_name: str, source_type: str, seed_category: str, query: str) -> dict:
    title = _clean_html(getattr(entry, "title", ""))
    summary = _clean_html(getattr(entry, "summary", "") or getattr(entry, "description", ""))
    link = getattr(entry, "link", "")
    date_value = getattr(entry, "published", None) or getattr(entry, "updated", None)
    categories, keyword_scores = classify(f"{title} {summary}", seed_category)
    item = {
        "title": title,
        "summary": summary[:700],
        "url": link,
        "domain": _domain(link),
        "published_at": _parse_date(date_value),
        "source": source_name,
        "source_type": source_type,
        "seed_category": seed_category,
        "query": query,
        "categories": categories,
        "keyword_scores": keyword_scores,
    }
    item["score"] = relevance_score(item)
    return item


def scan_rss(max_per_feed: int = 6) -> list[dict]:
    items: list[dict] = []
    headers = {"User-Agent": USER_AGENT}

    for category, query, url in google_news_urls():
        try:
            response = requests.get(url, headers=headers, timeout=12)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
            for entry in feed.entries[:max_per_feed]:
                items.append(_entry_to_item(entry, "Google News", "search", category, query))
        except Exception:
            continue

    for source_name, url in OFFICIAL_FEEDS.items():
        try:
            response = requests.get(url, headers=headers, timeout=12)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
            for entry in feed.entries[:max_per_feed]:
                item = _entry_to_item(entry, source_name, "official", "UX" if "Nielsen" in source_name else "Analytics", source_name)
                items.append(item)
        except Exception:
            continue

    return items


def scan_gdelt(max_per_query: int = 15) -> list[dict]:
    """Interroge GDELT DOC 2.0. Aucun token requis. Les erreurs restent non bloquantes."""
    items: list[dict] = []
    broad_queries = {
        "UX": '("UX design" OR "UX research" OR Figma OR "product design")',
        "Analytics": '("product analytics" OR "web analytics" OR GA4 OR Contentsquare OR Amplitude)',
        "CRO": '(CRO OR "A/B testing" OR experimentation OR Kameleoon OR "AB Tasty")',
        "IA": '("AI analytics" OR "AI UX" OR "generative AI" OR "agentic analytics")',
    }
    headers = {"User-Agent": USER_AGENT}
    for category, query in broad_queries.items():
        params = {
            "query": query,
            "mode": "ArtList",
            "maxrecords": max_per_query,
            "format": "json",
            "sort": "HybridRel",
        }
        try:
            response = requests.get("https://api.gdeltproject.org/api/v2/doc/doc", params=params, headers=headers, timeout=15)
            response.raise_for_status()
            payload = response.json()
            for article in payload.get("articles", []):
                title = _clean_html(article.get("title", ""))
                link = article.get("url", "")
                categories, keyword_scores = classify(title, category)
                item = {
                    "title": title,
                    "summary": _clean_html(article.get("seendate", "")),
                    "url": link,
                    "domain": _domain(link),
                    "published_at": _parse_date(article.get("seendate")),
                    "source": article.get("domain") or "GDELT",
                    "source_type": "gdelt",
                    "seed_category": category,
                    "query": query,
                    "categories": categories,
                    "keyword_scores": keyword_scores,
                }
                item["score"] = relevance_score(item)
                items.append(item)
        except Exception:
            continue
    return items


def dedupe(items: Iterable[dict]) -> list[dict]:
    best: dict[str, dict] = {}
    for item in items:
        title_key = re.sub(r"[^a-z0-9]+", "", item.get("title", "").lower())[:180]
        key = title_key or item.get("url", "")
        if not key:
            continue
        current = best.get(key)
        if current is None or item.get("score", 0) > current.get("score", 0):
            best[key] = item
    return sorted(best.values(), key=lambda x: (x.get("published_at", ""), x.get("score", 0)), reverse=True)


def scan_all(use_gdelt: bool = True, max_per_feed: int = 6) -> list[dict]:
    items = scan_rss(max_per_feed=max_per_feed)
    if use_gdelt:
        items.extend(scan_gdelt())
    return dedupe(items)


def save_news(items: list[dict], path: Path = DATA_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(items),
        "items": items,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_news(path: Path = DATA_PATH) -> dict:
    if not path.exists():
        return {"generated_at": None, "count": 0, "items": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"generated_at": None, "count": 0, "items": []}


def trend_terms(items: list[dict], top_n: int = 20) -> list[tuple[str, int]]:
    vocabulary = sorted({term for values in KEYWORDS.values() for term in values}, key=len, reverse=True)
    counts: Counter[str] = Counter()
    for item in items:
        text = f" {item.get('title', '')} {item.get('summary', '')} ".lower()
        for term in vocabulary:
            if term.lower() in text:
                counts[term] += 1
    return counts.most_common(top_n)


def category_counts(items: list[dict]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for item in items:
        for category in item.get("categories", []):
            counts[category] += 1
    return dict(counts.most_common())
