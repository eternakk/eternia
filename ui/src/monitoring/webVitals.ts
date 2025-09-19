/* Lightweight Core Web Vitals reporter (no external deps)
 * Guarded by feature flag at the component level.
 */
export type Metric = {
  name: string;
  value: number;
  id?: string;
  detail?: unknown;
};

export type ReportFn = (metric: Metric) => void;

function tryObserve(entryType: string, cb: (entry: PerformanceEntry) => void): (() => void) | null {
  if (typeof PerformanceObserver === 'undefined') return null;
  try {
    const po = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) cb(entry);
    });
    // @ts-ignore newer types
    po.observe({ type: entryType, buffered: true });
    return () => {
      try { po.disconnect(); } catch {}
    };
  } catch {
    return null;
  }
}

export function initWebVitals(report: ReportFn = (m) => console.log('[web-vitals]', m)) {
  const cleanups: Array<() => void> = [];

  // LCP
  const stopLcp = tryObserve('largest-contentful-paint', (entry) => {
    report({ name: 'LCP', value: entry.startTime, detail: { entry } });
  });
  if (stopLcp) cleanups.push(stopLcp);

  // CLS
  const stopCls = tryObserve('layout-shift', (entry: any) => {
    if (!entry.hadRecentInput) {
      report({ name: 'CLS', value: entry.value, detail: { entry } });
    }
  });
  if (stopCls) cleanups.push(stopCls);

  // FID (approx via first-input)
  const stopFid = tryObserve('first-input', (entry: any) => {
    const fid = entry.processingStart - entry.startTime;
    report({ name: 'FID', value: fid, detail: { entry } });
  });
  if (stopFid) cleanups.push(stopFid);

  // FCP via paint
  const stopPaint = tryObserve('paint', (entry) => {
    if (entry.name === 'first-contentful-paint') {
      report({ name: 'FCP', value: entry.startTime, detail: { entry } });
    }
  });
  if (stopPaint) cleanups.push(stopPaint);

  // Navigation timing as fallback baseline
  try {
    const nav = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming | undefined;
    if (nav) {
      report({ name: 'TTFB', value: nav.responseStart, detail: { entry: nav } });
    }
  } catch {
    // ignore
  }

  // Return cleanup to stop observers if needed
  return () => {
    for (const fn of cleanups) fn();
  };
}
