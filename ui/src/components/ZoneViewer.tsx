import {useEffect, useRef, useState} from 'react';
import {changeZone, getZones, Zone} from '../api';
import {useErrorHandler} from '../utils/errorHandling';
import {useZone} from '../contexts/ZoneContext';
import {Pagination} from './ui/Pagination';

// Cache duration in milliseconds (5 minutes)
const CACHE_DURATION = 5 * 60 * 1000;

export default function ZoneViewer() {
    const [zones, setZones] = useState<Zone[]>([]);
    const [error, setError] = useState<Error | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [changingZone, setChangingZone] = useState<string | null>(null);
    const {handleApiError, withErrorHandling} = useErrorHandler();
    const {currentZone, setCurrentZone} = useZone();

    // Pagination state
    const [currentPage, setCurrentPage] = useState<number>(1);
    const [itemsPerPage] = useState<number>(6); // Show 6 zones per page (3x2 grid)

    // Cache reference
    const cacheRef = useRef<{
        data: Zone[] | null;
        timestamp: number;
    }>({
        data: null,
        timestamp: 0
    });

    // Last request time reference for debouncing
    const lastRequestTimeRef = useRef<number>(0);
    const minRequestInterval = 2000; // Minimum 2 seconds between requests

    useEffect(() => {
        const fetchZones = async () => {
            // Check if we should use cached data
            const now = Date.now();
            const cache = cacheRef.current;

            // Use cache if it's valid and not expired
            if (cache.data && now - cache.timestamp < CACHE_DURATION) {
                setZones(cache.data);
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
                const data = await getZones();
                if (data) {
                    // Update state and cache
                    setZones(data);
                    cacheRef.current = {
                        data,
                        timestamp: now
                    };
                }
                setError(null);
            } catch (err) {
                handleApiError(err, 'Failed to fetch zones');
                setError(err as Error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchZones();

        // Set up polling
        const intervalId = setInterval(fetchZones, 10000);

        // Clean up interval on unmount
        return () => clearInterval(intervalId);
    }, [handleApiError]);

    if (error) return <div>Error loading zones.</div>;
    if (isLoading && !zones.length) return <div>Loading zones...</div>;

    // Function to handle zone selection
    const handleZoneSelect = withErrorHandling(async (zoneName: string) => {
        // Don't do anything if we're already changing to this zone
        if (changingZone === zoneName) return;

        try {
            // Set the changing zone to show loading state
            setChangingZone(zoneName);

            // First update the zone on the server
            await changeZone(zoneName);

            // Then update the local state
            setCurrentZone(zoneName);
        } catch (error) {
            console.error('Failed to change zone:', error);
            // Don't update local state if server update fails
        } finally {
            // Clear the changing zone state
            setChangingZone(null);
        }
    }, "Failed to change zone");

    // Calculate pagination
    const indexOfLastItem = currentPage * itemsPerPage;
    const indexOfFirstItem = indexOfLastItem - itemsPerPage;
    const currentZones = zones.slice(indexOfFirstItem, indexOfLastItem);

    // Handle page change
    const handlePageChange = (pageNumber: number) => {
        setCurrentPage(pageNumber);
        // Scroll to top of the grid when page changes
        document.getElementById('zones-grid')?.scrollIntoView({ behavior: 'smooth' });
    };

    return (
        <div className="p-4">
            <h2 className="text-xl font-bold mb-2" id="zones-heading">Zones</h2>
            <div 
                id="zones-grid"
                className="grid grid-cols-1 md:grid-cols-3 gap-4" 
                role="radiogroup" 
                aria-labelledby="zones-heading"
                aria-live="polite"
            >
                {currentZones.map((zone: any) => {
                    const isSelected = currentZone === zone.name;
                    const isChanging = changingZone === zone.name;
                    return (
                        <div
                            key={zone.id}
                            className={`${isSelected ? 'bg-blue-200 border-blue-500' : 'bg-gray-100'} shadow rounded p-4 cursor-pointer transition-colors duration-200 hover:bg-blue-100 border-2 ${isSelected ? 'border-blue-500' : 'border-transparent'} ${isChanging ? 'opacity-70' : ''} focus:outline-none focus:ring-2 focus:ring-blue-500`}
                            onClick={() => handleZoneSelect(zone.name)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' || e.key === ' ') {
                                    e.preventDefault();
                                    handleZoneSelect(zone.name);
                                }
                            }}
                            role="radio"
                            aria-checked={isSelected}
                            aria-busy={isChanging}
                            tabIndex={0}
                            aria-label={`Zone ${zone.name}${isSelected ? ', currently selected' : ''}${isChanging ? ', changing' : ''}`}
                        >
                            <div className="font-semibold">{zone.name}</div>
                            <div>
                                Modifiers: {Array.isArray(zone.modifiers) ? zone.modifiers.join(', ') : String(zone.modifiers) || 'None'}
                            </div>
                            <div>
                                Emotion: <span
                                className={`emotion-badge emotion-${(zone.emotion || 'neutral').toLowerCase()}`}
                                aria-label={`Emotion: ${zone.emotion || 'Neutral'}`}
                                >{zone.emotion || 'Neutral'}</span>
                            </div>
                            {isSelected && (
                                <div className="mt-2 text-blue-700 font-semibold" aria-hidden="true">
                                    ✓ Currently Selected
                                </div>
                            )}
                            {isChanging && (
                                <div className="mt-2 text-orange-500 font-semibold animate-pulse" aria-live="polite">
                                    ⟳ Changing Zone...
                                </div>
                            )}
                        </div>
                    );
                })}
                {currentZones.length === 0 && (
                    <div className="col-span-3 p-4 text-gray-500 text-center">
                        No zones available.
                    </div>
                )}
            </div>

            {/* Pagination component */}
            {zones.length > itemsPerPage && (
                <Pagination
                    totalItems={zones.length}
                    itemsPerPage={itemsPerPage}
                    currentPage={currentPage}
                    onPageChange={handlePageChange}
                    className="mt-6"
                />
            )}
        </div>
    );
}
