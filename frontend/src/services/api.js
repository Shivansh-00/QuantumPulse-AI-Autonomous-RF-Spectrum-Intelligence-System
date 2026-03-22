const API_BASE = '/api';

async function request(endpoint, options = {}) {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json();
}

export const api = {
  // RF Simulation
  simulate: (params) =>
    request('/rf/simulate', { method: 'POST', body: JSON.stringify(params) }),

  quickSim: () => request('/rf/quick-sim'),

  analyze: (signal, sampleRate) =>
    request('/rf/analyze', {
      method: 'POST',
      body: JSON.stringify({ signal, sample_rate: sampleRate }),
    }),

  // AI Prediction
  predict: (signalData, modelType = 'lstm') =>
    request('/predict/congestion', {
      method: 'POST',
      body: JSON.stringify({ signal_data: signalData, model_type: modelType }),
    }),

  trainModel: (modelType = 'lstm', epochs = 20) =>
    request(`/predict/train?model_type=${encodeURIComponent(modelType)}&epochs=${epochs}`, {
      method: 'POST',
    }),

  // Optimization
  optimize: (signalConfigs, bandOccupancy = null) =>
    request('/optimize/frequency', {
      method: 'POST',
      body: JSON.stringify({
        signal_configs: signalConfigs,
        band_occupancy: bandOccupancy,
      }),
    }),

  // Autonomous
  autonomousStatus: () => request('/autonomous/status'),

  // Scenarios
  listScenarios: () => request('/features/scenarios'),
  getScenario: (id) => request(`/features/scenarios/${encodeURIComponent(id)}`),

  // AI Assistant
  askAssistant: (question) =>
    request('/features/assistant/ask', {
      method: 'POST',
      body: JSON.stringify({ question }),
    }),

  // Health
  health: () => request('/health'),
};
