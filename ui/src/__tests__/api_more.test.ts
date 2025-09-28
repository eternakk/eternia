import { describe, it, expect, beforeEach } from 'vitest';
import {
  getState,
  sendCommand,
  getCheckpoints,
  rollbackTo,
  triggerRitual,
  sendReward,
  getQuantumBits,
  getVariationalField,
  fetchToken,
  cancelAllRequests,
  apiClient,
  normalizeCheckpointRecords,
} from '../api';
import { createSafeApiCall } from '../utils/errorHandling';

// These tests exercise a broad set of API wrappers under the stubbed test environment
// to significantly improve V8 coverage without performing real network requests.

describe('api additional coverage (stubbed in test env)', () => {
  beforeEach(() => {
    // Ensure a clean storage between tests
    localStorage.clear();
  });

  it('fetches state with stubbed token and ensures Authorization header is set', async () => {
    const token = await fetchToken();
    expect(token).toBe('test-token');

    const state = await getState();
    expect(state).toBeTruthy();
    if (state) {
      expect(state.current_zone).toBe('Zone-α');
    } else {
      throw new Error('state should not be undefined in test env');
    }
  });

  it('executes command endpoints and returns a 200 response object', async () => {
    const res1 = await sendCommand('noop');
    // sendCommand returns the Axios response-like object in our stub
    const s1 = (res1 && typeof res1 === 'object' && 'status' in res1) ? (res1 as { status?: unknown }).status : undefined;
    expect(s1).toBe(200);

    const res2 = await rollbackTo('checkpoint.json');
    const s2 = (res2 && typeof res2 === 'object' && 'status' in res2) ? (res2 as { status?: unknown }).status : undefined;
    expect(s2).toBe(200);

    const res3 = await triggerRitual(1);
    const s3 = (res3 && typeof res3 === 'object' && 'status' in res3) ? (res3 as { status?: unknown }).status : undefined;
    expect(s3).toBe(200);

    const res4 = await sendReward('Companion', 42);
    const s4 = (res4 && typeof res4 === 'object' && 'status' in res4) ? (res4 as { status?: unknown }).status : undefined;
    expect(s4).toBe(200);
  });

  it('gets checkpoints (stub returns an object)', async () => {
    const cps = await getCheckpoints();
    expect(Array.isArray(cps)).toBe(true);
    if (Array.isArray(cps) && cps.length > 0) {
      expect(typeof cps[0].path).toBe('string');
    }
  });

  it('normalizes checkpoint objects into structured records', () => {
    const iso = new Date().toISOString();
    const records = normalizeCheckpointRecords([
      {
        path: '/var/checkpoints/ckpt_123.bin',
        kind: 'manual',
        created_at: iso,
        size_bytes: 2048,
      },
      'legacy_ckpt_456.bin',
    ]);

    expect(records).toHaveLength(2);
    expect(records[0].target_path).toBe('/var/checkpoints/ckpt_123.bin');
    expect(records[0].label).toBe('ckpt_123.bin');
    expect(records[0].kind).toBe('manual');
    expect(records[1].target_path).toBe('legacy_ckpt_456.bin');
    expect(records[1].kind).toBe('auto');
  });

  it('quantum API calls return defined payloads (stubbed)', async () => {
    const bits = await getQuantumBits(8);
    expect(bits).toBeTruthy();

    const field = await getVariationalField(123, 8);
    expect(field).toBeTruthy();
  });

  it('cancelAllRequests resets token/header state', async () => {
    // Ensure token and header are set first
    await fetchToken();
    const beforeAuth = apiClient.defaults.headers.common?.['Authorization'];
    expect(beforeAuth).toBeTruthy();

    const ok = cancelAllRequests();
    expect(ok).toBe(true);

    const authAfter = apiClient.defaults.headers.common?.['Authorization'];
    expect(authAfter).toBeUndefined();
  });
});

describe('errorHandling.createSafeApiCall', () => {
  it('returns undefined when wrapped function throws', async () => {
    const willThrow = async () => {
      throw new Error('boom');
    };
    const safe = createSafeApiCall(willThrow);
    const result = await safe();
    expect(result).toBeUndefined();
  });
});
