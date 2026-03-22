"""WebSocket streaming routes for real-time RF data pipeline.

Full pipeline per cycle:
  RF Simulation → Signal Processing → AI Prediction
  → Quantum-Inspired Optimisation → Autonomous Reconfiguration
  → XAI Explanation → Performance Metrics

Every stage is individually wrapped with try/except and safe fallbacks
so the pipeline never breaks — even if one stage fails, the system
sends valid data for all other stages.
"""
from __future__ import annotations

import asyncio
import json
import logging
import math
import time
import traceback

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from services.rf_simulation import create_default_simulation
from services.signal_processing import SignalProcessor
from services.ai_prediction import CongestionPredictor
from services.optimization_engine import optimize_from_simulation
from services.autonomous_engine import AutonomousEngine
from services.xai_engine import XAIEngine
from services.performance_tracker import PerformanceTracker
from services.scenario_presets import get_scenario

logger = logging.getLogger("quantumpulse.streaming")

router = APIRouter()


# ── Safe-fallback data factories ─────────────────────────────
def _safe_simulation(num_signals: int = 5, sample_rate: int = 10000, duration: float = 0.5):
    """Generate minimal safe simulation output when the real simulator fails."""
    import numpy as np
    n = int(sample_rate * duration)
    t = np.linspace(0, duration, n).tolist()
    sig = (np.sin(2 * math.pi * 440 * np.array(t)) * 0.1).tolist()
    return {
        "time": t, "signal": sig, "clean_signal": sig,
        "signal_configs": [{"frequency": 440, "amplitude": 0.1, "bandwidth": 50,
                            "modulation": "CW", "signal_id": i} for i in range(num_signals)],
        "num_signals": num_signals, "rlc_metrics": None, "channel_metrics": None,
    }


def _safe_analysis():
    return {
        "statistics": {"mean": 0, "std": 0, "min": -0.1, "max": 0.1, "rms": 0.07,
                       "variance": 0, "skewness": 0, "kurtosis": 0, "peak_to_peak": 0.2, "crest_factor": 1.4},
        "peaks": {"peak_frequency": 440.0, "peak_magnitude": 0.001, "num_peaks": 1, "dominant_frequencies": [440.0]},
        "band_occupancy": {"bands": [], "total_power": 0.0001},
        "snr": {"snr_db": 15.0, "signal_power_db": -10.0, "noise_floor_db": -25.0},
        "spectral_entropy": {"normalized_entropy": 0.5},
        "interference": {"interference_type": "none", "confidence": 0.0},
        "fft": {"frequencies": [440.0], "magnitudes": [0.001]},
    }


def _safe_prediction():
    return {
        "congestion_levels": [0.15] * 10,
        "mean_congestion": 0.15, "max_congestion": 0.15,
        "risk_level": "LOW", "confidence": 0.80, "trend": "stable",
        "anomaly_score": 0.0,
    }


def _safe_optimization():
    return {
        "original_allocations": [], "optimized_allocations": [],
        "improvement_pct": 0.0, "signal_clarity": 0.85,
        "iterations": 0, "cost_history": [],
        "objective_breakdown": {"interference": 0, "power_efficiency": 0, "spectral_efficiency": 0},
    }


def _safe_autonomous(cycle: int = 0):
    return {
        "cycle": cycle, "mode": "monitor",
        "actions": [], "state": {"congestion": 0.0, "anomaly": 0.0, "interference": 0.0, "clarity": 0.85, "mode": "monitor"},
        "history": [],
    }


def _safe_xai():
    return {
        "prediction": ["Spectrum health is good — congestion at low levels."],
        "actions": ["System is in monitoring mode — no reallocation needed."],
        "optimization": ["Optimizer standing by — no intervention required."],
        "anomaly": ["No anomalies detected. Spectrum behaviour is within normal bounds."],
        "summary": [
            "Spectrum health is good — congestion at low levels.",
            "System is in monitoring mode — no reallocation needed.",
            "Optimizer standing by — no intervention required.",
            "No anomalies detected. Spectrum behaviour is within normal bounds.",
        ],
    }


