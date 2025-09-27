# Epic A1 – Existing UI and WebSocket Integration Points

## Frontend Rendering Stack
- `ui/src/App.tsx` composes providers (`FeatureFlagProvider`, `NotificationProvider`, `LoadingProvider`, `WorldStateProvider`) before rendering core panels. `ZoneCanvas` is already lazy-loaded via `createLazyComponent` and uses `@react-three/fiber`, making it the natural insertion point for richer 3D scenes.
- `WorldStateProvider` (`ui/src/contexts/WorldStateContext.tsx`) polls `/api/state` every ~3s (configurable via `refreshInterval`) and exposes helpers like `useWorldState`, `useCurrentZone`, and `useZoneModifiers`. Any scene manager should subscribe here for baseline world/zone snapshots.
- `ZoneCanvas` (`ui/src/components/ZoneCanvas.tsx`) renders cached GLTF assets with Drei helpers, calculates lighting/FX from emotion + modifiers, and already handles asset caching, suspense fallback, and modal overlays. It currently relies on REST polling for state and `getZoneAssets(zone)` for asset URLs. Extending this component—or factoring its logic into a shared scene manager—gives immediate three.js scaffolding.

## WebSocket Utilities
- Backend endpoint `services/api/server.py#L343` exposes `/ws`. Authentication is a JSON token handshake, and the connection is rate-limited and tracked in `clients` for broadcast.
- Governor/Zone events flow through `modules/utilities/event_adapter.LegacyEventAdapter`, which normalizes objects to `{t, event, payload}`. The broadcaster coroutine relays these payloads to all websocket clients.
- Frontend hook `ui/src/hooks/useGovEvents.ts` wraps the connection with `reconnecting-websocket`, converts the HTTP API URL into a WS URL, pushes parsed messages into React state, and is consumed by `LogConsole`. This hook is the thin point to extend: a new `useSimulationStream` could reuse the same transport while projecting payloads into typed scene mutations.

## Candidate Integration Points for 3D Scene Updates
- **Initial state**: Pull zone geometries, modifiers, and companions via `WorldStateProvider` + `getZones`/`getZoneAssets` cache. `ZoneCanvas` already memoizes emotion intensity, so the 3D scene should centralize that logic instead of duplicating it.
- **Real-time updates**: Leverage `useGovEvents` (or a derivative hook) to listen for `zone_changed`, `zone_modifier_added`, `checkpoint_*`, etc. These events already contain zone names/modifier info suitable for incremental scene updates.
- **Agent/companion data**: `getAgents()` in `ui/src/api.ts` writes to `localStorage('last_agents')`; any spatialized companions can subscribe to the same feed or extend the REST polling layer.
- **Governor actions**: Events like `policy_violation`, `pause`, and `rollback_complete` arrive over the websocket and can drive cinematic overlays or scene-level state changes once the renderer listens to the stream.

## Follow-Up Notes
- Documented payload shapes live in `modules/utilities/event_adapter._convert_to_legacy_format`; adding new event classes there will automatically surface via websocket.
- Asset URLs fetched from `/zone/assets?name=<zone>` should be normalized to absolute paths before loading GLTF/skyboxes to avoid CORS/runtime errors.
- Tests already stub websocket auth in `tests/integration/test_auth_integration.py`; new client hooks should be covered with similar stubs to avoid network coupling in Vitest.

## Next Steps
1. Design a dedicated scene state manager (context or Zustand store) that merges REST snapshots with websocket deltas.
2. Extend the websocket hook to expose typed events (`zoneChanged`, `modifierAdded`, `governorAlert`) rather than raw JSON.
3. Prototype a refactored `ZoneCanvas` that delegates to the new manager while keeping current emotion/modifier visual logic intact, ensuring backwards compatibility during gradual rollout.

## Realtime Wiring (2025-09-26)
- Added `SceneManager` realtime state that hydrates zones and governor flags from normalized websocket events.
- `useSimulationStream` provides filtered/typed event access; manager now exposes `realtime` maps for downstream components.
- `ZoneCanvas` keeps scene focus in sync via `setActiveZone`, enabling future camera/lighting reactions to governor/state changes.
- Scene manager now computes zone-influenced camera orbits and lighting boosts (ambient/exposure) with governor pause dimming to keep the renderer reactive to live state.

