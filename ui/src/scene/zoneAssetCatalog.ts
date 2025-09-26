import { SceneRealtimeState } from "./SceneState";

export interface ZoneAssetDefinition {
  model?: string;
  skybox?: string;
  tooltip?: string;
  tags?: string[];
}

const BASE_ZONE_ASSETS: Record<string, ZoneAssetDefinition> = {
  "Quantum Forest": {
    model: "/static/models/forest.glb",
    skybox: "/static/sky/forest_cave_2k.hdr",
    tooltip: "Entangled canopy where quantum rituals weave the first story arc.",
    tags: ["origin:core", "biome:forest"],
  },
  "Orikum Sea": {
    model: "/static/models/boat_josefa.glb",
    skybox: "/static/sky/simons_town_rocks_2k.hdr",
    tooltip: "Ever-shifting tides shaped by companion voyages and alignment rites.",
    tags: ["origin:coast", "biome:sea"],
  },
  "Library of Shared Minds": {
    model: "/static/models/bookshelf.glb",
    skybox: "/static/sky/empty_warehouse_01_2k.hdr",
    tooltip: "Repository of collective memory where governor decrees manifest as glyphs.",
    tags: ["origin:knowledge", "structure:library"],
  },
};

const MODIFIER_HIGHLIGHTS: Record<string, string> = {
  "Luminous Cascade": "Amplify emissive materials and add cascading particle ribbons.",
  "Shroud of Memory": "Blend volumetric fog and dim ambient to evoke hazy recollection.",
  "Volcanic Surge": "Inject heat shimmer and ember streaks around terrain seams.",
  "Cosmic Awareness": "Layer starfield projections and subtle parallax textures.",
};

const DEFAULT_ASSET: ZoneAssetDefinition = {
  model: "/static/models/default_zone.glb",
  skybox: "/static/sky/studio_small_09_2k.hdr",
  tooltip: "Uncharted zone awaiting art direction.",
};

export function getZoneAssetDefinition(zoneName: string): ZoneAssetDefinition {
  return BASE_ZONE_ASSETS[zoneName] ?? DEFAULT_ASSET;
}

export function describeModifiers(modifiers: Iterable<string>): string[] {
  const descriptions: string[] = [];
  for (const mod of modifiers) {
    if (MODIFIER_HIGHLIGHTS[mod]) {
      descriptions.push(`${mod}: ${MODIFIER_HIGHLIGHTS[mod]}`);
    }
  }
  return descriptions;
}

export function buildTooltip(zoneName: string, realtime: SceneRealtimeState): string | undefined {
  const base = getZoneAssetDefinition(zoneName).tooltip;
  const realtimeZone = realtime.zones.get(zoneName);
  if (!realtimeZone) return base;
  const modifierNotes = describeModifiers(realtimeZone.modifiers);
  if (modifierNotes.length === 0) {
    return base;
  }
  const modifierSuffix = modifierNotes.join("\n");
  return [base, modifierSuffix].filter(Boolean).join("\n\n");
}

export const ZONE_ASSET_KEYS = Object.freeze(Object.keys(BASE_ZONE_ASSETS));
