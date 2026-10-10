# PILOT VS REAL DATA INTEGRITY REPORT

**Status:** `PILOT_DATA_ISOLATION_PASS`
**Date:** October 6, 2026
**Auditor:** Planwise Enterprise Systems Architecture & Quality Assurance
**Target:** Frontend 2.0 Customer UX & Professional Mode (`apps/web/`)
**Baseline Pilot:** `1,100 sq ft` / `102.19 m²` (`proj-mumbai-real-1100`, Bandra West, Mumbai, G+1, ₹45.2L)

---

## 1. EXECUTIVE SUMMARY & VERIFICATION STATUS

```text
==================================================
PILOT DATA ISOLATION STATUS:
PILOT_DATA_ISOLATION_PASS
==================================================

1. AUTHORITATIVE PILOT BASELINE:
   - Kept 100% immutable in artifacts/pilot_handoff/
   - Available via explicit "Load Pilot Golden Benchmark" action
   - Preserved in all automated backend and regression suites (172/172 PASS)

2. REAL PROJECT ISOLATION:
   - Dynamic plot area (sq ft / sq m) preserved from user input
   - Independent custom project IDs generated (proj-cust-*)
   - Zero silent fallback to 1,100 sq ft or Bandra West
   - Zero hardcoded cost defaulting (no silent fallback to ₹45.2 lakh)

3. UNAVAILABLE DATA RESILIENCE:
   - When real project data or solver results are unavailable:
     Displays: "Project data is temporarily unavailable." with [Retry]
   - Empty/error states distinctly separated from pilot fixtures

4. TEST EXECUTION:
   - Frontend Unit Tests: 20/20 PASSED (vitest)
   - Production Build: PASSED (tsc && vite build in 3.79s)
   - Pilot Handoff Integrity: 16/16 PASSED
   - Real Plot End-to-End Suite: 13/13 PASSED
   - Full Backend Regression: 172/172 PASSED (0 failures)
```

---

## 2. AUDIT OF SILENT FALLBACK BEHAVIORS REMOVED

Prior to this fix, several components used the authoritative 1,100 sq ft pilot values as fallback defaults when real customer data was missing or empty. All such silent fallbacks have been eliminated and replaced with strict three-tier classification:
1. **PILOT FIXTURE** (active only when `project.id === 'proj-mumbai-real-1100'`)
2. **REAL PROJECT DATA** (derived strictly from `project.declaredPlotAreaSqFt`, parcel coordinates, or backend feasibility metrics)
3. **EMPTY / UNAVAILABLE DATA** (renders explicit user alert `"Project data is temporarily unavailable."` with a `[Retry]` action)

---

## 3. COMPONENT-BY-COMPONENT REMEDIATION TABLE

