import { describe, it, expect } from 'vitest';
import featureFlags from '../config/featureFlags';

// Simple sanity tests to execute and validate the feature flags configuration.
describe('config/featureFlags', () => {
  it('contains expected feature keys and enabled states', () => {
    const keys = Object.keys(featureFlags);
    expect(keys).toContain('advanced-search');
    expect(keys).toContain('new-dashboard-layout');
    expect(keys).toContain('admin-analytics');
    expect(keys).toContain('real-time-collaboration');
    expect(keys).toContain('experimental-ai-suggestions');
    expect(keys).toContain('beta-features');
    expect(keys).toContain('enhanced-visualization');

    expect(featureFlags['advanced-search'].enabled).toBe(true);
    expect(featureFlags['experimental-ai-suggestions'].enabled).toBe(false);
  });

  it('supports rolloutPercentage and enabledForGroups when provided', () => {
    expect(featureFlags['new-dashboard-layout'].rolloutPercentage).toBe(50);
    expect(featureFlags['admin-analytics'].enabledForGroups).toContain('admin');
    expect(featureFlags['beta-features'].enabledForGroups).toContain('beta-tester');
  });
});
