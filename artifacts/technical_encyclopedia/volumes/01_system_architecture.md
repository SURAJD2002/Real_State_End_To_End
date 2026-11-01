# Volume I — System Overview and Architecture

## 1. Executive Technical Summary
**Planwise Enterprise** is a high-assurance, computational land-to-home development platform designed for precision civil engineering, statutory urban compliance, and deterministic architectural generation. Unlike generative AI systems that synthesize hallucinatory imagery or unstructured 2D sketches, Planwise operates as a deterministic, mathematically verifiable engineering pipeline.

The platform executes an automated, sequential workflow:
1. **Land & GIS Intake:** Parsing WGS84 geodesic coordinates, cadastral survey boundaries, and municipal frontage road parameters.
2. **Statutory Feasibility:** Computing zoning envelopes, mandatory front/rear/side setbacks, ground coverage, and Floor Space Index (FSI/FAR) under strict regulatory engines (e.g., Mumbai DCPR 2034 and BBMP 2026 Building Bye-Laws).
3. **Discrete Combinatorial Layout Optimization:** Formulating room programs and daylight requirements as a Constraint Satisfaction Problem (CSP) solved deterministically via the Google OR-Tools CP-SAT solver (fixed seed `42`).
4. **Watertight 3D Solid Geometry:** Synthesizing true 2-manifold boundary representations ($B\text{-rep}$) with an Euler characteristic $\chi = 2$ using the Manifold3D C++ computational geometry engine.
5. **Standardized Quantity Takeoff (QTO) & Costing:** Computing bills of quantities (BOQ) with strict opening deductions conforming to Indian Standard IS 1200.
6. **Multi-View Architectural CAD Compilation:** Generating 9 synchronized architectural projection sheets (floor plans, exterior elevations, building sections) in vector PDF and SVG formats.
7. **BIM Interoperability:** Emitting ISO 16739-1 compliant Industry Foundation Classes (IFC4 SPF) models with complete spatial hierarchies.
8. **Multi-Stage Engineering Review & Handoff:** Enforcing a rigorous 7-stage engineering sign-off gate sequence (G0 through G6) governed by cryptographic SHA-256 release manifests.

---

## 2. Platform Architecture & Data Flow Diagrams


<div class="diagram-container">
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 465" width="100%" height="465px" class="svg-diagram" style="max-height:465px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;">
<defs>
  <marker id="arr" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
    <path d="M0,0 L6,3 L0,6 Z" fill="#2563eb" />
  </marker>
  <marker id="arr-gray" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
    <path d="M0,0 L6,3 L0,6 Z" fill="#64748b" />
  </marker>
</defs>

<text x="350" y="24" text-anchor="middle" font-size="13" font-weight="bold" fill="#0f172a">DIAGRAM 1: PLANWISE ENTERPRISE — THREE-TIER DECOUPLED ARCHITECTURE</text>
<!-- Presentation Layer -->
<rect x="30" y="45" width="640" height="70" rx="4" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.2"/>
<text x="45" y="65" font-size="11" font-weight="bold" fill="#1e40af">1. PRESENTATION LAYER (apps/web)</text>
<text x="45" y="82" font-size="9" fill="#334155">React 18.3 • TypeScript • Vite • TailwindCSS • Lucide Icons • Canvas CAD Blueprint Engine (CadBlueprintView)</text>
<text x="45" y="98" font-size="9" fill="#64748b">Customer Workflow (Land → Feasibility → Design → Cost → Review) | Professional Reviewer Workflow (EngineerReviewView)</text>

<!-- Gateway & Orchestration Layer -->
<rect x="30" y="145" width="640" height="75" rx="4" fill="#f0fdf4" stroke="#22c55e" stroke-width="1.2"/>
<text x="45" y="165" font-size="11" font-weight="bold" fill="#15803d">2. API GATEWAY & ORCHESTRATION LAYER (apps/api-gateway)</text>
<text x="45" y="182" font-size="9" fill="#334155">FastAPI 0.142 • Pydantic 2.13 • Uvicorn • 65 Validated REST Endpoints • In-Memory Mock/Ledger & Postgres Repository</text>
<text x="45" y="198" font-size="9" fill="#64748b">Route Handlers: /api/v1/projects • /calculate-feasibility • /design-options • /qto • /cost • /engineer-reviews • /releases</text>

