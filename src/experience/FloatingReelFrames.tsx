import { useRef, Suspense } from "react";
import { useFrame } from "@react-three/fiber";
import { useVideoTexture, RoundedBox } from "@react-three/drei";
import * as THREE from "three";

interface FrameDef {
  src: string;
  position: [number, number, number];
  rotation: [number, number, number];
  scale: number;
  speed: number;
}

const FRAMES: FrameDef[] = [
  { src: "/assets/videos/reel-1.mp4", position: [-4.4, 1.5, -1], rotation: [0, 0.5, 0.05], scale: 1, speed: 0.6 },
  { src: "/assets/videos/reel-2.mp4", position: [4.6, -0.6, -0.5], rotation: [0, -0.55, -0.06], scale: 1.1, speed: 0.5 },
  { src: "/assets/videos/reel-3.mp4", position: [-3.6, -1.9, 1.2], rotation: [0, 0.4, -0.04], scale: 0.82, speed: 0.7 },
  { src: "/assets/videos/show-1.mp4", position: [3.6, 2.2, 0.8], rotation: [0, -0.4, 0.05], scale: 0.8, speed: 0.65 },
  { src: "/assets/videos/reel-4.mp4", position: [-5.2, -0.4, -1.6], rotation: [0, 0.6, 0.03], scale: 0.7, speed: 0.55 },
  { src: "/assets/videos/show-2.mp4", position: [5.4, 1.4, -1.4], rotation: [0, -0.6, -0.04], scale: 0.68, speed: 0.62 },
];

function ReelPlane({ def }: { def: FrameDef }) {
  const group = useRef<THREE.Group>(null);
  const texture = useVideoTexture(def.src, {
    muted: true,
    loop: true,
    start: true,
    crossOrigin: "anonymous",
  });
  texture.colorSpace = THREE.SRGBColorSpace;

  useFrame((state) => {
    if (!group.current) return;
    const t = state.clock.elapsedTime * def.speed;
    group.current.position.y = def.position[1] + Math.sin(t) * 0.25;
    group.current.position.x = def.position[0] + Math.cos(t * 0.7) * 0.12;
    group.current.rotation.z = def.rotation[2] + Math.sin(t * 0.5) * 0.04;
  });

  return (
    <group ref={group} position={def.position} rotation={def.rotation} scale={def.scale}>
      {/* gold frame */}
      <RoundedBox args={[1.32, 2.3, 0.06]} radius={0.06} smoothness={4} castShadow>
        <meshPhysicalMaterial
          color="#0d0a07"
          metalness={0.9}
          roughness={0.25}
          clearcoat={1}
          emissive="#d6a65f"
          emissiveIntensity={0.08}
        />
      </RoundedBox>
      {/* video surface */}
      <mesh position={[0, 0, 0.05]}>
        <planeGeometry args={[1.18, 2.12]} />
        <meshBasicMaterial map={texture} toneMapped={false} />
      </mesh>
    </group>
  );
}

/** Lightweight glass panel — used on mobile instead of heavy video textures. */
function GlassPanel({ def }: { def: FrameDef }) {
  const group = useRef<THREE.Group>(null);
  useFrame((state) => {
    if (!group.current) return;
    const t = state.clock.elapsedTime * def.speed;
    group.current.position.y = def.position[1] + Math.sin(t) * 0.25;
    group.current.rotation.z = def.rotation[2] + Math.sin(t * 0.5) * 0.04;
  });
  return (
    <group ref={group} position={def.position} rotation={def.rotation} scale={def.scale}>
      <RoundedBox args={[1.18, 2.1, 0.06]} radius={0.06} smoothness={3}>
        <meshPhysicalMaterial
          color="#0d0a07"
          metalness={0.85}
          roughness={0.2}
          clearcoat={1}
          emissive="#d6a65f"
          emissiveIntensity={0.18}
        />
      </RoundedBox>
    </group>
  );
}

interface Props {
  reduced?: boolean;
}

/** Floating reel/video planes orbiting the content engine. */
export default function FloatingReelFrames({ reduced = false }: Props) {
  const frames = reduced ? FRAMES.slice(0, 3) : FRAMES;
  return (
    <Suspense fallback={null}>
      {frames.map((def) =>
        reduced ? <GlassPanel key={def.src} def={def} /> : <ReelPlane key={def.src} def={def} />
      )}
    </Suspense>
  );
}
