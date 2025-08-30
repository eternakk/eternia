import { jsx as _jsx } from "react/jsx-runtime";
import { createContext, useContext, useReducer, useEffect, useState, useRef } from 'react';
import axios from 'axios';
import { getState, fetchToken, cancelAllRequests } from '../api';
import { useErrorHandler } from '../utils/errorHandling';
// Define the initial state
const initialState = {
    worldState: null,
    isLoading: false,
    error: null,
    lastUpdated: null,
};
// Create the reducer function
const appStateReducer = (state, action) => {
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
        default:
            return state;
    }
};
const AppStateContext = createContext(undefined);
export const AppStateProvider = ({ children, refreshInterval = 1000, }) => {
    const [state, dispatch] = useReducer(appStateReducer, initialState);
    const { handleApiError } = useErrorHandler();
    const [isPageVisible, setIsPageVisible] = useState(true);
    const lastRequestTimeRef = useRef(0);
    const minRequestInterval = 1000; // Minimum time between requests in ms
    const refreshState = async () => {
        // Check if enough time has passed since the last request
        const now = Date.now();
        if (now - lastRequestTimeRef.current < minRequestInterval) {
            return; // Skip this request if it's too soon after the last one
        }
        // Update the last request time
        lastRequestTimeRef.current = now;
        dispatch({ type: 'FETCH_STATE_START' });
        try {
            // Ensure we have a valid token before making the request
            try {
                await fetchToken();
            }
            catch (tokenError) {
                console.error('Failed to refresh token before state fetch:', tokenError);
                // Continue anyway, as the interceptor will handle token issues
            }
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
            if (axios.isAxiosError(error) && error.response?.status === 401) {
                console.log('Authentication error during state refresh, attempting to get new token...');
                try {
                    // Clear existing token
                    localStorage.removeItem('token');
                    // Try to get a new token
                    await fetchToken();
                }
                catch (tokenError) {
                    console.error('Failed to refresh token after 401 error:', tokenError);
                }
            }
        }
    };
    // Fetch token when component mounts
    useEffect(() => {
        const initializeToken = async () => {
            try {
                const token = await fetchToken();
                if (!token) {
                    console.error('Failed to initialize token');
                    // Retry after a short delay
                    setTimeout(() => {
                        initializeToken();
                    }, 3000);
                }
            }
            catch (error) {
                handleApiError(error, 'Failed to fetch authentication token');
                // Retry after a short delay
                setTimeout(() => {
                    initializeToken();
                }, 3000);
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
    return (_jsx(AppStateContext.Provider, { value: { state, dispatch, refreshState }, children: children }));
};
// Create a hook to use the app state context
export const useAppState = () => {
    const context = useContext(AppStateContext);
    if (context === undefined) {
        throw new Error('useAppState must be used within an AppStateProvider');
    }
    return context;
};
