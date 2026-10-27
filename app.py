from __future__ import annotations

import html
from datetime import datetime

import pandas as pd
import streamlit as st

from insights import (
    WORLD_TREND_BASKETS,
    google_trends_compare_url,
    google_trends_explore_url,
    load_history,
    profession_evolution,
    save_history_snapshot,
    skill_mentions,
    topic_momentum,
    user_skill_gaps,
)
from learning import modules_for_lane
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
    page_title="RadarV369 · UX × Web Analytics",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

LANES = ["Web Analytics", "UX / UI", "Convergence"]

st.markdown(
    """
    <style>
      :root{--orange:#ff7900;--black:#111;--grey:#69707a;--soft:#f6f6f6;--line:#e7e7e7;--white:#fff;}
      html,body,[class*="css"]{font-family:"Helvetica Neue",Arial,sans-serif;}
      .stApp{background:#fff;color:#111;}
      .block-container{padding-top:1rem;padding-bottom:4rem;max-width:1540px;}
      [data-testid="stSidebar"]{background:#111;border-right:0;}
      [data-testid="stSidebar"] *{color:#fff;}
      [data-testid="stSidebar"] hr{border-color:#333;}
      [data-testid="stSidebar"] .stButton>button{background:#ff7900;color:#111;border:0;font-weight:850;}
      .brand-title{font-size:2.45rem;font-weight:900;letter-spacing:-.05em;line-height:1;margin:0;}
      .brand-title span{color:#ff7900;}
      .brand-sub{color:#6b7280;margin-top:7px;font-size:.94rem;}
      .kicker{font-size:.7rem;letter-spacing:.14em;text-transform:uppercase;color:#ff7900;font-weight:900;margin-bottom:5px;}
      .hero{background:#111;color:#fff;border-radius:22px;padding:32px 34px;margin:18px 0;position:relative;overflow:hidden;}
      .hero:after{content:"";position:absolute;width:220px;height:220px;border:42px solid #ff7900;border-radius:50%;right:-95px;top:-105px;}
      .hero h2{font-size:1.8rem;letter-spacing:-.035em;max-width:940px;margin:0 0 8px;font-weight:900;}
      .hero p{color:#d5d5d5;max-width:980px;margin:0;font-size:.98rem;line-height:1.55;}
      .scope-grid{display:grid;grid-template-columns:1fr .72fr 1fr;gap:10px;margin:0 0 22px;}
      .scope-card{border:1px solid #e7e7e7;border-radius:16px;padding:16px;background:#fff;min-height:112px;}
      .scope-card.center{background:#fff7ef;border-color:#ffd3ae;}
      .scope-card b{display:block;font-size:.72rem;text-transform:uppercase;letter-spacing:.1em;color:#ff7900;margin-bottom:6px;}
      .scope-card strong{font-size:1.05rem;}
      .scope-card p{font-size:.82rem;color:#6b7280;line-height:1.42;margin:7px 0 0;}
      .section-title{font-size:1.55rem;font-weight:900;letter-spacing:-.035em;margin:0 0 5px;}
      .section-desc{color:#6b7280;font-size:.92rem;margin:0 0 18px;}
      .signal-card,.future-card,.evo-card{border:1px solid #e7e7e7;border-radius:16px;padding:17px 18px;background:#fff;margin-bottom:10px;box-shadow:0 4px 15px rgba(0,0,0,.025);}
      .signal-card:hover,.future-card:hover{border-color:#cfcfcf;}
      .source-label{font-size:.69rem;font-weight:900;text-transform:uppercase;letter-spacing:.085em;color:#6b7280;margin-bottom:6px;}
      .signal-title{font-size:1rem;font-weight:850;line-height:1.3;margin:0 0 8px;}
      .muted{color:#6b7280;font-size:.84rem;line-height:1.45;}
      .pill{display:inline-block;border-radius:999px;padding:4px 9px;margin:2px 4px 2px 0;font-size:.71rem;font-weight:800;background:#f1f1f1;}
      .pill.orange{background:#fff0e2;color:#934500;}
      .orange-line{border-left:5px solid #ff7900;background:#fff7ef;border-radius:10px;padding:13px 15px;margin:10px 0;}
      .future-score{font-weight:900;color:#ff7900;}
      div[data-testid="stMetric"]{border:1px solid #e7e7e7;border-radius:15px;padding:10px 14px;background:#fff;}
      div[data-testid="stMetricValue"]{font-weight:900;letter-spacing:-.035em;}
      .stTabs [data-baseweb="tab-list"]{gap:3px;border-bottom:1px solid #e7e7e7;overflow-x:auto;}
      .stTabs [data-baseweb="tab"]{height:46px;font-size:.87rem;font-weight:850;white-space:nowrap;}
      .stButton>button,.stLinkButton>a{border-radius:10px;font-weight:800;}
      @media(max-width:900px){.scope-grid{grid-template-columns:1fr}.brand-title{font-size:2rem}.hero{padding:24px}}
    </style>
    """,
    unsafe_allow_html=True,
)

