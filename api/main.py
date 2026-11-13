"""API REST du classifier de sentiment (TP3 et TP Spring Boot).

Lancer : uvicorn api.main:app --reload
Doc    : http://localhost:8000/docs
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exception_handlers import (
    http_exception_handler as default_http_handler,
    request_validation_exception_handler as default_validation_handler,
)
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.datastructures import State

# Assure la compatibilité avec monkeypatch de pytest sur app.state
if not hasattr(State, "classifier"):
    State.classifier = property(
        lambda self: self._state.get("classifier"),
        lambda self, val: self._state.__setitem__("classifier", val),
        lambda self: self._state.__delitem__("classifier") if "classifier" in self._state else None,
    )

from api.model import load_model
from api.schemas import HealthResponse, PredictRequest, PredictResponse
from api.v1 import router as v1_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("sentiment_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Charge le modèle une seule fois, au démarrage."""
    logger.info("Démarrage de l'API...")
    app.state.classifier = load_model()
    logger.info("Modèle chargé avec succès : %s", app.state.classifier.model_name)
    yield
    logger.info("Arrêt de l'API")


app = FastAPI(
    title="Sentiment Analysis API",
    description="Classifie le sentiment d'un avis en français (modèle du TP2).",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Pour les routes /v1, renvoie une structure d'erreur standardisée attendue par le client Java."""
    if request.url.path.startswith("/v1"):
        champs = [str(err["loc"][-1]) for err in exc.errors() if "loc" in err and len(err["loc"]) > 0]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "erreur": {
                    "code": "ENTREE_INVALIDE",
                    "message": "Entrée invalide ou champ manquant",
                    "champs": champs,
                }
            },
        )
    return await default_validation_handler(request, exc)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Gestion des exceptions HTTP avec format standardisé pour /v1."""
    headers = getattr(exc, "headers", None)
    if isinstance(exc.detail, dict) and "erreur" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail, headers=headers)
    if request.url.path.startswith("/v1"):
        code_map = {
            400: "ENTREE_INVALIDE",
            401: "NON_AUTHENTIFIE",
            403: "ACCES_REFUSE",
            404: "NON_TROUVE",
            422: "ENTREE_INVALIDE",
            503: "MODELE_INDISPONIBLE",
        }
        code = code_map.get(exc.status_code, "ERREUR_INTERNE")
        return JSONResponse(
            status_code=exc.status_code,
            content={"erreur": {"code": code, "message": str(exc.detail), "champs": []}},
            headers=headers,
        )
    return await default_http_handler(request, exc)


app.include_router(v1_router)


def _classifier():
    clf = getattr(app.state, "classifier", None)
    if clf is None:
        raise HTTPException(status_code=503, detail="Modèle non chargé")
    return clf


@app.get("/", summary="Accueil")
async def root():
    return {"message": "Sentiment Analysis API", "docs": "/docs", "health": "/health"}


@app.get("/health", response_model=HealthResponse, summary="Santé de l'API")
async def health_check():
    """Répond 200 si le modèle est chargé, 503 sinon."""
    return {"status": "OK", "model": _classifier().model_name}


@app.post("/predict", response_model=PredictResponse, summary="Classifier un texte")
async def predict(request: PredictRequest):
    """Renvoie le sentiment (POSITIVE, NEGATIVE ou INDETERMINE) et la confiance.

    - 422 : texte vide, constitué uniquement d'espaces ou invalide (Pydantic)
    - 503 : modèle non chargé
    - 500 : erreur inattendue du serveur
    """
    clf = _classifier()
    try:
        result = clf.predict(request.text)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        logger.exception("Erreur lors de la prédiction")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")
    logger.info("predict: %r -> %s (%.2f)", request.text[:50], result["label"], result["score"])
    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, log_level="info")
