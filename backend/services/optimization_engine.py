"""Quantum-Inspired Optimization Engine.

Multi-objective simulated-quantum-annealing optimizer for RF frequency
allocation, interference minimization, and power management.  Integrates
RLC circuit and channel-model awareness into the cost function so the
optimizer accounts for physical propagation constraints.
"""
from __future__ import annotations

import math
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from copy import deepcopy


# ══════════════════════════════════════════════════════════════════
#  Data Structures
# ══════════════════════════════════════════════════════════════════

@dataclass
class FrequencyBand:
    """Represents a frequency band with its properties."""
    center_freq: float
    bandwidth: float
    current_power: float
    max_capacity: float = 1.0
    noise_floor_db: float = -100.0


@dataclass
class SignalAllocation:
    """A signal assigned to a frequency band."""
    signal_id: int
    frequency: float
    bandwidth: float
    priority: int = 1
    power: float = 1.0          # transmit power (linear)
    modulation: str = "AM"


@dataclass
class OptimizationResult:
    """Result of frequency optimization with multi-objective metrics."""
    allocations: List[Dict]
    total_interference: float
    signal_clarity: float
    improvement_pct: float
    iterations: int
    power_efficiency: float = 0.0
    spectral_efficiency: float = 0.0
    pareto_rank: int = 1
    temperature_history: List[float] = field(default_factory=list)
    cost_history: List[float] = field(default_factory=list)
    objective_breakdown: Dict = field(default_factory=dict)


# ══════════════════════════════════════════════════════════════════
#  Multi-Objective Cost Function
# ══════════════════════════════════════════════════════════════════

class MultiObjectiveCost:
    """Weighted multi-objective cost combining interference, clarity,
    spectral efficiency, power efficiency, and physical constraints."""

    def __init__(
        self,
        w_interference: float = 1.0,
        w_clarity: float = 10.0,
        w_power: float = 0.5,
        w_spectral: float = 2.0,
        w_range: float = 0.1,
        freq_range: Tuple[float, float] = (100.0, 5000.0),
        rlc_resonant: Optional[float] = None,
        rlc_bandwidth: Optional[float] = None,
    ):
        self.w_interference = w_interference
        self.w_clarity = w_clarity
        self.w_power = w_power
        self.w_spectral = w_spectral
        self.w_range = w_range
        self.freq_range = freq_range
        self.rlc_resonant = rlc_resonant
        self.rlc_bandwidth = rlc_bandwidth

    def interference(self, allocs: List[SignalAllocation]) -> float:
        total = 0.0
        n = len(allocs)
        for i in range(n):
            for j in range(i + 1, n):
                freq_diff = abs(allocs[i].frequency - allocs[j].frequency)
                overlap = (allocs[i].bandwidth + allocs[j].bandwidth) / 2.0 - freq_diff
                if overlap > 0:
                    prio_factor = 1.0 + 0.1 * (allocs[i].priority + allocs[j].priority)
                    total += overlap / prio_factor
        return total

    def clarity(self, allocs: List[SignalAllocation]) -> float:
        if len(allocs) < 2:
            return 1.0
        min_sep = float("inf")
        for i in range(len(allocs)):
            for j in range(i + 1, len(allocs)):
                sep = abs(allocs[i].frequency - allocs[j].frequency)
                req = (allocs[i].bandwidth + allocs[j].bandwidth) / 2.0
                min_sep = min(min_sep, sep / req if req > 0 else sep)
        if min_sep == float("inf"):
            return 1.0
        return 1.0 / (1.0 + math.exp(-2.0 * (min_sep - 1.0)))

    def power_efficiency(self, allocs: List[SignalAllocation]) -> float:
        """Lower total power is better — returns penalty."""
        if not allocs:
            return 0.0
        return sum(a.power for a in allocs) / len(allocs)

    def spectral_efficiency(self, allocs: List[SignalAllocation]) -> float:
        """Fraction of the available spectrum utilised (higher is better)."""
        if not allocs:
            return 0.0
        total_bw = sum(a.bandwidth for a in allocs)
        available = self.freq_range[1] - self.freq_range[0]
        return min(total_bw / available, 1.0) if available > 0 else 0.0

    def rlc_penalty(self, allocs: List[SignalAllocation]) -> float:
        """Penalise allocations far from RLC passband centre."""
        if self.rlc_resonant is None:
            return 0.0
        half_bw = (self.rlc_bandwidth or 500.0) / 2.0
        penalty = 0.0
        for a in allocs:
            dist = abs(a.frequency - self.rlc_resonant)
            if dist > half_bw:
                penalty += (dist - half_bw) / half_bw
        return penalty

    def range_penalty(self, allocs: List[SignalAllocation]) -> float:
        return sum(
            max(0.0, self.freq_range[0] - a.frequency) +
            max(0.0, a.frequency - self.freq_range[1])
            for a in allocs
        )

    def __call__(self, allocs: List[SignalAllocation]) -> float:
        interf = self.interference(allocs)
        clar = self.clarity(allocs)
        pwr = self.power_efficiency(allocs)
        spec = self.spectral_efficiency(allocs)
        rlc = self.rlc_penalty(allocs)
        rng = self.range_penalty(allocs)

        cost = (
            self.w_interference * interf
            - self.w_clarity * clar
            + self.w_power * pwr
            - self.w_spectral * spec
            + self.w_range * rng
            + 0.5 * rlc
        )
        return cost

    def breakdown(self, allocs: List[SignalAllocation]) -> Dict:
        return {
            "interference": round(self.interference(allocs), 4),
            "clarity": round(self.clarity(allocs), 4),
            "power_efficiency": round(self.power_efficiency(allocs), 4),
            "spectral_efficiency": round(self.spectral_efficiency(allocs), 4),
            "rlc_penalty": round(self.rlc_penalty(allocs), 4),
        }


