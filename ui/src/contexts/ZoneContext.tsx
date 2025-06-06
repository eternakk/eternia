import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useAppState } from './AppStateContext';
import { changeZone } from '../api';
import { useErrorHandler } from '../utils/errorHandling';

// Define the shape of our zone state
interface ZoneState {
  currentZone: string | null;
  setCurrentZone: (zone: string) => void;
  zoneModifiers: Record<string, string[]>;
  getModifiersForZone: (zone: string) => string[];
}

// Create the context
const ZoneContext = createContext<ZoneState | undefined>(undefined);

// Create a provider component
interface ZoneProviderProps {
  children: ReactNode;
}

export const ZoneProvider: React.FC<ZoneProviderProps> = ({ children }) => {
  const { state } = useAppState();
  const [currentZone, setCurrentZone] = useState<string | null>(null);
  const [zoneModifiers, setZoneModifiers] = useState<Record<string, string[]>>({});
  const { handleApiError } = useErrorHandler();

  // Function to set the current zone
  const handleSetCurrentZone = async (zone: string) => {
    console.log(`ZoneContext: Manually setting zone to ${zone}`);

    // Update local state immediately for responsive UI
    setCurrentZone(zone);

    // Make API call to update the zone on the backend
    try {
      await changeZone(zone);
      console.log(`ZoneContext: Successfully updated zone to ${zone} on the backend`);
    } catch (error) {
      handleApiError(error, `Failed to change zone to ${zone}`);
      // Note: We don't revert the local state change here to avoid UI flickering
      // The worldState update will eventually sync the state if needed
    }
  };

  // Function to get modifiers for a specific zone
  const getModifiersForZone = (zone: string): string[] => {
    return zoneModifiers[zone] || [];
  };

  // Only update the zone state when current_zone changes from worldState
  useEffect(() => {
    const newZone = state.worldState?.current_zone || null;
    // Always update from worldState if it's different, even if it's null
    if (newZone !== currentZone) {
      console.log(`ZoneContext: Updating zone from ${currentZone} to ${newZone} (from worldState)`);
      setCurrentZone(newZone);
    }
  }, [state.worldState?.current_zone, currentZone]);

  // Update zone modifiers when worldState changes
  useEffect(() => {
    if (state.worldState?.modifiers) {
      console.log(`ZoneContext: Updating zone modifiers`, state.worldState.modifiers);
      setZoneModifiers(state.worldState.modifiers);
    }
  }, [state.worldState?.modifiers]);

  // Create the context value object
  const contextValue: ZoneState = {
    currentZone,
    setCurrentZone: handleSetCurrentZone,
    zoneModifiers,
    getModifiersForZone
  };

  return (
    <ZoneContext.Provider value={contextValue}>
      {children}
    </ZoneContext.Provider>
  );
};

// Create a hook to use the zone context
export const useZone = () => {
  const context = useContext(ZoneContext);
  if (context === undefined) {
    throw new Error('useZone must be used within a ZoneProvider');
  }
  return context;
};
