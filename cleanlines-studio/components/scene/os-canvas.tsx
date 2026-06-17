"use client";

import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { useVideoTexture, useTexture, Environment, Billboard } from "@react-three/drei";
import { EffectComposer, Bloom, Vignette } from "@react-three/postprocessing";
import {
  Component,
  Suspense,
  useMemo,
  useRef,
  type MutableRefObject,
  type ReactNode,
} from "react";
import * as THREE from "three";
import { asset } from "@/lib/asset";

const GOLD = "#d8b274";
const GOLD_BRIGHT = "#f4d79e";
const R = 1.65;

type NumRef = MutableRefObject<number>;

const CW = 0.74;
const CH = 0.98;

// world locations + the clip that "bloops" out of each
const MARKERS = [
  { lat: 40, lng: -74, src: asset("/videos/reel-1.mp4") }, // New York
  { lat: 51, lng: 0, src: asset("/videos/reel-2.mp4") }, // London
  { lat: 35, lng: 139, src: asset("/videos/reel-3.mp4") }, // Tokyo
  { lat: -23, lng: -46, src: asset("/videos/example-1.mp4") }, // São Paulo
  { lat: 1, lng: 103, src: asset("/videos/ambient-1.mp4") }, // Singapore
  { lat: -33, lng: 151, src: asset("/videos/ambient-2.mp4") }, // Sydney
];

function latLngToVec(radius: number, lat: number, lng: number) {
  const phi = ((90 - lat) * Math.PI) / 180;
  const theta = ((lng + 180) * Math.PI) / 180;
  return new THREE.Vector3(
    -radius * Math.sin(phi) * Math.cos(theta),
    radius * Math.cos(phi),
    radius * Math.sin(phi) * Math.sin(theta)
  );
}

function easeOutBack(x: number) {
  const c1 = 1.70158;
  const c3 = c1 + 1;
  return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2);
}

/* ---------- realistic earth ---------- */
function Earth() {
  const [day, night, topo] = useTexture([
    "https://cdn.jsdelivr.net/npm/three-globe/example/img/earth-blue-marble.jpg",
    "https://cdn.jsdelivr.net/npm/three-globe/example/img/earth-night.jpg",
    "https://cdn.jsdelivr.net/npm/three-globe/example/img/earth-topology.png",
  ]);
  return (
    <mesh>
      <sphereGeometry args={[R, 96, 96]} />
      <meshStandardMaterial
        map={day}
        emissiveMap={night}
        emissive="#ffcaa0"
        emissiveIntensity={0.65}
        bumpMap={topo}
        bumpScale={0.05}
        metalness={0.1}
        roughness={0.85}
        envMapIntensity={0.5}
      />
    </mesh>
  );
}

function EarthFallback() {
  return (
    <mesh>
      <sphereGeometry args={[R, 64, 64]} />
      <meshStandardMaterial color="#0c2c52" emissive="#06203f" emissiveIntensity={0.4} roughness={0.7} metalness={0.2} />
    </mesh>
  );
}

function Atmosphere() {
  return (
    <mesh scale={1.14}>
      <sphereGeometry args={[R, 48, 48]} />
      <meshBasicMaterial color="#3e8bff" transparent opacity={0.12} side={THREE.BackSide} />
    </mesh>
  );
}

/* ---------- video card ---------- */
function Frame() {
  return (
    <mesh>
      <boxGeometry args={[CW + 0.05, CH + 0.05, 0.04]} />
      <meshStandardMaterial color="#0c0a08" emissive={GOLD} emissiveIntensity={0.2} metalness={0.8} roughness={0.3} envMapIntensity={1.2} />
    </mesh>
  );
}
function FallbackFace() {
  return (
    <group>
      <Frame />
      <mesh position={[0, 0, 0.03]}>
        <planeGeometry args={[CW, CH]} />
        <meshStandardMaterial color="#161009" emissive={GOLD} emissiveIntensity={0.3} />
      </mesh>
    </group>
  );
}
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
        <planeGeometry args={[CW, CH]} />
        <meshBasicMaterial map={texture} toneMapped={false} />
      </mesh>
    </group>
  );
}
class TextureBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    return this.state.failed ? <FallbackFace /> : this.props.children;
  }
}

