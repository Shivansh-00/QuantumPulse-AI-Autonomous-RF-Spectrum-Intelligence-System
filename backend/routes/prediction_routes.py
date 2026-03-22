"""AI Prediction API routes."""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.schemas import PredictionRequest, PredictionResponse
from models.db_models import PredictionLog
from services.ai_prediction import CongestionPredictor

logger = logging.getLogger("quantumpulse.prediction")

router = APIRouter()

# Lazy-initialized predictor instance
_predictor_cache = {}


def _get_predictor(model_type: str = "lstm") -> CongestionPredictor:
    if model_type not in _predictor_cache:
        _predictor_cache[model_type] = CongestionPredictor(model_type=model_type)
    return _predictor_cache[model_type]


@router.post("/congestion", response_model=PredictionResponse)
async def predict_congestion(
    request: PredictionRequest, db: AsyncSession = Depends(get_db)
):
    """Predict spectrum congestion from signal data."""
    predictor = _get_predictor(request.model_type)
    result = predictor.predict(request.signal_data)

    # Log prediction (best-effort — don't fail the response if DB is down)
    try:
        log = PredictionLog(
            mean_congestion=result["mean_congestion"],
            max_congestion=result["max_congestion"],
            risk_level=result["risk_level"],
            congestion_levels=result["congestion_levels"],
            model_type=request.model_type,
        )
        db.add(log)
        logger.info("Prediction: risk=%s mean=%.3f", result["risk_level"], result["mean_congestion"])
    except Exception as exc:
        logger.warning("Failed to log prediction to DB: %s", exc)

    return result


@router.post("/train")
async def train_model(model_type: str = "lstm", epochs: int = 20):
    """Train prediction model on synthetic data."""
    predictor = _get_predictor(model_type)
    sequences, targets = predictor.generate_synthetic_training_data(num_samples=100)
    train_result = predictor.train_on_data(sequences, targets, epochs=epochs)
    logger.info("Training complete: model=%s epochs=%d loss=%.4f", model_type, epochs, train_result["final_loss"])
    return {
        "status": "training_complete",
        "model_type": model_type,
        **train_result,
    }
