"""
Circuit Breaker Module for Eternia

This module provides a circuit breaker implementation for external service calls.
It helps to prevent cascading failures and improve resilience by failing fast
when external services are unavailable or experiencing issues.

Example usage:
    from modules.utilities.circuit_breaker import CircuitBreaker

    # Create a circuit breaker for an external service
    breaker = CircuitBreaker(
        name="example-service",
        failure_threshold=5,
        reset_timeout=60,
        half_open_timeout=30
    )

    # Use the circuit breaker to make an external service call
    try:
        with breaker:
            # Make the external service call
            result = requests.get("https://example.com/api")
            return result.json()
    except CircuitBreakerOpen:
        # Handle the case where the circuit breaker is open
        return {"error": "Service unavailable"}
    except Exception as e:
        # Handle other exceptions
        return {"error": str(e)}
"""

import asyncio
import functools
import logging
import time
from enum import Enum
from typing import Any, Callable, Dict, Optional, TypeVar, cast

logger = logging.getLogger(__name__)

# Type variables for generic function types
T = TypeVar("T")
R = TypeVar("R")


class CircuitState(Enum):
    """
    Enum representing the possible states of a circuit breaker.
    
    - CLOSED: The circuit is closed and requests are allowed through.
    - OPEN: The circuit is open and requests are blocked.
    - HALF_OPEN: The circuit is half-open, allowing a limited number of requests through
      to test if the service has recovered.
    """
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerOpen(Exception):
    """
    Exception raised when a request is made while the circuit breaker is open.
    """
    def __init__(self, name: str, reset_time: float):
        """
        Initialize the exception.
        
        Args:
            name: The name of the circuit breaker.
            reset_time: The time when the circuit breaker will reset.
        """
        self.name = name
        self.reset_time = reset_time
        self.reset_time_str = time.strftime("%H:%M:%S", time.localtime(reset_time))
        super().__init__(
            f"Circuit breaker '{name}' is open. "
            f"Requests are blocked until {self.reset_time_str}."
        )


