import { useTelemetryStore } from "../../services/telemetryStore";

interface Props {
  targetId: string | null;
}

export function TelemetryPanel({ targetId }: Props) {
  const telemetry = useTelemetryStore((state) => targetId ? state.objects[targetId] : null);

  if (!targetId) {
    return (
        <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", fontStyle: "italic", textAlign: "center", padding: "20px" }}>
            NO_TARGET_ACQUIRED
        </div>
    );
  }

  if (!telemetry) {
    return (
        <div style={{ fontSize: "0.7rem", color: "var(--primary-color)", textAlign: "center", padding: "20px" }}>
            AWAITING_DATA_STREAM...
        </div>
    );
  }

  const { position, velocity, proper_time, coordinate_time, validation } = telemetry;
  const formatNum = (n: number) => n.toExponential(3);
  const timeDrift = coordinate_time - proper_time;
  // Dilation factor (dt/dtau). 1.0 means no dilation.
  const dilationFactor = coordinate_time > 0 ? (coordinate_time / proper_time) : 1.0;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--border-color)", paddingBottom: "4px" }}>
         <div style={{ fontSize: "0.8rem", fontWeight: 800, color: "var(--primary-color)" }}>{targetId.toUpperCase()}</div>
         <div style={{ fontSize: "0.6rem", color: "var(--text-muted)" }}>ID: {targetId.slice(0, 8)}</div>
      </div>

      <div className="telemetry-grid">
         <span className="telemetry-label">POS_X</span>
         <span className="telemetry-value">{formatNum(position[0])}</span>
         <span className="telemetry-label">POS_Y</span>
         <span className="telemetry-value">{formatNum(position[1])}</span>
         <span className="telemetry-label">POS_Z</span>
         <span className="telemetry-value">{formatNum(position[2])}</span>
      </div>

      <div className="telemetry-grid" style={{ marginTop: "4px", borderTop: "1px solid rgba(255,255,255,0.05)", paddingTop: "4px" }}>
         <span className="telemetry-label">VEL_X</span>
         <span className="telemetry-value">{formatNum(velocity[0])}</span>
         <span className="telemetry-label">VEL_Y</span>
         <span className="telemetry-value">{formatNum(velocity[1])}</span>
      </div>

      <div style={{ marginTop: "8px", padding: "8px", background: "rgba(0,229,255,0.05)", borderRadius: "4px", border: "1px solid rgba(0,229,255,0.1)" }}>
         <div style={{ fontSize: "0.6rem", color: "var(--primary-color)", fontWeight: "bold", marginBottom: "8px", textTransform: "uppercase" }}>Relativistic Time Dilation</div>
         
         <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "8px" }}>
            <div style={{ flex: 1 }}>
               <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "2px" }}>
                  <span style={{ fontSize: "0.55rem", color: "var(--text-muted)" }}>PROPER (LOCAL)</span>
                  <span style={{ fontSize: "0.55rem", color: "#fff" }}>{proper_time.toFixed(4)}s</span>
               </div>
               <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ fontSize: "0.55rem", color: "var(--text-muted)" }}>COORDINATE (SYS)</span>
                  <span style={{ fontSize: "0.55rem", color: "#fff" }}>{coordinate_time.toFixed(4)}s</span>
               </div>
            </div>
            <div style={{ width: "40px", height: "40px", borderRadius: "50%", border: "2px solid var(--primary-color)", display: "flex", alignItems: "center", justifyContent: "center", position: "relative" }}>
               <div style={{ width: "2px", height: "15px", background: "var(--primary-color)", transformOrigin: "bottom", transform: `rotate(${(proper_time * 360) % 360}deg)` }} />
               <div style={{ position: "absolute", width: "1px", height: "18px", background: "rgba(255,255,255,0.2)", transformOrigin: "bottom", transform: `rotate(${(coordinate_time * 360) % 360}deg)` }} />
            </div>
         </div>

         <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontSize: "0.6rem", color: "var(--text-muted)" }}>DILATION FACTOR (γ)</span>
            <span style={{ fontSize: "0.7rem", color: dilationFactor > 1.0001 ? "#ffcc33" : "var(--primary-color)", fontWeight: "bold" }}>
               {dilationFactor.toFixed(6)}x
            </span>
         </div>
         <div style={{ fontSize: "0.55rem", color: "var(--text-muted)", marginTop: "2px" }}>
            TIME_LOST: <span style={{ color: "#fff" }}>{timeDrift.toFixed(6)}s</span>
         </div>
      </div>

      {validation && (
        <div style={{ marginTop: "4px", padding: "8px", background: "rgba(0,0,0,0.2)", borderRadius: "4px", border: `1px solid ${validation.is_stable ? "var(--border-color)" : "#ff4444"}` }}>
           <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: "0.6rem", fontWeight: "bold", color: validation.is_stable ? "var(--primary-color)" : "#ff4444" }}>
                {validation.is_stable ? "STATUS: STABLE" : "STATUS: CRITICAL"}
              </span>
              <span style={{ fontSize: "0.6rem", color: "var(--text-muted)" }}>
                R/Rs: <span style={{ color: "var(--text-color)" }}>{(validation.r / validation.rs).toFixed(3)}</span>
              </span>
           </div>
        </div>
      )}
    </div>
  );
}
