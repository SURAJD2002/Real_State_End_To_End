# Planwise Enterprise — Land-to-Home Development & Construction Platform

[![Controlled Pilot Readiness: PASS](https://img.shields.io/badge/Pilot%20Readiness-PASS-emerald?style=flat-square)](PLANWISE_PILOT_READINESS_REPORT.md)
[![Security Verification: VERIFIED](https://img.shields.io/badge/Security-JWKS%20ES256%20Verified-blue?style=flat-square)](PLANWISE_PILOT_READINESS_REPORT.md)
[![Database: PostgreSQL 16 + PostGIS](https://img.shields.io/badge/Database-PostgreSQL%2016%20%2B%20PostGIS-336791?style=flat-square)](supabase/migrations)
[![Frontend: React 19 + Vite 6](https://img.shields.io/badge/Frontend-React%2019%20%2B%20Vite%206-61DAFB?style=flat-square)](apps/web)
[![Backend: FastAPI + Pydantic v2](https://img.shields.io/badge/Backend-FastAPI%20%2B%20Pydantic%20v2-009688?style=flat-square)](apps/api-gateway)

An institutional-grade, end-to-end **Land-to-Home Development & Construction Platform** built according to the **Development-Ready Delta Specification** and the **Archonet Planwise Engineering Master Plan**.

---

> [!IMPORTANT]
> ### ⚖️ Professional Engineering & Statutory Compliance Disclaimer
> - **Computational validation is NOT professional certification.** Automated evaluations compute rule-based statutory parameters (e.g., Mumbai MCGM DCPR 2034, NBC 2016, IS 456), but **do not constitute professional engineering stamps or architectural licensure**.
> - **Automated reviews do NOT authorize construction.** Gates G0 through G8 and cryptographic release fingerprints provide immutable evidence and auditability; physical site release, groundbreaking, and construction kickoff strictly require attributable wet-ink/digital stamps and formal statutory building sanctions issued by the relevant local municipal authority.
> - Planwise Enterprise is an engineering coordination tool designed to assist licensed architects, structural engineers, and developers.

---

## 1. Project Overview & Problem Statement

Residential real estate development faces severe fragmentation across the project lifecycle:
- **Spatial Uncertainty:** Cadastral parcel intake frequently relies on imprecise boundary descriptions and uncalibrated paper records.
- **Regulatory Disconnect:** Statutory zoning calculations (FSI, TDR, setback rules) are performed manually, introducing non-compliance risks and costly revision cycles.
- **Siloed BIM & Costing:** Architectural models are detached from Bill of Quantities (BOQ), leading to budget overruns and discrepancies between designs and construction estimates.
- **Unverifiable Handoffs:** Engineering reviews, site releases, and contractor milestones lack immutable provenance, resulting in dispute risks.

**Planwise Enterprise** addresses this fragmentation with a deterministic, mathematically unified digital pipeline bridging six core project lifecycle stages:

$$\textbf{Land} \longrightarrow \textbf{Feasibility} \longrightarrow \textbf{Design} \longrightarrow \textbf{Cost / BOQ} \longrightarrow \textbf{Build Lock} \longrightarrow \textbf{Engineer Review} \longrightarrow \textbf{Handoff}$$

---

## 2. Product Scope & Intended Users

Planwise Enterprise provides dedicated workspaces tailored to the key participants in property development:

| User Persona | Key Capabilities in Platform |
| :--- | :--- |
| **Landowners & Customers** | Interactive CAD parcel digitizer, debounced auto-save (600ms), real-time DCPR 2034 feasibility HUD, parametric house options carousel, 2D interactive floor plans, and cryptographic `[REQUEST BUILD]` locking. |
| **Licensed Engineers & Architects** | Attributable verification dashboard, G0–G8 engineering review gates, structural and MEP clash detection checks, immutable release fingerprint inspection, open-standard **IFC4 STEP** exports, and 9-sheet publication drawing compiler. |
| **Quantity Surveyors & Estimators** | Model-linked Bill of Quantities (BOQ) with CPWD DSR rate snapshots (Standard, Premium, Luxury tiers), material takeoffs (QTO), and deterministic CPM construction schedules. |
| **Enterprise Tenant Administrators** | Multi-tenant organization isolation, zero-trust Role-Based Access Control (RBAC: `OWNER`, `ADMIN`, `MEMBER`, `VIEWER`), and Supabase PostgreSQL persistence with Row Level Security (RLS). |

---

## 3. End-to-End Workflow

```mermaid
flowchart LR
    A[1. Land Intake] -->|WGS84 PostGIS Polygon| B[2. Statutory Feasibility]
    B -->|DCPR 2034 Setbacks & FSI| C[3. Parametric Design]
    C -->|OR-Tools CP-SAT Layouts| D[4. Traceable BOQ & CPM]
    D -->|Model Takeoff & CPWD Rates| E[5. Immutable Build Lock]
    E -->|SHA-256 Release Fingerprint| F[6. Engineer Review G0-G8]
    F -->|Attributable Sign-off| G[7. BIM IFC4 & Drawing Handoff]
```

1. **Land Intake:** Digital boundary definition via interactive map or parcel coordinates, converted into WGS84 PostGIS polygons (`SRID 4326`) with local metric transformations (UTM Zone 43N).
2. **Statutory Feasibility:** Deterministic rule engine evaluating Mumbai MCGM DCPR 2034 (Regulation 30, 31, 33) and Bangalore BBMP rules to compute permissible FSI, directional setbacks, and buildable footprints.
3. **Parametric Design:** Constraint-driven discrete space solver (Google OR-Tools CP-SAT) generating compliant floor plans (`compact_2bhk`, `family_3bhk`, `duplex_3bhk`) with structural column grids ($300\text{mm} \times 450\text{mm}$).
4. **Traceable BOQ & Cost:** Dynamic Quantity Takeoff (`quantity = measure(model_elements)`) calculating concrete, steel, masonry, and finishes mapped to versioned CPWD DSR rate cards and a 16-activity CPM schedule.
5. **Immutable Build Lock:** Customer confirmation dialog requiring mandatory legal acknowledgements to freeze the design version and generate a composite cryptographic SHA-256 release fingerprint:
   $$\text{Fingerprint} = \text{SHA-256}(\text{geometry} \parallel \text{regulation} \parallel \text{design} \parallel \text{boq} \parallel \text{schedule})$$
6. **Engineer Review (G0–G8):** Digital verification gates for boundary provenance, structural checks, MEP clearance, and commercial scope confirmation.
7. **Handoff:** Generation of open-standard **IFC4 STEP** BIM models, 9-sheet architectural publication drawings (SVG/PDF), and customer home reports.

---

## 4. Verified System Architecture

```
                                  +---------------------------------------------+
                                  |      Customer & Engineer Web Studio         |
                                  |             (React 19 + Vite 6)             |
                                  |  - Mapbox / Leaflet CAD Parcel Digitizer    |
                                  |  - Statutory Feasibility Heads-Up Display   |
                                  |  - Parametric House Floor Plan Viewer (2D)  |
                                  |  - Traceable BOQ Takeoff Explorer           |
                                  |  - Attributable G0-G8 Review Gate Console   |
                                  |  - Supabase Auth Client (ES256 Session)     |
                                  +----------------------+----------------------+
                                                         |
                                            (HTTP / REST / Bearer JWT)
                                                         v
                                  +---------------------------------------------+
                                  |          FastAPI Gateway Service            |
                                  |            (Python 3.12+ / 3.14)            |
                                  |  - JWKS ES256 Token Signature Verifier      |
                                  |  - Zero-Trust Multi-Tenant RBAC Resolver    |
                                  |  - Project & PostGIS Spatial Repositories   |
                                  |  - Feasibility, CBM, and QTO Controllers    |
                                  |  - PDF & Drawing Sheet Compiler Pipeline    |
                                  +----+--------------------+--------------+----+
                                       |                    |              |
                 +---------------------+                    |              +---------------------+
                 v                                          v                                    v
+---------------------------------+  +-------------------------------+  +---------------------------------+
|     Computational Workers       |  |  Supabase PostgreSQL 16 DB    |  |       Object & File Store       |
| - workers/geometry (UTM 43N)    |  |  - PostGIS 3.3+ Spatial Engine|  | - S3 / MinIO Object Storage     |
| - workers/regulation (DCPR 2034)|  |  - 34 RLS-Protected Tables    |  | - IFC4 STEP Physical Files      |
| - workers/generation (CP-SAT)   |  |  - Security-Definer Org Map   |  | - Compiled 9-Sheet SVG / PDFs   |
| - workers/qto (CPWD DSR BOQ)    |  |  - Immutable Releases & Audits|  | - Customer Home Reports         |
| - workers/release (IFC4 BIM)    |  |  - Transactional Pooler (6543)|  |                                 |
+---------------------------------+  +-------------------------------+  +---------------------------------+
```

---

## 5. Technology Stack & Actual Versions

| Tier | Technologies & Actual Versions | Purpose |
| :--- | :--- | :--- |
| **Frontend** | React `19.0.0`, Vite `6.4.4`, TypeScript `5.7.3`, TailwindCSS `3.4.17`, Lucide Icons | Responsive Customer Studio, CAD viewer, and Engineer Console |
| **Backend** | Python `3.14.4` (compatible `3.12+`), FastAPI `0.115.0`, Uvicorn `0.30.6`, Starlette `0.38.6` | High-throughput stateless RESTful API Gateway |
| **Data & Validation**| Pydantic `2.9.2`, Shapely `2.0.6`, PostGIS, PyJWT `2.15.1`, Cryptography `50.0.2` | Geometric clipping, schema enforcement, and cryptographic JWKS verification |
| **Optimization** | Google OR-Tools `9.11.4210` (CP-SAT Solver) | Discrete combinatorial room placement and Pareto multi-objective ranking |
| **Database** | PostgreSQL `16.3` with PostGIS `3.3+` (Supabase Managed Cloud / Local Docker) | Spatial parcel geometries, tenant isolation, and audit ledgers |
| **Authentication** | Supabase Auth (`@supabase/supabase-js` `2.49.1`), Asymmetric `ES256` JWKS | Zero-trust session management and token verification |
| **Export Formats** | IFC4 (ISO 16739-1:2018 STEP), SVG, PDF (ReportLab `4.2.5`), CSV | Open-standard BIM interchange, publication drawing sets, and reports |

---

## 6. Repository Directory Structure

```
Real_State_End_To_End/
├── apps/
│   ├── api-gateway/            # FastAPI stateless REST API & authentication gateway
│   │   ├── main.py             # Route handlers & controller endpoints
│   │   ├── auth.py             # JWKS ES256 & HS256 cryptographic verification
│   │   ├── postgres_repository.py # Production PostgreSQL & PostGIS transactional repository
│   │   └── ledger_repository.py# Append-only audit trail and review ledger
│   └── web/                    # React 19 + TypeScript + Vite frontend application
│       ├── src/
│       │   ├── components/     # UI Views (CAD intake, Feasibility HUD, Review, BOQ)
│       │   │   ├── auth/       # Login, Register, Forgot Password, Reset Password views
│       │   │   ├── CadBlueprintView.tsx # Vector CAD interactive blueprint
│       │   │   └── DrawingSheetsModal.tsx # 9-Sheet architectural drawing viewer
│       │   ├── context/        # AuthContext & Session management
│       │   ├── lib/            # supabaseClient.ts client instance
│       │   ├── types.ts        # Shared TypeScript domain contracts
│       │   └── App.tsx         # Root application router and workflow state
│       ├── package.json        # Frontend dependencies
│       └── vite.config.ts      # Vite bundler configuration & /api proxy
├── packages/
│   ├── schemas/                # Pydantic v2 schemas (CBM, QTO, BOQ, Brief, Release)
│   ├── rules/                  # Statutory regulation packs (Mumbai DCPR 2034, BBMP)
│   └── shared-types/           # Shared cross-service type contracts
├── workers/
│   ├── geometry/               # PostGIS / UTM 43N coordinate projection & boundary clipping
│   ├── regulation/             # Mumbai DCPR 2034 statutory rule engine & explainability traces
│   ├── generation/             # CP-SAT house floor plan generator & 9-sheet drawing compiler
│   ├── qto/                    # Quantity Takeoff, CPWD DSR rate snapshots, and BOQ rollup
│   ├── schedule/               # 16-activity CPM precedence network scheduler
│   ├── release/                # SHA-256 release fingerprinting & open-standard IFC4 BIM compiler
│   ├── reports/                # Customer Home Report and Technical Dossier builders
│   └── evidence/               # Surveyor site evidence intake & provenance
├── supabase/
│   └── migrations/             # Production versioned PostgreSQL migrations (01 through 08)
├── tests/                      # Automated unit, integration, and security test suites
│   ├── test_auth_security_negative.py # 11 negative security tests (forged JWT, RBAC, IDOR)
│   ├── test_cross_tenant_isolation.py # 7 RLS database isolation tests
│   ├── test_persistence_and_auth_workflow.py # End-to-end persistence & process restart tests
│   ├── test_real_plot_end_to_end.py   # Canonical 1,100 sq ft plot end-to-end pipeline
│   └── test_drawing_compiler.py       # 9-sheet architectural drawing compilation test
├── docs/                       # Technical architecture blueprints & reports index
├── artifacts/                  # Generated audit evidence, sample IFC4 files, and PDF sheets
├── assets/                     # Genuine UI screenshots and architectural diagrams
├── .env.example                # Safe environment variable configuration template
├── CONTRIBUTING.md             # Developer contribution guidelines
├── SECURITY.md                 # Security policy & responsible vulnerability disclosure
└── README.md                   # Authoritative repository documentation
```

---

## 7. Implementation Status Across Project Phases

| Phase | Description | Status | Verification Evidence |
| :--- | :--- | :---: | :--- |
| **Phase 1** | Spatial parcel intake, PostGIS boundaries, and coordinate normalization | **VERIFIED** | `tests/test_m1_site_and_rules.py` (PASS) |
| **Phase 2** | Mumbai MCGM DCPR 2034 statutory regulation engine | **VERIFIED** | `tests/test_real_plot_end_to_end.py` (PASS) |
| **Phase 3** | Parametric CP-SAT house generation (2BHK, 3BHK, Duplex) | **VERIFIED** | `tests/test_m2_generator_and_solids.py` (PASS) |
| **Phase 4** | Model-linked QTO, CPWD DSR rate cards, and CPM schedule | **VERIFIED** | `tests/test_m3_qto_and_cost.py` (PASS) |
| **Phase 5** | Cryptographic build lock, SHA-256 fingerprint, and IFC4 BIM | **VERIFIED** | `tests/test_pilot_handoff_integrity.py` (PASS) |
| **Phase 6** | Immutable Engineer Review Console & G0–G8 verification gates | **VERIFIED** | `tests/test_phase7_engineer_review.py` (PASS) |
| **Phase 7** | 9-Sheet architectural drawing compilation & publication set | **VERIFIED** | `tests/test_drawing_compiler.py` (PASS) |
| **Phase 8 (Security & Persistence)** | Supabase PostgreSQL 16 persistence, ES256 JWKS auth, RLS tenant isolation | **VERIFIED** | `tests/test_auth_security_negative.py` (PASS), `tests/test_cross_tenant_isolation.py` (PASS) |
| **Phase 8 (Field Telemetry)** | Real-time IoT sensor telemetry, on-site construction tracking | **PLANNED** | *Not implemented in current codebase.* |

---

## 8. Prerequisites & Environment Setup

### Required Tools
- **Python 3.12+** (tested with 3.14.4)
- **Node.js 20.x+** and **npm 10+**
- **Docker & Docker Compose** (for local PostGIS/Redis) OR access to a linked **Supabase project**

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SURAJD2002/Real_State_End_To_End.git
   cd Real_State_End_To_End
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   cp .env.example apps/web/.env
   ```
   *Edit `.env` and `apps/web/.env` with your actual sandbox database URLs and Supabase anon key.*

3. **Install Python virtual environment & dependencies:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Install Web Application dependencies:**
   ```bash
   npm install
   cd apps/web && npm install && cd ../..
   ```

---

## 9. Local Development Instructions

### Running the Services Locally

1. **Start Database (Local Docker):**
   ```bash
   npm run docker:up
   ```

2. **Start Backend API Gateway:**
   ```bash
   source .venv/bin/activate
   cd apps/api-gateway
   python3 main.py
   # Gateway runs on http://127.0.0.1:5001 (Swagger docs at http://127.0.0.1:5001/docs)
   ```

3. **Start Web Frontend (in a separate terminal):**
   ```bash
   npm --prefix apps/web run dev
   # Vite development server runs on http://localhost:5173
   ```

---

## 10. Database Schema & Migration Workflow

The database schema is structured into 8 sequential PostgreSQL migrations with PostGIS extensions located in `supabase/migrations/`:

| Migration # | Filename | Tables Created & Features |
| :--- | :--- | :--- |
| `01` | `20261010010000_init_postgis_schema.sql` | PostGIS extension, `projects`, `parcels`, `parcel_roads`, `parcel_constraints`, `feasibility_runs` |
| `02` | `20261010020000_canonical_building_model.sql` | `design_versions`, `building_models`, `building_levels`, `spaces`, `building_elements`, `openings` |
| `03` | `20261010030000_site_evidence_and_rule_engine.sql` | `site_reference_frames`, `site_evidence`, `regulation_rule_packs`, `rule_execution_traces` |
| `04` | `20261010040000_qto_boq_and_cost_engine.sql` | `qto_measurement_rules`, `construction_assemblies`, `material_catalog`, `cost_estimates` |
| `05` | `20261010050000_engineer_review_and_releases.sql` | `releases`, `build_requests`, `engineer_reviews`, `engineer_review_gates`, `review_issues` |
| `06` | `20261010060000_generated_reports.sql` | `generated_reports` (PDF metadata, cryptographic manifest hashes, SHA-256) |
| `07` | `20261010070000_security_and_rls_policies.sql` | Enables RLS across all 34 domain tables; default-deny for anonymous role |
| `08` | `20261010080000_organization_membership_mapping.sql` | `organizations`, `organization_memberships`, and `public.get_user_organization_ids()` helper |

### Safe Migration Workflow
- **Inspect migration status:**
  ```bash
  npx supabase migration list
  ```
- **Never apply blind schema resets or overwrite applied migrations.** Remote migrations must be sequentially versioned with standard timestamps.

---

## 11. Authentication, Authorization & Tenant Isolation

1. **Cryptographic Token Verification:**
   - Evaluated server-side in [`apps/api-gateway/auth.py`](file:///Users/surajkumar/Desktop/Real_state_dev/apps/api-gateway/auth.py).
   - Validates public `ES256` asymmetric keys from Supabase project JWKS with automated key caching and rotation.
   - Rejects unsigned tokens (`none`), expired tokens, wrong audience, and forged signatures with HTTP 401.
2. **Zero-Trust Organization Resolution:**
   - Verified token `sub` is mapped to `public.organization_memberships`.
   - Roles (`OWNER`, `ADMIN`, `MEMBER`, `VIEWER`) are resolved strictly from the database. Client payload roles are ignored.
3. **Database Row Level Security (RLS):**
   - 34 of 34 tables have `rowsecurity = true`.
   - Security-definer helper function `public.get_user_organization_ids()` pins `search_path = pg_catalog, public`.
   - Verified by automated cross-tenant test suite (`test_cross_tenant_isolation.py`).

---

## 12. API Documentation & Verified Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` / `/api/health` | Health check returning service status and version |
| `GET` | `/api/v1/auth/session` | Resolves authenticated user, tenant organization, and RBAC role |
| `GET` | `/api/v1/projects` | Lists projects belonging strictly to the caller's tenant organization |
| `POST` | `/api/v1/projects` | Creates project and persists parcel geometry to PostgreSQL |
| `GET` | `/api/v1/projects/{id}` | Retrieves project details (cross-tenant requests return 403) |
| `PUT` | `/api/v1/projects/{id}/geometries` | Auto-saves PostGIS parcel coordinates with version increment |
| `POST` | `/api/v1/projects/{id}/calculate-feasibility` | Computes deterministic statutory feasibility (DCPR 2034) |
| `GET` | `/api/v1/projects/{id}/house-options` | Returns generated parametric house options (`compact_2bhk`, etc.) |
| `POST` | `/api/v1/design-versions/{id}/build-request` | Locks design option and generates immutable release fingerprint |
| `GET` | `/api/v1/releases/{id}/ifc` | Downloads open-standard IFC4 STEP BIM physical model |
| `POST` | `/api/v1/releases/{id}/approvals` | Updates G0–G8 engineering verification gate decisions |
| `POST` | `/api/v1/design-versions/{id}/drawings/compile` | Compiles publication-grade 9-sheet architectural drawing set |
| `POST` | `/api/v1/design-versions/{id}/reports/home` | Generates customer home report PDF with SHA-256 hash |

---

## 13. Test Commands & Verified Results

**Audit Date:** 2026-10-10
**Test Runner:** Python `unittest` via `.venv/bin/python`

### 1. Negative Security & Token Verification Test Suite
```bash
./.venv/bin/python -m unittest tests/test_auth_security_negative.py
```
- **Outcome:** **11/11 PASSED** (60.45s)
- **Verified:** Rejection of unsigned tokens (401), forged symmetric keys (401), forged asymmetric EC keys (401), tampered payloads (401), expired tokens (401), invalid audiences (401), invalid issuers (401), privilege escalation containment, cross-tenant reads (403), cross-tenant writes (403), and live Supabase Auth token integration (200).

### 2. Multi-Tenant Cross-Tenant RLS Isolation Test Suite
```bash
./.venv/bin/python -m unittest tests/test_cross_tenant_isolation.py
```
- **Outcome:** **7/7 PASSED** (58.25s)
- **Verified:** Anonymous role default-deny across all project and report tables; cross-tenant SELECT returns 0 rows; cross-tenant UPDATE affects 0 rows; cross-tenant INSERT blocked by WITH CHECK.

### 3. End-to-End Persistence & Auth Workflow Test Suite
```bash
./.venv/bin/python -m unittest tests/test_persistence_and_auth_workflow.py
```
- **Outcome:** **6/6 PASSED** (107.71s)
- **Verified:** Project creation, PostGIS parcel auto-save, feasibility calculation persistence, and full rehydration after volatile memory purge.

### 4. Canonical 1,100 sq ft Real Plot End-to-End Pipeline
```bash
./.venv/bin/python -m unittest tests/test_real_plot_end_to_end.py
```
- **Outcome:** **13/13 PASSED** (15.78s)
- **Verified:** Complete end-to-end M1 $\rightarrow$ M2 $\rightarrow$ M3 pipeline: coordinate transformation, DCPR 2034 setbacks, CP-SAT generation, QTO takeoff, CPWD costing, and CPM scheduling.

### 5. Frontend Production Build
```bash
npm --prefix apps/web run build
```
- **Outcome:** **0 Errors** (Built cleanly in 4.24s via Vite `6.4.4` and TypeScript `5.7.3`).

---

## 14. Environment Variables Reference

Use placeholders only. Never commit active credentials.

| Variable | Description | Safe Example / Default |
| :--- | :--- | :--- |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:password@localhost:5432/realestate_feasibility` |
| `SUPABASE_URL` | Supabase Cloud project URL | `https://your-project-ref.supabase.co` |
| `SUPABASE_ANON_KEY` | Public publishable anon key | `your_supabase_anon_key_placeholder` |
| `SUPABASE_SERVICE_ROLE_KEY` | Server-only admin key (never on client) | `your_service_role_key_placeholder` |
| `JWT_SECRET` | Symmetric fallback JWT secret ($\ge 32$ chars) | `your_jwt_secret_min_32_characters_placeholder` |
| `API_PORT` | FastAPI service port | `5001` |
| `API_HOST` | FastAPI service host bind | `0.0.0.0` |
| `CORS_ORIGINS` | Permitted client web origins | `http://localhost:5173,http://localhost:3000` |
| `VITE_API_BASE_URL` | Frontend API Gateway URL | `http://localhost:5001/api/v1` |
| `VITE_SUPABASE_URL` | Frontend Supabase endpoint | `https://your-project-ref.supabase.co` |
| `VITE_SUPABASE_ANON_KEY` | Frontend Supabase anon key | `your_supabase_anon_key_placeholder` |

---

## 15. Troubleshooting Guide

- **Error: `Invalid token format or signature` (HTTP 401)**
  - *Cause:* The Bearer token was signed with an unrecognized key, has expired, or failed cryptographic verification.
  - *Resolution:* Sign in via Supabase Auth to obtain a fresh ES256 session token or configure matching `JWT_SECRET` for testing.
- **Error: `Cross-tenant access denied` (HTTP 403)**
  - *Cause:* Attempted to access or mutate a project belonging to a different organization.
  - *Resolution:* Authenticate with an account that is a member of the project's organization.
- **Error: PostGIS function not found (`ST_GeomFromText`)**
  - *Cause:* PostGIS extension missing on database.
  - *Resolution:* Run `CREATE EXTENSION IF NOT EXISTS postgis;` on the target PostgreSQL database.
- **Vite Proxy Connection Refused (`5001`)**
  - *Cause:* Backend API Gateway is not running.
  - *Resolution:* Start API Gateway via `cd apps/api-gateway && python3 main.py`.

---

## 16. Technical Documentation Index

Detailed engineering blueprints and audit reports are available in the repository:

- [PLANWISE_PILOT_READINESS_REPORT.md](PLANWISE_PILOT_READINESS_REPORT.md) — Authoritative Pilot Readiness Matrix and P0 Security Verification
- [PLANWISE_PERSISTENCE_MAPPING.md](PLANWISE_PERSISTENCE_MAPPING.md) — Complete Endpoint-to-Table Mapping
- [PLANWISE_AUTHENTICATION_AND_AUTHORIZATION.md](PLANWISE_AUTHENTICATION_AND_AUTHORIZATION.md) — Auth & Tenancy Architecture
- [SUPABASE_SECURITY_RLS_AUDIT.md](SUPABASE_SECURITY_RLS_AUDIT.md) — Row Level Security Policy Verification
- [PHASE_9_M2_PROFESSIONAL_DRAWING_PIPELINE_REPORT.md](PHASE_9_M2_PROFESSIONAL_DRAWING_PIPELINE_REPORT.md) — Architectural Drawing Compiler
- [PHASE_9_M1_IFC_PROFESSIONALIZATION_REPORT.md](PHASE_9_M1_IFC_PROFESSIONALIZATION_REPORT.md) — IFC4 BIMSTEP Georeferencing
- [docs/README.md](docs/README.md) — Complete Engineering Document Index

---

## 17. Current Limitations & Known Risks

1. **Email Rate Limiting (Default Supabase Free Tier):**
   - For pilot deployments with external testers, connect a custom SMTP provider (e.g., AWS SES, Resend) to avoid standard 3 emails/hour limits on password resets.
2. **PostgreSQL High Concurrency:**
   - In containerized production deployments with high concurrent worker tasks, route backend connections through Supabase Transaction Pooler (port `6543`).
3. **Statutory Pack Expansion:**
   - Mumbai MCGM DCPR 2034 is fully codified and verified. Bangalore BBMP rules are structurally supported, while other jurisdictions are currently modeled as templates.

---

## 18. Security & Contributions

- **Security Disclosures:** Please review [SECURITY.md](SECURITY.md) for confidential reporting procedures. Do not file public GitHub issues for security vulnerabilities.
- **Contributions:** Please review [CONTRIBUTING.md](CONTRIBUTING.md) for branch guidelines, coding standards, and pull request workflows.
