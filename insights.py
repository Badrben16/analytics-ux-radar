from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote_plus

from source_catalog import EVOLUTION_TOPICS, LANE_TERMS, SKILL_VOCAB

HISTORY_PATH = Path("data/history.json")

WORLD_TREND_BASKETS = {
    "Web Analytics": ["Web Analytics", "Product Analytics", "GA4", "AI Search", "Generative Engine Optimization"],
    "UX / UI": ["UX Research", "Figma", "AI UX", "Design Systems", "Accessibility"],
    "Convergence": ["CRO", "A/B Testing", "Experimentation", "Experience Analytics", "Personalization"],
}


def google_trends_explore_url(term: str) -> str:
    return f"https://trends.google.com/trends/explore?date=today%205-y&q={quote_plus(term)}"


def google_trends_compare_url(terms: list[str]) -> str:
    selected = [t for t in terms if t][:5]
    query = ",".join(quote_plus(t) for t in selected)
    return f"https://trends.google.com/trends/explore?date=today%205-y&q={query}"


def _contains(text: str, term: str) -> bool:
    return term.lower() in text.lower()


def _published_age_days(item: dict) -> int:
    try:
        dt = datetime.fromisoformat((item.get("published_at") or "").replace("Z", "+00:00"))
        if not dt.tzinfo:
            dt = dt.replace(tzinfo=timezone.utc)
        return max(0, (datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).days)
    except Exception:
        return 30


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
    return [{"skill": skill, "mentions": count, "family": families.get(skill.lower(), "Autre")} for skill, count in counts.most_common(top_n)]


def user_skill_gaps(items: list[dict], current_skills: list[str], top_n: int = 15, lane: str | None = None) -> list[dict]:
    current = {s.lower() for s in current_skills}
    market = skill_mentions(items, top_n=80, lane=lane)
    return [row for row in market if row["skill"].lower() not in current][:top_n]


def topic_momentum(items: list[dict], top_n: int = 20, lane: str | None = None) -> list[dict]:
    vocabulary = sorted({term for values in LANE_TERMS.values() for term in values}, key=len, reverse=True)
    scores: Counter[str] = Counter()
    raw: Counter[str] = Counter()
    scoped = [item for item in items if not lane or item.get("lane") == lane]
    for item in scoped:
        text = f" {item.get('title','')} {item.get('summary','')} ".lower()
        age_days = _published_age_days(item)
        weight = 5 if age_days <= 7 else 4 if age_days <= 30 else 2 if age_days <= 90 else 1
        for term in vocabulary:
            if term.lower() in text:
                scores[term] += weight
                raw[term] += 1
    if not scores:
        return []
    max_score = max(scores.values()) or 1
    return [{"term": term, "mentions": raw[term], "momentum": round(100 * score / max_score), "google_trends_url": google_trends_explore_url(term)} for term, score in scores.most_common(top_n)]


def profession_evolution(items: list[dict], lane: str) -> list[dict]:
    scoped = [item for item in items if item.get("lane") == lane]
    rows: list[dict] = []
    for cfg in EVOLUTION_TOPICS.get(lane, []):
        recent = 0
        previous = 0
        examples: list[str] = []
        for item in scoped:
            text = f"{item.get('title','')} {item.get('summary','')}".lower()
            if not any(term.lower() in text for term in cfg["terms"]):
                continue
            age = _published_age_days(item)
            if age <= 30:
                recent += 1
            elif age <= 90:
                previous += 1
            if len(examples) < 3 and item.get("title"):
                examples.append(item["title"])
        previous_monthly = previous / 2.0
        delta = recent - previous_monthly
        evidence = recent + previous
        if recent >= 2 and delta >= 1:
            status = "Accélération"
        elif recent >= 1 and previous == 0:
            status = "Émergent"
        elif recent >= 1 and abs(delta) < 1:
            status = "Stable"
        elif recent == 0 and previous > 0:
            status = "À surveiller"
        else:
            status = "Signal faible"
        score = min(100, round(recent * 22 + max(delta, 0) * 14 + min(evidence, 5) * 5))
        rows.append({"topic": cfg["topic"], "status": status, "score": score, "recent": recent, "previous_monthly": round(previous_monthly, 1), "delta": round(delta, 1), "horizon": cfg["horizon"], "why": cfg["why"], "examples": examples, "google_trends_url": google_trends_explore_url(cfg["topic"])})
    return sorted(rows, key=lambda row: (row["score"], row["recent"]), reverse=True)


def save_history_snapshot(items: list[dict], path: Path = HISTORY_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        history = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    except Exception:
        history = []
    today = datetime.now(timezone.utc).date().isoformat()
    lanes = ("Web Analytics", "UX / UI", "Convergence")
    snapshot = {
        "date": today,
        "count": len(items),
        "lanes": {lane: {"count": sum(1 for item in items if item.get("lane") == lane), "skills": skill_mentions(items, 25, lane=lane), "topics": topic_momentum(items, 25, lane=lane), "evolution": profession_evolution(items, lane)} for lane in lanes},
        "skills": skill_mentions(items, 35),
        "topics": topic_momentum(items, 35),
    }
    history = [h for h in history if h.get("date") != today]
    history.append(snapshot)
    history = history[-365:]
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
