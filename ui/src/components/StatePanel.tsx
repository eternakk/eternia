import { useAppState } from "../contexts/AppStateContext";
import { memo } from "react";

const StatePanel = () => {
  const { state } = useAppState();
  const { worldState, isLoading, error } = state;

  if (error) {
    return (
      <div className="p-4 border rounded-xl shadow bg-white">
        <h2 className="font-semibold mb-2">World State</h2>
        <div className="text-red-500">Error loading state. Please try refreshing.</div>
      </div>
    );
  }

  if (isLoading || !worldState) {
    return (
      <div className="p-4 border rounded-xl shadow bg-white">
        <h2 className="font-semibold mb-2">World State</h2>
        <div className="text-gray-500">Loading state…</div>
      </div>
    );
  }

  return (
    <div className="p-4 border rounded-xl shadow bg-white" role="region" aria-labelledby="world-state-heading">
      <div className="flex justify-between items-center mb-2">
        <h2 className="font-semibold" id="world-state-heading">World State</h2>

        {/* Mobile view - simplified display with only critical info */}
        <div className="md:hidden flex items-center space-x-2" aria-label="Critical world state information">
          <span className="px-2 py-1 bg-blue-100 rounded text-xs" aria-label={`Cycle: ${worldState.cycle}`}>
            Cycle: {worldState.cycle}
          </span>
          <span 
            className={`px-2 py-1 rounded text-xs emotion-badge-small emotion-${(worldState.emotion || 'neutral').toLowerCase()}`}
            aria-label={`Emotion: ${worldState.emotion ?? "Neutral"}`}
          >
            {worldState.emotion ?? "Neutral"}
          </span>
        </div>
      </div>

      {/* Desktop view - full information */}
      <ul className="hidden md:block space-y-1 text-sm" aria-label="World state details">
        <li>Cycle: {worldState.cycle}</li>
        <li>Identity Score: {worldState.identity_score.toFixed(3)}</li>
        <li>Emotion: {worldState.emotion ?? "–"}</li>
        <li>Modifiers: {Object.keys(worldState.modifiers).length}</li>
        {state.lastUpdated && (
          <li className="text-xs text-gray-500">
            Last updated: {new Date(state.lastUpdated || 0).toLocaleTimeString()}
          </li>
        )}
      </ul>

      {/* Mobile view - expandable details */}
      <div className="md:hidden mt-2">
        <details className="text-sm">
          <summary 
            className="cursor-pointer text-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="Show additional world state details"
            tabIndex={0}
          >
            Show Details
          </summary>
          <ul className="mt-2 space-y-1 pl-2 border-l-2 border-blue-100" aria-label="Additional world state details">
            <li>Identity Score: {worldState.identity_score.toFixed(3)}</li>
            <li>Modifiers: {Object.keys(worldState.modifiers).length}</li>
            {state.lastUpdated && (
              <li className="text-xs text-gray-500">
                Last updated: {new Date(state.lastUpdated || 0).toLocaleTimeString()}
              </li>
            )}
          </ul>
        </details>
      </div>
    </div>
  );
};

export default memo(StatePanel);
