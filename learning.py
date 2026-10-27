from __future__ import annotations

LEARNING_MODULES = [
    {
        "skill": "GA4 & Measurement",
        "lane": "Web Analytics",
        "level": "Intermédiaire",
        "duration": "2–3 h",
        "why": "Consolider la mesure événementielle, les paramètres GA4 et la qualité du tracking.",
        "project": "Auditer un parcours et proposer un plan de marquage GA4 propre avec événements, paramètres et KPI.",
        "keywords": ["GA4", "Google Analytics", "tracking", "measurement", "analytics"],
        "resources": [
            ("Google Skillshop", "https://skillshop.withgoogle.com/"),
            ("Google Analytics Help", "https://support.google.com/analytics/"),
        ],
    },
    {
        "skill": "SQL & BigQuery",
        "lane": "Web Analytics",
        "level": "Intermédiaire",
        "duration": "4–6 h",
        "why": "Passer de la lecture de dashboards à l’analyse autonome des données brutes.",
        "project": "Construire une requête BigQuery GA4 pour analyser acquisition, engagement et conversion.",
        "keywords": ["SQL", "BigQuery", "data", "GA4"],
        "resources": [
            ("Google Cloud Skills", "https://www.cloudskillsboost.google/catalog?keywords=BigQuery"),
            ("SQLBolt", "https://sqlbolt.com/"),
        ],
    },
    {
        "skill": "Contentsquare / Experience Analytics",
        "lane": "Convergence",
        "level": "Intermédiaire",
        "duration": "2–4 h",
        "why": "Relier comportement utilisateur, friction UX et mesure quantitative.",
        "project": "Identifier 3 frictions sur un parcours puis formuler des hypothèses testables.",
        "keywords": ["Contentsquare", "Air360", "Experience Analytics", "UX analytics", "friction"],
        "resources": [
            ("Contentsquare Training", "https://contentsquare.com/support/training-certification/"),
            ("Air360 Blog", "https://www.air360.io/fr/blog/"),
        ],
    },
    {
        "skill": "CRO & A/B Testing",
        "lane": "Convergence",
        "level": "Intermédiaire",
        "duration": "3–5 h",
        "why": "Transformer les insights UX et Analytics en expérimentations mesurables.",
        "project": "Créer une fiche d’expérimentation : problème, hypothèse, KPI, variante, critères de décision.",
        "keywords": ["CRO", "A/B testing", "Kameleoon", "AB Tasty", "Optimizely", "experimentation"],
        "resources": [
            ("Kameleoon Resources", "https://www.kameleoon.com/fr/ressources"),
            ("AB Tasty Blog", "https://www.abtasty.com/fr/blog/"),
        ],
    },
    {
        "skill": "Product Analytics",
        "lane": "Web Analytics",
        "level": "Intermédiaire",
        "duration": "3–4 h",
        "why": "Élargir l’analyse web vers les funnels, cohortes, activation et rétention produit.",
        "project": "Définir un funnel produit, ses événements et un dashboard activation/rétention.",
        "keywords": ["Product Analytics", "Amplitude", "Mixpanel", "funnel", "retention"],
        "resources": [
            ("Amplitude Product Analytics", "https://amplitude.com/explore/analytics/product-analytics-guide"),
            ("Mixpanel Blog", "https://mixpanel.com/blog/"),
        ],
    },
    {
        "skill": "UX Research & Usability",
        "lane": "UX / UI",
        "level": "Fondamentaux",
        "duration": "3–4 h",
        "why": "Structurer les méthodes qualitatives qui complètent la donnée comportementale.",
        "project": "Préparer un protocole de test utilisateur de 30 minutes avec objectifs, tâches et grille d’observation.",
        "keywords": ["UX Research", "user research", "usability", "usability testing"],
        "resources": [
            ("Nielsen Norman Group", "https://www.nngroup.com/articles/"),
        ],
    },
    {
        "skill": "Figma & Prototypage",
        "lane": "UX / UI",
        "level": "Fondamentaux",
        "duration": "3–5 h",
        "why": "Mieux collaborer avec les designers et matérialiser rapidement une hypothèse UX.",
        "project": "Créer un prototype cliquable d’un parcours court avec composants et variantes.",
        "keywords": ["Figma", "prototype", "prototyping", "design system", "UI"],
        "resources": [
            ("Figma Learn", "https://help.figma.com/hc/fr"),
        ],
    },
    {
        "skill": "Accessibilité numérique",
        "lane": "UX / UI",
        "level": "Fondamentaux",
        "duration": "2–4 h",
        "why": "Intégrer l’accessibilité dans les audits UX, analytics et recette produit.",
        "project": "Auditer une page sur navigation clavier, contraste, alternatives textuelles et structure.",
        "keywords": ["accessibility", "accessibilité", "RGAA", "WCAG", "WAI"],
        "resources": [
            ("W3C WAI", "https://www.w3.org/WAI/"),
            ("RGAA officiel", "https://accessibilite.numerique.gouv.fr/rgaa/"),
        ],
    },
    {
        "skill": "GEO / AI Search",
        "lane": "GEO / AI Search",
        "level": "Émergent",
        "duration": "3–5 h",
        "why": "Comprendre comment les moteurs génératifs citent, résument et recommandent les contenus.",
        "project": "Créer un mini audit GEO : requêtes cibles, citations IA, pages visibles, sources citées et trafic IA.",
        "keywords": ["GEO", "Generative Engine Optimization", "AI Search", "AI Overviews", "LLMO", "AEO", "ChatGPT Search", "Perplexity"],
        "resources": [
            ("Google Search Central", "https://developers.google.com/search"),
            ("OpenAI", "https://openai.com/"),
            ("Perplexity", "https://www.perplexity.ai/"),
        ],
    },
]


