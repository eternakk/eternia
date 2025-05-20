```mermaid
flowchart TD
    %% ─────────────────────────────────────────────────────────────────
    %%    PRESENT‑DAY STACK  (code that already exists)
    %% ─────────────────────────────────────────────────────────────────
    subgraph Core_Runtime
        direction TB
        governor[Alignment‑Governor]
        eval[Eval Harness<br/>(Safety Tests)]
        world[EternaWorld<br/>(Physics • Symbols • Companions)]
        tracker[State‑Tracker<br/>(checksums • metrics)]
        governor --> world
        eval --> governor
        world --> tracker
        tracker --> governor
    end

    subgraph Data_Stores
        artifacts[(Artifacts/<br/>Checkpoints)]
        logs[(Gov & Runtime Logs)]
    end
    tracker --> artifacts
    governor --> logs
    world --> logs

    %% ─────────────────────────────────────────────────────────────────
    %%    CONTROL / OBSERVABILITY LAYER  (building now)
    %% ─────────────────────────────────────────────────────────────────
    subgraph Control_Surface
        api[FastAPI / gRPC<br/>Bridge]
        ws[(WebSocket Hub)]
        api --> ws
    end
    governor <--> api
    tracker  --> api
    world --command--> api

    %% ─────────────────────────────────────────────────────────────────
    %%    USER‑FACING LAYERS
    %% ─────────────────────────────────────────────────────────────────
    subgraph Dashboard
        react[React / Next.js<br/>Mission‑Control]
        react --> ws
    end

    subgraph Immersive
        gl[WebGL / WebGPU<br/>Scene Window]
        xr[WebXR / VR Shell<br/>(Future)]
        bci[Neural / BCI<br/>(Future)]
        gl --> ws
        xr --> ws
        bci --> ws
    end

    %% ─────────────────────────────────────────────────────────────────
    %%    EXTERNAL AGENTS / COLLABORATORS
    %% ─────────────────────────────────────────────────────────────────
    friends[Remote Users<br/>(JWT Auth)]
    auditors[Safety Auditors]
    friends --> react
    auditors --> react
```
---
## 1  Core Runtime  (implemented)

| Module | Purpose | Key files |
|--------|---------|-----------|
| **EternaWorld** | Master object that unites physics, symbolic modifiers, companions, memory, etc. | `world_builder.py` |
| **Alignment‑Governor** | Hard failsafe: pause, rollback, or shutdown on policy breach. | `modules/governor.py` |
| **Eval Harness** | Unit‑tests that flag disallowed behaviours (net‑calls, self‑replication, identity drift). | `tests/alignment/*` |
| **State‑Tracker** | Persists evolution stats, chain‑of‑thought tensors, and model hashes. | `modules/state_tracker.py` |
| **Artifacts dir** | Binary checkpoints (`*.bin`), hashed weights, governor logs. | `artifacts/`, `logs/` |

---

## 2  Control / Observability Layer  (in progress)

| Component | Details |
|-----------|---------|
| **FastAPI / gRPC Bridge** | REST & RPC endpoints:<br/>`/state` (GET), `/command/pause`, `/command/rollback`, real‑time `/log` stream. |
| **WebSocket Hub** | Push‑only diff updates to clients (dashboard, future VR shell). |

---

## 3  Dashboard (React)  (next sprint)

* Live gauges: emotion intensity, symbolic modifiers, physics profile.
* Governor panel: **Play • Pause • Rollback • Kill**.
* Log console (tail ‑f on governor & runtime logs).
* Auth: local token today → JWT for remote collaborators tomorrow.

---

## 4  Immersive Path (road‑mapped)

| Stage | Tech | Goal |
|-------|------|------|
| **WebGL/WebGPU Window** | React‑Three‑Fiber or PixiJS | 3‑D “through the glass” view of current zone. |
| **WebXR / VR Shell** | Browser‑native XR | Full room‑scale presence, simple hand input. |
| **Neural / BCI Interface** | External hardware | Direct sensory write; dashboard becomes fallback. |

---

## 5  External Interfaces

* **Remote Users / Friends** – Connect via dashboard; governed by role‑based permissions.
* **Safety Auditors** – Read‑only log access; can trigger governor kill‑switch.

---

## Data Flow Summary

1. **World tick** → metrics → **State‑Tracker** → logs / checkpoints.  
2. Metrics feed **Alignment‑Governor**; policy breach triggers rollback.  
3. **FastAPI** polls governor + tracker → broadcasts deltas via **WebSocket**.  
4. **React dashboard** renders UI; sends user commands back to FastAPI.  
5. Future immersive clients attach to the same WebSocket without touching governor code.

---

_Authored: April 19 2025_