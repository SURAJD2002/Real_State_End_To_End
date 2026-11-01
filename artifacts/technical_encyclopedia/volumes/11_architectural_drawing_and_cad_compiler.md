# Volume XI — Architectural Drawing and CAD Compiler

## 1. Multi-View Orthographic Projection Compiler
Planwise Enterprise incorporates a dedicated **Architectural Drawing Compiler** (`workers/generation/drawing_compiler.py`) that translates the Canonical Building Model into standard multi-view projection drawings conforming to Bureau of Indian Standards (BIS) architectural drafting conventions (SP 46: 2003).

---

## 2. Drawing Compiler Source Code Listing (`drawing_compiler.py`)

```python
"""
Planwise Enterprise — Deterministic Professional Drawing Compiler
Milestone 2 — Professional Drawing Pipeline
==================================================================

Architecture:
  CBM (Canonical Building Model)
   ↓
  Drawing Compiler (Deterministic extraction & projection)
   ↓
  Projection / View Generation (Plans, Elevations, Sections)
   ↓
  Dimension Engine & Annotations (Meters & Millimeters from CBM)
   ↓
  Door / Window Tagging & Schedules (Traceable to CBM IDs)
   ↓
  Title Block & North Arrow (ISO 128 / Planwise Standard)
   ↓
  Dual Output: Publication-Grade PDF & Structured Semantic SVG

Guarantees:
1. Zero AI or image-to-drawing hallucination.
2. Read-only treatment of CBM — CBM is NEVER mutated.
3. 100% byte-for-byte reproducible PDF and SVG artifacts across repeated compilation.
4. Professional boundary disclaimers on every sheet (preliminary, licensed engineer review required).
5. Explicit architectural scales (1:100 default) preserving physical scale on A3 sheet.
6. Emits `drawing_manifest.json` binding all drawing hashes, CBM hash, and source elements.
"""

import os
import io
import math
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A3, landscape

from packages.schemas.building_model import (
    CanonicalBuildingModel,
    ElementType,
    WallType,
    OpeningType,
    StairType
)
from workers.generation.drawing_styles import (
    SHEET_SIZES,
    LINE_WEIGHTS,
    COLORS,
    FONT_SIZES,
    SCALE_POINTS_PER_METER,
    DISCLAIMER_PRELIMINARY,
    DISCLAIMER_STRUCTURAL
)
from workers.generation.projections import (
    generate_floor_plan,
    generate_elevation,
    generate_section
)


# =============================================================================
# Structured Exception Hierarchy
# =============================================================================

class DrawingCompilerError(Exception):
    """Base exception for Drawing Compiler operations."""
    def __init__(self, code: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message
        self.details = details or {}


class DrawingSourceDataMissingError(DrawingCompilerError):
    """Raised when required authoritative CBM geometry is missing."""
    def __init__(self, missing_dependency: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="DRAWING_SOURCE_DATA_MISSING",
            message=f"Authoritative CBM lacks required geometry: {missing_dependency}",
            details={"missingDependency": missing_dependency, **(details or {})}
        )


class DrawingGeometryInvalidError(DrawingCompilerError):
    """Raised when CBM geometry contains degenerate or invalid coordinate data."""
    def __init__(self, element_id: str, reason: str):
        super().__init__(
            code="DRAWING_GEOMETRY_INVALID",
            message=f"Invalid geometry in element '{element_id}': {reason}",
            details={"elementId": element_id, "reason": reason}
        )


class DrawingGenerationFailedError(DrawingCompilerError):
    """Raised when view generation or sheet compilation fails."""
    def __init__(self, drawing_id: str, reason: str):
        super().__init__(
            code="DRAWING_GENERATION_FAILED",
            message=f"Failed to generate drawing '{drawing_id}': {reason}",
            details={"drawingId": drawing_id, "reason": reason}
        )


# =============================================================================
# Drawing Set Specifications (Milestone 2 Required Views)
# =============================================================================

DRAWING_SPECS: List[Dict[str, Any]] = [
    {
        "drawingId": "A-101",
        "drawingTitle": "GROUND FLOOR PLAN",
        "viewType": "PLAN",
        "levelId": "LVL-000",
        "sheetNumber": "1 OF 9",
        "scale": "1:100",
        "description": "Ground floor layout with architectural walls, openings, stairs, structural columns, and room dimensions."
    },
    {
        "drawingId": "A-102",
        "drawingTitle": "FIRST FLOOR PLAN",
        "viewType": "PLAN",
        "levelId": "LVL-001",
        "sheetNumber": "2 OF 9",
        "scale": "1:100",
        "description": "First floor layout with master bedroom suite, attached bath, living balcony, and stair core."
    },
    {
        "drawingId": "A-103",
        "drawingTitle": "TERRACE / ROOF PLAN",
        "viewType": "ROOF_PLAN",
        "levelId": "LVL-ROOF",
        "sheetNumber": "3 OF 9",
        "scale": "1:100",
        "description": "Terrace level plan showing parapet perimeter, stair cabin enclosure, and rainwater drainage falls."
    },
    {
        "drawingId": "A-201",
        "drawingTitle": "FRONT ELEVATION (SOUTH)",
        "viewType": "ELEVATION",
        "direction": "SOUTH",
        "sheetNumber": "4 OF 9",
        "scale": "1:100",
        "description": "South principal street elevation showing entry facade, fenestration, plinth, and floor level datums."
    },
    {
        "drawingId": "A-202",
        "drawingTitle": "REAR ELEVATION (NORTH)",
        "viewType": "ELEVATION",
        "direction": "NORTH",
        "sheetNumber": "5 OF 9",
        "scale": "1:100",
        "description": "North rear elevation showing boundary envelope, service fenestration, and vertical height markers."
    },
    {
        "drawingId": "A-203",
        "drawingTitle": "LEFT ELEVATION (WEST)",
        "viewType": "ELEVATION",
        "direction": "WEST",
        "sheetNumber": "6 OF 9",
        "scale": "1:100",
        "description": "West flank elevation showing side setback profile, fenestration bands, and floor slab datums."
    },
    {
        "drawingId": "A-204",
        "drawingTitle": "RIGHT ELEVATION (EAST)",
        "viewType": "ELEVATION",
        "direction": "EAST",
        "sheetNumber": "7 OF 9",
        "scale": "1:100",
        "description": "East flank elevation showing side wall masses, ventilation louvers, and roof parapet level."
    },
    {
        "drawingId": "A-301",
        "drawingTitle": "LONGITUDINAL SECTION (A-A)",
        "viewType": "SECTION",
        "cutPlane": "A-A",

```

