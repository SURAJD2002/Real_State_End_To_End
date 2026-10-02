# PLANWISE ENTERPRISE — M2 GAP ANALYSIS
## Deterministic House Layout Generator + Geometry Compiler + Manifold3D Solid Model

---

### 1. Executive Repository Audit
An exhaustive audit of the existing codebase confirms that:
1. **M1 (Site & Rules) is complete and authoritative**:
   - `packages/schemas/coordinates.py` & `workers/geometry/crs_engine.py`: Sub-nanometer WGS84 $\leftrightarrow$ ECEF $\leftrightarrow$ ENU (SECS) $\leftrightarrow$ BCS transforms using Bowring's 1985 formulation.
   - `packages/schemas/site_evidence.py` & `workers/evidence/evidence_engine.py`: L0–L4 provenance model, blocking BUILD releases if $< L3$.
   - `packages/schemas/regulation_rules.py` & `workers/regulation/rule_engine.py`: Declarative rule packs (`MUMBAI-DCPR-2034-V1` & `BBMP-BENGALURU-2026-V1`), edge classification, explicit road widening surrender, directional setbacks, FSI components, coverage, height, parking, and `RuleExecutionTrace`.
   - Output contract provides: `buildableCoordinatesSECS`, `effectivePermittedFootprintSqm`, `SiteReferenceFrame`, and rule traces.
2. **Canonical Building Model (CBM) exists and is authoritative**:
   - `packages/schemas/building_model.py`: Fully normalized hierarchy: `Project` $\rightarrow$ `Site` $\rightarrow$ `DesignOption` $\rightarrow$ `BuildingLevel` $\rightarrow$ `Space` $\rightarrow$ `BuildingElement` (Walls, Slabs, Columns, Stairs) $\rightarrow$ `Opening` (Doors, Windows) $\rightarrow$ `StructuralGrid`.
   - `workers/generation/model_compiler.py`: Deterministic compiler from room layouts into CBM with SHA-256 fingerprinting.
   - `workers/generation/validation_engine.py`: Automated rule check validation suite (NBC 2016 dimensions, structural spans, referential integrity).
   - `workers/generation/projections.py`: Pure mathematical derivations of 2D Floor Plan, Facade Elevations (N/S/E/W), Transverse Section Cuts (A-A), and 3D scene meshes for Three.js.
3. **Current Generation Limitations (Pre-M2)**:
   - `workers/generation/house_generator.py` previously relied on parameterized static archetype templates (`compact_2bhk`, `family_3bhk`, `duplex_3bhk`) with hardcoded coordinate ratios rather than a dynamic constraint optimization solver.
   - `ortools` was imported optionally; CP-SAT constraint formulation was not wired to M1 `buildableCoordinatesSECS` or dynamic customer briefs.
   - Solid 3D geometry was limited to polygonal boundary extrusions rather than certified 2-manifold watertight boundary representations (B-Reps).
   - No multi-objective Pareto filtering frontier across distinct candidates.

---

### 2. Comprehensive Gap Analysis Matrix

