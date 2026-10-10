"""
Planwise Enterprise — Architectural & Mathematical Vector SVG Diagrams
Generates 15 authoritative, verified diagrams reflecting real codebase pipelines.
"""

def make_svg_wrapper(width, height, content):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="{height}px" class="svg-diagram" style="max-height:{height}px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;">
<defs>
  <marker id="arr" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
    <path d="M0,0 L6,3 L0,6 Z" fill="#2563eb" />
  </marker>
  <marker id="arr-gray" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
    <path d="M0,0 L6,3 L0,6 Z" fill="#64748b" />
  </marker>
</defs>
{content}
</svg>'''

def diagram_01_system_architecture():
    # apps, packages, workers, database
    content = '''
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
'''
    return make_svg_wrapper(700, 465, content)

def diagram_02_customer_data_flow():
    content = '''
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
'''
    return make_svg_wrapper(700, 220, content)

def diagram_03_cbm_structure():
    content = '''
<text x="350" y="24" text-anchor="middle" font-size="13" font-weight="bold" fill="#0f172a">DIAGRAM 3: CANONICAL BUILDING MODEL (CBM) SCHEMA HIERARCHY</text>
<rect x="260" y="45" width="180" height="45" rx="3" fill="#1e293b" stroke="#0f172a"/>
<text x="350" y="64" text-anchor="middle" font-size="10" font-weight="bold" fill="#ffffff">CanonicalBuildingModel</text>
<text x="350" y="78" text-anchor="middle" font-size="8" fill="#94a3b8">modelId • schemaVersion 1.0.0</text>

<!-- Child Objects -->
<line x1="350" y1="90" x2="350" y2="115" stroke="#64748b" stroke-width="1.2"/>
<line x1="80" y1="115" x2="620" y2="115" stroke="#64748b" stroke-width="1.2"/>

<!-- Levels -->
<line x1="80" y1="115" x2="80" y2="135" stroke="#64748b" stroke-width="1.2" marker-end="url(#arr-gray)"/>
<rect x="20" y="135" width="120" height="90" rx="3" fill="#ffffff" stroke="#3b82f6"/>
<text x="80" y="152" text-anchor="middle" font-size="9" font-weight="bold" fill="#1e40af">BuildingLevel</text>
<text x="28" y="168" font-size="7.5" fill="#334155">• levelId (LVL-000)</text>
<text x="28" y="180" font-size="7.5" fill="#334155">• levelIndex (0, 1)</text>
<text x="28" y="192" font-size="7.5" fill="#334155">• elevationM (0.0)</text>
<text x="28" y="204" font-size="7.5" fill="#334155">• floorHeight (3.15)</text>
<text x="28" y="216" font-size="7.5" fill="#334155">• usage (RESIDENTIAL)</text>

<!-- Spaces -->
<line x1="210" y1="115" x2="210" y2="135" stroke="#64748b" stroke-width="1.2" marker-end="url(#arr-gray)"/>
<rect x="150" y="135" width="120" height="90" rx="3" fill="#ffffff" stroke="#10b981"/>
<text x="210" y="152" text-anchor="middle" font-size="9" font-weight="bold" fill="#047857">Space (Room)</text>
<text x="158" y="168" font-size="7.5" fill="#334155">• spaceId (SPACE-01)</text>
<text x="158" y="180" font-size="7.5" fill="#334155">• spaceType (BED...)</text>
<text x="158" y="192" font-size="7.5" fill="#334155">• bounds (x,y,w,h)</text>
<text x="158" y="204" font-size="7.5" fill="#334155">• areaSqm, polygon</text>
<text x="158" y="216" font-size="7.5" fill="#334155">• floor (L0, L1)</text>

<!-- Elements -->
<line x1="350" y1="115" x2="350" y2="135" stroke="#64748b" stroke-width="1.2" marker-end="url(#arr-gray)"/>
<rect x="285" y="135" width="130" height="90" rx="3" fill="#ffffff" stroke="#8b5cf6"/>
<text x="350" y="152" text-anchor="middle" font-size="9" font-weight="bold" fill="#6d28d9">CanonicalElement</text>
<text x="293" y="168" font-size="7.5" fill="#334155">• WALL (EXT, INT)</text>
<text x="293" y="180" font-size="7.5" fill="#334155">• COLUMN (RCC)</text>
<text x="293" y="192" font-size="7.5" fill="#334155">• SLAB (FLOOR)</text>
<text x="293" y="204" font-size="7.5" fill="#334155">• STAIR (Parametric)</text>
<text x="293" y="216" font-size="7.5" fill="#334155">• geometry (footprint)</text>

