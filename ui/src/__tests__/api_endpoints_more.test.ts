import { describe, it, expect, beforeEach } from 'vitest';
import {
  getZones,
  getZoneAssets,
  changeZone,
  getRituals,
  getAgents,
  fetchToken,
} from '../api';

// These tests rely on the test-environment stubs in api.ts (IS_TEST_ENV)

describe('api endpoints (zones/rituals/agents) under stubbed test env', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('getZones returns an array with at least one zone', async () => {
    await fetchToken();
    const zones = await getZones();
    expect(zones && zones.length).toBeGreaterThan(0);
  });

  it('getZoneAssets returns an object with optional fields', async () => {
    await fetchToken();
    const assets = await getZoneAssets('Zone-α');
    expect(assets).toBeTruthy();
  });

  it('changeZone returns a response object', async () => {
    await fetchToken();
    const res = await changeZone('Zone-β');
    const status = (res && typeof res === 'object' && 'status' in res) ? (res as { status?: unknown }).status : undefined;
    expect(status).toBe(200);
  });

  it('getRituals returns list of rituals', async () => {
    await fetchToken();
    const rituals = await getRituals();
    expect(rituals && rituals.length).toBeGreaterThan(0);
  });

  it('getAgents returns list of agents', async () => {
    await fetchToken();
    const agents = await getAgents();
    expect(agents && agents.length).toBeGreaterThan(0);
  });
});
