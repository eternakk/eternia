// Minimal test-time stub for @opentelemetry/api to satisfy Vite resolution.
// Tests may further vi.mock this module; this stub is only to ensure the path resolves.

export const SpanStatusCode = { ERROR: 'ERROR' } as const;
export const SpanKind = { INTERNAL: 'INTERNAL' } as const;

const tracer = {
  startSpan: (name: string, ...args: unknown[]) => {
    void args;
    return {
      name,
      attributes: {} as Record<string, unknown>,
      setAttribute: (k: string, v: unknown) => { void k; void v; },
      setStatus: (s: unknown) => { void s; },
      recordException: (e: unknown) => { void e; },
      end: () => {},
    };
  },
};

export const trace = {
  getTracer: (serviceName?: string) => { void serviceName; return tracer; },
  setSpan: (ctx: unknown, span: unknown) => { void ctx; void span; return {}; },
  getSpan: (ctx: unknown) => { void ctx; return undefined as unknown; },
};

export const context = {
  active: () => ({}),
  with: (ctx: unknown, fn: (...args: unknown[]) => unknown) => { void ctx; return (fn as () => unknown)(); },
};
