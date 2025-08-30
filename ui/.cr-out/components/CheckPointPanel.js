import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import useSWR from "swr";
import { getCheckpoints, rollbackTo } from "../api";
import { useState, useEffect, useRef } from "react";
// Cache duration in milliseconds (5 minutes)
const CACHE_DURATION = 5 * 60 * 1000;
// Helper function to parse checkpoint filename and extract information
const parseCheckpointInfo = (filename) => {
    var _a;
    // Example filename format: checkpoint_2023-05-15_14-30-45_0.85.json
    // Try to extract timestamp and continuity score from filename
    const parts = ((_a = filename.split("/").pop()) === null || _a === void 0 ? void 0 : _a.split("_")) || [];
    let timestamp = null;
    let continuityScore = null;
    // Check if we have date and time parts (at positions 1 and 2)
    if (parts.length >= 3) {
        const datePart = parts[1];
        const timePart = parts[2];
        if (datePart && timePart) {
            // Try to parse the date
            try {
                // Handle different date formats
                if (datePart.includes("-") && timePart.includes("-")) {
                    // Format: 2023-05-15_14-30-45
                    const dateStr = `${datePart}T${timePart.replace(/-/g, ":")}`;
                    timestamp = new Date(dateStr);
                }
            }
            catch (e) {
                console.warn("Failed to parse timestamp from checkpoint filename:", e);
            }
        }
    }
    // Try to extract continuity score (usually a number between 0 and 1)
    // It might be in the last part before the extension
    if (parts.length >= 4) {
        const lastPart = parts[parts.length - 1].split(".")[0]; // Remove file extension
        const scoreValue = parseFloat(lastPart);
        if (!isNaN(scoreValue) && scoreValue >= 0 && scoreValue <= 1) {
            continuityScore = scoreValue;
        }
    }
    return {
        filename,
        displayName: filename.split("/").pop() || filename,
        timestamp,
        continuityScore,
        // If we couldn't parse the timestamp, use the filename for sorting
        sortKey: timestamp ? timestamp.getTime() : filename
    };
};
export default function CheckpointPanel() {
    const [isPageVisible, setIsPageVisible] = useState(true);
    const [selectedCheckpoint, setSelectedCheckpoint] = useState();
    const [isRestoring, setIsRestoring] = useState(false);
    // Last request time reference for debouncing
    const lastRequestTimeRef = useRef(0);
    const minRequestInterval = 2000; // Minimum 2 seconds between requests
    // Set up visibility change detection
    useEffect(() => {
        const handleVisibilityChange = () => {
            setIsPageVisible(document.visibilityState === 'visible');
        };
        // Set initial visibility state
        handleVisibilityChange();
        // Add event listener for visibility changes
        document.addEventListener('visibilitychange', handleVisibilityChange);
        // Clean up event listener
        return () => {
            document.removeEventListener('visibilitychange', handleVisibilityChange);
        };
    }, []);
    // Custom fetcher with debouncing
    const debouncedFetcher = async (...args) => {
        const now = Date.now();
        // Debounce requests
        if (now - lastRequestTimeRef.current < minRequestInterval) {
            // If we're debouncing, return the cached data if available
            const cachedData = localStorage.getItem('checkpoints_cache');
            if (cachedData) {
                const cache = JSON.parse(cachedData);
                if (now - cache.timestamp < CACHE_DURATION) {
                    return cache.data;
                }
            }
            // If no cache or expired, wait for the minimum interval
            await new Promise(resolve => setTimeout(resolve, minRequestInterval));
        }
        lastRequestTimeRef.current = Date.now();
        // Make the actual request
        const data = await getCheckpoints(...args);
        // Cache the result
        localStorage.setItem('checkpoints_cache', JSON.stringify({
            data,
            timestamp: Date.now()
        }));
        return data;
    };
    const { data: files, mutate } = useSWR("ckpts", debouncedFetcher, {
        // Pause polling when page is not visible
        refreshWhenHidden: false,
        // Don't revalidate when window is focused if page is not visible
        revalidateOnFocus: isPageVisible,
        // Only poll when page is visible
        refreshWhenOffline: false,
        // Disable polling completely when page is not visible
        refreshInterval: isPageVisible ? 10000 : 0,
        // Add caching
        dedupingInterval: 5000, // Dedupe requests within 5 seconds
    });
    // Handle restore action
    const handleRestore = async () => {
        if (isRestoring)
            return;
        setIsRestoring(true);
        try {
            await rollbackTo(selectedCheckpoint);
            await mutate(); // refresh list
        }
        finally {
            setIsRestoring(false);
        }
    };
    if (!files)
        return null;
    // Parse and sort checkpoints
    const checkpoints = files
        .map(parseCheckpointInfo)
        .sort((a, b) => {
        // Handle both number and string types for sortKey
        if (typeof a.sortKey === 'number' && typeof b.sortKey === 'number') {
            return b.sortKey - a.sortKey; // Sort newest first for timestamps
        }
        else {
            // Convert to strings for comparison if they're not both numbers
            return String(b.sortKey).localeCompare(String(a.sortKey));
        }
    });
    return (_jsxs("div", { className: "p-4 border rounded-xl shadow bg-white", children: [_jsx("h2", { className: "font-semibold mb-2", children: "Checkpoints" }), _jsxs("div", { className: "mb-4 max-h-60 overflow-y-auto border rounded", children: [_jsxs("div", { className: "sticky top-0 bg-gray-100 p-2 grid grid-cols-12 gap-2 text-xs font-semibold border-b", children: [_jsx("div", { className: "col-span-7", children: "Timestamp" }), _jsx("div", { className: "col-span-3", children: "Continuity" }), _jsx("div", { className: "col-span-2", children: "Action" })] }), checkpoints.length === 0 ? (_jsx("div", { className: "p-4 text-center text-gray-500", children: "No checkpoints available" })) : (_jsxs("div", { className: "divide-y", children: [_jsxs("div", { className: `p-2 grid grid-cols-12 gap-2 items-center hover:bg-blue-50 cursor-pointer ${!selectedCheckpoint ? 'bg-blue-100' : ''}`, onClick: () => setSelectedCheckpoint(undefined), children: [_jsx("div", { className: "col-span-7 text-sm font-medium", children: "Latest (Current State)" }), _jsx("div", { className: "col-span-3", children: "-" }), _jsx("div", { className: "col-span-2", children: _jsx("button", { onClick: (e) => {
                                                e.stopPropagation();
                                                setSelectedCheckpoint(undefined);
                                            }, className: "text-xs px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600", "aria-label": "Select latest checkpoint", children: "Select" }) })] }), checkpoints.map((checkpoint, index) => (_jsxs("div", { className: `p-2 grid grid-cols-12 gap-2 items-center hover:bg-blue-50 cursor-pointer ${selectedCheckpoint === checkpoint.filename ? 'bg-blue-100' : ''}`, onClick: () => setSelectedCheckpoint(checkpoint.filename), children: [_jsx("div", { className: "col-span-7 text-sm", children: checkpoint.timestamp
                                            ? checkpoint.timestamp.toLocaleString()
                                            : checkpoint.displayName }), _jsx("div", { className: "col-span-3", children: checkpoint.continuityScore !== null
                                            ? _jsx("span", { className: "px-2 py-0.5 bg-green-100 rounded-full text-xs", children: checkpoint.continuityScore.toFixed(3) })
                                            : '-' }), _jsx("div", { className: "col-span-2", children: _jsx("button", { onClick: (e) => {
                                                e.stopPropagation();
                                                setSelectedCheckpoint(checkpoint.filename);
                                            }, className: "text-xs px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600", "aria-label": `Select checkpoint ${checkpoint.displayName}`, children: "Select" }) })] }, `${checkpoint.filename}-${index}`)))] }))] }), _jsx("button", { onClick: handleRestore, disabled: isRestoring, className: `w-full py-2 rounded font-medium flex items-center justify-center ${isRestoring
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-indigo-600 text-white hover:bg-indigo-700'}`, "aria-busy": isRestoring, children: isRestoring ? (_jsxs(_Fragment, { children: [_jsxs("svg", { className: "animate-spin -ml-1 mr-2 h-4 w-4 text-white", xmlns: "http://www.w3.org/2000/svg", fill: "none", viewBox: "0 0 24 24", children: [_jsx("circle", { className: "opacity-25", cx: "12", cy: "12", r: "10", stroke: "currentColor", strokeWidth: "4" }), _jsx("path", { className: "opacity-75", fill: "currentColor", d: "M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" })] }), "Restoring..."] })) : (_jsx(_Fragment, { children: "Restore Checkpoint" })) })] }));
}
