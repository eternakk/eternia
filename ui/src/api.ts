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
const TOKEN_CACHE_DURATION = 5 * 60 * 1000; // 5 minutes in milliseconds

// Function to fetch the token from the server
export const fetchToken = async () => {
  const now = Date.now();
  try {
    // Check if we already have a token in localStorage with timestamp
    const storedTokenData = localStorage.getItem('tokenData');
    if (storedTokenData) {
      try {
        const { token, timestamp } = JSON.parse(storedTokenData);
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
    if (tokenFetchPromise && (now - lastTokenFetch < 5000)) {
      console.log('Token fetch already in progress, reusing request');
      return tokenFetchPromise;
    }
    // Set the last fetch time and create a new fetch promise
    lastTokenFetch = now;
    tokenFetchPromise = (async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
        const response = await axios.get(`${apiUrl}/api/token`);
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
        console.error('Failed to fetch token:', error);
        // Clear any existing token to prevent using an invalid one
        localStorage.removeItem('tokenData');
        TOKEN = '';
        return null;
      } finally {
        // Clear the promise after a short delay to allow concurrent requests to use it
        setTimeout(() => {
          tokenFetchPromise = null;
        }, 5000);
      }
    })();
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
      TOKEN = '';
      // Reset token fetch tracking
      lastTokenFetch = 0;
      tokenFetchPromise = null;
      // Try to get a new token
      try {
        await fetchToken();
        // If the token was refreshed successfully, retry the original request
        if (TOKEN) {
          // Get the original request configuration
          const originalRequest = error.config;
          // Update the Authorization header with the new token
          originalRequest.headers['Authorization'] = `Bearer ${TOKEN}`;
          // Retry the request with the new token
          return axios(originalRequest);
        }
      } catch (refreshError) {
        console.error("Failed to refresh token:", refreshError);
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
      }
    }
    // If no valid token in memory or localStorage, fetch a new one
    const token = await fetchToken();
    if (!token) {
      throw new Error('Failed to fetch authentication token');
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
