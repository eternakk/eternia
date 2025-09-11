import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState, useEffect, useRef, useCallback } from 'react';
import { getAgents } from '../api';
import { useErrorHandler } from '../utils/errorHandling';
import { useSwipeable } from 'react-swipeable';
import { Pagination } from './ui/Pagination';
import { useWorldState } from '../contexts/WorldStateContext';
// Emotion icons mapping
const emotionIcons = {
    joy: { icon: '😊', color: 'text-yellow-500' },
    grief: { icon: '😢', color: 'text-blue-500' },
    anger: { icon: '😠', color: 'text-red-500' },
    fear: { icon: '😨', color: 'text-purple-500' },
    awe: { icon: '😲', color: 'text-indigo-500' },
    neutral: { icon: '😐', color: 'text-gray-500' },
};
// Helper function to get emotion display info
const getEmotionDisplay = (emotion) => {
    const normalizedEmotion = (emotion || 'neutral').toLowerCase();
    return emotionIcons[normalizedEmotion] || emotionIcons.neutral;
};
// Stress level component
const StressLevelBar = ({ level }) => {
    // Normalize level to 0-100 range
    const normalizedLevel = Math.min(Math.max(level, 0), 100);
    // Determine color based on stress level
    let color = 'bg-green-500';
    if (normalizedLevel > 70)
        color = 'bg-red-500';
    else if (normalizedLevel > 40)
        color = 'bg-yellow-500';
    return (_jsx("div", { className: "w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700", role: "progressbar", "aria-valuenow": normalizedLevel, "aria-valuemin": 0, "aria-valuemax": 100, children: _jsx("div", { className: `${color} h-2.5 rounded-full`, style: { width: `${normalizedLevel}%` } }) }));
};
const isZone = (z) => {
    return typeof z === 'object' && z !== null && 'name' in z && typeof z.name === 'string';
};
const renderZoneLabel = (z) => {
    if (typeof z === 'string')
        return z;
    if (isZone(z))
        return z.name;
    return 'Unknown';
};
export default function AgentDashboard() {
    const [agents, setAgents] = useState([]);
    const [error, setError] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [currentAgentIndex, setCurrentAgentIndex] = useState(0);
    const { refreshState } = useWorldState(); // Use WorldStateContext for auto-refresh
    // Pagination state for desktop view
    const [currentPage, setCurrentPage] = useState(1);
    const [itemsPerPage] = useState(6); // Show 6 agents per page (3x2 grid)
    const { handleApiError } = useErrorHandler();
    // Cache reference
    const cacheRef = useRef({
        data: null,
        timestamp: 0
    });
    // Last request time reference for debouncing
    const lastRequestTimeRef = useRef(0);
    const minRequestInterval = 2000; // Minimum 2 seconds between requests
    const fetchAgents = useCallback(async () => {
        // Check if we should use cached data
        const now = Date.now();
        const cache = cacheRef.current;
        // Use cache if it's valid and not expired
        if (cache.data && now - cache.timestamp < 5 * 60 * 1000) {
            setAgents(cache.data);
            setIsLoading(false);
            return;
        }
        // Debounce requests
        if (now - lastRequestTimeRef.current < minRequestInterval) {
            return; // Skip this request if it's too soon
        }
        lastRequestTimeRef.current = now;
        try {
            setIsLoading(true);
            const data = await getAgents();
            if (data) {
                // Add random stress levels for demonstration (in a real app, this would come from the API)
                const agentsWithStress = data.map(agent => ({
                    ...agent,
                    stressLevel: Math.floor(Math.random() * 100)
                }));
                // Update state and cache
                setAgents(agentsWithStress);
                cacheRef.current = {
                    data: agentsWithStress,
                    timestamp: now
                };
            }
            setError(null);
        }
        catch (err) {
            handleApiError(err, 'Failed to fetch agents');
            setError(err);
        }
        finally {
            setIsLoading(false);
        }
    }, [handleApiError]);
    useEffect(() => {
        fetchAgents();
        // Set up polling
        const intervalId = setInterval(() => {
            fetchAgents();
            // Also refresh world state to keep everything in sync
            refreshState();
        }, 10000);
        // Clean up interval on unmount
        return () => clearInterval(intervalId);
    }, [fetchAgents, refreshState]);
    // Setup swipe handlers
    const handleNextAgent = () => {
        if (agents.length > 0) {
            setCurrentAgentIndex((prevIndex) => (prevIndex + 1) % agents.length);
        }
    };
    const handlePrevAgent = () => {
        if (agents.length > 0) {
            setCurrentAgentIndex((prevIndex) => (prevIndex - 1 + agents.length) % agents.length);
        }
    };
    const swipeHandlers = useSwipeable({
        onSwipedLeft: handleNextAgent,
        onSwipedRight: handlePrevAgent,
        preventScrollOnSwipe: true,
        trackMouse: false
    });
    if (error)
        return _jsx("div", { className: "p-4 border rounded-xl shadow bg-white", children: "Error loading agents." });
    if (isLoading && !agents.length)
        return _jsx("div", { className: "p-4 border rounded-xl shadow bg-white", children: "Loading agents..." });
    // Render a single agent card for mobile view
    const renderMobileView = () => {
        if (agents.length === 0)
            return _jsx("div", { children: "No agents available." });
        const agent = agents[currentAgentIndex];
        const emotionDisplay = getEmotionDisplay(agent.emotion);
        return (_jsxs("div", { ...swipeHandlers, className: "relative", role: "region", "aria-label": `Agent card for ${agent.name}`, "aria-roledescription": "swipeable card", children: [_jsxs("div", { className: "bg-white shadow rounded p-4 flex flex-col items-start", tabIndex: 0, "aria-label": `Agent ${agent.name}, role: ${agent.role}, emotion: ${agent.emotion || 'Neutral'}`, children: [_jsxs("div", { className: "flex items-center mb-2 w-full", children: [_jsx("span", { className: "font-semibold", children: agent.name }), _jsxs("span", { className: "ml-2 text-sm text-gray-500", children: ["(", agent.role, ")"] })] }), _jsx("div", { children: _jsxs("span", { children: ["Zone: ", renderZoneLabel(agent.zone)] }) }), _jsxs("div", { className: "mt-2 flex items-center w-full", children: [_jsx("span", { className: "mr-2", children: "Mood:" }), _jsxs("span", { className: `flex items-center ${emotionDisplay.color}`, "aria-label": `Emotion: ${agent.emotion || 'Neutral'}`, children: [_jsx("span", { className: "mr-1", children: emotionDisplay.icon }), agent.emotion || "Neutral"] })] }), _jsxs("div", { className: "mt-2 w-full", children: [_jsxs("div", { className: "flex items-center mb-1", children: [_jsx("span", { className: "mr-2", children: "Stress:" }), _jsxs("span", { className: "text-xs", children: [agent.stressLevel, "%"] })] }), _jsx(StressLevelBar, { level: agent.stressLevel })] })] }), _jsxs("div", { className: "mt-4 flex justify-between items-center", role: "navigation", "aria-label": "Agent navigation", children: [_jsx("button", { onClick: handlePrevAgent, className: "px-3 py-1 bg-slate-200 rounded focus:outline-none focus:ring-2 focus:ring-blue-500", "aria-label": "Previous agent", children: "Previous" }), _jsxs("div", { className: "text-sm text-gray-500", "aria-live": "polite", "aria-atomic": "true", children: [currentAgentIndex + 1, " of ", agents.length] }), _jsx("button", { onClick: handleNextAgent, className: "px-3 py-1 bg-slate-200 rounded focus:outline-none focus:ring-2 focus:ring-blue-500", "aria-label": "Next agent", children: "Next" })] })] }));
    };
    // Render grid view for desktop with pagination
    const renderDesktopView = () => {
        // Calculate pagination
        const indexOfLastItem = currentPage * itemsPerPage;
        const indexOfFirstItem = indexOfLastItem - itemsPerPage;
        const currentAgents = agents.slice(indexOfFirstItem, indexOfLastItem);
        // Handle page change
        const handlePageChange = (pageNumber) => {
            setCurrentPage(pageNumber);
            // Scroll to top of the list when page changes
            document.getElementById('agents-grid')?.scrollIntoView({ behavior: 'smooth' });
        };
        return (_jsxs(_Fragment, { children: [_jsxs("div", { className: "grid grid-cols-12 gap-2 mb-2 font-semibold text-sm text-gray-600 px-2", children: [_jsx("div", { className: "col-span-3", children: "Name" }), _jsx("div", { className: "col-span-3", children: "Role" }), _jsx("div", { className: "col-span-2", children: "Zone" }), _jsx("div", { className: "col-span-2", children: "Mood" }), _jsx("div", { className: "col-span-2", children: "Stress" })] }), _jsxs("div", { id: "agents-grid", className: "grid grid-cols-1 gap-4", role: "list", "aria-label": `List of agents, page ${currentPage} of ${Math.ceil(agents.length / itemsPerPage)}`, children: [currentAgents.map((agent) => {
                            const emotionDisplay = getEmotionDisplay(agent.emotion);
                            return (_jsx("div", { className: "bg-white shadow rounded p-4 focus:outline-none focus:ring-2 focus:ring-blue-500", role: "listitem", tabIndex: 0, "aria-label": `Agent ${agent.name}, role: ${agent.role}, emotion: ${agent.emotion || 'Neutral'}`, children: _jsxs("div", { className: "grid grid-cols-12 gap-2 items-center", children: [_jsx("div", { className: "col-span-3 font-semibold", children: agent.name }), _jsx("div", { className: "col-span-3 text-sm text-gray-600", children: agent.role }), _jsx("div", { className: "col-span-2 text-sm", children: renderZoneLabel(agent.zone) }), _jsx("div", { className: "col-span-2", children: _jsxs("span", { className: `flex items-center ${emotionDisplay.color}`, "aria-label": `Emotion: ${agent.emotion || 'Neutral'}`, children: [_jsx("span", { className: "mr-1", children: emotionDisplay.icon }), _jsx("span", { className: "text-sm", children: agent.emotion || "Neutral" })] }) }), _jsx("div", { className: "col-span-2", children: _jsxs("div", { className: "flex flex-col", children: [_jsxs("span", { className: "text-xs mb-1", children: [agent.stressLevel, "%"] }), _jsx(StressLevelBar, { level: agent.stressLevel })] }) })] }) }, agent.name));
                        }), currentAgents.length === 0 && (_jsx("div", { className: "col-span-12 p-4 text-gray-500 text-center", children: "No agents available." }))] }), agents.length > itemsPerPage && (_jsx(Pagination, { totalItems: agents.length, itemsPerPage: itemsPerPage, currentPage: currentPage, onPageChange: handlePageChange, className: "mt-6" }))] }));
    };
    return (_jsxs("div", { className: "p-4 border rounded-xl shadow bg-white", role: "region", "aria-labelledby": "agents-heading", children: [_jsx("h2", { className: "text-xl font-bold mb-4", id: "agents-heading", children: "Agents" }), _jsx("div", { className: "block md:hidden", "aria-label": "Agent cards, swipeable view", children: renderMobileView() }), _jsx("div", { className: "hidden md:block", "aria-label": "Agent cards, grid view", children: renderDesktopView() })] }));
}
