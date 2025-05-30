"""
Integration tests for the event system.

These tests verify that different components can communicate correctly through the event bus.
"""

import asyncio
import unittest
from unittest.mock import MagicMock

from modules.utilities.event_bus import (
    Event, EventBus, EventListener, EventPriority, event_handler
)
from modules.governor_events import (
    GovernorEvent, PauseEvent, ResumeEvent, ShutdownEvent
)


class TestEventComponent(EventListener):
    """A test component that listens for events."""

    def __init__(self):
        self.pause_event_received = False
        self.resume_event_received = False
        self.shutdown_event_received = False
        self.shutdown_reason = None
        super().__init__()

    @event_handler(PauseEvent)
    def handle_pause(self, event: PauseEvent):
        """Handle pause events."""
        self.pause_event_received = True

    @event_handler(ResumeEvent)
    def handle_resume(self, event: ResumeEvent):
        """Handle resume events."""
        self.resume_event_received = True

    @event_handler(ShutdownEvent)
    def handle_shutdown(self, event: ShutdownEvent):
        """Handle shutdown events."""
        self.shutdown_event_received = True
        self.shutdown_reason = event.reason


class TestAsyncEventComponent(EventListener):
    """A test component that listens for events with async handlers."""

    def __init__(self):
        self.pause_event_received = False
        self.resume_event_received = False
        super().__init__()

    @event_handler(PauseEvent)
    async def handle_pause(self, event: PauseEvent):
        """Handle pause events asynchronously."""
        # Simulate some async processing
        await asyncio.sleep(0.1)
        self.pause_event_received = True

    @event_handler(ResumeEvent)
    async def handle_resume(self, event: ResumeEvent):
        """Handle resume events asynchronously."""
        # Simulate some async processing
        await asyncio.sleep(0.1)
        self.resume_event_received = True


class TestPriorityEventComponent(EventListener):
    """A test component that tests event handler priorities."""

    def __init__(self):
        self.execution_order = []
        super().__init__()

    @event_handler(PauseEvent, priority=EventPriority.LOW)
    def handle_pause_low(self, event: PauseEvent):
        """Low priority handler."""
        self.execution_order.append("LOW")

    @event_handler(PauseEvent, priority=EventPriority.NORMAL)
    def handle_pause_normal(self, event: PauseEvent):
        """Normal priority handler."""
        self.execution_order.append("NORMAL")

    @event_handler(PauseEvent, priority=EventPriority.HIGH)
    def handle_pause_high(self, event: PauseEvent):
        """High priority handler."""
        self.execution_order.append("HIGH")

    @event_handler(PauseEvent, priority=EventPriority.MONITOR)
    def handle_pause_monitor(self, event: PauseEvent):
        """Monitor priority handler."""
        self.execution_order.append("MONITOR")


class EventSystemIntegrationTest(unittest.TestCase):
    """Integration tests for the event system."""

    def test_event_publishing_and_handling(self):
        """Test that events are correctly published and handled."""
        # Create a test component
        component = TestEventComponent()

        # Create and publish events
        event_bus = EventBus()
        event_bus.publish(PauseEvent(timestamp=1.0))
        event_bus.publish(ResumeEvent(timestamp=2.0))
        event_bus.publish(ShutdownEvent(timestamp=3.0, reason="Test shutdown"))

        # Verify that the component received the events
        self.assertTrue(component.pause_event_received)
        self.assertTrue(component.resume_event_received)
        self.assertTrue(component.shutdown_event_received)
        self.assertEqual(component.shutdown_reason, "Test shutdown")

    async def async_test_async_event_handling(self):
        """Test async event handlers."""
        # Create a test component
        component = TestAsyncEventComponent()

        # Create and publish events asynchronously
        event_bus = EventBus()
        await event_bus.publish_async(PauseEvent(timestamp=1.0))
        await event_bus.publish_async(ResumeEvent(timestamp=2.0))

        # Verify that the component received the events
        self.assertTrue(component.pause_event_received)
        self.assertTrue(component.resume_event_received)

    def test_async_event_handling(self):
        """Run the async test using an event loop."""
        asyncio.run(self.async_test_async_event_handling())

    def test_event_handler_priority(self):
        """Test that event handlers are executed in priority order."""
        # Create a test component
        component = TestPriorityEventComponent()

        # Create and publish an event
        event_bus = EventBus()
        event_bus.publish(PauseEvent(timestamp=1.0))

        # Verify the execution order (higher priority first)
        expected_order = ["HIGH", "NORMAL", "LOW", "MONITOR"]
        self.assertEqual(component.execution_order, expected_order)

    def test_event_unsubscription(self):
        """Test that event handlers can be unsubscribed."""
        # Create a mock handler
        mock_handler = MagicMock()

        # Subscribe to an event
        event_bus = EventBus()
        event_bus.subscribe(PauseEvent, mock_handler)

        # Publish an event and verify the handler was called
        event_bus.publish(PauseEvent(timestamp=1.0))
        mock_handler.assert_called_once()

        # Reset the mock and unsubscribe
        mock_handler.reset_mock()
        event_bus.unsubscribe(PauseEvent, mock_handler)

        # Publish again and verify the handler was not called
        event_bus.publish(PauseEvent(timestamp=1.0))
        mock_handler.assert_not_called()


if __name__ == "__main__":
    unittest.main()