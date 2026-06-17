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
  { src: "/assets/videos/reel-1.mp4", position: [-4.2, 1.4, -1], rotation: [0, 0.5, 0.05], scale: 1, speed: 0.6 },
  { src: "/assets/videos/reel-2.mp4", position: [4.4, -0.6, -0.5], rotation: [0, -0.55, -0.06], scale: 1.1, speed: 0.5 },
  { src: "/assets/videos/reel-3.mp4", position: [-3.4, -1.8, 1.2], rotation: [0, 0.4, -0.04], scale: 0.8, speed: 0.7 },
  { src: "/assets/videos/show-1.mp4", position: [3.4, 2.1, 0.8], rotation: [0, -0.4, 0.05], scale: 0.78, speed: 0.65 },
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

/** Floating reel/video planes orbiting the content engine. */
export default function FloatingReelFrames() {
  return (
    <Suspense fallback={null}>
      {FRAMES.map((def) => (
        <ReelPlane key={def.src} def={def} />
      ))}
    </Suspense>
  );
}
