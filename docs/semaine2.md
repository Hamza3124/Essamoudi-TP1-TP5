# Semaine 2 : Modèle de sentiment, notes du binôme

## 1. Mesures obtenues

- **Source des données** : jeu de démonstration (`data/demo_reviews.csv`), 290 avis (232 entraînement, 58 test).
- **Exactitude (Accuracy)** : 0.8793 (87.9 %)
- **F1 macro** : 0.879 (seuil d'acceptation : 0.85 -> **ACCEPTÉ**)
- **Rappel sur la classe négative** : 0.931 (93.1 %)

## 2. Lecture des erreurs

Sur les 58 avis du jeu de test, le modèle commet **7 erreurs** :
- 2 faux positifs (négatifs classés positifs).
- 5 faux négatifs (positifs classés négatifs).

Exemples d'erreurs :
1. `vérité=positive, prédit=negative` : « Taille trop petite et retour payant au déballage, sauf que ensuite produit conforme à la description, très satisfait. »
2. `vérité=positive, prédit=negative` : « Commande jamais reçue et remboursement en attente au début, sauf que ensuite je recommande. »
3. `vérité=negative, prédit=positive` : « Service impeccable et livraison en avance sur le papier, sauf que ensuite produit cassé à l'arrivée. »

**Analyse** :
Ces avis sont construits avec un retournement (« sauf que ensuite », « mais finalement »). Le modèle linéaire fondé sur un sac de n-grammes (TF-IDF) additionne les poids lexicaux sans comprendre la structure temporelle ou syntaxique où la conclusion renverse la proposition initiale. Les termes négatifs présents dans la première moitié ont un poids cumulé supérieur aux termes positifs de la seconde moitié (ou inversement), ce qui fait basculer la prédiction du mauvais côté.

## 3. Décision d'acceptation du modèle

Le modèle est **accepté** pour le passage à l'étape suivante car son F1 macro (0.879) est supérieur au seuil contractuel de 0.85. De plus, le rappel sur les avis négatifs (0.931) est élevé, ce qui minimise les réclamations clients non détectées. Néanmoins, sa sensibilité aux avis mitigés et aux tournures avec retournement justifiera la mise en place d'un seuil d'abstention (TP4).

## 4. Analyse d'explicabilité (SHAP)

L'ouverture du modèle via SHAP et les coefficients de la régression logistique révèle que certains mots-outils (« je », « en », « au ») figurent parmi les termes les plus influents. Le modèle a appris des tournures statistiques spécifiques au jeu d'entraînement, et pas uniquement des termes intrinsèquement porteurs de sentiment. Sur un avis mitigé, les contributions positives et négatives se compensent presque (environ -1.01 vs +0.92 en log-odds), plaçant la prédiction finale proche de l'indécision (confiance de 53.35 %).

