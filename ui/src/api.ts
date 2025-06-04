import axios from "axios";
import { createSafeApiCall } from "./utils/errorHandling";

const TOKEN = import.meta.env.VITE_ETERNA_TOKEN;

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
  headers: { Authorization: `Bearer ${TOKEN}` },
});

// Add response interceptor for global error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API Error:", error);
    return Promise.reject(error);
  }
);

// Base API functions
const baseGetState = () => api.get<State>("/state").then(r => r.data);
const baseSendCommand = (a: string) => api.post(`/command/${a}`);
const baseGetCheckpoints = () => api.get<string[]>("/checkpoints").then(r => r.data);
const baseRollbackTo = (file?: string) =>
  api.post("/command/rollback", null, { params: { file } });
const baseTriggerRitual = (id: number) => api.post(`/api/rituals/trigger/${id}`);
const baseSendReward = (companionName: string, value: number) => 
  api.post(`/reward/${companionName}`, { value });

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
