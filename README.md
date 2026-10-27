# RadarV369

**ACE by Orange Business · UX, Analytics, GEO & Skills Intelligence Platform**

RadarV369 est une plateforme de veille métier conçue pour un squad **UX + Analytics**.

> Les usages changent → les technologies accélèrent → les métiers évoluent → les frontières se rapprochent → le squad s’adapte.

## Ce que fait la V2

### Web Analytics
Veille ciblée sur GA4, Contentsquare, Air360, Amplitude, Mixpanel, Tealium, Adobe Analytics, Piano Analytics, Matomo, Product Analytics, tracking et data quality.

### UX / UI
Veille Figma, UX Research, usability, Product Design, accessibilité, design systems et tests utilisateurs.

### Convergence UX × Analytics
CRO, experimentation, A/B testing, Kameleoon, AB Tasty, Optimizely, Qualtrics, Experience Analytics et Voice of Customer.

### GEO / AI Search
Generative Engine Optimization, AI Overviews, AI Mode, ChatGPT Search, Perplexity, citations LLM, AI referrals et visibilité de marque dans les moteurs génératifs.

### Tendances
- momentum des sujets dans les sources surveillées ;
- Google Trends séparé du scoring métier ;
- historique quotidien jusqu’à 120 jours.

### Skills Radar
Détecte les compétences visibles dans la veille et permet de comparer avec les compétences déjà maîtrisées.

### Learning Hub
Parcours courts, ressources officielles et mini-projets autour de GA4, SQL/BigQuery, Contentsquare, CRO, Product Analytics, UX Research, Figma, accessibilité et GEO.

### CV Lab
Compare un CV avec une fiche de poste pour détecter les compétences explicites couvertes, les gaps et les axes de repositionnement.

## Sources

La V2 est **curated-first** : pas de recherche web générique.

- blogs et sites officiels / spécialisés ciblés ;
- Google News uniquement avec requêtes `site:` et marque ;
- Reddit sur communautés métier sélectionnées ;
- GitHub Releases sur outils publics suivis ;
- Google Trends ;
- LinkedIn Watch via liens de recherche ciblés, sans scraping.

GDELT n’est plus utilisé dans la V2 car il générait trop de bruit hors sujet.

## Lancer dans GitHub Codespaces

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Ouvrir ensuite le port **8501** proposé par Codespaces.

## Refresh automatique

Le workflow GitHub Actions `.github/workflows/refresh.yml` exécute un refresh en semaine, met à jour :

- `data/news.json`
- `data/history.json`

et conserve l’historique pour suivre l’évolution des sujets et compétences.

## Principes de scoring

La pertinence 1–5 est une aide au tri, pas un score de vérité.

Elle tient compte de :

- présence réelle de termes métier dans le contenu ;
- appartenance à une source professionnelle surveillée ;
- convergence avec plusieurs domaines ;
- nature de la source (curated watch, Reddit métier, GitHub Release).

## Roadmap

- [x] Flux séparés Web Analytics / UX / Convergence / GEO
- [x] Sources curated-first
- [x] Reddit ciblé
- [x] GitHub Releases
- [x] Google Trends
- [x] Skills Radar
- [x] Learning Hub
- [x] CV Lab
- [ ] Jobs Radar avec statistiques de compétences demandées
- [ ] Connecteur LinkedIn officiel si accès Community Management approuvé
- [ ] Digest Teams / email
- [ ] Benchmark concurrence
