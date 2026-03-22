import React, { useState } from 'react';

const SECTION_ICONS = {
  prediction: '🧠',
  actions: '⚡',
  optimization: '⚛️',
  anomaly: '⚠️',
};

const SECTION_LABELS = {
  prediction: 'AI Prediction',
  actions: 'Autonomous Actions',
  optimization: 'Optimization',
  anomaly: 'Anomaly Detection',
};

const SECTION_COLORS = {
  prediction: 'border-pulse-500/30',
  actions: 'border-yellow-500/30',
  optimization: 'border-green-500/30',
  anomaly: 'border-red-500/30',
};

export default React.memo(function XAIPanel({ xai }) {
  const [expanded, setExpanded] = useState(true);

  if (!xai || !xai.summary || xai.summary.length === 0) {
    return (
      <div className="h-24 flex items-center justify-center text-gray-600 text-sm">
        Waiting for AI explanations...
      </div>
    );
  }

  const sections = ['prediction', 'actions', 'optimization', 'anomaly'].filter(
    (s) => xai[s] && xai[s].length > 0,
  );

  return (
    <div className="space-y-3">
      {/* Toggle */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-quantum-400 text-lg">💡</span>
          <span className="text-xs text-gray-400 uppercase tracking-wider">
            Explainable AI — Why these decisions?
          </span>
        </div>
        <button
          onClick={() => setExpanded((p) => !p)}
          className="text-xs text-gray-500 hover:text-white transition px-2 py-1 rounded bg-gray-800/50"
        >
          {expanded ? 'Collapse' : 'Expand'}
        </button>
      </div>

      {expanded && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {sections.map((section) => (
            <div
              key={section}
              className={`bg-gray-900/50 rounded-lg p-3 border-l-2 ${SECTION_COLORS[section]}`}
            >
              <div className="flex items-center gap-1.5 mb-2">
                <span>{SECTION_ICONS[section]}</span>
                <span className="text-[10px] text-gray-400 uppercase tracking-wider font-semibold">
                  {SECTION_LABELS[section]}
                </span>
              </div>
              <ul className="space-y-1">
                {xai[section].map((line, i) => (
                  <li key={i} className="text-xs text-gray-300 leading-relaxed">
                    {line}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
});