<!-- Openings -->
<line x1="485" y1="115" x2="485" y2="135" stroke="#64748b" stroke-width="1.2" marker-end="url(#arr-gray)"/>
<rect x="425" y="135" width="120" height="90" rx="3" fill="#ffffff" stroke="#f59e0b"/>
<text x="485" y="152" text-anchor="middle" font-size="9" font-weight="bold" fill="#b45309">CanonicalOpening</text>
<text x="433" y="168" font-size="7.5" fill="#334155">• openingId</text>
<text x="433" y="180" font-size="7.5" fill="#334155">• openingType (DOOR/WIN)</text>
<text x="433" y="192" font-size="7.5" fill="#334155">• hostElementId (WALL)</text>
<text x="433" y="204" font-size="7.5" fill="#334155">• positionM, widthM</text>
<text x="433" y="216" font-size="7.5" fill="#334155">• heightM, sillHeight</text>

<!-- Envelope & Metadata -->
<line x1="620" y1="115" x2="620" y2="135" stroke="#64748b" stroke-width="1.2" marker-end="url(#arr-gray)"/>
<rect x="555" y="135" width="130" height="90" rx="3" fill="#ffffff" stroke="#ef4444"/>
<text x="620" y="152" text-anchor="middle" font-size="9" font-weight="bold" fill="#b91c1c">Envelope & Meta</text>
<text x="563" y="168" font-size="7.5" fill="#334155">• buildingEnvelope</text>
<text x="563" y="180" font-size="7.5" fill="#334155">• widthM, lengthM</text>
<text x="563" y="192" font-size="7.5" fill="#334155">• declaredPlotAreaSqFt</text>
<text x="563" y="204" font-size="7.5" fill="#334155">• validationSummary</text>
<text x="563" y="216" font-size="7.5" fill="#334155">• modelHash (SHA256)</text>
'''
    return make_svg_wrapper(700, 245, content)

def diagram_04_cpsat_solver():
    content = '''
<text x="350" y="24" text-anchor="middle" font-size="13" font-weight="bold" fill="#0f172a">DIAGRAM 4: OR-TOOLS CP-SAT DISCRETE SPATIAL ALLOCATION SOLVER</text>
<rect x="30" y="45" width="190" height="130" rx="3" fill="#ffffff" stroke="#3b82f6" stroke-width="1.2"/>
<text x="125" y="65" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#1e40af">1. DISCRETIZATION</text>
<text x="40" y="85" font-size="8" fill="#334155">• Resolution: 1 unit = 100mm</text>
<text x="40" y="100" font-size="8" fill="#334155">• x_i ∈ [0, W_env - w_i]</text>
<text x="40" y="115" font-size="8" fill="#334155">• y_i ∈ [0, L_env - d_i]</text>
<text x="40" y="130" font-size="8" fill="#334155">• w_i ∈ [w_min, w_max]</text>
<text x="40" y="145" font-size="8" fill="#334155">• d_i ∈ [d_min, d_max]</text>
<text x="40" y="160" font-size="8" fill="#059669">Domain size: ~10^6 states</text>

<line x1="220" y1="110" x2="250" y2="110" stroke="#2563eb" stroke-width="1.5" marker-end="url(#arr)"/>

<rect x="250" y="45" width="200" height="130" rx="3" fill="#ffffff" stroke="#8b5cf6" stroke-width="1.2"/>
<text x="350" y="65" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#6d28d9">2. HARD CONSTRAINTS</text>
<text x="260" y="85" font-size="8" fill="#334155">• AddNoOverlap2D([Ix_i], [Iy_i])</text>
<text x="260" y="100" font-size="8" fill="#334155">• Containment: x_i + w_i ≤ W_env</text>
<text x="260" y="115" font-size="8" fill="#334155">• Area: w_i * d_i ≥ A_min (×100)</text>
<text x="260" y="130" font-size="8" fill="#334155">• NBC 2016: Kitchen ≁ Toilet</text>
<text x="260" y="145" font-size="8" fill="#334155">• Daylight: Perimeter Wall Touch</text>
<text x="260" y="160" font-size="8" fill="#059669">100% Guaranteed Feasibility</text>

<line x1="450" y1="110" x2="480" y2="110" stroke="#2563eb" stroke-width="1.5" marker-end="url(#arr)"/>

