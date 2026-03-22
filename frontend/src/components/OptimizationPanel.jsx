import React, { useMemo, useState } from 'react';
import {
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ZAxis, Legend,
  LineChart, Line,
} from 'recharts';

export default React.memo(function OptimizationPanel({ optimization }) {
  const [view, setView] = useState('allocation'); // 'allocation' | 'convergence'

  const originalData = useMemo(() => {
    if (!optimization?.original_allocations) return [];
    return optimization.original_allocations.map((a) => ({
      freq: parseFloat(a.frequency.toFixed(1)),
      bw: parseFloat(a.bandwidth.toFixed(1)),
      id: a.signal_id,
    }));
  }, [optimization]);

  const optimizedData = useMemo(() => {
    if (!optimization?.optimized_allocations) return [];
    return optimization.optimized_allocations.map((a) => ({
      freq: parseFloat(a.frequency.toFixed(1)),
      bw: parseFloat(a.bandwidth.toFixed(1)),
      id: a.signal_id,
    }));
  }, [optimization]);

  const convergenceData = useMemo(() => {
    if (!optimization?.cost_history?.length) return [];
    const histLen = optimization.cost_history.length;
    const iters = optimization.iterations || histLen;
    return optimization.cost_history.map((cost, i) => ({
      iteration: Math.round(i * (iters / Math.max(histLen, 1))),
      cost: parseFloat((cost ?? 0).toFixed(4)),
    }));
  }, [optimization]);

  if (!optimization) {
    return <div className="h-64 flex items-center justify-center text-gray-600">Waiting for data...</div>;
  }

  return (
    <div>
      {/* Metrics Row */}
      <div className="flex flex-wrap items-center gap-6 mb-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-green-400 font-mono">
            {(optimization.improvement_pct ?? 0).toFixed(1)}%
          </div>
          <div className="text-[10px] text-gray-500 uppercase">Interference Reduction</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-quantum-400 font-mono">
            {((optimization.signal_clarity ?? 0) * 100).toFixed(1)}%
          </div>
          <div className="text-[10px] text-gray-500 uppercase">Signal Clarity</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-pulse-400 font-mono">
            {optimization.iterations ?? 0}
          </div>
          <div className="text-[10px] text-gray-500 uppercase">Iterations</div>
        </div>

        {/* View toggle */}
        <div className="ml-auto flex gap-1">
          <button
            onClick={() => setView('allocation')}
            className={`px-3 py-1 rounded text-xs font-medium transition ${
              view === 'allocation'
                ? 'bg-quantum-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:text-white'
            }`}
          >
            Before vs After
          </button>
          <button
            onClick={() => setView('convergence')}
            className={`px-3 py-1 rounded text-xs font-medium transition ${
              view === 'convergence'
                ? 'bg-quantum-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:text-white'
            }`}
          >
            Convergence
          </button>
        </div>
      </div>

      {/* Charts */}
      {view === 'allocation' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Before */}
          <div>
            <h4 className="text-xs text-red-400 font-semibold mb-2 uppercase">Original Allocation</h4>
            <ResponsiveContainer width="100%" height={200}>
              <ScatterChart margin={{ bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis
                  dataKey="freq"
                  name="Frequency"
                  stroke="#475569"
                  tick={{ fontSize: 10 }}
                  label={{ value: 'Frequency (Hz)', position: 'bottom', fill: '#64748b', fontSize: 10 }}
                />
                <YAxis
                  dataKey="bw"
                  name="Bandwidth"
                  stroke="#475569"
                  tick={{ fontSize: 10 }}
                  label={{ value: 'BW', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 10 }}
                />
                <ZAxis range={[80, 80]} />
                <Tooltip
                  contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8, fontSize: 11 }}
                  formatter={(v, name) => [v.toFixed(1), name]}
                />
                <Scatter data={originalData} fill="#ef4444" opacity={0.9} />
              </ScatterChart>
            </ResponsiveContainer>
          </div>

          {/* After */}
          <div>
            <h4 className="text-xs text-green-400 font-semibold mb-2 uppercase">Optimized Allocation</h4>
            <ResponsiveContainer width="100%" height={200}>
              <ScatterChart margin={{ bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis
                  dataKey="freq"
                  name="Frequency"
                  stroke="#475569"
                  tick={{ fontSize: 10 }}
                  label={{ value: 'Frequency (Hz)', position: 'bottom', fill: '#64748b', fontSize: 10 }}
                />
                <YAxis
                  dataKey="bw"
                  name="Bandwidth"
                  stroke="#475569"
                  tick={{ fontSize: 10 }}
                  label={{ value: 'BW', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 10 }}
                />
                <ZAxis range={[80, 80]} />
                <Tooltip
                  contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8, fontSize: 11 }}
                  formatter={(v, name) => [v.toFixed(1), name]}
                />
                <Scatter data={optimizedData} fill="#22c55e" opacity={0.9} />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={convergenceData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis
              dataKey="iteration"
              stroke="#475569"
              tick={{ fontSize: 10 }}
              label={{ value: 'Iteration', position: 'bottom', fill: '#64748b', fontSize: 11 }}
            />
            <YAxis stroke="#475569" tick={{ fontSize: 10 }} />
            <Tooltip
              contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8, fontSize: 12 }}
            />
            <Line
              type="monotone"
              dataKey="cost"
              stroke="#3380ff"
              dot={false}
              strokeWidth={2}
              name="Cost Function"
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
});
