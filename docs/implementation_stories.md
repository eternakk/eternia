# Implementation Stories & Task Breakdown

Derived from *Implementation Roadmap: Prompt-Based World Generation*. Each story below links the high-level intent to concrete success signals; see `docs/tasks.md` for the detailed checklist and owners.

## Epic EP1 – Integrate Sloyd for Prompt-Based 3D Asset Generation

### Story EP1-S1 – As a world builder, I can type a prompt and see the matching prop appear in the web client
- Deliver a FastAPI → Sloyd pipeline that turns text prompts into cached GLB assets.
- Broadcast spawn updates over WebSockets and render them in Three.js with loading states.
- Provide a lightweight developer UI for prompts, error feedback, and iterative testing.
- Route generated objects through the Alignment Governor so active laws can veto unsafe spawns before state mutation.
- Acceptance: supported prompts render correctly positioned props within seconds across sessions.

### Story EP1-S2 – As a VR user, I see spawned props materialize inside the Unreal client in sync with the web view
- Subscribe Unreal to the shared world-state channel and import GLB assets at runtime.
- Spawn actors with working materials/collision and validate VR scale + stereo fidelity.
- (Optional) expose in-headset tools for issuing prompts during development playtests.
- Honour governor pause/rollback states so the VR client never instantiates assets that laws reject.
- Acceptance: simultaneous prop generation displays in both clients without manual asset import.

### Story EP1-S3 – As an autonomous agent, I can request objects that appear at my chosen location
- Expose a backend hook so AI logic triggers the Sloyd flow without human UI.
- Log and announce agent-driven spawns, applying placement rules tied to the agent’s context.
- Add guardrails and toggles that let operators pause autonomous generation safely.
- Evaluate agent prompts against law/policy allowlists and emit `PolicyViolationEvent` when blocked.
- Acceptance: scripted agent demo spawns multiple valid props while preventing unsupported prompts.

## Epic EP2 – Intelligent NPCs with Inworld AI Integration

### Story EP2-S1 – As a player, I hold a text conversation with an NPC that stays in character
- Author Inworld personas and wire up a FastAPI relay that preserves session context.
- Surface dialogue through chat UI or in-world bubbles with typing indicators and error fallbacks.
- Calibrate personas/guardrails so responses stay lore-aligned and concise.
- Funnel NPC-initiated world changes back through the governor so laws can approve or refuse them.
- Acceptance: multi-turn conversations reference prior exchanges and respect persona constraints.

### Story EP2-S2 – (Future) As a player, I hear voiced NPC replies and see their animations react
- Layer TTS playback, spatial audio, and simple talk animations on top of Story EP2-S1.
- Map emotion metadata to gestures or expressions; consider STT for player input.
- Acceptance: demo conversation where NPC speech, animation, and audio timing remain in sync.

## Epic EP3 – Asset Styling and Enhancement with Scenario AI

### Story EP3-S1 – As an art director, I restyle generated props so they match Eternia’s visual language
- Train or select a Scenario model representing the target art direction.
- Pipeline Scenario outputs into runtime material swaps for web and Unreal clients.
- Cache+monitor styling runs, allowing asynchronous updates when AI assets finish processing.
- Notify the governor of styling-driven physics/material changes and respect any law vetoes.
- Acceptance: before/after comparison shows consistent style application across at least three prop types.

### Story EP3-S2 – As a content designer, I batch-produce themed decor and UI assets in one pass
- Script Scenario batch prompts that yield coherent sets of images/textures.
- Import curated outputs into placement tools or UI kits with minimal manual cleanup.
- Document repeatable steps so non-engineers can regenerate sets as art direction evolves.
- Demonstrate batch placement adheres to density/zone laws via recorded enforcement events.
- Acceptance: populate a showcase area with a themed asset set generated in a single workflow.

## Epic EP4 – Full Environment Generation with Marble (World Labs)

### Story EP4-S1 – As a developer, I explore a Marble-generated environment directly inside Eternia
- Secure Marble access, collect splat outputs, and render them through Spark in the Three.js client.
- Provide controls for prompting, loading, and navigating scenes; capture performance notes.
- Outline Unreal integration research options (conversion, point cloud shaders, WebXR bridge).
- Gate environment swaps through the governor, logging law approvals or rejections.
- Acceptance: recorded walkthrough of two distinct Marble prompts rendered in the client with navigation.

### Story EP4-S2 – As a developer, I save standout AI worlds and reload them later
- Persist Marble splat outputs with metadata, previews, and catalog browsing.
- Rehydrate stored worlds on demand via Spark; plan Unreal parity as APIs mature.
- Store law-compliance status with each world and prevent reloads once a governing rule disallows them.
- Acceptance: demonstrate save/load cycle surviving server restarts for multiple generated environments.

---

**Working agreements**
- Stories remain definition-of-done only when related checkboxes in `docs/tasks.md` are complete and tests/docs are merged.
- Capture deviations or blocked subtasks in `docs/implementation_notes.md` and raise follow-up issues tagged with the corresponding story code.
