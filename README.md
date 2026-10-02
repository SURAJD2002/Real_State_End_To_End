# Planwise Enterprise — Land-to-Home Development & Construction Platform

An institutional-grade, end-to-end **Land-to-Home Development & Construction Platform** built according to the **Development-Ready Delta Specification** and the **Archonet Planwise Engineering Master Plan**.

The platform provides a complete, deterministic bridge across the six core project stages:
$$\textbf{Land} \longrightarrow \textbf{Feasibility} \longrightarrow \textbf{Design} \longrightarrow \textbf{Cost} \longrightarrow \textbf{Build Review} \longrightarrow \textbf{Engineer Review}$$

---

### ⚠️ Implementation Scope & Engineering Boundaries

- **Current Implementation:** **Phase 7 COMPLETE** (Phases 1 through 7 are complete, fully integrated, and backed by automated regression tests: 101/101 PASS).
- **Phase 8 NOT IMPLEMENTED** (Execution Tracking & Field Telemetry is not implemented; no Phase 8 code or features are present).
- **Professional Verification Boundary:**
  - **Computational validation $\neq$ professional certification** (Computational validation is NOT professional certification).
  - **Engineer Review does NOT automatically authorize construction.** Specifically, **Gates G5 (Site Release) and G6 (Construction Kickoff) do NOT grant automatic construction authorization.** Automated evaluations verify rule-based statutory criteria (e.g., Mumbai MCGM DCPR 2034, NBC 2016, IS 456), but physical site release and construction kickoff strictly require attributable review, wet-ink / digital stamping, and statutory municipal permits signed by a licensed professional engineer (Delta Spec §14).
  - No features beyond Phase 7 are implemented or active.

---

## 🏛 System Architecture & Delta Specification Pillars

```
                                  +-----------------------------------------+
                                  |   Customer Studio (React 19 + Vite)     |
                                  |  - CAD Parcel Digitizer & Setback Map   |
                                  |  - Feasibility HUD (DCPR 2034 FSI & GDV)|
                                  |  - 3 Parametric House Options (CP-SAT)  |
                                  |  - 2D Floor Plan Viewer & Column Grid   |
                                  |  - Traceable BOQ Takeoff Explorer       |
                                  |  - [REQUEST BUILD] Immutable Lock Modal |
                                  +--------------------+--------------------+
                                                       |
                                            (HTTP / REST / OpenAPI)
                                                       v
                                  +-----------------------------------------+
                                  |       FastAPI Stateless Gateway         |
                                  |  - /api/v1/projects & auto-save (600ms) |
                                  |  - /api/v1/projects/:id/house-options   |
                                  |  - /api/v1/design-versions/:id/build    |
                                  |  - /api/v1/releases/:id/approvals       |
                                  |  - /api/v1/releases/:id/ifc (BIM IFC4)  |
                                  +----+--------------------+---------------+
                                       |                    |
                 +---------------------+                    +---------------------+
                 v                                                                v
+---------------------------------+                              +---------------------------------+
|   Computational Workers         |                              |   Licensed Engineer Dashboard   |
| - Geometry: UTM 43N & Setbacks  |                              | - Immutable SHA-256 Fingerprint |
| - Regulation: Mumbai DCPR 2034  |                              | - Verification Gates G0 to G8   |
| - Generation: Bounded Archetypes|                              | - Attributable Review Sign-Off  |
| - Takeoff: Traceable QTO & BOQ  |                              | - Download IFC4 BIM Model       |
| - Schedule: CPM Precedence Net  |                              | - Download Release Manifest     |
+---------------------------------+                              +---------------------------------+
```

---

## 🔑 Key Subsystems & Deliverables

### 1. Parametric House Generator (`workers/generation/house_generator.py`)
- Solves discrete room placement, adjacencies, and circulation constraints per **NBC 2016 Part 3**:
  - `compact_2bhk`: Contemporary 2BHK ($95\text{ m}^2$), 1 floor, covered parking bay.
  - `family_3bhk`: Courtyard Villa ($145\text{ m}^2$), dual master suites, sky lightwell.
  - `duplex_3bhk`: Executive Residence ($180\text{ m}^2$), 2 levels with private upper terrace.
- Places 2D architectural room spaces, outer walls, interior partitions, doors, windows, and structural column grids ($300\text{mm} \times 450\text{mm}$).
- Computes multi-objective Pareto scores across area efficiency, daylight proxy, ventilation proxy, privacy, circulation quality, and budget fit.