<!-- Computational Core & Workers Layer -->
<rect x="30" y="250" width="640" height="120" rx="4" fill="#faf5ff" stroke="#a855f7" stroke-width="1.2"/>
<text x="45" y="270" font-size="11" font-weight="bold" fill="#7e22ce">3. COMPUTATIONAL WORKERS & SCHEMAS (workers/ & packages/)</text>
<rect x="45" y="282" width="135" height="75" rx="3" fill="#ffffff" stroke="#cbd5e1"/>
<text x="52" y="298" font-size="8.5" font-weight="bold" fill="#0f172a">Regulation (M1)</text>
<text x="52" y="312" font-size="7.5" fill="#475569">rule_engine.py</text>
<text x="52" y="324" font-size="7.5" fill="#475569">MUMBAI_DCPR_2034</text>
<text x="52" y="336" font-size="7.5" fill="#475569">BBMP_2026</text>
<text x="52" y="348" font-size="7.5" fill="#059669">Shapely 2.1.2</text>

<rect x="195" y="282" width="145" height="75" rx="3" fill="#ffffff" stroke="#cbd5e1"/>
<text x="202" y="298" font-size="8.5" font-weight="bold" fill="#0f172a">Generation (M2)</text>
<text x="202" y="312" font-size="7.5" fill="#475569">cpsat_solver.py</text>
<text x="202" y="324" font-size="7.5" fill="#475569">Google OR-Tools CP-SAT</text>
<text x="202" y="336" font-size="7.5" fill="#475569">model_compiler.py</text>
<text x="202" y="348" font-size="7.5" fill="#059669">Manifold3D 3.5.4</text>

<rect x="355" y="282" width="145" height="75" rx="3" fill="#ffffff" stroke="#cbd5e1"/>
<text x="362" y="298" font-size="8.5" font-weight="bold" fill="#0f172a">QTO & Cost (M3)</text>
<text x="362" y="312" font-size="7.5" fill="#475569">measurement_engine.py</text>
<text x="362" y="324" font-size="7.5" fill="#475569">IS 1200 Part 1,2,3,12</text>
<text x="362" y="336" font-size="7.5" fill="#475569">cost_engine.py</text>
<text x="362" y="348" font-size="7.5" fill="#059669">Rate Snapshots</text>

<rect x="515" y="282" width="140" height="75" rx="3" fill="#ffffff" stroke="#cbd5e1"/>
<text x="522" y="298" font-size="8.5" font-weight="bold" fill="#0f172a">Review & Release</text>
<text x="522" y="312" font-size="7.5" fill="#475569">G0-G6 Review Gates</text>
<text x="522" y="324" font-size="7.5" fill="#475569">IFC4 STEP Exporter</text>
<text x="522" y="336" font-size="7.5" fill="#475569">Manifest Engine</text>
<text x="522" y="348" font-size="7.5" fill="#059669">ReportLab PDF</text>

<!-- Persistence Layer -->
<rect x="30" y="395" width="640" height="55" rx="4" fill="#f8fafc" stroke="#64748b" stroke-width="1.2"/>
<text x="45" y="415" font-size="11" font-weight="bold" fill="#334155">4. PERSISTENCE LAYER (PostgreSQL 15+ & PostGIS 3.3)</text>
<text x="45" y="432" font-size="8.5" fill="#475569">Migrations 01-06 • PostGIS Polygons • CBM Relational Tables • QTO Measurement Rules • Release Ledger • Audit Hashes</text>

<!-- Connectors -->
<line x1="350" y1="115" x2="350" y2="145" stroke="#2563eb" stroke-width="1.5" marker-end="url(#arr)"/>
<line x1="350" y1="220" x2="350" y2="250" stroke="#2563eb" stroke-width="1.5" marker-end="url(#arr)"/>
<line x1="350" y1="370" x2="350" y2="395" stroke="#2563eb" stroke-width="1.5" marker-end="url(#arr)"/>

