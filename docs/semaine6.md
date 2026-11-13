# Semaine 6 : le paquet, notes du binôme

> Trois questions, quelques phrases chacune. Répondez avec ce que vous avez observé.

## 1. Pourquoi le modèle n'est-il pas dans la roue ? Comment le paquet le trouve-t-il ?

Le modèle entraîné (`models/sentiment.joblib`) n'est pas inclus dans la roue car il possède son propre cycle de vie distinct de celui du code applicatif : le modèle peut être réentraîné, ajusté ou remplacé sans nécessiter de recompilation ou de redistribution du paquet Python. De plus, les artefacts binaires de modèles peuvent être volumineux et varient selon l'environnement de déploiement. Le paquet localise le modèle grâce à la fonction `chemin_modele()` dans `sentiment_app/predict.py`, qui lit prioritairement la variable d'environnement `SENTIMENT_MODELE` si elle est définie, ou utilise le chemin local par défaut `models/sentiment.joblib` à la racine du projet.

## 2. Qu'est-ce qui a changé dans api/model.py quand predict() est entré dans le paquet, et pourquoi est-ce mieux ?

Toutes les manipulations manuelles du chemin d'exécution Python (`RACINE = Path(...)`, `sys.path.insert(0, str(RACINE / "src"))`) ainsi que les exceptions de linter associées (`# noqa: E402`) ont été supprimées. `api/model.py` importe désormais directement le module installé via `from sentiment_app.predict import charger_modele, predict as _predict`. Cette approche est conforme aux standards Python : le code ne dépend plus de la disposition relative des répertoires sur le disque, évite la pollution globale de `sys.path`, et garantit un fonctionnement robuste en environnement de production où le paquet est installé dans `site-packages`.

## 3. La roue installée hors du dépôt : qu'a-t-il fallu lui fournir, et pourquoi scikit-learn est-il épinglé dans pyproject.toml ?

Hors du dépôt, la roue installée ne contient que les modules de code (`api`, `sentiment_app`, `ui`) sans les données d'entraînement ni le modèle sérialisé. Pour pouvoir exécuter des inférences, il a donc fallu lui fournir le chemin vers le fichier de modèle entraîné via la variable d'environnement `SENTIMENT_MODELE` (en son absence, la commande affiche un message d'erreur explicite indiquant la marche à suivre et renvoie le code de sortie 1).
scikit-learn est obligatoirement épinglé (`>=1.5,<1.6`) dans `pyproject.toml` car la sérialisation avec `joblib` dépend de la structure interne des objets de scikit-learn. Un modèle entraîné avec scikit-learn 1.5 ne peut être relu de façon fiable qu'avec une version compatible 1.5, sous peine d'erreurs d'incompatibilité de version ou de ruptures de contrats internes (ex. `InconsistentVersionWarning` ou `AttributeError`).

