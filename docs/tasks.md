# Eternia UE Roadmap Tasks

This document tracks the prioritized tasks for the Eternia UE5.6 initiative. Each item maps to an epic/story pairing
from the Genesis Valley delivery plan. Check off tasks as work completes and note any deviations or waivers in
`docs/implementation_notes.md`.

## Epic A — Project skeleton & performance budget (Day 0–1)
**Acceptance**: Fresh clone < 25 GB; project opens on Mac and plays third-person template at ≥30 FPS.

### Story A1 — Minimal UE project shell
- [ ] A1.1 Install Unreal Engine 5.6 (Editor only) on Mac, excluding optional extras.
- [ ] A1.2 Create a new project: Games → Third Person → Blueprint; disable Ray Tracing during setup.
- [ ] A1.3 Enable Nanite, Lumen (Software), and Virtual Texture Streaming; set scalability preset to High.
- [ ] A1.4 Audit plugins and enable only those required now (MetaHuman, Mass AI, Behavior Tree, EQS, Pixel Streaming as justified).

### Story A2 — Disk footprint controls
- [ ] A2.1 Delete unused Starter Content assets from the new project.
- [ ] A2.2 Configure Derived Data Cache to a custom path with a 30–40 GB cap.
- [ ] A2.3 Set Texture Streaming pool size to ~1–1.5 GB and enable Streamable Mips on large textures.
- [ ] A2.4 Adopt Git hygiene: extend `.gitignore` and configure Git LFS for `/Content/**/Textures/**`, `/Content/**/Meshes/**`, `/Saved`, `/Intermediate`.

### Story A3 — Repo layout & validation
- [ ] A3.1 Create the UE project structure: `EterniaUE/` root with `Content/Worlds/GenesisValley`, `Content/AI/Companions/{BT,BB,EQS}`, `Content/MetaHumans/Firstborns`, and `Content/Blueprints/{Player,Interact,Systems}`.
- [ ] A3.2 Sync plan and setup notes into `docs/implementation_notes.md` and reference this checklist.
- [ ] A3.3 Verify clean clone size stays under 25 GB (excluding DDC/LFS pulls) and document measurement.
- [ ] A3.4 Launch the project on target Mac hardware, confirm ≥30 FPS in the third-person template, and capture evidence.

## Epic B — Genesis Valley environment (Day 2–3)
**Acceptance**: Walkable valley (navmesh built), dream-grade lighting, 60–90 sec camera path looks teaser-ready.

### Story B1 — Sky & lighting
- [ ] B1.1 Place SkyAtmosphere, Movable Directional Light, Sky Light (real-time capture), and Exponential Height Fog with volumetric fog enabled.
- [ ] B1.2 Add an unbound Post Process Volume with filmic LUT, bloom, subtle chromatic aberration, and warm god-ray feel.
- [ ] B1.3 Capture lighting reference shots and record settings in implementation notes.

### Story B2 — Terrain & sacred focal point
- [ ] B2.1 Sculpt the valley and ridge layout within Genesis Valley world partition.
- [ ] B2.2 Kitbash a temple/altar focal point using free or low-poly assets (document sources).
- [ ] B2.3 Run a PCG pass for sparse olive trees, pillars, and flags; configure LODs and enable Nanite where available.

### Story B3 — Time-of-day & ritual VFX
- [ ] B3.1 Implement `TimeOfDay_BP` blueprint with timeline driving the sun angle on a ~5 minute loop.
- [ ] B3.2 Author particle ribbons for ritual wind and hook an audio cue for day→night transition.
- [ ] B3.3 Bake navmesh, author a 60–90 second cinematic camera path, and review the captured flythrough.

## Epic C — Explorer experience (Day 3)
**Acceptance**: Player can walk, look, interact, and trigger one visible ritual effect.

### Story C1 — Player tuning
- [ ] C1.1 Customize the third-person character with a slower, cinematic spring arm and camera settings.
- [ ] C1.2 Map input actions: Move, Look, Interact (E), Ritual (R) using Enhanced Input or Input Mapping Context.
- [ ] C1.3 Playtest traversal to confirm responsive movement without nausea; log adjustments.

### Story C2 — Interaction & ritual
- [ ] C2.1 Build an `InteractComponent` with line trace highlighting for usable actors (e.g., temple brazier, banner).
- [ ] C2.2 Implement ritual action that triggers a world modifier (warm color grade + music layer for 30 s).
- [ ] C2.3 Validate interaction flow end-to-end and capture a short demo clip.

## Epic D — Firstborn companions (Day 4–6)
**Acceptance**: ≥3 companions wander, greet the player, converse, enter Dormant instead of dying, and persist state across runs.

### Story D1 — Data model & lifecycle
- [ ] D1.1 Create `CompanionState` data asset schema: Name, BirthTick, GrowthLevel, Energy, Bonds[], StateEnum {Awake, Dormant, Pilgrimage}.
- [ ] D1.2 Implement SaveGame slot with autosave every 60 s and on exit; restore states on BeginPlay.
- [ ] D1.3 Replace death mechanics with Dormant state transitions including cocoon/prayer pose and auto-wake logic.

### Story D2 — AI stack
- [ ] D2.1 Build `AIController_BP`, Blackboard (TargetLoc, PlayerActor, FriendActor, Energy, State), and Behavior Tree (Dormant wait selector vs wander sequence).
- [ ] D2.2 Add services that tick energy down, greet near player, and converse near friends; ensure EQS `Find Random Reachable Point (radius 800–1200)` drives movement.
- [ ] D2.3 Configure AI Perception (Sight/Hearing) to notice player and companions; tune sensing ranges.
- [ ] D2.4 Simulate multi-companion behavior in PIE and record observations.

