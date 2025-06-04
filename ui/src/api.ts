import axios from "axios";
import { createSafeApiCall } from "./utils/errorHandling";

// We'll fetch the token from the server
let TOKEN = '';
// Add a cooldown mechanism to prevent infinite token fetch attempts
let lastTokenFetchTime = 0;
const TOKEN_FETCH_COOLDOWN = 5000; // 5 seconds cooldown

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
  baseURL: "http://localhost:8000",
});

// Add a cleanup function to cancel all pending requests
export const cancelAllRequests = () => {
  // Create a new CancelToken source
  const source = axios.CancelToken.source();

  // Cancel all pending requests
  source.cancel('Application is closing');

  console.log('All pending API requests cancelled');

  // Clear token from localStorage
  localStorage.removeItem('token');
  TOKEN = '';
};

// Function to fetch the token from the server
export const fetchToken = async () => {
  try {
    // Check if we already have a token in localStorage
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      TOKEN = storedToken;
      api.defaults.headers.common['Authorization'] = `Bearer ${TOKEN}`;
      console.log('Using stored token');
      return TOKEN;
    }

    // Check if we're within the cooldown period
    const currentTime = Date.now();
    if (currentTime - lastTokenFetchTime < TOKEN_FETCH_COOLDOWN) {
      console.log(`Token fetch on cooldown. Please wait ${(TOKEN_FETCH_COOLDOWN - (currentTime - lastTokenFetchTime)) / 1000} seconds.`);
      return null;
    }

    // Update the last fetch time
    lastTokenFetchTime = currentTime;

    // If no stored token, fetch a new one
    console.log('No stored token, fetching new token...');
    const response = await axios.get('http://localhost:8000/api/token');

    if (!response.data || !response.data.token) {
      throw new Error('Invalid response from token endpoint');
    }

    TOKEN = response.data.token;

    // Store the token in localStorage for persistence
    localStorage.setItem('token', TOKEN);

    // Update the default headers with the new token
    api.defaults.headers.common['Authorization'] = `Bearer ${TOKEN}`;
    console.log('Token fetched and stored successfully');
    return TOKEN;
  } catch (error) {
    console.error('Failed to fetch token:', error);
    // Clear any existing token to prevent using an invalid one
    localStorage.removeItem('token');
    TOKEN = '';
    // Still update the last fetch time to enforce cooldown even on failures
    lastTokenFetchTime = Date.now();
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

      // Clear the stored token
      localStorage.removeItem('token');
      TOKEN = '';

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
  if (!TOKEN) {
    const token = await fetchToken();
    if (!token) {
      // Instead of throwing an error, return a specific error object
      // This allows the calling function to handle the error appropriately
      return { error: 'Token fetch on cooldown or failed' };
    }
  }
  return { success: true };
};

// Base API functions
const baseGetState = async () => {
  const tokenResult = await ensureToken();
  if (tokenResult.error) {
    throw new Error(tokenResult.error);
  }
  return api.get<State>("/state").then(r => r.data);
};

const baseSendCommand = async (a: string) => {
  const tokenResult = await ensureToken();
  if (tokenResult.error) {
    throw new Error(tokenResult.error);
  }
  return api.post(`/command/${a}`);
};

const baseGetCheckpoints = async () => {
  const tokenResult = await ensureToken();
  if (tokenResult.error) {
    throw new Error(tokenResult.error);
  }
  return api.get<string[]>("/checkpoints").then(r => r.data);
};

const baseRollbackTo = async (file?: string) => {
  const tokenResult = await ensureToken();
  if (tokenResult.error) {
    throw new Error(tokenResult.error);
  }
  return api.post("/command/rollback", null, { params: { file } });
};

const baseTriggerRitual = async (id: number) => {
  const tokenResult = await ensureToken();
  if (tokenResult.error) {
    throw new Error(tokenResult.error);
  }
  return api.post(`/api/rituals/trigger/${id}`);
};

const baseSendReward = async (companionName: string, value: number) => {
  const tokenResult = await ensureToken();
  if (tokenResult.error) {
    throw new Error(tokenResult.error);
  }
  return api.post(`/reward/${companionName}`, { value });
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
  const tokenResult = await ensureToken();
  if (tokenResult.error) {
    throw new Error(tokenResult.error);
  }
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
  const tokenResult = await ensureToken();
  if (tokenResult.error) {
    throw new Error(tokenResult.error);
  }
  return api.get<ZoneAssets>("/zone/assets", {
    params: { name: zoneName }
  }).then(r => r.data);
};

export const getZoneAssets = createSafeApiCall(
  baseGetZoneAssets,
  "Failed to fetch zone assets"
);

// Add function to change the current zone
const baseChangeZone = async (zoneName: string) => {
  const tokenResult = await ensureToken();
  if (tokenResult.error) {
    throw new Error(tokenResult.error);
  }
  return api.post("/api/change_zone", { zone: zoneName });
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
  const tokenResult = await ensureToken();
  if (tokenResult.error) {
    throw new Error(tokenResult.error);
  }
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
  zone: string | object | null;
  memory: any;
}

// Add function to fetch agents
const baseGetAgents = async () => {
  const tokenResult = await ensureToken();
  if (tokenResult.error) {
    throw new Error(tokenResult.error);
  }
  return api.get<Agent[]>("/api/agents").then(r => r.data);
};

export const getAgents = createSafeApiCall(
  baseGetAgents,
  "Failed to fetch agents"
);