---

## 3. Complete Inventory of the 9 Architectural Sheets

| Sheet Number | Drawing Title | Scale | Projection Type | Key Visual Information Included |
| :--- | :--- | :---: | :--- | :--- |
| **A-101** | Ground Floor Plan | 1:100 | Horizontal Section at $Z = +1.2\text{ m}$ | Room dimensions, wall thicknesses, door swings, window schedules, column grid |
| **A-102** | First Floor Plan | 1:100 | Horizontal Section at $Z = +4.2\text{ m}$ | Upper bedrooms, balconies, staircase cutout, plumbing shaft locations |
| **A-103** | Terrace & Roof Plan | 1:100 | Top Down Exterior Projection | Parapet wall ($1.0\text{ m}$), rainwater drain slope (1:100), overhead water tank |
| **A-201** | Front Elevation (South)| 1:100 | Vertical Exterior Projection | Plinth level ($+0.6\text{ m}$), floor heights, lintel levels, parapet top, facade finishes |
| **A-202** | Rear Elevation (North) | 1:100 | Vertical Exterior Projection | Rear fenestrations, kitchen utility access, rear boundary setback clearance |
| **A-203** | Left Elevation (West) | 1:100 | Vertical Exterior Projection | Side setback clearance, toilet louvers, stair tower profile |
| **A-204** | Right Elevation (East) | 1:100 | Vertical Exterior Projection | Side fenestrations, sunshade chajjas, compound wall plinth |
| **A-301** | Longitudinal Section A-A | 1:100 | Vertical Cut through Living & Stair | Foundation footing, plinth beam, slab thicknesses ($150\text{ mm}$), stair tread/riser |
| **A-302** | Cross Section B-B | 1:100 | Vertical Cut through Bedrooms & Toilet | Sunken slab ($300\text{ mm}$), lintel beam, sill levels, parapet coping |

---

## 4. Vector CAD Rendering and Export Pipeline
Drawings are generated as pure vector graphics:
- **Primary Internal Format:** SVG (Scalable Vector Graphics) with millimeter viewBox units.
- **Title Block Template:** Bureau of Indian Standards compliant title block containing Project Title, Client Name, Plot Number, Scale, Drawing Number, Revision, and Lead Engineer Signature Box.
- **PDF Compilation:** High-resolution vector PDF rendered via Chrome/Puppeteer vector print backend without rasterization loss.
- **Verification Evidence:** All 9 PDF drawing sheets are verified on disk in `artifacts/test_drawings_m2/` and cataloged in `drawing_manifest.json`.
