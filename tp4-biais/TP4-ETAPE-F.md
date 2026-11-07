# TP4, étape F : le modèle sert-il tous les avis de la même façon ? (20 min)

**Objectif.** Mesurer les performances par groupe d'avis, et distinguer un vrai facteur d'un facteur
confondant. **Programme** : chapitre 1, point 6 (biais), et chapitre 5, point 3 (métriques adaptées).

## Ce que l'étape fait comprendre

1. Une métrique globale cache des écarts : le F1 de 0,879 mélange des groupes très inégalement servis.
2. Un biais se mesure groupe par groupe, avec l'effectif de chaque groupe.
3. Un écart peut venir d'une autre variable : il faut croiser avant de conclure.

## Faire

```powershell
python C:\IA-DEV\complements-lot1\appliquer_complements.py C:\IA-DEV\sentiment-app --etape tp4
python src/biais.py
python -m pytest tests/test_biais.py -q
```

## Contrôle T27a : valeurs attendues (modèle de démonstration, seuil 0.60)

```text
Selon la présence d'un retournement
  groupe                      avis  exactitude  erreurs  vers humain  restantes
  avec retournement             17       0.588        7           15          2
  direct                        41       1.000        0            1          0

Selon la longueur
  court (9 mots ou moins)       31       1.000        0            0          0
  long (plus de 9 mots)         27       0.741        7           16          2

Les deux à la fois
  court, direct                 31       1.000        0            0          0
  long, avec retournement       17       0.588        7           15          2
  long, direct                  10       1.000        0            1          0
```

Puis `8 passed`. « Vers humain » compte les avis sous le seuil d'abstention ; « restantes », les
erreurs parmi les avis auxquels l'API répond.

## Ajouter au compte rendu (docs/semaine4.md)

Deux phrases : quel groupe est moins bien servi, et pourquoi la longueur n'est pas la cause (les 10 avis
longs sans retournement sont tous justes). Puis une question ouverte : l'abstention règle-t-elle le
problème, ou le déplace-t-elle vers les agents qui traitent les avis à vérifier ?

## Pièges

- Conclure sur un groupe de 17 avis comme sur 4 000 : citer les effectifs.
- Détecter « mais » dans « maison » : la détection se fait sur des mots entiers, et un test le vérifie.
- Confondre biais et erreur : un biais est un écart entre groupes, pas un taux d'erreur.
