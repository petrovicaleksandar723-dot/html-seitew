import { Suspense, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import {
  Environment,
  Lightformer,
  ContactShadows,
  OrbitControls,
  AdaptiveDpr,
} from "@react-three/drei";
import { EffectComposer, Bloom } from "@react-three/postprocessing";
import * as THREE from "three";
import HeroArtifact from "./HeroArtifact";
import GLBArtifact from "./GLBArtifact";
import ErrorBoundary from "../components/ui/ErrorBoundary";

/** Tracks scroll progress through the hero into a ref (no re-renders). */
function ScrollProbe({ target }: { target: React.MutableRefObject<number> }) {
  useFrame(() => {
    const p = Math.min(1, Math.max(0, window.scrollY / window.innerHeight));
    target.current = p;
  });
  return null;
}

/** Interactive 3D hero canvas — glass+gold artifact on ivory, drag to rotate. */
export default function HeroCanvas() {
  const scroll = useRef(0);
  const reduced =
    typeof window !== "undefined" &&
    (window.matchMedia("(pointer: coarse)").matches || window.innerWidth < 760);

  return (
    <Canvas
      className="hero3d__canvas"
      shadows
      dpr={reduced ? [1, 1.5] : [1, 2]}
      gl={{
        antialias: true,
        alpha: false,
        powerPreference: "high-performance",
        toneMapping: THREE.ACESFilmicToneMapping,
        toneMappingExposure: 1.1,
      }}
      camera={{ position: [0, 0.2, 7], fov: 38 }}
      onCreated={({ scene }) => {
        scene.background = new THREE.Color("#f1ebdf");
      }}
    >
      <ScrollProbe target={scroll} />
      <ambientLight intensity={0.6} />
      <directionalLight position={[4, 6, 5]} intensity={2.2} castShadow shadow-mapSize={[1024, 1024]} />
      <directionalLight position={[-5, 2, -3]} intensity={0.7} color="#caa05a" />

      <Suspense fallback={null}>
        {/* real Higgsfield GLB mark; falls back to the procedural artifact */}
        <ErrorBoundary fallback={<HeroArtifact scroll={scroll} />}>
          <Suspense fallback={<HeroArtifact scroll={scroll} />}>
            <GLBArtifact scroll={scroll} />
          </Suspense>
        </ErrorBoundary>

        <ContactShadows
          position={[0, -2.1, 0]}
          opacity={0.35}
          scale={11}
          blur={2.6}
          far={4}
          color="#3a2c14"
        />

        <Environment resolution={256} frames={1}>
          <Lightformer intensity={2.4} color="#ffffff" position={[0, 4, 4]} scale={[10, 5, 1]} />
          <Lightformer intensity={1.6} color="#f4d7a1" position={[-5, 1, 3]} scale={[6, 6, 1]} />
          <Lightformer intensity={1.2} color="#caa05a" position={[5, -2, 2]} scale={[6, 6, 1]} />
          <Lightformer intensity={1} color="#ffffff" position={[0, -4, -3]} scale={[8, 4, 1]} />
        </Environment>

        {!reduced && (
          <EffectComposer enableNormalPass={false}>
            <Bloom intensity={0.5} luminanceThreshold={0.7} luminanceSmoothing={0.4} mipmapBlur />
          </EffectComposer>
        )}
      </Suspense>

      {/* drag-to-rotate; gentle auto-orbit; locked zoom/pan for a framed feel */}
      <OrbitControls
        enableZoom={false}
        enablePan={false}
        enabled={!reduced}
        autoRotate
        autoRotateSpeed={0.4}
        minPolarAngle={Math.PI / 2.6}
        maxPolarAngle={Math.PI / 1.8}
        rotateSpeed={0.6}
      />

      <AdaptiveDpr pixelated />
    </Canvas>
  );
}
