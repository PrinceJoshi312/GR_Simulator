import { theme } from "../../styles/theme";
import { addCatalogObject, addCustomObject, type RunPayload } from "../../services/runService";
import { useState } from "react";
import { useTelemetryStore } from "../../services/telemetryStore";

type Props = {
  runId: string | null;
  onObjectAdded: (run: RunPayload) => void;
  targetId?: string | null;
};

const PLANETS = [
  { id: "mercury", name: "Mercury", color: "#A5A5A5", size: 0.4 },
  { id: "venus", name: "Venus", color: "#E3BB76", size: 0.9 },
  { id: "earth", name: "Earth", color: "#2271B3", size: 1.0 },
  { id: "mars", name: "Mars", color: "#E27B58", size: 0.5 },
  { id: "jupiter", name: "Jupiter", color: "#D39C7E", size: 3.0 },
  { id: "saturn", name: "Saturn", color: "#C5AB6E", size: 2.5 },
  { id: "uranus", name: "Uranus", color: "#B5E3E3", size: 1.5 },
  { id: "neptune", name: "Neptune", color: "#6081FF", size: 1.5 },
];

export function CatalogControls({ runId, onObjectAdded, targetId }: Props) {
  const [loading, setLoading] = useState(false);
  const telemetryObjects = useTelemetryStore((state) => state.objects);

  const handleAdd = async (planetId: string) => {
    if (!runId) return;
    setLoading(true);
    try {
      const updatedRun = await addCatalogObject(runId, planetId);
      onObjectAdded(updatedRun);
    } catch (e) {
      console.error("Failed to add planet", e);
    } finally {
      setLoading(false);
    }
  };

  const handleAddSatellite = async () => {
    if (!runId || !targetId || !telemetryObjects[targetId]) return;
    setLoading(true);
    try {
      const target = telemetryObjects[targetId];
      // Place near the target with some offset and relative velocity
      // Coordinates in telemetry are in visual units (1e9 m), need to convert back for API
      const offset = 5e9; 
      const updatedRun = await addCustomObject(runId, {
        name: `sat_${targetId}_${Date.now() % 1000}`,
        mass: 3.3e23, // Mercury mass
        x: target.position[0] * 1e9 + offset,
        y: target.position[1] * 1e9,
        vx: target.velocity[0] * 1e9,
        vy: target.velocity[1] * 1e9 + 5000, // Extra velocity for orbit
      });
      onObjectAdded(updatedRun);
    } catch (e) {
      console.error("Failed to add satellite", e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ marginTop: "20px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
        <h3 style={{ fontSize: "0.8em", color: theme.colors.textMuted, margin: 0, textTransform: "uppercase" }}>Object Catalog</h3>
        {targetId && targetId !== "sun" && (
          <button
            onClick={handleAddSatellite}
            disabled={!runId || loading}
            style={{
              padding: "4px 8px",
              background: theme.colors.primary,
              color: theme.colors.primaryText,
              border: "none",
              borderRadius: "4px",
              fontSize: "0.65em",
              fontWeight: "bold",
              cursor: "pointer"
            }}
          >
            + ADD SATELLITE TO {targetId.toUpperCase()}
          </button>
        )}
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "8px" }}>
        {PLANETS.map((planet) => (
          <button
            key={planet.id}
            onClick={() => handleAdd(planet.id)}
            disabled={!runId || loading}
            style={{
              padding: "6px",
              background: theme.colors.surfaceElevated,
              border: `1px solid ${theme.colors.border}`,
              borderRadius: "4px",
              color: theme.colors.text,
              fontSize: "0.7em",
              cursor: (!runId || loading) ? "not-allowed" : "pointer",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: "4px",
              transition: "transform 0.1s"
            }}
            onMouseEnter={(e) => (e.currentTarget.style.transform = "scale(1.05)")}
            onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
          >
            <div style={{ width: "12px", height: "12px", borderRadius: "50%", background: planet.color }} />
            {planet.name}
          </button>
        ))}
      </div>
    </div>
  );
}
