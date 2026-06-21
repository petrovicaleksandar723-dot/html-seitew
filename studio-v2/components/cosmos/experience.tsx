"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import * as THREE from "three";
import { useFrame, useThree } from "@react-three/fiber";
import { RoundedBox, Float } from "@react-three/drei";
import { asset } from "@/lib/asset";

const REELS = [
  asset("/videos/reel-1.mp4"),
  asset("/videos/reel-2.mp4"),
  asset("/videos/reel-3.mp4"),
  asset("/videos/reel-4.mp4"),
  asset("/videos/final.mp4"),
];

/* ---- camera path (scroll-scrubbed flight through the cosmos) ---- */
const CAM_POINTS = [
  new THREE.Vector3(0, 0.4, 13),
  new THREE.Vector3(3.2, 1.2, 7),
  new THREE.Vector3(-3.4, -0.6, 1),
  new THREE.Vector3(3.0, 1.4, -6),
  new THREE.Vector3(-2.2, -0.4, -13),
  new THREE.Vector3(0, 0.6, -21),
  new THREE.Vector3(0, 0, -30),
];
const LOOK_POINTS = [
  new THREE.Vector3(0, 0.2, 6),
  new THREE.Vector3(0, 0.4, 2),
  new THREE.Vector3(0, -0.2, -4),
  new THREE.Vector3(0, 0.4, -10),
  new THREE.Vector3(0, 0, -17),
  new THREE.Vector3(0, 0.2, -26),
  new THREE.Vector3(0, 0, -34),
];

export function CameraRig() {
  const camera = useThree((s) => s.camera);
  const camPath = useMemo(() => new THREE.CatmullRomCurve3(CAM_POINTS, false, "catmullrom", 0.4), []);
  const lookPath = useMemo(() => new THREE.CatmullRomCurve3(LOOK_POINTS, false, "catmullrom", 0.4), []);
  const t = useRef(0);
  const lookV = useRef(new THREE.Vector3());

  useFrame((_, dt) => {
    const max = document.documentElement.scrollHeight - window.innerHeight;
    const p = max > 0 ? window.scrollY / max : 0;
    // smooth on top of Lenis to kill micro-jitter
    t.current = THREE.MathUtils.damp(t.current, THREE.MathUtils.clamp(p, 0, 1), 5, dt);
    const tt = THREE.MathUtils.clamp(t.current, 0.0001, 0.9999);
    camPath.getPointAt(tt, camera.position);
    lookPath.getPointAt(tt, lookV.current);
    camera.lookAt(lookV.current);
  });
  return null;
}

/* ---- non-blocking video texture (never suspends the whole scene) ---- */
function useManualVideoTexture(src: string) {
  const [tex, setTex] = useState<THREE.VideoTexture | null>(null);
  useEffect(() => {
    const v = document.createElement("video");
    v.crossOrigin = "anonymous";
    v.muted = true;
    v.loop = true;
    v.playsInline = true;
    v.preload = "auto";
    v.src = src;
    const t = new THREE.VideoTexture(v);
    t.colorSpace = THREE.SRGBColorSpace;
    const onCanPlay = () => {
      v.play().catch(() => {});
      setTex(t);
    };
    v.addEventListener("canplay", onCanPlay, { once: true });
    v.load();
    // also try immediately in case it's cached
    v.play().catch(() => {});
    return () => {
      v.removeEventListener("canplay", onCanPlay);
      v.pause();
      v.src = "";
      t.dispose();
    };
  }, [src]);
  return tex;
}

