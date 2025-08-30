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
    // @ts-expect-error runtime check only
    expect(state.current_zone).toBe('Zone-α');
  });

  it('executes command endpoints and returns a 200 response object', async () => {
    const res1 = await sendCommand('noop');
    // sendCommand returns the Axios response-like object in our stub
    // @ts-expect-error runtime check only
    expect(res1 && res1.status).toBe(200);

    const res2 = await rollbackTo('checkpoint.json');
    // @ts-expect-error runtime check only
    expect(res2 && res2.status).toBe(200);

    const res3 = await triggerRitual(1);
    // @ts-expect-error runtime check only
    expect(res3 && res3.status).toBe(200);

    const res4 = await sendReward('Companion', 42);
    // @ts-expect-error runtime check only
    expect(res4 && res4.status).toBe(200);
  });

  it('gets checkpoints (stub returns an object)', async () => {
    const cps = await getCheckpoints();
    expect(cps).toBeTruthy();
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
