import { useGovEvents } from "../hooks/useGovEvents";
import { useState } from "react";
import { VirtualList } from "./ui/VirtualList";

export default function LogConsole() {
  const log = useGovEvents();
  const [isExpanded, setIsExpanded] = useState(false);

  // Group logs by event type for collapsible sections
  const groupedLogs = log.reduce((groups, event) => {
    // Skip certain events
    if (event.event === "checkpoint_saved" || event.event === "checkpoint_scheduled") {
      return groups;
    }

    // Create a group if it doesn't exist
    if (!groups[event.event]) {
      groups[event.event] = [];
    }

    // Add the event to its group
    groups[event.event].push(event);

    return groups;
  }, {});

  // Get the most recent log entries (up to 5) for the collapsed mobile view
  const recentLogs = [...log]
    .filter(e => e.event !== "checkpoint_saved" && e.event !== "checkpoint_scheduled")
    .sort((a, b) => b.t - a.t)
    .slice(0, 5);

  return (
    <div className="border rounded-xl shadow bg-black text-green-300" role="log" aria-labelledby="console-log-heading">
      {/* Header with toggle button for mobile */}
      <div className="flex justify-between items-center p-2 border-b border-gray-700">
        <h2 className="text-sm font-mono" id="console-log-heading">Console Log</h2>
        <button 
          className="md:hidden px-2 py-1 bg-gray-800 rounded text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
          onClick={() => setIsExpanded(!isExpanded)}
          aria-expanded={isExpanded}
          aria-controls="log-content-mobile"
          aria-label={isExpanded ? "Collapse log" : "Expand log"}
        >
          {isExpanded ? "Collapse" : "Expand"}
        </button>
      </div>

      {/* Desktop view - full log with virtualized list */}
      <div 
        className="hidden md:block" 
        role="region" 
        aria-label="Full event log"
      >
        <VirtualList
          items={log.filter(e => e.event !== "checkpoint_saved" && e.event !== "checkpoint_scheduled")}
          renderItem={(e) => (
            <div className="py-1">
              [{new Date(e.t * 1000).toLocaleTimeString()}] {e.event}
              {e.payload ? " → " + JSON.stringify(e.payload) : ""}
            </div>
          )}
          itemHeight={24} // Approximate height of each log entry
          height={240} // Same as h-60 (15rem = 240px)
          className="p-4 text-xs"
          ariaLabel="Virtualized event log"
        />
      </div>

      {/* Mobile view - collapsed by default with recent logs */}
      <div className="md:hidden" id="log-content-mobile">
        {/* Recent logs (always visible) */}
        <div 
          className="p-2 text-xs border-b border-gray-700" 
          aria-label="Recent events"
          tabIndex={0}
        >
          <div className="font-bold mb-1">Recent Events:</div>
          {recentLogs.map((e, i) => (
            <div key={i} className="truncate">
              [{new Date(e.t * 1000).toLocaleTimeString()}] {e.event}
            </div>
          ))}
        </div>

        {/* Expandable full log with collapsible sections by event type */}
        {isExpanded && (
          <div 
            className="p-2 text-xs max-h-80 overflow-y-auto" 
            aria-label="All events grouped by type"
          >
            {Object.entries(groupedLogs).map(([eventType, events]) => (
              <details key={eventType} className="mb-2">
                <summary 
                  className="cursor-pointer font-bold focus:outline-none focus:ring-2 focus:ring-blue-500"
                  tabIndex={0}
                  aria-label={`${eventType} events, ${events.length} entries`}
                >
                  {eventType} ({events.length})
                </summary>
                <div 
                  className="pl-2 mt-1 border-l border-gray-700" 
                  aria-label={`${eventType} event details`}
                >
                  <VirtualList
                    items={events}
                    renderItem={(e) => (
                      <div className="mb-1">
                        [{new Date(e.t * 1000).toLocaleTimeString()}]
                        {e.payload ? " → " + JSON.stringify(e.payload) : ""}
                      </div>
                    )}
                    itemHeight={24} // Approximate height of each log entry
                    height={Math.min(events.length * 24, 200)} // Max height of 200px or less if fewer items
                    className="overflow-y-auto"
                    ariaLabel={`${eventType} event details`}
                  />
                </div>
              </details>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
