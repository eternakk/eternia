# Eternia UE Roadmap Tasks

This document tracks the prioritized tasks for the Eternia UE5.6 initiative. Each item maps back to an epic/story from
the Genesis Valley delivery plan. Check off tasks as work completes and log deviations or waivers in
`docs/implementation_notes.md`.

## Epic A1′ — First-person project skeleton (Day 0–1)

**Acceptance**: Fresh clone < 25 GB; first-person template runs ≥30 FPS on target Mac hardware.

### Tasks

- [ ] A1′.1 Install Unreal Engine 5.6 (Editor only) on Mac, skipping optional extras.
    - [x] Verify disk headroom (≥120 GB free) and document path used for UE installation.
    - [x] Capture the installed components list (Editor only) for implementation notes.
- [x] A1′.2 Create a new project: Games → First Person → Blueprint with Ray Tracing OFF.
    - [x] Create project under `EterniaUE/` directory and confirm it opens without starter content warnings.
    - [x] Record engine version, template settings, and default map in implementation notes.
- [x] A1′.3 Enable only required systems: Enhanced Input, Behavior Tree, EQS, Mass AI, Lumen (Software), Nanite, Virtual
  Textures, Pixel Streaming (for later).
    - [x] Audit default plugin list and disable any extras before first commit.
    - [x] Export list of enabled plugins/settings to include in documentation.
- [x] A1′.4 Set editor performance baselines: scalability preset High; Texture Pool ≈ 1–1.5 GB; Derived Data Cache
  capped 30–40 GB at custom path.
    - [x] Configure DDC path outside repo (e.g., `~/Library/Application Support/Unreal Engine/DDC_Eternia`) and note
      cap.
    - [x] Capture screenshots or textual confirmation of scalability/texture pool settings for notes.
- [x] A1′.5 Configure repo hygiene: extend `.gitignore`, add Git LFS for `/Content/**/Textures/**`,
  `/Content/**/Meshes/**`, `/Saved`, `/Intermediate`; confirm post-commit project size < 25 GB.
    - [x] Update root `.gitignore` with UE-specific exclusions (`Binaries/`, `DerivedDataCache/`, `Saved/`, etc.).
    - [x] Add `.gitattributes` entries for UE assets (`*.uasset`, `*.umap`, texture/mesh directories).
    - [x] Run `git lfs install` / `git lfs track` locally to ensure filters apply before committing new binaries.
    - [x] Document repo size measurement (fresh clone + initial commit) in implementation notes.

## Epic B — Genesis Valley environment (Day 2–3)

**Acceptance**: Walkable first-person level with evocative lighting and baked navmesh.

### Tasks

- [ ] B.1 Place SkyAtmosphere, Movable Directional Light, Sky Light (real-time capture), and Exponential Height Fog with
  volumetric fog enabled.
- [ ] B.2 Add an unbound Post Process Volume with warm LUT, bloom, slight chromatic aberration, and gentle god-rays.
- [ ] B.3 Sculpt valley + ridge layout and kitbash temple/altar focal point using free/low-poly assets; document
  sources.
- [ ] B.4 Run a PCG pass for sparse olive trees, pillars, and flags; configure LODs and enable Nanite where available.
- [ ] B.5 Implement `TimeOfDay_BP` with ~5 minute loop driving sun angle; author ritual VFX (ribbons/embers) and an
  audio cue.
- [ ] B.6 Bake navmesh, validate walkable area from first-person perspective, and capture lighting reference shots.

## Epic C′ — Explorer embodiment (Day 1–2)

**Acceptance**: Player can walk, look, and interact with at least one world object in first person.

### Tasks

- [ ] C′.1 Tune camera: FOV 90°, minimal head-bob (~1 cm) with toggle option.
- [ ] C′.2 Adjust `CharacterMovement` realism: Walk 150 cm/s, Jog 350 cm/s, Accel/Decel 2048→1200; disable jump or set
  low `JumpZVelocity`.
