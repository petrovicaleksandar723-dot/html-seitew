"use client";

import { Suspense } from "react";
import * as THREE from "three";
import { Canvas } from "@react-three/fiber";
import { AdaptiveDpr, Preload } from "@react-three/drei";
import { EffectComposer, Bloom, ChromaticAberration, Vignette } from "@react-three/postprocessing";
import { Experience } from "@/components/cosmos/experience";

export function CosmosScene() {
  return (
    <div className="pointer-events-none fixed inset-0 z-0">
      <Canvas
        dpr={[1, 1.6]}
        performance={{ min: 0.5 }}
        gl={{ antialias: true, powerPreference: "high-performance", toneMapping: THREE.ACESFilmicToneMapping, toneMappingExposure: 1.05 }}
        camera={{ fov: 38, position: [0, 0.4, 13], near: 0.1, far: 80 }}
      >
        <Suspense fallback={null}>
          <Experience />
          <Preload all />
        </Suspense>
        <EffectComposer multisampling={0}>
          <Bloom intensity={0.85} luminanceThreshold={0.55} luminanceSmoothing={0.25} mipmapBlur radius={0.7} />
          <ChromaticAberration
            offset={new THREE.Vector2(0.0009, 0.0009)}
            radialModulation={false}
            modulationOffset={0}
          />
          <Vignette eskil={false} offset={0.25} darkness={0.78} />
        </EffectComposer>
        <AdaptiveDpr pixelated={false} />
      </Canvas>
    </div>
  );
}
