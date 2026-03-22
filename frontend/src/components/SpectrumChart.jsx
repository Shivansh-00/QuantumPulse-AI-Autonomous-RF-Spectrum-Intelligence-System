import React, { useMemo } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';

export default React.memo(function SpectrumChart({ simulation }) {
  const chartData = useMemo(() => {
    if (!simulation?.time || !simulation?.signal) return [];
    // Downsample to ~300 points for smooth rendering
    const step = Math.max(1, Math.floor(simulation.time.length / 300));
    const data = [];
    for (let i = 0; i < simulation.time.length; i += step) {
      data.push({
        t: parseFloat((simulation.time[i] * 1000).toFixed(2)),
        signal: parseFloat(simulation.signal[i].toFixed(4)),
        clean: simulation.clean_signal
          ? parseFloat(simulation.clean_signal[i].toFixed(4))
          : undefined,
      });
    }
    return data;
  }, [simulation]);

  if (!chartData.length) {
    return <div className="h-64 flex items-center justify-center text-gray-600">Waiting for data...</div>;
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
        <XAxis
          dataKey="t"
          stroke="#475569"
          tick={{ fontSize: 10 }}
          label={{ value: 'Time (ms)', position: 'bottom', fill: '#64748b', fontSize: 11 }}
        />
        <YAxis stroke="#475569" tick={{ fontSize: 10 }} />
        <Tooltip
          contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8, fontSize: 12 }}
          labelFormatter={(v) => `${v} ms`}
        />
        <Line
          type="monotone"
          dataKey="signal"
          stroke="#3380ff"
          dot={false}
          strokeWidth={1.5}
          name="Signal + Noise"
        />
        <Line
          type="monotone"
          dataKey="clean"
          stroke="#22c55e"
          dot={false}
          strokeWidth={1}
          strokeDasharray="4 2"
          name="Clean Signal"
          opacity={0.6}
        />
      </LineChart>
    </ResponsiveContainer>
  );
});
