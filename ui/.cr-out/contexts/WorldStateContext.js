import { jsx as _jsx } from "react/jsx-runtime";
import { createContext, useContext, useReducer, useEffect, useState, useRef, useCallback } from 'react';
import axios from 'axios';
import { getState, fetchToken, cancelAllRequests, changeZone } from '../api';
import { useErrorHandler } from '../utils/errorHandling';
// Define the initial state
const initialState = {
    worldState: null,
    isLoading: false,
    error: null,
    lastUpdated: null,
    currentZone: null,
    zoneModifiers: {},
};
// Create the reducer function
const worldStateReducer = (state, action) => {
    switch (action.type) {
        case 'FETCH_STATE_START':
            return {
                ...state,
                isLoading: true,
                error: null,
            };
        case 'FETCH_STATE_SUCCESS':
            return {
                ...state,
                worldState: action.payload,
                isLoading: false,
                error: null,
                lastUpdated: Date.now(),
                currentZone: action.payload.current_zone || state.currentZone,
                zoneModifiers: action.payload.modifiers || state.zoneModifiers,
            };
        case 'FETCH_STATE_ERROR':
            return {
                ...state,
                isLoading: false,
                error: action.payload,
            };
        case 'SET_LOADING':
            return {
                ...state,
                isLoading: action.payload,
            };
        case 'SET_CURRENT_ZONE':
            return {
                ...state,
                currentZone: action.payload,
            };
        case 'SET_ZONE_MODIFIERS':
            return {
                ...state,
                zoneModifiers: action.payload,
            };
        default:
            return state;
    }
};
const WorldStateContext = createContext(undefined);
export const WorldStateProvider = ({ children, refreshInterval = 10000, // Increased from 3000ms to 10000ms (10 seconds)
 }) => {
    const [state, dispatch] = useReducer(worldStateReducer, initialState);
    const { handleApiError } = useErrorHandler();
    const [isPageVisible, setIsPageVisible] = useState(true);
    const lastRequestTimeRef = useRef(0);
    const minRequestInterval = 1000; // Minimum time between requests in ms
    // Function to refresh the state
    const refreshState = async () => {
        var _a;
        // Check if enough time has passed since the last request
        const now = Date.now();
        if (now - lastRequestTimeRef.current < minRequestInterval) {
            return; // Skip this request if it's too soon after the last one
        }
        // Update the last request time
        lastRequestTimeRef.current = now;
        dispatch({ type: 'FETCH_STATE_START' });
        try {
            // Don't explicitly fetch token here - the API call will handle token if needed
            // through the axios interceptors in api.ts
            const data = await getState();
            if (data) {
                // Only update state if there's an actual change in the data
                if (!state.worldState ||
                    state.worldState.current_zone !== data.current_zone ||
                    state.worldState.cycle !== data.cycle ||
                    state.worldState.emotion !== data.emotion ||
                    state.worldState.identity_score !== data.identity_score ||
                    JSON.stringify(state.worldState.modifiers) !== JSON.stringify(data.modifiers)) {
                    dispatch({ type: 'FETCH_STATE_SUCCESS', payload: data });
                }
                else {
                    // If no changes, just set loading to false
                    dispatch({ type: 'SET_LOADING', payload: false });
                }
            }
            else {
                throw new Error('Failed to fetch state data');
            }
        }
        catch (error) {
            handleApiError(error, 'Failed to fetch world state');
            dispatch({ type: 'FETCH_STATE_ERROR', payload: error });
            // If the error is related to authentication, try to refresh the token
            // but only if we haven't tried too recently to avoid hammering the server
            if (axios.isAxiosError(error) && ((_a = error.response) === null || _a === void 0 ? void 0 : _a.status) === 401) {
                const lastTokenRefresh = parseInt(localStorage.getItem('lastTokenRefresh') || '0');
                const now = Date.now();
                const tokenRefreshCooldown = 30000; // 30 seconds cooldown between 401-triggered refreshes
                if (now - lastTokenRefresh > tokenRefreshCooldown) {
                    console.log('Authentication error during state refresh, attempting to get new token...');
                    try {
                        // Clear existing token data
                        localStorage.removeItem('tokenData');
                        localStorage.removeItem('token'); // Also clear old format token if it exists
                        // Record this refresh attempt
                        localStorage.setItem('lastTokenRefresh', now.toString());
                        // Try to get a new token
                        await fetchToken();
                    }
                    catch (tokenError) {
                        console.error('Failed to refresh token after 401 error:', tokenError);
                    }
                }
                else {
                    console.log(`Skipping token refresh after 401 error (cooldown: ${Math.round((tokenRefreshCooldown - (now - lastTokenRefresh)) / 1000)}s remaining)`);
                }
            }
        }
    };
    // Function to set the current zone
    const setCurrentZone = async (zone) => {
        console.log(`WorldStateContext: Setting zone to ${zone}`);
        // Update local state immediately for responsive UI
        dispatch({ type: 'SET_CURRENT_ZONE', payload: zone });
        // Make API call to update the zone on the backend
        try {
            await changeZone(zone);
            console.log(`WorldStateContext: Successfully updated zone to ${zone} on the backend`);
        }
        catch (error) {
            handleApiError(error, `Failed to change zone to ${zone}`);
            // Note: We don't revert the local state change here to avoid UI flickering
            // The worldState update will eventually sync the state if needed
        }
    };
    // Function to get modifiers for a specific zone
    const getModifiersForZone = useCallback((zone) => {
        return state.zoneModifiers[zone] || [];
    }, [state.zoneModifiers]);
    // Fetch token when component mounts - with limited retries
    useEffect(() => {
        let retryCount = 0;
        const maxRetries = 3;
        const retryDelay = 5000; // 5 seconds between retries
        const initializeToken = async () => {
            try {
                const token = await fetchToken();
                if (!token && retryCount < maxRetries) {
                    console.warn(`Failed to initialize token, retry ${retryCount + 1}/${maxRetries} in ${retryDelay / 1000}s`);
                    retryCount++;
                    // Retry after a delay with exponential backoff
                    setTimeout(() => {
                        initializeToken();
                    }, retryDelay * Math.pow(2, retryCount - 1));
                }
                else if (!token) {
                    console.error('Failed to initialize token after maximum retry attempts');
                }
            }
            catch (error) {
                handleApiError(error, 'Failed to fetch authentication token');
                if (retryCount < maxRetries) {
                    console.warn(`Token fetch error, retry ${retryCount + 1}/${maxRetries} in ${retryDelay / 1000}s`);
                    retryCount++;
                    // Retry after a delay with exponential backoff
                    setTimeout(() => {
                        initializeToken();
                    }, retryDelay * Math.pow(2, retryCount - 1));
                }
                else {
                    console.error('Failed to initialize token after maximum retry attempts');
                }
            }
        };
        initializeToken();
    }, [handleApiError]);
    // Set up visibility change detection and beforeunload handler
    useEffect(() => {
        const handleVisibilityChange = () => {
            setIsPageVisible(document.visibilityState === 'visible');
        };
        // Handle page unload (browser/tab close)
        const handleBeforeUnload = () => {
            // Cancel all pending requests and clear the token
            cancelAllRequests();
            console.log('Application closing: All requests cancelled and token cleared');
        };
        // Set initial visibility state
        handleVisibilityChange();
        // Add event listeners
        document.addEventListener('visibilitychange', handleVisibilityChange);
        window.addEventListener('beforeunload', handleBeforeUnload);
        // Clean up event listeners
        return () => {
            document.removeEventListener('visibilitychange', handleVisibilityChange);
            window.removeEventListener('beforeunload', handleBeforeUnload);
        };
    }, []);
    // Set up polling for state updates, but only when page is visible
    useEffect(() => {
        // Don't set up polling if page is not visible
        if (!isPageVisible)
            return;
        // Initial fetch when becoming visible
        refreshState();
        const intervalId = setInterval(() => {
            refreshState();
        }, refreshInterval);
        return () => clearInterval(intervalId);
    }, [refreshInterval, isPageVisible]);
    return (_jsx(WorldStateContext.Provider, { value: { state, dispatch, refreshState, setCurrentZone, getModifiersForZone }, children: children }));
};
// Create a hook to use the world state context
export const useWorldState = () => {
    const context = useContext(WorldStateContext);
    if (context === undefined) {
        throw new Error('useWorldState must be used within a WorldStateProvider');
    }
    return context;
};
// Convenience hooks for specific parts of the state
export const useCurrentZone = () => {
    const { state, setCurrentZone } = useWorldState();
    return { currentZone: state.currentZone, setCurrentZone };
};
export const useZoneModifiers = () => {
    const { state, getModifiersForZone } = useWorldState();
    return { zoneModifiers: state.zoneModifiers, getModifiersForZone };
};
export default WorldStateContext;
