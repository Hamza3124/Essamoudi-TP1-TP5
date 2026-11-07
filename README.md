# sentiment-app : Application fil rouge (TP1 à TP5)

Application fil rouge du cours *Développement et déploiement d'applications intelligentes*.
Ce dépôt regroupe l'implémentation complète des **5 premiers travaux pratiques (TP1 à TP5)**, couvrant l'ensemble du cycle de vie d'un composant d'intelligence artificielle : du cadrage métier jusqu'au déploiement d'une interface utilisateur supervisée.

---

## Les 5 Travaux Pratiques couverts

| TP | Sujet | Composants clés | Statut & Tests |
| --- | --- | --- | --- |
| **TP1** | **Cadrage et Environnement** | Fiches de cadrage argumentées (`docs/cadrage/`), structure du projet, configuration Git et CI initiale. | 34 tests passants (`test_cadrage.py`, `test_environment.py`, `test_git_history.py`) |
| **TP2** | **Composant IA & Explicabilité SHAP** | Pipeline Scikit-Learn (TF-IDF + Régression logistique), inférence unitaire (`src/predict.py`), matrice de confusion (`src/evaluate.py`), explicabilité SHAP des log-odds et mots-outils (`src/expliquer.py`). | 8 tests passants (`test_model.py`, `test_explicabilite.py`) |
| **TP3** | **Backend API REST (FastAPI)** | Serveur FastAPI (`api/main.py`), cycle de vie `lifespan` pour charger le modèle une seule fois au démarrage, contrats Pydantic v2 stricts (`api/schemas.py`), endpoints `/health` et `/predict`, codes HTTP 422 standardisés. | 6 tests passants (`test_api.py`) |
| **TP4** | **Robustesse, Incertitude & Biais** | Seuil d'abstention à 0.60 avec flag `INDETERMINE` (Human-in-the-loop), analyse des biais par sous-groupes (connecteurs de retournement vs longueur), démonstration du facteur confondant (`src/biais.py`). | 8 tests passants (`test_biais.py`) |
| **TP5** | **Interface Web & Visualisations (Streamlit)** | Frontend Streamlit (`ui/app.py`), client HTTP typé (`ui/client.py`) gérant les pannes et timeouts, onglets unitaire et batch CSV, composants graphiques purs de répartition des verdicts et histogramme de confiance (`ui/graphiques.py`). | 16 tests passants (`test_graphiques.py`, `test_client.py`, `test_interface.py`) |

---

## Installation et Démarrage rapide

### 1. Environnement virtuel et dépendances

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Entraîner le modèle de démonstration

```powershell
python src/make_demo.py
python src/train.py
```

### 3. Exécuter l'ensemble de la suite de tests

```powershell
pytest -v
```
*(Attendu : 76 tests passés au vert)*

### 4. Lancer l'API Backend (FastAPI)

```powershell
uvicorn api.main:app --reload
```
*Documentation Swagger disponible sur : `http://localhost:8000/docs`*

### 5. Lancer l'Interface Utilisateur (Streamlit)

```powershell
streamlit run ui/app.py
```
*Application accessible sur : `http://localhost:8501`*

---

## Structure du dépôt

```text
sentiment-app/
├── api/                  # Backend FastAPI (TP3)
│   ├── main.py           # Application, cycle de vie lifespan, endpoints /health et /predict
│   ├── model.py          # Raccord singleton au modèle, seuil d'abstention à 0.60
│   └── schemas.py        # Modèles Pydantic v2 (PredictRequest, PredictResponse)
├── src/                  # Composants Machine Learning et analyse (TP2, TP4)
│   ├── make_demo.py      # Génération du jeu de données synthétique déterministe
│   ├── train.py          # Entraînement TF-IDF + Régression logistique (F1 >= 0.85)
│   ├── evaluate.py       # Matrice de confusion et analyse d'erreurs
│   ├── predict.py        # Inférence unitaire
│   ├── expliquer.py      # Explicabilité locale SHAP (LinearExplainer) (TP2 Étape F)
│   └── biais.py          # Mesure d'équité et facteurs confondants (TP4 Étape F)
├── ui/                   # Frontend Streamlit (TP5)
│   ├── app.py            # Interface interactive (onglets unitaire et lot)
│   ├── client.py         # Client HTTP découplé pour consommer l'API REST
│   └── graphiques.py     # Fonctions pures de visualisation (répartition et histogramme)
├── data/                 # Jeux de données (sample_reviews.csv, avis_exemple.csv)
├── models/               # Métriques versionnées (metrics.json) et modèle (.joblib ignoré)
├── docs/                 # Comptes-rendus hebdomadaires (semaine2 à semaine5) et cadrage
├── tests/                # 76 tests pytest automatisés (TP1 à TP5)
├── .github/workflows/    # Intégration Continue (GitHub Actions ci.yml)
├── requirements.txt      # Dépendances du projet
└── README.md
```

---

## Auteur

| Rôle | Nom | Identifiant GitHub | Travail réalisé |
| --- | --- | --- | --- |
| Étudiant | Hamza Essamoudi | @Hamza3124 | **TP1 à TP5** : Cadrage, Entraînement & SHAP, API FastAPI, Biais & Abstention, Frontend Streamlit & Visualisations |
