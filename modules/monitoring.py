"""
Monitoring Module for Eternia

This module provides metrics collection and exposition for the Eternia application.
It uses the Prometheus client library to collect metrics and expose them via HTTP.

Example usage:
    from modules.monitoring import metrics
    
    # Increment a counter
    metrics.http_requests_total.labels(method='GET', endpoint='/api/zones').inc()
    
    # Observe a histogram
    metrics.http_request_duration_seconds.observe(0.5)
"""

import time
import logging
from typing import Callable, Dict, Any, Optional
from functools import wraps

from prometheus_client import Counter, Histogram, Gauge, Summary
from prometheus_client import REGISTRY, PROCESS_COLLECTOR, PLATFORM_COLLECTOR
from prometheus_client.exposition import generate_latest

from config.config_manager import config
from modules.validation import validate_params, validate_type

# Configure logging
logger = logging.getLogger(__name__)

class EterniaMetrics:
    """
    Metrics collection for the Eternia application.
    
    This class provides metrics collectors for various aspects of the application,
    including HTTP requests, simulation performance, and system resources.
    """
    
    def __init__(self) -> None:
        """Initialize the metrics collectors."""
        # HTTP metrics
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total number of HTTP requests',
            ['method', 'endpoint', 'status']
        )
        
        self.http_request_duration_seconds = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint'],
            buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, float('inf'))
        )
        
        # Simulation metrics
        self.simulation_step_duration_seconds = Histogram(
            'simulation_step_duration_seconds',
            'Simulation step duration in seconds',
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, float('inf'))
        )
        
        self.simulation_steps_total = Counter(
            'simulation_steps_total',
            'Total number of simulation steps'
        )
        
        self.simulation_entities = Gauge(
            'simulation_entities',
            'Number of entities in the simulation',
            ['type']
        )
        
        # Governor metrics
        self.governor_interventions_total = Counter(
            'governor_interventions_total',
            'Total number of governor interventions',
            ['type', 'reason']
        )
        
        self.governor_state = Gauge(
            'governor_state',
            'Current state of the governor',
            ['state']
        )
        
        # System metrics
        self.system_memory_usage_bytes = Gauge(
            'system_memory_usage_bytes',
            'Memory usage in bytes'
        )
        
        # API metrics
        self.api_requests_in_flight = Gauge(
            'api_requests_in_flight',
            'Number of API requests currently being processed'
        )
        
        self.api_request_latency = Summary(
            'api_request_latency_seconds',
            'API request latency in seconds',
            ['method', 'endpoint']
        )
        
        # Quantum metrics (Sprint 3)
        self.quantum_requests_total = Counter(
            'quantum_requests_total',
            'Total number of quantum API requests',
            ['type', 'status']
        )
        self.quantum_timeouts_total = Counter(
            'quantum_timeouts_total',
            'Total number of timed out quantum API requests',
            ['type']
        )
        # Using a gauge for average entropy; we set it to the latest observed value.
        # Prometheus can compute averages over time via recording rules.
        self.quantum_entropy_avg = Gauge(
            'quantum_entropy_avg',
            'Average entropy of QRNG results (last observed value)'
        )
        self.quantum_entropy = Summary(
            'quantum_entropy',
            'Observed entropy from QRNG draws'
        )
        
        logger.info("Eternia metrics initialized")
    
    @validate_params(method=lambda v, p: validate_type(v, str, p))
    def track_http_request(self, method: str, endpoint: str, status_code: int, duration: float) -> None:
        """
        Track an HTTP request.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: Request endpoint
            status_code: HTTP status code
            duration: Request duration in seconds
            
        Raises:
            TypeValidationError: If method is not a string
        """
        try:
            self.http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status=str(status_code)
            ).inc()
            
            self.http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            logger.debug(f"Tracked HTTP request: {method} {endpoint} {status_code} {duration:.4f}s")
        except Exception as e:
            logger.error(f"Error tracking HTTP request: {e}")
    
    def track_simulation_step(self, duration: float) -> None:
        """
        Track a simulation step.
        
        Args:
            duration: Step duration in seconds
        """
        try:
            self.simulation_step_duration_seconds.observe(duration)
            self.simulation_steps_total.inc()
            
            logger.debug(f"Tracked simulation step: {duration:.4f}s")
        except Exception as e:
            logger.error(f"Error tracking simulation step: {e}")
    
    @validate_params(entity_type=lambda v, p: validate_type(v, str, p))
    def set_simulation_entities(self, entity_type: str, count: int) -> None:
        """
        Set the number of entities in the simulation.
        
        Args:
            entity_type: Type of entity (companion, zone, etc.)
            count: Number of entities
            
        Raises:
            TypeValidationError: If entity_type is not a string
        """
        try:
            self.simulation_entities.labels(type=entity_type).set(count)
            
            logger.debug(f"Set simulation entities: {entity_type}={count}")
        except Exception as e:
            logger.error(f"Error setting simulation entities: {e}")
    
    @validate_params(
        intervention_type=lambda v, p: validate_type(v, str, p),
        reason=lambda v, p: validate_type(v, str, p)
    )
    def track_governor_intervention(self, intervention_type: str, reason: str) -> None:
        """
        Track a governor intervention.
        
        Args:
            intervention_type: Type of intervention (pause, rollback, etc.)
            reason: Reason for the intervention
            
        Raises:
            TypeValidationError: If intervention_type or reason is not a string
        """
        try:
            self.governor_interventions_total.labels(
                type=intervention_type,
                reason=reason
            ).inc()
            
            logger.debug(f"Tracked governor intervention: {intervention_type} due to {reason}")
        except Exception as e:
            logger.error(f"Error tracking governor intervention: {e}")
    
    @validate_params(state=lambda v, p: validate_type(v, str, p))
    def set_governor_state(self, state: str) -> None:
        """
        Set the current state of the governor.
        
        Args:
            state: Current state (running, paused, etc.)
            
        Raises:
            TypeValidationError: If state is not a string
        """
        try:
            # Reset all states
            for s in ['running', 'paused', 'error']:
                self.governor_state.labels(state=s).set(0)
            
            # Set the current state
            self.governor_state.labels(state=state).set(1)
            
            logger.debug(f"Set governor state: {state}")
        except Exception as e:
            logger.error(f"Error setting governor state: {e}")
    
    def set_memory_usage(self, usage_bytes: int) -> None:
        """
        Set the current memory usage.
        
        Args:
            usage_bytes: Memory usage in bytes
        """
        try:
            self.system_memory_usage_bytes.set(usage_bytes)
            
            logger.debug(f"Set memory usage: {usage_bytes} bytes")
        except Exception as e:
            logger.error(f"Error setting memory usage: {e}")
    
    def observe_qrng_entropy(self, entropy: float) -> None:
        """Observe entropy for QRNG results and update averages."""
        try:
            self.quantum_entropy.observe(float(entropy))
            self.quantum_entropy_avg.set(float(entropy))
        except Exception as e:
            logger.error(f"Error observing quantum entropy: {e}")

    def inc_quantum_request(self, kind: str, status: str) -> None:
        """Increment quantum request counter for a given kind and status."""
        try:
            self.quantum_requests_total.labels(type=str(kind), status=str(status)).inc()
        except Exception as e:
            logger.error(f"Error incrementing quantum request counter: {e}")

    def inc_quantum_timeout(self, kind: str) -> None:
        """Increment quantum timeouts counter for a given kind."""
        try:
            self.quantum_timeouts_total.labels(type=str(kind)).inc()
        except Exception as e:
            logger.error(f"Error incrementing quantum timeout counter: {e}")

    def generate_latest_metrics(self) -> bytes:
        """
        Generate the latest metrics in Prometheus format.
        
        Returns:
            Metrics in Prometheus format
        """
        try:
            return generate_latest(REGISTRY)
        except Exception as e:
            logger.error(f"Error generating metrics: {e}")
            return b""


def http_metrics_middleware(app):
    """
    FastAPI middleware for tracking HTTP request metrics.
    
    Args:
        app: FastAPI application
    """
    @app.middleware("http")
    async def track_request_metrics(request, call_next):
        start_time = time.time()
        
        # Increment in-flight requests
        metrics.api_requests_in_flight.inc()
        
        try:
            response = await call_next(request)
            
            # Track request metrics
            duration = time.time() - start_time
            metrics.track_http_request(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code,
                duration=duration
            )
            
            # Track request latency
            metrics.api_request_latency.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)
            
            return response
        except Exception as e:
            logger.error(f"Error in HTTP request: {e}")
            raise
        finally:
            # Decrement in-flight requests
            metrics.api_requests_in_flight.dec()


def track_time(metric: Optional[Histogram] = None):
    """
    Decorator for tracking the execution time of a function.
    
    Args:
        metric: Histogram to use for tracking. If None, uses simulation_step_duration_seconds.
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Use the provided metric or default to simulation_step_duration_seconds
            if metric is not None:
                metric.observe(duration)
            else:
                metrics.simulation_step_duration_seconds.observe(duration)
                
            return result
        return wrapper
    return decorator


# Create a singleton instance
metrics = EterniaMetrics()