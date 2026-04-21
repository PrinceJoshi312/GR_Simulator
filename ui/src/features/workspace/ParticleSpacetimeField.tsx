import { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { useTelemetryStore } from "../../services/telemetryStore";

export function ParticleSpacetimeField() {
  const pointsRef = useRef<THREE.Points>(null!);
  const count = 2000;
  const range = 1000; // Total size of the field in visual units

  // Initial grid positions
  const [positions, originalPositions] = useMemo(() => {
    const pos = new Float32Array(count * 3);
    const orig = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      // Create a large flat grid on the XZ plane
      const x = (Math.random() - 0.5) * range;
      const z = (Math.random() - 0.5) * range;
      const y = 0;
      
      pos[i * 3] = x;
      pos[i * 3 + 1] = y;
      pos[i * 3 + 2] = z;

      orig[i * 3] = x;
      orig[i * 3 + 1] = y;
      orig[i * 3 + 2] = z;
    }
    return [pos, orig];
  }, []);

  const objects = useTelemetryStore((state) => state.objects);

  useFrame(() => {
    if (!pointsRef.current) return;
    const posAttr = pointsRef.current.geometry.attributes.position;
    const posArray = posAttr.array as Float32Array;

    // We only have the sun at [0,0,0] as a fixed point
    // plus any planets from telemetry.
    const massiveBodies = [
      { x: 0, y: 0, z: 0, mass: 100 }, // Sun (visual weight)
      ...Object.values(objects).map(obj => ({
        x: obj.position[0],
        y: obj.position[1], // Should be 0
        z: obj.position[2],
        mass: 10 // Planet weight
      }))
    ];

    for (let i = 0; i < count; i++) {
      const ox = originalPositions[i * 3];
      const oy = originalPositions[i * 3 + 1];
      const oz = originalPositions[i * 3 + 2];

      let dx = 0;
      let dy = 0;
      let dz = 0;

      massiveBodies.forEach(body => {
        const distSq = (ox - body.x) ** 2 + (oy - body.y) ** 2 + (oz - body.z) ** 2;
        const dist = Math.sqrt(distSq);
        if (dist > 1) {
          // Particles "sink" into the Y axis based on potential
          const pull = (body.mass * 200) / (dist + 50);
          dy -= pull;
        }
      });

      posArray[i * 3] = ox;
      posArray[i * 3 + 1] = dy;
      posArray[i * 3 + 2] = oz;
    }

    posAttr.needsUpdate = true;
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={positions.length / 3}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={1.5}
        color="#44aaff"
        transparent
        opacity={0.6}
        sizeAttenuation
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
}
