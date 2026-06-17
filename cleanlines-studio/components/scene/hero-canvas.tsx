"use client";

import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { Float, useVideoTexture } from "@react-three/drei";
import { EffectComposer, Bloom, Vignette } from "@react-three/postprocessing";
import { Component, Suspense, useMemo, useRef, type ReactNode } from "react";
import * as THREE from "three";
import { asset } from "@/lib/asset";

const GOLD = "#d8b274";
const GOLD_BRIGHT = "#f4d79e";

const CARD_W = 0.96;
const CARD_H = 1.46;

const CARDS = [
  { src: asset("/videos/showreel.mp4"), a: 0.3, r: 2.9, y: 0.7 },
  { src: asset("/videos/reel-1.mp4"), a: 1.75, r: 3.05, y: -0.5 },
  { src: asset("/videos/reel-2.mp4"), a: 3.2, r: 2.8, y: 1.15 },
  { src: asset("/videos/reel-3.mp4"), a: 4.7, r: 3.0, y: -0.9 },
];

/* ---------- Floating premium phone ---------- */
function Phone() {
  const group = useRef<THREE.Group>(null);
  useFrame((state) => {
    if (!group.current) return;
    group.current.rotation.z = Math.sin(state.clock.elapsedTime * 0.4) * 0.04;
  });
  return (
    <Float speed={1.4} rotationIntensity={0.25} floatIntensity={0.7}>
      <group ref={group} rotation={[0.04, -0.35, 0]}>
        <mesh castShadow>
          <boxGeometry args={[1.55, 3.2, 0.18]} />
          <meshStandardMaterial color="#0c0b09" metalness={0.9} roughness={0.28} />
        </mesh>
        <mesh position={[0, 0, 0.095]}>
          <boxGeometry args={[1.42, 3.06, 0.02]} />
          <meshStandardMaterial color="#000000" emissive={GOLD} emissiveIntensity={0.12} metalness={0.6} roughness={0.4} />
        </mesh>
        <mesh position={[0, 0, 0.108]}>
          <planeGeometry args={[1.34, 2.98]} />
          <meshBasicMaterial color="#14110b" />
        </mesh>
        {[1.02, 0.32, -0.42].map((y, i) => (
          <mesh key={i} position={[0, y, 0.12]}>
            <planeGeometry args={[1.16, 0.52]} />
            <meshStandardMaterial color="#1c1710" emissive={GOLD} emissiveIntensity={0.35 - i * 0.07} />
          </mesh>
        ))}
        <mesh position={[0, -1.05, 0.122]}>
          <planeGeometry args={[1.16, 0.34]} />
          <meshStandardMaterial color={GOLD} emissive={GOLD_BRIGHT} emissiveIntensity={0.6} />
        </mesh>
      </group>
    </Float>
  );
}

/* ---------- Card frame (shared) ---------- */
function Frame() {
  return (
    <mesh>
      <boxGeometry args={[CARD_W + 0.08, CARD_H + 0.08, 0.05]} />
      <meshStandardMaterial color="#0c0a08" emissive={GOLD} emissiveIntensity={0.16} metalness={0.7} roughness={0.34} />
    </mesh>
  );
}

/* Emissive fallback (used while loading or if a video can't decode) */
function FallbackCard() {
  return (
    <group>
      <Frame />
      <mesh position={[0, 0, 0.03]}>
        <planeGeometry args={[CARD_W, CARD_H]} />
        <meshStandardMaterial color="#161009" emissive={GOLD} emissiveIntensity={0.3} />
      </mesh>
      <mesh position={[0, 0.45, 0.04]}>
        <planeGeometry args={[CARD_W * 0.55, 0.18]} />
        <meshBasicMaterial color={GOLD_BRIGHT} />
      </mesh>
    </group>
  );
}

/* Live video texture card */
function VideoFace({ src }: { src: string }) {
  const texture = useVideoTexture(src, {
    crossOrigin: "anonymous",
    muted: true,
    loop: true,
    start: true,
    playsInline: true,
  });
  return (
    <group>
      <Frame />
      <mesh position={[0, 0, 0.03]}>
        <planeGeometry args={[CARD_W, CARD_H]} />
        <meshBasicMaterial map={texture} toneMapped={false} />
      </mesh>
    </group>
  );
}

