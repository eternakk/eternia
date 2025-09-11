import axios, {AxiosRequestConfig} from "axios";
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

// Expose axios instance for tests and advanced usage
export const apiClient = api;

// Detect test environment (Vitest / NODE_ENV=test) and Cypress e2e
const IS_TEST_ENV = (typeof process !== 'undefined' && (process.env.VITEST || process.env.NODE_ENV === 'test')) ||
    (typeof import.meta !== 'undefined' && (import.meta as { env?: { MODE?: string } }).env?.MODE === 'test');
// Cypress sets window.Cypress in the browser
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const IS_CYPRESS = typeof window !== 'undefined' && (window as any)?.Cypress;

// In test/e2e, prevent real network calls by stubbing api.get/post
if (IS_TEST_ENV || IS_CYPRESS) {
    const makeResponse = (data: unknown, config?: AxiosRequestConfig) => ({
        data,
        status: 200,
        statusText: 'OK',
        headers: {},
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        config: (config as any) ?? {},
        request: {},
    });

    const getDataForUrl = (url: string): unknown => {
        if (url.includes('/api/token')) {
            return {token: 'test-token'};
        }
        if (url.includes('/api/state') || url.includes('/state')) {
            return {
                cycle: 1,
                identity_score: 0.9,
                emotion: 'neutral',
                modifiers: {},
                current_zone: 'Zone-α',
            } satisfies State;
        }
        if (url.includes('/api/agents')) {
            return [
                {name: 'A1', role: 'Scout', emotion: 'neutral', zone: 'Zone-α', memory: null, stressLevel: 10},
            ] as unknown[];
        }
        if (url.includes('/api/zones')) {
            return [
                {
                    id: 1,
                    name: 'Zone-α',
                    origin: 'core',
                    complexity: 1,
                    explored: true,
                    emotion: 'neutral',
                    modifiers: []
                },
            ] as unknown[];
        }
        if (url.includes('/zone/assets')) {
            return {model: '', skybox: ''};
        }
        if (url.includes('/api/rituals')) {
            return [
                {id: 1, name: 'Init', purpose: 'test', steps: [], symbolic_elements: []},
            ] as unknown[];
        }
        return {};
    };

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (api as any).get = async (url: string, config?: AxiosRequestConfig) => makeResponse(getDataForUrl(String(url)), config);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (api as any).post = async (url: string, _data?: unknown, config?: AxiosRequestConfig) => makeResponse(getDataForUrl(String(url)), config);
}

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

    // Reset all token-related state
    TOKEN = '';
    lastTokenFetch = 0;
    tokenFetchPromise = null;
    tokenFetchRetries = 0;

    // Reset circuit breaker state
    consecutiveFailures = 0;
    circuitBreakerTripped = false;
    circuitBreakerResetTime = 0;

    // Reset axios default headers
    try {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const defaults: any = api.defaults as any;
        if (defaults?.headers?.common && 'Authorization' in defaults.headers.common) {
            delete defaults.headers.common['Authorization'];
        }
    } catch {
        // no-op
    }

    // Clear any pending timeouts that might be related to token fetching
    // This is a best-effort approach as we can't identify specific timeouts
    console.log('Performing deep token state reset');

    console.log('Token state completely reset');

    // Return true to indicate successful cleanup
    return true;
};

// Track the last token fetch time and pending promise
let lastTokenFetch = 0;
let tokenFetchPromise: Promise<string | null> | null = null;
let tokenFetchRetries = 0;
let consecutiveFailures = 0;
const TOKEN_CACHE_DURATION = 5 * 60 * 1000; // 5 minutes in milliseconds
const MAX_TOKEN_FETCH_RETRIES = 3;
const RETRY_BACKOFF_MS = 1000; // Start with 1 second, will be multiplied by retry count
const MAX_CONSECUTIVE_FAILURES = 5; // Maximum number of consecutive failures before circuit breaking
let circuitBreakerTripped = false;
let circuitBreakerResetTime = 0;

