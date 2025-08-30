import { jsx as _jsx } from "react/jsx-runtime";
import { createContext, useContext, useState, useEffect } from 'react';
import { useAppState } from './AppStateContext';
import { changeZone } from '../api';
import { useErrorHandler } from '../utils/errorHandling';
// Create the context
const ZoneContext = createContext(undefined);
export const ZoneProvider = ({ children }) => {
    var _a, _b;
    const { state } = useAppState();
    const [currentZone, setCurrentZone] = useState(null);
    const [zoneModifiers, setZoneModifiers] = useState({});
    const { handleApiError } = useErrorHandler();
    // Function to set the current zone
    const handleSetCurrentZone = async (zone) => {
        console.log(`ZoneContext: Manually setting zone to ${zone}`);
        // Update local state immediately for responsive UI
        setCurrentZone(zone);
        // Make API call to update the zone on the backend
        try {
            await changeZone(zone);
            console.log(`ZoneContext: Successfully updated zone to ${zone} on the backend`);
        }
        catch (error) {
            handleApiError(error, `Failed to change zone to ${zone}`);
            // Note: We don't revert the local state change here to avoid UI flickering
            // The worldState update will eventually sync the state if needed
        }
    };
    // Function to get modifiers for a specific zone
    const getModifiersForZone = (zone) => {
        return zoneModifiers[zone] || [];
    };
    // Only update the zone state when current_zone changes from worldState
    useEffect(() => {
        var _a;
        const newZone = ((_a = state.worldState) === null || _a === void 0 ? void 0 : _a.current_zone) || null;
        // Always update from worldState if it's different, even if it's null
        if (newZone !== currentZone) {
            console.log(`ZoneContext: Updating zone from ${currentZone} to ${newZone} (from worldState)`);
            setCurrentZone(newZone);
        }
    }, [(_a = state.worldState) === null || _a === void 0 ? void 0 : _a.current_zone, currentZone]);
    // Update zone modifiers when worldState changes
    useEffect(() => {
        var _a;
        if ((_a = state.worldState) === null || _a === void 0 ? void 0 : _a.modifiers) {
            console.log(`ZoneContext: Updating zone modifiers`, state.worldState.modifiers);
            setZoneModifiers(state.worldState.modifiers);
        }
    }, [(_b = state.worldState) === null || _b === void 0 ? void 0 : _b.modifiers]);
    // Create the context value object
    const contextValue = {
        currentZone,
        setCurrentZone: handleSetCurrentZone,
        zoneModifiers,
        getModifiersForZone
    };
    return (_jsx(ZoneContext.Provider, { value: contextValue, children: children }));
};
// Create a hook to use the zone context
export const useZone = () => {
    const context = useContext(ZoneContext);
    if (context === undefined) {
        throw new Error('useZone must be used within a ZoneProvider');
    }
    return context;
};
