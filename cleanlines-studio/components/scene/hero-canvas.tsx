"use client";

import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { Float } from "@react-three/drei";
import { EffectComposer, Bloom, Vignette } from "@react-three/postprocessing";
import { useMemo, useRef } from "react";
import * as THREE from "three";

const GOLD = "#d8b274";
const GOLD_BRIGHT = "#f4d79e";

/* ---------- Floating premium phone ---------- */
function Phone() {
  const group = useRef<THREE.Group>(null);
  useFrame((state) => {
    if (!group.current) return;
    const t = state.clock.elapsedTime;
    group.current.rotation.z = Math.sin(t * 0.4) * 0.04;
  });

  return (
    <Float speed={1.4} rotationIntensity={0.25} floatIntensity={0.7}>
      <group ref={group} rotation={[0.04, -0.35, 0]}>
        {/* body */}
        <mesh castShadow>
          <boxGeometry args={[1.55, 3.2, 0.18]} />
          <meshStandardMaterial
            color="#0c0b09"
            metalness={0.9}
            roughness={0.28}
          />
        </mesh>
        {/* bezel frame glow */}
        <mesh position={[0, 0, 0.095]}>
          <boxGeometry args={[1.42, 3.06, 0.02]} />
          <meshStandardMaterial
            color="#000000"
            emissive={GOLD}
            emissiveIntensity={0.12}
            metalness={0.6}
            roughness={0.4}
          />
        </mesh>
        {/* screen */}
        <mesh position={[0, 0, 0.108]}>
          <planeGeometry args={[1.34, 2.98]} />
          <meshBasicMaterial color="#14110b" />
        </mesh>
        {/* reel preview blocks */}
        {[1.02, 0.32, -0.42].map((y, i) => (
          <mesh key={i} position={[0, y, 0.12]}>
            <planeGeometry args={[1.16, 0.52]} />
            <meshStandardMaterial
              color="#1c1710"
              emissive={GOLD}
              emissiveIntensity={0.35 - i * 0.07}
            />
          </mesh>
        ))}
        {/* caption lines */}
        {[-1.05, -1.22, -1.39].map((y, i) => (
          <mesh key={`l${i}`} position={[-0.18 - i * 0.04, y, 0.122]}>
            <planeGeometry args={[0.9 - i * 0.22, 0.045]} />
            <meshBasicMaterial color={GOLD_BRIGHT} />
          </mesh>
        ))}
        {/* CTA pill */}
        <mesh position={[0, -1.05, 0.122]}>
          <planeGeometry args={[1.16, 0.34]} />
          <meshStandardMaterial
            color={GOLD}
            emissive={GOLD_BRIGHT}
            emissiveIntensity={0.6}
          />
        </mesh>
      </group>
    </Float>
  );
}

/* ---------- Orbiting glass content modules ---------- */
function OrbitModules() {
  const ring = useRef<THREE.Group>(null);
  const items = useMemo(
    () => [
      { a: 0, r: 2.7, y: 0.9, c: GOLD },
      { a: 1.05, r: 3.0, y: -0.4, c: "#e0915f" },
      { a: 2.1, r: 2.6, y: 1.3, c: GOLD_BRIGHT },
      { a: 3.14, r: 3.1, y: 0.2, c: GOLD },
      { a: 4.2, r: 2.7, y: -1.1, c: "#cdbf9a" },
      { a: 5.2, r: 2.9, y: 0.7, c: GOLD_BRIGHT },
    ],
    []
  );

  useFrame((state, delta) => {
    if (ring.current) ring.current.rotation.y += delta * 0.12;
  });

  return (
    <group ref={ring}>
      {items.map((it, i) => (
        <Float
          key={i}
          speed={2}
          rotationIntensity={0.6}
          floatIntensity={1.1}
        >
          <group
            position={[
              Math.cos(it.a) * it.r,
              it.y,
              Math.sin(it.a) * it.r,
            ]}
            rotation={[0, -it.a + Math.PI / 2, 0]}
          >
            <mesh>
              <boxGeometry args={[0.82, 1.02, 0.04]} />
              <meshStandardMaterial
                color="#100e0b"
                emissive={it.c}
                emissiveIntensity={0.18}
                metalness={0.7}
                roughness={0.35}
                transparent
                opacity={0.92}
              />
            </mesh>
            <mesh position={[0, 0.28, 0.03]}>
              <planeGeometry args={[0.6, 0.32]} />
              <meshStandardMaterial
                color={it.c}
                emissive={it.c}
                emissiveIntensity={0.5}
              />
            </mesh>
            {[0.02, -0.12, -0.26].map((y, j) => (
              <mesh key={j} position={[-0.06, y, 0.03]}>
                <planeGeometry args={[0.5 - j * 0.12, 0.04]} />
                <meshBasicMaterial color="#d9cdb6" />
              </mesh>
            ))}
          </group>
        </Float>
      ))}
    </group>
  );
}

