import { theme } from "../../styles/theme";

export function PhysicsOverlay() {
  return (
    <div style={{
      position: "absolute",
      top: "20px",
      left: "20px",
      maxWidth: "280px",
      background: "rgba(0, 0, 0, 0.7)",
      border: `1px solid ${theme.colors.border}`,
      borderRadius: "8px",
      padding: "15px",
      color: theme.colors.text,
      fontFamily: theme.typography.fontFamily,
      backdropFilter: "blur(4px)",
      pointerEvents: "none",
      zIndex: 10
    }}>
      <h4 style={{ margin: "0 0 10px 0", color: theme.colors.primary, fontSize: "0.9em", textTransform: "uppercase", letterSpacing: "0.05em" }}>
        Multi-Body Spacetime
      </h4>
      <p style={{ fontSize: "0.75em", lineHeight: "1.4", margin: 0, color: theme.colors.textMuted }}>
        You are observing bodies moving along <strong>geodesics</strong> in a dynamically curved spacetime. 
        Spacetime fabric is warped in real-time by the combined mass of the Sun and all orbiting planets.
      </p>
      <div style={{ marginTop: "12px", fontSize: "0.7em", borderTop: `1px solid ${theme.colors.borderSubtle}`, paddingTop: "10px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
          <span>Metric:</span>
          <span style={{ color: theme.colors.primary }}>Hybrid Post-Newtonian</span>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <span>Symmetry:</span>
          <span style={{ color: theme.colors.primary }}>Multi-Body Dynamic</span>
        </div>
      </div>
    </div>
  );
}
