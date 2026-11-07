"""Tests de l'explication du modèle (TP2, étape F).

Ignorés tant que le modèle ou le jeu de démonstration manquent sur le poste, comme les tests de
prédiction du TP2. Dès le TP3, la CI entraîne le modèle : ils y tournent aussi.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

RACINE = Path(__file__).resolve().parents[1]
MODELE = RACINE / "models" / "sentiment.joblib"
DEMO = RACINE / "data" / "demo_reviews.csv"

sys.path.insert(0, str(RACINE / "src"))


@pytest.fixture(scope="module")
def modele():
    if not MODELE.exists() or not DEMO.exists():
        pytest.skip("modèle ou jeu de démonstration absent sur ce poste (normal en CI au TP2)")
    import joblib

    import expliquer

    return joblib.load(MODELE), expliquer.avis_de_reference()


@pytest.fixture(scope="module")
def explication(modele):
    import expliquer

    pipeline, reference = modele
    return expliquer.expliquer(pipeline, expliquer.AVIS_PAR_DEFAUT, reference)


def test_les_contributions_redonnent_la_sortie_du_modele(explication):
    total = explication["base"] + explication["valeurs"].sum()
    assert total == pytest.approx(explication["sortie"], abs=1e-6)


def test_pour_un_modele_lineaire_shap_se_calcule_a_la_main(modele, explication):
    import expliquer

    pipeline, reference = modele
    vect, clf = pipeline.named_steps["tfidf"], pipeline.named_steps["clf"]
    x = vect.transform([expliquer.AVIS_PAR_DEFAUT]).toarray()[0]
    moyenne = np.asarray(vect.transform(reference).mean(axis=0)).ravel()
    assert np.allclose(explication["valeurs"], clf.coef_[0] * (x - moyenne))


def test_les_termes_influents_sont_ordonnes(modele):
    import expliquer

    positifs, negatifs = expliquer.mots_influents(modele[0], n=8)
    assert len(positifs) == len(negatifs) == 8
    assert all(c > 0 for _, c in positifs) and all(c < 0 for _, c in negatifs)
    assert [c for _, c in positifs] == sorted((c for _, c in positifs), reverse=True)
    assert [c for _, c in negatifs] == sorted(c for _, c in negatifs)


def test_l_avis_mitige_fait_hesiter_le_modele(explication):
    assert max(explication["probas"].values()) < 0.60
    vers_negatif = sum(v for _, v in explication["presents"] if v < 0)
    vers_positif = sum(v for _, v in explication["presents"] if v > 0)
    assert abs(vers_negatif + vers_positif) < 0.2, "les deux moitiés de l'avis se compensent presque"
