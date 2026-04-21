import { create } from "zustand";

export type WorkspaceMode = "guided" | "expert";

export interface WorkspaceState {
  mode: WorkspaceMode;
  setMode: (mode: WorkspaceMode) => void;
  toggleMode: () => void;
}

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  mode: "guided",
  setMode: (mode) => set({ mode }),
  toggleMode: () => set((state) => ({ 
    mode: state.mode === "guided" ? "expert" : "guided" 
  })),
}));
