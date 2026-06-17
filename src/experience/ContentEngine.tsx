import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { RoundedBox, Torus } from "@react-three/drei";
import * as THREE from "three";

/** Build a pointy-top hexagonal ring (outer hex with a hex hole), extruded. */
function useHexRing(outer: number, inner: number, depth: number) {
  return useMemo(() => {
    const hexPath = (r: number, path: THREE.Shape | THREE.Path) => {
      for (let i = 0; i < 6; i++) {
        const a = Math.PI / 2 + (i * Math.PI) / 3;
        const x = Math.cos(a) * r;
        const y = Math.sin(a) * r;
        if (i === 0) path.moveTo(x, y);
        else path.lineTo(x, y);
      }
      path.closePath();
    };
    const shape = new THREE.Shape();
    hexPath(outer, shape);
    const hole = new THREE.Path();
    hexPath(inner, hole);
    shape.holes.push(hole);
    const geo = new THREE.ExtrudeGeometry(shape, {
      depth,
      bevelEnabled: true,
      bevelThickness: 0.07,
      bevelSize: 0.06,
      bevelSegments: 4,
      steps: 1,
    });
    geo.center();
    geo.computeVertexNormals();
    return geo;
  }, [outer, inner, depth]);
}

/**
 * The 3D Cleanlines Studios logo: an extruded gold hexagon framing the three
 * signature "clean lines". Rotates, floats and reacts to the pointer; wrapped in
 * slowly orbiting accent rings and a warm core glow — the hero centrepiece.
 */
export default function ContentEngine() {
  const group = useRef<THREE.Group>(null);
  const logo = useRef<THREE.Group>(null);
  const ringA = useRef<THREE.Mesh>(null);
  const ringB = useRef<THREE.Mesh>(null);
  const glow = useRef<THREE.Mesh>(null);

  const hexGeo = useHexRing(1.62, 1.2, 0.36);

  const gold = useMemo(
    () =>
      new THREE.MeshPhysicalMaterial({
        color: "#e7bd78",
        metalness: 1,
        roughness: 0.22,
        clearcoat: 1,
        clearcoatRoughness: 0.18,
        emissive: new THREE.Color("#b9863f"),
        emissiveIntensity: 0.7,
      }),
    []
  );
  const goldBright = useMemo(
    () =>
      new THREE.MeshPhysicalMaterial({
        color: "#f4d7a1",
        metalness: 1,
        roughness: 0.14,
        clearcoat: 1,
        emissive: new THREE.Color("#f4d7a1"),
        emissiveIntensity: 1.3,
      }),
    []
  );

  useFrame((state, delta) => {
    const t = state.clock.elapsedTime;
    const { x, y } = state.pointer;

    if (group.current) {
      group.current.rotation.y += (x * 0.5 - group.current.rotation.y) * 0.04;
      group.current.rotation.x += (-y * 0.32 - group.current.rotation.x) * 0.04;
      group.current.position.y = Math.sin(t * 0.8) * 0.12;
    }
    if (logo.current) {
      logo.current.rotation.y = Math.sin(t * 0.35) * 0.5;
      logo.current.rotation.z = Math.sin(t * 0.25) * 0.05;
    }
    if (ringA.current) ringA.current.rotation.z += delta * 0.22;
    if (ringB.current) {
      ringB.current.rotation.x += delta * 0.16;
      ringB.current.rotation.y -= delta * 0.1;
    }
    if (glow.current) {
      const s = 1 + Math.sin(t * 1.4) * 0.06;
      glow.current.scale.setScalar(s);
      glow.current.quaternion.copy(state.camera.quaternion);
    }
  });

  return (
    <group ref={group} scale={1.02}>
      {/* local key light so the mark reads bright wherever it's placed */}
      <pointLight position={[0, 0, 3]} intensity={28} color="#ffe9c2" distance={14} decay={1.4} />
      {/* warm core glow behind the mark */}
      <mesh ref={glow} position={[0, 0, -0.5]}>
        <circleGeometry args={[3.2, 48]} />
        <meshBasicMaterial color="#d6a65f" transparent opacity={0.34} depthWrite={false} blending={THREE.AdditiveBlending} />
      </mesh>

      {/* the logo */}
      <group ref={logo}>
        {/* hexagon frame */}
        <mesh geometry={hexGeo} material={gold} castShadow />

        {/* the three clean lines */}
        <RoundedBox args={[1.5, 0.16, 0.24]} radius={0.07} smoothness={3} position={[0, 0.34, 0.04]} material={goldBright} />
        <RoundedBox args={[1.02, 0.16, 0.24]} radius={0.07} smoothness={3} position={[-0.18, 0, 0.04]} material={goldBright} />
        <RoundedBox args={[0.58, 0.16, 0.24]} radius={0.07} smoothness={3} position={[-0.4, -0.34, 0.04]} material={goldBright} />
      </group>

      {/* orbiting accent rings */}
      <Torus ref={ringA} args={[2.5, 0.012, 16, 140]} rotation={[Math.PI / 2.3, 0, 0]}>
        <meshStandardMaterial color="#d6a65f" metalness={1} roughness={0.3} emissive="#8c5a22" emissiveIntensity={0.4} />
      </Torus>
      <Torus ref={ringB} args={[3.05, 0.008, 16, 150]} rotation={[Math.PI / 3, Math.PI / 4, 0]}>
        <meshStandardMaterial color="#f4d7a1" metalness={1} roughness={0.25} emissive="#d6a65f" emissiveIntensity={0.3} />
      </Torus>
    </group>
  );
}
