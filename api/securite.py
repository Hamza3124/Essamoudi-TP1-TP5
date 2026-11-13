"""Sécurité de l'API /v1 : authentification par clé d'API et gestion des rôles."""
from __future__ import annotations

import os
from typing import Dict, Optional
from fastapi import Header, HTTPException, status
from dotenv import load_dotenv

load_dotenv()


def charger_cles() -> Dict[str, str]:
    """Charge les clés d'API et leurs rôles associés depuis les variables d'environnement.

    Supporte le format 'cle1:role1,cle2:role2' dans API_KEYS
    ainsi que la variable unitaire API_KEY (rôle 'client' par défaut).
    """
    cles: Dict[str, str] = {}
    brut = os.getenv("API_KEYS", "")
    if brut:
        for paire in brut.split(","):
            paire = paire.strip()
            if not paire:
                continue
            if ":" in paire:
                cle, role = paire.split(":", 1)
                cles[cle.strip()] = role.strip()
            else:
                cles[paire] = "client"

    cle_unique = os.getenv("API_KEY", "")
    if cle_unique and cle_unique != "changez-moi" and cle_unique not in cles:
        cles[cle_unique] = "client"

    return cles


def verifier_cle(x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> str:
    """Valide la clé d'API transmise dans l'en-tête X-API-Key.

    Renvoie le rôle associé si valide.
    Lève un code HTTP 401 avec corps standardisé et en-tête WWW-Authenticate sinon.
    """
    cles = charger_cles()
    if not x_api_key or x_api_key not in cles:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "erreur": {
                    "code": "NON_AUTHENTIFIE",
                    "message": "Clé d'API absente ou invalide",
                    "champs": [],
                }
            },
            headers={"WWW-Authenticate": "APIKey"},
        )
    return cles[x_api_key]


def verifier_role(role_requis: str):
    """Dépendance FastAPI vérifiant qu'une clé possède le rôle requis (ou admin)."""
    def _dependance(role: str = verifier_cle):
        if role != role_requis and role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "erreur": {
                        "code": "ACCES_REFUSE",
                        "message": "Rôle insuffisant pour cette opération",
                        "champs": [],
                    }
                },
            )
        return role
    return _dependance

