import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

function parseCoverageThresholdFromEnv(): Partial<Record<'branches' | 'functions' | 'lines' | 'statements', number>> | undefined {
  const candidates = [
    process.env.npm_config_coveragethreshold, // from --coverageThreshold=...
    // Some environments might preserve casing
    (process.env as Record<string, string | undefined>)['npm_config_coverageThreshold'],
    process.env.COVERAGE_THRESHOLD,
  ];

  const raw = candidates.find((v): v is string => Boolean(v));
  if (!raw) return undefined;

  try {
    const parsed: unknown = JSON.parse(raw);
    const hasGlobal =
      parsed !== null &&
      typeof parsed === 'object' &&
      'global' in (parsed as Record<string, unknown>);

    const globalCandidate: unknown = hasGlobal
      ? (parsed as { global: unknown }).global
      : parsed;

    if (!globalCandidate || typeof globalCandidate !== 'object') return undefined;

    const out: Partial<Record<'branches' | 'functions' | 'lines' | 'statements', number>> = {};
    const g = globalCandidate as Record<string, unknown>;
    for (const key of ['branches', 'functions', 'lines', 'statements'] as const) {
      const v = g[key];
      if (typeof v === 'number') out[key] = v;
    }
    return Object.keys(out).length ? out : undefined;
  } catch (err) {
    console.warn('[vitest] Failed to parse COVERAGE_THRESHOLD JSON:', err);
    return undefined;
  }
}

const thresholds = parseCoverageThresholdFromEnv();

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    include: ['**/__tests__/**/*.{test,spec}.{ts,tsx}'],
    coverage: {
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules/', 'src/test/'],
      // Use V8 provider by default; thresholds will apply if provided
      provider: 'v8',
      thresholds,
    },
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },
});