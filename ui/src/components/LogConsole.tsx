import { useGovEvents } from "../hooks/useGovEvents";
import { useEffect, useRef } from "react";

export default function LogConsole() {
  const log = useGovEvents();
  const logContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new logs are added
  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [log]);

  return (
    <div 
      ref={logContainerRef}
      className="p-4 border rounded-xl shadow bg-black text-green-300 text-xs h-60 overflow-y-auto"
    >
      {log.length === 0 ? (
        <div className="text-yellow-300 italic">
          No events to display. Waiting for events...
        </div>
      ) : (
        log.map((e, i) => {
          // Skip certain events that would clutter the log
          if (e.event === "checkpoint_saved" || e.event === "checkpoint_scheduled") return null;

          // Special handling for status messages
          if (e.event === "websocket_status" || e.event === "websocket_connected") {
            return (
              <div key={i} className="text-yellow-300 italic">
                [{new Date(e.t * 1000).toLocaleTimeString()}] {e.payload?.status || e.event}
              </div>
            );
          }

          // Regular event display
          return (
            <div key={i}>
              [{new Date(e.t * 1000).toLocaleTimeString()}] {e.event}
              {e.payload ? " → " + JSON.stringify(e.payload) : ""}
            </div>
          );
        })
      )}
    </div>
  );
}
