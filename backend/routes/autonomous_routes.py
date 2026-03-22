"""Autonomous reconfiguration API routes."""
from __future__ import annotations

import logging

from fastapi import APIRouter

from services.autonomous_engine import AutonomousEngine

logger = logging.getLogger("quantumpulse.autonomous")

router = APIRouter()

# Module-level singleton (lightweight; real work happens in the WebSocket pipeline)
_engine: AutonomousEngine | None = None


def _get_engine() -> AutonomousEngine:
    global _engine
    if _engine is None:
        _engine = AutonomousEngine()
    return _engine


@router.get("/status")
async def autonomous_status():
    """Return the current autonomous engine state."""
    return _get_engine().get_status()
