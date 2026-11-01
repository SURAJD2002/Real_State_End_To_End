"""
Planwise Enterprise — Technical Encyclopedia Volumes VI - X
Volume VI: Database, Persistence, and Data Lineage
Volume VII: Canonical Building Model & Domain Schemas
Volume VIII: Land, GIS, and Statutory Feasibility
Volume IX: Design Generation and Computational Optimization
Volume X: Computational Geometry and 3D Model Generation
"""

from scripts.encyclopedia_volumes.expanded_content import (
    get_all_sql_migrations, get_real_code_snippet, get_svg_diagram_html
)

def get_volume_06() -> dict:
    migration_docs = get_all_sql_migrations()
    diag7 = get_svg_diagram_html("07_change_propagation_dag.svg", "Diagram 7: Change Propagation DAG and Dependency Cascade")
    md = f"""# Volume VI — Database, Persistence, and Data Lineage

## 1. Database Architecture & Migration Topology
The persistent storage layer is built on **PostgreSQL 16** with relational tables, foreign key constraints, and JSONB document columns.

{diag7}

The repository contains **14 SQL migration files** across two directories:
1. `supabase/migrations/` (8 Active Migrations):
   - `20261010010000_initial_schema.sql` — Core tables (`organizations`, `users`, `projects`, `plots`).
   - `20261010020000_statutory_and_feasibility.sql` — Feasibility records and statutory rule packs.
   - `20261010030000_cbm_and_designs.sql` — Canonical Building Model storage (`designs`, `floors`, `rooms`).
   - `20261010040000_qto_and_cost.sql` — Bill of quantities and itemized rate catalogs.
   - `20261010050000_engineer_review_and_releases.sql` — Engineering review gates and release ledger.
   - `20261010060000_audit_logs.sql` — Immutable event audit logging.
   - `20261010070000_security_and_rls_policies.sql` — Enables RLS on 34 tables and declares access policies.
   - `20261010080000_organization_membership_mapping.sql` — Multi-tenant organization member relations.
2. `database/migrations/` (6 Legacy Migrations):
   - Mirror migrations `01` through `06` used for standalone PostgreSQL container deployments without Supabase extensions.

---

## 2. Inventory of Tables and Row-Level Security Enablement
All 34 application tables have `ALTER TABLE ... ENABLE ROW LEVEL SECURITY;` executed in migration `07`:

| Table Name | Primary Key | Foreign Keys | RLS Enabled | Core Purpose |
| :--- | :--- | :--- | :---: | :--- |
| `organizations` | `id (UUID)` | None | Yes | Multi-tenant organization boundaries |
| `users` | `id (UUID)` | `organizations(id)` | Yes | User identity, credentials, and enterprise roles |
| `organization_members`| `id (UUID)`| `org_id`, `user_id` | Yes | Organization membership mapping |
| `projects` | `id (UUID)` | `org_id`, `user_id` | Yes | Top-level project entity and plot reference |
| `plots` | `id (UUID)` | `projects(id)` | Yes | Boundary coordinates, road width, jurisdiction |
| `feasibility_reports` | `id (UUID)` | `plots(id)` | Yes | Setback envelopes, permissible FSI, coverage |
| `designs` | `id (UUID)` | `projects(id)` | Yes | Canonical Building Model JSON and metadata |
| `floors` | `id (UUID)` | `designs(id)` | Yes | Floor level definitions and elevation heights |
| `rooms` | `id (UUID)` | `floors(id)` | Yes | Room dimensions, usage types, boundary vectors |
| `wall_segments` | `id (UUID)` | `floors(id)` | Yes | Centerline wall coordinates, thickness, materials |
| `openings` | `id (UUID)` | `wall_segments(id)` | Yes | Doors and windows dimensions and schedules |
| `boq_records` | `id (UUID)` | `designs(id)` | Yes | Itemized IS 1200 quantity takeoffs |
| `cost_estimates` | `id (UUID)` | `boq_records(id)` | Yes | Rate catalogs, markups, and cost waterfall |
| `engineer_reviews` | `id (UUID)` | `projects(id)` | Yes | G0–G6 sign-off status, comments, timestamps |
| `releases` | `id (UUID)` | `projects(id)` | Yes | Immutable release ledger and manifest hashes |
| `audit_logs` | `id (UUID)` | `organizations(id)` | Yes | Append-only event ledger |

---

## 3. Complete DDL Specification of Active Supabase SQL Migrations

{migration_docs}
"""
    return {"title": "Volume VI — Database, Persistence, and Data Lineage", "md": md}


def get_volume_07() -> dict:
    cbm_code = get_real_code_snippet("packages/schemas/building_model.py", max_lines=250)
    diag3 = get_svg_diagram_html("03_cbm_structure.svg", "Diagram 3: Canonical Building Model Topological Hierarchy")
    md = f"""# Volume VII — Canonical Building Model and Domain Schemas

## 1. The Canonical Building Model (CBM) Paradigm
The **Canonical Building Model (CBM)** is the authoritative, single-source-of-truth domain model in Planwise Enterprise. Implemented in `packages/schemas/building_model.py` using **Pydantic v2**, the CBM decouples spatial programming from geometry kernels, quantity takeoffs, drawing compilers, and IFC emissions.

{diag3}

---

## 2. Authoritative Domain Schema Code Listing (`packages/schemas/building_model.py`)

```python
{cbm_code}
```

---

## 3. Coordinate Conventions and Physical Units
- **Length:** International Standard Meters ($m$) rounded to 4 decimal places ($0.1\\text{{ mm}}$ precision).
- **Area:** Square Meters ($m^2$) and Square Feet (sq ft) where $1\\text{{ m}}^2 = 10.7639\\text{{ sq ft}}$.
- **Volume:** Cubic Meters ($m^3$).
- **Mass:** Metric Tonnes (MT) or Kilograms (kg).
- **Coordinate System:** Right-handed Cartesian $(X, Y, Z)$:
  - $+X$: East / Width axis.
  - $+Y$: North / Depth axis.
  - $+Z$: Up / Vertical elevation axis ($Z = 0.0$ at Ground Plinth level).
"""
    return {"title": "Volume VII — Canonical Building Model and Domain Schemas", "md": md}


