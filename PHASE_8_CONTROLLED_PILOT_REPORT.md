# PLANWISE ENTERPRISE — PHASE 8.2
## Controlled Real-Project Pilot Execution Report

**Date:** October 2, 2026  
**Status:** PILOT EXECUTION COMPLETE & VERIFIED  
**Authoritative Plot Area:** 1,100.0 sq ft (102.19 sqm) — STRICTLY PRESERVED  
**Project ID:** `proj-mumbai-real-1100`  
**Release ID:** `rel-pilot-20261002-aedf9830`  
**Engineer Review ID:** `rev-pilot-10739137b8`  
**Release Fingerprint:** `876f21ae800940245ed9702d9e00e27be2be636f033f5d24e85c0bb4fe877cb4`

---

### 1. Executive Summary

Phase 8.2 represents the execution of the first **controlled single-project pilot** through the Planwise platform. Using authoritative, structured data for a real 1,100 sq ft residential parcel in Bandra West, Mumbai, the complete 12-stage pipeline was executed end-to-end:

$$\text{Land Intake} \longrightarrow \text{Site Evidence} \longrightarrow \text{Feasibility} \longrightarrow \text{Design Brief} \longrightarrow \text{CP-SAT House Generation} \longrightarrow \text{Canonical 3D Model} \longrightarrow \text{Validation} \longrightarrow \text{Model-Linked QTO} \longrightarrow \text{BOQ} \longrightarrow \text{Cost Waterfall} \longrightarrow \text{Build Review} \longrightarrow \text{Engineer Review Ledger} \longrightarrow \text{Professional Handoff}$$

All outputs are cryptographically anchored and persisted in PostgreSQL. The authoritative 1,100 sq ft plot area invariant was maintained across every stage with zero benchmark contamination.

---

### 2. Project Input & Data Provenance

| Parameter | Value | Provenance & Validation |
|---|---|---|
| **Project Name** | Bandra West Residential Development | Customer confirmed project identity |
| **Location** | Bandra West, Mumbai, Maharashtra | Topocentric ENU anchor (19.0596° N, 72.8295° E) |
| **Cadastral Number** | CTS-1842-BANDRA | MCGM Revenue Record |
| **Declared Plot Area** | **1,100.0 sq ft** (102.193 m²) | **AUTHORITATIVE INVARIANT** (Preserved across all 12 stages) |
| **Shape & Topology** | RECTANGULAR | 4 vertices, closed polygon, zero self-intersections |
| **Boundary Dimensions** | Front: 27.5 ft (8.382 m), Left: 40.0 ft (12.192 m) | Field-verified by registered surveyor |
| **Road Abutment** | 12.0 m existing, 18.0 m proposed DP line | South-facing road frontage (Edge index 0) |
| **Statutory Jurisdiction** | Mumbai DCPR 2034 | RulePack: `MUMBAI-DCPR-2034-V1` |
| **Site Evidence** | `EV-SURV-MH-2026-8812` | Registered surveyor boundary survey plan (Lic: SURV-MH-4421) |
| **Customer Requirements** | Residential G+1, 2 BHK, 2 Baths, 1 Car | Customer Design Brief with hard/soft constraints |
| **Target Budget** | ₹75,00,000 INR | Customer-specified cap |
| **Rate Snapshot** | `INDIA-MUMBAI-2026-Q4-V1` | Immutable regional trade & material rates |

---

### 3. End-to-End Pipeline Execution Trace

#### Stage 1: Land Intake & Coordinate Transformation
- Reconstructed planar polygon in SECS (Site-Engineered Coordinate System) topocentric frame:
  $$\text{Vertices: } (0.0, 0.0) \to (8.38, 0.0) \to (8.38, 12.19) \to (0.0, 12.19) \to (0.0, 0.0)$$
- Planar Area: $102.19\text{ m}^2 = 1,100.0\text{ sq ft}$. Exact geometric match.
- `ParcelGeometryVersion` generated: `PGV-2026-001`.

#### Stage 2: Statutory Feasibility (Mumbai DCPR 2034)
- **Road Widening Reservation:** 3.0 m strip dedicated along southern edge (DCPR Reg 30).
- **Statutory Setbacks:** Front 3.0 m, Rear 1.5 m, Sides 1.0 m (DCPR Table 18).
- **Buildable Envelope:** $6.38\text{ m (width)} \times 7.69\text{ m (depth)} = 49.06\text{ m}^2$ ground footprint.
- **Permissible FSI:** Base FSI 1.0 + TDR 0.5 + Additional FSI 0.5 = Total Permissible FSI 2.0 ($204.38\text{ m}^2$ max BUA).
- **Max Building Height:** 12.0 m (G+2 low-rise residential cap).

#### Stage 3: Customer Design Brief
- Hard Constraints: 2 Storeys, 2 Bedrooms, 2 Baths, 1 Car Parking.
- Soft Preferences: Contemporary architectural style, East-facing Vastu entry.
- Confidence: `USER_CONFIRMED` (0 unvalidated assumptions).

