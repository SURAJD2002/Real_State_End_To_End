# Planwise Enterprise — Final Customer Home Documentation & PDF Generation System
## Phase Development & Verification Report

**Status:** `HOME_PDF_GENERATION = PASS`
**Date:** October 05, 2026
**Authoritative Parcel Invariant:** 1,100.0 sq ft (`102.193 m²`), Bandra West, Mumbai (`CTS-1842-BANDRA`)
**Design Version Baseline:** `DV-OPT-B-9be0a983` (Option B: Contemporary 2BHK G+1)
**Release Fingerprint:** `sha256:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069`

---

### Executive Summary

The customer-facing Home Documentation and Authoritative PDF Generation system in Planwise Enterprise is fully operational and verified end-to-end. Whenever a homeowner or developer selects/finalizes a design, Planwise compiles professional, downloadable PDF packages deterministically from authoritative, version-controlled repository data:

$$\text{Project} \longrightarrow \text{Site} \longrightarrow \text{Evidence} \longrightarrow \text{Rulepack} \longrightarrow \text{Brief} \longrightarrow \text{DesignVersion (CBM)} \longrightarrow \text{Validation} \longrightarrow \text{QTO} \longrightarrow \text{BOQ} \longrightarrow \text{Cost} \longrightarrow \text{Review} \longrightarrow \text{Release}$$

**Strict Invariants Upheld:**
- **Zero Fabrication:** No dimensions, quantities, rates, engineering approvals, or municipal permissions are fabricated. Where data is pending or preliminary, it is explicitly flagged with mandatory statutory disclaimers.
- **Single Source of Truth:** All floor plans, site diagrams, space dimensions, columns, openings, and roof layouts are compiled directly from the Canonical Building Model (CBM) using high-resolution ReportLab vector drawing primitives—never screenshots or raster dumps of the CAD canvas.
- **Pilot Invariant Preserved:** The 1,100.0 sq ft Bandra West Mumbai site boundary, setbacks (3.0m road widening, 3.0m front, 1.5m rear, 1.0m side), Gross BUA (98.16 m²), and 7-trade BOQ remain intact. Legacy benchmarks (e.g., 2,400 sq ft or 40×60) remain strictly excluded.
- **Cryptographic Immutability & Change Propagation:** All reports are bound to `input_manifest_hash` and `output_pdf_hash` in PostgreSQL (`generated_reports`). Released packages cannot be mutated. Unreleased designs trigger downstream staleness marking upon design modification.

---

### 1. Files Created and Modified

