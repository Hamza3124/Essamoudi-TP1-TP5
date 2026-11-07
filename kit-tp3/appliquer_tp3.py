#!/usr/bin/env python
"""Installe le kit TP3 (l'API FastAPI) dans un dépôt sentiment-app existant.

Usage, depuis ce dossier :
  python appliquer_tp3.py ../sentiment-app --simulation   # voir ce qui sera fait, sans rien écrire
  python appliquer_tp3.py ../sentiment-app

Prérequis : le TP2 (src/predict.py). Le script copie api/, tests/test_api.py, docs/semaine3.md
et les documents du TP, sans jamais écraser un fichier existant. Il vérifie que requirements.txt
contient FastAPI, uvicorn et httpx, permet à pytest d'importer api/ (pytest.ini), puis apprend
à la CI à installer l'API et à entraîner le modèle avant les tests.
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
A_COPIER = [
    "api/__init__.py", "api/model.py", "api/schemas.py", "api/main.py",
    "tests/test_api.py", "docs/semaine3.md", "TP3-ENONCE.md", "MARCHE-A-SUIVRE-TP3.md",
]
DEPENDANCES = {"fastapi": "fastapi==0.115.*", "uvicorn": "uvicorn[standard]==0.30.*", "httpx": "httpx==0.27.*"}
PAQUETS_CI = '"fastapi==0.115.*" "httpx==0.27.*" "uvicorn==0.30.*"'
ENTRAINEMENT = "python src/make_demo.py && python src/train.py"


def nom_paquet(ligne: str) -> str:
    ligne = ligne.split("#", 1)[0].strip()
    if not ligne or ligne.startswith("-"):
        return ""
    return re.split(r"[\[<>=!~ ;]", ligne, maxsplit=1)[0].lower().replace("_", "-")


def completer_requirements(depot: Path, simulation: bool) -> None:
    req = depot / "requirements.txt"
    if not req.is_file():
        print("  ATTENTION      requirements.txt introuvable")
        return
    lignes = req.read_text(encoding="utf-8").splitlines()
    presents = {nom_paquet(ligne) for ligne in lignes}
    manquants = [version for nom, version in DEPENDANCES.items() if nom not in presents]
    if not manquants:
        print("  déjà là        requirements.txt : fastapi, uvicorn, httpx")
        return
    print(f"  complète       requirements.txt : {', '.join(manquants)}")
    if not simulation:
        req.write_text("\n".join(lignes).rstrip() + "\n" + "\n".join(manquants) + "\n", encoding="utf-8")


def completer_pytest_ini(depot: Path, simulation: bool) -> None:
    """Sans « pythonpath = . », la commande pytest seule ne trouve pas le paquet api/."""
    ini = depot / "pytest.ini"
    if not ini.is_file():
        print("  ATTENTION      pytest.ini introuvable : ajoutez « pythonpath = . » à la configuration de pytest")
        return
    lignes = ini.read_text(encoding="utf-8").splitlines()
    if any(ligne.strip().startswith("pythonpath") for ligne in lignes):
        print("  déjà là        pytest.ini : pythonpath")
        return
    if "[pytest]" not in [ligne.strip() for ligne in lignes]:
        print("  ATTENTION      pytest.ini sans section [pytest] : ajoutez « pythonpath = . » à la main")
        return
    position = [ligne.strip() for ligne in lignes].index("[pytest]") + 1
    lignes.insert(position, "pythonpath = .")
    print("  complète       pytest.ini : pythonpath = . (les tests importent api/)")
    if not simulation:
        ini.write_text("\n".join(lignes) + "\n", encoding="utf-8")


def adapter_ci(depot: Path, simulation: bool) -> None:
    ci = depot / ".github" / "workflows" / "ci.yml"
    if not ci.is_file():
        print("  ATTENTION      .github/workflows/ci.yml introuvable : ajoutez à la main l'installation de")
        print(f"                 fastapi et httpx, puis « {ENTRAINEMENT} » avant les tests")
        return
    lignes = ci.read_text(encoding="utf-8").splitlines()
    texte = "\n".join(lignes)
    modifs = []

    # 1. Les paquets de l'API, si la CI installe une liste de paquets plutôt que requirements.txt
    if "fastapi" not in texte:
        for i, ligne in enumerate(lignes):
            if "pip install" in ligne and "requirements-dev" not in ligne:
                if "-r requirements.txt" not in ligne:
                    lignes[i] = ligne.rstrip() + " " + PAQUETS_CI
                    modifs.append("installation de fastapi, httpx et uvicorn")
                break

    # 2. L'entraînement du modèle, juste avant l'étape qui lance pytest
    if "src/train.py" not in texte:
        tests = next((i for i, ligne in enumerate(lignes)
                      if re.search(r"\bpytest\b", ligne) and "pip install" not in ligne
                      and not ligne.lstrip().startswith("#")), None)
        if tests is None:
            print(f"  ATTENTION      étape pytest introuvable dans ci.yml : ajoutez « {ENTRAINEMENT} » avant les tests")
        else:
            debut = tests
            while debut > 0 and not lignes[debut].lstrip().startswith("- "):
                debut -= 1
            retrait = lignes[debut][: len(lignes[debut]) - len(lignes[debut].lstrip())]
            activation = ". .venv/bin/activate && " if ".venv/bin/activate" in lignes[tests] else ""
            lignes[debut:debut] = [
                f"{retrait}- name: Modèle de démonstration, pour les tests de l'API (TP3)",
                f"{retrait}  run: {activation}{ENTRAINEMENT}",
            ]
            modifs.append("entraînement du modèle avant les tests")

    if not modifs:
        print("  déjà là        .github/workflows/ci.yml")
        return
    print(f"  complète       .github/workflows/ci.yml : {', '.join(modifs)}")
    if not simulation:
        ci.write_text("\n".join(lignes) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("depot", help="chemin du dépôt sentiment-app")
    parser.add_argument("--simulation", action="store_true", help="n'écrit rien, affiche seulement")
    args = parser.parse_args()

    depot = Path(args.depot).expanduser().resolve()
    if not (depot / "README.md").is_file() or not (depot / "tests").is_dir():
        print(f"ERREUR : {depot} ne ressemble pas au dépôt du cours (README.md et tests/ attendus)")
        return 1
    predict = depot / "src" / "predict.py"
    if not predict.is_file() or "def charger_modele" not in predict.read_text(encoding="utf-8"):
        print("ERREUR : src/predict.py du TP2 introuvable, ou sans charger_modele(). Faites d'abord le TP2.")
        return 1
    print(f"Dépôt cible : {depot}")

    for chemin in A_COPIER:
        src, dst = KIT / chemin, depot / chemin
        if not src.exists():
            print(f"  ABSENT DU KIT  {chemin}")
        elif dst.exists():
            print(f"  conservé       {chemin} (déjà présent, non écrasé)")
        else:
            print(f"  ajoute         {chemin}")
            if not args.simulation:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
    completer_requirements(depot, args.simulation)
    completer_pytest_ini(depot, args.simulation)
    adapter_ci(depot, args.simulation)

    print("\nSimulation : rien n'a été écrit." if args.simulation else
          "\nKit installé. Suite, dans le dépôt : python src/train.py, puis MARCHE-A-SUIVRE-TP3.md, contrôle T14.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
