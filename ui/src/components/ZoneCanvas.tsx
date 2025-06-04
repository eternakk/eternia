import { Canvas } from "@react-three/fiber";
import { OrbitControls, Environment, useGLTF } from "@react-three/drei";
import { Suspense, useEffect, useMemo, useState, memo, useRef } from "react";
import { EffectComposer, Bloom } from "@react-three/postprocessing";
import { useErrorHandler } from "../utils/errorHandling";
import { useAppState } from "../contexts/AppStateContext";
import { useZone } from "../contexts/ZoneContext";
import { getZoneAssets } from "../api";

// Define types for better type safety
interface Assets {
  model?: string;
  skybox?: string;
}

// Move Model component outside of Scene for better performance
const Model = memo(({ modelUrl }: { modelUrl: string }) => {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const gltf: any = useGLTF(modelUrl);
  return <primitive object={gltf.scene} dispose={null} />;
});

// Memoize the Scene component to prevent unnecessary re-renders
const Scene = memo(({ zone, emotion, intensity }: { zone: string; emotion: string | null; intensity: number }) => {
  const [assets, setAssets] = useState<Assets | null>(null);
  const { handleApiError } = useErrorHandler();
  const assetsCache = useRef<Record<string, Assets>>({});
  const prevZoneRef = useRef<string | null>(null);

  // Fetch assets for the zone only when the zone changes
  useEffect(() => {
    // Skip if zone hasn't changed
    if (zone === prevZoneRef.current) {
      return;
    }

    prevZoneRef.current = zone;
    console.log("Scene: Fetching assets for zone:", zone);

    const fetchAssets = async () => {
      if (!zone) return;

      // Check if assets for this zone are already in the cache
      if (assetsCache.current[zone]) {
        setAssets(assetsCache.current[zone]);
        return;
      }

      try {
        const assets = await getZoneAssets(zone);
        // Store the assets in the cache
        assetsCache.current[zone] = assets;
        setAssets(assets);
      } catch (error) {
        handleApiError(error, `Failed to load assets for zone: ${zone}`);
        setAssets(null);
      }
    };

    fetchAssets();
  }, [zone, handleApiError]);

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

  // Memoize the scene content to prevent unnecessary rerenders
  const sceneContent = useMemo(() => {
    if (!assets) return null;

    return (
      <>
        <ambientLight intensity={0.4 + intensity * 0.05} color={tint} />
        <Suspense fallback={null}>
          {assets.skybox && <Environment files={assets.skybox} background />}
          {assets.model && <Model modelUrl={assets.model} />}
        </Suspense>
      </>
    );
  }, [assets, intensity, tint]);

  return sceneContent;
});

// Memoize the ZoneCanvas component to prevent unnecessary re-renders
const ZoneCanvas = () => {
  const { state } = useAppState();
  const { worldState, isLoading: isStateLoading, error } = state;
  const { currentZone } = useZone();
  const { handleApiError } = useErrorHandler();

  // Use refs to store previous values for comparison
  const prevZoneRef = useRef<string | null>(null);
  const prevEmotionRef = useRef<string | null>(null);
  const prevIdentityScoreRef = useRef<number>(0);

  // Determine which zone to display - use selected zone from ZoneContext if available, otherwise use worldState
  const zoneToDisplay = useMemo(() => {
    const newZone = currentZone || (worldState?.current_zone || null);
    // Only update the ref if the zone has changed
    if (newZone !== prevZoneRef.current) {
      prevZoneRef.current = newZone;
      console.log("Zone changed to:", newZone);
    }
    return newZone;
  }, [currentZone, worldState?.current_zone]);

  // Memoize the identity score calculation
  const identityScore = useMemo(() => {
    const newScore = worldState ? worldState.identity_score : 0;
    // Only update the ref if the score has changed
    if (newScore !== prevIdentityScoreRef.current) {
      prevIdentityScoreRef.current = newScore;
    }
    return newScore;
  }, [worldState?.identity_score]);

  // Memoize the emotion value to prevent unnecessary rerenders
  const emotion = useMemo(() => {
    const newEmotion = worldState?.emotion || null;
    // Only update the ref if the emotion has changed
    if (newEmotion !== prevEmotionRef.current) {
      prevEmotionRef.current = newEmotion;
    }
    return newEmotion;
  }, [worldState?.emotion]);

  // Use useMemo to memoize the entire Canvas component
  // This will only re-render when one of the dependencies changes
  const canvasComponent = useMemo(() => {
    console.log("Rendering Canvas with zone:", zoneToDisplay);

    // Handle error state
    if (error) {
      return (
        <div className="h-96 bg-slate-300 flex items-center justify-center">
          <div className="text-red-500">Error loading scene. Please try refreshing.</div>
        </div>
      );
    }

    // Handle loading state
    if (isStateLoading) {
      return (
        <div className="h-96 bg-slate-300 flex items-center justify-center">
          <div className="text-gray-500">Loading state...</div>
        </div>
      );
    }

    // Handle no worldState
    if (!worldState) {
      return (
        <div className="h-96 bg-slate-300 flex items-center justify-center">
          <div className="text-gray-500">No zone data available.</div>
        </div>
      );
    }

    // Render the actual canvas when we have worldState
    return (
      <Canvas className="h-96" frameloop="demand">
        <Suspense fallback={null}>
          <Scene
            zone={zoneToDisplay || ""}
            emotion={emotion}
            intensity={identityScore * 10}
          />
          {/* emotion‑driven bloom */}
          <EffectComposer>
            <Bloom
              luminanceThreshold={0}
              luminanceSmoothing={0.9}
              intensity={0.1 + identityScore * 0.8}
            />
          </EffectComposer>
        </Suspense>

        <OrbitControls enablePan={false} />
      </Canvas>
    );
  }, [zoneToDisplay, emotion, identityScore, worldState, error, isStateLoading]);

  return canvasComponent;
};

// Use React.memo to prevent unnecessary rerenders
export default memo(ZoneCanvas);
