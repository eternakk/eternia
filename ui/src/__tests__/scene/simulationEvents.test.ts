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
    expect(changed).toMatchObject({ kind: 'zone.changed', zoneName: 'Zone-1', isNew: true });

    const explored = normalizeSimulationEvent(baseEvent('zone_explored', { zone_name: 'Zone-2' }));
    expect(explored).toMatchObject({ kind: 'zone.explored', zoneName: 'Zone-2' });

    const modifier = normalizeSimulationEvent(baseEvent('zone_modifier_added', { zone_name: 'Zone-3', modifier: 'Glow' }));
    expect(modifier).toMatchObject({ kind: 'zone.modifier_added', zoneName: 'Zone-3', modifier: 'Glow' });
  });

  it('normalizes governor lifecycle events', () => {
    expect(normalizeSimulationEvent(baseEvent('pause'))).toMatchObject({ kind: 'governor.pause' });
    expect(normalizeSimulationEvent(baseEvent('resume'))).toMatchObject({ kind: 'governor.resume' });

    const shutdown = normalizeSimulationEvent(baseEvent('shutdown', 'maintenance'));
    expect(shutdown).toMatchObject({ kind: 'governor.shutdown', reason: null });

    const rollback = normalizeSimulationEvent(baseEvent('rollback_complete', { checkpoint: 'ckpt-1' }));
    expect(rollback).toMatchObject({ kind: 'governor.rollback_complete', checkpoint: 'ckpt-1' });

    const continuity = normalizeSimulationEvent(baseEvent('continuity_breach', { detail: 42 }));
    expect(continuity).toMatchObject({ kind: 'governor.continuity_breach', metrics: { detail: 42 } });

    expect(normalizeSimulationEvent(baseEvent('checkpoint_scheduled'))).toMatchObject({ kind: 'governor.checkpoint_scheduled' });

    const saved = normalizeSimulationEvent(baseEvent('checkpoint_saved', { path: 'ckpt-path' }));
    expect(saved).toMatchObject({ kind: 'governor.checkpoint_saved', path: 'ckpt-path' });

    const policy = normalizeSimulationEvent(baseEvent('policy_violation', { policy_name: 'safety', metrics: { score: 1 } }));
    expect(policy).toMatchObject({ kind: 'governor.policy_violation', policyName: 'safety', metrics: { score: 1 } });

    const law = normalizeSimulationEvent(baseEvent('law_enforced', { law_name: 'alignment', event_name: 'breach', payload: { foo: 'bar' } }));
    expect(law).toMatchObject({ kind: 'governor.law_enforced', lawName: 'alignment', eventName: 'breach', payload: { foo: 'bar' } });
  });

  it('normalizes pause/resume even when payloads are non-objects', () => {
    const saved = normalizeSimulationEvent({ t: undefined as unknown as number, event: 'checkpoint_saved', payload: 'direct-path' });
    expect(saved).toMatchObject({ kind: 'governor.checkpoint_saved', path: 'direct-path' });
    expect(saved.timestamp).toBeGreaterThan(0);
  });

  it('falls back to unknown events when type is not recognized', () => {
    const event = normalizeSimulationEvent(baseEvent('something_new', { foo: 'bar' }));
    expect(event).toMatchObject({ kind: 'unknown', event: 'something_new', payload: { foo: 'bar' } });
  });

  it('coerces invalid zone names into empty strings', () => {
    const changed = normalizeSimulationEvent(baseEvent('zone_changed', { is_new: false }));
    expect(changed.zoneName).toBe('');
  });
});
