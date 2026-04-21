# Story 3.3: Save/Load State with Deterministic Replay

Status: done

## Story

As a researcher,
I want to save and load simulation states,
so that I can pause my work and reproduce results with perfect fidelity.

## Acceptance Criteria

1. **State Serialization (AC: 1):** The system implements a robust serialization format for `SimulationRun` that captures:
    - Metadata: scenario_id, seed, G, central_mass, engine_version, app_version.
    - Current state: state, timestep.
    - Object state: Full `ObjectState` (x, y, vx, vy, proper_time, coordinate_time) for all objects.
2. **Save Endpoint (AC: 2):** Implement `POST /runs/{run_id}/save` which returns a JSON payload (or file download) containing the full state. Extension: `.grsim`.
3. **Load Endpoint (AC: 3):** Implement `POST /runs/load` which accepts a `.grsim` payload and initializes a new `SimulationRun`. The new run should have a fresh `run_id` but identical physics parameters.
4. **Deterministic Replay (AC: 4):** Verified through tests: loading a state and stepping for $N$ steps must result in the exact same coordinates as stepping the original simulation for the same total duration.
5. **Version Validation (AC: 5):** The loading process checks for `engine_version` compatibility and refuses to load states from incompatible future versions or corrupted schemas.

## Tasks / Subtasks

- [ ] **Backend: Serialization Domain Logic (AC: 1, 5)**
  - [ ] Implement `to_dict()` and `from_dict()` methods for `SimulationRun` and its sub-components in `backend/app/domain/simulation/engine.py`.
  - [ ] Add version compatibility check logic.
- [ ] **Backend: API Extension (AC: 2, 3)**
  - [ ] Add `POST /runs/{run_id}/save` to `backend/app/api/routers/runs.py`.
  - [ ] Add `POST /runs/load` to `backend/app/api/routers/runs.py`.
- [ ] **Testing: Determinism Verification (AC: 4)**
  - [ ] Create `backend/tests/regression/test_save_load_determinism.py`.
  - [ ] Test sequence: Start run -> step 100 -> save -> load -> step 100 on both -> compare object states.

## Dev Notes

- **NumPy types:** Remember that `np.float64` is not JSON-serializable by default. Use `float()` conversion during serialization and `np.float64()` during deserialization.
- **Fresh Run ID:** When loading, generate a new `run_id` to avoid collisions with active runs, but keep all other physics-impacting values.
- **Schema Versioning:** The `engine_version` in the JSON should be checked against `SimulationEngine.version`.

### Project Structure Notes

- **API:** Keep these in `runs.py` as they are primary run lifecycle operations.

### References

- [Source: _bmad-output/planning-artifacts/prd.md#Functional Requirements (FR21)]
- [Source: _bmad-output/planning-artifacts/architecture.md#State & Determinism]

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

### Completion Notes List

### File List
