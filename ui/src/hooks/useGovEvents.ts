import { useEffect, useRef, useState } from "react";
import ReconnectingWebSocket from "reconnecting-websocket";

export interface GovEvent {
  t: number;
  event: string;
  payload: any;
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

  const ws = new ReconnectingWebSocket("ws://localhost:8000/ws");
  wsRef.current = ws;

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