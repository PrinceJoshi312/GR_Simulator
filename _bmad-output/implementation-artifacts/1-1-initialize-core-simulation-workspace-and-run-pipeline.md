# Story 1.1: Initialize Core Simulation Workspace and Run Pipeline

Status: done

## Story

As a researcher,  
I want to launch the simulator and execute a baseline Schwarzschild scenario,  
so that I can begin testing relativistic behavior immediately.

## Acceptance Criteria

1. Given a fresh local setup, when I start backend and UI services, then I can run a default scenario from the workspace.
2. Given a running workspace, when I use lifecycle controls, then `run/pause/reset` actions are available and functional.
3. Given a completed or active baseline run, when I inspect run metadata, then constants, seed, and version are captured for reproducibility.

## Tasks / Subtasks

- [x] Scaffold backend service and typed contracts for baseline run lifecycle (AC: 1, 2, 3)
  - [x] Create `backend/app/main.py` app entry with health and run router mounting.
  - [x] Add canonical response/error envelope models in `backend/app/contracts/`.
  - [x] Add initial run endpoints (`POST /runs`, `POST /runs/{run_id}/pause`, `POST /runs/{run_id}/reset`).
- [x] Scaffold simulation domain baseline for Schwarzschild default scenario (AC: 1, 3)
  - [x] Add domain stubs in `backend/app/domain/physics/` (`metric.py`, `christoffel.py`) and `backend/app/domain/simulation/engine.py`.
  - [x] Implement deterministic seed handling and default constants loading path.
  - [x] Include run provenance payload (`g`, `central_mass`, `seed`, `scenario_id`, `engine_version`).
- [x] Scaffold UI workspace shell and run lifecycle controls (AC: 1, 2)
  - [x] Initialize Vite + React TypeScript shell in `ui/` (if not present).
  - [x] Add baseline workspace layout in `ui/src/features/workspace/`.
  - [x] Add persistent lifecycle controls (`run/pause/reset`) in stable control region.
- [x] Wire UI to backend contracts with explicit state transitions (AC: 1, 2, 3)
  - [x] Create typed service client in `ui/src/services/` matching backend envelope.
  - [x] Implement control-state model `idle/loading/running/warning/error`.
  - [x] Surface run metadata in workspace status strip/panel.
- [x] Add deterministic regression and integration tests for startup/run lifecycle (AC: 1, 2, 3)
  - [x] Backend integration tests for lifecycle endpoints and metadata persistence.
  - [x] UI tests for lifecycle control availability and state transitions.
  - [x] Add first deterministic regression test to verify repeatable baseline run metadata and step output signatures.

### Review Findings

- [x] [Review][Patch] API errors bypass canonical error envelope; `pause`/`reset` return FastAPI default `detail` payload instead of `{data:null,meta,error}` [`backend/app/api/routers/runs.py`]
- [x] [Review][Patch] UI service methods do not check `response.ok` / envelope error and assume `json.data` always exists, causing runtime failure paths [`ui/src/services/runService.ts`]
- [x] [Review][Patch] `handlePause` and `handleReset` lack `try/catch`, risking unhandled promise rejections and broken UI state on network/API failures [`ui/src/features/workspace/Workspace.tsx`]
- [x] [Review][Patch] Run provenance omits app/API version required by story context (`engine_version` present but no app version) [`backend/app/domain/simulation/engine.py`, `backend/app/contracts/runs.py`, `ui/src/features/workspace/Workspace.tsx`]
- [x] [Review][Patch] Regression/integration coverage is incomplete for stated requirements (no step-output determinism assertion, no error/invalid-transition API coverage, no envelope contract assertions) [`backend/tests/regression/test_deterministic_seed.py`, `backend/tests/integration/test_runs_api.py`]
- [x] [Review][Patch] UI controls are not extracted into `ui/src/features/controls/` as required by story file structure constraints [`ui/src/features/workspace/Workspace.tsx`]
- [x] [Review][Patch] Unused `Field` import in contracts can trigger lint/type quality gates [`backend/app/contracts/runs.py`]

## Dev Notes

### Epic Context

Story 1.1 is the first story of Epic 1 (Scientific Simulation Foundation). It establishes the baseline execution loop that all subsequent physics, telemetry, validation, and mission stories build on. This story should prioritize correctness of workflow and contract shape over deep physics completeness.

### Technical Requirements

- Use Python 3.10+ backend with FastAPI and Pydantic typed boundaries.
- Use React + TypeScript frontend in desktop-first workspace model.
- Treat deterministic mode as non-negotiable from first runnable flow.
- Ensure scientific values use `float64` minimum through contracts and engine internals.
- Track and expose run metadata required for reproducibility: constants, seed, engine/app version, scenario identity.

### Architecture Compliance Guardrails

- Respect module boundaries:
  - Domain logic only inside `backend/app/domain/*`.
  - API serialization only at `backend/app/api/*` and `backend/app/contracts/*`.
  - UI must consume backend only via typed REST services; no direct domain coupling.
- Enforce naming/format patterns:
  - Python `snake_case`, React component files `PascalCase.tsx`.
  - API/resource names and JSON fields in `snake_case`.
  - Canonical envelopes:
    - Success: `{ "data": ..., "meta": { ... }, "error": null }`
    - Error: `{ "data": null, "meta": { "request_id": ... }, "error": { ... } }`
- Preserve deterministic provenance through each lifecycle transition (`run`, `pause`, `reset`).

