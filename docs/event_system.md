# Event System Documentation

## Overview

The Eternia project now has a consistent event system for communication between components. This system implements the publisher-subscriber pattern, allowing for loose coupling between components. Components can publish events to the event bus, and other components can subscribe to these events without having direct dependencies on each other.

## Key Components

### Event Bus

The event bus is the central component of the event system. It manages event subscriptions and publications. The event bus is implemented as a singleton, so there is only one instance of it in the application.

```python
from modules.utilities.event_bus import event_bus

# Publish an event
event_bus.publish(MyEvent())

# Subscribe to an event
event_bus.subscribe(MyEvent, my_handler_function)
```

### Events

Events are objects that represent something that has happened in the system. All events should inherit from the `Event` base class.

```python
from modules.utilities.event_bus import Event

class MyEvent(Event):
    def __init__(self, data):
        self.data = data
```

### Event Handlers

Event handlers are functions or methods that are called when an event is published. They receive the event object as a parameter.

```python
def my_handler_function(event: MyEvent):
    print(f"Received event with data: {event.data}")
```

### Event Listeners

Event listeners are components that listen to events. The `EventListener` base class provides a convenient way to register event handlers using the `@event_handler` decorator.

```python
from modules.utilities.event_bus import EventListener, event_handler

class MyComponent(EventListener):
    def __init__(self):
        super().__init__()  # Register event handlers
    
    @event_handler(MyEvent)
    def handle_my_event(self, event: MyEvent):
        print(f"Received event with data: {event.data}")
```

## Governor Events

The governor component publishes several events that other components can subscribe to:

- `PauseEvent`: Fired when the simulation is paused.
- `ResumeEvent`: Fired when the simulation is resumed.
- `ShutdownEvent`: Fired when the simulation is shut down.
- `RollbackEvent`: Fired when the simulation is rolled back.
- `ContinuityBreachEvent`: Fired when identity continuity is below threshold.
- `CheckpointScheduledEvent`: Fired when a checkpoint is scheduled.
- `CheckpointSavedEvent`: Fired when a checkpoint is saved.
- `PolicyViolationEvent`: Fired when a policy is violated.
- `LawEnforcedEvent`: Fired when a law is enforced.

## Legacy Compatibility

The event system includes an adapter that bridges the legacy event queue mechanism with the new event bus. This allows components that are still using the legacy mechanism to receive events from the event bus.

## Example Usage

### Publishing Events

```python
from modules.utilities.event_bus import event_bus
from modules.governor_events import PauseEvent
import time

# Create and publish an event
event = PauseEvent(timestamp=time.time())
event_bus.publish(event)
```

### Subscribing to Events

```python
from modules.utilities.event_bus import event_bus, EventListener, event_handler
from modules.governor_events import PauseEvent

# Using the event_bus directly
def handle_pause(event: PauseEvent):
    print(f"Simulation paused at {event.timestamp}")

event_bus.subscribe(PauseEvent, handle_pause)

# Using the EventListener base class
class MyComponent(EventListener):
    def __init__(self):
        super().__init__()  # Register event handlers
    
    @event_handler(PauseEvent)
    def handle_pause(self, event: PauseEvent):
        print(f"Simulation paused at {event.timestamp}")
```

### Asynchronous Event Handling

The event system supports both synchronous and asynchronous event handlers. Asynchronous handlers are automatically detected and scheduled to run in the event loop.

```python
import asyncio
from modules.utilities.event_bus import event_bus, EventListener, event_handler
from modules.governor_events import PauseEvent

# Using the event_bus directly
async def handle_pause_async(event: PauseEvent):
    await asyncio.sleep(1)  # Simulate some async work
    print(f"Simulation paused at {event.timestamp}")

event_bus.subscribe(PauseEvent, handle_pause_async)

# Using the EventListener base class
class MyAsyncComponent(EventListener):
    def __init__(self):
        super().__init__()  # Register event handlers
    
    @event_handler(PauseEvent)
    async def handle_pause(self, event: PauseEvent):
        await asyncio.sleep(1)  # Simulate some async work
        print(f"Simulation paused at {event.timestamp}")
```

## Best Practices

1. **Define clear event interfaces**: Each event should have a clear purpose and a well-defined set of properties.
2. **Keep events immutable**: Once an event is created, it should not be modified. This prevents unexpected behavior when multiple handlers process the same event.
3. **Use event priorities wisely**: The event system supports different priority levels for event handlers. Use them to ensure that handlers are called in the appropriate order.
4. **Handle exceptions in event handlers**: Exceptions in event handlers are caught by the event bus, but it's still a good practice to handle exceptions in your handlers to prevent unexpected behavior.
5. **Use the EventListener base class**: The EventListener base class provides a convenient way to register event handlers and ensures that they are properly unregistered when the component is destroyed.