# Implementation Notes

This log captures day-to-day implementation context. The first section tracks the active prompt-based world generation roadmap sourced from `Implementation Roadmap_ Prompt-Based World Generation.pdf`. Legacy Unreal-first notes remain available in the archive section for historical reference.

## Current Roadmap — Prompt-Based World Generation

### Cross-epic coordination
- Secure and store external service credentials (`SLOYD_API_KEY`, `INWORLD_API_KEY`, `SCENARIO_API_KEY`, `MARBLE_API_TOKEN`) via `config/settings/*.yaml` or secrets manager; document rotation cadence in `docs/secure_coding_guidelines.md`.
- Establish shared storage conventions for generated artifacts (e.g., `artifacts/generated_models/`, CDN vs. local static hosting) with retention policies and cost tracking.
- Standardize world-state broadcast schemas so web, Unreal, and automation agents consume identical spawn/update payloads.
- Plan observability: instrument generation latencies, API costs, and error codes; feed metrics into the existing Prometheus stack for early anomaly detection.
- Thread every mutation path through `AlignmentGovernor` (event bus + policy callbacks) so laws can veto, rollback, or approve before state changes persist; expand tests around `LawEnforcedEvent`/`PolicyViolationEvent`.

### Epic EP1 — Integrate Sloyd for Prompt-Based 3D Asset Generation
#### Status summary
- Deliverables still in planning; no Sloyd API key or endpoint scaffolding checked in.
- Three.js client already has GLTF loading utilities we can extend; Unreal runtime import flow remains unproven.

#### Key technical notes
- Prefer Sloyd GLB output with Unreal-friendly axis configuration (`"unreal": {"zAxisUp": true}`) to minimize post-processing.
- Cache downloaded GLBs server-side to avoid repeated fetches and enable replay/undo; consider hashing prompt + template as cache key.
- Adopt `glTFRuntime` (or equivalent) for UE5 runtime imports; evaluate packaging/licensing implications before commit.
- Maintain idempotent world-state updates so repeated spawn events do not duplicate objects.

#### Near-term actions
- Request/obtain Sloyd API credentials and add placeholders in settings templates.
- Scaffold FastAPI endpoint (`POST /api/generate_model`) with schema validation and outbound request helper.
- Define WebSocket `spawn` message format and extend the web client to react to new object payloads.
- Prototype Unreal listener + GLB importer in a standalone branch to validate runtime performance.

#### Risks & dependencies
- Sloyd rate limits and prompt restrictions (no characters/vegetation) may require prompt sanitization and retry logic.
- Runtime GLB imports could cause frame hitches; may need background loading strategies or level streaming.
- Storage footprint of generated assets could grow quickly; must set cleanup policy early.

### Epic EP2 — Intelligent NPCs with Inworld AI Integration
#### Status summary
- No Inworld integration code exists yet; conversation systems currently limited to internal tooling.
- UI support for NPC chat is pending; will likely extend existing Mission Control interface.

#### Key technical notes
- Use Inworld Simple API for initial integration; retain session IDs to preserve conversation memory.
- Centralize dialogue transcripts for audit/compliance under `data/conversations/` or existing logging pipeline.
- Consider moderation/guardrails layer before forwarding player input to Inworld to prevent disallowed content.

#### Near-term actions
- Author first wave of NPC personas in the Inworld portal and export identifiers.
- Implement backend relay endpoint with structured error responses and telemetry.
- Design chat UI mock (web first) featuring typing indicators and fallback messaging; plan VR HUD parity later.

#### Risks & dependencies
- API latency may exceed realtime thresholds; evaluate streaming responses or optimistic UI cues.
- Persona drift requires fast iteration on Inworld configurations; budget time for tuning.
- Voice/animation roadmap (Story EP2-S2) depends on asset availability and animation pipeline maturity.

### Epic EP3 — Asset Styling and Enhancement with Scenario AI
#### Status summary
- No Scenario credentials configured; styling pipeline remains aspirational.
- Need curated concept art set to train or fine-tune Scenario models.

