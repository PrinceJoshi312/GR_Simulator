# Product Brief: GRsimulator

## Executive Summary

GRsimulator is a Python-based, physics-accurate solar system simulation that models planetary orbits using Einsteinian spacetime curvature (Schwarzschild metric) instead of Newtonian gravity. It transforms complex General Relativity (GR) formulas into a tangible, real-time 3D experience, allowing users to visualize relativistic phenomena like Mercury's perihelion precession and gravitational time dilation.

Built on a modular, four-layer architecture, GRsimulator is designed to grow from a high-fidelity educational tool into a high-performance astrophysical prototyping engine. By separating physics and numerics from rendering, the project ensures scientific rigor while providing an accessible, extensible platform for students, researchers, and space enthusiasts.

## The Problem

Newtonian gravity is a highly effective approximation, but it fails to account for the precise orbital mechanics of bodies near massive stars. Understanding and visualizing General Relativity is notoriously difficult; existing tools often either oversimplify the math or lack the interactive visualization needed for deep intuition. 

Educational institutions and physics enthusiasts currently lack a "middle ground"—a tool that is scientifically accurate enough to model real-world GR effects but accessible enough to run on a standard workstation with a modern 3D interface.

## The Solution

GRsimulator provides a "relativistically correct" simulation environment. Unlike Newtonian simulators that add "corrections" as an afterthought, GRsimulator treats spacetime as a geometric manifold. It calculates planetary paths as geodesics within the Sun's Schwarzschild field, providing:
- **True Geodesic Integration:** Real-time solving of Christoffel symbols and the geodesic equation.
- **Relativistic Visualization:** Accurate rendering of Mercury's 43 arcsec/century precession and time dilation effects.
- **Modular Architecture:** A clean separation of concerns (Physics, Numerics, Simulation, Rendering) that allows for independent testing and future expansion into rotating metrics (Kerr) and N-body GR.

## What Makes This Different

- **Physics-First Approach:** Many "space simulators" prioritize visuals over accuracy. GRsimulator reverses this, ensuring the math is sound before the first frame is rendered.
- **Geodesic Modeling:** While Newtonian simulators use $F=ma$, GRsimulator solves for the shortest path in curved spacetime, providing a more fundamental representation of gravity.
- **Extensible Framework:** The four-layer design is built for evolution. It anticipates the shift from Schwarzschild to Kerr metrics and from CPU-based Python to GPU-accelerated C++/CUDA, providing a long-term roadmap for high-performance research.

## Who This Serves

- **Physics Students & Educators:** A visual aid for General Relativity courses, making "invisible" math interactive.
- **Science Communicators:** A high-fidelity tool for demonstrating complex astrophysical concepts to a broad audience.
- **Astrophysics Enthusiasts:** A sandbox for "hard science" simulation hobbyists who have outgrown Newtonian physics.
- **Researchers:** A lightweight prototyping tool for testing GR-based orbital dynamics before committing to large-scale clusters.

## Success Criteria

- **Scientific Accuracy:** Empirically validated results matching known GR solutions (e.g., Mercury's 43 arcsec/century precession).
- **Numerical Stability:** Minimal orbital drift over long-term simulations through high-order adaptive solvers.
- **Performance:** Maintain a smooth, real-time 3D frame rate while performing complex geodesic calculations.
- **Extensibility:** Successful implementation of the Schwarzschild-to-Kerr metric transition as a proof of architectural modularity.

## Scope (v1)

- **Metric:** Schwarzschild (static, spherically symmetric mass).
- **Bodies:** Sun (central mass) + 8 planets (Mercury through Neptune) + Pluto.
- **Physics:** Geodesic motion in equatorial plane; Christoffel symbol solving.
- **Visualization:** 3D rendering with orbit trails, camera controls, and basic UI for time/mass adjustments.
- **Exclusions:** Rotating central masses (Kerr), N-body GR coupling between planets, and light ray tracing (v1).

## Vision

GRsimulator aims to become the definitive open-source platform for relativistic orbital dynamics. Within 2-3 years, it will evolve into a GPU-accelerated engine capable of modeling multi-body GR systems, frame-dragging around rotating black holes (Kerr metric), and gravitational lensing through light ray tracing. It will bridge the gap between educational demos and high-end research software.
