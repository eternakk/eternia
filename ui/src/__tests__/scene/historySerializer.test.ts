import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import type { SceneState } from '@/scene/SceneManager';
import type { SceneRealtimeState } from '@/scene/SceneState';
import type { SimulationEvent } from '@/scene';
import type { CheckpointRecord } from '@/api.ts';
import { serializeSceneState } from '@/scene/history/serializer';

describe('serializeSceneState', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2025-03-01T12:00:00Z'));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  const buildScene = (): SceneState => ({
    activeZone: 'Zone-beta',
    camera: {
      position: [6, 7, 8],
      target: [0, 1, 2],
      fov: 60,
      near: 0.2,
      far: 300,
    },
    lighting: {
      ambientIntensity: 0.75,
      exposure: 1.4,
    },
    render: {
      frameloop: 'demand',
      dpr: [1, 2],
    },
  });

  const buildRealtime = (): SceneRealtimeState => {
    const violation = {
      kind: 'governor.policy_violation',
      timestamp: 123,
      raw: { t: 123, event: 'policy_violation', payload: {} },
      policyName: 'safety-first',
      metrics: null,
      zoneName: 'Zone-alpha',
    } as unknown as SimulationEvent;

    const rollback = {
      kind: 'governor.rollback_complete',
      timestamp: 456,
      raw: { t: 456, event: 'rollback_complete', payload: { checkpoint: 'ckpt-final' } },
      checkpoint: 'ckpt-final',
    } as unknown as SimulationEvent;

    const zones = new Map<string, { name: string; isExplored: boolean; modifiers: Set<string> }>();
    zones.set('Zone-beta', { name: 'Zone-beta', isExplored: false, modifiers: new Set(['Moon', 'Sun']) });
    zones.set('Zone-alpha', { name: 'Zone-alpha', isExplored: true, modifiers: new Set(['Aurora']) });

    return {
      zones,
      activeZone: 'Zone-beta',
      governor: {
        isPaused: true,
        lastViolation: violation,
        lastRollback: rollback,
      },
    };
  };

  it('captures scene and realtime snapshots with stable ordering and signature', () => {
    const scene = buildScene();
    const realtime = buildRealtime();
    const checkpoint: CheckpointRecord = {
      path: 'ckpts/ckpt-final',
      created_at: '2025-03-01T11:55:00Z',
      kind: 'manual',
      label: 'final',
    };

    const entry = serializeSceneState(scene, realtime, { checkpoint });

    expect(entry.timestamp).toBe('2025-03-01T12:00:00.000Z');
    expect(entry.checkpoint).toEqual(checkpoint);

    expect(entry.scene).toEqual({
      activeZone: 'Zone-beta',
      camera: {
        position: [6, 7, 8],
        target: [0, 1, 2],
        fov: 60,
        near: 0.2,
        far: 300,
      },
      lighting: {
        ambientIntensity: 0.75,
        exposure: 1.4,
      },
      render: {
        frameloop: 'demand',
        dpr: [1, 2],
      },
    });

    expect(entry.realtime.activeZone).toBe('Zone-beta');
    expect(entry.realtime.zones.map((z) => z.name)).toEqual(['Zone-alpha', 'Zone-beta']);
    expect(entry.realtime.zones[0].modifiers).toEqual(['Aurora']);
    expect(entry.realtime.zones[1].modifiers).toEqual(['Moon', 'Sun']);

    expect(entry.realtime.governor).toEqual({
      isPaused: true,
      lastViolation: {
        kind: 'governor.policy_violation',
        timestamp: 123,
        zoneName: 'Zone-alpha',
      },
      lastRollback: {
        kind: 'governor.rollback_complete',
        timestamp: 456,
        checkpoint: 'ckpt-final',
      },
    });

    expect(entry.signature).toBe(JSON.stringify({ scene: entry.scene, realtime: entry.realtime }));
  });

  it('creates defensive copies of render configuration arrays', () => {
    const scene = buildScene();
    const realtime = buildRealtime();
    const originalDpr = scene.render.dpr as [number, number];

    const entry = serializeSceneState(scene, realtime);

    originalDpr[0] = 4;
    expect(entry.scene.render.dpr).toEqual([1, 2]);
  });
});
