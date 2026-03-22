"""RF Spectrum Simulation Engine.

Generates realistic multi-signal RF spectrum environments with
RLC circuit modeling, multipath fading, Doppler effects, and
configurable propagation parameters for AI-based spectrum analysis.
"""
from __future__ import annotations

import math
import numpy as np
from dataclasses import dataclass, field
from typing import List, Literal, Optional


# ══════════════════════════════════════════════════════════════════
#  RLC Circuit Model
# ══════════════════════════════════════════════════════════════════

@dataclass
class RLCConfig:
    """Parameters for a series RLC bandpass circuit."""
    resistance: float = 50.0      # Ohms
    inductance: float = 1e-3      # Henrys
    capacitance: float = 1e-6     # Farads

    @property
    def resonant_frequency(self) -> float:
        """Natural resonant frequency f0 = 1/(2*pi*sqrt(LC))."""
        return 1.0 / (2.0 * math.pi * math.sqrt(self.inductance * self.capacitance))

    @property
    def quality_factor(self) -> float:
        """Q = (1/R)*sqrt(L/C)  —  higher Q means sharper tuning."""
        return (1.0 / self.resistance) * math.sqrt(self.inductance / self.capacitance)

    @property
    def bandwidth_3db(self) -> float:
        """3-dB bandwidth = f0 / Q."""
        q = self.quality_factor
        return self.resonant_frequency / q if q > 0 else float("inf")

    def impedance(self, freq: float) -> complex:
        """Complex impedance Z(f) = R + j(wL - 1/wC)."""
        omega = 2.0 * math.pi * freq
        if omega == 0:
            return complex(self.resistance, -1e12)
        z_l = omega * self.inductance
        z_c = 1.0 / (omega * self.capacitance)
        return complex(self.resistance, z_l - z_c)

    def transfer_function(self, freqs: np.ndarray) -> np.ndarray:
        """Magnitude of voltage transfer function |H(f)| for the RLC filter."""
        omega = 2.0 * np.pi * freqs
        omega = np.where(omega == 0, 1e-12, omega)
        z_l = omega * self.inductance
        z_c = 1.0 / (omega * self.capacitance)
        z_total = np.sqrt(self.resistance**2 + (z_l - z_c)**2)
        return self.resistance / z_total


# ══════════════════════════════════════════════════════════════════
#  Channel & Propagation Models
# ══════════════════════════════════════════════════════════════════

@dataclass
class ChannelConfig:
    """Wireless channel propagation parameters."""
    fading_model: str = "rayleigh"        # "none", "rayleigh", "rician"
    rician_k_factor: float = 6.0          # dB
    num_multipath: int = 6
    max_delay_spread: float = 1e-4        # seconds

    doppler_shift_hz: float = 0.0
    doppler_spread_hz: float = 5.0

    path_loss_exponent: float = 3.0
    reference_distance: float = 1.0       # meters
    distance: float = 100.0               # meters