</svg>
  <div class="diagram-caption">Diagram 1: Planwise Enterprise Three-Tier Decoupled Architecture</div>
</div>



<div class="diagram-container">
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 220" width="100%" height="220px" class="svg-diagram" style="max-height:220px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;">
<defs>
  <marker id="arr" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
    <path d="M0,0 L6,3 L0,6 Z" fill="#2563eb" />
  </marker>
  <marker id="arr-gray" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
    <path d="M0,0 L6,3 L0,6 Z" fill="#64748b" />
  </marker>
</defs>

<text x="350" y="24" text-anchor="middle" font-size="13" font-weight="bold" fill="#0f172a">DIAGRAM 2: END-TO-END CUSTOMER DATA LINEAGE & STATE TRANSITIONS</text>
<rect x="25" y="45" width="95" height="60" rx="3" fill="#ffffff" stroke="#2563eb" stroke-width="1.2"/>
<text x="72" y="65" text-anchor="middle" font-size="8.5" font-weight="bold" fill="#1e40af">1. LAND</text>
<text x="72" y="80" text-anchor="middle" font-size="7.5" fill="#334155">Declared Area</text>
<text x="72" y="93" text-anchor="middle" font-size="7.5" fill="#059669">e.g. 1500 sq ft</text>

<line x1="120" y1="75" x2="140" y2="75" stroke="#2563eb" stroke-width="1.2" marker-end="url(#arr)"/>

<rect x="140" y="45" width="105" height="60" rx="3" fill="#ffffff" stroke="#2563eb" stroke-width="1.2"/>
<text x="192" y="65" text-anchor="middle" font-size="8.5" font-weight="bold" fill="#1e40af">2. FEASIBILITY</text>
<text x="192" y="80" text-anchor="middle" font-size="7.5" fill="#334155">M1 Rule Engine</text>
<text x="192" y="93" text-anchor="middle" font-size="7.5" fill="#059669">Setbacks & FSI</text>

<line x1="245" y1="75" x2="265" y2="75" stroke="#2563eb" stroke-width="1.2" marker-end="url(#arr)"/>

<rect x="265" y="45" width="105" height="60" rx="3" fill="#ffffff" stroke="#2563eb" stroke-width="1.2"/>
<text x="317" y="65" text-anchor="middle" font-size="8.5" font-weight="bold" fill="#1e40af">3. INTAKE</text>
<text x="317" y="80" text-anchor="middle" font-size="7.5" fill="#334155">Customer Brief</text>
<text x="317" y="93" text-anchor="middle" font-size="7.5" fill="#059669">BHK, Bath, Floors</text>

<line x1="370" y1="75" x2="390" y2="75" stroke="#2563eb" stroke-width="1.2" marker-end="url(#arr)"/>

<rect x="390" y="45" width="105" height="60" rx="3" fill="#ffffff" stroke="#2563eb" stroke-width="1.2"/>
<text x="442" y="65" text-anchor="middle" font-size="8.5" font-weight="bold" fill="#1e40af">4. GENERATION</text>
<text x="442" y="80" text-anchor="middle" font-size="7.5" fill="#334155">CP-SAT Solver</text>
<text x="442" y="93" text-anchor="middle" font-size="7.5" fill="#059669">Pareto Options</text>

<line x1="495" y1="75" x2="515" y2="75" stroke="#2563eb" stroke-width="1.2" marker-end="url(#arr)"/>

<rect x="515" y="45" width="80" height="60" rx="3" fill="#ffffff" stroke="#2563eb" stroke-width="1.2"/>
<text x="555" y="65" text-anchor="middle" font-size="8.5" font-weight="bold" fill="#1e40af">5. COST</text>
<text x="555" y="80" text-anchor="middle" font-size="7.5" fill="#334155">BOQ & QTO</text>
<text x="555" y="93" text-anchor="middle" font-size="7.5" fill="#059669">IS 1200 Engine</text>

<line x1="595" y1="75" x2="615" y2="75" stroke="#2563eb" stroke-width="1.2" marker-end="url(#arr)"/>

