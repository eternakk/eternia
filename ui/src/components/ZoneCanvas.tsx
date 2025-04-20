import { Canvas } from "@react-three/fiber";
import { OrbitControls, Environment, useGLTF } from "@react-three/drei";
import { Suspense, useEffect, useMemo, useState } from "react";
import axios from "axios";
import useSWR from "swr";
import { getState } from "../api";

function Scene({ zone, emotion, intensity }: { zone: string; emotion: string | null; intensity: number }) {
  const [assets, setAssets] = useState<any | null>(null);

  useEffect(() => {
  if (!zone) return;                  // guard: don’t call without a name

  console.log("Fetching assets for zone:", zone);   // ← see what React thinks
  axios
    .get(`http://localhost:8000/zone/assets`, {     // absolute URL avoids proxy issues
      params: { name: zone },
    })
    .then(r => setAssets(r.data))
    .catch(err => console.error("asset error", err));
}, [zone]);

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

  if (!assets) return null;

  const Model = () => {
    /**
     * useGLTF returns a GLTF result whose `.scene` can be passed
     * directly to a <primitive>.  Casting to `any` bypasses the
     * TS "Property 'scene' does not exist" complaint without
     * disabling type‑checking for the whole file.
     */
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const gltf: any = useGLTF(assets.model);
    return <primitive object={gltf.scene} dispose={null} />;
  };

  return (
    <>
      <ambientLight intensity={0.4 + intensity * 0.05} color={tint} />
      <Suspense fallback={null}>
        {assets.skybox && <Environment files={assets.skybox} background />}
        {assets.model && <Model />}
      </Suspense>
    </>
  );
}

export default function ZoneCanvas() {
const { data } = useSWR("state", getState, { refreshInterval: 1000 });
useEffect(() => {
  console.log("state.current_zone =", data?.current_zone);
}, [data]);
  if (!data) return <div className="h-96 bg-slate-300" />;

  return (
    <Canvas className="h-96">
      <Scene
        zone={data.current_zone ?? ""}
        emotion={data.emotion}
        intensity={data.identity_score * 10}
      />
      <OrbitControls enablePan={false} />
    </Canvas>
  );
}