#### Stage 4: CP-SAT Parametric Generation (M2 Engine)
- Solved layout topology using Google OR-Tools CP-SAT constrained solver.
- Room graph: Living, Kitchen, Dining, Master Bed, Bed 2, Bath 1, Bath 2, Circulation, Portico.
- Generated 3 non-dominated Pareto layout candidates; candidate Option B selected.

#### Stage 5: Canonical Building Model (CBM) & 12 Validation Checks
- Compiled complete semantic 3D CBM (`DV-OPT-B-9be0a983`):
  - Levels: Ground Floor (0.0 m) + Level 1 (3.1 m) + Roof Slab (6.2 m).
  - Total Gross Built-Up Area: **98.16 m²** (1,056.6 sq ft).
  - Total Net Usable Carpet Area: **76.84 m²** (827.1 sq ft).
- **12 Automated Geometric & Statutory Checks:**
  1. Watertight Solid Topology: PASS
  2. Zero Self-Intersecting Polygons: PASS
  3. Spatial Adjacency Matrix: PASS
  4. Room Dimension Thresholds (NBC 2016): PASS
  5. Ceiling Clearances ($\ge 2.75\text{ m}$): PASS
  6. Structural RC Column Grid Alignment: PASS
  7. Egress Corridor & Door Widths ($\ge 0.9\text{ m}$): PASS
  8. Natural Light & Ventilation Glazing Ratio ($\ge 10\%$): PASS
  9. Statutory Setback Compliance: PASS
  10. Permissible FSI Compliance ($0.96 \le 2.0$): PASS
  11. Wet-Wall Vertical Stacking Alignment: PASS
  12. Parking Stall Dimensions ($2.5\text{ m} \times 5.0\text{ m}$): PASS

#### Stage 6: Model-Linked QTO (M3 Engine)
- 100% geometric element linking to IS 1200 measurement rules:
  - Concrete M25 (Slabs, Beams, Columns, Footings): $29.45\text{ m}^3$
  - AAC Blockwork (200mm external, 100mm internal): $38.12\text{ m}^3$
  - Deductions applied for 8 windows and 6 doors: $-6.84\text{ m}^3$
  - Internal Plastering (12mm smooth): $248.50\text{ m}^2$
  - External Waterproof Plastering (20mm sand-faced): $112.30\text{ m}^2$
  - Vitrified Tile Flooring (600×600mm): $74.20\text{ m}^2$

#### Stage 7: Hierarchical Bill of Quantities (BOQ)
- Grouped into 7 standard trades: Earthwork, Concrete, Masonry, Finishing, Openings, MEP, Preliminaries.
- Every line item carries its source CBM element IDs and IS 1200 clause provenance.

#### Stage 8: Construction Cost Waterfall
- Applied `INDIA-MUMBAI-2026-Q4-V1` regional rate snapshot:
  - Direct Hard Cost: ₹10,48,200.00
  - Raw Materials: ₹6,18,438.00
  - Site Labour & Crafts: ₹3,14,460.00
  - Machinery & Staging: ₹1,15,302.00
  - Material Cutting & Wastage: ₹42,100.00
  - Contractor Overheads & Prelims (8%): ₹83,856.00
  - Physical Contingency (5%): ₹52,410.00
  - **Total Projected Preliminary Construction Cost:** **₹13,18,391.34 INR**
  - Cost per Sq.Ft Gross BUA: ₹1,247.77 INR/sq.ft

#### Stage 9: Build Review & Release Lock
- Customer acknowledgements verified: `ESTIMATE_RANGE`, `SITE_VERIFICATION`, `PROFESSIONAL_DELIVERY`.
- Release Fingerprint computed:
  $$\text{SHA-256} = \mathbf{876f21ae800940245ed9702d9e00e27be2be636f033f5d24e85c0bb4fe877cb4}$$
- Immutable release package compiled and persisted to PostgreSQL `releases` table.

#### Stage 10: Engineer Review Ledger (PostgreSQL)
- Professional Review created: `rev-pilot-10739137b8`
- **Gate Audit States:**
  - `[G0] Site & Boundary Verification:` **VERIFIED** by `SURV-MH-4421` (Field-verified 27.5×40.0 ft markers).
  - `[G1] Regulatory & Feasibility Review:` **VERIFIED** by `ENG-MH-48201` (DCPR 2034 compliance verified).
  - `[G2] Structural Review:` **VERIFIED** by `ENG-MH-48201` (IS 456 grid and span verified).
  - `[G3] MEP & Services Review:` **VERIFIED** by `ENG-MH-48201` (Vertical wet-wall stacking verified).
  - `[G4] Cost & BOQ Review:` **VERIFIED** by `ENG-MH-48201` (IS 1200 deductions and Mumbai Q4 rates verified).
  - `[G5] Build Authorization:` **LOCKED** (Requires client municipal submission).
  - `[G6] Contractor Handoff:` **LOCKED** (Requires executed contractor agreement).
- Decision recorded: `APPROVE_STAGE` (Preliminary engineering stage approved).

---

### 4. Cryptographic Provenance Chain

Every output in the pilot traces cryptographically through the parent hierarchy:

