# Planwise Enterprise: Next Phase Architecture Specification
**Document Version:** 2.0.0
**Target Milestone:** Post-Pilot Enterprise Maturation (Phases 9–13)
**Baseline Pilot Anchor:** `proj-mumbai-real-1100` (Bandra West, 1,100 sq ft, Option B G+1, Release `rel-pilot-20261002-aedf9830`, Design `DV-OPT-B-9be0a983`)
**Core Invariant:** Canonical Building Model (CBM) is the mathematical source of truth. Zero AI hallucination in statutory, structural, geometric, or financial pipelines.

---

## 1. Architectural Philosophy & Invariants

```
                                +-----------------------------------+
                                |     CANONICAL BUILDING MODEL      |
                                |            (CBM v1/v2)            |
                                |    Mathematical Source of Truth   |
                                +-----------------+-----------------+
                                                  |
         +--------------------+-------------------+-------------------+--------------------+
         |                    |                   |                   |                    |
         v                    v                   v                   v                    v
+-----------------+  +-----------------+  +---------------+  +-----------------+  +-----------------+
|   OPEN BIM /    |  |  PROFESSIONAL   |  |  STRUCTURAL   |  |   QTO & BOQ     |  |  CONSTRUCTION   |
|   IFC4 EXPORT   |  | DRAWING SHEETS  |  |  ANALYTICAL   |  | (IS 1200 Engine)|  |   CPM SCHEDULE  |
|  Georeferenced  |  |  (ISO 128 /     |  |   WIREFRAME   |  | (3-tier plaster |  | (Precedence,    |
| (IfcMapConvert) |  |   PreDCR DXF)   |  | (.e2k / JSON) |  |  deductions)    |  |  floors, float) |
+-----------------+  +-----------------+  +---------------+  +-----------------+  +-----------------+
```

### Core Invariants:
1. **Mathematical Single Source of Truth:**
   - No derived artifact (IFC, DXF, PDF, QTO, BOQ, Cost Estimate, or Schedule) may store independent geometric truth.
   - All spatial, volumetric, and material properties are deterministically compiled from CBM.
2. **AI Boundary Integrity:**
   - Assistive AI is strictly confined to unstructured brief parsing, natural-language explanation, and visual impression watermarking.
   - Prohibited from computing setbacks, column sizing, load paths, quantities, costs, or statutory approvals.
3. **Statutory & Professional Boundary:**
   - Computational validation $\neq$ Professional certification.
   - Gates G0, G1, G2, G3, and G4 require certified human professional review.
   - Gates G5 (Municipal Sanction) and G6 (Contractor Handoff) remain strictly `LOCKED` until external legal authorities issue formal sanctions.
4. **Immutable Release Cryptography:**
   - Released design packages are frozen with SHA-256 digests in PostgreSQL (`releases` table).
   - Any geometric, regulatory, or rate change creates a new version; unreleased draft packages are marked `is_stale = true`.

---

## 2. Priority 1 — BIM / IFC Professionalization

