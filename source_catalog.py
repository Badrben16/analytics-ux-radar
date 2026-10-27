from __future__ import annotations

from urllib.parse import quote_plus

GOOGLE_NEWS_BASE = "https://news.google.com/rss/search?q={query}&hl=fr&gl=FR&ceid=FR:fr"

# Le radar est volontairement CURATED-FIRST : on suit des éditeurs et communautés métier,
# plutôt que de lancer des requêtes UX/Analytics trop larges dans tout Google News.
SOURCE_WATCHES = {
    "Web Analytics": [
        {"name": "Contentsquare", "query": "site:contentsquare.com/blog Contentsquare", "brand": "contentsquare"},
        {"name": "Air360", "query": "site:air360.io/blog Air360", "brand": "air360"},
        {"name": "Google Analytics", "query": "site:blog.google Google Analytics GA4", "brand": "google analytics"},
        {"name": "Amplitude", "query": "site:amplitude.com/blog Amplitude analytics", "brand": "amplitude"},
        {"name": "Mixpanel", "query": "site:mixpanel.com/blog Mixpanel analytics", "brand": "mixpanel"},
        {"name": "Tealium", "query": "site:tealium.com/blog Tealium analytics", "brand": "tealium"},
        {"name": "Adobe Analytics", "query": "site:experienceleague.adobe.com Adobe Analytics", "brand": "adobe analytics"},
        {"name": "Piano Analytics", "query": "site:piano.io analytics product analytics", "brand": "piano"},
    ],
    "UX / UI": [
        {"name": "Figma", "query": "site:figma.com/blog Figma design UX", "brand": "figma"},
        {"name": "Nielsen Norman Group", "query": "site:nngroup.com/articles UX research usability", "brand": "nielsen norman"},
        {"name": "Baymard", "query": "site:baymard.com/blog UX ecommerce", "brand": "baymard"},
        {"name": "Smashing Magazine", "query": "site:smashingmagazine.com UX design usability", "brand": "smashing magazine"},
        {"name": "W3C WAI", "query": "site:w3.org/WAI accessibility UX", "brand": "w3c"},
    ],
    "Convergence": [
        {"name": "Kameleoon", "query": "site:kameleoon.com/blog Kameleoon experimentation", "brand": "kameleoon"},
        {"name": "AB Tasty", "query": "site:abtasty.com/blog AB Tasty experimentation", "brand": "ab tasty"},
        {"name": "Optimizely", "query": "site:optimizely.com experimentation CRO analytics UX", "brand": "optimizely"},
        {"name": "Contentsquare CRO", "query": "site:contentsquare.com/blog CRO UX analytics", "brand": "contentsquare"},
        {"name": "Air360 UX Analytics", "query": "site:air360.io/blog UX analytics conversion", "brand": "air360"},
        {"name": "Mixpanel Design + Analytics", "query": "site:mixpanel.com/blog designers product analytics UX", "brand": "mixpanel"},
    ],
}

REDDIT_FEEDS = [
    {"name": "r/webanalytics", "url": "https://www.reddit.com/r/webanalytics/new/.rss", "lane": "Web Analytics"},
    {"name": "r/analytics", "url": "https://www.reddit.com/r/analytics/new/.rss", "lane": "Web Analytics"},
    {"name": "r/UXDesign", "url": "https://www.reddit.com/r/UXDesign/new/.rss", "lane": "UX / UI"},
    {"name": "r/userexperience", "url": "https://www.reddit.com/r/userexperience/new/.rss", "lane": "UX / UI"},
    {"name": "r/ProductManagement", "url": "https://www.reddit.com/r/ProductManagement/new/.rss", "lane": "Convergence"},
]

# LinkedIn ne fournit pas de RSS public stable pour les posts. On ne scrape pas LinkedIn.
# L'interface propose des recherches directes pour les marques suivies.
LINKEDIN_WATCH_TERMS = [
    "Contentsquare", "Air360", "Google Analytics", "Amplitude", "Mixpanel", "Tealium",
    "Figma", "Nielsen Norman Group", "Kameleoon", "AB Tasty", "Optimizely",
]

LANE_TERMS = {
    "Web Analytics": [
        "web analytics", "digital analytics", "product analytics", "ga4", "google analytics",
        "contentsquare", "air360", "amplitude", "mixpanel", "tealium", "piano analytics",
        "adobe analytics", "bigquery", "tracking", "tagging", "datalayer", "data layer",
        "measurement", "funnel", "cohort", "retention", "activation", "session replay",
        "heatmap", "data quality", "attribution", "analytics data",
    ],
    "UX / UI": [
        "ux research", "user research", "user experience", "ux design", "ui design", "product design",
        "figma", "usability", "prototype", "wireframe", "design system", "accessibility",
        "accessibilite", "wcag", "rgaa", "journey map", "service design", "interaction design",
        "user testing", "usability testing", "design research",
    ],
    "Convergence": [
        "cro", "conversion rate optimization", "conversion optimisation", "a/b testing", "ab testing",
        "experimentation", "kameleoon", "ab tasty", "optimizely", "personalization", "personnalisation",
        "customer journey", "digital experience", "experience analytics", "friction", "conversion",
        "product analytics", "ux analytics", "behavior analytics", "behaviour analytics", "qualtrics",
        "voice of customer", "customer feedback", "nps",
    ],
}

SKILL_VOCAB = {
    "Web Analytics & Data": [
        "GA4", "Google Analytics", "Adobe Analytics", "Piano Analytics", "SQL", "BigQuery",
        "Snowflake", "Databricks", "Looker", "Looker Studio", "Power BI", "Tableau",
        "Tealium", "GTM", "Google Tag Manager", "DataLayer", "tracking", "data quality",
        "attribution", "measurement plan",
    ],
    "Product Analytics": [
        "Amplitude", "Mixpanel", "product analytics", "funnel", "cohort", "retention",
        "activation", "feature adoption", "North Star Metric", "experimentation",
    ],
    "UX / UI & Research": [
        "Figma", "UX Research", "user research", "usability testing", "wireframe", "prototype",
        "design system", "accessibility", "RGAA", "WCAG", "service design", "journey map",
        "interaction design", "product design",
    ],
    "CRO & Experimentation": [
        "CRO", "A/B testing", "AB Tasty", "Kameleoon", "Optimizely", "conversion rate",
        "hypothesis", "statistical significance", "multivariate testing", "personalization",
    ],
    "Experience & Voice of Customer": [
        "Contentsquare", "Air360", "Hotjar", "FullStory", "Qualtrics", "NPS", "customer feedback",
        "session replay", "heatmap", "voice of customer", "friction",
    ],
    "Tech & AI": [
        "Python", "JavaScript", "HTML", "CSS", "API", "AI", "LLM", "GenAI", "automation",
        "n8n", "GitHub", "Git", "prompt engineering", "agentic analytics",
    ],
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
