import React from 'react';

const MetricCard = React.memo(({ label, value, unit, color, subtitle }) => (
  <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-800/50 text-center">
    <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">{label}</div>
    <div className={`text-2xl font-bold font-mono ${color}`}>
      {value}
      {unit && <span className="text-sm ml-0.5">{unit}</span>}
    </div>
    {subtitle && <div className="text-[9px] text-gray-600 mt-0.5">{subtitle}</div>}
  </div>
));

export default React.memo(function PerformancePanel({ performance }) {
  if (!performance) {
    return (
      <div className="h-32 flex items-center justify-center text-gray-600">
        Waiting for performance data...
      </div>
    );
  }

  const {
    interference_reduction_pct = 0,
    latency_ms = 0,
    spectrum_efficiency = 0,
    signal_stability = 0,
    snr_db = 0,
    congestion_before = 0,
    congestion_after = 0,
    learning_cycles = 0,
  } = performance;

  const congestionReduction = congestion_before > 0
    ? ((congestion_before - congestion_after) / congestion_before * 100).toFixed(1)
    : '0.0';

  return (
    <div className="space-y-4">
      {/* Main metrics grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <MetricCard
          label="Interference Reduction"
          value={interference_reduction_pct.toFixed(1)}
          unit="%"
          color="text-green-400"
          subtitle="vs. original allocation"
        />
        <MetricCard
          label="Response Time"
          value={latency_ms.toFixed(0)}
          unit="ms"
          color={latency_ms < 100 ? 'text-green-400' : latency_ms < 500 ? 'text-yellow-400' : 'text-red-400'}
          subtitle="Real-time processing"
        />
        <MetricCard
          label="Spectrum Efficiency"
          value={(spectrum_efficiency * 100).toFixed(1)}
          unit="%"
          color="text-quantum-400"
          subtitle="bandwidth utilization"
        />
        <MetricCard
          label="Signal Stability"
          value={(signal_stability * 100).toFixed(1)}
          unit="%"
          color={signal_stability > 0.7 ? 'text-green-400' : signal_stability > 0.4 ? 'text-yellow-400' : 'text-red-400'}
          subtitle="SNR + entropy + interference"
        />
      </div>

      {/* Before vs After congestion bar */}
      <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-800/50">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs text-gray-400 uppercase tracking-wider">Congestion: Before vs After</span>
          <span className="text-xs font-mono text-green-400">↓ {congestionReduction}% reduced</span>
        </div>
        <div className="space-y-2">
          <div>
            <div className="flex justify-between text-[10px] mb-0.5">
              <span className="text-red-400">Before</span>
              <span className="text-gray-500 font-mono">{(congestion_before * 100).toFixed(1)}%</span>
            </div>
            <div className="h-3 bg-gray-800 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-700 ease-out"
                style={{
                  width: `${Math.min(congestion_before * 100, 100)}%`,
                  background: 'linear-gradient(90deg, #ef4444, #f87171)',
                }}
              />
            </div>
          </div>
          <div>
            <div className="flex justify-between text-[10px] mb-0.5">
              <span className="text-green-400">After</span>
              <span className="text-gray-500 font-mono">{(congestion_after * 100).toFixed(1)}%</span>
            </div>
            <div className="h-3 bg-gray-800 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-700 ease-out"
                style={{
                  width: `${Math.min(congestion_after * 100, 100)}%`,
                  background: 'linear-gradient(90deg, #22c55e, #4ade80)',
                }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Bottom row — learning indicator */}
      <div className="flex items-center gap-3 text-xs text-gray-500">
        <div className="flex items-center gap-1.5">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-quantum-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-quantum-500" />
          </span>
          <span>Self-Learning Active</span>
        </div>
        <span className="text-gray-600">|</span>
        <span>
          <span className="font-mono text-quantum-300">{learning_cycles}</span> feedback cycles completed
        </span>
        <span className="text-gray-600">|</span>
        <span>System improves over time using continuous feedback loops</span>
      </div>
    </div>
  );
});
