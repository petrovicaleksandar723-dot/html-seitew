import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { FloatingReelFrames } from "./FloatingReelFrames";
import { heroState } from "./heroState";

/** The central abstract "Content Engine": a gold physical torus-knot with
 *  orbiting rings and a halo of floating glass reel frames. */
export function ContentEngine() {
  const group = useRef<THREE.Group>(null);
  const knot = useRef<THREE.Mesh>(null);
  const ring1 = useRef<THREE.Mesh>(null);
  const ring2 = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    const t = state.clock.elapsedTime;

    // smooth pointer
    heroState.tx += (heroState.px - heroState.tx) * 0.05;
    heroState.ty += (heroState.py - heroState.ty) * 0.05;

    if (knot.current) {
      knot.current.rotation.x = t * 0.14;
      knot.current.rotation.y = t * 0.2;
    }
    if (ring1.current) ring1.current.rotation.z = t * 0.16;
    if (ring2.current) ring2.current.rotation.z = -t * 0.12;

    if (group.current) {
      const s = heroState.scroll;
      group.current.rotation.y = heroState.tx * 0.4 + s * 0.6;
      group.current.rotation.x = heroState.ty * 0.25;
      group.current.scale.setScalar(1 - s * 0.25);
      group.current.position.y = -s * 1.2;
    }
  });

  return (
    <group ref={group} position={[2.1, 0, 0]}>
      <mesh ref={knot}>
        <torusKnotGeometry args={[1.35, 0.34, 220, 32, 2, 3]} />
        <meshPhysicalMaterial
          color="#2a2118"
          metalness={1}
          roughness={0.28}
          clearcoat={1}
          clearcoatRoughness={0.25}
          emissive="#140d04"
          emissiveIntensity={0.6}
        />
      </mesh>

      <mesh ref={ring1} rotation={[1.2, 0, 0]}>
        <torusGeometry args={[2.55, 0.012, 16, 160]} />
        <meshStandardMaterial color="#d6a65f" metalness={1} roughness={0.3} emissive="#8c5a22" emissiveIntensity={0.4} />
      </mesh>
      <mesh ref={ring2} rotation={[-0.7, 0.5, 0]}>
        <torusGeometry args={[3.15, 0.008, 16, 160]} />
        <meshStandardMaterial color="#d6a65f" metalness={1} roughness={0.3} emissive="#8c5a22" emissiveIntensity={0.4} />
      </mesh>

      <FloatingReelFrames />
    </group>
  );
}
