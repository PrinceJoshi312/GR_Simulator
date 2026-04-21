import { useState, useEffect } from "react";

interface Props {
  initialParams: { timestep: number; g: number; central_mass: number; angular_momentum: number };
  onUpdate: (params: { timestep: number; g: number; central_mass: number; angular_momentum: number }) => void;
  disabled?: boolean;
}

export function AdvancedControls({ initialParams, onUpdate, disabled }: Props) {
  const [params, setParams] = useState(initialParams);

  useEffect(() => {
    setParams(initialParams);
  }, [initialParams]);

  const handleChange = (key: keyof typeof params, value: string) => {
    const numValue = parseFloat(value);
    if (!isNaN(numValue)) {
      const newParams = { ...params, [key]: numValue };
      setParams(newParams);
    }
  };

  const handleApply = () => {
    onUpdate(params);
  };

  return (
    <div style={{ marginTop: "16px", display: "flex", flexDirection: "column", gap: "12px" }}>
      <div>
        <label className="telemetry-label" style={{ fontSize: "0.6rem", display: "block", marginBottom: "4px" }}>G CONSTANT</label>
        <input 
          type="number" 
          value={params.g} 
          onChange={(e) => handleChange("g", e.target.value)}
          className="telemetry-value"
          style={{ width: "100%", background: "rgba(0,0,0,0.3)", border: "1px solid var(--border-color)", color: "var(--text-color)", padding: "4px 8px", borderRadius: "4px", fontFamily: "var(--font-mono)" }}
          disabled={disabled}
        />
      </div>

      <div>
        <label className="telemetry-label" style={{ fontSize: "0.6rem", display: "block", marginBottom: "4px" }}>CENTRAL MASS (KG)</label>
        <input 
          type="number" 
          value={params.central_mass} 
          onChange={(e) => handleChange("central_mass", e.target.value)}
          className="telemetry-value"
          style={{ width: "100%", background: "rgba(0,0,0,0.3)", border: "1px solid var(--border-color)", color: "var(--text-color)", padding: "4px 8px", borderRadius: "4px", fontFamily: "var(--font-mono)" }}
          disabled={disabled}
        />
      </div>

      <div>
        <label className="telemetry-label" style={{ fontSize: "0.6rem", display: "block", marginBottom: "4px" }}>ANGULAR MOMENTUM (A)</label>
        <input 
          type="number" 
          step="0.1"
          value={params.angular_momentum} 
          onChange={(e) => handleChange("angular_momentum", e.target.value)}
          className="telemetry-value"
          style={{ width: "100%", background: "rgba(0,0,0,0.3)", border: "1px solid var(--border-color)", color: "var(--text-color)", padding: "4px 8px", borderRadius: "4px", fontFamily: "var(--font-mono)" }}
          disabled={disabled}
        />
        <div style={{ fontSize: "0.6rem", color: "var(--text-muted)", marginTop: "2px" }}>
          Kerr Parameter: a = J/Mc
        </div>
      </div>

      <button
        onClick={handleApply}
        disabled={disabled}
        className="neon-button"
        style={{ width: "100%", fontSize: "0.7rem", marginTop: "8px" }}
      >
        RECALIBRATE PHYSICS
      </button>
    </div>
  );
}
