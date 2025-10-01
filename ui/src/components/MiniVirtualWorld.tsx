// @ts-nocheck
import React from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import {
  KeyboardControls,
  useKeyboardControls,
  PointerLockControls,
  Sky,
  Stars,
  Text
} from "@react-three/drei";
import * as THREE from "three";
import { motion } from "framer-motion";
import { MousePointerClick, MoveRight, MoveLeft, MoveUp, MoveDown, RefreshCw } from "lucide-react";

/**
 * Mini Virtual World – single‑file React component
 * - First‑person exploration with WASD + mouse‑look (click canvas to lock)
 * - Deterministic, lightweight procedural scene (trees + rocks)
 * - Clean UI overlay with Tailwind + Framer Motion
 * - Built with react‑three‑fiber & drei, no external assets
 */

// --- Small utilities --------------------------------------------------------
function mulberry32(seed = 123456789) {
  return function () {
    let t = (seed += 0x6d2b79f5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// --- Player (first-person controller) --------------------------------------
function Player({ speed = 6, sprint = 11, resetKey }) {
  const { camera } = useThree();
  const controls = useKeyboardControls();
  const up = React.useMemo(() => new THREE.Vector3(0, 1, 0), []);
  const fwd = React.useMemo(() => new THREE.Vector3(), []);
  const right = React.useMemo(() => new THREE.Vector3(), []);
  const move = React.useMemo(() => new THREE.Vector3(), []);

  // Initial eye height & spawn
  React.useEffect(() => {
    camera.position.set(0, 1.7, 5);
  }, [camera]);

  // Reset to origin when parent toggles resetKey
  React.useEffect(() => {
    camera.position.set(0, 1.7, 5);
  }, [resetKey, camera]);

  useFrame((_, dt) => {
    const { forward, back, left, right: r, run } = controls.get();
    const v = (run ? sprint : speed) * dt;

    // derive forward/right from camera orientation
    fwd.set(0, 0, -1).applyQuaternion(camera.quaternion).normalize();
    right.copy(fwd).cross(up).normalize();

    move.set(0, 0, 0);
    if (forward) move.add(fwd);
    if (back) move.sub(fwd);
    if (left) move.sub(right);
    if (r) move.add(right);
    if (move.lengthSq() > 0) move.normalize().multiplyScalar(v);

    camera.position.add(move);
    camera.position.y = 1.7; // keep constant eye height (no gravity for now)
  });

  return null;
}

// --- World geometry ---------------------------------------------------------
function Ground() {
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
      <planeGeometry args={[500, 500, 64, 64]} />
      <meshStandardMaterial color="#3a5a40" />
    </mesh>
  );
}

function Trees({ count = 120, radius = 180 }) {
  const positions = React.useMemo(() => {
    const rand = mulberry32(42);
    const arr = [];
    for (let i = 0; i < count; i++) {
      const a = rand() * Math.PI * 2;
      const r = (0.2 + rand() * 0.8) * radius;
      const x = Math.cos(a) * r;
      const z = Math.sin(a) * r;
      arr.push([x, z, 1 + rand() * 0.8]); // scale variation
    }
    return arr;
  }, [count, radius]);

  return (
    <group>
      {positions.map(([x, z, s], i) => (
        <group position={[x, 0, z]} key={i} scale={s}>
          {/* trunk */}
          <mesh castShadow position={[0, 1.1, 0]}>
            <cylinderGeometry args={[0.18, 0.22, 2.2, 8]} />
            <meshStandardMaterial color="#6f4e37" />
          </mesh>
          {/* crown */}
          <mesh castShadow position={[0, 2.4, 0]}>
            <coneGeometry args={[1.1, 1.8, 12]} />
            <meshStandardMaterial color="#2e7d32" />
          </mesh>
        </group>
      ))}
    </group>
  );
}

function Rocks({ count = 50, radius = 120 }) {
  const rocks = React.useMemo(() => {
    const rand = mulberry32(7);
    const arr = [];
    for (let i = 0; i < count; i++) {
      const a = rand() * Math.PI * 2;
      const r = (0.1 + rand() * 0.9) * radius;
      const x = Math.cos(a) * r;
      const z = Math.sin(a) * r;
      const s = 0.4 + rand() * 1.1;
      arr.push({ x, z, s, rot: rand() * Math.PI * 2 });
    }
    return arr;
  }, [count, radius]);

  return (
    <group>
      {rocks.map((k, i) => (
        <mesh key={i} position={[k.x, 0.3 * k.s, k.z]} rotation={[0, k.rot, 0]} castShadow>
          <icosahedronGeometry args={[0.5 * k.s, 0]} />
          <meshStandardMaterial color="#8d99ae" roughness={0.9} />
        </mesh>
      ))}
    </group>
  );
}

function Sunlight() {
  const light = React.useRef();
  return (
    <group>
      <ambientLight intensity={0.35} />
      <directionalLight
        ref={light}
        castShadow
        intensity={1.0}
        position={[50, 80, 25]}
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
      />
      {/* hint of warmth */}
      <hemisphereLight intensity={0.2} groundColor={new THREE.Color("#3a5a40")} />
    </group>
  );
}

// --- HUD overlay ------------------------------------------------------------
function HUD({ controlsRef, locked, onReset }) {
  return (
    <div className="pointer-events-none absolute inset-0 select-none">
      {/* Top-left help card */}
      <motion.div
        initial={{ opacity: 0, y: -6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="pointer-events-auto m-3 inline-flex items-center gap-3 rounded-2xl bg-zinc-900/70 px-4 py-3 text-zinc-100 shadow-xl backdrop-blur"
      >
        <MousePointerClick className="h-4 w-4" />
        <span className="text-sm">
          Click the scene to <b>mouse‑look</b>. Use <b>W/A/S/D</b> (or arrows), hold <b>Shift</b> to sprint.
        </span>
      </motion.div>

      {/* Bottom center status */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2">
        <motion.div
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-full bg-zinc-900/60 px-4 py-2 text-xs text-zinc-200 backdrop-blur shadow-lg"
        >
          {locked ? "Pointer locked – press Esc to release" : "Click to enter – Esc to pause"}
        </motion.div>
      </div>

      {/* Bottom-right controls */}
      <div className="pointer-events-auto absolute bottom-4 right-4 flex gap-2">
        <button
          onClick={() => onReset?.()}
          className="rounded-2xl bg-zinc-900/80 px-3 py-2 text-xs text-zinc-100 shadow-lg backdrop-blur transition hover:bg-zinc-800"
        >
          <div className="flex items-center gap-2">
            <RefreshCw className="h-3.5 w-3.5" />
            Reset position
          </div>
        </button>
      </div>
    </div>
  );
}

// --- Main exported component ------------------------------------------------
export default function MiniVirtualWorld() {
  const [locked, setLocked] = React.useState(false);
  const [resetKey, setResetKey] = React.useState(0);
  const plcRef = React.useRef(null);

  const keyboardMap = React.useMemo(
    () => [
      { name: "forward", keys: ["KeyW", "ArrowUp"] },
      { name: "back", keys: ["KeyS", "ArrowDown"] },
      { name: "left", keys: ["KeyA", "ArrowLeft"] },
      { name: "right", keys: ["KeyD", "ArrowRight"] },
      { name: "run", keys: ["ShiftLeft", "ShiftRight"] }
    ],
    []
  );

  return (
    <div className="relative h-[78vh] w-full overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-950">
      <KeyboardControls map={keyboardMap}>
        <Canvas shadows camera={{ fov: 75, position: [0, 1.7, 5] }}>
          <fog attach="fog" args={["#a7c7e7", 80, 260]} />
          <Sunlight />
          <Sky turbidity={7} rayleigh={2} mieCoefficient={0.005} mieDirectionalG={0.9} inclination={0.48} />
          <Stars radius={300} depth={40} count={2500} factor={3} fade speed={0.2} />

          <Player resetKey={resetKey} />
          <Ground />
          <Trees />
          <Rocks />

          <PointerLockControls
            ref={plcRef}
            onLock={() => setLocked(true)}
            onUnlock={() => setLocked(false)}
            selector="#__canvas_lock_target__"
          />
        </Canvas>
      </KeyboardControls>

      {/* Transparent overlay to make it easy to click/lock */}
      <button
        id="__canvas_lock_target__"
        aria-label="Lock pointer"
        title="Click to play"
        onClick={() => plcRef.current?.lock?.()}
        className="absolute inset-0 z-[1] cursor-crosshair bg-transparent"
      />

      <HUD
        controlsRef={plcRef}
        locked={locked}
        onReset={() => setResetKey((n) => n + 1)}
      />
    </div>
  );
}
