# Planwise Enterprise — Phase 9 Milestone 2: Professional Drawing Pipeline Report

**Status:** `M2_DRAWING_PASS`
**Milestone:** Phase 9 — Milestone 2 (M2)
**Author:** Lead Architectural Drawing Systems Engineer, Planwise Enterprise
**Date:** October 5, 2026
**Authoritative Pilot Baseline:** `proj-mumbai-real-1100` | Release `rel-pilot-20261002-aedf9830` | Design Version `DV-OPT-B-9be0a983`
**Release Fingerprint:** `876f21ae800940245ed9702d9e00e27be2be636f033f5d24e85c0bb4fe877cb4`

---

## 1. Executive Summary

Milestone 2 establishes a fully deterministic, publication-grade architectural drawing compiler for Planwise Enterprise. In strict compliance with the core architectural invariant, the **Canonical Building Model (CBM)** remains the single source of truth: no generative AI hallucinations, no image-to-drawing approximations, and no independent geometries are permitted.

Every line, wall, room polygon, opening tag, dimension witness line, and level datum marker generated across the 9 standard drawing sheets is derived directly and mathematically from the versioned CBM. The drawing compiler emits dual publication formats: standalone, printable ISO 128 **A3 Landscape vector PDFs** (compiled via ReportLab with deterministic document digest seeding) and structured **semantic SVGs** with hierarchical groupings and explicit `data-cbm-id` traceability.

Repeated compilation runs on identical CBM inputs demonstrate **100% byte-for-byte SHA-256 identity** across all 9 PDFs, all 9 SVGs, and the `drawing_manifest.json` file. The authoritative pilot handoff artifacts in `artifacts/pilot_handoff/` remain strictly immutable and untouched.

---

## 2. Existing CBM Input

The compiler consumes the authoritative Canonical Building Model for Option B (`DV-OPT-B-9be0a983`):

- **Levels (3):**
  - `LVL-000`: Ground Floor (`elevationM = 0.000 m`)
  - `LVL-001`: First Floor (`elevationM = 3.150 m`)
  - `LVL-ROOF`: Terrace / Roof (`elevationM = 6.300 m`)
- **Building Envelope:** Width $5.38\text{ m} \times \text{Length } 3.19\text{ m} \times \text{Height } 7.20\text{ m}$
- **Spaces (12):**
  - Ground Floor: Entrance Foyer ($3.60\text{ m}^2$), Living Room ($16.28\text{ m}^2$), Dining Area ($9.60\text{ m}^2$), Modular Kitchen ($6.96\text{ m}^2$), Utility / Yard ($3.04\text{ m}^2$), Puja Room ($2.08\text{ m}^2$), Bedroom 2 ($11.52\text{ m}^2$), Bathroom 2 ($3.60\text{ m}^2$), Staircase Core ($6.72\text{ m}^2$).
  - First Floor: Master Bedroom Suite ($14.04\text{ m}^2$), Master Attached Bath ($3.74\text{ m}^2$), Living Balcony ($4.18\text{ m}^2$).
- **Elements (20+):**
  - External Walls (4): `WALL-EXT-001` through `WALL-EXT-004` (AAC blockwork, $200\text{ mm}$ thickness, centerline coordinates).
  - Internal Partitions (8): `WALL-INT-005` through `WALL-INT-012` ($150\text{ mm}$ thickness).
  - Columns (4): `COL-A1`, `COL-A2`, `COL-B1`, `COL-B2` ($300 \times 450\text{ mm}$ reinforced concrete, spanning plinth to roof).
  - Slabs (3): `SLAB-PLINTH` ($-0.15\text{ m}$), `SLAB-L1` ($+3.00\text{ m}$), `SLAB-ROOF` ($+6.15\text{ m}$).
  - Staircase (1): `STAIR-001` ($U\text{-shape}$, $18$ risers @ $175\text{ mm}$, treads @ $250\text{ mm}$, $1$ intermediate landing).
  - Openings (20): 13 doors (`DOOR-001`..`DOOR-013`) and 7 windows (`WIN-001`..`WIN-007`).
