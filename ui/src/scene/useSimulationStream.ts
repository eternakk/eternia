import { useMemo } from "react";
import { useGovEvents } from "../hooks/useGovEvents";
import {
  normalizeSimulationEvent,
  SimulationEvent,
  SimulationEventKind,
} from "./simulationEvents";

export interface SimulationStreamOptions {
  filter?: SimulationEventKind[];
  includeUnknown?: boolean;
}

export interface SimulationStreamResult {
  events: SimulationEvent[];
  latest: SimulationEvent | null;
  latestByKind: Map<SimulationEventKind, SimulationEvent>;
}

function useFilterSet(filter?: SimulationEventKind[]) {
  return useMemo(() => {
    if (!filter || filter.length === 0) return null;
    return new Set(filter);
  }, [filter?.join("|")]);
}

export function useSimulationStream(options: SimulationStreamOptions = {}): SimulationStreamResult {
  const { filter, includeUnknown = false } = options;
  const rawEvents = useGovEvents();
  const filterSet = useFilterSet(filter);

  const normalized = useMemo(() => {
    const mapped = rawEvents.map(normalizeSimulationEvent);
    return mapped.filter((event) => {
      if (filterSet && !filterSet.has(event.kind)) {
        return false;
      }
      if (!includeUnknown && event.kind === "unknown") {
        return false;
      }
      return true;
    });
  }, [filterSet, includeUnknown, rawEvents]);

  const latest = normalized.length > 0 ? normalized[normalized.length - 1] : null;

  const latestByKind = useMemo(() => {
    const map = new Map<SimulationEventKind, SimulationEvent>();
    for (const event of normalized) {
      map.set(event.kind, event);
    }
    return map;
  }, [normalized]);

  return { events: normalized, latest, latestByKind };
}
