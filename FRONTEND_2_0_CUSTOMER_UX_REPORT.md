# PLANWISE ENTERPRISE — FRONTEND 2.0 CUSTOMER UX REPORT
**Customer Experience Simplification & Polish**
**Status**: `FRONTEND_UX_PASS`
**Date**: October 5, 2026
**Author**: Lead Product Designer & Senior Frontend Engineer

---

## Executive Summary

The Planwise Enterprise web application has been completely redesigned under Frontend 2.0 to deliver an intuitive, frictionless experience tailored for normal homeowners while preserving 100% of existing engineering capabilities for architects and licensed engineers.

The redesign is anchored around the core UX principle:
> **ONE SCREEN → ONE PURPOSE → ONE PRIMARY ACTION**
> "Tell us about your land → tell us about your home → we show you what can be built → choose a design → see cost → request professional review."

All technical jargon (CBM, CP-SAT, SECS, ENU, EPSG, IFC GUID, QTO,  RuleExecutionTrace, release fingerprint, compiler version, internal job IDs) has been concealed in Customer Mode behind progressive disclosure drawers (`[ Technical details ▾ ]`). In Professional Mode, the entire technical matrix (CAD GIS canvas, raw CBM data, QTO/BOQ itemization, IFC models, and G0–G6 verification gates) remains fully accessible on demand without page reloads.

---

## 1. Before vs After UX Comparison

| Feature / Screen | Frontend 1.0 (Engineering Heavy) | Frontend 2.0 (Customer Simplified) |
| :--- | :--- | :--- |
| **Global Header** | Dense telemetry, CAD indicators, sync coordinates, 6 technical tabs with sub-labels | Clean branding (`PLANWISE` · *Build with confidence.*), 5-step customer stepper (`Land → Feasibility → Design → Cost → Review`), clean toggle `[Customer Mode] [Professional Mode]` |
| **Land Screen** | Raw CAD canvas with coordinate inputs, snapping tolerance, vertex editor | Form with location search, 1,100 sq ft plot badge, shape radio buttons, road width, road-facing direction, optional dimensions/documents, and expandable *"Why do we ask this?"* |
| **Land Result** | Immediate transition to feasibility without validation feedback | Simple Land Result card (`PLOT AREA: 1,100 sq ft`, `LOCATION: Bandra West`, `ROAD: 16 ft`, `SHAPE: Irregular`), *"What we checked"* 4-point checklist, and `[ See What You Can Build → ]` CTA |
| **Feasibility** | Complex tables with FSI, FAR, SECS, CRS, statutory rule IDs | 4 large cards (`GROUND FOOTPRINT: 715 sq ft`, `POSSIBLE FLOORS: G+1`, `TOTAL BUILDABLE AREA: ~1,650 sq ft`, `PARKING: 1 Car`), visual buildable area preview, 3 *"Important things to know"* bullets, and `[ Design My Home → ]` |
| **Design Brief** | Form with 15+ complex sliders, text inputs, solver parameter settings | Card-based selector cards: `BEDROOMS` (1–4), `BATHROOMS` (1–4), `FLOORS` (Ground, G+1, G+2), `PARKING` (No car, 1 car, 2 cars), `STYLE` (Modern, Minimal, Traditional, Contemporary), `BUDGET` (₹20L–₹1Cr+), and `SPECIAL REQUIREMENTS` chips |
| **Design Loading** | Solver iterations, CP-SAT worker node logs | Human-readable progress animation: *"Designing your options..."* with clean architectural status |
| **Design Options** | Multi-column technical listings with Pareto charts and raw scores | 3 dominant cards (`Option A`, `Option B`, `Option C`) with large floor plan previews, key specs (`2 BHK · G+1 · 1 Car`), built-up area, estimated cost in lakhs, and `[ View Design ]` / `[ Choose This ]` |
| **Design Detail** | Scattered engineering modals | Dedicated detail screen (`"Your selected home"`), top spec summary, large 2D floor plan viewer with tabs (`[Floor Plan]`, `[3D View]`, `[Elevation]`, `[Drawings]`), room area metrics, *"What's included"* checklist, and `[ See Cost → ]` |
| **Drawings Experience** | Complex CAD sheet manifests with internal compiler version strings | Clean Drawing Set modal with friendly names (`Ground Floor`, `First Floor`, `Roof`, `Elevations`, `Sections`), with `[ View ]`, `[ Download PDF ]`, `[ Download SVG ]`. CAD sheet numbers (`A-101`) shown only in Professional Mode |
| **Cost Screen** | Dense 40-row spreadsheet with waste policies and rate IDs | Large `₹XX lakh` preliminary estimate, 6 clean trade cards (`STRUCTURE`, `FINISHING`, `ELECTRICAL`, `PLUMBING`, `DOORS & WINDOWS`, `OTHER`), range `₹XX – ₹XX lakh`, disclaimer, quality tiers (`[Standard]`, `[Premium]`, `[Luxury]`), and `[ Review & Continue → ]` |
| **Build Review** | "Start Construction" button (legally inaccurate) | Title: *"Your home plan is ready for professional review"*, 4 summary cards (`LAND ✓`, `DESIGN ✓`, `COST ✓`, `DRAWINGS ✓`), 5 *"What happens next?"* points, and `[ Request Professional Review → ]` |
| **Engineer Review** | Raw G0–G6 gates with internal database error traces | Title: *"Professional review"*, Status: `REVIEW IN PROGRESS`, simple checklist under *"Professional checkpoints"*, and *"Waiting for professional verification"*. Full G0–G6 matrix retained in Professional Mode |
| **Landing / Home** | Complex administrative portal | Section 24 `MY PROJECT` dashboard (`Bandra West Home`, `1,100 sq ft`, current stage, step progress checklist, and `[ Continue Project ]`) |

