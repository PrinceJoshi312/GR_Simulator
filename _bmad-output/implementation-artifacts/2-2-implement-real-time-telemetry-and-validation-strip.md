# Story 2.2: Implement Real-Time Telemetry and Validation Strip

Status: done

## Story

As a researcher,
I want live telemetry and validation context,
so that I can interpret outputs confidently while a run is active.

## Acceptance Criteria

1. **Real-Time Telemetry Stream:** The system provides a real-time data stream (SSE or WebSocket) from the backend simulation engine to the UI. (AC: 1)
2. **Telemetry Insight Panel:** A dedicated UI panel displays position, velocity, proper time, and coordinate time for the selected object in real-time. (AC: 2)
3. **Validation Strip:** A persistent trust layer displays run health, benchmark context, and solver confidence signals (e.g., tolerance health). (AC: 3)
4. **State Consistency:** Simulation state transitions (`idle`, `loading`, `running`, `warning`, `error`) are visually reflected in the UI and consistent with architecture rules. (AC: 4)
5. **Numerical Stability Cues:** The UI provides visual indicators if numerical drift or extreme mass ratios approach precision limits. (AC: 5)

## Tasks / Subtasks

- [x] **Backend: Implement Telemetry Streaming (AC: 1)**
  - [x] Add `/runs/{run_id}/telemetry` SSE endpoint in `backend/app/api/routers/runs.py`.
  - [x] Implement a background task/loop in `SimulationEngine` to call `step_run` at a fixed frequency (e.g., 60Hz) when a run is active.
  - [x] Integrate a broadcast mechanism (e.g., `asyncio.Queue` or a simple observer pattern) to push telemetry to the SSE endpoint.
- [x] **Backend: Domain Validation Logic (AC: 3, 5)**
  - [x] Create `backend/app/domain/validation` directory.
  - [x] Implement basic validation checks (e.g., checking `isfinite` for all states, monitoring radius for black hole "plunge").
  - [x] Add validation metadata to the telemetry stream (e.g., `is_stable`, `error_estimate`).
- [x] **Frontend: Telemetry Insight Panel (AC: 2)**
  - [x] Create `ui/src/features/telemetry/TelemetryPanel.tsx`.
  - [x] Connect the panel to `useTelemetryStore` to display live data for the selected object.
  - [x] Ensure formatting follows scientific standards (e.g., scientific notation for large/small numbers).
- [x] **Frontend: Validation Strip (AC: 3, 4, 5)**
  - [x] Create `ui/src/features/workspace/ValidationStrip.tsx`.
  - [x] Display simulation state, run health, and stability indicators.
  - [x] Use icon + text + color triplets as per UX spec (not color-dependent only).
- [x] **Frontend: Connect Real Telemetry (AC: 1)**
  - [x] Update `ui/src/services/telemetryService.ts` to replace mock logic with a real SSE connection to the backend.
  - [x] Ensure the connection handles re-connects and cleanup on unmount.

## Dev Notes

- **SSE vs WebSockets:** Used Server-Sent Events (SSE) for telemetry streaming via `sse-starlette` in FastAPI.
- **Background Loop:** Implemented a `lifespan` manager in `main.py` that runs a 60Hz simulation loop, stepping all active runs and broadcasting their state.
- **Validation:** Added a `validation` domain in the backend to calculate stability signals (finite checks, Schwarzschild radius proximity) in real-time.
- **Scaling:** Applied a `SCALE_FACTOR` of `1e-9` in the frontend telemetry service to map SI units (meters) to Three.js visual units safely.

### Project Structure Notes

- **Backend:** 
  - `app/main.py`: Lifespan and background loop.
  - `app/domain/simulation/engine.py`: `asyncio.Queue` based broadcast and subscription logic.
  - `app/domain/validation/checker.py`: New validation domain.
- **Frontend:**
  - `ui/src/features/telemetry/TelemetryPanel.tsx`: New component.
  - `ui/src/features/workspace/ValidationStrip.tsx`: New component.
  - `ui/src/services/telemetryService.ts`: Switched to real EventSource implementation.

### References

- [Source: _bmad-output/planning-artifacts/prd.md#Functional Requirements (FR19, FR21)]
- [Source: _bmad-output/planning-artifacts/architecture.md#API & Communication Patterns]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Component Strategy]
- [Source: _bmad-output/planning-artifacts/epics.md#Story 2.2]

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

- 2026-04-14: Implemented SSE telemetry backend.
- 2026-04-14: Added background simulation loop in FastAPI lifespan.
- 2026-04-14: Created validation domain and integrated with telemetry broadcast.
- 2026-04-14: Built TelemetryPanel and ValidationStrip UI components.
- 2026-04-14: Replaced mock telemetry with real SSE stream in UI.
- 2026-04-14: Fixed regression in existing runs API tests by updating TestClient usage.

### Completion Notes List

- Real-time telemetry streaming from Schwarzschild engine to UI is fully functional.
- Live validation signals (stability, event horizon proximity) are calculated and displayed.
- Dark-themed scientific UI panels implemented for telemetry and status tracking.
- All integration tests pass.

### File List

- `backend/app/main.py`
- `backend/app/domain/simulation/engine.py`
- `backend/app/domain/validation/checker.py`
- `backend/app/api/routers/runs.py`
- `backend/pyproject.toml`
- `backend/tests/integration/test_runs_api.py`
- `backend/tests/integration/test_telemetry_api.py`
- `ui/src/features/telemetry/TelemetryPanel.tsx`
- `ui/src/features/workspace/ValidationStrip.tsx`
- `ui/src/features/workspace/Workspace.tsx`
- `ui/src/services/telemetryService.ts`
- `ui/src/services/telemetryStore.ts`
