from __future__ import annotations

import io
import re
from collections import defaultdict

from pypdf import PdfReader

from config import SKILL_VOCAB


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def extract_text_from_upload(uploaded_file) -> str:
    if uploaded_file is None:
        return ""
    name = uploaded_file.name.lower()
    data = uploaded_file.read()
    if name.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(data))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    if name.endswith((".txt", ".md")):
        return data.decode("utf-8", errors="ignore")
    return ""


def detect_skills(text: str) -> dict[str, list[str]]:
    haystack = normalize(text)
    found: dict[str, list[str]] = defaultdict(list)
    for family, skills in SKILL_VOCAB.items():
        for skill in skills:
            if skill.lower() in haystack:
                found[family].append(skill)
    return dict(found)


def flatten_skill_map(skill_map: dict[str, list[str]]) -> set[str]:
    return {skill.lower() for values in skill_map.values() for skill in values}


def analyze_cv_against_job(cv_text: str, job_text: str) -> dict:
    cv_skills = detect_skills(cv_text)
    job_skills = detect_skills(job_text)
    cv_flat = flatten_skill_map(cv_skills)
    job_flat = flatten_skill_map(job_skills)

    matched = sorted(job_flat & cv_flat)
    missing = sorted(job_flat - cv_flat)
    extra = sorted(cv_flat - job_flat)
    score = round((len(matched) / len(job_flat) * 100), 1) if job_flat else 0.0

    gaps_by_family: dict[str, list[str]] = {}
    for family, skills in job_skills.items():
        gaps = [s for s in skills if s.lower() not in cv_flat]
        if gaps:
            gaps_by_family[family] = gaps

    strengths_by_family: dict[str, list[str]] = {}
    for family, skills in job_skills.items():
        matches = [s for s in skills if s.lower() in cv_flat]
        if matches:
            strengths_by_family[family] = matches

    recommendations: list[str] = []
    if missing:
        recommendations.append(
            "Faire apparaître explicitement les compétences réellement maîtrisées mais absentes du CV, en priorité : "
            + ", ".join(missing[:8])
            + "."
        )
    if any(term in normalize(job_text) for term in ("impact", "kpi", "conversion", "retention", "business")):
        recommendations.append(
            "Renforcer les réalisations chiffrées : KPI avant/après, gain de conversion, qualité de données, adoption ou temps économisé."
        )
    if any(term in normalize(job_text) for term in ("product", "produit", "roadmap", "feature")):
        recommendations.append(
            "Reformuler les expériences pour montrer la contribution aux décisions produit, pas seulement la production de reporting."
        )
    if any(term in normalize(job_text) for term in ("ux", "user experience", "cro", "experimentation", "a/b")):
        recommendations.append(
            "Mettre en avant les analyses de parcours, frictions, hypothèses, expérimentations et recommandations UX/CRO."
        )
    if any(term in normalize(job_text) for term in ("sql", "bigquery", "snowflake", "databricks")):
        recommendations.append(
            "Ajouter des exemples concrets d'analyses SQL/data : jointures, cohortes, funnels, contrôle qualité ou automatisation."
        )

    return {
        "score": score,
        "matched": matched,
        "missing": missing,
        "extra": extra,
        "job_skills": job_skills,
        "cv_skills": cv_skills,
        "gaps_by_family": gaps_by_family,
        "strengths_by_family": strengths_by_family,
        "recommendations": recommendations,
    }


def suggested_profile_angle(job_text: str) -> str:
    text = normalize(job_text)
    product = sum(text.count(x) for x in ("product", "retention", "activation", "feature", "roadmap"))
    cro = sum(text.count(x) for x in ("cro", "conversion", "a/b", "experimentation"))
    ux = sum(text.count(x) for x in ("ux", "research", "figma", "usability", "accessibility"))
    analytics = sum(text.count(x) for x in ("analytics", "ga4", "sql", "bigquery", "tracking"))

    scores = {
        "Product Analyst": product,
        "CRO / Experimentation Analyst": cro,
        "UX / Experience Analyst": ux,
        "Digital / Web Analyst": analytics,
    }
    return max(scores, key=scores.get) if any(scores.values()) else "Analytics & UX"
