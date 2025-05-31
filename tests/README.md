# Eternia Project Tests

This directory contains tests for the Eternia project.

## Test Structure

- `tests/`: Contains unit tests for individual modules
- `tests/integration/`: Contains integration tests for system workflows
- `tests/alignment/`: Contains tests for alignment and safety criteria

## Running Tests

To run all tests:

```bash
pytest tests/
```

To run a specific test file:

```bash
pytest tests/test_file_utils.py
```

To run tests with verbose output:

```bash
pytest -v tests/
```

## Property-Based Testing

The Eternia project uses property-based testing for complex simulation logic. Property-based testing generates random inputs to test properties that should hold true for all valid inputs, rather than testing specific examples.

### Requirements

Property-based tests require the Hypothesis library:

```bash
pip install hypothesis
```

Or install all dependencies from requirements.txt:

```bash
pip install -r requirements.txt
```

### Running Property-Based Tests

To run property-based tests:

```bash
pytest tests/test_property_based.py tests/test_social_interaction_property.py
```

### Property-Based Test Files

- `tests/test_property_based.py`: Contains property-based tests for:
  - `EmotionalCircuitSystem.process_emotion`: Tests that the method correctly handles different types of emotions
  - `PhysicsZoneRegistry.assign_profile`: Tests that the method correctly handles safe and unsafe profiles
  - `TimeSynchronizer.adjust_time_flow`: Tests that the method correctly adjusts time flow based on sensory profile and cognitive load

- `tests/test_social_interaction_property.py`: Contains property-based tests for:
  - `SocialInteractionModule.invite_user`: Tests that the method correctly handles users based on their allowed status
  - `SocialInteractionModule.initiate_safe_interaction`: Tests that the method correctly handles interactions based on user existence and permissions
  - `SocialInteractionModule.assign_collaborative_challenge`: Tests that the method correctly handles challenge assignment based on user existence

### Writing Property-Based Tests

To write a property-based test, use the `@given` decorator from Hypothesis to specify the types of inputs to generate:

```python
from hypothesis import given, strategies as st

@given(
    name=st.text(min_size=1, max_size=20),
    intensity=st.integers(min_value=0, max_value=10),
    direction=st.sampled_from(["inward", "outward", "locked", "flowing"])
)
def test_process_emotion_does_not_raise_exception(self, name, intensity, direction):
    # Test code here
```

For more information on Hypothesis, see the [Hypothesis documentation](https://hypothesis.readthedocs.io/).