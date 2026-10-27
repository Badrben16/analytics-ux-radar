from __future__ import annotations

from urllib.parse import quote_plus

GOOGLE_NEWS_BASE = "https://news.google.com/rss/search?q={query}&hl=fr&gl=FR&ceid=FR:fr"

# Curated-first: the radar follows named professional sources instead of broad
# web queries. This deliberately reduces noise and false positives.
SOURCE_WATCHES = {
    "Web Analytics": [
        {"name": "Contentsquare", "query": "site:contentsquare.com/blog Contentsquare analytics", "brand": "contentsquare"},
        {"name": "Air360", "query": "site:air360.io/blog Air360 analytics", "brand": "air360"},
        {"name": "Google Analytics", "query": "site:blog.google/products/marketingplatform Google Analytics GA4", "brand": "google analytics"},
        {"name": "Google Analytics Help", "query": "site:support.google.com/analytics GA4 analytics", "brand": "google analytics"},
        {"name": "Amplitude", "query": "site:amplitude.com/blog Amplitude product analytics", "brand": "amplitude"},
        {"name": "Mixpanel", "query": "site:mixpanel.com/blog Mixpanel product analytics", "brand": "mixpanel"},
        {"name": "Tealium", "query": "site:tealium.com/blog Tealium analytics", "brand": "tealium"},
        {"name": "Adobe Analytics", "query": "site:experienceleague.adobe.com Adobe Analytics", "brand": "adobe analytics"},
        {"name": "Piano Analytics", "query": "site:piano.io analytics product analytics", "brand": "piano"},
        {"name": "Matomo", "query": "site:matomo.org/blog analytics", "brand": "matomo"},
    ],
    "UX / UI": [
        {"name": "Figma", "query": "site:figma.com/blog Figma design UX", "brand": "figma"},
        {"name": "Nielsen Norman Group", "query": "site:nngroup.com/articles UX research usability", "brand": "nielsen norman"},
        {"name": "Baymard", "query": "site:baymard.com/blog UX usability", "brand": "baymard"},
        {"name": "Smashing Magazine", "query": "site:smashingmagazine.com UX design usability", "brand": "smashing magazine"},
        {"name": "W3C WAI", "query": "site:w3.org/WAI accessibility UX WCAG", "brand": "w3c"},
        {"name": "Deque", "query": "site:deque.com/blog accessibility UX axe", "brand": "deque"},
    ],
    "Convergence": [
        {"name": "Kameleoon", "query": "site:kameleoon.com/blog Kameleoon experimentation", "brand": "kameleoon"},
        {"name": "AB Tasty", "query": "site:abtasty.com/blog AB Tasty experimentation", "brand": "ab tasty"},
        {"name": "Optimizely", "query": "site:optimizely.com experimentation CRO analytics UX", "brand": "optimizely"},
        {"name": "Contentsquare CRO", "query": "site:contentsquare.com/blog CRO UX analytics", "brand": "contentsquare"},
        {"name": "Air360 UX Analytics", "query": "site:air360.io/blog UX analytics conversion", "brand": "air360"},
        {"name": "Qualtrics", "query": "site:qualtrics.com/blog digital experience customer feedback UX", "brand": "qualtrics"},
        {"name": "GrowthBook", "query": "site:growthbook.io/blog experimentation product analytics", "brand": "growthbook"},
    ],
    "GEO / AI Search": [
        {"name": "Google Search Central", "query": "site:developers.google.com/search/blog AI Overviews AI Mode search", "brand": "google search"},
        {"name": "Google Search", "query": "site:blog.google/products/search AI Overviews AI Mode", "brand": "google"},
        {"name": "OpenAI", "query": "site:openai.com ChatGPT Search search citations", "brand": "openai"},
        {"name": "Perplexity", "query": "site:perplexity.ai/hub/blog search citations publishers", "brand": "perplexity"},
        {"name": "Bing Webmaster", "query": "site:blogs.bing.com/webmaster AI search", "brand": "bing"},
        {"name": "Ahrefs", "query": "site:ahrefs.com/blog GEO AI search LLM SEO", "brand": "ahrefs"},
        {"name": "Semrush", "query": "site:semrush.com/blog generative engine optimization AI search", "brand": "semrush"},
    ],
}

REDDIT_FEEDS = [
    {"name": "r/webanalytics", "url": "https://www.reddit.com/r/webanalytics/new/.rss", "lane": "Web Analytics"},
    {"name": "r/analytics", "url": "https://www.reddit.com/r/analytics/new/.rss", "lane": "Web Analytics"},
    {"name": "r/UXDesign", "url": "https://www.reddit.com/r/UXDesign/new/.rss", "lane": "UX / UI"},
    {"name": "r/userexperience", "url": "https://www.reddit.com/r/userexperience/new/.rss", "lane": "UX / UI"},
    {"name": "r/ProductManagement", "url": "https://www.reddit.com/r/ProductManagement/new/.rss", "lane": "Convergence"},
    {"name": "r/SEO", "url": "https://www.reddit.com/r/SEO/new/.rss", "lane": "GEO / AI Search"},
    {"name": "r/TechSEO", "url": "https://www.reddit.com/r/TechSEO/new/.rss", "lane": "GEO / AI Search"},
]

