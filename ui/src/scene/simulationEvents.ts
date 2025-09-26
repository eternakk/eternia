import type { GovEvent } from "../hooks/useGovEvents";

export type SimulationEventKind =
  | "zone.changed"
  | "zone.explored"
  | "zone.modifier_added"
  | "governor.pause"
  | "governor.resume"
  | "governor.shutdown"
  | "governor.rollback_complete"
  | "governor.continuity_breach"
  | "governor.checkpoint_scheduled"
  | "governor.checkpoint_saved"
  | "governor.policy_violation"
  | "governor.law_enforced"
  | "unknown";

export interface SimulationEventBase {
  kind: SimulationEventKind;
  timestamp: number;
  raw: GovEvent;
}

export interface ZoneChangedEvent extends SimulationEventBase {
  kind: "zone.changed";
  zoneName: string;
  isNew: boolean;
}

export interface ZoneExploredEvent extends SimulationEventBase {
  kind: "zone.explored";
  zoneName: string;
}

export interface ZoneModifierAddedEvent extends SimulationEventBase {
  kind: "zone.modifier_added";
  zoneName: string;
  modifier: string;
}

export interface GovernorPauseEvent extends SimulationEventBase {
  kind: "governor.pause";
}

export interface GovernorResumeEvent extends SimulationEventBase {
  kind: "governor.resume";
}

export interface GovernorShutdownEvent extends SimulationEventBase {
  kind: "governor.shutdown";
  reason: string | null;
}

export interface GovernorRollbackEvent extends SimulationEventBase {
  kind: "governor.rollback_complete";
  checkpoint: string | null;
}

export interface GovernorContinuityBreachEvent extends SimulationEventBase {
  kind: "governor.continuity_breach";
  metrics: unknown;
}

export interface GovernorCheckpointScheduledEvent extends SimulationEventBase {
  kind: "governor.checkpoint_scheduled";
}

export interface GovernorCheckpointSavedEvent extends SimulationEventBase {
  kind: "governor.checkpoint_saved";
  path: string | null;
}

export interface GovernorPolicyViolationEvent extends SimulationEventBase {
  kind: "governor.policy_violation";
  policyName: string;
  metrics: unknown;
}

export interface GovernorLawEnforcedEvent extends SimulationEventBase {
  kind: "governor.law_enforced";
  lawName: string;
  eventName: string;
  payload: unknown;
}

export interface UnknownSimulationEvent extends SimulationEventBase {
  kind: "unknown";
  event: string;
  payload: unknown;
}

export type SimulationEvent =
  | ZoneChangedEvent
  | ZoneExploredEvent
  | ZoneModifierAddedEvent
  | GovernorPauseEvent
  | GovernorResumeEvent
  | GovernorShutdownEvent
  | GovernorRollbackEvent
  | GovernorContinuityBreachEvent
  | GovernorCheckpointScheduledEvent
  | GovernorCheckpointSavedEvent
  | GovernorPolicyViolationEvent
  | GovernorLawEnforcedEvent
  | UnknownSimulationEvent;

function asString(value: unknown): string | null {
  return typeof value === "string" ? value : null;
}

function toTimestamp(value: number | undefined): number {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  return Date.now() / 1000;
}

export function normalizeSimulationEvent(event: GovEvent): SimulationEvent {
  const timestamp = toTimestamp(event.t);
  const rawPayload = event.payload;
  const payload =
    typeof rawPayload === "object" && rawPayload !== null
      ? (rawPayload as Record<string, unknown>)
      : null;

  switch (event.event) {
    case "zone_changed": {
      return {
        kind: "zone.changed",
        timestamp,
        raw: event,
        zoneName: asString(payload?.zone_name) ?? "",
        isNew: Boolean(payload?.is_new),
      };
    }
    case "zone_explored": {
      return {
        kind: "zone.explored",
        timestamp,
        raw: event,
        zoneName: asString(payload?.zone_name) ?? "",
      };
    }
    case "zone_modifier_added": {
      return {
        kind: "zone.modifier_added",
        timestamp,
        raw: event,
        zoneName: asString(payload?.zone_name) ?? "",
        modifier: asString(payload?.modifier) ?? "",
      };
    }
    case "pause":
      return { kind: "governor.pause", timestamp, raw: event };
    case "resume":
      return { kind: "governor.resume", timestamp, raw: event };
    case "shutdown":
      return {
        kind: "governor.shutdown",
        timestamp,
        raw: event,
        reason: asString(payload) ?? null,
      };
    case "rollback_complete":
      return {
        kind: "governor.rollback_complete",
        timestamp,
        raw: event,
        checkpoint:
          typeof rawPayload === "string" ? rawPayload : asString(payload?.checkpoint) ?? null,
      };
    case "continuity_breach":
      return {
        kind: "governor.continuity_breach",
        timestamp,
        raw: event,
        metrics: payload ?? null,
      };
    case "checkpoint_scheduled":
      return { kind: "governor.checkpoint_scheduled", timestamp, raw: event };
    case "checkpoint_saved":
      return {
        kind: "governor.checkpoint_saved",
        timestamp,
        raw: event,
        path: typeof rawPayload === "string" ? rawPayload : asString(payload?.path) ?? null,
      };
    case "policy_violation":
      return {
        kind: "governor.policy_violation",
        timestamp,
        raw: event,
        policyName: asString(payload?.policy_name) ?? "",
        metrics: payload?.metrics ?? null,
      };
    case "law_enforced":
      return {
        kind: "governor.law_enforced",
        timestamp,
        raw: event,
        lawName: asString(payload?.law_name) ?? "",
        eventName: asString(payload?.event_name) ?? "",
        payload: payload?.payload ?? null,
      };
    default:
      return {
        kind: "unknown",
        timestamp,
        raw: event,
        event: event.event,
        payload: event.payload,
      };
  }
}
