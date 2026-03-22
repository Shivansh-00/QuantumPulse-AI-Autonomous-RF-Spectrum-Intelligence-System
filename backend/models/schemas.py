"""Pydantic schemas for API request/response validation."""
from __future__ import annotations

from typing import List, Optional, Dict
from pydantic import BaseModel, Field


# ═══════════════ RF Simulation ═══════════════

class SignalConfigSchema(BaseModel):
    frequency: float = Field(..., gt=0, description="Signal frequency in Hz")
    amplitude: float = Field(1.0, gt=0)
    bandwidth: float = Field(100.0, gt=0)
    modulation: str = Field("AM", pattern="^(AM|FM|CW|BPSK|QPSK)$")
    priority: int = Field(1, ge=1, le=10)


class SimulationRequest(BaseModel):
    num_signals: int = Field(5, ge=1, le=50)
    sample_rate: int = Field(10000, ge=1000, le=100000)
    duration: float = Field(1.0, gt=0, le=10.0)
    noise_level: float = Field(0.1, ge=0, le=2.0)
    signals: Optional[List[SignalConfigSchema]] = None


class SimulationResponse(BaseModel):
    time: List[float]
    signal: List[float]
    clean_signal: List[float]
    noise: List[float]
    interference: List[float]
    sample_rate: int
    duration: float
    num_signals: int
    signal_configs: List[Dict]
    rlc_metrics: Optional[Dict] = None
    channel_metrics: Optional[Dict] = None


# ═══════════════ Signal Processing ═══════════════

class AnalysisRequest(BaseModel):
    signal: List[float]
    sample_rate: int = 10000


class AnalysisResponse(BaseModel):
    fft: Dict
    power_spectrum: Dict
    spectrogram: Dict
    statistics: Dict
    peaks: Dict
    band_occupancy: Dict
    snr: Optional[Dict] = None
    spectral_entropy: Optional[float] = None
    interference: Optional[Dict] = None


# ═══════════════ AI Prediction ═══════════════

class PredictionRequest(BaseModel):
    signal_data: List[float] = Field(..., min_length=50, max_length=50000)
    model_type: str = Field("lstm", pattern="^(lstm|transformer)$")


class PredictionResponse(BaseModel):
    congestion_levels: List[float]
    mean_congestion: float
    max_congestion: float
    prediction_horizon: int
    risk_level: str
    confidence: Optional[float] = None
    trend: Optional[str] = None
    anomaly_score: Optional[float] = None
    confidence_interval: Optional[Dict] = None


# ═══════════════ Optimisation ═══════════════

class OptimizationRequest(BaseModel):
    signal_configs: List[Dict]
    band_occupancy: Optional[List[Dict]] = None
    rlc_resonant: Optional[float] = None
    rlc_bandwidth: Optional[float] = None


class OptimizationResponse(BaseModel):
    original_allocations: List[Dict]
    optimized_allocations: List[Dict]
    total_interference: float
    signal_clarity: float
    improvement_pct: float
    iterations: int
    power_efficiency: Optional[float] = None
    spectral_efficiency: Optional[float] = None
    objective_breakdown: Optional[Dict] = None
    temperature_history: List[float]
    cost_history: List[float]


# ═══════════════ Autonomous ═══════════════

class AutonomousStatusResponse(BaseModel):
    cycle: int
    mode: str
    congestion: float
    risk: str
    anomaly: float
    interference: float
    clarity: float
    history_length: int
    history: List[Dict]


# ═══════════════ Full Pipeline ═══════════════

class PipelineRequest(BaseModel):
    num_signals: int = Field(5, ge=1, le=50)
    sample_rate: int = Field(10000, ge=1000, le=100000)
    duration: float = Field(1.0, gt=0, le=10.0)
    noise_level: float = Field(0.1, ge=0, le=2.0)


class PipelineResponse(BaseModel):
    simulation: SimulationResponse
    analysis: AnalysisResponse
    prediction: PredictionResponse
    optimization: OptimizationResponse
