import { useTelemetryStore } from "./telemetryStore";

let eventSource: EventSource | null = null;

// Scientific scale factor: 1 meter = 1e-9 visual units (1 million km = 1 unit)
// This makes Mercury (~58M km) appear at ~58 units from center.
const SCALE_FACTOR = 1e-9;

const BACKEND_URL = "http://localhost:8000";

export function connectTelemetry(runId: string) {
  if (eventSource) {
    eventSource.close();
  }

  // Connect to real backend SSE endpoint
  const url = `${BACKEND_URL}/runs/${runId}/telemetry`;
  eventSource = new EventSource(url);

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      
      // The backend snapshot contains 'objects' list
      if (data.objects && Array.isArray(data.objects)) {
        const newObjects: Record<string, any> = {};
        
        data.objects.forEach((obj: any) => {
          const state = obj.state;
          const validation = obj.validation;

          // Map 2D physics (x, y) to 3D visualization (x, 0, z)
          newObjects[obj.name] = {
            position: [state.x * SCALE_FACTOR, 0, state.y * SCALE_FACTOR],
            velocity: [state.vx * SCALE_FACTOR, 0, state.vy * SCALE_FACTOR],
            newtonian_position: [state.nx * SCALE_FACTOR, 0, state.ny * SCALE_FACTOR],
            proper_time: state.proper_time,
            coordinate_time: state.coordinate_time,
            validation: validation ? {
              is_stable: validation.is_stable,
              is_finite: validation.is_finite,
              is_outside_rs: validation.is_outside_rs,
              r: validation.r,
              rs: validation.rs,
              error_estimate: validation.error_estimate
            } : undefined
          };
        });
        
        useTelemetryStore.getState().updateAllTelemetry(newObjects);
      }
    } catch (err) {
      console.error("[Telemetry] Failed to parse message:", err);
    }
  };

  eventSource.addEventListener("ping", () => {
    // Heartbeat received, no action needed but useful for debugging
    // console.debug("[Telemetry] Heartbeat");
  });

  eventSource.onerror = (err) => {
    console.error("[Telemetry] Connection error:", err);
    // Note: EventSource automatically attempts to reconnect on error
  };
}

export function disconnectTelemetry() {
  if (eventSource) {
    console.log("[Telemetry] Disconnecting...");
    eventSource.close();
    eventSource = null;
  }
  useTelemetryStore.getState().resetTelemetry();
}

/**
 * Legacy mock implementation removed for Story 2.2.
 * Real-time telemetry is now driven by the backend Schwarzschild engine.
 */
