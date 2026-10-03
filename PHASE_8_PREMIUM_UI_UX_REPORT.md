# PLANWISE ENTERPRISE — PREMIUM APPLICATION UI/UX REDESIGN REPORT
**Execution Date:** October 2, 2026  
**Audience:** Product Design, Engineering Leadership, Institutional Stakeholders  
**Scope:** Frontend UI/UX Redesign across the entire Planwise Workflow (`Land → Feasibility → Design → Cost → Build → Engineer`)

---

## Executive Summary

Planwise Enterprise was redesigned from an internal dark-mode engineering dashboard into a **polished, institutional-grade Land-to-Home Development & Construction Platform**. 

The design addresses every UX principle outlined in the specification:
1. **One Product, One Visual Language, One Consistent Experience**
2. **Restrained Architectural Palette & Strict Spacing System**
3. **Persistent Global Application Shell & Workflow Stepper**
4. **Persistent Project Context Bar preserving the authoritative 1,100 sq ft benchmark**
5. **Clear separation of Customer Mode (intuitive, low cognitive load) and Technical View (engineering rigor, CAD, CBM, gates)**
6. **Zero breakage of underlying computational logic (M1/M2/M3), release ledgers, IFC generation, or G0–G6 statutory gates.**

---

## 1. UI/UX Audit (Before vs. After)

| Screen / Area | Pre-Redesign State (Deficiencies) | Post-Redesign State (Refinements) |
| :--- | :--- | :--- |
| **Global Aesthetics** | Dark `#07090e` engineering prototype look; mixed border radii (8/12/16/24px); rainbow status badges (indigo, cyan, emerald, purple, amber) | Restrained architectural palette (`#0b0d11` canvas, `#12151c` surface); strict 6px/8px/12px radius scale; single Planwise signature blue (`#2563eb`) accent |
| **Global Shell** | Generic top navigation; lacked persistent project metadata; contained outdated "10,000 sqm Benchmark" button | Persistent Workflow Stepper (`Land → Feasibility → Design → Cost → Build → Engineer`) with completed checkmarks; persistent Project Context Bar (`Bandra West · Mumbai \| Residential · 1,100 sq ft`) |
| **Land Intake** | Looked like a GIS database input form; exposed technical terms; unclear customer hierarchy | "Tell us about your land" headline; customer-friendly `[ 1,100 ] [sq ft]` input; segmented shape selector; road width input; primary `[ Check My Land ]` CTA |
| **Feasibility Report** | Complex engineering tables and HUD elements shown by default | "What can you build here?" headline; 5 compact metric cards (1,100 sq ft plot, 715 sq ft footprint, G+1 floors, 1,650 sq ft BUA, 1 car); architectural SVG site diagram; plain-language conditions checklist; technical details hidden behind accordion |
| **Design Intake** | Monolithic form; CP-SAT solver logs and raw optimization terminology | Guided 4-group conversational questionnaire (Who is it for? How to use it? What should it feel like? Anything important?); target budget chips; humanized generation progress loader |
| **Design Options** | Compact sidebar options that felt like database rows | Spacious architectural cards with visual floor plan preview; key metadata badges; lifestyle suitability tags; dedicated `[ View Design ]` 6-tab modal (Overview, Plan, 3D, Spaces, Materials, Cost) |
| **Cost Summary** | Engineering BOQ tables with raw lines displayed initially | "How much will it cost?" headline; clear hero cost display (₹45.2L, ₹3,616/sq ft, range ₹42.0L–₹48.8L); visual proportional trade bars; finish tier selector; IS 1200 calculation explainer |
| **Build Review** | Felt like an abrupt developer form or "Start Construction" button | "Ready to move forward?" transition from design to project delivery; 4-item readiness verification; 4-step "What happens next?" sequence; professional freeze trigger with acknowledgements |
| **Engineer Review** | Wall of engineering gates shown unconditionally to all users | Dual-mode experience: **Customer View** presents high-level status ("Professional review in progress") and 5 milestone cards; **Reviewer View** presents the institutional G0–G6 Gate Matrix with status, owner, timestamp, blocking issue, and required action |

