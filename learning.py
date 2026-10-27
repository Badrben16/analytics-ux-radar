from __future__ import annotations

LEARNING_MODULES = [
    {
        "skill": "AI / Agentic Analytics",
        "lane": "Web Analytics",
        "level": "Avancé",
        "duration": "4–6 h",
        "horizon": "2026–2028",
        "future_score": 5,
        "why": "Comprendre comment les copilots et agents changent l’exploration, le diagnostic et la recommandation dans l’analytics.",
        "project": "Construire une grille d’évaluation d’un agent analytics : descriptif, diagnostic, prédictif, prescriptif, traçabilité et validation humaine.",
        "keywords": ["Agent Analytics", "analytics agent", "AI", "Amplitude", "Mixpanel"],
        "resources": [
            ("Amplitude · AI analytics agents", "https://amplitude.com/blog/ai-analytics-agents-task-based-evaluation"),
            ("Mixpanel · State of Digital Analytics 2026", "https://mixpanel.com/blog/digital-analytics-benchmarks-2026/"),
        ],
    },
    {
        "skill": "AI Search / GEO Measurement",
        "lane": "Web Analytics",
        "level": "Intermédiaire",
        "duration": "3–5 h",
        "horizon": "2026–2028",
        "future_score": 5,
        "why": "Mesurer la visibilité et les visites issues des moteurs génératifs devient une extension naturelle du Web Analytics.",
        "project": "Créer un framework de mesure : AI referrals, pages citées, requêtes, citations LLM, engagement et conversion post-clic.",
        "keywords": ["AI Search", "GEO", "AI referrals", "LLM citations", "Search Console"],
        "resources": [
            ("Google Search Central · Google Trends", "https://developers.google.com/search/docs/monitor-debug/trends-start"),
            ("Google Trends API alpha", "https://developers.google.com/search/apis/trends"),
            ("Google Search Central Blog", "https://developers.google.com/search/blog"),
        ],
    },
    {
        "skill": "Product Analytics & Decision Metrics",
        "lane": "Web Analytics",
        "level": "Intermédiaire",
        "duration": "4–6 h",
        "horizon": "Maintenant",
        "future_score": 5,
        "why": "Le métier évolue de l’audience et du reporting vers activation, rétention, adoption et décision produit.",
        "project": "Construire un funnel activation → rétention avec cohortes et proposer trois décisions produit basées sur les données.",
        "keywords": ["Product Analytics", "retention", "activation", "cohort", "Amplitude", "Mixpanel"],
        "resources": [
            ("Amplitude · Product Analytics", "https://amplitude.com/explore/analytics/product-analytics-guide"),
            ("Mixpanel · Signals & Stories", "https://mixpanel.com/blog/"),
        ],
    },
    {
        "skill": "Measurement Quality, Privacy & Server-side",
        "lane": "Web Analytics",
        "level": "Avancé",
        "duration": "5–8 h",
        "horizon": "Maintenant",
        "future_score": 4,
        "why": "La valeur de l’analytics dépend de plus en plus de la qualité de collecte, de la gouvernance et de la résilience de la mesure.",
        "project": "Auditer un plan de marquage puis définir contrôles qualité, consentement, server-side et règles d’observabilité.",
        "keywords": ["GA4", "server-side tagging", "consent mode", "data quality", "Tealium"],
        "resources": [
            ("Google Analytics Help", "https://support.google.com/analytics/"),
            ("Google Tag Manager · Server-side", "https://developers.google.com/tag-platform/tag-manager/server-side"),
        ],
    },
    {
        "skill": "AI-assisted UX & Product Design",
        "lane": "UX / UI",
        "level": "Intermédiaire",
        "duration": "3–5 h",
        "horizon": "2026–2028",
        "future_score": 5,
        "why": "L’IA accélère l’exploration et le prototypage ; la différenciation se déplace vers le jugement, le craft et la qualité de décision.",
        "project": "Produire trois directions de design avec IA, documenter les choix rejetés et justifier la solution finale par critères UX.",
        "keywords": ["Figma", "AI design", "AI prototyping", "product design"],
        "resources": [
            ("Figma · State of the Designer 2026", "https://www.figma.com/reports/state-of-the-designer-2026/"),
            ("Figma · AI Report 2026", "https://www.figma.com/blog/2026-ai-report/"),
        ],
    },
    {
        "skill": "Human–AI Interaction",
        "lane": "UX / UI",
        "level": "Avancé",
        "duration": "4–6 h",
        "horizon": "2026–2029",
        "future_score": 5,
        "why": "Concevoir des expériences IA exige de nouveaux patterns autour de la confiance, du contrôle, des erreurs et de la transparence.",
        "project": "Auditer un assistant IA : onboarding, confiance, confirmation, erreurs, explicabilité, contrôle utilisateur et reprise manuelle.",
        "keywords": ["AI UX", "Human-AI Interaction", "conversational UX", "agentic UX"],
        "resources": [
            ("Nielsen Norman Group", "https://www.nngroup.com/articles/"),
            ("Figma · AI Report 2026", "https://www.figma.com/blog/2026-ai-report/"),
        ],
    },
    {
        "skill": "Agentic, Conversational & Multimodal UX",
        "lane": "UX / UI",
        "level": "Avancé",
        "duration": "4–6 h",
        "horizon": "2027–2029",
        "future_score": 5,
        "why": "Les interfaces futures combinent écran, langage naturel, voix, contexte et actions déléguées à des agents.",
        "project": "Concevoir un parcours hybride écran + conversation + action agentique avec garde-fous et points de reprise utilisateur.",
        "keywords": ["agentic UX", "conversational UX", "multimodal", "adaptive interface"],
        "resources": [
            ("Figma Blog", "https://www.figma.com/blog/"),
            ("W3C WAI", "https://www.w3.org/WAI/"),
        ],
    },
    {
        "skill": "Accessibility for AI-era Interfaces",
        "lane": "UX / UI",
        "level": "Intermédiaire",
        "duration": "3–5 h",
        "horizon": "Maintenant",
        "future_score": 4,
        "why": "L’accessibilité reste un fondement du métier et doit être étendue aux nouveaux composants, assistants et interactions multimodales.",
        "project": "Tester un parcours avec clavier, lecteur d’écran, contrastes et états dynamiques puis proposer un plan de correction.",
        "keywords": ["accessibility", "WCAG", "RGAA", "axe-core"],
        "resources": [
            ("W3C WAI", "https://www.w3.org/WAI/"),
            ("Deque University", "https://dequeuniversity.com/"),
            ("RGAA", "https://accessibilite.numerique.gouv.fr/rgaa/"),
        ],
    },
    {
        "skill": "Experience Analytics → Hypothesis",
        "lane": "Convergence",
        "level": "Intermédiaire",
        "duration": "3–5 h",
        "horizon": "Maintenant",
        "future_score": 5,
        "why": "Le point de rencontre UX × Analytics est la capacité à transformer un signal comportemental en problème d’expérience puis en hypothèse testable.",
        "project": "À partir d’un replay/heatmap/funnel, documenter friction → preuve → hypothèse → métrique → expérience.",
        "keywords": ["Contentsquare", "Air360", "Experience Analytics", "friction", "session replay"],
        "resources": [
            ("Contentsquare Training", "https://contentsquare.com/support/training-certification/"),
            ("Air360 Blog", "https://www.air360.io/fr/blog/"),
        ],
    },
    {
        "skill": "AI-powered Experimentation",
        "lane": "Convergence",
        "level": "Avancé",
        "duration": "4–6 h",
        "horizon": "2026–2028",
        "future_score": 5,
        "why": "L’IA réduit le coût de fabrication des variantes : la valeur se déplace vers l’hypothèse, le protocole, la métrique et l’interprétation.",
        "project": "Créer un protocole A/B test complet puis générer rapidement une variante avec IA sans sacrifier QA, tracking et décision statistique.",
        "keywords": ["experimentation", "A/B testing", "Kameleoon", "AB Tasty", "AI experimentation"],
        "resources": [
            ("Kameleoon · AI & experimentation", "https://www.kameleoon.com/blog/when-ai-breaks-the-technical-lock-on-experimentation"),
            ("AB Tasty Blog", "https://www.abtasty.com/blog/"),
            ("GrowthBook", "https://www.growthbook.io/"),
        ],
    },
    {
        "skill": "Human + Agent Experience Measurement",
        "lane": "Convergence",
        "level": "Avancé",
        "duration": "4–7 h",
        "horizon": "2026–2029",
        "future_score": 5,
        "why": "La convergence future consiste à concevoir et mesurer simultanément les expériences humaines, conversationnelles et agentiques.",
        "project": "Définir un modèle de parcours où humains et agents interviennent : étapes, événements, frictions, confiance, succès et escalade.",
        "keywords": ["human and agent experience", "agent journeys", "Contentsquare", "AI"],
        "resources": [
            ("Contentsquare · AI-first Experience Platform", "https://contentsquare.com/press/new-ai-first-experience-platform/"),
            ("Amplitude · Agent Analytics", "https://amplitude.com/blog/agent-analytics"),
        ],
    },
]


def modules_for_lane(lane: str | None = None) -> list[dict]:
    if not lane or lane == "Tous":
        return LEARNING_MODULES
    return [module for module in LEARNING_MODULES if module["lane"] == lane]


def recommend_modules(skills: list[str], limit: int = 6) -> list[dict]:
    wanted = " ".join(skills).lower()
    scored: list[tuple[int, dict]] = []
    for module in LEARNING_MODULES:
        score = sum(1 for keyword in module.get("keywords", []) if keyword.lower() in wanted)
        if score:
            scored.append((score, module))
    scored.sort(key=lambda row: (row[0], row[1].get("future_score", 0)), reverse=True)
    return [module for _, module in scored[:limit]]