## Setup Checklist for Scene Integration (A1.6)

**Environment & Secrets**
- Ensure `config/mcp/.env` (or local `.env`) includes:
  - `VITE_API_URL` pointing to the Eternia API host (defaults to `http://localhost:8000`).
  - `VITE_ETERNA_TOKEN` valid for websocket authentication (matches `/ws` handshake in `useGovEvents`).
- Verify backend websocket endpoint `/ws` is reachable; rate limiting/authorization failures surface as console errors during connection.

**Dependencies & Build Steps**
- Node 18+ with npm; install UI deps via `npm install` (Three.js stack: `three`, `@react-three/fiber`, `@react-three/drei`, `@react-three/postprocessing`; realtime stack: `reconnecting-websocket`).
- Keep TypeScript tooling aligned (`typescript@~5.7.2`, `vite@^6.3.1`, `vitest@^3.1.4`) to avoid compiler drift.
- Run `npm run typecheck` and targeted vitest suites (`npm run test -- src/scene/__tests__/*.test.tsx`) after scene changes to validate typings and realtime wiring.

**Runtime Expectations**
- `SceneManagerProvider` must wrap the app (see `src/App.tsx`) so `useSceneManager`/`SceneRenderer` share context.
- Websocket traffic flows through `useGovEvents` → `useSimulationStream` → `SceneManager`; ensure these hooks mount on pages where realtime visuals are required.
- GLTF assets and skyboxes load from `/zone/assets?name=<zone>`; confirm CORS/static hosting permits fetches from the configured `VITE_API_URL`.

**Operational Notes**
- Live modifier effects combine REST snapshots (`WorldStateProvider`) with websocket deltas; keep backend event schemas in sync with `modules/utilities/event_adapter._convert_to_legacy_format`.
- Governor pauses dim lighting and show UI banners (handled in `ZoneCanvas`); test pause/resume flows before demos.
- Document any new asset paths or governor event types here when extending the scene to keep implementers aligned.

## World Entity Data Inventory (A1.7)

To keep Eternia's simulated world coherent across REST polling, realtime streams, and 3D rendering, align on the following data sources:

| Domain | REST Source | Realtime Source | Notes for Renderers |
| --- | --- | --- | --- |
| Zones | `getZones()` (`ui/src/api.ts`) → `Zone { id, name, origin, complexity, explored, emotion, modifiers }` | `zone.changed`, `zone.explored` events from `useSimulationStream` | `SceneManager.realtime.zones` merges REST snapshot with event deltas; use `explored` and `origin` to drive asset selection, `emotion` for base tinting. |
| Modifiers | `State.modifiers` map in `getState()` + per-zone `Zone.modifiers` | `zone.modifier_added` events (payload `{ zone_name, modifier }`) | `modifiers` drive lighting boosts/FX; maintain canonical modifier names (see event adapter cases) when adding new visual effects. |
| Rituals | `getRituals()` returning `Ritual { id, name, purpose, steps, symbolic_elements }` | Governor events such as `law_enforced`, `policy_violation`, future `ritual_*` events | Ritual metadata informs UI overlays and companion choreography; ensure any new ritual events are added to `normalizeSimulationEvent`. |
| Governor State | `WorldStateProvider` exposes `current_zone`, `identity_score`, `emotion` | `governor.pause`, `governor.resume`, `governor.policy_violation`, `governor.rollback_complete` | Lighting/camera responds to pause + violations; record decisions for narrative telemetry. |

**Vision Guardrails**
- Treat REST (`/api/state`, `/api/zones`, `/api/rituals`) as authoritative checkpoint snapshots; websocket events are incremental truth that keep the world alive between polls.
- When new world mechanics land (e.g., companion paths, environmental hazards), introduce both REST schema updates and companion websocket events so scene state stays deterministic for replay/undo workflows.
- Keep serialized identifiers (zone names, modifier strings, ritual IDs) stable—3D asset lookup tables (A1.8) will rely on them for mesh/material binding.

This inventory should be revisited whenever backend schemas evolve to preserve immersion and narrative consistency across Mission Control and the 3D interface.

