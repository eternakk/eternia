# Prompt-Based World Generation Tasks

This backlog mirrors the deliverables outlined in *Implementation Roadmap: Prompt-Based World Generation*. Each task rolls up to a story, and every story maps to an epic. Keep checkboxes in sync with actual progress and reference `docs/implementation_stories.md` for narrative context and acceptance criteria.

## Epic EP1 — Integrate Sloyd for Prompt-Based 3D Asset Generation

**Outcome**: Natural-language prompts produce game-ready props that synchronize across web and Unreal VR clients, with AI agents able to spawn assets autonomously.

## Safety & Law Compliance (applies across EP1–EP4)

- [ ] Map new generation events to `AlignmentGovernor` triggers so `_enforce_laws` evaluates before world mutations (e.g., emit `spawn_entity` payloads with prompt metadata).
- [ ] Register policy callbacks guarding prompt input, placement coordinates, and asset metadata; rollback or block when active laws would be violated.
- [ ] Produce regression checks demonstrating at least one active law response (publish `LawEnforcedEvent`/`PolicyViolationEvent`) for each integration path.
- [ ] Document enforcement outcomes and mitigations in `docs/implementation_notes.md` for every feature that mutates the world.

### Story EP1-S1 — Developer can generate a 3D prop from a text prompt (web prototype)
- [ ] Acquire Sloyd API access and key; store credentials in FastAPI settings or env vars.
- [ ] Implement POST `/api/generate_model` accepting prompt + optional style/category parameters.
- [ ] Handle Sloyd API responses, surfacing clear errors for invalid prompts or rate limits.
- [ ] Download returned GLB asset, assign unique filename, and expose it via static hosting.
- [ ] Insert generated object into world state with unique ID and default transform.
- [ ] Broadcast spawn events over WebSockets so all clients receive object metadata.
- [ ] Load GLB assets in Three.js using `GLTFLoader`, applying transform and loading states.
- [ ] Ship developer prompt UI in React for submitting generation requests and viewing status/errors.
- [ ] Exercise the full prompt → model → placement loop with supported object categories.
- [ ] Iterate on parameters (LOD, orientation) until prompts reliably yield correctly placed assets.
- [ ] Emit governor-compatible generation events and verify laws/policies can veto unsafe spawns before world state mutations commit.

### Story EP1-S2 — Generated objects appear in the Unreal Engine VR client (runtime import)
- [ ] Connect Unreal client to backend state stream (WebSocket preferred, REST polling fallback).
- [ ] Parse spawn messages in Unreal and route them to the import pipeline.
- [ ] Integrate a runtime glTF importer (e.g., glTFRuntime plugin) into the UE5 project.
- [ ] Download GLB data via Unreal HTTP module, saving to an accessible location if needed.
- [ ] Spawn actors from imported meshes with correct transforms and collision defaults.
- [ ] Verify materials/textures load; adjust importer or Sloyd parameters for fidelity.
- [ ] Validate VR presentation (scale, stereo, collision) for newly spawned assets.
- [ ] Optional: add in-engine prompt tool (UMG widget or console command) to trigger generation.
- [ ] Run sync tests with web + VR clients to confirm simultaneous spawn and positioning.
- [ ] Profile runtime imports for hitching/memory; note mitigations for future optimization.
- [ ] Confirm Unreal client respects governor pause/rollback decisions and suppresses imports when a law blocks the request.

### Story EP1-S3 — AI agent can suggest and generate new world objects via prompts
- [ ] Define agent prompt interface (command format or helper function).
- [ ] Expose backend hook so simulation logic can call the Sloyd generation pipeline directly.
- [ ] Implement exemplar agent behavior that triggers generation under scripted conditions.
- [ ] Derive placement coordinates from agent context (location offsets or supplied transforms).
- [ ] Broadcast AI-spawned objects and surface in-client notifications/logs.
- [ ] Validate agent-driven generations across multiple clients and sessions.
- [ ] Add guardrails for unsupported prompts and log all AI generation attempts.
- [ ] Provide configuration toggle to enable/disable autonomous spawning during tests.
- [ ] Register governor policy callbacks for agent-driven prompts and log `PolicyViolationEvent` outcomes when requests conflict with active laws.

## Epic EP2 — Intelligent NPCs with Inworld AI Integration

**Outcome**: NPCs converse via Inworld, with a roadmap to voice-playback and animation.