/* Error boundary so a failed texture degrades to FallbackCard instead of crashing the canvas */
class TextureBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    if (this.state.failed) return <FallbackCard />;
    return this.props.children;
  }
}

function VideoCards() {
  const ring = useRef<THREE.Group>(null);
  useFrame((_, delta) => {
    if (ring.current) ring.current.rotation.y += delta * 0.12;
  });
  return (
    <group ref={ring}>
      {CARDS.map((c, i) => (
        <Float key={i} speed={1.8} rotationIntensity={0.4} floatIntensity={1.1}>
          <group
            position={[Math.cos(c.a) * c.r, c.y, Math.sin(c.a) * c.r]}
            rotation={[0, -c.a + Math.PI / 2, 0]}
          >
            <TextureBoundary>
              <Suspense fallback={<FallbackCard />}>
                <VideoFace src={c.src} />
              </Suspense>
            </TextureBoundary>
          </group>
        </Float>
      ))}
    </group>
  );
}

function Rings() {
  const a = useRef<THREE.Mesh>(null);
  const b = useRef<THREE.Mesh>(null);
  useFrame((_, delta) => {
    if (a.current) a.current.rotation.z += delta * 0.08;
    if (b.current) b.current.rotation.z -= delta * 0.05;
  });
  return (
    <group rotation={[Math.PI / 2.3, 0, 0]}>
      <mesh ref={a}>
        <torusGeometry args={[3.7, 0.008, 16, 120]} />
        <meshStandardMaterial color={GOLD} emissive={GOLD} emissiveIntensity={2} />
      </mesh>
      <mesh ref={b} rotation={[0.4, 0, 0]}>
        <torusGeometry args={[4.4, 0.006, 16, 120]} />
        <meshStandardMaterial color={GOLD_BRIGHT} emissive={GOLD_BRIGHT} emissiveIntensity={1.4} />
      </mesh>
    </group>
  );
}

function Dust() {
  const ref = useRef<THREE.Points>(null);
  const positions = useMemo(() => {
    const n = 380;
    const arr = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) {
      arr[i * 3] = (Math.random() - 0.5) * 16;
      arr[i * 3 + 1] = (Math.random() - 0.5) * 11;
      arr[i * 3 + 2] = (Math.random() - 0.5) * 9;
    }
    return arr;
  }, []);
  useFrame((_, delta) => {
    if (ref.current) ref.current.rotation.y += delta * 0.015;
  });
  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={positions.length / 3} array={positions} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial size={0.026} color={GOLD_BRIGHT} transparent opacity={0.55} sizeAttenuation depthWrite={false} />
    </points>
  );
}

function ParallaxRig({ children }: { children: ReactNode }) {
  const group = useRef<THREE.Group>(null);
  const { pointer } = useThree();
  useFrame(() => {
    if (!group.current) return;
    group.current.rotation.y += (pointer.x * 0.28 - group.current.rotation.y) * 0.05;
    group.current.rotation.x += (-pointer.y * 0.18 - group.current.rotation.x) * 0.05;
  });
  return <group ref={group}>{children}</group>;
}

export default function HeroCanvas() {
  return (
    <Canvas
      dpr={[1, 2]}
      gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
      camera={{ position: [0, 0.3, 8.5], fov: 38 }}
    >
      <color attach="background" args={["#050505"]} />
      <fog attach="fog" args={["#050505", 9, 18]} />
      <ambientLight intensity={0.35} />
      <directionalLight position={[4, 6, 6]} intensity={1.6} color="#fff2d6" />
      <pointLight position={[-5, -2, 4]} intensity={40} color={GOLD} />
      <pointLight position={[3, 3, -4]} intensity={26} color={GOLD_BRIGHT} />

      <ParallaxRig>
        <Phone />
        <Suspense fallback={null}>
          <VideoCards />
        </Suspense>
        <Rings />
        <Dust />
      </ParallaxRig>

      <EffectComposer multisampling={4}>
        <Bloom intensity={0.8} luminanceThreshold={0.25} luminanceSmoothing={0.5} mipmapBlur />
        <Vignette eskil={false} offset={0.22} darkness={0.92} />
      </EffectComposer>
    </Canvas>
  );
}
