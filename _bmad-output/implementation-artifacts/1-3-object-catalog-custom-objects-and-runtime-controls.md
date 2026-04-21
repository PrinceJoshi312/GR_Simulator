# Story 1.3: Object Catalog, Custom Objects, and Runtime Controls

Status: done

## Story

As a simulation user,  
I want to load standard bodies, add custom objects, and tune parameters at runtime,  
so that I can explore different relativistic conditions.

## Acceptance Criteria

1. Given the simulation workspace is running, when I select catalog bodies or create a custom object, then objects are added with validated initial conditions.
2. Given a running workspace, when I update timestep, G, or central mass, then runtime controls apply safely without corrupting run state.
3. Given run lifecycle controls, when I pause/resume/reset, then deterministic behavior is preserved.

## Tasks / Subtasks

- [x] Add object catalog and custom-object registration to simulation engine (AC: 1)
  - [x] Support loading predefined catalog bodies.
  - [x] Validate custom object mass/state inputs.
- [x] Add runtime parameter controls for timestep/G/central-mass updates (AC: 2)
  - [x] Apply validated params without invalidating active run state.
- [x] Expose engine controls through typed run API endpoints (AC: 1, 2, 3)
  - [x] Add routes for catalog load, custom object add, and runtime parameter update.
  - [x] Preserve canonical response/error envelopes.
- [x] Expand integration/regression coverage for object management and controls (AC: 1, 2, 3)
  - [x] Add API tests for object add/catalog load/param update.
  - [x] Add deterministic checks across pause/resume/reset and parameter updates.

### Review Findings

- [x] [Review][Patch] `step_run` default path does not apply `run.timestep` updates (`dt` default 1.0 masks runtime timestep control), so AC2 runtime controls are not fully effective in integration behavior [`backend/app/domain/simulation/engine.py`]
- [x] [Review][Patch] `reset_run` only toggles lifecycle state and does not restore baseline object/time state, weakening deterministic-reset semantics in AC3 [`backend/app/domain/simulation/engine.py`]
- [x] [Review][Patch] Runtime parameter updates do not enforce finite numeric values, risking NaN/Inf corruption in active run state [`backend/app/domain/simulation/engine.py`]
- [x] [Review][Patch] Object/parameter controls are applied regardless of run lifecycle state, conflicting with AC preconditions that assume running workspace context [`backend/app/domain/simulation/engine.py`]
- [x] [Review][Patch] Regression coverage does not verify deterministic behavior after runtime parameter updates (task marked complete without full evidence) [`backend/tests/regression/test_deterministic_seed.py`]
- [x] [Review][Patch] Shared module-level engine state in API router risks cross-run/test state bleed and unbounded in-memory growth [`backend/app/api/routers/runs.py`]

## Dev Notes

Follow established backend boundaries from Stories 1.1 and 1.2. Keep APIs typed and deterministic behavior explicit.

## Dev Agent Record

### Agent Model Used

Codex 5.3

### Debug Log References

- 2026-04-13 create/dev kickoff for Story 1.3
- 2026-04-13 DS implementation for Story 1.3
- `pytest` (backend): 12 passed
- `npm test` (ui): 1 passed
- 2026-04-13 CR batch fixes applied for 6 review findings

### Completion Notes List

- Story created from sprint backlog and set to in-progress for immediate implementation.
- Added catalog/custom-object management plus runtime parameter updates in simulation engine.
- Added API routes for catalog object add, custom object add, runtime parameter updates, and resume lifecycle.
- Expanded integration/regression tests to cover object workflows and deterministic lifecycle controls.
- Applied review-driven fixes for timestep application, reset baseline restoration, run-state guards, finite runtime-param checks, and app-scoped engine lifecycle.

### File List

- `_bmad-output/implementation-artifacts/1-3-object-catalog-custom-objects-and-runtime-controls.md`
- `backend/app/contracts/runs.py`
- `backend/app/domain/simulation/engine.py`
- `backend/app/api/routers/runs.py`
- `backend/app/main.py`
- `backend/tests/integration/test_runs_api.py`
- `backend/tests/regression/test_deterministic_seed.py`

## Change Log

- 2026-04-13: Story 1.3 started for implementation.
- 2026-04-13: Implemented Story 1.3 object catalog/custom object/runtime controls; moved story to `review`.
- 2026-04-13: Applied CR patch set and validation tests; moved story to `done`.
