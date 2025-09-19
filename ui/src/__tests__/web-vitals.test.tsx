import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import { FeatureFlagProvider } from '../contexts/FeatureFlagContext';
import WebVitalsReporter from '../components/WebVitalsReporter';

const flags = {
  // minimal set; only web_vitals matters for this test
  'web_vitals': { name: 'web_vitals', enabled: true },
  'ui_skeletons': { name: 'ui_skeletons', enabled: false },
  'ui_cache': { name: 'ui_cache', enabled: false },
  'advanced-search': { name: 'advanced-search', enabled: false },
  'new-dashboard-layout': { name: 'new-dashboard-layout', enabled: false },
  'admin-analytics': { name: 'admin-analytics', enabled: false },
  'real-time-collaboration': { name: 'real-time-collaboration', enabled: false },
  'experimental-ai-suggestions': { name: 'experimental-ai-suggestions', enabled: false },
  'beta-features': { name: 'beta-features', enabled: false },
  'enhanced-visualization': { name: 'enhanced-visualization', enabled: false },
} as any;

describe('WebVitalsReporter', () => {
  it('logs an enabled message when the feature flag is on', () => {
    const spy = vi.spyOn(console, 'log').mockImplementation(() => {});

    render(
      <FeatureFlagProvider initialFlags={flags}>
        <WebVitalsReporter />
      </FeatureFlagProvider>
    );

    expect(spy).toHaveBeenCalled();
    const calls = spy.mock.calls.map((c) => String(c[0]));
    expect(calls.some((s) => s.includes('[WebVitalsReporter] enabled'))).toBe(true);

    spy.mockRestore();
  });
});
