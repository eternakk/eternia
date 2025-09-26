import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SceneManagerProvider, useSceneManager } from "../SceneManager";
import { useSimulationStream } from "../useSimulationStream";

vi.mock("../useSimulationStream");

const mockedStream = vi.mocked(useSimulationStream);

const HookProbe = () => {
  const manager = useSceneManager();
  const zones = Array.from(manager.realtime.zones.entries()).map(([name, zone]) => ({
    name,
    isExplored: zone.isExplored,
    modifiers: Array.from(zone.modifiers.values()),
  }));
  return (
    <pre data-testid="probe">{JSON.stringify({
      activeZone: manager.realtime.activeZone,
      zones,
      paused: manager.realtime.governor.isPaused,
      violation: manager.realtime.governor.lastViolation?.kind ?? null,
      camera: manager.state.camera,
      lighting: manager.state.lighting,
    })}</pre>
  );
};

describe("SceneManager realtime updates", () => {
  it("tracks zone changes and modifiers", () => {
    mockedStream.mockReturnValue({
      events: [
        {
          kind: "zone.changed",
          timestamp: 1,
          raw: { t: 1, event: "zone_changed", payload: { zone_name: "Zone-Ω", is_new: true } },
          zoneName: "Zone-Ω",
          isNew: true,
        },
        {
          kind: "zone.modifier_added",
          timestamp: 2,
          raw: { t: 2, event: "zone_modifier_added", payload: { zone_name: "Zone-Ω", modifier: "Luminous Cascade" } },
          zoneName: "Zone-Ω",
          modifier: "Luminous Cascade",
        },
      ],
      latest: null,
      latestByKind: new Map(),
    });

    render(
      <SceneManagerProvider>
        <HookProbe />
      </SceneManagerProvider>
    );

    const data = JSON.parse(screen.getByTestId("probe").textContent || "{}");
    expect(data.activeZone).toBe("Zone-Ω");
    const zoneEntry = data.zones.find((entry: { name: string }) => entry.name === "Zone-Ω");
    expect(zoneEntry).toBeDefined();
    expect(zoneEntry.isExplored).toBe(true);
    expect(zoneEntry.modifiers).toContain("Luminous Cascade");
    expect(data.camera.position[1]).toBeCloseTo(5.5, 1);
    expect(data.lighting.ambientIntensity).toBeGreaterThan(0.4);
  });

  it("captures governor pause/resume signals", () => {
    mockedStream.mockReturnValue({
      events: [
        {
          kind: "governor.pause",
          timestamp: 1,
          raw: { t: 1, event: "pause", payload: null },
        },
        {
          kind: "governor.resume",
          timestamp: 2,
          raw: { t: 2, event: "resume", payload: null },
        },
      ],
      latest: null,
      latestByKind: new Map(),
    });

    render(
      <SceneManagerProvider>
        <HookProbe />
      </SceneManagerProvider>
    );

    const data = JSON.parse(screen.getByTestId("probe").textContent || "{}");
    expect(data.paused).toBe(false);
    expect(data.lighting.ambientIntensity).toBeCloseTo(0.4, 1);
  });
});
