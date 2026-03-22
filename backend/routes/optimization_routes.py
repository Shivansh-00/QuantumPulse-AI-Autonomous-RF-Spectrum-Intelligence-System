"""Optimization API routes."""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.schemas import OptimizationRequest, OptimizationResponse
from models.db_models import OptimizationLog
from services.optimization_engine import optimize_from_simulation

logger = logging.getLogger("quantumpulse.optimization")

router = APIRouter()


@router.post("/frequency", response_model=OptimizationResponse)
async def optimize_frequencies(
    request: OptimizationRequest, db: AsyncSession = Depends(get_db)
):
    """Run quantum-inspired frequency optimization."""
    result = optimize_from_simulation(
        signal_configs=request.signal_configs,
        band_occupancy=request.band_occupancy,
        rlc_resonant=request.rlc_resonant,
        rlc_bandwidth=request.rlc_bandwidth,
    )

    # Log result (best-effort — don't fail the response if DB is down)
    try:
        log = OptimizationLog(
            original_allocations=result["original_allocations"],
            optimized_allocations=result["optimized_allocations"],
            total_interference=result["total_interference"],
            signal_clarity=result["signal_clarity"],
            improvement_pct=result["improvement_pct"],
            iterations=result["iterations"],
        )
        db.add(log)
        logger.info("Optimization: improvement=%.1f%% clarity=%.3f", result["improvement_pct"], result["signal_clarity"])
    except Exception as exc:
        logger.warning("Failed to log optimization to DB: %s", exc)

    return result