/* ---- a floating phone playing a brand reel ---- */
function FloatingPhone({
  src,
  position,
  rotation = [0, 0, 0],
  scale = 1,
}: {
  src: string;
  position: [number, number, number];
  rotation?: [number, number, number];
  scale?: number;
}) {
  const tex = useManualVideoTexture(src);
  return (
    <Float speed={1.4} rotationIntensity={0.25} floatIntensity={0.5}>
      <group position={position} rotation={rotation as unknown as THREE.Euler} scale={scale}>
        <RoundedBox args={[1.05, 2.1, 0.12]} radius={0.09} smoothness={4} castShadow>
          <meshStandardMaterial color="#0c0c10" roughness={0.35} metalness={0.6} />
        </RoundedBox>
        {/* gold rim */}
        <RoundedBox args={[1.1, 2.15, 0.1]} radius={0.1} smoothness={4} position={[0, 0, -0.02]}>
          <meshStandardMaterial color="#d8b274" roughness={0.3} metalness={0.9} emissive="#a87f3e" emissiveIntensity={0.25} />
        </RoundedBox>
        {/* screen (dark until its reel is ready — never blocks the scene) */}
        <mesh position={[0, 0, 0.066]}>
          <planeGeometry args={[0.9, 1.92]} />
          <meshBasicMaterial map={tex ?? null} color={tex ? "#ffffff" : "#0a0a0c"} toneMapped={false} />
        </mesh>
        {/* screen glow */}
        <pointLight position={[0, 0, 0.6]} intensity={2.4} distance={3.4} color="#bfe6ff" />
      </group>
    </Float>
  );
}

/* ---- drifting champagne particle field ---- */
function Particles({ count = 1400 }: { count?: number }) {
  const ref = useRef<THREE.Points>(null!);
  const geo = useMemo(() => {
    const g = new THREE.BufferGeometry();
    const pos = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      pos[i * 3] = (Math.random() - 0.5) * 24;
      pos[i * 3 + 1] = (Math.random() - 0.5) * 16;
      pos[i * 3 + 2] = (Math.random() - 0.5) * 50 - 12;
    }
    g.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    return g;
  }, [count]);

  const sprite = useMemo(() => {
    const c = document.createElement("canvas");
    c.width = c.height = 64;
    const x = c.getContext("2d")!;
    const grad = x.createRadialGradient(32, 32, 0, 32, 32, 32);
    grad.addColorStop(0, "rgba(244,215,160,1)");
    grad.addColorStop(0.4, "rgba(216,178,116,0.6)");
    grad.addColorStop(1, "rgba(216,178,116,0)");
    x.fillStyle = grad;
    x.fillRect(0, 0, 64, 64);
    return new THREE.CanvasTexture(c);
  }, []);

  useFrame((_, dt) => {
    ref.current.rotation.y += dt * 0.02;
    ref.current.rotation.x += dt * 0.005;
  });

  return (
    <points ref={ref} geometry={geo}>
      <pointsMaterial
        size={0.14}
        map={sprite}
        transparent
        depthWrite={false}
        blending={THREE.AdditiveBlending}
        color="#f1d6a0"
        sizeAttenuation
      />
    </points>
  );
}

/* ---- the whole scene contents ---- */
export function Experience() {
  return (
    <>
      <color attach="background" args={["#060504"]} />
      <fog attach="fog" args={["#060504", 14, 40]} />
      <ambientLight intensity={0.35} />
      <hemisphereLight args={["#fff1da", "#1a1420", 0.4]} />
      <directionalLight position={[6, 8, 6]} intensity={1.1} color="#fff1da" />
      <pointLight position={[0, 0, -16]} intensity={6} distance={26} color="#d8b274" />

      <CameraRig />
      <Particles />

      {/* phones placed along the flight path */}
      <FloatingPhone src={REELS[0]} position={[-2.6, 0.6, 6]} rotation={[0, 0.5, 0.05]} scale={1.1} />
      <FloatingPhone src={REELS[1]} position={[2.8, -0.4, 1.5]} rotation={[0, -0.5, -0.04]} scale={1.0} />
      <FloatingPhone src={REELS[2]} position={[-2.4, 0.9, -4.5]} rotation={[0, 0.45, 0.06]} scale={1.15} />
      <FloatingPhone src={REELS[3]} position={[2.6, -0.6, -10]} rotation={[0, -0.5, -0.05]} scale={1.05} />
      <FloatingPhone src={REELS[4]} position={[0, 0.3, -17.5]} rotation={[0, 0.1, 0]} scale={1.25} />

      {/* gold "core" glow at journey's end */}
      <mesh position={[0, 0, -26]}>
        <icosahedronGeometry args={[1.1, 1]} />
        <meshStandardMaterial color="#f1d6a0" emissive="#d8b274" emissiveIntensity={2.2} roughness={0.2} metalness={0.7} flatShading />
      </mesh>
      <pointLight position={[0, 0, -26]} intensity={9} distance={20} color="#f1d6a0" />
    </>
  );
}
