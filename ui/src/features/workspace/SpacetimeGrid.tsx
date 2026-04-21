
import { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { useTelemetryStore } from "../../services/telemetryStore";

import { calculateDisplacement } from "./physicsUtils";

export function SpacetimeGrid() {
  const meshRef = useRef<THREE.Mesh>(null!);
  const segments = 64; // High resolution
  const range = 5000; 

  const geometry = useMemo(() => {
    const geo = new THREE.PlaneGeometry(range, range, segments, segments);
    geo.rotateX(-Math.PI / 2);
    return geo;
  }, [range, segments]);

  const objects = useTelemetryStore((state) => state.objects);

  useFrame(() => {
    if (!meshRef.current) return;
    const posAttr = meshRef.current.geometry.attributes.position;
    const posArray = posAttr.array as Float32Array;

    for (let i = 0; i < posArray.length; i += 3) {
      const x = posArray[i];
      const z = posArray[i + 2];
      posArray[i + 1] = calculateDisplacement(x, z, objects);
    }

    posAttr.needsUpdate = true;
    meshRef.current.geometry.computeVertexNormals(); // For better lighting
  });

  return (
    <mesh ref={meshRef} geometry={geometry}>
      <meshStandardMaterial 
        color="#00e5ff" 
        wireframe 
        transparent 
        opacity={0.12} 
        emissive="#00e5ff"
        emissiveIntensity={0.2}
        metalness={0.8}
        roughness={0.2}
        depthWrite={false}
      />
    </mesh>
  );
}
