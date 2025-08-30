import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useRef, useState, useMemo } from 'react';
import { getZones } from '../api';
import { useErrorHandler } from '../utils/errorHandling';
import { useCurrentZone } from '../contexts/WorldStateContext';
import { Pagination } from './ui/Pagination';
// Cache duration in milliseconds (5 minutes)
const CACHE_DURATION = 5 * 60 * 1000;
// Status badge component
const StatusBadge = ({ explored }) => {
    return (_jsx("span", { className: `px-2 py-0.5 rounded-full text-xs ${explored
            ? 'bg-green-100 text-green-800'
            : 'bg-purple-100 text-purple-800'}`, "aria-label": explored ? 'Explored zone' : 'New zone', children: explored ? 'Explored' : 'New' }));
};
export default function ZoneViewer() {
    const [zones, setZones] = useState([]);
    const [error, setError] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [changingZone, setChangingZone] = useState(null);
    const { handleApiError, withErrorHandling } = useErrorHandler();
    const { currentZone, setCurrentZone } = useCurrentZone();
    // Search and filter state
    const [searchTerm, setSearchTerm] = useState('');
    const [filterStatus, setFilterStatus] = useState('all');
    // Pagination state
    const [currentPage, setCurrentPage] = useState(1);
    const [itemsPerPage] = useState(6); // Show 6 zones per page (3x2 grid)
    // Cache reference
    const cacheRef = useRef({
        data: null,
        timestamp: 0
    });
    // Last request time reference for debouncing
    const lastRequestTimeRef = useRef(0);
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
            }
            catch (err) {
                handleApiError(err, 'Failed to fetch zones');
                setError(err);
            }
            finally {
                setIsLoading(false);
            }
        };
        fetchZones();
        // Set up polling
        const intervalId = setInterval(fetchZones, 10000);
        // Clean up interval on unmount
        return () => clearInterval(intervalId);
    }, [handleApiError]);
    // Reset to first page when search or filter changes
    useEffect(() => {
        setCurrentPage(1);
    }, [searchTerm, filterStatus]);
    // Filter and search zones
    const filteredZones = useMemo(() => {
        return zones.filter(zone => {
            // Apply search filter
            const matchesSearch = zone.name.toLowerCase().includes(searchTerm.toLowerCase());
            // Apply status filter
            let matchesStatus = true;
            if (filterStatus === 'explored') {
                matchesStatus = zone.explored === true;
            }
            else if (filterStatus === 'new') {
                matchesStatus = zone.explored === false;
            }
            return matchesSearch && matchesStatus;
        });
    }, [zones, searchTerm, filterStatus]);
    // Calculate pagination
    const indexOfLastItem = currentPage * itemsPerPage;
    const indexOfFirstItem = indexOfLastItem - itemsPerPage;
    const currentZones = filteredZones.slice(indexOfFirstItem, indexOfLastItem);
    if (error)
        return _jsx("div", { className: "p-4 border rounded-xl shadow bg-white text-red-500", children: "Error loading zones." });
    if (isLoading && !zones.length)
        return _jsx("div", { className: "p-4 border rounded-xl shadow bg-white", children: "Loading zones..." });
    // Function to handle zone selection
    const handleZoneSelect = withErrorHandling(async (zoneName) => {
        // Don't do anything if we're already changing to this zone
        if (changingZone === zoneName)
            return;
        try {
            // Set the changing zone to show loading state
            setChangingZone(zoneName);
            // Update the zone using the setCurrentZone function from WorldStateContext
            // This will update both the local state and make the API call
            await setCurrentZone(zoneName);
        }
        catch (error) {
            console.error('Failed to change zone:', error);
            // Error handling is done in the setCurrentZone function
        }
        finally {
            // Clear the changing zone state
            setChangingZone(null);
        }
    }, "Failed to change zone");
    // Handle page change
    const handlePageChange = (pageNumber) => {
        setCurrentPage(pageNumber);
        // Scroll to top of the grid when page changes
        document.getElementById('zones-grid')?.scrollIntoView({ behavior: 'smooth' });
    };
    return (_jsxs("div", { className: "p-4 border rounded-xl shadow bg-white", children: [_jsx("h2", { className: "text-xl font-bold mb-4", id: "zones-heading", children: "Zones" }), _jsxs("div", { className: "mb-4 flex flex-col sm:flex-row gap-2", children: [_jsxs("div", { className: "flex-1", children: [_jsx("label", { htmlFor: "zone-search", className: "sr-only", children: "Search zones" }), _jsxs("div", { className: "relative", children: [_jsx("div", { className: "absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none", children: _jsx("svg", { className: "h-5 w-5 text-gray-400", fill: "currentColor", viewBox: "0 0 20 20", children: _jsx("path", { fillRule: "evenodd", d: "M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z", clipRule: "evenodd" }) }) }), _jsx("input", { id: "zone-search", type: "text", placeholder: "Search zones...", value: searchTerm, onChange: (e) => setSearchTerm(e.target.value), className: "block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm" })] })] }), _jsxs("div", { children: [_jsx("label", { htmlFor: "status-filter", className: "sr-only", children: "Filter by status" }), _jsxs("select", { id: "status-filter", value: filterStatus, onChange: (e) => setFilterStatus(e.target.value), className: "block w-full pl-3 pr-10 py-2 border border-gray-300 rounded-md leading-5 bg-white focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm", children: [_jsx("option", { value: "all", children: "All Zones" }), _jsx("option", { value: "explored", children: "Explored Only" }), _jsx("option", { value: "new", children: "New Only" })] })] })] }), _jsxs("div", { className: "mb-2 text-sm text-gray-500", children: ["Showing ", currentZones.length, " of ", filteredZones.length, " zones", searchTerm && ` matching "${searchTerm}"`, filterStatus !== 'all' && ` (${filterStatus} only)`] }), _jsxs("div", { id: "zones-grid", className: "grid grid-cols-1 md:grid-cols-3 gap-4", role: "radiogroup", "aria-labelledby": "zones-heading", "aria-live": "polite", children: [currentZones.map((zone) => {
                        const isSelected = currentZone === zone.name;
                        const isChanging = changingZone === zone.name;
                        return (_jsxs("div", { className: `${isSelected ? 'bg-blue-200 border-blue-500' : 'bg-gray-100'} shadow rounded p-4 cursor-pointer transition-colors duration-200 hover:bg-blue-100 border-2 ${isSelected ? 'border-blue-500' : 'border-transparent'} ${isChanging ? 'opacity-70' : ''} focus:outline-none focus:ring-2 focus:ring-blue-500`, onClick: () => handleZoneSelect(zone.name), onKeyDown: (e) => {
                                if (e.key === 'Enter' || e.key === ' ') {
                                    e.preventDefault();
                                    handleZoneSelect(zone.name);
                                }
                            }, role: "radio", "aria-checked": isSelected, "aria-busy": isChanging, tabIndex: 0, "aria-label": `Zone ${zone.name}${isSelected ? ', currently selected' : ''}${isChanging ? ', changing' : ''}`, children: [_jsxs("div", { className: "flex justify-between items-center mb-2", children: [_jsx("div", { className: "font-semibold", children: zone.name }), _jsx(StatusBadge, { explored: zone.explored })] }), _jsxs("div", { className: "mb-2 text-sm", children: [_jsx("span", { className: "font-medium", children: "Origin:" }), " ", zone.origin || 'Unknown'] }), _jsxs("div", { className: "mb-2 text-sm", children: [_jsx("span", { className: "font-medium", children: "Complexity:" }), " ", zone.complexity || 'N/A'] }), _jsxs("div", { className: "mb-2", children: [_jsx("span", { className: "font-medium text-sm", children: "Modifiers:" }), _jsx("div", { className: "mt-1 flex flex-wrap gap-1", children: Array.isArray(zone.modifiers) && zone.modifiers.length > 0 ? (zone.modifiers.map((mod, idx) => (_jsx("span", { className: "px-2 py-0.5 bg-gray-200 rounded-full text-xs", children: mod }, idx)))) : (_jsx("span", { className: "text-xs text-gray-500", children: "None" })) })] }), _jsxs("div", { children: [_jsx("span", { className: "font-medium text-sm", children: "Emotion:" }), ' ', _jsx("span", { className: `emotion-badge emotion-${(zone.emotion || 'neutral').toLowerCase()}`, "aria-label": `Emotion: ${zone.emotion || 'Neutral'}`, children: zone.emotion || 'Neutral' })] }), isSelected && (_jsx("div", { className: "mt-2 text-blue-700 font-semibold", "aria-hidden": "true", children: "\u2713 Currently Selected" })), isChanging && (_jsx("div", { className: "mt-2 text-orange-500 font-semibold animate-pulse", "aria-live": "polite", children: "\u27F3 Changing Zone..." }))] }, zone.id));
                    }), currentZones.length === 0 && (_jsx("div", { className: "col-span-3 p-4 text-gray-500 text-center", children: searchTerm || filterStatus !== 'all'
                            ? 'No zones match your search or filter criteria.'
                            : 'No zones available.' }))] }), filteredZones.length > itemsPerPage && (_jsx(Pagination, { totalItems: filteredZones.length, itemsPerPage: itemsPerPage, currentPage: currentPage, onPageChange: handlePageChange, className: "mt-6" }))] }));
}
