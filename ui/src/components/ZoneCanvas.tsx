import { Canvas } from "@react-three/fiber";
import {OrbitControls, PerspectiveCamera, Stars} from "@react-three/drei";
import useSWR from "swr";
import { getState } from "../api";
import { useMemo } from "react";

function emotionToColor(emotion?: string, intensity = 0) {
  // very rough mapping – tweak later
  const map: Record<string, string> = {
    joy: "#ffd700",
    awe: "#8ec5ff",
    grief: "#2f4f4f",
    anger: "#ff4500",
    fear: "#551a8b",
    neutral: "#cccccc",
  };
  const base = map[emotion ?? "neutral"] || "#888888";
  // darken or lighten by intensity (0‑10)
  const factor = 0.3 + intensity / 20;         // 0.3‑0.8
  return base + Math.round(factor * 255).toString(16).padStart(2, "0");
}

export default function ZoneCanvas() {
  const { data } = useSWR("state", getState, { refreshInterval: 1000 });

  const bgColor = useMemo(() => {
    if (!data) return "#000000";
    return emotionToColor(data.emotion, data.identity_score * 10);
  }, [data]);

  if (!data) return <div className="h-96 bg-slate-300">Loading…</div>;

  return (
    <Canvas className="h-96" style={{ background: bgColor }}>
      {/* put camera 12 units back so we’re outside the sphere */}
      <PerspectiveCamera makeDefault position={[0, 0, 12]} />

      {/* softer ambient + key light */}
      <ambientLight intensity={0.5} />
      <directionalLight position={[4, 4, 4]} intensity={0.7} />

      {/* smaller, brighter sphere so it pops */}
      <mesh>
        <sphereGeometry args={[2, 32, 32]} />
        <meshStandardMaterial color="#8888ff" roughness={0.2} metalness={0.1} />
      </mesh>

      <Stars radius={50} factor={6} />
      <OrbitControls enablePan={false} />
    </Canvas>
  );
}