| Component | Previous Silent Fallback | Remediated Behavior | Data Source |
|---|---|---|---|
| `types.ts` | Missing `declaredPlotAreaSqFt` field | Added `declaredPlotAreaSqFt?: number` to `ProjectData` and `ProjectData.parcel` | Customer intake / API |
| `LandIntakeView.tsx` | `parsedAreaSqft` defaulted to `|| 1100`; placeholder `"1100"`; CTS survey hardcoded to `CTS-1842-BANDRA` | Accepts `initialPlotArea`; does NOT fall back to 1100 if user clears input; placeholder updated to `"e.g. 1500"`; survey number dynamic (`CTS-SITE-REF`) | User Form Input |
| `FeasibilitySummaryView.tsx` | Hardcoded `footprintSqFt = 715`, `floorsText = "G+1"`, `approxBuildableSqFt = 1650`, badge `"1,100 sq ft · Bandra West"` | Strict check: if pilot, uses pilot fixtures; if real project, dynamically computes footprint, permissible BUA, and floors from `feasibility`; if data missing, shows `"Project data is temporarily unavailable."` with `[Retry]` | `project` + `feasibility` |
| `DesignOptionsView.tsx` | `formatCostLakh` returned `'₹45.2 lakh'` when amount missing; hardcoded `4520000` fallback | Requires explicit `isPilotOption` flag; for real options without cost, displays `'Estimate calculating...'`; if `options.length === 0`, displays `"Project data is temporarily unavailable."` with `[Retry]` | `HouseOption.boq` |
| `CostSummaryView.tsx` | Badge hardcoded to `"1,100 sq ft Plot · Bandra West"`; `totalCost` defaulted to `4520000` | Accepts `project`; dynamically formats badge with real plot area and location; if BOQ missing and non-pilot, shows `"Project data is temporarily unavailable."` with `[Retry]` | `project` + `boq` |
| `BuildReviewView.tsx` | Badge & cards hardcoded to `"1,100 sq ft · Bandra West"`, `"2 BHK · G+1"`, and `4520000` | Dynamic `badgeText` using `project.declaredPlotAreaSqFt` and `project.name`; dynamic room and floor counts from `layout`; dynamic cost | `project` + `layout` + `boq` |
| `EngineerReviewView.tsx` | Hardcoded `declaredSqFt = 1100`, `Bandra West, Mumbai`, `16.0 ft road` | Checks `isPilot`; dynamically derives `declaredSqFt` from project or displays `'Pending Survey'`; displays real location and actual road width | `project` + `feasibility` |
| `MyProjectModal.tsx` | Hardcoded `"1,100 sq ft"`, `"Bandra West, Mumbai"`, `"16 ft road width"`, `"Mumbai DCPR 2034"` | Fully dynamic: reads `plotAreaSqFt`, `locationText`, `roadWidthFt`, and `jurisdictionText` from active project | `project` |
| `HomeReportDownloadModal.tsx` | Hardcoded `"1,100 sq ft"`, `"102.19 m²"`, `"Bandra West Residential Development"` | Fully dynamic: derives `plotAreaSqFt`, metric conversion, real project name, and actual cost per sq ft | `project` + `layout` |
| `App.tsx` | `handleConfirmLandPlot` defaulted project ID to `'proj-mumbai-real-1100'` and cadastral number to `'CTS-1842-BANDRA'` | Generates clean `proj-cust-*` IDs for custom plots; preserves `declaredPlotAreaSqFt`; wires `onRetry` callbacks to feasibility and design generation | State Controller |

---

## 4. REGRESSION & INTEGRITY TEST RESULTS

### A. Frontend Unit Tests (Vitest)
```text
✓ src/components/map/cadGeometry.test.ts (20 tests) 5ms
Test Files: 1 passed (1)
Tests:      20 passed (20)
Duration:   271ms
```

### B. Frontend Production Build
```text
vite v6.4.3 building for production...
✓ 1932 modules transformed.
dist/index.html                     1.36 kB │ gzip:   0.71 kB
dist/assets/index-ng7c5cdE.css     66.75 kB │ gzip:   9.84 kB
dist/assets/index-6WEI9uRn.js   2,477.99 kB │ gzip: 670.91 kB
✓ built in 3.79s
```

### C. Backend Regression Suite
```text
1. test_pilot_handoff_integrity.py:
   Ran 16 tests in 0.134s -> OK (Pilot release hash and immutable artifacts 100% verified)

2. test_real_plot_end_to_end.py:
   Ran 13 tests in 15.831s -> OK (Dynamic custom parcel geometries and pipelines 100% verified)

3. Full Backend Unit & Pipeline Suite:
   Ran 172 tests in 49.466s -> OK (Zero failures, zero regressions)
```

---

## 5. CONCLUSION

The frontend architecture now maintains strict data isolation:
- The authoritative 1,100 sq ft Bandra West pilot remains an immutable reference benchmark.
- Real homeowner inputs (e.g., 2,400 sq ft, 800 sq ft, custom road widths) are strictly preserved across all 6 workflow stages and modals.
- No silent substitution of pilot fixtures occurs when real data is processing or unavailable.
