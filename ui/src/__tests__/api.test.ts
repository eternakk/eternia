import { describe, it, expect } from 'vitest';
import { getZones, getAgents, getRituals, getZoneAssets, changeZone } from '../api';

// These tests exercise the stubbed API paths in test environment to improve V8 coverage
// for src/api.ts without making real network requests.

describe('api (stubbed in test env)', () => {
  it('fetches zones', async () => {
    const zones = await getZones();
    expect(zones).toBeTruthy();
    expect(Array.isArray(zones)).toBe(true);
    const first = (zones as any[])[0];
    expect(first).toMatchObject({ name: 'Zone-α' });
  });

  it('fetches agents', async () => {
    const agents = await getAgents();
    expect(agents).toBeTruthy();
    expect(Array.isArray(agents)).toBe(true);
    const first = (agents as any[])[0];
    expect(first).toMatchObject({ name: 'A1' });
  });

  it('fetches rituals', async () => {
    const rituals = await getRituals();
    expect(rituals).toBeTruthy();
    expect(Array.isArray(rituals)).toBe(true);
    const first = (rituals as any[])[0];
    expect(first).toMatchObject({ id: 1 });
  });

  it('fetches zone assets', async () => {
    const assets = await getZoneAssets('Zone-α');
    expect(assets).toBeTruthy();
    expect(assets).toMatchObject({ model: '', skybox: '' });
  });

  it('changes zone (stubbed)', async () => {
    const res = await changeZone('Zone-α');
    expect(res).toBeDefined();
  });
});