### Story D3 — Growth & bonds
- [ ] D3.1 Track bond increments after successful conversations between companions.
- [ ] D3.2 Promote GrowthLevel after thresholds of bonds/rituals; adjust patrol radius and idle animations accordingly.
- [ ] D3.3 Expose debug visuals or logs to review growth and bond metrics.

### Story D4 — MetaHuman integration
- [ ] D4.1 Create two optimized MetaHumans with lightweight LODs (hair cards only if budget permits).
- [ ] D4.2 Build additional companions using a lightweight shared skeleton rig.
- [ ] D4.3 Validate full companion roster performance and persistence in packaged builds.

## Epic E — Sound & vibe (Day 6)
**Acceptance**: Audible shift at day→night cycle and during ritual overlay.

### Story E1 — Adaptive ambience
- [ ] E1.1 Source/create audio assets: ambient bed (wind/desert choir), ritual layer (low drums), spot SFX (banners/torches).
- [ ] E1.2 Implement volume-based mixing so proximity to the temple scales choir intensity and ritual triggers add drums.
- [ ] E1.3 Test audio transitions across day/night and ritual states, adjusting mix levels to avoid clipping.
- [ ] E1.4 Document audio routing and assets for future updates.

## Epic F — Remote GPU build & Pixel Streaming (Day 7–8)
**Acceptance**: Shareable URL streams Windows build; user can walk Genesis Valley with audio/video intact; total GPU spend ≤ $60.

### Story F1 — Windows packaging readiness
- [ ] F1.1 Update Project Settings → Platforms → Windows: target D3D12, disable Ray Tracing, set build to Shipping.
- [ ] F1.2 Disable unused plugins ahead of packaging to reduce build size.

### Story F2 — Remote GPU provisioning
- [ ] F2.1 Evaluate rental options (cost vs specs) and book a Windows Server VM with recent NVIDIA GPU.
- [ ] F2.2 Install NVIDIA drivers and UE 5.6; clone the repo via Git LFS; document setup checkpoints.
- [ ] F2.3 Track session time to enforce 6–10 hour budget; shut down VM when idle.

### Story F3 — Pixel Streaming pipeline
- [ ] F3.1 Enable Pixel Streaming plugin and package the project for Windows (Shipping configuration).
- [ ] F3.2 Launch UE signalling web server and configure packaged build with Pixel Streaming flags pointing to the server.
- [ ] F3.3 Open stream URL in Safari/Chrome on Mac, verify controls, latency, and audio/video quality; capture test log.

### Story F4 — Cost hygiene & monitoring
- [ ] F4.1 Set bitrate (2–6 Mbps) and resolution (1280×720/1600×900) for stable streaming at target costs.
- [ ] F4.2 Maintain a run log with start/stop times, bandwidth usage, and spend estimates.
- [ ] F4.3 Confirm VM shutdown after tests and document teardown steps for repeatability.

## Epic G — Web teaser (optional, Day 9)
**Acceptance**: Lightweight teaser link available without GPU session.

### Story G1 — Teaser creation
- [ ] G1.1 Decide between offline camera path render and lightweight Babylon.js/three.js scene.
- [ ] G1.2 Produce 30–60 second render or interactive web scene asset; ensure file size stays manageable.
- [ ] G1.3 Host teaser asset and provide link referencing Pixel Streaming demo when live.
- [ ] G1.4 Update docs with teaser publishing steps and refresh schedule.

## Epic H — Storage & performance guardrails (continuous)
**Acceptance**: Project + DDC + assets remain < ~150 GB, runtime fits within 24 GB RAM target.

### Story H1 — Continuous optimization
- [ ] H1.1 Track cumulative storage usage (project, DDC, packaged builds) and surface warnings approaching 150 GB.
- [ ] H1.2 Favor free/low-poly assets initially; log swaps to higher fidelity assets with rationale.
- [ ] H1.3 Evaluate World Partition or level streaming needs as Genesis Valley expands; document decisions.
- [ ] H1.4 Purge `/Saved/Cooked` and stale DDC data before archiving builds; script clean-up if needed.
- [ ] H1.5 Log memory usage and performance profiles during playtests to confirm 24 GB RAM comfort zone.

## One-sitting checklists

### UE settings baseline
- [ ] Verify Nanite enabled for frequently used static meshes.
- [ ] Confirm Lumen GI/Reflections set to Software.
- [ ] Ensure Virtual Texture Streaming is ON.
- [ ] Set scalability preset to High.
- [ ] Keep Texture Pool Size at ~1000–1500 MB.

### Companion AI minimal loop
- [ ] Blackboard keys present: `TargetLoc` (Vector), `PlayerActor` (Object), `FriendActor` (Object), `Energy` (Float 0–100), `State` (Enum).
- [ ] Behavior Tree: Root → Selector (Dormant? → Wait; else → Sequence {EQS RandomPoint, MoveTo, Idle/Greet}).
- [ ] Service every 2 s: decrement Energy by rate*dt; if <20 set State=Dormant; when ≥80 return to Awake.

### Persistence sanity pass
- [ ] On BeginPlay load SaveGame data and apply to each companion.
- [ ] Timer every 60 s writes SaveGame and on exit flush state.

### Pixel Streaming quick run
- [ ] Package Windows (Shipping) build.
- [ ] Start signalling server.
- [ ] Launch packaged exe with Pixel Streaming flags.
- [ ] Open streaming URL in browser and smoke test controls/audio.