| Research Requirement | Existing Implementation | Missing Work | M2 Action |
| :--- | :--- | :--- | :--- |
| **Customer Brief Model** | Implicit / hardcoded in archetype definitions | Normalized versioned `CustomerBrief` schema with source, confidence, and hard vs soft constraint flags | Implement `CustomerBrief` schema in `packages/schemas/customer_brief.py` |
| **Room Program Model** | Dictionary list in `house_generator.py` | Strongly typed `RoomProgram` & `RoomSpecification` with NBC 2016 min/max areas, widths, aspect ratios, daylight/ventilation requirements | Implement `RoomProgram` schema and centralized standards |
| **Room Adjacency Graph** | Ad-hoc lists in comments | Formal directed/undirected graph with `REQUIRED_ADJACENCY`, `PREFERRED_ADJACENCY`, `FORBIDDEN_ADJACENCY`, and privacy buffers | Implement `RoomAdjacencyGraph` in `packages/schemas/room_graph.py` |
| **CP-SAT Layout Solver** | Fallback bay-ratio layout generator | Real OR-Tools CP-SAT formulation with integer-scaled coordinates (`SOLVER_UNIT_MM`), non-overlap, footprint containment, multi-floor, and stair zones | Implement `workers/generation/cpsat_solver.py` |
| **Multi-Option Diversity** | 3 fixed archetypes (`2BHK`, `3BHK`, `Duplex`) | Algorithmic generation of $\ge 3$ distinct candidates via exclusion cuts / no-goods constraints and spatial fingerprinting | Implement multi-candidate generation with spatial differentiation |
| **Pareto Filtering** | Hardcoded scores in `house_generator.py` | Multi-objective scoring (carpet efficiency, circulation ratio, daylight proxy, constructability proxy, customer fit) & non-dominated Pareto frontier | Implement `ParetoEvaluator` in `workers/generation/pareto_filter.py` |
| **Deterministic Geometry Compiler** | Basic rectangular room wall offsets | End-to-end compiler converting CP-SAT rectangular assignments into canonical walls, openings, slabs, and columns | Enhance `model_compiler.py` to ingest CP-SAT solver results |
| **Manifold3D Solid Modeling** | Extruded Three.js visual meshes only | Solid geometry kernel (`manifold3d`) creating watertight 2-manifold solids for walls, slabs, columns, and stairs with boolean operations | Integrate `manifold3d` in `workers/geometry/solid_engine.py` |
| **Geometry & Solid Validation** | 2D polygon validity in `validation_engine.py` | Explicit 3D 2-manifold validation (watertight, positive volume, non-manifold edge detection, degenerate face rejection) | Implement `GeometryValidationResult` & manifold checks |
| **Parametric Stairs** | Hardcoded dog-legged placeholder | Parametric stair generator obeying riser/tread constraints, floor-to-floor heights, and landing geometry | Implement deterministic stair synthesis in geometry compiler |
| **Deterministic Openings** | Static opening ratio calculation | Wall-intersection openings obeying clearance, access, circulation, and daylight proxies | Implement opening synthesizer in geometry compiler |
| **Structural Grid Proxy** | Heuristic 4m grid generator | Grid alignment tied to room partitions and preliminary column placement | Harden structural column grid generator |
| **Reproducibility Fingerprinting** | Model SHA-256 fingerprinting | Complete design version fingerprint: $\text{SHA256}(\text{Site} + \text{Rules} + \text{Brief} + \text{Solver} + \text{Compiler} + \text{CBM})$ | Implement versioned reproducible design fingerprinting |
| **M2 Golden Benchmarks** | M1 Golden Benchmarks (site/rules only) | 5 deterministic M2 layout benchmarks (Villa, Narrow Plot, Irregular Plot, Corner Plot, Duplex) | Implement `tests/benchmarks/m2_generation_benchmark.py` |
| **Async Generation API** | Synchronous endpoint in `main.py` | Async job workflow with state progression (`REQUESTED` $\rightarrow$ `SOLVE` $\rightarrow$ `COMPILE` $\rightarrow$ `VALIDATE` $\rightarrow$ `COMPLETED`) | Implement async endpoints and background task handler |
| **Frontend UI Integration** | Static options carousel | Dynamic generation trigger, Pareto comparison view, 2D/3D inspection, and constraint breakdown | Connect real M2 generation pipeline to `HouseOptionsCarousel.tsx` & Studio |

---

### 3. Reusable Assets & Anti-Duplication Strategy
To honor the strict directive: **DO NOT REBUILD EXISTING SYSTEMS**:
1. **Reuse `CanonicalBuildingModel`**:
   The domain models in `packages/schemas/building_model.py` are mature, schema-versioned (`1.0.0`), and already wired to IFC4 export, QTO takeoffs, and BOQ cost schedules. M2 outputs will compile directly into `CanonicalBuildingModel`.
2. **Reuse M1 Coordinate & Rule Outputs**:
   M2 consumes `buildableCoordinatesSECS`, `effectivePermittedFootprintSqm`, `SiteReferenceFrame`, and `RuleExecutionTrace` constraints without altering M1 algorithms or benchmarks.
3. **Reuse Projections & Renderers**:
   `projections.py` already derives floor plans, elevations, sections, and Three.js 3D meshes from CBM. The frontend will consume these projections directly.
4. **Harden Rather than Replace**:
   `workers/generation/house_generator.py` will be upgraded from heuristic archetypes to invoke the deterministic `cpsat_solver.py`, `pareto_filter.py`, and `solid_engine.py`.

---

### 4. Implementation Plan for M2
- **Phase 1**: Customer Brief & Constraint Model (`packages/schemas/customer_brief.py`).
- **Phase 2**: Room Program & NBC 2016 Standards (`packages/schemas/room_program.py`).
- **Phase 3**: Room Adjacency Graph (`packages/schemas/room_graph.py`).
- **Phase 4**: Integer CP-SAT Layout Solver (`workers/generation/cpsat_solver.py`).
- **Phase 5**: Controlled Diversity & Multi-Option Generator.
- **Phase 6**: Multi-Objective Pareto Filter (`workers/generation/pareto_filter.py`).
- **Phase 7 & 8**: Deterministic Geometry Compiler & Manifold3D Solid Engine (`workers/geometry/solid_engine.py`).
- **Phase 9, 10, 11, 12**: CBM Compilation, Deterministic Openings, Stairs, Structural Grid Proxy.
- **Phase 13 & 14**: Comprehensive Design Validation & Structured Failure Explanations.
- **Phase 15 & 16**: Performance Benchmarking ($< 5\text{s}$ target) & 5 Golden M2 Benchmarks.
- **Phase 17 & 18**: Versioned Async APIs in `apps/api-gateway/main.py`.
- **Phase 19, 20, 21**: Frontend Studio Integration in `App.tsx` and `HouseOptionsCarousel.tsx`.
- **Phase 22, 23, 24**: Reproducibility Fingerprinting, Change Propagation, Comprehensive Unit Test Suite.