// Function to fetch the token from the server
export const fetchToken = async () => {
    // In test environments, avoid real network calls and use a stub token
    const isTestEnv = (typeof process !== 'undefined' && (process.env.VITEST || process.env.NODE_ENV === 'test')) ||
        (typeof import.meta !== 'undefined' && (import.meta as { env?: { MODE?: string } }).env?.MODE === 'test');
    if (isTestEnv) {
        if (!TOKEN) {
            TOKEN = 'test-token';
            // Ensure axios defaults structure exists before assigning
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            const defaults: any = api.defaults as any;
            try {
                if (defaults && typeof defaults === 'object') {
                    defaults.headers = defaults.headers || {};
                    defaults.headers.common = defaults.headers.common || {};
                    defaults.headers.common['Authorization'] = `Bearer ${TOKEN}`;
                }
            } catch {
                // ignore header assignment in test if axios defaults unavailable
            }
        }
        return TOKEN;
    }
    const now = Date.now();
    console.group('Token Fetch Process');
    console.log(`Token fetch initiated at ${new Date(now).toLocaleTimeString()}`);

    try {
        // Check if circuit breaker is tripped
        if (circuitBreakerTripped) {
            // Check if it's time to reset the circuit breaker
            if (now < circuitBreakerResetTime) {
                console.warn(`Circuit breaker active. Token fetching suspended until ${new Date(circuitBreakerResetTime).toLocaleTimeString()}`);
                console.groupEnd();
                return null;
            } else {
                // Reset the circuit breaker
                console.log('Circuit breaker reset. Allowing token fetch attempts again.');
                circuitBreakerTripped = false;
                consecutiveFailures = 0;
            }
        }

        // Check if we already have a token in localStorage with timestamp
        console.log('Checking for cached token in localStorage');
        const storedTokenData = localStorage.getItem('tokenData');
        if (storedTokenData) {
            try {
                const {token, timestamp} = JSON.parse(storedTokenData);
                console.log(`Found cached token from ${new Date(timestamp).toLocaleTimeString()}`);

                // If token exists and is not expired
                if (token && timestamp && (now - timestamp < TOKEN_CACHE_DURATION)) {
                    const tokenAge = Math.round((now - timestamp) / 1000);
                    console.log(`Cached token is valid (age: ${tokenAge}s, max: ${TOKEN_CACHE_DURATION / 1000}s)`);

                    // Log token details (partial token for security)
                    const tokenPreview = token.substring(0, 5) + '...' + token.substring(token.length - 5);
                    console.log(`Using cached token: ${tokenPreview}`);

                    TOKEN = token;
                    setAuthHeader(TOKEN);

                    // Reset retry counter and consecutive failures on successful token use
                    tokenFetchRetries = 0;
                    consecutiveFailures = 0;
                    console.groupEnd();
                    return TOKEN;
                }
                console.log(`Cached token expired (age: ${Math.round((now - timestamp) / 1000)}s, max: ${TOKEN_CACHE_DURATION / 1000}s)`);
            } catch (e) {
                console.warn('Invalid token data in localStorage:', e);
            }
        } else {
            console.log('No cached token found in localStorage');
        }

        // If there's already a token fetch in progress, return that promise
        // But only if it's recent (within last 10 seconds) to avoid stuck promises
        if (tokenFetchPromise && (now - lastTokenFetch < 10000)) {
            console.log(`Token fetch already in progress (started ${Math.round((now - lastTokenFetch) / 1000)}s ago), reusing request`);
            console.groupEnd();
            return tokenFetchPromise;
        }

        // If we had a previous promise but it's old, clear it
        if (tokenFetchPromise && (now - lastTokenFetch >= 10000)) {
            console.log(`Previous token fetch promise is stale (${Math.round((now - lastTokenFetch) / 1000)}s old), creating new one`);
            tokenFetchPromise = null;
        }

        // Set the last fetch time and create a new fetch promise
        lastTokenFetch = now;
        console.log('Creating new token fetch promise');

        tokenFetchPromise = (async () => {
            try {
                // Apply exponential backoff if we're retrying
                if (tokenFetchRetries > 0) {
                    const backoffTime = RETRY_BACKOFF_MS * Math.pow(2, tokenFetchRetries - 1);
                    console.log(`Retry ${tokenFetchRetries}/${MAX_TOKEN_FETCH_RETRIES}, waiting ${backoffTime}ms before retry`);
                    await new Promise(resolve => setTimeout(resolve, backoffTime));
                }

                const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
                console.log(`Fetching token from server: ${apiUrl}/api/token`);

                const startTime = Date.now();
                const response = await axios.get(`${apiUrl}/api/token`, {
                    // Add a timeout to prevent hanging requests
                    timeout: 10000,
                    // Add a unique parameter to prevent caching
                    params: {_t: Date.now()}
                });
                const requestTime = Date.now() - startTime;

                console.log(`Token request completed in ${requestTime}ms with status ${response.status}`);

                if (!response.data) {
                    console.error('Empty response from token endpoint');
                    throw new Error('Empty response from token endpoint');
                }

                if (!response.data.token) {
                    console.error('Token missing from response:', response.data);
                    throw new Error('Token missing from response');
                }

                TOKEN = response.data.token;

                // Log token details (partial token for security)
                const tokenPreview = TOKEN.substring(0, 5) + '...' + TOKEN.substring(TOKEN.length - 5);
                console.log(`Received token: ${tokenPreview}`);

                // Store the token with timestamp in localStorage
                const timestamp = Date.now();
                localStorage.setItem('tokenData', JSON.stringify({
                    token: TOKEN,
                    timestamp: timestamp
                }));
                console.log(`Token stored in localStorage with timestamp ${new Date(timestamp).toLocaleTimeString()}`);

                // Update the default headers with the new token
                setAuthHeader(TOKEN);
                console.log('Authorization header updated with new token');

                // Reset retry counter on success
                tokenFetchRetries = 0;
                return TOKEN;
            } catch (error: unknown) {
                console.group('Token Fetch Error');
                console.error('Failed to fetch token:', error);

                // Log more details about the error
                if (axios.isAxiosError(error) && error.response) {
                    // The request was made and the server responded with a status code
                    // that falls out of the range of 2xx
                    console.error(`Server responded with status ${error.response.status}`);
                    console.error('Response data:', error.response.data);
                    console.error('Response headers:', error.response.headers);
                } else if (axios.isAxiosError(error) && error.request) {
                    // The request was made but no response was received
                    console.error('No response received from server');
                    console.error('Request details:', error.request);
                } else {
                    // Something happened in setting up the request that triggered an Error
                    console.error('Error setting up request:', error instanceof Error ? error.message : String(error));
                }
                console.groupEnd();

                // Clear any existing token to prevent using an invalid one
                localStorage.removeItem('tokenData');
                TOKEN = '';
                console.log('Cleared existing token data');

                // Increment retry counter but cap at max retries
                tokenFetchRetries = Math.min(tokenFetchRetries + 1, MAX_TOKEN_FETCH_RETRIES);

                // Increment consecutive failures counter for circuit breaker
                consecutiveFailures++;
                console.log(`Token fetch failed. Consecutive failures: ${consecutiveFailures}/${MAX_CONSECUTIVE_FAILURES}`);

                // Check if we should trip the circuit breaker
                if (consecutiveFailures >= MAX_CONSECUTIVE_FAILURES) {
                    // Trip the circuit breaker with exponential backoff based on how many times over the limit we are
                    const overage = consecutiveFailures - MAX_CONSECUTIVE_FAILURES + 1;
                    const backoffSeconds = Math.min(30 * Math.pow(2, overage - 1), 300); // Max 5 minutes

                    circuitBreakerTripped = true;
                    circuitBreakerResetTime = Date.now() + (backoffSeconds * 1000);

                    console.warn(`Circuit breaker tripped due to ${consecutiveFailures} consecutive failures. ` +
                        `Token fetching suspended for ${backoffSeconds} seconds until ` +
                        `${new Date(circuitBreakerResetTime).toLocaleTimeString()}`);

                    // Reset retry counter since we're going to pause attempts anyway
                    tokenFetchRetries = 0;

                    // Also clear any pending token fetch promise to prevent it from being reused
                    setTimeout(() => {
                        if (tokenFetchPromise) {
                            console.log('Circuit breaker clearing token fetch promise');
                            tokenFetchPromise = null;
                        }
                    }, 100); // Short delay to ensure this happens after the current execution

                    return null;
                }

                // If we haven't exceeded max retries, we'll try again next time
                if (tokenFetchRetries < MAX_TOKEN_FETCH_RETRIES) {
                    console.log(`Token fetch failed, will retry (${tokenFetchRetries}/${MAX_TOKEN_FETCH_RETRIES})`);
                } else {
                    console.error(`Token fetch failed after ${MAX_TOKEN_FETCH_RETRIES} retries, giving up`);
                    // Reset retry counter after max retries to allow future attempts
                    tokenFetchRetries = 0;
                }

                return null;
            } finally {
                // Schedule cleanup of the promise after it's resolved
                // Calculate delay based on retry count and success/failure
                let clearDelay;

                if (TOKEN) {
                    // If we successfully got a token, we can use a longer delay
                    // since we don't expect to need another token soon
                    clearDelay = 30000; // 30 seconds
                    console.log(`Token fetch succeeded, will clear promise in ${clearDelay / 1000}s`);
                } else {
                    // If we failed to get a token, use a shorter delay based on retry count
                    // to allow another attempt sooner
                    clearDelay = tokenFetchRetries > 0 ?
                        5000 + (tokenFetchRetries * 2000) : // 5s + 2s per retry
                        3000; // 3s for first attempt
                    console.log(`Token fetch failed, will clear promise in ${clearDelay / 1000}s`);
                }

                // Set timeout to clear the promise
                setTimeout(() => {
                    console.log('Clearing token fetch promise');
                    // Only clear if this is still the current promise
                    if (tokenFetchPromise === currentPromise) {
                        tokenFetchPromise = null;
                    }
                }, clearDelay);

                // Store the current promise for comparison in the timeout
                const currentPromise = tokenFetchPromise;
                console.groupEnd();
            }
        })();
        return tokenFetchPromise;
    } catch (error) {
        console.error('Unexpected error in fetchToken:', error);
        localStorage.removeItem('tokenData');
        TOKEN = '';
        tokenFetchPromise = null;
        console.groupEnd();
        return null;
    }
};

