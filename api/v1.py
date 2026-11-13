"""Router de l'API /v1 : routes versionnées et protégées."""
from __future__ import annotations

import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status

from api.schemas import HealthResponse, PredictRequest, PredictResponse
from api.securite import verifier_cle

logger = logging.getLogger("sentiment_api.v1")

router = APIRouter(prefix="/v1", tags=["v1"])


def get_classifier_v1(request: Request):
    """Récupère l'instance du classifieur ou renvoie une erreur 503 standardisée."""
    clf = getattr(request.app.state, "classifier", None)
    if clf is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "erreur": {
                    "code": "MODELE_INDISPONIBLE",
                    "message": "Modèle de sentiment non chargé",
                    "champs": [],
                }
            },
        )
    return clf


@router.get("/health", response_model=HealthResponse, summary="Santé de l'API v1")
async def health_check_v1(request: Request):
    """Vérification de l'état de l'API v1 (route publique)."""
    clf = get_classifier_v1(request)
    return {"status": "OK", "model": clf.model_name}


@router.post("/predict", response_model=PredictResponse, summary="Classifier un texte (v1)")
async def predict_v1(
    body: PredictRequest,
    request: Request,
    role: str = Depends(verifier_cle),
):
    """Analyse le sentiment d'un texte.

    Nécessite une clé d'API valide passée dans l'en-tête X-API-Key.
    """
    clf = get_classifier_v1(request)
    try:
        result = clf.predict(body.text)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "erreur": {
                    "code": "ENTREE_INVALIDE",
                    "message": str(e),
                    "champs": ["text"],
                }
            },
        )
    except Exception:
        logger.exception("Erreur lors de la prédiction v1")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "erreur": {
                    "code": "ERREUR_INTERNE",
                    "message": "Erreur interne du serveur",
                    "champs": [],
                }
            },
        )
    logger.info("v1 predict (%s): %r -> %s (%.2f)", role, body.text[:50], result["label"], result["score"])
    return result