#### Key technical notes
- Use Scenario to generate textures or style overlays that align with Sloyd UV maps; store outputs with versioning for rollback.
- Apply textures asynchronously: spawn object immediately, then swap material when styled asset arrives.
- Capture prompts, seeds, and model versions for reproducibility in `artifacts/scenario/runs.json`.

#### Near-term actions
- Pick target art direction and assemble 15–30 reference images for Scenario training or selection.
- Prototype Scenario API call inside a background task worker to avoid blocking generation loop.
- Extend rendering layer (web + Unreal) with hot-reload capability for materials sourced from disk or HTTP.

#### Risks & dependencies
- Quality variance may require manual curation; plan for human review before assets ship to production worlds.
- Texture licensing and input data rights must be vetted to avoid contaminating proprietary styles.
- Scenario API costs can escalate with batch generation; cache aggressively and monitor usage.

### Epic EP4 — Full Environment Generation with Marble (World Labs)
#### Status summary
- Marble access pending; integration blocked until beta credentials confirmed.
- Spark renderer not yet integrated into the Three.js client.

#### Key technical notes
- Marble outputs Gaussian splats; rely on World Labs’ Spark library to visualize in browsers/VR.
- Large splat datasets (100+ MB) require streaming or progressive loading strategies to avoid main-thread stalls.
- Unreal rendering may need R&D (point-cloud shader or WebXR bridge) before production viability.

#### Near-term actions
- Request Marble beta access and confirm SDK/API availability.
- Create isolated Spark proof-of-concept in the web client reading sample splat data.
- Design developer UI for prompt submission, load progress, and scene toggling between canonical and AI-generated spaces.
- Draft persistence schema for saving Marble outputs with metadata and optional thumbnails.

#### Risks & dependencies
- Platform access or licensing terms could delay delivery; maintain fallback plan focused on Sloyd + Scenario.
- Performance on lower-end devices (or VR headsets) may require aggressive level-of-detail tuning.
- Storage and bandwidth costs for splat assets could be significant; evaluate CDN or cold storage options.

---

## Legacy Unreal Roadmap (Epics A1′–H)

### Epic A1′ — First-person project skeleton

### Current state analysis
- First-person Unreal project now lives under `EterniaUE/` (Blueprint template). Ray tracing is disabled in `Config/DefaultEngine.ini`, curated plugins are pinned in `.uproject`, and the Derived Data Cache now points to an external path.
- Root `.gitignore` now includes Unreal-specific exclusions (`Binaries/`, `DerivedDataCache/`, `Saved/`, etc.), and `.gitattributes` plus Git LFS tracking cover `.uasset`/`.umap` and heavy texture/mesh directories. Local Git LFS hooks installed (`git lfs install` on 2025-10-07).
- Documentation still needs the UE 5.6 installation footprint (install path, component list) and a confirmed Derived Data Cache location; `docs/notes_epic_a1_integration.md` targets the old third-person scope.
- Backend tooling (Python/Node) will coexist with UE assets, so we must ensure large binaries stay out of standard git
  history to protect repo size budgets (<25 GB target).

### Planned changes & touchpoints
1. **UE 5.6 Installation (A1′.1)**
   - Confirm at least 120 GB free disk before installing; document install path and the Editor-only component list.
   - Capture installer metadata (version, build number) for traceability.
2. **Project creation (A1′.2)**
   - Generate a First Person Blueprint template under `EterniaUE/` with Ray Tracing disabled during project wizard.
   - Record default map, target hardware settings, and initial content selections.
3. **Plugin and system curation (A1′.3)**
   - Enable only the UE 5.6 equivalents: Enhanced Input, Gameplay Behavior Tree & EQS editors, MassEntity + MassAI suite,
     Lumen Global Illumination & Reflections (set to *Software*), Virtual Shadow Maps, Virtual Texture Streaming. Keep the
     Pixel Streaming plugin installed but disabled until Epic F to avoid extra editor startup cost.
   - Export the enabled plugin/rendering snapshot (Markdown or screenshot). UE 5.6 relocates most Rendering toggles under
     *Project Settings → Engine → Rendering*, so capture that layout for future audits.