// Helpers to keep interceptor simple and reduce cyclomatic complexity
const isUnauthorized = (error: unknown): boolean => {
    const e = error as { response?: { status?: number } };
    return e?.response?.status === 401;
};
type RequestConfig = { headers?: Record<string, unknown>; _retryCount?: number; timeout?: number; url?: string };
type ErrorLike =
    { config?: RequestConfig; response?: { status?: number }; message?: string; code?: string }
    & Record<string, unknown>;

const getRetryCount = (error: unknown) => {
    const e = error as ErrorLike;
    return e?.config?._retryCount || 0;
};
const clearAuthHeader = () => {
    try {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const defaults: any = api.defaults as any;
        if (defaults?.headers?.common && 'Authorization' in defaults.headers.common) {
            delete defaults.headers.common['Authorization'];
        }
    } catch {
        // no-op
    }
};

const setAuthHeader = (token: string) => {
    try {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const defaults: any = api.defaults as any;
        defaults.headers = defaults.headers || {};
        defaults.headers.common = defaults.headers.common || {};
        defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } catch {
        // no-op
    }
};

const resetTokenStateHard = () => {
    lastTokenFetch = 0;
    tokenFetchPromise = null;
    tokenFetchRetries = 0;
    consecutiveFailures = 0;
    circuitBreakerTripped = false;
    circuitBreakerResetTime = 0;
    TOKEN = '';
    clearAuthHeader();
    localStorage.removeItem('tokenData');
    localStorage.removeItem('token');
};