### 2.1 Standard Georeferencing Operations
To ensure exported IFC models federate seamlessly with municipal GIS platforms and Autodesk Civil 3D, the IFC serializer in [manifest_engine.py](file:///Users/surajkumar/Desktop/Real_state_dev/workers/release/manifest_engine.py) will incorporate formal buildingSMART georeferencing entities:
- **`IFCPROJECTEDCRS`**:
  Defines the authoritative projected coordinate reference system (e.g. `EPSG:32643` for UTM Zone 43N Mumbai, or `EPSG:7767` for Survey of India Zone IIb).
- **`IFCMAPCONVERSION`**:
  Binds the project's local Cartesian origin (0, 0, 0) to Eastings, Northings, Orthogonal Height, scale factor, and planar grid rotation angle ($\cos \theta, \sin \theta$).
- **`IFCGEOMETRICREPRESENTATIONCONTEXT`**:
  Directly references the `IfcMapConversion` entity.

### 2.2 Deterministic RFC 4122 v5 GUIDs
Replace ad-hoc string entity IDs with deterministic 22-character base64 IFC Globally Unique Identifiers:
- Seeded via RFC 4122 namespace UUIDv5: `UUIDv5(NAMESPACE_PLANWISE, f"{release_id}:{element_id}")`.
- Encoded using standard buildingSMART 64-character alphabet (`0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_$`).
- Guarantees element GUID stability across repeated export runs for unchanged elements.

### 2.3 Standard buildingSMART Property Sets & Classifications
Every physical element (`IfcWall`, `IfcColumn`, `IfcSlab`, `IfcDoor`, `IfcWindow`) receives:
- **`Pset_WallCommon` / `Pset_ConcreteElementGeneral`**:
  Declares `LoadBearing`, `IsExternal`, `FireRating`, `AcousticRating`, `NominalThickness`.
- **`IfcClassificationReference`**:
  Binds element to Uniclass 2015 (`Pr_20_85_12_02` for AAC Blocks) and CPWD DSR sub-heads.

---

## 3. Priority 2 — Professional Drawing Pipeline

### 3.1 Architectural Drawing Compiler Architecture
A dedicated compiler worker transforming CBM 3D geometry into publication-grade vector drawing sheets:
```
CBM (Spaces, Walls, Columns, Openings, Grids)
   │
   ▼
[Drawing Layout Engine]
   ├── Coordinate Projection (Top-down Plan, Front/Rear Elevation, Cross-Section)
   ├── Dimension String Generator (Chain dimensions: Wall thickness, Room clear width, Opening offsets)
   ├── Grid Line Annotation (Bubbles A-B, 1-4 with dimension callouts)
   ├── Room Tagging (Room name, Floor finish, Carpet area m², Sill/Lintel levels)
   └── Door/Window Schedule Tags (D1, D2, W1, W2 markers linked to opening schedules)
   │
   ▼
[Sheet Composition Engine]
   ├── ISO 128 / Council of Architecture Title Block (Project name, Client, Scale 1:100, Revision, Date)
   ├── True North Arrow & Scale Bar (Metric 1:100 / 1:50)
   ├── Revision History Block & Release Hash Seal
   └── Mandatory Legal Disclaimer Watermark
   │
   ▼
[Output Serializers]
   ├── High-Resolution Scaled PDF Drawing Sheet (A1 / A2 / A3)
   ├── Clean Vector SVG
   └── AutoDCR-ready Layered DXF
```

---

## 4. Priority 3 — Structural Analytical Model Compiler

### 4.1 Assistive Responsibility Boundary
Planwise does **NOT** build an internal black-box Finite Element Analysis (FEA) solver. Licensed structural engineers bear exclusive legal liability for seismic and gravity frame certification.
Planwise generates an **Analytical Structural Model** that certified engineers can import directly into certified software (CSI ETABS, STAAD.Pro).

### 4.2 Analytical Wireframe Specification
- **Structural Nodes:** Located at 3D intersections of column centerlines, beam centerlines, and foundation centroids.
- **Line Elements (Members):** Centerline frame elements for columns and beams with section profiles ($300 \times 450$ mm RC column, $230 \times 350$ mm RC beam).
- **Supports & Releases:** Pinned or fixed boundary conditions at foundation level; moment-resisting beam-column connections.
- **Gravity & Lateral Load Assignments (IS 875 Parts 1 & 2):**
  - Dead Loads (DL): Self-weight multiplier 1.0; masonry wall UDL on beams ($18 \text{ kN/m}^3 \times 0.23\text{m} \times 2.85\text{m} = 11.8\text{ kN/m}$).
  - Imposed Loads (LL): Residential habitable rooms ($2.0\text{ kN/m}^2$), balconies/stairs ($3.0\text{ kN/m}^2$).
  - Load Combinations: $1.5(\text{DL} + \text{LL})$, $1.2(\text{DL} + \text{LL} \pm \text{EL})$, $1.5(\text{DL} \pm \text{EL})$, $0.9\text{DL} \pm 1.5\text{EL}$ per IS 1893:2016.
- **Export Format:** Structured JSON and CSI ETABS text archive (`.e2k`).

### 4.3 Mandatory Seismic Detailing Guardrail (IS 13920:2016)
- **Minimum Column Dimension:** Under Clause 7.1.1, for earthquake-resistant frames in Seismic Zone III (Mumbai $Z=0.16$), no column dimension shall be less than **$300\text{ mm}$**.
- **Audit & Remediation:** Eliminate all residual $230\text{ mm}$ column references from reports and schedule renderers, establishing an invariant check in `validation_engine.py`.

---

## 5. Priority 4 — Preliminary MEP Model & Sizing

### 5.1 Domestic & Flushing Water Balance (NBC 2016 Part 9)
- **Per Capita Consumption:** $135\text{ lpcd}$ for residential units ($90\text{ lpcd}$ domestic + $45\text{ lpcd}$ flushing).
- **Occupancy Sizing:** 5 persons per 2BHK/3BHK unit.
- **Storage Sizing:**
  - Underground Sump (UGT): $1.0\times$ to $1.5\times$ daily requirement.
  - Overhead Tank (OHT): $0.5\times$ daily requirement.
  - Mumbai Bandra 1,100 sq ft pilot: 5 persons $\times 135\text{ L} = 675\text{ L/day}$.
  - Minimum OHT: $500\text{ L}$ domestic + $250\text{ L}$ flushing.

### 5.2 Electrical Distribution & Conduits (IS 732)
- **Connected Load Estimation:** Lighting ($10\text{ W/m}^2$), Power points ($1000\text{ W}$ kitchen/bath), AC points ($2000\text{ W}$ per bedroom/living).
- **Distribution Board (DB):** Main DB allocation with dedicated residual current circuit breakers (RCCB 30mA).
- **Conduit Reservations:** Vertical shafts reserved in CBM service runs.

---

## 6. Priority 5 — QTO Engineering & IS 1200 Compliance

### 6.1 Strict 3-Tier Plaster Deduction Engine (IS 1200 Part 6 Clause 4)
Replace uniform opening deductions with exact Indian Standard logic:
1. **Openings up to $0.50\text{ m}^2$:**
   - **Deduction:** $0.0\text{ m}^2$ (No deduction).
   - **Addition:** No addition for jambs, sills, or soffits.
2. **Openings between $0.50\text{ m}^2$ and $3.00\text{ m}^2$:**
   - **Deduction:** Deduct for **one face only** (i.e. $1.0 \times \text{Width} \times \text{Height}$).
   - **Addition:** No addition for jambs, sills, or soffits.
3. **Openings exceeding $3.00\text{ m}^2$:**
   - **Deduction:** Deduct for **both faces** (i.e. $2.0 \times \text{Width} \times \text{Height}$).
   - **Addition:** Measure jambs, sills, and soffits separately and add to plaster takeoff area:
     $$\text{Addition} = (2 \times \text{Height} + \text{Width}) \times \text{Wall Thickness}$$

### 6.2 Structural Intersection Volume Clipping (IS 1200 Part 2)
Prevent concrete double-counting at column-beam-slab junctions:
- **Columns:** Continuous from footing to roof (priority 1).
- **Beams:** Measured clear between column faces (priority 2).
- **Slabs:** Measured clear between beam faces (priority 3).

---

## 7. Priority 6 — Dynamic First-Principles Cost Engineering

### 7.1 CPWD DAR Standard Build-Up Formula
Evolve beyond static rate cards to dynamic first-principles rate analysis:
$$\text{Unit Rate} = \left[ \sum (Q_m \cdot R_m \cdot (1 + W_m)) + \sum (Q_l \cdot R_l) + \sum (Q_p \cdot R_p) \right] \times 1.01 \times 1.15 \times (1 + \text{GST})$$
Where:
- $Q_m, Q_l, Q_p$: Consumption coefficients per unit output from CPWD DAR 2023.
- $R_m, R_l, R_p$: Real-time or snapshot market rates for materials, labour, and plant.
- $W_m$: Standard statutory wastage (Cement: 5%, Steel: 3%, Sand: 10%, AAC Blocks: 8%).
- $1.01$: Mandatory 1% water charges on prime cost.
- $1.15$: Standard 15% contractor profit and overheads (CPOH).
- $\text{GST}$: 18% Goods and Services Tax on works contracts.

### 7.2 Invariant Protection for Controlled Pilot
The baseline pilot rate snapshot `INDIA-MUMBAI-2026-Q4-V1` remains immutable. The dynamic cost engine operates as an extensible rate provider that can calculate updated project estimates while reproducing the exact pilot baseline when configured with baseline rate inputs.

---

## 8. Priority 7 — Construction Scheduling Engine (CPM)

### 8.1 Critical Path Precedence Network
Upgrade [cpm_engine.py](file:///Users/surajkumar/Desktop/Real_state_dev/workers/schedule/cpm_engine.py) to execute rigorous CPM network analysis:
- **Activity WBS Hierarchy:**
  1. Level 1: Substructure (Mobilization, Excavation, PCC, Footings, Plinth Beams).
  2. Level 2: Superstructure (L0 Columns, L0 Slab, L1 Columns, L1 Terrace Slab).
  3. Level 3: Architecture & Envelope (AAC Masonry, Waterproofing, External Plaster).
  4. Level 4: MEP Rough-ins (Concealed Conduits, Wet Stacks, Hydrostatic Testing).
  5. Level 5: Finishes & Handover (Internal Plaster, Flooring, Painting, Snagging).
- **CPM Mathematical Solver:**
  - Forward Pass: Early Start ($ES$), Early Finish ($EF = ES + D$).
  - Backward Pass: Late Finish ($LF$), Late Start ($LS = LF - D$).
  - Total Float ($TF = LS - ES = LF - EF$).
  - Free Float ($FF = \min(ES_{\text{successors}}) - EF$).
  - Critical Path Identification: Activities with $TF = 0$.
- **Calendar & Weather Modeling:**
  - Date projection from project commencement date.
  - Regional monsoon buffer: Automatically expands plastering and earthwork activity durations during Mumbai monsoon window (June 10 – September 20).

---

## 9. System Dependency Graph

```
                                  [Level 0: Spatial Ground Truth]
                                   PostGIS Spatial Schema (SRID 4326/32643)
                                   SiteEvidenceEngine (L0–L4 Confidence)
                                                 │
                                                 ▼
                                  [Level 1: Core Mathematical Model]
                                   CanonicalBuildingModel (CBM v1/v2)
                                   Double-Precision Geodetic Coordinate Kernel
                                                 │
         ┌───────────────────────────────────────┼───────────────────────────────────────┐
         │                                       │                                       │
         ▼                                       ▼                                       ▼
[Level 2A: Open BIM & Permitting]   [Level 2B: Engineering Analysis]        [Level 2C: Quantities & Cost]
• Priority 1: Georeferenced IFC4    • Priority 3: Structural Wireframe      • Priority 5: IS 1200 3-Tier QTO
  (IfcMapConversion, UUIDv5)          (.e2k Export, IS 13920 Min 300mm)       (Plaster & Concrete Clipping)
• Priority 2: Professional Drawings • Priority 4: Preliminary MEP Systems   • Priority 6: Dynamic CPWD DAR
  (Scaled ISO 128 Sheets / DXF)       (Water Balance, Electrical Loads)       (First-Principles Rate Build-up)
         │                                       │                                       │
         └───────────────────────────────────────┼───────────────────────────────────────┘
                                                 │
                                                 ▼
                                  [Level 3: Professional Verification]
                                   G0–G6 Gate Ledger (PostgreSQL + Cryptographic Hashes)
                                   Mandatory Human Professional Boundary
                                                 │
                                                 ▼
                                  [Level 4: Scheduling & Project Delivery]
                                   Priority 7: Construction CPM Schedule (WBS, Floats, Monsoon)
                                   Complete Customer & Technical Dossier Packages
```

---

## 10. Phased Engineering Roadmap

| Milestone | Subsystem Scope | Primary Deliverables | Target Timeline / Status |
| :--- | :--- | :--- | :--- |
| **Milestone 1** | **BIM / IFC Professionalization** | • Deterministic RFC 4122 v5 UUIDs (22-char base64)<br>• `IfcMapConversion` & `IfcProjectedCRS` georeferencing<br>• Standard `Pset_*` property sets & Uniclass tags<br>• Automated IFC compliance tests | **Recommended First Step** |
| **Milestone 2** | **Professional Drawing Compiler** | • Standalone scaled ISO 128 drawing sheet generator (PDF/SVG)<br>• Elevation & cross-section projection engines<br>• Chain dimensioning, grid bubbles, room tags | Milestone 2 |
| **Milestone 3** | **Structural Analytical Model** | • Analytical frame compiler (nodes, members, dead/live loads)<br>• CSI ETABS `.e2k` & JSON export<br>• IS 13920 column dimension verification ($\ge 300$ mm) | Milestone 3 |
| **Milestone 4** | **QTO IS 1200 Deduction Engine** | • 3-Tier plaster deduction engine (IS 1200 Part 6 Clause 4)<br>• Boolean CSG volume clipping for beam-column nodes<br>• Full QTO regression against 1,100 sq ft pilot | Milestone 4 |
| **Milestone 5** | **Dynamic Cost & Rate Build-up** | • CPWD DAR 2023 first-principles rate build-up calculator<br>• Material wastage, labour constants, contractor overheads<br>• Dynamic rate indexation | Milestone 5 |
| **Milestone 6** | **Construction Scheduling (CPM)** | • Rigorous CPM forward/backward pass & float calculation<br>• Calendar date mapping & Mumbai monsoon buffer<br>• Schedule visualization API & UI Gantt view | Milestone 6 |
| **Milestone 7** | **Preliminary MEP Coordination** | • NBC 2016 Part 9 domestic/flushing water storage engine<br>• Electrical connected load & DB sizing<br>• Vertical shaft clash prevention | Milestone 7 |

---

## 11. Rollback Strategy & Anti-Regression Safeguards

1. **Pilot Baseline Freezing:**
   The Bandra West 1,100 sq ft pilot dataset (`proj-mumbai-real-1100`, release `rel-pilot-20261002-aedf9830`, design `DV-OPT-B-9be0a983`) serves as the permanent golden reference.
2. **Regression Gate:**
   Prior to merging any milestone, run:
   ```bash
   .venv/bin/python3 -m unittest discover tests
   npm --prefix apps/web test
   ```
   All 136 backend tests and 20 frontend Vitest tests must pass without regression.
3. **Additive Architecture:**
   New entities (`IfcMapConversion`, analytical wireframes, 3-tier deductions, CPM schedules) are introduced additively. Core schemas maintain backward compatibility with existing releases.