<rect x="615" y="45" width="65" height="60" rx="3" fill="#ffffff" stroke="#2563eb" stroke-width="1.2"/>
<text x="647" y="65" text-anchor="middle" font-size="8.5" font-weight="bold" fill="#1e40af">6. LOCK</text>
<text x="647" y="80" text-anchor="middle" font-size="7.5" fill="#334155">Release</text>
<text x="647" y="93" text-anchor="middle" font-size="7.5" fill="#059669">SHA-256</text>

<!-- Bottom Detail Boxes -->
<rect x="25" y="130" width="655" height="75" rx="3" fill="#f1f5f9" stroke="#cbd5e1"/>
<text x="35" y="148" font-size="8.5" font-weight="bold" fill="#0f172a">State Persistence & Provenance Trail:</text>
<text x="35" y="165" font-size="8" fill="#334155">• Project ID: proj-cust-[random] (generated dynamically, never hardcoded reference project)</text>
<text x="35" y="180" font-size="8" fill="#334155">• Geometries PUT: PUT /api/v1/projects/{id}/geometries stores declaredPlotAreaSqFt and increments parcel.version</text>
<text x="35" y="195" font-size="8" fill="#334155">• CBM Envelope: derived dynamically as sqrt(plotSqM * coverage * aspect_ratio) with zero silent fallbacks</text>

</svg>
  <div class="diagram-caption">Diagram 2: End-to-End Customer Data Flow from Land Ingestion to Handover</div>
</div>


---

## 3. Product Purpose, Supported Users, and Workflows

### 2.1 Target Personas
- **Enterprise Land Developers & Real Estate Firms:** Ingest raw land parcels (1,000 to 10,000+ sq ft), instantly evaluate statutory feasibility, and generate multi-alternative floor plans.
- **Municipal Compliance & Liasoning Consultants:** Validate setbacks, FSI consumption, and maximum building heights against statutory municipal codes.
- **Structural & MEP Engineers:** Review computational building models, verify load-bearing grid alignments, and inspect technical drawings prior to construction handoff.
- **General Contractors & Estimators:** Access deterministic BOQ quantities, rate breakdowns, and material schedules mapped to IS 1200 measurement standards.

### 2.2 End-to-End Workflow Pipeline
```
[Land Intake] ──> [Statutory Feasibility] ──> [Design Program] ──> [CP-SAT Solver]
       │                    │                         │                  │
   WGS84 GPS          DCPR 2034 / BBMP         BHK & Dimensions     Grid Placement
       │                    │                         │                  │
       ▼                    ▼                         ▼                  ▼
[CBM Building Model] ──> [Manifold3D Solids] ──> [IS 1200 QTO] ──> [Cost Waterfall]
       │                         │                     │                 │
Watertight Mesh          Euler Chi = 2         Opening Deductions   Rate Catalogs
       │                         │                     │                 │
       ▼                         ▼                         ▼             ▼
[Drawing Compiler] ────> [IFC4 BIM Export] ────> [Review Gates] ──> [Release Ledger]
  9 PDF Sheets              ISO 16739-1               G0 to G6       SHA-256 Manifest
```

---

## 3. Technology Stack and Verified Versions

| Layer | Component / Library | Verified Version | Purpose & Implementation |
| :--- | :--- | :--- | :--- |
| **Frontend Core** | React | `18.3.1` (Vite) | Single-page reactive user interface (`apps/web`) |
| **Frontend Typing** | TypeScript | `5.6.3` | Strict static type safety across UI models |
| **Styling & Icons** | Tailwind CSS / Lucide | `3.4.1` / `0.344.0` | Design system and engineering iconography |
| **CAD Rendering** | HTML5 Canvas / SVG | Native DOM | Interactive vector floor plan and blueprint viewer |
| **API Gateway** | FastAPI | `0.115.0` | High-performance asynchronous REST gateway (`apps/api-gateway`) |
| **Web Server** | Uvicorn | `0.30.6` | ASGI production server binding |
| **Data Validation** | Pydantic | `2.9.2` | Strict contract validation and serialization |
| **Optimization** | Google OR-Tools | `9.10.4067` | CP-SAT constraint programming solver engine |
| **3D Geometry** | Manifold3D | `3.0.0` | C++ watertight mesh solids modeling kernel |
| **Planar Geometry** | Shapely | `2.0.6` | Cartesian polygon operations, buffering, setbacks |
| **BIM Export** | IfcOpenShell | `0.7.0` | ISO 16739-1 IFC4 SPF data model generation |
| **Database** | PostgreSQL / Supabase | `16.1` / `2.45.0` | Multi-tenant relational storage with RLS policies |
| **PDF Generation** | Puppeteer / Chrome | `23.4.0` / Chrome 144 | Headless vector-accurate documentation compilation |

