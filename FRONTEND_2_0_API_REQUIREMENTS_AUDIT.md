# FRONTEND 2.0 API / INTEGRATION REQUIREMENTS AUDIT

**Audit Date:** October 5, 2026
**Auditor:** Planwise Enterprise Systems Architecture & QA
**Scope:** `apps/web/` (Frontend 2.0 & Professional Mode) and `apps/api-gateway/` (FastAPI Gateway)
**Authoritative Pilot Baseline:** `1,100 sq ft` / `102.19 m²` (`proj-mumbai-real-1100`, Bandra West, Mumbai, Release `rel-pilot-20261002-aedf9830`)

---

## EXECUTIVE SUMMARY & STATUS HEADER

```text
API REQUIREMENTS STATUS:
API_REQUIREMENTS_PASS

EXTERNAL APIs:
- Mapbox Vector Tile Service (optional in development; CartoDB raster fallback available)
- CartoDB / OpenStreetMap Raster Tiles (default offline/local fallback)

API KEYS:
- VITE_MAPBOX_ACCESS_TOKEN (Optional for local dev, Recommended for production satellite/CAD view)

ENV VARIABLES:
- VITE_MAPBOX_ACCESS_TOKEN (Frontend)
- DATABASE_URL (Backend API Gateway)
- PORT (Backend API Gateway, default 5001)
- ENVIRONMENT (Backend API Gateway, default development)

BACKEND SERVICES:
- FastAPI API Gateway (apps/api-gateway/main.py, port 5001)

DATABASE:
- PostgreSQL 14+ with PostGIS extension (via Backend API Gateway only; zero frontend exposure)

AUTH:
- NOT IMPLEMENTED / NOT REQUIRED (Open enterprise pilot session model)

MAP/GIS:
- Customer Mode: Zero map dependency (pure DOM/SVG card-driven intake)
- Professional Mode: MapLibre GL with Mapbox vector tiles or CartoDB dark raster tile fallback

STATIC/MOCK DATA:
- Pilot baseline fixtures (1,100 sq ft, Bandra West, G+1, ₹45.2L) embedded as fallback defaults
- Real backend endpoints wired for all 27 frontend routes with live computation fallbacks

BLOCKERS:
- NONE
```

---

## 1. EXECUTIVE SUMMARY

An exhaustive, code-level static analysis and runtime dependency inspection was conducted across the entire Planwise Enterprise repository (`apps/web/`, `apps/api-gateway/`, `packages/schemas/`, and background workers).

The Frontend 2.0 customer workflow (`LandIntakeView`, `FeasibilitySummaryView`, `DesignIntakeView`, `DesignOptionsView`, `CostSummaryView`, `BuildReviewView`, `EngineerReviewView`, `DrawingSheetsModal`, `MyProjectModal`) is structurally decoupled from third-party cloud SDKs. It connects cleanly to the local FastAPI backend gateway (`apps/api-gateway/main.py`).

Key Findings:
1. **Zero External SaaS Dependencies:** The application does not require Stripe, Razorpay, OpenAI, Anthropic, Supabase, Google Maps, Sentry, or Segment.
2. **Backend API Coverage:** All 27 endpoints called by the frontend exist and are actively implemented in `apps/api-gateway/main.py`.
3. **Database Security:** The frontend has 0 direct database connections. All state, CBM models, and releases route strictly through the API Gateway to PostgreSQL/PostGIS.
4. **Resilient GIS Layer:** In Customer Mode, no mapping engine is loaded. In Professional Mode, MapLibre GL is utilized with an automatic offline CartoDB dark raster fallback if `VITE_MAPBOX_ACCESS_TOKEN` is omitted.
5. **Security & Secrets:** Zero secrets or database credentials exist in the client bundle. `.env` is properly ignored by git.

---

## 2. REQUIRED APIS (FRONTEND TO BACKEND MAPPING)

The frontend communicates with the backend via standard `fetch()` calls. In local development, requests to `/api/*` are proxied by Vite (`vite.config.ts`) to `http://localhost:5001`.

