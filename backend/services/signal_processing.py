"""Signal Processing Service.

Advanced spectral analysis and feature extraction for RF signals,
including SNR estimation, spectral entropy, interference classification,
and cyclostationary feature detection for AI pipeline input.
"""
from __future__ import annotations

import numpy as np
from scipy import signal as scipy_signal
from scipy.fft import fft, fftfreq
from typing import List, Dict, Optional


class SignalProcessor:
    """Processes RF signal data to extract spectral, statistical, and AI features."""

    def __init__(self, signal_data: List[float], sample_rate: int):
        self.signal = np.array(signal_data)
        self.sample_rate = sample_rate
        self.num_samples = len(self.signal)

    # ──────────────────── Core Spectral Analysis ────────────────────

    def compute_fft(self) -> dict:
        """Compute FFT and return frequency-domain representation."""
        yf = fft(self.signal)
        xf = fftfreq(self.num_samples, 1.0 / self.sample_rate)

        positive_mask = xf >= 0
        freqs = xf[positive_mask]
        magnitudes = 2.0 / self.num_samples * np.abs(yf[positive_mask])  # type: ignore[index]

        return {
            "frequencies": freqs.tolist(),
            "magnitudes": magnitudes.tolist(),
        }

    def compute_power_spectrum(self) -> dict:
        """Compute power spectral density using Welch's method."""
        nperseg = min(256, max(16, self.num_samples // 4))
        freqs, psd = scipy_signal.welch(
            self.signal, fs=self.sample_rate, nperseg=nperseg,
        )
        return {
            "frequencies": freqs.tolist(),
            "power_density": psd.tolist(),
        }

    def compute_spectrogram(self) -> dict:
        """Compute spectrogram for time-frequency analysis."""
        nperseg = min(128, max(16, self.num_samples // 8))
        freqs, times, Sxx = scipy_signal.spectrogram(
            self.signal, fs=self.sample_rate, nperseg=nperseg,
        )
        return {
            "frequencies": freqs.tolist(),
            "times": times.tolist(),
            "intensity": Sxx.tolist(),
        }

    # ──────────────────── Statistical Features ────────────────────

    def extract_statistical_features(self) -> dict:
        """Extract comprehensive statistical features from the signal."""
        sig = self.signal
        mean_val = float(np.mean(sig))
        std_val = float(np.std(sig))
        var_val = float(np.var(sig))
        rms_val = float(np.sqrt(np.mean(sig ** 2)))
        peak_val = float(np.max(np.abs(sig)))

        return {
            "mean": mean_val,
            "std": std_val,
            "variance": var_val,
            "rms": rms_val,
            "peak": peak_val,
            "crest_factor": float(peak_val / rms_val if rms_val > 0 else 0),
            "kurtosis": float(
                np.mean((sig - mean_val) ** 4) / (var_val ** 2)
                if var_val > 0 else 0
            ),
            "skewness": float(
                np.mean((sig - mean_val) ** 3) / (std_val ** 3)
                if std_val > 0 else 0
            ),
            "dynamic_range_db": float(
                20 * np.log10(peak_val / (np.min(np.abs(sig[sig != 0])) + 1e-12))
                if peak_val > 0 else 0
            ),
            "zero_crossing_rate": float(
                np.sum(np.abs(np.diff(np.sign(sig)))) / (2.0 * self.num_samples)
            ),
        }

    # ──────────────────── Peak Detection ────────────────────

    def detect_peaks(self, threshold_db: float = -20.0) -> dict:
        """Detect dominant frequency peaks in the spectrum."""
        fft_data = self.compute_fft()
        magnitudes = np.array(fft_data["magnitudes"])
        frequencies = np.array(fft_data["frequencies"])

        mag_db = 20 * np.log10(magnitudes + 1e-12)
        max_db = np.max(mag_db)

        peak_indices, _ = scipy_signal.find_peaks(
            mag_db, height=max_db + threshold_db, distance=10,
        )

        peaks = []
        for idx in peak_indices:
            peaks.append({
                "frequency": float(frequencies[idx]),
                "magnitude": float(magnitudes[idx]),
                "magnitude_db": float(mag_db[idx]),
            })
        peaks.sort(key=lambda p: p["magnitude"], reverse=True)

        return {
            "num_peaks": len(peaks),
            "peaks": peaks[:20],
            "peak_frequency": float(frequencies[np.argmax(magnitudes)]),
            "peak_magnitude": float(np.max(magnitudes)),
        }

    # ──────────────────── Band Occupancy ────────────────────

    def compute_band_occupancy(self, num_bands: int = 10) -> dict:
        """Compute occupancy levels across frequency bands."""
        fft_data = self.compute_fft()
        magnitudes = np.array(fft_data["magnitudes"])
        frequencies = np.array(fft_data["frequencies"])

        max_freq = frequencies[-1] if len(frequencies) > 0 else 1.0
        band_width = max_freq / num_bands
        bands = []

        for i in range(num_bands):
            f_low = i * band_width
            f_high = (i + 1) * band_width
            mask = (frequencies >= f_low) & (frequencies < f_high)
            band_power = float(np.mean(magnitudes[mask] ** 2)) if np.any(mask) else 0.0

            bands.append({
                "band_index": i,
                "freq_low": float(f_low),
                "freq_high": float(f_high),
                "power": band_power,
                "center_freq": float((f_low + f_high) / 2),
            })

        max_power = max(b["power"] for b in bands) if bands else 1.0
        for b in bands:
            b["occupancy"] = b["power"] / max_power if max_power > 0 else 0.0

        return {
            "num_bands": num_bands,
            "band_width": float(band_width),
            "bands": bands,
        }

    # ──────────────────── SNR Estimation ────────────────────

    def estimate_snr(self, noise_floor_percentile: float = 10.0) -> dict:
        """Estimate Signal-to-Noise Ratio from the signal itself.

        Uses PSD noise-floor estimation: the lowest `noise_floor_percentile`
        of spectral bins approximates the noise power.
        """
        psd = self.compute_power_spectrum()
        power = np.array(psd["power_density"])

        noise_threshold = np.percentile(power, noise_floor_percentile)
        noise_bins = power[power <= noise_threshold]
        signal_bins = power[power > noise_threshold]

        noise_power = float(np.mean(noise_bins)) if len(noise_bins) > 0 else 1e-12
        signal_power = float(np.mean(signal_bins)) if len(signal_bins) > 0 else 0.0

        snr_linear = signal_power / noise_power if noise_power > 0 else float("inf")
        snr_db = float(10.0 * np.log10(snr_linear)) if snr_linear > 0 else 0.0

        return {
            "snr_db": snr_db,
            "signal_power": signal_power,
            "noise_power": noise_power,
            "noise_floor_db": float(10 * np.log10(noise_power + 1e-12)),
        }

    # ──────────────────── Spectral Entropy ────────────────────

    def compute_spectral_entropy(self) -> dict:
        """Compute spectral entropy — a measure of signal complexity.

        High entropy ≈ noise-like, low entropy ≈ tonal/narrowband.
        """
        fft_data = self.compute_fft()
        magnitudes = np.array(fft_data["magnitudes"])
        power = magnitudes ** 2
        total = np.sum(power)

        if total == 0:
            return {"spectral_entropy": 0.0, "normalized_entropy": 0.0}

        p = power / total
        p = p[p > 0]  # remove zeros for log
        entropy = float(-np.sum(p * np.log2(p)))
        max_entropy = np.log2(len(p)) if len(p) > 0 else 1.0
        normalized = entropy / max_entropy if max_entropy > 0 else 0.0

        return {
            "spectral_entropy": entropy,
            "normalized_entropy": float(normalized),
        }

    # ──────────────────── Interference Classification ────────────────────

    def classify_interference(self) -> dict:
        """Classify detected interference patterns.

        Categories:
        - narrowband: single strong tone interferer
        - wideband: broadband noise-like interference
        - pulsed: intermittent burst interference
        - none: clean spectrum
        """
        stats = self.extract_statistical_features()
        peaks = self.detect_peaks(threshold_db=-15.0)
        entropy = self.compute_spectral_entropy()
        snr = self.estimate_snr()

        # Decision logic based on features
        num_peaks = peaks["num_peaks"]
        norm_entropy = entropy["normalized_entropy"]
        kurtosis = stats["kurtosis"]
        crest = stats["crest_factor"]

        classifications = []
        confidence = 0.0

        if num_peaks <= 3 and norm_entropy < 0.5:
            classifications.append("narrowband")
            confidence = max(confidence, 0.6 + (0.5 - norm_entropy))
        if norm_entropy > 0.8 and snr["snr_db"] < 5.0:
            classifications.append("wideband")
            confidence = max(confidence, norm_entropy)
        if kurtosis > 5.0 and crest > 4.0:
            classifications.append("pulsed")
            confidence = max(confidence, min(kurtosis / 10.0, 1.0))
        if not classifications:
            classifications.append("none")
            confidence = 0.9

        return {
            "interference_type": classifications[0],
            "all_types": classifications,
            "confidence": float(min(confidence, 1.0)),
            "indicators": {
                "num_peaks": num_peaks,
                "spectral_entropy": norm_entropy,
                "kurtosis": kurtosis,
                "crest_factor": crest,
                "snr_db": snr["snr_db"],
            },
        }

    # ──────────────────── AI Feature Vector ────────────────────

    def extract_ai_features(self, num_bands: int = 10) -> dict:
        """Extract a feature vector suitable for AI model input.

        Combines spectral, statistical, and derived features into
        a flat vector for LSTM/Transformer prediction models.
        """
        stats = self.extract_statistical_features()
        snr = self.estimate_snr()
        entropy = self.compute_spectral_entropy()
        occupancy = self.compute_band_occupancy(num_bands)

        band_powers = [b["power"] for b in occupancy["bands"]]
        band_occupancies = [b["occupancy"] for b in occupancy["bands"]]

        feature_vector = [
            stats["rms"],
            stats["peak"],
            stats["crest_factor"],
            stats["kurtosis"],
            stats["skewness"],
            stats["zero_crossing_rate"],
            snr["snr_db"],
            entropy["normalized_entropy"],
        ] + band_powers + band_occupancies

        return {
            "feature_vector": feature_vector,
            "feature_names": [
                "rms", "peak", "crest_factor", "kurtosis", "skewness",
                "zero_crossing_rate", "snr_db", "spectral_entropy",
            ] + [f"band_{i}_power" for i in range(num_bands)]
              + [f"band_{i}_occ" for i in range(num_bands)],
            "num_features": len(feature_vector),
        }

    # ──────────────────── Full Analysis ────────────────────

    def full_analysis(self) -> dict:
        """Run complete signal analysis and return all features."""
        return {
            "fft": self.compute_fft(),
            "power_spectrum": self.compute_power_spectrum(),
            "spectrogram": self.compute_spectrogram(),
            "statistics": self.extract_statistical_features(),
            "peaks": self.detect_peaks(),
            "band_occupancy": self.compute_band_occupancy(),
            "snr": self.estimate_snr(),
            "spectral_entropy": self.compute_spectral_entropy(),
            "interference": self.classify_interference(),
        }