- **Structural Grid:** Grid Lines A ($X=0.0\text{ m}$), B ($X=4.0\text{ m}$), 1 ($Y=0.0\text{ m}$), 2 ($Y=3.19\text{ m}$).

---

## 3. Drawing Compiler Architecture

The compiler is organized into decoupled, modular components:

```
CanonicalBuildingModel (CBM)
  │
  ├──> workers/generation/drawing_styles.py  (Centralized ISO 128 styling tokens)
  │      ├── Sheet Sizes (A3 Landscape: 1190.55 × 841.89 pt)
  │      ├── Line Weights (Cut: 1.42 pt, Major: 0.99 pt, Minor: 0.71 pt, Dim: 0.35 pt)
  │      ├── Color Tokens & Typographic Scale
  │      └── Scale Conversion (1:100 = 28.3465 pt/m)
  │
  ├──> workers/generation/projections.py      (Deterministic orthographic projections)
  │      ├── generate_floor_plan(model, level_id)
  │      ├── generate_elevation(model, facade_direction)
  │      └── generate_section(model, cut_plane, cut_axis)
  │
  └──> workers/generation/drawing_compiler.py (Orchestrator & Serializer)
         ├── ViewportTransformer (Translates metric coordinates to paper points)
         ├── Dimension Engine (Outer envelope, grid bays, room bounds)
         ├── Door & Window Tagging Engine (D01.., W01..)
         ├── Schedule Generator (Door & Window schedules on sheet)
         ├── ISO 7200 / BIS SP 46 Title Block & North Arrow
         ├── SVG Serializer (Semantic <g id="..."> & data-cbm-id tags)
         ├── PDF Serializer (ReportLab vector canvas with deterministic digest)
         └── Manifest Engine (Emits drawing_manifest.json with SHA-256 hashes)
```

---

## 4. Required Drawing Types & Plan Generation

Nine publication sheets are generated:

| Drawing ID | Title | View Type | Level / Cut | Scale | Sheet |
|---|---|---|---|---|---|
| **A-101** | Ground Floor Plan | `PLAN` | `LVL-000` | 1:100 | 1 OF 9 |
| **A-102** | First Floor Plan | `PLAN` | `LVL-001` | 1:100 | 2 OF 9 |
| **A-103** | Terrace / Roof Plan | `ROOF_PLAN` | `LVL-ROOF` | 1:100 | 3 OF 9 |
| **A-201** | Front Elevation (South) | `ELEVATION` | SOUTH | 1:100 | 4 OF 9 |
| **A-202** | Rear Elevation (North) | `ELEVATION` | NORTH | 1:100 | 5 OF 9 |
| **A-203** | Left Elevation (West) | `ELEVATION` | WEST | 1:100 | 6 OF 9 |
| **A-204** | Right Elevation (East) | `ELEVATION` | EAST | 1:100 | 7 OF 9 |
| **A-301** | Longitudinal Section (A-A) | `SECTION` | Axis X ($X=4.0\text{ m}$) | 1:100 | 8 OF 9 |
| **A-302** | Cross Section (B-B) | `SECTION` | Axis Y ($Y=3.19\text{ m}$) | 1:100 | 9 OF 9 |

### Missing Data Protection
If a requested view cannot be projected because the CBM lacks required geometry (e.g. attempting to project a second floor `LVL-002` that does not exist in a single-story archetype), the compiler raises:
```json
{
  "error": "DRAWING_SOURCE_DATA_MISSING",
  "message": "Authoritative CBM lacks required geometry: Level 'LVL-002' not found in Canonical Building Model."
}
```
Geometry is never silently fabricated.

---

## 5. Elevation Generation

Orthographic elevations are projected for all four cardinal directions (South, North, West, East):
- **Ground Line:** Continuous heavy baseline ($0.60\text{ mm} / 1.70\text{ pt}$).
- **Wall Masses:** Rendered with visible outline stroke and subtle architectural fill (`#F1F5F9`).
- **Slab Bands:** Visual slab edges at plinth, first floor, and roof levels.
- **Fenestration:** Window frames in sky blue (`#0284C7`), glazing in light tint (`#E0F2FE`), and exterior doors with door leaf styling.
- **Level Datum Markers:** Red dashed level lines (`#DC2626`) with standardized ISO level annotations:
  - `GROUND (±0.000)`
  - `FIRST (+3.150)`
  - `TERRACE (+6.300)`

