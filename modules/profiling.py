"""
Profiling Module for Eternia

This module provides performance profiling for critical paths in the Eternia application.
It uses cProfile for function-level profiling and line_profiler for line-level profiling,
and exposes the results as Prometheus metrics for visualization in dashboards.

Example usage:
    from modules.profiling import profile_function, profile_critical_path
    
    # Profile a function with cProfile
    @profile_function
    def my_function():
        # Function code
        pass
    
    # Profile a critical path with detailed metrics
    @profile_critical_path(path_name="simulation_loop")
    def simulation_step():
        # Critical path code
        pass
"""

import cProfile
import functools
import io
import logging
import pstats
import time
from typing import Callable, Dict, List, Optional, Any, Union

from prometheus_client import Histogram, Summary, Gauge

from modules.monitoring import metrics

# Configure logging
logger = logging.getLogger(__name__)

# Define critical paths for profiling
CRITICAL_PATHS = [
    "simulation_loop",
    "companion_update",
    "physics_calculation",
    "emotion_processing",
    "governor_check",
    "world_step",
    "api_request",
]

class ProfilingMetrics:
    """
    Metrics for performance profiling.
    
    This class extends the EterniaMetrics class with additional metrics for
    performance profiling of critical paths.
    """
    
    def __init__(self):
        """Initialize profiling metrics."""
        # Critical path execution time
        self.critical_path_duration_seconds = Histogram(
            'critical_path_duration_seconds',
            'Critical path execution time in seconds',
            ['path_name'],
            buckets=(0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0, float('inf'))
        )
        
        # Function execution time
        self.function_duration_seconds = Histogram(
            'function_duration_seconds',
            'Function execution time in seconds',
            ['function_name', 'module'],
            buckets=(0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0, float('inf'))
        )
        
        # Function call count
        self.function_calls_total = Gauge(
            'function_calls_total',
            'Total number of function calls',
            ['function_name', 'module']
        )
        
        # Memory usage per critical path
        self.critical_path_memory_usage_bytes = Gauge(
            'critical_path_memory_usage_bytes',
            'Memory usage in bytes for a critical path',
            ['path_name']
        )
        
        # CPU time per critical path
        self.critical_path_cpu_seconds = Summary(
            'critical_path_cpu_seconds',
            'CPU time in seconds for a critical path',
            ['path_name', 'cpu_type']
        )
        
        logger.info("Profiling metrics initialized")

# Create a singleton instance
profiling_metrics = ProfilingMetrics()

def profile_function(func: Callable) -> Callable:
    """
    Decorator for profiling a function using cProfile.
    
    This decorator profiles the function using cProfile and records the
    execution time, call count, and other metrics.
    
    Args:
        func: The function to profile
        
    Returns:
        Decorated function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        # Get function metadata
        function_name = func.__name__
        module_name = func.__module__
        
        # Create a Profile instance
        profiler = cProfile.Profile()
        
        # Start profiling
        start_time = time.time()
        profiler.enable()
        
        try:
            # Call the function
            result = func(*args, **kwargs)
            return result
        finally:
            # Stop profiling
            profiler.disable()
            duration = time.time() - start_time
            
            # Record metrics
            profiling_metrics.function_duration_seconds.labels(
                function_name=function_name,
                module=module_name
            ).observe(duration)
            
            # Process profiling statistics
            s = io.StringIO()
            ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
            ps.print_stats(10)  # Print top 10 functions
            
            # Extract call count
            for func_info, (cc, nc, tt, ct, callers) in ps.stats.items():
                if func_info[2] == function_name:
                    profiling_metrics.function_calls_total.labels(
                        function_name=function_name,
                        module=module_name
                    ).set(cc)
                    break
            
            # Log profiling information at debug level
            logger.debug(f"Profile for {function_name}: {s.getvalue()}")
    
    return wrapper

def profile_critical_path(path_name: str) -> Callable:
    """
    Decorator for profiling a critical path.
    
    This decorator profiles a critical path and records detailed metrics
    including execution time, memory usage, and CPU time.
    
    Args:
        path_name: Name of the critical path (must be one of CRITICAL_PATHS)
        
    Returns:
        Decorator function
    """
    if path_name not in CRITICAL_PATHS:
        logger.warning(f"Unknown critical path: {path_name}. Using anyway, but consider adding it to CRITICAL_PATHS.")
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Start profiling
            start_time = time.time()
            start_memory = get_memory_usage()
            
            # Create a Profile instance
            profiler = cProfile.Profile()
            profiler.enable()
            
            try:
                # Call the function
                result = func(*args, **kwargs)
                return result
            finally:
                # Stop profiling
                profiler.disable()
                duration = time.time() - start_time
                end_memory = get_memory_usage()
                memory_used = end_memory - start_memory
                
                # Record metrics
                profiling_metrics.critical_path_duration_seconds.labels(
                    path_name=path_name
                ).observe(duration)
                
                # Record memory usage if positive (to avoid misleading metrics due to GC)
                if memory_used > 0:
                    profiling_metrics.critical_path_memory_usage_bytes.labels(
                        path_name=path_name
                    ).set(memory_used)
                
                # Process profiling statistics
                s = io.StringIO()
                ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
                ps.print_stats(10)  # Print top 10 functions
                
                # Extract CPU times
                total_cpu_time = 0
                for func_info, (cc, nc, tt, ct, callers) in ps.stats.items():
                    total_cpu_time += tt
                
                # Record CPU time
                profiling_metrics.critical_path_cpu_seconds.labels(
                    path_name=path_name,
                    cpu_type='total'
                ).observe(total_cpu_time)
                
                # Log profiling information
                logger.debug(f"Profile for {path_name}: duration={duration:.4f}s, memory={memory_used} bytes")
                logger.debug(f"Detailed profile for {path_name}: {s.getvalue()}")
        
        return wrapper
    
    return decorator

def get_memory_usage() -> int:
    """
    Get the current memory usage.
    
    Returns:
        Current memory usage in bytes
    """
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss
    except ImportError:
        logger.warning("psutil not installed, cannot measure memory usage")
        return 0
    except Exception as e:
        logger.error(f"Error getting memory usage: {e}")
        return 0

def get_top_functions(path_name: str, limit: int = 5) -> List[Dict[str, Union[str, float]]]:
    """
    Get the top functions for a critical path based on execution time.
    
    Args:
        path_name: Name of the critical path
        limit: Maximum number of functions to return
        
    Returns:
        List of dictionaries with function information
    """
    # This would normally query Prometheus for the data
    # For now, return a placeholder
    return [
        {
            "function_name": "placeholder",
            "module": "placeholder",
            "duration": 0.0,
            "calls": 0
        }
    ]

def create_profile_dashboard() -> None:
    """
    Create a Grafana dashboard for performance profiling.
    
    This function creates a Grafana dashboard for visualizing performance
    profiling metrics. It uses the Grafana API to create the dashboard.
    """
    # This would normally use the Grafana API to create a dashboard
    # For now, just log a message
    logger.info("Creating performance profiling dashboard")
    
    # In a real implementation, this would:
    # 1. Create a dashboard JSON definition
    # 2. Use the Grafana API to create or update the dashboard
    # 3. Return the dashboard URL