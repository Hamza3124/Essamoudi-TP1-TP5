# Semaine 3 : l'API, notes du binôme

> Deux questions, quelques phrases chacune. Répondez avec ce que vous avez observé, pas avec le cours.

## 1. Pourquoi l'API refuse-t-elle de démarrer sans `models/sentiment.joblib`, plutôt que de démarrer et de répondre 503 ?

Refuser de démarrer applique le principe du **Fail Fast** : le modèle de machine learning est la dépendance cœur indispensable au fonctionnement du service. Si le fichier `.joblib` est manquant, l'API ne peut fournir aucune prédiction utile. Démarrer pour répondre systématiquement 503 masquerait une erreur de configuration ou de déploiement majeure, gaspillerait des ressources et tromperait les orchestrateurs de conteneurs (comme Docker ou Kubernetes) qui ont besoin qu'un processus défaillant échoue immédiatement (`CrashLoopBackOff`) pour déclencher une alerte ou annuler un déploiement défectueux.

## 2. Un texte vide est refusé deux fois : par Pydantic, puis par `predict()`. Est-ce redondant ?

Ce n'est pas une redondance inutile, mais une application du principe de **défense en profondeur** et de **séparation des responsabilités** :
- **La couche API (Pydantic)** valide le contrat HTTP aux frontières du système et rejette immédiatement les requêtes malformées avec un code d'erreur HTTP 422 standardisé, sans solliciter le pipeline de calcul.
- **La couche domaine (`predict()`)** protège l'intégrité de la logique métier. Comme cette fonction est autonome et peut être appelée en dehors de FastAPI (ex. en script CLI, tâche par lots ou tests unitaires), elle doit valider ses propres préconditions pour ne pas propager un état incohérent dans le modèle.

