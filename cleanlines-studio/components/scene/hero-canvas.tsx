"use client";

import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { Float, useVideoTexture, Environment, Billboard } from "@react-three/drei";
import { EffectComposer, Bloom, Vignette } from "@react-three/postprocessing";
import {
  Component,
  Suspense,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import * as THREE from "three";
import { asset } from "@/lib/asset";

const GOLD = "#d8b274";
const GOLD_BRIGHT = "#f4d79e";

const CARD_W = 0.96;
const CARD_H = 1.46;

const CARDS = [
  { src: asset("/videos/showreel.mp4"), a: 0.3, r: 3.1, y: 0.8 },
  { src: asset("/videos/reel-1.mp4"), a: 1.75, r: 3.25, y: -0.6 },
  { src: asset("/videos/reel-2.mp4"), a: 3.2, r: 3.0, y: 1.2 },
  { src: asset("/videos/reel-3.mp4"), a: 4.7, r: 3.2, y: -1.0 },
];

/* ---------- Interactive 3D "CL" monogram ---------- */
const deg = (d: number) => THREE.MathUtils.degToRad(d);

function ringGeometry() {
  const oR = 1.0;
  const iR = 0.74;
  const c = new THREE.Shape();
  c.absarc(0, 0, oR, deg(42), deg(318), false);
  c.absarc(0, 0, iR, deg(318), deg(42), true);
  const geo = new THREE.ExtrudeGeometry(c, {
    depth: 0.26,
    bevelEnabled: true,
    bevelThickness: 0.05,
    bevelSize: 0.035,
    bevelSegments: 4,
    curveSegments: 64,
  });
  geo.center();
  return geo;
}

function lGeometry() {
  const L = new THREE.Shape();
  const x0 = -0.1;
  const x1 = 0.17;
  const top = 0.56;
  const bot = -0.92;
  const footX = 0.92;
  const footTop = -0.64;
  L.moveTo(x0, top);
  L.lineTo(x1, top);
  L.lineTo(x1, footTop);
  L.lineTo(footX, footTop);
  L.lineTo(footX, bot);
  L.lineTo(x0, bot);
  L.closePath();
  const geo = new THREE.ExtrudeGeometry(L, {
    depth: 0.3,
    bevelEnabled: true,
    bevelThickness: 0.05,
    bevelSize: 0.03,
    bevelSegments: 4,
    curveSegments: 24,
  });
  return geo;
}

function Logo3D() {
  const geoC = useMemo(ringGeometry, []);
  const geoL = useMemo(lGeometry, []);
  const grp = useRef<THREE.Group>(null);
  const spin = useRef(0);
  const dragging = useRef(false);
  const [hover, setHover] = useState(false);

  useEffect(() => {
    const move = (e: PointerEvent) => {
      if (!dragging.current || !grp.current) return;
      grp.current.rotation.y += e.movementX * 0.012;
      grp.current.rotation.x = THREE.MathUtils.clamp(
        grp.current.rotation.x + e.movementY * 0.008,
        -0.7,
        0.7
      );
    };
    const up = () => {
      dragging.current = false;
      document.body.style.cursor = "";
    };
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up);
    return () => {
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", up);
    };
  }, []);

  useFrame((state, dt) => {
    const g = grp.current;
    if (!g) return;
    if (!dragging.current) g.rotation.y += dt * 0.35 + spin.current * dt;
    spin.current *= 0.94;
    g.position.y = Math.sin(state.clock.elapsedTime * 0.8) * 0.06;
    const target = (hover ? 1.5 : 1.4);
    const s = THREE.MathUtils.lerp(g.scale.x, target, 0.12);
    g.scale.setScalar(s);
  });

  const material = (
    <meshStandardMaterial
      color="#f0cf8e"
      metalness={1}
      roughness={0.17}
      envMapIntensity={1.6}
      emissive="#6b4a12"
      emissiveIntensity={0.25}
    />
  );

  return (
    <group
      ref={grp}
      position={[-0.08, 0.05, 0]}
      scale={1.4}
      onPointerDown={(e) => {
        e.stopPropagation();
        dragging.current = true;
        document.body.style.cursor = "grabbing";
      }}
      onPointerOver={() => {
        setHover(true);
        document.body.style.cursor = "grab";
      }}
      onPointerOut={() => {
        setHover(false);
        if (!dragging.current) document.body.style.cursor = "";
      }}
      onClick={(e) => {
        e.stopPropagation();
        spin.current += 7;
      }}
    >
      <mesh geometry={geoC}>{material}</mesh>
      <mesh geometry={geoL} position={[0, 0, 0.03]}>
        <meshStandardMaterial
          color="#fbe6b0"
          metalness={1}
          roughness={0.14}
          envMapIntensity={1.8}
          emissive="#6b4a12"
          emissiveIntensity={0.28}
        />
      </mesh>
    </group>
  );
}

