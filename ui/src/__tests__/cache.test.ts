import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { getState, apiClient, __clearUiCacheForTests, __getUiCacheSize, __setUiCacheTTLForTests } from '../api';

// The api module in test mode stubs apiClient.get/post to return canned data.
// We wrap apiClient.get to count invocations to verify caching behavior.

describe('UI API GET cache (feature-flagged)', () => {
  let originalGet: any;

  beforeEach(() => {
    // Ensure clean cache and storage before each test
    __clearUiCacheForTests();
    __setUiCacheTTLForTests(10_000); // default TTL for tests
    localStorage.clear();

    // Patch apiClient.get to count calls
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    originalGet = (apiClient as any).get;
  });

  afterEach(() => {
    // Restore original get
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (apiClient as any).get = originalGet;
  });

  it('caches GET responses when enabled via localStorage flag', async () => {
    localStorage.setItem('ff_ui_cache', '1');

    let calls = 0;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (apiClient as any).get = async (...args: any[]) => {
      calls += 1;
      return originalGet.apply(apiClient, args);
    };

    // First call should hit network (stub) and populate cache
    const s1 = await getState();
    expect(s1).toBeTruthy();

    // Second call should come from cache without incrementing calls
    const s2 = await getState();
    expect(s2).toBeTruthy();

    expect(calls).toBe(1);
    expect(__getUiCacheSize()).toBeGreaterThanOrEqual(1);
  });

  it('does not cache when disabled', async () => {
    localStorage.setItem('ff_ui_cache', '0');
    __clearUiCacheForTests();

    let calls = 0;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (apiClient as any).get = async (...args: any[]) => {
      calls += 1;
      return originalGet.apply(apiClient, args);
    };

    await getState();
    await getState();

    expect(calls).toBe(2);
    expect(__getUiCacheSize()).toBe(0);
  });
});