# ══════════════════════════════════════════════════════════════════
#  Quantum-Inspired Optimizer
# ══════════════════════════════════════════════════════════════════

class QuantumInspiredOptimizer:
    """Simulated quantum annealing with tunnelling, superposition
    initialisation, and entanglement-inspired crossover.

    The optimizer also supports adaptive tunnelling probability that
    increases as the temperature drops, allowing the search to escape
    local minima more aggressively in the late-cooling phase.
    """

    def __init__(
        self,
        num_bands: int = 10,
        freq_range: Tuple[float, float] = (100.0, 5000.0),
        initial_temp: float = 100.0,
        cooling_rate: float = 0.995,
        min_temp: float = 0.01,
        max_iterations: int = 5000,
        quantum_tunneling_prob: float = 0.1,
        population_size: int = 5,
        rlc_resonant: Optional[float] = None,
        rlc_bandwidth: Optional[float] = None,
    ):
        self.num_bands = num_bands
        self.freq_range = freq_range
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.min_temp = min_temp
        self.max_iterations = max_iterations
        self.quantum_tunneling_prob = quantum_tunneling_prob
        self.population_size = population_size
        self.rng = np.random.default_rng()

        self.cost_fn = MultiObjectiveCost(
            freq_range=freq_range,
            rlc_resonant=rlc_resonant,
            rlc_bandwidth=rlc_bandwidth,
        )

    # ── Neighbour generators ──────────────────────────────────

    def _quantum_neighbor(
        self, allocations: List[SignalAllocation], temperature: float
    ) -> List[SignalAllocation]:
        new_allocs = deepcopy(allocations)
        if not new_allocs:
            return new_allocs

        # Adaptive tunnelling: higher probability at lower temperatures
        adaptive_tunnel = self.quantum_tunneling_prob * (1.0 + 2.0 * (1.0 - temperature / self.initial_temp))
        adaptive_tunnel = min(adaptive_tunnel, 0.5)

        if self.rng.random() < adaptive_tunnel:
            # Quantum tunnelling: large jump
            idx = self.rng.integers(0, len(new_allocs))
            new_allocs[idx].frequency = float(
                self.rng.uniform(self.freq_range[0], self.freq_range[1])
            )
            # Occasionally also adjust power
            if self.rng.random() < 0.3:
                new_allocs[idx].power = float(self.rng.uniform(0.1, 2.0))
        else:
            # Classical small perturbation
            idx = self.rng.integers(0, len(new_allocs))
            width = self.freq_range[1] - self.freq_range[0]
            perturbation = self.rng.normal(0, width * 0.05)
            new_freq = new_allocs[idx].frequency + perturbation
            new_allocs[idx].frequency = float(
                np.clip(new_freq, self.freq_range[0], self.freq_range[1])
            )

        return new_allocs

    def _entanglement_crossover(
        self, state_a: List[SignalAllocation], state_b: List[SignalAllocation]
    ) -> List[SignalAllocation]:
        """Combine two states by mixing frequency assignments."""
        child = deepcopy(state_a)
        for i in range(len(child)):
            if i < len(state_b) and self.rng.random() < 0.5:
                child[i].frequency = state_b[i].frequency
                child[i].power = state_b[i].power
        return child

    def _superposition_init(
        self, signals: List[SignalAllocation], num_states: int = 10
    ) -> List[SignalAllocation]:
        best_state = None
        best_cost = float("inf")
        for _ in range(num_states):
            candidate = deepcopy(signals)
            for alloc in candidate:
                alloc.frequency = float(
                    self.rng.uniform(self.freq_range[0], self.freq_range[1])
                )
            cost = self.cost_fn(candidate)
            if cost < best_cost:
                best_cost = cost
                best_state = candidate
        return best_state or signals

    # ── Main optimisation loop ────────────────────────────────

    def optimize(
        self,
        signals: List[SignalAllocation],
        band_occupancy: Optional[List[Dict]] = None,
    ) -> OptimizationResult:
        """Run multi-population quantum-inspired simulated annealing."""
        initial_interference = self.cost_fn.interference(signals)

        # Initialise a small population with superposition
        population = [
            self._superposition_init(signals)
            for _ in range(self.population_size)
        ]
        pop_costs = [self.cost_fn(p) for p in population]

        best_idx = int(np.argmin(pop_costs))
        best = deepcopy(population[best_idx])
        best_cost = pop_costs[best_idx]

        temperature = self.initial_temp
        temp_history: List[float] = []
        cost_history: List[float] = []

        iterations = 0
        for i in range(self.max_iterations):
            if temperature < self.min_temp:
                break

            for p_idx in range(self.population_size):
                current = population[p_idx]
                current_cost = pop_costs[p_idx]

                neighbor = self._quantum_neighbor(current, temperature)

                # Entanglement crossover with a random other member
                if self.population_size > 1 and self.rng.random() < 0.15:
                    other_idx = self.rng.integers(0, self.population_size)
                    if other_idx != p_idx:
                        neighbor = self._entanglement_crossover(neighbor, population[other_idx])

                neighbor_cost = self.cost_fn(neighbor)

                delta = neighbor_cost - current_cost
                if delta < 0 or self.rng.random() < math.exp(-delta / max(temperature, 1e-10)):
                    population[p_idx] = neighbor
                    pop_costs[p_idx] = neighbor_cost

                    if neighbor_cost < best_cost:
                        best = deepcopy(neighbor)
                        best_cost = neighbor_cost

            temperature *= self.cooling_rate
            temp_history.append(temperature)
            cost_history.append(best_cost)
            iterations = i + 1

        # Final metrics
        final_interference = self.cost_fn.interference(best)
        final_clarity = self.cost_fn.clarity(best)
        final_spec_eff = self.cost_fn.spectral_efficiency(best)
        final_pwr_eff = self.cost_fn.power_efficiency(best)

        improvement = (
            (initial_interference - final_interference) / initial_interference * 100
            if initial_interference > 0 else 0.0
        )

        # Down-sample histories for JSON transport
        step = max(1, len(temp_history) // 100)

        return OptimizationResult(
            allocations=[
                {
                    "signal_id": a.signal_id,
                    "frequency": round(a.frequency, 2),
                    "bandwidth": a.bandwidth,
                    "priority": a.priority,
                    "power": round(a.power, 4),
                    "modulation": a.modulation,
                }
                for a in best
            ],
            total_interference=float(final_interference),
            signal_clarity=float(final_clarity),
            improvement_pct=float(improvement),
            iterations=iterations,
            power_efficiency=round(final_pwr_eff, 4),
            spectral_efficiency=round(final_spec_eff, 4),
            temperature_history=temp_history[::step],
            cost_history=cost_history[::step],
            objective_breakdown=self.cost_fn.breakdown(best),
        )


# ══════════════════════════════════════════════════════════════════
#  Convenience wrapper
# ══════════════════════════════════════════════════════════════════

def optimize_from_simulation(
    signal_configs: List[Dict],
    band_occupancy: Optional[List[Dict]] = None,
    rlc_resonant: Optional[float] = None,
    rlc_bandwidth: Optional[float] = None,
) -> dict:
    """Optimise frequency allocation from simulation output, with
    optional RLC passband awareness."""
    signals = []
    for i, cfg in enumerate(signal_configs):
        signals.append(
            SignalAllocation(
                signal_id=i,
                frequency=cfg.get("frequency", 1000.0),
                bandwidth=cfg.get("bandwidth", 100.0),
                priority=cfg.get("priority", 1),
                power=cfg.get("power", 1.0),
                modulation=cfg.get("modulation", "AM"),
            )
        )

    optimizer = QuantumInspiredOptimizer(
        rlc_resonant=rlc_resonant,
        rlc_bandwidth=rlc_bandwidth,
    )
    result = optimizer.optimize(signals, band_occupancy)

    return {
        "original_allocations": [
            {
                "signal_id": i,
                "frequency": cfg.get("frequency", 1000.0),
                "bandwidth": cfg.get("bandwidth", 100.0),
            }
            for i, cfg in enumerate(signal_configs)
        ],
        "optimized_allocations": result.allocations,
        "total_interference": result.total_interference,
        "signal_clarity": result.signal_clarity,
        "improvement_pct": result.improvement_pct,
        "iterations": result.iterations,
        "power_efficiency": result.power_efficiency,
        "spectral_efficiency": result.spectral_efficiency,
        "objective_breakdown": result.objective_breakdown,
        "temperature_history": result.temperature_history,
        "cost_history": result.cost_history,
    }
