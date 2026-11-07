"""Les graphiques de l'onglet « Un fichier d'avis » (TP5, étape G).

Deux fonctions pures : elles reçoivent les réponses de l'API et renvoient un tableau prêt à tracer.
La page les affiche avec st.bar_chart ; les tests les vérifient sans lancer Streamlit.
"""

from __future__ import annotations

import pandas as pd

from ui.client import Reponse

COURTS = {"POSITIVE": "positif", "NEGATIVE": "négatif", "INDETERMINE": "à vérifier"}
REFUS = "refus ou erreur"


def repartition(reponses: list[Reponse]) -> pd.DataFrame:
    """Le nombre d'avis par verdict, toutes les catégories présentes, même vides."""
    noms = [COURTS.get(r.label or "", REFUS) if r.ok else REFUS for r in reponses]
    categories = [*COURTS.values(), REFUS]
    comptes = [noms.count(c) for c in categories]
    return pd.DataFrame({"avis": comptes}, index=pd.Index(categories, name="verdict"))


def histogramme_confiances(reponses: list[Reponse], pas: int = 10) -> pd.DataFrame:
    """Le nombre d'avis par tranche de confiance, de 50 à 100 %, par pas de `pas` points.

    Les refus et les erreurs n'ont pas de confiance : ils ne sont pas comptés.
    """
    bornes = list(range(50, 100, pas))
    tranches = [f"{b}-{b + pas} %" for b in bornes]
    comptes = [0] * len(bornes)
    for r in reponses:
        if r.ok and r.score is not None:
            rang = min(int((r.score * 100 - 50) // pas), len(bornes) - 1)  # 100 % va dans la dernière
            comptes[max(rang, 0)] += 1
    return pd.DataFrame({"avis": comptes}, index=pd.Index(tranches, name="confiance"))
