import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { sendCommand, rollbackTo, sendReward, getQuantumBits } from "../api";
import { useErrorHandler } from "../utils/errorHandling";
import { useState } from "react";
import { useNotification } from "../contexts/NotificationContext";
// Icons for buttons
const icons = {
    play: "▶️",
    pause: "⏸️",
    step: "⏭️",
    reset: "🔄",
    emergency: "🛑",
    reward: "👍",
    punish: "👎"
};
export default function ControlPanel() {
    // Default companion name or get it from somewhere else if needed
    const companionName = "default";
    const { withErrorHandling } = useErrorHandler();
    const { addNotification } = useNotification();
    const [isLoading, setIsLoading] = useState({});
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const handleObserveOracle = withErrorHandling(async () => {
        var _a;
        setIsLoading(prev => ({ ...prev, observe: true }));
        try {
            const res = await getQuantumBits(128);
            if (res) {
                const preview = ((_a = res.bits) === null || _a === void 0 ? void 0 : _a.slice(0, 16)) || "";
                addNotification({
                    type: 'success',
                    message: `Observed oracle → backend=${res.backend}, H≈${res.entropy.toFixed(3)}, bits=${preview}…`,
                    duration: 5000,
                });
            }
        }
        finally {
            setIsLoading(prev => ({ ...prev, observe: false }));
        }
    }, "Failed to observe oracle");
    // Wrap API calls with error handling
    const handleSendCommand = withErrorHandling(async (action) => {
        setIsLoading({ ...isLoading, [action]: true });
        try {
            await sendCommand(action);
        }
        finally {
            setIsLoading({ ...isLoading, [action]: false });
        }
    }, "Failed to send command");
    const handleRollback = withErrorHandling(async () => {
        setIsLoading({ ...isLoading, rollback: true });
        try {
            await rollbackTo();
        }
        finally {
            setIsLoading({ ...isLoading, rollback: false });
        }
    }, "Failed to rollback");
    const handleSendReward = withErrorHandling(async (value) => {
        const rewardType = value > 0 ? "positive" : "negative";
        setIsLoading({ ...isLoading, [rewardType]: true });
        try {
            await sendReward(companionName, value);
        }
        finally {
            setIsLoading({ ...isLoading, [rewardType]: false });
        }
    }, "Failed to send reward");
    // Handle emergency stop
    const handleEmergencyStop = withErrorHandling(async () => {
        setIsLoading({ ...isLoading, emergency: true });
        try {
            // Call the AlignmentGovernor.shutdown() method via the API
            await sendCommand("emergency_shutdown");
        }
        finally {
            setIsLoading({ ...isLoading, emergency: false });
        }
    }, "Failed to execute emergency shutdown");
    return (_jsxs("div", { className: "p-4 border rounded-xl shadow bg-white", role: "region", "aria-labelledby": "controls-heading", children: [_jsxs("div", { className: "flex justify-between items-center mb-4", children: [_jsx("h2", { className: "font-semibold", id: "controls-heading", children: "Controls" }), _jsx("button", { className: "md:hidden px-2 py-1 rounded bg-slate-800 text-white focus:outline-none focus:ring-2 focus:ring-blue-500", onClick: () => setIsMenuOpen(!isMenuOpen), "aria-expanded": isMenuOpen, "aria-controls": "control-panel-content", "aria-label": isMenuOpen ? "Hide controls" : "Show controls", children: isMenuOpen ? "Hide Controls" : "Show Controls" })] }), _jsxs("div", { id: "control-panel-content", className: `${isMenuOpen ? 'block' : 'hidden'} md:block`, "aria-hidden": !isMenuOpen && window.innerWidth < 768, children: [_jsxs("div", { className: "mb-4", children: [_jsx("h3", { className: "text-sm font-medium mb-2 text-gray-700", children: "Simulation Control" }), _jsxs("div", { className: "flex gap-2 flex-wrap", role: "toolbar", "aria-label": "Simulation controls", children: [_jsxs("button", { onClick: () => handleSendCommand("resume"), className: "flex items-center px-3 py-2 rounded bg-green-600 text-white text-sm hover:bg-green-700 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-green-500", disabled: isLoading.resume, "aria-busy": isLoading.resume, "aria-label": `Run simulation${isLoading.resume ? ', loading' : ''}`, children: [_jsx("span", { className: "mr-1", children: icons.play }), isLoading.resume ? "..." : "Run"] }), _jsxs("button", { onClick: () => handleSendCommand("pause"), className: "flex items-center px-3 py-2 rounded bg-yellow-600 text-white text-sm hover:bg-yellow-700 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-yellow-500", disabled: isLoading.pause, "aria-busy": isLoading.pause, "aria-label": `Pause simulation${isLoading.pause ? ', loading' : ''}`, children: [_jsx("span", { className: "mr-1", children: icons.pause }), isLoading.pause ? "..." : "Pause"] }), _jsxs("button", { onClick: () => handleSendCommand("step"), className: "flex items-center px-3 py-2 rounded bg-blue-600 text-white text-sm hover:bg-blue-700 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-blue-500", disabled: isLoading.step, "aria-busy": isLoading.step, "aria-label": `Step simulation${isLoading.step ? ', loading' : ''}`, children: [_jsx("span", { className: "mr-1", children: icons.step }), isLoading.step ? "..." : "Step"] }), _jsxs("button", { onClick: () => handleSendCommand("reset"), className: "flex items-center px-3 py-2 rounded bg-gray-600 text-white text-sm hover:bg-gray-700 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-gray-500", disabled: isLoading.reset, "aria-busy": isLoading.reset, "aria-label": `Reset simulation${isLoading.reset ? ', loading' : ''}`, children: [_jsx("span", { className: "mr-1", children: icons.reset }), isLoading.reset ? "..." : "Reset"] })] })] }), _jsxs("div", { className: "mb-4", children: [_jsx("h3", { className: "text-sm font-medium mb-2 text-gray-700", children: "Emergency Controls" }), _jsxs("div", { className: "flex gap-2", role: "toolbar", "aria-label": "Emergency controls", children: [_jsxs("button", { onClick: handleEmergencyStop, className: "flex items-center px-3 py-2 rounded bg-red-600 text-white text-sm hover:bg-red-700 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-red-500", disabled: isLoading.emergency, "aria-busy": isLoading.emergency, "aria-label": `Emergency Stop${isLoading.emergency ? ', loading' : ''}`, children: [_jsx("span", { className: "mr-1", children: icons.emergency }), isLoading.emergency ? "..." : "Emergency Stop"] }), _jsxs("button", { onClick: handleRollback, className: "flex items-center px-3 py-2 rounded bg-purple-600 text-white text-sm hover:bg-purple-700 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-purple-500", disabled: isLoading.rollback, "aria-busy": isLoading.rollback, "aria-label": `Rollback simulation${isLoading.rollback ? ', loading' : ''}`, children: [_jsx("span", { className: "mr-1", children: "\u23EA" }), isLoading.rollback ? "..." : "Rollback"] })] })] }), _jsxs("div", { children: [_jsx("h3", { className: "text-sm font-medium mb-2 text-gray-700", children: "Feedback Controls" }), _jsxs("div", { className: "flex gap-2", role: "toolbar", "aria-label": "Feedback controls", children: [_jsxs("button", { onClick: () => handleSendReward(1), className: "flex items-center px-3 py-2 bg-green-600 text-white rounded disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-green-500", disabled: isLoading.positive, "aria-busy": isLoading.positive, "aria-label": `Positive reward${isLoading.positive ? ', loading' : ''}`, children: [_jsx("span", { className: "mr-1", children: icons.reward }), isLoading.positive ? "..." : "Positive"] }), _jsxs("button", { onClick: () => handleSendReward(-1), className: "flex items-center px-3 py-2 bg-red-600 text-white rounded disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-red-500", disabled: isLoading.negative, "aria-busy": isLoading.negative, "aria-label": `Negative reward${isLoading.negative ? ', loading' : ''}`, children: [_jsx("span", { className: "mr-1", children: icons.punish }), isLoading.negative ? "..." : "Negative"] })] })] }), _jsxs("div", { className: "mt-4", children: [_jsx("h3", { className: "text-sm font-medium mb-2 text-gray-700", children: "Quantum" }), _jsx("div", { className: "flex gap-2", role: "toolbar", "aria-label": "Quantum controls", children: _jsxs("button", { onClick: handleObserveOracle, className: "flex items-center px-3 py-2 rounded bg-indigo-600 text-white text-sm hover:bg-indigo-700 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-indigo-500", disabled: isLoading.observe, "aria-busy": isLoading.observe, "aria-label": `Observe Oracle${isLoading.observe ? ', loading' : ''}`, children: [_jsx("span", { className: "mr-1", children: "\uD83C\uDF00" }), isLoading.observe ? "..." : "Observe Oracle"] }) })] }), _jsx("div", { className: "mt-4 text-xs text-gray-500", children: _jsx("p", { children: "Keyboard shortcuts: Space = Pause/Resume, S = Step" }) })] })] }));
}
