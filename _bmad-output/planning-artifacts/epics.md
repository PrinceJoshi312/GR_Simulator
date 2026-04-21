---
stepsCompleted: [1, 2, 3, 4]
inputDocuments:
  - "_bmad-output/planning-artifacts/prd.md"
  - "_bmad-output/planning-artifacts/architecture.md"
  - "_bmad-output/planning-artifacts/ux-design-specification.md"
lastStep: 4
status: "complete"
completedAt: "2026-04-13"
---

# GRsimulator - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for GRsimulator, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: System can calculate the Schwarzschild metric tensor for a static, spherically symmetric central mass.
FR2: System can solve Christoffel symbols for the equatorial plane (theta = pi/2).
FR3: System can integrate the geodesic equation for test particles within the specified metric.
FR4: System can account for gravitational time dilation (proper time tau vs coordinate time t) for all active objects.
FR5: System can simulate Mercury perihelion precession as an emergent property of spacetime geometry.
FR6: System can support multiple object scales, ranging from solar masses (10^30 kg) to human masses (70 kg), in the same simulation environment.
FR7: Users can configure active propulsion (thrust vectors) for specific objects (rockets).
FR8: System can solve non-geodesic equations of motion by incorporating external thrust into the relativistic framework.
FR9: Users can plan and simulate complex trajectories (for example, slingshot maneuvers) that account for thrust and curvature.
FR10: Users can monitor real-time relativistic time-drift (proper vs coordinate) during active missions.
FR11: Users can load initial conditions for standard solar system bodies (Sun + 8 Planets + Pluto) from a pre-configured catalog.
FR12: Users can define custom objects with specific mass, initial position, and velocity.
FR13: Users can adjust simulation parameters (time-step, mass of the central body, gravitational constant) in real-time.
FR14: Users can pause, resume, and reset the simulation state.
FR15: Users can execute pre-defined scenarios (for example, mercury_precession.py, falcon9_launch.py) via CLI or script loader.
FR16: System can render a 3D visualization of curved spacetime paths.
FR17: System can display persistent orbit trails that track the historical path of each object.
FR18: Users can control a 3D camera (pan, zoom, rotate, follow-object) to inspect simulation from any angle.
FR19: System can display real-time telemetry (position, velocity, proper time, coordinate time) for the selected object.
FR20: Users can export simulation telemetry history to standard formats (CSV/NumPy) for external research.
FR21: System can run a built-in validation suite comparing simulation results against analytical Schwarzschild solutions.
FR22: System can generate accuracy reports detailing deviation from theoretical predictions.
FR23: Users can save and load simulation states (state serialization) to reproduce specific orbital anomalies or mission results.

### NonFunctional Requirements

NFR1: Geodesic integration for a single test particle must complete in under 10ms per time-step on a standard CPU.
NFR2: 3D visualization must maintain 60 FPS during active simulation.
NFR3: Loading full solar system catalog and pre-calculating metric tensor should complete in under 2 seconds.
NFR4: Cumulative orbital radius error for stable Schwarzschild orbit must not exceed 0.01 percent per 100 orbits.
NFR5: Metric-related calculations must use float64 precision at minimum.
NFR6: Same seed and initial conditions must yield identical results across different hardware architectures.
NFR7: System must remain numerically stable for mass ratios up to 10^30:1.
NFR8: Simulation layer must support up to 100 independent objects without significant accuracy loss.
NFR9: Core physics logic must be clear, unobfuscated Python with inline mathematical comments.
NFR10: Exported telemetry must include metadata header specifying G, M, and metric parameters for the run.

### Additional Requirements

- Use Python 3.10+ with FastAPI and Pydantic for typed API boundaries.
- Use PostgreSQL as system of record and Redis for telemetry/session acceleration.
- Enforce deterministic simulation mode and provenance metadata across runs, validation, and exports.
- Standardize API envelope and error format contracts for all endpoints.
- Include CI gates for lint, typecheck, unit/integration/e2e, and deterministic regression checks.
- Use environment profiles (`dev`, `scientific-test`, `release`) with typed configuration loading.
- Maintain strict architectural boundaries between domain simulation logic and UI/infrastructure adapters.
- Initialize UI workspace from Vite + React + TypeScript baseline selected in architecture decisions.

### UX Design Requirements

