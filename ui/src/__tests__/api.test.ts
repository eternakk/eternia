import {describe, expect, it} from 'vitest';
import {changeZone, getAgents, getRituals, getZoneAssets, getZones} from '../api';

// Define types based on expected data structure
interface Zone {
    name: string;
}

interface Agent {
    name: string;
}

interface Ritual {
    id: number;
}

// These tests exercise the stubbed API paths in test environment to improve V8 coverage
// for src/api.ts without making real network requests.

describe('api (stubbed in test env)', () => {
    it('fetches zones', async () => {
        const zones = await getZones();
        expect(zones).toBeTruthy();
        expect(Array.isArray(zones)).toBe(true);
        const firstZone: Zone = (zones as Zone[])[0];
        expect(firstZone).toMatchObject({name: 'Zone-α'});
    });

    it('fetches agents', async () => {
        const agents = await getAgents();
        expect(agents).toBeTruthy();
        expect(Array.isArray(agents)).toBe(true);
        const firstAgent: Agent = (agents as Agent[])[0];
        expect(firstAgent).toMatchObject({name: 'A1'});
    });

    it('fetches rituals', async () => {
        const rituals = await getRituals();
        expect(rituals).toBeTruthy();
        expect(Array.isArray(rituals)).toBe(true);
        const firstRitual: Ritual = (rituals as Ritual[])[0];
        expect(firstRitual).toMatchObject({id: 1});
    });

    it('fetches zone assets', async () => {
        const assets = await getZoneAssets('Zone-α');
        expect(assets).toBeTruthy();
        expect(assets).toMatchObject({model: '', skybox: ''});
    });

    it('changes zone (stubbed)', async () => {
        const res = await changeZone('Zone-α');
        expect(res).toBeDefined();
    });
});
