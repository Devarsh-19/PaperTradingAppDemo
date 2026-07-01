import { useEffect, useRef, useState } from 'react';
import { useAuthStore } from '../stores/authStore';

type WebSocketEvent = 'price_update' | 'order_update' | 'portfolio_update';

interface WebSocketMessage {
  event: WebSocketEvent;
  data: any;
}

export const useWebSocket = () => {
  const { token } = useAuthStore();
  const wsRef = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const subscribersRef = useRef<Record<string, Set<(data: any) => void>>>({
    price_update: new Set(),
    order_update: new Set(),
    portfolio_update: new Set(),
  });

  useEffect(() => {
    if (!token) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = import.meta.env.VITE_API_URL ? new URL(import.meta.env.VITE_API_URL).host : window.location.host;
    
    // Nginx routes /ws/prices to the backend
    const wsUrl = import.meta.env.VITE_API_URL 
        ? `${protocol}//${host}/ws/prices?token=${token}`
        : `ws://localhost:8000/ws/prices?token=${token}`;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
      // Basic reconnect could be added here
    };

    ws.onmessage = (event) => {
      try {
        const msg: WebSocketMessage = JSON.parse(event.data);
        if (msg.event && subscribersRef.current[msg.event]) {
          subscribersRef.current[msg.event].forEach((cb) => cb(msg.data));
        }
      } catch (err) {
        console.error('Failed to parse WS message', err);
      }
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
        ws.close();
      }
    };
  }, [token]);

  const subscribe = (event: WebSocketEvent, callback: (data: any) => void) => {
    if (!subscribersRef.current[event]) {
      subscribersRef.current[event] = new Set();
    }
    subscribersRef.current[event].add(callback);
    return () => {
      subscribersRef.current[event].delete(callback);
    };
  };

  const subscribeToSymbols = (symbols: string[]) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'subscribe', symbols }));
    }
  };

  const unsubscribeFromSymbols = (symbols: string[]) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'unsubscribe', symbols }));
    }
  };

  return {
    isConnected,
    subscribe,
    subscribeToSymbols,
    unsubscribeFromSymbols,
  };
};
