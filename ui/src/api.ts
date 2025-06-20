import axios from "axios";
import {createSafeApiCall} from "./utils/errorHandling";

// We'll fetch the token from the server
let TOKEN = '';

export interface State {
    cycle: number;
    identity_score: number;
    emotion: string | null;
    modifiers: Record<string, string[]>;
    current_zone: string;          // ← ensure this exists
}

export interface ApiError {
    message: string;
    status?: number;
}

// Create axios instance with default configuration
const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

// Add a cleanup function to cancel all pending requests
export const cancelAllRequests = () => {
    // Create a new CancelToken source
    const source = axios.CancelToken.source();

    // Cancel all pending requests
    source.cancel('Application is closing');

    console.log('All pending API requests cancelled');

    // Clear token data from localStorage
    localStorage.removeItem('tokenData');
    // Also clear old format token if it exists
    localStorage.removeItem('token');
    TOKEN = '';
    // Reset token fetch tracking
    lastTokenFetch = 0;
    tokenFetchPromise = null;
};

// Track the last token fetch time and pending promise
let lastTokenFetch = 0;
let tokenFetchPromise: Promise<string | null> | null = null;
const TOKEN_CACHE_DURATION = 15 * 60 * 1000; // 15 minutes in milliseconds

// Function to fetch the token from the server with retry logic
export const fetchToken = async () => {
    const now = Date.now();

    try {
        // Check if we already have a token in localStorage with timestamp
        const storedTokenData = localStorage.getItem('tokenData');
        if (storedTokenData) {
            try {
                const {token, timestamp} = JSON.parse(storedTokenData);

                // If token exists and is not expired
                if (token && timestamp && (now - timestamp < TOKEN_CACHE_DURATION)) {
                    TOKEN = token;
                    api.defaults.headers.common['Authorization'] = `Bearer ${TOKEN}`;
                    console.log('Using cached token');
                    return TOKEN;
                }
                console.log('Cached token expired, fetching new token...');
            } catch (e) {
                console.warn('Invalid token data in localStorage, fetching new token...');
            }
        } else {
            console.log('No cached token, fetching new token...');
        }

        // If there's already a token fetch in progress, return that promise
        // Extend the window to 10 seconds to reduce likelihood of multiple fetches
        if (tokenFetchPromise && (now - lastTokenFetch < 10000)) {
            console.log('Token fetch already in progress, reusing request');
            return tokenFetchPromise;
        }

        // Set the last fetch time and create a new fetch promise
        lastTokenFetch = now;
        tokenFetchPromise = (async () => {
            // Implement retry with exponential backoff for rate limiting
            let retries = 0;
            const maxRetries = 3;
            const baseDelay = 1000; // Start with 1 second delay

            while (retries <= maxRetries) {
                try {
                    // Use the api instance to ensure consistent configuration
                    const response = await api.get('/api/token');

                    if (!response.data || !response.data.token) {
                        throw new Error('Invalid response from token endpoint');
                    }

                    TOKEN = response.data.token;

                    // Store the token with timestamp in localStorage
                    localStorage.setItem('tokenData', JSON.stringify({
                        token: TOKEN,
                        timestamp: Date.now()
                    }));

                    // Update the default headers with the new token
                    api.defaults.headers.common['Authorization'] = `Bearer ${TOKEN}`;
                    console.log('Token fetched and stored successfully');
                    return TOKEN;
                } catch (error) {
                    // Check if this is a rate limit error (429)
                    if (error.response && error.response.status === 429) {
                        retries++;
                        if (retries <= maxRetries) {
                            // Calculate delay with exponential backoff and jitter
                            const delay = baseDelay * Math.pow(2, retries) + Math.random() * 1000;
                            console.log(`Rate limited, retrying in ${Math.round(delay / 1000)} seconds (attempt ${retries}/${maxRetries})...`);
                            await new Promise(resolve => setTimeout(resolve, delay));
                            continue; // Try again after delay
                        }
                    }

                    console.error('Failed to fetch token:', error);
                    // Clear any existing token to prevent using an invalid one
                    localStorage.removeItem('tokenData');
                    TOKEN = '';
                    return null;
                }
            }

            return null; // All retries failed
        })();

        // Set a longer timeout to clear the promise
        const clearPromise = () => {
            tokenFetchPromise = null;
        };

        // Add a success and error handler to the promise
        tokenFetchPromise.then(clearPromise).catch(clearPromise);

        return tokenFetchPromise;
    } catch (error) {
        console.error('Unexpected error in fetchToken:', error);
        localStorage.removeItem('tokenData');
        TOKEN = '';
        tokenFetchPromise = null;
        return null;
    }
};

