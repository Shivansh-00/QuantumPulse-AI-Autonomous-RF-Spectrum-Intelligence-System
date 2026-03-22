"""Autonomous Reconfiguration Engine.

Combines AI prediction, spectral analysis, and quantum-inspired
optimisation into a closed-loop controller that continuously monitors
the RF environment and autonomously reallocates frequency resources
when congestion or interference thresholds are exceeded.
"""
from __future__ import annotations

import time
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional

from .ai_prediction import CongestionPredictor
from .optimization_engine import optimize_from_simulation


# ══════════════════════════════════════════════════════════════════
#  Data Structures
# ══════════════════════════════════════════════════════════════════

@dataclass
class ReconfigAction:
    """Describes a single reconfiguration action taken by the engine."""
    timestamp: float
    action_type: str          # "reallocate" | "power_adjust" | "alert"
    signal_id: int
    old_frequency: float
    new_frequency: float
    old_power: float
    new_power: float
    reason: str


@dataclass
class AutonomousState:
    """Snapshot of the autonomous engine's internal state."""
    cycle: int = 0
    congestion_level: float = 0.0
    risk_level: str = "LOW"
    anomaly_score: float = 0.0
    interference_total: float = 0.0
    signal_clarity: float = 1.0
    last_action_time: float = 0.0
    pending_actions: List[ReconfigAction] = field(default_factory=list)
    history: List[Dict] = field(default_factory=list)
    mode: str = "monitor"     # "monitor" | "optimise" | "emergency"


# ══════════════════════════════════════════════════════════════════
#  Autonomous Reconfiguration Engine
# ══════════════════════════════════════════════════════════════════

class AutonomousEngine:
    """Closed-loop autonomous spectrum manager.

    Decision flow per cycle:
      1. Predict future congestion with the AI predictor.
      2. Evaluate thresholds (congestion, anomaly, interference).
      3. If thresholds are exceeded → run quantum-inspired optimiser
         and generate reconfiguration actions.
      4. Log actions into the history for the dashboard.
    """

    # Thresholds
    CONGESTION_WARN = 0.40
    CONGESTION_CRIT = 0.70
    ANOMALY_THRESHOLD = 0.50
    MIN_RECONFIG_INTERVAL = 3.0   # seconds between reconfigurations

    def __init__(self, predictor: Optional[CongestionPredictor] = None):
        self.predictor = predictor or CongestionPredictor(model_type="lstm")
        self.state = AutonomousState()

    # ── Public API ────────────────────────────────────────────

    def evaluate(
        self,
        signal_data: List[float],
        signal_configs: List[Dict],
        analysis: Optional[Dict] = None,
        rlc_resonant: Optional[float] = None,
        rlc_bandwidth: Optional[float] = None,
    ) -> Dict:
        """Run one autonomous evaluation cycle.

        Parameters
        ----------
        signal_data : raw time-domain samples for AI prediction
        signal_configs : per-signal dicts (frequency, bandwidth, priority, …)
        analysis : output from signal_processing.full_analysis() (optional)
        rlc_resonant / rlc_bandwidth : RLC passband params for the optimizer
        """
        self.state.cycle += 1
        now = time.time()

        # ── 1. Predict ───────────────────────────────────────
        prediction = self.predictor.predict(signal_data)
        self.state.congestion_level = prediction["mean_congestion"]
        self.state.risk_level = prediction["risk_level"]
        self.state.anomaly_score = prediction.get("anomaly_score", 0.0)

        # ── 2. Decide mode ───────────────────────────────────
        if self.state.congestion_level >= self.CONGESTION_CRIT or self.state.anomaly_score >= self.ANOMALY_THRESHOLD:
            self.state.mode = "emergency"
        elif self.state.congestion_level >= self.CONGESTION_WARN:
            self.state.mode = "optimise"
        else:
            self.state.mode = "monitor"

        actions: List[ReconfigAction] = []

        # ── 3. Optimise if needed ────────────────────────────
        should_reconfig = (
            self.state.mode in ("optimise", "emergency")
            and (now - self.state.last_action_time) >= self.MIN_RECONFIG_INTERVAL
            and len(signal_configs) > 0
        )

        optimization_result = None
        if should_reconfig:
            optimization_result = optimize_from_simulation(
                signal_configs,
                rlc_resonant=rlc_resonant,
                rlc_bandwidth=rlc_bandwidth,
            )
            self.state.interference_total = optimization_result["total_interference"]
            self.state.signal_clarity = optimization_result["signal_clarity"]

            # Build per-signal actions
            for orig, opt in zip(
                optimization_result.get("original_allocations", []),
                optimization_result.get("optimized_allocations", []),
            ):
                freq_delta = abs(opt["frequency"] - orig["frequency"])
                if freq_delta > 1.0:  # only log meaningful changes
                    actions.append(ReconfigAction(
                        timestamp=now,
                        action_type="reallocate",
                        signal_id=orig["signal_id"],
                        old_frequency=orig["frequency"],
                        new_frequency=opt["frequency"],
                        old_power=1.0,
                        new_power=opt.get("power", 1.0),
                        reason=f"{'EMERGENCY' if self.state.mode == 'emergency' else 'OPTIMISE'}: "
                               f"congestion={self.state.congestion_level:.2f}, "
                               f"anomaly={self.state.anomaly_score:.3f}",
                    ))

            if actions:
                self.state.last_action_time = now

        self.state.pending_actions = actions

        # ── 4. Record history ────────────────────────────────
        entry = {
            "cycle": self.state.cycle,
            "timestamp": now,
            "mode": self.state.mode,
            "congestion": round(self.state.congestion_level, 4),
            "risk": self.state.risk_level,
            "anomaly": round(self.state.anomaly_score, 4),
            "actions_count": len(actions),
        }
        self.state.history.append(entry)
        if len(self.state.history) > 200:
            self.state.history = self.state.history[-200:]

        # ── Build response ───────────────────────────────────
        return {
            "cycle": self.state.cycle,
            "mode": self.state.mode,
            "prediction": prediction,
            "actions": [
                {
                    "action_type": a.action_type,
                    "signal_id": a.signal_id,
                    "old_frequency": round(a.old_frequency, 2),
                    "new_frequency": round(a.new_frequency, 2),
                    "old_power": round(a.old_power, 4),
                    "new_power": round(a.new_power, 4),
                    "reason": a.reason,
                }
                for a in actions
            ],
            "optimization": optimization_result,
            "state": {
                "congestion": round(self.state.congestion_level, 4),
                "risk": self.state.risk_level,
                "anomaly": round(self.state.anomaly_score, 4),
                "interference": round(self.state.interference_total, 4),
                "clarity": round(self.state.signal_clarity, 4),
                "mode": self.state.mode,
            },
            "history": self.state.history[-20:],
        }

    def get_status(self) -> Dict:
        """Return the current engine state without running a cycle."""
        return {
            "cycle": self.state.cycle,
            "mode": self.state.mode,
            "congestion": round(self.state.congestion_level, 4),
            "risk": self.state.risk_level,
            "anomaly": round(self.state.anomaly_score, 4),
            "interference": round(self.state.interference_total, 4),
            "clarity": round(self.state.signal_clarity, 4),
            "history_length": len(self.state.history),
            "history": self.state.history[-20:],
        }
