"""Tests des graphiques de la page (TP5, étape G)."""
from pathlib import Path

import pandas as pd
import pytest

from ui import graphiques
from ui.client import Reponse

RACINE = Path(__file__).resolve().parents[1]
MODELE = RACINE / "models" / "sentiment.joblib"


def test_la_repartition_montre_toutes_les_categories():
    reponses = [Reponse(True, "POSITIVE", 0.9), Reponse(True, "POSITIVE", 0.7),
                Reponse(False, message="Texte refusé")]
    assert graphiques.repartition(reponses)["avis"].to_dict() == {
        "positif": 2, "négatif": 0, "à vérifier": 0, "refus ou erreur": 1}


def test_l_histogramme_range_chaque_confiance_dans_sa_tranche():
    reponses = [Reponse(True, "INDETERMINE", 0.5), Reponse(True, "POSITIVE", 0.6),
                Reponse(True, "NEGATIVE", 0.799), Reponse(True, "POSITIVE", 1.0),
                Reponse(False, message="API injoignable")]
    assert graphiques.histogramme_confiances(reponses)["avis"].to_dict() == {
        "50-60 %": 1, "60-70 %": 1, "70-80 %": 1, "80-90 %": 0, "90-100 %": 1}


def test_les_graphiques_s_affichent(tmp_path):
    from streamlit.testing.v1 import AppTest

    page = tmp_path / "page.py"
    page.write_text(
        "import sys\n"
        f"sys.path.insert(0, {str(RACINE)!r})\n"
        "import streamlit as st\n"
        "from ui import graphiques\n"
        "from ui.client import Reponse\n"
        "r = [Reponse(True, 'POSITIVE', 0.777), Reponse(True, 'INDETERMINE', 0.5162)]\n"
        "st.bar_chart(graphiques.repartition(r))\n"
        "st.bar_chart(graphiques.histogramme_confiances(r))\n",
        encoding="utf-8",
    )
    resultat = AppTest.from_file(str(page), default_timeout=30).run()
    assert not resultat.exception
    assert len(resultat.get("arrow_vega_lite_chart")) == 2


def test_le_fichier_d_exemple_a_travers_l_api():
    if not MODELE.exists():
        pytest.skip("models/sentiment.joblib absent sur ce poste")
    from fastapi.testclient import TestClient

    from api.main import app
    from ui import client

    textes = pd.read_csv(RACINE / "data" / "avis_exemple.csv")["text"].astype(str).tolist()
    with TestClient(app) as session:
        reponses = client.predire_lot(session, textes)
    assert graphiques.repartition(reponses)["avis"].to_dict() == {
        "positif": 3, "négatif": 2, "à vérifier": 1, "refus ou erreur": 0}
    assert graphiques.histogramme_confiances(reponses)["avis"].to_dict() == {
        "50-60 %": 1, "60-70 %": 1, "70-80 %": 3, "80-90 %": 1, "90-100 %": 0}
