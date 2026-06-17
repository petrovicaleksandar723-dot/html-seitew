"use client";

import { useMemo, useRef, useState } from "react";
import * as THREE from "three";
import { useFrame } from "@react-three/fiber";
import {
  OrthographicCamera,
  ContactShadows,
  RoundedBox,
  Html,
  AdaptiveDpr,
} from "@react-three/drei";

/* ------------------------------------------------------------------ palette */
const C = {
  wood: "#b9824f",
  woodDark: "#9c6a3c",
  platform: "#caa06f",
  metal: "#33333b",
  metalLight: "#4a4a55",
  plastic: "#e9e3d6",
  gold: "#d8b274",
  goldBright: "#f1d6a0",
  screen: "#bfe6ff",
  screenWarm: "#ffd9a0",
  plant: "#5f8f57",
  plantDark: "#487043",
  sofa: "#c2674168",
  sofaSolid: "#c06a44",
  rug: "#274a6e",
  dark: "#1c1c22",
};

function std(color: string, opts: Partial<THREE.MeshStandardMaterialParameters> = {}) {
  return <meshStandardMaterial color={color} roughness={0.7} metalness={0.05} {...opts} />;
}

/* --------------------------------------------------------------- floor tex */
function useFloorTexture() {
  return useMemo(() => {
    const c = document.createElement("canvas");
    c.width = c.height = 512;
    const x = c.getContext("2d")!;
    x.fillStyle = C.wood;
    x.fillRect(0, 0, 512, 512);
    // planks
    for (let i = 0; i < 8; i++) {
      const g = x.createLinearGradient(0, i * 64, 512, i * 64);
      g.addColorStop(0, "rgba(0,0,0,0.05)");
      g.addColorStop(0.5, "rgba(255,255,255,0.04)");
      g.addColorStop(1, "rgba(0,0,0,0.06)");
      x.fillStyle = g;
      x.fillRect(0, i * 64, 512, 62);
      x.strokeStyle = "rgba(60,35,15,0.35)";
      x.lineWidth = 2;
      x.strokeRect(0, i * 64, 512, 64);
    }
    const t = new THREE.CanvasTexture(c);
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    t.repeat.set(2, 2);
    t.anisotropy = 8;
    return t;
  }, []);
}

/* screen content texture */
function useScreenTexture(kind: "timeline" | "grade" | "grid") {
  return useMemo(() => {
    const c = document.createElement("canvas");
    c.width = 256;
    c.height = 160;
    const x = c.getContext("2d")!;
    x.fillStyle = "#0c1622";
    x.fillRect(0, 0, 256, 160);
    if (kind === "timeline") {
      x.fillStyle = "#132030";
      for (let i = 0; i < 5; i++) {
        x.fillStyle = i % 2 ? "#1b2b40" : "#16243a";
        x.fillRect(8, 18 + i * 26, 240, 18);
      }
      const cols = ["#d8b274", "#bfe6ff", "#7ad28f", "#f0a0a0"];
      for (let i = 0; i < 5; i++) {
        x.fillStyle = cols[i % cols.length];
        const w = 30 + Math.random() * 90;
        x.fillRect(12 + Math.random() * 60, 20 + i * 26, w, 14);
      }
      x.fillStyle = "#d8b274";
      x.fillRect(120, 8, 2, 144);
    } else if (kind === "grade") {
      const g = x.createLinearGradient(0, 0, 256, 160);
      g.addColorStop(0, "#2a3a55");
      g.addColorStop(1, "#d8b274");
      x.fillStyle = g;
      x.fillRect(16, 16, 224, 100);
      x.fillStyle = "#0c1622";
      x.fillRect(16, 124, 224, 22);
      x.fillStyle = "#d8b274";
      for (let i = 0; i < 12; i++) x.fillRect(22 + i * 18, 128 + Math.random() * 12, 8, 14);
    } else {
      for (let i = 0; i < 12; i++) {
        x.fillStyle = `hsl(${30 + Math.random() * 30},40%,${30 + Math.random() * 30}%)`;
        x.fillRect(10 + (i % 4) * 60, 10 + Math.floor(i / 4) * 48, 52, 40);
      }
    }
    return new THREE.CanvasTexture(c);
  }, [kind]);
}

