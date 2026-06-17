"use client";

import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { useVideoTexture, useTexture, Environment, Billboard, RoundedBox } from "@react-three/drei";
import { EffectComposer, Bloom, HueSaturation, BrightnessContrast } from "@react-three/postprocessing";
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
const R = 1.5;

type NumRef = MutableRefObject<number>;

// world locations + the clip that "bloops" out of each
const MARKERS = [
  { lat: 40, lng: -74, src: asset("/videos/reel-1.mp4") }, // New York
  { lat: 51, lng: 0, src: asset("/videos/reel-2.mp4") }, // London
  { lat: 35, lng: 139, src: asset("/videos/reel-3.mp4") }, // Tokyo
  { lat: -30, lng: 140, src: asset("/videos/example-1.mp4") }, // Sydney-ish
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
        emissive="#ffdca8"
        emissiveIntensity={1.5}
        bumpMap={topo}
        bumpScale={0.07}
        metalness={0.05}
        roughness={0.9}
        envMapIntensity={0.6}
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
    <mesh scale={1.025}>
      <sphereGeometry args={[R, 64, 64]} />
      <meshBasicMaterial
        color="#2f6dd0"
        transparent
        opacity={0.06}
        side={THREE.BackSide}
        depthWrite={false}
      />
    </mesh>
  );
}

/* ---------- 3D phone showing the clip on its screen ---------- */
const PH_W = 0.58;
const PH_H = 1.18;
const SCR_W = 0.5;
const SCR_H = 1.06;

function PhoneBody({ children }: { children: ReactNode }) {
  return (
    <group>
      <RoundedBox args={[PH_W, PH_H, 0.07]} radius={0.075} smoothness={5}>
        <meshStandardMaterial color="#0a0a0c" metalness={0.95} roughness={0.22} envMapIntensity={1.7} />
      </RoundedBox>
      {/* screen well */}
      <mesh position={[0, 0, 0.033]}>
        <planeGeometry args={[SCR_W + 0.02, SCR_H + 0.02]} />
        <meshBasicMaterial color="#000000" />
      </mesh>
      {children}
      {/* notch */}
      <mesh position={[0, SCR_H / 2 - 0.02, 0.04]}>
        <planeGeometry args={[0.12, 0.03]} />
        <meshBasicMaterial color="#000000" />
      </mesh>
    </group>
  );
}

function PhoneVideo({ src }: { src: string }) {
  const texture = useVideoTexture(src, {
    crossOrigin: "anonymous",
    muted: true,
    loop: true,
    start: true,
    playsInline: true,
  });
  // cover-fill the portrait screen so the clip plays like a full-screen reel
  useFrame(() => {
    const img = texture.image as HTMLVideoElement | undefined;
    if (!img || !img.videoWidth) return;
    const a = img.videoWidth / img.videoHeight;
    const planeA = SCR_W / SCR_H;
    if (a > planeA) {
      const r = planeA / a;
      texture.repeat.set(r, 1);
      texture.offset.set((1 - r) / 2, 0);
    } else {
      const r = a / planeA;
      texture.repeat.set(1, r);
      texture.offset.set(0, (1 - r) / 2);
    }
  });
  return (
    <PhoneBody>
      <mesh position={[0, 0, 0.037]}>
        <planeGeometry args={[SCR_W, SCR_H]} />
        <meshBasicMaterial map={texture} toneMapped={false} />
      </mesh>
    </PhoneBody>
  );
}

function PhoneFallback() {
  return (
    <PhoneBody>
      <mesh position={[0, 0, 0.037]}>
        <planeGeometry args={[SCR_W, SCR_H]} />
        <meshStandardMaterial color="#161009" emissive={GOLD} emissiveIntensity={0.3} />
      </mesh>
    </PhoneBody>
  );
}

class TextureBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    return this.state.failed ? <PhoneFallback /> : this.props.children;
  }
}

/* marker: glowing pin on the globe + beam + popping billboard card */
function Marker({ lat, lng, src, index }: { lat: number; lng: number; src: string; index: number }) {
  const surface = useMemo(() => latLngToVec(R + 0.01, lat, lng), [lat, lng]);
  const cardPos = useMemo(() => latLngToVec(R + 0.95, lat, lng), [lat, lng]);
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
              <Suspense fallback={<PhoneFallback />}>
                <PhoneVideo src={src} />
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
    const v = Math.min(Math.abs(velocity?.current ?? 0) * 7, 3);
    g.current.rotation.y += dt * (0.03 + v) + (progress?.current ?? 0) * 0.05;
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

/* pointer parallax (hover / swipe) */
function Rig({ children }: { children: ReactNode }) {
  const g = useRef<THREE.Group>(null);
  const { pointer } = useThree();
  useFrame(() => {
    if (!g.current) return;
    g.current.rotation.y += (pointer.x * 0.3 - g.current.rotation.y) * 0.05;
    g.current.rotation.x += (-pointer.y * 0.2 - g.current.rotation.x) * 0.05;
  });
  return <group ref={g}>{children}</group>;
}

export default function OsCanvas({ progress, velocity }: { progress?: NumRef; velocity?: NumRef }) {
  return (
    <Canvas
      dpr={[1, 2]}
      gl={{
        antialias: true,
        alpha: true,
        powerPreference: "high-performance",
        toneMappingExposure: 1.35,
      }}
      camera={{ position: [0, 0.4, 9.6], fov: 40 }}
    >
      {/* low ambient + a strong sun = realistic day/night terminator (shadow) */}
      <ambientLight intensity={0.18} />
      <directionalLight position={[6, 2.5, 4]} intensity={4.4} color="#fff4dd" />
      <directionalLight position={[-3, 1, 3]} intensity={0.8} color="#bcd4ff" />
      <pointLight position={[-6, 0, 1]} intensity={28} color="#4f7bff" />
      <Suspense fallback={null}>
        <Environment preset="sunset" />
      </Suspense>

      <Rig>
        <Globe progress={progress} velocity={velocity} />
      </Rig>

      <EffectComposer multisampling={4}>
        <Bloom intensity={1.5} luminanceThreshold={0.18} luminanceSmoothing={0.65} mipmapBlur />
        <HueSaturation saturation={0.34} />
        <BrightnessContrast brightness={0.05} contrast={0.26} />
      </EffectComposer>
    </Canvas>
  );
}
