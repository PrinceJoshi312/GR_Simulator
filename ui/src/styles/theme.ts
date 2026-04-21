export const theme = {
  colors: {
    background: "#000000",
    surface: "#050505",
    surfaceElevated: "#0a0a0a",
    border: "#222222",
    borderSubtle: "#111111",
    primary: "#00e5ff",
    primaryText: "#000000",
    text: "#eeeeee",
    textMuted: "#888888",
    textDisabled: "#444444",
    success: "#4CAF50",
    warning: "#FF9800",
    error: "#F44336",
    info: "#2196F3",
    accent: "#9C27B0",
  },
  spacing: (n: number) => `${n * 8}px`,
  typography: {
    fontFamily: "Inter, system-ui, sans-serif",
    fontFamilyMono: "monospace",
    fontSize: {
      xs: "0.7em",
      sm: "0.75em",
      md: "0.8em",
      lg: "1em",
      xl: "1.1em",
    },
  },
  shadows: {
    focus: "0 0 0 2px #00e5ff",
  },
};
