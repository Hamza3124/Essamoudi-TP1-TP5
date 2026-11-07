# TP2, étape F : ce que regarde le modèle (20 min)

**Objectif.** Ouvrir le modèle : quels termes pèsent le plus, et pourquoi il se trompe sur un avis mitigé.
**Programme** : chapitre 5, point 4 (explicabilité, SHAP en introduction).

## Ce que l'étape fait comprendre

1. Un modèle linéaire s'explique exactement : sa sortie, en log-odds, est une somme de contributions,
   une par terme. SHAP calcule ces contributions par rapport à un avis de référence, la moyenne des avis
   d'entraînement ; la valeur de base plus les contributions redonnent exactement la sortie du modèle.
2. Les termes les plus influents ne sont pas toujours ceux qu'on attend : le modèle apprend aussi les
   tournures de ses données.
3. Sur un avis mitigé, les deux moitiés se compensent presque : le modèle hésite, et c'est mesurable.

## Faire

```powershell
python C:\IA-DEV\complements-lot1\appliquer_complements.py C:\IA-DEV\sentiment-app --etape tp2
python src/expliquer.py
python -m pytest tests/test_explicabilite.py -q
python src/expliquer.py "Produit cassé et service injoignable, à fuir"
```

## Contrôle C6 : valeurs attendues (modèle de démonstration)

```text
Les 8 termes qui poussent le plus vers « positive » :
  je (+0.771), que je (+0.764), en (+0.683), livraison en (+0.677), avance (+0.677), ...
Les 8 termes qui poussent le plus vers « negative » :
  arrivée (-0.923), produit cassé (-0.923), cassé arrivée (-0.923), cassé (-0.923), au (-0.689), ...

Avis : « Taille trop petite et retour payant au déballage, sauf que ensuite produit conforme ... »
Prédiction : negative (confiance 0.5335)
Valeur de base, l'avis moyen d'entraînement : -0.0114
Termes présents qui poussent vers « negative » : 20, au total -1.0061
  déballage sauf (-0.0989), au déballage (-0.0754), déballage (-0.0754), au (-0.0607), ...
Termes présents qui poussent vers « positive » : 13, au total +0.9177
  description (+0.0946), description très (+0.0946), la description (+0.0946), ...
Les termes absents, au total : -0.0345
Base + contributions = -0.1343 ; sortie du modèle = -0.1343
```

Puis `4 passed`. Si les valeurs diffèrent, le modèle chargé n'est pas celui de démonstration :
`python src/train.py`, sans option. En CI, au TP2, ces tests sont ignorés faute de modèle ; dès le TP3,
la CI entraîne le modèle et les exécute.

## Ajouter au compte rendu (docs/semaine2.md)

Une quatrième phrase : ce que révèlent les termes les plus influents. Attendu : des mots-outils (« je »,
« en », « au ») figurent parmi eux ; le modèle a appris des tournures du jeu de démonstration, pas
seulement des mots porteurs de sentiment.

## Pièges

- `No module named 'shap'` : `pip install -r requirements.txt`, qui l'épingle depuis le TP1.
- Lire la liste des contributions sans regarder les totaux : sur l'avis mitigé, les plus fortes
  contributions individuelles sont positives, mais les termes négatifs sont plus nombreux.
- Croire que SHAP explique le monde : il explique le modèle, y compris ses défauts.
