"use client";

import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { Float, useVideoTexture, Environment, Billboard } from "@react-three/drei";
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

type NumRef = MutableRefObject<number>;

const NODE_VIDEOS = [
  asset("/videos/reel-1.mp4"),
  asset("/videos/reel-2.mp4"),
  asset("/videos/reel-3.mp4"),
  asset("/videos/example-1.mp4"),
  asset("/videos/ambient-1.mp4"),
  asset("/videos/ambient-2.mp4"),
];

const CW = 0.86;
const CH = 1.12;

/* faceted gold core */
function Core({ progress }: { progress?: NumRef }) {
  const ref = useRef<THREE.Mesh>(null);
  const inner = useRef<THREE.Mesh>(null);
  useFrame((_, delta) => {
    const p = progress?.current ?? 0;
    if (ref.current) {
      ref.current.rotation.y += delta * 0.25 + p * 0.05;
      ref.current.rotation.x += delta * 0.1;
      const s = 1 + p * 0.2;
      ref.current.scale.setScalar(s);
    }
    if (inner.current) inner.current.rotation.y -= delta * 0.4;
  });
  return (
    <Float speed={1.2} floatIntensity={0.5} rotationIntensity={0.2}>
      <mesh ref={ref}>
        <icosahedronGeometry args={[1.05, 0]} />
        <meshStandardMaterial
          color="#e7c483"
          metalness={1}
          roughness={0.15}
          envMapIntensity={1.6}
          emissive="#3a2a10"
          emissiveIntensity={0.35}
          flatShading
        />
      </mesh>
      <mesh ref={inner} scale={0.55}>
        <icosahedronGeometry args={[1, 0]} />
        <meshStandardMaterial
          color={GOLD_BRIGHT}
          emissive={GOLD_BRIGHT}
          emissiveIntensity={2.2}
          toneMapped={false}
        />
      </mesh>
    </Float>
  );
}

function Frame() {
  return (
    <mesh>
      <boxGeometry args={[CW + 0.06, CH + 0.06, 0.05]} />
      <meshStandardMaterial
        color="#0c0a08"
        emissive={GOLD}
        emissiveIntensity={0.18}
        metalness={0.8}
        roughness={0.3}
        envMapIntensity={1.2}
      />
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
    if (this.state.failed) return <FallbackFace />;
    return this.props.children;
  }
}

function Nodes({
  progress,
  velocity,
}: {
  progress?: NumRef;
  velocity?: NumRef;
}) {
  const ring = useRef<THREE.Group>(null);
  const nodes = useMemo(
    () =>
      NODE_VIDEOS.map((src, i) => {
        const a = (i / NODE_VIDEOS.length) * Math.PI * 2;
        const r = 3.2;
        return {
          src,
          a,
          pos: new THREE.Vector3(
            Math.cos(a) * r,
            Math.sin(a * 1.5) * 0.5,
            Math.sin(a) * r
          ),
        };
      }),
    []
  );

  useFrame((_, delta) => {
    if (!ring.current) return;
    const v = Math.min(Math.abs(velocity?.current ?? 0) * 9, 4);
    ring.current.rotation.y += delta * (0.18 + v) + (progress?.current ?? 0) * 0.04;
  });

  return (
    <group ref={ring}>
      {nodes.map((n, i) => {
        const geo = new THREE.BufferGeometry().setFromPoints([
          new THREE.Vector3(0, 0, 0),
          n.pos,
        ]);
        return (
          <group key={i}>
            <primitive
              object={
                new THREE.Line(
                  geo,
                  new THREE.LineBasicMaterial({
                    color: GOLD,
                    transparent: true,
                    opacity: 0.3,
                  })
                )
              }
            />
            <Float speed={2.2} floatIntensity={0.9} rotationIntensity={0}>
              <group position={n.pos}>
                <Billboard>
                  <TextureBoundary>
                    <Suspense fallback={<FallbackFace />}>
                      <VideoFace src={n.src} />
                    </Suspense>
                  </TextureBoundary>
                </Billboard>
              </group>
            </Float>
          </group>
        );
      })}
    </group>
  );
}

/* pointer parallax (hover/swipe) + scroll-driven downward travel */
function Rig({
  progress,
  children,
}: {
  progress?: NumRef;
  children: ReactNode;
}) {
  const g = useRef<THREE.Group>(null);
  const { pointer } = useThree();
  useFrame(() => {
    if (!g.current) return;
    g.current.rotation.y += (pointer.x * 0.3 - g.current.rotation.y) * 0.05;
    g.current.rotation.x += (-pointer.y * 0.2 - g.current.rotation.x) * 0.05;
    const targetY = -(progress?.current ?? 0) * 3.4;
    g.current.position.y += (targetY - g.current.position.y) * 0.08;
  });
  return <group ref={g}>{children}</group>;
}

export default function OsCanvas({
  progress,
  velocity,
}: {
  progress?: NumRef;
  velocity?: NumRef;
}) {
  return (
    <Canvas
      dpr={[1, 2]}
      gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
      camera={{ position: [0, 1.1, 7.6], fov: 42 }}
    >
      <ambientLight intensity={0.35} />
      <directionalLight position={[5, 6, 5]} intensity={2} color="#fff1cf" />
      <pointLight position={[-6, 0, 2]} intensity={60} color="#3e6bff" />
      <pointLight position={[5, -2, -2]} intensity={45} color="#ff3da6" />
      <pointLight position={[0, 0, 0]} intensity={20} color={GOLD_BRIGHT} />
      <Suspense fallback={null}>
        <Environment preset="sunset" />
      </Suspense>

      <Rig progress={progress}>
        <Core progress={progress} />
        <Suspense fallback={null}>
          <Nodes progress={progress} velocity={velocity} />
        </Suspense>
      </Rig>

      <EffectComposer multisampling={4}>
        <Bloom intensity={1.1} luminanceThreshold={0.22} luminanceSmoothing={0.6} mipmapBlur />
        <Vignette eskil={false} offset={0.2} darkness={0.85} />
      </EffectComposer>
    </Canvas>
  );
}