/* ---------- Card frame ---------- */
function Frame() {
  return (
    <mesh>
      <boxGeometry args={[CARD_W + 0.08, CARD_H + 0.08, 0.05]} />
      <meshStandardMaterial color="#0c0a08" emissive={GOLD} emissiveIntensity={0.16} metalness={0.7} roughness={0.34} />
    </mesh>
  );
}

function FallbackCard() {
  return (
    <group>
      <Frame />
      <mesh position={[0, 0, 0.03]}>
        <planeGeometry args={[CARD_W, CARD_H]} />
        <meshStandardMaterial color="#161009" emissive={GOLD} emissiveIntensity={0.3} />
      </mesh>
    </group>
  );
}

function VideoFace({ src }: { src: string }) {
  const texture = useVideoTexture(src, {
    crossOrigin: "anonymous",
    muted: true,
    loop: true,
    start: true,
    playsInline: true,
  });
  return (
    <group>
      <Frame />
      <mesh position={[0, 0, 0.03]}>
        <planeGeometry args={[CARD_W, CARD_H]} />
        <meshBasicMaterial map={texture} toneMapped={false} />
      </mesh>
    </group>
  );
}

class TextureBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    if (this.state.failed) return <FallbackCard />;
    return this.props.children;
  }
}

function VideoCards() {
  const ring = useRef<THREE.Group>(null);
  useFrame((_, delta) => {
    if (ring.current) ring.current.rotation.y += delta * 0.12;
  });
  return (
    <group ref={ring}>
      {CARDS.map((c, i) => (
        <Float key={i} speed={1.8} rotationIntensity={0} floatIntensity={1.0}>
          <group position={[Math.cos(c.a) * c.r, c.y, Math.sin(c.a) * c.r]}>
            <Billboard>
              <TextureBoundary>
                <Suspense fallback={<FallbackCard />}>
                  <VideoFace src={c.src} />
                </Suspense>
              </TextureBoundary>
            </Billboard>
          </group>
        </Float>
      ))}
    </group>
  );
}

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
        <torusGeometry args={[3.8, 0.008, 16, 120]} />
        <meshStandardMaterial color={GOLD} emissive={GOLD} emissiveIntensity={2} />
      </mesh>
      <mesh ref={b} rotation={[0.4, 0, 0]}>
        <torusGeometry args={[4.5, 0.006, 16, 120]} />
        <meshStandardMaterial color={GOLD_BRIGHT} emissive={GOLD_BRIGHT} emissiveIntensity={1.4} />
      </mesh>
    </group>
  );
}

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
        <bufferAttribute attach="attributes-position" count={positions.length / 3} array={positions} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial size={0.026} color={GOLD_BRIGHT} transparent opacity={0.55} sizeAttenuation depthWrite={false} />
    </points>
  );
}

function ParallaxRig({ children }: { children: ReactNode }) {
  const group = useRef<THREE.Group>(null);
  const { pointer } = useThree();
  useFrame(() => {
    if (!group.current) return;
    group.current.rotation.y += (pointer.x * 0.22 - group.current.rotation.y) * 0.04;
    group.current.rotation.x += (-pointer.y * 0.14 - group.current.rotation.x) * 0.04;
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
      <fog attach="fog" args={["#070506", 9, 19]} />
      <ambientLight intensity={0.35} />
      {/* cinematic colored lighting */}
      <directionalLight position={[4, 6, 6]} intensity={2.6} color="#fff1cf" />
      <pointLight position={[-6, 1, 2]} intensity={70} color="#3e6bff" />
      <pointLight position={[5, -2, -3]} intensity={55} color="#ff3da6" />
      <pointLight position={[0, 4, -5]} intensity={40} color={GOLD_BRIGHT} />
      <pointLight position={[0, 0, 6]} intensity={22} color="#ffffff" />
      <Suspense fallback={null}>
        <Environment preset="sunset" />
      </Suspense>

      <Logo3D />
      <ParallaxRig>
        <Suspense fallback={null}>
          <VideoCards />
        </Suspense>
        <Rings />
        <Dust />
      </ParallaxRig>

      <EffectComposer multisampling={4}>
        <Bloom intensity={1.15} luminanceThreshold={0.22} luminanceSmoothing={0.6} mipmapBlur />
        <Vignette eskil={false} offset={0.2} darkness={0.92} />
      </EffectComposer>
    </Canvas>
  );
}