---

## 2. Planwise Design System Tokens

Defined in `apps/web/src/index.css`:

### Color Palette
- **Canvas / Background:** `#0b0d11` (Deep Charcoal / Near-Black)
- **Primary Surface:** `#12151c` (Restrained Dark Slate Surface)
- **Elevated Surface:** `#181d26` (Floating Panels & Modals)
- **Surface Hover:** `#1e2430`
- **Subtle Hairline Border:** `rgba(255, 255, 255, 0.08)`
- **Medium Border:** `rgba(255, 255, 255, 0.14)`
- **Planwise Signature Accent:** `#2563eb` (Royal Architectural Blue, hover `#1d4ed8`)
- **Restrained Status Success:** `#16a34a` (Emerald Green)
- **Restrained Status Warning:** `#d97706` (Warm Amber)
- **Restrained Status Error:** `#dc2626` (Red)

### Typography & Spacing Grid
- **Scale:** 4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px
- **Body Font:** Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif
- **Monospace Numerical Font:** JetBrains Mono, 'SF Mono', Menlo, Consolas, monospace
- **Radii System:** Strictly 6px (small elements), 8px (buttons & inputs), 12px (cards), 16px (major panels/modals)

### Standardized Component Library (`.pw-*`)
- `.pw-page`, `.pw-container`, `.pw-container-wide`: Unified responsive layout containers
- `.pw-card`, `.pw-card-interactive`, `.pw-card-selected`: Institutional card surfaces
- `.pw-btn-primary`, `.pw-btn-secondary`, `.pw-btn-ghost`: Standardized 38px/44px buttons with consistent padding
- `.pw-input`: Standardized 42px form inputs with focus rings
- `.pw-badge-neutral`, `.pw-badge-success`, `.pw-badge-warning`, `.pw-badge-primary`: Restrained status pills
- `.pw-segmented-control`, `.pw-segmented-btn`: Mode toggles
- `.pw-metric-card`: Structured numerical display card

---

## 3. Application Shell & Workflow Stepper

The persistent header in `apps/web/src/components/Navbar.tsx`:
1. **Brand Identity:** Planwise logo mark + Enterprise tag.
2. **Persistent Project Context Bar:**
   `Bandra West · Mumbai · Residential · 1,100 sq ft` with real-time `[Build Frozen]` indicator upon lock.
3. **Workflow Stepper:**
   `1. Land → 2. Feasibility → 3. Design → 4. Cost → 5. Build → 6. Engineer`
   - **Completed:** Subtle emerald checkmark pill (`✓`)
   - **Active:** Solid Planwise blue badge with step number
   - **Future:** Muted slate styling
4. **Persistent Mode Switch:**
   - `Customer View`: Simplified, conversational, low jargon.
   - `Technical View`: Exposes CAD map canvas, GIS layers, CBM inspection, and G0–G6 gate controls.

---

## 4. Page-by-Page Redesign Details

### 4.1 Land Page (`LandIntakeView.tsx`)
- Headline: *"Tell us about your land"*
- Subtext: *"We'll check what can realistically be built on it."*
- Form Sections:
  1. **Location:** Street address input with City/State/Country sub-fields.
  2. **Plot Area:** Prominent `[ 1,100 ] [ sq ft ]` default customer input with unit toggle.
  3. **Plot Shape:** 3 distinct radio cards: Regular, Irregular, I'm not sure.
  4. **Road Access:** Numerical road width (16 ft default) and road-facing direction select.
  5. **Additional Details:** Collapsible dimensions with automatic area-mismatch detection preserving the 1,100 sq ft authoritative invariant.
  6. **Documents:** Drag-and-drop document upload area for 7/12 extract / property card.
- Primary CTA: `[ Check My Land ]` with progress steps.

### 4.2 Feasibility Page (`FeasibilitySummaryView.tsx`)
- Headline: *"What can you build here?"*
- Top 5 Metric Cards:
  - Plot: `1,100 sq ft`
  - Ground footprint: `715 sq ft` (65% coverage)
  - Possible floors: `G+1` (2 storeys)
  - Approx. buildable area: `1,650 sq ft`
  - Parking: `1 car`
