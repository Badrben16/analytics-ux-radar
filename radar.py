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

from source_catalog import GITHUB_RELEASE_WATCHES, LANE_TERMS, REDDIT_FEEDS, source_query_urls

DATA_PATH = Path("data/news.json")
USER_AGENT = "RadarV369/2.1 (+https://github.com/Badrben16/analytics-ux-radar)"


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
    text = text.lower()
    term = term.lower().strip()
    if not term:
        return False
    # Avoid noisy substring matches for short acronyms such as UX, CRO, GEO.
    if len(term) <= 4 and term.replace("/", "").replace("-", "").isalnum():
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
    if item.get("source_type") in {"official-watch", "github-release"}:
        score += 1
    if item.get("source_type") == "reddit" and primary_hits >= 2:
        score += 1
    return max(1, min(5, score))


def _categories_from_matches(primary_lane: str, matches: dict[str, list[str]]) -> list[str]:
    cats = [primary_lane]
    for lane in LANE_TERMS:
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

    source_title = ""
    try:
        source_obj = getattr(entry, "source", None)
        if source_obj:
            source_title = _clean_html(getattr(source_obj, "title", "") if hasattr(source_obj, "title") else source_obj.get("title", ""))
    except Exception:
        source_title = ""

    brand_present = _contains_term(f"{text} {source_title}", brand)
    # Strict gate: either the article itself has a real signal for the lane,
    # or the curated watched brand is explicitly present.
    if not matches.get(lane) and not brand_present:
        return None

    item = {
        "title": title,
        "summary": summary[:1000],
        "url": link,
        "domain": _domain(link),
        "published_at": _parse_date(getattr(entry, "published", None) or getattr(entry, "updated", None)),
        "source": source_title or watch_name,
        "watch": watch_name,
        "source_type": "official-watch",
        "lane": lane,
        "query": f"{watch_name} · source surveillée",
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

    # Broad communities require explicit lane evidence. Narrow UX communities
    # are already curated enough to accept posts with a weaker lexical signal.
    strict_sources = {"r/analytics", "r/ProductManagement", "r/SEO", "r/TechSEO"}
    if feed_cfg["name"] in strict_sources and not matches.get(lane):
        return None

    item = {
        "title": title,
        "summary": summary[:1000],
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


def scan_github_releases(max_per_repo: int = 3) -> list[dict]:
    items: list[dict] = []
    headers = {"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"}
    for watch in GITHUB_RELEASE_WATCHES:
        repo = watch["repo"]
        try:
            response = requests.get(
                f"https://api.github.com/repos/{repo}/releases",
                params={"per_page": max_per_repo},
                headers=headers,
                timeout=12,
            )
            response.raise_for_status()
            for release in response.json():
                title = release.get("name") or release.get("tag_name") or repo
                body = _clean_html(release.get("body", ""))[:1000]
                text = f"{watch['name']} {title} {body}"
                matches = lane_matches(text)
                lane = watch["lane"]
                item = {
                    "title": f"{watch['name']} · {title}",
                    "summary": body or f"Nouvelle release publique de {watch['name']}.",
                    "url": release.get("html_url", ""),
                    "domain": "github.com",
                    "published_at": _parse_date(release.get("published_at") or release.get("created_at")),
                    "source": "GitHub Releases",
                    "watch": watch["name"],
                    "source_type": "github-release",
                    "lane": lane,
                    "query": repo,
                    "lane_matches": matches,
                    "categories": _categories_from_matches(lane, matches),
                }
                item["score"] = _score_item(item)
                items.append(item)
        except Exception:
            continue
    return items


def dedupe(items: Iterable[dict]) -> list[dict]:
    best: dict[str, dict] = {}
    for item in items:
        title_key = re.sub(r"[^a-z0-9]+", "", item.get("title", "").lower())[:220]
        key = title_key or item.get("url", "")
        if not key:
            continue
        current = best.get(key)
        if current is None or item.get("score", 0) > current.get("score", 0):
            best[key] = item
    return sorted(best.values(), key=lambda x: (x.get("published_at", ""), x.get("score", 0)), reverse=True)


def scan_all(
    use_gdelt: bool = False,
    max_per_feed: int = 6,
    include_reddit: bool = True,
    include_releases: bool = True,
) -> list[dict]:
    # `use_gdelt` is kept for backward compatibility only. GDELT is deliberately
    # disabled in V2 because it produced too much off-topic noise.
    items = scan_curated_news(max_per_feed=max_per_feed)
    if include_reddit:
        items.extend(scan_reddit(max_per_feed=max(4, max_per_feed)))
    if include_releases:
        items.extend(scan_github_releases(max_per_repo=3))
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
