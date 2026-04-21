import { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { Color, AdditiveBlending, BackSide, DoubleSide } from "three";
import { useTelemetryStore } from "../../services/telemetryStore";

interface CelestialBodyProps {
  id: string;
  size?: number;
  color?: string;
  initialPosition?: [number, number, number];
}

import { calculateDisplacement } from "./physicsUtils";

export function CelestialBody({ id, size = 1, color = "orange", initialPosition = [0, 0, 0] }: CelestialBodyProps) {
  const meshRef = useRef<THREE.Mesh>(null!);
  const atmosphereRef = useRef<THREE.Mesh>(null!);
  const detailRef = useRef<THREE.Mesh>(null!);
  const objects = useTelemetryStore((state) => state.objects);


  // Increase base sizes for better visibility as requested
  const visualScale = id === "sun" ? 4.0 : 2.5;
  const finalSize = size * visualScale;

  useFrame((state) => {
    let currentX = 0;
    let currentZ = 0;

    if (id !== "sun" && objects[id]) {
      const pos = objects[id].position;
      currentX = pos[0];
      currentZ = pos[2];
    } else if (id === "sun") {
      currentX = 0;
      currentZ = 0;
    }

    const dy = calculateDisplacement(currentX, currentZ, objects);
    
    // Position the body ON the curvature
    meshRef.current.position.set(currentX, dy, currentZ);
    if (atmosphereRef.current) {
      atmosphereRef.current.position.set(currentX, dy, currentZ);
    }
    if (detailRef.current) {
      detailRef.current.position.set(currentX, dy, currentZ);
    }

    // Rotations
    meshRef.current.rotation.y += id === "sun" ? 0.002 : 0.01;
    if (detailRef.current) {
      detailRef.current.rotation.y += id === "sun" ? 0.003 : 0.015;
    }
  });

  const atmosColor = useMemo(() => new Color(color).multiplyScalar(1.5), [color]);

  const texture = useMemo(() => {
    const canvas = document.createElement("canvas");
    canvas.width = 256;
    canvas.height = 256;
    const ctx = canvas.getContext("2d");
    if (!ctx) return null;

    // Fill base color
    ctx.fillStyle = color;
    ctx.fillRect(0, 0, 256, 256);

    // Add some noise/variation
    for (let i = 0; i < 500; i++) {
      const x = Math.random() * 256;
      const y = Math.random() * 256;
      const radius = Math.random() * 3 + 1;
      ctx.fillStyle = id === "sun" ? "#ffffaa" : "rgba(0,0,0,0.1)";
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fill();
    }
    
    // Add some stripes/bands for giants
    if (id === "jupiter" || id === "saturn") {
        for(let i=0; i<5; i++) {
            ctx.fillStyle = "rgba(255,255,255,0.1)";
            ctx.fillRect(0, i*50, 256, 20);
        }
    }

    const tex = new THREE.CanvasTexture(canvas);
    return tex;
  }, [color, id]);

  return (
    <>
      {/* Main Body */}
      <mesh ref={meshRef} position={initialPosition} castShadow receiveShadow>
        <sphereGeometry args={[finalSize, 64, 64]} />
        <meshStandardMaterial 
          map={texture}
          color={color} 
          emissive={id === "sun" ? color : "black"} 
          emissiveIntensity={id === "sun" ? 2.0 : 0.05}
          roughness={id === "sun" ? 0.1 : 0.6}
          metalness={id === "sun" ? 0.0 : 0.3}
        />
        {id === "sun" && <pointLight intensity={2000} distance={5000} color={color} />}
      </mesh>

      {/* Surface Detail / Clouds / Atmosphere layer */}
      <mesh ref={detailRef} position={initialPosition} scale={1.02}>
        <sphereGeometry args={[finalSize, 64, 64]} />
        <meshStandardMaterial
          color={id === "sun" ? "#ffcc00" : "white"}
          transparent
          opacity={id === "sun" ? 0.3 : 0.2}
          wireframe={id === "sun"}
          blending={id === "sun" ? AdditiveBlending : undefined}
        />
      </mesh>

      {/* Atmospheric Glow */}
      <mesh ref={atmosphereRef} position={initialPosition}>
        <sphereGeometry args={[finalSize * (id === "sun" ? 1.15 : 1.08), 64, 64]} />
        <meshBasicMaterial
          color={atmosColor}
          transparent
          opacity={id === "sun" ? 0.3 : 0.1}
          blending={AdditiveBlending}
          side={BackSide}
        />
      </mesh>

      {/* Additional Sun Corona/Glow if sun */}
      {id === "sun" && (
        <mesh position={initialPosition} scale={1.5}>
          <sphereGeometry args={[finalSize, 32, 32]} />
          <meshBasicMaterial
            color={color}
            transparent
            opacity={0.1}
            blending={AdditiveBlending}
            side={DoubleSide}
          />
        </mesh>
      )}
    </>
  );
}
