import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { useGLTF } from "@react-three/drei";
import * as THREE from "three";
import { MODEL_URL } from "./modelConfig";

interface Props {
  scroll: React.MutableRefObject<number>;
}

/**
 * Loads the Higgsfield-generated Cleanlines 3D mark (GLB) and presents it as the
 * interactive hero artifact: auto-centered + normalized, floating, scroll-tilted.
 * Suspends while loading; an ErrorBoundary upstream falls back to the procedural
 * artifact if the model fails to load (e.g. CORS).
 */
export default function GLBArtifact({ scroll }: Props) {
  const group = useRef<THREE.Group>(null);
  const { scene } = useGLTF(MODEL_URL);

  // clone, center, normalize scale, enable shadows
  const model = useMemo(() => {
    const root = scene.clone(true);
    const box = new THREE.Box3().setFromObject(root);
    const size = new THREE.Vector3();
    const center = new THREE.Vector3();
    box.getSize(size);
    box.getCenter(center);
    root.position.sub(center);
    const maxDim = Math.max(size.x, size.y, size.z) || 1;
    const s = 3.6 / maxDim;
    root.scale.setScalar(s);
    root.traverse((o) => {
      const m = o as THREE.Mesh;
      if (m.isMesh) {
        m.castShadow = true;
        m.receiveShadow = true;
        const mat = m.material as THREE.MeshStandardMaterial;
        if (mat && "envMapIntensity" in mat) mat.envMapIntensity = 1.4;
      }
    });
    return root;
  }, [scene]);

  useFrame((state, delta) => {
    if (!group.current) return;
    const t = state.clock.elapsedTime;
    group.current.position.y = Math.sin(t * 0.7) * 0.12;
    group.current.rotation.y += delta * 0.18;
    group.current.rotation.x = THREE.MathUtils.lerp(
      group.current.rotation.x,
      -0.05 + scroll.current * 1.0,
      0.08
    );
  });

  return (
    <group ref={group}>
      <primitive object={model} />
    </group>
  );
}

useGLTF.preload(MODEL_URL);
