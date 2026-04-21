# ⬡ GRsimulator v0.2.0
### *Advanced General Relativity Command Center*

> "Gravity is not a force that pulls; it is the very shape of space and time itself."

**GRsimulator** is a professional-grade scientific simulation engine that models the universe as Einstein saw it. It moves beyond simple Newtonian physics to solve the **Einstein Field Equations** in real-time, visualizing the "fabric" of spacetime through a modern glassmorphism command center.

---

## 🌟 Why GRsimulator?

Most simulators treat gravity as an invisible string pulling planets together. **GRsimulator** treats the Sun or a Black Hole as a weight curving the four-dimensional sheet of spacetime.

- **Kerr & Schwarzschild Metrics:** Support for both static (Schwarzschild) and rotating (Kerr) central masses.
- **Scientific Rigor:** High-fidelity 4th-Order Runge-Kutta (RK4) integration with `float64` precision.
- **Relativistic Time Dilation:** Real-time monitoring of **Proper Time ($\tau$)** vs **Coordinate Time ($t$)**.
- **Frame Dragging:** Witness the **Lense-Thirring effect** around spinning black holes.
- **Einstein vs. Newton Mode:** Toggle real-time "Ghost Orbits" to see where classical physics fails and General Relativity takes over.
- **Top-Down Perspective:** Switch to a high-altitude system view to visualize the global curvature of the solar system.

---

## 🚀 Key Features

- **Modern Glassmorphism UI:** A sleek, aerospace-inspired dashboard with real-time telemetry HUDs.
- **Dynamic Spacetime Fabric:** High-resolution 3D grid that deforms in real-time based on object mass.
- **Einstein vs. Newton Comparison:** Visual wireframe "ghosts" follow purely Newtonian paths, making orbital precession (like Mercury's) instantly visible.
- **Relativistic Time Dilation HUD:** A dual-hand clock visualizer comparing the Local Proper Time (τ) of an object to the System Coordinate Time (t).
- **Top-Down Camera Mode:** A unified "Map View" that locks high above the system to show the Sun and planets simultaneously with their curvature.
- **Temporal Compression:** Adjustable time-scaling from real-time to watching millennia pass in seconds.
- **Scenario Presets:** Instant loading of the Solar System, extreme Black Hole orbits, or Mercury's anomalous precession.

---

## 🛠️ Performance & Customization

The simulator is designed to be scalable based on your hardware. If you experience performance issues or want higher visual fidelity:

- **Grid Resolution:** You can increase or decrease the "smoothness" of the spacetime grid by modifying the `segments` variable in `ui/src/features/workspace/SpacetimeGrid.tsx`. 
    - Higher segments (e.g., 128) provide a "liquid-like" fabric but require a stronger GPU.
    - Lower segments (e.g., 32) are recommended for integrated graphics or older devices.
- **Particle Count:** Adjust the `count` in `ui/src/features/workspace/ParticleSpacetimeField.tsx` to change the density of the background star warping effect.

---

## 📐 The Physics (How It Works)

- **Backend:** FastAPI (Python 3.12) - Domain-Driven Design physics kernel.
- **Frontend:** React 19, TypeScript, Vite.
- **Visualization:** React-Three-Fiber (WebGL), Three.js.
- **Math:** NumPy (Vectorized tensor calculations).
- **Communication:** Server-Sent Events (SSE) for 60Hz telemetry streaming.

---

## 📐 The Physics (How It Works)

1.  **The Metric:** We define the geometry of space (Schwarzschild or Kerr).
2.  **The Connection:** We calculate the "slopes" of curvature (Christoffel Symbols).
3.  **The Path:** We solve the **Geodesic Equation** to find the object's path.
4.  **The Solve:** RK4 integrator steps through time to update 4D coordinates.

---

## 📚 Deep Dive Documentation

For a detailed understanding of the project, explore the following:
*   **[Physics Engine Deep Dive](docs/deep-dive/PHYSICS_ENGINE.md)**: Mathematical breakdown of metrics and equations.
*   **[Code Architecture](docs/deep-dive/CODE_ARCHITECTURE.md)**: Technical overview of the Backend and Frontend design.
*   **[Further Study & Resources](docs/deep-dive/RESOURCES.md)**: Links to textbooks and research papers.

---

## 🚥 Getting Started

### Prerequisites
- Python 3.12+
- Node.js 18+

### Setup & Run
1. **Backend:**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
2. **Frontend:**
   ```bash
   cd ui
   npm install
   npm run dev
   ```

---

## 📜 License & Usage
This project is an **Open-Source Educational & Scientific Research Tool**.

*Created as a Technical Challenge Project by Prince Joshi.*
