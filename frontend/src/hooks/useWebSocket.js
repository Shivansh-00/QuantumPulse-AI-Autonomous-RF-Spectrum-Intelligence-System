import { useState, useEffect, useRef, useCallback } from 'react';

const MAX_RECONNECT_DELAY = 30000;
const BASE_RECONNECT_DELAY = 1000;

/**
 * Custom hook for WebSocket connection to the RF streaming pipeline.
 * Features: exponential backoff reconnect, connection quality tracking,
 * requestAnimationFrame-throttled state updates to prevent render thrashing.
 */
export function useWebSocket(url) {
  const [data, setData] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const [reconnectAttempt, setReconnectAttempt] = useState(0);
  const wsRef = useRef(null);
  const reconnectTimer = useRef(null);
  const attemptRef = useRef(0);
  const rafRef = useRef(null);
  const latestDataRef = useRef(null);
  const wasConnectedRef = useRef(false);
  const mountedRef = useRef(true);

  const connect = useCallback(() => {
    // Clean up any existing connection
    if (wsRef.current) {
      try { wsRef.current.close(); } catch { /* ignore */ }
    }

    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = url || `${protocol}//${window.location.host}/ws/stream`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        if (!mountedRef.current) return;
        setIsConnected(true);
        setError(null);
        attemptRef.current = 0;
        setReconnectAttempt(0);
        wasConnectedRef.current = true;
      };

      ws.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          if (parsed && typeof parsed === 'object') {
            // Throttle: buffer the latest message and flush once per animation frame
            latestDataRef.current = parsed;
            if (!rafRef.current) {
              rafRef.current = requestAnimationFrame(() => {
                rafRef.current = null;
                if (latestDataRef.current) {
                  setData(latestDataRef.current);
                }
              });
            }
          }
        } catch {
          // ignore malformed messages
        }
      };

      ws.onerror = () => {
        if (!mountedRef.current) return;
        setError('WebSocket connection error');
        setIsConnected(false);
      };

      ws.onclose = (event) => {
        if (!mountedRef.current) return;
        setIsConnected(false);

        // Normal closure (code 1000) or component unmount — don't reconnect
        if (event.code === 1000) return;

        // Only show reconnect attempt if we had a successful connection before
        if (wasConnectedRef.current) {
          attemptRef.current += 1;
          setReconnectAttempt(attemptRef.current);
        }

        // Exponential backoff: 1s, 2s, 4s, 8s, ... capped at 30s
        const delay = Math.min(
          BASE_RECONNECT_DELAY * Math.pow(2, attemptRef.current),
          MAX_RECONNECT_DELAY,
        );
        reconnectTimer.current = setTimeout(connect, delay);
      };

      wsRef.current = ws;
    } catch (err) {
      setError(err.message);
    }
  }, [url]);

  const sendConfig = useCallback((config) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(config));
    }
  }, []);

  const disconnect = useCallback(() => {
    mountedRef.current = false;
    if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
    if (wsRef.current) wsRef.current.close(1000, 'unmount');
  }, []);

  useEffect(() => {
    mountedRef.current = true;
    connect();
    return disconnect;
  }, [connect, disconnect]);

  return { data, isConnected, error, sendConfig, disconnect, connect, reconnectAttempt };
}
