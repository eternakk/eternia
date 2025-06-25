"""
Circuit Breaker Example for Eternia

This example demonstrates how to use the circuit breaker pattern to make external service calls
more resilient. It shows both synchronous and asynchronous usage patterns.

To run this example:
    python -m examples.circuit_breaker_example
"""

import asyncio
import logging
import random
import time
from typing import Dict, Any

import requests

from modules.utilities.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpen,
    circuit_breaker,
    async_circuit_breaker,
    create_circuit_breaker,
    get_circuit_breaker_states,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("circuit_breaker_example")


# Example 1: Using the CircuitBreaker class directly with a context manager
def example_context_manager():
    """
    Example of using the CircuitBreaker class directly with a context manager.
    """
    logger.info("Example 1: Using CircuitBreaker with context manager")
    
    # Create a circuit breaker for the external service
    breaker = CircuitBreaker(
        name="example-service",
        failure_threshold=3,  # Trip after 3 consecutive failures
        reset_timeout=10,     # Wait 10 seconds before trying again
        half_open_timeout=5,  # Allow 5 seconds in half-open state
        required_success_count=2  # Require 2 successful calls to close the circuit
    )
    
    # Simulate some service calls
    for i in range(10):
        try:
            with breaker:
                # Simulate an external service call
                result = call_external_service(i)
                logger.info(f"Call {i} succeeded: {result}")
        except CircuitBreakerOpen as e:
            logger.warning(f"Call {i} blocked: {e}")
        except Exception as e:
            logger.error(f"Call {i} failed: {e}")
        
        # Add a small delay between calls
        time.sleep(1)


# Example 2: Using the circuit_breaker decorator
@circuit_breaker(
    name="weather-service",
    failure_threshold=3,
    reset_timeout=10,
    fallback_result={"temperature": 0, "condition": "Unknown"}
)
def get_weather(city: str) -> Dict[str, Any]:
    """
    Example of using the circuit_breaker decorator to protect a function.
    
    Args:
        city: The city to get weather for.
        
    Returns:
        Dict[str, Any]: The weather data.
    """
    # Simulate an external API call to get weather data
    # In a real application, this would be an actual API call
    if random.random() < 0.7:  # 70% chance of success
        return {
            "city": city,
            "temperature": random.randint(0, 30),
            "condition": random.choice(["Sunny", "Cloudy", "Rainy", "Snowy"])
        }
    else:
        # Simulate a service failure
        raise Exception("Weather service unavailable")


def example_decorator():
    """
    Example of using the circuit_breaker decorator.
    """
    logger.info("Example 2: Using circuit_breaker decorator")
    
    # Make some calls to the weather service
    for i in range(10):
        try:
            city = random.choice(["New York", "London", "Tokyo", "Paris", "Sydney"])
            weather = get_weather(city)
            logger.info(f"Weather in {city}: {weather}")
        except Exception as e:
            logger.error(f"Failed to get weather: {e}")
        
        # Add a small delay between calls
        time.sleep(1)


# Example 3: Using the async_circuit_breaker decorator
@async_circuit_breaker(
    name="news-service",
    failure_threshold=3,
    reset_timeout=10,
    fallback_result={"headlines": ["No news available"]}
)
async def get_news_headlines() -> Dict[str, Any]:
    """
    Example of using the async_circuit_breaker decorator to protect an async function.
    
    Returns:
        Dict[str, Any]: The news headlines.
    """
    # Simulate an async external API call to get news headlines
    # In a real application, this would be an actual API call using aiohttp or httpx
    await asyncio.sleep(0.5)  # Simulate network delay
    
    if random.random() < 0.7:  # 70% chance of success
        return {
            "headlines": [
                "Breaking News: " + random.choice([
                    "New AI breakthrough announced",
                    "Global climate agreement reached",
                    "Major tech company announces new product",
                    "Scientific discovery changes understanding of universe"
                ])
                for _ in range(3)
            ]
        }
    else:
        # Simulate a service failure
        raise Exception("News service unavailable")


async def example_async_decorator():
    """
    Example of using the async_circuit_breaker decorator.
    """
    logger.info("Example 3: Using async_circuit_breaker decorator")
    
    # Make some calls to the news service
    for i in range(10):
        try:
            headlines = await get_news_headlines()
            logger.info(f"Headlines: {headlines}")
        except Exception as e:
            logger.error(f"Failed to get headlines: {e}")
        
        # Add a small delay between calls
        await asyncio.sleep(1)


# Example 4: Using the circuit breaker registry
def example_registry():
    """
    Example of using the circuit breaker registry.
    """
    logger.info("Example 4: Using circuit breaker registry")
    
    # Create and register a circuit breaker
    create_circuit_breaker(
        name="stock-service",
        failure_threshold=3,
        reset_timeout=10
    )
    
    # Get the states of all registered circuit breakers
    states = get_circuit_breaker_states()
    logger.info(f"Circuit breaker states: {states}")


# Helper function to simulate an external service call
def call_external_service(call_id: int) -> Dict[str, Any]:
    """
    Simulate an external service call.
    
    Args:
        call_id: The ID of the call.
        
    Returns:
        Dict[str, Any]: The response data.
        
    Raises:
        Exception: If the service call fails.
    """
    # Simulate a service that fails after a few calls
    if call_id >= 3 and call_id <= 5:
        raise Exception("Service temporarily unavailable")
    
    # Simulate a successful response
    return {"status": "ok", "data": f"Response from call {call_id}"}


# Example 5: Real-world example with actual HTTP request
def example_real_http_request():
    """
    Example of using the circuit breaker with a real HTTP request.
    """
    logger.info("Example 5: Using circuit breaker with real HTTP request")
    
    # Create a circuit breaker for the HTTP service
    breaker = CircuitBreaker(
        name="http-service",
        failure_threshold=3,
        reset_timeout=10
    )
    
    # Make some HTTP requests
    for i in range(5):
        try:
            with breaker:
                # Make a real HTTP request
                # Note: This URL sometimes returns a 429 (Too Many Requests) status,
                # which is perfect for demonstrating the circuit breaker
                response = requests.get("https://httpbin.org/status/200,429,500,503", timeout=5)
                response.raise_for_status()  # Raise an exception for 4xx/5xx status codes
                logger.info(f"HTTP request {i} succeeded: {response.status_code}")
        except CircuitBreakerOpen as e:
            logger.warning(f"HTTP request {i} blocked: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request {i} failed: {e}")
        
        # Add a small delay between requests
        time.sleep(1)


async def main():
    """
    Run all examples.
    """
    # Run the examples
    example_context_manager()
    example_decorator()
    await example_async_decorator()
    example_registry()
    
    # Only run the real HTTP request example if requests is installed
    try:
        import requests
        example_real_http_request()
    except ImportError:
        logger.warning("Skipping real HTTP request example: requests package not installed")


if __name__ == "__main__":
    asyncio.run(main())