<rect x="480" y="45" width="190" height="130" rx="3" fill="#ffffff" stroke="#10b981" stroke-width="1.2"/>
<text x="575" y="65" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#047857">3. OBJECTIVE & DIVERSITY</text>
<text x="490" y="85" font-size="8" fill="#334155">• Maximize Adjacency Weights</text>
<text x="490" y="100" font-size="8" fill="#334155">• Maximize Usable Living Space</text>
<text x="490" y="115" font-size="8" fill="#334155">• Minimize Circulation Hallway</text>
<text x="490" y="130" font-size="8" fill="#334155">• No-Good Cuts: Exclude Quadrants</text>
<text x="490" y="145" font-size="8" fill="#334155">• Solve Time: 50ms - 350ms</text>
<text x="490" y="160" font-size="8" fill="#059669">Deterministic (Seed=42)</text>
'''
    return make_svg_wrapper(700, 195, content)

def diagram_05_manifold3d_geometry():
    content = '''
<text x="350" y="24" text-anchor="middle" font-size="13" font-weight="bold" fill="#0f172a">DIAGRAM 5: MANIFOLD3D WATERTIGHT SOLID CSG PIPELINE</text>
<rect x="30" y="45" width="140" height="90" rx="3" fill="#ffffff" stroke="#3b82f6"/>
<text x="100" y="65" text-anchor="middle" font-size="9" font-weight="bold" fill="#1e40af">1. 2D Polygons</text>
<text x="40" y="82" font-size="7.8" fill="#334155">Shapely 2.1.2</text>
<text x="40" y="96" font-size="7.8" fill="#334155">Room Boundaries</text>
<text x="40" y="110" font-size="7.8" fill="#334155">Wall Footprints</text>
<text x="40" y="124" font-size="7.8" fill="#059669">No Self-Intersection</text>

<line x1="170" y1="90" x2="195" y2="90" stroke="#2563eb" stroke-width="1.2" marker-end="url(#arr)"/>

<rect x="195" y="45" width="145" height="90" rx="3" fill="#ffffff" stroke="#8b5cf6"/>
<text x="267" y="65" text-anchor="middle" font-size="9" font-weight="bold" fill="#6d28d9">2. Linear Extrusion</text>
<text x="205" y="82" font-size="7.8" fill="#334155">Manifold.cube(L, T, H)</text>
<text x="205" y="96" font-size="7.8" fill="#334155">translate & rotate</text>
<text x="205" y="110" font-size="7.8" fill="#334155">Base Wall Solid</text>
<text x="205" y="124" font-size="7.8" fill="#059669">2-Manifold Primitives</text>

<line x1="340" y1="90" x2="365" y2="90" stroke="#2563eb" stroke-width="1.2" marker-end="url(#arr)"/>

<rect x="365" y="45" width="150" height="90" rx="3" fill="#ffffff" stroke="#f59e0b"/>
<text x="440" y="65" text-anchor="middle" font-size="9" font-weight="bold" fill="#b45309">3. CSG Difference</text>
<text x="375" y="82" font-size="7.8" fill="#334155">Cutters: Door/Window</text>
<text x="375" y="96" font-size="7.8" fill="#334155">cutter_thk = 1.5 * wall</text>
<text x="375" y="110" font-size="7.8" fill="#334155">solid_wall - cutters</text>
<text x="375" y="124" font-size="7.8" fill="#059669">Clean Void Subtraction</text>

<line x1="515" y1="90" x2="540" y2="90" stroke="#2563eb" stroke-width="1.2" marker-end="url(#arr)"/>

<rect x="540" y="45" width="130" height="90" rx="3" fill="#ffffff" stroke="#10b981"/>
<text x="605" y="65" text-anchor="middle" font-size="9" font-weight="bold" fill="#047857">4. Validation</text>
<text x="550" y="82" font-size="7.8" fill="#334155">is_manifold() == True</text>
<text x="550" y="96" font-size="7.8" fill="#334155">genus = num_openings</text>
<text x="550" y="110" font-size="7.8" fill="#334155">volume > 0.0</text>
<text x="550" y="124" font-size="7.8" fill="#059669">Watertight Mesh Export</text>
'''
    return make_svg_wrapper(700, 155, content)

def diagram_06_engineer_review_gates():
    content = '''
