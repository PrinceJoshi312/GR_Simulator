import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { OrbitControls, PerspectiveCamera, Stars } from "@react-three/drei";
import { CelestialBody } from "./CelestialBody";
import { OrbitTrail } from "./OrbitTrail";
import { CandidateTrail } from "./CandidateTrail";
import { SpacetimeGrid } from "./SpacetimeGrid";
import { useTelemetryStore } from "../../services/telemetryStore";
import { useRef } from "react";
import { Vector3 } from "three";

interface ViewportProps {
  objects?: Array<{ id: string; color: string; size: number; initialPosition: [number, number, number] }>;
  targetId?: string | null;
  cameraMode?: "standard" | "top-down";
  comparisonMode?: boolean;
}

function NewtonianGhost({ id, size, color }: { id: string, size: number, color: string }) {
  const meshRef = useRef<THREE.Mesh>(null!);
  const objects = useTelemetryStore((state) => state.objects);

  useFrame(() => {
    if (objects[id]) {
      const nPos = objects[id].newtonian_position;
      meshRef.current.position.set(nPos[0], 0, nPos[2]);
    }
  });

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[size * 2.5, 32, 32]} />
      <meshBasicMaterial color={color} transparent opacity={0.3} wireframe />
    </mesh>
  );
}

function CameraController({ targetId, objectsMetadata, cameraMode }: { targetId?: string | null, objectsMetadata: ViewportProps["objects"], cameraMode?: "standard" | "top-down" }) {
  const { camera, controls } = useThree();
  const telemetryObjects = useTelemetryStore((state) => state.objects);
  // Smaller base offset for follow mode to "zoom in"
  const followOffset = useRef(new Vector3(0, 10, 25));
  const topDownOffset = useRef(new Vector3(0, 0, 600)); // High above for top-down

  useFrame(() => {
    if (targetId && telemetryObjects[targetId]) {
      const pos = telemetryObjects[targetId].position;
      const metadata = objectsMetadata?.find(o => o.id === targetId);
      // Scaled based on planet size, but capped for large bodies like sun
      const sizeScale = metadata ? Math.max(2, Math.min(metadata.size * 3, 15)) : 5; 
      
      let targetPos: Vector3;

      if (cameraMode === "top-down") {
        // Top-down: follow X, Z (which maps to simulation X, Y)
        // Look from high Y down to the XZ plane
        targetPos = new Vector3(
          pos[0],
          topDownOffset.current.z + (sizeScale * 5), // Using 'z' field of offset but as 'y' coordinate
          pos[2]
        );
      } else {
        const offset = followOffset.current;
        targetPos = new Vector3(
          pos[0] + offset.x * (sizeScale / 5), 
          pos[1] + offset.y * (sizeScale / 5), 
          pos[2] + offset.z * (sizeScale / 5)
        );
      }
      
      camera.position.lerp(targetPos, 0.1);
      
      if (controls) {
        // @ts-ignore
        const targetVec = new Vector3(...pos);
        // @ts-ignore
        controls.target.lerp(targetVec, 0.1);
        controls.update();
      }
    }
  });

  return null;
}

export function Viewport({ objects = [], targetId, cameraMode = "standard", comparisonMode = false }: ViewportProps) {
  return (
    <div style={{ width: "100%", height: "100%", position: "relative" }}>
      <Canvas
        gl={{ antialias: true }}
        shadows
        onCreated={({ gl }) => {
          gl.setClearColor("#000000");
        }}
      >
        <PerspectiveCamera makeDefault position={[0, 20, 50]} fov={45} />
        <OrbitControls makeDefault enableDamping dampingFactor={0.05} minDistance={1} maxDistance={2000} />

        <CameraController targetId={targetId} objectsMetadata={objects} cameraMode={cameraMode} />

        <ambientLight intensity={0.2} />

        {/* Central Sun */}
        <CelestialBody id="sun" size={12} color="#ffcc33" initialPosition={[0, 0, 0]} />

        {/* Scenario Objects */}
        {objects.map((obj) => (
          <group key={obj.id}>
            <CelestialBody id={obj.id} size={obj.size} color={obj.color} initialPosition={obj.initialPosition} />
            {comparisonMode && <NewtonianGhost id={obj.id} size={obj.size} color={obj.color} />}
            <OrbitTrail objectId={obj.id} color={obj.color} maxPoints={5000} />
          </group>
        ))}

        <CandidateTrail />

        <SpacetimeGrid />
        <Stars radius={300} depth={60} count={10000} factor={7} saturation={0} fade speed={1} />
      </Canvas>

      <div style={{ position: "absolute", bottom: "10px", right: "10px", color: "white", fontSize: "10px", background: "rgba(0,0,0,0.5)", padding: "5px", borderRadius: "4px" }}>
        Renderer: WebGL | {targetId ? `Following: ${targetId}` : "Free Camera"}
      </div>
    </div>
  );
}
