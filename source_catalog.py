from __future__ import annotations

from urllib.parse import quote_plus

GOOGLE_NEWS_BASE = "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"

# RadarV369 follows only two professions and the space where they overlap:
# 1) Web Analytics
# 2) UX / UI
# 3) Convergence UX × Analytics
#
# GEO / AI Search is deliberately treated as an evolution of Web Analytics,
# not as a standalone profession lane.
SOURCE_WATCHES = {
    "Web Analytics": [
        {"name": "Google Analytics", "query": "site:blog.google/products/marketingplatform Google Analytics GA4 measurement", "brand": "google analytics"},
        {"name": "Google Analytics Help", "query": "site:support.google.com/analytics GA4 measurement analytics", "brand": "google analytics"},
        {"name": "Contentsquare", "query": "site:contentsquare.com analytics AI experience agent journeys", "brand": "contentsquare"},
        {"name": "Air360", "query": "site:air360.io/blog analytics UX analytics product analytics", "brand": "air360"},
        {"name": "Amplitude", "query": "site:amplitude.com/blog product analytics agent analytics AI analytics", "brand": "amplitude"},
        {"name": "Mixpanel", "query": "site:mixpanel.com/blog digital analytics AI product analytics 2026", "brand": "mixpanel"},
        {"name": "Tealium", "query": "site:tealium.com/blog analytics measurement server-side tagging", "brand": "tealium"},
        {"name": "Adobe Analytics", "query": "site:experienceleague.adobe.com Adobe Analytics customer journey analytics AI", "brand": "adobe analytics"},
        {"name": "Piano Analytics", "query": "site:piano.io analytics product analytics measurement", "brand": "piano"},
        {"name": "Matomo", "query": "site:matomo.org/blog analytics privacy measurement", "brand": "matomo"},
        {"name": "Google Search Central", "query": "site:developers.google.com/search/blog AI Overviews AI Mode Search Console trends", "brand": "google search"},
        {"name": "Google Search", "query": "site:blog.google/products/search AI Overviews AI Mode search", "brand": "google"},
        {"name": "OpenAI Search", "query": "site:openai.com ChatGPT Search citations publishers search", "brand": "openai"},
        {"name": "Perplexity", "query": "site:perplexity.ai/hub/blog search citations publishers", "brand": "perplexity"},
        {"name": "Ahrefs AI Search", "query": "site:ahrefs.com/blog AI search GEO LLM citations analytics", "brand": "ahrefs"},
        {"name": "Semrush AI Search", "query": "site:semrush.com/blog AI search generative engine optimization analytics", "brand": "semrush"},
    ],
    "UX / UI": [
        {"name": "Figma", "query": "site:figma.com/blog 2026 AI design UX product design", "brand": "figma"},
        {"name": "Figma Research", "query": "site:figma.com/reports designer AI UX 2026", "brand": "figma"},
        {"name": "Nielsen Norman Group", "query": "site:nngroup.com/articles AI UX research usability interaction design", "brand": "nielsen norman"},
        {"name": "Baymard", "query": "site:baymard.com/blog UX usability ecommerce research", "brand": "baymard"},
        {"name": "Smashing Magazine", "query": "site:smashingmagazine.com UX design AI accessibility design systems", "brand": "smashing magazine"},
        {"name": "W3C WAI", "query": "site:w3.org/WAI accessibility WCAG UX emerging technology", "brand": "w3c"},
        {"name": "Deque", "query": "site:deque.com/blog accessibility AI UX axe", "brand": "deque"},
    ],
    "Convergence": [
        {"name": "Contentsquare Experience", "query": "site:contentsquare.com experience analytics AI human agent journeys experimentation", "brand": "contentsquare"},
        {"name": "Kameleoon", "query": "site:kameleoon.com/blog AI experimentation CRO prompt based experimentation", "brand": "kameleoon"},
        {"name": "AB Tasty", "query": "site:abtasty.com/blog AI experimentation CRO personalization UX analytics", "brand": "ab tasty"},
        {"name": "Optimizely", "query": "site:optimizely.com experimentation personalization analytics UX AI", "brand": "optimizely"},
        {"name": "Qualtrics", "query": "site:qualtrics.com/blog digital experience customer feedback AI UX analytics", "brand": "qualtrics"},
        {"name": "GrowthBook", "query": "site:growthbook.io/blog experimentation product analytics AI", "brand": "growthbook"},
        {"name": "PostHog", "query": "site:posthog.com/blog product analytics experimentation session replay AI", "brand": "posthog"},
    ],
}

REDDIT_FEEDS = [
    {"name": "r/webanalytics", "url": "https://www.reddit.com/r/webanalytics/new/.rss", "lane": "Web Analytics"},
    {"name": "r/analytics", "url": "https://www.reddit.com/r/analytics/new/.rss", "lane": "Web Analytics"},
    {"name": "r/TechSEO", "url": "https://www.reddit.com/r/TechSEO/new/.rss", "lane": "Web Analytics"},
    {"name": "r/UXDesign", "url": "https://www.reddit.com/r/UXDesign/new/.rss", "lane": "UX / UI"},
    {"name": "r/userexperience", "url": "https://www.reddit.com/r/userexperience/new/.rss", "lane": "UX / UI"},
    {"name": "r/ProductManagement", "url": "https://www.reddit.com/r/ProductManagement/new/.rss", "lane": "Convergence"},
]