class ChannelModel:
    """Applies realistic wireless channel effects to a signal."""

    def __init__(self, config: ChannelConfig, sample_rate: int, rng: np.random.Generator):
        self.config = config
        self.sample_rate = sample_rate
        self.rng = rng

    def apply_path_loss(self, signal: np.ndarray) -> tuple:
        """Log-distance path loss model."""
        d = max(self.config.distance, self.config.reference_distance)
        pl_db = 10.0 * self.config.path_loss_exponent * math.log10(d / self.config.reference_distance)
        attenuation = 10.0 ** (-pl_db / 20.0)
        return signal * attenuation, pl_db

    def apply_multipath_fading(self, signal: np.ndarray) -> tuple:
        """Apply multipath fading using a tapped-delay-line model."""
        n = len(signal)
        output = np.zeros(n)
        tap_info = []
        max_delay_samples = max(1, int(self.config.max_delay_spread * self.sample_rate))

        for tap in range(self.config.num_multipath):
            delay = self.rng.integers(0, max_delay_samples + 1)

            if self.config.fading_model == "rayleigh":
                h_real = self.rng.standard_normal()
                h_imag = self.rng.standard_normal()
                gain = math.sqrt(h_real**2 + h_imag**2) / math.sqrt(self.config.num_multipath)
                phase = math.atan2(h_imag, h_real)
            elif self.config.fading_model == "rician":
                k_linear = 10.0 ** (self.config.rician_k_factor / 10.0)
                if tap == 0:
                    h_real = math.sqrt(k_linear / (1 + k_linear)) + self.rng.standard_normal() * math.sqrt(0.5 / (1 + k_linear))
                    h_imag = self.rng.standard_normal() * math.sqrt(0.5 / (1 + k_linear))
                else:
                    h_real = self.rng.standard_normal() * math.sqrt(0.5 / (1 + k_linear))
                    h_imag = self.rng.standard_normal() * math.sqrt(0.5 / (1 + k_linear))
                gain = math.sqrt(h_real**2 + h_imag**2) / math.sqrt(self.config.num_multipath)
                phase = math.atan2(h_imag, h_real)
            else:
                gain = 1.0 / self.config.num_multipath if tap == 0 else 0.0
                phase = 0.0

            if delay < n and gain > 1e-6:
                output[delay:] += gain * np.cos(phase) * signal[:n - delay]

            tap_info.append({"delay_samples": int(delay), "gain": float(gain), "phase_rad": float(phase)})

        return output, {"taps": tap_info, "model": self.config.fading_model}

    def apply_doppler(self, signal: np.ndarray, carrier_freq: float) -> np.ndarray:
        """Apply Doppler frequency shift and Jakes-model spread."""
        n = len(signal)
        t = np.arange(n) / self.sample_rate

        if abs(self.config.doppler_shift_hz) > 0.01:
            signal = signal * np.cos(2.0 * np.pi * self.config.doppler_shift_hz * t)

        if self.config.doppler_spread_hz > 0.01:
            num_oscillators = 8
            doppler_gain = np.ones(n)
            for k in range(num_oscillators):
                alpha = 2.0 * math.pi * k / num_oscillators
                fd = self.config.doppler_spread_hz * math.cos(alpha)
                phi = self.rng.uniform(0, 2.0 * math.pi)
                doppler_gain += (1.0 / num_oscillators) * np.cos(2.0 * np.pi * fd * t + phi)
            doppler_gain /= np.max(np.abs(doppler_gain))
            signal = signal * doppler_gain

        return signal

    def apply_all(self, signal: np.ndarray, carrier_freq: float = 1000.0) -> dict:
        """Apply full channel model pipeline and return metrics."""
        result = {"original_power": float(np.mean(signal**2))}

        out, pl_db = self.apply_path_loss(signal)
        result["path_loss_db"] = pl_db

        out, multipath_info = self.apply_multipath_fading(out)
        result["multipath"] = multipath_info

        out = self.apply_doppler(out, carrier_freq)
        result["received_power"] = float(np.mean(out**2))
        result["signal"] = out
        return result


# ══════════════════════════════════════════════════════════════════
#  Signal Configuration & Simulation Engine
# ══════════════════════════════════════════════════════════════════

@dataclass
class SignalConfig:
    """Configuration for a single RF signal component."""
    frequency: float = 1000.0     # Hz
    amplitude: float = 1.0
    phase: float = 0.0            # radians
    bandwidth: float = 100.0      # Hz
    modulation: str = "AM"        # AM, FM, CW, BPSK, QPSK
    priority: int = 1


@dataclass
class SimulationConfig:
    """Full simulation configuration."""
    sample_rate: int = 10000
    duration: float = 1.0
    noise_level: float = 0.1
    signals: List[SignalConfig] = field(default_factory=list)
    interference_prob: float = 0.3
    rlc: Optional[RLCConfig] = None
    channel: Optional[ChannelConfig] = None


