# Eternia System Architecture Documentation

## 1. System Overview

Eternia is a complex world simulation system with AI companions, physics, emotions, and safety mechanisms. The system is designed to create and manage a virtual world where AI companions can interact, evolve, and be governed by safety policies.

## 2. High-Level Architecture

The Eternia system follows a modular architecture with clear separation of concerns. The main components are:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Eternia System                               │
│                                                                     │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────────┐   │
│  │  Simulation   │    │   Governance  │    │  User Interface   │   │
│  │    Core       │◄───┤   & Safety    │    │                   │   │
│  │               │    │               │    │                   │   │
│  └───────┬───────┘    └───────────────┘    └─────────┬─────────┘   │
│          │                                           │             │
│          │            ┌───────────────┐              │             │
│          └───────────►│    Services   │◄─────────────┘             │
│                       │    Layer      │                            │
│                       │               │                            │
│                       └───────────────┘                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 3. Core Components

### 3.1 Simulation Core

The simulation core is responsible for managing the virtual world, its entities, and the simulation loop.

```
┌─────────────────────────────────────────────────────────────┐
│                    Simulation Core                           │
│                                                             │
│  ┌───────────────┐    ┌───────────────┐    ┌─────────────┐  │
│  │  EternaWorld  │◄───┤  World Builder│    │   Physics   │  │
│  │               │    │               │    │             │  │
│  └───────┬───────┘    └───────────────┘    └─────────────┘  │
│          │                                                   │
│          ▼                                                   │
│  ┌───────────────┐    ┌───────────────┐    ┌─────────────┐  │
│  │  Companions   │    │   Emotions    │    │  Evolution  │  │
│  │               │    │               │    │             │  │
│  └───────────────┘    └───────────────┘    └─────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Key Components:

- **EternaWorld**: The central class that manages the world state and simulation loop
- **World Builder**: Responsible for setting up and initializing the world
- **Physics**: Handles physical interactions and constraints
- **Companions**: Manages AI companions and their behaviors
- **Emotions**: Handles emotional states and responses
- **Evolution**: Manages the evolution of entities over time

### 3.2 Governance & Safety

The governance and safety layer ensures that the simulation adheres to defined policies and safety constraints.

```
┌─────────────────────────────────────────────────────────────┐
│                  Governance & Safety                         │
│                                                             │
│  ┌───────────────┐    ┌───────────────┐    ┌─────────────┐  │
│  │  Alignment    │◄───┤  Law Parser   │    │  Protection │  │
│  │  Governor     │    │               │    │             │  │
│  └───────┬───────┘    └───────────────┘    └─────────────┘  │
│          │                                                   │
│          ▼                                                   │
│  ┌───────────────┐    ┌───────────────┐                     │
│  │  State        │    │  Governor     │                     │
│  │  Tracker      │    │  Events       │                     │
│  └───────────────┘    └───────────────┘                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Key Components:

- **Alignment Governor**: Ensures that the simulation adheres to safety policies
- **Law Parser**: Parses and interprets laws and policies
- **Protection**: Implements protection mechanisms
- **State Tracker**: Tracks the state of the world and entities
- **Governor Events**: Manages events related to governance

### 3.3 User Interface

The user interface provides a way for users to interact with the simulation.

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface                            │
│                                                             │
│  ┌───────────────┐    ┌───────────────┐    ┌─────────────┐  │
│  │  React/TS     │◄───┤  Components   │    │  State      │  │
│  │  Frontend     │    │               │    │  Management │  │
│  └───────┬───────┘    └───────────────┘    └─────────────┘  │
│          │                                                   │
│          ▼                                                   │
│  ┌───────────────┐                                          │
│  │  API Client   │                                          │
│  │               │                                          │
│  └───────────────┘                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Key Components:

- **React/TS Frontend**: The main frontend application built with React and TypeScript
- **Components**: Reusable UI components
- **State Management**: Manages the frontend state
- **API Client**: Communicates with the backend services

### 3.4 Services Layer

The services layer provides APIs and interfaces for communication between components.