// Add response interceptor for global error handling and token refresh
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        console.error("API Error:", error);

        // Check if the error is due to an invalid token (401 Unauthorized)
        if (error.response && error.response.status === 401) {
            console.log("Token invalid, clearing and refreshing...");

            // Clear the stored token data
            localStorage.removeItem('tokenData');
            // Also clear old format token if it exists
            localStorage.removeItem('token');

            // Don't reset TOKEN here to avoid race conditions with other requests
            // Only reset token fetch tracking to force a new token fetch
            lastTokenFetch = 0;

            // Keep the tokenFetchPromise if it exists to avoid multiple simultaneous token requests
            // This ensures that all 401 errors happening at the same time will use the same token refresh request

            // Try to get a new token
            try {
                const newToken = await fetchToken();

                // If the token was refreshed successfully, retry the original request
                if (newToken) {
                    // Get the original request configuration
                    const originalRequest = error.config;
                    // Update the Authorization header with the new token
                    originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
                    // Retry the request with the new token using the api instance
                    return api(originalRequest);
                }
            } catch (refreshError) {
                console.error("Failed to refresh token:", refreshError);
                // Only reset TOKEN and tokenFetchPromise if the refresh failed
                TOKEN = '';
                tokenFetchPromise = null;
            }
        }

        // Handle rate limiting (429 Too Many Requests)
        if (error.response && error.response.status === 429) {
            // Get the original request configuration
            const originalRequest = error.config;

            // Check if we've already tried to retry this request
            if (originalRequest._retryCount === undefined) {
                originalRequest._retryCount = 0;
            }

            // Limit the number of retries
            if (originalRequest._retryCount < 3) {
                originalRequest._retryCount++;

                // Calculate delay with exponential backoff and jitter
                const delay = 1000 * Math.pow(2, originalRequest._retryCount) + Math.random() * 1000;
                console.log(`Rate limited, retrying in ${Math.round(delay / 1000)} seconds (attempt ${originalRequest._retryCount}/3)...`);

                // Wait for the calculated delay
                await new Promise(resolve => setTimeout(resolve, delay));

                // Retry the request
                return api(originalRequest);
            }

            console.error("Rate limit retry attempts exhausted");
        }

        return Promise.reject(error);
    }
);

// Function to ensure token is fetched before making API calls
const ensureToken = async () => {
    // Track token fetch attempts to prevent excessive requests
    const now = Date.now();
    const lastTokenCheck = parseInt(localStorage.getItem('lastTokenCheck') || '0');
    const tokenCheckCooldown = 1000; // 1 second between token checks

    // If we've checked the token very recently, skip the check
    if (now - lastTokenCheck < tokenCheckCooldown) {
        // If we have a token in memory, use it
        if (TOKEN) {
            api.defaults.headers.common['Authorization'] = `Bearer ${TOKEN}`;
            return;
        }
    }

    // Update the last token check time
    localStorage.setItem('lastTokenCheck', now.toString());

    // First check if we have a valid token in memory
    if (TOKEN) {
        // Make sure the Authorization header is set
        api.defaults.headers.common['Authorization'] = `Bearer ${TOKEN}`;
        return;
    }

    // Try to get token from localStorage first
    const storedTokenData = localStorage.getItem('tokenData');
    if (storedTokenData) {
        try {
            const {token, timestamp} = JSON.parse(storedTokenData);
            const tokenAge = now - timestamp;

            // If token exists and is not expired, use it
            if (token && timestamp && (tokenAge < TOKEN_CACHE_DURATION)) {
                TOKEN = token;
                api.defaults.headers.common['Authorization'] = `Bearer ${TOKEN}`;
                console.log(`Using cached token (age: ${Math.round(tokenAge / 1000)}s, expires in: ${Math.round((TOKEN_CACHE_DURATION - tokenAge) / 1000)}s)`);
                return;
            } else if (token && timestamp) {
                console.log(`Cached token expired (age: ${Math.round(tokenAge / 1000)}s, expired ${Math.round((tokenAge - TOKEN_CACHE_DURATION) / 1000)}s ago)`);
            }
        } catch (e) {
            // Invalid token data, will fetch a new one
            console.warn('Invalid token data in localStorage:', e);
        }
    }

    // If no valid token in memory or localStorage, fetch a new one
    // Use a timeout to prevent hanging indefinitely
    let timeoutId: number | null = null;
    let retryCount = 0;
    const maxRetries = 2; // Maximum number of retries

    while (retryCount <= maxRetries) {
        try {
            // Create a promise that rejects after timeout
            const timeoutPromise = new Promise<string | null>((_, reject) => {
                timeoutId = window.setTimeout(() => {
                    reject(new Error('Token fetch timeout'));
                }, 10000); // 10 second timeout
            });

            // Race between token fetch and timeout
            const token = await Promise.race([
                fetchToken(),
                timeoutPromise
            ]);

            if (token) {
                // Ensure the token is set in the headers
                api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
                return; // Success, exit the function
            }

            // If we get here, token is null but no error was thrown
            // Increment retry count and try again if we haven't exceeded max retries
            retryCount++;
            if (retryCount <= maxRetries) {
                console.log(`Token fetch returned null, retrying (${retryCount}/${maxRetries})...`);
                // Add a delay before retrying
                await new Promise(resolve => setTimeout(resolve, 1000 * retryCount));
            }
        } catch (error) {
            // If we get a rate limit error, retry after a delay
            if (error.response && error.response.status === 429) {
                retryCount++;
                if (retryCount <= maxRetries) {
                    const delay = 1000 * Math.pow(2, retryCount) + Math.random() * 1000;
                    console.log(`Rate limited in ensureToken, retrying in ${Math.round(delay / 1000)} seconds (${retryCount}/${maxRetries})...`);
                    await new Promise(resolve => setTimeout(resolve, delay));
                } else {
                    console.error('Rate limit retry attempts exhausted in ensureToken');
                    throw new Error('Failed to fetch authentication token: rate limit exceeded');
                }
            } else {
                // For other errors, log and throw
                console.error('Error ensuring token:', error);
                throw new Error('Failed to fetch authentication token');
            }
        } finally {
            // Clear timeout if it's still active
            if (timeoutId !== null) {
                clearTimeout(timeoutId);
                timeoutId = null;
            }
        }
    }

    // If we've exhausted all retries, throw an error
    throw new Error('Failed to fetch authentication token after multiple attempts');
};

