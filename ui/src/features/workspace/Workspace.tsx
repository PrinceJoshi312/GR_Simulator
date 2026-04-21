import { useState, useEffect, useMemo } from "react";

import { createRun, pauseRun, resetRun, updateRuntimeParams, removeObject, type RunPayload } from "../../services/runService";
import { SimulationControls } from "../controls/SimulationControls";
import { ScenarioControls } from "../controls/ScenarioControls";
import { CatalogControls } from "../controls/CatalogControls";
import { Viewport } from "./Viewport";
import { ValidationStrip } from "./ValidationStrip";
import { TelemetryPanel } from "../telemetry/TelemetryPanel";
import { PhysicsOverlay } from "./PhysicsOverlay";
import { MissionPlanner } from "../mission-planning/MissionPlanner";
import { connectTelemetry, disconnectTelemetry } from "../../services/telemetryService";
import { useWorkspaceStore } from "../../services/workspaceStore";
import "../../styles/dashboard.css";

export function Workspace() {
  const [run, setRun] = useState<RunPayload | null>(null);
  const [state, setState] = useState("idle");
  const [targetId, setTargetId] = useState<string | null>(null);
  const [cameraMode, setCameraMode] = useState<"standard" | "top-down">("standard");
  const [comparisonMode, setComparisonMode] = useState(false);
  
  const { mode, toggleMode } = useWorkspaceStore();

  const CATALOG_METADATA: Record<string, { color: string; size: number }> = {
    mercury: { color: "#A5A5A5", size: 1.2 },
    venus: { color: "#E3BB76", size: 2.0 },
    earth: { color: "#2271B3", size: 2.2 },
    mars: { color: "#E27B58", size: 1.5 },
    jupiter: { color: "#D39C7E", size: 5.0 },
    saturn: { color: "#C5AB6E", size: 4.5 },
    uranus: { color: "#B5E3E3", size: 3.5 },
    neptune: { color: "#6081FF", size: 3.5 },
    sun: { color: "#ffcc33", size: 12.0 }
  };

  const objects = useMemo(() => {
    if (!run || !run.objects) {
      return [
        { id: "mercury", color: CATALOG_METADATA.mercury.color, size: CATALOG_METADATA.mercury.size, initialPosition: [57.9, 0, 0] as [number, number, number] },
        { id: "earth", color: CATALOG_METADATA.earth.color, size: CATALOG_METADATA.earth.size, initialPosition: [149.6, 0, 0] as [number, number, number] }
      ];
    }
    return run.objects.map(obj => ({
      id: obj.name,
      color: CATALOG_METADATA[obj.name.toLowerCase()]?.color || "#ffffff",
      size: CATALOG_METADATA[obj.name.toLowerCase()]?.size || 1.0,
      initialPosition: [obj.state.x / 1e9, obj.state.y / 1e9, 0] as [number, number, number]
    }));
  }, [run]);

  async function handleRun() {
    setState("loading");
    try {
      const started = await createRun("solar-system");
      setRun(started);
      setState(started.state);
      connectTelemetry(started.run_id);
    } catch {
      setState("error");
    }
  }

  async function handlePause() {
    if (!run) return;
    try {
      const paused = await pauseRun(run.run_id);
      setRun(paused);
      setState(paused.state);
    } catch {
      setState("error");
    }
  }

  async function handleReset() {
    if (!run) return;
    try {
      const reset = await resetRun(run.run_id);
      setRun(reset);
      setState(reset.state);
      disconnectTelemetry();
      setTargetId(null);
    } catch {
      setState("error");
    }
  }

  async function handleUpdateParams(params: { timestep: number; g: number; central_mass: number; angular_momentum: number }) {
    if (!run) return;
    try {
      const updated = await updateRuntimeParams(run.run_id, params);
      setRun(updated);
    } catch {
      setState("error");
    }
  }

  async function handleRemoveObject(name: string) {
    if (!run) return;
    try {
      const updated = await removeObject(run.run_id, name);
      setRun(updated);
      if (targetId === name) {
        setTargetId(null);
      }
    } catch {
      setState("error");
    }
  }

  useEffect(() => {
    return () => disconnectTelemetry();
  }, []);

  const runParams = run ? { 
    timestep: run.timestep, 
    g: run.g, 
    central_mass: run.central_mass, 
    angular_momentum: run.angular_momentum 
  } : undefined;

  return (
    <div className="workspace-container">
      <header className="header">
        <div style={{ display: "flex", alignItems: "center", gap: "24px" }}>
          <div className="header-logo">GRSIMULATOR // v0.2.0</div>
          <button 
            onClick={toggleMode}
            className={`neon-button ${mode === "expert" ? "active" : ""}`}
            style={{ fontSize: "0.6rem", padding: "4px 8px" }}
          >
            MODE: {mode}
          </button>
        </div>
        <div style={{ display: "flex", gap: "16px", alignItems: "center" }}>
          <div className="telemetry-value" style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>
            ENGINE_STATE: <span style={{ color: "var(--primary-color)" }}>{state.toUpperCase()}</span>
          </div>
        </div>
      </header>
      
      <aside className="sidebar">
        <section className="glass-panel">
          <div className="section-title">Scenario Selector</div>
          <ScenarioControls onScenarioChange={(newRun) => {
            setRun(newRun);
            setState(newRun.state);
            connectTelemetry(newRun.run_id);
          }} disabled={state === "running"} />
        </section>

        <section className="glass-panel">
          <div className="section-title">Manual Controls</div>
          <SimulationControls 
            hasRun={!!run} 
            onRun={handleRun} 
            onPause={handlePause} 
            onReset={handleReset} 
            mode={mode}
            runParams={runParams}
            onUpdateParams={handleUpdateParams}
          />
        </section>

        <section className="glass-panel">
          <div className="section-title">Object Catalog</div>
          <CatalogControls 
            runId={run?.run_id || null} 
            targetId={targetId} 
            onObjectAdded={(updatedRun) => setRun(updatedRun)} 
          />
        </section>

        {mode === "expert" && run && (
          <section className="glass-panel">
            <div className="section-title">Mission Planner</div>
            <MissionPlanner />
          </section>
        )}

        {run && (
           <section className="glass-panel" style={{ marginTop: "auto" }}>
              <div className="section-title">Run Context</div>
              <div className="telemetry-grid">
                 <span className="telemetry-label">SCENARIO</span>
                 <span className="telemetry-value">{run.scenario_id}</span>
                 <span className="telemetry-label">CENTRAL_M</span>
                 <span className="telemetry-value">{run.central_mass.toExponential(2)} kg</span>
                 <span className="telemetry-label">G_CONST</span>
                 <span className="telemetry-value">{run.g.toExponential(4)}</span>
              </div>
           </section>
        )}
      </aside>

      <main className="viewport-area">
        <Viewport objects={objects} targetId={targetId} cameraMode={cameraMode} comparisonMode={comparisonMode} />
        
        {mode === "guided" && <PhysicsOverlay />}

        <div style={{ position: "absolute", top: "20px", right: "20px", display: "flex", flexDirection: "column", gap: "10px", width: "280px" }}>
           <section className="glass-panel" style={{ padding: "12px" }}>
              <div className="section-title">Live Telemetry</div>
              <TelemetryPanel targetId={targetId} />
           </section>
        </div>

        <div style={{ position: "absolute", bottom: "20px", left: "20px", display: "flex", gap: "10px", alignItems: "flex-end" }}>
            <div className="glass-panel" style={{ display: "flex", gap: "8px", padding: "8px" }}>
              <button 
                onClick={() => setTargetId(null)} 
                className={`neon-button ${targetId === null ? "active" : ""}`}
                style={{ fontSize: "0.7rem" }}
              >
                FREE CAM
              </button>
              {objects.map(obj => (
                <button 
                  key={obj.id}
                  onClick={() => setTargetId(obj.id)} 
                  className={`neon-button ${targetId === obj.id ? "active" : ""}`}
                  style={{ fontSize: "0.7rem" }}
                >
                  {obj.id}
                </button>
              ))}
              <div style={{ width: "1px", background: "var(--border-color)", margin: "0 4px" }} />
              <button 
                onClick={() => setCameraMode(prev => prev === "standard" ? "top-down" : "standard")} 
                className={`neon-button ${cameraMode === "top-down" ? "active" : ""}`}
                style={{ fontSize: "0.7rem" }}
              >
                TOP-DOWN
              </button>
              <button 
                onClick={() => setComparisonMode(prev => !prev)} 
                className={`neon-button ${comparisonMode ? "active" : ""}`}
                style={{ fontSize: "0.7rem" }}
              >
                EINSTEIN VS NEWTON
              </button>
            </div>
        </div>
      </main>

      <footer className="footer">
        <div style={{ flex: 1 }}>SYSTEM_READY // NO_ERRORS_DETECTED</div>
        <ValidationStrip state={state} runId={run?.run_id} />
      </footer>
    </div>
  );
}
