"""Contrats d'entrée et de sortie de l'API (Pydantic v2)."""
from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class PredictRequest(BaseModel):
    """Requête de prédiction."""
    text: str = Field(..., min_length=1, max_length=2000, description="Texte à classifier",
                      examples=["Livraison rapide, produit conforme, très satisfait"])

    @field_validator("text")
    @classmethod
    def valider_texte_non_vide(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Le texte ne peut pas être vide ou constitué uniquement d'espaces")
        return v


class PredictResponse(BaseModel):
    """Réponse de prédiction."""
    label: str = Field(..., description="POSITIVE, NEGATIVE ou INDETERMINE")
    score: float = Field(..., ge=0, le=1, description="Confiance de la classe prédite")
    text: str = Field(..., description="Aperçu du texte analysé (100 caractères)")


class HealthResponse(BaseModel):
    """Réponse de l'endpoint de santé."""
    status: str = Field(..., description="OK si le modèle est chargé")
    model: str = Field(..., description="Nom du modèle servi")


class ErrorResponse(BaseModel):
    """Format standard des erreurs FastAPI."""
    detail: str