- [ ] C′.3 Implement crouch toggle with smooth camera height interpolation.
- [ ] C′.4 Configure Enhanced Input mappings: Move, Look, Interact (E), Ritual (R), Inspector (Tab), Freecam (F1).
- [ ] C′.5 Build `InteractComponent` with forward line trace, highlight outline, and “Press E” prompt.
- [ ] C′.6 Playtest traversal/interaction; log comfort tweaks and responsiveness adjustments.

## Epic D — Firstborn companions (Day 3–5)

**Acceptance**: 3–6 companions wander, greet, converse, enter Dormant (not dead), and persist across runs.

### Tasks

- [ ] D.1 Author `CompanionState` DataAsset: Name, BirthTick, GrowthLevel, Energy, Bonds[], State {Awake, Dormant,
  Pilgrimage}.
- [ ] D.2 Implement SaveGame slot with autosave every 60 s and on exit; restore companion state on BeginPlay.
- [ ] D.3 Replace death mechanics with Dormant flow: cocoon/prayer pose, AI paused, auto-wake when Energy ≥ threshold.
- [ ] D.4 Build AI stack: `AIController`, Blackboard (TargetLoc, PlayerActor, FriendActor, Energy, State), Behavior
  Tree (Selector → Dormant Wait 20–60 s / Sequence {EQS random point (radius 800–1200), MoveTo, idle/social}).
- [ ] D.5 Add services: energy drain, greet player when nearby, converse when near friend (synced idles); configure AI
  Perception Sight/Hearing ranges.
- [ ] D.6 Track GrowthLevel increments after N socials/rituals; expand patrol radius and idle sets accordingly; expose
  debug readouts.
- [ ] D.7 Create two lightweight MetaHumans (trim LODs/hair) plus 1–4 companions on shared lightweight skeleton;
  validate performance and persistence.

## Epic I — Sandbox Inspector HUD (Day 4–6)

**Acceptance**: Press Tab to open live state inspector; HUD actions mutate the world and reflect backend responses.

### Tasks

- [ ] I.1 Design UMG Inspector HUD toggled with Tab; tabs: World (time-of-day, modifiers, weather), Companions (Energy,
  GrowthLevel, top Bonds), Events (rolling 100 entries), Actions (ritual trigger, spawn companion, toggle Dormant).
- [ ] I.2 Implement local backend endpoints (or mocks): `GET /world/state`, `GET /companions`, `GET /events`,
  `POST /actions/*` for rituals/spawns/dormant toggles.
- [ ] I.3 Integrate UE HTTP/WebSocket polling (1–2 Hz with debounce); parse JSON into `WorldState_BP` as single source
  of truth shared with gameplay.
- [ ] I.4 Bind HUD widgets to `WorldState_BP` properties; surface errors and stale-data indicators.
- [ ] I.5 Wire action buttons to POST endpoints; upon success update gameplay + HUD; handle failures with user feedback
  and retries.
- [ ] I.6 Document bridge setup, endpoint contracts, and Blueprint polling graphs in implementation notes.

## Epic J — Physics & “feelings” baseline (Day 6)

**Acceptance**: Movement feels grounded, ritual shifts mood audibly/visually, `PainGovernor` slider drives vignette
intensity.

### Tasks

- [ ] J.1 Maintain default gravity (~9.81 m/s²); tune physical materials for realistic friction/restitution on ground
  and stone.
- [ ] J.2 Disable motion blur; keep lens flare low; bind vignette intensity to `PainGovernor` (0–1) for future
  modulation.
- [ ] J.3 Layer audio: footsteps, ambient wind bed, ritual drum layer triggered by modifier; balance levels to avoid
  clipping.
- [ ] J.4 Playtest mood transitions and record baseline metrics (FPS, audio mix, vignette response) for future tuning.

## Epic E — Sound & vibe (Day 6)

**Acceptance**: Audible shift during day→night cycle and ritual overlay.

### Tasks

- [ ] E.1 Source or create audio assets: ambient bed (wind/desert choir), ritual layer (low drums), spot SFX (
  banners/torches).