## Zone Asset Lookup Catalog (A1.8)

- `ui/src/scene/zoneAssetCatalog.ts` centralizes mesh/skybox definitions per zone and ties narrative tooltips to modifier highlights. The catalog mirrors `assets/zone_assets.json` while adding design notes (`tags`) for future biome-aware renderers.
- `getZoneAssetDefinition(zoneName)` returns the default visuals; API responses from `/zone/assets` override these selectively, ensuring offline previews still render a meaningful scene.
- `buildTooltip(zoneName, realtime)` fuses the base lore snippet with active modifier guidance so Zone Details can explain why a space looks/behaves a certain way.
- Modifier guidance (`MODIFIER_HIGHLIGHTS`) should grow alongside visual implementations—keep descriptions short, evocative, and aligned with the alignment governor’s narrative constraints.
- `zoneGeometryLoader.ts` wraps Drei’s GLTF caching with hover metadata and pointer hooks, ensuring every mesh instantiation can surface lore tooltips and future interaction hotspots without redundant asset loads.
- Pointer interactions now dispatch `eternia:zone-hover` / `eternia:zone-clicked` events from the scene graph, letting ritual planners and governor overlays respond to spatial focus without polling React state.

When introducing new zones or modifiers, update both the backend manifest and this catalog so the simulated world’s look-and-feel stays in lockstep with its systemic logic.

## Overlay Performance Baseline (A1.10 Prep)

- Capture frame timing and asset load metrics via `npm run test -- src/scene/__tests__` (logic) plus manual `performance.mark` probes in `ZoneCanvas` before/after overlay changes.
- Record navigator CPU/GPU traces while triggering governor pause/resume and modifier storms; store snapshots under `artifacts/perf/overlays/<date>.md` with environment info (GPU, driver, browser).
- Define target budgets: <16ms average frame, <50ms hover-to-tooltip latency, <200ms rollback overlay activation.
- Before shipping new cinematic overlays, run the baseline checklist and note deviations in this file so we maintain the immersive feel without dropping frames in the simulated world.

### Snapshot-driven Overlay Validation (A1.10)

- Sample overlays now ship with deterministic fixtures in `ui/src/__tests__/fixtures/overlaySnapshots.ts`; each entry lists canonical zones and live modifiers sourced from recorded simulation snapshots.
- The vitest suite `npm run test -- src/__tests__/ZoneEventOverlay.snapshot.test.tsx` dispatches `eternia:zone-hover` / `eternia:zone-clicked` events derived from those fixtures and asserts that tooltips, modifiers, and dismissal flows render correctly.
- `buildTooltip` fidelity is verified end-to-end by constructing a synthetic `SceneRealtimeState` for every fixture and ensuring the overlay reflects governor lighting cues (pause dimming, modifier highlights, etc.).
- Add new fixtures whenever backend snapshot schemas evolve; keep one-to-one parity with stored snapshots under `artifacts/perf/overlays/` so automated validation mirrors real operator scenarios.

## Asset Naming & Art Pipeline Coordination (A1.11)

- Meshes: name GLTF files `zone_<slug>.glb`, where `<slug>` matches the lowercase, dash-separated zone identifier used in backend `Zone.name` (e.g., `Quantum Forest` → `zone_quantum-forest.glb`). Auxiliary variants (night, ritual, damaged) append `_variant`, keeping primary mesh untouched.
- Skyboxes/HDRIs: store as `sky_<slug>_<lighting>.hdr` with lighting keywords (`dawn`, `noon`, `storm`) to signal tone-mapping targets. Reference these keys from `zoneAssetCatalog.ts` to avoid hard-coded paths in scene components.
- Materials & textures live under `assets/materials/<slug>/` with filenames mirroring mesh material slots. Coordinate updates with the art pipeline by logging changes in `docs/art_pipeline_changelog.md` (create entries per sprint) and tagging affected modifiers.
- Tooltip copy and modifier highlight strings remain the contract between design and rendering; any change to naming must update both the asset manifest and the `MODIFIER_HIGHLIGHTS` dictionary to keep scene overlays aligned with the authored lore.
- Review cycle: art pipeline submits asset manifests (mesh + skybox + thumbnails) via pull request, referencing the zone slug and modifier coverage. Scene integrators update `zoneAssetCatalog.ts` and rerun `npm run test -- src/__tests__/ZoneEventOverlay.snapshot.test.tsx` to confirm overlays surface the new art notes.

