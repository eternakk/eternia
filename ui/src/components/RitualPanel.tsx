import { useState, useEffect, useRef, useCallback } from 'react';
import { triggerRitual, getRituals, Ritual } from '../api';
import { useErrorHandler } from '../utils/errorHandling';
import { Pagination } from './ui/Pagination';

// Cache duration in milliseconds (5 minutes)
const CACHE_DURATION = 5 * 60 * 1000;

export default function RitualPanel() {
    const [rituals, setRituals] = useState<Ritual[]>([]);
    const [error, setError] = useState<Error | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const { handleApiError } = useErrorHandler();

    // Pagination state
    const [currentPage, setCurrentPage] = useState<number>(1);
    const [itemsPerPage] = useState<number>(5); // Show 5 rituals per page

    // Cache reference
    const cacheRef = useRef<{
        data: Ritual[] | null;
        timestamp: number;
    }>({
        data: null,
        timestamp: 0
    });

    // Last request time reference for debouncing
    const lastRequestTimeRef = useRef<number>(0);
    const minRequestInterval = 2000; // Minimum 2 seconds between requests

    const fetchRituals = useCallback(async () => {
        // Check if we should use cached data
        const now = Date.now();
        const cache = cacheRef.current;

        // Use cache if it's valid and not expired
        if (cache.data && now - cache.timestamp < CACHE_DURATION) {
            setRituals(cache.data);
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
            const data = await getRituals();
            if (data) {
                // Update state and cache
                setRituals(data);
                cacheRef.current = {
                    data,
                    timestamp: now
                };
            }
            setError(null);
        } catch (err) {
            handleApiError(err, 'Failed to fetch rituals');
            setError(err as Error);
        } finally {
            setIsLoading(false);
        }
    }, [handleApiError]);

    useEffect(() => {
        fetchRituals();

        // Set up polling
        const intervalId = setInterval(fetchRituals, 10000);

        // Clean up interval on unmount
        return () => clearInterval(intervalId);
    }, [fetchRituals]);

    const handleTriggerRitual = async (id: number) => {
        try {
            await triggerRitual(id);
            // Refetch rituals after triggering
            fetchRituals();
        } catch (err) {
            handleApiError(err, 'Failed to trigger ritual');
        }
    };

    if (error) return <div>Error loading rituals.</div>;
    if (isLoading && !rituals.length) return <div>Loading rituals...</div>;

    // Calculate pagination
    const indexOfLastItem = currentPage * itemsPerPage;
    const indexOfFirstItem = indexOfLastItem - itemsPerPage;
    const currentRituals = rituals.slice(indexOfFirstItem, indexOfLastItem);

    // Handle page change
    const handlePageChange = (pageNumber: number) => {
        setCurrentPage(pageNumber);
        // Scroll to top of the list when page changes
        document.getElementById('rituals-list')?.scrollIntoView({ behavior: 'smooth' });
    };

    return (
        <div className="p-4">
            <h3 className="text-xl font-bold mb-2" id="rituals-heading">Available Rituals</h3>
            <ul 
                id="rituals-list"
                className="mb-4"
                role="list"
                aria-labelledby="rituals-heading"
                aria-live="polite"
            >
                {currentRituals.map((ritual: Ritual) => (
                    <li key={ritual.id} className="flex items-center mb-2 p-2 border-b border-gray-200">
                        <span className="flex-1">{ritual.name}</span>
                        <button
                            onClick={() => handleTriggerRitual(ritual.id)}
                            className="ml-2 px-3 py-1 bg-indigo-600 text-white rounded hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                            aria-label={`Trigger ${ritual.name} ritual`}
                        >
                            Trigger
                        </button>
                    </li>
                ))}
                {currentRituals.length === 0 && (
                    <li className="p-2 text-gray-500">No rituals available.</li>
                )}
            </ul>

            {/* Pagination component */}
            {rituals.length > itemsPerPage && (
                <Pagination
                    totalItems={rituals.length}
                    itemsPerPage={itemsPerPage}
                    currentPage={currentPage}
                    onPageChange={handlePageChange}
                    className="mt-4"
                />
            )}
        </div>
    );
}
