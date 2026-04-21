---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
inputDocuments:
  - "_bmad-output/planning-artifacts/prd.md"
  - "_bmad-output/planning-artifacts/ux-design-specification.md"
  - "_bmad-output/planning-artifacts/product-brief.md"
  - "_bmad-output/planning-artifacts/product-brief.distillate.md"
  - "docs/TECHNICAL_DETAILS.md"
workflowType: "architecture"
lastStep: 8
status: "complete"
completedAt: "2026-04-13"
project_name: "GRsimulator"
user_name: "Prince Joshi"
date: "2026-04-13"
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**  
The project requires a simulation architecture that supports relativistic physics computation (metric tensor, Christoffel symbols, geodesic integration), real-time object evolution, interactive simulation control, 3D visualization, telemetry, data export, validation tooling, and state persistence. Architecturally this implies clean boundaries between physics kernel, numerics orchestration, simulation state management, and presentation/runtime interaction layers.

**Non-Functional Requirements:**  
NFRs are architecture-driving: low-latency integration, high render throughput, strict numeric precision, deterministic replay, extreme mass-ratio stability, and transparent scientific logic. The architecture must enforce reproducibility and include explicit metadata propagation for persisted/exported artifacts.

**Scale & Complexity:**  
This is a high-complexity scientific application combining mathematically sensitive computation with interactive visualization. It requires modular layering and strict contracts to prevent coupling between correctness-critical physics paths and UI responsiveness.

- Primary domain: Scientific simulation + interactive visualization
- Complexity level: High
- Estimated architectural components: 10-14 core components/subsystems

### Technical Constraints & Dependencies

- Python 3.10+ ecosystem with heavy numeric dependencies (`numpy`, `scipy`) and rendering stack requirements
- Precision baseline at `float64`, with potential optional `float128` path for edge scenarios
- Deterministic execution expectations for reproducible results across runs
- Scenario/state persistence and export contracts must preserve simulation provenance
- Extensibility requirement for future metrics and richer mission dynamics without architectural rewrites

### Cross-Cutting Concerns Identified

- Determinism and reproducibility guarantees
- Performance budgeting across compute and render loops
- Validation and scientific observability at runtime
- Error handling and numerical stability safeguards
- Configuration/versioning for scenarios and saved states
- Accessibility and UI consistency for data-dense workflows

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- System split: Python simulation core + API boundary + React desktop-first UI shell
- Persistence baseline: PostgreSQL 18
- API style: REST-first with typed contracts
- Runtime determinism: reproducible simulation mode as first-class requirement
- Validation and telemetry pipelines as architecture-level components

**Important Decisions (Shape Architecture):**
- Cache/runtime acceleration: Redis 8.6
- Backend framework: FastAPI 0.135.x + Pydantic 2.13
- Frontend stack alignment: React 19 + Vite starter + Vitest 4.1 + Playwright 1.59
- Packaging strategy: desktop-first now, final shell choice deferred until post-MVP validation
- Container baseline: Docker Engine 29.x

**Deferred Decisions (Post-MVP):**
- Full multi-process desktop packaging hardening
- Distributed compute offload and GPU acceleration path
- Multi-user collaboration and remote simulation orchestration

### Data Architecture

- Primary database: PostgreSQL 18
- Data modeling: strict schema with provenance fields on runs, scenarios, exports, and validation artifacts
- Validation layer: Pydantic models at API boundaries with domain-layer scientific invariants
- Migration strategy: versioned migrations from day 1
- Caching strategy: Redis for hot telemetry buffers, scenario lookup acceleration, and transient job states

### Authentication & Security

- MVP auth posture: local/project-scoped minimal auth unless multi-user deployment path is activated
- Authorization model: role capability flags prepared early (research, instructor, operator)
- Security middleware: request validation, standardized error envelopes, input size/rate guards
- Data protection: integrity metadata on exports and run artifacts; optional signing for later collaboration modes

### API & Communication Patterns

- API pattern: REST-first contract between UI shell and Python simulation services
- Documentation: OpenAPI generation via FastAPI and typed client contract checks
- Error handling: canonical error envelope with code, message, context, and actionable hint
- Throughput controls: local throttling and backpressure for high-frequency telemetry endpoints
- Internal communication: explicit adapter boundaries between domain services and exposed APIs