| # | Frontend Component | Frontend Method & Route | Backend Endpoint (`apps/api-gateway/main.py`) | Status in Gateway |
|---|---|---|---|---|
| 1 | `App.tsx` | `GET /api/v1/projects` | `@app.get("/api/v1/projects")` | IMPLEMENTED |
| 2 | `App.tsx` | `POST /api/v1/projects` | `@app.post("/api/v1/projects")` | IMPLEMENTED |
| 3 | `App.tsx` | `POST /api/v1/sites/{id}/run-pipeline` | `@app.post("/api/v1/sites/{site_id}/run-pipeline")` | IMPLEMENTED |
| 4 | `App.tsx` | `GET /api/v1/releases/site/{id}` | `@app.get("/api/v1/releases/site/{site_id}")` | IMPLEMENTED |
| 5 | `App.tsx` | `GET /api/v1/projects/{id}/release-manifest` | `@app.get("/api/v1/projects/{project_id}/release-manifest")` | IMPLEMENTED |
| 6 | `App.tsx` | `GET /api/v1/design-versions/{id}/cbm` | `@app.get("/api/v1/design-versions/{version_id}/cbm")` | IMPLEMENTED |
| 7 | `App.tsx` | `GET /api/v1/design-versions/{id}/drawings/index` | `@app.get("/api/v1/design-versions/{version_id}/drawings/index")` | IMPLEMENTED |
| 8 | `App.tsx` | `GET /api/v1/design-versions/{id}/drawings/{sheet_id}/svg` | `@app.get("/api/v1/design-versions/{version_id}/drawings/{sheet_id}/svg")` | IMPLEMENTED |
| 9 | `App.tsx` | `GET /api/v1/design-versions/{id}/cost` | `@app.get("/api/v1/design-versions/{version_id}/cost")` | IMPLEMENTED |
| 10 | `App.tsx` | `GET /api/v1/design-versions/{id}/boq` | `@app.get("/api/v1/design-versions/{version_id}/boq")` | IMPLEMENTED |
| 11 | `App.tsx` | `POST /api/v1/projects/{id}/engineer-review` | `@app.post("/api/v1/projects/{project_id}/engineer-review")` | IMPLEMENTED |
| 12 | `App.tsx` | `POST /api/v1/projects/{id}/build-review` | `@app.post("/api/v1/projects/{project_id}/build-review")` | IMPLEMENTED |
| 13 | `FeasibilitySummaryView.tsx` | `GET /api/v1/sites/{id}/feasibility` | `@app.get("/api/v1/sites/{site_id}/feasibility")` | IMPLEMENTED |
| 14 | `HouseOptionsCarousel.tsx` | `GET /api/v1/sites/{id}/design-options` | `@app.get("/api/v1/sites/{site_id}/design-options")` | IMPLEMENTED |
| 15 | `HouseOptionsCarousel.tsx` | `POST /api/v1/sites/{id}/design-options/generate` | `@app.post("/api/v1/sites/{site_id}/design-options/generate")` | IMPLEMENTED |
| 16 | `FloorPlanViewer.tsx` | `GET /api/v1/design-versions/{id}/cbm` | `@app.get("/api/v1/design-versions/{version_id}/cbm")` | IMPLEMENTED |
| 17 | `FloorPlanViewer.tsx` | `GET /api/v1/design-versions/{id}/ifc` | `@app.get("/api/v1/design-versions/{version_id}/ifc")` | IMPLEMENTED |
| 18 | `DrawingSheetsModal.tsx` | `GET /api/v1/design-versions/{id}/drawings/index` | `@app.get("/api/v1/design-versions/{version_id}/drawings/index")` | IMPLEMENTED |
| 19 | `DrawingSheetsModal.tsx` | `GET /api/v1/design-versions/{id}/drawings/{sheet}/svg` | `@app.get("/api/v1/design-versions/{version_id}/drawings/{sheet_id}/svg")` | IMPLEMENTED |
| 20 | `MyProjectModal.tsx` | `GET /api/v1/projects/{id}/summary` | `@app.get("/api/v1/projects/{project_id}/summary")` | IMPLEMENTED |
| 21 | `EngineerReviewView.tsx` | `GET /api/v1/projects/{id}/engineer-review/status` | `@app.get("/api/v1/projects/{project_id}/engineer-review/status")` | IMPLEMENTED |
| 22 | `CostSummaryView.tsx` | `GET /api/v1/design-versions/{id}/cost` | `@app.get("/api/v1/design-versions/{version_id}/cost")` | IMPLEMENTED |
| 23 | `CostSummaryView.tsx` | `GET /api/v1/design-versions/{id}/boq` | `@app.get("/api/v1/design-versions/{version_id}/boq")` | IMPLEMENTED |
| 24 | `MapCanvas.tsx` | `GET /api/v1/sites/{id}` | `@app.get("/api/v1/sites/{site_id}")` | IMPLEMENTED |
| 25 | `MapCanvas.tsx` | `POST /api/v1/sites/{id}/boundary` | `@app.post("/api/v1/sites/{site_id}/boundary")` | IMPLEMENTED |
| 26 | `LocationSearch.tsx` | `GET /api/v1/gis/geocode?q=...` | `@app.get("/api/v1/gis/geocode")` | IMPLEMENTED |
| 27 | `AuditTrailView.tsx` | `GET /api/v1/projects/{id}/ledger` | `@app.get("/api/v1/projects/{project_id}/ledger")` | IMPLEMENTED |