/* --------------------------------------------------------------- primitives */
function Plant({ s = 1 }: { s?: number }) {
  return (
    <group scale={s}>
      <mesh position={[0, 0.25, 0]} castShadow>
        <cylinderGeometry args={[0.22, 0.28, 0.5, 12]} />
        {std(C.plastic)}
      </mesh>
      {[
        [0, 0.85, 0, 0.45],
        [0.2, 1.05, 0.1, 0.34],
        [-0.18, 1.0, -0.12, 0.3],
      ].map((p, i) => (
        <mesh key={i} position={[p[0], p[1], p[2]]} castShadow>
          <icosahedronGeometry args={[p[3], 0]} />
          {std(i % 2 ? C.plantDark : C.plant, { flatShading: true })}
        </mesh>
      ))}
    </group>
  );
}

function Monitor({ tex }: { tex: THREE.Texture }) {
  return (
    <group>
      <mesh position={[0, 0.18, 0]} castShadow>
        <boxGeometry args={[0.5, 0.36, 0.05]} />
        {std(C.dark)}
      </mesh>
      <mesh position={[0, 0.18, 0.027]}>
        <planeGeometry args={[0.44, 0.3]} />
        <meshStandardMaterial map={tex} emissive={"#9fd2ff"} emissiveMap={tex} emissiveIntensity={1.1} toneMapped={false} />
      </mesh>
      <mesh position={[0, -0.02, 0]} castShadow>
        <cylinderGeometry args={[0.03, 0.03, 0.06, 8]} />
        {std(C.metalLight)}
      </mesh>
      <mesh position={[0, -0.06, 0]} castShadow>
        <boxGeometry args={[0.2, 0.02, 0.12]} />
        {std(C.metalLight)}
      </mesh>
    </group>
  );
}

function Desk() {
  const top = useScreenTexture("timeline");
  const grade = useScreenTexture("grade");
  return (
    <group>
      {/* desk top */}
      <RoundedBox args={[1.7, 0.08, 0.8]} radius={0.02} position={[0, 0.7, 0]} castShadow receiveShadow>
        {std(C.woodDark)}
      </RoundedBox>
      {[
        [-0.78, 0.35, 0.32],
        [0.78, 0.35, 0.32],
        [-0.78, 0.35, -0.32],
        [0.78, 0.35, -0.32],
      ].map((p, i) => (
        <mesh key={i} position={p as [number, number, number]} castShadow>
          <boxGeometry args={[0.07, 0.7, 0.07]} />
          {std(C.metal)}
        </mesh>
      ))}
      {/* dual monitors */}
      <group position={[-0.32, 0.74, 0]} rotation={[0, 0.18, 0]}>
        <Monitor tex={top} />
      </group>
      <group position={[0.32, 0.74, 0]} rotation={[0, -0.18, 0]}>
        <Monitor tex={grade} />
      </group>
      {/* keyboard */}
      <mesh position={[0, 0.75, 0.28]} castShadow>
        <boxGeometry args={[0.42, 0.03, 0.14]} />
        {std(C.plastic)}
      </mesh>
      {/* chair */}
      <group position={[0, 0, 0.75]}>
        <RoundedBox args={[0.45, 0.08, 0.42]} radius={0.04} position={[0, 0.46, 0]} castShadow>
          {std(C.dark)}
        </RoundedBox>
        <RoundedBox args={[0.45, 0.5, 0.08]} radius={0.04} position={[0, 0.72, 0.2]} castShadow>
          {std(C.dark)}
        </RoundedBox>
        <mesh position={[0, 0.27, 0]} castShadow>
          <cylinderGeometry args={[0.04, 0.04, 0.4, 8]} />
          {std(C.metalLight)}
        </mesh>
        {[0, 1, 2, 3, 4].map((i) => {
          const a = (i / 5) * Math.PI * 2;
          return (
            <mesh key={i} position={[Math.cos(a) * 0.22, 0.06, Math.sin(a) * 0.22]} castShadow>
              <boxGeometry args={[0.18, 0.05, 0.05]} />
              {std(C.metal)}
            </mesh>
          );
        })}
      </group>
    </group>
  );
}

