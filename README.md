# sentiment-app : Application fil rouge (TP1 à TP6 + Service Spring Boot)

Application fil rouge du cours *Développement et déploiement d'applications intelligentes*.
Ce dépôt regroupe l'implémentation complète des **6 travaux pratiques (TP1 à TP6)** ainsi que l'extension **Microservice Java / Spring Boot**, couvrant l'ensemble du cycle de vie d'un composant d'intelligence artificielle : du cadrage métier jusqu'au packaging professionnel et à l'interopérabilité multi-langages.

---

## Les Travaux Pratiques couverts

| TP / Module | Sujet | Composants clés | Statut & Tests |
| --- | --- | --- | --- |
| **TP1** | **Cadrage et Environnement** | Fiches de cadrage argumentées (`docs/cadrage/`), structure du projet, configuration Git et CI initiale. | 34 tests passants (`test_cadrage.py`, `test_environment.py`, `test_git_history.py`) |
| **TP2** | **Composant IA & Explicabilité SHAP** | Pipeline Scikit-Learn (TF-IDF + Régression logistique), inférence unitaire (`sentiment_app/predict.py`), matrice de confusion (`src/evaluate.py`), explicabilité SHAP des log-odds et mots-outils (`src/expliquer.py`). | 8 tests passants (`test_model.py`, `test_explicabilite.py`) |
| **TP3** | **Backend API REST (FastAPI)** | Serveur FastAPI (`api/main.py`), cycle de vie `lifespan` pour charger le modèle une seule fois au démarrage, contrats Pydantic v2 stricts (`api/schemas.py`), endpoints `/health` et `/predict`, codes HTTP standardisés. | 6 tests passants (`test_api.py`) |
| **TP4** | **Robustesse, Incertitude & Biais** | Seuil d'abstention à 0.60 avec flag `INDETERMINE` (Human-in-the-loop), analyse des biais par sous-groupes (connecteurs de retournement vs longueur), démonstration du facteur confondant (`src/biais.py`). | 8 tests passants (`test_biais.py`) |
| **TP5** | **Interface Web & Visualisations (Streamlit)** | Frontend Streamlit (`ui/app.py`), client HTTP typé (`ui/client.py`) gérant les pannes et timeouts, onglets unitaire et batch CSV, composants graphiques purs de répartition des verdicts et histogramme de confiance (`ui/graphiques.py`). | 16 tests passants (`test_graphiques.py`, `test_client.py`, `test_interface.py`) |
| **TP Spring Boot** | **Interopérabilité Java & Sécurité API** | Extension de l'API Python avec `/v1` sécurisé par `X-API-Key` (`api/v1.py`, `api/securite.py`) ; Microservice Java Spring Boot (`java/avis-service/`) consommant l'API Python via `SentimentClient` (transport `jdk-http11`, timeouts, mapping d'erreurs 502/503). Scripts e2e et CI GitHub Actions dédiée. | 26 tests JUnit passants + 6 tests e2e validés (`e2e_spring.ps1`) |
| **TP6** | **Packaging & Distribution (Roue .whl)** | Création du paquet Python `sentiment_app`, suppression des hacks `sys.path`, modèle configurable via `SENTIMENT_MODELE`, commande globale CLI `sentiment` (`--version`, `predict`, `serve`, `ui`), construction de roue (`.whl`) installable hors dépôt. | 6 tests packaging passants (Total: **82 tests pytest passés au vert**) |

---

## Installation et Démarrage rapide

### 1. Environnement virtuel et installation en mode développement (TP6)

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -e .
pip install -r requirements-dev.txt
```

### 2. Entraîner le modèle de démonstration

```powershell
python src/make_demo.py
python src/train.py
```
*(Génère `models/sentiment.joblib` et met à jour `models/metrics.json`)*

### 3. Exécuter l'ensemble des tests Python

```powershell
pytest -v
```
*(Attendu : **82 tests passés au vert**, 0 échec)*

---

## Utilisation des composants

### A. La commande CLI `sentiment` (TP6)

Grâce au packaging de l'application, la commande `sentiment` est accessible directement :

```powershell
# Vérifier la version installée
sentiment --version
# Attendu : sentiment-app 0.6.0

# Effectuer une prédiction unitaire (avec seuil d'abstention)
sentiment predict "Livraison rapide, produit conforme, très satisfait"
sentiment predict "xqzvb wlkptr grombu"

# Lancer le serveur d'API (FastAPI)
sentiment serve --host 127.0.0.1 --port 8000

# Lancer l'interface utilisateur (Streamlit)
sentiment ui
```

### B. Construction de la Roue Python (`.whl`)

Pour distribuer l'application sous forme de paquet autonome (sans tests, sans données, sans modèle) :

```powershell
python -m build --wheel
```
La roue est générée dans `dist/sentiment_app-0.6.0-py3-none-any.whl`.

Hors du dépôt, elle s'installe et s'exécute en pointant vers un modèle avec `SENTIMENT_MODELE` :
```powershell
pip install dist\sentiment_app-0.6.0-py3-none-any.whl
$env:SENTIMENT_MODELE = "chemin\vers\sentiment.joblib"
sentiment predict "Produit de grande qualité"
```

### C. Le Microservice Java / Spring Boot (`avis-service`)

Le service Java écoute sur le port **8081** et relaie les demandes d'analyse de sentiment vers l'API Python (port **8000**) via le contrat sécurisé `/v1` :

```powershell
# 1. Dans le dossier du service Java
cd java\avis-service

# 2. Exécuter les tests unitaires et d'intégration JUnit
.\mvnw.cmd test

# 3. Lancer le service Java avec sa configuration
$env:SENTIMENT_API_KEY = "e2e-cle-client-tp-spring"
$env:SENTIMENT_API_URL = "http://127.0.0.1:8000"
.\mvnw.cmd spring-boot:run
```

Pour exécuter la validation automatique de bout en bout (Python FastAPI + Spring Boot) :
```powershell
powershell -ExecutionPolicy Bypass -File scripts\e2e_spring.ps1
```
*(Bilan attendu : 6/6 tests de bout en bout OK, 0 échec)*

---

## Structure du dépôt

```text
sentiment-app/
├── sentiment_app/        # Paquet Python officiel (TP6)
│   ├── __init__.py       # Déclaration de version unique (__version__ = "0.6.0")
│   ├── __main__.py       # Point d'entrée pour python -m sentiment_app
│   ├── cli.py            # Commande console sentiment (predict, serve, ui)
│   └── predict.py        # Inférence unitaire, support de SENTIMENT_MODELE
├── api/                  # Backend FastAPI (TP3 + Extension TP Spring Boot)
│   ├── main.py           # Serveur FastAPI, cycle lifespan, gestionnaires d'erreurs
│   ├── model.py          # Raccord propre à sentiment_app.predict (sans sys.path)
│   ├── schemas.py        # Schémas Pydantic v2
│   ├── securite.py       # Authentification API Key X-API-Key (rôles client/admin)
│   └── v1.py             # Router /v1 avec codes d'erreurs standardisés
├── java/avis-service/    # Microservice Java Spring Boot (Programme 2.7)
│   ├── pom.xml           # Configuration Maven & dépendances Spring Boot 3 / Java 21
│   ├── src/main/java/    # Code source : AvisController, SentimentClient, ClientHttpConfig
│   └── src/test/java/    # Tests JUnit, MockMvc, WireMock et ApiReelleTest
├── src/                  # Composants ML et rétrocompatibilité
│   ├── predict.py        # Fichier de compatibilité (redirige vers sentiment_app.predict)
│   ├── make_demo.py      # Génération du jeu synthétique
│   ├── train.py          # Entraînement TF-IDF + Régression logistique (scikit-learn 1.5)
│   ├── evaluate.py       # Matrice de confusion et métriques
│   ├── expliquer.py      # Explicabilité locale SHAP (LinearExplainer) (TP2)
│   └── biais.py          # Mesure d'équité et facteurs confondants (TP4)
├── ui/                   # Frontend Streamlit (TP5)
│   ├── app.py            # Application web interactive
│   ├── client.py         # Client HTTP typé consommant l'API
│   └── graphiques.py     # Graphiques purs Altair / Streamlit
├── scripts/              # Scripts d'automatisation et de validation
│   ├── e2e_spring.ps1    # Test de bout en bout Spring Boot <-> Python (PowerShell)
│   ├── e2e_spring.sh     # Test de bout en bout Spring Boot <-> Python (Bash / CI)
│   ├── lancer_projet.ps1 # Lance les 3 services (FastAPI, Spring Boot, Streamlit)
│   └── arreter_projet.ps1# Arrête proprement les services
├── docs/                 # Fiches de cadrage et comptes-rendus hebdomadaires
│   ├── semaine6.md       # Réponses techniques et observations du TP6
│   └── cadrage/          # Fiches de cadrage métier (TP1)
├── tests/                # 82 tests pytest automatisés (TP1 à TP6)
│   └── test_packaging.py # Validation des métadonnées, de la commande et de la roue (TP6)
├── .github/workflows/    # Intégration Continue (GitHub Actions)
│   ├── ci.yml            # CI Python : tests complets et étape de la roue hors dépôt
│   └── tp-spring.yml     # CI Java : tests JUnit et validation bout en bout contre l'API
├── pyproject.toml        # Métadonnées du paquet, dépendances et points d'entrée (TP6)
├── CHANGELOG.md          # Journal des versions (v0.1.0 à v0.6.0)
├── RAPPORT-TP-SPRING.md  # Rapport de TP Spring Boot avec justifications et preuves
└── README.md             # Ce document
```

---

## Étiquettes Git (Tags)

- `tp-spring` : Livrable complet du service Spring Boot et de l'API sécurisée.
- `v0.6.0` : Livrable complet du paquet installable, de la commande CLI et de la roue.

---

## Auteur

| Rôle | Nom | Identifiant GitHub | Travail réalisé |
| --- | --- | --- | --- |
| Étudiant | Hamza Essamoudi | @Hamza3124 | **TP1 à TP6 + Spring Boot** : Cadrage, Entraînement & SHAP, API FastAPI, Biais & Abstention, Frontend Streamlit, Microservice Java Spring Boot, Packaging Python & Distribution Wheel |
