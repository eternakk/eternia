import type { SimulationEvent } from "./simulationEvents";

export interface ZoneState {
  name: string;
  isExplored: boolean;
  modifiers: Set<string>;
}

export interface GovernorState {
  isPaused: boolean;
  lastViolation?: SimulationEvent;
  lastRollback?: SimulationEvent;
}

export interface SceneRealtimeState {
  zones: Map<string, ZoneState>;
  activeZone: string | null;
  governor: GovernorState;
}

export const createInitialRealtimeState = (): SceneRealtimeState => ({
  zones: new Map<string, ZoneState>(),
  activeZone: null,
  governor: {
    isPaused: false,
  },
});
