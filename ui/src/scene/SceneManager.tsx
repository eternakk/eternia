import {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { useSimulationStream } from "./useSimulationStream";
import { createInitialRealtimeState, SceneRealtimeState, ZoneState } from "./SceneState";
import type { SimulationEvent } from "./simulationEvents";

export type Vec3 = [number, number, number];

export interface SceneCameraConfig {
  position: Vec3;
  target: Vec3;
  fov: number;
  near: number;
  far: number;
}

export interface SceneLightingConfig {
  ambientIntensity: number;
  exposure: number;
}

export interface SceneRenderConfig {
  frameloop: "always" | "demand" | "never";
  dpr: number | [number, number];
}

export interface SceneState {
  activeZone: string | null;
  camera: SceneCameraConfig;
  lighting: SceneLightingConfig;
  render: SceneRenderConfig;
}

const DEFAULT_CAMERA: SceneCameraConfig = {
  position: [6, 6, 6],
  target: [0, 1.25, 0],
  fov: 45,
  near: 0.1,
  far: 200,
};

const DEFAULT_LIGHTING: SceneLightingConfig = {
  ambientIntensity: 0.4,
  exposure: 1.0,
};

const DEFAULT_RENDER: SceneRenderConfig = {
  frameloop: "demand",
  dpr: [1, 1.5],
};

const DEFAULT_STATE: SceneState = {
  activeZone: null,
  camera: DEFAULT_CAMERA,
  lighting: DEFAULT_LIGHTING,
  render: DEFAULT_RENDER,
};

export interface SceneManagerContextValue {
  state: SceneState;
  setActiveZone: (zone: string | null) => void;
  updateCamera: (partial: Partial<SceneCameraConfig>) => void;
  updateLighting: (partial: Partial<SceneLightingConfig>) => void;
  updateRenderConfig: (partial: Partial<SceneRenderConfig>) => void;
  realtime: SceneRealtimeState;
  reset: () => void;
}

const SceneManagerContext = createContext<SceneManagerContextValue | undefined>(undefined);

interface SceneManagerProviderProps {
  children: ReactNode;
  initialState?: Partial<SceneState>;
}

export function SceneManagerProvider({ children, initialState }: SceneManagerProviderProps) {
  const initialConfigRef = useRef<SceneState>({
    ...DEFAULT_STATE,
    ...initialState,
    camera: { ...DEFAULT_CAMERA, ...(initialState?.camera ?? {}) },
    lighting: { ...DEFAULT_LIGHTING, ...(initialState?.lighting ?? {}) },
    render: { ...DEFAULT_RENDER, ...(initialState?.render ?? {}) },
  });

  const [state, setState] = useState<SceneState>(initialConfigRef.current);
  const [realtime, setRealtime] = useState<SceneRealtimeState>(createInitialRealtimeState);
  const { events, latestByKind } = useSimulationStream();
  const lastCameraSignature = useRef<string | null>(null);
  const lastLightingSignature = useRef<string | null>(null);

  const setActiveZone = useCallback((zone: string | null) => {
    setState((prev) => (prev.activeZone === zone ? prev : { ...prev, activeZone: zone }));
  }, []);

  const updateCamera = useCallback((partial: Partial<SceneCameraConfig>) => {
    setState((prev) => ({
      ...prev,
      camera: {
        ...prev.camera,
        ...partial,
        position: (partial.position ?? prev.camera.position) as Vec3,
        target: (partial.target ?? prev.camera.target) as Vec3,
      },
    }));
  }, []);

  const updateLighting = useCallback((partial: Partial<SceneLightingConfig>) => {
    setState((prev) => ({
      ...prev,
      lighting: {
        ...prev.lighting,
        ...partial,
      },
    }));
  }, []);

  const updateRenderConfig = useCallback((partial: Partial<SceneRenderConfig>) => {
    setState((prev) => ({
      ...prev,
      render: {
        ...prev.render,
        ...partial,
      },
    }));
  }, []);

  const reset = useCallback(() => {
    setState(initialConfigRef.current);
    setRealtime(createInitialRealtimeState());
  }, []);

  useEffect(() => {
    if (!events.length) return;

    setRealtime((prev) => {
      let next: SceneRealtimeState | null = null;

      const ensureZone = (name: string): ZoneState => {
        if (!next) {
          next = { zones: new Map(prev.zones), activeZone: prev.activeZone, governor: { ...prev.governor } };
        }
        if (!next.zones.has(name)) {
          next.zones.set(name, { name, isExplored: false, modifiers: new Set() });
        }
        return next.zones.get(name)!;
      };

      const applyEvent = (event: SimulationEvent) => {
        switch (event.kind) {
          case "zone.changed": {
            if (!event.zoneName) return;
            const zone = ensureZone(event.zoneName);
            zone.isExplored ||= event.isNew;
            next?.zones.set(event.zoneName, zone);
            next!.activeZone = event.zoneName;
            break;
          }
          case "zone.explored": {
            if (!event.zoneName) return;
            const zone = ensureZone(event.zoneName);
            zone.isExplored = true;
            next?.zones.set(event.zoneName, zone);
            break;
          }
          case "zone.modifier_added": {
            if (!event.zoneName) return;
            const zone = ensureZone(event.zoneName);
            if (event.modifier) {
              zone.modifiers.add(event.modifier);
              next?.zones.set(event.zoneName, zone);
            }
            break;
          }
          case "governor.pause": {
            if (!next) {
              next = { zones: new Map(prev.zones), activeZone: prev.activeZone, governor: { ...prev.governor } };
            }
            next.governor.isPaused = true;
            break;
          }
          case "governor.resume": {
            if (!next) {
              next = { zones: new Map(prev.zones), activeZone: prev.activeZone, governor: { ...prev.governor } };
            }
            next.governor.isPaused = false;
            break;
          }
          case "governor.policy_violation": {
            if (!next) {
              next = { zones: new Map(prev.zones), activeZone: prev.activeZone, governor: { ...prev.governor } };
            }
            next.governor.lastViolation = event;
            break;
          }
          case "governor.rollback_complete": {
            if (!next) {
              next = { zones: new Map(prev.zones), activeZone: prev.activeZone, governor: { ...prev.governor } };
            }
            next.governor.lastRollback = event;
            break;
          }
          default:
            break;
        }
      };

      for (const event of events) {
        applyEvent(event);
      }

      if (!next) return prev;

      if (next.activeZone && next.zones.has(next.activeZone)) {
        return next;
      }

      if (latestByKind.has("zone.changed")) {
        next.activeZone = (latestByKind.get("zone.changed") as SimulationEvent & { kind: "zone.changed" }).zoneName;
      }

      return next;
    });
  }, [events, latestByKind]);

  const activeZoneName = realtime.activeZone;
  const activeZoneState = activeZoneName ? realtime.zones.get(activeZoneName) : undefined;
  const modifiersSignature = useMemo(() => {
    if (!activeZoneState) return "";
    return Array.from(activeZoneState.modifiers).sort().join("|");
  }, [activeZoneState]);

  useEffect(() => {
    if (activeZoneName) {
      const cameraPreset = deriveCameraPreset(activeZoneName, activeZoneState);
      if (cameraPreset) {
        const signature = JSON.stringify(cameraPreset);
        if (signature !== lastCameraSignature.current) {
          updateCamera(cameraPreset);
          lastCameraSignature.current = signature;
        }
      }
    }

    const lightingPreset = deriveLightingPreset(activeZoneState, realtime.governor);
    const lightingSignature = JSON.stringify(lightingPreset);
    if (lightingSignature !== lastLightingSignature.current) {
      updateLighting(lightingPreset);
      lastLightingSignature.current = lightingSignature;
    }
  }, [activeZoneName, modifiersSignature, realtime.governor, activeZoneState, updateCamera, updateLighting]);

  const value = useMemo<SceneManagerContextValue>(
    () => ({
      state,
      setActiveZone,
      updateCamera,
      updateLighting,
      updateRenderConfig,
      realtime,
      reset,
    }),
    [reset, realtime, setActiveZone, state, updateCamera, updateLighting, updateRenderConfig]
  );

  return <SceneManagerContext.Provider value={value}>{children}</SceneManagerContext.Provider>;
}

export function useSceneManager(): SceneManagerContextValue {
  const ctx = useContext(SceneManagerContext);
  if (!ctx) {
    throw new Error("useSceneManager must be used within a SceneManagerProvider");
  }
  return ctx;
}

export function useSceneState(): SceneState {
  return useSceneManager().state;
}

export function useSceneCamera(): SceneCameraConfig {
  return useSceneManager().state.camera;
}

export function useSceneLighting(): SceneLightingConfig {
  return useSceneManager().state.lighting;
}

export function useSceneRenderConfig(): SceneRenderConfig {
  return useSceneManager().state.render;
}

export const defaultSceneState = DEFAULT_STATE;

function deriveCameraPreset(zoneName: string, zone: ZoneState | undefined): Partial<SceneCameraConfig> | null {
  if (!zoneName) return null;
  const angle = hashZone(zoneName);
  const radius = 6 + (zone?.modifiers.size ?? 0) * 0.2;
  const height = 4 + (zone?.isExplored ? 1.5 : 0.5);
  const position: Vec3 = [
    Math.cos(angle) * radius,
    height,
    Math.sin(angle) * radius,
  ];

  return {
    position,
    target: [0, 1.25, 0],
    fov: 45,
    near: 0.1,
    far: 200,
  } satisfies Partial<SceneCameraConfig>;
}

function deriveLightingPreset(
  zone: ZoneState | undefined,
  governor: SceneRealtimeState["governor"],
): Partial<SceneLightingConfig> {
  let ambient = 0.4;
  let exposure = 1.0;

  if (zone) {
    const modifiers = zone.modifiers;
    if (modifiers.has("Luminous Cascade") || modifiers.has("Vibrant Pulse")) {
      ambient += 0.25;
      exposure += 0.2;
    }
    if (modifiers.has("Shroud of Memory")) {
      ambient -= 0.15;
      exposure -= 0.1;
    }
    if (modifiers.has("Volcanic Surge")) {
      ambient += 0.1;
      exposure += 0.15;
    }
  }

  if (governor.isPaused) {
    ambient -= 0.2;
    exposure -= 0.2;
  }

  return {
    ambientIntensity: Math.max(0.1, ambient),
    exposure: Math.max(0.5, exposure),
  } satisfies Partial<SceneLightingConfig>;
}

function hashZone(zoneName: string): number {
  let hash = 0;
  for (let i = 0; i < zoneName.length; i++) {
    hash = (hash << 5) - hash + zoneName.charCodeAt(i);
    hash |= 0;
  }
  const normalized = Math.abs(hash % 360);
  return (normalized / 180) * Math.PI;
}
