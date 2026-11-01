# Volume III — Frontend Application Deep Dive

## 1. Application Entry Point and Architecture
The frontend is a modern single-page application (SPA) built with **React 18.3.1**, **TypeScript 5.6.3**, and **Vite**. The build outputs are static assets optimized for rapid client-side routing and hardware-accelerated canvas rendering.

- **Entry File:** `apps/web/src/main.tsx` initializes the React DOM root and wraps the application with `AuthProvider` and `ProjectProvider`.
- **Top-Level Orchestrator:** `apps/web/src/App.tsx` controls the primary workflow navigation, header state, active project switcher, and view routing.

---

## 2. Global State & Context Management

### 2.1 `AuthContext` (`apps/web/src/context/AuthContext.tsx`)
Provides identity and authorization context across all components:
- `user`: Authenticated user entity (`id`, `email`, `role`, `organization_id`, `full_name`).
- `token`: Active JWT Bearer token stored securely in browser `localStorage`.
- `login(credentials)`: Authenticates against Supabase Auth endpoint or initiates offline deterministic developer bypass.
- `logout()`: Clears credentials, invalidates session state, and redirects to login modal.
- `hasRole(requiredRole)`: Utility method for conditional UI rendering based on enterprise roles (`CHIEF_ENGINEER`, `STRUCTURAL_ENGINEER`, `ESTIMATOR`, `CLIENT`).

### 2.2 `ProjectContext` (`apps/web/src/context/ProjectContext.tsx`)
Maintains current project lifecycle state:
- `currentProject`: Active project entity (plot size, orientation, zoning, active design option).
- `activeCBM`: In-memory Canonical Building Model representation for live floor plan mutations.
- `loadProject(id)`: Fetches project entity from `/api/v1/projects/{id}` and updates local state.

---

## 3. Screen-by-Screen Component Hierarchy & Workflows

### 3.1 Land Intake Screen (`LandInputView.tsx`)
- **Purpose:** Ingest cadastral land coordinates and frontage road dimensions.
- **Inputs:** Polygon vertex coordinates `[(x0, y0), (x1, y1), ...]`, road width in meters, municipal jurisdiction (Mumbai / Bengaluru).
- **Interactive Canvas:** Renders plot geometry in real time with coordinate validation, aspect ratio calculation, and orientation Compass rose.
- **API Dispatch:** `POST /api/v1/projects` creates the project entity with boundary polygon payload.

### 3.2 Feasibility Analysis Screen (`FeasibilityView.tsx`)
- **Purpose:** Displays statutory zoning envelopes, mandatory setbacks, and maximum buildable volume.
- **Visuals:** Dual-layer canvas showing plot boundary (blue) and statutory buildable envelope (green) with dimensioned setbacks.
- **Metrics Card:**
  - Total Plot Area: e.g. 1,500 sq ft (139.35 sq m).
  - Permissible Ground Coverage: 60% (83.61 sq m).
  - Permissible FSI / FAR: 1.50 (209.03 sq m permissible built-up area).
  - Front Setback: 3.0 m | Rear Setback: 2.0 m | Side Setbacks: 1.5 m each.

### 3.3 Design Brief & Optimization Screen (`DesignBriefView.tsx`)
- **Purpose:** Collects spatial program requirements (e.g. 2BHK vs 3BHK, master bedroom location, parking bays).
- **Execution:** Dispatches `POST /api/v1/design-options` to trigger the Google OR-Tools CP-SAT solver.
- **Results Presentation:** Displays 3 deterministic layout alternatives (Option A: Balanced Living, Option B: Vaastu Compliant, Option C: Maximum Efficiency).

### 3.4 Floor Plan Detail & Mutation View (`FloorPlanDetailView.tsx`)
- **Purpose:** Interactive CAD-style visualizer for inspecting and mutating room dimensions.
- **Features:** Room selection, dimension modification sliders (e.g., expanding living room by +1.5 ft), instant boundary validation, and real-time CBM recalculation.

### 3.5 Bill of Quantities & Cost View (`CostSummaryView.tsx`)
- **Purpose:** Displays deterministic material quantities and cost waterfall.
- **Tables:** Structured tables for Concrete (cu m), Reinforcement Steel (MT), Brick Masonry (sq m), Plastering (sq m), Flooring (sq ft), and Painting.
- **Waterfall:** Base Construction Cost $\rightarrow$ Overhead (10%) $\rightarrow$ Contractor Profit (15%) $\rightarrow$ Contingency (5%) $\rightarrow$ GST Tax (18%).

