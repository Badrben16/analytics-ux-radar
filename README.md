# Analytics × UX Radar

Plateforme de veille pour un squad **UX + Analytics**.

## Objectif

Suivre automatiquement :
- les actualités UX, Product Design, UX Research, accessibilité et design systems ;
- les actualités Web Analytics, Product Analytics, CRO, A/B testing, tracking et data quality ;
- les technologies et outils qui font évoluer les deux métiers ;
- les signaux de convergence UX × Analytics ;
- les compétences qui montent dans le marché ;
- l'adéquation d'un CV avec une fiche de poste cible.

## Fonctionnalités V1

- Scan web gratuit via **Google News RSS** et flux RSS officiels.
- Catégorisation automatique : UX, Analytics, CRO, IA, Product, Accessibilité.
- Score de pertinence pour le squad.
- Détection de tendances par fréquence des mots-clés.
- Dashboard Streamlit avec filtres, recherche et liens vers les sources.
- Onglet **CV Lab** : comparaison CV ↔ fiche de poste, score de couverture et compétences manquantes.
- Script de refresh réutilisable pour automatiser la collecte.
- Workflow GitHub Actions planifié chaque matin.

## Lancer en local

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## Sources gratuites

La V1 n'a besoin d'aucune clé API pour fonctionner :
- Google News RSS (requêtes thématiques)
- RSS officiels déclarés dans `config.py`

Les connecteurs GDELT/Jobs pourront être ajoutés ensuite dans le même pipeline.

## Automatisation

Le workflow `.github/workflows/refresh.yml` lance `scripts/refresh.py` chaque matin et met à jour `data/news.json` si de nouveaux éléments sont trouvés.

## CV Lab

Le CV reste traité dans la session Streamlit. La V1 accepte :
- texte collé ;
- fichier `.txt` / `.md` ;
- PDF texte via `pypdf`.

Le score est une aide à la lecture, pas une décision de recrutement.

## Roadmap

- [x] Radar UX + Analytics
- [x] Scan RSS / Google News
- [x] Tendances et scoring
- [x] CV Lab
- [ ] Offres d'emploi et Skills Radar
- [ ] Veille concurrence / benchmark parcours
- [ ] Résumés IA optionnels
- [ ] Digest Teams / email
- [ ] Historique mensuel et évolution des compétences
