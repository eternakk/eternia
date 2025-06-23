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
    delete api.defaults.headers.common['Authorization'];

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
        const { token, timestamp } = JSON.parse(storedTokenData);
        console.log(`Found cached token from ${new Date(timestamp).toLocaleTimeString()}`);

        // If token exists and is not expired
        if (token && timestamp && (now - timestamp < TOKEN_CACHE_DURATION)) {
          const tokenAge = Math.round((now - timestamp) / 1000);
          console.log(`Cached token is valid (age: ${tokenAge}s, max: ${TOKEN_CACHE_DURATION/1000}s)`);

          // Log token details (partial token for security)
          const tokenPreview = token.substring(0, 5) + '...' + token.substring(token.length - 5);
          console.log(`Using cached token: ${tokenPreview}`);

          TOKEN = token;
          api.defaults.headers.common['Authorization'] = `Bearer ${TOKEN}`;

          // Reset retry counter and consecutive failures on successful token use
          tokenFetchRetries = 0;
          consecutiveFailures = 0;
          console.groupEnd();
          return TOKEN;
        }
        console.log(`Cached token expired (age: ${Math.round((now - timestamp) / 1000)}s, max: ${TOKEN_CACHE_DURATION/1000}s)`);
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
          params: { _t: Date.now() }
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
        api.defaults.headers.common['Authorization'] = `Bearer ${TOKEN}`;
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
          console.log(`Token fetch succeeded, will clear promise in ${clearDelay/1000}s`);
        } else {
          // If we failed to get a token, use a shorter delay based on retry count
          // to allow another attempt sooner
          clearDelay = tokenFetchRetries > 0 ? 
            5000 + (tokenFetchRetries * 2000) : // 5s + 2s per retry
            3000; // 3s for first attempt
          console.log(`Token fetch failed, will clear promise in ${clearDelay/1000}s`);
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

// Add response interceptor for global error handling and token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // Don't log aborted requests as errors
    if (axios.isCancel(error)) {
      console.log("Request cancelled:", error.message);
      return Promise.reject(error);
    }

    console.error("API Error:", error);

    // Check if the error is due to an invalid token (401 Unauthorized)
    if (error.response && error.response.status === 401) {
      // Check if this request has already been retried to prevent infinite loops
      const retryCount = error.config._retryCount || 0;
      const maxRetries = 2; // Fewer retries for interceptor to avoid blocking UI

      if (retryCount >= maxRetries) {
        console.error(`Request has already been retried ${retryCount} times, giving up`);
        // When we give up after max retries, we should perform a complete reset
        // to ensure a clean state for future requests
        console.log("Performing complete token state reset after max retries");
        cancelAllRequests();
        return Promise.reject(error);
      }

      console.log(`Token invalid (retry ${retryCount + 1}/${maxRetries}), clearing and refreshing...`);

      // Clear the stored token data
      localStorage.removeItem('tokenData');
      // Also clear old format token if it exists
      localStorage.removeItem('token');
      TOKEN = '';

      try {
        // Always perform a complete reset of token fetch state for 401 errors
        // This ensures we start fresh with each authentication failure
        console.log("Resetting token fetch state for fresh attempt after 401 error");

        // Reset all token-related state variables
        lastTokenFetch = 0;
        tokenFetchPromise = null;
        tokenFetchRetries = 0;
        consecutiveFailures = 0;
        circuitBreakerTripped = false;
        circuitBreakerResetTime = 0;

        // Also reset axios default headers to ensure no stale token is used
        delete api.defaults.headers.common['Authorization'];

        console.log("Complete token state reset performed for 401 error");

        // Add delay with exponential backoff for retries
        if (retryCount > 0) {
          const backoffTime = RETRY_BACKOFF_MS * Math.pow(2, retryCount - 1);
          console.log(`Interceptor retry ${retryCount + 1}/${maxRetries}, waiting ${backoffTime}ms before retry`);
          await new Promise(resolve => setTimeout(resolve, backoffTime));
        }

        // Try to get a new token
        const token = await fetchToken();

        // If the token was refreshed successfully, retry the original request
        if (token) {
          // Get the original request configuration
          const originalRequest = error.config;
          // Update the Authorization header with the new token
          originalRequest.headers['Authorization'] = `Bearer ${token}`;
          // Mark this request as retried
          originalRequest._retryCount = retryCount + 1;
          // Add a timeout to prevent hanging requests
          originalRequest.timeout = 10000;
          // Retry the request with the new token
          console.log("Token refreshed, retrying original request");
          return axios(originalRequest);
        } else {
          console.error("Token refresh returned null, cannot retry request");
          return Promise.reject(error);
        }
      } catch (refreshError: unknown) {
        console.error(`Failed to refresh token: ${refreshError instanceof Error ? refreshError.message : String(refreshError)}`);
        // Add the refresh error to the original error for better debugging
        error.refreshError = refreshError;
        return Promise.reject(error);
      }
    }

    // For network errors, provide more helpful error message
    if (error.message === 'Network Error') {
      console.error("Network error detected. Please check your internet connection.");
      error.isNetworkError = true;

      // If this is a token fetch request that failed with a network error,
      // we should reset the token fetch state to allow future attempts
      if (error.config && error.config.url && error.config.url.includes('/api/token')) {
        console.log("Network error on token fetch, performing complete state reset");

        // Immediately mark the current fetch as failed by setting tokenFetchPromise to null
        // This allows new fetch attempts to start without waiting for the timeout
        if (tokenFetchPromise) {
          console.log("Clearing failed token fetch promise immediately");
          tokenFetchPromise = null;
        }

        // Perform an immediate partial reset to prevent further requests from using stale state
        TOKEN = '';
        delete api.defaults.headers.common['Authorization'];

        // Reset the rest of the state after a delay to prevent immediate retries
        setTimeout(() => {
          console.log("Performing complete token state reset after network error");

          // Reset all token-related state variables
          lastTokenFetch = 0;
          tokenFetchRetries = 0;
          consecutiveFailures = 0;
          circuitBreakerTripped = false;
          circuitBreakerResetTime = 0;

          // Also clear localStorage to ensure no stale token is used
          localStorage.removeItem('tokenData');
          localStorage.removeItem('token');

          console.log("Token state completely reset after network error");
        }, 5000); // Wait 5 seconds before allowing new token fetches
      }
    }

    // For timeout errors, provide more helpful error message
    if (error.code === 'ECONNABORTED' && error.message.includes('timeout')) {
      console.error("Request timed out. The server might be overloaded or unreachable.");
      error.isTimeoutError = true;

      // If this is a token fetch request that timed out,
      // we should reset the token fetch state to allow future attempts
      if (error.config && error.config.url && error.config.url.includes('/api/token')) {
        console.log("Timeout on token fetch, performing complete state reset");

        // Immediately mark the current fetch as failed by setting tokenFetchPromise to null
        // This allows new fetch attempts to start without waiting for the timeout
        if (tokenFetchPromise) {
          console.log("Clearing timed out token fetch promise immediately");
          tokenFetchPromise = null;
        }

        // Perform an immediate partial reset to prevent further requests from using stale state
        TOKEN = '';
        delete api.defaults.headers.common['Authorization'];

        // Reset the rest of the state after a delay to prevent immediate retries
        setTimeout(() => {
          console.log("Performing complete token state reset after timeout");

          // Reset all token-related state variables
          lastTokenFetch = 0;
          tokenFetchRetries = 0;
          consecutiveFailures = 0;
          circuitBreakerTripped = false;
          circuitBreakerResetTime = 0;

          // Also clear localStorage to ensure no stale token is used
          localStorage.removeItem('tokenData');
          localStorage.removeItem('token');

          console.log("Token state completely reset after timeout");
        }, 5000); // Wait 5 seconds before allowing new token fetches
      }
    }

    return Promise.reject(error);
  }
);

