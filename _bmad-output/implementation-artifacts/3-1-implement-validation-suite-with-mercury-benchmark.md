# Story 3.1: Implement Validation Suite with Mercury Benchmark

Status: done

## Story

As a researcher,
I want automated comparison against analytical Schwarzschild expectations,
so that I can verify simulation correctness.

## Acceptance Criteria

1. **Analytical Benchmarking (AC: 1):** The system implements the Schwarzschild perihelion precession formula: $\Delta \phi = \frac{6 \pi G M}{c^2 a (1-e^2)}$ to calculate reference values.
2. **Mercury Precession Test (AC: 2):** A specialized benchmark identifies perihelion points in simulation telemetry, calculates the actual precession angle, and compares it to the analytical reference.
3. **Pass/Fail Thresholds (AC: 3):** Validation results include a boolean `is_passed` status based on a configurable deviation threshold (default 5%).
4. **Validation Endpoint (AC: 4):** A POST `/runs/{run_id}/validate` endpoint triggers the suite and returns structured results including actual vs. expected values and relative deviation.
5. **Historical Telemetry (AC: 5):** The simulation engine preserves enough historical state (radial distances and angles) to detect at least two full orbits for precession calculation.

## Tasks / Subtasks

- [x] **Backend: Validation Domain Logic (AC: 1, 2, 3)**
  - [x] Implement `backend/app/domain/validation/benchmarks.py` with `calculate_theoretical_precession` and `run_mercury_precession_benchmark`.
  - [x] Implement `validate_orbit_circularity` as a secondary stability check.
- [x] **Backend: Simulation Engine Integration (AC: 2, 5)**
  - [x] Update `SimulationRun` to include `telemetry_history` (limiting to ~50,000 steps to prevent memory leaks).
  - [x] Update `step_run` to record object `x, y, r, t` in the history.
  - [x] Implement `run_validation_suite(run_id)` in `SimulationEngine` to perform the perihelion detection and precession averaging.
- [x] **Backend: API Extension (AC: 4)**
  - [x] Add `POST /runs/{run_id}/validate` to `backend/app/api/routers/runs.py`.
- [x] **Testing: Accuracy Verification**
  - [x] Create `backend/tests/unit/test_benchmarks.py` to verify the analytical formula.
  - [x] Create `backend/tests/integration/test_validation_api.py` to verify the full validation flow.

### Review Findings

- [x] [Review][Patch] Potential Division by Zero in Orbital Estimates [backend/app/domain/simulation/engine.py:315]
- [x] [Review][Patch] Numerical Instability in Perihelion Detection [backend/app/domain/simulation/engine.py:303]
- [x] [Review][Patch] Potential Race Condition on Telemetry History [backend/app/domain/simulation/engine.py:293]
- [x] [Review][Patch] Memory Consumption Risks (50k steps cap) [backend/app/domain/simulation/engine.py:228]
- [x] [Review][Defer] 2D Projection Assumption [backend/app/domain/simulation/engine.py:307] — deferred, pre-existing (equatorial geodesic limitation)

## Dev Notes

- **Perihelion Detection:** Identify perihelia by finding local minima in the radial history ($r_{i} < r_{i-1}$ and $r_{i} < r_{i+1}$).
- **Precession Calculation:** Calculate the angular difference $\Delta \phi$ between successive perihelia. Note that Mercury's precession is very small (~43 arcsec/century), so for shorter simulations, we compare the "instantaneous" per-revolution precession.
- **Precision:** Ensure `float64` is used throughout the validation chain to avoid adding non-physical numerical noise to the deviation report.
- **Memory Management:** Clear `telemetry_history` on simulation reset.

### Project Structure Notes

- **Validation Logic:** Stays in `app/domain/validation`.
- **Engine Logic:** Integration happens in `app/domain/simulation/engine.py`.
- **Contracts:** Validation results should follow the standard success envelope.

### References

- [Source: _bmad-output/planning-artifacts/prd.md#Functional Requirements (FR5, FR21)]
- [Source: _bmad-output/planning-artifacts/architecture.md#Validation & Scientific Observability]
- [Source: _bmad-output/planning-artifacts/epics.md#Story 3.1]

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

- Verified formula: Schwarzschild precession $\Delta \phi$ is the correct analytical benchmark for this phase.
- Designed `telemetry_history` structure to support orbital analysis without unbounded memory growth.
- Identified perihelion detection as the robust method for "actual" precession measurement.

### Completion Notes List

- Story context created - technical strategy for Mercury benchmark established.
- Implemented Schwarzschild perihelion precession analytical formula.
- Added telemetry history recording to SimulationEngine with 50,000 step limit.
- Implemented perihelion detection and precession calculation in run_validation_suite.
- Added POST /runs/{run_id}/validate endpoint.
- Verified implementation with unit and integration tests.
- Fixed Pydantic serialization issues for numpy types by converting to standard Python types.

### File List

- backend/app/domain/validation/benchmarks.py
- backend/app/domain/simulation/engine.py
- backend/app/api/routers/runs.py
- backend/tests/unit/test_benchmarks.py
- backend/tests/integration/test_validation_api.py