---

## 6. Section Generation

Sections cut through the real 3D geometry of the building:
- **Longitudinal Section (A-A):** Plane cut along Axis $X = 4.0\text{ m}$ traversing the living room, staircase core, and master suite.
- **Cross Section (B-B):** Plane cut along Axis $Y = 3.19\text{ m}$ traversing the building transverse width.
- **Cut Elements:** Cut walls are highlighted with deep charcoal architectural cut fill (`#334155`), cut slabs with solid fill (`#1E293B`), and spatial clear heights are annotated (e.g., `CLR HT: 3.15 m`).
- **Level Datums:** Aligned with elevation markers.

---

## 7. Dimension Engine

Dimensions are derived strictly from CBM coordinates in metric meters:
- **Zero Pixel-to-Geometry Inference:** Dimensions are calculated mathematically from coordinate bounds.
- **Precision:** Internal calculations use double-precision floats; display formats display `X.XX m` on dimension strings and clear millimeters (`XXXX mm`) in schedules.
- **Generated Dimension Chains:**
  - Overall Building Footprint Width ($5.38\text{ m}$).
  - Overall Building Footprint Depth ($3.19\text{ m}$).
  - Structural Grid Bay Dimensions (A to B: $4.00\text{ m}$, 1 to 2: $3.19\text{ m}$).
  - Room Clear Width & Depth inside room polygons.
  - Floor-to-floor vertical heights ($3.15\text{ m}$, $3.15\text{ m}$).

---

## 8. Annotation, Tagging & Schedules

- **Room Labels:** Centered in room bounding boxes with uppercase room name and authoritative area:
  ```
  LIVING ROOM
  16.28 m²
  ```
- **Door / Window Tagging:** Openings sorted deterministically by `(hostWallId, positionM)`:
  - Doors: `D01`, `D02`, `D03`...
  - Windows: `W01`, `W02`, `W03`...
  - Placed inside circular tag bubbles ($6\text{ pt}$ radius) near opening positions.
- **Tabular Schedules on Sheet:**
  - **DOOR SCHEDULE:** Tag, Type, Clear Width (mm), Height (mm), Level.
  - **WINDOW SCHEDULE:** Tag, Type, Width (mm), Height (mm), Level.

---

## 9. ISO 128 Standards & Title Block