### Frontend Architecture

- State model: separate concerns for simulation controls, telemetry stream, UI state, and workspace preferences
- Component architecture: design-system primitives plus domain-specific telemetry and validation components
- Routing: workspace-first model (scenario -> run -> analysis)
- Performance strategy: controlled render cadence, memoized selectors, viewport/render isolation
- Bundle strategy: feature-sliced lazy loading for non-critical analysis modules

### Infrastructure & Deployment

- Runtime baseline: Dockerized services with local desktop-first profile
- CI/CD gates: lint, typecheck, unit/integration/e2e, and deterministic simulation regression checks
- Environment profiles: dev, scientific-test, and release with deterministic defaults
- Observability: structured logs with run/session IDs and telemetry diagnostics for performance and drift
- Scaling posture: vertical-first MVP with future decomposition around simulation jobs and analytics

### Decision Impact Analysis

**Implementation Sequence:**
1. Stand up backend simulation/API skeleton (FastAPI + typed models)
2. Introduce canonical domain contracts (scenario, run, telemetry, validation report, export metadata)
3. Build UI workspace shell from Vite/React starter
4. Integrate telemetry streaming and validation strip
5. Add persistence/caching and deterministic replay enforcement
6. Add test gates for correctness and regression stability

**Cross-Component Dependencies:**
- Determinism requirements shape domain model, API contracts, persistence, and testing strategy
- Telemetry cadence shapes backend throughput design and frontend render architecture
- Validation/reporting requirements affect both compute pipelines and UX trust surfaces
- Export metadata contracts must remain consistent across simulation, storage, and UI layers

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

Critical conflict points identified: naming, structure, formats, communication, and process behavior across backend, simulation, and UI layers.

### Naming Patterns

**Database Naming Conventions:**
- Tables use `snake_case` plural (`simulation_runs`, `telemetry_samples`)
- Columns use `snake_case` (`created_at`, `scenario_id`)
- Foreign keys use `<entity>_id` (`run_id`, `object_id`)
- Indexes use `idx_<table>_<column>` (`idx_simulation_runs_created_at`)

**API Naming Conventions:**
- REST resources are plural (`/runs`, `/scenarios`, `/telemetry`)
- Path params use braces and snake_case (`/runs/{run_id}`)
- Query params use `snake_case`
- Wire-format field names are `snake_case`

**Code Naming Conventions:**
- Python: modules/functions/variables `snake_case`, classes `PascalCase`
- React/TypeScript: components `PascalCase`, hooks `camelCase`
- Python files: `snake_case.py`; React component files: `PascalCase.tsx`

### Structure Patterns

**Project Organization:**
- Backend modules by boundary: `core`, `physics`, `numerics`, `simulation`, `validation`, `api`, `infra`
- Frontend modules by feature: `workspace`, `controls`, `telemetry`, `validation`, `shared`
- Backend tests mirrored under `tests/`; frontend unit tests co-located; e2e in dedicated `e2e/`

**File Structure Patterns:**
- Shared contracts in explicit contracts package/folder
- No cross-layer imports that bypass boundaries
- Typed config loaders for environment handling

### Format Patterns

**API Response Formats:**
- Success: `{ "data": ..., "meta": { ... }, "error": null }`
- Error: `{ "data": null, "meta": { "request_id": ... }, "error": { "code": "...", "message": "...", "context": {...}, "hint": "..." } }`
- Timestamps in ISO-8601 UTC strings
- Precision-sensitive values include units/metadata

**Data Exchange Formats:**
- JSON keys: `snake_case`
- Booleans: `true/false`
- Nulls explicit (no sentinel strings)
- Ordered telemetry as arrays; keyed summaries as objects

### Communication Patterns

**Event System Patterns:**
- Event names use `domain.entity.action` (`simulation.run.started`)
- Payloads include `event_id`, `event_version`, `occurred_at`, and contextual IDs
- Breaking payload changes require event version bump

**State Management Patterns:**
- Immutable state updates in frontend
- Actions named `<feature>/<action>`
- Derived data via selectors rather than duplicated state

### Process Patterns