```
┌─────────────────────────────────────────────────────────────┐
│                    Services Layer                            │
│                                                             │
│  ┌───────────────┐    ┌───────────────┐    ┌─────────────┐  │
│  │  API Service  │◄───┤  Interfaces   │    │  Utilities  │  │
│  │               │    │               │    │             │  │
│  └───────────────┘    └───────────────┘    └─────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Key Components:

- **API Service**: Provides RESTful APIs for frontend-backend communication
- **Interfaces**: Defines interfaces for component communication
- **Utilities**: Provides utility functions and services

## 4. Data Flow

The data flow in the Eternia system follows a cyclical pattern:

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  User Input   │────►│  API Service  │────►│  EternaWorld  │
│               │     │               │     │               │
└───────────────┘     └───────────────┘     └───────┬───────┘
                                                   │
                                                   ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  UI Update    │◄────│  API Response │◄────│  Simulation   │
│               │     │               │     │  Processing   │
└───────────────┘     └───────────────┘     └───────────────┘
```

1. User input is received through the UI
2. The input is sent to the API service
3. The API service forwards the input to the EternaWorld
4. The EternaWorld processes the input and updates the simulation
5. The updated state is sent back through the API service
6. The UI is updated with the new state

## 5. Component Interactions

### 5.1 Main Simulation Loop

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  EternaWorld  │────►│  Collect      │────►│  Governor     │
│               │     │  Metrics      │     │  Tick         │
└───────┬───────┘     └───────────────┘     └───────┬───────┘
        ▲                                           │
        │                                           ▼
        │                                   ┌───────────────┐
        └───────────────────────────────────┤  World Step   │
                                            │               │
                                            └───────────────┘
```

The main simulation loop:
1. Collects metrics from the world
2. Passes the metrics to the governor for safety checks
3. If approved, steps the world forward
4. Repeats

### 5.2 Companion Update Process

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  Update RL    │────►│  Handle Law   │────►│  Execute      │
│  Companion    │     │  Compliance   │     │  Action       │
└───────┬───────┘     └───────────────┘     └───────┬───────┘
        ▲                                           │
        │                                           ▼
        │                                   ┌───────────────┐
        └───────────────────────────────────┤  Update Agent │
                                            │  Evolution    │
                                            └───────────────┘
```

The companion update process:
1. Updates the RL (Reinforcement Learning) companion
2. Checks for law compliance
3. Executes the chosen action
4. Updates the agent's evolution

## 6. Technology Stack

- **Backend**: Python
- **Frontend**: TypeScript, React, Tailwind CSS
- **Build Tools**: Vite
- **AI/ML**: PyTorch (for RL companions)
- **API**: RESTful APIs

## 7. Deployment Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                      Client Device                             │
│                                                               │
│  ┌───────────────┐                                            │
│  │  Web Browser  │                                            │
│  │               │                                            │
│  └───────┬───────┘                                            │
│          │                                                     │
└──────────┼─────────────────────────────────────────────────────┘
           │
           ▼
┌──────────┴─────────────────────────────────────────────────────┐
│                      Server                                     │
│                                                               │
│  ┌───────────────┐    ┌───────────────┐    ┌─────────────┐    │
│  │  Web Server   │◄───┤  API Service  │◄───┤  Simulation │    │
│  │               │    │               │    │  Core       │    │
│  └───────────────┘    └───────────────┘    └─────────────┘    │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

The deployment architecture consists of:
1. Client devices running web browsers
2. A server running the web server, API service, and simulation core

## 8. Future Architecture Considerations

- **Scalability**: Consider containerization with Docker for consistent deployment
- **Monitoring**: Implement monitoring and alerting for production deployments
- **Performance**: Optimize the simulation loop and memory usage for large simulations
- **Data Management**: Implement proper database schema for persistent storage

## 9. Conclusion

The Eternia system architecture is designed to be modular, maintainable, and extensible. The clear separation of concerns between the simulation core, governance & safety, user interface, and services layer allows for independent development and testing of each component.