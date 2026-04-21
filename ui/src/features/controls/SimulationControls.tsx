import { AdvancedControls } from "./AdvancedControls";
import { WorkspaceMode } from "../../services/workspaceStore";

type Props = {
  hasRun: boolean;
  onRun: () => void;
  onPause: () => void;
  onReset: () => void;
  mode: WorkspaceMode;
  runParams?: { timestep: number; g: number; central_mass: number; angular_momentum: number };
  onUpdateParams?: (params: { timestep: number; g: number; central_mass: number; angular_momentum: number }) => void;
};

export function SimulationControls({ 
  hasRun, 
  onRun, 
  onPause, 
  onReset, 
  mode,
  runParams,
  onUpdateParams
}: Props) {

  const handleSpeedChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (runParams && onUpdateParams) {
        onUpdateParams({ ...runParams, timestep: parseFloat(e.target.value) });
    }
  };

  return (
    <section aria-label="simulation-controls">
      <div style={{ display: "flex", gap: "8px", marginBottom: "16px" }}>
        <button 
          onClick={onRun} 
          className={`neon-button ${!hasRun ? "active" : ""}`}
          style={{ flex: 1, fontSize: "0.7rem" }}
          disabled={hasRun}
        >
          INITIATE
        </button>
        <button 
          onClick={onPause} 
          disabled={!hasRun} 
          className="neon-button"
          style={{ flex: 1, fontSize: "0.7rem" }}
        >
          PAUSE
        </button>
        <button 
          onClick={onReset} 
          disabled={!hasRun} 
          className="neon-button"
          style={{ flex: 1, fontSize: "0.7rem" }}
        >
          RESET
        </button>
      </div>

      {runParams && (
        <div style={{ marginBottom: "16px" }}>
           <div className="section-title" style={{ fontSize: "0.6rem", color: "var(--text-muted)" }}>Temporal Compression</div>
           <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
             <input 
                type="range" 
                min="1" 
                max="86400" 
                step="100"
                value={runParams.timestep}
                onChange={handleSpeedChange}
                style={{ flex: 1, accentColor: "var(--primary-color)" }}
             />
             <span style={{ fontSize: "0.7rem", fontFamily: "var(--font-mono)", minWidth: "60px", textAlign: "right" }}>
                {runParams.timestep.toFixed(0)}s/step
             </span>
           </div>
           <div style={{ fontSize: "0.55rem", color: "var(--text-muted)", marginTop: "4px" }}>
              1 step = { (runParams.timestep / 3600).toFixed(1) } hours
           </div>
        </div>
      )}

      {mode === "expert" && runParams && onUpdateParams && (
        <AdvancedControls 
          initialParams={runParams} 
          onUpdate={onUpdateParams}
          disabled={!hasRun}
        />
      )}

      {mode === "guided" && (
        <div className="glass-panel" style={{ fontSize: "0.65rem", color: "var(--text-muted)", padding: "10px", marginTop: "12px", borderStyle: "dashed" }}>
          SYS_LOG: Select scenario and INITIATE to begin geodesic integration.
        </div>
      )}
    </section>
  );
}
