"""Performance Metrics Calculator.

Computes key before/after performance metrics that demonstrate
the system's effectiveness:
  - Interference Reduction %
  - Latency Improvement (simulated processing latency)
  - Spectrum Efficiency Gain
  - Signal Stability Score
"""
from __future__ import annotations

import time
import numpy as np
from typing import Dict, Optional


class PerformanceTracker:
    """Tracks and computes performance metrics across pipeline cycles."""

    def __init__(self):
        self._history: list[Dict] = []
        self._cycle = 0
        self._learning_cycles = 0

    def compute(
        self,
        sim_result: Dict,
        analysis: Dict,
        prediction: Dict,
        optimization: Dict,
        autonomous_state: Dict,
        pipeline_latency_ms: float,
    ) -> Dict:
        """Compute performance metrics for the current cycle."""
        self._cycle += 1
        self._learning_cycles += 1

        # ── Interference Reduction ──────────────────────────
        orig_allocs = optimization.get("original_allocations", [])
        opt_allocs = optimization.get("optimized_allocations", [])
        improvement_pct = optimization.get("improvement_pct", 0.0)

        # ── Spectrum Efficiency ─────────────────────────────
        spectral_eff = optimization.get("spectral_efficiency", 0.0) or 0.0
        power_eff = optimization.get("power_efficiency", 0.0) or 0.0

        # ── Signal Stability Score ──────────────────────────
        # Based on SNR, entropy, and interference classification
        snr_info = analysis.get("snr") or {}
        snr_db = snr_info.get("snr_db", 10.0)
        entropy = analysis.get("spectral_entropy")
        if isinstance(entropy, dict):
            entropy_val = entropy.get("normalized_entropy", 0.5)
        else:
            entropy_val = entropy if entropy is not None else 0.5

        ifc = analysis.get("interference") or {}
        ifc_conf = ifc.get("confidence", 0.0)
        ifc_type = ifc.get("interference_type", "none")

        # Higher SNR = more stable, lower entropy = more stable, no interference = stable
        snr_score = min(snr_db / 30.0, 1.0)   # normalize to 0-1
        entropy_score = 1.0 - entropy_val       # lower entropy = higher stability
        ifc_score = 1.0 if ifc_type == "none" else max(0, 1.0 - ifc_conf)
        stability = round((snr_score * 0.4 + entropy_score * 0.3 + ifc_score * 0.3), 4)

        # ── Congestion Before / After ───────────────────────
        congestion_before = prediction.get("mean_congestion", 0.5)
        # After optimization congestion is reduced proportionally
        congestion_after = congestion_before * max(0, 1.0 - improvement_pct / 100.0)

        # ── Build metrics dict ──────────────────────────────
        metrics = {
            "interference_reduction_pct": round(improvement_pct, 2),
            "latency_ms": round(pipeline_latency_ms, 1),
            "spectrum_efficiency": round(spectral_eff, 4),
            "power_efficiency": round(power_eff, 4),
            "signal_stability": round(stability, 4),
            "snr_db": round(snr_db, 2),
            "congestion_before": round(congestion_before, 4),
            "congestion_after": round(congestion_after, 4),
            "total_signals": sim_result.get("num_signals", 0),
            "cycle": self._cycle,
            "learning_cycles": self._learning_cycles,
        }

        self._history.append(metrics)
        if len(self._history) > 200:
            self._history = self._history[-200:]

        return metrics

    @property
    def history(self) -> list[Dict]:
        return self._history[-50:]

    @property
    def learning_cycles(self) -> int:
        return self._learning_cycles
