import { describe, expect, it } from "vitest";
import { normalizeSimulationEvent } from "../simulationEvents";
import type { GovEvent } from "../../hooks/useGovEvents";

describe("normalizeSimulationEvent", () => {
  it("maps zone_changed events to typed structure", () => {
    const raw: GovEvent = {
      t: 123,
      event: "zone_changed",
      payload: {
        zone_name: "Zone-β",
        is_new: true,
      },
    };

    const normalized = normalizeSimulationEvent(raw);

    expect(normalized.kind).toBe("zone.changed");
    expect(normalized.timestamp).toBe(123);
    if (normalized.kind === "zone.changed") {
      expect(normalized.zoneName).toBe("Zone-β");
      expect(normalized.isNew).toBe(true);
    }
    expect(normalized.raw).toBe(raw);
  });

  it("returns unknown wrapper for unhandled events", () => {
    const raw: GovEvent = {
      t: Number.NaN,
      event: "mystery_event",
      payload: { mystery: true },
    };

    const normalized = normalizeSimulationEvent(raw);

    expect(normalized.kind).toBe("unknown");
    if (normalized.kind === "unknown") {
      expect(normalized.event).toBe("mystery_event");
      expect(normalized.payload).toEqual({ mystery: true });
    }
    expect(normalized.timestamp).toBeTypeOf("number");
  });

  it("keeps policy violation metadata", () => {
    const raw: GovEvent = {
      t: 42,
      event: "policy_violation",
      payload: {
        policy_name: "no-fly-zone",
        metrics: { severity: "high" },
      },
    };

    const normalized = normalizeSimulationEvent(raw);

    expect(normalized.kind).toBe("governor.policy_violation");
    if (normalized.kind === "governor.policy_violation") {
      expect(normalized.policyName).toBe("no-fly-zone");
      expect(normalized.metrics).toEqual({ severity: "high" });
    }
  });
});
