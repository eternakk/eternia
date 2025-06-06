import React, { useState, useEffect } from 'react';
import { useAppState } from '../contexts/AppStateContext';
import { useZone } from '../contexts/ZoneContext';

interface ZoneEmotionDashboardProps {
  className?: string;
}

/**
 * Dashboard component to monitor zone and emotion state changes in real-time
 */
export const ZoneEmotionDashboard: React.FC<ZoneEmotionDashboardProps> = ({ 
  className = '' 
}) => {
  const { state } = useAppState();
  const { worldState } = state;
  const { currentZone, zoneModifiers } = useZone();
  
  // State to track changes
  const [changes, setChanges] = useState<Array<{
    timestamp: Date;
    type: 'zone' | 'emotion' | 'modifier';
    message: string;
  }>>([]);
  
  // Previous state for comparison
  const [prevState, setPrevState] = useState<{
    zone: string | null;
    emotion: string | null;
    modifiers: Record<string, string[]>;
  }>({
    zone: null,
    emotion: null,
    modifiers: {},
  });
  
  // Effect to detect and log zone changes
  useEffect(() => {
    if (currentZone !== prevState.zone) {
      const newChange = {
        timestamp: new Date(),
        type: 'zone' as const,
        message: `Zone changed from ${prevState.zone || 'none'} to ${currentZone || 'none'}`,
      };
      
      setChanges(prev => [newChange, ...prev].slice(0, 50)); // Keep last 50 changes
      setPrevState(prev => ({ ...prev, zone: currentZone }));
    }
  }, [currentZone, prevState.zone]);
  
  // Effect to detect and log emotion changes
  useEffect(() => {
    if (worldState?.emotion !== prevState.emotion) {
      const newChange = {
        timestamp: new Date(),
        type: 'emotion' as const,
        message: `Emotion changed from ${prevState.emotion || 'none'} to ${worldState?.emotion || 'none'}`,
      };
      
      setChanges(prev => [newChange, ...prev].slice(0, 50)); // Keep last 50 changes
      setPrevState(prev => ({ ...prev, emotion: worldState?.emotion || null }));
    }
  }, [worldState?.emotion, prevState.emotion]);
  
  // Effect to detect and log modifier changes
  useEffect(() => {
    // Check if modifiers have changed
    const hasModifiersChanged = () => {
      // Check if zones have changed
      const currentZones = Object.keys(zoneModifiers);
      const prevZones = Object.keys(prevState.modifiers);
      
      if (currentZones.length !== prevZones.length) return true;
      
      // Check if any zone's modifiers have changed
      for (const zone of currentZones) {
        const currentMods = zoneModifiers[zone] || [];
        const prevMods = prevState.modifiers[zone] || [];
        
        if (currentMods.length !== prevMods.length) return true;
        
        // Check if any modifier has changed
        for (const mod of currentMods) {
          if (!prevMods.includes(mod)) return true;
        }
      }
      
      return false;
    };
    
    if (hasModifiersChanged()) {
      // Find which zone's modifiers changed
      const changedZones: string[] = [];
      
      Object.keys(zoneModifiers).forEach(zone => {
        const currentMods = zoneModifiers[zone] || [];
        const prevMods = prevState.modifiers[zone] || [];
        
        if (currentMods.length !== prevMods.length) {
          changedZones.push(zone);
        } else {
          // Check if any modifier has changed
          for (const mod of currentMods) {
            if (!prevMods.includes(mod)) {
              changedZones.push(zone);
              break;
            }
          }
        }
      });
      
      // Also check for removed zones
      Object.keys(prevState.modifiers).forEach(zone => {
        if (!zoneModifiers[zone] && !changedZones.includes(zone)) {
          changedZones.push(zone);
        }
      });
      
      // Create a change entry for each changed zone
      changedZones.forEach(zone => {
        const currentMods = zoneModifiers[zone] || [];
        const prevMods = prevState.modifiers[zone] || [];
        
        const newChange = {
          timestamp: new Date(),
          type: 'modifier' as const,
          message: `Modifiers for zone '${zone}' changed from [${prevMods.join(', ')}] to [${currentMods.join(', ')}]`,
        };
        
        setChanges(prev => [newChange, ...prev].slice(0, 50)); // Keep last 50 changes
      });
      
      // Update previous state
      setPrevState(prev => ({ ...prev, modifiers: { ...zoneModifiers } }));
    }
  }, [zoneModifiers, prevState.modifiers]);
  
  // Format timestamp
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  };
  
  // Get icon for change type
  const getIcon = (type: 'zone' | 'emotion' | 'modifier') => {
    switch (type) {
      case 'zone':
        return '🌍';
      case 'emotion':
        return '😊';
      case 'modifier':
        return '🔄';
      default:
        return '📝';
    }
  };
  
  return (
    <div className={`zone-emotion-dashboard ${className}`}>
      <h2 className="text-xl font-bold mb-4">Zone & Emotion Dashboard</h2>
      
      <div className="current-state mb-4 p-4 bg-gray-100 rounded-md">
        <h3 className="text-lg font-semibold mb-2">Current State</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="font-medium">Current Zone:</p>
            <p className="ml-2">{currentZone || 'None'}</p>
          </div>
          <div>
            <p className="font-medium">Current Emotion:</p>
            <p className="ml-2">{worldState?.emotion || 'None'}</p>
          </div>
        </div>
      </div>
      
      <div className="changes-log">
        <h3 className="text-lg font-semibold mb-2">Recent Changes</h3>
        {changes.length === 0 ? (
          <p className="text-gray-500 italic">No changes detected yet</p>
        ) : (
          <div className="max-h-96 overflow-y-auto">
            {changes.map((change, index) => (
              <div 
                key={index} 
                className={`mb-2 p-2 rounded-md ${
                  change.type === 'zone' 
                    ? 'bg-blue-50' 
                    : change.type === 'emotion' 
                      ? 'bg-yellow-50' 
                      : 'bg-green-50'
                }`}
              >
                <div className="flex items-start">
                  <span className="mr-2">{getIcon(change.type)}</span>
                  <div className="flex-1">
                    <p className="text-sm text-gray-500">{formatTime(change.timestamp)}</p>
                    <p>{change.message}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ZoneEmotionDashboard;