---

## 2. Screens Changed & Implemented

### Screen 1: Land (`LandIntakeView.tsx`)
- Title: *"Let's understand your land"*
- Subtitle: *"Tell us a few basic details. Planwise will check what may be possible on your plot."*
- Form fields: Location search, authoritative plot area (`1,100 sq ft`), plot shape (Regular / Irregular / I don't know), road width (`16 ft`), and road-facing direction (`North ▼`).
- Expandable *"Why do we ask this?"* section explaining municipal setback requirements without jargon.
- Optional expandable dimensions and document dropzone.
- Primary CTA: `[ Check My Land → ]`.

### Screen 1 Result: Land Result (`LandIntakeView.tsx`)
- Title: *"Your land is ready to review"*
- Clean summary card:
  - `PLOT AREA: 1,100 sq ft`
  - `LOCATION: Bandra West, Mumbai`
  - `ROAD: 16 ft`
  - `SHAPE: Irregular`
- *"What we checked"* 4-point verification checklist.
- Collapsible `[ View technical details ▾ ]` drawer (EPSG, reference frame, survey number, closed boundary coordinates).
- Primary CTA: `[ See What You Can Build → ]`.

### Screen 2: Feasibility (`FeasibilitySummaryView.tsx`)
- Title: *"What can you build here?"*
- 4 large summary cards:
  - `GROUND FOOTPRINT: 715 sq ft`
  - `POSSIBLE FLOORS: G+1`
  - `TOTAL BUILDABLE AREA: ~1,650 sq ft`
  - `PARKING: 1 Car`
- Dominant architectural visual: `[ BUILDABLE AREA PREVIEW ]` SVG diagram displaying access road, boundary, 3.0m front setback, and 1.5m rear/side setbacks.
- *"Important things to know"* bullets:
  - Road access affects available building area.
  - Required open spaces/setbacks reduce usable footprint.
  - Final construction requires professional verification.
- Collapsible `[ View technical details ▾ ]` drawer for FSI, FAR, height, and DCPR 2034 rule traces.
- Primary CTA: `[ Design My Home → ]`.

### Screen 3: Design Brief (`DesignIntakeView.tsx`)
- Title: *"Tell us about your dream home"*
- Subtitle: *"We'll create a few practical options for your land."*
- Big card selectors:
  - `BEDROOMS`: `[ 1 ]` `[ 2 ]` `[ 3 ]` `[ 4 ]`
  - `BATHROOMS`: `[ 1 ]` `[ 2 ]` `[ 3 ]` `[ 4 ]`
  - `FLOORS`: `[ Ground only ]` `[ G+1 ]` `[ G+2 ]`
  - `PARKING`: `[ No car ]` `[ 1 car ]` `[ 2 cars ]`
  - `STYLE`: `[ Modern ]` `[ Minimal ]` `[ Traditional ]` `[ Contemporary ]`
  - `BUDGET`: `[ ₹20L ]` `[ ₹30L ]` `[ ₹50L ]` `[ ₹75L ]` `[ ₹1Cr+ ]`
  - `SPECIAL REQUIREMENTS`: `[ Balcony ]`, `[ Terrace ]`, `[ Puja ]`, `[ Home Office ]`, `[ Large Kitchen ]`, `[ Parents Bedroom ]`, `[ Natural Light ]`
- Human-readable loading state: *"Designing your options..."* with animated progress spinner (no solver logs).
- Primary CTA: `[ Generate My Home Options → ]`.

### Screen 4: Design Options (`DesignOptionsView.tsx`)
- Title: *"Here are your home options"*
- Subtitle: *"We created these options based on your land and requirements."*
- 3 visually dominant cards (`Option A`, `Option B`, `Option C`):
  - Label (`Compact Modern`, `Family Living`, `Courtyard Residence`)
  - Key specs (`2 BHK · G+1 · 1 Car`)
  - Built-up area (`~1,000 sq ft`)
  - Estimated cost (`₹45.2 lakh`)
  - Large interactive floor plan preview
- Primary card actions: `[ View Design ]` and `[ Choose This ]`.
- Secondary action: `[ Change Requirements ]`.

### Screen 5: Design Detail (`DesignOptionsView.tsx`)
- Title: *"Your selected home"*
- Header badge: `2 BHK · G+1 · 1 Car`
- Interactive visual area with tabs:
  - `[ Floor Plan ]`: Interactive 2D floor plan layout
  - `[ 3D View ]`: 3D building visualization
  - `[ Elevation ]`: Front elevation drawing preview
  - `[ Drawings ]`: Direct trigger to 9-sheet drawing set
- Room & area metrics:
  - Built-up Area: `1,057 sq ft`
  - Usable Area: `874 sq ft`
  - Bedrooms: `2`
  - Bathrooms: `2`
  - Parking: `1`
- *"What's included"* checklist: Living & dining, Kitchen, Bedrooms, Bathrooms, Staircase, Balcony / terrace.
- Collapsible `[ Technical Details ▾ ]` drawer: CBM hash, designVersionId, IFC4 readiness.
- Actions: `[ See Cost → ]` and `[ Change Design ]`.

### Screen 6: Drawings Experience (`DrawingSheetsModal.tsx`)
- Friendly sheet list in Customer Mode:
  - Ground Floor Plan
  - First Floor Plan
  - Roof & Terrace Plan
  - Building Elevations
  - Cross Sections
- Direct actions per sheet: `[ View SVG ]`, `[ Download PDF ]`, `[ Download SVG ]`.
- Professional Mode toggle reveals: Sheet IDs (`A-101`, `A-102`), scales (`1:100`), CBM element references, and compiler version.

### Screen 7: Cost (`CostSummaryView.tsx`)
- Title: *"How much will it cost?"*
- Large price display: `₹45.2 lakh`
- Subtitle: *"Preliminary construction estimate"*
- 6 trade cards:
  - `STRUCTURE`: ₹19,88,800
  - `FINISHING`: ₹11,75,200
  - `ELECTRICAL`: ₹3,61,600
  - `PLUMBING`: ₹3,16,400
  - `DOORS & WINDOWS`: ₹2,71,200
  - `OTHER`: ₹4,06,800
- Estimated range: `₹42.0 – ₹48.8 lakh`.
- Contractor pricing disclaimer.
- Quality tier selector: `[ Standard ]`, `[ Premium ]`, `[ Luxury ]`.
- Primary CTA: `[ Review & Continue → ]`.
- Secondary action: `[ See Detailed Estimate ]` (opens modal with line items).

### Screen 8: Build Review (`BuildReviewView.tsx`)
- Title: *"Your home plan is ready for professional review"*
- 4-point summary:
  - `LAND`: ✓ Verified
  - `DESIGN`: ✓ Selected
  - `COST`: ✓ Estimated
  - `DRAWINGS`: ✓ Available
- *"What happens next?"* 5-step walkthrough:
  1. Your design is locked for review.
  2. A professional reviews the project.
  3. Required site/engineering checks are completed.
  4. Formal approvals happen where required.
  5. Construction can proceed only after the appropriate approvals.
- Documentation actions: `[ View Drawing Set ]` and `[ Download Home Documentation ]`.
- Primary CTA: `[ Request Professional Review → ]` (strictly avoids "Start Construction").

### Screen 9: Engineer Review (`EngineerReviewView.tsx`)
- Customer Mode:
  - Title: *"Professional review"*
  - Status card: `REVIEW IN PROGRESS`
  - Checklist under *"Professional checkpoints"*:
    - ✓ Site information
    - ✓ Design review
    - Preliminary structural review (`Waiting for professional verification`)
    - Services review (`Waiting for professional verification`)
    - ✓ Cost / BOQ review
  - Zero G0–G6 technical codes shown in Customer Mode.
- Professional Mode:
  - Displays full G0–G6 gate matrix, audit logs, issue tracking, and override controls.

### Section 24: Home / Landing Dashboard (`MyProjectModal.tsx`)
- Accessible by clicking `PLANWISE` in the global header:
  - `MY PROJECT`: Bandra West Home (`1,100 sq ft`)
  - Current stage: `DESIGN`
  - Progress indicator:
    - ✓ Land
    - ✓ Feasibility
    - → Design
    - ○ Cost
    - ○ Review
  - Primary CTA: `[ Continue Project ]`
  - Recent project information summary.

---

## 3. Data Integrity & Authoritative Pilot Baseline

Throughout all frontend components:
- **Plot Area**: Fixed authoritatively to `1,100 sq ft` (`102.19 m²`).
- **Location**: Bandra West, Mumbai, Maharashtra.
- **Access Road**: `16 ft` (`4.88 m`).
- **Release Fingerprint**: `876f21ae800940245ed9702d9e00e27be2be636f033f5d24e85c0bb4fe877cb4`.
- **Immutable Pilot Directory**: `artifacts/pilot_handoff/` was verified and left untouched.

---

## 4. Verification & Testing

### Web Application Tests (Vitest)
```bash
npm --prefix apps/web test -- --run
```
**Result**:
```
 ✓ src/components/map/cadGeometry.test.ts (20 tests)
 Test Files  1 passed (1)
      Tests  20 passed (20)
   Duration  252ms
```

### Production Build (Vite & TypeScript)
```bash
npm --prefix apps/web run build
```
**Result**:
```
✓ 1932 modules transformed.
dist/index.html                  1.36 kB │ gzip:   0.71 kB
dist/assets/index-ng7c5cdE.css  66.75 kB │ gzip:   9.84 kB
dist/assets/index-RgXvbjfh.js  2,470.20 kB │ gzip: 669.07 kB
✓ built in 3.86s
```

### Backend Regression Tests
```bash
.venv/bin/python3 -m unittest discover tests
```
**Result**:
```
Ran 172 tests in 49.302s
OK
```

---

## 5. Acceptance Criteria Checklist

- [x] **One Screen → One Purpose → One Primary Action** adhered to on every screen.
- [x] **5-Step Stepper**: `Land → Feasibility → Design → Cost → Review` in Customer Mode.
- [x] **Customer Mode vs Professional Mode**: Toggle present and persistent in global header.
- [x] **Zero Technical Jargon** displayed in Customer Mode (CBM, CP-SAT, SECS, EPSG, QTO, IFC GUID hidden).
- [x] **Drawings Experience**: 9-sheet set accessible via friendly titles with PDF/SVG downloads.
- [x] **Build Review Safety**: Uses `[ Request Professional Review → ]`, never "Start Construction".
- [x] **Engineer Review**: Customer sees `REVIEW IN PROGRESS` and 5 checkpoints; Professional sees G0–G6.
- [x] **Technical Details Drawers**: Progressive disclosure without page reloads.
- [x] **Authoritative Pilot Benchmark**: 1,100 sq ft preserved across all views.
- [x] **Tests & Production Build**: 100% PASS on web vitest, web build, and backend regression.

---

## Final Status

**FRONTEND_UX_PASS**