---

## 4. Repository Architecture and Directory Topology

The codebase is organized as a decoupled polyglot monorepo:
```
Real_state_dev/
├── apps/
│   ├── api-gateway/            # FastAPI REST backend (main.py, auth.py, database.py)
│   └── web/                    # React Vite TypeScript frontend (src/components, src/context)
├── packages/
│   ├── schemas/                # Shared Pydantic data models (cbm.py, engineer_review.py)
│   └── geometry/               # Computational geometry abstractions (solid_modeler.py)
├── workers/
│   ├── statutory/              # Rule engines (mumbai_dcpr.py, bbmp_rules.py)
│   ├── optimization/           # CP-SAT room layout solver (layout_optimizer.py)
│   ├── cost/                   # IS 1200 QTO and cost engines (boq_engine.py, cost_engine.py)
│   ├── generation/             # 9-sheet architectural drawing compiler (drawing_compiler.py)
│   └── release/                # Release ledger & manifest engine (manifest_engine.py)
├── database/
│   └── migrations/             # 6 legacy relational schema migrations (01_initial to 06_audit)
├── supabase/
│   └── migrations/             # 8 active Supabase migrations (01 to 08 including RLS policies)
├── tests/                      # 19 automated test suites (230 test cases)
├── scripts/                    # Build scripts, E2E runners, and documentation compilers
└── artifacts/                  # Generated forensic proofs, CAD drawings, IFC models, PDFs
```

---

## 5. Runtime Process Topology & Startup Sequence

In a live staging or production environment, the runtime consists of three primary processes:
1. **Frontend Server (`localhost:5173`):** Vite development server serving React 18 bundles.
2. **API Gateway (`localhost:5001`):** Uvicorn server running `apps.api-gateway.main:app` with 4 worker threads.
3. **PostgreSQL / Supabase Database (`localhost:5432`):** Relational persistence store with Supabase Auth services.

### Application Startup Flow
```
[uvicorn start] ──> [main.py lifespan] ──> [Connect DB Pool (psycopg2)]
                          │
                          ├──> [Validate Database Schema Migrations]
                          ├──> [Initialize In-Memory Fallback Stores]
                          ├──> [Mount CORS & Security Middleware]
                          └──> [Expose 73 OpenAPI REST Endpoints]
```

---

## 6. End-to-End Request Lifecycle
A typical request (e.g. generating design options for a 1,500 sq ft plot) traces through the stack:
1. **Client Action:** User enters plot boundary vertices and clicks "Generate Plans".
2. **Frontend Dispatch:** `DesignOptionsView.tsx` issues `POST /api/v1/design-options` with JWT header.
3. **Gateway Ingestion:** FastAPI `get_current_user` extracts `sub` and `organization_id` from the Bearer token.
4. **Validation:** Pydantic validates `DesignBriefRequest` against `packages/schemas/cbm.py`.
5. **Statutory Check:** `workers/statutory/mumbai_dcpr.py` calculates setback envelope.
6. **CP-SAT Solving:** `workers/optimization/layout_optimizer.py` instantiates CP-SAT solver with seed 42.
7. **Mesh Synthesis:** `packages/geometry/solid_modeler.py` evaluates Manifold3D watertight solids.
8. **Drawing Compilation:** `workers/generation/drawing_compiler.py` generates SVG vectors.
9. **Persistence & Return:** Gateway records design ID in memory/PostgreSQL and returns JSON with 3 options.
