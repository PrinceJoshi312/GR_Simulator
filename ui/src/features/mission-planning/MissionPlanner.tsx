import React, { useState } from "react";
import { useMissionPlanningStore, Burn } from "./missionPlanningStore";
import { useWorkspaceStore } from "../../services/workspaceStore";
import { runService } from "../../services/runService";

export function MissionPlanner() {
  const { currentRun } = useWorkspaceStore();
  const { 
    burnPlan, 
    addBurn, 
    removeBurn, 
    clearPlan, 
    setPredictedPath, 
    setPredicting, 
    isPredicting,
    lookaheadDuration,
    setLookahead
  } = useMissionPlanningStore();

  const [newBurn, setNewBurn] = useState<Burn>({
    start_t: 0,
    duration: 60,
    magnitude: 1000,
    angle_rad: 0,
  });

  const handlePredict = async () => {
    if (!currentRun || !currentRun.objects || currentRun.objects.length === 0) return;
    
    setPredicting(true);
    try {
      // Use the first object (usually the rocket) for prediction
      const targetName = currentRun.objects[0].name;
      const res = await fetch(`/api/runs/${currentRun.run_id}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          object_name: targetName,
          burn_plan: burnPlan,
          lookahead_duration: lookaheadDuration
        })
      });
      const json = await res.json();
      if (json.data && json.data.path) {
        setPredictedPath(json.data.path);
      }
    } catch (err) {
      console.error("Prediction failed", err);
    } finally {
      setPredicting(false);
    }
  };

  return (
    <div style={{ padding: "15px", background: "#111", color: "#eee", borderRadius: "8px", border: "1px solid #333" }}>
      <h3 style={{ margin: "0 0 15px 0", color: "#ffcc00" }}>🚀 Mission Planner</h3>
      
      <div style={{ marginBottom: "20px" }}>
        <label style={{ display: "block", fontSize: "12px", marginBottom: "5px" }}>Lookahead (seconds)</label>
        <input 
          type="number" 
          value={lookaheadDuration} 
          onChange={(e) => setLookahead(Number(e.target.value))}
          style={{ width: "100%", background: "#222", color: "#fff", border: "1px solid #444", padding: "5px" }}
        />
      </div>

      <div style={{ marginBottom: "20px" }}>
        <h4 style={{ fontSize: "14px", marginBottom: "10px" }}>Add Burn</h4>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
          <div>
            <label style={{ fontSize: "10px" }}>Start T (s)</label>
            <input type="number" value={newBurn.start_t} onChange={e => setNewBurn({...newBurn, start_t: Number(e.target.value)})} style={inputStyle} />
          </div>
          <div>
            <label style={{ fontSize: "10px" }}>Duration (s)</label>
            <input type="number" value={newBurn.duration} onChange={e => setNewBurn({...newBurn, duration: Number(e.target.value)})} style={inputStyle} />
          </div>
          <div>
            <label style={{ fontSize: "10px" }}>Magnitude (N)</label>
            <input type="number" value={newBurn.magnitude} onChange={e => setNewBurn({...newBurn, magnitude: Number(e.target.value)})} style={inputStyle} />
          </div>
          <div>
            <label style={{ fontSize: "10px" }}>Angle (rad)</label>
            <input type="number" value={newBurn.angle_rad} onChange={e => setNewBurn({...newBurn, angle_rad: Number(e.target.value)})} style={inputStyle} />
          </div>
        </div>
        <button 
          onClick={() => addBurn(newBurn)}
          style={{ width: "100%", marginTop: "10px", padding: "8px", background: "#333", color: "#fff", border: "1px solid #555", cursor: "pointer" }}
        >
          Add to Plan
        </button>
      </div>

      <div style={{ marginBottom: "20px" }}>
        <h4 style={{ fontSize: "14px", marginBottom: "10px" }}>Burn Sequence</h4>
        {burnPlan.length === 0 && <div style={{ fontSize: "12px", color: "#666" }}>No burns scheduled.</div>}
        {burnPlan.map((burn, i) => (
          <div key={i} style={{ fontSize: "12px", background: "#222", padding: "8px", marginBottom: "5px", borderRadius: "4px", position: "relative" }}>
            T+{burn.start_t}s: {burn.magnitude}N for {burn.duration}s @ {burn.angle_rad}rad
            <button 
              onClick={() => removeBurn(i)}
              style={{ position: "absolute", right: "5px", top: "5px", background: "none", border: "none", color: "#f44", cursor: "pointer" }}
            >
              ×
            </button>
          </div>
        ))}
      </div>

      <div style={{ display: "flex", gap: "10px" }}>
        <button 
          onClick={handlePredict}
          disabled={isPredicting}
          style={{ flex: 1, padding: "10px", background: "#ffcc00", color: "#000", fontWeight: "bold", border: "none", borderRadius: "4px", cursor: isPredicting ? "wait" : "pointer" }}
        >
          {isPredicting ? "Calculating..." : "Project Trajectory"}
        </button>
        <button 
          onClick={clearPlan}
          style={{ padding: "10px", background: "#444", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer" }}
        >
          Clear
        </button>
      </div>
    </div>
  );
}

const inputStyle = {
  width: "100%", 
  background: "#222", 
  color: "#fff", 
  border: "1px solid #444", 
  padding: "5px",
  fontSize: "12px"
};
