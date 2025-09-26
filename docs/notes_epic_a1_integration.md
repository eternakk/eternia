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