head_logo, head_copy = st.columns([1.05, 3], vertical_alignment="center")
with head_logo:
    st.image("assets/ace_logo.svg", width=300)
with head_copy:
    st.markdown(
        """
        <div class="kicker">ACE by Orange Business · métier intelligence</div>
        <div class="brand-title">Radar<span>V369</span></div>
        <div class="brand-sub">UX / UI · Web Analytics · Convergence des deux métiers</div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="hero">
      <h2>Suivre comment UX/UI et Web Analytics évoluent — et surtout où les deux métiers se rejoignent.</h2>
      <p>
        RadarV369 ne suit plus des tendances grand public. Il observe les sources professionnelles mondiales,
        détecte les mutations de compétences et relie les signaux UX, Analytics, IA, expérimentation et mesure d’expérience.
        GEO / AI Search est intégré au métier Web Analytics.
      </p>
    </div>
    <div class="scope-grid">
      <div class="scope-card">
        <b>Métier 01</b>
        <strong>Web Analytics</strong>
        <p>Measurement, GA4, Product Analytics, data quality, AI/Agentic Analytics, AI Search/GEO et nouveaux parcours humains + agents.</p>
      </div>
      <div class="scope-card center">
        <b>Zone commune</b>
        <strong>Convergence</strong>
        <p>Experience Analytics, CRO, experimentation, VoC, friction, personnalisation et boucle insight → design → test → mesure.</p>
      </div>
      <div class="scope-card">
        <b>Métier 02</b>
        <strong>UX / UI</strong>
        <p>Research, product design, Figma, accessibility, AI-assisted design, Human–AI Interaction et interfaces agentiques/multimodales.</p>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=1800, show_spinner=False)
def live_scan(max_per_feed: int, include_reddit: bool, include_releases: bool) -> list[dict]:
    return scan_all(
        use_gdelt=False,
        max_per_feed=max_per_feed,
        include_reddit=include_reddit,
        include_releases=include_releases,
    )


def fmt_date(value: str) -> str:
    try:
        return datetime.fromisoformat((value or "").replace("Z", "+00:00")).strftime("%d/%m/%Y")
    except Exception:
        return ""


def clean(value: str) -> str:
    return html.escape(value or "", quote=False)


def render_feed(rows: list[dict], translate: bool, limit: int = 36) -> None:
    if not rows:
        st.info("Aucun signal pertinent dans le snapshot actuel. Lance un nouveau scan.")
        return
    for item in rows[:limit]:
        title = item.get("title") or "Sans titre"
        summary = item.get("summary") or "Résumé non fourni par la source."
        if translate:
            title = translate_to_french(title)
            summary = translate_to_french(summary)
        source = item.get("watch") or item.get("source") or "Source"
        categories = "".join(
            f'<span class="pill orange">{clean(category)}</span>'
            for category in item.get("categories", [])[:4]
        )
        st.markdown(
            f"""
            <div class="signal-card">
              <div class="source-label">{clean(source)} · {fmt_date(item.get('published_at',''))} · pertinence {item.get('score',1)}/5</div>
              <div class="signal-title">{clean(title)}</div>
              <div>{categories}</div>
              <div class="muted" style="margin-top:9px">{clean(summary[:600])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if item.get("url"):
            st.link_button("Ouvrir la source", item["url"])


def skill_options() -> list[str]:
    return sorted({skill for values in SKILL_VOCAB.values() for skill in values}, key=str.lower)


def evolution_table(lane: str, items: list[dict]) -> pd.DataFrame:
    rows = profession_evolution(items, lane)
    return pd.DataFrame(
        [
            {
                "Mutation": row["topic"],
                "Signal": row["status"],
                "Score Radar": row["score"],
                "30 jours": row["recent"],
                "vs période précédente": row["delta"],
                "Horizon": row["horizon"],
            }
            for row in rows
        ]
    )


stored = load_news()
if "news_items" not in st.session_state:
    st.session_state.news_items = [i for i in stored.get("items", []) if i.get("lane") in LANES]

with st.sidebar:
    st.markdown("## RadarV369")
    st.caption("UX/UI × Web Analytics · sources métier mondiales")
    include_reddit = st.toggle("Reddit métier", value=True)
    include_releases = st.toggle("GitHub Releases", value=True)
    max_per_feed = st.slider("Profondeur par source", 2, 10, 5)
    if st.button("Scanner maintenant", type="primary", use_container_width=True):
        with st.spinner("Scan mondial UX/UI, Web Analytics et Convergence..."):
            fresh = live_scan(max_per_feed, include_reddit, include_releases)
            fresh = [i for i in fresh if i.get("lane") in LANES]
            st.session_state.news_items = fresh
            try:
                save_news(fresh)
                save_history_snapshot(fresh)
            except Exception:
                pass
        st.success(f"{len(fresh)} signaux métier collectés")
        st.rerun()

    st.divider()
    min_score = st.slider("Pertinence minimum", 1, 5, 2)
    translate_default = st.toggle("Traduire en français", value=False)
    st.divider()
    st.caption("Pas de Trending Now grand public. GEO/AI Search est inclus dans Web Analytics.")

items = [i for i in st.session_state.news_items if i.get("lane") in LANES]
counts = lane_counts(items)
skills = skill_mentions(items, 40) if items else []
history = load_history()

cross_items = [
    item
    for item in items
    if item.get("lane") == "Convergence"
    or len({c for c in item.get("categories", []) if c in LANES}) >= 2
]

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Signaux", len(items))
k2.metric("Web Analytics", counts.get("Web Analytics", 0))
k3.metric("UX / UI", counts.get("UX / UI", 0))
k4.metric("Convergence", len(cross_items))
k5.metric("Skills détectées", len(skills))

(
    overview_tab,
    analytics_tab,
    ux_tab,
    convergence_tab,
    evolution_tab,
    trends_tab,
    learning_tab,
    sources_tab,
) = st.tabs(
    [
        "Radar",
        "Web Analytics",
        "UX / UI",
        "Convergence",
        "Évolution métiers",
        "Trends Monde",
        "Skills & Formations",
        "Sources",
    ]
)

with overview_tab:
    st.markdown("<div class='kicker'>Vue métier</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Ce qui change maintenant</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-desc'>Top signaux professionnels, puis lecture séparée des deux métiers et de leur zone commune.</div>",
        unsafe_allow_html=True,
    )

    top = sorted(
        [i for i in items if i.get("score", 0) >= min_score],
        key=lambda x: (x.get("score", 0), x.get("published_at", "")),
        reverse=True,
    )[:8]
    if top:
        cols = st.columns(4)
        for idx, item in enumerate(top):
            with cols[idx % 4]:
                st.markdown(
                    f"""
                    <div class="signal-card" style="min-height:190px">
                      <div class="source-label">{clean(item.get('lane',''))} · {clean(item.get('watch', item.get('source','')))}</div>
                      <div class="signal-title">{clean(item.get('title','Sans titre')[:155])}</div>
                      <div class="muted">Pertinence <b>{item.get('score',1)}/5</b> · {fmt_date(item.get('published_at',''))}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if item.get("url"):
                    st.link_button("Voir", item["url"], use_container_width=True)

    st.markdown("### Trois mutations à surveiller")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            """<div class="orange-line"><b>Web Analytics</b><br>
            Dashboard → copilots/agents · audience → product analytics · SEO classique → mesure AI Search/GEO · humains → humains + agents.</div>""",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """<div class="orange-line"><b>UX / UI</b><br>
            Écrans → interfaces conversationnelles/multimodales · prototype → canvas + code · IA de production → IA de collaboration et décision.</div>""",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """<div class="orange-line"><b>Convergence</b><br>
            Observer → comprendre → concevoir → tester → mesurer. La valeur se déplace vers la qualité des hypothèses et de la décision.</div>""",
            unsafe_allow_html=True,
        )

with analytics_tab:
    st.markdown("<div class='kicker'>Métier 01</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Web Analytics</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-desc'>Measurement, Product Analytics, qualité des données, IA/agents, AI Search/GEO et mesure des nouveaux parcours.</div>",
        unsafe_allow_html=True,
    )
    render_feed(items_for_lane(items, "Web Analytics", min_score), translate_default)

with ux_tab:
    st.markdown("<div class='kicker'>Métier 02</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>UX / UI</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-desc'>Research, design, accessibilité, Figma, AI-assisted design, Human–AI Interaction et nouvelles interfaces.</div>",
        unsafe_allow_html=True,
    )
    render_feed(items_for_lane(items, "UX / UI", min_score), translate_default)

with convergence_tab:
    st.markdown("<div class='kicker'>Zone commune</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>UX × Web Analytics</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-desc'>Là où les deux métiers se croisent : Experience Analytics, friction, VoC, CRO, expérimentation, personnalisation et décision produit.</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        """<div class="orange-line"><b>Modèle de convergence RadarV369</b><br>
        Signal quantitatif → compréhension de la friction → hypothèse UX → prototype/variante → expérimentation → mesure → apprentissage.</div>""",
        unsafe_allow_html=True,
    )
    conv_rows = [i for i in cross_items if i.get("score", 0) >= min_score]
    conv_rows = sorted(conv_rows, key=lambda x: (x.get("score", 0), x.get("published_at", "")), reverse=True)
    render_feed(conv_rows, translate_default)

with evolution_tab:
    st.markdown("<div class='kicker'>Métier intelligence</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Suivi de l’évolution des deux métiers</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-desc'>Le score Radar compare les signaux récents aux semaines précédentes dans le corpus métier. Ce n’est pas un score Google Trends.</div>",
        unsafe_allow_html=True,
    )

    for lane in LANES:
        st.markdown(f"### {lane}")
        rows = profession_evolution(items, lane)
        if rows:
            df = evolution_table(lane, items)
            st.dataframe(df, hide_index=True, use_container_width=True)
            top_rows = rows[:3]
            cols = st.columns(len(top_rows))
            for idx, row in enumerate(top_rows):
                with cols[idx]:
                    st.markdown(
                        f"""
                        <div class="evo-card">
                          <div class="source-label">{clean(row['status'])} · {clean(row['horizon'])}</div>
                          <div class="signal-title">{clean(row['topic'])}</div>
                          <div class="future-score">Radar {row['score']}/100</div>
                          <div class="muted" style="margin-top:7px">{clean(row['why'])}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.link_button("Voir dans Google Trends Monde", row["google_trends_url"], use_container_width=True)
        else:
            st.info("Lance un scan pour alimenter le suivi.")

    if history:
        st.markdown("### Historique du radar")
        hist_rows = []
        for snap in history:
            row = {"Date": snap.get("date")}
            for lane in LANES:
                row[lane] = snap.get("lanes", {}).get(lane, {}).get("count", 0)
            hist_rows.append(row)
        hist_df = pd.DataFrame(hist_rows)
        if not hist_df.empty:
            st.line_chart(hist_df.set_index("Date"))

with trends_tab:
    st.markdown("<div class='kicker'>Worldwide · métier uniquement</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Google Trends Monde — UX/UI, Web Analytics et Convergence</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-desc'>Aucun Trending Now grand public. On compare uniquement des termes structurants des deux métiers sur 5 ans, à l’échelle mondiale.</div>",
        unsafe_allow_html=True,
    )

    for lane in LANES:
        terms = WORLD_TREND_BASKETS[lane]
        st.markdown(f"### {lane}")
        st.write(" · ".join(f"**{term}**" for term in terms))
        st.link_button(
            f"Comparer ces 5 termes dans Google Trends Monde",
            google_trends_compare_url(terms),
            use_container_width=True,
        )

        momentum = topic_momentum(items, 12, lane=lane) if items else []
        if momentum:
            df = pd.DataFrame(momentum[:10])[["term", "mentions", "momentum"]]
            df.columns = ["Sujet détecté", "Mentions", "Momentum Radar"]
            st.dataframe(df, hide_index=True, use_container_width=True)
            cols = st.columns(5)
            for idx, row in enumerate(momentum[:5]):
                with cols[idx]:
                    st.link_button(
                        row["term"][:28],
                        google_trends_explore_url(row["term"]),
                        use_container_width=True,
                    )
        st.divider()

    st.caption(
        "Google Trends mesure l’intérêt de recherche mondial. Le Momentum Radar mesure la présence récente du sujet dans les sources professionnelles surveillées : les deux signaux sont complémentaires."
    )

with learning_tab:
    st.markdown("<div class='kicker'>Future skills</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Skills & formations récentes / futures</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-desc'>Priorité aux transformations 2026–2029 et aux ressources officielles : IA, agents, Human–AI Interaction, experimentation et mesure d’expérience.</div>",
        unsafe_allow_html=True,
    )

    selected_lane = st.selectbox("Domaine", ["Tous"] + LANES, index=0)
    modules = modules_for_lane(selected_lane)
    for module in modules:
        stars = "★" * int(module.get("future_score", 0))
        st.markdown(
            f"""
            <div class="future-card">
              <div class="source-label">{clean(module['lane'])} · {clean(module['level'])} · {clean(module['horizon'])}</div>
              <div class="signal-title">{clean(module['skill'])}</div>
              <div class="future-score">{stars}</div>
              <div class="muted" style="margin-top:7px"><b>Pourquoi maintenant :</b> {clean(module['why'])}</div>
              <div class="muted" style="margin-top:7px"><b>Mini-projet :</b> {clean(module['project'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        resource_cols = st.columns(min(3, max(1, len(module["resources"]))))
        for idx, (label, url) in enumerate(module["resources"]):
            with resource_cols[idx % len(resource_cols)]:
                st.link_button(label, url, use_container_width=True)

    st.markdown("### Gap de compétences du squad / profil")
    current_skills = st.multiselect(
        "Compétences déjà maîtrisées",
        skill_options(),
        default=[],
        placeholder="GA4, Figma, Contentsquare, SQL, UX Research...",
    )
    gaps = user_skill_gaps(items, current_skills, 15) if items else []
    if gaps:
        gap_df = pd.DataFrame(gaps).rename(columns={"skill": "Compétence", "mentions": "Signaux", "family": "Famille"})
        st.dataframe(gap_df, hide_index=True, use_container_width=True)

with sources_tab:
    st.markdown("<div class='kicker'>Transparence</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Sources surveillées</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-desc'>Curated-first : blogs officiels, Google News ultra ciblé, Reddit métier et GitHub Releases. Pas de GDELT ni de Trending Now généraliste.</div>",
        unsafe_allow_html=True,
    )

    for lane in LANES:
        st.markdown(f"### {lane}")
        st.write(" · ".join(w["name"] for w in SOURCE_WATCHES.get(lane, [])))

    st.markdown("### Reddit métier")
    st.write(" · ".join(row["name"] for row in REDDIT_FEEDS))

    st.markdown("### GitHub Releases")
    st.write(" · ".join(row["name"] for row in GITHUB_RELEASE_WATCHES))

    st.markdown("### LinkedIn Watch")
    st.caption("Pas de scraping : liens de recherche ciblés uniquement.")
    cols = st.columns(4)
    for idx, term in enumerate(LINKEDIN_WATCH_TERMS):
        with cols[idx % 4]:
            st.link_button(term, linkedin_search_url(term), use_container_width=True)