- Visual Site Diagram: Scaled SVG drawing showing access road, 1,100 sq ft boundary, statutory 3.0m road setback, and 715 sq ft green buildable envelope.
- Site Conditions: Clear affirmative checklist (`✓ Road access confirmed`, `✓ Buildable envelope identified`, `✓ Applicable development rules checked`) and verification disclaimer.
- Progressive Disclosure: Collapsible `[ View technical details ]` drawer for base FSI, permissible FSI, and road deductions.

### 4.3 Design Intake (`DesignIntakeView.tsx`)
- Headline: *"Tell us how you want your home to work."*
- 4 Guided Steps:
  - **Step 1 (Who is it for?):** 1–4 BHK bedroom pills and bathroom selectors.
  - **Step 2 (How to use it?):** Floor levels (G, G+1, G+2), parking spaces (None, 1 car, 2 cars), balcony and terrace checkboxes.
  - **Step 3 (Feel & Style):** Modern, Minimal, Traditional, Contemporary cards.
  - **Step 4 (Important preferences):** Chips for Parents' room on ground floor, Large kitchen, Home office, Pooja room, Natural light, Small shop, plus target budget buttons (`₹35L`, `₹45L`, `₹55L`, `₹75L`, `₹1 Cr`).
- Primary CTA: `[ Generate House Options ]`.
- Polished Loader: 4 polite human messages ("Creating feasible house options...", "Checking space requirements...", "Checking circulation...", "Preparing 3D models...").

### 4.4 Design Options & Detail View (`DesignOptionsView.tsx`)
- Large architectural cards presenting each generated option:
  - Option Letter & Typology: `Option A · 2 BHK · G+1`
  - Visual floor plan preview canvas powered by `FloorPlanViewer`
  - Metrics: Built-up area (`1,250 sq ft`), Estimated cost (`₹45.2 lakh`), Parking (`1 car`)
  - Suitability tag: `Good for: Family living`
  - Actions: `[ View Design ]` and `[ Choose This ]`
- Comprehensive Design Detail Modal:
  - Large visual area with 6 dedicated tabs:
    1. **Overview:** Key metrics and room listing.
    2. **Floor Plan:** High-resolution architectural 2D canvas.
    3. **3D Model:** Interactive 3D building view.
    4. **Spaces:** Room-by-room area breakdown.
    5. **Materials:** Finish quality specifications.
    6. **Cost:** High-level trade summary with direct link to Cost page.

### 4.5 Cost Summary (`CostSummaryView.tsx`)
- Headline: *"How much will it cost?"*
- Hero Metrics Card:
  - Estimated Construction Cost: `₹45,20,000`
  - Unit Rate: `₹3,616 / sq ft`
  - Estimated Range: `₹42.0L – ₹48.8L`
  - Built-up: `1,250 sq ft BUA`
- Quality Tier Selector: Standard, Premium, Luxury tabs updating rates dynamically.
- Visual Trade Breakdown: Proportional multi-segment bar and individual trade cards (Structure, Finishing, Electrical, Plumbing, Doors & Windows, Other & Prelims).
- Explainability: Collapsible *"How was this calculated?"* outlining IS 1200 deterministic rules.
- Exports: `[ Download BOQ (CSV) ]` and `[ Download Estimate (JSON) ]`.
- Primary CTA: `[ Proceed to Build Review ]`.

### 4.6 Build Review (`BuildReviewView.tsx`)
- Headline: *"Ready to move forward?"*
- Readiness Checklist:
  - Land: `✓ Verified (1,100 sq ft)`
  - Design: `✓ Selected (2 BHK · G+1)`
  - Cost: `✓ Estimated (₹45.2 Lakh)`
  - Engineering: `Professional review required`
- *"What happens next?"* 4-Stage Visual Sequence:
  1. Your selected design is frozen.
  2. The project package is prepared.
  3. A professional engineer reviews it.
  4. Required approvals are completed.
- Primary Action: `[ Request Build Review ]` (freezes the design and transitions to Engineer Review).

