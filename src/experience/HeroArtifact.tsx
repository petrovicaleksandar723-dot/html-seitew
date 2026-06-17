import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { RoundedBox, Torus } from "@react-three/drei";
import * as THREE from "three";

/** Extruded pointy-top hexagon ring (outer hex with a hex hole). */
function useHexRing(outer: number, inner: number, depth: number) {
  return useMemo(() => {
    const hex = (r: number, path: THREE.Shape | THREE.Path) => {
      for (let i = 0; i < 6; i++) {
        const a = Math.PI / 2 + (i * Math.PI) / 3;
        const x = Math.cos(a) * r;
        const y = Math.sin(a) * r;
        i === 0 ? path.moveTo(x, y) : path.lineTo(x, y);
      }
      path.closePath();
    };
    const shape = new THREE.Shape();
    hex(outer, shape);
    const hole = new THREE.Path();
    hex(inner, hole);
    shape.holes.push(hole);
    const geo = new THREE.ExtrudeGeometry(shape, {
      depth,
      bevelEnabled: true,
      bevelThickness: 0.08,
      bevelSize: 0.07,
      bevelSegments: 5,
      steps: 1,
    });
    geo.center();
    geo.computeVertexNormals();
    return geo;
  }, [outer, inner, depth]);
}

/** Solid hexagon prism (glass core). */
function useHexPrism(r: number, depth: number) {
  return useMemo(() => {
    const shape = new THREE.Shape();
    for (let i = 0; i < 6; i++) {
      const a = Math.PI / 2 + (i * Math.PI) / 3;
      const x = Math.cos(a) * r;
      const y = Math.sin(a) * r;
      i === 0 ? shape.moveTo(x, y) : shape.lineTo(x, y);
    }
    shape.closePath();
    const geo = new THREE.ExtrudeGeometry(shape, {
      depth,
      bevelEnabled: true,
      bevelThickness: 0.12,
      bevelSize: 0.12,
      bevelSegments: 6,
      steps: 1,
    });
    geo.center();
    geo.computeVertexNormals();
    return geo;
  }, [r, depth]);
}

interface Props {
  /** 0..1 scroll progress through the hero, drives extra rotation. */
  scroll: React.MutableRefObject<number>;
}

/**
 * The Cleanlines artifact: a glass hexagon core, a gold extruded hex ring and
 * the three signature "clean lines" in polished gold. Floats, reacts to the
 * pointer and adds scroll-linked rotation. OrbitControls (in HeroCanvas) let the
 * user drag to rotate the whole scene.
 */
export default function HeroArtifact({ scroll }: Props) {
  const group = useRef<THREE.Group>(null);
  const ringRef = useRef<THREE.Mesh>(null);

  const ringGeo = useHexRing(1.72, 1.34, 0.34);
  const coreGeo = useHexPrism(1.2, 0.9);

  const glass = useMemo(
    () =>
      new THREE.MeshPhysicalMaterial({
        color: "#fff7e9",
        metalness: 0,
        roughness: 0.04,
        transmission: 1,
        thickness: 1.6,
        ior: 1.52,
        clearcoat: 1,
        clearcoatRoughness: 0.06,
        attenuationColor: new THREE.Color("#caa05a"),
        attenuationDistance: 2.2,
        envMapIntensity: 1.4,
        transparent: true,
      }),
    []
  );
  const goldMetal = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: "#caa050",
        metalness: 1,
        roughness: 0.22,
        envMapIntensity: 1.5,
      }),
    []
  );
  const goldBright = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: "#e7c074",
        metalness: 1,
        roughness: 0.16,
        envMapIntensity: 1.6,
      }),
    []
  );

  useFrame((state, delta) => {
    const t = state.clock.elapsedTime;
    if (group.current) {
      group.current.position.y = Math.sin(t * 0.7) * 0.12;
      // base auto-rotation + scroll-linked rotation
      group.current.rotation.y += delta * 0.18;
      group.current.rotation.y += scroll.current * 0.0; // scroll handled below for x tilt
      group.current.rotation.x = THREE.MathUtils.lerp(
        group.current.rotation.x,
        -0.12 + scroll.current * 1.1,
        0.08
      );
    }
    if (ringRef.current) ringRef.current.rotation.z += delta * 0.1;
  });

  return (
    <group ref={group} scale={1.15}>
      {/* glass core */}
      <mesh geometry={coreGeo} material={glass} renderOrder={2} />
      {/* gold hex ring frame */}
      <mesh ref={ringRef} geometry={ringGeo} material={goldMetal} castShadow />
      {/* three clean lines */}
      <RoundedBox args={[1.55, 0.16, 0.5]} radius={0.07} smoothness={4} position={[0, 0.36, 0]} material={goldBright} castShadow />
      <RoundedBox args={[1.06, 0.16, 0.5]} radius={0.07} smoothness={4} position={[-0.18, 0, 0]} material={goldBright} castShadow />
      <RoundedBox args={[0.6, 0.16, 0.5]} radius={0.07} smoothness={4} position={[-0.42, -0.36, 0]} material={goldBright} castShadow />
      {/* slim orbiting accent ring */}
      <Torus args={[2.45, 0.01, 16, 140]} rotation={[Math.PI / 2.4, 0, 0]} material={goldMetal} />
    </group>
  );
}
