import { useEffect, useRef, useState } from "react";
import ReconnectingWebSocket from "reconnecting-websocket";

export interface GovEvent {
  t: number;
  event: string;
  payload: any;
}

export function useGovEvents() {
  const [log, setLog] = useState<GovEvent[]>([]);
  const [connected, setConnected] = useState<boolean>(false);
  // Initialize with null to make it explicit
  const wsRef = useRef<ReconnectingWebSocket | null>(null);

  useEffect(() => {
    // Close any existing connection before creating a new one
    if (wsRef.current) {
      wsRef.current.close();
    }

    console.log("Initializing WebSocket connection...");

    // Get the token from environment variables
    const TOKEN = import.meta.env.VITE_ETERNA_TOKEN;
    if (!TOKEN) {
      console.warn("VITE_ETERNA_TOKEN is not set. WebSocket authentication may fail.");
    }

    // Get the WebSocket URL from environment variables or use default
    const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws";
    console.log("Using WebSocket URL:", WS_URL);

    // Create a new WebSocket connection with debug enabled
    const ws = new ReconnectingWebSocket(WS_URL, [], {
      debug: true,
      reconnectInterval: 3000,
    });
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("WebSocket connection established");
      setConnected(true);

      // Send authentication token when connection is established
      try {
        console.log("Sending authentication token...");
        ws.send(JSON.stringify({ token: TOKEN }));
      } catch (error) {
        console.error("Failed to send authentication token:", error);
      }

      // Add a test event to the log to verify it's working
      setLog(prev => [...prev, {
        t: Date.now() / 1000,
        event: "websocket_connected",
        payload: { status: "Connected to event stream" }
      }]);
    };

    ws.onmessage = (evt) => {
      try {
        console.log("Received WebSocket message:", evt.data);
        const data: GovEvent = JSON.parse(evt.data);
        setLog((prev) => [...prev.slice(-200), data]);
      } catch (error) {
        console.error("Failed to parse WebSocket message:", error);
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      setConnected(false);
    };

    ws.onclose = () => {
      console.log("WebSocket connection closed");
      setConnected(false);
    };

    // Cleanup function
    return () => {
      console.log("Cleaning up WebSocket connection");
      ws.close();
      wsRef.current = null;
    };
  }, []);

  // If not connected and no logs, show a connection status message
  if (!connected && log.length === 0) {
    return [{
      t: Date.now() / 1000,
      event: "websocket_status",
      payload: { status: "Connecting to event stream..." }
    }];
  }

  return log;
}
