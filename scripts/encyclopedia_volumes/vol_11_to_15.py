"""
Planwise Enterprise — Technical Encyclopedia Volumes XI - XV
Volume XI: Architectural Drawing and CAD Compiler
Volume XII: Quantity Takeoff, BOQ, and Cost Engine
Volume XIII: Engineering Review, Releases, and Construction Handoff
Volume XIV: IFC/BIM and Interoperability
Volume XV: AI Boundary and Deterministic Behavior
"""

from scripts.encyclopedia_volumes.expanded_content import (
    get_real_code_snippet
)

def get_volume_11() -> dict:
    compiler_code = get_real_code_snippet("workers/generation/drawing_compiler.py", max_lines=180)
    md = f"""# Volume XI — Architectural Drawing and CAD Compiler

## 1. Multi-View Orthographic Projection Compiler
Planwise Enterprise incorporates a dedicated **Architectural Drawing Compiler** (`workers/generation/drawing_compiler.py`) that translates the Canonical Building Model into standard multi-view projection drawings conforming to Bureau of Indian Standards (BIS) architectural drafting conventions (SP 46: 2003).

---

## 2. Drawing Compiler Source Code Listing (`drawing_compiler.py`)

```python
{compiler_code}
```

---

## 3. Complete Inventory of the 9 Architectural Sheets

| Sheet Number | Drawing Title | Scale | Projection Type | Key Visual Information Included |
| :--- | :--- | :---: | :--- | :--- |
| **A-101** | Ground Floor Plan | 1:100 | Horizontal Section at $Z = +1.2\\text{{ m}}$ | Room dimensions, wall thicknesses, door swings, window schedules, column grid |
| **A-102** | First Floor Plan | 1:100 | Horizontal Section at $Z = +4.2\\text{{ m}}$ | Upper bedrooms, balconies, staircase cutout, plumbing shaft locations |
| **A-103** | Terrace & Roof Plan | 1:100 | Top Down Exterior Projection | Parapet wall ($1.0\\text{{ m}}$), rainwater drain slope (1:100), overhead water tank |
| **A-201** | Front Elevation (South)| 1:100 | Vertical Exterior Projection | Plinth level ($+0.6\\text{{ m}}$), floor heights, lintel levels, parapet top, facade finishes |
| **A-202** | Rear Elevation (North) | 1:100 | Vertical Exterior Projection | Rear fenestrations, kitchen utility access, rear boundary setback clearance |
| **A-203** | Left Elevation (West) | 1:100 | Vertical Exterior Projection | Side setback clearance, toilet louvers, stair tower profile |
| **A-204** | Right Elevation (East) | 1:100 | Vertical Exterior Projection | Side fenestrations, sunshade chajjas, compound wall plinth |
| **A-301** | Longitudinal Section A-A | 1:100 | Vertical Cut through Living & Stair | Foundation footing, plinth beam, slab thicknesses ($150\\text{{ mm}}$), stair tread/riser |
| **A-302** | Cross Section B-B | 1:100 | Vertical Cut through Bedrooms & Toilet | Sunken slab ($300\\text{{ mm}}$), lintel beam, sill levels, parapet coping |

---

## 4. Vector CAD Rendering and Export Pipeline
Drawings are generated as pure vector graphics:
- **Primary Internal Format:** SVG (Scalable Vector Graphics) with millimeter viewBox units.
- **Title Block Template:** Bureau of Indian Standards compliant title block containing Project Title, Client Name, Plot Number, Scale, Drawing Number, Revision, and Lead Engineer Signature Box.
- **PDF Compilation:** High-resolution vector PDF rendered via Chrome/Puppeteer vector print backend without rasterization loss.
- **Verification Evidence:** All 9 PDF drawing sheets are verified on disk in `artifacts/test_drawings_m2/` and cataloged in `drawing_manifest.json`.
"""
    return {"title": "Volume XI — Architectural Drawing and CAD Compiler", "md": md}