/* ---------- Light rings ---------- */
function Rings() {
  const a = useRef<THREE.Mesh>(null);
  const b = useRef<THREE.Mesh>(null);
  useFrame((_, delta) => {
    if (a.current) a.current.rotation.z += delta * 0.08;
    if (b.current) b.current.rotation.z -= delta * 0.05;
  });
  return (
    <group rotation={[Math.PI / 2.3, 0, 0]}>
      <mesh ref={a}>
        <torusGeometry args={[3.6, 0.008, 16, 120]} />
        <meshStandardMaterial
          color={GOLD}
          emissive={GOLD}
          emissiveIntensity={2}
        />
      </mesh>
      <mesh ref={b} rotation={[0.4, 0, 0]}>
        <torusGeometry args={[4.3, 0.006, 16, 120]} />
        <meshStandardMaterial
          color={GOLD_BRIGHT}
          emissive={GOLD_BRIGHT}
          emissiveIntensity={1.4}
        />
      </mesh>
    </group>
  );
}

/* ---------- Particle dust ---------- */
function Dust() {
  const ref = useRef<THREE.Points>(null);
  const positions = useMemo(() => {
    const n = 380;
    const arr = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) {
      arr[i * 3] = (Math.random() - 0.5) * 16;
      arr[i * 3 + 1] = (Math.random() - 0.5) * 11;
      arr[i * 3 + 2] = (Math.random() - 0.5) * 9;
    }
    return arr;
  }, []);
  useFrame((_, delta) => {
    if (ref.current) ref.current.rotation.y += delta * 0.015;
  });
  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={positions.length / 3}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.026}
        color={GOLD_BRIGHT}
        transparent
        opacity={0.55}
        sizeAttenuation
        depthWrite={false}
      />
    </points>
  );
}

/* ---------- Pointer parallax rig ---------- */
function ParallaxRig({ children }: { children: React.ReactNode }) {
  const group = useRef<THREE.Group>(null);
  const { pointer } = useThree();
  useFrame(() => {
    if (!group.current) return;
    group.current.rotation.y +=
      (pointer.x * 0.28 - group.current.rotation.y) * 0.05;
    group.current.rotation.x +=
      (-pointer.y * 0.18 - group.current.rotation.x) * 0.05;
  });
  return <group ref={group}>{children}</group>;
}

export default function HeroCanvas() {
  return (
    <Canvas
      dpr={[1, 2]}
      gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
      camera={{ position: [0, 0.3, 8.5], fov: 38 }}
    >
      <color attach="background" args={["#050505"]} />
      <fog attach="fog" args={["#050505", 9, 18]} />
      <ambientLight intensity={0.25} />
      <directionalLight position={[4, 6, 6]} intensity={1.6} color="#fff2d6" />
      <pointLight position={[-5, -2, 4]} intensity={40} color={GOLD} />
      <pointLight position={[3, 3, -4]} intensity={26} color={GOLD_BRIGHT} />

      <ParallaxRig>
        <Phone />
        <OrbitModules />
        <Rings />
        <Dust />
      </ParallaxRig>

      <EffectComposer multisampling={4}>
        <Bloom
          intensity={0.9}
          luminanceThreshold={0.22}
          luminanceSmoothing={0.5}
          mipmapBlur
        />
        <Vignette eskil={false} offset={0.22} darkness={0.92} />
      </EffectComposer>
    </Canvas>
  );
}
