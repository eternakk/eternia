import { describe, expect, it } from 'vitest';
import { normalizeSimulationEvent } from '@/scene/simulationEvents';
import type { GovEvent } from '@/hooks/useGovEvents';

describe('normalizeSimulationEvent', () => {
  const baseEvent = (event: string, payload: unknown = {}): GovEvent => ({
    t: 10,
    event,
    payload,
  });

  it('normalizes zone events with defaults', () => {
    const changed = normalizeSimulationEvent(baseEvent('zone_changed', { zone_name: 'Zone-1', is_new: true }));
    expect(changed.kind).toBe('zone.changed');
    if (changed.kind === 'zone.changed') {
      expect(changed.zoneName).toBe('Zone-1');
      expect(changed.isNew).toBe(true);
    }

    const explored = normalizeSimulationEvent(baseEvent('zone_explored', { zone_name: 'Zone-2' }));
    expect(explored.kind).toBe('zone.explored');
    if (explored.kind === 'zone.explored') {
      expect(explored.zoneName).toBe('Zone-2');
    }

    const modifier = normalizeSimulationEvent(baseEvent('zone_modifier_added', { zone_name: 'Zone-3', modifier: 'Glow' }));
    expect(modifier.kind).toBe('zone.modifier_added');
    if (modifier.kind === 'zone.modifier_added') {
      expect(modifier.zoneName).toBe('Zone-3');
      expect(modifier.modifier).toBe('Glow');
    }
  });

  it('normalizes governor lifecycle events', () => {
    expect(normalizeSimulationEvent(baseEvent('pause'))).toMatchObject({ kind: 'governor.pause' });
    expect(normalizeSimulationEvent(baseEvent('resume'))).toMatchObject({ kind: 'governor.resume' });

    const shutdown = normalizeSimulationEvent(baseEvent('shutdown', 'maintenance'));
    expect(shutdown).toMatchObject({ kind: 'governor.shutdown', reason: null });

    const rollback = normalizeSimulationEvent(baseEvent('rollback_complete', { checkpoint: 'ckpt-1' }));
    expect(rollback.kind).toBe('governor.rollback_complete');
    if (rollback.kind === 'governor.rollback_complete') {
      expect(rollback.checkpoint).toBe('ckpt-1');
    }

    const continuity = normalizeSimulationEvent(baseEvent('continuity_breach', { detail: 42 }));
    expect(continuity.kind).toBe('governor.continuity_breach');
    if (continuity.kind === 'governor.continuity_breach') {
      expect(continuity.metrics).toEqual({ detail: 42 });
    }

    expect(normalizeSimulationEvent(baseEvent('checkpoint_scheduled'))).toMatchObject({ kind: 'governor.checkpoint_scheduled' });

    const saved = normalizeSimulationEvent(baseEvent('checkpoint_saved', { path: 'ckpt-path' }));
    expect(saved.kind).toBe('governor.checkpoint_saved');
    if (saved.kind === 'governor.checkpoint_saved') {
      expect(saved.path).toBe('ckpt-path');
    }

    const policy = normalizeSimulationEvent(baseEvent('policy_violation', { policy_name: 'safety', metrics: { score: 1 } }));
    expect(policy.kind).toBe('governor.policy_violation');
    if (policy.kind === 'governor.policy_violation') {
      expect(policy.policyName).toBe('safety');
      expect(policy.metrics).toEqual({ score: 1 });
    }

    const law = normalizeSimulationEvent(baseEvent('law_enforced', { law_name: 'alignment', event_name: 'breach', payload: { foo: 'bar' } }));
    expect(law.kind).toBe('governor.law_enforced');
    if (law.kind === 'governor.law_enforced') {
      expect(law.lawName).toBe('alignment');
      expect(law.eventName).toBe('breach');
      expect(law.payload).toEqual({ foo: 'bar' });
    }
  });

  it('normalizes pause/resume even when payloads are non-objects', () => {
    const saved = normalizeSimulationEvent({ t: undefined as unknown as number, event: 'checkpoint_saved', payload: 'direct-path' });
    expect(saved.kind).toBe('governor.checkpoint_saved');
    if (saved.kind === 'governor.checkpoint_saved') {
      expect(saved.path).toBe('direct-path');
    }
    expect(saved.timestamp).toBeGreaterThan(0);
  });

  it('falls back to unknown events when type is not recognized', () => {
    const event = normalizeSimulationEvent(baseEvent('something_new', { foo: 'bar' }));
    expect(event).toMatchObject({ kind: 'unknown', event: 'something_new', payload: { foo: 'bar' } });
  });

  it('coerces invalid zone names into empty strings', () => {
    const changed = normalizeSimulationEvent(baseEvent('zone_changed', { is_new: false }));
    expect(changed.kind).toBe('zone.changed');
    if (changed.kind === 'zone.changed') {
      expect(changed.zoneName).toBe('');
    }
  });
});
