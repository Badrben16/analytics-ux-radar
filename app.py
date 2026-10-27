from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

from cv_lab import analyze_cv_against_job, extract_text_from_upload, suggested_profile_angle
from insights import (
    fetch_google_trending_now,
    google_trends_explore_url,
    load_history,
    skill_mentions,
    topic_momentum,
    user_skill_gaps,
)
from learning import LEARNING_MODULES, modules_for_lane, recommend_modules
from radar import items_for_lane, lane_counts, load_news, save_news, scan_all
from source_catalog import (
    GITHUB_RELEASE_WATCHES,
    LINKEDIN_WATCH_TERMS,
    REDDIT_FEEDS,
    SKILL_VOCAB,
    SOURCE_WATCHES,
    linkedin_search_url,
)
from translation import translate_to_french

st.set_page_config(
    page_title="RadarV369 · ACE by Orange Business",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

LANES = ["Web Analytics", "UX / UI", "Convergence", "GEO / AI Search"]

st.markdown(
    """
    <style>
      :root{--orange:#ff7900;--black:#111111;--grey:#6b7280;--soft:#f5f5f5;--line:#e7e7e7;--white:#ffffff;}
      html,body,[class*="css"]{font-family:"Helvetica Neue",Arial,sans-serif;}
      .stApp{background:#ffffff;color:#111111;}
      .block-container{padding-top:1rem;padding-bottom:4rem;max-width:1540px;}
      [data-testid="stSidebar"]{background:#111111;border-right:0;}
      [data-testid="stSidebar"] *{color:#ffffff;}
      [data-testid="stSidebar"] hr{border-color:#333333;}
      [data-testid="stSidebar"] .stButton>button{background:#ff7900;color:#111111;border:0;font-weight:800;}
      [data-testid="stSidebar"] .stSlider [role="slider"]{background:#ff7900;}
      .brandbar{display:flex;align-items:center;justify-content:space-between;gap:28px;padding:8px 0 18px;border-bottom:1px solid #e7e7e7;margin-bottom:18px;}
      .brandcopy{min-width:0;}
      .brand-kicker{font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;font-weight:800;color:#ff7900;margin-bottom:6px;}
      .brand-title{font-size:2.35rem;line-height:1;font-weight:850;letter-spacing:-.045em;margin:0;}
      .brand-title span{color:#ff7900;}
      .brand-sub{font-size:.93rem;color:#6b7280;margin-top:8px;}
      .hero{background:#111111;color:#ffffff;border-radius:22px;padding:30px 34px;margin-bottom:18px;position:relative;overflow:hidden;}
      .hero:after{content:"";position:absolute;width:220px;height:220px;border:42px solid #ff7900;border-radius:50%;right:-92px;top:-104px;opacity:.96;}
      .hero h2{font-size:1.75rem;margin:0 0 8px;font-weight:850;letter-spacing:-.03em;max-width:920px;}
      .hero p{margin:0;color:#d4d4d4;max-width:960px;font-size:.97rem;}
      .story{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin:0 0 20px;}
      .story-card{border:1px solid #e7e7e7;background:#fafafa;border-radius:13px;padding:12px 13px;font-size:.82rem;font-weight:750;min-height:64px;}
      .story-card b{display:block;color:#ff7900;font-size:.72rem;margin-bottom:4px;}
      .section-kicker{font-size:.7rem;letter-spacing:.13em;text-transform:uppercase;font-weight:850;color:#ff7900;margin-bottom:5px;}
      .section-title{font-size:1.55rem;font-weight:850;letter-spacing:-.03em;margin:0 0 6px;}
      .section-desc{color:#6b7280;margin:0 0 18px;font-size:.92rem;}
      .kpi-card{border:1px solid #e7e7e7;border-radius:16px;background:#ffffff;padding:14px 16px;box-shadow:0 4px 15px rgba(0,0,0,.025);}
      .signal-card{border:1px solid #e7e7e7;border-radius:16px;background:#ffffff;padding:17px 18px;margin-bottom:10px;box-shadow:0 4px 16px rgba(0,0,0,.025);}
      .signal-card:hover{border-color:#cfcfcf;}
      .source-label{font-size:.69rem;font-weight:850;text-transform:uppercase;letter-spacing:.09em;color:#6b7280;margin-bottom:6px;}
      .signal-title{font-size:1rem;font-weight:800;line-height:1.28;margin:0 0 8px;}
      .muted{color:#6b7280;font-size:.84rem;line-height:1.42;}
      .pill{display:inline-block;background:#f1f1f1;border-radius:999px;padding:4px 9px;margin:2px 4px 2px 0;font-size:.72rem;font-weight:750;}
      .pill-orange{background:#fff0e2;color:#9a4700;}
      .score-high{color:#111111;font-weight:900;}
      .orange-line{border-left:5px solid #ff7900;background:#fff7ef;border-radius:10px;padding:13px 15px;margin:10px 0;}
      .learning-card{border:1px solid #e7e7e7;border-radius:16px;padding:18px;background:#fff;margin-bottom:12px;}
      .learning-card h4{margin:0 0 6px;font-size:1.02rem;}
      div[data-testid="stMetric"]{border:1px solid #e7e7e7;border-radius:15px;padding:10px 14px;background:#fff;}
      div[data-testid="stMetricValue"]{font-weight:900;letter-spacing:-.035em;}
      .stButton>button,.stLinkButton>a{border-radius:10px;font-weight:800;}
      .stTabs [data-baseweb="tab-list"]{gap:3px;border-bottom:1px solid #e7e7e7;overflow-x:auto;}
      .stTabs [data-baseweb="tab"]{height:46px;font-size:.87rem;font-weight:800;border-radius:9px 9px 0 0;white-space:nowrap;}
      @media(max-width:900px){.story{grid-template-columns:1fr 1fr}.brand-title{font-size:1.9rem}.hero{padding:24px}.brandbar{display:block}}
    </style>
    """,
    unsafe_allow_html=True,
)

# Header: brand lockup + platform identity.
head_logo, head_copy = st.columns([1.05, 2.95], vertical_alignment="center")
with head_logo:
    st.image("assets/ace_logo.svg", width=310)
with head_copy:
    st.markdown(
        """
        <div class="brandcopy">
          <div class="brand-kicker">Squad Intelligence Platform</div>
          <div class="brand-title">Radar<span>V369</span></div>
          <div class="brand-sub">UX · Web Analytics · CRO · GEO / AI Search · Skills Intelligence</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="hero">
      <h2>Les usages changent. Les technologies accélèrent. Les métiers UX & Analytics évoluent.</h2>
      <p>RadarV369 transforme la veille en signaux actionnables : actualités métier, outils, tendances, évolution des compétences, apprentissage et convergence UX × Analytics.</p>
    </div>
    <div class="story">
      <div class="story-card"><b>01 · USAGES</b>Nouveaux parcours, IA, selfcare, recherche conversationnelle.</div>
      <div class="story-card"><b>02 · TECHNOLOGIES</b>Analytics, Experience Analytics, experimentation, GenAI.</div>
      <div class="story-card"><b>03 · MÉTIERS</b>Web Analyst, Product Analyst, UX, CRO, GEO se transforment.</div>
      <div class="story-card"><b>04 · FRONTIÈRES</b>Data, design, research et produit se rapprochent.</div>
      <div class="story-card"><b>05 · SQUAD</b>Observer → apprendre → expérimenter → mesurer.</div>
    </div>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=1800, show_spinner=False)
def live_scan(max_per_feed: int, include_reddit: bool, include_releases: bool):
    return scan_all(
        use_gdelt=False,
        max_per_feed=max_per_feed,
        include_reddit=include_reddit,
        include_releases=include_releases,
    )


@st.cache_data(ttl=1800, show_spinner=False)
def google_trends_fr():
    return fetch_google_trending_now(20)


def fmt_date(value: str) -> str:
    try:
        dt = datetime.fromisoformat((value or "").replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y")
    except Exception:
        return ""


def score_reason(item: dict) -> list[str]:
    reasons = []
    matches = item.get("lane_matches", {}) or {}
    primary = item.get("lane", "")
    primary_hits = matches.get(primary, [])
    if primary_hits:
        reasons.append("Signaux détectés : " + ", ".join(primary_hits[:6]))
    cross = [lane for lane, terms in matches.items() if lane != primary and terms]
    if cross:
        reasons.append("Croise aussi : " + ", ".join(cross))
    if item.get("source_type") == "official-watch":
        reasons.append("Source / marque professionnelle explicitement surveillée")
    elif item.get("source_type") == "github-release":
        reasons.append("Release GitHub d’un outil suivi")
    elif item.get("source_type") == "reddit":
        reasons.append("Signal communauté Reddit ciblée")
    return reasons or ["Signal provenant d’une source curatée"]


def render_feed(rows: list[dict], key_prefix: str, translate: bool, limit: int = 45):
    if not rows:
        st.info("Aucun signal pertinent dans le snapshot actuel. Lance un nouveau scan.")
        return
    for idx, item in enumerate(rows[:limit]):
        title = item.get("title") or "Sans titre"
        if translate:
            title = translate_to_french(title)
        source = item.get("watch") or item.get("source") or "Source"
        summary = item.get("summary") or "Résumé non fourni par la source."
        if translate:
            summary = translate_to_french(summary)
        st.markdown(
            f"""
            <div class="signal-card">
              <div class="source-label">{source} · {fmt_date(item.get('published_at',''))} · pertinence {item.get('score',1)}/5</div>
              <div class="signal-title">{title}</div>
              <div>{''.join(f'<span class="pill pill-orange">{c}</span>' for c in item.get('categories',[])[:4])}</div>
              <div class="muted" style="margin-top:9px">{summary[:520]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns([1, 4])
        with c1:
            if item.get("url"):
                st.link_button("Ouvrir la source", item["url"], use_container_width=True)
        with c2:
            with st.popover("Pourquoi ce signal ?"):
                for reason in score_reason(item):
                    st.write("• " + reason)
        if idx < len(rows[:limit]) - 1:
            st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)


def skill_options() -> list[str]:
    return sorted({skill for skills in SKILL_VOCAB.values() for skill in skills}, key=str.lower)


stored = load_news()
if "news_items" not in st.session_state:
    # Old V1 snapshots had no lane and are intentionally discarded to avoid noise.
    st.session_state.news_items = [i for i in stored.get("items", []) if i.get("lane") in LANES]

with st.sidebar:
    st.markdown("## RadarV369")
    st.caption("Curated-first · sources métier uniquement")
    include_reddit = st.toggle("Communautés Reddit", value=True)
    include_releases = st.toggle("GitHub Releases", value=True)
    max_per_feed = st.slider("Profondeur par source", 2, 10, 5)
    if st.button("Scanner maintenant", type="primary", use_container_width=True):
        with st.spinner("Scan Web Analytics, UX/UI, Convergence et GEO..."):
            fresh = live_scan(max_per_feed, include_reddit, include_releases)
            st.session_state.news_items = fresh
            try:
                save_news(fresh)
            except Exception:
                pass
        st.success(f"{len(fresh)} signaux pertinents collectés")
        st.rerun()

    st.divider()
    min_score = st.slider(
        "Pertinence minimum",
        1, 5, 2,
        help="Le score mesure la proximité avec les domaines suivis et la qualité de la source. Il ne mesure pas la vérité d’un article.",
    )
    translate_default = st.toggle("Traduire en français", value=False)
    st.divider()
    st.caption("Sources : blogs ciblés + Google News restreint + Reddit métier + GitHub Releases + Google Trends.")
    if stored.get("generated_at"):
        try:
            dt = datetime.fromisoformat(stored["generated_at"].replace("Z", "+00:00"))
            st.caption(f"Snapshot repo : {dt:%d/%m/%Y %H:%M}")
        except Exception:
            pass

items = [i for i in st.session_state.news_items if i.get("lane") in LANES]
counts = lane_counts(items)
momentum = topic_momentum(items, 20) if items else []
skills = skill_mentions(items, 30) if items else []
history = load_history()

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Signaux", len(items))
k2.metric("Web Analytics", counts.get("Web Analytics", 0))
k3.metric("UX / UI", counts.get("UX / UI", 0))
k4.metric("Convergence", counts.get("Convergence", 0))
k5.metric("GEO / AI Search", counts.get("GEO / AI Search", 0))
k6.metric("Skills détectées", len(skills))

(
    overview_tab,
    analytics_tab,
    ux_tab,
    convergence_tab,
    geo_tab,
    trends_tab,
    skills_tab,
    learning_tab,
    cv_tab,
    sources_tab,
) = st.tabs([
    "Vue d’ensemble",
    "Web Analytics",
    "UX / UI",
    "Convergence",
    "GEO / AI Search",
    "Tendances",
    "Skills Radar",
    "Learning Hub",
    "CV Lab",
    "Sources",
])

with overview_tab:
    st.markdown("<div class='section-kicker'>Radar hebdomadaire</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Ce que le squad doit regarder maintenant</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-desc'>Les signaux les mieux scorés, issus uniquement des sources métier suivies.</div>", unsafe_allow_html=True)

    top = sorted([i for i in items if i.get("score", 0) >= min_score], key=lambda x: (x.get("score", 0), x.get("published_at", "")), reverse=True)[:8]
    if top:
        cols = st.columns(4)
        for idx, item in enumerate(top):
            with cols[idx % 4]:
                st.markdown(
                    f"""
                    <div class="signal-card" style="min-height:205px">
                      <div class="source-label">{item.get('lane','')} · {item.get('watch',item.get('source',''))}</div>
                      <div class="signal-title">{item.get('title','Sans titre')[:150]}</div>
                      <div class="muted">Pertinence <b>{item.get('score',1)}/5</b> · {fmt_date(item.get('published_at',''))}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if item.get("url"):
                    st.link_button("Voir", item["url"], use_container_width=True)
    else:
        st.info("Lance un scan pour afficher les signaux prioritaires.")

    c1, c2 = st.columns([1.15, 1])
    with c1:
        st.markdown("### Sujets en momentum")
        if momentum:
            df = pd.DataFrame(momentum[:10])[["term", "momentum", "mentions"]]
            df.columns = ["Sujet", "Momentum", "Mentions"]
            st.dataframe(df, hide_index=True, use_container_width=True)
        else:
            st.caption("Pas encore assez de données.")
    with c2:
        st.markdown("### Compétences visibles")
        for row in skills[:10]:
            st.write(f"**{row['skill']}** · {row['family']} · {row['mentions']} signal(s)")

    st.markdown("### Lecture stratégique")
    st.markdown(
        """
        <div class="orange-line"><b>Le radar ne cherche pas à collecter le plus d’articles possible.</b><br>
        Il cherche à détecter les changements pertinents : outils, pratiques, nouvelles attentes métier, convergence UX × Data et montée de GEO / AI Search.</div>
        """,
        unsafe_allow_html=True,
    )

with analytics_tab:
    st.markdown("<div class='section-kicker'>Métier 01</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Web Analytics & Product Analytics</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-desc'>GA4, Contentsquare, Air360, Amplitude, Mixpanel, Tealium, Adobe, Piano, Matomo, tracking, data quality, BigQuery et mesure produit.</div>", unsafe_allow_html=True)
    rows = items_for_lane(items, "Web Analytics", min_score)
    render_feed(rows, "analytics", translate_default)

with ux_tab:
    st.markdown("<div class='section-kicker'>Métier 02</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>UX / UI & Research</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-desc'>Figma, UX Research, usability, Product Design, accessibilité, design systems, tests utilisateurs et qualité d’expérience.</div>", unsafe_allow_html=True)
    rows = items_for_lane(items, "UX / UI", min_score)
    render_feed(rows, "ux", translate_default)

with convergence_tab:
    st.markdown("<div class='section-kicker'>Zone commune</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>UX × Analytics : de l’insight à l’expérimentation</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-desc'>CRO, A/B testing, Kameleoon, AB Tasty, Optimizely, Qualtrics, Experience Analytics, friction et Voice of Customer.</div>", unsafe_allow_html=True)
    st.markdown("**Observer → Comprendre → Concevoir → Tester → Mesurer → Apprendre**")
    rows = items_for_lane(items, "Convergence", min_score)
    render_feed(rows, "conv", translate_default)

with geo_tab:
    st.markdown("<div class='section-kicker'>Nouveau radar</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>GEO / AI Search</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-desc'>Generative Engine Optimization, AI Overviews, AI Mode, ChatGPT Search, Perplexity, LLM citations, AI referrals et visibilité de marque dans les moteurs génératifs.</div>", unsafe_allow_html=True)

    g1, g2, g3, g4 = st.columns(4)
    g1.metric("À mesurer", "AI referrals")
    g2.metric("À surveiller", "Citations LLM")
    g3.metric("Search", "AI Overviews")
    g4.metric("Business", "Conversion IA")
    st.markdown(
        """
        <div class="orange-line"><b>Lecture GEO pour le squad :</b> suivre d’où viennent les visites IA, quelles pages sont citées, quelles requêtes déclenchent la marque et si ces visites convertissent réellement.</div>
        """,
        unsafe_allow_html=True,
    )
    rows = items_for_lane(items, "GEO / AI Search", min_score)
    render_feed(rows, "geo", translate_default)

with trends_tab:
    st.markdown("<div class='section-kicker'>Évolution</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Tendances métier & technologies</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-desc'>Le momentum du radar mesure la répétition récente d’un sujet dans les sources surveillées. Google Trends reste un signal séparé.</div>", unsafe_allow_html=True)

    t1, t2 = st.columns([1.25, 1])
    with t1:
        st.markdown("### Momentum métier")
        if momentum:
            df = pd.DataFrame(momentum[:15])
            st.bar_chart(df.set_index("term")["momentum"])
            st.dataframe(df[["term", "mentions", "momentum"]].rename(columns={"term":"Sujet","mentions":"Mentions","momentum":"Momentum"}), hide_index=True, use_container_width=True)
        else:
            st.info("Lance un scan pour calculer les tendances.")
    with t2:
        st.markdown("### Google Trends · France")
        gt = google_trends_fr()
        if gt:
            st.caption("Trending Now est grand public : on l’affiche comme signal externe, jamais comme vérité métier.")
            for row in gt[:10]:
                st.write(f"**{row['term']}**" + (f" · {row['traffic']}" if row.get("traffic") else ""))
        else:
            st.caption("Flux Google Trends temporairement indisponible.")

    st.markdown("### Requêtes métier à comparer dans Google Trends")
    tracked = ["Product Analytics", "UX Research", "CRO", "A/B Testing", "Figma", "Contentsquare", "Kameleoon", "GA4", "GEO", "AI Search"]
    cols = st.columns(5)
    for idx, term in enumerate(tracked):
        with cols[idx % 5]:
            st.link_button(term, google_trends_explore_url(term), use_container_width=True)

    if len(history) >= 2:
        st.markdown("### Historique RadarV369")
        hist_df = pd.DataFrame([{"Date": h.get("date"), "Signaux": h.get("count", 0)} for h in history])
        if not hist_df.empty:
            st.line_chart(hist_df.set_index("Date"))

with skills_tab:
    st.markdown("<div class='section-kicker'>Skills Intelligence</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Compétences qui apparaissent dans le marché observé</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-desc'>Ce radar s’appuie sur la veille éditoriale. La prochaine brique Jobs Radar permettra de mesurer la demande recruteur séparément.</div>", unsafe_allow_html=True)

    if skills:
        skill_df = pd.DataFrame(skills)
        st.dataframe(skill_df.rename(columns={"skill":"Compétence","mentions":"Mentions","family":"Famille"}), hide_index=True, use_container_width=True)

    current_skills = st.multiselect(
        "Compétences déjà maîtrisées par le squad / profil",
        skill_options(),
        default=[],
        placeholder="GA4, Figma, SQL, Contentsquare, Kameleoon...",
    )
    gaps = user_skill_gaps(items, current_skills, top_n=15) if items else []
    if gaps:
        st.markdown("### Priorités potentielles à renforcer")
        gap_df = pd.DataFrame(gaps).rename(columns={"skill":"Compétence","mentions":"Signaux","family":"Famille"})
        st.dataframe(gap_df, hide_index=True, use_container_width=True)
        st.caption("Une compétence absente de la sélection n’est pas forcément absente du squad : ce bloc sert à ouvrir la discussion.")

with learning_tab:
    st.markdown("<div class='section-kicker'>Learning Hub</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Transformer les tendances en montée en compétences</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-desc'>Parcours courts, ressources officielles et mini-projets pour produire une preuve concrète de compétence.</div>", unsafe_allow_html=True)

    filter_lane = st.selectbox("Domaine", ["Tous"] + LANES, key="learning_lane")
    modules = modules_for_lane(filter_lane)
    for module in modules:
        st.markdown(
            f"""
            <div class="learning-card">
              <div class="source-label">{module['lane']} · {module['level']} · {module['duration']}</div>
              <h4>{module['skill']}</h4>
              <div class="muted"><b>Pourquoi :</b> {module['why']}</div>
              <div class="muted" style="margin-top:8px"><b>Mini-projet :</b> {module['project']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        rcols = st.columns(min(3, max(1, len(module["resources"]))))
        for idx, (label, url) in enumerate(module["resources"]):
            with rcols[idx % len(rcols)]:
                st.link_button(label, url, use_container_width=True)

with cv_tab:
    st.markdown("<div class='section-kicker'>Career Intelligence</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>CV Lab</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-desc'>Comparer un CV à une fiche de poste et détecter les écarts de compétences sans inventer d’expérience.</div>", unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        uploaded = st.file_uploader("CV (.pdf, .txt, .md)", type=["pdf", "txt", "md"])
        cv_paste = st.text_area("Ou colle le texte du CV", height=300)
    with right:
        job_text = st.text_area("Fiche de poste cible", height=365, placeholder="Product Analyst, CRO Analyst, UX Analyst, Web Analyst, GEO...")

    cv_text = cv_paste.strip()
    if uploaded is not None and not cv_text:
        try:
            cv_text = extract_text_from_upload(uploaded)
        except Exception as exc:
            st.error(f"Impossible de lire ce fichier : {exc}")

    if st.button("Analyser CV ↔ poste", type="primary", disabled=not (cv_text and job_text)):
        result = analyze_cv_against_job(cv_text, job_text)
        st.markdown(f"### Positionnement détecté : **{suggested_profile_angle(job_text)}**")
        st.metric("Couverture des compétences explicites", f"{result['score']} %")
        a, b = st.columns(2)
        with a:
            st.success("Compétences couvertes")
            st.write(", ".join(result["matched"]) if result["matched"] else "Aucune compétence explicite reconnue.")
        with b:
            st.warning("Compétences à vérifier / renforcer")
            st.write(", ".join(result["missing"]) if result["missing"] else "Pas de gap explicite détecté.")
        if result["gaps_by_family"]:
            st.markdown("### Gaps par famille")
            for family, values in result["gaps_by_family"].items():
                st.write(f"**{family}** — {', '.join(values)}")
        st.markdown("### Recommandations")
        for rec in result["recommendations"]:
            st.write("• " + rec)
        if result["missing"]:
            st.markdown("### Formations suggérées")
            for module in recommend_modules(result["missing"], 5):
                st.write(f"**{module['skill']}** · {module['lane']} · {module['duration']}")

with sources_tab:
    st.markdown("<div class='section-kicker'>Transparence</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Sources & méthode de collecte</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-desc'>Curated-first : la plateforme privilégie des sources nommées et refuse les requêtes génériques qui produisent du bruit.</div>", unsafe_allow_html=True)

    for lane in LANES:
        st.markdown(f"### {lane}")
        names = [w["name"] for w in SOURCE_WATCHES.get(lane, [])]
        st.write(" · ".join(names) if names else "—")

    st.markdown("### Reddit ciblé")
    st.write(" · ".join(row["name"] for row in REDDIT_FEEDS))

    st.markdown("### GitHub Releases")
    st.write(" · ".join(row["name"] for row in GITHUB_RELEASE_WATCHES))

    st.markdown("### LinkedIn Watch")
    st.caption("Pas de scraping. Ces boutons ouvrent des recherches LinkedIn ciblées ; une API officielle pourra être branchée plus tard si l’accès Community Management est approuvé.")
    lcols = st.columns(4)
    for idx, term in enumerate(LINKEDIN_WATCH_TERMS):
        with lcols[idx % 4]:
            st.link_button(term, linkedin_search_url(term), use_container_width=True)

    st.markdown("### Scoring")
    st.write(
        "La pertinence 1–5 combine : présence réelle de signaux métier dans le contenu, source professionnelle surveillée, convergence avec un autre domaine et nature de la source (blog ciblé, Reddit métier, GitHub Release)."
    )
    st.warning("Google Trends Trending Now est volontairement séparé du scoring métier : une tendance grand public n’est pas nécessairement pertinente pour le squad.")
