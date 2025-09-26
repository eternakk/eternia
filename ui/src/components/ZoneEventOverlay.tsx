import { useEffect, useState } from "react";

interface ZoneEventDetail {
  zone: string;
  modifiers?: string[];
  tooltip?: string | null;
}

type ZoneHoverEvent = CustomEvent<ZoneEventDetail>;
type ZoneClickedEvent = CustomEvent<ZoneEventDetail>;

const formatModifiers = (mods?: string[]) => {
  if (!mods || mods.length === 0) return "None";
  return mods.join(", ");
};

export default function ZoneEventOverlay() {
  const [hoverInfo, setHoverInfo] = useState<ZoneEventDetail | null>(null);
  const [focusInfo, setFocusInfo] = useState<ZoneEventDetail | null>(null);

  useEffect(() => {
    const handleHover = (event: Event) => {
      const detail = (event as ZoneHoverEvent).detail;
      if (!detail) {
        setHoverInfo(null);
        return;
      }
      if (!detail.tooltip) {
        setHoverInfo(null);
        return;
      }
      setHoverInfo(detail);
    };

    const handleClick = (event: Event) => {
      const detail = (event as ZoneClickedEvent).detail;
      if (!detail) return;
      setFocusInfo(detail);
    };

    window.addEventListener("eternia:zone-hover", handleHover);
    window.addEventListener("eternia:zone-clicked", handleClick);

    return () => {
      window.removeEventListener("eternia:zone-hover", handleHover);
      window.removeEventListener("eternia:zone-clicked", handleClick);
    };
  }, []);

  const clearFocus = () => setFocusInfo(null);

  if (!hoverInfo && !focusInfo) {
    return null;
  }

  const activeHover = hoverInfo && (!focusInfo || focusInfo.zone !== hoverInfo.zone);

  return (
    <div className="pointer-events-none fixed top-4 right-4 space-y-3 z-50 max-w-sm text-sm">
      {focusInfo && (
        <div className="pointer-events-auto bg-slate-900/90 text-white rounded-lg shadow-lg p-4 border border-slate-700">
          <div className="flex justify-between items-start gap-3">
            <div>
              <h3 className="font-semibold text-base">{focusInfo.zone}</h3>
              <p className="text-xs text-slate-300">Modifiers: {formatModifiers(focusInfo.modifiers)}</p>
            </div>
            <button
              type="button"
              onClick={clearFocus}
              className="text-slate-300 hover:text-white"
              aria-label="Dismiss zone focus overlay"
            >
              ×
            </button>
          </div>
          {focusInfo.tooltip && (
            <p className="mt-2 whitespace-pre-line text-xs text-slate-200">{focusInfo.tooltip}</p>
          )}
        </div>
      )}

      {activeHover && (
        <div className="bg-slate-800/80 text-white rounded-md shadow px-3 py-2 border border-slate-600">
          <div className="font-semibold text-sm">Hover: {hoverInfo.zone}</div>
          <div className="text-xs text-slate-200 whitespace-pre-line mt-1">
            {hoverInfo.tooltip}
          </div>
        </div>
      )}
    </div>
  );
}