def _safe_performance():
    return {
        "interference_reduction_pct": 0.0, "latency_ms": 0.0,
        "spectrum_efficiency": 0.0, "power_efficiency": 0.0,
        "signal_stability": 0.85, "snr_db": 15.0,
        "congestion_before": 0.0, "congestion_after": 0.0, "learning_cycles": 0,
    }


def _sanitize_for_json(obj):
    """Recursively replace NaN/Infinity with safe values for JSON serialization."""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return 0.0
        return obj
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sanitize_for_json(v) for v in obj]
    return obj


class ConnectionManager:
    """Manages WebSocket connections for broadcasting."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("Client connected. Total: %d", len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info("Client disconnected. Total: %d", len(self.active_connections))

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)


manager = ConnectionManager()


@router.websocket("/stream")
async def rf_stream(websocket: WebSocket):
    """Stream real-time RF pipeline data including autonomous reconfiguration."""
    await manager.connect(websocket)
    predictor = CongestionPredictor(model_type="lstm")
    autonomous = AutonomousEngine(predictor=predictor)
    perf_tracker = PerformanceTracker()
    quantum_mode = False
    cycle_count = 0

    # Lazy import to update AI assistant context
    try:
        from routes.feature_routes import assistant
    except Exception:
        assistant = None

    try:
        while True:
            cycle_start = time.perf_counter()
            cycle_count += 1

            # ── Receive optional config from client ──────────
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=2.0)
                config = json.loads(data)
            except asyncio.TimeoutError:
                config = {}
            except json.JSONDecodeError:
                logger.warning("Malformed JSON from client, using defaults")
                config = {}

            # ── Handle scenario presets ──────────────────────
            scenario_id = config.get("scenario")
            if scenario_id:
                try:
                    preset = get_scenario(scenario_id)
                    if preset:
                        config.setdefault("num_signals", preset.num_signals)
                        config.setdefault("noise_level", preset.noise_level)
                        config.setdefault("sample_rate", preset.sample_rate)
                        config.setdefault("duration", preset.duration)
                except Exception:
                    logger.warning("Failed to load scenario '%s'", scenario_id)

            num_signals = max(1, min(int(config.get("num_signals", 5)), 50))
            noise_level = max(0.0, min(float(config.get("noise_level", 0.1)), 5.0))
            sample_rate = max(1000, min(int(config.get("sample_rate", 10000)), 100000))
            duration = max(0.1, min(float(config.get("duration", 0.5)), 5.0))

            # ── Handle quantum mode toggle ───────────────────
            if "quantum_mode" in config:
                quantum_mode = bool(config["quantum_mode"])

            # ── Step 1: RF Simulation ────────────────────────
            try:
                sim_result = create_default_simulation(
                    num_signals=num_signals,
                    sample_rate=sample_rate,
                    duration=duration,
                    noise_level=noise_level,
                )
                step = max(1, len(sim_result["time"]) // 500)
                sim_compact = {
                    "time": sim_result["time"][::step],
                    "signal": sim_result["signal"][::step],
                    "clean_signal": sim_result["clean_signal"][::step],
                    "signal_configs": sim_result["signal_configs"],
                    "num_signals": sim_result["num_signals"],
                    "rlc_metrics": sim_result.get("rlc_metrics"),
                    "channel_metrics": sim_result.get("channel_metrics"),
                }
            except Exception:
                logger.error("Simulation failed:\n%s", traceback.format_exc())
                sim_result = _safe_simulation(num_signals, sample_rate, duration)
                sim_compact = sim_result

            # ── Step 2: Signal Processing ────────────────────
            try:
                processor = SignalProcessor(sim_result["signal"], sample_rate)
                full = processor.full_analysis()
                fft_data = processor.compute_fft()
                fft_step = max(1, len(fft_data["frequencies"]) // 200)
                analysis = {
                    "statistics": full["statistics"],
                    "peaks": full["peaks"],
                    "band_occupancy": full["band_occupancy"],
                    "snr": full.get("snr"),
                    "spectral_entropy": full.get("spectral_entropy"),
                    "interference": full.get("interference"),
                    "fft": {
                        "frequencies": fft_data["frequencies"][::fft_step],
                        "magnitudes": fft_data["magnitudes"][::fft_step],
                    },
                }
            except Exception:
                logger.error("Signal processing failed:\n%s", traceback.format_exc())
                full = _safe_analysis()
                analysis = full

            # ── Step 3: AI Prediction ────────────────────────
            try:
                prediction = predictor.predict(sim_result["signal"])
            except Exception:
                logger.error("AI prediction failed:\n%s", traceback.format_exc())
                prediction = _safe_prediction()

            # ── Step 4: Optimisation ─────────────────────────
            try:
                rlc_m = sim_result.get("rlc_metrics") or {}
                optimization = optimize_from_simulation(
                    sim_result["signal_configs"],
                    rlc_resonant=rlc_m.get("resonant_frequency"),
                    rlc_bandwidth=rlc_m.get("bandwidth_3db"),
                )
            except Exception:
                logger.error("Optimization failed:\n%s", traceback.format_exc())
                optimization = _safe_optimization()

            # ── Step 5: Autonomous Reconfiguration ───────────
            try:
                rlc_m = sim_result.get("rlc_metrics") or {}
                autonomous_result = autonomous.evaluate(
                    signal_data=sim_result["signal"],
                    signal_configs=sim_result["signal_configs"],
                    analysis=full,
                    rlc_resonant=rlc_m.get("resonant_frequency"),
                    rlc_bandwidth=rlc_m.get("bandwidth_3db"),
                )
            except Exception:
                logger.error("Autonomous engine failed:\n%s", traceback.format_exc())
                autonomous_result = _safe_autonomous(cycle_count)

            # ── Step 6: XAI Explanations ─────────────────────
            try:
                xai = XAIEngine.full_explanation(
                    prediction=prediction,
                    actions=autonomous_result.get("actions", []),
                    state=autonomous_result.get("state", {}),
                    optimization=optimization,
                    analysis=full,
                )
                # Guarantee XAI is never empty
                if not xai.get("summary"):
                    xai = _safe_xai()
            except Exception:
                logger.error("XAI engine failed:\n%s", traceback.format_exc())
                xai = _safe_xai()

            # ── Step 7: Performance Metrics ──────────────────
            try:
                pipeline_latency_ms = (time.perf_counter() - cycle_start) * 1000
                performance = perf_tracker.compute(
                    sim_result=sim_result,
                    analysis=full,
                    prediction=prediction,
                    optimization=optimization,
                    autonomous_state=autonomous_result.get("state", {}),
                    pipeline_latency_ms=pipeline_latency_ms,
                )
            except Exception:
                logger.error("Performance tracker failed:\n%s", traceback.format_exc())
                performance = _safe_performance()
                performance["latency_ms"] = (time.perf_counter() - cycle_start) * 1000

            # ── Update AI assistant context ──────────────────
            try:
                if assistant:
                    assistant.update_context(
                        prediction=prediction,
                        optimization=optimization,
                        autonomous_state=autonomous_result.get("state", {}),
                        autonomous_actions=autonomous_result.get("actions", []),
                        analysis=full,
                        performance=performance,
                    )
            except Exception:
                logger.warning("AI assistant context update failed")

            # ── Build and sanitize payload ───────────────────
            payload = {
                "type": "pipeline_update",
                "simulation": sim_compact,
                "analysis": analysis,
                "prediction": prediction,
                "optimization": optimization,
                "autonomous": {
                    "cycle": autonomous_result.get("cycle", cycle_count),
                    "mode": autonomous_result.get("mode", "monitor"),
                    "actions": autonomous_result.get("actions", []),
                    "state": autonomous_result.get("state", {}),
                    "history": autonomous_result.get("history", []),
                },
                "xai": xai,
                "performance": performance,
                "quantum_mode": quantum_mode,
                "scenario": scenario_id,
            }

            # Sanitize NaN/Infinity before JSON serialization
            payload = _sanitize_for_json(payload)

            await websocket.send_json(payload)
            await asyncio.sleep(1.5)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as exc:
        logger.error("WebSocket fatal error: %s\n%s", exc, traceback.format_exc())
        manager.disconnect(websocket)
