import { useEffect, useRef, useState } from "react";
import ReconnectingWebSocket from "reconnecting-websocket";

export interface GovEvent {
  t: number;
  event: string;
  payload: unknown;
}

export function useGovEvents() {
  const [log, setLog] = useState<GovEvent[]>([]);
  // Initialize with null to make it explicit
  const wsRef = useRef<ReconnectingWebSocket | null>(null);

  useEffect(() => {
    // Close any existing connection before creating a new one
    if (wsRef.current) {
      wsRef.current.close();
    }

    const TOKEN = import.meta.env.VITE_ETERNA_TOKEN;
    // Use the same API URL environment variable as in api.ts, but convert to WebSocket URL
    const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
    // Convert HTTP URL to WebSocket URL (replace http:// with ws:// or https:// with wss://)
    const wsUrl = apiUrl.replace(/^http/, 'ws') + "/ws";
    console.log("Connecting to WebSocket at:", wsUrl);
    const ws = new ReconnectingWebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      // Send authentication token when connection is established
      ws.send(JSON.stringify({ token: TOKEN }));
    };

    ws.onmessage = (evt) => {
      try {
        const data: GovEvent = JSON.parse(evt.data);
        setLog((prev) => [...prev.slice(-200), data]);
      } catch (error) {
        console.error("Failed to parse WebSocket message:", error);
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, []);

  return log;
}