4. **Performance baselines (A1′.4)**
   - Set scalability preset to High, Texture Pool ≈ 1–1.5 GB, and store the Derived Data Cache outside the repo with a
     30–40 GB cap (e.g., `~/Library/Application Support/Unreal Engine/DDC_Eternia`).
   - Document configuration steps and include console commands/config sections needed to reproduce settings.
5. **Repo hygiene (A1′.5)**
   - Extend `.gitignore` with Unreal folders (`Binaries/`, `DerivedDataCache/`, `Intermediate/`, `Saved/`, project
     workspace files, generated build info).
   - Introduce `.gitattributes` and run `git lfs track` for `/Content/**/Textures/**`, `/Content/**/Meshes/**`, and other
     heavy asset directories; keep `Saved/` and `Intermediate/` ignored via `.gitignore` to prevent accidental commits.
   - After the initial commit, measure repo size (fresh clone without DDC) and note the value here.

### Open questions / dependencies
- Need confirmation on preferred storage location for shared DDC (default per-user vs shared network path).
- Determine whether Pixel Streaming plugin should remain disabled until Epic F work, or enabled upfront for
  configuration parity.
- Verify whether CI/CD workflows require adjustment to skip UE directories (current pipelines assume Python/Node
  projects only).

### Deliverables
- Updated `docs/tasks.md` with sub-task checklist (complete).
- `.gitignore` and `.gitattributes` changes once UE project scaffolded.
- Recorded installation + configuration evidence attached to this document as plaintext references or screenshot paths.

### Execution log
- 2025-10-06: Verified disk headroom via `df -h ~` (≈294 GiB free) — sufficient for UE 5.6 Editor install; logged path
  `/System/Volumes/Data` as mount reference.
- 2025-10-06: Added Unreal-specific exclusions to root `.gitignore` (Binaries, Intermediate, DerivedDataCache, Saved,
  VS workspace artifacts) to prevent transient files from entering git history.
- 2025-10-06: Created repository `.gitattributes` with Git LFS filters for `.uasset`, `.umap`, and texture/mesh
 directories; run `git lfs install` locally before adding new binary assets.
- 2025-10-06: Attempted `git lfs install`; command failed because Git LFS was not yet installed. Resolved on 2025-10-07 after installing Git LFS via Homebrew.
- 2025-10-07: Installed Git LFS via Homebrew and ran `git lfs install`; tracked `.uasset`/`.umap` plus texture/mesh directories to ensure large assets remain outside normal Git history.
- 2025-10-07: Recorded UE 5.6 Editor install components: Core Components (36.20 GB), Starter Content (641.71 MB), Templates & Feature Packs (792.17 MB), Editor Symbols for Debugging (126.22 GB).
- 2025-10-07: Created `EterniaUE` First Person Blueprint project (Ray Tracing disabled, Starter Content skipped). Default map `Lvl_FirstPerson` retained; project name updated to EterniaUE. EngineAssociation 5.6 recorded in `.uproject`; Config/Content ready for plugin audit.
- 2025-10-07: Plugin curation snapshot — Enabled: EnhancedInput, BehaviorTreeEditor (Editor), EnvironmentQueryEditor (Editor), MassEntity, MassAI, GameplayStateTree, PixelStreaming (Win64 only). Disabled: ModelingToolsEditorMode.
- 2025-10-07: Derived Data Cache redirected to `/Users/klajdikolaj/Library/Application Support/Unreal Engine/DDC_Eternia` with 35 GB cap; created external directory and removed reliance on repo-local cache.
- 2025-10-07: Converted UE 5.6 to use project-local DDC via InstalledDerivedDataBackendGraph override; confirmed writes to `/Users/klajdikolaj/Library/Application Support/Unreal Engine/DDC_Eternia` (~168 MB after cook).
- 2025-10-07: Measured repo footprint excluding caches/node_modules via Python scan — ≈8.28 GiB (8,890,404,882 bytes); within <25 GB acceptance budget.

