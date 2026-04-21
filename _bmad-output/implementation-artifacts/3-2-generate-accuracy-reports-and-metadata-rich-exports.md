# Story 3.2: Generate Accuracy Reports and Metadata-Rich Exports

Status: done

## Story

As a researcher,
I want structured reports and exportable telemetry,
so that I can conduct external analysis and peer review.

## Acceptance Criteria

1. **Accuracy Report Generation (AC: 1):** The system generates a structured report (JSON/HTML) summarizing the results of the validation suite, including explicit deviation metrics for each benchmark (e.g., Mercury precession) and a summary of pass/fail counts.
2. **CSV Telemetry Export (AC: 2):** Users can export the `telemetry_history` for any object as a CSV file. Columns must include `t, x, y, vx, vy, r, proper_time, coordinate_time`.
3. **NumPy Telemetry Export (AC: 3):** Users can export the `telemetry_history` as a compressed NumPy (`.npz`) file containing the structured data and a metadata dictionary.
4. **Metadata Provenance (AC: 4):** Every export includes a metadata header specifying:
    - Gravitational constant (G)
    - Central mass (M)
    - Schwarzschild radius (Rs)
    - Speed of light (c)
    - Simulation seed and engine version
    - Provenance info (Run ID, timestamp)
5. **Export API Endpoints (AC: 5):**
    - `GET /reports/{run_id}/accuracy`: Returns the latest accuracy report.
    - `GET /reports/{run_id}/exports/csv?object_name=X`: Downloads CSV export.
    - `GET /reports/{run_id}/exports/numpy?object_name=X`: Downloads NumPy export.

## Tasks / Subtasks

- [x] **Backend: Telemetry Recording Fix (AC: 2, 3)**
  - [x] Update `SimulationEngine.step_run` in `backend/app/domain/simulation/engine.py` to record `vx, vy, proper_time, coordinate_time` in the `telemetry_history` deque.
- [x] **Backend: Export Domain Logic (AC: 2, 3, 4)**
  - [x] Implement `backend/app/domain/validation/exports.py` for CSV and NumPy generation.
  - [x] **CSV Format:** Use `# key: value` for metadata lines, followed by the header row. Use `float64` precision.
  - [x] **NumPy Format:** Use `np.savez_compressed` with keys `telemetry` (data array) and `metadata` (provenance dict).
- [x] **Backend: Report Domain Logic (AC: 1)**
  - [x] Implement `backend/app/domain/validation/reports.py` to aggregate `ValidationResult` objects into a serializable JSON report with a summary header.
- [x] **Backend: API Implementation (AC: 5)**
  - [x] Create `backend/app/api/routers/reports.py` and register it in `app/main.py`.
  - [x] Implement file response streaming using FastAPI `StreamingResponse` for CSV and NumPy downloads to handle large histories efficiently.
- [x] **Testing: Export and Report Integrity**
  - [x] Create `backend/tests/integration/test_exports.py` to verify file contents, metadata headers (G, M, Rs, c), and data precision.
  - [x] Create `backend/tests/unit/test_reports.py` to verify report aggregation and summary logic.

## Dev Notes

- **Metadata Extraction:** Ensure `c` and `Rs` are correctly extracted from the `metric` calculation logic in the domain layer to ensure consistency.
- **CSV Header Pattern:**
  ```csv
  # run_id: uuid-string
  # G: 6.67430e-11
  # M: 1.98847e30
  # Rs: 2953.36
  # c: 299792458.0
  # seed: 12345
  # timestamp: 2026-04-20T...
  t,x,y,vx,vy,r,proper_time,coordinate_time
  ...
  ```
- **NumPy Keys:** The `.npz` file MUST use keys `telemetry` and `metadata`. Use `np.fromiter` for efficient array creation from the history deque.
- **Memory Efficiency:** Telemetry history is capped at 50,000 steps (~4MB per object). Use generators to stream the CSV response line-by-line.
- **Precision:** Maintain `float64` precision (minimum) for all exported values.

### Project Structure Notes

- **Exports/Reports:** Logic belongs in `app/domain/validation` as part of the scientific observability pipeline.
- **API:** Use a dedicated `app/api/routers/reports.py` to keep `runs.py` focused on simulation lifecycle.

### References

- [Source: _bmad-output/planning-artifacts/prd.md#Functional Requirements (FR20, FR22)]
- [Source: _bmad-output/planning-artifacts/prd.md#Non-Functional Requirements (NFR10)]
- [Source: _bmad-output/planning-artifacts/architecture.md#Export & Scientific Observability]

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References
- Initial telemetry test failed due to missing channels (vx, vy, etc.)
- Fixed Schwarzschild radius error in tests by using realistic G/M.
- Fixed NameError in reports.py due to misplaced imports.

### Completion Notes List
- Implemented full telemetry recording (8 channels).
- Created domain logic for CSV/NumPy exports with standardized metadata.
- Created reports router with streaming support for large exports.
- Verified all features with unit and integration tests (23 total tests passing).

### Review Findings

- [x] [Review][Patch] Encapsulation Violation: API directly accesses private engine state [backend/app/api/routers/reports.py:25]
- [x] [Review][Patch] Memory Efficiency: Telemetry deques copied to lists/tuples [backend/app/domain/validation/exports.py:33, 46]
- [x] [Review][Patch] Potential Concurrency Issue: Unprotected iteration over telemetry deque [backend/app/api/routers/reports.py:54, 73]
