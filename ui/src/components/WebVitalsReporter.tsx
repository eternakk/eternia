import { useEffect } from 'react';
import { useIsFeatureEnabled } from '../contexts/FeatureFlagContext';
import { initWebVitals, Metric } from '../monitoring/webVitals';

export default function WebVitalsReporter() {
  const enabled = useIsFeatureEnabled('web_vitals');

  useEffect(() => {
    if (!enabled) return;
    // Initial signal for tests/diagnostics
    // eslint-disable-next-line no-console
    console.log('[WebVitalsReporter] enabled');
    const cleanup = initWebVitals((m: Metric) => {
      // For now, just log. This could be sent to a backend endpoint later.
      // eslint-disable-next-line no-console
      console.log('[WebVitalsReporter]', m.name, Math.round(m.value), m);
    });
    return () => { try { cleanup?.(); } catch {} };
  }, [enabled]);

  return null;
}
