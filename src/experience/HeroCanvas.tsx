import { Suspense, useRef } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { Environment, Lightformer, AdaptiveDpr } from "@react-three/drei";
import { EffectComposer, Bloom, Vignette } from "@react-three/postprocessing";
import * as THREE from "three";
import ContentEngine from "./ContentEngine";
import FloatingReelFrames from "./FloatingReelFrames";
import DepthParticles from "./DepthParticles";
import HeroLights from "./HeroLights";

/**
 * Scroll-linked camera: dollies back and tilts as the hero scrolls away, so the
 * WebGL engine carries the transition into the next scene.
 */
function CameraRig() {
  const { camera } = useThree();
  const scroll = useRef(0);

  useFrame(() => {
    // progress through the first viewport
    scroll.current = Math.min(1, window.scrollY / window.innerHeight);
    const p = scroll.current;
    const targetZ = 8 + p * 4;
    const targetY = p * 1.4;
    camera.position.z += (targetZ - camera.position.z) * 0.06;
    camera.position.y += (targetY - camera.position.y) * 0.06;
    camera.lookAt(0, 0, 0);
  });

  return null;
}

/** Full WebGL hero canvas — the main wow moment. */
export default function HeroCanvas() {
  const reduced =
    typeof window !== "undefined" &&
    (window.matchMedia("(pointer: coarse)").matches || window.innerWidth < 720);

  return (
    <Canvas
      className="hero__canvas"
      dpr={reduced ? [1, 1.4] : [1, 1.8]}
      gl={{
        antialias: true,
        alpha: true,
        powerPreference: "high-performance",
        toneMapping: THREE.ACESFilmicToneMapping,
        toneMappingExposure: 1.05,
      }}
      camera={{ position: [0, 0, 8], fov: 42 }}
      onCreated={({ scene }) => {
        scene.fog = new THREE.FogExp2("#020202", 0.045);
      }}
    >
      <color attach="background" args={["#020202"]} />
      <CameraRig />
      <HeroLights />

      {/* Logo + particles render immediately — no async dependency. */}
      <group position={reduced ? [0, 0, 0] : [1.5, 0.5, 0.2]} scale={reduced ? 1 : 1.8}>
        <ContentEngine />
      </group>
      <DepthParticles count={reduced ? 180 : 460} />

      {/* Environment (reflections) in its own boundary so it can't block the logo. */}
      <Suspense fallback={null}>
        <Environment resolution={256} frames={1}>
          <Lightformer intensity={2.2} color="#f4d7a1" position={[0, 4, 4]} scale={[8, 4, 1]} />
          <Lightformer intensity={1.4} color="#d6a65f" position={[-5, -2, 2]} scale={[6, 6, 1]} />
          <Lightformer intensity={1} color="#5b7da8" position={[5, 2, -4]} scale={[5, 5, 1]} />
        </Environment>
      </Suspense>

      {/* Floating video panels suspend on video decode — fully isolated. */}
      <Suspense fallback={null}>
        <FloatingReelFrames reduced={reduced} />
      </Suspense>

      {!reduced && (
        <EffectComposer enableNormalPass={false}>
          <Bloom
            intensity={0.9}
            luminanceThreshold={0.2}
            luminanceSmoothing={0.5}
            mipmapBlur
            radius={0.75}
          />
          <Vignette eskil={false} offset={0.25} darkness={0.85} />
        </EffectComposer>
      )}

      <AdaptiveDpr pixelated />
    </Canvas>
  );
}
