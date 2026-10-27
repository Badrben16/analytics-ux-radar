from __future__ import annotations

LEARNING_RESOURCES = {
    "GA4": [
        {"title": "Google Skillshop — Google Analytics", "provider": "Google", "url": "https://skillshop.withgoogle.com/", "type": "Formation officielle"},
    ],
    "Google Analytics": [
        {"title": "Google Skillshop — Google Analytics", "provider": "Google", "url": "https://skillshop.withgoogle.com/", "type": "Formation officielle"},
    ],
    "BigQuery": [
        {"title": "Google Cloud Skills — BigQuery", "provider": "Google Cloud", "url": "https://www.cloudskillsboost.google/catalog?keywords=BigQuery", "type": "Parcours"},
    ],
    "SQL": [
        {"title": "SQLBolt — exercices SQL", "provider": "SQLBolt", "url": "https://sqlbolt.com/", "type": "Exercices gratuits"},
    ],
    "Contentsquare": [
        {"title": "Contentsquare Training & Certification", "provider": "Contentsquare", "url": "https://contentsquare.com/support/training-certification/", "type": "Formation officielle"},
        {"title": "Essential Learning Kit — UX Designer", "provider": "Contentsquare", "url": "https://support.contentsquare.com/hc/en-us/articles/37271805796497-Essential-Learning-Kit-UX-Designer", "type": "Kit métier"},
    ],
    "Air360": [
        {"title": "Air360 Blog — UX analytics & CRO", "provider": "Air360", "url": "https://www.air360.io/fr/blog/", "type": "Ressources"},
    ],
    "Amplitude": [
        {"title": "Amplitude — Product Analytics Guide", "provider": "Amplitude", "url": "https://amplitude.com/explore/analytics/product-analytics-guide", "type": "Guide officiel"},
        {"title": "Amplitude Blog", "provider": "Amplitude", "url": "https://amplitude.com/blog", "type": "Ressources"},
    ],
    "Mixpanel": [
        {"title": "Mixpanel — Signals & Stories", "provider": "Mixpanel", "url": "https://mixpanel.com/blog/", "type": "Ressources"},
    ],
    "Figma": [
        {"title": "Figma Learn", "provider": "Figma", "url": "https://help.figma.com/hc/fr", "type": "Cours officiels"},
    ],
    "UX Research": [
        {"title": "Nielsen Norman Group — Articles UX Research", "provider": "NN/g", "url": "https://www.nngroup.com/articles/", "type": "Références"},
    ],
    "user research": [
        {"title": "Nielsen Norman Group — Articles UX Research", "provider": "NN/g", "url": "https://www.nngroup.com/articles/", "type": "Références"},
    ],
    "usability testing": [
        {"title": "Nielsen Norman Group — Usability", "provider": "NN/g", "url": "https://www.nngroup.com/articles/", "type": "Références"},
    ],
    "accessibility": [
        {"title": "W3C Web Accessibility Initiative", "provider": "W3C", "url": "https://www.w3.org/WAI/", "type": "Référence officielle"},
    ],
    "RGAA": [
        {"title": "RGAA — Référentiel officiel", "provider": "DINUM", "url": "https://accessibilite.numerique.gouv.fr/rgaa/", "type": "Référence officielle"},
    ],
    "CRO": [
        {"title": "Kameleoon Resources — Experimentation", "provider": "Kameleoon", "url": "https://www.kameleoon.com/fr/ressources?field_type_target_id=2", "type": "Ressources"},
        {"title": "AB Tasty Blog — Experimentation & CRO", "provider": "AB Tasty", "url": "https://www.abtasty.com/fr/blog/", "type": "Ressources"},
    ],
    "A/B testing": [
        {"title": "Kameleoon — A/B Test & Experimentation", "provider": "Kameleoon", "url": "https://www.kameleoon.com/platform/experimentation", "type": "Guide produit"},
        {"title": "AB Tasty Blog", "provider": "AB Tasty", "url": "https://www.abtasty.com/fr/blog/", "type": "Ressources"},
    ],
    "Kameleoon": [
        {"title": "Kameleoon Resources", "provider": "Kameleoon", "url": "https://www.kameleoon.com/fr/ressources?field_type_target_id=2", "type": "Ressources"},
    ],
    "AB Tasty": [
        {"title": "AB Tasty Blog", "provider": "AB Tasty", "url": "https://www.abtasty.com/fr/blog/", "type": "Ressources"},
    ],
    "Product Analytics": [
        {"title": "Amplitude — Product Analytics Guide", "provider": "Amplitude", "url": "https://amplitude.com/explore/analytics/product-analytics-guide", "type": "Guide officiel"},
        {"title": "Mixpanel Blog", "provider": "Mixpanel", "url": "https://mixpanel.com/blog/", "type": "Ressources"},
    ],
}


def resources_for_skill(skill: str) -> list[dict]:
    if skill in LEARNING_RESOURCES:
        return LEARNING_RESOURCES[skill]
    low = skill.lower()
    for key, rows in LEARNING_RESOURCES.items():
        if key.lower() == low:
            return rows
    return []


def build_learning_plan(gaps: list[dict], max_skills: int = 8) -> list[dict]:
    plan: list[dict] = []
    for gap in gaps[:max_skills]:
        skill = gap.get("skill", "")
        plan.append({
            "skill": skill,
            "family": gap.get("family", ""),
            "signal": gap.get("mentions", 0),
            "resources": resources_for_skill(skill),
        })
    return plan
