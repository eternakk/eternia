import {Canvas} from "@react-three/fiber";
import {Environment, OrbitControls, useGLTF} from "@react-three/drei";
import {memo, Suspense, useCallback, useEffect, useMemo, useRef, useState} from "react";
import {Bloom, EffectComposer} from "@react-three/postprocessing";
import {useErrorHandler} from "../utils/errorHandling";
import {useAppState} from "../contexts/AppStateContext";
import {useZone} from "../contexts/ZoneContext";
import {getZoneAssets} from "../api";

// Define types for better type safety
interface Assets {
    model?: string;
    skybox?: string;
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
    modifiers = []
}: { 
    assets: Assets; 
    emotion: string | null; 
    intensity: number;
    modifiers?: string[];
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

    return (
        <>
            {/* Base lighting adjusted by emotion and modifiers */}
            <ambientLight 
                intensity={0.4 + intensity * 0.05 + (visualEffects.luminousCascade ? 0.2 : 0)} 
                color={tint}
            />

            {/* Add directional light for volcanic effects */}
            {visualEffects.volcanicSurge && (
                <directionalLight 
                    position={[5, 5, 5]} 
                    intensity={1.5} 
                    color="#ff4500" 
                />
            )}

            {/* Add point light for resonance effects */}
            {visualEffects.harmonicResonance && (
                <pointLight 
                    position={[0, 2, 0]} 
                    intensity={1.2} 
                    color="#7df9ff" 
                    distance={10}
                />
            )}

            {/* Add fog for shroud effects */}
            {visualEffects.shroudOfMemory && (
                <fog attach="fog" color="#1e2024" near={1} far={15} />
            )}

            <Suspense fallback={null}>
                {assets.skybox && <Environment files={assets.skybox} background/>}
                {assets.model && <Model modelUrl={assets.model}/>}
            </Suspense>
        </>
    );
});

// Memoize the ZoneCanvas component to prevent unnecessary re-renders
const ZoneCanvas = () => {
    const {state} = useAppState();
    const {worldState, isLoading: isStateLoading, error} = state;
    const {currentZone, getModifiersForZone} = useZone(); // Use the ZoneContext for current_zone and modifiers
    const [assets, setAssets] = useState<Assets | null>(null);
    const {handleApiError} = useErrorHandler();

    // Create a ref to store the cache
    const assetsCache = useRef<Record<string, Assets>>({});

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
            if (zoneAssets) {
                // Store the assets in the cache
                assetsCache.current[zone] = zoneAssets;
                setAssets(zoneAssets);
            } else {
                throw new Error(`No assets found for zone: ${zone}`);
            }
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
            } else {
                // Clear assets if zone is null
                setAssets(null);
            }
        }
    }, [currentZone, fetchAssets]);

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

    // Update modifiers ref when currentZone changes
    useEffect(() => {
        if (currentZone) {
            const zoneModifiers = getModifiersForZone(currentZone);
            modifiersRef.current = zoneModifiers;
            console.log(`ZoneCanvas: Updated modifiers for ${currentZone}:`, zoneModifiers);
        } else {
            modifiersRef.current = [];
        }
    }, [currentZone, getModifiersForZone]);

    // Memoize the entire Canvas component based only on zone and assets
    // This prevents re-renders when only emotion or identity score changes
    // which allows user interactions to persist between state updates
    const canvasComponent = useMemo(() => {
        if (!assets || !worldState) return null;

        // Use the current ref values inside the memo
        // This ensures we always have the latest values without triggering re-renders
        const currentEmotion = emotionRef.current;
        const currentIdentityScore = identityScoreRef.current;
        const currentModifiers = modifiersRef.current;

        return (
            <Canvas key={currentZone} className="h-64 sm:h-80 md:h-96" frameloop="demand">
                <Suspense fallback={null}>
                    <Scene
                        assets={assets}
                        emotion={currentEmotion}
                        intensity={currentIdentityScore * 10}
                        modifiers={currentModifiers}
                    />
                    {/* emotion‑driven bloom */}
                    <EffectComposer>
                        <Bloom
                            luminanceThreshold={0}
                            luminanceSmoothing={0.9}
                            intensity={0.1 + currentIdentityScore * 0.8}
                        />
                    </EffectComposer>
                </Suspense>

                <OrbitControls 
                    enablePan={true}
                    enableZoom={true}
                    enableRotate={true}
                    makeDefault
                    minDistance={2}
                    maxDistance={10}
                    />
            </Canvas>
        );
    }, [currentZone, assets, worldState]); // Only depend on zone and assets to prevent unnecessary re-renders

    if (error) {
        return (
            <div className="h-96 bg-slate-300 flex items-center justify-center">
                <div className="text-red-500">Error loading scene. Please try refreshing.</div>
            </div>
        );
    }

    // Only check for state loading
    if (isStateLoading) {
        return (
            <div className="h-96 bg-slate-300 flex items-center justify-center">
                <div className="text-gray-500">Loading state...</div>
            </div>
        );
    }

    // Don't render the Canvas if we don't have assets or worldState
    if (!assets || !worldState) {
        return (
            <div className="h-96 bg-slate-300 flex items-center justify-center">
                <div className="text-gray-500">No zone data available.</div>
            </div>
        );
    }

    return canvasComponent;
};

export default memo(ZoneCanvas);