- [ ] E.2 Implement volume-based mixing so proximity to the temple scales choir intensity and ritual triggers add drums.
- [ ] E.3 Test audio transitions across day/night and ritual states; adjust mix levels to avoid clipping.
- [ ] E.4 Document audio routing, cue assets, and mixing notes for future updates.

## Epic F — Remote GPU build & Pixel Streaming (Day 7–8)

**Acceptance**: Streamed Windows build (1280×720 @ 2–6 Mbps) accessible via URL; Inspector works; GPU spend ≤ $60.

### Story F1 — Windows packaging readiness

- [ ] F1.1 Update Project Settings → Platforms → Windows: target D3D12, disable Ray Tracing, set build to Shipping.
- [ ] F1.2 Disable unused plugins ahead of packaging to reduce build size.

### Story F2 — Remote GPU provisioning

- [ ] F2.1 Evaluate rental options and book hour-capped Windows Server VM with recent NVIDIA GPU.
- [ ] F2.2 Install NVIDIA drivers and UE 5.6; clone repo via Git LFS; document setup checkpoints.
- [ ] F2.3 Track session time to enforce ≤10 hour budget; shut down VM when idle.

### Story F3 — Pixel Streaming pipeline

- [ ] F3.1 Enable Pixel Streaming plugin and package project for Windows (Shipping configuration).
- [ ] F3.2 Launch signalling web server; run packaged app with Pixel Streaming flags targeting the server.
- [ ] F3.3 Open stream URL in Safari/Chrome on Mac; verify controls, latency, audio/video, Inspector updates; capture
  test log.

### Story F4 — Cost hygiene & monitoring

- [ ] F4.1 Set bitrate 2–6 Mbps and resolution 1280×720 or 1600×900 for smooth streaming within budget.
- [ ] F4.2 Maintain run log (start/stop times, bandwidth, spend estimates).
- [ ] F4.3 Confirm VM shutdown after each session and document teardown steps for repeatability.

## Epic G — Web teaser (optional, Day 9)

**Acceptance**: Lightweight teaser link available without GPU session.

### Story G1 — Teaser creation

- [ ] G1.1 Decide between offline camera path render and lightweight Babylon.js/three.js scene.
- [ ] G1.2 Produce 30–60 second render or interactive web scene asset; ensure file size stays manageable.
- [ ] G1.3 Host teaser asset and provide link referencing Pixel Streaming demo when live.
- [ ] G1.4 Update docs with teaser publishing steps and refresh schedule.

## Epic H — Storage & performance guardrails (continuous)

**Acceptance**: Project + DDC + assets remain < ~150 GB; runtime fits within 24 GB RAM target.

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

- [ ] Blackboard keys present: `TargetLoc` (Vector), `PlayerActor` (Object), `FriendActor` (Object), `Energy` (Float
  0–100), `State` (Enum).
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

### Quick switch from third-person (if upgrading an existing project)

- [ ] Convert ThirdPerson character by adding head-mounted `CameraComponent`; remove spring arm.
- [ ] Hide third-person mesh in first-person view or plan full-body awareness upgrade.
- [ ] Rebind inputs via Enhanced Input; remove third-person camera lag.

### Recommended hotkeys

- [ ] WASD move
- [ ] Mouse look
- [ ] E Interact
- [ ] R Ritual
- [ ] Tab Inspector HUD
- [ ] F1 Freecam toggle
- [ ] F2 Photo mode pause

### Storage & RAM guardrails

- [ ] Prefer low/medium fidelity assets; document upgrades to higher fidelity with rationale.
- [ ] Trim MetaHuman LODs; keep active companions ≤6 until Mass expansion.
- [ ] Keep combined project + DDC + derived artifacts ≤ 120–150 GB; monitor usage regularly.
- [ ] Purge `/Saved/Cooked` and stale DDC before packaging or archiving builds.
- [ ] Validate runtime memory footprint stays within 24 GB during playtests.
