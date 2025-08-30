import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { Canvas } from "@react-three/fiber";
import { Environment, OrbitControls, useGLTF } from "@react-three/drei";
import { memo, Suspense, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Bloom, EffectComposer } from "@react-three/postprocessing";
import { useErrorHandler } from "../utils/errorHandling";
import { useCurrentZone, useWorldState, useZoneModifiers } from "../contexts/WorldStateContext";
import { getZoneAssets } from "../api";
// Move Model component outside of Scene for better performance
const Model = memo(({ modelUrl }) => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const gltf = useGLTF(modelUrl);
    return _jsx("primitive", { object: gltf.scene, dispose: null });
});
// Memoize the Scene component to prevent unnecessary re-renders
const Scene = memo(({ assets, emotion, intensity, modifiers = [] }) => {
    // Memoize the tint color calculation
    const tint = useMemo(() => {
        const colors = {
            grief: "#1e2024",
            joy: "#ffd54f",
            awe: "#8ec5ff",
            anger: "#ff7043",
            fear: "#4a148c",
            neutral: "#999999",
        };
        return colors[emotion !== null && emotion !== void 0 ? emotion : "neutral"] || "#777777";
    }, [emotion]);
    // Determine visual effects based on modifiers
    const hasModifier = useCallback((name) => {
        return modifiers.some(mod => mod.includes(name));
    }, [modifiers]);
    // Calculate visual effects based on modifiers
    const visualEffects = useMemo(() => {
        return {
            // Dimensional effects
            dimensionalExpansion: hasModifier("Dimensional Expansion"),
            cosmicAwareness: hasModifier("Cosmic Awareness"),
            // Light effects
            luminousCascade: hasModifier("Luminous Cascade"),
            vibrantPulse: hasModifier("Vibrant Pulse"),
            // Atmospheric effects
            shroudOfMemory: hasModifier("Shroud of Memory"),
            // Energy effects
            volcanicSurge: hasModifier("Volcanic Surge"),
            transformativeHeat: hasModifier("Transformative Heat"),
            // Resonance effects
            harmonicResonance: hasModifier("Harmonic Resonance"),
            connectionWeave: hasModifier("Connection Weave"),
        };
    }, [hasModifier]);
    // Log active modifiers for debugging
    useEffect(() => {
        if (modifiers.length > 0) {
            console.log("Active zone modifiers:", modifiers);
            console.log("Visual effects:", visualEffects);
        }
    }, [modifiers, visualEffects]);
    return (_jsxs(_Fragment, { children: [_jsx("ambientLight", { intensity: 0.4 + intensity * 0.05 + (visualEffects.luminousCascade ? 0.2 : 0), color: tint }), visualEffects.volcanicSurge && (_jsx("directionalLight", { position: [5, 5, 5], intensity: 1.5, color: "#ff4500" })), visualEffects.harmonicResonance && (_jsx("pointLight", { position: [0, 2, 0], intensity: 1.2, color: "#7df9ff", distance: 10 })), visualEffects.shroudOfMemory && (_jsx("fog", { attach: "fog", color: "#1e2024", near: 1, far: 15, args: ["#1e2024", 1, 15] })), _jsxs(Suspense, { fallback: null, children: [assets.skybox && _jsx(Environment, { files: assets.skybox, background: true }), assets.model && _jsx(Model, { modelUrl: assets.model })] })] }));
});
// Define the ModifierLegend component
const ModifierLegend = ({ modifiers }) => {
    // Define icons and colors for different modifier types
    const modifierIcons = {
        "Dimensional Expansion": {
            icon: "🌌",
            color: "#8A2BE2",
            description: "Expands the dimensional properties of the zone"
        },
        "Cosmic Awareness": {
            icon: "👁️",
            color: "#4B0082",
            description: "Enhances perception beyond normal limits"
        },
        "Luminous Cascade": {
            icon: "✨",
            color: "#FFD700",
            description: "Creates cascading light effects throughout the zone"
        },
        "Vibrant Pulse": {
            icon: "💓",
            color: "#FF1493",
            description: "Generates rhythmic energy pulses"
        },
        "Shroud of Memory": {
            icon: "🌫️",
            color: "#708090",
            description: "Creates a fog-like effect that obscures distant objects"
        },
        "Volcanic Surge": {
            icon: "🌋",
            color: "#FF4500",
            description: "Increases heat and energy in the zone"
        },
        "Transformative Heat": {
            icon: "🔥",
            color: "#FF8C00",
            description: "Enables transformation through thermal energy"
        },
        "Harmonic Resonance": {
            icon: "🎵",
            color: "#1E90FF",
            description: "Creates harmonious vibrations throughout the zone"
        },
        "Connection Weave": {
            icon: "🕸️",
            color: "#32CD32",
            description: "Forms connections between elements in the zone"
        }
    };
    // Filter to only show modifiers that are active and have defined icons
    const activeModifiers = modifiers.filter(mod => modifierIcons[mod]);
    if (activeModifiers.length === 0)
        return null;
    return (_jsxs("div", { className: "absolute bottom-4 right-4 bg-black bg-opacity-70 rounded-lg p-2 text-white z-10 max-w-xs", children: [_jsx("h3", { className: "text-sm font-semibold mb-1", children: "Zone Modifiers" }), _jsx("div", { className: "space-y-1 text-xs", children: activeModifiers.map((modifier) => {
                    var _a, _b;
                    return (_jsxs("div", { className: "flex items-center", children: [_jsx("span", { className: "mr-2 w-6 h-6 flex items-center justify-center rounded-full", style: { backgroundColor: ((_a = modifierIcons[modifier]) === null || _a === void 0 ? void 0 : _a.color) || '#777' }, children: ((_b = modifierIcons[modifier]) === null || _b === void 0 ? void 0 : _b.icon) || '❓' }), _jsx("span", { className: "truncate", title: modifier, children: modifier })] }, modifier));
                }) })] }));
};
// Define the ZoneDetails component
const ZoneDetails = ({ zoneName, modifiers, emotion, onClose }) => {
    return (_jsx("div", { className: "absolute inset-0 bg-black bg-opacity-70 flex items-center justify-center p-4 z-20", children: _jsxs("div", { className: "bg-white rounded-lg p-4 max-w-md w-full max-h-[80vh] overflow-y-auto", children: [_jsxs("div", { className: "flex justify-between items-center mb-4", children: [_jsx("h2", { className: "text-xl font-bold", children: zoneName }), _jsx("button", { onClick: onClose, className: "text-gray-500 hover:text-gray-700", "aria-label": "Close zone details", children: _jsx("svg", { className: "w-6 h-6", fill: "none", stroke: "currentColor", viewBox: "0 0 24 24", children: _jsx("path", { strokeLinecap: "round", strokeLinejoin: "round", strokeWidth: 2, d: "M6 18L18 6M6 6l12 12" }) }) })] }), _jsxs("div", { className: "mb-4", children: [_jsx("h3", { className: "font-semibold mb-2", children: "Emotion" }), _jsx("div", { className: `inline-block px-3 py-1 rounded-full emotion-badge emotion-${(emotion || 'neutral').toLowerCase()}`, children: emotion || "Neutral" })] }), _jsxs("div", { children: [_jsx("h3", { className: "font-semibold mb-2", children: "Modifiers" }), modifiers.length > 0 ? (_jsx("ul", { className: "space-y-2", children: modifiers.map((modifier) => (_jsx("li", { className: "bg-gray-100 p-2 rounded", children: modifier }, modifier))) })) : (_jsx("p", { className: "text-gray-500", children: "No modifiers active in this zone." }))] })] }) }));
};
// Memoize the ZoneCanvas component to prevent unnecessary re-renders
const ZoneCanvas = () => {
    var _a, _b, _c, _d;
    const worldStateResult = useWorldState();
    const state = (_a = worldStateResult === null || worldStateResult === void 0 ? void 0 : worldStateResult.state) !== null && _a !== void 0 ? _a : { worldState: null, isLoading: false, error: null };
    const { worldState, isLoading: isStateLoading, error } = state;
    const currentZoneResult = useCurrentZone();
    const currentZone = (_b = currentZoneResult === null || currentZoneResult === void 0 ? void 0 : currentZoneResult.currentZone) !== null && _b !== void 0 ? _b : null; // Use the currentZone from WorldStateContext with fallback
    const zoneModifiersResult = useZoneModifiers();
    const getModifiersForZone = (_c = zoneModifiersResult === null || zoneModifiersResult === void 0 ? void 0 : zoneModifiersResult.getModifiersForZone) !== null && _c !== void 0 ? _c : (() => []); // Use the zone modifiers with fallback
    const [assets, setAssets] = useState(null);
    const errorHandlerResult = useErrorHandler();
    const handleApiError = (_d = errorHandlerResult === null || errorHandlerResult === void 0 ? void 0 : errorHandlerResult.handleApiError) !== null && _d !== void 0 ? _d : ((error, message) => console.error(message, error));
    // State for zone details modal
    const [showZoneDetails, setShowZoneDetails] = useState(false);
    // Create a ref for the container element to attach click handler
    const containerRef = useRef(null);
    // Create a ref to store the cache
    const assetsCache = useRef({});
    // Store the previous zone to detect changes
    const prevZoneRef = useRef(null);
    // Clear cache when component unmounts or when window is about to unload
    useEffect(() => {
        const handleBeforeUnload = () => {
            // Clear the assets cache when the application is closed
            assetsCache.current = {};
            console.log('Application closing: Assets cache cleared');
        };
        // Add event listener
        window.addEventListener('beforeunload', handleBeforeUnload);
        // Clean up event listener and cache when component unmounts
        return () => {
            window.removeEventListener('beforeunload', handleBeforeUnload);
            assetsCache.current = {};
        };
    }, []);
    // Memoize the emotion to prevent unnecessary re-renders
    const emotion = useMemo(() => worldState === null || worldState === void 0 ? void 0 : worldState.emotion, [worldState === null || worldState === void 0 ? void 0 : worldState.emotion]);
    // Memoize the identity score calculation
    const identityScore = useMemo(() => {
        return worldState ? worldState.identity_score : 0;
    }, [worldState === null || worldState === void 0 ? void 0 : worldState.identity_score]);
    // Memoize the fetchAssets function to prevent unnecessary re-renders
    const fetchAssets = useCallback(async (zone) => {
        if (!zone)
            return;
        // Check if assets for this zone are already in the cache
        if (assetsCache.current[zone]) {
            setAssets(assetsCache.current[zone]);
            return;
        }
        try {
            console.log(`Fetching assets for zone: ${zone}`);
            const zoneAssets = await getZoneAssets(zone);
            if (zoneAssets) {
                // Store the assets in the cache
                assetsCache.current[zone] = zoneAssets;
                setAssets(zoneAssets);
            }
            else {
                throw new Error(`No assets found for zone: ${zone}`);
            }
        }
        catch (error) {
            handleApiError(error, `Failed to load assets for zone: ${zone}`);
            setAssets(null);
        }
    }, [handleApiError]);
    // Only fetch assets when zone actually changes
    useEffect(() => {
        // Check if zone has changed, even if it's null
        if (currentZone !== prevZoneRef.current) {
            console.log(`Zone changed from ${prevZoneRef.current} to ${currentZone}`);
            prevZoneRef.current = currentZone;
            if (currentZone) {
                fetchAssets(currentZone).then();
                // Close zone details when zone changes
                setShowZoneDetails(false);
            }
            else {
                // Clear assets if zone is null
                setAssets(null);
            }
        }
    }, [currentZone, fetchAssets]);
    // Create a stable reference to emotion, identityScore, and modifiers
    const emotionRef = useRef(emotion);
    const identityScoreRef = useRef(identityScore);
    const modifiersRef = useRef([]);
    // Update refs when values change, but don't trigger re-renders
    useEffect(() => {
        emotionRef.current = emotion;
    }, [emotion]);
    useEffect(() => {
        identityScoreRef.current = identityScore;
    }, [identityScore]);
    // Update modifiers ref when currentZone changes
    useEffect(() => {
        if (currentZone) {
            const zoneModifiers = getModifiersForZone(currentZone);
            modifiersRef.current = zoneModifiers;
            console.log(`ZoneCanvas: Updated modifiers for ${currentZone}:`, zoneModifiers);
        }
        else {
            modifiersRef.current = [];
        }
    }, [currentZone, getModifiersForZone]);
    // Handle click on the canvas to show zone details
    const handleCanvasClick = useCallback((e) => {
        // Only handle clicks on the canvas itself, not on the legend or other overlays
        if (e.target === e.currentTarget || e.target.tagName === 'CANVAS') {
            setShowZoneDetails(true);
        }
    }, []);
    // Memoize the entire Canvas component based only on zone and assets
    // This prevents re-renders when only emotion or identity score changes
    // which allows user interactions to persist between state updates
    const canvasComponent = useMemo(() => {
        if (!assets || !worldState)
            return null;
        // Use the current ref values inside the memo
        // This ensures we always have the latest values without triggering re-renders
        const currentEmotion = emotionRef.current;
        const currentIdentityScore = identityScoreRef.current;
        const currentModifiers = modifiersRef.current;
        return (_jsxs("div", { ref: containerRef, className: "relative h-64 sm:h-80 md:h-96", onClick: handleCanvasClick, role: "button", "aria-label": `View details for zone ${currentZone}`, tabIndex: 0, onKeyDown: (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    setShowZoneDetails(true);
                }
            }, children: [_jsxs(Canvas, { className: "h-full", frameloop: "demand", children: [_jsxs(Suspense, { fallback: null, children: [_jsx(Scene, { assets: assets, emotion: currentEmotion, intensity: currentIdentityScore * 10, modifiers: currentModifiers }), _jsx(EffectComposer, { children: _jsx(Bloom, { luminanceThreshold: 0, luminanceSmoothing: 0.9, intensity: 0.1 + currentIdentityScore * 0.8 }) })] }), _jsx(OrbitControls, { enablePan: true, enableZoom: true, enableRotate: true, makeDefault: true, minDistance: 2, maxDistance: 10 })] }, currentZone), _jsx(ModifierLegend, { modifiers: currentModifiers }), _jsx("div", { className: "absolute top-4 left-4 bg-black bg-opacity-50 text-white px-3 py-1 rounded text-sm", children: "Click to view zone details" }), showZoneDetails && currentZone && (_jsx(ZoneDetails, { zoneName: currentZone, modifiers: currentModifiers, emotion: currentEmotion, onClose: () => setShowZoneDetails(false) }))] }));
    }, [currentZone, assets, worldState, handleCanvasClick]); // Added handleCanvasClick to dependencies
    if (error) {
        return (_jsx("div", { className: "h-96 bg-slate-300 flex items-center justify-center", children: _jsx("div", { className: "text-red-500", children: "Error loading scene. Please try refreshing." }) }));
    }
    // Only check for state loading
    if (isStateLoading) {
        return (_jsx("div", { className: "h-96 bg-slate-300 flex items-center justify-center", children: _jsx("div", { className: "text-gray-500", children: "Loading state..." }) }));
    }
    // Don't render the Canvas if we don't have assets or worldState
    if (!assets || !worldState) {
        return (_jsx("div", { className: "h-96 bg-slate-300 flex items-center justify-center", children: _jsx("div", { className: "text-gray-500", children: "No zone data available." }) }));
    }
    return canvasComponent;
};
export default memo(ZoneCanvas);
