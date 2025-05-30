# Governor Events Documentation

## Overview

The Governor Events module defines a set of events that are specific to the AlignmentGovernor component in the Eternia system. These events are published by the governor and can be subscribed to by other components, allowing for loose coupling between the governor and components that need to react to governor actions.

The events in this module extend the base `Event` class from the event bus system and provide specific information about governor actions such as pausing, resuming, shutting down, and rolling back the simulation.

## Event Types

### GovernorEvent

The `GovernorEvent` class is the base class for all governor-specific events. It includes a timestamp indicating when the event occurred.

```python
from modules.governor_events import GovernorEvent

class MyCustomGovernorEvent(GovernorEvent):
    def __init__(self, timestamp: float, custom_data: str):
        super().__init__(timestamp)
        self.custom_data = custom_data
```

### PauseEvent

The `PauseEvent` is fired when the simulation is paused by the governor. It contains only the timestamp of when the pause occurred.

```python
from modules.governor_events import PauseEvent

# Create a pause event
event = PauseEvent(timestamp=time.time())
```

### ResumeEvent

The `ResumeEvent` is fired when the simulation is resumed after being paused. It contains only the timestamp of when the resume occurred.

```python
from modules.governor_events import ResumeEvent

# Create a resume event
event = ResumeEvent(timestamp=time.time())
```

### ShutdownEvent

The `ShutdownEvent` is fired when the simulation is shut down. It includes the timestamp and a reason for the shutdown.

```python
from modules.governor_events import ShutdownEvent

# Create a shutdown event
event = ShutdownEvent(timestamp=time.time(), reason="User requested shutdown")
```

### RollbackEvent

The `RollbackEvent` is fired when the simulation is rolled back to a previous checkpoint. It includes the timestamp and the path to the checkpoint that was rolled back to.

```python
from modules.governor_events import RollbackEvent
from pathlib import Path

# Create a rollback event
event = RollbackEvent(timestamp=time.time(), checkpoint=Path("artifacts/checkpoints/ckpt_123456789.bin"))
```

### ContinuityBreachEvent

The `ContinuityBreachEvent` is fired when the identity continuity score falls below the threshold set in the governor. It includes the timestamp and the metrics that triggered the breach.

```python
from modules.governor_events import ContinuityBreachEvent

# Create a continuity breach event
metrics = {"identity_continuity": 0.85, "other_metric": 42}
event = ContinuityBreachEvent(timestamp=time.time(), metrics=metrics)
```

### CheckpointScheduledEvent

The `CheckpointScheduledEvent` is fired when a checkpoint is scheduled to be created. It contains only the timestamp.

```python
from modules.governor_events import CheckpointScheduledEvent

# Create a checkpoint scheduled event
event = CheckpointScheduledEvent(timestamp=time.time())
```

### CheckpointSavedEvent

The `CheckpointSavedEvent` is fired when a checkpoint has been saved. It includes the timestamp and the path where the checkpoint was saved.

```python
from modules.governor_events import CheckpointSavedEvent
from pathlib import Path

# Create a checkpoint saved event
event = CheckpointSavedEvent(timestamp=time.time(), path=Path("artifacts/checkpoints/ckpt_123456789.bin"))
```

### PolicyViolationEvent

The `PolicyViolationEvent` is fired when a policy registered with the governor returns `False`, indicating a violation. It includes the timestamp, the name of the policy that was violated, and the metrics that triggered the violation.

```python
from modules.governor_events import PolicyViolationEvent

# Create a policy violation event
metrics = {"some_metric": 100, "other_metric": 42}
event = PolicyViolationEvent(timestamp=time.time(), policy_name="resource_limit_policy", metrics=metrics)
```

### LawEnforcedEvent

The `LawEnforcedEvent` is fired when a law is enforced by the governor. It includes the timestamp, the name of the law that was enforced, the name of the event that triggered the law, and the payload of that event.

```python
from modules.governor_events import LawEnforcedEvent

# Create a law enforced event
payload = {"zone": "restricted_area", "agent": "explorer_1"}
event = LawEnforcedEvent(timestamp=time.time(), law_name="no_entry_law", event_name="zone_entered", payload=payload)
```

## Usage with Event Bus

Governor events are typically published by the AlignmentGovernor class and can be subscribed to by other components using the event bus.

### Publishing Events

The governor automatically publishes these events when the corresponding actions occur. However, if you need to manually publish an event:

```python
from modules.utilities.event_bus import event_bus
from modules.governor_events import PauseEvent
import time

# Create and publish an event
event = PauseEvent(timestamp=time.time())
event_bus.publish(event)
```

### Subscribing to Events

Components can subscribe to governor events to react to governor actions:

```python
from modules.utilities.event_bus import EventListener, event_handler
from modules.governor_events import PauseEvent, ResumeEvent, ShutdownEvent

class MyComponent(EventListener):
    def __init__(self):
        super().__init__()  # Register event handlers
    
    @event_handler(PauseEvent)
    def handle_pause(self, event: PauseEvent):
        print(f"Simulation paused at {event.timestamp}")
        # Pause component activities
    
    @event_handler(ResumeEvent)
    def handle_resume(self, event: ResumeEvent):
        print(f"Simulation resumed at {event.timestamp}")
        # Resume component activities
    
    @event_handler(ShutdownEvent)
    def handle_shutdown(self, event: ShutdownEvent):
        print(f"Simulation shut down at {event.timestamp} due to: {event.reason}")
        # Clean up resources
```

## Best Practices

1. **Use the appropriate event type**: Choose the most specific event type for your needs to ensure that subscribers receive the right information.

2. **Include relevant data**: When creating custom governor events, include all relevant data that subscribers might need to respond appropriately.

3. **Handle events appropriately**: Components that subscribe to governor events should handle them in a way that maintains the integrity of the simulation.

4. **Consider event priorities**: When subscribing to events, consider using event priorities to ensure that critical handlers are called before less important ones.

5. **Log event handling**: Log when events are received and how they are handled to aid in debugging and monitoring.

6. **Clean up subscriptions**: Ensure that components unsubscribe from events when they are no longer needed to prevent memory leaks.