## Alignment Governor Editor Surface (A1.12)

- Mutations: terrain sculpting and physics tuning rely on the `POST /command/{action}` router. Relevant governor actions include `pause`, `resume`, `step`, `step_reset`, `reset`, `shutdown`, `emergency_stop`, and `rollback`. Terrain/physics edits must wrap their mutations between `pause` and `resume` to avoid conflicting with live simulation ticks.
- State adjustments route through `POST /command/rollback` (rollback to checkpoints) and future editor-specific endpoints under `services/api/routers/state.py` (`POST /state/apply` pending). Ensure sculpt tools capture the checkpoint filename returned from `/command/rollback` for audit trails.
- Authentication: all `/command/*` endpoints require bearer tokens issued via the auth service. Test tokens (`test-token-for-authentication`) unlock the pipeline in staging; production editors must hold users with the `EXECUTE` permission. Requests without `EXECUTE` raise a 403 and log a sanitized fingerprint of the caller.
- Authorization flow: editor UI should call `/auth/session` (see `services/api/auth/auth_service.py`) to confirm token validity and surface warnings before enabling destructive controls. Governor responses (`governor.pause`, `governor.policy_violation`, `governor.rollback_complete`) stream over websockets and must be mirrored in editor state to provide immediate feedback on allowed/disallowed edits.
- Safety checklist: every mutation must (1) save a checkpoint via `governor.rollback` helpers, (2) submit a diff summary to the Alignment Governor log channel (`services/api/routers/log.py`), and (3) re-run overlay validation to ensure new terrain/physics parameters still highlight correctly in `ZoneEventOverlay`.

## Editor Workflow Design (A1.13)

1. **Preparation Stage**
   - Validate operator authentication (`/auth/session`) → lock editor controls until token + `EXECUTE` role confirmed.
   - Display current governor status (`governor.isPaused`, `governor._rollback_active`) via `useSimulationStream`; block edits if rollback is active.
2. **Sculpting Session**
   - On “Enter Edit Mode” trigger: send `POST /command/pause`, then request a new checkpoint (`POST /command/rollback` with `file=null`) to capture the pre-edit state ID returned in the response (`detail` field).
   - Terrain tools operate on a staged heightmap buffer; physics controls (gravity, damping, collision layers) expose sliders bound to a shadow copy of `world.eterna.config`. UI keeps a diff view (original vs staged) for review.
   - Provide live overlays (wireframe mesh, collider outlines) toggled per tool; reuse `ZoneEventOverlay` hooks for tooltips explaining modifier impacts.
3. **Review & Commit**
   - Summarize edits (height delta metrics, physics parameter changes) in a side panel; require operator acknowledgment and an optional narrative note.
   - On commit: POST staged payload to future `/state/apply` (plan) or existing admin endpoint, then `POST /command/resume`. If commit fails, UI automatically triggers `POST /command/rollback` with checkpoint filename.
4. **Abort / Undo**
   - Provide “Abort Edits” button that issues `POST /command/rollback` with the checkpoint captured at pause time and then resumes the governor.
5. **Session Logging**
   - Emit structured event to `/log/editor` (planned) or reuse `services/api/routers/log.py` to capture operator, checkpoint IDs, and diff summary for audit.

### UI States
- **Idle**: overlays hidden, edit controls disabled.
- **Editing**: scene dimming applied, gizmos active, governor paused banner displayed.
- **Pending Commit**: disable sculpt inputs, show spinner while mutation request is in-flight.
- **Error**: highlight failed parameters, auto-offer rollback.

## Optimistic Mutation Strategy (A1.14)

- **Local Diff Buffer**: maintain an in-memory store (e.g., Zustand) capturing applied terrain deltas and physics tweaks. Render these immediately for responsive feedback while queuing mutation payloads.
- **Mutation Pipeline**:
  1. Serialize staged edits and post to editor API.
  2. Assume success: refresh scene state from local buffer, mark diff as “committed”.
  3. If API response returns error or `governor.policy_violation`, automatically revert buffer (apply checkpoint) and surface violation details in UI.
