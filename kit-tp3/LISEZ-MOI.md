# Kit TP3 : exposer le modèle par une API (semaine 3)

Ce kit se superpose au dépôt `sentiment-app` en fin de TP2. Il n'écrase rien.

## Installation, depuis ce dossier

```bash
python appliquer_tp3.py ../sentiment-app --simulation   # voir sans rien écrire
python appliquer_tp3.py ../sentiment-app
```

Si Windows a ajouté un dossier en décompressant l'archive, donnez le chemin complet du dépôt, par exemple `python appliquer_tp3.py C:\Tp-DEV\sentiment-app`.

## Ce que le kit ajoute

| Fichier | Rôle |
| --- | --- |
| `api/schemas.py` | Le contrat : ce que l'API accepte et ce qu'elle renvoie (Pydantic v2) |
| `api/model.py` | Le raccord au modèle du TP2 : appelle `predict()`, ne connaît pas scikit-learn |
| `api/main.py` | L'application : chargement du modèle au démarrage, `/health`, `/predict`, codes d'erreur |
| `tests/test_api.py` | Six tests de l'API, sans serveur à lancer |
| `docs/semaine3.md` | Les deux questions du compte rendu |
| `TP3-ENONCE.md`, `MARCHE-A-SUIVRE-TP3.md` | L'énoncé et le pas à pas, contrôles T14 à T20 |

Le script vérifie aussi que `requirements.txt` contient FastAPI, uvicorn et httpx, ajoute `pythonpath = .` à `pytest.ini` pour que les tests trouvent `api/`, et complète `.github/workflows/ci.yml` : la CI installe l'API et entraîne le modèle de démonstration avant les tests.

## Prérequis

Le TP2 terminé (`pytest -q` à 42 passed), sous Python 3.11. Le dossier `app/` créé au TP1 reste vide : l'API du cours vit dans `api/`.