UX-DR1: Implement a desktop-first multi-panel workspace that keeps viewport, controls, telemetry, and status/validation context simultaneously visible.
UX-DR2: Provide scenario-first onboarding with one-click runnable presets and guided overlays for first-run success.
UX-DR3: Implement progressive disclosure with guided and expert modes sharing one spatial model to avoid relearning.
UX-DR4: Build domain UI components defined in UX spec: Simulation Control Surface, Telemetry Insight Panel, Validation Strip, Parameter Delta Inspector, and Relativistic Clock Comparator.
UX-DR5: Enforce persistent run lifecycle affordances (run/pause/reset/export) in stable locations across views.
UX-DR6: Implement real-time feedback loops connecting parameter changes to visual trajectories and telemetry deltas.
UX-DR7: Apply dark-first scientific visual system with semantic status colors and high-legibility overlays.
UX-DR8: Use 8px spacing scale with compact variants for dense telemetry contexts.
UX-DR9: Implement trust cues: benchmark alignment indicators, run metadata visibility, and explainable cause-effect traces.
UX-DR10: Enforce WCAG 2.2 AA accessibility baseline, including keyboard operability, non-color-only status signals, and visible focus states.
UX-DR11: Implement responsive strategy with desktop full workflow, tablet reduced-density touch support, and mobile companion mode.
UX-DR12: Standardize UX consistency patterns for button hierarchy, form validation, error recovery, loading states, and navigation context.

### FR Coverage Map

FR1: Epic 1 - Schwarzschild metric computation in simulation foundation
FR2: Epic 1 - Christoffel symbol solving in core physics layer
FR3: Epic 1 - Geodesic integration pipeline and runtime stepping
FR4: Epic 1 - Proper vs coordinate time tracking in core simulation state
FR5: Epic 3 - Mercury perihelion precession benchmark validation
FR6: Epic 1 - Multi-scale numerical stability baseline handling
FR7: Epic 4 - Thrust vector configuration for rocket-class objects
FR8: Epic 4 - Non-geodesic EOM with external propulsion terms
FR9: Epic 4 - Mission trajectory planning and maneuver iteration
FR10: Epic 4 - Real-time mission relativistic drift monitoring
FR11: Epic 1 - Standard solar system catalog load capabilities
FR12: Epic 1 - Custom object definition and registration
FR13: Epic 1 - Runtime simulation parameter adjustment
FR14: Epic 1 - Pause/resume/reset lifecycle controls
FR15: Epic 1 - Script/scenario execution entry points
FR16: Epic 2 - 3D visualization rendering workspace
FR17: Epic 2 - Persistent orbit trail visualization
FR18: Epic 2 - 3D camera navigation and follow controls
FR19: Epic 2 - Real-time telemetry display for selected objects
FR20: Epic 3 - Metadata-rich telemetry export to CSV/NumPy
FR21: Epic 3 - Built-in analytical validation suite
FR22: Epic 3 - Accuracy report generation pipeline
FR23: Epic 3 - Save/load state serialization and replay

## Epic List

### Epic 1: Scientific Simulation Foundation
Deliver a complete deterministic Schwarzschild simulation baseline with scenario loading, object management, and simulation lifecycle controls.
**FRs covered:** FR1, FR2, FR3, FR4, FR6, FR11, FR12, FR13, FR14, FR15

### Epic 2: Relativistic Visualization & Telemetry Workspace
Deliver the interactive desktop-first 3D workspace with camera control, trails, telemetry surfaces, and UX consistency/accessibility foundations.
**FRs covered:** FR16, FR17, FR18, FR19

### Epic 3: Validation, Accuracy, and Reproducibility
Deliver scientific trust tooling (benchmarks, reports, exports, and state replay) required for credible usage.
**FRs covered:** FR5, FR20, FR21, FR22, FR23

### Epic 4: Active Propulsion and Mission Planning
Deliver non-geodesic propulsion, mission trajectory planning, and real-time relativistic mission telemetry for advanced scenarios.
**FRs covered:** FR7, FR8, FR9, FR10

## Epic 1: Scientific Simulation Foundation

Deliver a complete deterministic Schwarzschild simulation baseline with scenario loading, object management, and simulation lifecycle controls.

### Story 1.1: Initialize Core Simulation Workspace and Run Pipeline

As a researcher,
I want to launch the simulator and execute a baseline Schwarzschild scenario,
So that I can begin testing relativistic behavior immediately.

**Acceptance Criteria:**

**Given** a fresh local setup
**When** I start backend and UI services
**Then** I can run a default scenario from the workspace
**And** run lifecycle controls (`run/pause/reset`) are available and functional.
**And** baseline run metadata (constants, seed, version) is captured for reproducibility.

### Story 1.2: Implement Schwarzschild Physics and Geodesic Integration

As a researcher,
I want metric, Christoffel, and geodesic computations implemented correctly,
So that simulation trajectories are physically meaningful.

**Acceptance Criteria:**

**Given** a valid central mass and initial object state
**When** simulation starts
**Then** Schwarzschild metric and equatorial Christoffel symbols are computed for integration.
**And** geodesic integration advances states using configured precision (`float64` minimum).
**And** proper time and coordinate time are tracked per active object.

### Story 1.3: Object Catalog, Custom Objects, and Runtime Controls

As a simulation user,
I want to load standard bodies, add custom objects, and tune parameters at runtime,
So that I can explore different relativistic conditions.

**Acceptance Criteria:**

**Given** the simulation workspace is running
**When** I select catalog bodies or create a custom object
**Then** objects are added with validated initial conditions.
**And** runtime controls for timestep, G, and central mass apply safely without corrupting run state.
**And** pause/resume/reset maintains deterministic behavior.

