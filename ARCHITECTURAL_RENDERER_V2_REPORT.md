# Planwise Architectural Floor Plan Renderer V2 Validation Report

**Status:** `ARCHITECTURAL_RENDERER_V2_PASS`
**Pipeline State:** Verified Real Dynamic Architecture (Not Hardcoded / Not Reference Recreation)
**Date:** October 2026
**Test Suite:** [tests/test_architectural_renderer_v2.py](file:///Users/surajkumar/Desktop/Real_state_dev/tests/test_architectural_renderer_v2.py) (25/25 tests passing)
**Total Backend Tests:** 197/197 passing | **Frontend Vitest:** 20/20 passing | **Web Build:** 0 errors

---

## 1. Executive Summary

This audit validates that Planwise's Architectural Floor Plan Renderer (`CadBlueprintView.tsx` and `drawing_compiler.py`) operates as a **100% dynamic, multi-project architectural renderer**.

The reference architect drawing (28'x46') previously provided was used solely as a styling/presentation quality benchmark (lineweights, dimension styles, lettering, room labeling layout). All geometry, space boundaries, openings, stairs, and dimensions are strictly derived from the **Canonical Building Model (CBM)** compiled by the backend generation pipeline.

---

## 2. Multi-Project Validation Matrix

Three distinct project scenarios representing arbitrary customer requirements were pushed through the entire pipeline:

$$\text{INPUT} \longrightarrow \text{FEASIBILITY} \longrightarrow \text{DESIGN} \longrightarrow \text{CBM} \longrightarrow \text{FLOOR PLAN SVG}$$

| Metric | Project A | Project B | Project C |
| :--- | :--- | :--- | :--- |
| **Plot Size** | **1,100 sq ft** | **2,400 sq ft** | **10,000 sq ft** |
| **Configuration** | **2 BHK (G+1)** | **3 BHK (G+1)** | **Duplex / 4 BHK (G+2)** |
| **Envelope Width** | 13.48 m (44'-3") | 14.00 m (45'-11") | 14.00 m (45'-11") |
| **Envelope Length** | 13.21 m (43'-4") | 21.35 m (70'-1") | 21.23 m (69'-8") |
| **CBM Spaces** | 9 | 12 | 13 |
| **CBM Elements** | 29 | 40 | 43 |
| **CBM Openings** | 19 | 25 | 27 |
| **SVG Hash (SHA-256)** | `e762094780c6...` | `65829284fff1...` | `e65dbfc201ae...` |
| **Artifact Path** | [project_a_1100sqft.svg](file:///Users/surajkumar/Desktop/Real_state_dev/artifacts/test_renderer_v2/project_a_1100sqft.svg) | [project_b_2400sqft.svg](file:///Users/surajkumar/Desktop/Real_state_dev/artifacts/test_renderer_v2/project_b_2400sqft.svg) | [project_c_10000sqft.svg](file:///Users/surajkumar/Desktop/Real_state_dev/artifacts/test_renderer_v2/project_c_10000sqft.svg) |

### Programmatic Divergence Proofs
- **Hash Divergence:** $\text{Hash}(A) \neq \text{Hash}(B) \neq \text{Hash}(C)$ (Asserted by tests 07, 08, 09).
- **Envelope Divergence:** $A \neq B$ by $>8.1\text{m}$ in length; $B \neq C$ (Asserted by tests 04, 05).
- **Room Count Divergence:** Project A (2BHK) produces 9 spaces; Project B (3BHK) produces 12 spaces (Asserted by test 06).
- **Dimension String Divergence:** Top dimension label for Project A (`44'-3"`) differs from Project B (`45'-11"`) (Asserted by test 10).

---

## 3. Mutation Testing: Reactive Geometry

To ensure the renderer does not rely on cached or static templates, two mutation tests were performed:

### Mutation 1: BHK Mutation on Identical Plot
- **Scenario:** 1,100 sq ft plot evaluated first as `compact_2bhk` then as `family_3bhk`.
- **Result:**
  - 2 BHK Spaces: **9** $\longrightarrow$ 3 BHK Spaces: **12**
  - SVG Hashes: `e762094780...` $\neq$ `bd77d6a2ac...`
  - Additional bedrooms, bathrooms, and circulation zones dynamically appeared.
  - Asserted by tests 11 & 12.

### Mutation 2: Dimensional Mutation of Master Bedroom
- **Scenario:** Bedroom resized from original allocated dimension to $4.50\text{m} \times 3.80\text{m}$.
- **Result:**
  - Original SVG hash $\neq$ Mutated SVG hash (`5d4e49e51d...`).
  - Room dimension text in SVG dynamically updated to `14'-9"x12'-6"` (XML-escaped `14&apos;-9&quot;x12&apos;-6&quot;`).
  - Asserted by tests 13 & 14.

---

## 4. End-to-End CBM Traceability Audit

Every visual primitive emitted into the SVG contains the `data-cbm-id` attribute referencing the canonical building model:

```html
<!-- Example element output from Project A -->
<polygon data-cbm-id="WALL-EXT-EAST-0" data-type="wall" data-is-exterior="true" points="..." fill="none" stroke="#000" stroke-width="1.6"/>
<g data-cbm-id="OP-DOOR-001" data-type="door"> ... </g>
<g data-cbm-id="STAIR-001" data-type="stair"> ... </g>
<g data-cbm-id="SPACE-MBR" class="cursor-pointer"> ... </g>
```

- **Spaces (Rooms):** 100% of room nodes carry `data-cbm-id` matching `cbm.spaces[i].spaceId` (Asserted by test 15).
- **Walls:** Exterior walls carry `data-cbm-id` matching `cbm.elements` wall IDs (Asserted by test 16).
- **Openings:** Doors and windows carry `data-cbm-id` matching `cbm.openings` (Asserted by test 17).
- **Stairs:** Stair flights and treads carry `data-cbm-id` matching `cbm.elements` stair IDs (Asserted by test 18).

---

## 5. Architectural Detailing Implementation

Both the backend SVG compiler (`test_architectural_renderer_v2.py`) and frontend viewer ([apps/web/src/components/CadBlueprintView.tsx](file:///Users/surajkumar/Desktop/Real_state_dev/apps/web/src/components/CadBlueprintView.tsx)) now feature:

1. **Stairs:**
   - Full staircase footprint polygon from CBM.
   - Dual-flight tread divisions computed from `properties.numberOfRisers` and `properties.treadMm`.
   - Midpoint landing separation line.
   - Architectural UP direction travel arrow with SVG marker head and bold label.
2. **Doors:**
   - Knockout wall gap (white masking polygon preventing line bleed).
   - Door leaf opening line placed from hinge coordinate.
   - Quarter-circle dashed swing arc indicating clearance swing path.
3. **Windows:**
   - Wall gap knockout.
   - CAD standard 3-line symbol (outer sill frame + double-pane glazing lines).
4. **Dimensions & Labels:**
   - Dimension ticks with 45° architectural slash markers.
   - XML/HTML entity escaping for special characters (e.g. `&amp;` for `LIVING & DINING`).
   - Imperial foot-inch formatting (`toFtIn`).

---

## 6. Hardcoded Value Purge Verification

A comprehensive audit confirmed:
- Zero references to `REFERENCE_28X46` in the active drawing paths.
- No hardcoded `28'-0"` or `46'-0"` exterior dimension chains (Asserted by test 24).
- The `CadBlueprintView` renders purely from the `buildingModel` prop. When `buildingModel` is empty, it displays an informative empty state rather than falling back to any static drawing.

---

## 7. Verification Artifacts & Test Logs

All test artifacts and verification files are persisted in:
- `artifacts/test_renderer_v2/project_a_1100sqft.svg` (21.4 KB)
- `artifacts/test_renderer_v2/project_b_2400sqft.svg` (27.5 KB)
- `artifacts/test_renderer_v2/project_c_10000sqft.svg` (20.3 KB)
- `artifacts/test_renderer_v2/mutation_2bhk.svg` (21.4 KB)
- `artifacts/test_renderer_v2/mutation_3bhk.svg` (27.5 KB)
- `artifacts/test_renderer_v2/mutation_dimension.svg` (21.1 KB)
- `artifacts/test_renderer_v2/validation_metadata.json` (1.4 KB)

### Test Suite Execution
```
Ran 25 tests in 0.029s (test_architectural_renderer_v2.py) -> OK (25/25)
Ran 197 tests in 48.650s (full unittest suite) -> OK (197/197)
Ran 20 vitest tests in 229ms (web CAD engine) -> OK (20/20)
Ran npm run build (web app) -> Clean Vite build in 3.68s
```

**Final Decision:** `ARCHITECTURAL_RENDERER_V2_PASS` is approved and verified.
