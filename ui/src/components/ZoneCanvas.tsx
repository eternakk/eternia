import { Canvas } from "@react-three/fiber";
import { OrbitControls, Environment, useGLTF } from "@react-three/drei";
import { Suspense, useEffect, useMemo, useState, useCallback, memo, useRef } from "react";
import axios from "axios";
import { EffectComposer, Bloom } from "@react-three/postprocessing";
import { useErrorHandler } from "../utils/errorHandling";
import { useAppState } from "../contexts/AppStateContext";

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
const Scene = memo(({ assets, emotion, intensity }: { assets: Assets; emotion: string | null; intensity: number }) => {
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
      <ambientLight intensity={0.4 + intensity * 0.05} color={tint} />
      <Suspense fallback={null}>
        {assets.skybox && <Environment files={assets.skybox} background />}
        {assets.model && <Model modelUrl={assets.model} />}
      </Suspense>
    </>
  );
});

// Memoize the ZoneCanvas component to prevent unnecessary re-renders
const ZoneCanvas = () => {
  const { state } = useAppState();
  const { worldState, isLoading: isStateLoading, error } = state;
  const [assets, setAssets] = useState<Assets | null>(null);
  const { handleApiError } = useErrorHandler();

  // Create a ref to store the cache
  const assetsCache = useRef<Record<string, Assets>>({});

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
      const response = await axios.get(`http://localhost:8000/zone/assets`, {
        params: { name: zone },
      });
      // Store the assets in the cache
      assetsCache.current[zone] = response.data;
      setAssets(response.data);
    } catch (error) {
      handleApiError(error, `Failed to load assets for zone: ${zone}`);
      setAssets(null);
    }
  }, [handleApiError]);

  // Only fetch assets when zone changes
  useEffect(() => {
    if (worldState?.current_zone) {
      fetchAssets(worldState.current_zone);
    }
  }, [worldState?.current_zone, fetchAssets]);

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

  return (
    <Canvas className="h-96" frameloop="demand">
      <Suspense fallback={null}>
        <Scene
          assets={assets}
          emotion={worldState.emotion}
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
};

export default memo(ZoneCanvas);
