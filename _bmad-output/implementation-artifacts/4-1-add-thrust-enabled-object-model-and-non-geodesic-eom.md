# Story 4.1: Add Thrust-Enabled Object Model and Non-Geodesic EOM

Status: review

## Story

As a mission planner,
I want thrust vectors applied to selected objects,
so that I can simulate powered trajectories in curved spacetime.

## Acceptance Criteria

1. **Thrust-Enabled Object Model (AC: 1):** Extend `SimulationObject` or create a `RocketObject` that includes optional thrust parameters: `thrust_magnitude` (Newtons), `thrust_vector` (unit vector in xy plane), and `is_active` (boolean).
2. **Non-Geodesic Equations of Motion (AC: 2):** Update the integration kernel in `SimulationEngine.step_run` to incorporate the 4-acceleration contribution from external thrust ($a^\mu_{thrust} = F^\mu / m$) into the geodesic equation.
3. **Thrust Isolation (AC: 3):** Ensure thrust terms only apply to objects explicitly marked as rockets; celestial bodies remain on standard geodesics.
4. **Safety Guards (AC: 4):** Implement checks to prevent infinite or extreme thrust values from causing integration divergence or division-by-zero.
5. **Real-time Control API (AC: 5):** Implement `POST /runs/{run_id}/objects/{name}/thrust` to toggle engine status and update thrust direction at runtime.

## Tasks / Subtasks

- [x] **Backend: Domain Model Extension (AC: 1, 3)**
  - [x] Update `SimulationObject` in `backend/app/domain/simulation/engine.py` to support `thrust` configuration.
  - [x] Add `mass_loss_rate` (optional) for future fuel consumption logic.
- [x] **Backend: Physics Engine Update (AC: 2, 4)**
  - [x] Modify `step_run` to calculate thrust-induced acceleration in the local frame and transform to coordinate frame.
  - [x] Implement safety clipping for thrust-to-mass ratios.
- [x] **Backend: API Implementation (AC: 5)**
  - [x] Add `POST /runs/{run_id}/objects/{name}/thrust` endpoint to `backend/app/api/routers/runs.py`.
- [x] **Testing: Non-Geodesic Verification**
  - [x] Create `backend/tests/unit/test_thrust_physics.py` to verify that a rocket with constant thrust deviates predictably from a geodesic.
  - [x] Verify that celestial bodies in the same run are unaffected by rocket thrust.

## Dev Notes

- **Physics Hint:** The non-geodesic EOM is $\frac{d^2 x^\mu}{d \tau^2} + \Gamma^\mu_{\alpha \beta} \frac{dx^\alpha}{d \tau} \frac{dx^\beta}{d \tau} = f^\mu / m$, where $f^\mu$ is the external 4-force. For low-velocity rockets in the Schwarzschild weak field, this simplifies to adding the thrust vector divided by mass to the coordinate acceleration, but for full relativity, ensure the vector is correctly applied relative to the proper time.
- **API Payload:**
  ```json
  {
    "is_active": true,
    "magnitude": 1000.0,
    "angle_rad": 0.785
  }
  ```

### Project Structure Notes

- **Physics logic:** Keep the thrust transformation logic in `app/domain/physics` if it requires metric tensor operations.

### References

- [Source: _bmad-output/planning-artifacts/prd.md#Functional Requirements (FR7, FR8)]
- [Source: _bmad-output/planning-artifacts/architecture.md#Advanced Propulsion]

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References
- Fixed index error in `test_mass_loss_during_burn` by searching for object by name instead of index.

### Completion Notes List
- Implemented `ThrustConfig` dataclass and integrated into `SimulationObject`.
- Updated `step_run` to include non-geodesic acceleration terms.
- Added safety clipping at 100g to prevent numerical instability with extreme thrust/low mass ratios.
- Implemented mass loss logic for active engines.
- Added runtime control API endpoint for thrust management.
- Verified with unit tests covering deviation, safety, and fuel consumption.

### File List
- `backend/app/domain/simulation/engine.py` (Modified)
- `backend/app/api/routers/runs.py` (Modified)
- `backend/tests/unit/test_thrust_physics.py` (New)
