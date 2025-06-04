```mermaid
flowchart TD
    %% ─────────────────────────────────────────────────────────────────
    %%    PRESENT‑DAY STACK  (code that already exists)
    %% ─────────────────────────────────────────────────────────────────
    subgraph Core_Runtime
        direction TB
        governor[Alignment‑Governor]
        eval[Eval Harness<br/>(Safety Tests)]
        world[EternaWorld<br/>(Physics • Symbols • Companions)]
        tracker[State‑Tracker<br/>(checksums • metrics)]
        interfaces[Standardized<br/>Interfaces]
        di[Dependency<br/>Injection]
        governor --> world
        eval --> governor
        world --> tracker
        tracker --> governor
        interfaces --> world
        interfaces --> governor
        interfaces --> tracker
        di --> interfaces
        di --> world
        di --> governor
        di --> tracker
    end

    subgraph Data_Stores
        artifacts[(Artifacts/<br/>Checkpoints)]
        logs[(Gov & Runtime Logs)]
    end
    tracker --> artifacts
    governor --> logs
    world --> logs

    %% ─────────────────────────────────────────────────────────────────
    %%    CONTROL / OBSERVABILITY LAYER  (building now)
    %% ─────────────────────────────────────────────────────────────────
    subgraph Control_Surface
        api[FastAPI / gRPC<br/>Bridge]
        api_interface[API Interface<br/>Layer]
        ws[(WebSocket Hub)]
        api --> ws
        api --> api_interface
    end
    api_interface <--> di
    api_interface <--> governor
    api_interface <--> world
    api_interface <--> tracker

    %% ─────────────────────────────────────────────────────────────────
    %%    USER‑FACING LAYERS
    %% ─────────────────────────────────────────────────────────────────
    subgraph Dashboard
        react[React / Next.js<br/>Mission‑Control]
        react --> ws
    end

    subgraph Immersive
        gl[WebGL / WebGPU<br/>Scene Window]
        xr[WebXR / VR Shell<br/>(Future)]
        bci[Neural / BCI<br/>(Future)]
        gl --> ws
        xr --> ws
        bci --> ws
    end

    %% ─────────────────────────────────────────────────────────────────
    %%    EXTERNAL AGENTS / COLLABORATORS
    %% ─────────────────────────────────────────────────────────────────
    friends[Remote Users<br/>(JWT Auth)]
    auditors[Safety Auditors]
    friends --> react
    auditors --> react
```
---
## 1  Core Runtime  (implemented)

| Module | Purpose | Key files |
|--------|---------|-----------|
| **EternaWorld** | Master object that unites physics, symbolic modifiers, companions, memory, etc. | `world_builder.py` |
| **Alignment‑Governor** | Hard failsafe: pause, rollback, or shutdown on policy breach. | `modules/governor.py` |
| **Eval Harness** | Unit‑tests that flag disallowed behaviours (net‑calls, self‑replication, identity drift). | `tests/alignment/*` |
| **State‑Tracker** | Persists evolution stats, chain‑of‑thought tensors, and model hashes. | `modules/state_tracker.py` |
| **Artifacts dir** | Binary checkpoints (`*.bin`), hashed weights, governor logs. | `artifacts/`, `logs/` |

---

## 2  Control / Observability Layer  (in progress)

| Component | Details |
|-----------|---------|
| **FastAPI / gRPC Bridge** | REST & RPC endpoints:<br/>`/state` (GET), `/command/pause`, `/command/rollback`, real‑time `/log` stream. |
| **WebSocket Hub** | Push‑only diff updates to clients (dashboard, future VR shell). |
| **API Interface** | Clean interface between core simulation logic and API server. |

---

## 3  Dashboard (React)  (next sprint)

* Live gauges: emotion intensity, symbolic modifiers, physics profile.
* Governor panel: **Play • Pause • Rollback • Kill**.
* Log console (tail ‑f on governor & runtime logs).
* Auth: local token today → JWT for remote collaborators tomorrow.

---

## 4  Immersive Path (road‑mapped)

| Stage | Tech | Goal |
|-------|------|------|
| **WebGL/WebGPU Window** | React‑Three‑Fiber or PixiJS | 3‑D "through the glass" view of current zone. |
| **WebXR / VR Shell** | Browser‑native XR | Full room‑scale presence, simple hand input. |
| **Neural / BCI Interface** | External hardware | Direct sensory write; dashboard becomes fallback. |

---

## 5  External Interfaces

* **Remote Users / Friends** – Connect via dashboard; governed by role‑based permissions.
* **Safety Auditors** – Read‑only log access; can trigger governor kill‑switch.

---

## 6  Architecture Enhancements (2023)

### Standardized Interfaces

To improve modularity and maintainability, standardized interfaces have been implemented for major system components:

| Interface | Purpose | Key files |
|-----------|---------|-----------|
| **ModuleInterface** | Base interface for all modules | `modules/interfaces.py` |
| **EvolutionInterface** | Interface for evolution-related functionality | `modules/interfaces.py` |
| **ConsciousnessInterface** | Interface for consciousness-related functionality | `modules/interfaces.py` |
| **AwarenessInterface** | Interface for awareness-related functionality | `modules/interfaces.py` |
| **SocialInterface** | Interface for social interaction functionality | `modules/interfaces.py` |
| **EmotionalInterface** | Interface for emotional functionality | `modules/interfaces.py` |
| **MemoryInterface** | Interface for memory-related functionality | `modules/interfaces.py` |
| **ExplorationInterface** | Interface for exploration functionality | `modules/interfaces.py` |
| **RuntimeInterface** | Interface for runtime functionality | `modules/interfaces.py` |
| **StateTrackerInterface** | Interface for state tracking functionality | `modules/interfaces.py` |

### Dependency Injection System

A dependency injection system has been implemented to reduce tight coupling between modules:

| Component | Purpose | Key files |
|-----------|---------|-----------|
| **DependencyContainer** | Container for managing dependencies | `modules/dependency_injection.py` |
| **ModuleInitializer** | Initializes and registers modules with the container | `modules/module_initializer.py` |

### API Interface Layer

A clean interface between the core simulation logic and the API server has been implemented:

| Component | Purpose | Key files |
|-----------|---------|-----------|
| **APIInterface** | Interface between core simulation logic and API server | `modules/api_interface.py` |

---

## Data Flow Summary

1. **World tick** → metrics → **State‑Tracker** → logs / checkpoints.  
2. Metrics feed **Alignment‑Governor**; policy breach triggers rollback.  
3. **FastAPI** polls governor + tracker → broadcasts deltas via **WebSocket**.  
4. **React dashboard** renders UI; sends user commands back to FastAPI.  
5. Future immersive clients attach to the same WebSocket without touching governor code.

### Updated Data Flow (2023)

1. **User Interaction**: The user interacts with the Dashboard UI, which sends commands to the API server.
2. **API Processing**: The API server processes the commands and forwards them to the **API Interface**.
3. **Core Simulation**: The API Interface interacts with the core simulation logic through the **Dependency Injection Container**.
4. **Governance**: The AlignmentGovernor monitors and controls the simulation to ensure safety.
5. **State Tracking**: The StateTracker tracks the state of the simulation and provides checkpoints and rollbacks.
6. **Event Propagation**: Events are propagated through the Event System to notify components of changes.
7. **UI Updates**: The API server sends updates to the Dashboard UI through WebSockets or SSE.

---

_Authored: April 19 2025_
_Updated: June 15 2025_
