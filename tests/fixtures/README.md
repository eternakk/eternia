# Test Fixtures for Eternia Project

This directory contains fixtures for testing the Eternia project. Fixtures are defined in the `conftest.py` files in the `tests` directory and its subdirectories.

## Common Fixtures

These fixtures are defined in `tests/conftest.py` and are available to all tests.

### Event System Fixtures

- `event_bus`: Returns a fresh EventBus instance.
- `pause_event`: Returns a PauseEvent instance.
- `resume_event`: Returns a ResumeEvent instance.
- `shutdown_event`: Returns a ShutdownEvent instance with reason "Test shutdown".

### Emotional System Fixtures

- `emotional_state`: Returns an EmotionalState instance. Parameters can be customized using indirect parametrization.
- `emotional_circuit_system`: Returns an EmotionalCircuitSystem instance with a mocked Eterna interface.

### Physics Fixtures

- `physics_profile`: Returns a PhysicsProfile instance. Parameters can be customized using indirect parametrization.
- `physics_zone_registry`: Returns a PhysicsZoneRegistry instance.

### Time Fixtures

- `time_synchronizer`: Returns a TimeSynchronizer instance with a mocked Eterna interface.
- `sensory_profile`: Returns a mocked sensory profile. Parameters can be customized using indirect parametrization.

### Social Interaction Fixtures

- `social_interaction_module`: Returns a SocialInteractionModule instance with mocked IMS and CCS.
- `user`: Returns a mocked User instance. Parameters can be customized using indirect parametrization.

### World Fixtures

- `mock_world`: Returns a mocked world instance with pre-configured companions and zones.
- `mock_governor`: Returns a mocked governor instance.

## Integration Test Fixtures

These fixtures are defined in `tests/integration/conftest.py` and are available to integration tests.

### API Testing Fixtures

- `client`: Returns a TestClient instance for the FastAPI app.
- `auth_headers`: Returns authentication headers for API requests.
- `patched_governor`: Returns a context manager that patches the governor in the API server.
- `patched_world`: Returns a context manager that patches the world in the API server.
- `patched_save_shutdown_state`: Returns a context manager that patches the save_shutdown_state function.
- `patched_event_queue`: Returns a context manager that patches the event_queue.
- `patched_asyncio_create_task`: Returns a context manager that patches asyncio.create_task.

## Usage Examples

### Basic Usage

```python
def test_event_publishing(event_bus, pause_event):
    # Use the fixtures directly
    event_bus.publish(pause_event)
    # ...
```

### Parametrized Usage

```python
@pytest.mark.parametrize("emotional_state", [
    {"name": "joy", "intensity": 8, "direction": "outward"},
    {"name": "grief", "intensity": 5, "direction": "inward"},
], indirect=True)
def test_process_emotion(emotional_circuit_system, emotional_state):
    # Use the parametrized fixture
    emotional_circuit_system.process_emotion(emotional_state)
    # ...
```

### API Testing

```python
def test_get_state(client):
    # Use the client fixture to make a request
    response = client.get("/state")
    assert response.status_code == 200
    # ...
```

### Patched Dependencies

```python
def test_command_pause(client, auth_headers, patched_governor):
    # Use the patched_governor fixture to mock the governor
    response = client.post("/command/pause", headers=auth_headers)
    assert response.status_code == 200
    patched_governor.pause.assert_called_once()
    # ...
```