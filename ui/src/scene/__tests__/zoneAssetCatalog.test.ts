import { describe, expect, it } from "vitest";
import { buildTooltip, describeModifiers, getZoneAssetDefinition } from "../zoneAssetCatalog";
import { createInitialRealtimeState } from "../SceneState";

describe("zoneAssetCatalog", () => {
  it("returns default assets when zone is unknown", () => {
    const assets = getZoneAssetDefinition("Unknown Realm");
    expect(assets.model).toBe("/static/models/default_zone.glb");
    expect(assets.tooltip).toContain("Uncharted zone");
  });

  it("summarizes known modifiers while skipping unknown entries", () => {
    const summary = describeModifiers(["Luminous Cascade", "Unknown", "Shroud of Memory"]);
    expect(summary).toHaveLength(2);
    expect(summary[0]).toContain("Luminous Cascade");
    expect(summary[1]).toContain("Shroud of Memory");
  });

  it("builds composite tooltip with realtime modifiers", () => {
    const realtime = createInitialRealtimeState();
    realtime.zones.set("Quantum Forest", {
      name: "Quantum Forest",
      isExplored: true,
      modifiers: new Set(["Luminous Cascade", "Cosmic Awareness"]),
    });

    const tooltip = buildTooltip("Quantum Forest", realtime);
    expect(tooltip).toContain("Entangled canopy");
    expect(tooltip?.split("\n\n")).toHaveLength(2);
    expect(tooltip).toContain("Cosmic Awareness");
  });
});
