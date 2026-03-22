import React, { useState, useRef, useEffect } from 'react';
import { api } from '../services/api';

const QUICK_QUESTIONS = [
  'Why did you change frequency?',
  'Any anomalies detected?',
  'How busy is the spectrum?',
  'What is the current mode?',
  'Show performance metrics',
];

export default function AIAssistantPanel() {
  const [messages, setMessages] = useState([
    { role: 'ai', text: 'Hello! I\'m your RF spectrum assistant. Ask me anything about the system\'s decisions, anomalies, or performance.' },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async (question) => {
    const q = (question || input).trim();
    if (!q || loading) return;

    setMessages((prev) => [...prev, { role: 'user', text: q }]);
    setInput('');
    setLoading(true);

    try {
      const res = await api.askAssistant(q);
      setMessages((prev) => [...prev, { role: 'ai', text: res.answer || 'System is operational. All modules running normally.' }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'ai', text: 'The system is still running. The assistant is temporarily unable to reach the server — I\'ll be back shortly!' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto space-y-2 mb-3 pr-1 max-h-64"
      >
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[85%] px-3 py-2 rounded-lg text-xs leading-relaxed ${
                m.role === 'user'
                  ? 'bg-quantum-600/20 text-quantum-200 border border-quantum-500/20'
                  : 'bg-gray-800/70 text-gray-300 border border-gray-700/30'
              }`}
            >
              {m.role === 'ai' && <span className="text-quantum-400 font-bold mr-1">AI:</span>}
              {m.text}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-800/70 text-gray-500 text-xs px-3 py-2 rounded-lg border border-gray-700/30">
              <span className="animate-pulse">Thinking...</span>
            </div>
          </div>
        )}
      </div>

      {/* Quick questions */}
      <div className="flex flex-wrap gap-1.5 mb-2">
        {QUICK_QUESTIONS.map((q) => (
          <button
            key={q}
            onClick={() => handleSend(q)}
            disabled={loading}
            className="px-2 py-1 rounded text-[10px] bg-gray-800/80 text-gray-400 hover:text-white
                       hover:bg-gray-700/80 transition border border-gray-700/30 disabled:opacity-50"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about the system..."
          disabled={loading}
          className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-xs text-white
                     placeholder-gray-600 focus:outline-none focus:border-quantum-500 disabled:opacity-50"
        />
        <button
          onClick={() => handleSend()}
          disabled={loading || !input.trim()}
          className="px-4 py-2 rounded-lg bg-quantum-600 text-white text-xs font-medium
                     hover:bg-quantum-500 transition disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Send
        </button>
      </div>
    </div>
  );
}
