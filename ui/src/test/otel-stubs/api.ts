// Minimal test-time stub for @opentelemetry/api to satisfy Vite resolution.
// Tests may further vi.mock this module; this stub is only to ensure the path resolves.

export const SpanStatusCode = { ERROR: 'ERROR' } as const;
export const SpanKind = { INTERNAL: 'INTERNAL' } as const;

const tracer = {
  startSpan: (name: string, _opts?: any) => ({
    name,
    attributes: {} as Record<string, unknown>,
    setAttribute: (_k: string, _v: unknown) => {},
    setStatus: (_s: any) => {},
    recordException: (_e: unknown) => {},
    end: () => {},
  }),
};

export const trace = {
  getTracer: (_serviceName?: string) => tracer,
  setSpan: (_ctx: any, _span: any) => ({}),
  getSpan: (_ctx: any) => undefined,
};

export const context = {
  active: () => ({}),
  with: (_ctx: any, fn: any) => fn(),
};