def get_volume_08() -> dict:
    rule_code = get_real_code_snippet("workers/regulation/rule_engine.py", max_lines=250)
    md = f"""# Volume VIII — Land, GIS, and Statutory Feasibility

## 1. Land Intake and Statutory Feasibility Architecture
The statutory feasibility engine (`workers/regulation/rule_engine.py`) orchestrates an authoritative, deterministic compliance pipeline:
```
SITE ──> PARCEL ──> ROAD CONTEXT ──> LAND USE ──> ROAD WIDENING ──> BUILDABLE AREA
                                                                         │
FINAL FEASIBILITY <── PARKING <── HEIGHT <── COVERAGE <── FSI/FAR <── SETBACKS
```

---

## 2. Statutory Rule Engine Implementation (`workers/regulation/rule_engine.py`)

```python
{rule_code}
```

---

## 3. Municipal Rule Packs (Mumbai DCPR 2034 & BBMP 2026)
Planwise packages declarative JSON rule definitions:
- **Mumbai DCPR 2034:** `packages/rules/mumbai_dcpr_2034_v1.json` (Regulation 43 Marginal Open Spaces, Table 12, FSI 1.50).
- **BBMP Bengaluru 2026:** `packages/rules/bbmp_bengaluru_2026.json` (Table 7 Setbacks, FAR 1.25 to 1.75).
"""
    return {"title": "Volume VIII — Land, GIS, and Statutory Feasibility", "md": md}


def get_volume_09() -> dict:
    cpsat_code = get_real_code_snippet("workers/generation/cpsat_solver.py", max_lines=250)
    diag4 = get_svg_diagram_html("04_cpsat_solver.svg", "Diagram 4: Google OR-Tools CP-SAT Layout Optimization Pipeline")
    md = f"""# Volume IX — Design Generation and Computational Optimization

## 1. Architectural Floor Plan Optimization via CP-SAT
Layout generation is executed as a **Discrete Constraint Satisfaction Problem (CSP)** using the **Google OR-Tools CP-SAT** engine (`workers/generation/cpsat_solver.py`).

Operates on integer-scaled coordinates ($1\\text{{ solver unit}} = 100\\text{{mm}} = 0.1\\text{{m}}$).

{diag4}

---

## 2. Solver Implementation Code Listing (`workers/generation/cpsat_solver.py`)

```python
{cpsat_code}
```

---

## 3. Multi-Objective Pareto Alternatives
To provide developers with diverse architectural options, the solver optimizes three distinct objectives:
- **Option A (Circulation Efficiency):** Minimizes total circulation corridor area while maximizing living room volume.
- **Option B (Vaastu Shastra Compliance):** Rewards placement of Kitchen in South-East (Agni corner) and Master Bedroom in South-West (Nairutya corner).
- **Option C (Maximum Living Space):** Maximizes aggregate bedroom and living room square footage at the expense of corridor buffer space.
"""
    return {"title": "Volume IX — Design Generation and Computational Optimization", "md": md}


def get_volume_10() -> dict:
    geom_code = get_real_code_snippet("workers/geometry/solid_engine.py", max_lines=250)
    diag5 = get_svg_diagram_html("05_manifold3d_geometry.svg", "Diagram 5: Manifold3D Watertight Mesh Boolean CSG Pipeline")
    md = f"""# Volume X — Computational Geometry and 3D Model Generation

## 1. Watertight 3D Solids Modeling with Manifold3D
3D physical geometry in Planwise is synthesized using the **Manifold3D** C++ computational geometry kernel (`workers/geometry/solid_engine.py`).

### The 2-Manifold Topological Invariant
A surface mesh is a **watertight 2-manifold** if and only if:
1. Every edge is shared by exactly two adjacent faces.
2. The neighbourhood of every vertex is topologically equivalent to an open 2D disk.
3. No self-intersections or non-manifold edges exist.
4. The **Euler characteristic** satisfies:
   $$\\chi = V - E + F = 2(1 - g)$$
   For closed genus-0 solids without through-holes, $\\chi = 2$.

{diag5}

---

## 2. Geometry Kernel Implementation Code Listing (`workers/geometry/solid_engine.py`)

```python
{geom_code}
```

---

## 3. Verification via Test Suite
The 3D kernel is verified by `tests/test_geometry_invariants.py`:
- Watertightness check returns `True`.
- Euler characteristic $\\chi = 2$ strictly confirmed.
- Volume is strictly positive ($V > 0$).
- Total surface area matches analytical polygon sum.
"""
    return {"title": "Volume X — Computational Geometry and 3D Model Generation", "md": md}
