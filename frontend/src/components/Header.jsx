import React from 'react';

export default React.memo(function Header({ isConnected, latencyMs, learningCycles, reconnectAttempt }) {
  const latencyColor = latencyMs != null
    ? (latencyMs < 50 ? 'text-green-400' : latencyMs < 150 ? 'text-yellow-400' : 'text-red-400')
    : 'text-gray-500';

  return (
    <header className="flex items-center justify-between px-6 py-4 border-b border-gray-800/50 bg-gray-950/80 backdrop-blur-md sticky top-0 z-50">
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-quantum-500 to-pulse-500 flex items-center justify-center font-bold text-sm">
          QP
        </div>
        <div>
          <h1 className="text-lg font-bold tracking-tight">
            QuantumPulse <span className="text-quantum-400">AI</span>
          </h1>
          <p className="text-[11px] text-gray-500 -mt-0.5">
            Autonomous RF Spectrum Intelligence
          </p>
        </div>
      </div>

      <div className="flex items-center gap-5 text-xs">
        {/* Self-Learning Tag */}
        {learningCycles > 0 && (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-purple-900/30 border border-purple-500/20">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-400 opacity-60" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-purple-500" />
            </span>
            <span className="text-purple-300 font-medium">Self-Learning</span>
            <span className="text-purple-500">#{learningCycles}</span>
          </div>
        )}

        {/* Latency */}
        {latencyMs != null && (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-gray-800/60 border border-gray-700/30">
            <span className={`font-mono font-bold ${latencyColor}`}>{Math.round(latencyMs)}ms</span>
            <span className="text-gray-500">latency</span>
          </div>
        )}

        {/* Connection Status */}
        <div className="flex items-center gap-2">
          <span className={`status-dot ${isConnected ? 'live' : 'bg-red-500'}`} />
          <span className={isConnected ? 'text-green-400' : 'text-red-400'}>
            {isConnected ? 'LIVE STREAM' : reconnectAttempt > 0 ? 'RECONNECTING' : 'DISCONNECTED'}
          </span>
        </div>
      </div>
    </header>
  );
});
