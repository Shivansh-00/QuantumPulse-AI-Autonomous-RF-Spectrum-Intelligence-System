"""Utility helpers for QuantumPulse AI."""
from __future__ import annotations

import numpy as np
from typing import List


def downsample(data: List[float], target_length: int = 500) -> List[float]:
    """Downsample a list to target_length for efficient transmission."""
    if len(data) <= target_length:
        return data
    step = len(data) // target_length
    return data[::step][:target_length]


def normalize(data: List[float]) -> List[float]:
    """Normalize data to [0, 1] range."""
    arr = np.array(data)
    min_val, max_val = arr.min(), arr.max()
    if max_val - min_val == 0:
        return [0.0] * len(data)
    return ((arr - min_val) / (max_val - min_val)).tolist()


def compute_snr(signal: List[float], noise: List[float]) -> float:
    """Compute Signal-to-Noise Ratio in dB."""
    sig_power = np.mean(np.array(signal) ** 2)
    noise_power = np.mean(np.array(noise) ** 2)
    if noise_power == 0:
        return float("inf")
    return float(10 * np.log10(sig_power / noise_power))
