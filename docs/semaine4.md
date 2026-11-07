# Semaine 4 : Tests approfondis, robustesse et analyse des biais

## 1. Analyse des performances par sous-groupes (Biais)

Sur les 58 avis du jeu de test :
- **Avis directs** : 41 avis, exactitude de **1.000 (100 %)**, 0 erreur.
- **Avis avec retournement** : 17 avis, exactitude de **0.588 (58.8 %)**, 7 erreurs.

Le groupe des avis comportant des connecteurs d'opposition (« mais », « sauf que », « cependant ») est nettement moins bien servi par le modèle.

## 2. Démonstration du facteur confondant (Longueur vs Retournement)

À première vue, les avis longs (> 9 mots) semblent moins performants (exactitude de 0.741) que les avis courts (1.000). Cependant, le croisement des deux variables prouve qu'il s'agit d'un **facteur confondant** :
- **Courts et directs** (31 avis) : exactitude 1.000 (0 erreur).
- **Longs et directs** (10 avis) : exactitude **1.000 (0 erreur)**.
- **Longs avec retournement** (17 avis) : exactitude **0.588 (7 erreurs)**.

La longueur brute n'est donc en rien la cause de la dégradation de la performance : les 10 avis longs dépourvus de retournement sont tous correctement classés. La difficulté provient exclusivement de la complexité syntaxique introduite par les retournements d'opinion que le sac de n-grammes ne sait pas modéliser.

## 3. Impact du seuil d'abstention (Human-in-the-loop)

Avec un seuil d'abstention fixé à **0.60** (`SEUIL_ABSTENTION = 0.60`) :
- Sur les 17 avis avec retournement, **15 avis litigieux sont envoyés vers un humain** (`INDETERMINE`).
- Le nombre d'erreurs restantes en production passe de 7 à seulement **2 erreurs**.

**Discussion** :
L'abstention ne résout pas intrinsèquement l'incapacité du modèle à comprendre les retournements, mais elle protège le système en évitant d'exposer des décisions erronées aux utilisateurs finaux. Elle déplace toutefois une partie de la charge de travail vers les opérateurs humains, ce qui nécessite de dimensionner le coût opérationnel de cette revue par rapport au coût d'une erreur d'inférence en production.

