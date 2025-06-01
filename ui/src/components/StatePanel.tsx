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
    <div className="p-4 border rounded-xl shadow bg-white">
      <h2 className="font-semibold mb-2">World State</h2>
      <ul className="space-y-1 text-sm">
        <li>Cycle: {worldState.cycle}</li>
        <li>Identity Score: {worldState.identity_score.toFixed(3)}</li>
        <li>Emotion: {worldState.emotion ?? "–"}</li>
        <li>Modifiers: {Object.keys(worldState.modifiers).length}</li>
        {worldState.lastUpdated && (
          <li className="text-xs text-gray-500">
            Last updated: {new Date(state.lastUpdated || 0).toLocaleTimeString()}
          </li>
        )}
      </ul>
    </div>
  );
};

export default memo(StatePanel);