class CircuitBreaker:
    """
    Circuit breaker implementation for external service calls.
    
    This class implements the circuit breaker pattern, which helps to prevent
    cascading failures and improve resilience by failing fast when external
    services are unavailable or experiencing issues.
    
    Attributes:
        name: The name of the circuit breaker.
        failure_threshold: The number of consecutive failures before the circuit opens.
        reset_timeout: The time in seconds to wait before transitioning from open to half-open.
        half_open_timeout: The time in seconds to wait in half-open state before closing.
        state: The current state of the circuit breaker.
        failure_count: The current count of consecutive failures.
        last_failure_time: The time of the last failure.
        reset_time: The time when the circuit breaker will reset.
        successful_test_calls: The number of successful test calls in half-open state.
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        reset_timeout: int = 60,
        half_open_timeout: int = 30,
        required_success_count: int = 3
    ):
        """
        Initialize the circuit breaker.
        
        Args:
            name: The name of the circuit breaker.
            failure_threshold: The number of consecutive failures before the circuit opens.
                Defaults to 5.
            reset_timeout: The time in seconds to wait before transitioning from open to half-open.
                Defaults to 60.
            half_open_timeout: The time in seconds to wait in half-open state before closing.
                Defaults to 30.
            required_success_count: The number of successful calls required in half-open state
                before closing the circuit. Defaults to 3.
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.half_open_timeout = half_open_timeout
        self.required_success_count = required_success_count
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.reset_time = 0.0
        self.successful_test_calls = 0
        self.half_open_start_time = 0.0
        
        logger.info(
            f"Circuit breaker '{name}' initialized with failure_threshold={failure_threshold}, "
            f"reset_timeout={reset_timeout}s, half_open_timeout={half_open_timeout}s"
        )
    
    def __enter__(self):
        """
        Enter the context manager.
        
        Raises:
            CircuitBreakerOpen: If the circuit breaker is open.
        """
        self._before_call()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager.
        
        Args:
            exc_type: The exception type, if an exception was raised.
            exc_val: The exception value, if an exception was raised.
            exc_tb: The exception traceback, if an exception was raised.
        
        Returns:
            bool: True if the exception should be suppressed, False otherwise.
        """
        if exc_type is None:
            # No exception, call was successful
            self._on_success()
        else:
            # An exception occurred, call failed
            self._on_failure()
        
        # Don't suppress the exception
        return False
    
    def _before_call(self):
        """
        Check if the circuit breaker is open before making a call.
        
        Raises:
            CircuitBreakerOpen: If the circuit breaker is open.
        """
        now = time.time()
        
        if self.state == CircuitState.OPEN:
            # Check if it's time to transition to half-open
            if now >= self.reset_time:
                logger.info(
                    f"Circuit breaker '{self.name}' transitioning from open to half-open"
                )
                self.state = CircuitState.HALF_OPEN
                self.successful_test_calls = 0
                self.half_open_start_time = now
            else:
                # Circuit is still open, block the request
                logger.warning(
                    f"Circuit breaker '{self.name}' is open. "
                    f"Requests are blocked until {time.strftime('%H:%M:%S', time.localtime(self.reset_time))}"
                )
                raise CircuitBreakerOpen(self.name, self.reset_time)
        
        if self.state == CircuitState.HALF_OPEN:
            # Check if we've been in half-open state for too long
            if now - self.half_open_start_time > self.half_open_timeout:
                logger.warning(
                    f"Circuit breaker '{self.name}' has been in half-open state for too long. "
                    f"Transitioning back to open state."
                )
                self._trip()
                raise CircuitBreakerOpen(self.name, self.reset_time)
    
    def _on_success(self):
        """
        Handle a successful call.
        """
        if self.state == CircuitState.CLOSED:
            # Reset failure count on success in closed state
            if self.failure_count > 0:
                logger.debug(
                    f"Circuit breaker '{self.name}' resetting failure count from {self.failure_count} to 0"
                )
                self.failure_count = 0
        
        elif self.state == CircuitState.HALF_OPEN:
            # Increment successful test calls in half-open state
            self.successful_test_calls += 1
            logger.info(
                f"Circuit breaker '{self.name}' successful test call: "
                f"{self.successful_test_calls}/{self.required_success_count}"
            )
            
            # If we've had enough successful test calls, close the circuit
            if self.successful_test_calls >= self.required_success_count:
                logger.info(
                    f"Circuit breaker '{self.name}' transitioning from half-open to closed "
                    f"after {self.successful_test_calls} successful test calls"
                )
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.successful_test_calls = 0
    
    def _on_failure(self):
        """
        Handle a failed call.
        """
        if self.state == CircuitState.CLOSED:
            # Increment failure count in closed state
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            logger.warning(
                f"Circuit breaker '{self.name}' failure count: {self.failure_count}/{self.failure_threshold}"
            )
            
            # If we've reached the failure threshold, open the circuit
            if self.failure_count >= self.failure_threshold:
                self._trip()
        
        elif self.state == CircuitState.HALF_OPEN:
            # Any failure in half-open state opens the circuit again
            logger.warning(
                f"Circuit breaker '{self.name}' failed in half-open state. "
                f"Transitioning back to open state."
            )
            self._trip()
    
    def _trip(self):
        """
        Trip the circuit breaker, transitioning to the open state.
        """
        self.state = CircuitState.OPEN
        self.reset_time = time.time() + self.reset_timeout
        
        logger.warning(
            f"Circuit breaker '{self.name}' tripped. "
            f"Circuit will remain open until {time.strftime('%H:%M:%S', time.localtime(self.reset_time))}"
        )
    
    def reset(self):
        """
        Reset the circuit breaker to its initial closed state.
        """
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.reset_time = 0.0
        self.successful_test_calls = 0
        self.half_open_start_time = 0.0
        
        logger.info(f"Circuit breaker '{self.name}' manually reset to closed state")
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get the current state of the circuit breaker.
        
        Returns:
            Dict[str, Any]: The current state.
        """
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "last_failure_time": self.last_failure_time,
            "reset_time": self.reset_time,
            "successful_test_calls": self.successful_test_calls,
            "required_success_count": self.required_success_count,
            "half_open_start_time": self.half_open_start_time,
            "half_open_timeout": self.half_open_timeout,
        }


def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    reset_timeout: int = 60,
    half_open_timeout: int = 30,
    required_success_count: int = 3,
    fallback_result: Optional[Any] = None
) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """
    Decorator for applying a circuit breaker to a function.
    
    Args:
        name: The name of the circuit breaker.
        failure_threshold: The number of consecutive failures before the circuit opens.
            Defaults to 5.
        reset_timeout: The time in seconds to wait before transitioning from open to half-open.
            Defaults to 60.
        half_open_timeout: The time in seconds to wait in half-open state before closing.
            Defaults to 30.
        required_success_count: The number of successful calls required in half-open state
            before closing the circuit. Defaults to 3.
        fallback_result: The result to return when the circuit is open.
            If None, a CircuitBreakerOpen exception will be raised. Defaults to None.
    
    Returns:
        Callable: The decorated function.
    """
    breaker = CircuitBreaker(
        name=name,
        failure_threshold=failure_threshold,
        reset_timeout=reset_timeout,
        half_open_timeout=half_open_timeout,
        required_success_count=required_success_count
    )
    
    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> R:
            try:
                with breaker:
                    return func(*args, **kwargs)
            except CircuitBreakerOpen:
                if fallback_result is not None:
                    return cast(R, fallback_result)
                raise
        
        return wrapper
    
    return decorator


