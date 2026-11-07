# TP3 : marche à suivre, étape par étape et contrôle par contrôle

Six étapes, sept contrôles numérotés T14 à T20, dans la suite de ceux du TP2. Ne passez à l'étape suivante que lorsque le contrôle précédent est vert.

## Étape A. Installer le kit (15 min, à deux)

Décompressez le kit à côté de votre dépôt, pas dedans, puis :

```bash
cd kit-tp3
python appliquer_tp3.py ../sentiment-app --simulation   # voir ce qui sera fait
python appliquer_tp3.py ../sentiment-app
cd ../sentiment-app
source .venv/bin/activate          # Windows : .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src/train.py
python -m pytest -q
```

Si Windows a ajouté un dossier en décompressant l'archive, donnez à `appliquer_tp3.py` le chemin complet du dépôt.

`python src/train.py` n'est pas une formalité : le TP2 s'est terminé sur le modèle Allociné, et le TP3 se fait avec le modèle du jeu de démonstration, celui que la CI entraîne.

### Contrôle T14 : 48 tests verts

Attendu : **48 passed**, soit les 42 du TP2 plus les 6 de l'API.

## Étape B. Lire le code de l'API (20 min)

Trois fichiers, dans cet ordre :

| Fichier | Ce qu'il faut y voir |
| --- | --- |
| `api/schemas.py` | Le contrat : `text`, chaîne de 1 à 2000 caractères ; la réponse : `label`, `score`, aperçu du texte |
| `api/model.py` | Le raccord : l'API appelle `predict()` du TP2 et ne touche jamais à scikit-learn |
| `api/main.py` | Le `lifespan`, qui charge le modèle une seule fois ; `_classifier()`, qui renvoie 503 s'il manque ; les deux routes |

Gardez une question en tête pour l'étape F : que se passe-t-il au démarrage si le modèle n'existe pas ?

## Étape C. Faire répondre l'API (30 min)

```bash
uvicorn api.main:app --reload
```

Le terminal affiche `Modèle chargé avec succès : tfidf-logreg (TP2, models/sentiment.joblib)`. Ouvrez `http://localhost:8000/docs`, puis, pour chaque route, « Try it out » et « Execute ».

### Contrôle T15 : le service est prêt

`GET /health` : **200**, avec `"status": "OK"` et `"model": "tfidf-logreg (TP2, models/sentiment.joblib)"`.

### Contrôle T16 : un avis positif

`POST /predict` avec `{"text": "Livraison rapide, produit conforme, très satisfait"}` : **200**, `"label": "POSITIVE"`, `"score": 0.777`.

### Contrôle T17 : un avis négatif

`POST /predict` avec `{"text": "Produit cassé et service injoignable, à fuir"}` : **200**, `"label": "NEGATIVE"`, `"score": 0.7465`.

## Étape D. Les refus (20 min)

Toujours dans `/docs`, envoyez trois requêtes invalides : `{"text": ""}`, `{}`, puis `{"text": 42}`.

### Contrôle T18 : 422 dans les trois cas

Les trois réponses sont des **422**, et leur `detail` nomme le champ fautif. Une requête invalide est une faute du client, pas une panne du serveur : jamais 500.

Arrêtez l'API (`Ctrl+C`).

## Étape E. Pousser et vérifier la CI (15 min)

Le kit a ajouté une étape à `.github/workflows/ci.yml`, juste avant les tests : `python src/make_demo.py && python src/train.py`. Sans elle, la CI n'aurait pas de modèle et ignorerait les tests de l'API sans bruit.

```bash
git add -A
git commit -m "Semaine 3 : API FastAPI"
git push
```

### Contrôle T19 : la CI est verte

Dans l'onglet Actions, l'étape « Modèle de démonstration » passe, puis l'étape des tests affiche 48 passed.

## Étape F. L'API sans modèle, puis le compte rendu (20 min)

```bash
mv models/sentiment.joblib models/sentiment.bak      # Windows : Rename-Item models/sentiment.joblib sentiment.bak
uvicorn api.main:app
mv models/sentiment.bak models/sentiment.joblib      # Windows : Rename-Item models/sentiment.bak sentiment.joblib
```

### Contrôle T20 : l'API refuse de démarrer

Le terminal affiche `FileNotFoundError: models/sentiment.joblib absent : lancez python src/train.py`, puis `Application startup failed`, et l'API ne démarre pas. Remettez le modèle en place.

Répondez ensuite aux deux questions de `docs/semaine3.md`, puis :

```bash
git add -A
git commit -m "Semaine 3 : compte rendu"
git push
```

## Récapitulatif des contrôles

| Contrôle | Commande ou essai | Résultat attendu |
| --- | --- | --- |
| T14 | `python -m pytest -q` | 48 passed |
| T15 | `GET /health` | 200, `status` OK, nom du modèle |
| T16 | `POST /predict`, avis positif | 200, `POSITIVE`, 0,777 |
| T17 | `POST /predict`, avis négatif | 200, `NEGATIVE`, 0,7465 |
| T18 | `{"text": ""}`, `{}`, `{"text": 42}` | 422 dans les trois cas |
| T19 | `git push`, onglet Actions | CI verte, 48 passed |
| T20 | `uvicorn api.main:app` sans modèle | `FileNotFoundError`, l'API ne démarre pas |

## En cas de blocage

| Message | Cause | Correction |
| --- | --- | --- |
| `ERREUR : src/predict.py du TP2 introuvable` | Le TP2 n'est pas dans le dépôt, ou en est une autre version | Installer le kit du TP2 d'abord |
| `ModuleNotFoundError: fastapi` | Dépendances non installées | `pip install -r requirements.txt` |
| 6 tests ignorés (`skipped`) | Pas de modèle sur le poste | `python src/train.py` |
| Le test qui attend `POSITIVE` échoue | Modèle Allociné encore sur le poste | `python src/train.py` |
| `uvicorn` : adresse déjà utilisée (`10048`) | Une autre API tourne déjà | Fermer l'autre terminal, ou `--port 8001` |
| CI rouge, `ModuleNotFoundError: fastapi` | La CI n'installe pas l'API | Vérifier que la ligne `pip install` de `ci.yml` contient `fastapi` et `httpx` |
| CI verte mais tests de l'API ignorés | La CI n'entraîne pas le modèle | Vérifier l'étape « Modèle de démonstration » avant les tests |