### 3.6 Engineer Review & Sign-Off Dashboard (`EngineerReviewView.tsx`)
- **Purpose:** High-security interface for reviewing and certifying project milestones G0 through G6.
- **Security Check:** Evaluates active user's credentials; gates action buttons for unauthorized roles.
- **Sign-Off Action:** Records cryptographic approval with reviewer timestamp, comments, and role identity via `POST /api/v1/projects/{id}/reviews`.

---

## 4. Live Frontend E2E Verification Evidence (13 Forensic Screenshots)
The entire frontend was verified using automated headless Google Chrome (`scripts/live_frontend_e2e.js`) across 12 sequential phases. All 13 forensic screenshots were captured at 1280x800 resolution and verified:


<div class="diagram-container">
  <div style="font-weight:bold; font-size:9pt; margin-bottom:4px; color:#0f172a;">Phase 1: Cadastral Land Intake (1,500 sq ft Plot Boundary Intake)</div>
  <img src="file:///Users/surajkumar/Desktop/Real_state_dev/artifacts/e2e_live_test/01_1500_land_input.png" class="screenshot-img" alt="Phase 1: Cadastral Land Intake (1,500 sq ft Plot Boundary Intake)"/>
  <div class="diagram-caption">Interactive vertex coordinate intake with real-time perimeter, area, and orientation validation. (Captured in live Chrome session on http://localhost:5173)</div>
</div>


<div class="diagram-container">
  <div style="font-weight:bold; font-size:9pt; margin-bottom:4px; color:#0f172a;">Phase 2: Statutory Feasibility Envelope (Mumbai DCPR 2034)</div>
  <img src="file:///Users/surajkumar/Desktop/Real_state_dev/artifacts/e2e_live_test/02_1500_feasibility.png" class="screenshot-img" alt="Phase 2: Statutory Feasibility Envelope (Mumbai DCPR 2034)"/>
  <div class="diagram-caption">Dual-layer canvas rendering statutory front, rear, and side setbacks with permissible FSI metrics. (Captured in live Chrome session on http://localhost:5173)</div>
</div>


<div class="diagram-container">
  <div style="font-weight:bold; font-size:9pt; margin-bottom:4px; color:#0f172a;">Phase 3: Spatial Program & Design Brief Intake</div>
  <img src="file:///Users/surajkumar/Desktop/Real_state_dev/artifacts/e2e_live_test/03_1500_design_intake.png" class="screenshot-img" alt="Phase 3: Spatial Program & Design Brief Intake"/>
  <div class="diagram-caption">Configuration form for room requirements, master bedroom orientation, and family program. (Captured in live Chrome session on http://localhost:5173)</div>
</div>


<div class="diagram-container">
  <div style="font-weight:bold; font-size:9pt; margin-bottom:4px; color:#0f172a;">Phase 4: CP-SAT Combinatorial Optimization Alternatives</div>
  <img src="file:///Users/surajkumar/Desktop/Real_state_dev/artifacts/e2e_live_test/04_1500_design_options.png" class="screenshot-img" alt="Phase 4: CP-SAT Combinatorial Optimization Alternatives"/>
  <div class="diagram-caption">Three Pareto-optimal floor plan alternatives generated via Google OR-Tools CP-SAT (seed=42). (Captured in live Chrome session on http://localhost:5173)</div>
</div>


<div class="diagram-container">
  <div style="font-weight:bold; font-size:9pt; margin-bottom:4px; color:#0f172a;">Phase 5: Multi-Tenant Project Switcher & Workspace Dialog</div>
  <img src="file:///Users/surajkumar/Desktop/Real_state_dev/artifacts/e2e_live_test/05_1500_my_project_modal.png" class="screenshot-img" alt="Phase 5: Multi-Tenant Project Switcher & Workspace Dialog"/>
  <div class="diagram-caption">Enterprise modal showing project isolation, plot sizes, and status tracking. (Captured in live Chrome session on http://localhost:5173)</div>
</div>


<div class="diagram-container">
  <div style="font-weight:bold; font-size:9pt; margin-bottom:4px; color:#0f172a;">Phase 6: Architectural Floor Plan Blueprint Detail View</div>
  <img src="file:///Users/surajkumar/Desktop/Real_state_dev/artifacts/e2e_live_test/06_1500_floor_plan_detail.png" class="screenshot-img" alt="Phase 6: Architectural Floor Plan Blueprint Detail View"/>
  <div class="diagram-caption">Detailed vector floor plan showing room dimensions, wall thicknesses, door swings, and window schedules. (Captured in live Chrome session on http://localhost:5173)</div>
</div>


<div class="diagram-container">
  <div style="font-weight:bold; font-size:9pt; margin-bottom:4px; color:#0f172a;">Phase 7: Real-Time Spatial Program Mutation (2BHK to 3BHK)</div>
  <img src="file:///Users/surajkumar/Desktop/Real_state_dev/artifacts/e2e_live_test/07_3bhk_mutation_floor_plan.png" class="screenshot-img" alt="Phase 7: Real-Time Spatial Program Mutation (2BHK to 3BHK)"/>
  <div class="diagram-caption">Dynamic layout re-solving with instant CBM recalculation and boundary validation. (Captured in live Chrome session on http://localhost:5173)</div>
</div>


<div class="diagram-container">
  <div style="font-weight:bold; font-size:9pt; margin-bottom:4px; color:#0f172a;">Phase 8: Interactive Room Dimension Slider Mutation</div>
  <img src="file:///Users/surajkumar/Desktop/Real_state_dev/artifacts/e2e_live_test/08_room_dimension_mutation.png" class="screenshot-img" alt="Phase 8: Interactive Room Dimension Slider Mutation"/>
  <div class="diagram-caption">Dynamic slider control expanding living room by +1.5 ft with immediate boundary recalculation. (Captured in live Chrome session on http://localhost:5173)</div>
</div>


<div class="diagram-container">
  <div style="font-weight:bold; font-size:9pt; margin-bottom:4px; color:#0f172a;">Phase 9: Medium Residential Parcel Optimization (2,400 sq ft)</div>
  <img src="file:///Users/surajkumar/Desktop/Real_state_dev/artifacts/e2e_live_test/09_2400_floor_plan.png" class="screenshot-img" alt="Phase 9: Medium Residential Parcel Optimization (2,400 sq ft)"/>
  <div class="diagram-caption">3BHK duplex configuration on medium urban parcel with courtyard ventilation. (Captured in live Chrome session on http://localhost:5173)</div>
</div>


<div class="diagram-container">
  <div style="font-weight:bold; font-size:9pt; margin-bottom:4px; color:#0f172a;">Phase 10: Luxury Estate Parcel Optimization (10,000 sq ft)</div>
  <img src="file:///Users/surajkumar/Desktop/Real_state_dev/artifacts/e2e_live_test/10_10000_floor_plan.png" class="screenshot-img" alt="Phase 10: Luxury Estate Parcel Optimization (10,000 sq ft)"/>
  <div class="diagram-caption">5BHK luxury estate layout with swimming pool setback, double garage, and servant quarters. (Captured in live Chrome session on http://localhost:5173)</div>
</div>


<div class="diagram-container">
  <div style="font-weight:bold; font-size:9pt; margin-bottom:4px; color:#0f172a;">Phase 11: IS 1200 Bill of Quantities & Cost Waterfall</div>
  <img src="file:///Users/surajkumar/Desktop/Real_state_dev/artifacts/e2e_live_test/11_cost_summary.png" class="screenshot-img" alt="Phase 11: IS 1200 Bill of Quantities & Cost Waterfall"/>
  <div class="diagram-caption">Itemized concrete, steel, masonry, and plaster quantities with multi-tier financial waterfall. (Captured in live Chrome session on http://localhost:5173)</div>
</div>


<div class="diagram-container">
  <div style="font-weight:bold; font-size:9pt; margin-bottom:4px; color:#0f172a;">Phase 12: Pre-Construction Technical Compliance Checklist</div>
  <img src="file:///Users/surajkumar/Desktop/Real_state_dev/artifacts/e2e_live_test/12_build_review.png" class="screenshot-img" alt="Phase 12: Pre-Construction Technical Compliance Checklist"/>
  <div class="diagram-caption">Automated pre-flight validation verifying clear headroom, egress widths, and MEP shafts. (Captured in live Chrome session on http://localhost:5173)</div>
</div>


<div class="diagram-container">
  <div style="font-weight:bold; font-size:9pt; margin-bottom:4px; color:#0f172a;">Phase 13: Multi-Stage Engineering Review Gate Dashboard (G0–G6)</div>
  <img src="file:///Users/surajkumar/Desktop/Real_state_dev/artifacts/e2e_live_test/13_engineer_review.png" class="screenshot-img" alt="Phase 13: Multi-Stage Engineering Review Gate Dashboard (G0–G6)"/>
  <div class="diagram-caption">Role-restricted engineer certification interface for G0 through G6 gate sign-offs. (Captured in live Chrome session on http://localhost:5173)</div>
</div>