def async_circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    reset_timeout: int = 60,
    half_open_timeout: int = 30,
    required_success_count: int = 3,
    fallback_result: Optional[Any] = None
) -> Callable[[Callable[..., asyncio.Future[R]]], Callable[..., asyncio.Future[R]]]:
    """
    Decorator for applying a circuit breaker to an async function.
    
    Args:
        name: The name of the circuit breaker.
        failure_threshold: The number of consecutive failures before the circuit opens.
            Defaults to 5.
        reset_timeout: The time in seconds to wait before transitioning from open to half-open.
            Defaults to 60.
        half_open_timeout: The time in seconds to wait in half-open state before closing.
            Defaults to 30.
        required_success_count: The number of successful calls required in half-open state
            before closing the circuit. Defaults to 3.
        fallback_result: The result to return when the circuit is open.
            If None, a CircuitBreakerOpen exception will be raised. Defaults to None.
    
    Returns:
        Callable: The decorated async function.
    """
    breaker = CircuitBreaker(
        name=name,
        failure_threshold=failure_threshold,
        reset_timeout=reset_timeout,
        half_open_timeout=half_open_timeout,
        required_success_count=required_success_count
    )
    
    def decorator(func: Callable[..., asyncio.Future[R]]) -> Callable[..., asyncio.Future[R]]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> R:
            try:
                with breaker:
                    return await func(*args, **kwargs)
            except CircuitBreakerOpen:
                if fallback_result is not None:
                    return cast(R, fallback_result)
                raise
        
        return wrapper
    
    return decorator


# Registry of circuit breakers for monitoring and management
_circuit_breakers: Dict[str, CircuitBreaker] = {}


def get_circuit_breaker(name: str) -> Optional[CircuitBreaker]:
    """
    Get a circuit breaker by name.
    
    Args:
        name: The name of the circuit breaker.
    
    Returns:
        Optional[CircuitBreaker]: The circuit breaker, or None if not found.
    """
    return _circuit_breakers.get(name)


def register_circuit_breaker(breaker: CircuitBreaker) -> None:
    """
    Register a circuit breaker for monitoring and management.
    
    Args:
        breaker: The circuit breaker to register.
    """
    _circuit_breakers[breaker.name] = breaker
    logger.info(f"Circuit breaker '{breaker.name}' registered")


def create_circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    reset_timeout: int = 60,
    half_open_timeout: int = 30,
    required_success_count: int = 3
) -> CircuitBreaker:
    """
    Create and register a circuit breaker.
    
    Args:
        name: The name of the circuit breaker.
        failure_threshold: The number of consecutive failures before the circuit opens.
            Defaults to 5.
        reset_timeout: The time in seconds to wait before transitioning from open to half-open.
            Defaults to 60.
        half_open_timeout: The time in seconds to wait in half-open state before closing.
            Defaults to 30.
        required_success_count: The number of successful calls required in half-open state
            before closing the circuit. Defaults to 3.
    
    Returns:
        CircuitBreaker: The created circuit breaker.
    """
    breaker = CircuitBreaker(
        name=name,
        failure_threshold=failure_threshold,
        reset_timeout=reset_timeout,
        half_open_timeout=half_open_timeout,
        required_success_count=required_success_count
    )
    register_circuit_breaker(breaker)
    return breaker


def get_all_circuit_breakers() -> Dict[str, CircuitBreaker]:
    """
    Get all registered circuit breakers.
    
    Returns:
        Dict[str, CircuitBreaker]: A dictionary of circuit breakers, keyed by name.
    """
    return _circuit_breakers.copy()


def get_circuit_breaker_states() -> Dict[str, Dict[str, Any]]:
    """
    Get the states of all registered circuit breakers.
    
    Returns:
        Dict[str, Dict[str, Any]]: A dictionary of circuit breaker states, keyed by name.
    """
    return {name: breaker.get_state() for name, breaker in _circuit_breakers.items()}


def reset_all_circuit_breakers() -> None:
    """
    Reset all registered circuit breakers to their initial closed state.
    """
    for breaker in _circuit_breakers.values():
        breaker.reset()
    
    logger.info("All circuit breakers reset to closed state")