### Story EP2-S1 — NPCs respond to player queries with AI-driven dialogue (text chat)
- [ ] Author Inworld NPC profiles and capture character identifiers.
- [ ] Secure API credentials and choose Simple API vs. engine SDK integration path.
- [ ] Add FastAPI route (e.g., POST `/api/npc/{npc_id}/message`) that relays messages to Inworld.
- [ ] Parse AI responses (text + metadata), handling API failures gracefully.
- [ ] Maintain NPC session state so conversations remain contextual.
- [ ] Build chat UI in React (and/or VR) with typing indicators and error handling.
- [ ] Display NPC replies in UI or as in-world bubbles linked to the actor.
- [ ] Conduct conversational tests to confirm session memory and persona fidelity.
- [ ] Tune personas or inject guardrails to keep dialogue on-theme and concise.
- [ ] Block or flag NPC-triggered actions that violate active laws; surface governor feedback in the chat workflow.

### Story EP2-S2 — (Future) Voice and animation for AI NPCs
- [ ] Integrate chosen text-to-speech service and cache generated audio.
- [ ] Stream or load audio in clients with spatial playback anchored to the NPC.
- [ ] Drive talking animations or visemes during playback.
- [ ] Map emotional metadata to gestures or facial expressions when available.
- [ ] Optional: add microphone capture + speech-to-text for player voice input.
- [ ] Test end-to-end voice conversations in flat and VR clients.
- [ ] Monitor latency; fall back to text-only when TTS fails or stalls.

## Epic EP3 — Asset Styling and Enhancement with Scenario AI

**Outcome**: Dynamically generated props inherit Eternia’s art direction through Scenario-powered styling and batch asset creation.

### Story EP3-S1 — Apply a custom art style to generated 3D models using AI
- [ ] Train or select Scenario style model aligned with Eternia’s visual targets.
- [ ] Design prompts (and optional reference inputs) for consistent texture generation.
- [ ] Integrate Scenario API call for styling requests within the backend pipeline.
- [ ] Apply returned textures/materials to Three.js and Unreal meshes at runtime.
- [ ] Offer a developer control to trigger styling on recently generated objects.
- [ ] Validate styled outputs against baseline models; adjust prompts or inputs as needed.
- [ ] Generate complementary 2D assets (icons/UI) for styled items.
- [ ] Cache styled artifacts to avoid repeated Scenario calls for identical prompts.
- [ ] Apply textures asynchronously so objects appear immediately and refine on update.
- [ ] Publish styling operations through the governor (e.g., `physics_modify` or `asset_style_update` events) and ensure laws such as Harmonized Physics can intervene.

### Story EP3-S2 — Batch-generate environment details and props with consistent style
- [ ] Identify high-impact asset families for batch generation (e.g., foliage, decor).
- [ ] Script Scenario batch prompts to produce varied yet cohesive outputs.
- [ ] Convert assets for in-game use (direct 2D usage or texturing lightweight meshes).
- [ ] Import generated assets and integrate placement workflows or blueprints.
- [ ] Review outputs for quality/style adherence; regenerate or curate as needed.
- [ ] Document runbooks so artists/designers can repeat or extend batch generation.
- [ ] Validate batch placement against governor policies (density, zone suitability) and capture enforcement evidence.

## Epic EP4 — Full Environment Generation with Marble (World Labs)

**Outcome**: AI-generated large-scale environments are explorable in Eternia, with persistence options for standout worlds.

### Story EP4-S1 — Generate and explore an AI-created environment from a prompt
- [ ] Secure Marble beta access and API/SDK credentials.
- [ ] Implement prompt submission flow to Marble (text-first, image optional).
- [ ] Capture Marble outputs (Gaussian splat data + metadata) for local use.
- [ ] Integrate Spark renderer into the Three.js client to display Marble scenes.
- [ ] Hook player navigation controls (web/VR) into Spark-rendered environments.
- [ ] Research Unreal ingestion path (conversion, point-cloud shader, or WebXR bridge).
- [ ] Provide developer UI controls for prompting, progress, and scene switching.
- [ ] Benchmark varied prompts for quality and performance across devices.
- [ ] Note strategies for merging Marble scenes with gameplay logic and future API growth.
- [ ] Emit governor review events (e.g., `physics_modify`, `zone_entered`) before swapping environments and honour law vetoes.

### Story EP4-S2 — Save and load AI-generated environments as game levels
- [ ] Persist Marble outputs with stable identifiers and metadata.
- [ ] Catalog generated worlds (prompt, timestamp, preview).
- [ ] Build load endpoint/function to rehydrate stored environments via Spark.
- [ ] Generate preview thumbnails or captures to aid selection.
- [ ] Plan Unreal parity if Marble scenes become importable assets.
- [ ] Validate save/load across restarts with multiple worlds.
- [ ] Document future user-facing access patterns and cost considerations.
- [ ] Store law-compliance status with each saved world and refuse reload when currently enabled laws would be violated.

---

**How to use this document**
- Open issues reference `Story` IDs (e.g., `EP1-S1`) to maintain traceability.
- Update checkboxes only after code, tests, and documentation land.
- Capture deviations, blockers, or accepted compromises in `docs/implementation_notes.md`.