### 4.7 Engineer Review (`EngineerReviewView.tsx`)
- **Customer View:**
  - Status hero: *"Professional review in progress"*
  - 5 Milestone Cards:
    1. Site & Boundary: `✓ Reviewed`
    2. Design: `✓ Reviewed`
    3. Structural: `Review in progress`
    4. MEP: `Review in progress`
    5. Approvals: `Pending`
  - Summary metrics and statutory responsibility notice.
- **Reviewer / Technical View:**
  - Full G0–G6 Gate Matrix with:
    - Gate Code & Title
    - Status badge
    - Owner (Licensed Surveyor, Structural Engineer, MEP Engineer, QS, Municipal Authority)
    - Last updated date
    - Blocking issue (if any)
    - Required action
    - Verification stamp and sign-off actions.

---

## 5. Verification & QA Results

### 5.1 Frontend Unit & CAD Tests
- Test Command: `npm --prefix apps/web test -- --run`
- Engine: Vitest v3.2.7
- Result: **20 passed (100%)**
- Validated: 3-vertex parcel, 4-vertex rectangle, edge insertions, vertex removals, butterfly self-intersection rejection, geodesic bearings, orthogonal snap, 15° step snap, 1m metric grid snap, UTM Zone 43N reprojection, frontage identification.

### 5.2 Frontend Production Build
- Build Command: `npm --prefix apps/web run build`
- Compiler: `tsc && vite build`
- Result: **Exit Code 0 — 0 TypeScript errors, 1,929 modules transformed.**
- Output: `dist/index.html` (1.36 kB), `dist/assets/index-*.css` (66.75 kB), `dist/assets/index-*.js` (2,447 kB).

### 5.3 Backend Regression Test Suite
- Test Command: `PYTHONPATH=. .venv/bin/python3 -m unittest discover tests`
- Result: **Ran 131 tests in 53.811s — OK (100% passing)**

### 5.4 Phase 7 & Phase 8 Targeted Tests
- Test Command: `PYTHONPATH=. .venv/bin/python3 -m unittest tests/test_phase7_engineer_review.py tests/test_phase8_1_persistence.py tests/test_controlled_pilot.py tests/test_pilot_handoff_integrity.py`
- Result: **Ran 45 tests in 15.615s — OK (100% passing)**

---

## 6. Files Changed

1. `apps/web/src/index.css`: Complete design system tokens, restrained architectural palette, strict spacing grid, typography rules, and `.pw-*` components.
2. `apps/web/src/components/Navbar.tsx`: Redesigned global header with workflow stepper, persistent project context bar (`1,100 sq ft`), and customer/technical view toggle.
3. `apps/web/src/components/LandIntakeView.tsx`: Customer land intake page with clean inputs, 1,100 sq ft default, and `[ Check My Land ]` CTA.
4. `apps/web/src/components/FeasibilitySummaryView.tsx`: Feasibility report page with 5 hero metrics, visual site diagram, and site conditions checklist.
5. `apps/web/src/components/DesignIntakeView.tsx`: Guided 4-group design questionnaire with budget presets and humanized generation progress loader.
6. `apps/web/src/components/DesignOptionsView.tsx`: Large architectural cards with floor plan preview and 6-tab design detail modal.
7. `apps/web/src/components/CostSummaryView.tsx`: Hero cost estimation card, visual trade breakdown bars, IS 1200 explainer, and BOQ export buttons.
8. `apps/web/src/components/BuildReviewView.tsx`: Transition view with 4-item readiness verification, What Happens Next sequence, and Request Build Review CTA.
9. `apps/web/src/components/EngineerReviewView.tsx`: Dual-mode customer milestones view vs institutional G0–G6 gate matrix.
10. `apps/web/src/App.tsx`: Synchronized application shell, canvas background, and viewMode bindings across all steps.

---

## Conclusion
Planwise Enterprise now looks, feels, and operates as an institutional-grade, trustworthy Land-to-Home Development & Construction Platform. Every step clearly conveys position, decisions, and forward actions, while technical sophistication remains easily accessible to professionals via the persistent Technical View.