# Public repositories with useful releases for the squad. No token is required
# for low-volume public API use, although GitHub applies anonymous rate limits.
GITHUB_RELEASE_WATCHES = [
    {"repo": "matomo-org/matomo", "name": "Matomo", "lane": "Web Analytics"},
    {"repo": "PostHog/posthog", "name": "PostHog", "lane": "Web Analytics"},
    {"repo": "GoogleChrome/web-vitals", "name": "web-vitals", "lane": "UX / UI"},
    {"repo": "GoogleChrome/lighthouse", "name": "Lighthouse", "lane": "UX / UI"},
    {"repo": "dequelabs/axe-core", "name": "axe-core", "lane": "UX / UI"},
    {"repo": "growthbook/growthbook", "name": "GrowthBook", "lane": "Convergence"},
]

# LinkedIn has no stable public RSS for arbitrary posts. We do not scrape it.
# These terms power direct LinkedIn search links in the UI.
LINKEDIN_WATCH_TERMS = [
    "Contentsquare", "Air360", "Google Analytics", "Amplitude", "Mixpanel", "Tealium",
    "Figma", "Nielsen Norman Group", "Kameleoon", "AB Tasty", "Optimizely", "Qualtrics",
    "GEO", "Generative Engine Optimization", "AI Search", "AI Overviews", "ChatGPT Search",
]

LANE_TERMS = {
    "Web Analytics": [
        "web analytics", "digital analytics", "product analytics", "ga4", "google analytics",
        "contentsquare", "air360", "amplitude", "mixpanel", "tealium", "piano analytics",
        "adobe analytics", "matomo", "posthog", "bigquery", "tracking", "tagging", "datalayer",
        "data layer", "measurement", "funnel", "cohort", "retention", "activation", "session replay",
        "heatmap", "data quality", "attribution", "analytics data", "measurement plan",
    ],
    "UX / UI": [
        "ux research", "user research", "user experience", "ux design", "ui design", "product design",
        "figma", "usability", "prototype", "wireframe", "design system", "accessibility",
        "accessibilite", "wcag", "rgaa", "journey map", "service design", "interaction design",
        "user testing", "usability testing", "design research", "web vitals", "lighthouse", "axe-core",
    ],
    "Convergence": [
        "cro", "conversion rate optimization", "conversion optimisation", "a/b testing", "ab testing",
        "experimentation", "kameleoon", "ab tasty", "optimizely", "growthbook", "personalization",
        "personnalisation", "customer journey", "digital experience", "experience analytics", "friction",
        "conversion", "ux analytics", "behavior analytics", "behaviour analytics", "qualtrics",
        "voice of customer", "customer feedback", "nps",
    ],
    "GEO / AI Search": [
        "generative engine optimization", "geo", "llmo", "aeo", "ai search", "ai overviews",
        "ai overview", "ai mode", "chatgpt search", "perplexity", "gemini search", "llm citations",
        "ai citations", "answer engine optimization", "generative search", "ai referrals", "ai traffic",
        "search console", "zero-click", "zero click", "brand visibility ai", "share of model",
    ],
}

SKILL_VOCAB = {
    "Web Analytics & Data": [
        "GA4", "Google Analytics", "Adobe Analytics", "Piano Analytics", "SQL", "BigQuery",
        "Snowflake", "Databricks", "Looker", "Looker Studio", "Power BI", "Tableau", "Matomo",
        "Tealium", "GTM", "Google Tag Manager", "DataLayer", "tracking", "data quality",
        "attribution", "measurement plan", "server-side tagging",
    ],
    "Product Analytics": [
        "Amplitude", "Mixpanel", "PostHog", "product analytics", "funnel", "cohort", "retention",
        "activation", "feature adoption", "North Star Metric", "experimentation",
    ],
    "UX / UI & Research": [
        "Figma", "UX Research", "user research", "usability testing", "wireframe", "prototype",
        "design system", "accessibility", "RGAA", "WCAG", "service design", "journey map",
        "interaction design", "product design", "Lighthouse", "web-vitals", "axe-core",
    ],
    "CRO & Experimentation": [
        "CRO", "A/B testing", "AB Tasty", "Kameleoon", "Optimizely", "GrowthBook", "conversion rate",
        "hypothesis", "statistical significance", "multivariate testing", "personalization",
    ],
    "Experience & Voice of Customer": [
        "Contentsquare", "Air360", "Hotjar", "FullStory", "Qualtrics", "NPS", "customer feedback",
        "session replay", "heatmap", "voice of customer", "friction",
    ],
    "GEO / AI Search": [
        "GEO", "Generative Engine Optimization", "AEO", "LLMO", "AI Search", "AI Overviews",
        "AI Mode", "ChatGPT Search", "Perplexity", "Search Console", "structured data", "Schema.org",
        "LLM citations", "AI visibility", "AI referrals",
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