def modules_for_lane(lane: str) -> list[dict]:
    if not lane or lane == "Tous":
        return LEARNING_MODULES
    return [module for module in LEARNING_MODULES if module.get("lane") == lane]


def recommend_modules(skills: list[str], limit: int = 5) -> list[dict]:
    wanted = [str(skill).lower() for skill in skills if skill]
    if not wanted:
        return LEARNING_MODULES[:limit]

    scored: list[tuple[int, dict]] = []
    for module in LEARNING_MODULES:
        haystack = " ".join(
            [
                module.get("skill", ""),
                module.get("lane", ""),
                module.get("why", ""),
                *module.get("keywords", []),
            ]
        ).lower()
        score = sum(1 for skill in wanted if skill in haystack or any(token in haystack for token in skill.split()))
        if score:
            scored.append((score, module))

    ranked = [module for _, module in sorted(scored, key=lambda row: row[0], reverse=True)]
    if len(ranked) < limit:
        for module in LEARNING_MODULES:
            if module not in ranked:
                ranked.append(module)
            if len(ranked) >= limit:
                break
    return ranked[:limit]


LEARNING_RESOURCES = {
    module["skill"]: [
        {"title": label, "provider": label, "url": url, "type": "Ressource"}
        for label, url in module["resources"]
    ]
    for module in LEARNING_MODULES
}


def resources_for_skill(skill: str) -> list[dict]:
    low = (skill or "").lower()
    for module in LEARNING_MODULES:
        haystack = [module["skill"], *module.get("keywords", [])]
        if any(low == value.lower() or low in value.lower() or value.lower() in low for value in haystack if value):
            return [
                {"title": label, "provider": label, "url": url, "type": "Ressource"}
                for label, url in module["resources"]
            ]
    return []


def build_learning_plan(gaps: list[dict], max_skills: int = 8) -> list[dict]:
    plan: list[dict] = []
    for gap in gaps[:max_skills]:
        skill = gap.get("skill", "")
        plan.append(
            {
                "skill": skill,
                "family": gap.get("family", ""),
                "signal": gap.get("mentions", 0),
                "resources": resources_for_skill(skill),
            }
        )
    return plan
