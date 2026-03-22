import React, { useCallback } from 'react';

const SCENARIOS = [
  { id: 'urban', label: '🏙️ Urban Network' },
  { id: 'satellite', label: '🛰️ Satellite System' },
  { id: 'defense', label: '🛡️ Defense Comms' },
  { id: 'iot', label: '📡 IoT Dense' },
];

export default React.memo(function ControlPanel({ config, onChange, quantumMode, scenario }) {
  const update = useCallback((key, value) => onChange({ ...config, [key]: value }), [config, onChange]);

  return (
    <div className="glass-card glow-border px-5 py-4 space-y-4">
      {/* Row 1: Scenario + Quantum Toggle */}
      <div className="flex flex-wrap items-center gap-4">
        <label className="flex flex-col gap-1 text-xs text-gray-400">
          Scenario
          <select
            value={config.scenario || scenario || 'urban'}
            onChange={(e) => update('scenario', e.target.value)}
            className="bg-gray-800 border border-gray-700 rounded px-2 py-1.5 text-white text-sm min-w-[160px]"
          >
            {SCENARIOS.map((s) => (
              <option key={s.id} value={s.id}>{s.label}</option>
            ))}
          </select>
        </label>

        <div className="flex flex-col gap-1 text-xs text-gray-400">
          Quantum Mode
          <button
            onClick={() => update('quantum_mode', !config.quantum_mode)}
            className={`relative px-4 py-1.5 rounded-lg text-sm font-bold uppercase tracking-wider transition-all duration-300 ${
              quantumMode
                ? 'bg-purple-600 text-white shadow-[0_0_20px_rgba(147,51,234,0.5)] border border-purple-400/50'
                : 'bg-gray-800 text-gray-500 border border-gray-700 hover:border-purple-500/40'
            }`}
          >
            {quantumMode && (
              <span className="absolute inset-0 rounded-lg animate-pulse bg-purple-500/10 pointer-events-none" />
            )}
            {quantumMode ? '⚛️ ACTIVE' : '⚛️ OFF'}
          </button>
        </div>
      </div>

      {/* Row 2: Signal Controls */}
      <div className="flex flex-wrap items-center gap-6">
        <label className="flex flex-col gap-1 text-xs text-gray-400">
          Signals
          <input
            type="range"
            min={1}
            max={20}
            value={config.num_signals}
            onChange={(e) => update('num_signals', parseInt(e.target.value))}
            className="w-32 accent-quantum-500"
          />
          <span className="text-white font-mono text-sm">{config.num_signals}</span>
        </label>

        <label className="flex flex-col gap-1 text-xs text-gray-400">
          Noise Level
          <input
            type="range"
            min={0}
            max={200}
            value={Math.round(config.noise_level * 100)}
            onChange={(e) => update('noise_level', parseInt(e.target.value) / 100)}
            className="w-32 accent-pulse-500"
          />
          <span className="text-white font-mono text-sm">
            {config.noise_level.toFixed(2)}
          </span>
        </label>

        <label className="flex flex-col gap-1 text-xs text-gray-400">
          Sample Rate
          <select
            value={config.sample_rate}
            onChange={(e) => update('sample_rate', parseInt(e.target.value))}
            className="bg-gray-800 border border-gray-700 rounded px-2 py-1 text-white text-sm"
          >
            <option value={5000}>5 kHz</option>
            <option value={10000}>10 kHz</option>
            <option value={20000}>20 kHz</option>
            <option value={44100}>44.1 kHz</option>
          </select>
        </label>
      </div>
    </div>
  );
});
