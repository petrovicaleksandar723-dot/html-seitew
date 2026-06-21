"use client";

import { useMemo, useRef } from "react";
import * as THREE from "three";
import { useFrame } from "@react-three/fiber";
import { Instances, Instance } from "@react-three/drei";

type Shard = {
  position: [number, number, number];
  scale: number;
  rotation: [number, number, number];
};

const HEROES: Array<[number, number, number]> = [
  [-5, 2, 2],
  [5, -1.5, -3],
  [-4, 1, -9],
  [4, 1.5, -15],
];

export function Shards() {
  const groupRef = useRef<THREE.Group>(null);

  const reducedMotion = useMemo(
    () =>
      typeof window !== "undefined" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches,
    []
  );

  const shards = useMemo<Shard[]>(() => {
    const rnd = (a: number, b: number) => a + Math.random() * (b - a);
    const out: Shard[] = [];
    for (let i = 0; i < 48; i++) {
      const hero = i < HEROES.length;
      let x = rnd(-10, 10);
      let y = rnd(-6.5, 6.5);
      const z = rnd(-24, 8);
      if (hero) {
        [x, y] = [HEROES[i][0], HEROES[i][1]];
      } else {
        const r = Math.hypot(x, y);
        if (r < 3.2) {
          const f = 3.2 / (r || 0.001);
          x *= f + rnd(0.1, 0.6);
          y *= f + rnd(0.1, 0.6);
        }
      }
      out.push({
        position: [x, y, hero ? HEROES[i][2] : z],
        scale: hero ? rnd(0.7, 1.0) : rnd(0.12, 0.5),
        rotation: [rnd(0, Math.PI * 2), rnd(0, Math.PI * 2), rnd(0, Math.PI * 2)],
      });
    }
    return out;
  }, []);

  useFrame((_, dt) => {
    if (reducedMotion || !groupRef.current) return;
    groupRef.current.rotation.y += dt * 0.02;
    groupRef.current.rotation.x += dt * 0.005;
  });

  return (
    <group ref={groupRef}>
      <Instances limit={48} range={48}>
        <octahedronGeometry args={[1, 0]} />
        <meshStandardMaterial
          color="#d8b274"
          metalness={0.6}
          roughness={0.32}
          emissive="#6e5020"
          emissiveIntensity={0.3}
          envMapIntensity={1.4}
          flatShading
        />
        {shards.map((s, i) => (
          <Instance
            key={i}
            position={s.position}
            scale={s.scale}
            rotation={s.rotation}
          />
        ))}
      </Instances>
    </group>
  );
}