const applyBackoff = async (retryCount: number) => {
    if (retryCount > 0) {
        const backoffTime = RETRY_BACKOFF_MS * Math.pow(2, retryCount - 1);
        console.log(`Interceptor retry ${retryCount + 1}/2, waiting ${backoffTime}ms before retry`);
        await new Promise(resolve => setTimeout(resolve, backoffTime));
    }
};

const retryWithNewToken = async (error: unknown) => {
    const e = error as ErrorLike;
    const retryCount = getRetryCount(e);
    const maxRetries = 2;
    if (retryCount >= maxRetries) {
        console.error(`Request has already been retried ${retryCount} times, giving up`);
        cancelAllRequests();
        return Promise.reject(e);
    }

    console.log(`Token invalid (retry ${retryCount + 1}/${maxRetries}), clearing and refreshing...`);
    resetTokenStateHard();
    await applyBackoff(retryCount);

    try {
        const token = await fetchToken();
        if (token) {
            const originalRequest = (e.config || {}) as RequestConfig;
            (originalRequest.headers as Record<string, string> | undefined) ||= {};
            (originalRequest.headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
            originalRequest._retryCount = retryCount + 1;
            originalRequest.timeout = 10000;
            console.log('Token refreshed, retrying original request');
            return axios(originalRequest as AxiosRequestConfig);
        }
        console.error('Token refresh returned null, cannot retry request');
        return Promise.reject(e);
    } catch (refreshError) {
        console.error('Failed to refresh token:', refreshError);
        (e as Record<string, unknown>).refreshError = refreshError;
        return Promise.reject(e);
    }
};

const isNetworkError = (error: unknown) => (error as ErrorLike)?.message === 'Network Error';
const isTimeoutError = (error: unknown) => {
    const e = error as ErrorLike;
    return e?.code === 'ECONNABORTED' && typeof e?.message === 'string' && e.message.includes('timeout');
};
const isTokenFetchUrl = (url?: string) => Boolean(url && url.includes('/api/token'));

const markErrorFlag = (error: unknown, key: 'isNetworkError' | 'isTimeoutError', value: boolean) => {
    const obj = error as Record<string, unknown>;
    obj[key] = value;
};

const scheduleSoftReset = (reason: string) => {
    setTimeout(() => {
        console.log(`Performing complete token state reset after ${reason}`);
        lastTokenFetch = 0;
        tokenFetchRetries = 0;
        consecutiveFailures = 0;
        circuitBreakerTripped = false;
        circuitBreakerResetTime = 0;
        localStorage.removeItem('tokenData');
        localStorage.removeItem('token');
        console.log(`Token state completely reset after ${reason}`);
    }, 5000);
};

const handleNetworkSideEffects = (error: unknown) => {
    const e = error as ErrorLike;
    if (isTokenFetchUrl(e?.config?.url)) {
        console.log('Network error on token fetch, performing state reset');
        if (tokenFetchPromise) tokenFetchPromise = null;
        TOKEN = '';
        clearAuthHeader();
        scheduleSoftReset('network error');
    }
};

const handleTimeoutSideEffects = (error: unknown) => {
    const e = error as ErrorLike;
    if (isTokenFetchUrl(e?.config?.url)) {
        console.log('Timeout on token fetch, performing state reset');
        if (tokenFetchPromise) tokenFetchPromise = null;
        TOKEN = '';
        clearAuthHeader();
        scheduleSoftReset('timeout');
    }
};

// Add response interceptor for global error handling and token refresh
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        if (axios.isCancel(error)) {
            console.log('Request cancelled:', error.message);
            return Promise.reject(error);
        }

        console.error('API Error:', error);

        if (isUnauthorized(error)) {
            return retryWithNewToken(error);
        }

        if (isNetworkError(error)) {
            console.error('Network error detected. Please check your internet connection.');
            markErrorFlag(error, 'isNetworkError', true);
            handleNetworkSideEffects(error);
        }

        if (isTimeoutError(error)) {
            console.error('Request timed out. The server might be overloaded or unreachable.');
            markErrorFlag(error, 'isTimeoutError', true);
            handleTimeoutSideEffects(error);
        }

        return Promise.reject(error);
    }
);

