import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
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
    return (_jsxs("div", { className: "border rounded-xl shadow bg-black text-green-300", role: "log", "aria-labelledby": "console-log-heading", children: [_jsxs("div", { className: "flex justify-between items-center p-2 border-b border-gray-700", children: [_jsx("h2", { className: "text-sm font-mono", id: "console-log-heading", children: "Console Log" }), _jsx("button", { className: "md:hidden px-2 py-1 bg-gray-800 rounded text-xs focus:outline-none focus:ring-2 focus:ring-blue-500", onClick: () => setIsExpanded(!isExpanded), "aria-expanded": isExpanded, "aria-controls": "log-content-mobile", "aria-label": isExpanded ? "Collapse log" : "Expand log", children: isExpanded ? "Collapse" : "Expand" })] }), _jsx("div", { className: "hidden md:block", role: "region", "aria-label": "Full event log", children: _jsx(VirtualList, { items: log.filter(e => e.event !== "checkpoint_saved" && e.event !== "checkpoint_scheduled"), renderItem: (e) => (_jsxs("div", { className: "py-1", children: ["[", new Date(e.t * 1000).toLocaleTimeString(), "] ", e.event, e.payload ? " → " + JSON.stringify(e.payload) : ""] })), itemHeight: 24, height: 240, className: "p-4 text-xs", ariaLabel: "Virtualized event log" }) }), _jsxs("div", { className: "md:hidden", id: "log-content-mobile", children: [_jsxs("div", { className: "p-2 text-xs border-b border-gray-700", "aria-label": "Recent events", tabIndex: 0, children: [_jsx("div", { className: "font-bold mb-1", children: "Recent Events:" }), recentLogs.map((e, i) => (_jsxs("div", { className: "truncate", children: ["[", new Date(e.t * 1000).toLocaleTimeString(), "] ", e.event] }, i)))] }), isExpanded && (_jsx("div", { className: "p-2 text-xs max-h-80 overflow-y-auto", "aria-label": "All events grouped by type", children: Object.entries(groupedLogs).map(([eventType, events]) => (_jsxs("details", { className: "mb-2", children: [_jsxs("summary", { className: "cursor-pointer font-bold focus:outline-none focus:ring-2 focus:ring-blue-500", tabIndex: 0, "aria-label": `${eventType} events, ${events.length} entries`, children: [eventType, " (", events.length, ")"] }), _jsx("div", { className: "pl-2 mt-1 border-l border-gray-700", "aria-label": `${eventType} event details`, children: _jsx(VirtualList, { items: events, renderItem: (e) => (_jsxs("div", { className: "mb-1", children: ["[", new Date(e.t * 1000).toLocaleTimeString(), "]", e.payload ? " → " + JSON.stringify(e.payload) : ""] })), itemHeight: 24, height: Math.min(events.length * 24, 200), className: "overflow-y-auto", ariaLabel: `${eventType} event details` }) })] }, eventType))) }))] })] }));
}