GITHUB_RELEASE_WATCHES = [
    {"repo": "matomo-org/matomo", "name": "Matomo", "lane": "Web Analytics"},
    {"repo": "PostHog/posthog", "name": "PostHog", "lane": "Web Analytics"},
    {"repo": "GoogleChrome/web-vitals", "name": "web-vitals", "lane": "UX / UI"},
    {"repo": "GoogleChrome/lighthouse", "name": "Lighthouse", "lane": "UX / UI"},
    {"repo": "dequelabs/axe-core", "name": "axe-core", "lane": "UX / UI"},
    {"repo": "growthbook/growthbook", "name": "GrowthBook", "lane": "Convergence"},
]

LINKEDIN_WATCH_TERMS = [
    "Web Analytics AI", "Product Analytics", "Agent Analytics", "GA4", "Contentsquare",
    "AI Search Analytics", "GEO Analytics", "UX Research AI", "Figma AI", "AI UX",
    "Design Systems AI", "Experimentation AI", "CRO", "Experience Analytics",
]

LANE_TERMS = {
    "Web Analytics": [
        "web analytics", "digital analytics", "product analytics", "ga4", "google analytics",
        "contentsquare", "air360", "amplitude", "mixpanel", "tealium", "piano analytics",
        "adobe analytics", "matomo", "posthog", "bigquery", "sql", "tracking", "tagging",
        "datalayer", "data layer", "measurement", "funnel", "cohort", "retention", "activation",
        "session replay", "heatmap", "data quality", "attribution", "analytics data",
        "measurement plan", "server-side tagging", "privacy", "consent mode",
        "agent analytics", "analytics agent", "analytics copilot", "conversational analytics",
        "generative engine optimization", "llmo", "aeo", "ai search", "ai overviews",
        "ai overview", "ai mode", "chatgpt search", "perplexity", "llm citations",
        "ai citations", "answer engine optimization", "generative search", "ai referrals",
        "ai traffic", "search console", "zero-click", "zero click", "ai visibility",
        "human and agent journeys", "agent journeys",
    ],
    "UX / UI": [
        "ux research", "user research", "user experience", "ux design", "ui design",
        "product design", "figma", "usability", "prototype", "prototyping", "wireframe",
        "design system", "accessibility", "accessibilite", "wcag", "rgaa", "journey map",
        "service design", "interaction design", "user testing", "usability testing",
        "design research", "web vitals", "lighthouse", "axe-core", "ai ux",
        "ai design", "ai prototyping", "multimodal", "conversational interface",
        "conversational ux", "agentic ux", "adaptive interface", "human ai interaction",
        "design to code", "code to canvas",
    ],
    "Convergence": [
        "cro", "conversion rate optimization", "conversion optimisation", "a/b testing",
        "ab testing", "experimentation", "kameleoon", "ab tasty", "optimizely", "growthbook",
        "personalization", "personnalisation", "customer journey", "digital experience",
        "experience analytics", "friction", "conversion", "ux analytics", "behavior analytics",
        "behaviour analytics", "qualtrics", "voice of customer", "customer feedback", "nps",
        "continuous discovery", "hypothesis", "causal inference", "decisioning",
        "prompt based experimentation", "ai experimentation", "experience optimization",
        "human and agent experience",
    ],
}