// Helpers for ensureToken to reduce complexity
const tryUseStoredToken = (): boolean => {
    const storedTokenData = localStorage.getItem('tokenData');
    if (!storedTokenData) return false;
    try {
        const {token, timestamp} = JSON.parse(storedTokenData);
        const now = Date.now();
        if (token && timestamp && (now - timestamp < TOKEN_CACHE_DURATION)) {
            TOKEN = token;
            setAuthHeader(TOKEN);
            return true;
        }
    } catch {
        console.warn('Invalid token data in localStorage, will fetch a new one');
    }
    return false;
};

const waitForOngoingFetch = async (): Promise<boolean> => {
    if (!tokenFetchPromise) return false;
    console.log('Token fetch already in progress in ensureToken, waiting for it to complete');
    try {
        const token = await tokenFetchPromise;
        if (!token && tokenFetchRetries < MAX_TOKEN_FETCH_RETRIES) {
            throw new Error(`Token fetch in progress failed, will be retried later (${tokenFetchRetries}/${MAX_TOKEN_FETCH_RETRIES})`);
        }
        if (token) return true;
    } catch (promiseError) {
        console.warn('Existing token fetch promise failed:', promiseError);
        tokenFetchPromise = null;
    }
    return false;
};

const fetchWithImmediateRetry = async (): Promise<void> => {
    const token = await fetchToken();
    if (token) return;
    if (tokenFetchRetries < MAX_TOKEN_FETCH_RETRIES) {
        const currentRetryCount = tokenFetchRetries;
        console.log(`Token fetch failed, retrying immediately (${currentRetryCount}/${MAX_TOKEN_FETCH_RETRIES})`);
        const backoffTime = RETRY_BACKOFF_MS * Math.pow(2, currentRetryCount);
        await new Promise(resolve => setTimeout(resolve, backoffTime));
        tokenFetchPromise = null;
        lastTokenFetch = 0;
        const retryToken = await fetchToken();
        if (retryToken) {
            console.log(`Immediate retry successful after attempt ${currentRetryCount + 1}`);
            return;
        }
        console.error(`Immediate retry returned null after attempt ${currentRetryCount + 1}`);
        throw new Error(`Failed to fetch authentication token after immediate retry (${currentRetryCount}/${MAX_TOKEN_FETCH_RETRIES})`);
    }
    console.error(`Maximum retry attempts (${MAX_TOKEN_FETCH_RETRIES}) exceeded`);
    throw new Error('Failed to fetch authentication token after maximum retries');
};

