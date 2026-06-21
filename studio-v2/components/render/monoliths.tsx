"use client";

import { useRef, useMemo } from "react";
import * as THREE from "three";
import { useFrame } from "@react-three/fiber";
import { RoundedBox, Float } from "@react-three/drei";

export function Monoliths() {
  const clusterRef = useRef<THREE.Group>(null);
  const leftRef = useRef<THREE.Group>(null);
  const midRef = useRef<THREE.Group>(null);
  const rightRef = useRef<THREE.Group>(null);

  const reducedMotion = useMemo(() => {
    if (typeof window === "undefined" || !window.matchMedia) return false;
    return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }, []);

  useFrame((_, dt) => {
    if (reducedMotion) return;

    const max = document.documentElement.scrollHeight - window.innerHeight;
    const p = max > 0 ? window.scrollY / max : 0;

    // Map scroll 0.55 -> 0.9 into a 0..1 rise factor.
    const t = THREE.MathUtils.clamp((p - 0.55) / (0.9 - 0.55), 0, 1);
    const y = THREE.MathUtils.lerp(-1.2, 0, t);

    if (leftRef.current) leftRef.current.position.y = y;
    if (rightRef.current) rightRef.current.position.y = y;
    if (midRef.current) midRef.current.position.y = y;

    if (clusterRef.current) clusterRef.current.rotation.y += dt * 0.05;
  });

  return (
    <group ref={clusterRef}>
      {/* Left side pillar */}
      <group ref={leftRef}>
        {/* gold rim behind */}
        <RoundedBox
          args={[1.42, 4.3, 1.42]}
          radius={0.13}
          smoothness={4}
          position={[-3.3, 0, -14.1]}
        >
          <meshStandardMaterial
            color="#d8b274"
            emissive="#a87f3e"
            emissiveIntensity={0.55}
            metalness={0.6}
            roughness={0.3}
          />
        </RoundedBox>
        {/* dark pillar */}
        <RoundedBox
          args={[1.3, 4.2, 1.3]}
          radius={0.12}
          smoothness={4}
          position={[-3.3, 0, -14]}
        >
          <meshStandardMaterial
            color="#1b1812"
            metalness={0.45}
            roughness={0.34}
            emissive="#2a2018"
            emissiveIntensity={0.18}
            envMapIntensity={1.2}
          />
        </RoundedBox>
      </group>

      {/* Middle featured pillar (taller) */}
      <group ref={midRef}>
        {/* gold rim behind, stronger gold */}
        <RoundedBox
          args={[1.42, 5.5, 1.42]}
          radius={0.13}
          smoothness={4}
          position={[0, 0.6, -14.1]}
        >
          <meshStandardMaterial
            color="#d8b274"
            emissive="#d8b274"
            emissiveIntensity={0.8}
            metalness={0.6}
            roughness={0.3}
          />
        </RoundedBox>
        {/* dark pillar */}
        <RoundedBox
          args={[1.3, 5.4, 1.3]}
          radius={0.12}
          smoothness={4}
          position={[0, 0.6, -14]}
        >
          <meshStandardMaterial
            color="#1b1812"
            metalness={0.45}
            roughness={0.34}
            emissive="#2a2018"
            emissiveIntensity={0.18}
            envMapIntensity={1.2}
          />
        </RoundedBox>
        {/* glowing cap */}
        <mesh position={[0, 3.1, -14]}>
          <icosahedronGeometry args={[0.5, 0]} />
          <meshStandardMaterial
            color="#f1d6a0"
            emissive="#d8b274"
            emissiveIntensity={2.4}
            flatShading
          />
        </mesh>
        <pointLight
          position={[0, 3.1, -14]}
          intensity={6}
          distance={9}
          color="#f1d6a0"
        />
      </group>

      {/* Right side pillar */}
      <group ref={rightRef}>
        {/* gold rim behind */}
        <RoundedBox
          args={[1.42, 4.3, 1.42]}
          radius={0.13}
          smoothness={4}
          position={[3.3, 0, -14.1]}
        >
          <meshStandardMaterial
            color="#d8b274"
            emissive="#a87f3e"
            emissiveIntensity={0.55}
            metalness={0.6}
            roughness={0.3}
          />
        </RoundedBox>
        {/* dark pillar */}
        <RoundedBox
          args={[1.3, 4.2, 1.3]}
          radius={0.12}
          smoothness={4}
          position={[3.3, 0, -14]}
        >
          <meshStandardMaterial
            color="#1b1812"
            metalness={0.45}
            roughness={0.34}
            emissive="#2a2018"
            emissiveIntensity={0.18}
            envMapIntensity={1.2}
          />
        </RoundedBox>
      </group>

      {/* Floating chrome torus-knot centerpiece */}
      <Float speed={1.5} rotationIntensity={0.6} floatIntensity={1.2}>
        <mesh position={[0, 3.6, -18]}>
          <torusKnotGeometry args={[1.1, 0.34, 180, 32]} />
          <meshStandardMaterial
            color="#eef2f6"
            metalness={0.55}
            roughness={0.16}
            emissive="#33404d"
            emissiveIntensity={0.25}
            envMapIntensity={1.6}
          />
        </mesh>
      </Float>
    </group>
  );
}
