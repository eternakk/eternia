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
const Scene = memo(({assets, emotion, intensity}: { assets: Assets; emotion: string | null; intensity: number }) => {
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

    return (
        <>
            <ambientLight intensity={0.4 + intensity * 0.05} color={tint}/>
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
    const {currentZone} = useZone(); // Use the ZoneContext for current_zone
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

    // Create a stable reference to emotion and identityScore
    const emotionRef = useRef(emotion);
    const identityScoreRef = useRef(identityScore);

    // Update refs when values change, but don't trigger re-renders
    useEffect(() => {
        emotionRef.current = emotion;
    }, [emotion]);

    useEffect(() => {
        identityScoreRef.current = identityScore;
    }, [identityScore]);

    // Memoize the entire Canvas component based only on zone and assets
    // This prevents re-renders when only emotion or identity score changes
    // which allows user interactions to persist between state updates
    const canvasComponent = useMemo(() => {
        if (!assets || !worldState) return null;

        // Use the current ref values inside the memo
        // This ensures we always have the latest values without triggering re-renders
        const currentEmotion = emotionRef.current;
        const currentIdentityScore = identityScoreRef.current;

        return (
            <Canvas key={currentZone} className="h-96" frameloop="demand">
                <Suspense fallback={null}>
                    <Scene
                        assets={assets}
                        emotion={currentEmotion}
                        intensity={currentIdentityScore * 10}
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

                <OrbitControls enablePan={false}/>
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