function CameraRig() {
  return (
    <group>
      {/* tripod */}
      {[0, 1, 2].map((i) => {
        const a = (i / 3) * Math.PI * 2;
        return (
          <mesh
            key={i}
            position={[Math.cos(a) * 0.28, 0.5, Math.sin(a) * 0.28]}
            rotation={[Math.sin(a) * 0.35, 0, -Math.cos(a) * 0.35]}
            castShadow
          >
            <cylinderGeometry args={[0.025, 0.025, 1.1, 8]} />
            {std(C.metal)}
          </mesh>
        );
      })}
      <mesh position={[0, 1.02, 0]} castShadow>
        <cylinderGeometry args={[0.06, 0.06, 0.08, 10]} />
        {std(C.metalLight)}
      </mesh>
      {/* camera body */}
      <group position={[0, 1.18, 0]}>
        <RoundedBox args={[0.34, 0.26, 0.24]} radius={0.03} castShadow>
          {std(C.dark)}
        </RoundedBox>
        <mesh position={[0, 0.05, 0.16]} rotation={[Math.PI / 2, 0, 0]} castShadow>
          <cylinderGeometry args={[0.1, 0.12, 0.18, 16]} />
          {std(C.metal)}
        </mesh>
        <mesh position={[0, 0.05, 0.26]}>
          <circleGeometry args={[0.07, 16]} />
          <meshStandardMaterial color={"#0a1018"} emissive={"#3a6f9f"} emissiveIntensity={0.5} />
        </mesh>
        <mesh position={[0, 0.2, -0.02]} castShadow>
          <boxGeometry args={[0.1, 0.08, 0.16]} />
          {std(C.metalLight)}
        </mesh>
      </group>
    </group>
  );
}

function Softbox() {
  return (
    <group>
      <mesh position={[0, 0.7, 0]} castShadow>
        <cylinderGeometry args={[0.03, 0.03, 1.4, 8]} />
        {std(C.metal)}
      </mesh>
      <group position={[0, 1.45, 0]} rotation={[0.5, 0.4, 0]}>
        <mesh castShadow>
          <boxGeometry args={[0.5, 0.5, 0.08]} />
          {std(C.metalLight)}
        </mesh>
        <mesh position={[0, 0, 0.05]}>
          <planeGeometry args={[0.44, 0.44]} />
          <meshStandardMaterial color={"#fff7e8"} emissive={"#fff2d8"} emissiveIntensity={1.6} toneMapped={false} />
        </mesh>
      </group>
      <pointLight position={[0.2, 1.3, 0.4]} intensity={6} distance={4} color={"#ffe9c4"} />
    </group>
  );
}

function Package({ offset, beltZ }: { offset: number; beltZ: number }) {
  const ref = useRef<THREE.Group>(null!);
  useFrame((s) => {
    const len = 2.6;
    let z = ((s.clock.elapsedTime * 0.5 + offset) % 1) * len - len / 2;
    ref.current.position.z = z;
    ref.current.position.y = 0.62 + Math.sin((z + offset) * 4) * 0.004;
  });
  return (
    <group ref={ref} position={[0, 0.62, 0]}>
      <RoundedBox args={[0.26, 0.18, 0.26]} radius={0.02} castShadow>
        {std(C.gold, { metalness: 0.2, roughness: 0.5 })}
      </RoundedBox>
      <mesh position={[0, 0.1, 0]}>
        <boxGeometry args={[0.27, 0.005, 0.06]} />
        {std(C.goldBright, { emissive: C.gold, emissiveIntensity: 0.4 })}
      </mesh>
    </group>
  );
}