def get_volume_12() -> dict:
    boq_code = get_real_code_snippet("workers/qto/boq_engine.py", max_lines=150)
    qto_code = get_real_code_snippet("workers/qto/qto_engine.py", max_lines=250)
    cost_code = get_real_code_snippet("workers/qto/cost_engine.py", max_lines=250)
    md = f"""# Volume XII — Quantity Takeoff, BOQ, and Cost Engine

## 1. Indian Standard IS 1200 Measurement Principles
Quantity extraction in Planwise (`workers/qto/qto_engine.py`) strictly adheres to **IS 1200: Methods of Measurement of Building Works**:

### 1.1 IS 1200 Part 2: Concrete Work
- Plinth beams, columns, lintels, and floor slabs measured net in cubic meters ($m^3$).
- Slab volume: $V_{{\\text{{slab}}}} = A_{{\\text{{slab}}}} \\times T_{{\\text{{slab}}}}$ ($T = 0.15\\text{{ m}}$).
- Column volume: $V_{{\\text{{col}}}} = N_{{\\text{{col}}}} \\times W \\times D \\times H$.

### 1.2 IS 1200 Part 3: Brick and Block Masonry
- Wall masonry volume calculated net in cubic meters ($m^3$):
  $$V_{{\\text{{masonry}}}} = L_{{\\text{{wall}}}} \\times T_{{\\text{{wall}}}} \\times H_{{\\text{{wall}}}} - V_{{\\text{{openings}}}} - V_{{\\text{{lintels}}}}$$

### 1.3 IS 1200 Part 12: Plastering Opening Deduction Rules
Strict opening deduction logic implemented in `workers/qto/qto_engine.py`:
- **Opening Area $< 0.5\\text{{ m}}^2$:** No deduction made; no addition for jambs/sills.
- **Opening Area $0.5\\text{{ m}}^2 \\le A \\le 3.0\\text{{ m}}^2$:** Deduction made for **one face only**; no addition for jambs or sills.
- **Opening Area $> 3.0\\text{{ m}}^2$:** Deductions made for **both faces** of the wall; additions made for jambs, sills, and soffits.

---

## 2. Model-Linked QTO Engine Implementation (`workers/qto/qto_engine.py`)

```python
{qto_code}
```

---

## 3. Deterministic Cost Engine Implementation (`workers/qto/cost_engine.py`)

```python
{cost_code}
```

---

## 4. Traceable BOQ Controller Interface (`workers/qto/boq_engine.py`)

```python
{boq_code}
```

---

## 5. Comprehensive Cost Waterfall Architecture
The financial calculation structures project expenditure into a transparent multi-tiered waterfall:
```
  Base Direct Material Cost
+ Direct Skilled & Unskilled Labour
─────────────────────────────────────────────────
= Subtotal Prime Cost (Direct Works)
+ Site Contractor Overhead (10.0%)
+ Contractor Margin & Profit (15.0%)
─────────────────────────────────────────────────
= Subtotal Base Construction Cost
+ Unforeseen Contingency Reserve (5.0%)
─────────────────────────────────────────────────
= Total Pre-Tax Project Estimate
+ Statutory GST Tax (18.0%)
─────────────────────────────────────────────────
= FINAL GROSS BUDGET ESTIMATE
```
"""
    return {"title": "Volume XII — Quantity Takeoff, BOQ, and Cost Engine", "md": md}


def get_volume_13() -> dict:
    from scripts.encyclopedia_volumes.expanded_content import get_svg_diagram_html
    review_schema = get_real_code_snippet("packages/schemas/engineer_review.py", max_lines=180)
    diag6 = get_svg_diagram_html("06_engineer_review_gates.svg", "Diagram 6: Seven-Stage Sequential Engineering Review Gate Transition Machine (G0–G6)")
    md = f"""# Volume XIII — Engineering Review, Releases, and Construction Handoff

## 1. Seven-Stage Engineering Review Gate Model (G0–G6)
Planwise enforces a rigorous, sequentially locked engineering sign-off gate sequence (`packages/schemas/engineer_review.py`):

{diag6}

```
[G0_SITE] ──> [G1_STRUCTURAL] ──> [G2_ARCHITECTURAL] ──> [G3_MEP]
    │                │                   │                  │
Boundary & GPS   Grid Alignment      NBC 2016 Flow      Plumbing & Power
    │                │                   │                  │
    ▼                ▼                   ▼                  ▼
[G4_STATUTORY] ─────────────────> [G5_COST] ───────> [G6_CONSTRUCTION]
Municipal Setbacks                BOQ & Budget       Contractor Handoff
```

---

## 2. Review Gate Schema Source Code (`engineer_review.py`)

```python
{review_schema}
```

---

## 3. Review Gate Roadmap Clarification (G7 & G8)
> [!NOTE]
> Historical documentation referenced review gates G0 through G8. In the actual code implementation:
> - **Active Review Gates:** Strictly **G0 through G6** (7 gates) implemented in `GateCode` enum and database tables.
> - **Roadmap Milestones:** `G7` (Site Release & Groundbreaking) and `G8` (Completion Certificate & Handover) represent statutory Critical Path Method (CPM) milestones in scheduling algorithms, but possess no active API review endpoints.
"""
    return {"title": "Volume XIII — Engineering Review, Releases, and Construction Handoff", "md": md}