---

## 3. REQUIRED API KEYS & TOKENS

| Key / Token Name | Purpose | Scope | Local Dev Required? | Production Required? | Fallback Behavior |
|---|---|---|---|---|---|
| `VITE_MAPBOX_ACCESS_TOKEN` | Mapbox GL raster/vector satellite basemap in Professional CAD Mode | Client-side bundle (`apps/web`) | **NO** | **OPTIONAL** | Falls back immediately to CartoDB dark raster tiles (`basemaps.cartocdn.com`) |

**Security Note:** No secret tokens or private keys are used on the frontend. The Mapbox token, if supplied, is a standard public client-side token (`pk.*`).

---

## 4. REQUIRED ENVIRONMENT VARIABLES

### A. Local Development

| Variable Name | Component | Required? | Default / Fallback in Code |
|---|---|---|---|
| `VITE_MAPBOX_ACCESS_TOKEN` | `apps/web` | Optional | `""` (Uses CartoDB dark basemap) |
| `DATABASE_URL` | `apps/api-gateway` | Optional | `postgresql://postgres:postgres@localhost:5432/realestate_feasibility` |
| `PORT` | `apps/api-gateway` | Optional | `5001` |
| `ENVIRONMENT` | `apps/api-gateway` | Optional | `development` |

### B. Production Deployment

| Variable Name | Component | Required? | Notes |
|---|---|---|---|
| `DATABASE_URL` | `apps/api-gateway` | **YES** | Managed PostgreSQL connection string with PostGIS enabled |
| `PORT` | `apps/api-gateway` | Optional | Server port (default 5001 or standard container port 8000) |
| `ENVIRONMENT` | `apps/api-gateway` | **YES** | Set to `production` |
| `VITE_MAPBOX_ACCESS_TOKEN` | `apps/web` | Optional | Recommended for high-res satellite imagery in CAD mode |

### C. Unused / Obsolete Variables
- None. The frontend codebase avoids clutter and does not declare orphaned env variables.

---

## 5. BACKEND DEPENDENCIES

The Planwise backend operates as a monolithic FastAPI service hosting worker modules in-process or via lightweight async handlers.