All styling tokens are centralized in [`workers/generation/drawing_styles.py`](file:///Users/surajkumar/Desktop/Real_state_dev/workers/generation/drawing_styles.py):
- **Line Weight Hierarchy:**
  - `CUT_WALL`: $0.50\text{ mm}$ ($1.42\text{ pt}$)
  - `VISIBLE_MAJOR`: $0.35\text{ mm}$ ($0.99\text{ pt}$)
  - `VISIBLE_MINOR`: $0.25\text{ mm}$ ($0.71\text{ pt}$)
  - `SECONDARY`: $0.18\text{ mm}$ ($0.50\text{ pt}$)
  - `DIMENSION`: $0.13\text{ mm}$ ($0.35\text{ pt}$)
  - `BORDER_HEAVY`: $0.60\text{ mm}$ ($1.70\text{ pt}$)
- **Title Block (ISO 7200 / BIS SP 46):** Located in bottom-right corner ($360 \times 145\text{ pt}$):
  - Company: `PLANWISE ENTERPRISE`
  - Subtitle: `AUTONOMOUS ARCHITECTURAL BIM`
  - Project: `Bandra West Residential Development`
  - Project ID: `proj-mumbai-real-1100`
  - Drawing Title & Drawing Number (e.g. `A-101`)
  - Revision: `R0`
  - Scale: `1:100`
  - Date: `2026-10-02`
  - Sheet: `1 OF 9`
  - Status: `PRELIMINARY / FOR PROFESSIONAL REVIEW`

---

## 10. PDF Generation & Determinism

Standalone A3 landscape printable PDFs ($1190.55 \times 841.89\text{ pt}$) are rendered using ReportLab Canvas:
- **Vector-Only Canvas:** All walls, slabs, windows, dimensions, arrows, and title blocks are drawn using vector primitives (`rect`, `line`, `circle`, `drawPath`, `drawString`). Zero bitmap rasterization.
- **Byte-for-Byte Determinism:** By overriding `c._doc.ID = lambda: (md5_seed, md5_seed)` where `md5_seed` is hashed from `f"{drawingId}:{cbmHash}:{sheetNumber}"`, ReportLab's non-deterministic clock-based timestamps and random document IDs are completely eliminated.
- Compiling the drawing set twice produces **identical SHA-256 hashes**.

---

## 11. SVG Generation & Traceability

Standalone SVGs conform to standard SVG 1.1 with explicit groupings:
```xml
<svg viewBox="0 0 1190.55 841.89" width="1190.55" height="841.89" data-drawing-id="A-101" data-scale="1:100">
  <g id="sheet-border"> ... </g>
  <g id="drawing-viewport">
    <g id="slabs"> ... </g>
    <g id="structural-grid"> ... </g>
    <g id="rooms">
      <rect data-cbm-id="SPACE-SP-LIVING-2" data-element-type="IfcSpace" ... />
    </g>
    <g id="walls">
      <polygon data-cbm-id="WALL-EXT-001" data-element-type="IfcWall" ... />
    </g>
    <g id="columns">
      <rect data-cbm-id="COL-A1" data-element-type="IfcColumn" ... />
    </g>
    <g id="stairs">
      <rect data-cbm-id="STAIR-001" data-element-type="IfcStair" ... />
    </g>
    <g id="openings"> ... </g>
    <g id="dimensions"> ... </g>
  </g>
  <g id="north-arrow"> ... </g>
  <g id="schedules"> ... </g>
  <g id="disclaimers"> ... </g>
  <g id="title-block"> ... </g>
</svg>
```

---

## 12. Drawing Manifest

The compilation process produces `artifacts/test_drawings_m2/drawing_manifest.json` binding all sheets:
```json
{
  "projectId": "proj-mumbai-real-1100",
  "releaseId": "rel-pilot-20261002-aedf9830",
  "designVersionId": "DV-OPT-B-9be0a983",
  "cbmHash": "sha256:ec57846e2168f7f042040e4a95bfa2db6d5a327f4be5b054c2a5ec31de5983ba",
  "compilerVersion": "1.0.0",
  "generationTimestamp": "2026-10-02T12:00:00Z",
  "totalSheets": 9,
  "manifestHash": "sha256:b887cf1d4de3dc7e78da6383a8b417e9976bb2d1fdfc2b64d471e95fa50b656b",
  "drawings": [ ... ]
}
```

---

## 13. Determinism Verification Table

| File | SHA-256 Pass 1 | SHA-256 Pass 2 | Match |
|---|---|---|---|
| `A-101_ground_floor_plan.svg` | `5ff9b52877be387c...` | `5ff9b52877be387c...` | **IDENTICAL** |
| `A-101_ground_floor_plan.pdf` | `150cd63bb1cd6f38...` | `150cd63bb1cd6f38...` | **IDENTICAL** |
| `A-102_first_floor_plan.svg` | `e0d30b0d02e7407e...` | `e0d30b0d02e7407e...` | **IDENTICAL** |
| `A-102_first_floor_plan.pdf` | `397f240cfd5d5a3d...` | `397f240cfd5d5a3d...` | **IDENTICAL** |
| `A-103_terrace___roof_plan.svg` | `f9ec53cf758899eb...` | `f9ec53cf758899eb...` | **IDENTICAL** |
| `A-103_terrace___roof_plan.pdf` | `f35d48ea81da8983...` | `f35d48ea81da8983...` | **IDENTICAL** |
| `A-201_front_elevation_south.svg`| `a6b83e406dcf2889...` | `a6b83e406dcf2889...` | **IDENTICAL** |
| `A-201_front_elevation_south.pdf`| `1989dbd52b03b712...` | `1989dbd52b03b712...` | **IDENTICAL** |
| `A-202_rear_elevation_north.svg` | `02e6d38ebde2707c...` | `02e6d38ebde2707c...` | **IDENTICAL** |
| `A-202_rear_elevation_north.pdf` | `2f4c0f3ad60b5781...` | `2f4c0f3ad60b5781...` | **IDENTICAL** |
| `A-203_left_elevation_west.svg` | `c5d7165189e9d955...` | `c5d7165189e9d955...` | **IDENTICAL** |
| `A-203_left_elevation_west.pdf` | `5e984d19386519d4...` | `5e984d19386519d4...` | **IDENTICAL** |
| `A-204_right_elevation_east.svg` | `aa7ea1dc6b72e4ef...` | `aa7ea1dc6b72e4ef...` | **IDENTICAL** |
| `A-204_right_elevation_east.pdf` | `8b8c442332b7d5db...` | `8b8c442332b7d5db...` | **IDENTICAL** |
| `A-301_longitudinal_section_a-a.svg`| `7f4c8facb1d4c671...` | `7f4c8facb1d4c671...` | **IDENTICAL** |
| `A-301_longitudinal_section_a-a.pdf`| `1ae1d3066b3e1cf2...` | `1ae1d3066b3e1cf2...` | **IDENTICAL** |
| `A-302_cross_section_b-b.svg` | `16d0d53423b963b7...` | `16d0d53423b963b7...` | **IDENTICAL** |
| `A-302_cross_section_b-b.pdf` | `ffefa90faea395be...` | `ffefa90faea395be...` | **IDENTICAL** |
| `drawing_manifest.json` | `c4dcae74b381ee22...` | `c4dcae74b381ee22...` | **IDENTICAL** |

---

## 14. Pilot Immutability Verification

`artifacts/pilot_handoff/` was verified before and after Milestone 2:
- Git status: `clean`, zero modifications.
- Manifest hash: `876f21ae800940245ed9702d9e00e27be2be636f033f5d24e85c0bb4fe877cb4` unchanged.
- All M2 test artifacts reside exclusively in `artifacts/test_drawings_m2/`.

---

## 15. API Endpoints

Five new endpoints were added to [`apps/api-gateway/main.py`](file:///Users/surajkumar/Desktop/Real_state_dev/apps/api-gateway/main.py):

1. `GET /api/v1/design-versions/{design_version_id}/drawings`
   Returns the complete drawing manifest and list of drawing sheets.
2. `GET /api/v1/design-versions/{design_version_id}/drawings/{drawing_id}`
   Returns detailed sheet metadata, scale, sheet number, and source CBM element IDs.
3. `GET /api/v1/design-versions/{design_version_id}/drawings/{drawing_id}/pdf`
   Returns standalone A3 landscape vector PDF (`Content-Type: application/pdf`).
4. `GET /api/v1/design-versions/{design_version_id}/drawings/{drawing_id}/svg`
   Returns semantic SVG drawing sheet (`Content-Type: image/svg+xml`).
5. `POST /api/v1/design-versions/{design_version_id}/drawings/compile`
   Compiles all 9 sheets to disk and returns the verified manifest.

All live endpoints verified on port `5001` with status `200 OK`.

---

## 16. Frontend Implementation

- **DrawingSheetsModal:** Created [`apps/web/src/components/DrawingSheetsModal.tsx`](file:///Users/surajkumar/Desktop/Real_state_dev/apps/web/src/components/DrawingSheetsModal.tsx).
- **Entry Point:** Integrated "VIEW DRAWINGS" button in [`apps/web/src/components/BuildReviewView.tsx`](file:///Users/surajkumar/Desktop/Real_state_dev/apps/web/src/components/BuildReviewView.tsx) next to "DOWNLOAD HOME PDF".
- **Customer View:** Displays clean, intuitive sheet navigation (Ground Floor, First Floor, Roof, Elevations, Sections) with live vector SVG previews and one-click PDF/SVG downloads.
- **Technical Mode Toggle:** When toggled by engineers/architects, reveals:
  - `[Drawing Manifest]`: CBM model hash, compiler version, timestamp.
  - `[Source CBM IDs]`: Active CBM element IDs projected on sheet.
  - `[Compiler Details]`: ISO 128 standards, scale, and projection parameters.
- **Build Status:** `tsc && vite build` passed with zero errors; 20/20 Vitest unit tests pass.

---

## 17. Test Results

### 1. Dedicated Drawing Compiler Test Suite ([`tests/test_drawing_compiler.py`](file:///Users/surajkumar/Desktop/Real_state_dev/tests/test_drawing_compiler.py))
```
Ran 20 tests in 4.174s — OK (20/20 PASS)
- test_01_floor_plan_generated: PASS
- test_02_elevation_generated: PASS
- test_03_section_generated: PASS
- test_04_room_labels_present: PASS
- test_05_dimensions_present: PASS
- test_06_doors_tagged: PASS
- test_07_windows_tagged: PASS
- test_08_north_arrow_present: PASS
- test_09_title_block_present: PASS
- test_10_drawing_scale_correct: PASS
- test_11_drawing_ids_deterministic: PASS
- test_12_cbm_traceability_present: PASS
- test_13_pdf_generated: PASS
- test_14_svg_generated: PASS
- test_15_repeated_compilation_produces_identical_svg: PASS
- test_16_repeated_compilation_produces_identical_pdf: PASS
- test_17_source_cbm_hash_preserved: PASS
- test_18_no_benchmark_contamination: PASS
- test_19_pilot_release_unchanged: PASS
- test_20_g5_g6_remain_locked: PASS
```

### 2. Full Backend Regression
```
Ran 172 tests in 48.664s — OK (172/172 PASS)
```

### 3. Frontend Tests & Build
```
Vitest: 20/20 tests PASS
Vite build: built in 3.96s (dist/ generated successfully)
```

---

## 18. Sample Output Sheets

All compiled test sheets are available in `artifacts/test_drawings_m2/`:
- `A-101_ground_floor_plan.pdf` (6,693 bytes) & `.svg` (22,206 bytes)
- `A-102_first_floor_plan.pdf` (5,910 bytes) & `.svg` (13,745 bytes)
- `A-103_terrace___roof_plan.pdf` (5,180 bytes) & `.svg` (10,958 bytes)
- `A-201_front_elevation_south.pdf` (5,263 bytes) & `.svg` (9,837 bytes)
- `A-202_rear_elevation_north.pdf` (4,978 bytes) & `.svg` (8,829 bytes)
- `A-203_left_elevation_west.pdf` (5,302 bytes) & `.svg` (9,886 bytes)
- `A-204_right_elevation_east.pdf` (4,978 bytes) & `.svg` (8,827 bytes)
- `A-301_longitudinal_section_a-a.pdf` (5,394 bytes) & `.svg` (10,317 bytes)
- `A-302_cross_section_b-b.pdf` (5,221 bytes) & `.svg` (9,531 bytes)
- `drawing_manifest.json` (4,393 bytes)

---

## 19. Known Limitations

1. **Sheet Size Scope:** M2 defaults to A3 landscape. While A2 parameters are centralized in `drawing_styles.py`, production compilation for M2 targets A3.
2. **Door Swings in Orthographic Cut:** Door openings are plotted with standardized tag bubbles and clear opening widths; full swing arcs are projected on floor plans when wall orientation is orthogonal.
3. **Stair Tread Count in Section Cut:** Transverse sections display cut flights and floor transitions; tread hatching follows standard drafting conventions.

---

## 20. Professional and Legal Boundary

Every standalone drawing sheet (SVG and PDF) prominently embeds the required safety notice:
> *"Computational drawing generated from the Planwise Canonical Building Model. This document is preliminary and requires review, coordination, and certification by the appropriate licensed professional before statutory submission or construction."*

Furthermore, any structural elements carry the explicit disclaimer:
> *"Structural representation shown is preliminary and derived from the Planwise canonical model. Final structural design and certification remain subject to licensed structural engineer review."*

Gates G5 (Municipal Sanction) and G6 (Construction Authorization) remain strictly **LOCKED**.

---

## 21. Exact Next Milestone

**M3: Structural Analytical Pipeline**
*(Note: M3 development has NOT been started in accordance with strict Milestone 2 scope constraints.)*

---

**STATUS: M2_DRAWING_PASS**