def get_volume_14() -> dict:
    ifc_snippet = get_real_code_snippet("artifacts/pilot_handoff/pilot_model_ifc4.ifc", max_lines=120)
    md = f"""# Volume XIV — IFC/BIM and Interoperability

## 1. Industry Foundation Classes (IFC4) Export Architecture
Planwise provides open BIM interoperability by exporting building models in **IFC4 SPF (STEP Physical File)** format conforming to **ISO 16739-1:2018** (`workers/release/manifest_engine.py`).

---

## 2. Emitted IFC4 SPF Model File Excerpt (`pilot_model_ifc4.ifc`)

```
{ifc_snippet}
```

---

## 3. Spatial Decomposition Hierarchy
The emitted IFC model establishes a compliant Industry Foundation Classes spatial hierarchy:
```
IfcProject ("Planwise Enterprise Autonomous Model")
└── IfcSite ("Plot Boundary Parcel", WGS84 Georeferenced)
    └── IfcBuilding ("Residential Villa / Multi-Story")
        ├── IfcBuildingStorey ("Level 00 - Ground Floor", Elevation: +0.0m)
        │   ├── IfcWall ("Exterior Brick Masonry 230mm")
        │   ├── IfcWall ("Interior Partition 115mm")
        │   ├── IfcSlab ("Floor Slab 150mm Concrete")
        │   ├── IfcDoor ("Standard Timber Flush Door 900x2100mm")
        │   ├── IfcWindow ("Aluminium Glazed Window 1200x1200mm")
        │   └── IfcColumn ("RCC Column 300x450mm")
        └── IfcBuildingStorey ("Level 01 - First Floor", Elevation: +3.0m)
            └── ...
```
"""
    return {"title": "Volume XIV — IFC/BIM and Interoperability", "md": md}


def get_volume_15() -> dict:
    md = """# Volume XV — AI Boundary and Deterministic Behavior

## 1. Rigorous Forensic Assessment: AI Claims vs. Reality
Many contemporary software platforms market themselves as "AI-powered." A forensic code audit of Planwise Enterprise reveals a critical architectural truth:

> [!IMPORTANT]
> **Planwise Enterprise does NOT rely on Large Language Models (LLMs), neural networks, or generative diffusion models in its core computational pipeline.**
> Every spatial layout, statutory setback, 3D solid mesh, quantity takeoff, and drawing projection is produced by **deterministic, mathematically verifiable algorithms**.

---

## 2. Subsystem Determinism Analysis

| Platform Subsystem | Implementation Type | Algorithm / Library | Determinism Guarantee |
| :--- | :--- | :--- | :---: |
| **Statutory Feasibility** | Pure Rule-Based Engine | Shapely polygon buffering | 100% Deterministic |
| **Room Layout Generation** | Discrete Constraint Satisfaction | Google OR-Tools CP-SAT (seed=42) | 100% Deterministic |
| **3D Solids Modeling** | Computational Geometry | Manifold3D C++ B-rep kernel | 100% Deterministic |
| **Quantity Takeoff (QTO)** | Standardized Formula Engine | IS 1200 deduction rules | 100% Deterministic |
| **Cost Waterfall** | Arithmetic Rate Engine | Regional rate catalog matrices | 100% Deterministic |
| **Drawing Compilation** | Vector Projection Engine | Python vector geometry compiler | 100% Deterministic |
| **BIM Generation** | Schema-Driven Serializer | IfcOpenShell ISO 16739 emitter | 100% Deterministic |
| **Review Gate Governance** | Finite State Machine | Strict role-based transition checks | 100% Deterministic |

---

## 3. Benefits of Algorithmic Determinism in Civil Engineering
1. **Zero Hallucination:** No generative hallucinations where doors lead to nowhere, walls float in mid-air, or setbacks violate municipal laws.
2. **Reproducibility:** Given the identical plot polygon and design brief, the system yields byte-for-byte identical CBM models and SHA-256 release hashes.
3. **Forensic Auditability:** Every quantity deduction and setback can be audited against statutory building codes and mathematical formulas.
"""
    return {"title": "Volume XV — AI Boundary and Deterministic Behavior", "md": md}
