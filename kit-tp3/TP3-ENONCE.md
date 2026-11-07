# TP3 : exposer le modèle par une API

**Module :** Développement et déploiement d'applications intelligentes
**Auteur :** A. Larhlimi
**Séance :** semaine 3, TP de 2 h, en binôme

## Objectif

Mettre le modèle du TP2 derrière une API HTTP que n'importe quel programme peut appeler : `/health` pour savoir si le service est prêt, `/predict` pour classer un avis. L'API n'entraîne rien et ne connaît pas scikit-learn : elle appelle `predict()` du TP2, charge le modèle une seule fois au démarrage, et répond avec des codes d'erreur qui disent la vérité.

## Prérequis

Le dépôt `sentiment-app` en fin de TP2 : `pytest -q` à `42 passed`, CI verte.

## Déroulé, six étapes

| Étape | Durée | Ce que vous faites | Contrôle |
| --- | --- | --- | --- |
| A | 15 min | Installer le kit, revenir au modèle de démonstration | T14 : 48 passed |
| B | 20 min | Lire `api/` : le contrat, le raccord, l'application | (lecture) |
| C | 30 min | Lancer l'API, interroger `/health` et `/predict` dans `/docs` | T15 : `/health` ; T16 : un avis positif ; T17 : un avis négatif |
| D | 20 min | Les refus : texte vide, champ absent, mauvais type | T18 : 422 dans les trois cas |
| E | 15 min | Pousser, vérifier la CI | T19 : CI verte, l'entraînement avant les tests |
| F | 20 min | L'API sans modèle, puis le compte rendu | T20 : l'API refuse de démarrer |

## Livrables, sur la branche `main`

- [ ] `api/` (contrat, raccord, application) et `tests/test_api.py`
- [ ] `pytest -q` affiche `48 passed`
- [ ] `.github/workflows/ci.yml` entraîne le modèle avant les tests ; CI verte
- [ ] `docs/semaine3.md` : les deux questions
- [ ] `models/sentiment.joblib` toujours absent de Git

## Grille de notation (TP3 sur 10)

| Critère | Points | Vérification |
| --- | --- | --- |
| L'API répond : `/health`, avis positif, avis négatif | 3 | T15 à T17 sur un clone frais |
| Les codes d'erreur disent la vérité : 422 pour une requête invalide, refus de démarrer sans modèle | 2 | T18, T20 |
| Tests verts en local et en CI | 2 | T14, T19 |
| `docs/semaine3.md` : les deux réponses, appuyées sur ce que vous avez observé | 3 | Lecture |

## Pièges fréquents

| Piège | Conséquence | Correction |
| --- | --- | --- |
| Charger le modèle à chaque requête | Chaque appel coûte un chargement complet | Le `lifespan` le charge une fois, au démarrage |
| Laisser une exception remonter | Le client reçoit 500 pour une requête simplement invalide | Le contrat Pydantic refuse en amont : 422 |
| Garder le modèle Allociné de la fin du TP2 | Un test qui attend `POSITIVE` sur un avis de livraison échoue | `python src/train.py` : le modèle de démonstration, celui de la CI |
| Une CI qui n'entraîne pas le modèle | Les tests de l'API y sont ignorés sans bruit | L'étape d'entraînement avant les tests, ajoutée par le kit |