/* marker: glowing pin on the globe + beam + popping billboard card */
function Marker({ lat, lng, src, index }: { lat: number; lng: number; src: string; index: number }) {
  const surface = useMemo(() => latLngToVec(R + 0.01, lat, lng), [lat, lng]);
  const cardPos = useMemo(() => latLngToVec(R + 1.25, lat, lng), [lat, lng]);
  const lineGeo = useMemo(
    () => new THREE.BufferGeometry().setFromPoints([surface, cardPos]),
    [surface, cardPos]
  );
  const card = useRef<THREE.Group>(null);
  const t = useRef(-index * 0.45);
  useFrame((_, dt) => {
    if (!card.current) return;
    t.current += dt;
    const x = Math.min(Math.max(t.current, 0), 1);
    card.current.scale.setScalar(Math.max(0.001, easeOutBack(x)));
  });
  return (
    <group>
      <mesh position={surface}>
        <sphereGeometry args={[0.045, 14, 14]} />
        <meshBasicMaterial color={GOLD_BRIGHT} toneMapped={false} />
      </mesh>
      <primitive
        object={new THREE.Line(lineGeo, new THREE.LineBasicMaterial({ color: GOLD, transparent: true, opacity: 0.45 }))}
      />
      <group position={cardPos}>
        <group ref={card} scale={0}>
          <Billboard>
            <TextureBoundary>
              <Suspense fallback={<FallbackFace />}>
                <VideoFace src={src} />
              </Suspense>
            </TextureBoundary>
          </Billboard>
        </group>
      </group>
    </group>
  );
}

/* spinning globe with everything attached */
function Globe({ progress, velocity }: { progress?: NumRef; velocity?: NumRef }) {
  const g = useRef<THREE.Group>(null);
  useFrame((_, dt) => {
    if (!g.current) return;
    const v = Math.min(Math.abs(velocity?.current ?? 0) * 9, 4);
    g.current.rotation.y += dt * (0.08 + v) + (progress?.current ?? 0) * 0.04;
  });
  return (
    <group ref={g} rotation={[0.35, 0, 0.1]}>
      <Suspense fallback={<EarthFallback />}>
        <Earth />
      </Suspense>
      <Atmosphere />
      {MARKERS.map((m, i) => (
        <Marker key={i} {...m} index={i} />
      ))}
    </group>
  );
}

/* pointer parallax + scroll-driven downward travel */
function Rig({ progress, children }: { progress?: NumRef; children: ReactNode }) {
  const g = useRef<THREE.Group>(null);
  const { pointer } = useThree();
  useFrame(() => {
    if (!g.current) return;
    g.current.rotation.y += (pointer.x * 0.3 - g.current.rotation.y) * 0.05;
    g.current.rotation.x += (-pointer.y * 0.2 - g.current.rotation.x) * 0.05;
    const targetY = -(progress?.current ?? 0) * 2.2;
    g.current.position.y += (targetY - g.current.position.y) * 0.08;
  });
  return <group ref={g}>{children}</group>;
}

export default function OsCanvas({ progress, velocity }: { progress?: NumRef; velocity?: NumRef }) {
  return (
    <Canvas
      dpr={[1, 2]}
      gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
      camera={{ position: [0, 0.6, 7.4], fov: 42 }}
    >
      <ambientLight intensity={0.45} />
      <directionalLight position={[5, 3, 5]} intensity={2.4} color="#fff1cf" />
      <pointLight position={[-6, 1, 3]} intensity={55} color="#3e6bff" />
      <pointLight position={[5, -2, -2]} intensity={40} color="#ff3da6" />
      <Suspense fallback={null}>
        <Environment preset="sunset" />
      </Suspense>

      <Rig progress={progress}>
        <Globe progress={progress} velocity={velocity} />
      </Rig>

      <EffectComposer multisampling={4}>
        <Bloom intensity={1.0} luminanceThreshold={0.25} luminanceSmoothing={0.6} mipmapBlur />
        <Vignette eskil={false} offset={0.2} darkness={0.82} />
      </EffectComposer>
    </Canvas>
  );
}
