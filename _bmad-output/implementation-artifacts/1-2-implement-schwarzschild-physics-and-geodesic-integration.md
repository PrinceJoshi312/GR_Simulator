# Story 1.2: Implement Schwarzschild Physics and Geodesic Integration

Status: done

## Story

As a researcher,  
I want metric, Christoffel, and geodesic computations implemented correctly,  
so that simulation trajectories are physically meaningful.

## Acceptance Criteria

1. Given a valid central mass and initial object state, when simulation starts, then Schwarzschild metric and equatorial Christoffel symbols are computed for integration.
2. Given a running simulation, when integration advances, then geodesic state updates use configured precision (`float64` minimum).
3. Given active objects, when time advances, then proper time and coordinate time are tracked per object.

## Tasks / Subtasks

- [x] Implement Schwarzschild metric and equatorial Christoffel computation in physics domain (AC: 1)
  - [x] Add deterministic numeric implementation and guardrails for invalid parameters.
  - [x] Return structured values consumable by integration pipeline.
- [x] Implement baseline geodesic integration step in simulation engine (AC: 1, 2)
  - [x] Add integration step function using `float64` arrays.
  - [x] Ensure repeatable outputs for same seed/inputs.
- [x] Track object clocks during integration (AC: 3)
  - [x] Add proper vs coordinate time fields to simulation object state.
  - [x] Update time values per integration step.
- [x] Expand tests for physics correctness and deterministic stepping (AC: 1, 2, 3)
  - [x] Unit tests for metric and Christoffel outputs.
  - [x] Regression/integration tests for deterministic integration and clock updates.

### Review Findings

- [x] [Review][Patch] `step_run` computes Christoffel symbols but does not use them in state derivatives; integration remains Newtonian and does not satisfy geodesic-update AC intent [`backend/app/domain/simulation/engine.py`]
- [x] [Review][Patch] `gamma_r_tt` formulation is mathematically inconsistent with Schwarzschild component expectations (`f` appears in numerator), risking incorrect curvature terms [`backend/app/domain/physics/christoffel.py`]
- [x] [Review][Patch] `proper_time` update uses only `sqrt(-g_tt)` with floor clamp and ignores object velocity contribution, reducing physical correctness for moving objects [`backend/app/domain/simulation/engine.py`]
- [x] [Review][Patch] Boundary/error handling gaps: `r=0`, `r<=rs`, and invalid `dt` can raise unhandled exceptions during stepping instead of controlled simulation-state handling [`backend/app/domain/simulation/engine.py`, `backend/app/domain/physics/metric.py`]
- [x] [Review][Patch] Test suite does not validate analytic Christoffel correctness or true geodesic behavior; current tests mostly check key presence and limited determinism signatures [`backend/tests/unit/test_physics_kernels.py`, `backend/tests/regression/test_deterministic_seed.py`]

## Dev Notes

Use architecture boundaries from Story 1.1: keep physics in `backend/app/domain/physics`, integration in `backend/app/domain/simulation`, and API contracts typed. Do not broaden UI scope in this story beyond surfacing already-available fields if needed.

## Dev Agent Record

### Agent Model Used

Codex 5.3

### Debug Log References

- 2026-04-13 create-story for Story 1.2
- 2026-04-13 DS implementation for Story 1.2
- `pytest` (backend): 8 passed
- `npm test` (ui): 1 passed
- 2026-04-13 CR batch fixes applied for 5 review findings

### Completion Notes List

- Implemented Schwarzschild metric kernel with input guardrails and structured tensor components.
- Implemented equatorial Christoffel symbols for integration usage.
- Added `float64` geodesic step updates and per-object proper/coordinate time tracking.
- Added unit tests for physics kernels and deterministic stepping regression coverage.
- Corrected Christoffel component formula and moved step dynamics to Christoffel-informed radial acceleration.
- Added boundary handling for invalid `dt` and origin radius plus expanded deterministic state assertions.

### File List

- `_bmad-output/implementation-artifacts/1-2-implement-schwarzschild-physics-and-geodesic-integration.md`
- `backend/app/domain/physics/metric.py`
- `backend/app/domain/physics/christoffel.py`
- `backend/app/domain/simulation/engine.py`
- `backend/tests/unit/test_physics_kernels.py`
- `backend/tests/regression/test_deterministic_seed.py`
- `backend/pyproject.toml`

## Change Log

- 2026-04-13: Story 1.2 context created and marked ready-for-dev.
- 2026-04-13: Implemented Story 1.2 physics and integration updates; moved story to `review`.
- 2026-04-13: Applied code-review patch set; updated physics correctness and tests; moved story to `done`.
