"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import { Float } from "@react-three/drei";
import { EffectComposer, Bloom } from "@react-three/postprocessing";
import { useMemo, useRef } from "react";
import * as THREE from "three";

const GOLD = "#d8b274";
const GOLD_BRIGHT = "#f4d79e";

function Core() {
  const ref = useRef<THREE.Mesh>(null);
  useFrame((_, delta) => {
    if (ref.current) {
      ref.current.rotation.y += delta * 0.25;
      ref.current.rotation.x += delta * 0.1;
    }
  });
  return (
    <Float speed={1.2} floatIntensity={0.5} rotationIntensity={0.2}>
      <mesh ref={ref}>
        <icosahedronGeometry args={[1.05, 0]} />
        <meshStandardMaterial
          color="#100d09"
          emissive={GOLD}
          emissiveIntensity={0.6}
          metalness={0.85}
          roughness={0.25}
          flatShading
        />
      </mesh>
    </Float>
  );
}

function Nodes() {
  const ring = useRef<THREE.Group>(null);
  const nodes = useMemo(
    () =>
      Array.from({ length: 6 }).map((_, i) => {
        const a = (i / 6) * Math.PI * 2;
        const r = 3;
        return {
          pos: new THREE.Vector3(
            Math.cos(a) * r,
            Math.sin(a * 1.5) * 0.6,
            Math.sin(a) * r
          ),
          c: i % 2 === 0 ? GOLD : GOLD_BRIGHT,
        };
      }),
    []
  );

  useFrame((_, delta) => {
    if (ring.current) ring.current.rotation.y += delta * 0.18;
  });

  return (
    <group ref={ring}>
      {nodes.map((n, i) => {
        const points = [new THREE.Vector3(0, 0, 0), n.pos];
        const geo = new THREE.BufferGeometry().setFromPoints(points);
        return (
          <group key={i}>
            <primitive
              object={
                new THREE.Line(
                  geo,
                  new THREE.LineBasicMaterial({
                    color: GOLD,
                    transparent: true,
                    opacity: 0.28,
                  })
                )
              }
            />
            <Float speed={2.4} floatIntensity={1} rotationIntensity={0.5}>
              <mesh position={n.pos}>
                <boxGeometry args={[0.62, 0.78, 0.05]} />
                <meshStandardMaterial
                  color="#100e0b"
                  emissive={n.c}
                  emissiveIntensity={0.35}
                  metalness={0.7}
                  roughness={0.3}
                />
              </mesh>
              <mesh position={[n.pos.x, n.pos.y + 0.18, n.pos.z + 0.03]}>
                <planeGeometry args={[0.44, 0.18]} />
                <meshStandardMaterial
                  color={n.c}
                  emissive={n.c}
                  emissiveIntensity={0.6}
                />
              </mesh>
            </Float>
          </group>
        );
      })}
    </group>
  );
}

export default function OsCanvas() {
  return (
    <Canvas
      dpr={[1, 2]}
      gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
      camera={{ position: [0, 1.2, 7.2], fov: 42 }}
    >
      <ambientLight intensity={0.3} />
      <pointLight position={[0, 0, 0]} intensity={18} color={GOLD_BRIGHT} />
      <directionalLight position={[5, 5, 5]} intensity={1.1} color="#fff2d6" />
      <Core />
      <Nodes />
      <EffectComposer multisampling={4}>
        <Bloom
          intensity={0.85}
          luminanceThreshold={0.2}
          luminanceSmoothing={0.5}
          mipmapBlur
        />
      </EffectComposer>
    </Canvas>
  );
}
