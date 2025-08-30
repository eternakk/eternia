/**
 * OpenTelemetry tracing utilities for the Eternia frontend.
 */

import React from 'react';
import { WebTracerProvider } from '@opentelemetry/sdk-trace-web';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import { BatchSpanProcessor } from '@opentelemetry/sdk-trace-base';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { ZoneContextManager } from '@opentelemetry/context-zone';
import { registerInstrumentations } from '@opentelemetry/instrumentation';
import { DocumentLoadInstrumentation } from '@opentelemetry/instrumentation-document-load';
import { XMLHttpRequestInstrumentation } from '@opentelemetry/instrumentation-xml-http-request';
import { FetchInstrumentation } from '@opentelemetry/instrumentation-fetch';
import { UserInteractionInstrumentation } from '@opentelemetry/instrumentation-user-interaction';
import { trace, context, SpanStatusCode, Span, SpanKind, Context } from '@opentelemetry/api';

// Global tracer instance
let tracer: ReturnType<typeof trace.getTracer> | null = null;

/**
 * Initialize OpenTelemetry tracing for the frontend.
 * 
 * @param serviceName - The name of the service
 * @param environment - The deployment environment (e.g., development, staging, production)
 * @param collectorUrl - The URL of the OpenTelemetry collector
 * @param additionalAttributes - Additional resource attributes to add to spans
 */
export function initTracing(
  serviceName: string,
  environment: string = 'development',
  collectorUrl: string = '/api/v1/traces',
  additionalAttributes: Record<string, string> = {}
): void {
  // Create a resource with service information
  const resource = new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: serviceName,
    [SemanticResourceAttributes.SERVICE_NAMESPACE]: 'eternia',
    [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: environment,
    ...additionalAttributes,
  });

  // Create a tracer provider with the resource
  const provider = new WebTracerProvider({ resource });

  // Create an OTLP exporter and add it to the tracer provider
  const exporter = new OTLPTraceExporter({
    url: collectorUrl,
  });
  
  // Add a batch span processor with the exporter
  provider.addSpanProcessor(new BatchSpanProcessor(exporter));

  // Register the tracer provider
  provider.register({
    contextManager: new ZoneContextManager(),
  });

  // Register instrumentations
  registerInstrumentations({
    instrumentations: [
      // Instrument document load
      new DocumentLoadInstrumentation(),
      
      // Instrument XMLHttpRequest
      new XMLHttpRequestInstrumentation({
        propagateTraceHeaderCorsUrls: [/.*/], // Propagate trace headers to all URLs
      }),
      
      // Instrument fetch
      new FetchInstrumentation({
        propagateTraceHeaderCorsUrls: [/.*/], // Propagate trace headers to all URLs
      }),
      
      // Instrument user interactions (clicks, etc.)
      new UserInteractionInstrumentation(),
    ],
  });

  // Get a tracer
  tracer = trace.getTracer(serviceName);

  console.log(`OpenTelemetry tracing initialized for service ${serviceName} in ${environment} environment`);
}

/**
 * Get the global tracer instance.
 * 
 * @returns The global tracer instance
 * @throws Error if tracing has not been initialized
 */
export function getTracer(): ReturnType<typeof trace.getTracer> {
  if (!tracer) {
    throw new Error('Tracing has not been initialized. Call initTracing() first.');
  }
  return tracer;
}

/**
 * Create a new span.
 * 
 * @param name - The name of the span
 * @param attributes - Attributes to add to the span
 * @param kind - The kind of span
 * @returns The created span
 */
export function createSpan(
  name: string,
  attributes: Record<string, string | number | boolean> = {},
  kind: SpanKind = SpanKind.INTERNAL
): Span {
  if (!tracer) {
    throw new Error('Tracing has not been initialized. Call initTracing() first.');
  }

  const span = tracer.startSpan(name, { kind });
  
  // Add attributes
  Object.entries(attributes).forEach(([key, value]) => {
    span.setAttribute(key, value);
  });
  
  return span;
}

/**
 * Execute a function within the context of a span.
 * 
 * @param name - The name of the span
 * @param fn - The function to execute
 * @param attributes - Attributes to add to the span
 * @param kind - The kind of span
 * @returns The result of the function
 */
export async function withSpan<T>(
  name: string,
  fn: (span: Span) => Promise<T> | T,
  attributes: Record<string, string | number | boolean> = {},
  kind: SpanKind = SpanKind.INTERNAL
): Promise<T> {
  if (!tracer) {
    return fn({} as Span);
  }

  const span = createSpan(name, attributes, kind);
  
  try {
    // Set the span as active
    return await context.with(trace.setSpan(context.active(), span), async () => {
      const result = await fn(span);
      span.end();
      return result;
    });
  } catch (error) {
    // Record the error
    span.setStatus({
      code: SpanStatusCode.ERROR,
      message: error instanceof Error ? error.message : String(error),
    });
    
    if (error instanceof Error) {
      span.recordException(error);
    }
    
    span.end();
    throw error;
  }
}

/**
 * Get the current active span.
 * 
 * @returns The current active span, or undefined if there is no active span
 */
export function getCurrentSpan(): Span | undefined {
  return trace.getSpan(context.active());
}

/**
 * Add an attribute to the current span.
 * 
 * @param key - The attribute key
 * @param value - The attribute value
 */
export function addSpanAttribute(key: string, value: string | number | boolean): void {
  const span = getCurrentSpan();
  if (span) {
    span.setAttribute(key, value);
  }
}

/**
 * Record an exception in the current span.
 * 
 * @param error - The error to record
 */
export function recordException(error: Error): void {
  const span = getCurrentSpan();
  if (span) {
    span.recordException(error);
    span.setStatus({
      code: SpanStatusCode.ERROR,
      message: error.message,
    });
  }
}

/**
 * Create a higher-order component that traces component rendering.
 * 
 * @param Component - The component to trace
 * @param name - The name of the span (defaults to the component's display name)
 * @returns The traced component
 */
export function traceComponent<P extends object>(
  Component: React.ComponentType<P>,
  name?: string
): React.ComponentType<P> {
  const displayName = Component.displayName || Component.name || 'UnknownComponent';
  const spanName = name || `render.${displayName}`;
  
  const TracedComponent = (props: P) => {
    const result = withSpan(
      spanName,
      () => React.createElement(Component, props),
      { component: displayName }
    );
    
    return result;
  };
  
  TracedComponent.displayName = `Traced(${displayName})`;
  
  return TracedComponent;
}

/**
 * Create a hook that traces a function.
 * 
 * @param name - The name of the span
 * @param attributes - Attributes to add to the span
 * @returns A function that traces the provided function
 */
export function useTraceFunction(
  name: string,
  attributes: Record<string, string | number | boolean> = {}
): <T>(fn: () => Promise<T> | T) => Promise<T> {
  return <T>(fn: () => Promise<T> | T): Promise<T> => {
    return withSpan(name, async () => {
      return await fn();
    }, attributes);
  };
}