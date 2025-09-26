import { Canvas, CanvasProps } from "@react-three/fiber";
import type { ReactNode } from "react";
import { Suspense, useMemo } from "react";
import { useSceneCamera, useSceneLighting, useSceneRenderConfig } from "./SceneManager";

export interface SceneRendererProps {
  children: ReactNode;
  className?: string;
  canvasKey?: string | number;
  camera?: CanvasProps["camera"];
  frameloop?: CanvasProps["frameloop"];
  dpr?: CanvasProps["dpr"];
}

/**
 * Lightweight shell component for Three.js scenes.
 * Centralizes Canvas defaults so higher-level views can focus on scene content.
 */
export function SceneRenderer({
  children,
  className,
  canvasKey,
  camera,
  frameloop,
  dpr,
}: SceneRendererProps) {
  const renderConfig = useSceneRenderConfig();
  const cameraConfig = useSceneCamera();
  const lightingConfig = useSceneLighting();

  const resolvedCamera = useMemo<CanvasProps["camera"]>(() => {
    if (camera) return camera;
    const [x, y, z] = cameraConfig.position;
    return {
      position: [x, y, z] as [number, number, number],
      fov: cameraConfig.fov,
      near: cameraConfig.near,
      far: cameraConfig.far,
    } satisfies CanvasProps["camera"];
  }, [camera, cameraConfig]);

  const resolvedFrameloop = frameloop ?? renderConfig.frameloop;
  const resolvedDpr = dpr ?? renderConfig.dpr;

  return (
    <Canvas
      key={canvasKey}
      className={className}
      frameloop={resolvedFrameloop}
      camera={resolvedCamera}
      dpr={resolvedDpr}
      gl={{ antialias: true, toneMappingExposure: lightingConfig.exposure }}
    >
      <Suspense fallback={null}>{children}</Suspense>
    </Canvas>
  );
}

export default SceneRenderer;
