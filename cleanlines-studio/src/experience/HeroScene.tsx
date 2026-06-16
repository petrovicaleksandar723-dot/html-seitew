import { useMemo, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";

function hexShape(r: number) {
  const s = new THREE.Shape();
  for (let i = 0; i < 6; i++) {
    const a = Math.PI / 2 + (i * Math.PI) / 3;
    const x = Math.cos(a) * r;
    const y = Math.sin(a) * r;
    if (i === 0) s.moveTo(x, y);
    else s.lineTo(x, y);
  }
  s.closePath();
  return s;
}

function Hexagon() {
  const ref = useRef<THREE.Group>(null);
  const geo = useMemo(() => {
    const shape = hexShape(2.2);
    const hole = new THREE.Path();
    for (let i = 0; i < 6; i++) {
      const a = Math.PI / 2 + (i * Math.PI) / 3;
      const x = Math.cos(a) * 1.5;
      const y = Math.sin(a) * 1.5;
      if (i === 0) hole.moveTo(x, y);
      else hole.lineTo(x, y);
    }
    hole.closePath();
    shape.holes.push(hole);
    const g = new THREE.ExtrudeGeometry(shape, {
      depth: 0.55,
      bevelEnabled: true,
      bevelThickness: 0.14,
      bevelSize: 0.12,
      bevelSegments: 3,
      curveSegments: 6,
    });
    g.center();
    return g;
  }, []);
  const core = useMemo(() => new THREE.IcosahedronGeometry(0.85, 0), []);

  useFrame((state, delta) => {
    const g = ref.current;
    if (!g) return;
    g.rotation.y += delta * 0.32;
    g.rotation.x = Math.sin(state.clock.elapsedTime * 0.3) * 0.12 - 0.1;
    const px = state.pointer.x * 1.1;
    const py = state.pointer.y * 0.8;
    state.camera.position.x += (px - state.camera.position.x) * 0.04;
    state.camera.position.y += (py - state.camera.position.y) * 0.04;
    state.camera.lookAt(0, 0, 0);
  });

  return (
    <group ref={ref}>
      <mesh geometry={geo}>
        <meshStandardMaterial color="#c9a25a" metalness={1} roughness={0.26} emissive="#140d03" emissiveIntensity={0.5} />
      </mesh>
      <mesh geometry={core}>
        <meshStandardMaterial color="#e8d2a0" metalness={1} roughness={0.18} emissive="#3a2c10" emissiveIntensity={0.7} />
      </mesh>
    </group>
  );
}

function Dust({ count }: { count: number }) {
  const ref = useRef<THREE.Points>(null);
  const geo = useMemo(() => {
    const g = new THREE.BufferGeometry();
    const pos = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      pos[i * 3] = (Math.random() - 0.5) * 30;
      pos[i * 3 + 1] = (Math.random() - 0.5) * 20;
      pos[i * 3 + 2] = (Math.random() - 0.5) * 16 - 2;
    }
    g.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    return g;
  }, [count]);
  useFrame((_, delta) => {
    if (ref.current) ref.current.rotation.y += delta * 0.04;
  });
  return (
    <points ref={ref} geometry={geo}>
      <pointsMaterial color="#c9a25a" size={0.045} transparent opacity={0.7} sizeAttenuation depthWrite={false} blending={THREE.AdditiveBlending} />
    </points>
  );
}

export function HeroScene() {
  const reduce = typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion:reduce)").matches;
  if (reduce) return null;
  const mobile = typeof window !== "undefined" && window.innerWidth < 760;
  return (
    <Canvas
      dpr={[1, mobile ? 1.5 : 2]}
      camera={{ position: [0, 0, 9], fov: 42 }}
      gl={{ antialias: !mobile, alpha: true, powerPreference: "high-performance" }}
    >
      <fogExp2 attach="fog" args={["#060608", 0.055]} />
      <ambientLight intensity={1.1} color="#40341f" />
      <directionalLight position={[5, 6, 6]} intensity={2.8} color="#ffe7b0" />
      <directionalLight position={[-6, -2, -5]} intensity={2.3} color="#c9a25a" />
      <pointLight position={[-3, 3, 6]} intensity={60} distance={50} color="#e8d2a0" />
      <Hexagon />
      <Dust count={mobile ? 240 : 700} />
    </Canvas>
  );
}