function Conveyor() {
  return (
    <group>
      <RoundedBox args={[0.7, 0.12, 2.7]} radius={0.04} position={[0, 0.5, 0]} castShadow receiveShadow>
        {std(C.dark)}
      </RoundedBox>
      {Array.from({ length: 9 }).map((_, i) => (
        <mesh key={i} position={[0, 0.5, -1.2 + i * 0.3]} rotation={[0, 0, Math.PI / 2]} castShadow>
          <cylinderGeometry args={[0.07, 0.07, 0.72, 12]} />
          {std(C.metalLight)}
        </mesh>
      ))}
      {[0, 0.34, 0.67].map((o, i) => (
        <Package key={i} offset={o} beltZ={0} />
      ))}
      {/* legs */}
      {[-1, 1].map((s) =>
        [-1.1, 1.1].map((z) => (
          <mesh key={`${s}${z}`} position={[s * 0.28, 0.22, z]} castShadow>
            <boxGeometry args={[0.06, 0.45, 0.06]} />
            {std(C.metal)}
          </mesh>
        ))
      )}
    </group>
  );
}

function RobotArm() {
  const base = useRef<THREE.Group>(null!);
  const upper = useRef<THREE.Group>(null!);
  const fore = useRef<THREE.Group>(null!);
  useFrame((s) => {
    const t = s.clock.elapsedTime;
    base.current.rotation.y = Math.sin(t * 0.4) * 0.6;
    upper.current.rotation.x = -0.5 + Math.sin(t * 0.5) * 0.25;
    fore.current.rotation.x = 0.8 + Math.cos(t * 0.5) * 0.3;
  });
  return (
    <group ref={base}>
      <mesh position={[0, 0.1, 0]} castShadow>
        <cylinderGeometry args={[0.24, 0.3, 0.2, 16]} />
        {std(C.metalLight)}
      </mesh>
      <mesh position={[0, 0.28, 0]} castShadow>
        <cylinderGeometry args={[0.16, 0.18, 0.2, 16]} />
        {std(C.gold, { metalness: 0.4, roughness: 0.4 })}
      </mesh>
      <group ref={upper} position={[0, 0.38, 0]}>
        <mesh position={[0, 0.4, 0]} castShadow>
          <boxGeometry args={[0.14, 0.85, 0.14]} />
          {std(C.metal)}
        </mesh>
        <group ref={fore} position={[0, 0.8, 0]}>
          <mesh position={[0, 0.32, 0]} castShadow>
            <boxGeometry args={[0.11, 0.7, 0.11]} />
            {std(C.metalLight)}
          </mesh>
          <mesh position={[0, 0.68, 0]} castShadow>
            <boxGeometry args={[0.16, 0.12, 0.16]} />
            {std(C.gold)}
          </mesh>
        </group>
      </group>
    </group>
  );
}

function Shelf() {
  const grid = useScreenTexture("grid");
  const bookCols = ["#c06a44", "#d8b274", "#3a5f7a", "#5f8f57", "#a8503c", "#e9e3d6"];
  return (
    <group>
      {/* floating shelves */}
      {[1.7, 2.15].map((y, r) => (
        <group key={r} position={[0, y, 0]}>
          <RoundedBox args={[1.5, 0.06, 0.32]} radius={0.02} castShadow receiveShadow>
            {std(C.woodDark)}
          </RoundedBox>
          {Array.from({ length: 9 }).map((_, i) => (
            <mesh key={i} position={[-0.62 + i * 0.15, 0.16, 0]} rotation={[0, 0, (Math.random() - 0.5) * 0.05]} castShadow>
              <boxGeometry args={[0.1, 0.26, 0.2]} />
              {std(bookCols[(i + r) % bookCols.length])}
            </mesh>
          ))}
        </group>
      ))}
      {/* picture wall */}
      <group position={[0, 1.0, 0]}>
        {Array.from({ length: 6 }).map((_, i) => (
          <mesh key={i} position={[-0.5 + (i % 3) * 0.5, 0.28 - Math.floor(i / 3) * 0.42, 0]} castShadow>
            <boxGeometry args={[0.4, 0.32, 0.03]} />
            <meshStandardMaterial map={grid} color={"#fff"} roughness={0.6} />
          </mesh>
        ))}
      </group>
    </group>
  );
}

