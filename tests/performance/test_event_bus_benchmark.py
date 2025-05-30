"""
Performance benchmarks for the Event Bus.

This module contains benchmark tests for the Event Bus component, measuring
the performance of subscribing, publishing, and unsubscribing operations.
"""

import asyncio
from typing import List

import pytest
from modules.utilities.event_bus import EventBus, EventPriority, Event


class TestEvent(Event):
    """Test event for benchmarking."""
    
    def __init__(self, value: int):
        self.value = value


def test_subscribe_performance(benchmark):
    """Benchmark the performance of subscribing to events."""
    event_bus = EventBus()
    
    def handler(event: TestEvent):
        pass
    
    # Measure the performance of subscribing to events
    benchmark(event_bus.subscribe, TestEvent, handler)


def test_publish_performance(benchmark):
    """Benchmark the performance of publishing events."""
    event_bus = EventBus()
    received_events = []
    
    def handler(event: TestEvent):
        received_events.append(event)
    
    # Subscribe to the event
    event_bus.subscribe(TestEvent, handler)
    
    # Create an event to publish
    event = TestEvent(42)
    
    # Measure the performance of publishing events
    benchmark(event_bus.publish, event)
    
    # Verify that the event was received
    assert len(received_events) == 1
    assert received_events[0].value == 42


def test_unsubscribe_performance(benchmark):
    """Benchmark the performance of unsubscribing from events."""
    event_bus = EventBus()
    
    def handler(event: TestEvent):
        pass
    
    # Subscribe to the event
    event_bus.subscribe(TestEvent, handler)
    
    # Measure the performance of unsubscribing from events
    benchmark(event_bus.unsubscribe, TestEvent, handler)


def test_publish_many_subscribers_performance(benchmark):
    """Benchmark the performance of publishing events with many subscribers."""
    event_bus = EventBus()
    num_subscribers = 100
    received_counts = [0] * num_subscribers
    
    # Create and subscribe multiple handlers
    handlers = []
    for i in range(num_subscribers):
        def make_handler(index):
            def handler(event: TestEvent):
                received_counts[index] += 1
            return handler
        
        handler = make_handler(i)
        handlers.append(handler)
        event_bus.subscribe(TestEvent, handler)
    
    # Create an event to publish
    event = TestEvent(42)
    
    # Measure the performance of publishing events with many subscribers
    benchmark(event_bus.publish, event)
    
    # Verify that all subscribers received the event
    assert all(count == 1 for count in received_counts)


def test_publish_with_priorities_performance(benchmark):
    """Benchmark the performance of publishing events with different priorities."""
    event_bus = EventBus()
    execution_order = []
    
    # Create and subscribe handlers with different priorities
    def high_priority_handler(event: TestEvent):
        execution_order.append("HIGH")
    
    def normal_priority_handler(event: TestEvent):
        execution_order.append("NORMAL")
    
    def low_priority_handler(event: TestEvent):
        execution_order.append("LOW")
    
    def monitor_handler(event: TestEvent):
        execution_order.append("MONITOR")
    
    event_bus.subscribe(TestEvent, high_priority_handler, EventPriority.HIGH)
    event_bus.subscribe(TestEvent, normal_priority_handler, EventPriority.NORMAL)
    event_bus.subscribe(TestEvent, low_priority_handler, EventPriority.LOW)
    event_bus.subscribe(TestEvent, monitor_handler, EventPriority.MONITOR)
    
    # Create an event to publish
    event = TestEvent(42)
    
    # Clear the execution order before benchmarking
    execution_order.clear()
    
    # Measure the performance of publishing events with different priorities
    benchmark(event_bus.publish, event)
    
    # Verify the execution order (higher priority first)
    expected_order = []
    for priority in sorted([EventPriority.HIGH, EventPriority.NORMAL, EventPriority.LOW, EventPriority.MONITOR], 
                          key=lambda p: p.value, reverse=True):
        expected_order.append(priority.name)
    assert execution_order == expected_order


@pytest.mark.asyncio
async def test_publish_async_performance(benchmark):
    """Benchmark the performance of publishing events asynchronously."""
    event_bus = EventBus()
    received_events = []
    
    async def async_handler(event: TestEvent):
        await asyncio.sleep(0.001)  # Simulate some async work
        received_events.append(event)
    
    # Subscribe to the event
    event_bus.subscribe(TestEvent, async_handler)
    
    # Create an event to publish
    event = TestEvent(42)
    
    # Measure the performance of publishing events asynchronously
    async def publish_async():
        await event_bus.publish_async(event)
    
    benchmark(asyncio.run, publish_async())
    
    # Verify that the event was received
    assert len(received_events) == 1
    assert received_events[0].value == 42