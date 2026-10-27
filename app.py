from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

from cv_lab import analyze_cv_against_job, extract_text_from_upload, suggested_profile_angle
from radar import category_counts, load_news, save_news, scan_all, trend_terms

st.set_page_config(
    page_title="Analytics × UX Radar",
    page_icon="📡",
    layout="wide",
)

st.markdown(
    """
    <style>
      :root { --orange:#ff7900; --ink:#111; --muted:#6b7280; }
      .block-container {padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1500px;}
      .hero {background:#111;color:white;padding:28px 32px;border-radius:18px;margin-bottom:18px;}
      .hero h1 {margin:0 0 6px 0;font-size:2.2rem;}
      .hero b {color:#ff7900;}
      .muted {color:#6b7280;font-size:.9rem;}
      .signal {border-left:5px solid #ff7900;padding:12px 16px;background:#fff8f1;border-radius:8px;margin:8px 0;}
      div[data-testid="stMetricValue"] {font-weight:800;}
      .stButton>button {border-radius:10px;font-weight:700;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1>Analytics <b>×</b> UX Radar</h1>
      <div>Les usages changent → les technologies changent → les métiers évoluent → le squad s'adapte.</div>
    </div>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=1800, show_spinner=False)
def live_scan(use_gdelt: bool, max_per_feed: int):
    return scan_all(use_gdelt=use_gdelt, max_per_feed=max_per_feed)


stored = load_news()
if "news_items" not in st.session_state:
    st.session_state.news_items = stored.get("items", [])

with st.sidebar:
    st.header("📡 Scan")
    use_gdelt = st.toggle("Inclure GDELT", value=True, help="Élargit la recherche au-delà de Google News RSS.")
    max_per_feed = st.slider("Articles par requête", 2, 12, 5)
    if st.button("Scanner le web maintenant", type="primary", use_container_width=True):
        with st.spinner("Scan UX, Analytics, CRO, Product et IA..."):
            items = live_scan(use_gdelt, max_per_feed)
            st.session_state.news_items = items
            try:
                save_news(items)
            except Exception:
                pass
        st.success(f"{len(items)} signaux collectés")

    st.divider()
    st.caption("La collecte de base fonctionne sans clé API payante.")
    if stored.get("generated_at"):
        try:
            dt = datetime.fromisoformat(stored["generated_at"].replace("Z", "+00:00"))
            st.caption(f"Dernier snapshot : {dt:%d/%m/%Y %H:%M}")
        except Exception:
            pass

items = st.session_state.news_items
counts = category_counts(items)

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Signaux", len(items))
m2.metric("UX", counts.get("UX", 0))
m3.metric("Analytics", counts.get("Analytics", 0))
m4.metric("CRO", counts.get("CRO", 0))
m5.metric("IA", counts.get("IA", 0))

radar_tab, trends_tab, convergence_tab, cv_tab, source_tab = st.tabs(
    ["📰 Radar", "📈 Évolutions", "🤝 UX × Analytics", "🧭 CV Lab", "⚙️ Sources"]
)

with radar_tab:
    st.subheader("Actualités & signaux marché")
    if not items:
        st.info("Clique sur **Scanner le web maintenant** pour alimenter le radar.")
    else:
        c1, c2, c3 = st.columns([2, 1, 1])
        search = c1.text_input("Rechercher", placeholder="GA4, Figma, CRO, Product Analytics...")
        all_categories = sorted({c for item in items for c in item.get("categories", [])})
        selected_categories = c2.multiselect("Domaines", all_categories, default=[])
        min_score = c3.selectbox("Score minimum", [1, 2, 3, 4, 5], index=2)

        filtered = []
        for item in items:
            hay = f"{item.get('title','')} {item.get('summary','')} {item.get('source','')}".lower()
            if search and search.lower() not in hay:
                continue
            if selected_categories and not set(selected_categories).intersection(item.get("categories", [])):
                continue
            if item.get("score", 0) < min_score:
                continue
            filtered.append(item)

        st.caption(f"{len(filtered)} éléments affichés")
        for item in filtered[:120]:
            tags = " · ".join(item.get("categories", []))
            title = item.get("title") or "Sans titre"
            with st.expander(f"{item.get('score', 1)}/5 · {title}"):
                st.markdown(f"**{tags}**  ")
                st.write(item.get("summary") or "Résumé non fourni par la source.")
                meta = f"Source : {item.get('source','')} · {item.get('domain','')} · requête : {item.get('query','')}"
                st.caption(meta)
                if item.get("url"):
                    st.link_button("Lire la source", item["url"])

with trends_tab:
    st.subheader("Ce qui monte dans les deux métiers")
    if not items:
        st.info("Lance un scan pour calculer les tendances.")
    else:
        terms = trend_terms(items, top_n=25)
        if terms:
            df = pd.DataFrame(terms, columns=["Terme", "Mentions"])
            st.bar_chart(df.set_index("Terme"))

        st.markdown("### Lecture métier")
        top_terms = [name for name, _ in terms[:8]]
        st.markdown(
            "<div class='signal'><b>Signal actuel :</b> "
            + (", ".join(top_terms) if top_terms else "pas encore assez de données")
            + ".</div>",
            unsafe_allow_html=True,
        )
        st.write(
            "Le radar ne cherche pas seulement des articles : il compte la répétition des technologies, méthodes et compétences. "
            "Avec un historique de plusieurs semaines, ce bloc devient un indicateur d'évolution du marché."
        )

        cat_df = pd.DataFrame(list(category_counts(items).items()), columns=["Domaine", "Volume"])
        if not cat_df.empty:
            st.markdown("### Répartition des signaux")
            st.bar_chart(cat_df.set_index("Domaine"))

with convergence_tab:
    st.subheader("La zone de convergence UX × Analytics")
    st.write(
        "Les signaux les plus intéressants pour le squad sont ceux qui touchent plusieurs disciplines : comportement, "
        "expérimentation, Product Analytics, CRO, IA et mesure de l'expérience."
    )
    convergence = [
        item for item in items
        if len(item.get("categories", [])) >= 2
        or {"CRO", "Product"}.intersection(item.get("categories", []))
    ]
    convergence = sorted(convergence, key=lambda x: x.get("score", 0), reverse=True)
    for item in convergence[:30]:
        st.markdown(
            f"**{item.get('score',1)}/5 — [{item.get('title','Sans titre')}]({item.get('url','#')})**  \n"
            f"{' · '.join(item.get('categories', []))} · {item.get('source','')}"
        )
        if item.get("summary"):
            st.caption(item["summary"][:280])

with cv_tab:
    st.subheader("CV Lab — adapter son positionnement au marché")
    st.write(
        "Colle une fiche de poste puis ton CV. Le Radar compare les compétences explicites et propose les priorités d'adaptation. "
        "Le CV n'est pas envoyé à un service externe par cette V1."
    )

    left, right = st.columns(2)
    with left:
        uploaded = st.file_uploader("CV (.pdf, .txt, .md)", type=["pdf", "txt", "md"])
        cv_paste = st.text_area("Ou colle le texte du CV", height=300)
    with right:
        job_text = st.text_area("Fiche de poste cible", height=365, placeholder="Colle ici l'offre Product Analyst, CRO Analyst, UX Analyst...")

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
            st.success("Compétences déjà couvertes")
            st.write(", ".join(result["matched"]) if result["matched"] else "Aucune compétence reconnue dans le vocabulaire V1.")
        with b:
            st.warning("Compétences à vérifier / renforcer")
            st.write(", ".join(result["missing"]) if result["missing"] else "Pas de gap explicite détecté.")

        if result["gaps_by_family"]:
            st.markdown("### Gaps par famille")
            for family, skills in result["gaps_by_family"].items():
                st.write(f"**{family}** — {', '.join(skills)}")

        st.markdown("### Recommandations d'adaptation")
        for rec in result["recommendations"]:
            st.write(f"- {rec}")

        if result["missing"]:
            st.markdown("### Plan de formation prioritaire")
            st.write(
                "1. Traiter d'abord les compétences demandées à plusieurs reprises dans les offres.  \n"
                "2. Produire une preuve : mini-projet, analyse, dashboard, A/B test ou étude de cas.  \n"
                "3. Ajouter ensuite la compétence au CV avec un résultat concret, pas comme simple mot-clé."
            )

with source_tab:
    st.subheader("Sources & fonctionnement")
    st.markdown(
        """
        **Collecte actuelle**
        - Google News RSS sur des requêtes UX, Analytics, CRO, Product et IA.
        - GDELT DOC 2.0 en complément, sans token.
        - Quelques flux officiels configurables dans `config.py`.

        **Scoring**
        - correspondance avec les mots-clés du squad ;
        - bonus si plusieurs domaines convergent ;
        - bonus expérimentation / Product Analytics / CRO ;
        - bonus source officielle.

        **Prochaines briques**
        - Job & Skills Radar avec collecte des offres ;
        - benchmark concurrence ;
        - Learning Hub avec formations associées aux gaps ;
        - résumé IA optionnel ;
        - digest Teams / email.
        """
    )
