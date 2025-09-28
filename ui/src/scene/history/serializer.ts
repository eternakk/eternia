import type {SceneState} from "@/scene";
import type {SceneRealtimeState} from "../SceneState";
import type {CheckpointRecord} from "@/api.ts";

export interface SerializedSceneStateSnapshot {
    activeZone: string | null;
    camera: {
        position: [number, number, number];
        target: [number, number, number];
        fov: number;
        near: number;
        far: number;
    };
    lighting: {
        ambientIntensity: number;
        exposure: number;
    };
    render: {
        frameloop: "always" | "demand" | "never";
        dpr: number | [number, number];
    };
}

export interface SerializedZoneSnapshot {
    name: string;
    isExplored: boolean;
    modifiers: string[];
}

export interface SerializedGovernorSnapshot {
    isPaused: boolean;
    lastViolation?: {
        kind: string;
        timestamp: number;
        zoneName?: string | null;
    } | null;
    lastRollback?: {
        kind: string;
        timestamp: number;
        checkpoint?: string | null;
    } | null;
}

export interface SerializedRealtimeSnapshot {
    activeZone: string | null;
    zones: SerializedZoneSnapshot[];
    governor: SerializedGovernorSnapshot;
}

export interface SceneHistoryEntry {
    timestamp: string;
    signature: string;
    scene: SerializedSceneStateSnapshot;
    realtime: SerializedRealtimeSnapshot;
    checkpoint?: CheckpointRecord;
}

const summarizeEvent = (
    event: SceneRealtimeState["governor"]["lastViolation"] | SceneRealtimeState["governor"]["lastRollback"],
): { kind: string; timestamp: number; zoneName?: string | null; checkpoint?: string | null } | null => {
    if (!event) {
        return null;
    }
    const base = {
        kind: event.kind,
        timestamp: event.timestamp,
    } as { kind: string; timestamp: number; zoneName?: string | null; checkpoint?: string | null };

    if (
        "zoneName" in event &&
        typeof (event as { zoneName?: unknown }).zoneName === "string"
    ) {
        base.zoneName = (event as { zoneName: string }).zoneName;
    }

    if (
        "checkpoint" in event &&
        typeof (event as { checkpoint?: unknown }).checkpoint === "string"
    ) {
        base.checkpoint = (event as { checkpoint: string }).checkpoint;
    }

    return base;
};

const buildGovernorSnapshot = (state: SceneRealtimeState): SerializedGovernorSnapshot => {
    return {
        isPaused: Boolean(state.governor.isPaused),
        lastViolation: summarizeEvent(state.governor.lastViolation),
        lastRollback: summarizeEvent(state.governor.lastRollback),
    };
};

const buildSceneSnapshot = (scene: SceneState): SerializedSceneStateSnapshot => {
    return {
        activeZone: scene.activeZone,
        camera: {
            position: [scene.camera.position[0], scene.camera.position[1], scene.camera.position[2]],
            target: [scene.camera.target[0], scene.camera.target[1], scene.camera.target[2]],
            fov: scene.camera.fov,
            near: scene.camera.near,
            far: scene.camera.far,
        },
        lighting: {
            ambientIntensity: scene.lighting.ambientIntensity,
            exposure: scene.lighting.exposure,
        },
        render: {
            frameloop: scene.render.frameloop,
            dpr: Array.isArray(scene.render.dpr) ? [...scene.render.dpr] as [number, number] : scene.render.dpr,
        },
    };
};

const buildRealtimeSnapshot = (realtime: SceneRealtimeState): SerializedRealtimeSnapshot => {
    const zones: SerializedZoneSnapshot[] = Array.from(realtime.zones.entries()).map(([name, zone]) => ({
        name,
        isExplored: zone.isExplored,
        modifiers: Array.from(zone.modifiers.values()).sort(),
    }));

    zones.sort((a, b) => a.name.localeCompare(b.name));

    return {
        activeZone: realtime.activeZone,
        zones,
        governor: buildGovernorSnapshot(realtime),
    };
};

const stableStringify = (value: unknown): string => {
    return JSON.stringify(value);
};

export const serializeSceneState = (
    scene: SceneState,
    realtime: SceneRealtimeState,
    options: { checkpoint?: CheckpointRecord } = {},
): SceneHistoryEntry => {
    const sceneSnapshot = buildSceneSnapshot(scene);
    const realtimeSnapshot = buildRealtimeSnapshot(realtime);
    const payload = {scene: sceneSnapshot, realtime: realtimeSnapshot};
    const signature = stableStringify(payload);

    const entry: SceneHistoryEntry = {
        timestamp: new Date().toISOString(),
        signature,
        scene: sceneSnapshot,
        realtime: realtimeSnapshot,
    };

    if (options.checkpoint) {
        entry.checkpoint = options.checkpoint;
    }

    return entry;
};
