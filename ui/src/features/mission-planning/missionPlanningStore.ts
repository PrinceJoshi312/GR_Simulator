import { create } from "zustand";

export interface Burn {
  start_t: number;
  duration: number;
  magnitude: number;
  angle_rad: number;
}

interface MissionPlanningState {
  burnPlan: Burn[];
  predictedPath: [number, number][];
  isPredicting: boolean;
  lookaheadDuration: number;
  targetObjectName: string | null;
  
  addBurn: (burn: Burn) => void;
  removeBurn: (index: number) => void;
  clearPlan: () => void;
  setPredictedPath: (path: [number, number][]) => void;
  setPredicting: (loading: boolean) => void;
  setTargetObject: (name: string) => void;
  setLookahead: (duration: number) => void;
}

export const useMissionPlanningStore = create<MissionPlanningState>((set) => ({
  burnPlan: [],
  predictedPath: [],
  isPredicting: false,
  lookaheadDuration: 3600, // 1 hour default
  targetObjectName: null,

  addBurn: (burn) => set((state) => ({ burnPlan: [...state.burnPlan, burn] })),
  removeBurn: (index) => set((state) => ({ 
    burnPlan: state.burnPlan.filter((_, i) => i !== index) 
  })),
  clearPlan: () => set({ burnPlan: [], predictedPath: [] }),
  setPredictedPath: (path) => set({ predictedPath: path }),
  setPredicting: (loading) => set({ isPredicting: loading }),
  setTargetObject: (name) => set({ targetObjectName: name }),
  setLookahead: (duration) => set({ lookaheadDuration: duration }),
}));
