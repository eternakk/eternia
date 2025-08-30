import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

function parseCoverageThresholdFromEnv(): Partial<Record<'branches' | 'functions' | 'lines' | 'statements', number>> | undefined {
  const candidates = [
    process.env.npm_config_coveragethreshold, // from --coverageThreshold=...
    // Some environments might preserve casing
    // @ts-ignore - env keys are strings
    (process.env as Record<string, string | undefined>)['npm_config_coverageThreshold'],
    process.env.COVERAGE_THRESHOLD,
  ];

  const raw = candidates.find(Boolean);
  if (!raw) return undefined;

  try {
    const parsed = JSON.parse(raw);
    const global = parsed && typeof parsed === 'object' && 'global' in parsed ? (parsed as any).global : parsed;
    if (!global || typeof global !== 'object') return undefined;

    const out: Partial<Record<'branches' | 'functions' | 'lines' | 'statements', number>> = {};
    for (const key of ['branches', 'functions', 'lines', 'statements'] as const) {
      const v = (global as Record<string, unknown>)[key];
      if (typeof v === 'number') out[key] = v;
    }
    return Object.keys(out).length ? out : undefined;
  } catch (err) {
    // eslint-disable-next-line no-console
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