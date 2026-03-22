"""Tests for core services."""
import numpy as np
from services.rf_simulation import RFSimulator, SimulationConfig, SignalConfig, create_default_simulation
from services.signal_processing import SignalProcessor
from services.optimization_engine import (
    QuantumInspiredOptimizer, SignalAllocation, optimize_from_simulation,
)
from services.ai_prediction import CongestionPredictor
from services.autonomous_engine import AutonomousEngine


# ═══════════════ RF Simulation ═══════════════

def test_rf_simulation_basic():
    """Test that RF simulation produces valid output."""
    result = create_default_simulation(num_signals=3, sample_rate=5000, duration=0.5)
    assert len(result["time"]) == 2500
    assert len(result["signal"]) == 2500
    assert result["num_signals"] == 3
    assert len(result["signal_configs"]) == 3
    # New: RLC and channel metrics should be present
    assert "rlc_metrics" in result
    assert "channel_metrics" in result


def test_rf_simulation_custom_signals():
    """Test simulation with custom signal configurations."""
    signals = [
        SignalConfig(frequency=1000, amplitude=1.0, modulation="AM"),
        SignalConfig(frequency=2000, amplitude=0.5, modulation="FM"),
    ]
    config = SimulationConfig(sample_rate=10000, duration=0.1, noise_level=0.0, signals=signals)
    sim = RFSimulator(config)
    result = sim.simulate()
    assert result["num_signals"] == 2
    assert len(result["signal"]) == 1000


def test_rf_simulation_bpsk_qpsk():
    """Test BPSK and QPSK modulations."""
    signals = [
        SignalConfig(frequency=1000, amplitude=1.0, modulation="BPSK", priority=2),
        SignalConfig(frequency=2000, amplitude=0.8, modulation="QPSK", priority=3),
    ]
    config = SimulationConfig(sample_rate=10000, duration=0.1, noise_level=0.05, signals=signals)
    sim = RFSimulator(config)
    result = sim.simulate()
    assert result["num_signals"] == 2
    assert len(result["signal"]) == 1000


# ═══════════════ Signal Processing ═══════════════

def test_signal_processing_fft():
    """Test FFT computation."""
    sr = 1000
    t = np.linspace(0, 1, sr, endpoint=False)
    signal = np.sin(2 * np.pi * 100 * t)
    processor = SignalProcessor(signal.tolist(), sr)
    fft_result = processor.compute_fft()
    assert len(fft_result["frequencies"]) > 0
    assert len(fft_result["magnitudes"]) > 0


def test_signal_processing_peaks():
    """Test peak detection on a known signal."""
    sr = 1000
    t = np.linspace(0, 1, sr, endpoint=False)
    signal = np.sin(2 * np.pi * 100 * t) + 0.5 * np.sin(2 * np.pi * 250 * t)
    processor = SignalProcessor(signal.tolist(), sr)
    peaks = processor.detect_peaks()
    assert peaks["num_peaks"] >= 1


def test_signal_processing_statistics():
    """Test statistical feature extraction."""
    signal = [1.0, 2.0, 3.0, 4.0, 5.0] * 100
    processor = SignalProcessor(signal, 1000)
    stats = processor.extract_statistical_features()
    assert "mean" in stats
    assert "variance" in stats
    assert "rms" in stats
    assert "dynamic_range_db" in stats
    assert "zero_crossing_rate" in stats


def test_signal_processing_snr():
    """Test SNR estimation."""
    sr = 1000
    t = np.linspace(0, 1, sr, endpoint=False)
    signal = np.sin(2 * np.pi * 100 * t)
    processor = SignalProcessor(signal.tolist(), sr)
    snr = processor.estimate_snr()
    assert "snr_db" in snr
    assert "noise_floor_db" in snr


def test_signal_processing_entropy():
    """Test spectral entropy computation."""
    sr = 1000
    t = np.linspace(0, 1, sr, endpoint=False)
    signal = np.sin(2 * np.pi * 100 * t)
    processor = SignalProcessor(signal.tolist(), sr)
    entropy = processor.compute_spectral_entropy()
    assert 0.0 <= entropy["normalized_entropy"] <= 1.0


def test_signal_processing_interference():
    """Test interference classification."""
    sr = 1000
    t = np.linspace(0, 1, sr, endpoint=False)
    signal = np.sin(2 * np.pi * 100 * t) + 0.1 * np.random.randn(sr)
    processor = SignalProcessor(signal.tolist(), sr)
    result = processor.classify_interference()
    assert result["interference_type"] in ("narrowband", "wideband", "pulsed", "none")
    assert 0.0 <= result["confidence"] <= 1.0


def test_signal_processing_full_analysis():
    """Test full_analysis includes new fields."""
    sr = 1000
    t = np.linspace(0, 1, sr, endpoint=False)
    signal = np.sin(2 * np.pi * 100 * t) + 0.05 * np.random.randn(sr)
    processor = SignalProcessor(signal.tolist(), sr)
    result = processor.full_analysis()
    assert "snr" in result
    assert "spectral_entropy" in result
    assert "interference" in result


# ═══════════════ Optimisation ═══════════════

