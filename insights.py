from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote_plus

from source_catalog import LANE_TERMS, SKILL_VOCAB

HISTORY_PATH = Path("data/history.json")


def google_trends_explore_url(term: str) -> str:
    return f"https://trends.google.com/trends/explore?geo=FR&q={quote_plus(term)}"


def _contains(text: str, term: str) -> bool:
    return term.lower() in text.lower()


def skill_mentions(items: list[dict], top_n: int = 30, lane: str | None = None) -> list[dict]:
    counts: Counter[str] = Counter()
    families: dict[str, str] = {}
    for family, skills in SKILL_VOCAB.items():
        for skill in skills:
            families[skill.lower()] = family

    scoped = [item for item in items if not lane or item.get("lane") == lane]
    for item in scoped:
        text = f" {item.get('title','')} {item.get('summary','')} ".lower()
        for family, skills in SKILL_VOCAB.items():
            for skill in skills:
                if _contains(text, skill):
                    counts[skill] += 1

    return [
        {"skill": skill, "mentions": count, "family": families.get(skill.lower(), "Autre")}
        for skill, count in counts.most_common(top_n)
    ]


def user_skill_gaps(items: list[dict], current_skills: list[str], top_n: int = 15, lane: str | None = None) -> list[dict]:
    current = {s.lower() for s in current_skills}
    market = skill_mentions(items, top_n=60, lane=lane)
    return [row for row in market if row["skill"].lower() not in current][:top_n]


def topic_momentum(items: list[dict], top_n: int = 20, lane: str | None = None) -> list[dict]:
    """Recency-weighted signal from the curated corpus, not a Google Trends score."""
    now = datetime.now(timezone.utc)
    vocabulary = sorted({term for values in LANE_TERMS.values() for term in values}, key=len, reverse=True)
    scores: Counter[str] = Counter()
    raw: Counter[str] = Counter()

    scoped = [item for item in items if not lane or item.get("lane") == lane]
    for item in scoped:
        text = f" {item.get('title','')} {item.get('summary','')} ".lower()
        try:
            dt = datetime.fromisoformat(item.get("published_at", "").replace("Z", "+00:00"))
            age_days = max(0, (now - dt).days)
        except Exception:
            age_days = 7
        weight = 5 if age_days <= 2 else 4 if age_days <= 7 else 2 if age_days <= 21 else 1
        for term in vocabulary:
            if term.lower() in text:
                scores[term] += weight
                raw[term] += 1

    if not scores:
        return []
    max_score = max(scores.values()) or 1
    return [
        {
            "term": term,
            "mentions": raw[term],
            "momentum": round(100 * score / max_score),
            "google_trends_url": google_trends_explore_url(term),
        }
        for term, score in scores.most_common(top_n)
    ]


def save_history_snapshot(items: list[dict], path: Path = HISTORY_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        history = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    except Exception:
        history = []

    today = datetime.now(timezone.utc).date().isoformat()
    snapshot = {
        "date": today,
        "count": len(items),
        "lanes": {
            lane: {
                "count": sum(1 for item in items if item.get("lane") == lane),
                "skills": skill_mentions(items, 20, lane=lane),
                "topics": topic_momentum(items, 20, lane=lane),
            }
            for lane in ("Web Analytics", "UX / UI", "Convergence")
        },
        "skills": skill_mentions(items, 25),
        "topics": topic_momentum(items, 25),
    }
    history = [h for h in history if h.get("date") != today]
    history.append(snapshot)
    history = history[-180:]
    path.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")


def load_history(path: Path = HISTORY_PATH) -> list[dict]:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []


def history_skill_series(history: list[dict], skill: str) -> list[dict]:
    rows: list[dict] = []
    for snapshot in history:
        mentions = 0
        for row in snapshot.get("skills", []):
            if row.get("skill", "").lower() == skill.lower():
                mentions = row.get("mentions", 0)
                break
        rows.append({"date": snapshot.get("date"), "mentions": mentions})
    return rows
