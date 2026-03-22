import React, { useState, useCallback, useMemo } from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import ErrorBoundary from './components/ErrorBoundary';
import Header from './components/Header';
import ControlPanel from './components/ControlPanel';
import SpectrumChart from './components/SpectrumChart';
import FFTChart from './components/FFTChart';
import HeatmapPanel from './components/HeatmapPanel';
import PredictionPanel from './components/PredictionPanel';
import OptimizationPanel from './components/OptimizationPanel';
import AutonomousPanel from './components/AutonomousPanel';
import WaveScene from './components/WaveScene';
import StatsBar from './components/StatsBar';
import PerformancePanel from './components/PerformancePanel';
import XAIPanel from './components/XAIPanel';
import AIAssistantPanel from './components/AIAssistantPanel';

export default function App() {
  const { data, isConnected, error, sendConfig, reconnectAttempt } = useWebSocket();
  const [config, setConfig] = useState({
    num_signals: 5,
    noise_level: 0.1,
    sample_rate: 10000,
    scenario: 'urban',
    quantum_mode: false,
  });

  const handleConfigChange = useCallback(
    (newConfig) => {
      setConfig(newConfig);
      sendConfig(newConfig);
    },
    [sendConfig],
  );

  const simulation = useMemo(() => data?.simulation, [data?.simulation]);
  const analysis = useMemo(() => data?.analysis, [data?.analysis]);
  const prediction = useMemo(() => data?.prediction, [data?.prediction]);
  const optimization = useMemo(() => data?.optimization, [data?.optimization]);
  const autonomous = useMemo(() => data?.autonomous, [data?.autonomous]);
  const xai = useMemo(() => data?.xai, [data?.xai]);
  const performance = useMemo(() => data?.performance, [data?.performance]);
  const quantumMode = data?.quantum_mode ?? config.quantum_mode;
  const scenario = data?.scenario ?? config.scenario;

  return (
    <div className="min-h-screen flex flex-col">
      <Header
        isConnected={isConnected}
        latencyMs={performance?.latency_ms}
        learningCycles={performance?.learning_cycles}
        reconnectAttempt={reconnectAttempt}
      />

      {/* Connection error banner */}
      {!isConnected && reconnectAttempt > 0 && (
        <div className="bg-yellow-900/30 border-b border-yellow-500/20 px-4 py-2 text-center text-xs text-yellow-300">
          Reconnecting to server{reconnectAttempt > 1 ? ` (attempt ${reconnectAttempt})` : ''}...
        </div>
      )}

      {/* 3D Hero Visualization */}
      <div className="h-64 w-full relative overflow-hidden">
        <ErrorBoundary fallbackMessage="3D visualization unavailable">
          <WaveScene signalData={simulation?.signal} />
        </ErrorBoundary>
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-gray-950 pointer-events-none" />
      </div>

      <main className="flex-1 px-4 lg:px-8 pb-8 -mt-8 relative z-10 space-y-6">
        {/* Stats Bar */}
        <ErrorBoundary fallbackMessage="Stats display error">
          <StatsBar analysis={analysis} prediction={prediction} optimization={optimization} autonomous={autonomous} />
        </ErrorBoundary>

        {/* Controls */}
        <ErrorBoundary fallbackMessage="Control panel error">
          <ControlPanel
            config={config}
            onChange={handleConfigChange}
            quantumMode={quantumMode}
            scenario={scenario}
          />
        </ErrorBoundary>

        {/* Performance Metrics - Full Width */}
        <ErrorBoundary fallbackMessage="Performance metrics error">
          <PerformancePanel performance={performance} />
        </ErrorBoundary>

        {/* Autonomous Reconfiguration - Full Width */}
        <div className="glass-card glow-border p-5 animate-slide-up">
          <h3 className="text-sm font-semibold text-cyan-400 uppercase tracking-wide mb-4">
            Autonomous Reconfiguration Engine
          </h3>
          <ErrorBoundary fallbackMessage="Autonomous engine display error">
            <AutonomousPanel autonomous={autonomous} />
          </ErrorBoundary>
        </div>

        {/* XAI + AI Assistant Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="glass-card glow-border p-5 animate-slide-up">
            <h3 className="text-sm font-semibold text-yellow-400 uppercase tracking-wide mb-4">
              🧠 Explainable AI — Why These Decisions?
            </h3>
            <ErrorBoundary fallbackMessage="XAI display error">
              <XAIPanel xai={xai} />
            </ErrorBoundary>
          </div>

          <div className="glass-card glow-border p-5 animate-slide-up">
            <h3 className="text-sm font-semibold text-quantum-400 uppercase tracking-wide mb-4">
              💬 AI Spectrum Assistant
            </h3>
            <ErrorBoundary fallbackMessage="AI Assistant error">
              <AIAssistantPanel />
            </ErrorBoundary>
          </div>
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Waveform */}
          <div className="glass-card glow-border p-5 animate-slide-up">
            <h3 className="text-sm font-semibold text-quantum-400 uppercase tracking-wide mb-4">
              RF Spectrum Waveform
            </h3>
            <ErrorBoundary fallbackMessage="Waveform chart error">
              <SpectrumChart simulation={simulation} />
            </ErrorBoundary>
          </div>

          {/* FFT */}
          <div className="glass-card glow-border p-5 animate-slide-up">
            <h3 className="text-sm font-semibold text-quantum-400 uppercase tracking-wide mb-4">
              Frequency Spectrum (FFT)
            </h3>
            <ErrorBoundary fallbackMessage="FFT chart error">
              <FFTChart analysis={analysis} />
            </ErrorBoundary>
          </div>

          {/* Heatmap */}
          <div className="glass-card glow-border p-5 animate-slide-up">
            <h3 className="text-sm font-semibold text-pulse-400 uppercase tracking-wide mb-4">
              Band Occupancy Heatmap
            </h3>
            <ErrorBoundary fallbackMessage="Heatmap error">
              <HeatmapPanel analysis={analysis} />
            </ErrorBoundary>
          </div>

          {/* Prediction */}
          <div className="glass-card glow-border p-5 animate-slide-up">
            <h3 className="text-sm font-semibold text-pulse-400 uppercase tracking-wide mb-4">
              AI Congestion Prediction
            </h3>
            <ErrorBoundary fallbackMessage="Prediction chart error">
              <PredictionPanel prediction={prediction} />
            </ErrorBoundary>
          </div>
        </div>

        {/* Optimization - Full Width */}
        <div className="glass-card glow-border p-5 animate-slide-up">
          <h3 className="text-sm font-semibold text-green-400 uppercase tracking-wide mb-4">
            Quantum-Inspired Frequency Optimization
          </h3>
          <ErrorBoundary fallbackMessage="Optimization chart error">
            <OptimizationPanel optimization={optimization} />
          </ErrorBoundary>
        </div>
      </main>
    </div>
  );
}
