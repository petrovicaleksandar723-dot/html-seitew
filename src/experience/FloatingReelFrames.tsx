import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

/** A ring of floating glass "reel frames" with glowing gold edges. */
export function FloatingReelFrames({ count = 6 }: { count?: number }) {
  const group = useRef<THREE.Group>(null);

  const frames = useMemo(() => {
    return new Array(count).fill(0).map((_, i) => {
      const ang = (i / count) * Math.PI * 2;
      const rad = 3.4 + (i % 2) * 0.7;
      return { ang, rad, baseY: Math.sin(ang * 1.7) * 1.5, ph: i };
    });
  }, [count]);

  const edges = useMemo(() => new THREE.EdgesGeometry(new THREE.PlaneGeometry(0.95, 1.55)), []);

  useFrame((state) => {
    const t = state.clock.elapsedTime;
    if (!group.current) return;
    group.current.children.forEach((child, i) => {
      const f = frames[i];
      const ang = f.ang + t * 0.06;
      child.position.x = Math.cos(ang) * f.rad;
      child.position.z = Math.sin(ang) * f.rad - 1;
      child.position.y = f.baseY + Math.sin(t * 0.6 + f.ph) * 0.25;
      child.rotation.y = -ang + Math.PI / 2;
    });
  });

  return (
    <group ref={group}>
      {frames.map((_, i) => (
        <group key={i}>
          <mesh>
            <planeGeometry args={[0.95, 1.55]} />
            <meshPhysicalMaterial
              color="#0a0908"
              metalness={0.4}
              roughness={0.2}
              transparent
              opacity={0.28}
              clearcoat={1}
              side={THREE.DoubleSide}
            />
          </mesh>
          <lineSegments geometry={edges}>
            <lineBasicMaterial color="#f4d7a1" transparent opacity={0.5} />
          </lineSegments>
        </group>
      ))}
    </group>
  );
}
