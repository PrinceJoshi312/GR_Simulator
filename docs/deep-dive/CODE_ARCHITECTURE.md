# Code Architecture: Technical Documentation

This document explains the software engineering principles, directory structure, and data flow of **GRsimulator**.

## 1. System Overview

The application is split into a **High-Performance Physics Backend** and a **Modern 3D Frontend Workspace**.

*   **Backend:** FastAPI (Python 3.12) - Handles tensor math, geodesic integration, and state management.
*   **Frontend:** React 19 + Vite - Handles 3D visualization, user controls, and data HUD.
*   **Communication:** Server-Sent Events (SSE) - Pushes 60fps telemetry snapshots from the backend to the UI.

---

## 2. Backend (The Physics Engine)

Located in `/backend`, the server is structured using **Domain-Driven Design (DDD)**.

### Core Modules:
1.  **`app/domain/physics`**: The mathematical heart. Contains metric tensors (Schwarzschild/Kerr) and Christoffel symbol logic.
2.  **`app/domain/simulation`**: Manages the `SimulationEngine`. This class maintains a collection of active simulation runs and handles the background loop.
3.  **`app/domain/validation`**: Real-time benchmarks (e.g., checking Mercury's precession against theoretical values).
4.  **`app/api`**: REST endpoints for controlling the simulation (Play, Pause, Add Object, Update Physics).

### The Heartbeat Loop:
The backend does not wait for the frontend to request data. A background `asyncio` task runs at 60Hz:
```python
async def simulation_loop(engine: SimulationEngine):
    while True:
        await engine.run_step_and_broadcast()
        await asyncio.sleep(1/60)
```
This ensures the physics integration remains deterministic and smooth, regardless of UI lag.

---

## 3. Frontend (The Command Center)

Located in `/ui`, the frontend uses a component-based architecture focused on real-time data visualization.

### Viewport Architecture (Three.js):
We use **React-Three-Fiber (R3F)** to bridge the gap between React state and the WebGL scene.
*   **`Viewport.tsx`**: The main 3D canvas.
*   **`CelestialBody.tsx`**: Procedurally generates planet surfaces and atmospheric glows.
*   **`SpacetimeGrid.tsx`**: A high-resolution mesh that deforms in real-time based on object mass/position using `calculateDisplacement`.

### State Management:
*   **Zustand**: Used for the **Telemetry Store**. High-frequency updates (60fps) are piped directly into this store from the SSE stream. R3F components subscribe to this store for zero-lag movement.
*   **React Context/State**: Used for UI configuration, themes, and sidebar state.

---

## 4. Real-time Telemetry (SSE)

Instead of traditional WebSockets, we use **Server-Sent Events (SSE)** for telemetry.
*   **Why?** SSE is lighter for one-way high-frequency data (Server -> Client).
*   **Process:**
    1.  Backend finishes a physics step.
    2.  Snapshots all object positions ($x, y, z$) and times ($t, \tau$).
    3.  Serializes to JSON and broadcasts to all connected clients.
    4.  Frontend receives the event and updates the 3D scene immediately.

---

## 5. UI/UX: Modern Glassmorphism

The interface is built with **Vanilla CSS** and CSS Variables for a "Scientific Dashboard" look.
*   **`backdrop-filter: blur()`**: Creates the semi-transparent glass effect.
*   **CSS Grid/Flexbox**: Handles the responsive layout (Sidebar for controls, HUD for telemetry, Center for Viewport).
*   **Neon Accents**: High-contrast colors (`#00e5ff`) are used for critical data points to ensure readability against the black background.

---

## 6. Directory Map

```text
/
├── backend/
│   ├── app/
│   │   ├── api/          # Routers and Endpoints
│   │   ├── contracts/    # Pydantic Schemas
│   │   ├── domain/       # Physics and Simulation Logic
│   │   └── main.py       # Entry point & Background task
├── ui/
│   ├── src/
│   │   ├── features/     # Components grouped by feature
│   │   ├── services/     # API and Telemetry clients
│   │   └── styles/       # Global CSS and Themes
├── docs/                 # Documentation
```