function Sofa() {
  return (
    <group>
      <RoundedBox args={[1.5, 0.4, 0.7]} radius={0.08} position={[0, 0.32, 0]} castShadow receiveShadow>
        {std(C.sofaSolid)}
      </RoundedBox>
      <RoundedBox args={[1.5, 0.5, 0.18]} radius={0.08} position={[0, 0.55, -0.28]} castShadow>
        {std(C.sofaSolid)}
      </RoundedBox>
      {[-0.66, 0.66].map((x) => (
        <RoundedBox key={x} args={[0.18, 0.45, 0.7]} radius={0.07} position={[x, 0.45, 0]} castShadow>
          {std(C.sofaSolid)}
        </RoundedBox>
      ))}
      {[-0.36, 0.36].map((x) => (
        <RoundedBox key={x} args={[0.62, 0.14, 0.6]} radius={0.06} position={[x, 0.55, 0.02]} castShadow>
          {std("#cf7a55")}
        </RoundedBox>
      ))}
    </group>
  );
}

function FloorLamp() {
  return (
    <group>
      <mesh position={[0, 0.02, 0]} castShadow>
        <cylinderGeometry args={[0.16, 0.18, 0.04, 16]} />
        {std(C.metal)}
      </mesh>
      <mesh position={[0, 0.8, 0]} castShadow>
        <cylinderGeometry args={[0.02, 0.02, 1.6, 8]} />
        {std(C.metalLight)}
      </mesh>
      <mesh position={[0, 1.65, 0]} castShadow>
        <coneGeometry args={[0.22, 0.3, 16, 1, true]} />
        {std(C.goldBright, { side: THREE.DoubleSide, emissive: C.gold, emissiveIntensity: 0.6 })}
      </mesh>
      <pointLight position={[0, 1.55, 0]} intensity={3} distance={3} color={"#ffe6bd"} />
    </group>
  );
}

/* ------------------------------------------------------------- interactivity */
type ZoneId = "produktion" | "schnitt" | "pipeline" | "marke";

function Zone({
  id,
  position,
  label,
  active,
  hovered,
  onHover,
  onSelect,
  children,
}: {
  id: ZoneId;
  position: [number, number, number];
  label: string;
  active: ZoneId | null;
  hovered: ZoneId | null;
  onHover: (z: ZoneId | null) => void;
  onSelect: (z: ZoneId) => void;
  children: React.ReactNode;
}) {
  const g = useRef<THREE.Group>(null!);
  const isOn = hovered === id || active === id;
  useFrame(() => {
    const target = isOn ? 0.18 : 0;
    g.current.position.y += (target - g.current.position.y) * 0.12;
  });
  return (
    <group position={position}>
      <group
        ref={g}
        onPointerOver={(e) => {
          e.stopPropagation();
          onHover(id);
          document.body.style.cursor = "pointer";
        }}
        onPointerOut={(e) => {
          e.stopPropagation();
          onHover(null);
          document.body.style.cursor = "";
        }}
        onClick={(e) => {
          e.stopPropagation();
          onSelect(id);
        }}
      >
        {children}
      </group>
      {/* highlight ring */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.02, 0]}>
        <ringGeometry args={[0.95, 1.08, 48]} />
        <meshBasicMaterial color={C.gold} transparent opacity={isOn ? 0.8 : 0.12} toneMapped={false} />
      </mesh>
      {/* hotspot marker */}
      <Html position={[0, isOn ? 2.4 : 2.1, 0]} center distanceFactor={9} zIndexRange={[20, 0]}>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onSelect(id);
          }}
          onPointerOver={() => onHover(id)}
          onPointerOut={() => onHover(null)}
          className={`select-none whitespace-nowrap rounded-full border px-3 py-1 font-mono text-[10px] uppercase tracking-[0.16em] backdrop-blur transition-all duration-300 ${
            isOn
              ? "border-gold bg-gold text-[#1a1206] scale-105"
              : "border-white/25 bg-black/40 text-white/80"
          }`}
        >
          {label}
        </button>
      </Html>
    </group>
  );
}

