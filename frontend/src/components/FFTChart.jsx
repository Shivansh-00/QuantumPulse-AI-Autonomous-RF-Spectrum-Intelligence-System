import React, { useMemo } from 'react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';

export default React.memo(function FFTChart({ analysis }) {
  const chartData = useMemo(() => {
    if (!analysis?.fft?.frequencies || !analysis?.fft?.magnitudes) return [];
    return analysis.fft.frequencies.map((f, i) => ({
      freq: parseFloat(f.toFixed(1)),
      mag: parseFloat(analysis.fft.magnitudes[i].toFixed(6)),
    }));
  }, [analysis]);

  if (!chartData.length) {
    return <div className="h-64 flex items-center justify-center text-gray-600">Waiting for data...</div>;
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <AreaChart data={chartData}>
        <defs>
          <linearGradient id="fftGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#d946ef" stopOpacity={0.4} />
            <stop offset="100%" stopColor="#d946ef" stopOpacity={0.02} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
        <XAxis
          dataKey="freq"
          stroke="#475569"
          tick={{ fontSize: 10 }}
          label={{ value: 'Frequency (Hz)', position: 'bottom', fill: '#64748b', fontSize: 11 }}
        />
        <YAxis stroke="#475569" tick={{ fontSize: 10 }} />
        <Tooltip
          contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8, fontSize: 12 }}
          labelFormatter={(v) => `${v} Hz`}
        />
        <Area
          type="monotone"
          dataKey="mag"
          stroke="#d946ef"
          fill="url(#fftGrad)"
          strokeWidth={1.5}
          name="Magnitude"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
});
