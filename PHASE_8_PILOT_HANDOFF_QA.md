# PLANWISE ENTERPRISE — PHASE 8 PILOT HANDOFF PACKAGE QA
## Comprehensive Quality Assurance & Forensic Integrity Audit

**Audit Date:** October 2, 2026  
**QA Engine:** Planwise Enterprise Static & Relational Verification Suite  
**Audit Target:** `artifacts/pilot_handoff/`  
**Target Project ID:** `proj-mumbai-real-1100`  
**Target Release ID:** `rel-pilot-20261002-aedf9830`  
**Target Design Version ID:** `DV-OPT-B-9be0a983`  
**Final QA Verdict:** **`HANDOFF_PACKAGE_BLOCKED`**

---

### Executive Summary

An exhaustive, non-destructive quality assurance audit was conducted on the physical pilot handoff package located in [`artifacts/pilot_handoff/`](file:///Users/surajkumar/Desktop/Real_state_dev/artifacts/pilot_handoff/). 

The audit evaluated 11 explicit verification criteria spanning IFC4 syntactic validity, spatial/physical entity completeness, release manifest binding, CBM element traceability, financial waterfall coherence, validation report alignment, PostgreSQL ledger persistence parity, cryptographic fingerprint consistency, benchmark contamination prevention, gate lock status (G5/G6), and mandatory professional handoff safety disclaimers.

**Key Finding:**  
While individual components exhibit valid syntax, proper engineering logic, and adherence to physical constraints (e.g. 100% valid CBM element mapping, zero benchmark contamination, and strict G5/G6 lock enforcement), the handoff package in `artifacts/pilot_handoff/` is **`BLOCKED`** due to critical release identification drift (ephemeral test execution overwriting target release artifacts), missing metadata fields in the release manifest, artifact manifest file naming/hash divergence, and unstated top-level handoff disclaimers.

---

### Detailed Verification Matrix (Items 1 – 11)

| Item | Requirement Description | Verification Method | Status | Findings / Discrepancy Summary |
|---|---|---|---|---|
| **1** | **IFC4 STEP Syntactic Validity** | Lexer parsing of ISO-10303-21 header, data block, and delimiter formatting | **PASS** | Valid STEP physical file format. Proper `HEADER;`, `FILE_DESCRIPTION`, `FILE_SCHEMA(('IFC4'))`, `DATA;`, entity structure `#<id>=ENTITY(...)`, and `END-ISO-10303-21;`. Zero syntax errors. |
| **2** | **IFC Spatial & Physical Entity Coverage** | Entity extraction (`IFCPROJECT`, `IFCSITE`, `IFCBUILDING`, `IFCBUILDINGSTOREY`, `IFCWALL`, `IFCDOOR`, `IFCWINDOW`, `IFCSLAB`, `IFCCOLUMN`, `IFCSPACE`) | **PASS** | All 10 expected entity types present: 1 Project, 1 Site, 1 Building, 3 Storeys (Ground, First, Terrace), 12 Walls, 13 Doors, 7 Windows, 3 Slabs, 4 Columns, 12 Spaces. |
| **3** | **Release Manifest Field & Identity Matching** | JSON schema & field-by-field parity check against target release `rel-pilot-20261002-aedf9830` | **FAIL (BLOCKED)** | `handoffPackageId` mismatch (actual: `pkg-rel-pilot-20261002-81c3abbd`); `releaseFingerprint` mismatch; `projectId` missing; `designVersionId` missing; `declaredPlotAreaSqFt` (1,100 sq ft) unstated; BOQ hash mismatch. |
| **4** | **BOQ CBM Element ID Traceability** | Validation of all 54 `sourceElementIds` against Canonical Building Model entities | **PASS** | 100% of referenced elements (`COL-*`, `SLAB-*`, `STAIR-001`, `WALL-*`, `DOOR-*`, `WIN-*`, `SPACE-*`, `SYS-ELEC-01`, `SYS-PLUMB-01`) correspond to valid CBM entities. |
| **5** | **Cost Estimate Waterfall vs BOQ & Manifest** | Mathematical cross-verification of direct hard costs, trade line totals, and manifest financial summary | **PASS** | Sum of BOQ line items (₹11,66,718.00) matches cost estimate `grossHardCost` exactly. Total cost (₹13,18,391.34) matches manifest `baseEstimate`. Unit cost (₹1,247.79/sq ft) matches across files. |
| **6** | **Validation Report vs Released Design Version** | Cross-reference of `designVersionId` and `modelHash` | **FAIL (BLOCKED)** | `designVersionId` in report is `DV-OPT-B-a7e0f279` instead of target `DV-OPT-B-9be0a983`. Hash does not match target release compiled model hash. |
| **7** | **Engineer Review JSON vs PostgreSQL Review State** | SQL comparison between `pilot_engineer_review.json` and PostgreSQL `realestate_feasibility` ledger | **FAIL (BLOCKED)** | The JSON file captures an ephemeral test review (`rev-pilot-0327c0111c` / `rel-pilot-20261002-81c3abbd`) rather than the target release review (`rev-pilot-10739137b8` / `rel-pilot-20261002-aedf9830`). Although internal fields match that ephemeral DB row, it is the wrong release review. |
| **8** | **Internal Artifact Hashes & Fingerprints Consistency** | SHA-256 calculation of physical files vs `artifactManifest` in `pilot_release_manifest.json` | **FAIL (BLOCKED)** | `artifactManifest` lists obsolete filenames (`Traceable_Bill_Of_Quantities.csv`, `BIM_IFC4_Coordinated_Model.ifc`) with mismatched hashes. The actual files (`pilot_boq_export.json`, `pilot_model_ifc4.ifc`, etc.) are not listed with their real SHA-256 digests. |
| **9** | **Benchmark Contamination Prevention** | Forensic token search for old benchmark values (`2400`, `2,400`, `40x60`, `40×60`, `10000`, `10,000`) | **PASS** | Zero benchmark contamination found across all 6 files. Authoritative 1,100 sq ft plot metrics strictly maintained. |
| **10** | **G5 & G6 Gate Lock Verification** | Inspection of gates G5 (`Build Authorization`) and G6 (`Contractor Handoff`) across JSON and PostgreSQL | **PASS** | G5 and G6 are strictly **LOCKED** / `AWAITING_PREREQUISITE` in all files and PostgreSQL records. Commercial and site execution boundaries remain fully enforced. |
| **11** | **Mandatory Safety Statements & Disclaimers** | Semantic and string search for the 4 required legal notices | **PARTIAL / FAIL** | `pilot_validation_report.json` and `pilot_cost_estimate.json` contain partial disclaimer statements, but `pilot_release_manifest.json` completely lacks top-level explicit notices for statutory municipal approval and construction authorization. |

---

### Discrepancy Register

The following register details every discrepancy detected during audit. In accordance with audit directives, none have been silently modified or repaired.

| ID | File | Exact Field | Expected Value | Actual Value | Severity | Impact Description |
|---|---|---|---|---|---|---|
| **DISC-01** | `pilot_release_manifest.json` | `handoffPackageId` | `"pkg-rel-pilot-20261002-aedf9830"` | `"pkg-rel-pilot-20261002-81c3abbd"` | **P0** | Handoff package identifier does not match target release `rel-pilot-20261002-aedf9830`. Caused by test runner re-execution overwriting artifacts. |
| **DISC-02** | `pilot_release_manifest.json` | `releaseFingerprint` | `"876f21ae800940245ed9702d9e00e27be2be636f033f5d24e85c0bb4fe877cb4"` | `"a6258a43f8212fb6909f267d456d257669e4f5c49911911c81f2b99ffac6c1f3"` | **P0** | Release cryptographic fingerprint in manifest does not match the immutable hash persisted in PostgreSQL for `rel-pilot-20261002-aedf9830`. |
| **DISC-03** | `pilot_release_manifest.json` | `projectId` (top-level or `projectContext.projectId`) | `"proj-mumbai-real-1100"` | Missing / `None` | **P1** | Release manifest fails to explicitly bind the project identifier `proj-mumbai-real-1100` in its schema. |
| **DISC-04** | `pilot_release_manifest.json` | `designVersionId` | `"DV-OPT-B-9be0a983"` | Missing / `None` | **P0** | Release manifest lacks explicit `designVersionId` binding (only contains general archetype `"m2_cpsat_opt-B"`). |
| **DISC-05** | `pilot_release_manifest.json` | `declaredPlotAreaSqFt` | `1100.0` | Missing / `None` | **P1** | Authoritative 1,100 sq ft plot area invariant is not recorded in `pilot_release_manifest.json`. |
| **DISC-06** | `pilot_release_manifest.json` | `artifactManifest` | Entries matching actual files: `pilot_model_ifc4.ifc`, `pilot_boq_export.json`, `pilot_cost_estimate.json`, `pilot_validation_report.json`, `pilot_engineer_review.json` | Mismatched entries: `2D_Architectural_Floor_Plans.json`, `Traceable_Bill_Of_Quantities.csv`, `Construction_CPM_Precedence_Schedule.json`, `BIM_IFC4_Coordinated_Model.ifc`, `Statutory_Compliance_Report_DCPR2034.pdf` | **P1** | File names and SHA-256 digests in manifest do not reflect the physical contents of `artifacts/pilot_handoff/`. |
| **DISC-07** | `pilot_validation_report.json` | `designVersionId` | `"DV-OPT-B-9be0a983"` | `"DV-OPT-B-a7e0f279"` | **P0** | Validation report is linked to an ephemeral design version instead of the audited candidate `DV-OPT-B-9be0a983`. |
| **DISC-08** | `pilot_validation_report.json` | `modelHash` | `"1786833c53ff394d01b1dfddd8686205abcf5d1f9399a30cc0611e4ba19593fe"` | `"sha256:1f76ddf128ad3554a9b7a200c8f32507a5e7aabf60b9b036274e7198b3c5afdc"` | **P1** | Model hash does not match target release compiled CBM hash in PostgreSQL. |
| **DISC-09** | `pilot_boq_export.json` | `releaseId` | `"rel-pilot-20261002-aedf9830"` | `"rel-pilot-20261002-81c3abbd"` | **P0** | BOQ export binds to an ephemeral test release instead of target release `rel-pilot-20261002-aedf9830`. |
| **DISC-10** | `pilot_boq_export.json` | `designVersionId` | `"DV-OPT-B-9be0a983"` | `"DV-OPT-B-a7e0f279"` | **P0** | BOQ export binds to an ephemeral design version instead of target design `DV-OPT-B-9be0a983`. |
| **DISC-11** | `pilot_cost_estimate.json` | `releaseId` | `"rel-pilot-20261002-aedf9830"` | `"rel-pilot-20261002-81c3abbd"` | **P0** | Cost estimate binds to an ephemeral test release instead of target release `rel-pilot-20261002-aedf9830`. |
| **DISC-12** | `pilot_engineer_review.json` | `id` | `"rev-pilot-10739137b8"` | `"rev-pilot-0327c0111c"` | **P0** | Engineer review JSON artifact contains the ephemeral test review ID rather than the target release review record. |
| **DISC-13** | `pilot_engineer_review.json` | `releaseId` | `"rel-pilot-20261002-aedf9830"` | `"rel-pilot-20261002-81c3abbd"` | **P0** | Engineer review references mismatched release ID. |
| **DISC-14** | `pilot_engineer_review.json` | `designVersionId` | `"DV-OPT-B-9be0a983"` | `"DV-OPT-B-a7e0f279"` | **P0** | Engineer review references mismatched design version ID. |
| **DISC-15** | `pilot_model_ifc4.ifc` | Line 4 `FILE_NAME` | `'rel-pilot-20261002-aedf9830.ifc'` | `'rel-pilot-20261002-81c3abbd.ifc'` | **P1** | IFC4 STEP header references mismatched release filename. |
| **DISC-16** | `pilot_release_manifest.json` | Top-level Disclaimers | Explicit statements: (1) computational validation is not professional certification, (2) preliminary cost is not contractor quotation, (3) municipal approval is pending, (4) construction authorization is pending | None present in `pilot_release_manifest.json` | **P1** | Primary release manifest fails to incorporate mandatory professional handoff disclaimers and statutory notices. |

---

### Root Cause Analysis

1. **Non-Isolated Test Output Directory:**  
   `workers/intake/controlled_pilot_runner.py` defaults its export directory to `artifacts/pilot_handoff/` via `self.output_dir = ROOT_DIR / "artifacts" / "pilot_handoff"`. When unit tests (`tests/test_controlled_pilot.py`) execute, `ControlledPilotRunner.execute_pilot()` is run anew with newly generated UUIDs (`rel-pilot-20261002-81c3abbd`, `DV-OPT-B-a7e0f279`, `rev-pilot-0327c0111c`), overwriting the authoritative pilot package artifacts on disk.
2. **Missing Metadata Fields in Handoff Package Template:**  
   `manifest_engine.py:compile_handoff_package` populates `projectContext` and `designOption`, but omits explicit top-level fields for `projectId`, `designVersionId`, and `declaredPlotAreaSqFt`.
3. **Static Manifest Artifact File Table:**  
   The `artifactManifest` generated in `manifest_engine.py` was authored with generalized file names (`Traceable_Bill_Of_Quantities.csv`, etc.) rather than dynamically hashing the actual files exported to `artifacts/pilot_handoff/`.

---

### File Classification

#### Exact Files Safe to Send to Professional:
**None (0 files)**  
*Reason: No file in `artifacts/pilot_handoff/` currently bears both the target release identifier `rel-pilot-20261002-aedf9830` and design version `DV-OPT-B-9be0a983`. Sending any of these files would introduce release version inconsistency with the PostgreSQL immutable ledger.*

#### Exact Files Requiring Correction:
1. **`artifacts/pilot_handoff/pilot_release_manifest.json`**
   - Correct `handoffPackageId` to `pkg-rel-pilot-20261002-aedf9830`.
   - Add top-level `projectId: "proj-mumbai-real-1100"`.
   - Add `designVersionId: "DV-OPT-B-9be0a983"`.
   - Add `declaredPlotAreaSqFt: 1100.0`.
   - Update `releaseFingerprint` to `876f21ae800940245ed9702d9e00e27be2be636f033f5d24e85c0bb4fe877cb4`.
   - Align `artifactManifest` names and SHA-256 hashes with the physical export files.
   - Include the 4 mandatory professional handoff disclaimers.
2. **`artifacts/pilot_handoff/pilot_validation_report.json`**
   - Correct `designVersionId` from `DV-OPT-B-a7e0f279` to `DV-OPT-B-9be0a983`.
   - Correct `modelHash` to match the target compiled CBM.
3. **`artifacts/pilot_handoff/pilot_boq_export.json`**
   - Correct `releaseId` from `rel-pilot-20261002-81c3abbd` to `rel-pilot-20261002-aedf9830`.
   - Correct `designVersionId` from `DV-OPT-B-a7e0f279` to `DV-OPT-B-9be0a983`.
4. **`artifacts/pilot_handoff/pilot_cost_estimate.json`**
   - Correct `releaseId` from `rel-pilot-20261002-81c3abbd` to `rel-pilot-20261002-aedf9830`.
   - Refine disclaimer to explicitly mention that preliminary cost is not a contractor quotation.
5. **`artifacts/pilot_handoff/pilot_engineer_review.json`**
   - Synchronize with PostgreSQL review record `rev-pilot-10739137b8` (release `rel-pilot-20261002-aedf9830`, design `DV-OPT-B-9be0a983`).
6. **`artifacts/pilot_handoff/pilot_model_ifc4.ifc`**
   - Correct line 4 `FILE_NAME` release file designation to `rel-pilot-20261002-aedf9830.ifc`.

---

### Final Quality Assurance Disposition

$$\mathbf{VERDICT: \quad HANDOFF\_PACKAGE\_BLOCKED}$$

The pilot handoff package exhibits strong underlying computational integrity (complete IFC4 structure, 100% CBM element ID traceability, exact financial reconciliation, zero benchmark contamination, and locked G5/G6 gates). However, because the physical files in `artifacts/pilot_handoff/` diverge in release identification, design versioning, and manifest digest synchronization from the authoritative target release `rel-pilot-20261002-aedf9830`, the package is blocked from release to external professionals until the listed discrepancies are formally reconciled.
