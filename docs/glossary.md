# Eternia Project Glossary

This document provides definitions for key concepts and terminology used in the Eternia project.

## A

### Alignment Governor
A hard-safety layer that monitors the Eternia simulation for safety violations and alignment issues. It can pause, roll back, or shut down the simulation when necessary. See also [Governance and Safety](#governance-and-safety).

### API Server
FastAPI server that provides an API for interacting with the simulation. It exposes endpoints for controlling the simulation and retrieving state information.

## C

### Checkpoint
A saved state of the simulation that can be used for rollbacks. Checkpoints are automatically created at regular intervals and stored in the `artifacts/checkpoints` directory.

### Companion
An agent within the Eternia simulation with emotional capabilities and social interactions. Companions are managed by the Companion Ecology.

### Companion Ecology
The system that manages companions (agents) in the simulation and their interactions.

### Consciousness Replica
A component that models the consciousness of agents within the simulation.

### Continuity Breach
Occurs when the identity continuity score falls below a threshold set in the governor, potentially triggering a rollback.

## E

### Emotional Agent
Base class for agents with emotional capabilities, providing methods for processing and responding to emotions.

### Emotional Circuit System
A system that processes emotions and their effects on the simulation world.

### Emotional State
A representation of an agent's emotional condition, including the type of emotion, its intensity, and direction.

### Eternia World
The main container for the simulation state, providing access to all subsystems including companions, exploration, rituals, etc.

### Event
An object that represents something that has happened in the system. All events inherit from the `Event` base class.

### Event Bus
The central component of the event system that manages event subscriptions and publications. It implements the publisher-subscriber pattern.

### Event Handler
A function or method that is called when an event is published. It receives the event object as a parameter.

### Event Listener
A component that listens to events. The `EventListener` base class provides a way to register event handlers using the `@event_handler` decorator.

### Exploration
The system that manages the exploration of zones and discovery of new areas within the simulation.

## G

### Governance and Safety
The systems and components responsible for ensuring the simulation operates within safe parameters. This includes the Alignment Governor, laws, and policies.

### Governor Events
Events published by the governor to communicate state changes, such as pause, resume, shutdown, rollback, etc.

## I

### Identity Continuity
A measure of how well the simulation maintains consistent identity properties over time. If this falls below a threshold, it may trigger a continuity breach.

## L

### Law
A rule that governs behavior within the simulation. Laws are triggered by events and can apply effects when their conditions are met.

### Law Enforcement
The process by which the governor enforces laws defined in the law registry.

### Law Parser
A component that parses law definitions from configuration files.

## M

### Memory Integration
The system that manages the integration of memories for agents within the simulation.

## P

### Physics Profile
A configuration of physical properties for a zone, including gravity, time flow, dimensions, and energy behavior.

### Policy
A custom callback registered with the governor that can trigger rollbacks when certain conditions are met.

### Property-Based Testing
A testing approach that generates random inputs to test properties that should hold true for all valid inputs, rather than testing specific examples.

## R

### Resonance Engine
A system that manages resonance between agents and the environment.

### Ritual
A defined sequence of actions that agents can perform, often with symbolic meaning and effects on the simulation.

### Rollback
The process of reverting the simulation to a previous checkpoint, typically in response to a safety violation or policy breach.

### Runtime
The component that manages the simulation cycle and time progression.

## S

### Social Interaction
The system that manages interactions between agents within the simulation.

### Social Presence
Defines how agents perceive and are perceived by others within the simulation.

### State Tracker
A component that tracks the state of the simulation, including checkpoints and rollbacks.

### Symbolic Emotion Map
A mapping between emotions and their symbolic representations in the simulation, such as rituals, zone effects, and modifiers.

## T

### Time Dilation
The adjustment of time flow within the simulation relative to real-world time.

### Time Synchronizer
A component that manages the synchronization of time between the simulation and the real world.

## W

### World Builder
The component responsible for creating and initializing the Eternia world, setting up all components and their initial state.

## Z

### Zone
A distinct area within the simulation with its own properties, modifiers, and characteristics.

### Zone Modifier
A modifier that affects zones and agents within them, potentially changing their behavior or properties.