- **Governor Feedback Loop**: listen for `governor.policy_violation` and `governor.rollback_complete` events mid-edit; if received, freeze controls and initiate rollback to last safe checkpoint.
- **Offline/Latency Handling**: queue mutations when offline; require explicit user confirmation when reconnecting before replaying buffered edits.

## Validation & Telemetry Requirements (A1.15)

- **Guards**: enforce terrain delta thresholds (max elevation change, slope limits) before submit; block physics params outside configured min/max and show inline validation errors.
- **Error Surfacing**: map backend error codes (400 invalid payload, 403 permission, 409 conflict) to human-readable banners. Provide “View Logs” link pointing to recent governor log entries.
- **Telemetry**: instrument with `ui/src/utils/tracing.ts` to emit spans for `editor.pause`, `editor.apply`, `editor.rollback`. Attach attributes: checkpoint ID, duration, number_of_vertices_modified, physics_fields_changed.
- **Metrics Export**: push event counts to `/monitoring/metrics` (planned) or local console for QA. Ensure test coverage via vitest (mocking tracing) to confirm instrumentation triggers once per action.

## Editor Usage Handbook Scope (A1.16)

- Document prerequisites (training checklist, required permissions, safety drills).
- Outline the step-by-step workflow described above, including screenshots of each UI state.
- Provide troubleshooting (e.g., “Rollback triggered automatically”, “Modifier conflicts detected”) along with escalation paths to Alignment Governor operators.
- Include quick-reference tables for asset naming (linking back to this note) and governor command cheat sheet.
- Host the handbook draft under `docs/editor_handbook.md` with versioned updates coordinated with art/design teams.
## Snapshot Schema Alignment (A1.17)

- Backend state snapshots now surface structured checkpoint metadata: each entry holds `path`, `label`, `kind`, `created_at`, optional `state_version`, `size_bytes`, and `continuity` score. The state tracker normalizes historical strings into this shape so legacy checkpoints remain consumable. Governor rollbacks append metadata describing the rollback target, keeping UI timelines lossless.
- `/command/checkpoints` returns these enriched objects; the UI normalizes responses via `normalizeCheckpointRecords` before rendering. Consumers that still need raw strings can map over `.path`.
- When adding new metadata fields, update `CheckpointRecord` in `ui/src/api.ts` and `modules/state_tracker.register_checkpoint` to ensure both directions stay in sync.

## Scene History Serialization (A1.18)

- `ui/src/scene/history/serializer.ts` converts `SceneState` + `SceneRealtimeState` snapshots into deterministic JSON payloads. Signatures use a stable JSON stringify so identical states collapse to the same hash, powering UI diffing.
- Snapshots capture camera/render settings, zone modifier sets (sorted for determinism), and distilled governor events (pause/violation/rollback). Optional checkpoint metadata attaches directly from the normalized backend payload.
- Serializer exports a `SceneHistoryEntry` shape consumed by history stacks, undo/redo tooling, or audit exports. Extend this module whenever new realtime fields arrive—keep serialization order consistent to avoid signature churn.

## History Stack & Undo Workflow (A1.19)

- `ui/src/scene/history/historyStack.ts` provides an in-memory ring buffer (default 50 entries) with undo/redo semantics. Dedupe mode prevents redundant entries when the serialized signature is unchanged.
- Pushing a new entry after an undo truncates the future branch, mirroring standard editor workflows. Max size trimming drops the oldest entries while keeping pointer alignment sane.
- Integrators can hydrate the stack with `serializeSceneState` outputs, letting UI glue expose “Undo terrain edit” or “Redo physics tweak” actions without bespoke bookkeeping.

## Rollback Regression Coverage (A1.20)

- State tracker checkpoint records now normalize both automatic and rollback-generated files, and governor events log the same metadata. `normalizeCheckpointRecords` guarantees UI components always receive structured fields even if API stubs or older services emit raw strings.
- Vitest suites cover serializer determinism and history stack behavior; Python integration tests continue validating database persistence using the enriched checkpoint schema. When adding new rollback flows, assert that governor events include the checkpoint fingerprint and that `list_checkpoints` exposes matching metadata.
