import { useState, useEffect, useRef, useCallback } from 'react';
import { getAgents, Agent } from '../api';
import { useErrorHandler } from '../utils/errorHandling';

// Cache duration in milliseconds (5 minutes)
const CACHE_DURATION = 5 * 60 * 1000;

export default function AgentDashboard() {
    const [agents, setAgents] = useState<Agent[]>([]);
    const [error, setError] = useState<Error | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);
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

    if (error) return <div>Error loading agents.</div>;
    if (isLoading && !agents.length) return <div>Loading agents...</div>;

    return (
        <div className="p-4">
            <h2 className="text-xl font-bold mb-2">Agents</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {agents.map((agent: any) => (
                    <div key={agent.name} className="bg-white shadow rounded p-4 flex flex-col items-start">
                        <div className="flex items-center mb-2">
                            <span className="font-semibold">{agent.name}</span>
                            <span className="ml-2 text-sm text-gray-500">({agent.role})</span>
                        </div>
                        <div>
                            <span>Zone: {agent.zone && typeof agent.zone === 'object' ? agent.zone.name : agent.zone || "Unknown"}</span>
                        </div>
                        <div className="mt-2 flex items-center">
              <span className={`emotion-badge emotion-${(agent.emotion || 'neutral').toLowerCase()}`}>
                {agent.emotion || "Neutral"}
              </span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
