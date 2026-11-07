"""Ce que regarde le modèle (TP2, étape F) : ses termes les plus influents, puis l'explication d'un avis.

    python src/expliquer.py                        # l'avis mitigé mal classé du jeu de démonstration
    python src/expliquer.py "Un avis à expliquer"

Le modèle est linéaire : sa sortie (en log-odds de la classe positive) est une somme de contributions,
une par terme du vocabulaire. SHAP calcule ces contributions par rapport à un avis de référence, la
moyenne des avis d'entraînement : la valeur de base, plus la somme des contributions, redonne
exactement la sortie du modèle.
"""

from __future__ import annotations

import argparse
import sys

import joblib
import numpy as np
from sklearn.model_selection import train_test_split

from train import GRAINE, MODELE, charger

AVIS_PAR_DEFAUT = (
    "Taille trop petite et retour payant au déballage, sauf que ensuite produit conforme "
    "à la description, très satisfait."
)


def mots_influents(pipeline, n: int = 8) -> tuple[list[tuple[str, float]], list[tuple[str, float]]]:
    """Les n termes qui poussent le plus vers « positive », puis vers « negative » (coefficients)."""
    termes = pipeline.named_steps["tfidf"].get_feature_names_out()
    coefs = pipeline.named_steps["clf"].coef_[0]
    ordre = np.argsort(coefs)
    positifs = [(str(termes[i]), float(coefs[i])) for i in ordre[::-1][:n]]
    negatifs = [(str(termes[i]), float(coefs[i])) for i in ordre[:n]]
    return positifs, negatifs


def avis_de_reference() -> list[str]:
    """Les avis d'entraînement, découpés exactement comme dans train.py."""
    df, _ = charger(False)
    x_train, _, _, _ = train_test_split(
        df["review"], df["label"], test_size=0.2, random_state=GRAINE, stratify=df["label"]
    )
    return list(x_train)


def expliquer(pipeline, texte: str, reference: list[str]) -> dict:
    """Valeurs SHAP d'un avis, en log-odds de la classe positive."""
    import shap  # importé ici : il est lent à charger

    vect, clf = pipeline.named_steps["tfidf"], pipeline.named_steps["clf"]
    fond = vect.transform(reference)
    explication = shap.LinearExplainer(clf, shap.maskers.Independent(fond, max_samples=fond.shape[0]))
    x = vect.transform([texte])
    valeurs = np.ravel(explication.shap_values(x))
    termes = vect.get_feature_names_out()
    presents = [(str(termes[i]), float(valeurs[i])) for i in x.nonzero()[1]]
    presents.sort(key=lambda t: abs(t[1]), reverse=True)
    return {
        "base": float(np.ravel(explication.expected_value)[0]),
        "valeurs": valeurs,
        "presents": presents,
        "absents": float(valeurs.sum() - sum(v for _, v in presents)),
        "sortie": float(clf.decision_function(x)[0]),
        "probas": dict(zip(clf.classes_, pipeline.predict_proba([texte])[0].round(4).tolist(), strict=True)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("texte", nargs="?", default=AVIS_PAR_DEFAUT)
    args = parser.parse_args()
    if not MODELE.exists():
        print("models/sentiment.joblib absent : lancez python src/train.py", file=sys.stderr)
        return 1
    pipeline = joblib.load(MODELE)
    positifs, negatifs = mots_influents(pipeline)
    print("Les 8 termes qui poussent le plus vers « positive » :")
    print("  " + ", ".join(f"{t} ({c:+.3f})" for t, c in positifs))
    print("Les 8 termes qui poussent le plus vers « negative » :")
    print("  " + ", ".join(f"{t} ({c:+.3f})" for t, c in negatifs))

    e = expliquer(pipeline, args.texte, avis_de_reference())
    verdict = max(e["probas"], key=e["probas"].get)
    print(f"\nAvis : « {args.texte} »")
    print(f"Prédiction : {verdict} (confiance {e['probas'][verdict]:.4f})")
    print(f"Valeur de base, l'avis moyen d'entraînement : {e['base']:+.4f}")
    vers_negatif = [(t, v) for t, v in e["presents"] if v < 0]
    vers_positif = [(t, v) for t, v in e["presents"] if v > 0]
    for nom, liste in (("negative", vers_negatif), ("positive", vers_positif)):
        total = sum(v for _, v in liste)
        print(f"Termes présents qui poussent vers « {nom} » : {len(liste)}, au total {total:+.4f}")
        print("  " + ", ".join(f"{t} ({v:+.4f})" for t, v in liste[:6]))
    print(f"Les termes absents, au total : {e['absents']:+.4f}")
    print(f"Base + contributions = {e['base'] + e['valeurs'].sum():+.4f} ; sortie du modèle = {e['sortie']:+.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