### UE 5.6 installation procedure (planned)
1. Download Epic Games Launcher (if not present) from https://www.unrealengine.com/en-US/download.
2. Within the launcher: Library → `+` → select **Unreal Engine 5.6**; choose **Options** and uncheck extras (e.g.,
   Starter Content, templates, target platforms) leaving only the **Editor** for macOS.
3. Set install location (default `/Users/Shared/Epic Games/UE_5.6`) and confirm available disk space ≥ forecasted 50–70
   GB usage.
4. After installation, record: engine version, install path, and installed components list; attach to this document under
   “Execution log”.

### First-person project scaffolding (planned)
1. Launch UE 5.6 → New Project → Games → **First Person** → Blueprint.
2. Disable Ray Tracing (Project Defaults step) and uncheck Starter Content.
3. Set project location to `<repo>/EterniaUE` and name project `EterniaUE` (ensures `.uproject` lives at repo root path `EterniaUE/EterniaUE.uproject`).
4. Open the project once created to validate shaders compile; note initial map (`FirstPersonMap`) and engine version in execution log.
5. Immediately save all and exit to keep initial content minimal.

### Plugin & system curation checklist (planned)
- Enabled plugins: `Enhanced Input`, `Gameplay Tasks`, `Behavior Tree`, `EQS`, `MassEntity`, `MassAI`, `Lumen`, `Nanite`, `Virtual Texture Tools`, `Pixel Streaming`.
- Disabled/unneeded (verify state): `StarterContent`, `Chaos Vehicles`, `Data Prep`, `Live Coding`, `Niagara` (unless required later).
- Export plugin list: `Edit → Plugins → Copy to Clipboard` (available via context menu) and paste snapshot in this document.

### Performance baseline configuration (planned)
1. `Settings → Engine Scalability Settings`: set preset to **High** and lock FPS to 60 for baseline testing.
2. `Project Settings → Rendering`: ensure Lumen Global Illumination/Reflections set to **Software**; enable Nanite and Virtual Texture Streaming.
3. `Project Settings → Engine → Rendering`: adjust Texture Streaming Pool to 1024–1536 MB (`r.Streaming.PoolSize=1200`).
4. `Project Settings → Derived Data Cache`: set to `Custom` path (recommend `~/Library/Application Support/Unreal Engine/DDC_Eternia`) and cap size via `MaxCacheSizeGB=35` in `Engine.ini`.
5. Capture console command confirmations (e.g., run `r.Streaming.PoolSize` in Output Log) for traceability.

### Post-skeleton repo checks (planned)
- Run `git lfs track 'EterniaUE/Content/**/*.uasset' 'EterniaUE/Content/**/*.umap'` after Git LFS installation. (Completed 2025-10-07.)
- Verify `git status` shows only `.uproject`, `Config/`, `Content/` base files (no `Binaries/`, `Intermediate/`, etc.).
- Measure clean repo size with `du -sh .` (excluding DDC) and log value; confirm <25 GB threshold.
- Pending: Run Unreal installer (Editor only), generate `EterniaUE` project, export enabled plugin list, configure DDC
  path, and document repo size after initial commit.

### Epic B — Genesis Valley environment

### Current state analysis
- Added Python editor automation at `EterniaUE/Content/Python/genesis_valley_setup.py` to seed the Genesis Valley level with required atmosphere, lighting, and post-process actors (tasks B.1–B.2).
- Script is idempotent: it creates `Content/GenesisValley/GenesisValley.umap` if missing, reuses existing actors by label, and safely reapplies lighting parameters.
- Post-process settings bias toward warm tones with subtle bloom, chromatic aberration, and light shafts to evoke ritual ambience without overpowering gameplay visibility.

### Execution steps
1. Launch UE 5.6, enable the Python Editor Script Plugin (if not already enabled), and open the EterniaUE project.
2. From the Python console or the Scripts dropdown, run:
   ```python
   import genesis_valley_setup
   genesis_valley_setup.main()
   ```
3. Confirm the new `GenesisValley` level loads with SkyAtmosphere, Movable Directional Light, Sky Light (real-time capture), Exponential Height Fog (volumetric on), and an unbound post-process volume.
4. Save the level (`File → Save Current Level`). Lighting can be previewed with `Build → Lighting Only` to validate tone.