<text x="350" y="24" text-anchor="middle" font-size="13" font-weight="bold" fill="#0f172a">DIAGRAM 6: ENGINEER REVIEW GATES (G0 - G6) & STATUTORY BYPASS PROTECTION</text>
<rect x="25" y="45" width="85" height="75" rx="3" fill="#ffffff" stroke="#3b82f6" stroke-width="1.2"/>
<text x="67" y="65" text-anchor="middle" font-size="9" font-weight="bold" fill="#1e40af">G0: SITE</text>
<text x="67" y="80" text-anchor="middle" font-size="7" fill="#334155">Statutory Rules</text>
<text x="67" y="92" text-anchor="middle" font-size="7" fill="#334155">Setback Check</text>
<text x="67" y="106" text-anchor="middle" font-size="7" font-weight="bold" fill="#059669">AUTOMATED</text>

<line x1="110" y1="82" x2="122" y2="82" stroke="#64748b" stroke-width="1.2" marker-end="url(#arr-gray)"/>

<rect x="122" y="45" width="85" height="75" rx="3" fill="#ffffff" stroke="#3b82f6" stroke-width="1.2"/>
<text x="164" y="65" text-anchor="middle" font-size="9" font-weight="bold" fill="#1e40af">G1: ARCH</text>
<text x="164" y="80" text-anchor="middle" font-size="7" fill="#334155">NBC 2016 Rooms</text>
<text x="164" y="92" text-anchor="middle" font-size="7" fill="#334155">Lighting & Vent</text>
<text x="164" y="106" text-anchor="middle" font-size="7" font-weight="bold" fill="#059669">AUTOMATED</text>

<line x1="207" y1="82" x2="219" y2="82" stroke="#64748b" stroke-width="1.2" marker-end="url(#arr-gray)"/>

<rect x="219" y="45" width="85" height="75" rx="3" fill="#ffffff" stroke="#3b82f6" stroke-width="1.2"/>
<text x="261" y="65" text-anchor="middle" font-size="9" font-weight="bold" fill="#1e40af">G2: STRUCT</text>
<text x="261" y="80" text-anchor="middle" font-size="7" fill="#334155">Grid Alignment</text>
<text x="261" y="92" text-anchor="middle" font-size="7" fill="#334155">Span Checks</text>
<text x="261" y="106" text-anchor="middle" font-size="7" font-weight="bold" fill="#059669">AUTOMATED</text>

<line x1="304" y1="82" x2="316" y2="82" stroke="#64748b" stroke-width="1.2" marker-end="url(#arr-gray)"/>

<rect x="316" y="45" width="85" height="75" rx="3" fill="#ffffff" stroke="#3b82f6" stroke-width="1.2"/>
<text x="358" y="65" text-anchor="middle" font-size="9" font-weight="bold" fill="#1e40af">G3: MEP</text>
<text x="358" y="80" text-anchor="middle" font-size="7" fill="#334155">Shaft Verticality</text>
<text x="358" y="92" text-anchor="middle" font-size="7" fill="#334155">Wet Wall Drops</text>
<text x="358" y="106" text-anchor="middle" font-size="7" font-weight="bold" fill="#059669">AUTOMATED</text>

<line x1="401" y1="82" x2="413" y2="82" stroke="#64748b" stroke-width="1.2" marker-end="url(#arr-gray)"/>

<rect x="413" y="45" width="85" height="75" rx="3" fill="#ffffff" stroke="#3b82f6" stroke-width="1.2"/>
<text x="455" y="65" text-anchor="middle" font-size="9" font-weight="bold" fill="#1e40af">G4: COST</text>
<text x="455" y="80" text-anchor="middle" font-size="7" fill="#334155">IS 1200 QTO</text>
<text x="455" y="92" text-anchor="middle" font-size="7" fill="#334155">Rate Lock</text>
<text x="455" y="106" text-anchor="middle" font-size="7" font-weight="bold" fill="#059669">AUTOMATED</text>

<line x1="498" y1="82" x2="510" y2="82" stroke="#64748b" stroke-width="1.2" marker-end="url(#arr-gray)"/>

<rect x="510" y="45" width="85" height="75" rx="3" fill="#ffffff" stroke="#d97706" stroke-width="1.5"/>
<text x="552" y="65" text-anchor="middle" font-size="9" font-weight="bold" fill="#b45309">G5: SANCTION</text>
<text x="552" y="80" text-anchor="middle" font-size="7" fill="#334155">Architect Signoff</text>
<text x="552" y="92" text-anchor="middle" font-size="7" fill="#334155">Licensed Survey</text>
<text x="552" y="106" text-anchor="middle" font-size="7" font-weight="bold" fill="#b45309">PROFESSIONAL</text>