class RFSimulator:
    """Core RF spectrum environment simulator with RLC modeling and channel effects."""

    def __init__(self, config: SimulationConfig):
        self.config = config
        self.num_samples = int(config.sample_rate * config.duration)
        self.time = np.linspace(0, config.duration, self.num_samples, endpoint=False)
        self.rng = np.random.default_rng()

    def generate_carrier(self, sig: SignalConfig) -> np.ndarray:
        """Generate a carrier signal with optional modulation."""
        carrier = sig.amplitude * np.sin(2 * np.pi * sig.frequency * self.time + sig.phase)

        if sig.modulation == "AM":
            mod_freq = sig.frequency * 0.01
            envelope = 1.0 + 0.5 * np.sin(2 * np.pi * mod_freq * self.time)
            carrier *= envelope
        elif sig.modulation == "FM":
            mod_index = 5.0
            mod_freq = sig.frequency * 0.005
            phase_deviation = mod_index * np.sin(2 * np.pi * mod_freq * self.time)
            carrier = sig.amplitude * np.sin(
                2 * np.pi * sig.frequency * self.time + phase_deviation + sig.phase
            )
        elif sig.modulation == "BPSK":
            symbol_rate = max(50, sig.bandwidth // 2)
            samples_per_symbol = max(1, int(self.config.sample_rate / symbol_rate))
            num_symbols = self.num_samples // samples_per_symbol + 1
            bits = self.rng.choice([-1, 1], size=num_symbols)
            bpsk_mod = np.repeat(bits, samples_per_symbol)[:self.num_samples]
            carrier = sig.amplitude * bpsk_mod * np.sin(2 * np.pi * sig.frequency * self.time + sig.phase)
        elif sig.modulation == "QPSK":
            symbol_rate = max(50, sig.bandwidth // 2)
            samples_per_symbol = max(1, int(self.config.sample_rate / symbol_rate))
            num_symbols = self.num_samples // samples_per_symbol + 1
            phases = self.rng.choice([np.pi/4, 3*np.pi/4, 5*np.pi/4, 7*np.pi/4], size=num_symbols)
            qpsk_phase = np.repeat(phases, samples_per_symbol)[:self.num_samples]
            carrier = sig.amplitude * np.sin(2 * np.pi * sig.frequency * self.time + qpsk_phase)

        return carrier

    def generate_noise(self) -> np.ndarray:
        """Generate AWGN (Additive White Gaussian Noise)."""
        return self.config.noise_level * self.rng.standard_normal(self.num_samples)

    def generate_interference(self) -> np.ndarray:
        """Generate random interference bursts."""
        interference = np.zeros(self.num_samples)

        if self.rng.random() < self.config.interference_prob:
            num_bursts = self.rng.integers(1, 4)
            for _ in range(num_bursts):
                start = self.rng.integers(0, max(self.num_samples // 2, 1))
                length = self.rng.integers(self.num_samples // 20, max(self.num_samples // 5, self.num_samples // 20 + 1))
                end = min(start + length, self.num_samples)
                burst_freq = self.rng.uniform(100, 2000)
                burst_amp = self.rng.uniform(0.5, 2.0)
                t_burst = self.time[start:end]
                interference[start:end] += burst_amp * np.sin(2 * np.pi * burst_freq * t_burst)

        return interference

    def _apply_rlc_filter(self, signal: np.ndarray) -> tuple:
        """Apply RLC circuit bandpass filter in the frequency domain."""
        rlc = self.config.rlc
        if rlc is None:
            return signal, {}

        from scipy.fft import fft, ifft, fftfreq
        N = len(signal)
        freqs = fftfreq(N, 1.0 / self.config.sample_rate)
        freq_magnitudes = np.abs(freqs)
        freq_magnitudes = np.where(freq_magnitudes == 0, 0.1, freq_magnitudes)

        H = rlc.transfer_function(freq_magnitudes)
        signal_fft = fft(signal)
        filtered_fft = signal_fft * H
        filtered_signal = np.real(ifft(filtered_fft))  # type: ignore[arg-type]

        rlc_metrics = {
            "resonant_frequency": float(rlc.resonant_frequency),
            "quality_factor": float(rlc.quality_factor),
            "bandwidth_3db": float(rlc.bandwidth_3db),
            "impedance_at_resonance": float(abs(rlc.impedance(rlc.resonant_frequency))),
        }
        return filtered_signal, rlc_metrics

    def simulate(self) -> dict:
        """Run the full simulation with RLC filtering and channel effects."""
        composite = np.zeros(self.num_samples)
        for sig in self.config.signals:
            composite += self.generate_carrier(sig)

        noise = self.generate_noise()
        interference = self.generate_interference()
        combined = composite + noise + interference

        # Channel effects
        channel_metrics = {}
        if self.config.channel:
            channel = ChannelModel(self.config.channel, self.config.sample_rate, self.rng)
            dominant_freq = self.config.signals[0].frequency if self.config.signals else 1000.0
            ch_result = channel.apply_all(combined, dominant_freq)
            combined = ch_result.pop("signal")
            channel_metrics = ch_result

        # RLC filtering
        rlc_metrics = {}
        if self.config.rlc:
            combined, rlc_metrics = self._apply_rlc_filter(combined)

        return {
            "time": self.time.tolist(),
            "signal": combined.tolist(),
            "clean_signal": composite.tolist(),
            "noise": noise.tolist(),
            "interference": interference.tolist(),
            "sample_rate": self.config.sample_rate,
            "duration": self.config.duration,
            "num_signals": len(self.config.signals),
            "signal_configs": [
                {
                    "frequency": s.frequency,
                    "amplitude": s.amplitude,
                    "bandwidth": s.bandwidth,
                    "modulation": s.modulation,
                    "priority": s.priority,
                }
                for s in self.config.signals
            ],
            "rlc_metrics": rlc_metrics,
            "channel_metrics": channel_metrics,
        }


def create_default_simulation(
    num_signals: int = 5,
    sample_rate: int = 10000,
    duration: float = 1.0,
    noise_level: float = 0.1,
) -> dict:
    """Factory: generate a simulation with random signals, RLC filter, and channel effects."""
    rng = np.random.default_rng()
    signals = []
    modulations = ["AM", "FM", "CW", "BPSK", "QPSK"]

    for _ in range(num_signals):
        signals.append(
            SignalConfig(
                frequency=float(rng.uniform(200, sample_rate / 2.5)),
                amplitude=float(rng.uniform(0.3, 1.5)),
                phase=float(rng.uniform(0, 2 * np.pi)),
                bandwidth=float(rng.uniform(50, 300)),
                modulation=rng.choice(modulations),
                priority=int(rng.integers(1, 6)),
            )
        )

    # Auto-configure RLC filter centered on the mean signal frequency
    avg_freq = float(np.mean([s.frequency for s in signals]))
    L = 1e-3
    C = 1.0 / ((2.0 * math.pi * avg_freq) ** 2 * L) if avg_freq > 0 else 1e-6
    rlc = RLCConfig(resistance=30.0, inductance=L, capacitance=C)

    channel = ChannelConfig(
        fading_model=rng.choice(["rayleigh", "rician"]),
        num_multipath=int(rng.integers(3, 8)),
        doppler_shift_hz=float(rng.uniform(-10, 10)),
        doppler_spread_hz=float(rng.uniform(1, 15)),
        distance=float(rng.uniform(10, 500)),
    )

    config = SimulationConfig(
        sample_rate=sample_rate,
        duration=duration,
        noise_level=noise_level,
        signals=signals,
        rlc=rlc,
        channel=channel,
    )

    simulator = RFSimulator(config)
    return simulator.simulate()
