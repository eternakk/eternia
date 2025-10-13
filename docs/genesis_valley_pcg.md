# Genesis Valley PCG Pass (Epic B.4)

This guide walks through building the automated foliage/prop placement required for Epic B.4. Follow the
checklist to get a repeatable `PCG_GenesisProps` graph that scatters trees, pillars, and banners with performance-friendly
settings.

## 1. Prerequisites

1. **Enable plugins**
   - `Edit → Plugins → Procedural Content Generation` → enable **PCG** (UE 5.6 bundles the former PCG Tools into this module). Restart the editor if prompted.
   - Optional: enable **Python Editor Script Plugin** if you plan to batch-edit graph settings via scripts.
2. **Content layout**
   - Store reusable assets under `Content/GenesisValley/`.
   - Imported marketplace/Fab assets currently land under `Content/Fab/...`; keep them but create easy-to-reference
     collections:
     - `Content/GenesisValley/Meshes/Mossy_Rock_A.uasset` (duplicate from Fab mesh you like).
     - `Content/GenesisValley/Meshes/Roman_Column_A.uasset` (the column you placed manually).
     - Optional: placeholder flag mesh (`SM_Flag_Cloth`) or use Modeling mode to author a simple banner plane.
   - Right-click the source meshes → **Duplicate** into the GenesisValley folder so the PCG graph can reference assets
     that ship with the project.
3. **Landscape prep**
   - `GV_Landscape` sculpted with the altar plateau finished.
   - (Optional) Draw a spline named `GV_ProcessionalPath` following the walkway; this becomes the seed for flag placement.

## 2. Build the PCG Graph

1. **Create the graph asset**
   - Right-click in `Content/GenesisValley/PCG/` → `PCG Graph` → name it `PCG_GenesisProps`.
2. **Open the PCG editor**
   - Double-click the graph, then add nodes using the palette or right-click context menu.

### 2.1 Shared Subgraph

```
Landscape Data → Surface Sampler → Bounds Filter → Attribute Demultiplexer → Static Mesh Spawners
```

- **Landscape Input**: add a `Landscape Data` node (PCG → Data → Landscape), leave **Target Actor** = `Self` so the
  component context supplies `GV_Landscape`. This node replaces the older `Landscape Sampler` in UE 5.4+.
- **Surface Sampler**:
  - `Sampling Method`: **Raycast**
  - `Slope Angle (Max)`: `15` (prevents trees from spawning on steep ridges)
  - `Hit Normal Z ≥ 0.85`
  - Enable `Write Steepness` if you plan to pipe slope values into later filters.
- **Bounds Filter**: create a Sphere (radius 600 uu centered on the altar) to focus points near the ritual area.
- **Attribute Demultiplexer**: branch the filtered points into three categories (trees, pillars, flags) using Attribute or Tag
  filters so each branch can tune density independently.

### 2.2 Trees Branch

1. If the slope cap still feels loose, add a **Density Filter** or **Filter by Attribute** node that reads the `Steepness`
   attribute and rejects values above 0.25 (~14°).
2. Add **Point Processing → Random Subsample**: `Density = 0.0008` (≈ one tree per 10 m²).
3. Add **Static Mesh Spawner**:
   - Mesh entries: `SM_GV_OliveTree_A`, `SM_GV_OliveTree_B` (create duplicates of the assets you like).
   - Set **Scale Range**: `Min 0.85`, `Max 1.15`.
   - Enable **Align to Surface**.
4. Optional: add **Seed Offset** parameter so you can randomize later.

### 2.3 Pillars Branch

1. Insert a **Bounds Filter** (Sphere radius 3000 uu, centered on the altar location) to keep pillars concentrated near the temple.
2. Use **Random Subsample** with `Max Count = 8` to limit duplicates.
3. Static Mesh Spawner settings:
   - Mesh: `SM_GV_RomanColumn_A`.
   - Enable **Align to Normal** off (keep upright), set `Rotation Yaw` random between -10° and +10°.
   - Turn on **Nanite** on the mesh asset for performance (Details panel → Nanite → Enable).

### 2.4 Flags Branch

1. Require a spline: add a `Spline Data` node referencing `GV_ProcessionalPath` (author the spline component in the level or a helper Blueprint if it does not already exist).
2. Use **Point Sampler → Spacing Sampler** with `Distance = 400` to space banners evenly.
3. Static Mesh Spawner for `SM_GV_Flag_A` with `Align to Tangent` enabled and slight sway randomization (rotate ±5°).
4. Optional: create a **Tag** attribute `"Flag"` for future gameplay logic.

### 2.5 Graph Outputs

- Combine the branches with **Static Mesh Merger** (or connect each directly) and feed into a final **Output** node.
- Promote exposed parameters (tree density, pillar radius, flag spacing) to graph parameters: right-click the numeric
  fields → `Expose → Create Parameter`. UE 5.6 lists these values in the PCG Component’s **User Parameters** section.

## 3. Instantiate in the Level

1. Drag `PCG_GenesisProps` from the Content Browser into the `GenesisValley` level (you’ll get a new Actor with a **PCG Component**).
2. In the PCG Component details panel:
   - Keep **Processing Mode** = `On Demand` while iterating, then switch to `Always` once the scatter is locked.
   - Set **Target Actor** → `GV_Landscape`.
   - Bind the processional spline through the **User Parameters** entry you exposed earlier.
   - Tweak density/seed parameters until perf hits the 60 FPS target on baseline Mac hardware.
3. Click **Regenerate** (or press **Build**) on the PCG Component to refresh instances. Toggle `Show → Nanite` to confirm meshes stream correctly.

## 4. Performance Checklist

- `stat fps` ≥ 60.
- Nanite enabled where possible.
- Use `HLOD`/`Cluster` only if needed; keep total instances under ~500 for the first pass.
- Save the level (`File → Save All`) so instances persist.

## 5. Documentation TODOs

- Capture screenshots of the PCG graph and resulting scatter; store under `artifacts/genesis_valley/pcg/`.
- Update `docs/implementation_notes.md` → "B.4" section with: assets used, parameter values, number of instances, perf metrics.
- If you tweak density for Mac performance, log the final counts (e.g., 120 trees, 7 pillars, 10 flags).

## 6. Optional Automation

- Use Unreal Python to mass-rename imported Fab meshes:
  ```python
  import unreal
  assets = unreal.EditorAssetLibrary.list_assets('/Game/Fab/', recursive=True)
  for asset_path in assets:
      if asset_path.endswith('_FoliageType'):
          continue
      asset = unreal.EditorAssetLibrary.load_asset(asset_path)
      unreal.EditorAssetLibrary.duplicate_asset(asset_path, asset_path.replace('/Fab/', '/GenesisValley/Meshes/'))
  ```
- Wrap PCG parameter edits in utility functions so you can randomize seeds per playtest.

Following this recipe completes Epic B.4 and leaves you with a maintainable PCG setup that can be iterated by designers or future automation passes.