**Error Handling Patterns:**
- Backend domain errors mapped once at API boundary
- User-facing errors are actionable and sanitized
- Recoverable numerical conditions presented as warnings

**Loading State Patterns:**
- Async lifecycle modeled as `idle/loading/success/error`
- Long simulations expose heartbeat and last-update indicators
- Global loading restricted to application bootstrap

### Enforcement Guidelines

**All AI Agents MUST:**
- Follow naming and format contracts exactly
- Respect module/layer boundaries
- Use canonical response and error envelopes
- Include units/provenance metadata for scientific outputs
- Add/update tests for every contract-affecting change

**Pattern Enforcement:**
- CI checks: lint, types, contract tests, deterministic regression tests
- Pattern deviations treated as architecture conformance defects
- Pattern updates require architecture-document change + migration note

### Pattern Examples

**Good Examples:**
- `POST /runs` returns canonical envelope with run provenance metadata
- `simulation.run.completed` event includes typed payload and version
- `TelemetryPanel.tsx` consumes contract-normalized models only

**Anti-Patterns:**
- Mixed camelCase/snake_case in API payloads
- UI importing physics internals directly
- Unversioned event payload changes
- Raw backend exception text surfaced to end users

## Project Structure & Boundaries

### Complete Project Directory Structure

```text
grsimulator/
├── README.md
├── LICENSE
├── .gitignore
├── .editorconfig
├── .env.example
├── docker-compose.yml
├── Makefile
├── docs/
│   ├── TECHNICAL_DETAILS.md
│   ├── architecture/
│   └── adr/
├── backend/
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   ├── api/
│   │   │   ├── deps.py
│   │   │   ├── routers/
│   │   │   └── schemas/
│   │   ├── domain/
│   │   │   ├── physics/
│   │   │   ├── numerics/
│   │   │   ├── simulation/
│   │   │   └── validation/
│   │   ├── infra/
│   │   │   ├── db/
│   │   │   ├── cache/
│   │   │   └── events/
│   │   └── contracts/
│   ├── alembic/
│   │   └── versions/
│   └── tests/
│       ├── unit/
│       ├── integration/
│       ├── contract/
│       └── regression/
├── ui/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── index.html
│   ├── src/
│   │   ├── main.tsx
│   │   ├── app/
│   │   ├── features/
│   │   ├── components/
│   │   ├── state/
│   │   ├── services/
│   │   ├── contracts/
│   │   ├── utils/
│   │   └── styles/
│   ├── e2e/
│   └── tests/
├── scripts/
│   ├── dev/
│   ├── qa/
│   └── release/
└── .github/
    └── workflows/
        ├── ci.yml
        └── regression.yml
```

### Architectural Boundaries

**API Boundaries:**
- UI communicates with backend only via typed REST endpoints
- No direct UI access to simulation internals or storage layers

**Component Boundaries:**
- Domain physics/numerics/simulation logic isolated from transport and rendering concerns
- UI domain components consume normalized contract models at service boundary

**Service Boundaries:**
- Backend separates domain services from infra adapters (database, cache, events)
- Contract translation occurs at API edge, not inside core scientific modules

**Data Boundaries:**
- PostgreSQL as system of record
- Redis for transient telemetry and run-session acceleration
- Export artifacts include immutable provenance metadata

### Requirements to Structure Mapping

**Feature/FR Mapping:**
- FR1-FR10 -> `backend/app/domain/physics|numerics|simulation`
- FR11-FR15 -> `backend/app/domain/simulation` + API routers for scenarios/runs
- FR16-FR20 -> `ui/src/features/workspace|telemetry|exports` + backend telemetry/export routes
- FR21-FR23 -> `backend/app/domain/validation` + persistence + UI validation views

**Cross-Cutting Concerns:**
- Determinism: domain engine + regression suites + run metadata contracts
- Performance: numerics loop + telemetry throttling + frontend render cadence controls
- Accessibility: UI components and interaction state patterns

### Integration Points

**Internal Communication:**
- Domain services communicate via explicit interfaces and typed contracts
- Event channels follow `domain.entity.action` naming

**External Integrations:**
- Scientific-tool integrations through export formats (CSV/NumPy)

**Data Flow:**
- Scenario config -> simulation engine -> telemetry stream -> UI panels + persistence -> validation reports + exports

