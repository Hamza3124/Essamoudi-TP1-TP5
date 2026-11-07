# Semaine 5 : l'interface, notes du binôme

> Trois questions, quelques phrases chacune. Répondez avec ce que vous avez observé.

## 1. Pourquoi l'interface n'importe-t-elle jamais `predict()` ni le fichier `.joblib` ?

L'interface applique une **séparation stricte des responsabilités (découplage client/serveur)** : elle agit en client web léger et délègue toute l'intelligence artificielle au service backend via des requêtes HTTP. Importer directement `predict()` ou charger le fichier `.joblib` dans le frontend dupliquerait la consommation mémoire du modèle, imposerait l'installation des dépendances lourdes de machine learning côté client, et empêcherait un déploiement distribué ou une montée en charge indépendante entre l'interface utilisateur et le moteur d'inférence.

## 2. Que montre l'interface quand le modèle hésite, et pourquoi est-ce mieux qu'un verdict forcé ?

Quand la probabilité prédite est inférieure au seuil d'abstention (0.60), l'interface affiche l'étiquette **« Je ne sais pas : à faire vérifier par un humain »** (`INDETERMINE`), accompagnée de la métrique de confiance (ex. 52 %) et d'un message d'information : *« La confiance est sous le seuil d'abstention : un humain doit trancher »*. 

Cette approche est bien plus robuste qu'un verdict forcé (pile ou face) : elle prévient les erreurs silencieuses sur des avis hors domaine, ambigus ou complexes (mots inventés, sarcasme, retournements), et permet une supervision humaine (*Human-in-the-loop*) garante de la qualité en production.

## 3. Que voit l'utilisateur quand l'API tombe ? Et le fichier `data/avis_exemple.csv` : combien d'avis partent vers un humain ?

- **Si l'API est arrêtée ou indisponible** : L'exception réseau est capturée proprement (`httpx.TransportError`) et l'application affiche un encadré d'erreur rouge explicite : `API injoignable : lancez d'abord uvicorn api.main:app`, sans planter ni lever d'erreur 500.
- **Sur le fichier `data/avis_exemple.csv`** (6 avis au total) :
  - **1 avis** est orienté vers un humain (`xqzvb wlkptr grombu`, confiance 52 % < seuil d'abstention).
  - **3 avis** sont classés positifs (`POSITIVE`).
  - **2 avis** sont classés négatifs (`NEGATIVE`).
  - **0 refus ou erreur**.
