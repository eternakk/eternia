import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { useAppState } from '../contexts/AppStateContext';
import { useZone } from '../contexts/ZoneContext';
/**
 * Dashboard component to monitor zone and emotion state changes in real-time
 */
export const ZoneEmotionDashboard = ({ className = '' }) => {
    const { state } = useAppState();
    const { worldState } = state;
    const { currentZone, zoneModifiers } = useZone();
    // State to track changes
    const [changes, setChanges] = useState([]);
    // Previous state for comparison
    const [prevState, setPrevState] = useState({
        zone: null,
        emotion: null,
        modifiers: {},
    });
    // Effect to detect and log zone changes
    useEffect(() => {
        if (currentZone !== prevState.zone) {
            const newChange = {
                timestamp: new Date(),
                type: 'zone',
                message: `Zone changed from ${prevState.zone || 'none'} to ${currentZone || 'none'}`,
            };
            setChanges(prev => [newChange, ...prev].slice(0, 50)); // Keep last 50 changes
            setPrevState(prev => ({ ...prev, zone: currentZone }));
        }
    }, [currentZone, prevState.zone]);
    // Effect to detect and log emotion changes
    useEffect(() => {
        if ((worldState === null || worldState === void 0 ? void 0 : worldState.emotion) !== prevState.emotion) {
            const newChange = {
                timestamp: new Date(),
                type: 'emotion',
                message: `Emotion changed from ${prevState.emotion || 'none'} to ${(worldState === null || worldState === void 0 ? void 0 : worldState.emotion) || 'none'}`,
            };
            setChanges(prev => [newChange, ...prev].slice(0, 50)); // Keep last 50 changes
            setPrevState(prev => ({ ...prev, emotion: (worldState === null || worldState === void 0 ? void 0 : worldState.emotion) || null }));
        }
    }, [worldState === null || worldState === void 0 ? void 0 : worldState.emotion, prevState.emotion]);
    // Effect to detect and log modifier changes
    useEffect(() => {
        // Check if modifiers have changed
        const hasModifiersChanged = () => {
            // Check if zones have changed
            const currentZones = Object.keys(zoneModifiers);
            const prevZones = Object.keys(prevState.modifiers);
            if (currentZones.length !== prevZones.length)
                return true;
            // Check if any zone's modifiers have changed
            for (const zone of currentZones) {
                const currentMods = zoneModifiers[zone] || [];
                const prevMods = prevState.modifiers[zone] || [];
                if (currentMods.length !== prevMods.length)
                    return true;
                // Check if any modifier has changed
                for (const mod of currentMods) {
                    if (!prevMods.includes(mod))
                        return true;
                }
            }
            return false;
        };
        if (hasModifiersChanged()) {
            // Find which zone's modifiers changed
            const changedZones = [];
            Object.keys(zoneModifiers).forEach(zone => {
                const currentMods = zoneModifiers[zone] || [];
                const prevMods = prevState.modifiers[zone] || [];
                if (currentMods.length !== prevMods.length) {
                    changedZones.push(zone);
                }
                else {
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
                    type: 'modifier',
                    message: `Modifiers for zone '${zone}' changed from [${prevMods.join(', ')}] to [${currentMods.join(', ')}]`,
                };
                setChanges(prev => [newChange, ...prev].slice(0, 50)); // Keep last 50 changes
            });
            // Update previous state
            setPrevState(prev => ({ ...prev, modifiers: { ...zoneModifiers } }));
        }
    }, [zoneModifiers, prevState.modifiers]);
    // Format timestamp
    const formatTime = (date) => {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    };
    // Get icon for change type
    const getIcon = (type) => {
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
    return (_jsxs("div", { className: `zone-emotion-dashboard ${className}`, children: [_jsx("h2", { className: "text-xl font-bold mb-4", children: "Zone & Emotion Dashboard" }), _jsxs("div", { className: "current-state mb-4 p-4 bg-gray-100 rounded-md", children: [_jsx("h3", { className: "text-lg font-semibold mb-2", children: "Current State" }), _jsxs("div", { className: "grid grid-cols-2 gap-4", children: [_jsxs("div", { children: [_jsx("p", { className: "font-medium", children: "Current Zone:" }), _jsx("p", { className: "ml-2", children: currentZone || 'None' })] }), _jsxs("div", { children: [_jsx("p", { className: "font-medium", children: "Current Emotion:" }), _jsx("p", { className: "ml-2", children: (worldState === null || worldState === void 0 ? void 0 : worldState.emotion) || 'None' })] })] })] }), _jsxs("div", { className: "changes-log", children: [_jsx("h3", { className: "text-lg font-semibold mb-2", children: "Recent Changes" }), changes.length === 0 ? (_jsx("p", { className: "text-gray-500 italic", children: "No changes detected yet" })) : (_jsx("div", { className: "max-h-96 overflow-y-auto", children: changes.map((change, index) => (_jsx("div", { className: `mb-2 p-2 rounded-md ${change.type === 'zone'
                                ? 'bg-blue-50'
                                : change.type === 'emotion'
                                    ? 'bg-yellow-50'
                                    : 'bg-green-50'}`, children: _jsxs("div", { className: "flex items-start", children: [_jsx("span", { className: "mr-2", children: getIcon(change.type) }), _jsxs("div", { className: "flex-1", children: [_jsx("p", { className: "text-sm text-gray-500", children: formatTime(change.timestamp) }), _jsx("p", { children: change.message })] })] }) }, index))) }))] })] }));
};
export default ZoneEmotionDashboard;
