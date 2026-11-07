# TP5, étape G : deux graphiques dans l'onglet fichier (20 min)

**Objectif.** Visualiser un lot d'avis : la répartition des verdicts et la confiance du modèle.
**Programme** : chapitre 2, point 5 (Streamlit, visualisation) et TP 3 de la liste minimale.

## Ce que l'étape fait comprendre

1. Les calculs restent hors de la page : `ui/graphiques.py` contient deux fonctions pures, testées
   sans lancer Streamlit ; la page ne fait que les afficher.
2. Un graphique de confiance montre ce que le tableau cache : combien d'avis sont tranchés de justesse.

## Faire

```powershell
python C:\IA-DEV\complements-lot1\appliquer_complements.py C:\IA-DEV\sentiment-app --etape tp5
python -m pytest tests/test_graphiques.py tests/test_interface.py -q
uvicorn api.main:app --reload
```

Dans un second terminal : `streamlit run ui/app.py`, onglet « Un fichier d'avis », puis
`data/avis_exemple.csv`.

Le script importe `graphiques` à côté de `client` dans `ui/app.py`, et ajoute cinq lignes sous le
résumé. Si votre page a été modifiée, il vous affiche ces lignes à placer vous-même.

## Contrôle T34a : valeurs attendues

- Répartition des verdicts : positif 3, négatif 2, à vérifier 1, refus ou erreur 0.
- Confiance par tranche : 50-60 % : 1 ; 60-70 % : 1 ; 70-80 % : 3 ; 80-90 % : 1 ; 90-100 % : 0.
- `9 passed` pour les deux fichiers de tests.

## Pièges

- Calculer les données dans la page : elles deviennent intestables.
- Oublier les catégories vides : la répartition les montre à zéro, pour comparer deux fichiers.
- Lire l'axe des verdicts dans un ordre fixe : Streamlit trie les catégories par ordre alphabétique.