### 2. Model-Linked Traceable BOQ Engine (`workers/qto/boq_engine.py`)
- Implements `quantity = measure(model_objects, takeoff_rule_version)` (Delta Spec §10 & §26):
  - `EXC-01`: Trench & foundation excavation ($m^3$)
  - `RCC-01`: Footing, column & slab concrete ($m^3$)
  - `MAS-01`: External & internal masonry ($m^2$) minus openings
  - `PL-01`: Smooth internal & sand-faced external plaster ($m^2$)
  - `FL-01`: Vitrified nano-polished tile flooring ($m^2$)
  - `DR-01`: Engineered wooden flush doors (count)
  - `WIN-01`: UPVC 3-track sliding windows (count)
  - `ELE-01`: Concealed copper wiring & modular switches (points)
  - `PLB-01`: Plumbing stacks & CP sanitary fixtures
  - `PNT-01`: Low-VOC interior emulsion & exterior weather-shield ($m^2$)
- Provides rate cards for **Standard**, **Premium**, and **Luxury** tiers with 5% contingency, 8% contractor prelims, and uncertainty ranges (Low -5% to High +10%). Exportable directly to CSV.

### 3. CPM Construction Schedule Engine (`workers/schedule/cpm_engine.py`)
- Deterministic 16-activity precedence network (Delta Spec §11):
  - Pre-construction release $\rightarrow$ Mobilization $\rightarrow$ Excavation $\rightarrow$ Foundation $\rightarrow$ Plinth $\rightarrow$ Structure $\rightarrow$ Masonry $\rightarrow$ MEP rough-in $\rightarrow$ Plaster $\rightarrow$ Waterproofing $\rightarrow$ Finishes $\rightarrow$ Commissioning $\rightarrow$ Final Handover.
  - Computes forward pass, critical path (zero float), duration in weeks, and calendar milestones.

### 4. BUILD Button & Immutable Release Lock (`workers/release/manifest_engine.py`)
- Customer confirmation dialog with mandatory legal/professional delivery acknowledgements (Delta Spec §12):
  1. Professional delivery request under a frozen design version.
  2. Estimate range and site verification requirement.
  3. Statutory municipal permit responsibility and change-order rules.
- Computes cryptographic release fingerprint:
  $$\text{release\_fingerprint} = \text{SHA-256}(\text{geometry\_hash} \parallel \text{regulation\_hash} \parallel \text{brief\_hash} \parallel \text{design\_hash} \parallel \text{boq\_hash} \parallel \text{schedule\_hash})$$
- Generates open-standard **IFC4 STEP** physical file (`.ifc`) for BIM coordination (Delta Spec §1).

### 5. Licensed Engineer & Contractor Verification Dashboard
- Viewable via the header switcher (**Customer Studio** $\leftrightarrow$ **Engineer Dashboard**).
- Displays the immutable SHA-256 Release Fingerprint.
- Implements the complete **G0 to G8 Human Verification Gates Matrix** (Delta Spec §14):
  - `G0`: Plot Intake & Boundary Provenance
  - `G1`: Statutory Feasibility Review
  - `G2`: Design Candidate Suitability
  - `G3`: Structural & MEP Preliminary Clash Check
  - `G4`: Build Lock & Commercial Scope Confirmation
  - `G5`: Site Release & Geotechnical Confirmation
  - `G6`: Construction Kickoff Authorization
  - `G7`: Milestone & QA Acceptance
  - `G8`: Completion Certificate & Final Handover
- One-click downloads for **Full Manifest (JSON)** and **BIM Model (IFC4)**.

---

## 📂 Repository & Project Structure

The codebase is organized into modular services, workers, schemas, and test suites:

- **`apps/`**: Application frontend and gateway services:
  - `apps/web/`: React 19 + Vite + TypeScript client containing the Customer Studio (CAD parcel digitizer, Feasibility HUD, House Options carousel, 2D Floor Plan viewer, Cost breakdown) and the Licensed Engineer Review Dashboard.
  - `apps/api-gateway/`: FastAPI stateless backend routing geometry, regulation, design generation, QTO/BOQ calculation, release locking, and verification gate handoffs.
- **`packages/`**: Reusable schemas, shared domain types, and statutory rule specifications:
  - `packages/schemas/`: Pydantic V2 schemas for Canonical Building Models (CBM), QTO, BOQ, rate snapshots, customer briefs, room graphs, and release manifests.
  - `packages/rules/`: Statutory regulation rule definitions (e.g., `mumbai_dcpr_2034_v1.json`, `bbmp_bengaluru_2026.json`) and golden benchmark fixtures.
  - `packages/shared-types/`: Shared TypeScript domain models mirroring backend schemas.
