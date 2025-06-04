import { sendCommand, rollbackTo, sendReward } from "../api";
import { useErrorHandler } from "../utils/errorHandling";
import { useState } from "react";

const actions = ["pause", "resume", "shutdown"] as const;

export default function ControlPanel() {
    // Default companion name or get it from somewhere else if needed
    const companionName = "default";
    const { withErrorHandling } = useErrorHandler();
    const [isLoading, setIsLoading] = useState<Record<string, boolean>>({});

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
        <div className="p-4 border rounded-xl shadow bg-white">
            <h2 className="font-semibold mb-2">Controls</h2>
            <div className="flex gap-3 flex-wrap">
                {actions.map((a) => (
                    <button
                        key={a}
                        onClick={() => handleSendCommand(a)}
                        className="px-3 py-1 rounded bg-slate-800 text-white text-sm hover:bg-slate-700 disabled:opacity-50"
                        disabled={isLoading[a]}
                    >
                        {isLoading[a] ? "..." : a.toUpperCase()}
                    </button>
                ))}
                <button
                    onClick={handleRollback}
                    className="px-3 py-1 rounded bg-slate-800 text-white text-sm hover:bg-slate-700 disabled:opacity-50"
                    disabled={isLoading.rollback}
                >
                    {isLoading.rollback ? "..." : "ROLLBACK"}
                </button>
            </div>
            <div className="mt-3 flex gap-2">
                <button
                    onClick={() => handleSendReward(1)}
                    className="px-2 py-1 bg-green-600 text-white rounded disabled:opacity-50"
                    disabled={isLoading.positive}
                >
                    {isLoading.positive ? "..." : "👍"}
                </button>
                <button
                    onClick={() => handleSendReward(-1)}
                    className="px-2 py-1 bg-red-600 text-white rounded disabled:opacity-50"
                    disabled={isLoading.negative}
                >
                    {isLoading.negative ? "..." : "👎"}
                </button>
            </div>
        </div>
    );
}