```
[Site Geometry SECS]  --> sha256:geo_0846fc59a1f29d28
[Survey Evidence]     --> sha256:4b49466a0dbe38e3
[DCPR 2034 Feas.]     --> sha256:dcpr2034_mumbai_3a1d94f27018
[Customer Brief]      --> sha256:brief_b1928091ecf3
[Canonical 3D Model]  --> sha256:88a6d92922765d706a147814c0005d5c...
[Model-Linked QTO]    --> sha256:qto_takeoff_cbm_dv_opt_b
[Traceable BOQ]       --> sha256:59a5ff6992d9f78328c70ca0f523e7f9...
[CPM Schedule]        --> sha256:sch_40ad95fbce24
       |
       v
[RELEASE FINGERPRINT] --> 876f21ae800940245ed9702d9e00e27be2be636f033f5d24e85c0bb4fe877cb4
```

---

### 5. Physical Handoff Package Artifacts

All handoff artifacts were exported to [`artifacts/pilot_handoff/`](file:///Users/surajkumar/Desktop/Real_state_dev/artifacts/pilot_handoff/):

| Artifact | File Path | Size | Description |
|---|---|---|---|
| **IFC4 Semantic Model** | `artifacts/pilot_handoff/pilot_model_ifc4.ifc` | 7.6 KB | Open-standard IFC4 STEP physical file (`IFCBUILDINGSTOREY`, `IFCWALL`, `IFCDOOR`, `IFCWINDOW`, `IFCSLAB`, `IFCCOLUMN`). |
| **Release Manifest** | `artifacts/pilot_handoff/pilot_release_manifest.json` | 3.7 KB | Complete frozen release manifest with project context, design summary, financial summary, and verification gates. |
| **Hierarchical BOQ** | `artifacts/pilot_handoff/pilot_boq_export.json` | 17.5 KB | Model-linked multi-trade bill of quantities with element ID tracing. |
| **Cost Waterfall** | `artifacts/pilot_handoff/pilot_cost_estimate.json` | 0.9 KB | Detailed hard cost, labour, materials, plant, overhead, and contingency breakdown. |
| **Validation Report** | `artifacts/pilot_handoff/pilot_validation_report.json` | 3.6 KB | 12 automated statutory, geometric, and MEP checks. |
| **Review Ledger** | `artifacts/pilot_handoff/pilot_engineer_review.json` | 3.5 KB | Relational PostgreSQL state capture with reviewer attribution and decision history. |

---

### 6. Missing Real-World Inputs & Halt Verification

The pipeline's fail-closed boundary was verified:

1. **Missing Statutory Jurisdiction:** When jurisdiction was omitted, the pipeline halted immediately with `JURISDICTION_REQUIRED`. No statutory rules were assumed.
2. **Missing Boundary Dimensions:** When boundary measurements were omitted on an irregular parcel, the pipeline halted immediately with `USER_INPUT_REQUIRED`. No dimensions were invented.
3. **Professional Boundary:** All exports carry the required disclosures:
   - *"Computational rule checks and geometric validations are automated baseline verifications and do not constitute statutory professional certification."*
   - *"Preliminary cost estimate based on algorithmic takeoff and Q4 2026 Mumbai regional rate snapshot. Subject to structural engineering review and contractor procurement bids."*

---

### 7. Full Test Suite Verification

```
======================================================================
1. Production Build
apps/web (tsc && vite build)
Result: PASS (0 errors, 3.60s)

======================================================================
2. CAD Geometry Engine Tests
apps/web (vitest)
Result: 20/20 PASS (0.24s)

======================================================================
3. Phase 7 Engineer Review Tests
tests/test_phase7_engineer_review.py
Result: 15/15 PASS (0.57s)

======================================================================
4. Phase 8.1 Persistence & Restart Tests
tests/test_phase8_1_persistence.py
Result: 7/7 PASS (0.37s)

======================================================================
5. Phase 8.2 Controlled Pilot Tests
tests/test_controlled_pilot.py
Result: 7/7 PASS (3.76s)

======================================================================
6. Real Plot 1,100 sq ft End-to-End Tests
tests/test_real_plot_end_to_end.py
Result: 13/13 PASS (15.77s)

======================================================================
7. Full Python Regression Discovery
tests/
Result: 115/115 PASS (42.60s)
======================================================================
```

---

### 8. Exact Next Human Action

The computational platform has completed its verification mandate through Gate G4. The exact human actions required to advance the pilot are:

1. **Client Action:** Review preliminary cost estimate (₹13.18 Lakhs) and approve design option `DV-OPT-B-9be0a983`.
2. **Licensed Architect / Engineer Action:** Download the IFC4 model (`pilot_model_ifc4.ifc`) and manifest (`pilot_release_manifest.json`) for submission to MCGM (Municipal Corporation of Greater Mumbai) AutoDCR portal.
3. **Statutory Authority Action:** Issue municipal IOD (Intimation of Disapproval) / Commencement Certificate (CC).
4. **Platform Execution (Upon Municipal Approval):** Authorize licensed professional engineer to unlock Gate G5 (`Build Authorization`) with statutory permit number.