- **`workers/`**: Computational pipeline worker engines:
  - `workers/geometry/`: Geodetic transformations (WGS84 $\leftrightarrow$ UTM Zone 43N) and boundary solid geometry compilation.
  - `workers/regulation/`: Rule execution engine evaluating setbacks, ground coverage, permissible FSI, and road width requirements.
  - `workers/generation/`: OR-Tools CP-SAT discrete constraint solver for residential floor plan generation and multi-objective Pareto ranking.
  - `workers/qto/`: DAG-based measurement engine, CPWD DSR rate snapshotting, BOQ rollup, and dynamic change propagation.
  - `workers/schedule/`: CPM precedence network calculating critical paths, activity float, and project duration.
  - `workers/release/`: SHA-256 cryptographic manifest generator and IFC4 STEP physical file compiler.
  - `workers/evidence/`: Document intake and provenance engine.
- **`tests/`**: Comprehensive test suites (101 automated tests across 8 test modules):
  - `test_phase7_engineer_review.py`: Gates G0–G8, professional handoff, manifest hashing, and IFC export.
  - `test_real_plot_end_to_end.py`: Invariant verification for the authoritative 1,100 sq ft real plot.
  - `test_canonical_building_model.py`: CBM structural validation.
  - `test_m1_site_and_rules.py`: Geodetic coordinate transforms and DCPR 2034 rule evaluation.
  - `test_m2_generator_and_solids.py`: House generation and solid model generation.
  - `test_m3_qto_and_cost.py`: QTO measurements, BOQ, and CPM scheduling.
  - `benchmarks/`: CP-SAT solver performance benchmarking suite.
- **`database/migrations/`** (or `migrations/`): Relational schema definitions with PostGIS 3.4 spatial extensions:
  - `02_canonical_building_model.sql`: Building model and spatial tables.
  - `03_site_evidence_and_rule_engine.sql`: Evidence and regulatory schemas.
  - `04_qto_boq_and_cost_engine.sql`: QTO, BOQ, and rate snapshot persistence.
- **`infrastructure/`**: Deployment and environment infrastructure:
  - `infrastructure/docker/`: Docker Compose configurations for PostgreSQL 16 + PostGIS 3.4 and Redis.
- **`docs/`**: Engineering documentation, architecture blueprints, and milestone delivery reports:
  - `docs/README.md`: Index of engineering specifications and master plans.
  - `PHASE_7_ENGINEER_REVIEW_REPORT.md` / `PHASE_7_ENGINEER_REVIEW_REPORT.pdf`: Authoritative Phase 7 verification report.
  - Milestone development reports, master plan blueprints, and gap analyses.

---

## 🚀 Live Services & Development Quickstart

| Service | Port / URL | Status | Description |
|---|---|:---:|---|
| **Web Application** | [http://localhost:5173](http://localhost:5173) | **RUNNING** | Customer Studio & Engineer Dashboard with 2D Floor Plan Viewer |
| **API Gateway** | [http://localhost:5001](http://localhost:5001) | **RUNNING** | FastAPI service with Swagger docs at [http://localhost:5001/docs](http://localhost:5001/docs) |

### Start Services Locally:
```bash
# 1. Start Docker PostGIS 16 & Redis
npm run docker:up

# 2. Start FastAPI Backend & Workers
source .venv/bin/activate
cd apps/api-gateway
python3 main.py

# 3. Start Frontend Workspace (in a separate terminal)
npm run dev:web
```

---

## 🧪 End-to-End Verification Test

To test the entire pipeline programmatically:
```bash
python3 -c "
import urllib.request, json
base = 'http://localhost:5173/api/v1'

# 1. Fetch House Options
with urllib.request.urlopen(f'{base}/projects/proj-mumbai-default-01/house-options') as r:
    opts = json.loads(r.read().decode())
print(f'Options count: {len(opts)}')

# 2. Lock Build Request
payload = json.dumps({
    'designVersionId': opts[0]['designVersionId'],
    'optionId': opts[0]['optionId'],
    'customerAcknowledgements': ['ESTIMATE_RANGE', 'SITE_VERIFICATION', 'PROFESSIONAL_DELIVERY']
}).encode()
req = urllib.request.Request(f'{base}/design-versions/{opts[0][\"designVersionId\"]}/build-request', data=payload, headers={'Content-Type':'application/json'}, method='POST')
with urllib.request.urlopen(req) as r:
    res = json.loads(r.read().decode())
print('Release Fingerprint:', res['releaseFingerprint'])

# 3. Gate G3 Approval
g_payload = json.dumps({'gate': 'G3', 'decision': 'APPROVED', 'notes': 'IS 456 verified'}).encode()
g_req = urllib.request.Request(f'{base}/releases/{res[\"releaseId\"]}/approvals', data=g_payload, headers={'Content-Type':'application/json'}, method='POST')
with urllib.request.urlopen(g_req) as r:
    g_res = json.loads(r.read().decode())
print('Gate Status:', g_res['lifecycleState'])
"
```
