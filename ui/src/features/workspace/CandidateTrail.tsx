import { useMemo } from "react";
import { Line } from "@react-three/drei";
import { Vector3 } from "three";
import { useMissionPlanningStore } from "../mission-planning/missionPlanningStore";

export function CandidateTrail() {
  const predictedPath = useMissionPlanningStore((state) => state.predictedPath);
  
  const points = useMemo(() => {
    if (!predictedPath || predictedPath.length === 0) {
      return [new Vector3(0, 0, 0), new Vector3(0, 0, 0)];
    }
    // Map 2D (x, y) to 3D (x, 0, z) - following the project convention
    // Note: The project seems to use (x, y) for physics and (x, 0, z) for 3D visualization.
    // Let's verify Axis Mapping from TECHNICAL_DETAILS.md
    return predictedPath.map(([x, y]) => new Vector3(x, 0, -y));
  }, [predictedPath]);

  if (predictedPath.length === 0) return null;

  return (
    <Line
      points={points}
      color="#ffcc00" // Golden yellow for candidate paths
      lineWidth={2}
      dashed
      dashScale={50}
      dashSize={1}
      gapSize={0.5}
      transparent
      opacity={0.8}
    />
  );
}
