import { useRef, useState, useEffect } from "react";
import { useFrame } from "@react-three/fiber";
import { Line } from "@react-three/drei";
import { Vector3 } from "three";
import { useTelemetryStore } from "../../services/telemetryStore";

interface OrbitTrailProps {
  objectId: string;
  color?: string;
  maxPoints?: number;
}

import { calculateDisplacement } from "./physicsUtils";

export function OrbitTrail({ objectId, color = "white", maxPoints = 1000 }: OrbitTrailProps) {
  const pointsRef = useRef<Vector3[]>([]);
  const lineRef = useRef<any>(null!);
  const objects = useTelemetryStore((state) => state.objects);

  useFrame(() => {
    if (objects[objectId]) {
      const rawPos = objects[objectId].position;
      const dy = calculateDisplacement(rawPos[0], rawPos[2], objects);
      const currentPos = new Vector3(rawPos[0], dy, rawPos[2]);
      
      // Add point if significant distance moved or first point
      const lastPoint = pointsRef.current[pointsRef.current.length - 1];
      // Adaptive threshold: move at least 0.2 units to record a new point, preventing jitter and redundant rendering
      if (!lastPoint || currentPos.distanceTo(lastPoint) > 0.2) {
        pointsRef.current.push(currentPos);
        
        if (pointsRef.current.length > maxPoints) {
          pointsRef.current.shift();
        }
        
        // Force update of the Line component points
        if (lineRef.current) {
          lineRef.current.setPoints(pointsRef.current);
        }
      }
    }
  });

  // Initial dummy points to prevent R3F Line errors
  const [initialPoints] = useState(() => [new Vector3(0, 0, 0), new Vector3(0, 0, 0)]);

  return (
    <Line
      ref={lineRef}
      points={initialPoints}
      color={color}
      lineWidth={1}
      transparent
      opacity={0.3}
    />
  );
}
