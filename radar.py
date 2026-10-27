from __future__ import annotations

import html
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

import feedparser
import requests
from dateutil import parser as date_parser

from source_catalog import LANE_TERMS, REDDIT_FEEDS, source_query_urls

DATA_PATH = Path("data/news.json")
USER_AGENT = "AnalyticsUXRadar/2.0 (+https://github.com/Badrben16/analytics-ux-radar)"


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


def _contains_term(text: str, term: str) -> bool:
    """Match phrases cleanly and avoid substring noise (ex: UX inside unrelated words)."""
    text = text.lower()
    term = term.lower().strip()
    if not term:
        return False
    if len(term) <= 3 and term.replace("/", "").isalnum():
        return re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", text) is not None
    return term in text


def lane_matches(text: str) -> dict[str, list[str]]:
    matches: dict[str, list[str]] = {}
    for lane, terms in LANE_TERMS.items():
        found = [term for term in terms if _contains_term(text, term)]
        if found:
            matches[lane] = found
    return matches


def _score_item(item: dict) -> int:
    matches = item.get("lane_matches", {}) or {}
    primary = item.get("lane")
    primary_hits = len(matches.get(primary, []))
    cross_hits = sum(1 for lane, terms in matches.items() if lane != primary and terms)

    score = 1
    if primary_hits >= 1:
        score += 1
    if primary_hits >= 3:
        score += 1
    if cross_hits >= 1:
        score += 1
    if item.get("source_type") in {"official-watch", "official"}:
        score += 1
    if item.get("source_type") == "reddit" and primary_hits >= 2:
        score += 1
    return max(1, min(5, score))


def _categories_from_matches(primary_lane: str, matches: dict[str, list[str]]) -> list[str]:
    cats = [primary_lane]
    for lane in ("Web Analytics", "UX / UI", "Convergence"):
        if lane != primary_lane and matches.get(lane):
            cats.append(lane)
    return cats


def _news_entry_to_item(entry, lane: str, watch_name: str, brand: str) -> dict | None:
    title = _clean_html(getattr(entry, "title", ""))
    summary = _clean_html(getattr(entry, "summary", "") or getattr(entry, "description", ""))
    if not title:
        return None
    link = getattr(entry, "link", "")
    text = f"{title} {summary}"
    matches = lane_matches(text)

    # Curated Google News queries are site/brand restricted. Still require either
    # a real primary-lane signal or the watched brand in the article text/source.
    source_title = ""
    try:
        source_title = _clean_html(getattr(getattr(entry, "source", {}), "title", ""))
    except Exception:
        source_title = ""
    brand_present = _contains_term(f"{text} {source_title}", brand)
    if not matches.get(lane) and not brand_present:
        return None

    item = {
        "title": title,
        "summary": summary[:900],
        "url": link,
        "domain": _domain(link),
        "published_at": _parse_date(getattr(entry, "published", None) or getattr(entry, "updated", None)),
        "source": source_title or watch_name,
        "watch": watch_name,
        "source_type": "official-watch",
        "lane": lane,
        "query": f"{watch_name} (source surveillée)",
        "lane_matches": matches,
        "categories": _categories_from_matches(lane, matches),
    }
    item["score"] = _score_item(item)
    return item


def scan_curated_news(max_per_feed: int = 6) -> list[dict]:
    items: list[dict] = []
    headers = {"User-Agent": USER_AGENT}
    for lane, watch_name, brand, url in source_query_urls():
        try:
            response = requests.get(url, headers=headers, timeout=12)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
            for entry in feed.entries[:max_per_feed]:
                item = _news_entry_to_item(entry, lane, watch_name, brand)
                if item:
                    items.append(item)
        except Exception:
            continue
    return items


def _reddit_entry_to_item(entry, feed_cfg: dict) -> dict | None:
    title = _clean_html(getattr(entry, "title", ""))
    summary = _clean_html(getattr(entry, "summary", "") or getattr(entry, "description", ""))
    if not title:
        return None
    lane = feed_cfg["lane"]
    text = f"{title} {summary}"
    matches = lane_matches(text)

    # The subreddit itself is curated, but require at least one métier signal for
    # broad communities such as r/analytics / r/ProductManagement.
    strict_sources = {"r/analytics", "r/ProductManagement"}
    if feed_cfg["name"] in strict_sources and not matches.get(lane):
        return None

    item = {
        "title": title,
        "summary": summary[:900],
        "url": getattr(entry, "link", ""),
        "domain": "reddit.com",
        "published_at": _parse_date(getattr(entry, "published", None) or getattr(entry, "updated", None)),
        "source": feed_cfg["name"],
        "watch": feed_cfg["name"],
        "source_type": "reddit",
        "lane": lane,
        "query": "Communauté Reddit ciblée",
        "lane_matches": matches,
        "categories": _categories_from_matches(lane, matches),
    }
    item["score"] = _score_item(item)
    return item


def scan_reddit(max_per_feed: int = 8) -> list[dict]:
    items: list[dict] = []
    headers = {"User-Agent": USER_AGENT, "Accept": "application/rss+xml,application/xml,text/xml"}
    for feed_cfg in REDDIT_FEEDS:
        try:
            response = requests.get(feed_cfg["url"], headers=headers, timeout=12)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
            for entry in feed.entries[:max_per_feed]:
                item = _reddit_entry_to_item(entry, feed_cfg)
                if item:
                    items.append(item)
        except Exception:
            continue
    return items


def dedupe(items: Iterable[dict]) -> list[dict]:
    best: dict[str, dict] = {}
    for item in items:
        title_key = re.sub(r"[^a-z0-9]+", "", item.get("title", "").lower())[:200]
        key = title_key or item.get("url", "")
        if not key:
            continue
        current = best.get(key)
        if current is None or item.get("score", 0) > current.get("score", 0):
            best[key] = item
    return sorted(best.values(), key=lambda x: (x.get("published_at", ""), x.get("score", 0)), reverse=True)


def scan_all(use_gdelt: bool = False, max_per_feed: int = 6, include_reddit: bool = True) -> list[dict]:
    # use_gdelt conservé pour compatibilité avec les anciennes versions, mais GDELT
    # n'est plus utilisé : trop de bruit pour une veille métier ciblée.
    items = scan_curated_news(max_per_feed=max_per_feed)
    if include_reddit:
        items.extend(scan_reddit(max_per_feed=max(4, max_per_feed)))
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


def lane_counts(items: list[dict]) -> dict[str, int]:
    counts: Counter[str] = Counter(item.get("lane", "Autre") for item in items)
    return dict(counts)


def category_counts(items: list[dict]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for item in items:
        for category in item.get("categories", []):
            counts[category] += 1
    return dict(counts.most_common())


def items_for_lane(items: list[dict], lane: str, min_score: int = 1) -> list[dict]:
    rows = [item for item in items if item.get("lane") == lane and item.get("score", 0) >= min_score]
    return sorted(rows, key=lambda x: (x.get("score", 0), x.get("published_at", "")), reverse=True)


def convergence_items(items: list[dict], min_score: int = 2) -> list[dict]:
    rows: list[dict] = []
    for item in items:
        cats = set(item.get("categories", []))
        is_cross = "Convergence" in cats or ({"Web Analytics", "UX / UI"} <= cats)
        if is_cross and item.get("score", 0) >= min_score:
            rows.append(item)
    return sorted(rows, key=lambda x: (x.get("score", 0), x.get("published_at", "")), reverse=True)