def test_optimization_basic():
    """Test optimization produces valid results."""
    signals = [
        SignalAllocation(signal_id=0, frequency=1000, bandwidth=200),
        SignalAllocation(signal_id=1, frequency=1050, bandwidth=200),
        SignalAllocation(signal_id=2, frequency=1100, bandwidth=200),
    ]
    optimizer = QuantumInspiredOptimizer(max_iterations=500)
    result = optimizer.optimize(signals)
    assert result.iterations > 0
    assert len(result.allocations) == 3
    assert result.signal_clarity >= 0
    assert result.objective_breakdown is not None


def test_optimization_from_simulation():
    """Test convenience optimization function."""
    configs = [
        {"frequency": 500, "bandwidth": 100},
        {"frequency": 550, "bandwidth": 100},
    ]
    result = optimize_from_simulation(configs)
    assert "improvement_pct" in result
    assert "power_efficiency" in result
    assert "spectral_efficiency" in result
    assert "objective_breakdown" in result
    assert len(result["optimized_allocations"]) == 2


def test_optimization_rlc_aware():
    """Test optimization with RLC passband awareness."""
    configs = [
        {"frequency": 1000, "bandwidth": 100, "priority": 2},
        {"frequency": 2000, "bandwidth": 100, "priority": 1},
    ]
    result = optimize_from_simulation(configs, rlc_resonant=1500, rlc_bandwidth=500)
    assert "improvement_pct" in result


# ═══════════════ AI Prediction ═══════════════

def test_ai_prediction():
    """Test that prediction model produces valid output with new fields."""
    predictor = CongestionPredictor(model_type="lstm")
    signal_data = np.random.randn(200).tolist()
    result = predictor.predict(signal_data)
    assert len(result["congestion_levels"]) == predictor.prediction_horizon
    assert result["risk_level"] in ("LOW", "MEDIUM", "HIGH")
    assert 0 <= result["mean_congestion"] <= 1
    # New fields
    assert "confidence" in result
    assert "trend" in result
    assert "anomaly_score" in result
    assert "confidence_interval" in result


def test_ai_synthetic_training():
    """Test synthetic data generation and training loop."""
    predictor = CongestionPredictor(model_type="lstm")
    seqs, targets = predictor.generate_synthetic_training_data(num_samples=10)
    assert len(seqs) == 10
    assert len(targets) == 10
    result = predictor.train_on_data(seqs, targets, epochs=2)
    assert result["epochs"] >= 2
    assert "final_loss" in result
    assert "best_loss" in result


def test_ai_transformer():
    """Test transformer model."""
    predictor = CongestionPredictor(model_type="transformer")
    signal_data = np.random.randn(200).tolist()
    result = predictor.predict(signal_data)
    assert len(result["congestion_levels"]) == predictor.prediction_horizon


# ═══════════════ Autonomous Engine ═══════════════

def test_autonomous_engine_monitor():
    """Test autonomous engine evaluation in low-congestion scenario."""
    engine = AutonomousEngine()
    signal_data = np.random.randn(200).tolist()
    signal_configs = [
        {"frequency": 1000, "bandwidth": 100, "priority": 1},
        {"frequency": 3000, "bandwidth": 100, "priority": 2},
    ]
    result = engine.evaluate(signal_data, signal_configs)
    assert "cycle" in result
    assert "mode" in result
    assert result["mode"] in ("monitor", "optimise", "emergency")
    assert "prediction" in result
    assert "state" in result


def test_autonomous_engine_status():
    """Test autonomous engine status endpoint."""
    engine = AutonomousEngine()
    status = engine.get_status()
    assert status["cycle"] == 0
    assert status["mode"] == "monitor"


# ═══════════════ Full Pipeline ═══════════════

def test_full_pipeline_integration():
    """Test the full pipeline end-to-end: simulate -> process -> predict -> optimize."""
    # Step 1: Simulate
    sim = create_default_simulation(num_signals=4, sample_rate=8000, duration=0.5)
    assert len(sim["signal"]) > 0
    assert "rlc_metrics" in sim

    # Step 2: Process
    processor = SignalProcessor(sim["signal"], 8000)
    full = processor.full_analysis()
    assert "snr" in full
    assert "spectral_entropy" in full
    assert "interference" in full

    # Step 3: Predict
    predictor = CongestionPredictor(model_type="lstm")
    prediction = predictor.predict(sim["signal"])
    assert prediction["risk_level"] in ("LOW", "MEDIUM", "HIGH")
    assert "confidence" in prediction

    # Step 4: Optimize
    rlc_m = sim.get("rlc_metrics") or {}
    opt_result = optimize_from_simulation(
        sim["signal_configs"],
        rlc_resonant=rlc_m.get("resonant_frequency"),
        rlc_bandwidth=rlc_m.get("bandwidth_3db"),
    )
    assert len(opt_result["optimized_allocations"]) == 4

    # Step 5: Autonomous
    engine = AutonomousEngine(predictor=predictor)
    auto_result = engine.evaluate(
        sim["signal"], sim["signal_configs"],
        rlc_resonant=rlc_m.get("resonant_frequency"),
        rlc_bandwidth=rlc_m.get("bandwidth_3db"),
    )
    assert auto_result["cycle"] == 1
