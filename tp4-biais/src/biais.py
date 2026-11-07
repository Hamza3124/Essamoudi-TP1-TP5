"""Le modèle traite-t-il tous les avis de la même façon ? (TP4, étape F)

    python src/biais.py

Mesure les performances du modèle par groupe d'avis, sur le jeu de test du TP2 : avis directs ou avec
un retournement (« mais », « sauf que »...), avis courts ou longs. Un écart important entre deux groupes
est un biais : le modèle sert moins bien une partie des avis. Le seuil d'abstention est celui de l'API.
"""

from __future__ import annotations

import re
import sys
from collections.abc import Callable
from pathlib import Path

import joblib
import numpy as np
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # pour importer api.model
from api.model import SEUIL_ABSTENTION  # noqa: E402
from train import GRAINE, MODELE, charger  # noqa: E402

CONNECTEURS = ("mais", "sauf que", "avant que", "puis", "pourtant", "cependant", "finalement")


def a_un_retournement(texte: str) -> bool:
    """Vrai si l'avis contient un connecteur qui peut renverser son sens (mot entier)."""
    bas = texte.lower()
    return any(re.search(rf"\b{re.escape(c)}\b", bas) for c in CONNECTEURS)


def nombre_de_mots(texte: str) -> int:
    return len(texte.split())


def mesurer(
    textes: list[str], vrais: list[str], predits: list[str], confiances: list[float],
    groupe: Callable[[str], str], seuil: float = SEUIL_ABSTENTION,
) -> dict[str, dict[str, float]]:
    """Par groupe : effectif, exactitude, erreurs, avis envoyés à un humain, erreurs restantes."""
    resultats: dict[str, dict[str, float]] = {}
    for nom in sorted({groupe(t) for t in textes}):
        idx = [i for i, t in enumerate(textes) if groupe(t) == nom]
        justes = [vrais[i] == predits[i] for i in idx]
        repondus = [i for i in idx if confiances[i] >= seuil]
        resultats[nom] = {
            "avis": len(idx),
            "exactitude": round(float(np.mean(justes)), 3),
            "erreurs": len(idx) - sum(justes),
            "vers_humain": len(idx) - len(repondus),
            "erreurs_restantes": sum(vrais[i] != predits[i] for i in repondus),
        }
    return resultats


def jeu_de_test() -> tuple[list[str], list[str], list[str], list[float]]:
    """Le jeu de test du TP2, avec les prédictions et les confiances du modèle."""
    df, _ = charger(False)
    _, x_test, _, y_test = train_test_split(
        df["review"], df["label"], test_size=0.2, random_state=GRAINE, stratify=df["label"]
    )
    pipeline = joblib.load(MODELE)
    textes = list(x_test)
    return (textes, list(y_test), list(pipeline.predict(textes)),
            pipeline.predict_proba(textes).max(axis=1).tolist())


def afficher(titre: str, resultats: dict[str, dict[str, float]]) -> None:
    print(f"\n{titre}")
    print(f"  {'groupe':<26}{'avis':>6}{'exactitude':>12}{'erreurs':>9}{'vers humain':>13}{'restantes':>11}")
    for nom, r in resultats.items():
        print(f"  {nom:<26}{r['avis']:>6}{r['exactitude']:>12.3f}{r['erreurs']:>9}"
              f"{r['vers_humain']:>13}{r['erreurs_restantes']:>11}")


def main() -> int:
    if not MODELE.exists():
        print("models/sentiment.joblib absent : lancez python src/train.py", file=sys.stderr)
        return 1
    textes, vrais, predits, confiances = jeu_de_test()
    mediane = int(np.median([nombre_de_mots(t) for t in textes]))
    print(f"Jeu de test : {len(textes)} avis ; seuil d'abstention : {SEUIL_ABSTENTION} ; "
          f"longueur médiane : {mediane} mots")

    def retournement(t: str) -> str:
        return "avec retournement" if a_un_retournement(t) else "direct"

    def longueur(t: str) -> str:
        return f"long (plus de {mediane} mots)" if nombre_de_mots(t) > mediane else f"court ({mediane} mots ou moins)"

    def croise(t: str) -> str:
        return f"{longueur(t).split()[0]}, {retournement(t)}"

    afficher("Selon la présence d'un retournement", mesurer(textes, vrais, predits, confiances, retournement))
    afficher("Selon la longueur", mesurer(textes, vrais, predits, confiances, longueur))
    afficher("Les deux à la fois", mesurer(textes, vrais, predits, confiances, croise))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