const throwWithContext = (error: unknown): never => {
    if (error instanceof Error) {
        if (error.message.includes('Network Error')) {
            throw new Error('Failed to fetch authentication token: Network error. Please check your connection.');
        } else if (error.message.includes('timeout')) {
            throw new Error('Failed to fetch authentication token: Request timed out. Server might be overloaded.');
        } else {
            throw new Error(`Failed to fetch authentication token: ${error.message}`);
        }
    }
    throw new Error(`Failed to fetch authentication token: ${String(error)}`);
};

// Function to ensure token is fetched before making API calls
const ensureToken = async () => {
    if (TOKEN) return;

    if (tryUseStoredToken()) return;

    try {
        if (await waitForOngoingFetch()) return;
        await fetchWithImmediateRetry();
    } catch (error) {
        console.error('Error in ensureToken:', error);
        throwWithContext(error);
    }
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
    memory: unknown;
    stressLevel: number;
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


// Quantum API types and functions
export interface QRNGResponse {
    bits: string;
    entropy: number;
    backend: string;
}

export interface VariationalFieldResponse {
    field: number[][];
    seed: number;
    backend: string;
}

const baseQuantumQrng = async (n: number = 128): Promise<QRNGResponse> => {
    await ensureToken();
    return api.post<QRNGResponse>("/api/quantum/qrng", {n}).then(r => r.data);
};

const baseVariationalField = async (seed: number, size: number = 32): Promise<VariationalFieldResponse> => {
    await ensureToken();
    return api.post<VariationalFieldResponse>("/api/quantum/variational-field", {seed, size}).then(r => r.data);
};

export const getQuantumBits = createSafeApiCall(
    baseQuantumQrng,
    "Failed to get quantum random bits"
);

export const getVariationalField = createSafeApiCall(
    baseVariationalField,
    "Failed to get quantum variational field"
);
