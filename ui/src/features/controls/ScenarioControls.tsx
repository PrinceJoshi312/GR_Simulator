import { createRun, type RunPayload } from "../../services/runService";

interface Props {
  onScenarioChange: (run: RunPayload) => void;
  disabled?: boolean;
}

export function ScenarioControls({ onScenarioChange, disabled }: Props) {
  const scenarios = [
    { id: "solar-system", name: "Solar System", description: "Standard planetary orbits." },
    { id: "black-hole", name: "Rotating Black Hole", description: "High curvature & Kerr spin.", a: 0.8 },
    { id: "mercury-only", name: "Relativistic Precession", description: "Mercury's anomalous orbit." },
  ];

  const handleSelect = async (scenarioId: string) => {
    try {
      const run = await createRun(scenarioId); 
      onScenarioChange(run);
    } catch (err) {
      console.error("Failed to load scenario", err);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
      {scenarios.map((s) => (
        <button
          key={s.id}
          disabled={disabled}
          onClick={() => handleSelect(s.id, s.a)}
          className="glass-panel"
          style={{ 
            textAlign: "left", 
            cursor: disabled ? "not-allowed" : "pointer",
            padding: "10px",
            border: "1px solid var(--border-color)",
            transition: "all 0.2s"
          }}
        >
          <div style={{ fontSize: "0.75rem", fontWeight: "bold", color: "var(--primary-color)" }}>{s.name.toUpperCase()}</div>
          <div style={{ fontSize: "0.6rem", color: "var(--text-muted)" }}>{s.description}</div>
        </button>
      ))}
    </div>
  );
}