EVOLUTION_TOPICS = {
    "Web Analytics": [
        {"topic": "AI / Agentic Analytics", "terms": ["agent analytics", "analytics agent", "analytics copilot", "conversational analytics"], "horizon": "2026–2028", "why": "L’analyse passe progressivement du dashboard à l’assistant capable d’explorer, diagnostiquer et recommander."},
        {"topic": "AI Search & GEO Measurement", "terms": ["ai search", "generative engine optimization", "ai referrals", "llm citations", "ai overviews", "chatgpt search"], "horizon": "2026–2028", "why": "Le Web Analyst doit mesurer les nouveaux parcours de recherche et la visibilité dans les moteurs génératifs."},
        {"topic": "Human + Agent Journeys", "terms": ["human and agent journeys", "agent journeys", "human and agent experience"], "horizon": "2026–2029", "why": "Les parcours ne concernent plus uniquement des humains : agents et assistants deviennent eux-mêmes des acteurs du parcours."},
        {"topic": "Privacy & Server-side Measurement", "terms": ["server-side tagging", "consent mode", "privacy", "data quality"], "horizon": "Maintenant", "why": "La qualité et la gouvernance de la mesure deviennent aussi importantes que le volume de données collecté."},
        {"topic": "Product Analytics", "terms": ["product analytics", "retention", "activation", "cohort", "feature adoption"], "horizon": "Maintenant", "why": "Le métier se rapproche de la décision produit : activation, rétention, adoption et impact plutôt que simple audience."},
    ],
    "UX / UI": [
        {"topic": "AI-assisted Design & Prototyping", "terms": ["ai design", "ai prototyping", "figma", "design to code", "code to canvas"], "horizon": "2026–2028", "why": "Le designer explore plus vite, prototype plus tôt et travaille davantage entre canvas, code et produit."},
        {"topic": "Human–AI Interaction", "terms": ["human ai interaction", "ai ux", "conversational ux", "conversational interface"], "horizon": "2026–2029", "why": "La conception doit couvrir confiance, contrôle, transparence, erreurs et coopération avec l’IA."},
        {"topic": "Agentic & Adaptive Interfaces", "terms": ["agentic ux", "adaptive interface", "multimodal"], "horizon": "2027–2029", "why": "Les interfaces deviennent plus adaptatives, multimodales et parfois pilotées par des agents."},
        {"topic": "Accessibility by Design", "terms": ["accessibility", "wcag", "rgaa", "axe-core"], "horizon": "Maintenant", "why": "L’accessibilité reste un socle non négociable et doit suivre les nouveaux usages IA."},
        {"topic": "Research + AI", "terms": ["ux research", "user research", "design research", "ai"], "horizon": "2026–2028", "why": "L’IA accélère la synthèse et l’exploration, mais augmente l’importance du jugement, de la méthode et de la validation humaine."},
    ],
    "Convergence": [
        {"topic": "Experience Analytics", "terms": ["experience analytics", "ux analytics", "session replay", "friction"], "horizon": "Maintenant", "why": "Quantitatif et qualitatif se rapprochent pour expliquer non seulement quoi, mais pourquoi."},
        {"topic": "AI Experimentation", "terms": ["ai experimentation", "prompt based experimentation", "experimentation", "a/b testing"], "horizon": "2026–2028", "why": "L’IA réduit le coût de création des variantes ; la valeur se déplace vers la qualité des hypothèses et de la décision."},
        {"topic": "Continuous Optimization", "terms": ["cro", "conversion", "personalization", "decisioning", "continuous discovery"], "horizon": "Maintenant", "why": "Observer → comprendre → concevoir → tester → mesurer devient une boucle continue et partagée."},
        {"topic": "Voice of Customer + Behavior", "terms": ["qualtrics", "voice of customer", "customer feedback", "behavior analytics"], "horizon": "Maintenant", "why": "Les verbatims et comportements sont combinés pour prioriser les problèmes d’expérience."},
        {"topic": "Human + Agent Experience", "terms": ["human and agent experience", "agent journeys", "digital experience"], "horizon": "2026–2029", "why": "UX et Analytics convergent pour mesurer et concevoir des expériences où humains et agents interagissent."},
    ],
}

SKILL_VOCAB = {
    "Web Analytics · Measurement & Data": ["GA4", "Google Analytics", "Adobe Analytics", "Piano Analytics", "SQL", "BigQuery", "Looker", "Looker Studio", "Matomo", "Tealium", "GTM", "Google Tag Manager", "DataLayer", "tracking", "data quality", "attribution", "measurement plan", "server-side tagging", "consent mode"],
    "Web Analytics · Product & AI": ["Amplitude", "Mixpanel", "PostHog", "product analytics", "funnel", "cohort", "retention", "activation", "feature adoption", "Agent Analytics", "AI Search", "GEO", "Generative Engine Optimization", "AI Overviews", "ChatGPT Search", "LLM citations", "AI referrals", "Search Console", "conversational analytics"],
    "UX / UI · Research & Craft": ["Figma", "UX Research", "user research", "usability testing", "wireframe", "prototype", "design system", "accessibility", "RGAA", "WCAG", "service design", "journey map", "interaction design", "product design", "Lighthouse", "web-vitals", "axe-core"],
    "UX / UI · AI & Future Interfaces": ["AI UX", "AI prototyping", "Human-AI Interaction", "conversational UX", "multimodal", "agentic UX", "adaptive interface", "design to code"],
    "Convergence UX × Analytics": ["CRO", "A/B testing", "AB Tasty", "Kameleoon", "Optimizely", "GrowthBook", "Contentsquare", "Air360", "Qualtrics", "NPS", "customer feedback", "session replay", "heatmap", "voice of customer", "friction", "experimentation", "personalization", "causal inference"],
    "Tech transverse": ["Python", "JavaScript", "HTML", "CSS", "API", "AI", "LLM", "GenAI", "automation", "GitHub", "Git", "prompt engineering"],
}


def source_query_urls() -> list[tuple[str, str, str, str]]:
    rows: list[tuple[str, str, str, str]] = []
    for lane, watches in SOURCE_WATCHES.items():
        for watch in watches:
            query = watch["query"]
            rows.append((lane, watch["name"], watch["brand"], GOOGLE_NEWS_BASE.format(query=quote_plus(query))))
    return rows


def linkedin_search_url(term: str) -> str:
    return "https://www.linkedin.com/search/results/content/?keywords=" + quote_plus(term)
