"""Feature routes — Scenarios, XAI, AI Assistant, Performance Metrics."""
from __future__ import annotations

import logging
from typing import Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from services.scenario_presets import list_scenarios, get_scenario
from services.xai_engine import XAIEngine
from services.ai_assistant import AIAssistant

logger = logging.getLogger("quantumpulse.features")
router = APIRouter()

# Module-level AI assistant singleton (shares latest context via streaming)
assistant = AIAssistant()


# ═══════════════ Scenario Presets ═══════════════

@router.get("/scenarios")
async def get_scenarios():
    """List all available real-world scenario presets."""
    try:
        return {"scenarios": list_scenarios()}
    except Exception as exc:
        logger.error("Failed to list scenarios: %s", exc)
        return {"scenarios": []}


@router.get("/scenarios/{scenario_id}")
async def get_scenario_detail(scenario_id: str):
    """Get a specific scenario preset with full configuration."""
    try:
        preset = get_scenario(scenario_id)
        if not preset:
            return {"error": "Scenario not found", "available": [s["id"] for s in list_scenarios()]}
        return {
            "id": preset.id,
            "name": preset.name,
            "description": preset.description,
            "config": {
                "num_signals": preset.num_signals,
                "noise_level": preset.noise_level,
                "sample_rate": preset.sample_rate,
                "duration": preset.duration,
            },
            "frequency_range": list(preset.frequency_range),
            "modulations": preset.modulations,
            "congestion_factor": preset.congestion_factor,
            "interference_intensity": preset.interference_intensity,
        }
    except Exception as exc:
        logger.error("Failed to get scenario '%s': %s", scenario_id, exc)
        return {"error": "Failed to load scenario", "available": []}


# ═══════════════ AI Assistant ═══════════════

class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)


@router.post("/assistant/ask")
async def ask_assistant(req: AskRequest):
    """Ask the AI assistant a question about the system's current state."""
    answer = assistant.ask(req.question)
    return {"question": req.question, "answer": answer}
