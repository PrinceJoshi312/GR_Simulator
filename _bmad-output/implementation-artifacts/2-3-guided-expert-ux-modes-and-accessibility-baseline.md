# Story 2.3: Guided/Expert UX Modes and Accessibility Baseline

Status: done

## Story

As a mixed-skill user,
I want guided and expert experiences with consistent controls,
so that I can use the tool effectively regardless of depth.

## Acceptance Criteria

1. **Workspace Mode Context (AC: 1):** The system supports a "Workspace Mode" (Guided vs Expert) that preserves the same spatial layout but adjusts information density and control depth.
2. **Guided Mode Enhancements (AC: 2):** Guided mode provides interactive tooltips and overlays explaining the physics of Schwarzschild orbits and how to use the basic controls (Run/Pause/Reset).
3. **Expert Mode Controls (AC: 3):** Expert mode exposes advanced parameter controls (Timestep, G, Central Mass) directly in the `SimulationControls` panel for high-frequency iteration.
4. **Accessibility Compliance (AC: 4):** All interactive elements have visible focus states and are keyboard-operable (WCAG 2.2 AA). Status indicators (Validation Strip, Telemetry) do not rely solely on color to communicate state.
5. **UX Pattern Consistency (AC: 5):** Standardize button hierarchy (Primary/Secondary), form validation (unit-aware constraints), and loading/error states across all workspace components.

## Tasks / Subtasks

- [x] **Frontend: Workspace Mode Architecture (AC: 1)**
  - [x] Implement a `useWorkspaceStore` or similar to manage the `mode` state (Guided/Expert).
  - [x] Add a mode-switching toggle in the `Workspace` header.
- [x] **Frontend: Guided Mode Overlays (AC: 2)**
  - [x] Implement instructional tooltips for the primary simulation lifecycle controls.
  - [x] Add a "Physics Context" overlay that explains the active metric (Schwarzschild) when in Guided mode.
- [x] **Frontend: Expert Mode Controls (AC: 3)**
  - [x] Update `SimulationControls.tsx` to include numeric inputs for `G`, `central_mass`, and `timestep` when in Expert mode.
  - [x] Ensure the controls are wired to the backend `update_runtime_params` endpoint via a new service or update to `runService.ts`.
- [x] **Frontend: Accessibility & UX Audit (AC: 4, 5)**
  - [x] Standardize the 8px spacing system and design tokens across all workspace components.
  - [x] Verify that all buttons and inputs are keyboard-operable with clear focus indicators.
  - [x] Ensure the `ValidationStrip` and `TelemetryPanel` use explicit text labels and iconography for state changes.
  - [x] Implement consistent loading and error patterns for all async simulation actions.

## Dev Notes

- **Layout Stability:** Transition between Guided and Expert modes is handled via Zustand state and does not cause layout shifts in the 3D viewport.
- **Theme System:** Introduced `ui/src/styles/theme.ts` to centralize colors, spacing, and typography tokens.
- **Accessibility:** Added ARIA roles, labels, and state attributes (`aria-pressed`, `aria-label`, `role="status"`). Improved color-only indicators with text and icon prefixes.

### Project Structure Notes

- **State Management:** `ui/src/services/workspaceStore.ts` handles UI mode.
- **Components:** 
  - `ui/src/features/controls/AdvancedControls.tsx`: Expert-only parameter tuning.
  - `ui/src/features/workspace/PhysicsOverlay.tsx`: Guided-only physics context.
- **Service:** Updated `ui/src/services/runService.ts` with `updateRuntimeParams`.

### References

- [Source: _bmad-output/planning-artifacts/prd.md#UX Design Requirements]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Component Strategy]
- [Source: _bmad-output/planning-artifacts/architecture.md#Frontend Architecture]
- [Source: _bmad-output/planning-artifacts/epics.md#Story 2.3]

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

- 2026-04-14: Created theme system and workspace store.
- 2026-04-14: Implemented dual-mode workspace header.
- 2026-04-14: Built AdvancedControls and wired to backend parameter endpoint.
- 2026-04-14: Added PhysicsOverlay for Guided mode context.
- 2026-04-14: Refactored ValidationStrip and TelemetryPanel for theme consistency and a11y.
- 2026-04-14: Verified all tests pass.

### Completion Notes List

- Workspace mode (Guided/Expert) is fully functional.
- Expert mode exposes real-time physics parameter tuning.
- Guided mode provides helpful overlays for education.
- UX consistency and accessibility foundations established.

### File List

- `ui/src/styles/theme.ts`
- `ui/src/services/workspaceStore.ts`
- `ui/src/services/runService.ts`
- `ui/src/features/controls/AdvancedControls.tsx`
- `ui/src/features/controls/SimulationControls.tsx`
- `ui/src/features/workspace/Workspace.tsx`
- `ui/src/features/workspace/PhysicsOverlay.tsx`
- `ui/src/features/workspace/ValidationStrip.tsx`
- `ui/src/features/telemetry/TelemetryPanel.tsx`
- `ui/tests/workspace.test.tsx`
