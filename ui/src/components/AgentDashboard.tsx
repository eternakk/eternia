import { useState, useEffect, useRef, useCallback } from 'react';
import { getAgents, Agent, Zone } from '../api';
import { useErrorHandler } from '../utils/errorHandling';
import { useSwipeable } from 'react-swipeable';
import { Pagination } from './ui/Pagination';
import { useWorldState } from '../contexts/WorldStateContext';

// Emotion icons mapping
const emotionIcons: Record<string, { icon: string; color: string }> = {
  joy: { icon: '😊', color: 'text-yellow-500' },
  grief: { icon: '😢', color: 'text-blue-500' },
  anger: { icon: '😠', color: 'text-red-500' },
  fear: { icon: '😨', color: 'text-purple-500' },
  awe: { icon: '😲', color: 'text-indigo-500' },
  neutral: { icon: '😐', color: 'text-gray-500' },
};

// Helper function to get emotion display info
const getEmotionDisplay = (emotion: string | null) => {
  const normalizedEmotion = (emotion || 'neutral').toLowerCase();
  return emotionIcons[normalizedEmotion] || emotionIcons.neutral;
};

// Stress level component
const StressLevelBar = ({ level }: { level: number }) => {
  // Normalize level to 0-100 range
  const normalizedLevel = Math.min(Math.max(level, 0), 100);

  // Determine color based on stress level
  let color = 'bg-green-500';
  if (normalizedLevel > 70) color = 'bg-red-500';
  else if (normalizedLevel > 40) color = 'bg-yellow-500';

  return (
    <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700" role="progressbar" aria-valuenow={normalizedLevel} aria-valuemin={0} aria-valuemax={100}>
      <div className={`${color} h-2.5 rounded-full`} style={{ width: `${normalizedLevel}%` }}></div>
    </div>
  );
};

const isZone = (z: unknown): z is Zone => {
  return typeof z === 'object' && z !== null && 'name' in (z as Record<string, unknown>) && typeof (z as { name?: unknown }).name === 'string';
};

const renderZoneLabel = (z: string | Zone | null): string => {
  if (typeof z === 'string') return z;
  if (isZone(z)) return z.name;
  return 'Unknown';
};

export default function AgentDashboard() {
    const [agents, setAgents] = useState<Agent[]>([]);
    const [error, setError] = useState<Error | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [currentAgentIndex, setCurrentAgentIndex] = useState<number>(0);
    const { refreshState } = useWorldState(); // Use WorldStateContext for auto-refresh

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

    if (error) return <div className="p-4 border rounded-xl shadow bg-white">Error loading agents.</div>;
    if (isLoading && !agents.length) return <div className="p-4 border rounded-xl shadow bg-white">Loading agents...</div>;

    // Render a single agent card for mobile view
    const renderMobileView = () => {
        if (agents.length === 0) return <div>No agents available.</div>;

        const agent = agents[currentAgentIndex];
        const emotionDisplay = getEmotionDisplay(agent.emotion);

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
                    <div className="flex items-center mb-2 w-full">
                        <span className="font-semibold">{agent.name}</span>
                        <span className="ml-2 text-sm text-gray-500">({agent.role})</span>
                    </div>
                    <div>
                        <span>Zone: {renderZoneLabel(agent.zone)}</span>
                    </div>
                    <div className="mt-2 flex items-center w-full">
                        <span className="mr-2">Mood:</span>
                        <span 
                            className={`flex items-center ${emotionDisplay.color}`}
                            aria-label={`Emotion: ${agent.emotion || 'Neutral'}`}
                        >
                            <span className="mr-1">{emotionDisplay.icon}</span>
                            {agent.emotion || "Neutral"}
                        </span>
                    </div>
                    <div className="mt-2 w-full">
                        <div className="flex items-center mb-1">
                            <span className="mr-2">Stress:</span>
                            <span className="text-xs">{agent.stressLevel}%</span>
                        </div>
                        <StressLevelBar level={agent.stressLevel} />
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
                {/* Column headers */}
                <div className="grid grid-cols-12 gap-2 mb-2 font-semibold text-sm text-gray-600 px-2">
                    <div className="col-span-3">Name</div>
                    <div className="col-span-3">Role</div>
                    <div className="col-span-2">Zone</div>
                    <div className="col-span-2">Mood</div>
                    <div className="col-span-2">Stress</div>
                </div>

                <div 
                    id="agents-grid"
                    className="grid grid-cols-1 gap-4"
                    role="list"
                    aria-label={`List of agents, page ${currentPage} of ${Math.ceil(agents.length / itemsPerPage)}`}
                >
                    {currentAgents.map((agent: Agent) => {
                        const emotionDisplay = getEmotionDisplay(agent.emotion);

                        return (
                            <div 
                                key={agent.name} 
                                className="bg-white shadow rounded p-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                role="listitem"
                                tabIndex={0}
                                aria-label={`Agent ${agent.name}, role: ${agent.role}, emotion: ${agent.emotion || 'Neutral'}`}
                            >
                                <div className="grid grid-cols-12 gap-2 items-center">
                                    <div className="col-span-3 font-semibold">{agent.name}</div>
                                    <div className="col-span-3 text-sm text-gray-600">{agent.role}</div>
                                    <div className="col-span-2 text-sm">
                                        {renderZoneLabel(agent.zone)}
                                    </div>
                                    <div className="col-span-2">
                                        <span 
                                            className={`flex items-center ${emotionDisplay.color}`}
                                            aria-label={`Emotion: ${agent.emotion || 'Neutral'}`}
                                        >
                                            <span className="mr-1">{emotionDisplay.icon}</span>
                                            <span className="text-sm">{agent.emotion || "Neutral"}</span>
                                        </span>
                                    </div>
                                    <div className="col-span-2">
                                        <div className="flex flex-col">
                                            <span className="text-xs mb-1">{agent.stressLevel}%</span>
                                            <StressLevelBar level={agent.stressLevel} />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                    {currentAgents.length === 0 && (
                        <div className="col-span-12 p-4 text-gray-500 text-center">
                            No agents available.
                        </div>
                    )}
                </div>

                {/* Pagination component */}
                {agents.length > itemsPerPage && (
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
        <div className="p-4 border rounded-xl shadow bg-white" role="region" aria-labelledby="agents-heading">
            <h2 className="text-xl font-bold mb-4" id="agents-heading">Agents</h2>

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