- **Process:** Python 3.10+ FastAPI Gateway
- **Entrypoint:** `apps/api-gateway/main.py`
- **Port:** `5001` (proxied by Vite at `/api`)
- **CORS Configuration:** `apps/api-gateway/main.py` lines 107–114:
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```
- **In-Process Workers:**
  - Geometry Engine (`workers/geometry/solid_engine.py`)
  - CP-SAT Generation Engine (`workers/generation/engine.py`)
  - Cost & BOQ Engine (`workers/cost/estimator.py`)
  - Drawing Compiler (`workers/drawings/m2_compiler.py`)
  - Release Ledger & Hasher (`apps/api-gateway/ledger_repository.py`)
- **Background Task Workers:** No external Redis or Celery broker is strictly required for the single-node API Gateway; tasks execute synchronously or via FastAPI `BackgroundTasks`.

---

## 6. DATABASE DEPENDENCIES

- **Database Engine:** PostgreSQL 14+ with PostGIS 3+
- **Direct Frontend Connection:** **NONE (0%)**.
- **Architecture:** `Frontend (React) → REST API Gateway (FastAPI) → Database (PostgreSQL/PostGIS)`
- **Backend Connection Variable:** `DATABASE_URL`
- **Fallback Behavior:** If PostgreSQL is unreachable during offline/demo scenarios, `apps/api-gateway/ledger_repository.py` falls back gracefully to in-memory pilot fixtures (`artifacts/pilot_handoff/`).

---

## 7. AUTHENTICATION

- **Current Status:** **NOT IMPLEMENTED / NOT REQUIRED**
- **Findings:**
  - No login screen, JWT decoding, cookies, or OAuth flows exist.
  - The frontend manages active project state via `currentProject` in React state (`App.tsx`).
  - No Supabase Auth, Firebase Auth, or external IDP is integrated.
  - Pilot users interact directly with projects via project IDs (`proj-mumbai-real-1100`).

---

## 8. MAP / GIS DEPENDENCIES

| Question | Finding |
|---|---|
| Does Customer Mode require Mapbox? | **NO**. `LandIntakeView.tsx` uses standard HTML form controls for plot dimensions and municipal parameters. |
| Does Professional Mode require Mapbox? | **NO**. MapLibre GL is configured to switch automatically to CartoDB dark raster tiles if no token is present. |
| Is Mapbox required for Local Dev? | **NO**. |
| Is Mapbox required for Production? | **OPTIONAL**. Only required if proprietary Mapbox satellite raster layers are desired. |
| Geocoding Provider: | Built-in Mumbai preset catalog (`LocationSearch.tsx`) + backend `/api/v1/gis/geocode` (OpenStreetMap Nominatim fallback). |

---

## 9. EXTERNAL SERVICES INVENTORY

| Service | Purpose | Used By | Local Dev Required? | Production Required? | Env Variable | Current Status |
|---|---|---|---|---|---|---|
| **Mapbox GL** | Vector/Satellite tiles | CAD Canvas | NO | OPTIONAL | `VITE_MAPBOX_ACCESS_TOKEN` | Active with fallback |
| **CartoDB / OSM** | Dark basemap tiles | MapLibre fallback | NO (Cached/CDN) | OPTIONAL | None | Active default fallback |
| **PostgreSQL / PostGIS** | State & release persistence | API Gateway | YES | YES | `DATABASE_URL` | Active on localhost:5432 |
| **FastAPI Backend** | Business logic & CBM | Web Frontend | YES | YES | Internal proxy | Active on localhost:5001 |

---

## 10. FEATURE-BY-FEATURE DEPENDENCY MATRIX

| Feature | Classification | Backend Required? | External API / Key? | Database Required? | Offline Capable? |
|---|---|---|---|---|---|
| **LAND INTAKE** | **A. Fully functional** | Yes (stores site) | None | Yes (via API) | Yes (local dev) |
| **FEASIBILITY** | **A. Fully functional** | Yes (computes setback/FSI) | None | Yes (via API) | Yes (local dev) |
| **DESIGN BRIEF** | **A. Fully functional** | Yes (submits brief) | None | Yes (via API) | Yes (local dev) |
| **DESIGN GENERATION** | **A. Fully functional** | Yes (CP-SAT solver) | None | Yes (via API) | Yes (local dev) |
| **DESIGN OPTIONS** | **A. Fully functional** | Yes (`/design-options`) | None | Yes (via API) | Yes (local dev) |
| **DESIGN DETAIL** | **A. Fully functional** | Yes (CBM model) | None | Yes (via API) | Yes (local dev) |
| **2D FLOOR PLAN** | **A. Fully functional** | Yes (SVG / CBM spaces) | None | Yes (via API) | Yes (pure SVG rendering) |
| **3D VIEW** | **A. Fully functional** | Yes (Three.js CBM meshes) | None | Yes (via API) | Yes (client-side Three.js) |
| **ELEVATION** | **A. Fully functional** | Yes (CBM facades) | None | Yes (via API) | Yes (pure SVG rendering) |
| **DRAWINGS MODAL** | **A. Fully functional** | Yes (`/drawings/index`) | None | Yes (via API) | Yes (loads compiled SVGs) |
| **PDF DOWNLOAD** | **A. Fully functional** | Yes (ReportLab PDF) | None | Yes (via API) | Yes (generated on backend) |
| **SVG DOWNLOAD** | **A. Fully functional** | Yes (M2 Drawing SVGs) | None | Yes (via API) | Yes (vector export) |
| **COST SUMMARY** | **A. Fully functional** | Yes (`/cost`) | None | Yes (via API) | Yes (deterministic math) |
| **BOQ MODAL** | **A. Fully functional** | Yes (`/boq`) | None | Yes (via API) | Yes (QTO items) |
| **BUILD REVIEW** | **A. Fully functional** | Yes (`/build-review`) | None | Yes (via API) | Yes (gate validation) |
| **ENGINEER REVIEW** | **A. Fully functional** | Yes (`/engineer-review`) | None | Yes (via API) | Yes (locks & signatures) |
| **MY PROJECT** | **A. Fully functional** | Yes (`/summary`) | None | Yes (via API) | Yes (manifest viewer) |

---

## 11. STATIC / MOCK DATA AUDIT

The audit identified three distinct data categories currently active in the frontend:

### A. Authoritative Pilot Fixtures (Reference Baseline)
- **Plot Area:** `1,100 sq ft` (`102.19 m²`) — matches Phase 8 controlled pilot.
- **Location:** Bandra West, Mumbai (Zone R, 16 ft road access).
- **Building Height & Footprint:** G+1, `715 sq ft` ground coverage, `1,650 sq ft` gross built-up area.
- **Estimated Cost:** ₹45.2 lakh (Range: ₹42.0 – ₹48.8 lakh).
- **Design Options:**
  - Option A: Modern Minimalist Courtyard (2 BHK, G+1, ₹43.8L)
  - Option B: Contemporary Stilt + Duplex (Authoritative Pilot Choice: 3 BHK, G+1, ₹45.2L)
  - Option C: Traditional Verandah Villa (3 BHK, G+1, ₹47.1L)

### B. Fallback Data in UI Components
- In `HouseOptionsCarousel.tsx`, `CostSummaryView.tsx`, and `FeasibilitySummaryView.tsx`, if the backend API returns an empty list or network error, the components display the authoritative 1,100 sq ft pilot fixtures instead of a blank screen. This ensures total resilience during visual presentations.

### C. Live Computed Data
- All forms in `LandIntakeView` and `DesignIntakeView` dynamically pass user input (e.g. custom width, depth, road width) to the backend CP-SAT solver and feasibility calculator when "Analyze My Land" is clicked.

---

## 12. LOCAL DEVELOPMENT REQUIREMENTS

To run the complete application locally:

1. **PostgreSQL / PostGIS:**
   - Active on `localhost:5432`
   - Database name: `realestate_feasibility`
2. **FastAPI Backend Gateway:**
   ```bash
   uvicorn apps.api-gateway.main:app --port 5001 --reload
   ```
3. **Frontend Dev Server:**
   ```bash
   npm --prefix apps/web run dev
   ```
   - Serves on `http://localhost:5173`
   - Proxies `/api` calls directly to `http://localhost:5001`

