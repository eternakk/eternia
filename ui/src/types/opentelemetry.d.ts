// Ambient declarations to satisfy TypeScript when OpenTelemetry packages are not installed.
// These modules are not bundled unless imported at runtime; this is only for type-checking.
/* eslint-disable @typescript-eslint/no-explicit-any */

declare module '@opentelemetry/sdk-trace-web' {
  export const WebTracerProvider: any;
}

declare module '@opentelemetry/resources' {
  export const Resource: any;
}

declare module '@opentelemetry/semantic-conventions' {
  export const SemanticResourceAttributes: any;
}

declare module '@opentelemetry/sdk-trace-base' {
  export const BatchSpanProcessor: any;
}

declare module '@opentelemetry/exporter-trace-otlp-http' {
  export const OTLPTraceExporter: any;
}

declare module '@opentelemetry/context-zone' {
  export const ZoneContextManager: any;
}

declare module '@opentelemetry/instrumentation' {
  export const registerInstrumentations: any;
}

declare module '@opentelemetry/instrumentation-document-load' {
  export const DocumentLoadInstrumentation: any;
}

declare module '@opentelemetry/instrumentation-xml-http-request' {
  export const XMLHttpRequestInstrumentation: any;
}

declare module '@opentelemetry/instrumentation-fetch' {
  export const FetchInstrumentation: any;
}

declare module '@opentelemetry/instrumentation-user-interaction' {
  export const UserInteractionInstrumentation: any;
}

declare module '@opentelemetry/api' {
  export type Span = any;
  export const SpanStatusCode: any;
  export const SpanKind: any;
  export const trace: any;
  export const context: any;
}