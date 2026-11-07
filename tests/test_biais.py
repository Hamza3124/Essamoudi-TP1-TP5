"""Tests de la mesure du biais (TP4, étape F)."""
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
MODELE = RACINE / "models" / "sentiment.joblib"
DEMO = RACINE / "data" / "demo_reviews.csv"

sys.path.insert(0, str(RACINE / "src"))

import biais  # noqa: E402


@pytest.mark.parametrize("texte, attendu", [
    ("Bon produit, mais livraison lente", True),
    ("Déçu au début, sauf que ensuite tout va bien", True),
    ("Livré à la maison en deux jours", False),        # « maison » ne contient pas le mot « mais »
    ("Utilisé depuis un mois sans souci", False),       # ni « depuis » le mot « puis »
    ("MAIS FINALEMENT très satisfait", True),
])
def test_retournement_detecte_sur_des_mots_entiers(texte, attendu):
    assert biais.a_un_retournement(texte) is attendu


def test_mesurer_compte_par_groupe():
    textes = ["a b", "c d e f", "g h", "i j k l"]
    vrais = ["positive", "negative", "negative", "positive"]
    predits = ["positive", "positive", "negative", "positive"]
    confiances = [0.9, 0.55, 0.8, 0.65]
    r = biais.mesurer(textes, vrais, predits, confiances,
                      lambda t: "long" if len(t.split()) > 2 else "court", seuil=0.60)
    assert r["court"] == {"avis": 2, "exactitude": 1.0, "erreurs": 0, "vers_humain": 0,
                          "erreurs_restantes": 0}
    assert r["long"] == {"avis": 2, "exactitude": 0.5, "erreurs": 1, "vers_humain": 1,
                         "erreurs_restantes": 0}


@pytest.fixture(scope="module")
def jeu():
    if not MODELE.exists() or not DEMO.exists():
        pytest.skip("modèle ou jeu de démonstration absent sur ce poste")
    return biais.jeu_de_test()


def test_les_avis_avec_retournement_sont_moins_bien_servis(jeu):
    r = biais.mesurer(*jeu, lambda t: "avec" if biais.a_un_retournement(t) else "direct")
    assert r["avec"]["exactitude"] < r["direct"]["exactitude"]


def test_la_longueur_n_explique_rien_une_fois_le_retournement_mis_a_part(jeu):
    textes, vrais, predits, _ = jeu
    longs_directs = [i for i, t in enumerate(textes)
                     if biais.nombre_de_mots(t) > 9 and not biais.a_un_retournement(t)]
    assert longs_directs, "le jeu de test contient des avis longs sans retournement"
    assert all(vrais[i] == predits[i] for i in longs_directs)
