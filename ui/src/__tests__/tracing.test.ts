import { describe, it, expect, vi } from 'vitest';
import React from 'react';
import { act } from '@testing-library/react';

// Mocks for OpenTelemetry packages to avoid heavy runtime deps
let currentSpan: any = undefined;

vi.mock('@opentelemetry/api', () => {
  const SpanStatusCode = { ERROR: 'ERROR' } as const;
  const SpanKind = { INTERNAL: 'INTERNAL' } as const;

  const tracer = {
    startSpan: (name: string, _opts?: any) => {
      const span: any = {
        name,
        attributes: {} as Record<string, unknown>,
        setAttribute: (k: string, v: unknown) => { span.attributes[k] = v; },
        setStatus: (s: any) => { span.status = s; },
        recordException: (e: unknown) => { span.exception = e; },
        end: () => { span.ended = true; },
      };
      return span;
    },
  };

  const trace = {
    getTracer: (_serviceName?: string) => tracer,
    setSpan: (_ctx: any, span: any) => { currentSpan = span; return { currentSpan: span }; },
    getSpan: (_ctx: any) => currentSpan,
  };

  const context = {
    active: () => ({}),
    with: (_ctx: any, fn: any) => fn(),
  };

  return { __esModule: true, trace, context, SpanStatusCode, SpanKind };
});

vi.mock('@opentelemetry/sdk-trace-web', () => {
  class WebTracerProvider {
    constructor(_opts?: any) {}
    addSpanProcessor(_p: any) {}
    register(_cfg?: any) {}
  }
  return { __esModule: true, WebTracerProvider };
});

vi.mock('@opentelemetry/resources', () => {
  class Resource { constructor(_attrs: any) { this.attributes = _attrs; } attributes: any }
  return { __esModule: true, Resource };
});

vi.mock('@opentelemetry/semantic-conventions', () => {
  const SemanticResourceAttributes = {
    SERVICE_NAME: 'service.name',
    SERVICE_NAMESPACE: 'service.namespace',
    DEPLOYMENT_ENVIRONMENT: 'deployment.environment',
  };
  return { __esModule: true, SemanticResourceAttributes };
});

vi.mock('@opentelemetry/sdk-trace-base', () => {
  class BatchSpanProcessor { constructor(_e: any) {} }
  return { __esModule: true, BatchSpanProcessor };
});

vi.mock('@opentelemetry/exporter-trace-otlp-http', () => {
  class OTLPTraceExporter { constructor(_opts?: any) {} }
  return { __esModule: true, OTLPTraceExporter };
});

vi.mock('@opentelemetry/context-zone', () => {
  class ZoneContextManager {}
  return { __esModule: true, ZoneContextManager };
});

vi.mock('@opentelemetry/instrumentation', () => ({
  __esModule: true,
  registerInstrumentations: (_cfg: any) => {},
}));

vi.mock('@opentelemetry/instrumentation-document-load', () => ({
  __esModule: true,
  DocumentLoadInstrumentation: class {},
}));

vi.mock('@opentelemetry/instrumentation-xml-http-request', () => ({
  __esModule: true,
  XMLHttpRequestInstrumentation: class { constructor(_opts?: any) {} },
}));

vi.mock('@opentelemetry/instrumentation-fetch', () => ({
  __esModule: true,
  FetchInstrumentation: class { constructor(_opts?: any) {} },
}));

vi.mock('@opentelemetry/instrumentation-user-interaction', () => ({
  __esModule: true,
  UserInteractionInstrumentation: class {},
}));

import {
  initTracing,
  getTracer,
  createSpan,
  withSpan,
  getCurrentSpan,
  addSpanAttribute,
  recordException,
  traceComponent,
  useTraceFunction,
} from '../utils/tracing';

describe('utils/tracing', () => {
  it('getTracer throws before init', () => {
    expect(() => getTracer()).toThrow();
  });

  it('initTracing initializes and getTracer returns a tracer', () => {
    initTracing('ui', 'test', '/otlp', { foo: 'bar' });
    const tracer = getTracer();
    expect(tracer).toBeTruthy();
  });

  it('createSpan creates a span and sets attributes', () => {
    const span = createSpan('op', { a: 1, b: 'x' });
    expect(span).toBeTruthy();
    // @ts-expect-error test-only check of mock properties
    expect(span.attributes.a).toBe(1);
    // @ts-expect-error test-only
    expect(span.ended).toBeUndefined();
    span.end();
    // @ts-expect-error test-only
    expect(span.ended).toBe(true);
  });

  it('withSpan executes function and ends span; success path', async () => {
    const res = await withSpan('work', async (span: any) => {
      // Within span context, getCurrentSpan should be defined
      expect(getCurrentSpan()).toBeTruthy();
      return 'ok';
    });
    expect(res).toBe('ok');
  });

  it('withSpan records error status and rethrows on failure', async () => {
    await expect(withSpan('fail', () => { throw new Error('boom'); })).rejects.toThrow('boom');
  });

  it('addSpanAttribute adds attribute to current span', async () => {
    await withSpan('attr', async (span: any) => {
      addSpanAttribute('k', 'v');
      expect(getCurrentSpan()).toBe(span);
      // @ts-expect-error test-only
      expect(span.attributes.k).toBe('v');
    });
  });

  it('recordException sets status and records error on current span', async () => {
    await withSpan('exc', async (span: any) => {
      const err = new Error('bad');
      recordException(err);
      // @ts-expect-error test-only
      expect(span.status?.code).toBe('ERROR');
      // @ts-expect-error test-only
      expect(span.status?.message).toBe('bad');
      // @ts-expect-error test-only
      expect(span.exception).toBe(err);
    });
  });

  it('traceComponent wraps component render in span and returns element', async () => {
    const C: React.FC = () => React.createElement('div', null, 'hello');
    const Traced = traceComponent(C);
    const elemPromise = Traced({});
    // withSpan returns a Promise, so the traced component resolves to element
    const elem: any = await elemPromise as any;
    expect(elem?.props?.children).toBe('hello');
  });

  it('useTraceFunction traces arbitrary function', async () => {
    const traced = useTraceFunction('task');
    const result = await traced(async () => 42);
    expect(result).toBe(42);
  });
});