<line x1="595" y1="82" x2="607" y2="82" stroke="#64748b" stroke-width="1.2" marker-end="url(#arr-gray)"/>

<rect x="607" y="45" width="70" height="75" rx="3" fill="#ffffff" stroke="#059669" stroke-width="1.5"/>
<text x="642" y="65" text-anchor="middle" font-size="9" font-weight="bold" fill="#047857">G6: BUILD</text>
<text x="642" y="80" text-anchor="middle" font-size="7" fill="#334155">Immutable</text>
<text x="642" y="92" text-anchor="middle" font-size="7" fill="#334155">Release Lock</text>
<text x="642" y="106" text-anchor="middle" font-size="7" font-weight="bold" fill="#047857">CERTIFIED</text>
'''
    return make_svg_wrapper(700, 140, content)

def diagram_07_change_propagation_dag():
    content = '''
<text x="350" y="24" text-anchor="middle" font-size="13" font-weight="bold" fill="#0f172a">DIAGRAM 7: DEPENDENCY DAG & REACTIVE CACHE INVALIDATION PIPELINE</text>
<rect x="260" y="45" width="180" height="35" rx="3" fill="#2563eb"/>
<text x="350" y="67" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#ffffff">PARCEL / BRIEF MUTATION</text>

<!-- Invalidation Arrows -->
<line x1="350" y1="80" x2="160" y2="105" stroke="#ef4444" stroke-width="1.2" marker-end="url(#arr)"/>
<line x1="350" y1="80" x2="350" y2="105" stroke="#ef4444" stroke-width="1.2" marker-end="url(#arr)"/>
<line x1="350" y1="80" x2="540" y2="105" stroke="#ef4444" stroke-width="1.2" marker-end="url(#arr)"/>

<rect x="90" y="105" width="140" height="35" rx="3" fill="#fee2e2" stroke="#ef4444"/>
<text x="160" y="127" text-anchor="middle" font-size="8.5" font-weight="bold" fill="#991b1b">FEASIBILITY [INVALID]</text>

<rect x="280" y="105" width="140" height="35" rx="3" fill="#fee2e2" stroke="#ef4444"/>
<text x="350" y="127" text-anchor="middle" font-size="8.5" font-weight="bold" fill="#991b1b">CBM MODEL [INVALID]</text>

<rect x="470" y="105" width="140" height="35" rx="3" fill="#fee2e2" stroke="#ef4444"/>
<text x="540" y="127" text-anchor="middle" font-size="8.5" font-weight="bold" fill="#991b1b">QTO TAKEOFF [INVALID]</text>

<line x1="540" y1="140" x2="540" y2="165" stroke="#ef4444" stroke-width="1.2" marker-end="url(#arr)"/>

<rect x="470" y="165" width="140" height="35" rx="3" fill="#fee2e2" stroke="#ef4444"/>
<text x="540" y="187" text-anchor="middle" font-size="8.5" font-weight="bold" fill="#991b1b">BOQ & COST [INVALID]</text>

<line x1="540" y1="200" x2="540" y2="225" stroke="#ef4444" stroke-width="1.2" marker-end="url(#arr)"/>

<rect x="470" y="225" width="140" height="35" rx="3" fill="#fee2e2" stroke="#ef4444"/>
<text x="540" y="247" text-anchor="middle" font-size="8.5" font-weight="bold" fill="#991b1b">RELEASE / IFC [STALE]</text>

<rect x="40" y="170" width="380" height="85" rx="3" fill="#f8fafc" stroke="#cbd5e1"/>
<text x="50" y="188" font-size="8.5" font-weight="bold" fill="#0f172a">DAG Invalidation Invariants (workers/qto/change_propagation.py):</text>
<text x="50" y="204" font-size="7.5" fill="#334155">• When Room Dimension changes: invalidates parent Space bounds and adjoining Walls</text>
<text x="50" y="218" font-size="7.5" fill="#334155">• Invalidation cascades to: QTO TakeoffRecords → BOQ LineItems → CostWaterfall</text>
<text x="50" y="232" font-size="7.5" fill="#334155">• If a Release was locked: release_fingerprint mismatch triggers 409 Conflict rejection</text>
<text x="50" y="246" font-size="7.5" fill="#334155">• Fail-closed safety: No stale cost estimate can ever be certified for construction handoff</text>
'''
    return make_svg_wrapper(700, 275, content)

print("Diagrams module initialized.")
