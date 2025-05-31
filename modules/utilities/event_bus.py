"""
Event bus for communication between components.

This module provides a central event bus that components can use to publish and subscribe to events.
It implements the publisher-subscriber pattern, allowing for loose coupling between components.
"""

import asyncio
import inspect
import logging
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable, Dict, List, TypeVar, Union, Coroutine

# Configure logging
logger = logging.getLogger("eternia.event_bus")

# Type for event handlers
T = TypeVar("T")
EventHandler = Callable[[T], None]
AsyncEventHandler = Callable[[T], Coroutine[Any, Any, None]]


class EventPriority(Enum):
    """Priority levels for event handlers."""

    LOW = auto()
    NORMAL = auto()
    HIGH = auto()
    MONITOR = auto()  # Monitors are called last and shouldn't modify the event


@dataclass
class HandlerRegistration:
    """Registration information for an event handler."""

    handler: Union[EventHandler, AsyncEventHandler]
    priority: EventPriority
    is_async: bool


class EventBus:
    """
    Central event bus for the application.

    The EventBus allows components to publish events and subscribe to events
    without having direct dependencies on each other.
    """

    _instance = None

    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the event bus if not already initialized."""
        if self._initialized:
            return

        # Dictionary mapping event types to sets of handlers
        self._handlers: Dict[type, List[HandlerRegistration]] = {}

        # Event loop for async event handling
        self._loop = asyncio.get_event_loop()

        self._initialized = True

    def subscribe(
        self,
        event_type: type,
        handler: Union[EventHandler, AsyncEventHandler],
        priority: EventPriority = EventPriority.NORMAL,
    ) -> None:
        """
        Subscribe to events of a specific type.

        Args:
            event_type: The type of event to subscribe to.
            handler: The function to call when an event of this type is published.
            priority: The priority of the handler. Higher priority handlers are called first.
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []

        # Check if handler is async
        is_async = asyncio.iscoroutinefunction(handler) or (
            inspect.ismethod(handler) and asyncio.iscoroutinefunction(handler.__func__)
        )

        # Add handler to the list
        self._handlers[event_type].append(
            HandlerRegistration(handler=handler, priority=priority, is_async=is_async)
        )

        # Sort handlers by priority (higher priority first)
        self._handlers[event_type].sort(
            key=lambda reg: reg.priority.value, reverse=True
        )

        # Get handler name safely, as it might be a mock in tests
        handler_name = getattr(handler, "__name__", str(handler))
        logger.debug(
            f"Subscribed {handler_name} to {event_type.__name__} events with {priority.name} priority"
        )

    def unsubscribe(
        self, event_type: type, handler: Union[EventHandler, AsyncEventHandler]
    ) -> bool:
        """
        Unsubscribe from events of a specific type.

        Args:
            event_type: The type of event to unsubscribe from.
            handler: The handler to remove.

        Returns:
            bool: True if the handler was removed, False if it wasn't found.
        """
        if event_type not in self._handlers:
            return False

        for i, reg in enumerate(self._handlers[event_type]):
            if reg.handler == handler:
                self._handlers[event_type].pop(i)
                # Get handler name safely, as it might be a mock in tests
                handler_name = getattr(handler, "__name__", str(handler))
                logger.debug(
                    f"Unsubscribed {handler_name} from {event_type.__name__} events"
                )
                return True

        return False

    def publish(self, event: Any) -> None:
        """
        Publish an event to all subscribers.

        Args:
            event: The event to publish. The type of this object determines
                  which subscribers receive the event.
        """
        event_type = type(event)

        if event_type not in self._handlers:
            logger.debug(f"No handlers registered for {event_type.__name__}")
            return

        logger.debug(f"Publishing {event_type.__name__} event")

        for reg in self._handlers[event_type]:
            try:
                if reg.is_async:
                    # Schedule async handler to run in the event loop
                    asyncio.create_task(reg.handler(event))
                else:
                    # Call sync handler directly
                    reg.handler(event)
            except Exception as e:
                # Get handler name safely, as it might be a mock in tests
                handler_name = getattr(reg.handler, "__name__", str(reg.handler))
                logger.error(f"Error in event handler {handler_name}: {str(e)}")

    async def publish_async(self, event: Any) -> None:
        """
        Publish an event to all subscribers, awaiting async handlers.

        This method awaits all async handlers before returning, unlike publish()
        which schedules them to run but doesn't wait.

        Args:
            event: The event to publish.
        """
        event_type = type(event)

        if event_type not in self._handlers:
            logger.debug(f"No handlers registered for {event_type.__name__}")
            return

        logger.debug(f"Publishing {event_type.__name__} event (async)")

        # Collect tasks for async handlers
        tasks = []

        for reg in self._handlers[event_type]:
            try:
                if reg.is_async:
                    # Create task for async handler
                    task = asyncio.create_task(reg.handler(event))
                    tasks.append(task)
                else:
                    # Call sync handler directly
                    reg.handler(event)
            except Exception as e:
                # Get handler name safely, as it might be a mock in tests
                handler_name = getattr(reg.handler, "__name__", str(reg.handler))
                logger.error(f"Error in event handler {handler_name}: {str(e)}")

        # Wait for all async handlers to complete
        if tasks:
            await asyncio.gather(*tasks)


# Singleton instance
event_bus = EventBus()


# Base class for all events
class Event:
    """Base class for all events in the system."""

    pass


# Standard system events
class SystemEvent(Event):
    """Base class for system events."""

    pass


class StartupEvent(SystemEvent):
    """Event fired when the system starts up."""

    pass


class ShutdownEvent(SystemEvent):
    """Event fired when the system is shutting down."""

    pass


class ComponentInitializedEvent(SystemEvent):
    """Event fired when a component is initialized."""

    def __init__(self, component_name: str):
        self.component_name = component_name


# Decorator for event handlers
def event_handler(event_type: type, priority: EventPriority = EventPriority.NORMAL):
    """
    Decorator for event handler methods.

    Example:
        @event_handler(MyEvent)
        def handle_my_event(self, event: MyEvent):
            # Handle the event

    Args:
        event_type: The type of event to handle.
        priority: The priority of the handler.
    """

    def decorator(func):
        func._event_type = event_type
        func._event_priority = priority
        return func

    return decorator


class EventListener:
    """
    Base class for components that listen to events.

    This class automatically registers all methods decorated with @event_handler
    when the component is initialized.
    """

    def __init__(self):
        """Initialize the event listener and register handlers."""
        self._register_handlers()

    def _register_handlers(self):
        """Register all methods decorated with @event_handler."""
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if hasattr(attr, "_event_type") and hasattr(attr, "_event_priority"):
                event_bus.subscribe(attr._event_type, attr, attr._event_priority)

    def __del__(self):
        """Unregister all handlers when the component is destroyed."""
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if hasattr(attr, "_event_type"):
                event_bus.unsubscribe(attr._event_type, attr)
