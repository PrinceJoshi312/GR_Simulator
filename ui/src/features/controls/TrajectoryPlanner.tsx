import { useState } from "react";
import { theme } from "../../styles/theme";

type Burn = { start_t: number; duration: number; magnitude: number; angle_rad: number };
type Props = { runId: string; onPredict: (burns: Burn[]) => void };

export function TrajectoryPlanner({ runId, onPredict }: Props) {
  const [burns, setBurns] = useState<Burn[]>([]);

  const addBurn = () => {
    setBurns([...burns, { start_t: 0, duration: 1, magnitude: 100, angle_rad: 0 }]);
  };

  const updateBurn = (index: number, field: keyof Burn, value: number) => {
    const newBurns = [...burns];
    newBurns[index][field] = value;
    setBurns(newBurns);
  };

  return (
    <div style={{ marginTop: "20px", padding: "10px", border: `1px solid ${theme.colors.border}` }}>
      <h3 style={{ fontSize: "0.9em" }}>Trajectory Planner</h3>
      {burns.map((burn, i) => (
        <div key={i} style={{ marginBottom: "10px" }}>
          <input type="number" placeholder="Start" value={burn.start_t} onChange={(e) => updateBurn(i, "start_t", parseFloat(e.target.value))} style={{ width: "50px" }} />
          <input type="number" placeholder="Dur" value={burn.duration} onChange={(e) => updateBurn(i, "duration", parseFloat(e.target.value))} style={{ width: "50px" }} />
          <button onClick={() => onPredict(burns)}>Plan</button>
        </div>
      ))}
      <button onClick={addBurn}>Add Burn</button>
    </div>
  );
}
