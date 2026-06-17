import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

/** Warm controlled gold lighting rig for the content engine. */
export default function HeroLights() {
  const key = useRef<THREE.PointLight>(null);
  const rim = useRef<THREE.SpotLight>(null);

  useFrame((state) => {
    const t = state.clock.elapsedTime;
    if (key.current) {
      key.current.position.x = Math.sin(t * 0.3) * 4;
      key.current.position.y = 2 + Math.cos(t * 0.22) * 1.5;
    }
    if (rim.current) {
      rim.current.intensity = 60 + Math.sin(t * 0.8) * 18;
    }
  });

  return (
    <>
      <ambientLight intensity={0.18} color="#3a2a14" />
      {/* warm gold key light */}
      <pointLight ref={key} position={[4, 3, 4]} intensity={42} color="#f4d7a1" distance={28} decay={1.4} />
      {/* deep amber fill from below */}
      <pointLight position={[-5, -3, 2]} intensity={20} color="#d6a65f" distance={26} decay={1.6} />
      {/* cool counter rim to carve the glass */}
      <pointLight position={[-3, 4, -5]} intensity={14} color="#5b7da8" distance={24} decay={1.6} />
      {/* sharp rim spot */}
      <spotLight
        ref={rim}
        position={[0, 6, 6]}
        angle={0.6}
        penumbra={1}
        intensity={60}
        color="#fff0d4"
        distance={30}
        decay={1.5}
      />
    </>
  );
}
