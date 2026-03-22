import React, { useMemo } from 'react';

const modeColors = {
  monitor: 'text-green-400',
  optimise: 'text-yellow-400',
  emergency: 'text-red-400',
};

export default React.memo(function StatsBar({ analysis, prediction, optimization, autonomous }) {
  const stats = useMemo(() => [
    {
      label: 'Peak Frequency',
      value: analysis?.peaks?.peak_frequency
        ? `${analysis.peaks.peak_frequency.toFixed(0)} Hz`
        : '—',
      color: 'text-quantum-400',
    },
    {
      label: 'SNR',
      value: analysis?.snr?.snr_db != null
        ? `${analysis.snr.snr_db.toFixed(1)} dB`
        : '—',
      color: 'text-quantum-300',
    },
    {
      label: 'Congestion Risk',
      value: prediction?.risk_level || '—',
      color:
        prediction?.risk_level === 'HIGH'
          ? 'text-red-400'
          : prediction?.risk_level === 'MEDIUM'
          ? 'text-yellow-400'
          : 'text-green-400',
    },
    {
      label: 'AI Confidence',
      value: prediction?.confidence != null
        ? `${(prediction.confidence * 100).toFixed(0)}%`
        : '—',
      color: 'text-pulse-400',
    },
    {
      label: 'Signal Clarity',
      value: optimization?.signal_clarity != null
        ? `${(optimization.signal_clarity * 100).toFixed(1)}%`
        : '—',
      color: 'text-green-400',
    },
    {
      label: 'Improvement',
      value: optimization?.improvement_pct != null
        ? `${optimization.improvement_pct.toFixed(1)}%`
        : '—',
      color: 'text-pulse-400',
    },
    {
      label: 'Engine Mode',
      value: autonomous?.mode?.toUpperCase() || '—',
      color: modeColors[autonomous?.mode] || 'text-gray-400',
    },
  ], [analysis, prediction, optimization, autonomous]);

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
      {stats.map((s) => (
        <div
          key={s.label}
          className="glass-card px-4 py-3 flex flex-col items-center text-center"
        >
          <span className="text-[10px] text-gray-500 uppercase tracking-wider">
            {s.label}
          </span>
          <span className={`text-lg font-bold font-mono ${s.color}`}>
            {s.value}
          </span>
        </div>
      ))}
    </div>
  );
});
