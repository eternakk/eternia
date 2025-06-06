import { sendCommand, rollbackTo, sendReward } from "../api";
import { useErrorHandler } from "../utils/errorHandling";
import { useState } from "react";

const actions = ["pause", "resume", "shutdown"] as const;

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

    return (
        <div className="p-4 border rounded-xl shadow bg-white" role="region" aria-labelledby="controls-heading">
            <div className="flex justify-between items-center mb-2">
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
                <div className="flex gap-3 flex-wrap" role="toolbar" aria-label="Simulation controls">
                    {actions.map((a) => (
                        <button
                            key={a}
                            onClick={() => handleSendCommand(a)}
                            className="px-3 py-2 rounded bg-slate-800 text-white text-sm hover:bg-slate-700 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            disabled={isLoading[a]}
                            aria-busy={isLoading[a]}
                            aria-label={`${a.charAt(0).toUpperCase() + a.slice(1)} simulation${isLoading[a] ? ', loading' : ''}`}
                        >
                            {isLoading[a] ? "..." : a.toUpperCase()}
                        </button>
                    ))}
                    <button
                        onClick={handleRollback}
                        className="px-3 py-2 rounded bg-slate-800 text-white text-sm hover:bg-slate-700 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        disabled={isLoading.rollback}
                        aria-busy={isLoading.rollback}
                        aria-label={`Rollback simulation${isLoading.rollback ? ', loading' : ''}`}
                    >
                        {isLoading.rollback ? "..." : "ROLLBACK"}
                    </button>
                </div>
                <div className="mt-3 flex gap-2" role="toolbar" aria-label="Reward controls">
                    <button
                        onClick={() => handleSendReward(1)}
                        className="px-3 py-2 bg-green-600 text-white rounded disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        disabled={isLoading.positive}
                        aria-busy={isLoading.positive}
                        aria-label={`Positive reward${isLoading.positive ? ', loading' : ''}`}
                    >
                        {isLoading.positive ? "..." : "👍"}
                    </button>
                    <button
                        onClick={() => handleSendReward(-1)}
                        className="px-3 py-2 bg-red-600 text-white rounded disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        disabled={isLoading.negative}
                        aria-busy={isLoading.negative}
                        aria-label={`Negative reward${isLoading.negative ? ', loading' : ''}`}
                    >
                        {isLoading.negative ? "..." : "👎"}
                    </button>
                </div>
            </div>
        </div>
    );
}
