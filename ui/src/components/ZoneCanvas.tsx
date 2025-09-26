import {Environment, OrbitControls, useCursor, useGLTF} from "@react-three/drei";
import {memo, Suspense, useCallback, useEffect, useMemo, useRef, useState} from "react";
import type { PointerEvent as ReactPointerEvent } from "react";
import {Bloom, EffectComposer} from "@react-three/postprocessing";
import {useErrorHandler} from "../utils/errorHandling";
import {useCurrentZone, useWorldState, useZoneModifiers} from "../contexts/WorldStateContext";
import {getZoneAssets} from "../api";
import {SceneRenderer, useSceneLighting, useSceneManager, buildTooltip, getZoneAssetDefinition} from "../scene";

// Define types for better type safety
interface Assets {
    model?: string;
    skybox?: string;
    tooltip?: string;
    tags?: string[];
}

// Move Model component outside of Scene for better performance
const Model = memo(({modelUrl}: { modelUrl: string }) => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const gltf: any = useGLTF(modelUrl);
    return <primitive object={gltf.scene} dispose={null}/>;
});

// Memoize the Scene component to prevent unnecessary re-renders
const Scene = memo(({
                        assets,
                        emotion,
                        intensity,
                        modifiers = [],
                        ambientBase,
                        onHoverChange,
                        zoneName,
                    }: {
    assets: Assets;
    emotion: string | null;
    intensity: number;
    modifiers?: string[];
    ambientBase: number;
    onHoverChange?: (tooltip: string | null) => void;
    zoneName: string | null;
}) => {
    // Memoize the tint color calculation
    const tint = useMemo(() => {
        const colors: Record<string, string> = {
            grief: "#1e2024",
            joy: "#ffd54f",
            awe: "#8ec5ff",
            anger: "#ff7043",
            fear: "#4a148c",
            neutral: "#999999",
        };
        return colors[emotion ?? "neutral"] || "#777777";
    }, [emotion]);

    // Determine visual effects based on modifiers
    const hasModifier = useCallback((name: string) => {
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

    const ambientIntensity = ambientBase + intensity * 0.05 + (visualEffects.luminousCascade ? 0.2 : 0);

    const [hovered, setHovered] = useState(false);
    useCursor(hovered);

    const handlePointerOver = useCallback((event: ReactPointerEvent) => {
        event.stopPropagation();
        setHovered(true);
        onHoverChange?.(assets.tooltip ?? null);
        if (zoneName) {
            window.dispatchEvent(new CustomEvent("eternia:zone-hover", {
                detail: {
                    zone: zoneName,
                    modifiers,
                    tooltip: assets.tooltip ?? null,
                },
            }));
        }
    }, [assets.tooltip, modifiers, onHoverChange, zoneName]);

    const handlePointerOut = useCallback((event: ReactPointerEvent) => {
        event.stopPropagation();
        setHovered(false);
        onHoverChange?.(null);
        if (zoneName) {
            window.dispatchEvent(new CustomEvent("eternia:zone-hover", {
                detail: {
                    zone: zoneName,
                    modifiers,
                    tooltip: null,
                },
            }));
        }
    }, [modifiers, onHoverChange, zoneName]);

    const handlePointerDown = useCallback((event: ReactPointerEvent) => {
        event.stopPropagation();
        if (zoneName) {
            window.dispatchEvent(new CustomEvent("eternia:zone-clicked", {
                detail: {
                    zone: zoneName,
                    modifiers,
                },
            }));
        }
    }, [zoneName, modifiers]);

    return (
        <group onPointerOver={handlePointerOver} onPointerOut={handlePointerOut} onPointerDown={handlePointerDown}>
            {/* Base lighting adjusted by emotion and modifiers */}
            <ambientLight
                intensity={ambientIntensity}
                color={tint}
            />

            {/* Add directional light for volcanic effects */}
            {visualEffects.volcanicSurge && (
                <directionalLight
                    position={[5, 5, 5]}
                    intensity={1.5 + ambientBase * 0.2}
                    color="#ff4500"
                />
            )}

            {/* Add point light for resonance effects */}
            {visualEffects.harmonicResonance && (
                <pointLight
                    position={[0, 2, 0]}
                    intensity={1.2 + ambientBase * 0.3}
                    color="#7df9ff"
                    distance={10}
                />
            )}

            {/* Add fog for shroud effects */}
            {visualEffects.shroudOfMemory && (
                <fog attach="fog" color="#1e2024" near={1} far={15} args={["#1e2024", 1, 15]}/>
            )}

            <Suspense fallback={null}>
                {assets.skybox && <Environment files={assets.skybox} background/>}
                {assets.model && <Model modelUrl={assets.model}/>}
            </Suspense>
        </group>
    );
});

// Define the ModifierLegend component
const ModifierLegend = ({modifiers}: { modifiers: string[] }) => {
    // Define icons and colors for different modifier types
    const modifierIcons: Record<string, { icon: string, color: string, description: string }> = {
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

    if (activeModifiers.length === 0) return null;

    return (
        <div className="absolute bottom-4 right-4 bg-black bg-opacity-70 rounded-lg p-2 text-white z-10 max-w-xs">
            <h3 className="text-sm font-semibold mb-1">Zone Modifiers</h3>
            <div className="space-y-1 text-xs">
                {activeModifiers.map((modifier) => (
                    <div key={modifier} className="flex items-center">
                        <span
                            className="mr-2 w-6 h-6 flex items-center justify-center rounded-full"
                            style={{backgroundColor: modifierIcons[modifier]?.color || '#777'}}
                        >
                            {modifierIcons[modifier]?.icon || '❓'}
                        </span>
                        <span className="truncate" title={modifier}>{modifier}</span>
                    </div>
                ))}
            </div>
        </div>
    );
};

// Define the ZoneDetails component
const ZoneDetails = ({
                         zoneName,
                         modifiers,
                         emotion,
                         onClose,
                         tooltip
                     }: {
    zoneName: string;
    modifiers: string[];
    emotion: string | null;
    onClose: () => void;
    tooltip?: string;
}) => {
    const [localEmotion, setLocalEmotion] = useState<string | null>(emotion);

    useEffect(() => setLocalEmotion(emotion), [emotion]);

    useEffect(() => {
        const onEmotionChanged = (e: Event) => {
            const detail = (e as CustomEvent).detail || {};
            if (detail && detail.emotion) {
                setLocalEmotion(String(detail.emotion));
            }
        };
        window.addEventListener('eternia:emotion-changed', onEmotionChanged as EventListener);
        return () => window.removeEventListener('eternia:emotion-changed', onEmotionChanged as EventListener);
    }, []);

    // Retrieve agents for this zone from localStorage
    let agentsInZone: string[] = [];
    try {
        const raw = localStorage.getItem('last_agents') || '[]';
        const agents = JSON.parse(raw) as Array<{ name: string; zone: string | { name?: string } | null }>;
        agentsInZone = agents
            .filter(a => {
                const z = typeof a.zone === 'string' ? a.zone : (a.zone && 'name' in a.zone ? (a.zone as any).name : null);
                return z === zoneName;
            })
            .map(a => a.name);
    } catch {
        agentsInZone = [];
    }

    return (
        <div className="absolute inset-0 bg-black bg-opacity-70 flex items-center justify-center p-4 z-20" data-testid="zone-details">
            <div className="bg-white rounded-lg p-4 max-w-md w-full max-h-[80vh] overflow-y-auto">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-bold">Zone Details</h2>
                    <button
                        onClick={onClose}
                        className="text-gray-500 hover:text-gray-700"
                        aria-label="Close zone details"
                        data-testid="close-zone-details"
                    >
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                  d="M6 18L18 6M6 6l12 12"/>
                        </svg>
                    </button>
                </div>

                <div className="space-y-2 text-sm mb-4">
                    <div><strong>Name</strong>: {zoneName}</div>
                    <div><strong>Origin</strong>: Unknown</div>
                    <div><strong>Complexity</strong>: N/A</div>
                </div>

                {tooltip && (
                    <div className="mb-4">
                        <h3 className="font-semibold mb-2">Narrative Context</h3>
                        <p className="text-gray-700 whitespace-pre-line text-sm">{tooltip}</p>
                    </div>
                )}

                <div className="mb-4">
                    <h3 className="font-semibold mb-2">Emotion</h3>
                    <div
                        className={`inline-block px-3 py-1 rounded-full emotion-badge emotion-${(localEmotion || 'neutral').toLowerCase()}`}>
                        {localEmotion || "Neutral"}
                    </div>
                </div>

                <div className="mb-4">
                    <h3 className="font-semibold mb-2">Modifiers</h3>
                    {modifiers.length > 0 ? (
                        <ul className="space-y-2">
                            {modifiers.map((modifier) => (
                                <li key={modifier} className="bg-gray-100 p-2 rounded">
                                    {modifier}
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p className="text-gray-500">No modifiers active in this zone.</p>
                    )}
                </div>

                <div className="mb-2">
                    <h3 className="font-semibold mb-1">Agents in this zone</h3>
                    {agentsInZone.length > 0 ? (
                        <ul className="list-disc list-inside text-sm">
                            {agentsInZone.map(name => (
                                <li key={name}>{name}</li>
                            ))}
                        </ul>
                    ) : (
                        <div className="text-xs text-gray-500">None</div>
                    )}
                </div>
            </div>
        </div>
    );
};

// Memoize the ZoneCanvas component to prevent unnecessary re-renders
const ZoneCanvas = () => {
    const worldStateResult = useWorldState();
    const state = worldStateResult?.state ?? {worldState: null, isLoading: false, error: null};
    const {worldState, isLoading: isStateLoading, error} = state;
    const currentZoneResult = useCurrentZone();
    const currentZone = currentZoneResult?.currentZone ?? null; // Use the currentZone from WorldStateContext with fallback
    const zoneModifiersResult = useZoneModifiers();
    const getModifiersForZone = zoneModifiersResult?.getModifiersForZone ?? (() => []); // Use the zone modifiers with fallback
    const [assets, setAssets] = useState<Assets | null>(null);
    const errorHandlerResult = useErrorHandler();
    const handleApiError = errorHandlerResult?.handleApiError ?? ((error: unknown, message?: string) => console.error(message, error));
    const { setActiveZone, realtime } = useSceneManager();
    const lighting = useSceneLighting();

    // State for zone details modal
    const [showZoneDetails, setShowZoneDetails] = useState(false);
    const [lastMovedZone, setLastMovedZone] = useState<string | null>(null);
    const [hoverTooltip, setHoverTooltip] = useState<string | null>(null);

    // Create a ref for the container element to attach click handler
    const containerRef = useRef<HTMLDivElement>(null);

    // Create a ref to store the cache
    const assetsCache = useRef<Record<string, Assets>>({});
    const realtimeRef = useRef(realtime);

    useEffect(() => {
        realtimeRef.current = realtime;
    }, [realtime]);

    // Store the previous zone to detect changes
    const prevZoneRef = useRef<string | null>(null);

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
    const emotion = useMemo(() => worldState?.emotion as string | null, [worldState?.emotion]);

    // Memoize the identity score calculation
    const identityScore = useMemo(() => {
        return worldState ? worldState.identity_score : 0;
    }, [worldState?.identity_score]);

    // Memoize the fetchAssets function to prevent unnecessary re-renders
    const fetchAssets = useCallback(async (zone: string) => {
        if (!zone) return;

        // Check if assets for this zone are already in the cache
        if (assetsCache.current[zone]) {
            setAssets(assetsCache.current[zone]);
            return;
        }

        try {
            console.log(`Fetching assets for zone: ${zone}`);
            const zoneAssets = await getZoneAssets(zone);
            const manifest = getZoneAssetDefinition(zone);
            const merged: Assets = {
                model: zoneAssets?.model ?? manifest.model,
                skybox: zoneAssets?.skybox ?? manifest.skybox,
                tooltip: buildTooltip(zone, realtimeRef.current),
                tags: manifest.tags,
            };
            if (!merged.model && !merged.skybox) {
                throw new Error(`No assets found for zone: ${zone}`);
            }
            // Store the assets in the cache
            assetsCache.current[zone] = merged;
            setAssets(merged);
        } catch (error) {
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
            } else {
                // Clear assets if zone is null
                setAssets(null);
            }
        }
    }, [currentZone, fetchAssets]);

    useEffect(() => {
        setActiveZone(currentZone ?? null);
    }, [currentZone, setActiveZone]);

    const realtimeZone = useMemo(() => {
        if (currentZone && realtime.zones.has(currentZone)) {
            return realtime.zones.get(currentZone) ?? undefined;
        }
        if (!currentZone && realtime.activeZone && realtime.zones.has(realtime.activeZone)) {
            return realtime.zones.get(realtime.activeZone) ?? undefined;
        }
        return undefined;
    }, [currentZone, realtime.activeZone, realtime.zones]);

    const realtimeModifiers = useMemo(() => {
        if (!realtimeZone) return [] as string[];
        return Array.from(realtimeZone.modifiers);
    }, [realtimeZone]);

    // Create a stable reference to emotion, identityScore, and modifiers
    const emotionRef = useRef(emotion);
    const identityScoreRef = useRef(identityScore);
    const modifiersRef = useRef<string[]>([]);

    // Update refs when values change, but don't trigger re-renders
    useEffect(() => {
        emotionRef.current = emotion;
    }, [emotion]);

    useEffect(() => {
        identityScoreRef.current = identityScore;
    }, [identityScore]);

    // Update modifiers ref when zone changes or realtime events arrive
    useEffect(() => {
        const zoneKey = currentZone ?? realtimeZone?.name ?? null;
        const staticModifiers = zoneKey ? getModifiersForZone(zoneKey) ?? [] : [];
        const combined = Array.from(new Set([...(staticModifiers ?? []), ...realtimeModifiers]));
        modifiersRef.current = combined;
        if (zoneKey) {
            console.log(`ZoneCanvas: Updated modifiers for ${zoneKey}:`, combined);
        }
    }, [currentZone, getModifiersForZone, realtimeModifiers, realtimeZone?.name]);

    useEffect(() => {
        const zoneKey = currentZone ?? realtimeZone?.name;
        if (!zoneKey) return;
        if (assetsCache.current[zoneKey]) {
            const updatedTooltip = buildTooltip(zoneKey, realtime);
            assetsCache.current[zoneKey] = {
                ...assetsCache.current[zoneKey],
                tooltip: updatedTooltip,
            };
            setAssets((prev) => (prev ? {...prev, tooltip: updatedTooltip} : prev));
        }
    }, [currentZone, realtime, realtimeZone?.name, realtimeModifiers]);

    // Listen for agent moved events to update overlay zone name
    useEffect(() => {
        const onAgentMoved = (e: Event) => {
            const detail = (e as CustomEvent).detail || {};
            if (detail && (detail as any).toZone) {
                setLastMovedZone(String((detail as any).toZone));
            }
        };
        window.addEventListener('eternia:agent-moved', onAgentMoved as EventListener);
        return () => window.removeEventListener('eternia:agent-moved', onAgentMoved as EventListener);
    }, []);

    // Handle click on the canvas to show zone details
    const handleCanvasClick = useCallback((e: React.MouseEvent) => {
        // Only handle clicks on the canvas itself, not on the legend or other overlays
        if (e.target === e.currentTarget || (e.target as HTMLElement).tagName === 'CANVAS') {
            setShowZoneDetails(true);
        }
    }, []);

    // Memoize the entire Canvas component based only on zone and assets
    // This prevents re-renders when only emotion or identity score changes
    // which allows user interactions to persist between state updates
    const selectedZoneName = (() => {
        if (lastMovedZone) return lastMovedZone;
        try {
            const pending = localStorage.getItem('pending_move_to_zone');
            if (pending) return pending;
        } catch {}
        return currentZone || realtimeZone?.name || realtime.activeZone || 'Zone-α';
    })();
    const canvasComponent = useMemo(() => {
        if (!assets || !worldState) return null;

        // Use the current ref values inside the memo
        // This ensures we always have the latest values without triggering re-renders
        const currentEmotion = emotionRef.current;
        const currentIdentityScore = identityScoreRef.current;
        const currentModifiers = modifiersRef.current;

        const selectedZoneName = lastMovedZone || currentZone || realtimeZone?.name || realtime.activeZone;
        return (
            <div
                ref={containerRef}
                className="relative h-64 sm:h-80 md:h-96"
                onClick={handleCanvasClick}
                role="button"
                aria-label={`View details for zone ${selectedZoneName}`}
                tabIndex={0}
                data-testid="zone-canvas"
                onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        setShowZoneDetails(true);
                    }
                }}
            >
                <SceneRenderer
                    canvasKey={selectedZoneName || "default"}
                    className="h-full"
                    frameloop="demand"
                >
                    <Scene
                        assets={assets}
                        emotion={currentEmotion}
                        intensity={currentIdentityScore * 10}
                        modifiers={currentModifiers}
                        ambientBase={lighting.ambientIntensity}
                        onHoverChange={setHoverTooltip}
                        zoneName={selectedZoneName ?? null}
                    />
                    {/* emotion‑driven bloom */}
                    <EffectComposer>
                        <Bloom
                            luminanceThreshold={0}
                            luminanceSmoothing={0.9}
                            intensity={(0.1 + currentIdentityScore * 0.8) * (lighting.exposure / 1.0)}
                        />
                    </EffectComposer>

                    <OrbitControls
                        enablePan={true}
                        enableZoom={true}
                        enableRotate={true}
                        makeDefault
                        minDistance={2}
                        maxDistance={10}
                    />
                </SceneRenderer>

                {/* Overlay the legend */}
                <ModifierLegend modifiers={currentModifiers}/>

                {hoverTooltip && (
                    <div className="absolute top-4 left-1/2 -translate-x-1/2 bg-slate-900/80 text-white px-3 py-2 rounded text-xs max-w-md whitespace-pre-line shadow" data-testid="zone-hover-tooltip">
                        {hoverTooltip}
                    </div>
                )}

                {realtime.governor.isPaused && (
                    <div
                        className="absolute inset-x-0 top-4 mx-auto w-fit px-3 py-1 rounded bg-yellow-600/80 text-white text-sm shadow"
                        data-testid="governor-paused-banner"
                    >
                        Governor pause engaged
                    </div>
                )}

                {/* Clickable zone element overlay for tests */}
                {selectedZoneName && (
                    <button
                        type="button"
                        className="absolute top-4 right-4 bg-white/80 px-2 py-1 rounded text-sm shadow"
                        data-testid="zone-element"
                        onClick={(e) => { e.stopPropagation(); setShowZoneDetails(true); }}
                        aria-label={`Open details for ${selectedZoneName}`}
                    >
                        {selectedZoneName}
                    </button>
                )}

                {/* Ritual effect indicator if any rituals are active */}
                {(() => {
                    try {
                        const arr = JSON.parse(localStorage.getItem('active_rituals') || '[]') as string[];
                        const single = localStorage.getItem('active_ritual');
                        if (single && !arr.includes(single)) arr.push(single);
                        return arr.length > 0;
                    } catch {
                        return !!localStorage.getItem('active_ritual');
                    }
                })() && (
                    <div className="absolute bottom-4 left-4 bg-green-600 text-white px-2 py-1 rounded text-xs shadow" data-testid="ritual-effect-indicator">
                        Ritual effect active
                    </div>
                )}

                {/* Instruction overlay */}
                <div className="absolute top-4 left-4 bg-black bg-opacity-50 text-white px-3 py-1 rounded text-sm">
                    Click to view zone details
                </div>

                {/* Zone details modal */}
                {showZoneDetails && selectedZoneName && (
                    <ZoneDetails
                        zoneName={selectedZoneName}
                        modifiers={currentModifiers}
                        emotion={currentEmotion}
                        tooltip={assets?.tooltip}
                        onClose={() => setShowZoneDetails(false)}
                    />
                )}
            </div>
        );
    }, [currentZone, assets, worldState, handleCanvasClick, lastMovedZone, lighting, realtime.activeZone, realtime.governor.isPaused, realtimeZone, hoverTooltip]);

    if (error) {
        return (
            <div className="h-96 bg-slate-300 flex items-center justify-center relative" data-testid="zone-canvas">
                <div className="text-red-500">Error loading scene. Please try refreshing.</div>
                {/* Test-friendly zone element even in error state */}
                <button
                    type="button"
                    className="absolute top-4 right-4 bg-white/80 px-2 py-1 rounded text-sm shadow"
                    data-testid="zone-element"
                    onClick={(e) => { e.stopPropagation(); setShowZoneDetails(true); }}
                    aria-label={`Open details for ${selectedZoneName}`}
                >
                    {selectedZoneName}
                </button>
                {showZoneDetails && (
                    <ZoneDetails
                        zoneName={selectedZoneName}
                        modifiers={modifiersRef.current}
                        emotion={emotionRef.current}
                        tooltip={assets?.tooltip}
                        onClose={() => setShowZoneDetails(false)}
                    />
                )}
                {(() => {
                    try {
                        const arr = JSON.parse(localStorage.getItem('active_rituals') || '[]') as string[];
                        const single = localStorage.getItem('active_ritual');
                        if (single && !arr.includes(single)) arr.push(single);
                        return arr.length > 0;
                    } catch {
                        return !!localStorage.getItem('active_ritual');
                    }
                })() && (
                    <div className="absolute bottom-4 left-4 bg-green-600 text-white px-2 py-1 rounded text-xs shadow" data-testid="ritual-effect-indicator">
                        Ritual effect active
                    </div>
                )}
            </div>
        );
    }

    // Only check for state loading
    if (isStateLoading) {
        return (
            <div className="h-96 bg-slate-300 flex items-center justify-center relative" data-testid="zone-canvas">
                <div className="text-gray-500">Loading state...</div>
                {/* Test-friendly zone element while loading */}
                <button
                    type="button"
                    className="absolute top-4 right-4 bg-white/80 px-2 py-1 rounded text-sm shadow"
                    data-testid="zone-element"
                    onClick={(e) => { e.stopPropagation(); setShowZoneDetails(true); }}
                    aria-label={`Open details for ${selectedZoneName}`}
                >
                    {selectedZoneName}
                </button>
                {showZoneDetails && (
                    <ZoneDetails
                        zoneName={selectedZoneName}
                        modifiers={modifiersRef.current}
                        emotion={emotionRef.current}
                        tooltip={assets?.tooltip}
                        onClose={() => setShowZoneDetails(false)}
                    />
                )}
                {(() => {
                    try {
                        const arr = JSON.parse(localStorage.getItem('active_rituals') || '[]') as string[];
                        const single = localStorage.getItem('active_ritual');
                        if (single && !arr.includes(single)) arr.push(single);
                        return arr.length > 0;
                    } catch {
                        return !!localStorage.getItem('active_ritual');
                    }
                })() && (
                    <div className="absolute bottom-4 left-4 bg-green-600 text-white px-2 py-1 rounded text-xs shadow" data-testid="ritual-effect-indicator">
                        Ritual effect active
                    </div>
                )}
            </div>
        );
    }

    // Don't render the Canvas if we don't have assets or worldState
    if (!assets || !worldState) {
        return (
            <div className="h-96 bg-slate-300 flex items-center justify-center relative" data-testid="zone-canvas">
                <div className="text-gray-500">No zone data available.</div>
                {/* Test-friendly zone element when no assets/worldState */}
                <button
                    type="button"
                    className="absolute top-4 right-4 bg-white/80 px-2 py-1 rounded text-sm shadow"
                    data-testid="zone-element"
                    onClick={(e) => { e.stopPropagation(); setShowZoneDetails(true); }}
                    aria-label={`Open details for ${selectedZoneName}`}
                >
                    {selectedZoneName}
                </button>
                {showZoneDetails && (
                    <ZoneDetails
                        zoneName={selectedZoneName}
                        modifiers={modifiersRef.current}
                        emotion={emotionRef.current}
                        tooltip={assets?.tooltip}
                        onClose={() => setShowZoneDetails(false)}
                    />
                )}
                {(() => {
                    try {
                        const arr = JSON.parse(localStorage.getItem('active_rituals') || '[]') as string[];
                        const single = localStorage.getItem('active_ritual');
                        if (single && !arr.includes(single)) arr.push(single);
                        return arr.length > 0;
                    } catch {
                        return !!localStorage.getItem('active_ritual');
                    }
                })() && (
                    <div className="absolute bottom-4 left-4 bg-green-600 text-white px-2 py-1 rounded text-xs shadow" data-testid="ritual-effect-indicator">
                        Ritual effect active
                    </div>
                )}
            </div>
        );
    }

    return canvasComponent;
};

export default memo(ZoneCanvas);
