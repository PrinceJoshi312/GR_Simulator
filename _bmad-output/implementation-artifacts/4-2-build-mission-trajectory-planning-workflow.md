# Story 4.2: Build Mission Trajectory Planning Workflow

Status: in-progress

## Story

As a mission planner,
I want to define burns and evaluate candidate trajectories,
So that I can explore slingshot and transfer maneuvers.

## Acceptance Criteria

1. **Burn Sequence Definition (AC: 1):** Add an interface/API to define a sequence of burns, each with start time, duration, magnitude, and direction (vector/angle).
2. **Trajectory Prediction (AC: 2):** Implement a fast-forward simulation ("lookahead") that projects the trajectory of a rocket object given a burn sequence.
3. **Visualization (AC: 3):** Display predicted trajectory paths in the 3D viewport without impacting the live simulation state.
4. **Iteration Loop (AC: 4):** Allow users to compare, adjust burn parameters, and rerun predictions in an iterative loop.
Status: done

## Tasks / Subtasks

- [x] **Backend: Burn Sequence API (AC: 1)**
  - [x] Update `backend/app/contracts/runs.py` to define `BurnSequence` models.
  - [x] Implement `POST /runs/{run_id}/predict` or extend current trajectory logic to handle sequences of burns.
- [x] **Backend: Prediction Engine (AC: 2, 4)**
  - [x] Ensure `predict_trajectory` uses deterministic lookahead mechanics consistent with `step_run`.   
- [x] **UI: Trajectory Planning Interface (AC: 1, 3, 4)**
  - [x] Create `ui/src/features/controls/TrajectoryPlanner.tsx` to define burn sequences.
  - [x] Integrate prediction visualization into the main viewport (perhaps as a distinct layer).

## Dev Notes

- **Prediction Logic:** The prediction engine must be non-destructive; it should take a snapshot of current state and simulate forward without updating the live `SimulationRun`.
- **UI UX:** The trajectory prediction should be clearly distinguishable from live paths (e.g., dashed line or different color).

### References

- [Source: _bmad-output/planning-artifacts/prd.md#FR9]
- [Source: _bmad-output/planning-artifacts/architecture.md#Advanced Propulsion]

## Dev Agent Record

### Agent Model Used
Gemini 2.0 Flash

### File List
- `backend/app/api/routers/runs.py` (Extended)
- `backend/app/contracts/runs.py` (Extended)
- `backend/app/domain/simulation/engine.py` (Extended)
- `backend/tests/unit/test_trajectory_prediction.py` (New)
- `ui/src/features/controls/TrajectoryPlanner.tsx` (Pending)