// Function to ensure token is fetched before making API calls
const ensureToken = async () => {
  // Check if we have a valid token in memory
  if (!TOKEN) {
    // Try to get token from localStorage first
    const storedTokenData = localStorage.getItem('tokenData');
    if (storedTokenData) {
      try {
        const { token, timestamp } = JSON.parse(storedTokenData);
        const now = Date.now();
        // If token exists and is not expired, use it
        if (token && timestamp && (now - timestamp < TOKEN_CACHE_DURATION)) {
          TOKEN = token;
          api.defaults.headers.common['Authorization'] = `Bearer ${TOKEN}`;
          return;
        }
      } catch (e) {
        // Invalid token data, will fetch a new one
        console.warn('Invalid token data in localStorage, will fetch a new one');
      }
    }

    // If no valid token in memory or localStorage, fetch a new one
    try {
      // If there's already a token fetch in progress, wait for it to complete
      if (tokenFetchPromise) {
        console.log('Token fetch already in progress in ensureToken, waiting for it to complete');
        try {
          const token = await tokenFetchPromise;

          // If the token fetch completed but didn't return a token and we haven't exceeded max retries,
          // we should still throw to prevent API calls from proceeding with an invalid token
          if (!token && tokenFetchRetries < MAX_TOKEN_FETCH_RETRIES) {
            throw new Error(`Token fetch in progress failed, will be retried later (${tokenFetchRetries}/${MAX_TOKEN_FETCH_RETRIES})`);
          }

          // If we have a token now, we can proceed
          if (token) {
            return;
          }
        } catch (promiseError) {
          // If the existing promise failed, log it but continue to try a new fetch
          console.warn('Existing token fetch promise failed:', promiseError);
          // Clear the failed promise to allow a new attempt
          tokenFetchPromise = null;
          // Don't reset retry counter here, let fetchToken handle that
        }
      }

      // If we get here, either there was no existing promise or it failed
      // Try to fetch a new token
      const token = await fetchToken();
      if (!token) {
        // If token fetch failed but hasn't exceeded max retries, retry immediately
        if (tokenFetchRetries < MAX_TOKEN_FETCH_RETRIES) {
          // Store the current retry count for logging
          const currentRetryCount = tokenFetchRetries;
          console.log(`Token fetch failed, retrying immediately (${currentRetryCount}/${MAX_TOKEN_FETCH_RETRIES})`);

          // Wait a moment before retrying to avoid hammering the server
          const backoffTime = RETRY_BACKOFF_MS * Math.pow(2, currentRetryCount);
          await new Promise(resolve => setTimeout(resolve, backoffTime));

          // Force a new token fetch by clearing the promise and last fetch time
          tokenFetchPromise = null;
          lastTokenFetch = 0;

          try {
            // Retry the token fetch
            const retryToken = await fetchToken();
            if (retryToken) {
              console.log(`Immediate retry successful after attempt ${currentRetryCount + 1}`);
              return; // Success, we can continue
            }

            // If we get here, the retry returned null but didn't throw
            console.error(`Immediate retry returned null after attempt ${currentRetryCount + 1}`);
            throw new Error(`Failed to fetch authentication token after immediate retry (${currentRetryCount}/${MAX_TOKEN_FETCH_RETRIES})`);
          } catch (retryError: unknown) {
            // If the retry threw an error, log it and throw a more informative error
            console.error(`Error during immediate retry attempt ${currentRetryCount + 1}:`, retryError);
            throw new Error(`Failed to fetch authentication token after immediate retry (${currentRetryCount}/${MAX_TOKEN_FETCH_RETRIES}): ${retryError instanceof Error ? retryError.message : String(retryError)}`);
          }
        } else {
          // If we've exceeded max retries, throw a more detailed error
          console.error(`Maximum retry attempts (${MAX_TOKEN_FETCH_RETRIES}) exceeded`);
          throw new Error('Failed to fetch authentication token after maximum retries');
        }
      }
    } catch (error: unknown) {
      console.error('Error in ensureToken:', error);

      // Add more context to the error for better debugging
      if (error instanceof Error) {
        if (error.message.includes('Network Error')) {
          throw new Error('Failed to fetch authentication token: Network error. Please check your connection.');
        } else if (error.message.includes('timeout')) {
          throw new Error('Failed to fetch authentication token: Request timed out. Server might be overloaded.');
        } else {
          // Rethrow the original error with more context
          throw new Error(`Failed to fetch authentication token: ${error.message}`);
        }
      } else {
        // Handle non-Error objects
        throw new Error(`Failed to fetch authentication token: ${String(error)}`);
      }
    }
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
    memory: any;
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
