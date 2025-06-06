import { useState, useEffect, useRef, useCallback } from 'react';
import { getAgents, Agent } from '../api';
import { useErrorHandler } from '../utils/errorHandling';
import { useSwipeable } from 'react-swipeable';
import { Pagination } from './ui/Pagination';

// Cache duration in milliseconds (5 minutes)
const CACHE_DURATION = 5 * 60 * 1000;

export default function AgentDashboard() {
    const [agents, setAgents] = useState<Agent[]>([]);
    const [error, setError] = useState<Error | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [currentAgentIndex, setCurrentAgentIndex] = useState<number>(0);

    // Pagination state for desktop view
    const [currentPage, setCurrentPage] = useState<number>(1);
    const [itemsPerPage] = useState<number>(6); // Show 6 agents per page (3x2 grid)
    const { handleApiError } = useErrorHandler();

    // Cache reference
    const cacheRef = useRef<{
        data: Agent[] | null;
        timestamp: number;
    }>({
        data: null,
        timestamp: 0
    });

    // Last request time reference for debouncing
    const lastRequestTimeRef = useRef<number>(0);
    const minRequestInterval = 2000; // Minimum 2 seconds between requests

    const fetchAgents = useCallback(async () => {
        // Check if we should use cached data
        const now = Date.now();
        const cache = cacheRef.current;

        // Use cache if it's valid and not expired
        if (cache.data && now - cache.timestamp < CACHE_DURATION) {
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
                // Update state and cache
                setAgents(data);
                cacheRef.current = {
                    data,
                    timestamp: now
                };
            }
            setError(null);
        } catch (err) {
            handleApiError(err, 'Failed to fetch agents');
            setError(err as Error);
        } finally {
            setIsLoading(false);
        }
    }, [handleApiError]);

    useEffect(() => {
        fetchAgents();

        // Set up polling
        const intervalId = setInterval(fetchAgents, 10000);

        // Clean up interval on unmount
        return () => clearInterval(intervalId);
    }, [fetchAgents]);

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

    if (error) return <div>Error loading agents.</div>;
    if (isLoading && !agents.length) return <div>Loading agents...</div>;

    // Render a single agent card for mobile view
    const renderMobileView = () => {
        if (agents.length === 0) return <div>No agents available.</div>;

        const agent = agents[currentAgentIndex];

        return (
            <div 
                {...swipeHandlers} 
                className="relative"
                role="region"
                aria-label={`Agent card for ${agent.name}`}
                aria-roledescription="swipeable card"
            >
                <div 
                    className="bg-white shadow rounded p-4 flex flex-col items-start"
                    tabIndex={0}
                    aria-label={`Agent ${agent.name}, role: ${agent.role}, emotion: ${agent.emotion || 'Neutral'}`}
                >
                    <div className="flex items-center mb-2">
                        <span className="font-semibold">{agent.name}</span>
                        <span className="ml-2 text-sm text-gray-500">({agent.role})</span>
                    </div>
                    <div>
                        <span>Zone: {agent.zone && typeof agent.zone === 'object' ? agent.zone.name : agent.zone || "Unknown"}</span>
                    </div>
                    <div className="mt-2 flex items-center">
                        <span 
                            className={`emotion-badge emotion-${(agent.emotion || 'neutral').toLowerCase()}`}
                            aria-label={`Emotion: ${agent.emotion || 'Neutral'}`}
                        >
                            {agent.emotion || "Neutral"}
                        </span>
                    </div>
                </div>

                {/* Navigation indicators */}
                <div 
                    className="mt-4 flex justify-between items-center"
                    role="navigation"
                    aria-label="Agent navigation"
                >
                    <button 
                        onClick={handlePrevAgent}
                        className="px-3 py-1 bg-slate-200 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        aria-label="Previous agent"
                    >
                        Previous
                    </button>
                    <div 
                        className="text-sm text-gray-500"
                        aria-live="polite"
                        aria-atomic="true"
                    >
                        {currentAgentIndex + 1} of {agents.length}
                    </div>
                    <button 
                        onClick={handleNextAgent}
                        className="px-3 py-1 bg-slate-200 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        aria-label="Next agent"
                    >
                        Next
                    </button>
                </div>
            </div>
        );
    };

    // Render grid view for desktop with pagination
    const renderDesktopView = () => {
        // Calculate pagination
        const indexOfLastItem = currentPage * itemsPerPage;
        const indexOfFirstItem = indexOfLastItem - itemsPerPage;
        const currentAgents = agents.slice(indexOfFirstItem, indexOfLastItem);

        // Handle page change
        const handlePageChange = (pageNumber: number) => {
            setCurrentPage(pageNumber);
            // Scroll to top of the list when page changes
            document.getElementById('agents-grid')?.scrollIntoView({ behavior: 'smooth' });
        };

        return (
            <>
                <div 
                    id="agents-grid"
                    className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
                    role="list"
                    aria-label={`List of agents, page ${currentPage} of ${Math.ceil(agents.length / itemsPerPage)}`}
                >
                    {currentAgents.map((agent: any) => (
                        <div 
                            key={agent.name} 
                            className="bg-white shadow rounded p-4 flex flex-col items-start focus:outline-none focus:ring-2 focus:ring-blue-500"
                            role="listitem"
                            tabIndex={0}
                            aria-label={`Agent ${agent.name}, role: ${agent.role}, emotion: ${agent.emotion || 'Neutral'}`}
                        >
                            <div className="flex items-center mb-2">
                                <span className="font-semibold">{agent.name}</span>
                                <span className="ml-2 text-sm text-gray-500">({agent.role})</span>
                            </div>
                            <div>
                                <span>Zone: {agent.zone && typeof agent.zone === 'object' ? agent.zone.name : agent.zone || "Unknown"}</span>
                            </div>
                            <div className="mt-2 flex items-center">
                                <span 
                                    className={`emotion-badge emotion-${(agent.emotion || 'neutral').toLowerCase()}`}
                                    aria-label={`Emotion: ${agent.emotion || 'Neutral'}`}
                                >
                                    {agent.emotion || "Neutral"}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Pagination component */}
                {agents.length > 0 && (
                    <Pagination
                        totalItems={agents.length}
                        itemsPerPage={itemsPerPage}
                        currentPage={currentPage}
                        onPageChange={handlePageChange}
                        className="mt-6"
                    />
                )}
            </>
        );
    };

    return (
        <div className="p-4" role="region" aria-labelledby="agents-heading">
            <h2 className="text-xl font-bold mb-2" id="agents-heading">Agents</h2>

            {/* Show mobile view on small screens, desktop view on md+ screens */}
            <div className="block md:hidden" aria-label="Agent cards, swipeable view">
                {renderMobileView()}
            </div>
            <div className="hidden md:block" aria-label="Agent cards, grid view">
                {renderDesktopView()}
            </div>
        </div>
    );
}
