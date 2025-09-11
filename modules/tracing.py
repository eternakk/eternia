"""
OpenTelemetry tracing module for Eternia.

This module provides utilities for distributed tracing using OpenTelemetry.
"""

import os
import logging
from functools import wraps
from typing import Optional, Callable, Dict, Any, TypeVar, cast

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlite3 import SQLite3Instrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor

# Type variables for decorators
F = TypeVar('F', bound=Callable[..., Any])

# Configure logger
logger = logging.getLogger(__name__)

# Global tracer instance
_tracer = None

def setup_tracing(
    service_name: str,
    environment: str = "development",
    otlp_endpoint: Optional[str] = None,
    resource_attributes: Optional[Dict[str, str]] = None,
    enable_logging_instrumentation: bool = True,
    enable_sqlite_instrumentation: bool = True,
    enable_requests_instrumentation: bool = True,
) -> None:
    """
    Set up OpenTelemetry tracing for the application.

    Args:
        service_name: The name of the service.
        environment: The deployment environment (e.g., development, staging, production).
        otlp_endpoint: The endpoint for the OpenTelemetry Collector. If None, uses the
                      OTEL_EXPORTER_OTLP_ENDPOINT environment variable or defaults to
                      "http://localhost:4317".
        resource_attributes: Additional resource attributes to add to spans.
        enable_logging_instrumentation: Whether to enable logging instrumentation.
        enable_sqlite_instrumentation: Whether to enable SQLite instrumentation.
        enable_requests_instrumentation: Whether to enable requests instrumentation.
    """
    global _tracer

    # Get the OTLP endpoint from the environment variable if not provided
    if otlp_endpoint is None:
        otlp_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")

    # Create resource with service information
    attributes = {
        "service.name": service_name,
        "service.namespace": "eternia",
        "deployment.environment": environment,
    }

    # Add additional resource attributes if provided
    if resource_attributes:
        attributes.update(resource_attributes)

    resource = Resource.create(attributes)

    # Create a tracer provider with the resource
    tracer_provider = TracerProvider(resource=resource)

    # Create an OTLP exporter and add it to the tracer provider
    otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)

    # Set the tracer provider
    trace.set_tracer_provider(tracer_provider)

    # Get a tracer
    _tracer = trace.get_tracer(service_name)

    # Instrument libraries
    if enable_requests_instrumentation:
        RequestsInstrumentor().instrument()

    if enable_sqlite_instrumentation:
        SQLite3Instrumentor().instrument()

    if enable_logging_instrumentation:
        LoggingInstrumentor().instrument(set_logging_format=True)

    logger.info(f"OpenTelemetry tracing initialized for service {service_name} in {environment} environment")

def instrument_fastapi(app):
    """
    Instrument a FastAPI application with OpenTelemetry.

    Args:
        app: The FastAPI application to instrument.
    """
    FastAPIInstrumentor.instrument_app(app)
    logger.info("FastAPI application instrumented with OpenTelemetry")

def get_tracer():
    """
    Get the global tracer instance.

    Returns:
        The global tracer instance.
    """
    if _tracer is None:
        raise RuntimeError("Tracing has not been set up. Call setup_tracing() first.")
    return _tracer

def trace_function(name: Optional[str] = None) -> Callable[[F], F]:
    """
    Decorator to trace a function.

    Args:
        name: The name of the span. If None, uses the function name.

    Returns:
        The decorated function.
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if _tracer is None:
                return func(*args, **kwargs)

            # Use the provided name or the function name
            span_name = name or f"{func.__module__}.{func.__qualname__}"

            with _tracer.start_as_current_span(span_name) as span:
                # Add function arguments as span attributes
                # Be careful not to include sensitive information
                span.set_attribute("function.name", func.__qualname__)
                span.set_attribute("function.module", func.__module__)

                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    # Record the exception in the span
                    span.record_exception(e)
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    raise

        return cast(F, wrapper)
    return decorator

def create_span(name: str, attributes: Optional[Dict[str, Any]] = None) -> trace.Span:
    """
    Create a new span.

    Args:
        name: The name of the span.
        attributes: Attributes to add to the span.

    Returns:
        The created span.
    """
    if _tracer is None:
        raise RuntimeError("Tracing has not been set up. Call setup_tracing() first.")

    span = _tracer.start_span(name)
    
    if attributes:
        for key, value in attributes.items():
            span.set_attribute(key, value)
    
    return span

def get_current_span() -> Optional[trace.Span]:
    """
    Get the current active span.

    Returns:
        The current active span, or None if there is no active span.
    """
    return trace.get_current_span()

def add_span_attribute(key: str, value: Any) -> None:
    """
    Add an attribute to the current span.

    Args:
        key: The attribute key.
        value: The attribute value.
    """
    span = get_current_span()
    if span:
        span.set_attribute(key, value)

def record_exception(exception: Exception) -> None:
    """
    Record an exception in the current span.

    Args:
        exception: The exception to record.
    """
    span = get_current_span()
    if span:
        span.record_exception(exception)
        span.set_status(trace.Status(trace.StatusCode.ERROR, str(exception)))

def inject_trace_context(carrier: Dict[str, str]) -> None:
    """
    Inject the current trace context into a carrier.

    This is useful for propagating trace context across service boundaries.

    Args:
        carrier: The carrier to inject the trace context into.
    """
    TraceContextTextMapPropagator().inject(carrier)

def extract_trace_context(carrier: Dict[str, str]) -> trace.SpanContext:
    """
    Extract a trace context from a carrier.

    This is useful for continuing a trace across service boundaries.

    Args:
        carrier: The carrier containing the trace context.

    Returns:
        The extracted span context.
    """
    context = TraceContextTextMapPropagator().extract(carrier)
    return trace.get_current_span(context).get_span_context()