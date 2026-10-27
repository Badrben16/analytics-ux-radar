from __future__ import annotations

from urllib.parse import quote_plus

GOOGLE_NEWS_BASE = "https://news.google.com/rss/search?q={query}&hl=fr&gl=FR&ceid=FR:fr"

TOPICS = {
    "UX": [
        "UX design",
        "UX research",
        "product design",
        "design system",
        "Figma AI",
        "accessibilite numerique UX",
    ],
    "Analytics": [
        "Google Analytics GA4",
        "web analytics",
        "product analytics",
        "data quality analytics",
        "BigQuery analytics",
        "tracking analytics",
    ],
    "CRO": [
        "CRO conversion rate optimization",
        "A/B testing experimentation",
        "AB Tasty",
        "Kameleoon",
        "conversion optimisation UX",
    ],
    "IA": [
        "AI UX design",
        "AI analytics",
        "agentic analytics",
        "generative AI product design",
    ],
    "Product": [
        "product analyst",
        "product analytics",
        "product manager analytics UX",
        "feature adoption retention analytics",
    ],
    "Marché": [
        "web analyst emploi compétences",
        "product analyst emploi compétences",
        "CRO analyst emploi compétences",
        "UX designer emploi compétences",
        "UX researcher emploi compétences",
        "product designer emploi compétences",
        "digital analyst emploi compétences",
    ],
}

OFFICIAL_FEEDS = {
    # Les URLs peuvent être enrichies au fil du temps. Les erreurs d'un flux
    # n'empêchent pas le radar de fonctionner car Google News sert de filet principal.
    "Nielsen Norman Group": "https://www.nngroup.com/feed/rss/",
    "Google Analytics Blog": "https://blog.google/products/marketingplatform/analytics/rss/",
}

KEYWORDS = {
    "UX": [
        "ux", "user experience", "ux research", "usability", "design system",
        "figma", "prototype", "accessibility", "accessibilite", "product design",
        "service design", "user research", "design thinking",
    ],
    "Analytics": [
        "analytics", "ga4", "google analytics", "bigquery", "tracking", "datalayer",
        "data layer", "tagging", "measurement", "product analytics", "mixpanel",
        "amplitude", "contentsquare", "piano analytics", "adobe analytics",
    ],
    "CRO": [
        "cro", "conversion rate", "a/b test", "ab test", "experimentation",
        "optimizely", "ab tasty", "kameleoon", "conversion", "funnel",
    ],
    "IA": [
        " ai ", "artificial intelligence", "intelligence artificielle", "generative ai",
        "genai", "llm", "agentic", "copilot", "agent ia", "machine learning",
    ],
    "Product": [
        "product analyst", "product analytics", "retention", "activation", "feature adoption",
        "roadmap", "product manager", "product-led", "cohort",
    ],
    "Marché": [
        "emploi", "recrutement", "job", "career", "carriere", "compétences", "competences",
        "skills", "salary", "salaire", "hiring", "talent", "fiche de poste",
    ],
}

SKILL_VOCAB = {
    "Analytics & Data": [
        "GA4", "Google Analytics", "Adobe Analytics", "Piano Analytics", "SQL", "BigQuery",
        "Snowflake", "Databricks", "Looker", "Looker Studio", "Power BI", "Tableau",
        "Tealium", "GTM", "Google Tag Manager", "DataLayer", "tracking", "data quality",
    ],
    "Product Analytics": [
        "Amplitude", "Mixpanel", "product analytics", "funnel", "cohort", "retention",
        "activation", "feature adoption", "North Star Metric", "experimentation",
    ],
    "UX & Research": [
        "Figma", "UX Research", "user research", "usability testing", "wireframe", "prototype",
        "design system", "accessibility", "RGAA", "WCAG", "service design", "journey map",
    ],
    "CRO & Experimentation": [
        "CRO", "A/B testing", "AB Tasty", "Kameleoon", "Optimizely", "conversion rate",
        "hypothesis", "statistical significance", "multivariate testing",
    ],
    "Experience & Voice of Customer": [
        "Contentsquare", "Hotjar", "FullStory", "Qualtrics", "NPS", "customer feedback",
        "session replay", "heatmap", "voice of customer",
    ],
    "Tech & AI": [
        "Python", "JavaScript", "HTML", "CSS", "API", "AI", "LLM", "GenAI", "automation",
        "n8n", "GitHub", "Git", "prompt engineering",
    ],
    "Ways of working": [
        "Agile", "Scrum", "Jira", "Confluence", "Product Manager", "stakeholder",
        "workshop", "roadmap", "discovery", "delivery",
    ],
}


def google_news_urls() -> list[tuple[str, str, str]]:
    urls: list[tuple[str, str, str]] = []
    for category, queries in TOPICS.items():
        for query in queries:
            urls.append((category, query, GOOGLE_NEWS_BASE.format(query=quote_plus(query))))
    return urls
