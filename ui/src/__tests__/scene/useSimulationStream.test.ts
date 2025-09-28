import { describe, expect, it, vi } from 'vitest';
import { renderHook } from '@testing-library/react';
import type { GovEvent } from '@/hooks/useGovEvents';
import type { SimulationEventKind } from '@/scene';
import { useSimulationStream } from '@/scene/useSimulationStream';

const events: GovEvent[] = [
  { t: 1, event: 'zone_changed', payload: { zone_name: 'Zone-1', is_new: true } },
  { t: 2, event: 'policy_violation', payload: { policy_name: 'alignment' } },
  { t: 3, event: 'something_else', payload: { misc: true } },
];

vi.mock('@/hooks/useGovEvents', () => ({
  useGovEvents: vi.fn(() => events),
}));

describe('useSimulationStream', () => {
  it('returns events sorted as normalized records', () => {
    const { result } = renderHook(() => useSimulationStream());

    expect(result.current.events).toHaveLength(2);
    expect(result.current.latest?.kind).toBe('governor.policy_violation');
    expect(result.current.latestByKind.get('zone.changed')?.kind).toBe('zone.changed');
    expect(result.current.latestByKind.get('governor.policy_violation')).toMatchObject({ kind: 'governor.policy_violation' });
  });

  it('filters events by kind and optional inclusion of unknowns', () => {
    const filter: SimulationEventKind[] = ['zone.changed'];
    const { result } = renderHook(() => useSimulationStream({ filter }));
    expect(result.current.events).toHaveLength(1);
    expect(result.current.events[0].kind).toBe('zone.changed');
    expect(result.current.latestByKind.size).toBe(1);

    const { result: allWithUnknown } = renderHook(() => useSimulationStream({ includeUnknown: true }));
    expect(allWithUnknown.current.events.map((event) => event.kind)).toContain('unknown');
    expect(allWithUnknown.current.events).toHaveLength(3);
  });

  it('memoizes filter sets to avoid unnecessary recalculation', () => {
    const filter: SimulationEventKind[] = ['zone.changed'];
    const { result, rerender } = renderHook((props: { filter: SimulationEventKind[] }) => useSimulationStream(props), {
      initialProps: { filter },
    });

    expect(result.current.events).toHaveLength(1);

    const nextFilter = [...filter];
    rerender({ filter: nextFilter });
    expect(result.current.events).toHaveLength(1);
  });
});
