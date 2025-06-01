# Module Map

This document provides an overview of the structure and dependencies between modules in the Eternia Project.

## Interfaces

### Module Interfaces
**File**: `modules/interfaces.py`
**Description**: Defines standardized interfaces for major system components to improve modularity and maintainability.
**Key Interfaces**:
- **ModuleInterface**: Base interface for all modules
- **EvolutionInterface**: Interface for evolution-related functionality
- **ConsciousnessInterface**: Interface for consciousness-related functionality
- **AwarenessInterface**: Interface for awareness-related functionality
- **SocialInterface**: Interface for social interaction functionality
- **EmotionalInterface**: Interface for emotional functionality
- **MemoryInterface**: Interface for memory-related functionality
- **ExplorationInterface**: Interface for exploration functionality
- **RuntimeInterface**: Interface for runtime functionality
- **StateTrackerInterface**: Interface for state tracking functionality

## Core Modules

### World Builder
**File**: `world_builder.py`
**Description**: Creates and initializes the Eternia world, setting up all components and their initial state.
**Dependencies**: Most other modules, as it instantiates and connects them.

### EternaWorld
**File**: `modules/eterna_world.py`
**Description**: The main container for the simulation state, providing access to all subsystems.
**Dependencies**: All subsystems (companions, exploration, rituals, etc.)

### Runtime
**File**: `modules/runtime.py`
**Description**: Manages the simulation cycle and time progression. Implements **RuntimeInterface**.
**Dependencies**: EternaWorld

## Governance and Safety

### AlignmentGovernor
**File**: `modules/governor.py`
**Description**: Hard-safety layer that can pause, rollback, or shut down the simulation based on safety criteria.
**Dependencies**: EternaWorld, StateTracker, EventBus

### Governor Events
**File**: `modules/governor_events.py`
**Description**: Events published by the governor to communicate state changes.
**Dependencies**: EventBus

### Laws
**File**: `modules/laws.py`
**Description**: Defines laws that govern behavior within the simulation.
**Dependencies**: LawParser

### Law Parser
**File**: `modules/law_parser.py`
**Description**: Parses law definitions from configuration files.
**Dependencies**: None

## State Management

### State Tracker
**File**: `modules/state_tracker.py`
**Description**: Tracks the state of the simulation, including checkpoints and rollbacks. Implements **StateTrackerInterface**.
**Dependencies**: EternaWorld

## Event System

### Event Bus
**File**: `modules/utilities/event_bus.py`
**Description**: Central event bus for communication between components using the publisher-subscriber pattern.
**Dependencies**: None

### Event Adapter
**File**: `modules/utilities/event_adapter.py`
**Description**: Bridges the legacy event queue mechanism with the new event bus.
**Dependencies**: EventBus

## Companions and Agents

### Companion Ecology
**File**: `modules/companion_ecology.py`
**Description**: Manages the companions (agents) in the simulation and their interactions.
**Dependencies**: Emotions, SocialInteraction

### Emotional Agent
**File**: `modules/emotional_agent.py`
**Description**: Base class for agents with emotional capabilities. Implements **EmotionalInterface**.
**Dependencies**: Emotions

### Emotions
**File**: `modules/emotions.py`
**Description**: Defines emotional states and transitions for agents.
**Dependencies**: EmotionDataLoader

### Emotion Data Loader
**File**: `modules/emotion_data_loader.py`
**Description**: Loads emotion data from configuration files.
**Dependencies**: None

### Social Interaction
**File**: `modules/social_interaction.py`
**Description**: Manages interactions between agents. Implements **SocialInterface**.
**Dependencies**: SocialPresence

### Social Presence
**File**: `modules/social_presence.py`
**Description**: Defines how agents perceive and are perceived by others.
**Dependencies**: None

## World and Environment

### Exploration
**File**: `modules/exploration.py`
**Description**: Manages the exploration of zones and discovery of new areas. Implements **ExplorationInterface**.
**Dependencies**: ZoneModifiers

### Zone Modifiers
**File**: `modules/zone_modifiers.py`
**Description**: Defines modifiers that affect zones and agents within them.
**Dependencies**: None

