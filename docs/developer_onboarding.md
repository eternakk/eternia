# Developer Onboarding Guide

## Introduction

Welcome to the Eternia Project! This guide will help you get started with the project, understand its architecture, and learn how to contribute effectively.

Eternia is a simulation system that models a world with companions (agents), emotions, social interactions, and various other components. The system is designed to be safe, observable, and controllable through a governance layer.

## Project Structure

The Eternia project is organized into several key directories:

- `modules/`: Contains the core modules of the system
- `services/`: Contains services like the API
- `tests/`: Contains test files
- `ui/`: Contains the frontend code
- `docs/`: Contains documentation
- `artifacts/`: Contains checkpoints and other artifacts
- `logs/`: Contains log files
- `config/`: Contains configuration files
- `world_builder.py`: The main file for building the Eternia world

## Development Environment Setup

### Prerequisites

- Python 3.10 or higher
- Node.js and npm (for frontend development)

### Setting Up the Python Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/your-organization/eternia.git
   cd eternia
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install the dependencies:
   ```bash
   pip install pytest pytest-asyncio fastapi httpx pydantic sse-starlette
   ```

4. Set up the environment:
   ```bash
   mkdir -p logs artifacts
   touch logs/eterna_runtime.log
   ```

5. Add the project root to PYTHONPATH:
   ```bash
   export PYTHONPATH=$PYTHONPATH:$(pwd)  # On Windows: set PYTHONPATH=%PYTHONPATH%;%cd%
   ```

### Setting Up the Frontend Environment

1. Navigate to the UI directory:
   ```bash
   cd ui
   ```

2. Install the dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

## Architecture Overview

The Eternia project follows a layered architecture:

### Core Runtime

- **EternaWorld**: The main container for the simulation state, providing access to all subsystems.
- **Alignment-Governor**: Hard-safety layer that can pause, rollback, or shut down the simulation based on safety criteria.
- **Eval Harness**: Unit-tests that flag disallowed behaviors.
- **State-Tracker**: Tracks the state of the simulation, including checkpoints and rollbacks.

### Control/Observability Layer

- **FastAPI/gRPC Bridge**: REST & RPC endpoints for controlling and observing the simulation.
- **WebSocket Hub**: Push-only diff updates to clients.

### Dashboard

- React/Next.js application for monitoring and controlling the simulation.

### Immersive Components (Future)

- WebGL/WebGPU for 3D visualization
- WebXR/VR for immersive experiences
- Neural/BCI interfaces

## Key Components and Their Relationships

### Core Modules

- **World Builder**: Creates and initializes the Eternia world, setting up all components and their initial state.
- **EternaWorld**: The main container for the simulation state, providing access to all subsystems.
- **Runtime**: Manages the simulation cycle and time progression.

### Governance and Safety

- **AlignmentGovernor**: Monitors and controls the EternaWorld.
- **Governor Events**: Events published by the governor to communicate state changes.
- **Laws**: Defines laws that govern behavior within the simulation.
- **Law Parser**: Loads and parses laws from configuration files.

### State Management

- **State Tracker**: Tracks the state of the EternaWorld.

### Event System

- **Event Bus**: Provides communication between components.
- **Event Adapter**: Bridges the legacy event queue with the Event Bus.

### Companions and Agents

- **Companion Ecology**: Manages the companions (agents) in the simulation and their interactions.
- **Emotional Agent**: Base class for agents with emotional capabilities.
- **Emotions**: Defines emotional states and transitions for agents.
- **Social Interaction**: Manages interactions between agents.
- **Social Presence**: Defines how agents perceive and are perceived by others.

### World and Environment

- **Exploration**: Manages the exploration of zones and discovery of new areas.
- **Zone Modifiers**: Defines modifiers that affect zones and agents within them.
- **Physics**: Simulates physical interactions within the world.

### Memory and Cognition

- **Memory Integration**: Manages memories for agents.
- **Consciousness Replica**: Models the consciousness of agents.
- **Thought**: Models the thought processes of agents.

### API and Services

- **API Server**: Provides an interface to the EternaWorld.
- **API Dependencies**: Injects dependencies into the API Server.
- **API Schemas**: Defines the data structures for the API Server.

## Development Workflow

### Running the Simulation

1. Start the API server:
   ```bash
   python services/api/server.py
   ```

2. Start the frontend development server:
   ```bash
   cd ui
   npm run dev
   ```

3. Access the dashboard at http://localhost:5173

### Making Changes

1. Create a new branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes to the codebase.

3. Run the tests to ensure your changes don't break existing functionality:
   ```bash
   pytest tests/
   ```

4. Commit your changes:
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

5. Push your changes to the remote repository:
   ```bash
   git push origin feature/your-feature-name
   ```

6. Create a pull request on GitHub.

## Testing

The Eternia project uses pytest for testing. There are several types of tests:

- **Unit tests**: Test individual components in isolation.
- **Integration tests**: Test the interaction between components.
- **Alignment tests**: Test that the system behaves according to safety criteria.

To run the tests:

```bash
# Run all tests
pytest tests/

# Run integration tests only
pytest tests/integration/

# Run a specific test file
pytest tests/path/to/test_file.py
```

## Deployment

The Eternia project can be deployed in various environments:

### Local Development

Follow the setup instructions above to run the project locally.

### Continuous Integration

The project uses GitHub Actions for continuous integration. The workflow is defined in `.github/workflows/python-tests.yml`. It runs the tests on every push to the main branch and on pull requests.

### Production Deployment

For production deployment, the project should be containerized using Docker and deployed to a suitable environment. This is a future task that has not yet been implemented.

## Additional Resources

- [Module Map](module_map.md): A comprehensive map of all modules and their relationships.
- [Architecture Documentation](architecture_v2.md): Detailed architecture documentation with diagrams.
- [Event System Documentation](event_system.md): Documentation for the event system.
- [Governor Documentation](governor.md): Documentation for the AlignmentGovernor component.
- [Governor Events Documentation](governor_events.md): Documentation for the governor events system.

## Getting Help

If you have any questions or need help, please reach out to the team through the appropriate channels.

## Contributing

We welcome contributions to the Eternia project! Please follow the development workflow described above and ensure that your changes adhere to the project's coding standards.