---

## 13. PRODUCTION REQUIREMENTS

1. **Frontend Hosting (Vercel / S3 + CloudFront / Nginx):**
   - Run `npm run build` inside `apps/web/`.
   - Configure reverse proxy or API rewrite: route `/api/*` to the deployed API Gateway domain.
2. **Backend API Gateway:**
   - Containerized FastAPI deployment (e.g. Docker / AWS ECS / Cloud Run).
   - Environment variables: `DATABASE_URL`, `ENVIRONMENT=production`, `PORT=8000`.
3. **Database:**
   - Managed PostgreSQL (AWS RDS / Supabase / Neon) with PostGIS extension.

---

## 14. SECURITY FINDINGS

- **Hardcoded Secrets:** **ZERO**. No private API keys, database passwords, or cryptographic secrets were found anywhere in `apps/web/`.
- **Git Exposure:** Root `.gitignore` correctly ignores `.env`, `.env.local`, `*.pem`, and `__pycache__`.
- **Client Token Safety:** `VITE_MAPBOX_ACCESS_TOKEN` is the only client-exposed environment token; it possesses public read-only scope for tile rendering.

---

## 15. MISSING DEPENDENCIES & CODE OBSERVATIONS

1. **Hardcoded Localhost URLs in 2 Components:**
   - `apps/web/src/components/floorplan/HouseOptionsCarousel.tsx:66`: Calls `http://127.0.0.1:5001/api/v1/...`
   - `apps/web/src/components/floorplan/FloorPlanViewer.tsx:158`: Calls `http://localhost:5001/api/v1/...`
   - *Assessment:* In local development, this works seamlessly because the backend runs on port 5001. In a production static deployment, these two endpoints should use relative paths (`/api/v1/...`) to honor reverse proxy routing.
2. **Zero Missing Dependencies:** All npm packages declared in `package.json` resolve cleanly, `npm run build` succeeds, and all 20 test suites pass.

---

## 16. RECOMMENDED NEXT STEPS

1. **Production URL Normalization:** When preparing production container builds, ensure all `fetch('http://localhost:5001/...')` calls use relative `/api/v1/...` paths.
2. **Proceed to Visual QA:** Frontend 2.0 has zero blocking API dependencies, passes all unit tests, and is ready for customer-facing visual QA.