### Physics
**File**: `modules/physics.py`
**Description**: Simulates physical interactions within the world.
**Dependencies**: None

## Memory and Cognition

### Memory Integration
**File**: `modules/memory_integration.py`
**Description**: Manages the integration of memories for agents. Implements **MemoryInterface**.
**Dependencies**: None

### Consciousness Replica
**File**: `modules/consciousness_replica.py`
**Description**: Models the consciousness of agents. Implements **ConsciousnessInterface**.
**Dependencies**: Thought

### Thought
**File**: `modules/thought.py`
**Description**: Models the thought processes of agents.
**Dependencies**: None

## Rituals and Culture

### Rituals
**File**: `modules/rituals.py`
**Description**: Defines rituals that agents can perform.
**Dependencies**: None

### Resonance Engine
**File**: `modules/resonance_engine.py`
**Description**: Manages resonance between agents and the environment.
**Dependencies**: None

## Evolution and Adaptation

### Evolution
**File**: `modules/evolution.py`
**Description**: Manages the evolution of agents and the environment over time. Implements **EvolutionInterface**.
**Dependencies**: None

### Time Dilation
**File**: `modules/time_dilation.py`
**Description**: Manages the perception and flow of time within the simulation.
**Dependencies**: None

## Utilities

### Logging Config
**File**: `modules/logging_config.py`
**Description**: Configures logging for the application.
**Dependencies**: None

### Validation
**File**: `modules/validation.py`
**Description**: Provides validation utilities for input data.
**Dependencies**: None

### String Utilities
**File**: `modules/utilities/string_utils.py`
**Description**: Utilities for string manipulation.
**Dependencies**: None

### Logging Utilities
**File**: `modules/utilities/logging_utils.py`
**Description**: Additional utilities for logging.
**Dependencies**: None

### File Utilities
**File**: `modules/utilities/file_utils.py`
**Description**: Utilities for file operations.
**Dependencies**: None

## API and Services

### API Server
**File**: `services/api/server.py`
**Description**: FastAPI server that provides an API for interacting with the simulation.
**Dependencies**: EternaWorld, AlignmentGovernor, EventBus

### API Dependencies
**File**: `services/api/deps.py`
**Description**: Dependency injection for the API server.
**Dependencies**: EternaWorld, AlignmentGovernor

### API Schemas
**File**: `services/api/schemas.py`
**Description**: Pydantic schemas for API requests and responses.
**Dependencies**: None

## Module Relationships

### Core Relationships
- **World Builder** creates and initializes the **EternaWorld**
- **EternaWorld** contains and provides access to all subsystems
- **Runtime** manages the simulation cycle for the **EternaWorld**

### Governance Relationships
- **AlignmentGovernor** monitors and controls the **EternaWorld**
- **AlignmentGovernor** publishes **Governor Events** to communicate state changes
- **AlignmentGovernor** enforces **Laws** within the simulation
- **Law Parser** loads and parses **Laws** from configuration files

### State Management Relationships
- **State Tracker** tracks the state of the **EternaWorld**
- **AlignmentGovernor** uses the **State Tracker** to manage checkpoints and rollbacks

### Event System Relationships
- **Event Bus** provides communication between components
- **Event Adapter** bridges the legacy event queue with the **Event Bus**
- **Governor Events** are published to the **Event Bus**

### Agent Relationships
- **Companion Ecology** manages **Emotional Agent** instances
- **Emotional Agent** uses **Emotions** to model emotional states
- **Social Interaction** manages interactions between **Emotional Agent** instances
- **Social Presence** defines how **Emotional Agent** instances perceive each other

### World Relationships
- **Exploration** manages the discovery of zones
- **Zone Modifiers** affect zones and agents within them
- **Physics** simulates physical interactions within the world

### Memory and Cognition Relationships
- **Memory Integration** manages memories for **Emotional Agent** instances
- **Consciousness Replica** models the consciousness of **Emotional Agent** instances
- **Thought** models the thought processes of **Emotional Agent** instances

### API Relationships
- **API Server** provides an interface to the **EternaWorld**
- **API Dependencies** injects dependencies into the **API Server**
- **API Schemas** defines the data structures for the **API Server**

---

_Updated: June 15 2025_
