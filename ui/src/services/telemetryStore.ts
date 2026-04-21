import { create } from "zustand";

export interface TelemetryState {
  objects: Record<string, {
    position: [number, number, number];
    velocity: [number, number, number];
    newtonian_position: [number, number, number];
    proper_time: number;
    coordinate_time: number;
    validation?: {
      is_stable: boolean;
      is_finite: boolean;
      is_outside_rs: boolean;
      r: number;
      rs: number;
      error_estimate: number;
    };
  }>;
  setTelemetry: (id: string, data: TelemetryState["objects"][string]) => void;
  updateAllTelemetry: (objects: TelemetryState["objects"]) => void;
  resetTelemetry: () => void;
}

export const useTelemetryStore = create<TelemetryState>((set) => ({
  objects: {},
  setTelemetry: (id, data) => set((state) => ({
    objects: { ...state.objects, [id]: data }
  })),
  updateAllTelemetry: (objects) => set({ objects }),
  resetTelemetry: () => set({ objects: {} }),
}));