### File Organization Patterns

**Configuration Files:**
- Root and module-level typed configuration with environment profiles

**Source Organization:**
- Backend by architecture layer and scientific domain
- UI by feature modules with shared design-system primitives

**Test Organization:**
- Unit/integration/contract/regression separation in backend
- UI unit tests plus dedicated end-to-end directory

**Asset Organization:**
- Static assets kept in UI source/public paths; build outputs excluded from source control

### Development Workflow Integration

**Development Server Structure:**
- Backend and UI run independently with shared typed contracts

**Build Process Structure:**
- Separate backend and frontend builds with integrated CI quality gates

**Deployment Structure:**
- Containerized composition for local and release profiles with environment-specific configuration

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:**  
Chosen technologies and versions are mutually compatible for a desktop-first scientific simulation platform, and the selected split between simulation core, API boundary, and UI shell is coherent.

**Pattern Consistency:**  
Implementation patterns align with architectural decisions and address major multi-agent conflict points (naming, contracts, boundaries, and process behaviors).

**Structure Alignment:**  
The proposed project structure supports all major architectural decisions and preserves clear boundaries between domain logic, transport, infrastructure, and UI concerns.

### Requirements Coverage Validation ✅

**Feature/FR Coverage:**  
All FR categories are mapped to concrete backend or UI modules with explicit integration points.

**Functional Requirements Coverage:**  
FR1-FR23 are architecturally supported across domain computation, simulation orchestration, visualization/telemetry surfaces, export, validation, and persistence.

**Non-Functional Requirements Coverage:**  
NFRs are covered through deterministic execution posture, precision requirements, performance budgeting, observability, contract enforcement, and regression testing strategy.

### Implementation Readiness Validation ✅

**Decision Completeness:**  
Critical and important decisions are documented with practical defaults and version-anchored technology selections.

**Structure Completeness:**  
Project tree, module boundaries, and integration points are sufficiently specific to guide implementation kickoff.

**Pattern Completeness:**  
Consistency rules are explicit enough to minimize implementation drift across multiple AI agents.

### Gap Analysis Results

**Critical Gaps:** None that block implementation planning.

**Important Gaps (Non-Blocking):**
- Final desktop packaging choice (Tauri/Electron/PySide) remains deferred until post-MVP validation.
- Future multi-user auth model should be formalized before collaboration features.

**Nice-to-Have Gaps:**
- Expanded ADR set for future architecture pivots (GPU acceleration, distributed execution).
- Broader event catalog for advanced mission workflows.

### Validation Issues Addressed

- Confirmed UX architecture alignment now that UX spec exists and is integrated.
- Preserved architectural coherence despite deferred packaging by defining stable contracts and boundaries.

### Architecture Completeness Checklist

**✅ Requirements Analysis**
- [x] Project context thoroughly analyzed
- [x] Scale and complexity assessed
- [x] Technical constraints identified
- [x] Cross-cutting concerns mapped

**✅ Architectural Decisions**
- [x] Critical decisions documented with versions
- [x] Technology stack fully specified
- [x] Integration patterns defined
- [x] Performance considerations addressed

**✅ Implementation Patterns**
- [x] Naming conventions established
- [x] Structure patterns defined
- [x] Communication patterns specified
- [x] Process patterns documented

**✅ Project Structure**
- [x] Complete directory structure defined
- [x] Component boundaries established
- [x] Integration points mapped
- [x] Requirements to structure mapping complete

### Architecture Readiness Assessment

**Overall Status:** READY FOR IMPLEMENTATION PLANNING

**Confidence Level:** High

**Key Strengths:**
- Strong scientific-domain boundary modeling
- Determinism and validation-first architectural posture
- Clear consistency rules for multi-agent implementation

**Areas for Future Enhancement:**
- Packaging hardening pathway
- Collaboration and distributed compute roadmap details

### Implementation Handoff

**AI Agent Guidelines:**
- Follow architectural decisions as documented
- Apply implementation patterns consistently across all modules
- Respect project boundaries and contract definitions
- Treat determinism, validation metadata, and regression checks as non-negotiable

**First Implementation Priority:**
- Initialize UI starter and scaffold backend simulation/API contract skeleton in parallel
