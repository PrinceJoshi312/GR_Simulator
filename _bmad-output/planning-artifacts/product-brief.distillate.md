# LLM Distillate: GRsimulator Product Brief

## Metadata
- **Product:** GRsimulator (General Relativity Solar System Gravity Simulator)
- **Version:** v1.0.0
- **Primary Model:** Schwarzschild (static, spherically symmetric)
- **Programming Language:** Python
- **Goal:** Relativistic planetary geodesic simulation

## Core Architecture (Four-Layer)
1. **Physics Layer:** Metric definitions (Schwarzschild), Christoffel symbols, and Geodesic equation solver.
2. **Numerics Layer:** High-order adaptive ODE solvers (e.g., Runge-Kutta) for geodesic integration.
3. **Simulation Layer:** Planet objects, system state management, and time evolution controls.
4. **Visualization Layer:** Real-time 3D renderer (Matplotlib/OpenGL/Three.js-ready) with orbit trails and camera control.

## Technical Specifications (v1)
- **Metric:** Schwarzschild (Spacetime around a static Sun mass $M$).
- **Equation of Motion:** Geodesic equation $\frac{d^2 x^\mu}{d\tau^2} + \Gamma^\mu_{\alpha\beta} \frac{dx^\alpha}{d\tau} \frac{dx^\beta}{d\tau} = 0$.
- **Christoffel Symbols:** Explicit equatorial plane $\Gamma^\mu_{\alpha\beta}$ for $(t, r, \theta, \phi)$ with $\theta = \pi/2$.
- **Planet Catalogue:** Sun + 8 planets + Pluto. Initial conditions derived from near-circular orbital distances (AU converted to meters).

## Success Criteria & Validation
- **Mercury Precession:** Reproduce 43 arcsec/century (measured against Schwarzschild analytical solutions).
- **Gravitational Time Dilation:** Correctly model proper time $\tau$ vs coordinate time $t$ for planetary observers.
- **Numerical Stability:** No non-physical orbital collapse over $10^3$ orbits.

## Roadmap & Extensions
- **Phase 2 (Kerr):** Frame-dragging effects from rotating Sun.
- **Phase 3 (N-Body):** Non-linear GR coupling between multiple gravitational bodies.
- **Phase 4 (Lensing):** Photon geodesic ray-tracing for visual distortions.
- **Performance:** C++/CUDA/CuPy integration for GPU acceleration.
