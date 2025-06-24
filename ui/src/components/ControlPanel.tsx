import { sendCommand, rollbackTo, sendReward } from "../api";
import { useErrorHandler } from "../utils/errorHandling";
import { useState } from "react";

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
    const [isLoading, setIsLoading] = useState<Record<string, boolean>>({});
    const [isMenuOpen, setIsMenuOpen] = useState<boolean>(false);

    // Wrap API calls with error handling
    const handleSendCommand = withErrorHandling(async (action: string) => {
        setIsLoading({ ...isLoading, [action]: true });
        try {
            await sendCommand(action);
        } finally {
            setIsLoading({ ...isLoading, [action]: false });
        }
    }, "Failed to send command");

    const handleRollback = withErrorHandling(async () => {
        setIsLoading({ ...isLoading, rollback: true });
        try {
            await rollbackTo();
        } finally {
            setIsLoading({ ...isLoading, rollback: false });
        }
    }, "Failed to rollback");

    const handleSendReward = withErrorHandling(async (value: number) => {
        const rewardType = value > 0 ? "positive" : "negative";
        setIsLoading({ ...isLoading, [rewardType]: true });
        try {
            await sendReward(companionName, value);
        } finally {
            setIsLoading({ ...isLoading, [rewardType]: false });
        }
    }, "Failed to send reward");

    // Handle emergency stop
    const handleEmergencyStop = withErrorHandling(async () => {
        setIsLoading({ ...isLoading, emergency: true });
        try {
            // Call the AlignmentGovernor.shutdown() method via the API
            await sendCommand("emergency_shutdown");
        } finally {
            setIsLoading({ ...isLoading, emergency: false });
        }
    }, "Failed to execute emergency shutdown");

    return (
        <div className="p-4 border rounded-xl shadow bg-white" role="region" aria-labelledby="controls-heading">
            <div className="flex justify-between items-center mb-4">
                <h2 className="font-semibold" id="controls-heading">Controls</h2>
                {/* Mobile menu toggle button - only visible on small screens */}
                <button 
                    className="md:hidden px-2 py-1 rounded bg-slate-800 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    onClick={() => setIsMenuOpen(!isMenuOpen)}
                    aria-expanded={isMenuOpen}
                    aria-controls="control-panel-content"
                    aria-label={isMenuOpen ? "Hide controls" : "Show controls"}
                >
                    {isMenuOpen ? "Hide Controls" : "Show Controls"}
                </button>
            </div>

            {/* Controls - always visible on md+ screens, toggleable on small screens */}
            <div 
                id="control-panel-content"
                className={`${isMenuOpen ? 'block' : 'hidden'} md:block`}
                aria-hidden={!isMenuOpen && window.innerWidth < 768}
            >
                {/* Simulation Control Group */}
                <div className="mb-4">
                    <h3 className="text-sm font-medium mb-2 text-gray-700">Simulation Control</h3>
                    <div className="flex gap-2 flex-wrap" role="toolbar" aria-label="Simulation controls">
                        <button
                            onClick={() => handleSendCommand("resume")}
                            className="flex items-center px-3 py-2 rounded bg-green-600 text-white text-sm hover:bg-green-700 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-green-500"
                            disabled={isLoading.resume}
                            aria-busy={isLoading.resume}
                            aria-label={`Run simulation${isLoading.resume ? ', loading' : ''}`}
                        >
                            <span className="mr-1">{icons.play}</span>
                            {isLoading.resume ? "..." : "Run"}
                        </button>
                        <button
                            onClick={() => handleSendCommand("pause")}
                            className="flex items-center px-3 py-2 rounded bg-yellow-600 text-white text-sm hover:bg-yellow-700 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-yellow-500"
                            disabled={isLoading.pause}
                            aria-busy={isLoading.pause}
                            aria-label={`Pause simulation${isLoading.pause ? ', loading' : ''}`}
                        >
                            <span className="mr-1">{icons.pause}</span>
                            {isLoading.pause ? "..." : "Pause"}
                        </button>
                        <button
                            onClick={() => handleSendCommand("step")}
                            className="flex items-center px-3 py-2 rounded bg-blue-600 text-white text-sm hover:bg-blue-700 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            disabled={isLoading.step}
                            aria-busy={isLoading.step}
                            aria-label={`Step simulation${isLoading.step ? ', loading' : ''}`}
                        >
                            <span className="mr-1">{icons.step}</span>
                            {isLoading.step ? "..." : "Step"}
                        </button>
                        <button
                            onClick={() => handleSendCommand("reset")}
                            className="flex items-center px-3 py-2 rounded bg-gray-600 text-white text-sm hover:bg-gray-700 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-gray-500"
                            disabled={isLoading.reset}
                            aria-busy={isLoading.reset}
                            aria-label={`Reset simulation${isLoading.reset ? ', loading' : ''}`}
                        >
                            <span className="mr-1">{icons.reset}</span>
                            {isLoading.reset ? "..." : "Reset"}
                        </button>
                    </div>
                </div>

                {/* Emergency Controls */}
                <div className="mb-4">
                    <h3 className="text-sm font-medium mb-2 text-gray-700">Emergency Controls</h3>
                    <div className="flex gap-2" role="toolbar" aria-label="Emergency controls">
                        <button
                            onClick={handleEmergencyStop}
                            className="flex items-center px-3 py-2 rounded bg-red-600 text-white text-sm hover:bg-red-700 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-red-500"
                            disabled={isLoading.emergency}
                            aria-busy={isLoading.emergency}
                            aria-label={`Emergency Stop${isLoading.emergency ? ', loading' : ''}`}
                        >
                            <span className="mr-1">{icons.emergency}</span>
                            {isLoading.emergency ? "..." : "Emergency Stop"}
                        </button>
                        <button
                            onClick={handleRollback}
                            className="flex items-center px-3 py-2 rounded bg-purple-600 text-white text-sm hover:bg-purple-700 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-purple-500"
                            disabled={isLoading.rollback}
                            aria-busy={isLoading.rollback}
                            aria-label={`Rollback simulation${isLoading.rollback ? ', loading' : ''}`}
                        >
                            <span className="mr-1">⏪</span>
                            {isLoading.rollback ? "..." : "Rollback"}
                        </button>
                    </div>
                </div>

                {/* Feedback Controls */}
                <div>
                    <h3 className="text-sm font-medium mb-2 text-gray-700">Feedback Controls</h3>
                    <div className="flex gap-2" role="toolbar" aria-label="Feedback controls">
                        <button
                            onClick={() => handleSendReward(1)}
                            className="flex items-center px-3 py-2 bg-green-600 text-white rounded disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-green-500"
                            disabled={isLoading.positive}
                            aria-busy={isLoading.positive}
                            aria-label={`Positive reward${isLoading.positive ? ', loading' : ''}`}
                        >
                            <span className="mr-1">{icons.reward}</span>
                            {isLoading.positive ? "..." : "Positive"}
                        </button>
                        <button
                            onClick={() => handleSendReward(-1)}
                            className="flex items-center px-3 py-2 bg-red-600 text-white rounded disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-red-500"
                            disabled={isLoading.negative}
                            aria-busy={isLoading.negative}
                            aria-label={`Negative reward${isLoading.negative ? ', loading' : ''}`}
                        >
                            <span className="mr-1">{icons.punish}</span>
                            {isLoading.negative ? "..." : "Negative"}
                        </button>
                    </div>
                </div>

                {/* Keyboard shortcuts info */}
                <div className="mt-4 text-xs text-gray-500">
                    <p>Keyboard shortcuts: Space = Pause/Resume, S = Step</p>
                </div>
            </div>
        </div>
    );
}