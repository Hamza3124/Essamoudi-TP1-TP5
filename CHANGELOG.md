# Journal des versions

Le numéro de version suit les TP : 0.N.0 à la fin du TP N. Chaque version publiée porte une étiquette Git `v0.N.0`.

## 0.6.0 (TP6) : le paquet

- **Pour celui qui installe** : l'application devient un paquet Python installable via une roue (`.whl`) ou `pip install .` ; fournit la commande en ligne `sentiment` (`--version`, `predict`, `serve`, `ui`) utilisable directement depuis n'importe où sans naviguer dans le dossier du dépôt.
- **Pour celui qui développe** : installation en mode éditable (`pip install -e .`) ; le code de prédiction a été déplacé dans `sentiment_app/predict.py` avec un module de compatibilité dans `src/predict.py` ; `api/model.py` importe directement `sentiment_app.predict` sans manipuler manuellement `sys.path`. Le chemin du modèle est rendu configurable via la variable d'environnement `SENTIMENT_MODELE`.
- **Pour la CI** : scikit-learn est strictement épinglé en 1.5 pour assurer la compatibilité binaire du modèle sérialisé (`joblib`) ; ajout d'une étape automatisée qui construit la roue (`python -m build --wheel`), l'installe dans un venv isolé hors du dépôt et valide son exécution de bout en bout.


## 0.5.0 (TP5) : l'interface

- Page Streamlit : un avis, ou un fichier d'avis ; le client HTTP traduit chaque réponse de l'API.

## 0.4.0 (TP4) : tests et qualité

- Contrat d'entrée testé, abstention `INDETERMINE`, jeu d'or, tests d'intégration, contrat typé, ruff, mypy, pre-commit.

## 0.3.0 (TP3) : l'API

- FastAPI : `/health`, `/predict`, contrat Pydantic ; la CI entraîne le modèle avant les tests.

## 0.2.0 (TP2) : le modèle

- TF-IDF et régression logistique ; les métriques sont versionnées, le modèle ne l'est pas.

## 0.1.0 (TP1) : le cadrage

- Environnement Python 3.11, structure du dépôt, trois fiches de cadrage, dépôt GitHub à deux auteurs.
