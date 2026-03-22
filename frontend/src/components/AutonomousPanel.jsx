import React from 'react';

const MODE_STYLES = {
  monitor: { bg: 'bg-green-500/10', border: 'border-green-500/30', text: 'text-green-400', label: 'MONITORING' },
  optimise: { bg: 'bg-yellow-500/10', border: 'border-yellow-500/30', text: 'text-yellow-400', label: 'OPTIMISING' },
  emergency: { bg: 'bg-red-500/10', border: 'border-red-500/30', text: 'text-red-400', label: 'EMERGENCY' },
};

export default React.memo(function AutonomousPanel({ autonomous }) {
  if (!autonomous) {
    return (
      <div className="h-48 flex items-center justify-center text-gray-600">
        Waiting for autonomous data...
      </div>
    );
  }

  const state = autonomous.state || {};
  const actions = autonomous.actions || [];
  const history = autonomous.history || [];
  const style = MODE_STYLES[autonomous.mode] || MODE_STYLES.monitor;

  return (
    <div className="space-y-4">
      {/* Mode & State Row */}
      <div className="flex flex-wrap items-center gap-4">
        <div
          className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider border ${style.bg} ${style.border} ${style.text}`}
        >
          {style.label}
        </div>
        <span className="text-xs text-gray-400">
          Cycle: <span className="font-mono text-white">{autonomous.cycle}</span>
        </span>
        <span className="text-xs text-gray-400">
          Congestion: <span className="font-mono text-white">{((state.congestion || 0) * 100).toFixed(1)}%</span>
        </span>
        <span className="text-xs text-gray-400">
          Anomaly: <span className="font-mono text-white">{(state.anomaly || 0).toFixed(3)}</span>
        </span>
        <span className="text-xs text-gray-400">
          Interference: <span className="font-mono text-white">{(state.interference || 0).toFixed(3)}</span>
        </span>
        <span className="text-xs text-gray-400">
          Clarity: <span className="font-mono text-white">{((state.clarity || 0) * 100).toFixed(1)}%</span>
        </span>
      </div>

      {/* Actions Table */}
      {actions.length > 0 && (
        <div>
          <h4 className="text-xs text-gray-500 uppercase tracking-wider mb-2">
            Reconfiguration Actions
          </h4>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="text-left text-gray-500 border-b border-gray-800">
                  <th className="py-1 pr-3">Signal</th>
                  <th className="py-1 pr-3">Old Freq</th>
                  <th className="py-1 pr-3">New Freq</th>
                  <th className="py-1 pr-3">Power</th>
                  <th className="py-1">Reason</th>
                </tr>
              </thead>
              <tbody>
                {actions.map((a, i) => (
                  <tr key={i} className="border-b border-gray-800/50">
                    <td className="py-1 pr-3 font-mono text-white">#{a.signal_id}</td>
                    <td className="py-1 pr-3 font-mono text-red-400">{a.old_frequency} Hz</td>
                    <td className="py-1 pr-3 font-mono text-green-400">{a.new_frequency} Hz</td>
                    <td className="py-1 pr-3 font-mono text-quantum-300">{a.new_power}</td>
                    <td className="py-1 text-gray-400 truncate max-w-[260px]">{a.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* History Timeline (last 10) */}
      {history.length > 0 && (
        <div>
          <h4 className="text-xs text-gray-500 uppercase tracking-wider mb-2">
            Recent History
          </h4>
          <div className="flex gap-1.5 overflow-x-auto pb-1">
            {history.slice(-10).map((h, i) => {
              const s = MODE_STYLES[h.mode] || MODE_STYLES.monitor;
              return (
                <div
                  key={i}
                  className={`flex-shrink-0 w-9 h-9 rounded flex flex-col items-center justify-center ${s.bg} border ${s.border}`}
                  title={`Cycle ${h.cycle}: ${h.mode} (${h.actions_count} actions)`}
                >
                  <span className={`text-[9px] font-bold ${s.text}`}>
                    {h.actions_count || 0}
                  </span>
                  <span className="text-[7px] text-gray-500">c{h.cycle}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
});
