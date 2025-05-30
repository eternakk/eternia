# Governor Documentation

## Overview

The Alignment Governor is a hard-safety layer that monitors the Eternia simulation for safety violations and alignment issues. It can pause the simulation, roll back to a previous checkpoint, or shut down the simulation entirely if necessary. It also manages checkpoints and enforces laws within the simulation.

The governor acts as a safeguard to ensure that the simulation maintains certain properties, such as identity continuity, and follows established policies and laws. It provides a centralized control mechanism for the simulation and integrates with the event system to communicate state changes to other components.

## Key Components

### AlignmentGovernor

The `AlignmentGovernor` class is the main component of the governor system. It monitors the simulation and takes action when necessary.

```python
from modules.governor import AlignmentGovernor
from world_builder import build_world
from modules.state_tracker import EternaStateTracker

# Create a world and state tracker
world = build_world()
state_tracker = EternaStateTracker(world)

# Create a governor
governor = AlignmentGovernor(world, state_tracker)
```

### Control Methods

The governor provides several methods for controlling the simulation:

- `pause()`: Pauses the simulation.
- `resume()`: Resumes the simulation after it has been paused.
- `shutdown(reason)`: Shuts down the simulation with a specified reason.
- `rollback(target=None)`: Rolls back the simulation to a previous checkpoint.

### Tick Method

The `tick(metrics)` method is called on each simulation step and determines if the world may continue. It checks for continuity breaches, policy violations, and manages checkpoint creation.

```python
# In the simulation loop
metrics = world.collect_metrics()
if governor.tick(metrics):
    world.step()
else:
    # Handle pause, shutdown, or rollback
    pass
```

### Policy Registration

The governor allows registering custom policy callbacks that can trigger rollbacks:

```python
def my_policy(metrics):
    # Return False to trigger a rollback
    if metrics.get("some_metric") > threshold:
        return False
    return True

governor.register_policy(my_policy)
```

### Law Enforcement

The governor enforces laws defined in the law registry. Laws are triggered by events and can apply effects when their conditions are met.

## Events

The governor publishes several events through the event bus:

- `PauseEvent`: Fired when the simulation is paused.
- `ResumeEvent`: Fired when the simulation is resumed.
- `ShutdownEvent`: Fired when the simulation is shut down.
- `RollbackEvent`: Fired when the simulation is rolled back.
- `ContinuityBreachEvent`: Fired when identity continuity is below threshold.
- `CheckpointScheduledEvent`: Fired when a checkpoint is scheduled.
- `CheckpointSavedEvent`: Fired when a checkpoint is saved.
- `PolicyViolationEvent`: Fired when a policy is violated.
- `LawEnforcedEvent`: Fired when a law is enforced.

## Checkpoints

The governor manages checkpoints of the simulation state:

- Checkpoints are automatically created at regular intervals (defined by `save_interval`).
- Checkpoints are stored in the `artifacts/checkpoints` directory.
- The governor keeps a limited number of checkpoints (defined by `MAX_CKPTS`).
- Checkpoints can be used for rollbacks when safety violations occur.

## Example Usage

### Creating a Governor

```python
from modules.governor import AlignmentGovernor
from world_builder import build_world

# Create a world
world = build_world()

# Create a governor
governor = AlignmentGovernor(world, world.state_tracker)
```

### Using the Governor in a Simulation Loop

```python
# Main simulation loop
while True:
    # Collect metrics from the world
    metrics = world.collect_metrics()
    
    # Check if the simulation should continue
    if governor.tick(metrics):
        # Step the world forward
        world.step()
    else:
        # The governor has paused, shut down, or rolled back the simulation
        if governor.is_shutdown():
            break
        # If paused, wait for resume command
```

### Registering a Custom Policy

```python
def identity_policy(metrics):
    """Ensure identity continuity stays above a dynamic threshold."""
    threshold = 0.85  # Could be dynamic based on other factors
    if metrics.get("identity_continuity", 1.0) < threshold:
        return False  # Trigger rollback
    return True

governor.register_policy(identity_policy)
```

## Best Practices

1. **Use the governor for safety-critical checks**: The governor should be used for checks that are essential for the safety and integrity of the simulation.

2. **Keep policy callbacks simple and focused**: Each policy callback should check a specific aspect of the simulation and return a clear boolean result.

3. **Handle governor events appropriately**: Components should subscribe to governor events and handle them appropriately, especially pause, resume, and shutdown events.

4. **Monitor checkpoint creation**: Ensure that checkpoints are being created regularly and that they are valid for rollbacks.

5. **Use rollbacks as a last resort**: Rollbacks should be used only when necessary, as they discard simulation progress.

6. **Log governor actions**: The governor logs its actions, but additional logging may be needed for specific use cases.

7. **Test governor behavior**: Test that the governor correctly handles continuity breaches, policy violations, and other safety issues.