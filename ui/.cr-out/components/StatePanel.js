import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useWorldState } from "../contexts/WorldStateContext";
import { memo, useState } from "react";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
// Custom tooltip component for charts
const CustomTooltip = ({ active, payload, label, tooltipText }) => {
    if (active && payload && payload.length) {
        return (_jsxs("div", { className: "bg-white p-2 border border-gray-200 shadow-md rounded text-sm", children: [_jsx("p", { className: "font-semibold", children: `${label}: ${payload[0].value}` }), _jsx("p", { className: "text-xs text-gray-600", children: tooltipText })] }));
    }
    return null;
};
const StatePanel = () => {
    var _a, _b, _c;
    const { state } = useWorldState();
    const { worldState, isLoading, error } = state;
    // State for historical data (in a real app, this would come from an API)
    const [cycleHistory] = useState(() => {
        // Generate some sample data for demonstration
        return Array.from({ length: 10 }, (_, i) => ({
            time: i,
            value: Math.floor(Math.random() * 20) + 1
        }));
    });
    const [continuityHistory] = useState(() => {
        // Generate some sample data for demonstration
        return Array.from({ length: 10 }, (_, i) => ({
            time: i,
            value: (Math.random() * 0.5 + 0.5).toFixed(3)
        }));
    });
    if (error) {
        return (_jsxs("div", { className: "p-4 border rounded-xl shadow bg-white", children: [_jsx("h2", { className: "font-semibold mb-2", children: "World State" }), _jsx("div", { className: "text-red-500", children: "Error loading state. Please try refreshing." })] }));
    }
    if (isLoading || !worldState) {
        return (_jsxs("div", { className: "p-4 border rounded-xl shadow bg-white", children: [_jsx("h2", { className: "font-semibold mb-2", children: "World State" }), _jsx("div", { className: "text-gray-500", children: "Loading state\u2026" })] }));
    }
    // Update history with current values (in a real app, this would be handled differently)
    if (worldState) {
        cycleHistory.push({ time: cycleHistory.length, value: worldState.cycle });
        if (cycleHistory.length > 10)
            cycleHistory.shift();
        continuityHistory.push({ time: continuityHistory.length, value: worldState.identity_score.toFixed(3) });
        if (continuityHistory.length > 10)
            continuityHistory.shift();
    }
    return (_jsxs("div", { className: "p-4 border rounded-xl shadow bg-white", role: "region", "aria-labelledby": "world-state-heading", children: [_jsxs("div", { className: "flex justify-between items-center mb-2", children: [_jsx("h2", { className: "font-semibold", id: "world-state-heading", children: "World State" }), _jsxs("div", { className: "md:hidden flex items-center space-x-2", "aria-label": "Critical world state information", children: [_jsxs("span", { className: "px-2 py-1 bg-blue-100 rounded text-xs", "aria-label": `Cycle: ${worldState.cycle}`, children: ["Cycle: ", worldState.cycle] }), _jsx("span", { className: `px-2 py-1 rounded text-xs emotion-badge-small emotion-${(worldState.emotion || 'neutral').toLowerCase()}`, "aria-label": `Emotion: ${(_a = worldState.emotion) !== null && _a !== void 0 ? _a : "Neutral"}`, children: (_b = worldState.emotion) !== null && _b !== void 0 ? _b : "Neutral" })] })] }), _jsxs("div", { className: "hidden md:block space-y-4", "aria-label": "World state details", children: [_jsxs("div", { className: "mb-4", children: [_jsxs("h3", { className: "text-sm font-medium mb-1 flex items-center", children: ["Cycle Progress", _jsx("span", { className: "ml-2 text-xs bg-blue-100 px-2 py-0.5 rounded-full", children: worldState.cycle }), _jsxs("div", { className: "relative group ml-2", children: [_jsx("span", { className: "cursor-help text-gray-400", children: "\u24D8" }), _jsx("div", { className: "absolute left-0 bottom-full mb-2 hidden group-hover:block bg-white p-2 rounded shadow-lg border border-gray-200 text-xs w-48 z-10", children: "Cycles represent discrete time steps in the simulation. Higher values indicate more processing has occurred." })] })] }), _jsx("div", { className: "h-24 w-full", children: _jsx(ResponsiveContainer, { width: "100%", height: "100%", children: _jsxs(BarChart, { data: cycleHistory, children: [_jsx(XAxis, { dataKey: "time", tick: false }), _jsx(YAxis, {}), _jsx(Tooltip, { content: _jsx(CustomTooltip, { tooltipText: "Number of processing cycles completed" }) }), _jsx(Bar, { dataKey: "value", fill: "#3b82f6", name: "Cycle" })] }) }) })] }), _jsxs("div", { className: "mb-4", children: [_jsxs("h3", { className: "text-sm font-medium mb-1 flex items-center", children: ["Identity Continuity", _jsx("span", { className: "ml-2 text-xs bg-green-100 px-2 py-0.5 rounded-full", children: worldState.identity_score.toFixed(3) }), _jsxs("div", { className: "relative group ml-2", children: [_jsx("span", { className: "cursor-help text-gray-400", children: "\u24D8" }), _jsx("div", { className: "absolute left-0 bottom-full mb-2 hidden group-hover:block bg-white p-2 rounded shadow-lg border border-gray-200 text-xs w-48 z-10", children: "Identity continuity measures how consistent the system's behavior is over time. Higher values indicate greater stability." })] })] }), _jsx("div", { className: "h-24 w-full", children: _jsx(ResponsiveContainer, { width: "100%", height: "100%", children: _jsxs(LineChart, { data: continuityHistory, children: [_jsx(XAxis, { dataKey: "time", tick: false }), _jsx(YAxis, { domain: [0, 1] }), _jsx(Tooltip, { content: _jsx(CustomTooltip, { tooltipText: "Measure of system stability and coherence" }) }), _jsx(Line, { type: "monotone", dataKey: "value", stroke: "#10b981", name: "Continuity", dot: false })] }) }) })] }), _jsxs("div", { className: "grid grid-cols-2 gap-2 text-sm", children: [_jsxs("div", { className: "flex items-center", children: [_jsx("span", { className: "mr-1", children: "Emotion:" }), _jsx("span", { className: `px-2 py-0.5 rounded text-xs emotion-badge emotion-${(worldState.emotion || 'neutral').toLowerCase()}`, children: (_c = worldState.emotion) !== null && _c !== void 0 ? _c : "Neutral" }), _jsxs("div", { className: "relative group ml-2", children: [_jsx("span", { className: "cursor-help text-gray-400", children: "\u24D8" }), _jsx("div", { className: "absolute left-0 bottom-full mb-2 hidden group-hover:block bg-white p-2 rounded shadow-lg border border-gray-200 text-xs w-48 z-10", children: "Current emotional state of the system, influencing behavior and zone characteristics." })] })] }), _jsxs("div", { className: "flex items-center", children: [_jsx("span", { className: "mr-1", children: "Modifiers:" }), _jsx("span", { className: "text-xs bg-purple-100 px-2 py-0.5 rounded-full", children: Object.keys(worldState.modifiers).length }), _jsxs("div", { className: "relative group ml-2", children: [_jsx("span", { className: "cursor-help text-gray-400", children: "\u24D8" }), _jsx("div", { className: "absolute left-0 bottom-full mb-2 hidden group-hover:block bg-white p-2 rounded shadow-lg border border-gray-200 text-xs w-48 z-10", children: "Active modifiers affecting zones and system behavior." })] })] })] }), state.lastUpdated && (_jsxs("div", { className: "text-xs text-gray-500 mt-2", children: ["Last updated: ", new Date(state.lastUpdated || 0).toLocaleTimeString()] }))] }), _jsx("div", { className: "md:hidden mt-2", children: _jsxs("details", { className: "text-sm", children: [_jsx("summary", { className: "cursor-pointer text-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500", "aria-label": "Show additional world state details", tabIndex: 0, children: "Show Details" }), _jsxs("div", { className: "mt-2 space-y-3 pl-2 border-l-2 border-blue-100", "aria-label": "Additional world state details", children: [_jsxs("div", { children: [_jsxs("div", { className: "text-xs font-medium mb-1", children: ["Cycle: ", worldState.cycle] }), _jsx("div", { className: "h-16 w-full", children: _jsx(ResponsiveContainer, { width: "100%", height: "100%", children: _jsx(BarChart, { data: cycleHistory.slice(-5), children: _jsx(Bar, { dataKey: "value", fill: "#3b82f6" }) }) }) })] }), _jsxs("div", { children: [_jsxs("div", { className: "text-xs font-medium mb-1", children: ["Identity Score: ", worldState.identity_score.toFixed(3)] }), _jsx("div", { className: "h-16 w-full", children: _jsx(ResponsiveContainer, { width: "100%", height: "100%", children: _jsx(LineChart, { data: continuityHistory.slice(-5), children: _jsx(Line, { type: "monotone", dataKey: "value", stroke: "#10b981", dot: false }) }) }) })] }), _jsxs("div", { children: ["Modifiers: ", Object.keys(worldState.modifiers).length] }), state.lastUpdated && (_jsxs("div", { className: "text-xs text-gray-500", children: ["Last updated: ", new Date(state.lastUpdated || 0).toLocaleTimeString()] }))] })] }) })] }));
};
export default memo(StatePanel);
