# Project Overview

GRsimulator is a high-fidelity, Python-based scientific simulation engine designed to model planetary motion using General Relativity (Schwarzschild metric).

## Executive Summary

The simulator provides a "relativistically correct" environment for orbital dynamics, featuring:
- **Scientific Rigor:** Schwarzschild geodesic integration with `float64` precision.
- **Interactive Workspace:** 3D React-based viewport for real-time telemetry and trajectory planning.
- **Mission Planning:** Active propulsion (thrust) support and relativistic time-drift monitoring.

## Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Physics Kernel** | NumPy, SciPy (Python 3.12) |
| **Backend API** | FastAPI |
| **Frontend** | React 19, Vite, TypeScript |
| **Visualization** | 3D Workspace (React) |

## Core Architecture

The project follows a layered architecture (Physics, Numerics, Simulation, Rendering) to ensure maintainability and scientific accuracy.

- **Physics:** Metric and Christoffel symbol computations.
- **Numerics:** Geodesic and non-geodesic EOM integration.
- **Simulation:** Run management, object states, and telemetry buffering.
- **Rendering:** Interactive 3D visualization and dashboard-based telemetry.
