import { useWorldState } from "../contexts/WorldStateContext";
import { memo, useState } from "react";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, TooltipProps } from 'recharts';
import { NameType, ValueType } from 'recharts/types/component/DefaultTooltipContent';

// Custom tooltip component for charts
const CustomTooltip = ({ active, payload, label, tooltipText }: TooltipProps<ValueType, NameType> & { tooltipText: string }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-2 border border-gray-200 shadow-md rounded text-sm">
        <p className="font-semibold">{`${label}: ${payload[0].value}`}</p>
        <p className="text-xs text-gray-600">{tooltipText}</p>
      </div>
    );
  }
  return null;
};

const StatePanel = () => {
  const { state } = useWorldState();
  const { worldState, isLoading, error } = state;
  
  // State for historical data (in a real app, this would come from an API)
  const [cycleHistory] = useState(() => {
    // Generate some sample data for demonstration
    return Array.from({ length: 10 }, (_, i) => ({
      time: i,
      value: Math.floor(Math.random() * 20) + 1
    }));
  });
  
  const [continuityHistory] = useState(() => {
    // Generate some sample data for demonstration
    return Array.from({ length: 10 }, (_, i) => ({
      time: i,
      value: (Math.random() * 0.5 + 0.5).toFixed(3)
    }));
  });

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

  // Update history with current values (in a real app, this would be handled differently)
  if (worldState) {
    cycleHistory.push({ time: cycleHistory.length, value: worldState.cycle });
    if (cycleHistory.length > 10) cycleHistory.shift();
    
    continuityHistory.push({ time: continuityHistory.length, value: worldState.identity_score.toFixed(3) });
    if (continuityHistory.length > 10) continuityHistory.shift();
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

      {/* Desktop view - charts and full information */}
      <div className="hidden md:block space-y-4" aria-label="World state details">
        {/* Cycle Chart */}
        <div className="mb-4">
          <h3 className="text-sm font-medium mb-1 flex items-center">
            Cycle Progress
            <span className="ml-2 text-xs bg-blue-100 px-2 py-0.5 rounded-full">{worldState.cycle}</span>
            <div className="relative group ml-2">
              <span className="cursor-help text-gray-400">ⓘ</span>
              <div className="absolute left-0 bottom-full mb-2 hidden group-hover:block bg-white p-2 rounded shadow-lg border border-gray-200 text-xs w-48 z-10">
                Cycles represent discrete time steps in the simulation. Higher values indicate more processing has occurred.
              </div>
            </div>
          </h3>
          <div className="h-24 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={cycleHistory}>
                <XAxis dataKey="time" tick={false} />
                <YAxis />
                <Tooltip content={<CustomTooltip tooltipText="Number of processing cycles completed" />} />
                <Bar dataKey="value" fill="#3b82f6" name="Cycle" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Continuity Chart */}
        <div className="mb-4">
          <h3 className="text-sm font-medium mb-1 flex items-center">
            Identity Continuity
            <span className="ml-2 text-xs bg-green-100 px-2 py-0.5 rounded-full">{worldState.identity_score.toFixed(3)}</span>
            <div className="relative group ml-2">
              <span className="cursor-help text-gray-400">ⓘ</span>
              <div className="absolute left-0 bottom-full mb-2 hidden group-hover:block bg-white p-2 rounded shadow-lg border border-gray-200 text-xs w-48 z-10">
                Identity continuity measures how consistent the system's behavior is over time. Higher values indicate greater stability.
              </div>
            </div>
          </h3>
          <div className="h-24 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={continuityHistory}>
                <XAxis dataKey="time" tick={false} />
                <YAxis domain={[0, 1]} />
                <Tooltip content={<CustomTooltip tooltipText="Measure of system stability and coherence" />} />
                <Line type="monotone" dataKey="value" stroke="#10b981" name="Continuity" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Other information */}
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="flex items-center">
            <span className="mr-1">Emotion:</span>
            <span 
              className={`px-2 py-0.5 rounded text-xs emotion-badge emotion-${(worldState.emotion || 'neutral').toLowerCase()}`}
            >
              {worldState.emotion ?? "Neutral"}
            </span>
            <div className="relative group ml-2">
              <span className="cursor-help text-gray-400">ⓘ</span>
              <div className="absolute left-0 bottom-full mb-2 hidden group-hover:block bg-white p-2 rounded shadow-lg border border-gray-200 text-xs w-48 z-10">
                Current emotional state of the system, influencing behavior and zone characteristics.
              </div>
            </div>
          </div>
          
          <div className="flex items-center">
            <span className="mr-1">Modifiers:</span>
            <span className="text-xs bg-purple-100 px-2 py-0.5 rounded-full">
              {Object.keys(worldState.modifiers).length}
            </span>
            <div className="relative group ml-2">
              <span className="cursor-help text-gray-400">ⓘ</span>
              <div className="absolute left-0 bottom-full mb-2 hidden group-hover:block bg-white p-2 rounded shadow-lg border border-gray-200 text-xs w-48 z-10">
                Active modifiers affecting zones and system behavior.
              </div>
            </div>
          </div>
        </div>

        {state.lastUpdated && (
          <div className="text-xs text-gray-500 mt-2">
            Last updated: {new Date(state.lastUpdated || 0).toLocaleTimeString()}
          </div>
        )}
      </div>

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
          <div className="mt-2 space-y-3 pl-2 border-l-2 border-blue-100" aria-label="Additional world state details">
            {/* Mini Cycle Chart */}
            <div>
              <div className="text-xs font-medium mb-1">Cycle: {worldState.cycle}</div>
              <div className="h-16 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={cycleHistory.slice(-5)}>
                    <Bar dataKey="value" fill="#3b82f6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            
            {/* Mini Continuity Chart */}
            <div>
              <div className="text-xs font-medium mb-1">Identity Score: {worldState.identity_score.toFixed(3)}</div>
              <div className="h-16 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={continuityHistory.slice(-5)}>
                    <Line type="monotone" dataKey="value" stroke="#10b981" dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
            
            <div>Modifiers: {Object.keys(worldState.modifiers).length}</div>
            
            {state.lastUpdated && (
              <div className="text-xs text-gray-500">
                Last updated: {new Date(state.lastUpdated || 0).toLocaleTimeString()}
              </div>
            )}
          </div>
        </details>
      </div>
    </div>
  );
};

export default memo(StatePanel);