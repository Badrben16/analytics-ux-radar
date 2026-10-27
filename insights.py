from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote_plus

import feedparser
import requests

from config import KEYWORDS, SKILL_VOCAB

HISTORY_PATH = Path('data/history.json')
TRENDS_RSS = 'https://trends.google.com/trending/rss?geo=FR'
USER_AGENT = 'AnalyticsUXRadar/1.5 (+https://github.com/Badrben16/analytics-ux-radar)'


def google_trends_explore_url(term: str) -> str:
    return f'https://trends.google.com/trends/explore?geo=FR&q={quote_plus(term)}'


def fetch_google_trending_now(limit: int = 20) -> list[dict]:
    """Public Google Trends Trending Now RSS (France). No API key required."""
    try:
        r = requests.get(TRENDS_RSS, headers={'User-Agent': USER_AGENT}, timeout=12)
        r.raise_for_status()
        feed = feedparser.parse(r.content)
    except Exception:
        return []

    rows: list[dict] = []
    for entry in feed.entries[:limit]:
        title = (getattr(entry, 'title', '') or '').strip()
        traffic = ''
        for key in ('ht_approx_traffic', 'approx_traffic'):
            if hasattr(entry, key):
                traffic = str(getattr(entry, key) or '')
                break
        rows.append({
            'term': title,
            'traffic': traffic,
            'link': getattr(entry, 'link', '') or google_trends_explore_url(title),
            'published': getattr(entry, 'published', ''),
        })
    return rows


def skill_mentions(items: list[dict], top_n: int = 20) -> list[dict]:
    counts: Counter[str] = Counter()
    families: dict[str, str] = {}
    for family, skills in SKILL_VOCAB.items():
        for skill in skills:
            families[skill.lower()] = family

    for item in items:
        text = f" {item.get('title','')} {item.get('summary','')} ".lower()
        for family, skills in SKILL_VOCAB.items():
            for skill in skills:
                if skill.lower() in text:
                    counts[skill] += 1

    return [
        {'skill': skill, 'mentions': count, 'family': families.get(skill.lower(), 'Autre')}
        for skill, count in counts.most_common(top_n)
    ]


def user_skill_gaps(items: list[dict], current_skills: list[str], top_n: int = 12) -> list[dict]:
    current = {s.lower() for s in current_skills}
    market = skill_mentions(items, top_n=40)
    gaps = [row for row in market if row['skill'].lower() not in current]
    return gaps[:top_n]


def topic_momentum(items: list[dict], top_n: int = 15) -> list[dict]:
    """Simple recency-weighted signal: newer mentions count more than older ones."""
    now = datetime.now(timezone.utc)
    vocabulary = sorted({term for values in KEYWORDS.values() for term in values}, key=len, reverse=True)
    scores: Counter[str] = Counter()
    raw: Counter[str] = Counter()
    for item in items:
        text = f" {item.get('title','')} {item.get('summary','')} ".lower()
        try:
            dt = datetime.fromisoformat(item.get('published_at','').replace('Z','+00:00'))
            age_days = max(0, (now - dt).days)
        except Exception:
            age_days = 7
        weight = 4 if age_days <= 2 else 3 if age_days <= 7 else 2 if age_days <= 21 else 1
        for term in vocabulary:
            if term.lower() in text:
                scores[term] += weight
                raw[term] += 1
    if not scores:
        return []
    max_score = max(scores.values()) or 1
    return [
        {
            'term': term,
            'mentions': raw[term],
            'momentum': round(100 * score / max_score),
            'google_trends_url': google_trends_explore_url(term),
        }
        for term, score in scores.most_common(top_n)
    ]


def save_history_snapshot(items: list[dict], path: Path = HISTORY_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        history = json.loads(path.read_text(encoding='utf-8')) if path.exists() else []
    except Exception:
        history = []
    today = datetime.now(timezone.utc).date().isoformat()
    snapshot = {
        'date': today,
        'count': len(items),
        'skills': skill_mentions(items, 20),
        'topics': topic_momentum(items, 20),
    }
    history = [h for h in history if h.get('date') != today]
    history.append(snapshot)
    history = history[-120:]
    path.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding='utf-8')


def load_history(path: Path = HISTORY_PATH) -> list[dict]:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return []
