import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Torus, Icosahedron } from "@react-three/drei";
import * as THREE from "three";

/**
 * The central "Content Engine": a glass core wrapped in slowly rotating torus
 * rings. Reacts to pointer for subtle parallax and keeps a continuous idle spin.
 */
export default function ContentEngine() {
  const group = useRef<THREE.Group>(null);
  const ringA = useRef<THREE.Mesh>(null);
  const ringB = useRef<THREE.Mesh>(null);
  const ringC = useRef<THREE.Mesh>(null);
  const core = useRef<THREE.Mesh>(null);

  useFrame((state, delta) => {
    const t = state.clock.elapsedTime;
    const { x, y } = state.pointer;

    if (group.current) {
      // pointer parallax — eased toward target
      group.current.rotation.y += (x * 0.4 - group.current.rotation.y) * 0.04;
      group.current.rotation.x += (-y * 0.25 - group.current.rotation.x) * 0.04;
    }
    if (ringA.current) ringA.current.rotation.z += delta * 0.25;
    if (ringB.current) {
      ringB.current.rotation.x += delta * 0.18;
      ringB.current.rotation.y += delta * 0.12;
    }
    if (ringC.current) ringC.current.rotation.y -= delta * 0.2;
    if (core.current) {
      core.current.rotation.y += delta * 0.4;
      const s = 1 + Math.sin(t * 1.5) * 0.03;
      core.current.scale.setScalar(s);
    }
  });

  return (
    <group ref={group} scale={1.05}>
      {/* glass core */}
      <Icosahedron ref={core} args={[1.05, 1]}>
        <meshPhysicalMaterial
          color="#1a140c"
          metalness={0.2}
          roughness={0.05}
          transmission={0.92}
          thickness={1.4}
          ior={1.5}
          clearcoat={1}
          clearcoatRoughness={0.1}
          attenuationColor="#d6a65f"
          attenuationDistance={2.4}
          transparent
        />
      </Icosahedron>

      {/* inner emissive seed */}
      <mesh>
        <sphereGeometry args={[0.42, 32, 32]} />
        <meshStandardMaterial
          color="#f4d7a1"
          emissive="#d6a65f"
          emissiveIntensity={2.4}
          toneMapped={false}
        />
      </mesh>

      {/* metallic rings */}
      <Torus ref={ringA} args={[2.0, 0.018, 16, 120]} rotation={[Math.PI / 2.2, 0, 0]}>
        <meshStandardMaterial color="#d6a65f" metalness={1} roughness={0.3} emissive="#8c5a22" emissiveIntensity={0.4} />
      </Torus>
      <Torus ref={ringB} args={[2.5, 0.012, 16, 120]} rotation={[Math.PI / 3, Math.PI / 4, 0]}>
        <meshStandardMaterial color="#f4d7a1" metalness={1} roughness={0.25} emissive="#d6a65f" emissiveIntensity={0.3} />
      </Torus>
      <Torus ref={ringC} args={[3.1, 0.008, 16, 140]} rotation={[Math.PI / 2.6, 0, Math.PI / 6]}>
        <meshStandardMaterial color="#8c5a22" metalness={1} roughness={0.4} emissive="#8c5a22" emissiveIntensity={0.25} />
      </Torus>
    </group>
  );
}