### UX Guardrails

- Keep run lifecycle affordances visible and stable (do not hide in nested menus).
- Preserve scenario-first flow: user should reach first meaningful run quickly.
- Maintain clear state communication (`idle/loading/running/warning/error`) with text + icon cues, not color-only.
- Keep workspace regions persistent: viewport, controls, telemetry/status context.
- Accessibility baseline (WCAG 2.2 AA): keyboard-operable controls, visible focus, actionable error feedback.

### File Structure Requirements

- Backend files to create or update:
  - `backend/app/main.py`
  - `backend/app/api/routers/health.py`
  - `backend/app/api/routers/runs.py`
  - `backend/app/contracts/` (run/request/response schemas)
  - `backend/app/domain/physics/metric.py`
  - `backend/app/domain/physics/christoffel.py`
  - `backend/app/domain/simulation/engine.py`
  - `backend/tests/integration/` and `backend/tests/regression/`
- UI files to create or update:
  - `ui/src/main.tsx`
  - `ui/src/features/workspace/`
  - `ui/src/features/controls/`
  - `ui/src/services/`
  - `ui/tests/` and/or `ui/e2e/`

### Testing Requirements

- Backend:
  - Endpoint tests for `run/pause/reset` happy path + invalid-state transitions.
  - Contract tests to enforce canonical envelope and `snake_case` fields.
  - Deterministic regression test using fixed seed and constants.
- Frontend:
  - Unit/component tests for control availability and lifecycle state rendering.
  - Integration test for backend-client interaction and metadata display.
- CI alignment:
  - Ensure lint/typecheck/unit/integration deterministic checks are wired or scaffolded.

### Latest Tech Information

- Architecture-pinned versions should be treated as baseline for this sprint:
  - FastAPI `0.135.x` (current stable observed: `0.135.3`)
  - React `19.x` (architecture baseline remains React 19)
  - Vite starter baseline (latest major observed is 8.x; keep project on architecture-approved baseline unless explicitly migrated)
- Do not upgrade framework major versions inside this story unless a migration task is explicitly added.

### Implementation Boundaries

- In scope:
  - First runnable end-to-end baseline path.
  - Lifecycle controls and reproducibility metadata plumbing.
  - Initial tests proving workflow integrity.
- Out of scope:
  - Full accuracy-complete physics implementation (Story 1.2).
  - Full telemetry panel and validation strip depth (Epic 2+).
  - Mission thrust/non-geodesic behavior (Epic 4).

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` (Story 1.1, Epic 1)]
- [Source: `_bmad-output/planning-artifacts/architecture.md` (Core Architectural Decisions, Implementation Patterns, Project Structure & Boundaries)]
- [Source: `_bmad-output/planning-artifacts/ux-design-specification.md` (Core User Experience, Component Strategy, UX Consistency Patterns, Responsive Design & Accessibility)]
- [Source: `_bmad-output/planning-artifacts/prd.md` (FR1-FR4, FR11-FR15, NFR4-NFR7)]

## Dev Agent Record

### Agent Model Used

Codex 5.3

### Debug Log References

- 2026-04-13 create-story workflow execution
- 2026-04-13 DS implementation scaffolded backend and UI baseline
- `pytest` (backend): 3 passed
- `npm test` (ui): 1 passed
- 2026-04-13 CR batch patches applied for 7 review findings

### Completion Notes List

- Implemented FastAPI baseline app with `health` and `runs` routers plus canonical envelope contract models.
- Implemented baseline simulation engine wiring with deterministic seed and run provenance metadata.
- Implemented UI workspace with persistent `Run/Pause/Reset` controls and live metadata panel.
- Added backend integration and regression tests for lifecycle + deterministic metadata consistency.
- Added frontend workspace interaction test covering run, pause, and reset state transitions.

### File List

- `_bmad-output/implementation-artifacts/1-1-initialize-core-simulation-workspace-and-run-pipeline.md`
- `backend/pyproject.toml`
- `backend/app/__init__.py`
- `backend/app/main.py`
- `backend/app/api/__init__.py`
- `backend/app/api/routers/__init__.py`
- `backend/app/api/routers/health.py`
- `backend/app/api/routers/runs.py`
- `backend/app/contracts/__init__.py`
- `backend/app/contracts/envelope.py`
- `backend/app/contracts/runs.py`
- `backend/app/domain/__init__.py`
- `backend/app/domain/physics/__init__.py`
- `backend/app/domain/physics/metric.py`
- `backend/app/domain/physics/christoffel.py`
- `backend/app/domain/simulation/__init__.py`
- `backend/app/domain/simulation/engine.py`
- `backend/tests/integration/test_runs_api.py`
- `backend/tests/regression/test_deterministic_seed.py`
- `ui/package.json`
- `ui/tsconfig.json`
- `ui/vite.config.ts`
- `ui/index.html`
- `ui/src/main.tsx`
- `ui/src/features/controls/SimulationControls.tsx`
- `ui/src/features/workspace/Workspace.tsx`
- `ui/src/services/runService.ts`
- `ui/tests/workspace.test.tsx`

## Change Log

- 2026-04-13: Implemented Story 1.1 baseline backend/UI run pipeline, lifecycle controls, provenance metadata, and tests; moved story to `review`.
- 2026-04-13: Applied 7 code-review patch fixes; aligned error envelopes, UI failure handling, provenance fields, controls extraction, and test coverage; moved story to `done`.
