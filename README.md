# Planwise Enterprise — Land-to-Home Development & Construction Platform

An institutional-grade, end-to-end **Land-to-Home Development & Construction Platform** built according to the **Development-Ready Delta Specification** and the **Archonet Planwise Engineering Master Plan**.

The platform provides a complete, deterministic bridge from raw land parcel digitization through statutory zoning compliance (**Mumbai MCGM DCPR 2034**), solver-backed residential floor-plan generation (**NBC 2016**), model-traceable Bill of Quantities (QTO/BOQ), Critical Path Method (CPM) construction scheduling, and an immutable professional engineer handoff workflow.

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
