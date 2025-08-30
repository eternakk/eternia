import {defineConfig} from 'vitest/config';
import react from '@vitejs/plugin-react';
import {resolve} from 'path';

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

const thresholdsFromEnv = parseCoverageThresholdFromEnv();
const thresholds = thresholdsFromEnv ?? { statements: 10, branches: 10, functions: 10, lines: 10 };

export default defineConfig({
    plugins: [react()],
    test: {
        environment: 'jsdom',
        globals: true,
        setupFiles: ['./src/test/setup.ts'],
        include: [
            '**/__tests__/**/*.test.ts?(x)',
            '**/__tests__/**/*.spec.ts?(x)',
            '**/__tests__/*.test.ts?(x)',
            '**/__tests__/*.spec.ts?(x)',
            'src/**/*.test.ts?(x)',
            'src/**/*.spec.ts?(x)'
        ],
        coverage: {
            provider: 'v8',
            reporter: ['text', 'json', 'html'],
            // Measure coverage on source files, not tests
            include: [
                'src/**/*.{ts,tsx}'
            ],
            exclude: [
                'node_modules/',
                'src/test/**',
                '**/*.test.*',
                '**/*.spec.*',
                '**/*.stories.*',
                '**/*.d.ts',
                // Exclude heavy UI-only code from coverage until dedicated tests exist
                'src/components/**/stories/**',
                'src/components/ui/**'
            ],
            all: true,
            thresholds,
        },
    },
    resolve: {
        alias: {
            '@': resolve(__dirname, './src'),
            // OpenTelemetry stubs for tests (avoid heavy deps in test env)
            '@opentelemetry/api': resolve(__dirname, './src/test/otel-stubs/api.ts'),
            '@opentelemetry/sdk-trace-web': resolve(__dirname, './src/test/otel-stubs/sdk-trace-web.ts'),
            '@opentelemetry/resources': resolve(__dirname, './src/test/otel-stubs/resources.ts'),
            '@opentelemetry/semantic-conventions': resolve(__dirname, './src/test/otel-stubs/semantic-conventions.ts'),
            '@opentelemetry/sdk-trace-base': resolve(__dirname, './src/test/otel-stubs/sdk-trace-base.ts'),
            '@opentelemetry/exporter-trace-otlp-http': resolve(__dirname, './src/test/otel-stubs/exporter-trace-otlp-http.ts'),
            '@opentelemetry/context-zone': resolve(__dirname, './src/test/otel-stubs/context-zone.ts'),
            '@opentelemetry/instrumentation': resolve(__dirname, './src/test/otel-stubs/instrumentation.ts'),
            '@opentelemetry/instrumentation-document-load': resolve(__dirname, './src/test/otel-stubs/instrumentation-document-load.ts'),
            '@opentelemetry/instrumentation-xml-http-request': resolve(__dirname, './src/test/otel-stubs/instrumentation-xml-http-request.ts'),
            '@opentelemetry/instrumentation-fetch': resolve(__dirname, './src/test/otel-stubs/instrumentation-fetch.ts'),
            '@opentelemetry/instrumentation-user-interaction': resolve(__dirname, './src/test/otel-stubs/instrumentation-user-interaction.ts'),
        },
    },
});