/* ----------------------------------------------------------------- the scene */
export function Scene({
  active,
  onSelect,
}: {
  active: ZoneId | null;
  onSelect: (z: ZoneId) => void;
}) {
  const root = useRef<THREE.Group>(null!);
  const floorTex = useFloorTexture();
  const [hovered, setHovered] = useState<ZoneId | null>(null);
  const intro = useRef(0);

  useFrame((s, dt) => {
    // intro ease
    intro.current = Math.min(1, intro.current + dt * 0.6);
    const e = 1 - Math.pow(1 - intro.current, 3);
    // mouse parallax + slow idle spin
    const px = s.pointer.x;
    const py = s.pointer.y;
    const baseSpin = s.clock.elapsedTime * 0.02;
    root.current.rotation.y += ((baseSpin + px * 0.4) - root.current.rotation.y) * 0.05;
    root.current.rotation.x += (0.02 + -py * 0.12 - root.current.rotation.x) * 0.05;
    root.current.position.y = -0.4 + (1 - e) * -3;
    root.current.scale.setScalar(0.8 + e * 0.2);
  });

  return (
    <>
      <OrthographicCamera makeDefault position={[14, 12, 14]} zoom={62} near={-50} far={100} />
      <ambientLight intensity={0.7} />
      <hemisphereLight args={["#fff3e0", "#2a2030", 0.75]} />
      {/* warm key + cool rim for form (shading only — grounding via baked
          contact shadows below, so no costly per-frame shadow-map render) */}
      <directionalLight position={[10, 16, 8]} intensity={2.2} color={"#fff1da"} />
      <directionalLight position={[-8, 6, -6]} intensity={0.6} color={"#8fb4ff"} />
      <pointLight position={[0, 9, 0]} intensity={0.5} color={"#ffe9c4"} />

      <group ref={root}>
        {/* platform */}
        <RoundedBox args={[12, 0.6, 12]} radius={0.12} position={[0, -0.3, 0]} receiveShadow castShadow>
          <meshStandardMaterial map={floorTex} roughness={0.8} metalness={0.02} />
        </RoundedBox>
        {/* rug */}
        <mesh position={[2.6, 0.015, 2.4]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
          <planeGeometry args={[3.6, 2.8]} />
          {std(C.rug, { roughness: 0.95 })}
        </mesh>

        {/* zones */}
        <Zone id="produktion" position={[-3.4, 0, -3]} label="Produktion" active={active} hovered={hovered} onHover={setHovered} onSelect={onSelect}>
          <CameraRig />
          <group position={[1.2, 0, -0.6]}>
            <Softbox />
          </group>
        </Zone>

        <Zone id="schnitt" position={[-3.2, 0, 2.6]} label="Schnitt & Post" active={active} hovered={hovered} onHover={setHovered} onSelect={onSelect}>
          <Desk />
        </Zone>

        <Zone id="pipeline" position={[1.4, 0, -2.6]} label="Content-System" active={active} hovered={hovered} onHover={setHovered} onSelect={onSelect}>
          <Conveyor />
          <group position={[0, 0.46, 1.6]}>
            <RobotArm />
          </group>
        </Zone>

        <Zone id="marke" position={[4.4, 0, -1.2]} label="Markenwelt" active={active} hovered={hovered} onHover={setHovered} onSelect={onSelect}>
          <Shelf />
        </Zone>

        {/* decor */}
        <group position={[3.0, 0, 2.6]}>
          <Sofa />
        </group>
        <group position={[1.2, 0, 3.2]}>
          <FloorLamp />
        </group>
        <group position={[-4.8, 0, -0.2]}>
          <Plant s={1.1} />
        </group>
        <group position={[4.9, 0, 2.0]}>
          <Plant s={0.9} />
        </group>
        <group position={[-1.2, 0, 4.6]}>
          <Plant s={1.0} />
        </group>

        {/* baked soft contact shadow — rendered once (rotates with the group,
            so a single bake stays correct) for smooth performance */}
        <ContactShadows
          frames={1}
          position={[0, 0.02, 0]}
          scale={16}
          blur={3}
          opacity={0.62}
          far={9}
          resolution={1024}
          color="#160c04"
        />
      </group>
      <AdaptiveDpr pixelated={false} />
    </>
  );
}

export type { ZoneId };
