from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

from config import SKILL_VOCAB
from cv_lab import analyze_cv_against_job, extract_text_from_upload, suggested_profile_angle
from insights import (
    fetch_google_trending_now,
    google_trends_explore_url,
    load_history,
    save_history_snapshot,
    skill_mentions,
    topic_momentum,
    user_skill_gaps,
)
from radar import category_counts, load_news, save_news, scan_all
from translation import translate_to_french

st.set_page_config(page_title="Analytics × UX Radar", page_icon="📡", layout="wide")

st.markdown(
    """
    <style>
      :root { --orange:#ff7900; --ink:#111111; --soft:#f6f6f6; --line:#e8e8e8; --muted:#6b7280; }
      .stApp { background:#fff; }
      .block-container {padding-top:1.2rem;padding-bottom:4rem;max-width:1550px;}
      [data-testid="stSidebar"] {background:#111111;}
      [data-testid="stSidebar"] * {color:#ffffff;}
      [data-testid="stSidebar"] .stButton button {background:#ff7900;color:#111;border:0;}
      .hero {background:#111;color:#fff;padding:34px 38px;border-radius:24px;margin:4px 0 20px;position:relative;overflow:hidden;}
      .hero:after {content:"";position:absolute;width:190px;height:190px;background:#ff7900;border-radius:50%;right:-72px;top:-78px;}
      .eyebrow {font-size:.76rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#ff7900;margin-bottom:9px;}
      .hero h1 {margin:0;font-size:2.45rem;line-height:1.05;letter-spacing:-.04em;}
      .hero p {margin:12px 0 0;color:#d7d7d7;font-size:1rem;max-width:900px;}
      .story {display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin:12px 0 22px;}
      .story-step {background:#f7f7f7;border:1px solid #ededed;border-radius:14px;padding:13px;font-size:.88rem;font-weight:700;}
      .story-step b {color:#ff7900;}
      .section-kicker {color:#ff7900;font-size:.76rem;font-weight:900;text-transform:uppercase;letter-spacing:.12em;}
      .card {background:#fff;border:1px solid #e8e8e8;border-radius:18px;padding:18px 20px;height:100%;box-shadow:0 5px 18px rgba(0,0,0,.035);}
      .card h3 {font-size:1rem;margin:0 0 8px;}
      .muted {color:#6b7280;font-size:.88rem;}
      .pill {display:inline-block;border-radius:999px;padding:4px 9px;margin:2px 4px 2px 0;background:#f2f2f2;font-size:.76rem;font-weight:700;}
      .pill-orange {background:#fff0e2;color:#9a4700;}
      .score {display:inline-flex;align-items:center;gap:6px;font-weight:900;}
      .dot {width:9px;height:9px;border-radius:50%;display:inline-block;background:#ff7900;}
      .signal {border-left:5px solid #ff7900;padding:13px 16px;background:#fff7ef;border-radius:10px;margin:8px 0 14px;}
      .small-label {font-size:.72rem;color:#6b7280;text-transform:uppercase;font-weight:800;letter-spacing:.08em;}
      div[data-testid="stMetric"] {border:1px solid #ededed;padding:12px 16px;border-radius:16px;background:#fff;}
      div[data-testid="stMetricValue"] {font-weight:900;letter-spacing:-.03em;}
      .stButton>button, .stLinkButton>a {border-radius:12px;font-weight:800;}
      .stTabs [data-baseweb="tab-list"] {gap:4px;border-bottom:1px solid #ececec;}
      .stTabs [data-baseweb="tab"] {height:46px;border-radius:10px 10px 0 0;font-weight:750;}
      @media(max-width:900px){.story{grid-template-columns:1fr 1fr}.hero h1{font-size:1.9rem}}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">Squad Intelligence Platform</div>
      <h1>Analytics <span style="color:#ff7900">×</span> UX Radar</h1>
      <p>Observer le marché, détecter les évolutions, comprendre les nouvelles compétences et transformer la veille en actions pour le squad.</p>
    </div>
    <div class="story">
      <div class="story-step"><b>01</b><br>Les usages changent</div>
      <div class="story-step"><b>02</b><br>Les technologies accélèrent</div>
      <div class="story-step"><b>03</b><br>UX & Analytics évoluent</div>
      <div class="story-step"><b>04</b><br>Les frontières se rapprochent</div>
      <div class="story-step"><b>05</b><br>Le squad s'adapte</div>
    </div>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=1800, show_spinner=False)
def live_scan(use_gdelt: bool, max_per_feed: int):
    return scan_all(use_gdelt=use_gdelt, max_per_feed=max_per_feed)


@st.cache_data(ttl=1800, show_spinner=False)
def google_trends_fr():
    return fetch_google_trending_now(25)


def score_reason(item: dict) -> list[str]:
    reasons: list[str] = []
    kw = item.get("keyword_scores", {}) or {}
    if kw:
        top = sorted(kw.items(), key=lambda x: x[1], reverse=True)[:3]
        reasons.append("Mots-clés : " + ", ".join(f"{k} ({v})" for k, v in top))
    cats = item.get("categories", []) or []
    if len(cats) >= 2:
        reasons.append("Croise plusieurs domaines du squad")
    text = f"{item.get('title','')} {item.get('summary','')}".lower()
    if any(k in text for k in ("a/b", "experimentation", "contentsquare", "product analytics", "cro")):
        reasons.append("Signal expérimentation / expérience / Product Analytics")
    if item.get("source_type") == "official":
        reasons.append("Source officielle")
    return reasons or ["Correspondance thématique générale"]


stored = load_news()
if "news_items" not in st.session_state:
    st.session_state.news_items = stored.get("items", [])

with st.sidebar:
    st.markdown("## 📡 Radar Control")
    st.caption("Collecte gratuite : RSS + Google News + GDELT")
    use_gdelt = st.toggle("Inclure GDELT", value=True)
    max_per_feed = st.slider("Profondeur du scan", 2, 12, 5)
    if st.button("Scanner le web maintenant", type="primary", use_container_width=True):
        with st.spinner("Scan du marché UX, Analytics, CRO, Product et IA..."):
            items_new = live_scan(use_gdelt, max_per_feed)
            st.session_state.news_items = items_new
            try:
                save_news(items_new)
                save_history_snapshot(items_new)
            except Exception:
                pass
        st.success(f"{len(items_new)} signaux collectés")
        st.rerun()

    st.divider()
    st.markdown("### Filtres rapides")
    sidebar_min_score = st.slider(
        "Pertinence minimum",
        1, 5, 3,
        help="1 = faible correspondance aux thèmes suivis ; 5 = forte convergence de mots-clés/domaines et/ou source officielle. Ce n'est pas une note de fiabilité scientifique.",
    )
    translate_default = st.toggle("Traduire les extraits en français", value=False, help="Traduction à la demande via un service gratuit/non officiel. Le lien conserve l'article original.")
    st.divider()
    if stored.get("generated_at"):
        try:
            dt = datetime.fromisoformat(stored["generated_at"].replace("Z", "+00:00"))
            st.caption(f"Snapshot : {dt:%d/%m/%Y %H:%M}")
        except Exception:
            pass
    st.caption("⚠️ Les scores sont des aides de tri, pas des vérités de marché.")

items = st.session_state.news_items
counts = category_counts(items)
momentum = topic_momentum(items, 15) if items else []
skills = skill_mentions(items, 15) if items else []

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Signaux", len(items))
m2.metric("UX", counts.get("UX", 0))
m3.metric("Analytics", counts.get("Analytics", 0))
m4.metric("CRO", counts.get("CRO", 0))
m5.metric("IA", counts.get("IA", 0))
m6.metric("Compétences détectées", len(skills))

(dashboard_tab, news_tab, trends_tab, skills_tab, convergence_tab, cv_tab, source_tab) = st.tabs([
    "🏠 Vue squad", "📰 Actualités", "📈 Tendances", "🎯 Compétences", "🤝 UX × Analytics", "🧭 CV Lab", "⚙️ Méthode"
])

with dashboard_tab:
    st.markdown("<div class='section-kicker'>Cette semaine</div>", unsafe_allow_html=True)
    st.subheader("Les signaux à regarder en priorité")
    if not items:
        st.info("Lance un scan depuis la barre latérale pour alimenter le radar.")
    else:
        top_items = sorted(items, key=lambda x: x.get("score", 0), reverse=True)[:6]
        cols = st.columns(3)
        for i, item in enumerate(top_items):
            with cols[i % 3]:
                cats = " ".join(f"<span class='pill'>{c}</span>" for c in item.get("categories", [])[:3])
                st.markdown(
                    f"<div class='card'><div class='small-label'>{item.get('source','Source')}</div>"
                    f"<h3>{item.get('title','Sans titre')}</h3>{cats}"
                    f"<p class='muted'>Pertinence <b>{item.get('score',1)}/5</b></p></div>",
                    unsafe_allow_html=True,
                )
                if item.get("url"):
                    st.link_button("Ouvrir", item["url"], use_container_width=True)

        c1, c2 = st.columns([1.2, 1])
        with c1:
            st.markdown("### 🔥 Momentum métier")
            if momentum:
                df = pd.DataFrame(momentum[:10])[["term", "momentum", "mentions"]].rename(columns={"term":"Sujet","momentum":"Momentum","mentions":"Mentions"})
                st.dataframe(df, hide_index=True, use_container_width=True)
        with c2:
            st.markdown("### 🎯 Compétences les plus visibles")
            for row in skills[:8]:
                st.markdown(f"**{row['skill']}** · {row['family']} — {row['mentions']} signaux")

with news_tab:
    st.subheader("Actualités & évolutions")
    st.caption("Le radar agrège des signaux. Les articles restent accessibles dans leur source originale.")
    if not items:
        st.info("Aucune donnée. Lance un scan.")
    else:
        c1, c2, c3 = st.columns([2, 1.2, 1])
        search = c1.text_input("Rechercher", placeholder="GA4, Figma, CRO, Product Analytics, accessibilité...")
        all_categories = sorted({c for item in items for c in item.get("categories", [])})
        selected_categories = c2.multiselect("Domaines", all_categories, default=[])
        sort_mode = c3.selectbox("Trier par", ["Date", "Pertinence"])

        filtered = []
        for item in items:
            hay = f"{item.get('title','')} {item.get('summary','')} {item.get('source','')}".lower()
            if search and search.lower() not in hay:
                continue
            if selected_categories and not set(selected_categories).intersection(item.get("categories", [])):
                continue
            if item.get("score", 0) < sidebar_min_score:
                continue
            filtered.append(item)
        if sort_mode == "Pertinence":
            filtered.sort(key=lambda x: (x.get("score", 0), x.get("published_at", "")), reverse=True)

        st.caption(f"{len(filtered)} éléments · seuil de pertinence : {sidebar_min_score}/5")
        for item in filtered[:100]:
            title = item.get("title") or "Sans titre"
            display_title = translate_to_french(title) if translate_default else title
            with st.expander(f"{item.get('score',1)}/5 · {display_title}"):
                tags = " ".join(f"<span class='pill pill-orange'>{c}</span>" for c in item.get("categories", []))
                st.markdown(tags, unsafe_allow_html=True)
                summary = item.get("summary") or "Résumé non fourni par la source."
                if translate_default:
                    summary = translate_to_french(summary)
                st.write(summary)
                with st.popover("Pourquoi ce score ?"):
                    st.write("Le score de pertinence sert uniquement à prioriser les signaux pour le squad.")
                    for reason in score_reason(item):
                        st.write(f"• {reason}")
                st.caption(f"{item.get('source','')} · {item.get('domain','')} · requête : {item.get('query','')}")
                if item.get("url"):
                    st.link_button("Lire l'article original", item["url"])

with trends_tab:
    st.subheader("Tendances & signaux émergents")
    st.write("On sépare ici la **popularité éditoriale** du radar et la **popularité de recherche** Google Trends.")
    t1, t2 = st.columns([1.2, 1])
    with t1:
        st.markdown("### Momentum dans notre veille")
        if momentum:
            df = pd.DataFrame(momentum)
            st.bar_chart(df.set_index("term")["momentum"])
            for row in momentum[:8]:
                st.markdown(f"**{row['term']}** — momentum {row['momentum']}/100 · [voir dans Google Trends]({row['google_trends_url']})")
        else:
            st.info("Lance un scan pour calculer le momentum.")

    with t2:
        st.markdown("### Google Trends · France")
        gt = google_trends_fr()
        if gt:
            st.caption("Trending Now grand public. Ce n'est pas limité à l'UX/Analytics.")
            for row in gt[:12]:
                traffic = f" · {row['traffic']}" if row.get('traffic') else ""
                st.markdown(f"**{row['term']}**{traffic}")
        else:
            st.warning("Le flux Google Trends n'est pas disponible pour le moment.")

    st.markdown("### Mots-clés métier à suivre dans Google Trends")
    tracked = ["Product Analytics", "UX Research", "CRO", "A/B Testing", "Figma", "Contentsquare", "GA4", "Amplitude"]
    cols = st.columns(4)
    for i, term in enumerate(tracked):
        with cols[i % 4]:
            st.link_button(term, google_trends_explore_url(term), use_container_width=True)

    st.info("Google ne fournit pas encore d'API Trends publique générale. Le radar utilise le flux Trending Now et des liens Explore ; on pourra brancher une API alpha/tiers plus tard sans changer l'interface.")

with skills_tab:
    st.subheader("Compétences à surveiller et à renforcer")
    st.caption("Ici, la fréquence vient du corpus de veille. Pour mesurer précisément la demande recruteur, le prochain module devra analyser un corpus d'offres d'emploi.")
    if not skills:
        st.info("Lance un scan pour détecter les compétences.")
    else:
        skill_df = pd.DataFrame(skills)
        st.dataframe(skill_df.rename(columns={"skill":"Compétence","mentions":"Signaux","family":"Famille"}), hide_index=True, use_container_width=True)
        all_skills = sorted({s for values in SKILL_VOCAB.values() for s in values}, key=str.lower)
        current = st.multiselect("Mes compétences actuelles", all_skills, placeholder="Sélectionne ce que tu maîtrises déjà...")
        if current:
            gaps = user_skill_gaps(items, current, 12)
            st.markdown("### Priorités potentielles")
            if gaps:
                for idx, row in enumerate(gaps, start=1):
                    priority = "Haute" if idx <= 4 else "Moyenne"
                    st.markdown(f"**{idx}. {row['skill']}** — {row['family']} · {row['mentions']} signaux · priorité **{priority}**")
            else:
                st.success("Tes compétences sélectionnées couvrent les principaux signaux détectés dans ce snapshot.")

        st.markdown("### Comment lire cette page")
        st.markdown("**Répétition dans les actualités ≠ demande d'emploi.** Elle permet de détecter les sujets émergents. Le CV Lab, lui, compare directement à une offre réelle.")

with convergence_tab:
    st.subheader("La zone de convergence UX × Analytics")
    st.markdown("<div class='signal'><b>Objectif :</b> passer de « UX fait les écrans / Analytics fait les chiffres » à <b>Observer → Comprendre → Concevoir → Tester → Mesurer → Apprendre</b>.</div>", unsafe_allow_html=True)
    convergence = [item for item in items if len(item.get("categories", [])) >= 2 or {"CRO", "Product"}.intersection(item.get("categories", []))]
    convergence = sorted(convergence, key=lambda x: (x.get("score", 0), x.get("published_at", "")), reverse=True)
    for item in convergence[:30]:
        st.markdown(f"**{item.get('score',1)}/5 — [{item.get('title','Sans titre')}]({item.get('url','#')})**")
        st.caption(f"{' · '.join(item.get('categories', []))} · {item.get('source','')}")

with cv_tab:
    st.subheader("CV Lab — marché → compétences → adaptation")
    st.write("Compare ton CV à une offre cible. Le moteur n'invente aucune expérience : il détecte les compétences couvertes et celles qu'il faut prouver ou apprendre.")
    left, right = st.columns(2)
    with left:
        uploaded = st.file_uploader("CV (.pdf, .txt, .md)", type=["pdf", "txt", "md"])
        cv_paste = st.text_area("Ou colle le texte du CV", height=280)
    with right:
        job_text = st.text_area("Fiche de poste cible", height=345, placeholder="Colle ici l'offre Product Analyst, CRO Analyst, UX Analyst...")
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
            st.success("Déjà couvert")
            st.write(", ".join(result["matched"]) if result["matched"] else "Aucune compétence reconnue.")
        with b:
            st.warning("À renforcer / prouver")
            st.write(", ".join(result["missing"]) if result["missing"] else "Pas de gap explicite détecté.")
        if result["gaps_by_family"]:
            st.markdown("### Gaps par famille")
            for family, gap_skills in result["gaps_by_family"].items():
                st.write(f"**{family}** — {', '.join(gap_skills)}")
        st.markdown("### Recommandations")
        for rec in result["recommendations"]:
            st.write(f"- {rec}")

with source_tab:
    st.subheader("Méthode & transparence")
    st.markdown("""
    **Pertinence 1–5**  
    Score heuristique de tri : mots-clés du squad + convergence entre domaines + bonus expérimentation/Product Analytics/CRO + bonus source officielle. Il ne mesure ni la vérité d'un article ni sa popularité.

    **Momentum 0–100**  
    Répétition des termes dans le corpus, pondérée par récence. Un sujet cité plusieurs fois récemment monte plus haut.

    **Google Trends**  
    Le module gratuit exploite le flux public *Trending Now France* et ouvre les mots-clés métier dans Google Trends Explore. Les valeurs Google Trends sont relatives et ne sont pas des volumes absolus.

    **Traduction**  
    La traduction FR porte sur les titres/extraits affichés, jamais sur une reproduction intégrale de l'article. Le lien ouvre toujours la source originale.

    **Compétences**  
    Le Skill Radar compte les compétences visibles dans la veille. Pour une analyse de recrutement robuste, on ajoutera un corpus spécifique d'offres d'emploi.
    """)
    history = load_history()
    st.markdown(f"### Historique disponible : **{len(history)} snapshot(s)**")
