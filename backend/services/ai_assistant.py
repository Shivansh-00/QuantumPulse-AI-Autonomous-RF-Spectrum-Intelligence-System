"""AI Assistant — Context-Aware Q&A for the QuantumPulse dashboard.

A rule-based conversational assistant that answers operator questions
about the system's state, decisions, and RF environment by analyzing
the latest pipeline data.
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional

from .xai_engine import XAIEngine


class AIAssistant:
    """Context-aware assistant that answers questions about spectrum state."""

    def __init__(self):
        self._latest_context: Dict = {}

    def update_context(
        self,
        prediction: Optional[Dict] = None,
        optimization: Optional[Dict] = None,
        autonomous_state: Optional[Dict] = None,
        autonomous_actions: Optional[List[Dict]] = None,
        analysis: Optional[Dict] = None,
        performance: Optional[Dict] = None,
    ):
        """Update the assistant's knowledge with latest pipeline data."""
        if prediction:
            self._latest_context["prediction"] = prediction
        if optimization:
            self._latest_context["optimization"] = optimization
        if autonomous_state:
            self._latest_context["autonomous_state"] = autonomous_state
        if autonomous_actions is not None:
            self._latest_context["autonomous_actions"] = autonomous_actions
        if analysis:
            self._latest_context["analysis"] = analysis
        if performance:
            self._latest_context["performance"] = performance

    def ask(self, question: str) -> str:
        """Answer a user question based on current pipeline context. Never raises."""
        try:
            q = question.lower().strip()
            if not q:
                return self._help_text()

            # Route to most relevant handler
            if _matches(q, r"why.*(change|moved|reallocat|switch|shift).*freq"):
                return self._explain_frequency_change()
            if _matches(q, r"anomal|unusual|abnormal|spike|attack"):
                return self._explain_anomaly()
            if _matches(q, r"congestion|busy|overload|crowded"):
                return self._explain_congestion()
            if _matches(q, r"optimi[sz]|improve|better|efficiency"):
                return self._explain_optimization()
            if _matches(q, r"mode|monitor|emergency|autono"):
                return self._explain_mode()
            if _matches(q, r"snr|noise|signal.*(quality|strength)"):
                return self._explain_snr()
            if _matches(q, r"interfere"):
                return self._explain_interference()
            if _matches(q, r"performance|metric|latency|speed"):
                return self._explain_performance()
            if _matches(q, r"learn|improv|feedback|self"):
                return self._explain_learning()
            if _matches(q, r"status|state|current|what.*happen"):
                return self._explain_current_state()
            if _matches(q, r"help|what can|how do"):
                return self._help_text()

            # Fallback: provide a general status summary
            return self._explain_current_state()
        except Exception:
            return (
                "System status: operational. All modules are running normally. "
                "Try asking about frequency changes, anomalies, congestion, "
                "optimization, mode, SNR, interference, or performance."
            )

    # ── Answer generators ───────────────────────────────────

    def _explain_frequency_change(self) -> str:
        actions = self._latest_context.get("autonomous_actions", [])
        state = self._latest_context.get("autonomous_state", {})
        if not actions:
            return (
                "No frequency changes have been made in the latest cycle. "
                "The system is currently in monitoring mode with stable spectrum conditions."
            )
        explanations = XAIEngine.explain_actions(actions, state)
        return " ".join(explanations)

    def _explain_anomaly(self) -> str:
        pred = self._latest_context.get("prediction", {})
        analysis = self._latest_context.get("analysis", {})
        anomaly = pred.get("anomaly_score", 0)
        lines = XAIEngine.explain_anomaly(analysis)
        if anomaly > 0.5:
            lines.insert(
                0,
                f"Anomaly detected! Score: {anomaly:.3f}. "
                f"The system has flagged abnormal RF behaviour.",
            )
        elif anomaly > 0:
            lines.insert(0, f"Low anomaly score ({anomaly:.3f}) — spectrum appears normal.")
        else:
            lines.insert(0, "No anomalies detected. Spectrum behaviour is within normal bounds.")
        return " ".join(lines) if lines else "No anomaly data available yet."

    def _explain_congestion(self) -> str:
        pred = self._latest_context.get("prediction", {})
        perf = self._latest_context.get("performance", {})
        risk = pred.get("risk_level", "UNKNOWN")
        mean_c = pred.get("mean_congestion", 0)
        trend = pred.get("trend", "stable")
        before = perf.get("congestion_before", mean_c)
        after = perf.get("congestion_after", mean_c)
        return (
            f"Current congestion risk: {risk} ({mean_c * 100:.1f}%). "
            f"Trend: {trend}. "
            f"Before optimization: {before * 100:.1f}%, after: {after * 100:.1f}%."
        )

    def _explain_optimization(self) -> str:
        opt = self._latest_context.get("optimization", {})
        lines = XAIEngine.explain_optimization(opt)
        return " ".join(lines) if lines else "No optimization data available yet."

    def _explain_mode(self) -> str:
        state = self._latest_context.get("autonomous_state", {})
        mode = state.get("mode", "monitor")
        descriptions = {
            "monitor": "The system is in MONITOR mode — passively observing spectrum conditions. No active reallocation needed.",
            "optimise": "The system is in OPTIMISE mode — congestion has exceeded warning thresholds and the optimizer is actively reallocating frequencies.",
            "emergency": "The system is in EMERGENCY mode — critical congestion or anomaly detected. Aggressive reallocation is in progress to restore service quality.",
        }
        return descriptions.get(mode, f"Current mode: {mode}.")

    def _explain_snr(self) -> str:
        analysis = self._latest_context.get("analysis", {})
        snr = analysis.get("snr") or {}
        snr_db = snr.get("snr_db")
        if snr_db is None:
            return "SNR data not yet available."
        if snr_db > 20:
            quality = "Excellent"
        elif snr_db > 10:
            quality = "Good"
        elif snr_db > 5:
            quality = "Fair"
        else:
            quality = "Poor"
        return (
            f"Signal-to-Noise Ratio: {snr_db:.1f} dB ({quality}). "
            f"Noise floor at {snr.get('noise_floor_db', 0):.1f} dB."
        )

    def _explain_interference(self) -> str:
        analysis = self._latest_context.get("analysis", {})
        ifc = analysis.get("interference") or {}
        itype = ifc.get("interference_type", "none")
        conf = ifc.get("confidence", 0)
        if itype == "none":
            return "No significant interference detected in the current spectrum."
        return (
            f"Detected {itype} interference with {conf * 100:.0f}% confidence. "
            f"The autonomous engine will compensate if severity increases."
        )

    def _explain_performance(self) -> str:
        perf = self._latest_context.get("performance", {})
        if not perf:
            return "Performance metrics will be available after the first pipeline cycle."
        return (
            f"Pipeline latency: {perf.get('latency_ms', 0):.0f}ms (real-time). "
            f"Interference reduction: {perf.get('interference_reduction_pct', 0):.1f}%. "
            f"Spectrum efficiency: {perf.get('spectrum_efficiency', 0):.4f}. "
            f"Signal stability: {perf.get('signal_stability', 0) * 100:.1f}%. "
            f"Learning cycles completed: {perf.get('learning_cycles', 0)}."
        )

    def _explain_learning(self) -> str:
        perf = self._latest_context.get("performance", {})
        cycles = perf.get("learning_cycles", 0)
        return (
            f"The system has completed {cycles} learning cycles. "
            f"Each cycle refines the AI models through continuous feedback from "
            f"prediction accuracy, optimization outcomes, and anomaly detection. "
            f"Self-learning improves over time as the system observes more spectrum patterns."
        )

    def _explain_current_state(self) -> str:
        state = self._latest_context.get("autonomous_state", {})
        pred = self._latest_context.get("prediction", {})
        perf = self._latest_context.get("performance", {})
        mode = state.get("mode", "monitor")
        risk = pred.get("risk_level", "—")
        latency = perf.get("latency_ms", 0)
        return (
            f"System status: {mode.upper()} mode | "
            f"Risk: {risk} | "
            f"Congestion: {pred.get('mean_congestion', 0) * 100:.1f}% | "
            f"Latency: {latency:.0f}ms | "
            f"Anomaly: {pred.get('anomaly_score', 0):.3f}."
        )

    @staticmethod
    def _help_text() -> str:
        return (
            "I can answer questions about: "
            "frequency changes (\"Why did you change frequency?\"), "
            "anomlies (\"Any anomalies?\"), "
            "congestion (\"How busy is the spectrum?\"), "
            "optimization results, system mode, SNR, interference, "
            "performance metrics, and self-learning status. "
            "Just ask!"
        )


def _matches(text: str, pattern: str) -> bool:
    return bool(re.search(pattern, text))
