# Quantum Integration Tasks for Eternia

This document breaks down the quantum computing integration plan into actionable tasks. Tasks are grouped by sprints and
can be executed incrementally. Where possible, each task is small, testable, and traceable.

Note on execution: All quantum features default to local/simulator backends and degrade gracefully to classical
randomness if quantum dependencies are unavailable. Determinism is preserved via stored seeds and measurement results.

## Legend

- [ ] pending
- [x] done
- [~] in progress

## Sprint 1: Foundations and Visual Impact

1. Documentation and planning
    - [x] Create this quantum_tasks.md with a clear roadmap, tasks, and acceptance criteria.
2. Core backend service
    - [x] Implement modules/quantum_service.py with:
        - [x] QRNG method with simulator-first, classical fallback
        - [x] variational_field(seed, size) returning a normalized 2D float array
        - [x] backend indicator and entropy estimation
3. API exposure (FastAPI)
    - [x] Add router services/api/routers/quantum.py with:
        - [x] POST /api/quantum/qrng { n } -> { bits, entropy, backend }
        - [x] POST /api/quantum/variational-field { seed, size } -> { field, seed, backend }
        - [x] Auth via Bearer scheme consistent with other routers; simple rate limit
    - [x] Register router in services/api/server.py and services/api/routers/__init__.py
4. Minimal integration (safe behind feature flag)
    - [x] Add feature flag (e.g., ET_USE_QUANTUM=true) in config
    - [x] World builder: seed zone modifiers using variational_field when flag is on
    - [x] Persist quantum seeds/results in state tracker for replay (recorded as discovery with metadata)
5. UI hooks (placeholders)
    - [x] Add API client methods for the two endpoints (ui/src/api.ts)
    - [x] Add an "Observe Oracle" button in ControlPanel to trigger QRNG and log result
6. Governance & safety
   - [x] Wrap quantum actions with guardrails (bounds, timeouts)
   - [x] Record quantum decisions to logs with circuit metadata
7. Observability & testing
   - [x] Add tracing tags (quantum.backend, quantum.type)
   - [x] Add basic tests for QuantumService methods and API endpoints

Acceptance criteria (Sprint 1):

- Calling /api/quantum/qrng returns a bitstring and entropy with nonzero length.
- Calling /api/quantum/variational-field returns a bounded (0..1) 2D array with the requested size and a backend marker.
- If quantum dependencies are missing, the system falls back to classical randomness with a clear backend label.
- No breaking changes to existing endpoints.
  k,

## Sprint 2: Mechanics and Entanglement

1. Quantum walks and layout optimization
    - [ ] Implement quantum_walk(params) producing adjacency/weights
    - [ ] Implement qaoa_optimize(qubo) for small problems (with simulator)
    - [ ] Add endpoints /api/quantum/quantum-walk and /api/quantum/qaoa-optimize
2. Entanglement mechanics
    - [ ] Add shared quantum_seed to Agent and Zone models
    - [ ] Bias zone modifiers with entangled variational fields
    - [ ] UI: show "Entangled" indicator for agent-zone pairs
3. Determinism & replay
    - [ ] Persist measurement outputs and seeds in State Tracker
    - [ ] Add loadable checkpoints with quantum metadata

Acceptance criteria (Sprint 2):

- Basic quest/path graph generated via quantum walk; reproducible with seed.
- QAOA returns feasible bitstring for small QUBOs; guarded by timeouts and limits.
- Entangled agent-zone influences are visible in the UI when toggled.

## Sprint 3: Caching, Metrics, and Polish

1. Performance & caching
    - [ ] Cache qrng pools and variational fields by seed/zone; invalidate on rituals
    - [ ] Batch prefetch on world load
2. Observability
    - [ ] Metrics: quantum_requests_total, quantum_entropy_avg, quantum_timeouts_total
    - [ ] Tracing spans annotated with backend and circuit types
3. UI polish
    - [ ] Shader-driven textures for quantum fields in ZoneCanvas
    - [ ] Toggle to reveal interference patterns in path graphs

Acceptance criteria (Sprint 3):

- Measurable reduction in latency for repeated requests via caching.
- Metrics visible in monitoring dashboards; traces tagged.
- Visual polish features present and toggleable without regressions.

## Notes and Constraints

- Keep circuits small (<= 16 qubits) when using simulators.
- Never make governance-critical decisions solely via quantum draws.
- Provide graceful degradation and replayability in all features.