// Base API functions
const baseGetState = async () => {
    await ensureToken();
    return api.get<State>("/state").then(r => r.data);
};

const baseSendCommand = async (a: string) => {
    await ensureToken();
    return api.post(`/command/${a}`);
};

const baseGetCheckpoints = async () => {
    await ensureToken();
    return api.get<string[]>("/checkpoints").then(r => r.data);
};

const baseRollbackTo = async (file?: string) => {
    await ensureToken();
    return api.post("/command/rollback", null, {params: {file}});
};

const baseTriggerRitual = async (id: number) => {
    await ensureToken();
    return api.post(`/api/rituals/trigger/${id}`);
};

const baseSendReward = async (companionName: string, value: number) => {
    await ensureToken();
    return api.post(`/reward/${companionName}`, {value});
};

// Exported API functions with error handling
// Note: These functions will log errors but won't show notifications
// Components should use useErrorHandler().withErrorHandling for notifications
export const getState = createSafeApiCall(
    baseGetState,
    "Failed to fetch state data"
);

export const sendCommand = createSafeApiCall(
    baseSendCommand,
    "Failed to send command"
);

export const getCheckpoints = createSafeApiCall(
    baseGetCheckpoints,
    "Failed to fetch checkpoints"
);

export const rollbackTo = createSafeApiCall(
    baseRollbackTo,
    "Failed to rollback to checkpoint"
);

export const triggerRitual = createSafeApiCall(
    baseTriggerRitual,
    "Failed to trigger ritual"
);

export const sendReward = createSafeApiCall(
    baseSendReward,
    "Failed to send reward"
);

// Define the Zone interface
export interface Zone {
    id: number;
    name: string;
    origin: string;
    complexity: number;
    explored: boolean;
    emotion: string;
    modifiers: string[];
}

// Add function to fetch zones
const baseGetZones = async () => {
    await ensureToken();
    return api.get<Zone[]>("/api/zones").then(r => r.data);
};

export const getZones = createSafeApiCall(
    baseGetZones,
    "Failed to fetch zones"
);

// Add function to fetch zone assets
export interface ZoneAssets {
    model?: string;
    skybox?: string;
}

const baseGetZoneAssets = async (zoneName: string) => {
    await ensureToken();
    return api.get<ZoneAssets>("/zone/assets", {
        params: {name: zoneName}
    }).then(r => r.data);
};

export const getZoneAssets = createSafeApiCall(
    baseGetZoneAssets,
    "Failed to fetch zone assets"
);

// Add function to change the current zone
const baseChangeZone = async (zoneName: string) => {
    await ensureToken();
    return api.post("/api/change_zone", {zone: zoneName});
};

export const changeZone = createSafeApiCall(
    baseChangeZone,
    "Failed to change zone"
);

// Define the Ritual interface
export interface Ritual {
    id: number;
    name: string;
    purpose: string;
    steps: string[];
    symbolic_elements: string[];
}

// Add function to fetch rituals
const baseGetRituals = async () => {
    await ensureToken();
    return api.get<Ritual[]>("/api/rituals").then(r => r.data);
};

export const getRituals = createSafeApiCall(
    baseGetRituals,
    "Failed to fetch rituals"
);

// Define the Agent interface
export interface Agent {
    name: string;
    role: string;
    emotion: string | null;
    zone: string | Zone | null;
    memory: any;
}

// Add function to fetch agents
const baseGetAgents = async () => {
    await ensureToken();
    return api.get<Agent[]>("/api/agents").then(r => r.data);
};

export const getAgents = createSafeApiCall(
    baseGetAgents,
    "Failed to fetch agents"
);
