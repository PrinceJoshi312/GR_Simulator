# Story 4.3: Real-Time Mission Time-Drift Monitoring

Status: ready-for-dev

## Story

As a mission planner,
I want proper-vs-coordinate time drift visible during active missions,
So that I can make time-aware planning decisions.

## Acceptance Criteria

1. **Telemetry Extension (AC: 1):** Extend telemetry stream to include `proper_time_drift` (delta between coordinate and proper time) for rocket objects.
2. **Real-time Indicator (AC: 2):** Implement a UI indicator in the telemetry panel showing live relativistic time-drift.
3. **Data Logging (AC: 3):** Ensure time-drift is included in mission telemetry exports.
Status: done

## Tasks / Subtasks

- [x] **Backend: Telemetry Enhancement (AC: 1, 3)**
  - [x] Update `backend/app/domain/simulation/engine.py` to calculate and include `proper_time_drift` in telemetry updates.
- [x] **UI: Relativistic Clock Comparator (AC: 2)**
  - [x] Update `ui/src/features/telemetry/TelemetryPanel.tsx` to display the drift indicator.
- [x] **Validation: Drift Verification (AC: 1)**
  - [x] Add unit test in `backend/tests/unit/test_telemetry_channels.py` to verify drift calculation accuracy for a powered trajectory.

## Dev Notes

- **Drift Logic:** $\Delta t = t_{coord} - \tau$. This should be monitored for all objects, but highlighted for mission-critical rocket trajectories.

### References

- [Source: _bmad-output/planning-artifacts/prd.md#FR10]
- [Source: _bmad-output/planning-artifacts/architecture.md#Advanced Propulsion]

## Dev Agent Record

### Agent Model Used
Gemini 2.0 Flash