### Task status & next steps
- **B.1, B.2** — Complete (2025-10-07) via `genesis_valley_setup.main()` automation; rerunnable for baseline lighting.
- **B.3 Landscape & focal point**
1. `B.3.a` Create landscape: Switch to **Landscape Mode** from the Select Mode dropdown (top-left, or press `Shift+2`). In
   the *Create* tab, target 63×63 sections (Section Size 63×63, 1 component), set Scale X/Y/Z = 100, assign `M_GenesisLandscape`, then click **Create Landscape**. Rename the actor to `GV_Landscape` in the Outliner.
2. `B.3.b` Sculpt `GV_Landscape`: With the *Sculpt* tab active, use Sculpt (strength 0.10–0.15, falloff 0.5) and `Ctrl+LMB`
   to carve the central basin (~60 m radius). Raise perimeter ridges using the same tab’s *Sculpt*/*Smooth* tools and
   establish a traversal channel leading to the altar terrace.
3. `B.3.c` Kitbash altar focal point: In Quixel Bridge grab free Megascans packs (*Ancient Ruins*, *Sandstone Blocks*, etc.), add to project, and assemble altar + plinth at basin apex (grid snap 10). Align entrance to player spawn.
4. `B.3.d` Asset log: Create "B.3 Asset Sources" subsection below capturing asset names, URLs, and placement notes (required for acceptance).
- **B.4 PCG foliage/props**
1. `B.4.a` Enable **Procedural Content Generation** (PCG) from `Edit → Plugins` (UE 5.6 merges the prior PCG Tools into this
   module). Restart if prompted, then create `Content/GenesisValley/PCG/PCG_GenesisProps` via *Add → PCG → PCG Graph*.
2. `B.4.b` Graph setup: use *Landscape Data* (Target Actor = `Self`) feeding a *Surface Sampler* (`Sampling Method = Raycast`,
   `Slope Angle (Max) = 15°`, `Min Hit Normal Z = 0.85`). Route the sampled points into a *Bounds Filter* (Sphere radius 600 uu
   around the temple) and branch to individual *Static Mesh Spawner* nodes for olive trees (`SM_OliveTree_01`, density
   0.0008/m²), stone pillars (`SM_Ruins_Pillar_02`, max count 6, seed 42), and flags (`SM_Flag_Cloth`, align to tangent).
   Drive the flag branch with a *Spline Data* node referencing the manually drawn `GV_ProcessionalPath`. Expose parameters
   (`TreeDensity`, `PillarRadius`, `FlagSpacing`, `SeedOffset`) using 5.6's **Create Parameter** context menu so runtime
   systems can override them.
3. `B.4.c` Instantiate graph: drag `PCG_GenesisProps` into the level to spawn a PCG Component. Leave **Processing Mode** = `On Demand` while tuning, set **Target Actor** to `GV_Landscape`, bind the processional spline via **User Parameters**, then click **Regenerate** to preview instances. Select each spawned mesh in the Content Browser, enable Nanite (where supported), and review LOD screen sizes (target 0.5 base). Validate viewport performance with `stat fps` (≥60 on baseline Mac).
4. `B.4.d` Capture screenshots of graph layout + density settings; save to `artifacts/genesis_valley/pcg/`.
5. See `docs/genesis_valley_pcg.md` for the full branching recipe, parameter defaults, and perf checklist. Expose PCG graph
   parameters (`TreeDensity`, `PillarRadius`, `FlagSpacing`, `SeedOffset`) so Eternia’s backend/world-state bridge can adjust
   scatter patterns when we start piping simulation data into Unreal.
- **B.5 Time of Day & ritual cues**
  1. `B.5.a` Blueprint drop-in: In `Content/GenesisValley/Blueprints`, create `TimeOfDay_BP` (Actor) referencing `GV_SunLight`, Niagara components, and ritual audio cue.
  2. `B.5.b` Timeline `SunCycle` (300 s loop) with `SunPitch` curve (0→65→-8). On update rotate sun; expose `LoopDuration` multiplier and `DefaultSunYaw`.
  3. `B.5.c` Niagara/audio: add `NS_RitualRibbons` & `NS_EmberBurst` (Auto Activate off). Timeline event at 240 s activates Niagara and plays `GV_Ritual_Cue` via `AudioComponent`. Document parameters for reuse.
  4. `B.5.d` Expose variables (`LoopDuration`, `DefaultSunYaw`, `RitualTriggerTime`, `RitualCueVolume`). Provide `SetRitualActive(bool)` helper; capture blueprint screenshots for notes.
- **B.6 Navigation & validation**
  1. `B.6.a` Place `NavMeshBoundsVolume` covering valley floor (X/Y 12000, Z 2000). Set runtime generation to *Dynamic Modifiers Only*.
  2. `B.6.b` Build Paths and preview with `P`. Add Nav Modifier on temple steps if needed; adjust `Agent Radius` to 34.
  3. `B.6.c` Run 60–90 s first-person walk (PIE) across valley, ridges, and altar. Note trouble spots and log adjustments here.
  4. `B.6.d` Capture dawn/noon/dusk screenshots (adjust `RitualTriggerTime` to 60/150/240). Store in `artifacts/genesis_valley/lighting/` with consistent filenames.

### Deliverables
- `EterniaUE/Content/Python/genesis_valley_setup.py` (automation for tasks B.1 & B.2).
- Saved `GenesisValley` level asset after script execution.
- Screenshots and metrics post-script (pending capture once lighting validated).

### Execution log
- 2025-10-07: Authored Python automation for tasks B.1–B.2 ensuring repeatable lighting baseline for Genesis Valley level.
- 2025-10-08: Marked B.1–B.2 complete, outlined B.3–B.6 subtasks with UE editor instructions and documentation checkpoints.
- 2025-10-08: Relocated raw Megascans downloads (Ground Gravel, Japanese Shrine Stairs, Roman Column, Mossy Cliff) to `EterniaUE/SourceAssets/Megascans/` for clean Content hierarchy prior to import.

### B.3 Asset Sources (to fill once placed)
- _Example_: Quixel Megascans `Ancient Ruins Pillar (ID XXXXX)`, used for altar columns.
- _Example_: Quixel Megascans `Sandstone Block (ID YYYYY)`, forming altar base.

### Epic C′ — Explorer embodiment

### TODOs
- Locomotion polish: tune FOV (90°), head-bob curve (~1 cm amplitude with toggle), walk/jog speeds (150/350 cm/s), crouch interpolation.
- `InteractComponent`: forward line trace, outline material parameter, press-E prompt widget; integrate with Enhanced Input mapping.
- Document comfort tweaks after 5-minute playtest.

### Epic D — Firstborn companions

### TODOs
- Pipeline: author `CompanionState` DataAsset → SaveGame persistence → lightweight AIController + Blackboard → placeholder Behavior Tree + EQS loop.
- Services: energy drain, greet when player proximity, idle conversations. Configure AI Perception (Sight 2000, Hearing 1200 default).
- Growth tracking: bump `GrowthLevel` after N socials/rituals; expose debug widget.
- Character fidelity: target 2 MetaHumans + 1–4 companions on shared skeleton; note performance impact.

### Epic I — Sandbox Inspector HUD

### TODOs
- Build HUD tabs (World/Companions/Events/Actions) backed by mock endpoints, then flip to local backend once stable.
- Polling layer: HTTP/WebSocket hybrid updating `WorldState_BP`; include stale-data indicator.
- Bind widgets; wire POST actions with retries and user feedback.
- Capture blueprint graphs + request/response contracts for documentation.

### Epic F — Pixel Streaming first pass

### TODOs
- Packaging: Windows Shipping build with Pixel Streaming plugin enabled; document settings.
- Infrastructure: bring up signalling server, launch packaged build with streaming flags, smoke-test 720p session, log latency + bandwidth.
- Cost hygiene: record VM usage, bitrate, run timestamps; iterate once on perf/quality.
