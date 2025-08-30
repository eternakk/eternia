import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useZone } from '../contexts/ZoneContext';
/**
 * Component to display modifiers for a zone
 *
 * If zoneName is not provided, it displays modifiers for the current zone.
 */
export const ZoneModifiers = ({ zoneName, className = '' }) => {
    const { currentZone, getModifiersForZone } = useZone();
    // Use the provided zoneName or fall back to the current zone
    const targetZone = zoneName || currentZone;
    // If no zone is specified or available, show a message
    if (!targetZone) {
        return _jsx("div", { className: `zone-modifiers ${className}`, children: "No active zone" });
    }
    // Get modifiers for the target zone
    const modifiers = getModifiersForZone(targetZone);
    // If no modifiers, show a message
    if (!modifiers || modifiers.length === 0) {
        return (_jsxs("div", { className: `zone-modifiers ${className}`, children: [_jsxs("h3", { children: ["Zone: ", targetZone] }), _jsx("p", { children: "No modifiers active" })] }));
    }
    return (_jsxs("div", { className: `zone-modifiers ${className}`, children: [_jsxs("h3", { children: ["Zone: ", targetZone] }), _jsx("h4", { children: "Active Modifiers:" }), _jsx("ul", { className: "modifier-list", children: modifiers.map((modifier, index) => (_jsx("li", { className: "modifier-item", children: modifier }, index))) })] }));
};
/**
 * Component to display modifiers for all zones
 */
export const AllZoneModifiers = ({ className = '' }) => {
    const { zoneModifiers } = useZone();
    // If no modifiers for any zone, show a message
    if (!zoneModifiers || Object.keys(zoneModifiers).length === 0) {
        return _jsx("div", { className: `all-zone-modifiers ${className}`, children: "No zone modifiers active" });
    }
    return (_jsxs("div", { className: `all-zone-modifiers ${className}`, children: [_jsx("h3", { children: "All Zone Modifiers" }), Object.entries(zoneModifiers).map(([zoneName, modifiers]) => (_jsxs("div", { className: "zone-section", children: [_jsx("h4", { children: zoneName }), modifiers.length === 0 ? (_jsx("p", { children: "No modifiers active" })) : (_jsx("ul", { className: "modifier-list", children: modifiers.map((modifier, index) => (_jsx("li", { className: "modifier-item", children: modifier }, index))) }))] }, zoneName)))] }));
};
