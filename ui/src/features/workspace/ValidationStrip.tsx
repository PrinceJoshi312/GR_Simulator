import { theme } from "../../styles/theme";

interface Props {
  state: string;
  runId?: string;
}

export function ValidationStrip({ state, runId }: Props) {
  const getStatusConfig = () => {
    switch (state) {
      case "running": return { color: theme.colors.success, text: "ACTIVE SIMULATION", icon: "●" };
      case "paused": return { color: theme.colors.warning, text: "SIMULATION PAUSED", icon: "‖" };
      case "idle": return { color: theme.colors.info, text: "SYSTEM READY", icon: "○" };
      case "loading": return { color: theme.colors.accent, text: "INITIALIZING...", icon: "…" };
      case "error": return { color: theme.colors.error, text: "SYSTEM ERROR", icon: "▲" };
      default: return { color: theme.colors.textDisabled, text: "UNKNOWN STATE", icon: "?" };
    }
  };

  const { color, text, icon } = getStatusConfig();

  return (
    <div 
      role="status"
      aria-live="polite"
      style={{ 
        background: theme.colors.surfaceElevated, 
        borderTop: `2px solid ${color}`,
        padding: "6px 15px",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        fontSize: theme.typography.fontSize.xs,
        color: theme.colors.text,
        fontFamily: theme.typography.fontFamilyMono,
        textTransform: "uppercase",
        letterSpacing: "0.05em"
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: "15px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
          <span style={{ color, fontSize: "1.2em" }} aria-hidden="true">{icon}</span>
          <span style={{ color, fontWeight: "bold" }}>{text}</span>
        </div>
        {runId && <span style={{ color: theme.colors.textDisabled }}>RUN_ID: {runId.slice(0, 8)}</span>}
      </div>
      
      <div style={{ display: "flex", gap: "20px" }}>
        <span style={{ color: theme.colors.textMuted }}>METRIC: <span style={{ color: theme.colors.text }}>SCHWARZSCHILD</span></span>
        <span style={{ color: theme.colors.textMuted }}>SOLVER: <span style={{ color: theme.colors.text }}>RK45</span></span>
        <span style={{ color: theme.colors.textMuted }}>PRECISION: <span style={{ color: theme.colors.text }}>F64</span></span>
      </div>
    </div>
  );
}
