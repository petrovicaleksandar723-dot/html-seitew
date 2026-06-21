"use client";

import { Suspense, useMemo, useRef } from "react";
import * as THREE from "three";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { Environment, Lightformer, AdaptiveDpr, Float } from "@react-three/drei";
import { EffectComposer, Bloom, ChromaticAberration, Vignette } from "@react-three/postprocessing";
import { Shards } from "@/components/render/shards";
import { Monoliths } from "@/components/render/monoliths";

function scrollRatio() {
  const max = document.documentElement.scrollHeight - window.innerHeight;
  return max > 0 ? THREE.MathUtils.clamp(window.scrollY / max, 0, 1) : 0;
}

/* scroll-scrubbed camera flight */
const CAM = [
  new THREE.Vector3(0, 1.5, 9),
  new THREE.Vector3(7, 2, 3),
  new THREE.Vector3(4, -1.5, -2),
  new THREE.Vector3(-6, 1, -6),
  new THREE.Vector3(-3, 1.6, -10),
  new THREE.Vector3(2.4, 1.8, -10),
  new THREE.Vector3(0, 1.8, -8.5),
];
const LOOK = [
  new THREE.Vector3(0, 0.5, 0),
  new THREE.Vector3(0, 0.5, -2),
  new THREE.Vector3(0, 0, -5),
  new THREE.Vector3(0, 0.9, -11),
  new THREE.Vector3(0, 1, -14),
  new THREE.Vector3(0, 1, -14.5),
  new THREE.Vector3(0, 1, -15),
];

function CameraRig() {
  const camera = useThree((s) => s.camera);
  const camPath = useMemo(() => new THREE.CatmullRomCurve3(CAM, false, "catmullrom", 0.4), []);
  const lookPath = useMemo(() => new THREE.CatmullRomCurve3(LOOK, false, "catmullrom", 0.4), []);
  const t = useRef(0);
  const lv = useRef(new THREE.Vector3());
  useFrame((_, dt) => {
    t.current = THREE.MathUtils.damp(t.current, scrollRatio(), 5, dt);
    const tt = THREE.MathUtils.clamp(t.current, 0.0001, 0.9999);
    camPath.getPointAt(tt, camera.position);
    lookPath.getPointAt(tt, lv.current);
    camera.lookAt(lv.current);
  });
  return null;
}

/* hero — a faceted glass crystal with a glowing core */
function Crystal() {
  const reduce = useMemo(() => typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches, []);
  const shell = useRef<THREE.Mesh>(null!);
  const core = useRef<THREE.Mesh>(null!);
  useFrame((_, dt) => {
    if (reduce) return;
    shell.current.rotation.y += dt * 0.16;
    shell.current.rotation.x += dt * 0.05;
    core.current.rotation.y -= dt * 0.3;
    const p = scrollRatio();
    const s = 2.2 * (1 + Math.sin(p * Math.PI) * 0.06);
    shell.current.scale.setScalar(s);
  });
  return (
    <Float speed={1.1} rotationIntensity={0.15} floatIntensity={0.5}>
      <group position={[0, 0.5, 0]}>
        <mesh ref={shell} scale={2.2}>
          <icosahedronGeometry args={[1, 0]} />
          <meshStandardMaterial
            color="#e9c887"
            metalness={0.7}
            roughness={0.16}
            emissive="#a87f3e"
            emissiveIntensity={0.35}
            envMapIntensity={1.5}
            flatShading
          />
        </mesh>
        <mesh ref={core} scale={0.85}>
          <icosahedronGeometry args={[1, 1]} />
          <meshStandardMaterial color="#f1d6a0" emissive="#d8b274" emissiveIntensity={2.6} roughness={0.2} metalness={0.6} flatShading />
        </mesh>
        <pointLight intensity={4} distance={9} color="#f1d6a0" />
      </group>
    </Float>
  );
}

function Contents() {
  return (
    <>
      <color attach="background" args={["#060504"]} />
      <fog attach="fog" args={["#060504", 14, 42]} />
      {/* explicit lighting so surfaces render even where the env map can't
          generate (headless / weak GPUs) — never rely on reflections alone */}
      <ambientLight intensity={0.85} />
      <hemisphereLight args={["#fff1da", "#241a12", 0.7]} />
      <directionalLight position={[6, 8, 4]} intensity={1.6} color="#fff1da" />
      <directionalLight position={[-6, 3, 6]} intensity={0.8} color="#9fb8ff" />
      <pointLight position={[0, 2, 6]} intensity={3} distance={20} color="#ffe9c4" />
      <pointLight position={[0, 1, -14]} intensity={4} distance={20} color="#ffe9c4" />

      {/* inline studio reflections — NO external HDR (nothing to suspend on) */}
      <Environment resolution={256}>
        <Lightformer intensity={2.4} position={[0, 5, -6]} scale={[12, 6, 1]} color="#fff1da" />
        <Lightformer intensity={1.6} position={[-7, 2, 2]} scale={[8, 8, 1]} color="#d8b274" />
        <Lightformer intensity={1.2} position={[7, -2, 4]} scale={[8, 8, 1]} color="#9fb8ff" />
        <Lightformer intensity={1.4} position={[0, -4, -8]} scale={[10, 4, 1]} color="#f1d6a0" />
      </Environment>

      <CameraRig />
      <Crystal />
      <Shards />
      <Monoliths />

      {/* gold core glowing behind the monoliths at journey's end */}
      <mesh position={[0, 1, -19.5]}>
        <icosahedronGeometry args={[0.9, 0]} />
        <meshStandardMaterial color="#f1d6a0" emissive="#d8b274" emissiveIntensity={2.4} flatShading metalness={0.7} roughness={0.2} />
      </mesh>
      <pointLight position={[0, 1, -19.5]} intensity={7} distance={16} color="#f1d6a0" />
    </>
  );
}

export function RenderScene() {
  return (
    <div className="pointer-events-none fixed inset-0 z-0">
      <Canvas
        dpr={[1, 1.6]}
        performance={{ min: 0.5 }}
        gl={{ antialias: true, preserveDrawingBuffer: true, powerPreference: "high-performance", toneMapping: THREE.ACESFilmicToneMapping, toneMappingExposure: 1.1 }}
        camera={{ fov: 38, position: [0, 1.5, 9], near: 0.1, far: 80 }}
      >
        <Suspense fallback={null}>
          <Contents />
        </Suspense>
        <EffectComposer multisampling={0}>
          <Bloom intensity={0.9} luminanceThreshold={0.5} luminanceSmoothing={0.25} mipmapBlur radius={0.75} />
          <ChromaticAberration offset={new THREE.Vector2(0.0009, 0.0009)} radialModulation={false} modulationOffset={0} />
          <Vignette eskil={false} offset={0.22} darkness={0.8} />
        </EffectComposer>
        <AdaptiveDpr pixelated={false} />
      </Canvas>
    </div>
  );
}
