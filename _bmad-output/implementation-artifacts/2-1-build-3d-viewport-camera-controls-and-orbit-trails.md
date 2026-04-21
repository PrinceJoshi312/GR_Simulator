# Story 2.1: Build 3D Viewport, Camera Controls, and Orbit Trails

Status: done

## Story

As an educator,  
I want interactive 3D views and orbit trails,  
so that I can visually explain relativistic effects.

## Acceptance Criteria

1. Given a running simulation, when I view the workspace, then object trajectories render in 3D with persistent trail support.
2. Given a running simulation, then camera controls (pan/zoom/rotate/follow) are available and smooth.
3. Given rendering requirements, then performance remains stable (60 FPS) under expected MVP object counts (up to 10 massive bodies).

## Tasks / Subtasks

- [x] Initialize Three.js/React Three Fiber (R3F) environment (AC: 1, 3)
  - [x] Install `@react-three/fiber`, `@react-three/drei`, and `three`.
  - [x] Configure `WebGPURenderer` (r183+) with WebGL fallback.
- [x] Implement 3D Viewport and Camera Controls (AC: 2)
  - [x] Implement `OrbitControls` for pan/zoom/rotate.
  - [x] Implement "Follow Object" camera mode for active focus.
- [x] Implement Relativistic Orbit Trails (AC: 1)
  - [x] Create persistent history buffer for object positions.
  - [x] Render historical paths as smooth 3D trails (Line or CatmullRomCurve3).
- [x] Connect Real-Time Telemetry to Visualization (AC: 1, 3)
  - [x] Bridge backend telemetry stream to R3F state.
  - [x] Optimize updates using Refs to avoid React re-renders in the render loop.

### Review Follow-ups (AI)
- [x] [AI-Review] [High] Implement explicit WebGPU feature check and automatic fallback to WebGLRenderer.
- [x] [AI-Review] [Med] Scale camera follow offset based on object size to prevent clipping.
- [x] [AI-Review] [Med] Optimize OrbitTrail distance threshold to reduce redundant point updates.

## Dev Notes
...
[rest of the file]
...
## Senior Developer Review (AI)

**Outcome:** Approved (2026-04-14)
**Status:** Done

### Action Items
- [x] [High] WebGPU fallback logic in Viewport.tsx.
- [x] [x] [Med] Dynamic camera offset for Follow Mode.
- [x] [Med] OrbitTrail distance threshold tuning.

### Technical Stack & Patterns
- **Three.js r183+** with **WebGPURenderer** is mandatory for 2026 performance standards.
- **React Three Fiber (R3F) v9+** for declarative 3D state.
- **@react-three/drei** for `OrbitControls` and helper primitives.
- **Zustand** is recommended for bridging the telemetry stream to the 3D loop without React jank.
- **Performance:** Never call `setState` inside `useFrame`. Mutate refs directly for positions and trails.

### Source Tree Components
- `ui/src/features/workspace/Viewport.tsx`: New component for the 3D Canvas.
- `ui/src/features/workspace/CelestialBody.tsx`: Component representing a planet/rocket.
- `ui/src/features/workspace/OrbitTrail.tsx`: Component for historical path rendering.
- `ui/src/services/telemetry.ts`: Ensure stream provides sufficient frequency for smooth 60fps interpolation.

### Testing Standards
- **Vitest** for unit tests of coordinate transformations.
- **Playwright** (if available) for E2E check of canvas mounting.
- **Performance Budget:** Baseline 60 FPS check on standard CPU/GPU.

## Project Structure Notes

- Follow the architecture decision: UI communicates via typed REST/Stream endpoints.
- Keep UI features in `ui/src/features`.
- Ensure SI units (meters) are mapped to meaningful 3D units (e.g., 1 AU = 100 units) to avoid precision artifacts in Three.js (Z-fighting).

## References

- [Source: _bmad-output/planning-artifacts/prd.md#Functional Requirements]
- [Source: _bmad-output/planning-artifacts/architecture.md#Frontend Architecture]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Visual Design Foundation]
- [Source: Latest 2026 Three.js/R3F Best Practices]

## Dev Agent Record

### Agent Model Used
Gemini 2.0 Flash

### Debug Log References
- 2026-04-14: Initialized 3D environment with Three.js r183 and R3F v9.
- 2026-04-14: Implemented WebGPURenderer with WebGL fallback in Viewport.
- 2026-04-14: Implemented OrbitControls and Follow Object camera logic.
- 2026-04-14: Implemented OrbitTrail with persistent history buffer and setPoints optimization.
- 2026-04-14: Connected Zustand telemetry store to R3F render loop using Refs.
- 2026-04-14: Addressed code review findings (WebGPU fallback, dynamic camera offset, trail threshold).

### Completion Notes List
- Successfully built the 3D viewport using WebGPURenderer for maximum 2026 performance.
- Implemented smooth camera follow logic that tracks relativistic objects via telemetry.
- Created persistent orbit trails that update efficiently without React re-renders.
- Verified workspace state updates with mocked Viewport in Vitest.
- Hardened renderer with explicit WebGPU feature check and safe WebGL fallback.

### File List
- `ui/src/features/workspace/Viewport.tsx`
- `ui/src/features/workspace/CelestialBody.tsx`
- `ui/src/features/workspace/OrbitTrail.tsx`
- `ui/src/services/telemetryStore.ts`
- `ui/src/services/telemetryService.ts`
- `ui/src/features/workspace/Workspace.tsx` (updated)
- `ui/tests/workspace.test.tsx` (updated)

## Change Log
- 2026-04-14: Story 2.1 implementation complete.
- 2026-04-14: Addressed code review findings - 3 items resolved.
