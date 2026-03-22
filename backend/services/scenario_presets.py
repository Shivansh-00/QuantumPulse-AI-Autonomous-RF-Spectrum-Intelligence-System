"""Real-World Scenario Presets for RF simulation.

Each preset adjusts simulation parameters to mimic a specific
real-world RF environment (urban, satellite, defense, IoT, etc.).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ScenarioPreset:
    """Describes a real-world RF scenario."""
    id: str
    name: str
    description: str
    num_signals: int
    noise_level: float
    sample_rate: int
    duration: float
    # Extra behavioural hints
    frequency_range: tuple[float, float]   # Hz bounds for signal generation
    modulations: list[str]
    congestion_factor: float               # 0.0 – 1.0  (drives signal density)
    interference_intensity: float          # multiplier on noise


PRESETS: Dict[str, ScenarioPreset] = {
    "urban": ScenarioPreset(
        id="urban",
        name="Urban Network",
        description="Dense urban cellular environment with heavy congestion, "
                    "many overlapping signals, and strong multipath interference.",
        num_signals=12,
        noise_level=0.25,
        sample_rate=10000,
        duration=0.5,
        frequency_range=(500, 3500),
        modulations=["AM", "FM", "QPSK", "BPSK"],
        congestion_factor=0.8,
        interference_intensity=1.5,
    ),
    "satellite": ScenarioPreset(
        id="satellite",
        name="Satellite System",
        description="Satellite communication link with low signal count, "
                    "high sample rate, and minimal interference but low SNR.",
        num_signals=4,
        noise_level=0.08,
        sample_rate=20000,
        duration=1.0,
        frequency_range=(1000, 8000),
        modulations=["BPSK", "QPSK"],
        congestion_factor=0.2,
        interference_intensity=0.5,
    ),
    "defense": ScenarioPreset(
        id="defense",
        name="Defense Communication",
        description="Military-grade spectrum with frequency-hopping signals, "
                    "electronic warfare interference, and high priority traffic.",
        num_signals=8,
        noise_level=0.35,
        sample_rate=20000,
        duration=0.5,
        frequency_range=(200, 7000),
        modulations=["BPSK", "QPSK", "CW"],
        congestion_factor=0.6,
        interference_intensity=2.0,
    ),
    "iot": ScenarioPreset(
        id="iot",
        name="IoT Dense Environment",
        description="Massive IoT deployment with many low-power narrowband "
                    "devices competing for limited spectrum resources.",
        num_signals=18,
        noise_level=0.12,
        sample_rate=10000,
        duration=0.5,
        frequency_range=(400, 2500),
        modulations=["AM", "CW", "BPSK"],
        congestion_factor=0.9,
        interference_intensity=1.0,
    ),
}


def list_scenarios() -> List[Dict]:
    """Return all available scenario presets as dicts."""
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "num_signals": p.num_signals,
            "noise_level": p.noise_level,
            "congestion_factor": p.congestion_factor,
        }
        for p in PRESETS.values()
    ]


def get_scenario(scenario_id: str) -> ScenarioPreset | None:
    """Retrieve a specific scenario preset by ID."""
    return PRESETS.get(scenario_id)
