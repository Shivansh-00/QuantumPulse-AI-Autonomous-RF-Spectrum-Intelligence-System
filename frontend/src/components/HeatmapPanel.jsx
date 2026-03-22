import React, { useMemo } from 'react';

export default React.memo(function HeatmapPanel({ analysis }) {
  const bands = useMemo(() => {
    return analysis?.band_occupancy?.bands || [];
  }, [analysis]);

  if (!bands.length) {
    return <div className="h-48 flex items-center justify-center text-gray-600">Waiting for data...</div>;
  }

  const getColor = (occupancy) => {
    if (occupancy > 0.8) return 'bg-red-500';
    if (occupancy > 0.6) return 'bg-orange-500';
    if (occupancy > 0.4) return 'bg-yellow-500';
    if (occupancy > 0.2) return 'bg-green-500';
    return 'bg-green-700';
  };

  return (
    <div>
      {/* Heatmap Grid */}
      <div className="grid grid-cols-5 sm:grid-cols-10 gap-1.5 mb-4">
        {bands.map((band, i) => (
          <div key={`band-${band.center_freq}`} className="flex flex-col items-center">
            <div
              className={`w-full aspect-square rounded-lg ${getColor(band.occupancy)} transition-colors duration-500`}
              style={{ opacity: 0.3 + band.occupancy * 0.7 }}
              title={`Band ${i}: ${band.freq_low.toFixed(0)}-${band.freq_high.toFixed(0)} Hz | Occupancy: ${(band.occupancy * 100).toFixed(0)}%`}
            />
            <span className="text-[9px] text-gray-500 mt-1 font-mono">
              {band.center_freq.toFixed(0)}
            </span>
          </div>
        ))}
      </div>

      {/* Legend */}
      <div className="flex items-center justify-center gap-4 text-[10px] text-gray-400">
        <div className="flex items-center gap-1"><div className="w-3 h-3 rounded bg-green-700" /> Low</div>
        <div className="flex items-center gap-1"><div className="w-3 h-3 rounded bg-green-500" /> Medium-Low</div>
        <div className="flex items-center gap-1"><div className="w-3 h-3 rounded bg-yellow-500" /> Medium</div>
        <div className="flex items-center gap-1"><div className="w-3 h-3 rounded bg-orange-500" /> High</div>
        <div className="flex items-center gap-1"><div className="w-3 h-3 rounded bg-red-500" /> Critical</div>
      </div>

      {/* Band details table */}
      <div className="mt-4 max-h-40 overflow-auto">
        <table className="w-full text-xs text-gray-400">
          <thead>
            <tr className="text-gray-500 border-b border-gray-800">
              <th className="py-1 text-left">Band</th>
              <th className="py-1 text-left">Range (Hz)</th>
              <th className="py-1 text-right">Power</th>
              <th className="py-1 text-right">Occupancy</th>
            </tr>
          </thead>
          <tbody>
            {bands.map((band, i) => (
              <tr key={`row-${band.center_freq}`} className="border-b border-gray-800/50">
                <td className="py-1 font-mono">{i}</td>
                <td className="py-1">{band.freq_low.toFixed(0)} – {band.freq_high.toFixed(0)}</td>
                <td className="py-1 text-right font-mono">{band.power.toFixed(6)}</td>
                <td className="py-1 text-right font-mono">{(band.occupancy * 100).toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
});
