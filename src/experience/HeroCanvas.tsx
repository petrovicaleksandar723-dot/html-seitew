import { useEffect, useRef } from "react";
import { Canvas } from "@react-three/fiber";
import * as THREE from "three";
import { ContentEngine } from "./ContentEngine";
import { DepthParticles } from "./DepthParticles";
import { HeroLights } from "./HeroLights";
import { heroState } from "./heroState";

export default function HeroCanvas() {
  const wrap = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fine = window.matchMedia("(pointer:fine)").matches;
    const onMove = (e: MouseEvent) => {
      heroState.px = (e.clientX / window.innerWidth - 0.5) * 2;
      heroState.py = (e.clientY / window.innerHeight - 0.5) * 2;
    };
    const onScroll = () => {
      const p = Math.min(1, (window.scrollY || 0) / window.innerHeight);
      heroState.scroll = p;
      if (wrap.current) wrap.current.style.opacity = String(Math.max(0, 1 - p * 1.1));
    };
    if (fine) window.addEventListener("mousemove", onMove);
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    return () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("scroll", onScroll);
    };
  }, []);

  return (
    <div ref={wrap} className="hero-canvas">
      <Canvas
        style={{ width: "100%", height: "100%" }}
        dpr={[1, 1.75]}
        camera={{ position: [0, 0, 9], fov: 42 }}
        gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
        onCreated={({ gl }) => {
          gl.toneMapping = THREE.ACESFilmicToneMapping;
          gl.toneMappingExposure = 1.12;
        }}
      >
        <fogExp2 attach="fog" args={["#020202", 0.07]} />
        <HeroLights />
        <ContentEngine />
        <DepthParticles />
      </Canvas>
    </div>
  );
}