## Epic 2: Relativistic Visualization & Telemetry Workspace

Deliver the interactive desktop-first 3D workspace with camera control, trails, telemetry surfaces, and UX consistency/accessibility foundations.

### Story 2.1: Build 3D Viewport, Camera Controls, and Orbit Trails

As an educator,
I want interactive 3D views and orbit trails,
So that I can visually explain relativistic effects.

**Acceptance Criteria:**

**Given** a running simulation
**When** I view the workspace
**Then** object trajectories render in 3D with persistent trail support.
**And** camera controls (pan/zoom/rotate/follow) are available and smooth.
**And** rendering remains stable under expected MVP object counts.

### Story 2.2: Implement Real-Time Telemetry and Validation Strip

As a researcher,
I want live telemetry and validation context,
So that I can interpret outputs confidently while a run is active.

**Acceptance Criteria:**

**Given** an active run
**When** telemetry updates stream
**Then** position, velocity, proper time, and coordinate time appear in real time.
**And** validation/status strip displays run health and benchmark context.
**And** state transitions (`idle/loading/running/warning/error`) are consistent with architecture rules.

### Story 2.3: Guided/Expert UX Modes and Accessibility Baseline

As a mixed-skill user,
I want guided and expert experiences with consistent controls,
So that I can use the tool effectively regardless of depth.

**Acceptance Criteria:**

**Given** the workspace UI
**When** I toggle guided vs expert mode
**Then** the spatial model remains consistent and only density/depth changes.
**And** button hierarchy, form validation, and error/loading patterns follow UX consistency rules.
**And** WCAG 2.2 AA requirements are met for focus visibility, keyboard operation, and non-color-only status messaging.

## Epic 3: Validation, Accuracy, and Reproducibility

Deliver scientific trust tooling (benchmarks, reports, exports, and state replay) required for credible usage.

### Story 3.1: Implement Validation Suite with Mercury Benchmark

As a researcher,
I want automated comparison against analytical Schwarzschild expectations,
So that I can verify simulation correctness.

**Acceptance Criteria:**

**Given** benchmark scenarios are available
**When** I execute the validation suite
**Then** computed metrics are compared to reference analytical expectations.
**And** Mercury precession benchmark output is produced with deviation values.
**And** pass/fail thresholds are configurable and recorded with run metadata.

### Story 3.2: Generate Accuracy Reports and Metadata-Rich Exports

As a researcher,
I want structured reports and exportable telemetry,
So that I can conduct external analysis and peer review.

**Acceptance Criteria:**

**Given** a completed run or validation job
**When** I request reports/exports
**Then** accuracy reports are generated with explicit deviation metrics.
**And** telemetry export is available in CSV/NumPy formats.
**And** each export includes metadata headers (G, M, metric parameters, seed/version/provenance).

### Story 3.3: Save/Load State with Deterministic Replay

As an advanced user,
I want to persist and replay simulation states,
So that I can reproduce anomalies and compare outcomes.

**Acceptance Criteria:**

**Given** a run in progress or completed
**When** I save state and later load it
**Then** the simulation resumes from equivalent state with deterministic continuation.
**And** state schema includes required contracts for objects, clocks, and simulation parameters.
**And** invalid or mismatched state files fail with actionable error messages.

## Epic 4: Active Propulsion and Mission Planning

Deliver non-geodesic propulsion, mission trajectory planning, and real-time relativistic mission telemetry for advanced scenarios.

### Story 4.1: Add Thrust-Enabled Object Model and Non-Geodesic EOM

As a mission planner,
I want thrust vectors applied to selected objects,
So that I can simulate powered trajectories in curved spacetime.

**Acceptance Criteria:**

**Given** a rocket-type object
**When** thrust configuration is applied
**Then** non-geodesic equations of motion include external force terms correctly.
**And** thrust behavior is isolated to eligible object types.
**And** safety checks prevent unstable/invalid control values from crashing runs.

### Story 4.2: Build Mission Trajectory Planning Workflow

As a mission planner,
I want to define burns and evaluate candidate trajectories,
So that I can explore slingshot and transfer maneuvers.

**Acceptance Criteria:**

**Given** mission objects and initial conditions
**When** I configure burn sequence/timing
**Then** trajectory candidates are simulated and visualized in the same workspace model.
**And** iteration loop supports compare-adjust-rerun workflow.
**And** candidate trajectory states can be saved/exported for follow-up.

### Story 4.3: Real-Time Mission Time-Drift Monitoring

As a mission planner,
I want proper-vs-coordinate time drift visible during active missions,
So that I can make time-aware planning decisions.

**Acceptance Criteria:**

**Given** an active mission run
**When** telemetry panel is open
**Then** proper and coordinate time deltas are displayed for selected mission objects.
**And** drift indicators update in real time with clear units and context.
**And** mission exports include time-drift telemetry channels and provenance metadata.
