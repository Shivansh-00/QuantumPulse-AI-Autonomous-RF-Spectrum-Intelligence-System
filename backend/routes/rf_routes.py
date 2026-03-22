"""RF Simulation API routes."""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.schemas import SimulationRequest, SimulationResponse, AnalysisRequest, AnalysisResponse
from models.db_models import SignalLog
from services.rf_simulation import (
    RFSimulator, SimulationConfig, SignalConfig, create_default_simulation,
)
from services.signal_processing import SignalProcessor
from utils.helpers import downsample

logger = logging.getLogger("quantumpulse.rf")

router = APIRouter()


@router.post("/simulate", response_model=SimulationResponse)
async def simulate_rf(request: SimulationRequest, db: AsyncSession = Depends(get_db)):
    """Generate RF spectrum simulation."""
    if request.signals:
        signals = [
            SignalConfig(
                frequency=s.frequency,
                amplitude=s.amplitude,
                bandwidth=s.bandwidth,
                modulation=s.modulation,
                priority=s.priority,
            )
            for s in request.signals
        ]
        config = SimulationConfig(
            sample_rate=request.sample_rate,
            duration=request.duration,
            noise_level=request.noise_level,
            signals=signals,
        )
        sim = RFSimulator(config)
        result = sim.simulate()
    else:
        result = create_default_simulation(
            num_signals=request.num_signals,
            sample_rate=request.sample_rate,
            duration=request.duration,
            noise_level=request.noise_level,
        )

    # Log to database (best-effort — don't fail the response if DB is down)
    try:
        log = SignalLog(
            sample_rate=result["sample_rate"],
            duration=result["duration"],
            num_signals=result["num_signals"],
            noise_level=request.noise_level,
            signal_configs=result["signal_configs"],
            signal_summary={
                "signal": downsample(result["signal"], 200),
                "clean_signal": downsample(result["clean_signal"], 200),
            },
        )
        db.add(log)
        logger.info("Simulation logged: %d signals @ %d Hz", result["num_signals"], result["sample_rate"])
    except Exception as exc:
        logger.warning("Failed to log simulation to DB: %s", exc)

    return result


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_signal(request: AnalysisRequest):
    """Analyze an RF signal and return spectral features."""
    processor = SignalProcessor(request.signal, request.sample_rate)
    return processor.full_analysis()


@router.get("/quick-sim")
async def quick_simulation():
    """Quick simulation with default parameters for testing."""
    result = create_default_simulation(num_signals=5)
    # Downsample for quick response
    step = max(1, len(result["time"]) // 1000)
    return {
        "time": result["time"][::step],
        "signal": result["signal"][::step],
        "clean_signal": result["clean_signal"][::step],
        "sample_rate": result["sample_rate"],
        "num_signals": result["num_signals"],
        "signal_configs": result["signal_configs"],
        "rlc_metrics": result.get("rlc_metrics"),
        "channel_metrics": result.get("channel_metrics"),
    }