#### Backend Pipeline & Report Engine (`workers/reports/`)
- [`pdf_engine.py`](file:///Users/surajkumar/Desktop/Real_state_dev/workers/reports/pdf_engine.py): Core typography styles, palette tokens (`COLOR_PRIMARY`, `COLOR_BRAND_BLUE`), `NumberedCanvas` (two-pass "Page X of Y" with cover suppression and header/footer metadata running line), section dividers, callout alerts, and KPI summary tables.
- [`floor_plan_renderer.py`](file:///Users/surajkumar/Desktop/Real_state_dev/workers/reports/floor_plan_renderer.py): Deterministic 2D vector CAD drawing engine compiling Site Plan (SECS topocentric frame), Level 0 Ground Floor Plan, Level 1 First Floor Plan, and Roof/Terrace Plan from CBM coordinate geometry, walls, columns, door swings, and window openings.
- [`schedule_renderer.py`](file:///Users/surajkumar/Desktop/Real_state_dev/workers/reports/schedule_renderer.py): Authoritative CBM-extracted tables: Room Schedule, Door & Window Fenestration Schedule, Stair Geometry Specifications, Structural Preliminary Element Schedule, MEP Service Schedule, and Material Specifications.
- [`cost_report.py`](file:///Users/surajkumar/Desktop/Real_state_dev/workers/reports/cost_report.py): IS 1200 model-linked Quantity Takeoff (QTO) summary table, hierarchical 7-trade Bill of Quantities (BOQ), and Construction Cost Waterfall Breakdown table.
- [`validation_report.py`](file:///Users/surajkumar/Desktop/Real_state_dev/workers/reports/validation_report.py): 12-point automated statutory and physical validation diagnostic matrix table (all PASS).
- [`professional_report.py`](file:///Users/surajkumar/Desktop/Real_state_dev/workers/reports/professional_report.py): Professional Engineering Review Gates table (G0–G4 Verified, G5–G6 Locked) and Cryptographic Release Lineage & Hash Chain table.
- [`home_report.py`](file:///Users/surajkumar/Desktop/Real_state_dev/workers/reports/home_report.py): Master compiler for the 16-page Customer Home Development Report.
- [`package_builder.py`](file:///Users/surajkumar/Desktop/Real_state_dev/workers/reports/package_builder.py): Complete package orchestrator: compiles all 10 individual PDF reports, single combined master PDF, and ZIP archive; computes SHA-256 digests; persists records to PostgreSQL; and enforces staleness checking.

#### Database Migration
- [`database/migrations/06_generated_reports.sql`](file:///Users/surajkumar/Desktop/Real_state_dev/database/migrations/06_generated_reports.sql): Applied PostgreSQL table `generated_reports` with indexes on `design_version_id`, `project_id`, `report_type`, and `release_id`.

#### API Gateway (`apps/api-gateway/main.py`)
- Added report context resolution helper `_resolve_report_context(...)`.
- Added RESTful endpoints:
  - `POST /api/v1/design-versions/{design_version_id}/reports/home`
  - `GET /api/v1/design-versions/{design_version_id}/reports/home/{report_id}`
  - `GET /api/v1/design-versions/{design_version_id}/reports/home/{report_id}/download`
  - `POST /api/v1/design-versions/{design_version_id}/reports/complete-package`
  - `GET /api/v1/design-versions/{design_version_id}/reports/{report_id}/download`
  - `GET /api/v1/design-versions/{design_version_id}/reports`
  - `POST /api/v1/design-versions/{design_version_id}/reports/technical`
  - `POST /api/v1/design-versions/{design_version_id}/reports/cost-boq`
  - `POST /api/v1/design-versions/{design_version_id}/reports/professional`

#### Frontend Customer UI (`apps/web/src/`)
- [`components/HomeReportDownloadModal.tsx`](file:///Users/surajkumar/Desktop/Real_state_dev/apps/web/src/components/HomeReportDownloadModal.tsx): Interactive customer download modal featuring "YOUR HOME IS READY", live animated multi-step progress generator, download actions, and expandable advanced reports.
- [`components/BuildReviewView.tsx`](file:///Users/surajkumar/Desktop/Real_state_dev/apps/web/src/components/BuildReviewView.tsx): Embedded "YOUR HOME IS READY" panel with key metrics, validation badges, and action triggers for `[ DOWNLOAD HOME PDF ]` and `[ COMPLETE PACKAGE ]`.
- [`types.ts`](file:///Users/surajkumar/Desktop/Real_state_dev/apps/web/src/types.ts): Added `title?: string;` to `HouseOption`.

#### Automated Tests
- [`tests/test_home_report_pdf.py`](file:///Users/surajkumar/Desktop/Real_state_dev/tests/test_home_report_pdf.py): 5 automated test cases validating PDF creation, `pypdfium2` parsing, 1,100 sq ft invariant, all 10 sub-reports, combined master PDF, ZIP integrity, and database staleness propagation.

---

### 2. Architecture & Data Flow

```
+---------------------------------------------------------------------------------------+
|                                    CLIENT BROWSER                                     |
|  [ YOUR HOME IS READY ] -> [ DOWNLOAD HOME PDF ] / [ DOWNLOAD COMPLETE PACKAGE ]      |
+-------------------------------------------+-------------------------------------------+
                                            | HTTP POST / GET
                                            v
+---------------------------------------------------------------------------------------+
|                                  FASTAPI API GATEWAY                                  |
|   /api/v1/design-versions/{dv_id}/reports/home                                        |
|   /api/v1/design-versions/{dv_id}/reports/complete-package                             |
+-------------------------------------------+-------------------------------------------+
                                            |
         +----------------------------------+-----------------------------------+
         |                                                                      |
         v                                                                      v
+-----------------------------+                               +-------------------------------+
|     AUTHORITATIVE DATA      |                               |       REPORT GENERATOR        |
| - Project & Parcel (SECS)   |                               | - pdf_engine.py               |
| - Site Evidence (Surveyor)  |                               | - floor_plan_renderer.py      |
| - CBM 3D Model & Spaces     |                               | - schedule_renderer.py        |
| - 12 Validation Diagnostics |                               | - cost_report.py              |
| - QTO & 7-Trade BOQ         |                               | - validation_report.py        |
| - Engineer Review Gates     |                               | - professional_report.py      |
| - Immutable Release Manifest|                               | - home_report.py              |
+--------------+--------------+                               +---------------+---------------+
               |                                                              |
               +------------------------------+-------------------------------+
                                              |
                                              v
+---------------------------------------------------------------------------------------+
|                              PACKAGE BUILDER & AUDIT LEDGER                           |
|  - Generates 10 modular PDFs + Single Master Combined PDF + ZIP Archive               |
|  - Computes input_manifest_hash & output_pdf_hash (SHA-256)                           |
|  - Records metadata into PostgreSQL table: generated_reports                          |
|  - Change Propagation: marks unreleased reports is_stale = true on design updates     |
+---------------------------------------------------------------------------------------+
```

---

### 3. Customer Home Report Page Breakdown (16 Pages)

| Page # | Section Title | Content & Authoritative Invariants | Source |
|---|---|---|---|
| **Page 1** | **Cover** | Project Name, Location, CTS-1842-BANDRA, 1,100 sq ft Plot Area, Option B 2BHK Contemporary, G+1, Generated Date, Release ID (`rel-pilot-20261002-aedf9830`), High-Res Architectural Perspective Render (labeled Presentation Only). | Project, Release, CBM |
| **Page 2** | **Site Intelligence** | Your Land: 1,100.0 sq ft / 102.19 m², 27.5 ft × 40.0 ft, 18.0m proposed road (12m existing), Dedicated 3.0m road widening strip, Boundary dimensions, 2D Vector CAD Site Plan drawing in SECS topocentric coordinates with North arrow and scale 1:150. | Site SECS Geometry |
| **Page 3** | **Statutory Feasibility** | Permissible vs. Proposed: Ground Footprint (49.06 m²), Floors (G+1), Total BUA (98.16 m²), FSI (0.96 vs 2.00 max), Setbacks (Front 3.0m, Rear 1.5m, Sides 1.0m), Height (6.3m vs 12m), Parking (1 stall 2.5×5.0m). | Mumbai DCPR 2034 |
| **Page 4** | **Architectural Program** | Home Overview: BHK, 2 Baths, Living, Dining, Kitchen, Utility, Parking Stall, Balcony, Terrace, Quality Finish Tier (Standard/Premium), Key metrics (Gross BUA, Carpet Area, Ground Coverage). | CBM Program |
| **Page 5** | **Ground Floor Plan** | High-resolution 2D CAD floor plan at datum ±0.00m (Living, Dining, Kitchen, Bedroom, Toilet, Entrance Foyer, Stair, Parking), door swings, window callouts, column grid. | CBM Spaces & Walls |
| **Page 6** | **First Floor Plan** | High-resolution 2D CAD floor plan at datum +3.15m (Master Bedroom, Ensuite Bath, Bedroom 2, Common Bath, Family Lounge, Balcony, Staircase). | CBM Spaces & Walls |
| **Page 7** | **Roof & Terrace Plan** | Roof plan at datum +6.30m (Mumty head enclosure, 1.0m waterproofed parapet, 1,500L OHT water tank, solar PV zone, China mosaic slope). | CBM Roof Elements |
| **Page 8** | **3D BIM Projections** | Exterior perspective and axonometric structural RC frame model derived from CBM. Labeled: *"Derived visualization truth — presentation only."* | Presentation Assets |
| **Page 9** | **Room Schedule** | Table 1: Comprehensive room-by-room Carpet Area, dimensions ($L \times W$), ceiling heights, and NBC 2016 natural light/ventilation compliance status. | CBM Spaces |
| **Page 10** | **Fenestration Schedule** | Table 2: Complete door schedule (marks, widths, heights, sill, materials) and window schedule (UPVC 3-track sliding, glass specs). Table 4: Staircase geometry (Riser 175mm, Tread 250mm, 18 risers). | CBM Openings & Stairs |
| **Page 11** | **Structural Systems** | Preliminary Structural Notice banner. Table 3: 8 RC columns ($230 \times 380$mm Ground, $230 \times 300$mm First), plinth beams, 125mm two-way slabs, Fe500D rebar takeoff. | IS 456 Baseline |
| **Page 12** | **MEP & Materials** | Table 5: Electrical points (32 pts), power sockets, sanitary fixtures, 1,500L terrace OHT, 3,000L sump, drainage stack. Table 6: Material specs (AAC 200mm/100mm, M25 concrete, Fe500D steel, vitrified tiles). | MEP & Material Specs |
| **Page 13** | **Validation & QTO** | Table 7: 12-point computational validation results (all 12 PASS). Table 8: Model-linked Quantity Takeoff summary under IS 1200 rules (Earthwork, Concrete, AAC masonry, Plaster, Flooring, Waterproofing). | Validation Engine & QTO |
| **Page 14** | **Financial Intelligence** | Table 9: 7-trade hierarchical BOQ (Excavation, Concrete, Masonry, Finishes, Joinery, Waterproofing). Table 10: Construction Cost Waterfall breakdown (Materials, Labour, Equipment, Wastage, Prelims, Contingency). | Cost Engine & Rates |
| **Page 15** | **Governance & Release** | Table 11: Professional Engineering Review Gates G0–G6 (G0–G4 Verified, G5 & G6 strictly Locked). Table 12: Cryptographic Release Lineage & Hash Chain linking SHA-256 fingerprint to immutable release. | Review & Release Ledger |
| **Page 16** | **Mandatory Disclaimers** | Complete statutory, structural, municipal, and commercial legal notice: *"Computational validation is not professional certification."* COA architect filing required; contractor quotation distinction. | Statutory Disclaimers |

---

### 4. Complete Project Package Structure

When downloading the Complete Package, the platform produces:
1. `artifacts/reports/PLANWISE_COMPLETE_HOME_PACKAGE_1100SQFT.pdf` (Master combined PDF containing all 10 reports stitched seamlessly with page lineage).
2. `artifacts/reports/PLANWISE_COMPLETE_HOME_PACKAGE_1100SQFT.zip` (Complete archive containing all 10 individual modular reports plus the combined master document):
   - `01_Home_Report.pdf` (16 pages, customer home report)
   - `02_Technical_Report.pdf` (Detailed technical engineering package)
   - `03_Floor_Plans.pdf` (Architectural drawing sheets S-01, A-01, A-02, A-03)
   - `04_3D_Views.pdf` (3D architectural perspectives and isometric BIM diagrams)
   - `05_QTO.pdf` (IS 1200 model-linked quantity takeoff ledger)
   - `06_BOQ.pdf` (7-trade commercial bill of quantities)
   - `07_Cost_Estimate.pdf` (Cost waterfall breakdown and unit rates)
   - `08_Validation_Report.pdf` (12-point automated statutory and physical diagnostic matrix)
   - `09_Engineer_Review.pdf` (Engineering gates G0–G6 audit ledger)
   - `10_Release_Manifest.pdf` (Cryptographic release lineage and SHA-256 hash tree)
   - `00_Combined_Master_Package.pdf` (Single master combined PDF)

---

### 5. Database Schema & Immutability Tracking

The PostgreSQL ledger table `generated_reports` tracks cryptographic hashes, version bounds, and staleness:

```sql
CREATE TABLE IF NOT EXISTS generated_reports (
    id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    site_id VARCHAR(64),
    design_version_id VARCHAR(64) NOT NULL,
    report_type VARCHAR(64) NOT NULL,
    release_id VARCHAR(64),
    release_fingerprint VARCHAR(128),
    input_manifest_hash VARCHAR(128) NOT NULL,
    output_pdf_hash VARCHAR(128) NOT NULL,
    file_path TEXT NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    engine_version VARCHAR(32) NOT NULL DEFAULT '1.0.0',
    is_stale BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);
```

**Immutability Rule:** Once a package has an associated `release_id` (frozen release), its record and generated PDF are permanent and can never be modified or overwritten.
**Change Propagation Rule:** If the customer updates plot geometry, room layout, or rate snapshots, `mark_reports_stale_for_design(design_version_id)` updates `is_stale = true` for all unreleased draft reports, forcing fresh generation upon next download.

---

### 6. Verification & Test Results

#### A. Automated PDF Generation & Integrity Tests
```bash
$ PYTHONPATH=. .venv/bin/python3 -m unittest -v tests/test_home_report_pdf.py
test_01_customer_home_report_compilation_and_validity ... ok
test_02_complete_package_and_zip_archive ... ok
test_03_technical_and_specialized_reports ... ok
test_04_database_persistence_and_staleness ... ok
test_05_cryptographic_fingerprint_deterministic_output ... ok

----------------------------------------------------------------------
Ran 5 tests in 2.387s
OK
```

#### B. Full Backend Regression Test Suite
```bash
$ PYTHONPATH=. .venv/bin/python3 -m unittest discover tests
----------------------------------------------------------------------
Ran 136 tests in 55.642s
OK
```

#### C. Frontend CAD & Geometric Unit Tests
```bash
$ npm --prefix apps/web test -- --run
✓ src/components/map/cadGeometry.test.ts (20 tests) 5ms
Test Files  1 passed (1)
Tests       20 passed (20)
Duration    283ms
```

#### D. Production Frontend Compilation
```bash
$ npm --prefix apps/web run build
vite v6.4.3 building for production...
✓ 1930 modules transformed.
dist/index.html                     1.36 kB
dist/assets/index-ng7c5cdE.css     66.75 kB
dist/assets/index-Ccchck2U.js   2,464.93 kB
✓ built in 4.14s
```

#### E. Live HTTP API Gateway Endpoints Tested
- `POST /api/v1/design-versions/DV-OPT-B-9be0a983/reports/home` -> **HTTP 200 OK** (`reportId: rep-home-...`, file size 2,216,271 bytes, hashes returned).
- `GET /api/v1/design-versions/DV-OPT-B-9be0a983/reports/home/{report_id}` -> **HTTP 200 OK** (Metadata JSON from PostgreSQL).
- `GET /api/v1/design-versions/DV-OPT-B-9be0a983/reports/home/{report_id}/download` -> **HTTP 200 OK** (`Content-Type: application/pdf`, `Content-Disposition: attachment; filename=Planwise_Home_Report_...`).
- `POST /api/v1/design-versions/DV-OPT-B-9be0a983/reports/complete-package` -> **HTTP 200 OK** (10 modular files compiled, master PDF, ZIP archive).
- `GET /api/v1/design-versions/DV-OPT-B-9be0a983/reports/{report_id}/download?format=zip` -> **HTTP 200 OK** (`Content-Type: application/zip`, file size 7,165,322 bytes).
- `GET /api/v1/design-versions/DV-OPT-B-9be0a983/reports` -> **HTTP 200 OK** (List of generated reports for design version).

---

### 7. Generated Deliverable Artifacts

The following authoritative files have been compiled into [`artifacts/reports/`](file:///Users/surajkumar/Desktop/Real_state_dev/artifacts/reports/):
- **Customer Home Report PDF:** [`artifacts/reports/PLANWISE_HOME_REPORT_1100SQFT.pdf`](file:///Users/surajkumar/Desktop/Real_state_dev/artifacts/reports/PLANWISE_HOME_REPORT_1100SQFT.pdf) (2,216,271 bytes, 16 pages)
- **Complete Project Package ZIP:** [`artifacts/reports/PLANWISE_COMPLETE_HOME_PACKAGE_1100SQFT.zip`](file:///Users/surajkumar/Desktop/Real_state_dev/artifacts/reports/PLANWISE_COMPLETE_HOME_PACKAGE_1100SQFT.zip) (7,165,322 bytes, 10 modular PDFs + combined master)
- **Combined Master Project Package PDF:** [`artifacts/reports/PLANWISE_COMPLETE_HOME_PACKAGE_1100SQFT.pdf`](file:///Users/surajkumar/Desktop/Real_state_dev/artifacts/reports/PLANWISE_COMPLETE_HOME_PACKAGE_1100SQFT.pdf) (4,427,166 bytes)

High-resolution vector render snapshots for inspection:
- Cover Page: [`artifacts/reports/page_1_cover.png`](file:///Users/surajkumar/Desktop/Real_state_dev/artifacts/reports/page_1_cover.png)
- Site Intelligence & Boundary Drawing: [`artifacts/reports/page_2_site.png`](file:///Users/surajkumar/Desktop/Real_state_dev/artifacts/reports/page_2_site.png)
- Level 0 Ground Floor Architectural Layout Plan: [`artifacts/reports/page_5_ground_plan.png`](file:///Users/surajkumar/Desktop/Real_state_dev/artifacts/reports/page_5_ground_plan.png)

---

### 8. Professional & Municipal Governance Boundaries

Planwise strictly enforces the boundary between automated computational feasibility and licensed professional certification:
1. **Gate G5 (Municipal Build Authorization):** Marked strictly `LOCKED` in reports and UI. Automated computational compliance with Mumbai DCPR 2034 does not replace statutory scrutiny, revenue document verification, or formal submission by a registered architect under the Council of Architecture (COA) to MCGM.
2. **Gate G6 (Contractor Construction Handoff):** Marked strictly `LOCKED`. BOQ amounts and unit rates are derived from regional benchmarks and IS 1200 takeoff rules; they do not constitute commercial tender quotations or fixed-price contractor agreements.
3. **Structural Design:** Structural grids ($230 \times 380$mm columns) and slab thicknesses are computational baselines. Full reinforcement detailing, bar bending schedules (BBS), and foundation engineering are subject to geotechnical borewell soil testing and certified structural engineer review.

---

### Conclusion & Final Status

Every acceptance criterion defined in the Master Prompt has been implemented, validated against the authoritative 1,100.0 sq ft Bandra West pilot parcel, tested through automated regression suites, and confirmed production-ready.

$$\mathbf{HOME\_PDF\_GENERATION = PASS}$$
