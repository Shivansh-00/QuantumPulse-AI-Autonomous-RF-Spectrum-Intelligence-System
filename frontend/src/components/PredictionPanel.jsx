import React, { useMemo } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine,
} from 'recharts';

export default React.memo(function PredictionPanel({ prediction }) {
  const chartData = useMemo(() => {
    if (!prediction?.congestion_levels) return [];
    return prediction.congestion_levels.map((level, i) => ({
      step: i + 1,
      congestion: parseFloat((level * 100).toFixed(1)),
    }));
  }, [prediction]);

  const riskColor =
    prediction?.risk_level === 'HIGH'
      ? '#ef4444'
      : prediction?.risk_level === 'MEDIUM'
      ? '#f59e0b'
      : '#22c55e';

  if (!chartData.length) {
    return <div className="h-64 flex items-center justify-center text-gray-600">Waiting for data...</div>;
  }

  return (
    <div>
      {/* Risk Badge + Extra Info */}
      <div className="flex flex-wrap items-center gap-4 mb-4">
        <div
          className="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider"
          style={{ backgroundColor: riskColor + '20', color: riskColor, border: `1px solid ${riskColor}40` }}
        >
          {prediction.risk_level} Risk
        </div>
        <span className="text-xs text-gray-400">
          Avg: <span className="font-mono text-white">{((prediction.mean_congestion ?? 0) * 100).toFixed(1)}%</span>
        </span>
        <span className="text-xs text-gray-400">
          Peak: <span className="font-mono text-white">{((prediction.max_congestion ?? 0) * 100).toFixed(1)}%</span>
        </span>
        {prediction.confidence != null && (
          <span className="text-xs text-gray-400">
            Confidence: <span className="font-mono text-quantum-300">{(prediction.confidence * 100).toFixed(0)}%</span>
          </span>
        )}
        {prediction.trend && (
          <span className="text-xs text-gray-400">
            Trend: <span className={`font-mono ${prediction.trend === 'increasing' ? 'text-red-400' : prediction.trend === 'decreasing' ? 'text-green-400' : 'text-gray-300'}`}>
              {prediction.trend === 'increasing' ? '↑' : prediction.trend === 'decreasing' ? '↓' : '→'} {prediction.trend}
            </span>
          </span>
        )}
        {prediction.anomaly_score != null && (
          <span className="text-xs text-gray-400">
            Anomaly: <span className={`font-mono ${prediction.anomaly_score > 0.5 ? 'text-red-400' : 'text-gray-300'}`}>{prediction.anomaly_score.toFixed(3)}</span>
          </span>
        )}
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis
            dataKey="step"
            stroke="#475569"
            tick={{ fontSize: 10 }}
            label={{ value: 'Future Time Step', position: 'bottom', fill: '#64748b', fontSize: 11 }}
          />
          <YAxis
            stroke="#475569"
            tick={{ fontSize: 10 }}
            domain={[0, 100]}
            label={{ value: '%', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 11 }}
          />
          <Tooltip
            contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8, fontSize: 12 }}
            formatter={(v) => [`${v}%`, 'Congestion']}
          />
          <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="5 5" label={{ value: 'High', fill: '#ef4444', fontSize: 10 }} />
          <ReferenceLine y={40} stroke="#f59e0b" strokeDasharray="5 5" label={{ value: 'Med', fill: '#f59e0b', fontSize: 10 }} />
          <Bar
            dataKey="congestion"
            radius={[4, 4, 0, 0]}
            fill={riskColor}
            fillOpacity={0.8}
            name="Congestion %"
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
});
