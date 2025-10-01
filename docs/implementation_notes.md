# Implementation Notes

## Epic A1′ — First-person project skeleton

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
   - Enable only: Enhanced Input, Behavior Tree, EQS, Mass AI, Lumen (Software), Nanite, Virtual Textures, Pixel
     Streaming.
   - Export the enabled plugin list (Markdown snippet or screenshot reference) for future audits; explicitly disable
     Starter Content and non-required plugins before the first commit.
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
