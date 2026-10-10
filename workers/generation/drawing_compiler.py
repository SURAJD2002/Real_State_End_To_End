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
        "cutAxis": "X",
        "sheetNumber": "8 OF 9",
        "scale": "1:100",
        "description": "Longitudinal section along building length showing slab depths, cut walls, room heights, and roof slab."
    },
    {
        "drawingId": "A-302",
        "drawingTitle": "CROSS SECTION (B-B)",
        "viewType": "SECTION",
        "cutPlane": "B-B",
        "cutAxis": "Y",
        "sheetNumber": "9 OF 9",
        "scale": "1:100",
        "description": "Transverse cross section through living and staircase core showing stair flights, floor transitions, and ceiling datums."
    }
]


# =============================================================================
# Viewport & Coordinate Transformer
# =============================================================================

class ViewportTransformer:
    """
    Transforms 2D architectural coordinates (meters) to sheet paper points.
    Preserves true architectural scale (default 1:100 = 28.3465 pt/m).
    """
    def __init__(
        self,
        bounds_u: Tuple[float, float],
        bounds_v: Tuple[float, float],
        sheet_w: float = 1190.55,
        sheet_h: float = 841.89,
        scale_name: str = "1:100"
    ):
        self.sheet_w = sheet_w
        self.sheet_h = sheet_h
        self.scale_name = scale_name
        self.pt_per_m = SCALE_POINTS_PER_METER.get(scale_name, 28.3465)

        u_min, u_max = bounds_u
        v_min, v_max = bounds_v
        self.model_cx = (u_min + u_max) / 2.0
        self.model_cy = (v_min + v_max) / 2.0

        # Viewport center in sheet coordinates (main drawing area)
        # Sheet usable area: left margin 56.69, right margin 28.35, title block occupies right 802..1162
        self.vp_cx = 420.0
        self.vp_cy = 440.0

    def to_pdf(self, u: float, v: float) -> Tuple[float, float]:
        """PDF coordinate system: (0,0) is bottom-left, Y increases upward."""
        x = self.vp_cx + (u - self.model_cx) * self.pt_per_m
        y = self.vp_cy + (v - self.model_cy) * self.pt_per_m
        return round(x, 2), round(y, 2)

    def to_svg(self, u: float, v: float) -> Tuple[float, float]:
        """SVG coordinate system: (0,0) is top-left, Y increases downward."""
        x = self.vp_cx + (u - self.model_cx) * self.pt_per_m
        y = (self.sheet_h - self.vp_cy) - (v - self.model_cy) * self.pt_per_m
        return round(x, 2), round(y, 2)


# =============================================================================
# Helper Utilities: Tagging, Dimensions, Formatting
# =============================================================================

def format_dim(val_m: float) -> str:
    """Deterministic dimension label: metric meters with 2 decimals."""
    return f"{val_m:.2f} m"


def format_dim_mm(val_m: float) -> str:
    """Deterministic dimension label: millimeters without decimals."""
    return f"{int(round(val_m * 1000))}"


def assign_opening_tags(openings: List[Any]) -> Dict[str, str]:
    """
    Deterministic opening tagging (D01, D02, ... and W01, W02, ...).
    Sorted deterministically by hostWallId and positionM.
    """
    doors = []
    windows = []
    for o in openings:
        op_type = getattr(o, "openingType", None)
        if hasattr(op_type, "value"):
            op_type_val = op_type.value
        elif isinstance(o, dict):
            op_type_val = o.get("openingType")
        else:
            op_type_val = str(op_type)

        op_id = getattr(o, "openingId", None) if not isinstance(o, dict) else o.get("openingId")
        host_wall = getattr(o, "hostWallId", "") if not isinstance(o, dict) else o.get("hostWallId", "")
        pos = getattr(o, "positionM", [0, 0]) if not isinstance(o, dict) else o.get("positionM", [0, 0])
        entry = {"openingId": op_id, "hostWallId": host_wall, "positionM": pos}

        if op_type_val == OpeningType.DOOR.value or op_type_val == "DOOR":
            doors.append(entry)
        elif op_type_val == OpeningType.WINDOW.value or op_type_val == "WINDOW":
            windows.append(entry)

    doors_sorted = sorted(doors, key=lambda d: (d.get("hostWallId", ""), d.get("positionM", [0, 0])))
    windows_sorted = sorted(windows, key=lambda w: (w.get("hostWallId", ""), w.get("positionM", [0, 0])))

    tags: Dict[str, str] = {}
    for idx, d in enumerate(doors_sorted, 1):
        tags[d["openingId"]] = f"D{idx:02d}"
    for idx, w in enumerate(windows_sorted, 1):
        tags[w["openingId"]] = f"W{idx:02d}"

    return tags


def draw_pdf_polygon(c: canvas.Canvas, points: List[Tuple[float, float]], fill: int = 1, stroke: int = 1) -> None:
    """Helper to draw a filled and/or stroked polygon on ReportLab canvas."""
    if not points:
        return
    path = c.beginPath()
    path.moveTo(points[0][0], points[0][1])
    for pt in points[1:]:
        path.lineTo(pt[0], pt[1])
    path.close()
    c.drawPath(path, fill=fill, stroke=stroke)


# =============================================================================
# SVG Generator (Structured Semantic XML)
# =============================================================================

def generate_svg_sheet(
    spec: Dict[str, Any],
    view_data: Dict[str, Any],
    cbm: CanonicalBuildingModel,
    project_meta: Dict[str, Any]
) -> str:
    """
    Generates a publication-grade ISO 128 architectural SVG drawing sheet.
    Organizes geometry into semantic <g id="..."> groups with data-cbm-id attributes.
    """
    sheet = SHEET_SIZES["A3_LANDSCAPE"]
    w = sheet["widthPt"]
    h = sheet["heightPt"]

    # Calculate model bounds
    view_type = spec["viewType"]
    if view_type in ["PLAN", "ROOF_PLAN"]:
        env_w = cbm.buildingEnvelope.get("widthM", 10.0)
        env_l = cbm.buildingEnvelope.get("lengthM", 10.0)
        transformer = ViewportTransformer((0.0, env_w), (0.0, env_l), w, h, spec["scale"])
    elif view_type == "ELEVATION":
        b = view_data["bounds"]
        transformer = ViewportTransformer((b["uMin"], b["uMax"]), (b["zMin"], b["zMax"]), w, h, spec["scale"])
    else:  # SECTION
        b = view_data["bounds"]
        transformer = ViewportTransformer((b["xMin"], b["xMax"]), (b["zMin"], b["zMax"]), w, h, spec["scale"])

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'data-drawing-id="{spec["drawingId"]}" data-scale="{spec["scale"]}">',
        f'<!-- Planwise Enterprise Professional Architectural Drawing Sheet -->',
        f'<!-- Generated deterministically from Canonical Building Model: {cbm.metadata.modelHash} -->',
        '<defs>',
        '  <style>',
        '    text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; }',
        '    .title { font-weight: 700; fill: #0F172A; }',
        '    .header { font-weight: 600; fill: #1E293B; }',
        '    .label { font-size: 7px; fill: #64748B; font-weight: 500; }',
        '    .value { font-size: 8.5px; fill: #0F172A; font-weight: 600; }',
        '    .dim-text { font-size: 6.5px; fill: #0F172A; font-weight: 500; text-anchor: middle; }',
        '    .room-name { font-size: 8px; font-weight: 700; fill: #0F172A; text-anchor: middle; }',
        '    .room-area { font-size: 6.8px; font-weight: 500; fill: #475569; text-anchor: middle; }',
        '    .tag-text { font-size: 6px; font-weight: 700; fill: #2563EB; text-anchor: middle; }',
        '    .grid-text { font-size: 8px; font-weight: 700; fill: #1E293B; text-anchor: middle; dominant-baseline: central; }',
        '  </style>',
        '</defs>',
        f'<rect x="0" y="0" width="{w}" height="{h}" fill="{COLORS["SHEET_BG"]}"/>',
        '<g id="sheet-border">',
        f'  <rect x="56.69" y="28.35" width="1105.51" height="785.19" fill="none" '
        f'stroke="{COLORS["BORDER"]}" stroke-width="{LINE_WEIGHTS["BORDER_HEAVY"]}"/>',
        '</g>'
    ]

    # 1. Viewport Geometry
    svg_parts.append('<g id="drawing-viewport">')

    if view_type in ["PLAN", "ROOF_PLAN"]:
        # Slabs
        svg_parts.append('  <g id="slabs">')
        for slab in [e for e in cbm.elements if e.elementType == ElementType.SLAB]:
            p1 = transformer.to_svg(0.0, 0.0)
            p2 = transformer.to_svg(cbm.buildingEnvelope.get("widthM", 8.0), cbm.buildingEnvelope.get("lengthM", 8.0))
            sx = min(p1[0], p2[0])
            sy = min(p1[1], p2[1])
            sw = abs(p2[0] - p1[0])
            sh = abs(p2[1] - p1[1])
            svg_parts.append(
                f'    <rect data-cbm-id="{slab.elementId}" data-element-type="IfcSlab" '
                f'x="{sx:.2f}" y="{sy:.2f}" width="{sw:.2f}" height="{sh:.2f}" '
                f'fill="#F8FAFC" stroke="{COLORS["SLAB_EDGE"]}" stroke-width="{LINE_WEIGHTS["VISIBLE_MAJOR"]}"/>'
            )
            break
        svg_parts.append('  </g>')

        # Structural Grid Lines
        svg_parts.append('  <g id="structural-grid">')
        if cbm.structuralGrid:
            for gl in cbm.structuralGrid.gridLinesX:
                coord = gl.coordinate
                p_start = transformer.to_svg(coord, -0.6)
                p_end = transformer.to_svg(coord, cbm.buildingEnvelope.get("lengthM", 8.0) + 0.6)
                svg_parts.append(
                    f'    <line x1="{p_start[0]:.2f}" y1="{p_start[1]:.2f}" x2="{p_end[0]:.2f}" y2="{p_end[1]:.2f}" '
                    f'stroke="{COLORS["BORDER"]}" stroke-width="{LINE_WEIGHTS["GRID_LINE"]}" stroke-dasharray="8,3,2,3"/>'
                )
                bubble_pt = transformer.to_svg(coord, -0.9)
                svg_parts.append(
                    f'    <circle cx="{bubble_pt[0]:.2f}" cy="{bubble_pt[1]:.2f}" r="7" '
                    f'fill="{COLORS["GRID_BUBBLE_BG"]}" stroke="{COLORS["GRID_BUBBLE_STROKE"]}" stroke-width="0.8"/>'
                )
                svg_parts.append(f'    <text class="grid-text" x="{bubble_pt[0]:.2f}" y="{bubble_pt[1]:.2f}">{gl.tag}</text>')

            for gl in cbm.structuralGrid.gridLinesY:
                coord = gl.coordinate
                p_start = transformer.to_svg(-0.6, coord)
                p_end = transformer.to_svg(cbm.buildingEnvelope.get("widthM", 8.0) + 0.6, coord)
                svg_parts.append(
                    f'    <line x1="{p_start[0]:.2f}" y1="{p_start[1]:.2f}" x2="{p_end[0]:.2f}" y2="{p_end[1]:.2f}" '
                    f'stroke="{COLORS["BORDER"]}" stroke-width="{LINE_WEIGHTS["GRID_LINE"]}" stroke-dasharray="8,3,2,3"/>'
                )
                bubble_pt = transformer.to_svg(-0.9, coord)
                svg_parts.append(
                    f'    <circle cx="{bubble_pt[0]:.2f}" cy="{bubble_pt[1]:.2f}" r="7" '
                    f'fill="{COLORS["GRID_BUBBLE_BG"]}" stroke="{COLORS["GRID_BUBBLE_STROKE"]}" stroke-width="0.8"/>'
                )
                svg_parts.append(f'    <text class="grid-text" x="{bubble_pt[0]:.2f}" y="{bubble_pt[1]:.2f}">{gl.tag}</text>')
        svg_parts.append('  </g>')

        # Rooms
        svg_parts.append('  <g id="rooms">')
        for room in view_data.get("spaces", []):
            b = room["bounds"]
            p_tl = transformer.to_svg(b["x"], b["y"] + b["height"])
            p_br = transformer.to_svg(b["x"] + b["width"], b["y"])
            rx = min(p_tl[0], p_br[0])
            ry = min(p_tl[1], p_br[1])
            rw = abs(p_br[0] - p_tl[0])
            rh = abs(p_br[1] - p_tl[1])
            svg_parts.append(
                f'    <rect data-cbm-id="{room["spaceId"]}" data-element-type="IfcSpace" '
                f'x="{rx:.2f}" y="{ry:.2f}" width="{rw:.2f}" height="{rh:.2f}" '
                f'fill="{room.get("color", "#F1F5F9")}1A" stroke="#E2E8F0" stroke-width="0.5"/>'
            )
            cx = rx + rw / 2.0
            cy = ry + rh / 2.0
            svg_parts.append(f'    <text class="room-name" x="{cx:.2f}" y="{cy - 2:.2f}">{room["name"].upper()}</text>')
            svg_parts.append(f'    <text class="room-area" x="{cx:.2f}" y="{cy + 8:.2f}">{room["areaSqm"]:.2f} m²</text>')
        svg_parts.append('  </g>')

        # Walls
        svg_parts.append('  <g id="walls">')
        for wall in view_data.get("walls", []):
            c_line = wall.get("centerline", [])
            th = wall.get("thicknessM", 0.20)
            is_ext = wall.get("wallType") == "EXTERNAL"
            fill_c = COLORS["CUT_WALL_FILL"] if is_ext else COLORS["INTERNAL_WALL_FILL"]
            stroke_w = LINE_WEIGHTS["CUT_WALL"] if is_ext else LINE_WEIGHTS["VISIBLE_MAJOR"]

            if len(c_line) >= 2:
                x1, y1 = c_line[0][0], c_line[0][1]
                x2, y2 = c_line[1][0], c_line[1][1]
                dx = x2 - x1
                dy = y2 - y1
                length = math.hypot(dx, dy)
                if length > 0.001:
                    nx = -dy / length * (th / 2.0)
                    ny = dx / length * (th / 2.0)
                    poly_pts = [
                        transformer.to_svg(x1 + nx, y1 + ny),
                        transformer.to_svg(x2 + nx, y2 + ny),
                        transformer.to_svg(x2 - nx, y2 - ny),
                        transformer.to_svg(x1 - nx, y1 - ny)
                    ]
                    pts_str = " ".join(f"{p[0]:.2f},{p[1]:.2f}" for p in poly_pts)
                    svg_parts.append(
                        f'    <polygon data-cbm-id="{wall["elementId"]}" data-element-type="IfcWall" '
                        f'points="{pts_str}" fill="{fill_c}" stroke="{COLORS["CUT_WALL_STROKE"]}" stroke-width="{stroke_w}"/>'
                    )
        svg_parts.append('  </g>')

        # Columns
        svg_parts.append('  <g id="columns">')
        for col in view_data.get("columns", []):
            cx = col.get("x", 0.0)
            cy = col.get("y", 0.0)
            w_m = col.get("widthM", 0.3)
            d_m = col.get("depthM", 0.45)
            p1 = transformer.to_svg(cx - w_m / 2.0, cy + d_m / 2.0)
            p2 = transformer.to_svg(cx + w_m / 2.0, cy - d_m / 2.0)
            c_x = min(p1[0], p2[0])
            c_y = min(p1[1], p2[1])
            c_w = abs(p2[0] - p1[0])
            c_h = abs(p2[1] - p1[1])
            svg_parts.append(
                f'    <rect data-cbm-id="{col["elementId"]}" data-element-type="IfcColumn" '
                f'x="{c_x:.2f}" y="{c_y:.2f}" width="{c_w:.2f}" height="{c_h:.2f}" '
                f'fill="{COLORS["COLUMN_FILL"]}" stroke="{COLORS["BORDER"]}" stroke-width="{LINE_WEIGHTS["VISIBLE_MAJOR"]}"/>'
            )
        svg_parts.append('  </g>')

        # Stairs
        svg_parts.append('  <g id="stairs">')
        for st in view_data.get("stairs", []):
            fp = st.get("footprintPolygon", [])
            if len(fp) >= 4:
                xs = [p[0] for p in fp]
                ys = [p[1] for p in fp]
                p1 = transformer.to_svg(min(xs), max(ys))
                p2 = transformer.to_svg(max(xs), min(ys))
                st_x = min(p1[0], p2[0])
                st_y = min(p1[1], p2[1])
                st_w = abs(p2[0] - p1[0])
                st_h = abs(p2[1] - p1[1])

                svg_parts.append(
                    f'    <rect data-cbm-id="{st["elementId"]}" data-element-type="IfcStair" '
                    f'x="{st_x:.2f}" y="{st_y:.2f}" width="{st_w:.2f}" height="{st_h:.2f}" '
                    f'fill="#F8FAFC" stroke="{COLORS["STAIR_TREAD"]}" stroke-width="{LINE_WEIGHTS["VISIBLE_MINOR"]}"/>'
                )

                # Draw treads
                num_treads = min(st.get("numberOfRisers", 18) // 2, 9)
                tread_step = st_h / float(num_treads)
                for tidx in range(1, num_treads):
                    ty = st_y + tidx * tread_step
                    svg_parts.append(
                        f'    <line x1="{st_x:.2f}" y1="{ty:.2f}" x2="{st_x + st_w:.2f}" y2="{ty:.2f}" '
                        f'stroke="{COLORS["STAIR_TREAD"]}" stroke-width="{LINE_WEIGHTS["SECONDARY"]}"/>'
                    )

                # Stair walk line and UP arrow
                mid_x = st_x + st_w / 2.0
                svg_parts.append(
                    f'    <line x1="{mid_x:.2f}" y1="{st_y + st_h - 4:.2f}" x2="{mid_x:.2f}" y2="{st_y + 10:.2f}" '
                    f'stroke="{COLORS["STAIR_ARROW"]}" stroke-width="1.0" marker-end="url(#arrow)"/>'
                )
                svg_parts.append(
                    f'    <polygon points="{mid_x:.2f},{st_y + 4:.2f} {mid_x - 3:.2f},{st_y + 10:.2f} {mid_x + 3:.2f},{st_y + 10:.2f}" '
                    f'fill="{COLORS["STAIR_ARROW"]}"/>'
                )
                svg_parts.append(f'    <text class="tag-text" x="{mid_x + 8:.2f}" y="{st_y + 12:.2f}">UP</text>')
        svg_parts.append('  </g>')

        # Openings (Doors and Windows) & Tags
        svg_parts.append('  <g id="openings">')
        tags = assign_opening_tags(cbm.openings)
        for door in view_data.get("doors", []):
            op_id = door["openingId"]
            tag = tags.get(op_id, "D")
            pos = door.get("positionM", [0.0, 0.0])
            p = transformer.to_svg(pos[0], pos[1])
            svg_parts.append(
                f'    <circle data-cbm-id="{op_id}" data-element-type="IfcDoor" '
                f'cx="{p[0]:.2f}" cy="{p[1]:.2f}" r="6" fill="#EFF6FF" stroke="{COLORS["DOOR_SWING"]}" stroke-width="0.8"/>'
            )
            svg_parts.append(f'    <text class="tag-text" x="{p[0]:.2f}" y="{p[1] + 2:.2f}">{tag}</text>')

        for win in view_data.get("windows", []):
            op_id = win["openingId"]
            tag = tags.get(op_id, "W")
            pos = win.get("positionM", [0.0, 0.0])
            p = transformer.to_svg(pos[0], pos[1])
            svg_parts.append(
                f'    <circle data-cbm-id="{op_id}" data-element-type="IfcWindow" '
                f'cx="{p[0]:.2f}" cy="{p[1]:.2f}" r="6" fill="#F0F9FF" stroke="{COLORS["WINDOW_FRAME"]}" stroke-width="0.8"/>'
            )
            svg_parts.append(f'    <text class="tag-text" x="{p[0]:.2f}" y="{p[1] + 2:.2f}">{tag}</text>')
        svg_parts.append('  </g>')

        # Dimensions
        svg_parts.append('  <g id="dimensions">')
        env_w = cbm.buildingEnvelope.get("widthM", 8.0)
        env_l = cbm.buildingEnvelope.get("lengthM", 8.0)

        # Overall Width (Bottom dimension string)
        p_w1 = transformer.to_svg(0.0, -1.8)
        p_w2 = transformer.to_svg(env_w, -1.8)
        svg_parts.append(
            f'    <line x1="{p_w1[0]:.2f}" y1="{p_w1[1]:.2f}" x2="{p_w2[0]:.2f}" y2="{p_w2[1]:.2f}" '
            f'stroke="{COLORS["DIMENSION_LINE"]}" stroke-width="{LINE_WEIGHTS["DIMENSION"]}"/>'
        )
        svg_parts.append(f'    <line x1="{p_w1[0]:.2f}" y1="{p_w1[1] - 4:.2f}" x2="{p_w1[0]:.2f}" y2="{p_w1[1] + 4:.2f}" stroke="{COLORS["DIMENSION_LINE"]}" stroke-width="0.8"/>')
        svg_parts.append(f'    <line x1="{p_w2[0]:.2f}" y1="{p_w2[1] - 4:.2f}" x2="{p_w2[0]:.2f}" y2="{p_w2[1] + 4:.2f}" stroke="{COLORS["DIMENSION_LINE"]}" stroke-width="0.8"/>')
        svg_parts.append(f'    <text class="dim-text" x="{(p_w1[0] + p_w2[0]) / 2.0:.2f}" y="{p_w1[1] - 3:.2f}">{format_dim(env_w)}</text>')

        # Overall Depth (Left dimension string)
        p_d1 = transformer.to_svg(-1.8, 0.0)
        p_d2 = transformer.to_svg(-1.8, env_l)
        svg_parts.append(
            f'    <line x1="{p_d1[0]:.2f}" y1="{p_d1[1]:.2f}" x2="{p_d2[0]:.2f}" y2="{p_d2[1]:.2f}" '
            f'stroke="{COLORS["DIMENSION_LINE"]}" stroke-width="{LINE_WEIGHTS["DIMENSION"]}"/>'
        )
        svg_parts.append(f'    <line x1="{p_d1[0] - 4:.2f}" y1="{p_d1[1]:.2f}" x2="{p_d1[0] + 4:.2f}" y2="{p_d1[1]:.2f}" stroke="{COLORS["DIMENSION_LINE"]}" stroke-width="0.8"/>')
        svg_parts.append(f'    <line x1="{p_d2[0] - 4:.2f}" y1="{p_d2[1]:.2f}" x2="{p_d2[0] + 4:.2f}" y2="{p_d2[1]:.2f}" stroke="{COLORS["DIMENSION_LINE"]}" stroke-width="0.8"/>')
        mid_y = (p_d1[1] + p_d2[1]) / 2.0
        svg_parts.append(f'    <text class="dim-text" x="{p_d1[0] - 12:.2f}" y="{mid_y:.2f}" transform="rotate(-90 {p_d1[0] - 12:.2f} {mid_y:.2f})">{format_dim(env_l)}</text>')
        svg_parts.append('  </g>')

    elif view_type == "ELEVATION":
        # Elevation drawing
        svg_parts.append('  <g id="ground-line">')
        gl = view_data["groundLine"]
        p_g1 = transformer.to_svg(gl["u1"], gl["z"])
        p_g2 = transformer.to_svg(gl["u2"], gl["z"])
        svg_parts.append(
            f'    <line x1="{p_g1[0]:.2f}" y1="{p_g1[1]:.2f}" x2="{p_g2[0]:.2f}" y2="{p_g2[1]:.2f}" '
            f'stroke="{COLORS["BORDER"]}" stroke-width="{LINE_WEIGHTS["BORDER_HEAVY"]}"/>'
        )
        svg_parts.append('  </g>')

        svg_parts.append('  <g id="walls">')
        for wall in view_data.get("walls", []):
            u, z = wall["u"], wall["z"]
            uw, zh = wall["width"], wall["height"]
            p_tl = transformer.to_svg(u, z + zh)
            p_br = transformer.to_svg(u + uw, z)
            wx = min(p_tl[0], p_br[0])
            wy = min(p_tl[1], p_br[1])
            ww = abs(p_br[0] - p_tl[0])
            wh = abs(p_br[1] - p_tl[1])
            svg_parts.append(
                f'    <rect data-cbm-id="{wall["elementId"]}" data-element-type="IfcWall" '
                f'x="{wx:.2f}" y="{wy:.2f}" width="{ww:.2f}" height="{wh:.2f}" '
                f'fill="#F1F5F9" stroke="{COLORS["CUT_WALL_STROKE"]}" stroke-width="{LINE_WEIGHTS["VISIBLE_MAJOR"]}"/>'
            )
        svg_parts.append('  </g>')

        svg_parts.append('  <g id="slab-bands">')
        for band in view_data.get("slabBands", []):
            u, z = band["u"], band["z"]
            uw, th = band["width"], band["thickness"]
            p_tl = transformer.to_svg(u, z + th)
            p_br = transformer.to_svg(u + uw, z)
            bx = min(p_tl[0], p_br[0])
            by = min(p_tl[1], p_br[1])
            bw = abs(p_br[0] - p_tl[0])
            bh = abs(p_br[1] - p_tl[1])
            svg_parts.append(
                f'    <rect x="{bx:.2f}" y="{by:.2f}" width="{bw:.2f}" height="{bh:.2f}" '
                f'fill="#CBD5E1" stroke="{COLORS["BORDER"]}" stroke-width="{LINE_WEIGHTS["VISIBLE_MINOR"]}"/>'
            )
        svg_parts.append('  </g>')

        svg_parts.append('  <g id="openings">')
        for op in view_data.get("openings", []):
            u, z = op["u"], op["z"]
            ow, oh = op["width"], op["height"]
            p_tl = transformer.to_svg(u, z + oh)
            p_br = transformer.to_svg(u + ow, z)
            ox = min(p_tl[0], p_br[0])
            oy = min(p_tl[1], p_br[1])
            ow_pt = abs(p_br[0] - p_tl[0])
            oh_pt = abs(p_br[1] - p_tl[1])
            fill_c = COLORS["WINDOW_GLASS"] if op["openingType"] == OpeningType.WINDOW.value else "#E2E8F0"
            stroke_c = COLORS["WINDOW_FRAME"] if op["openingType"] == OpeningType.WINDOW.value else COLORS["DOOR_LEAF"]
            svg_parts.append(
                f'    <rect data-cbm-id="{op["openingId"]}" data-element-type="IfcOpening" '
                f'x="{ox:.2f}" y="{oy:.2f}" width="{ow_pt:.2f}" height="{oh_pt:.2f}" '
                f'fill="{fill_c}" stroke="{stroke_c}" stroke-width="{LINE_WEIGHTS["VISIBLE_MINOR"]}"/>'
            )
        svg_parts.append('  </g>')

        svg_parts.append('  <g id="level-markers">')
        for lm in view_data.get("levelMarkers", []):
            p1 = transformer.to_svg(lm["u1"], lm["elevationM"])
            p2 = transformer.to_svg(lm["u2"], lm["elevationM"])
            sign = "±" if abs(lm["elevationM"]) < 0.01 else ("+" if lm["elevationM"] > 0 else "")
            svg_parts.append(
                f'    <line x1="{p1[0]:.2f}" y1="{p1[1]:.2f}" x2="{p2[0]:.2f}" y2="{p2[1]:.2f}" '
                f'stroke="{COLORS["LEVEL_DATUM"]}" stroke-width="0.6" stroke-dasharray="4,2"/>'
            )
            svg_parts.append(
                f'    <text x="{p2[0] + 6:.2f}" y="{p2[1] + 3:.2f}" font-size="7px" font-weight="600" fill="{COLORS["LEVEL_DATUM"]}">'
                f'{lm["name"]} ({sign}{lm["elevationM"]:.3f})</text>'
            )
        svg_parts.append('  </g>')

    else:  # SECTION
        svg_parts.append('  <g id="ground-line">')
        gl = view_data["groundLine"]
        p_g1 = transformer.to_svg(gl["x1"], gl["z"])
        p_g2 = transformer.to_svg(gl["x2"], gl["z"])
        svg_parts.append(
            f'    <line x1="{p_g1[0]:.2f}" y1="{p_g1[1]:.2f}" x2="{p_g2[0]:.2f}" y2="{p_g2[1]:.2f}" '
            f'stroke="{COLORS["BORDER"]}" stroke-width="{LINE_WEIGHTS["BORDER_HEAVY"]}"/>'
        )
        svg_parts.append('  </g>')

        svg_parts.append('  <g id="slabs">')
        for slab in view_data.get("slabs", []):
            x1, x2 = slab["x1"], slab["x2"]
            z, th = slab["z"], slab["thickness"]
            p_tl = transformer.to_svg(x1, z + th)
            p_br = transformer.to_svg(x2, z)
            sx = min(p_tl[0], p_br[0])
            sy = min(p_tl[1], p_br[1])
            sw = abs(p_br[0] - p_tl[0])
            sh = abs(p_br[1] - p_tl[1])
            svg_parts.append(
                f'    <rect data-cbm-id="{slab["elementId"]}" data-element-type="IfcSlab" '
                f'x="{sx:.2f}" y="{sy:.2f}" width="{sw:.2f}" height="{sh:.2f}" '
                f'fill="{COLORS["CUT_WALL_FILL"]}" stroke="{COLORS["BORDER"]}" stroke-width="{LINE_WEIGHTS["CUT_WALL"]}"/>'
            )
        svg_parts.append('  </g>')

        svg_parts.append('  <g id="cut-walls">')
        for wall in view_data.get("cutWalls", []):
            x, z = wall["x"], wall["z"]
            th, ht = wall["thickness"], wall["height"]
            p_tl = transformer.to_svg(x, z + ht)
            p_br = transformer.to_svg(x + th, z)
            wx = min(p_tl[0], p_br[0])
            wy = min(p_tl[1], p_br[1])
            ww = abs(p_br[0] - p_tl[0])
            wh = abs(p_br[1] - p_tl[1])
            svg_parts.append(
                f'    <rect data-cbm-id="{wall["elementId"]}" data-element-type="IfcWall" '
                f'x="{wx:.2f}" y="{wy:.2f}" width="{ww:.2f}" height="{wh:.2f}" '
                f'fill="{COLORS["INTERNAL_WALL_FILL"]}" stroke="{COLORS["BORDER"]}" stroke-width="{LINE_WEIGHTS["CUT_WALL"]}"/>'
            )
        svg_parts.append('  </g>')

        svg_parts.append('  <g id="cut-spaces">')
        for sp in view_data.get("cutSpaces", []):
            x1, x2 = sp["x1"], sp["x2"]
            p1 = transformer.to_svg(x1, 1.2)
            p2 = transformer.to_svg(x2, 1.2)
            cx = (p1[0] + p2[0]) / 2.0
            svg_parts.append(f'    <text class="room-name" x="{cx:.2f}" y="{p1[1]:.2f}">{sp["name"].upper()}</text>')
            svg_parts.append(f'    <text class="room-area" x="{cx:.2f}" y="{p1[1] + 9:.2f}">CLR HT: {sp["clearHeightM"]:.2f} m</text>')
        svg_parts.append('  </g>')

        svg_parts.append('  <g id="level-markers">')
        for lm in view_data.get("levels", []):
            p1 = transformer.to_svg(lm["x1"], lm["elevationM"])
            p2 = transformer.to_svg(lm["x2"], lm["elevationM"])
            sign = "±" if abs(lm["elevationM"]) < 0.01 else ("+" if lm["elevationM"] > 0 else "")
            svg_parts.append(
                f'    <line x1="{p1[0]:.2f}" y1="{p1[1]:.2f}" x2="{p2[0]:.2f}" y2="{p2[1]:.2f}" '
                f'stroke="{COLORS["LEVEL_DATUM"]}" stroke-width="0.6" stroke-dasharray="4,2"/>'
            )
            svg_parts.append(
                f'    <text x="{p2[0] + 6:.2f}" y="{p2[1] + 3:.2f}" font-size="7px" font-weight="600" fill="{COLORS["LEVEL_DATUM"]}">'
                f'{lm["name"]} ({sign}{lm["elevationM"]:.3f})</text>'
            )
        svg_parts.append('  </g>')

    svg_parts.append('</g>')  # end drawing-viewport

    # 2. North Arrow (for Plans)
    if view_type in ["PLAN", "ROOF_PLAN"]:
        svg_parts.append('<g id="north-arrow">')
        na_x = 1110.0
        na_y = 110.0
        svg_parts.append(f'  <circle cx="{na_x}" cy="{na_y}" r="22" fill="#FFFFFF" stroke="{COLORS["BORDER"]}" stroke-width="1.2"/>')
        svg_parts.append(f'  <polygon points="{na_x},{na_y - 18} {na_x - 6},{na_y + 12} {na_x},{na_y + 6}" fill="{COLORS["NORTH_ARROW_DARK"]}"/>')
        svg_parts.append(f'  <polygon points="{na_x},{na_y - 18} {na_x + 6},{na_y + 12} {na_x},{na_y + 6}" fill="{COLORS["NORTH_ARROW_LIGHT"]}" stroke="{COLORS["BORDER"]}" stroke-width="0.6"/>')
        svg_parts.append(f'  <text x="{na_x}" y="{na_y - 21}" font-size="9px" font-weight="800" fill="{COLORS["BORDER"]}" text-anchor="middle">N</text>')
        svg_parts.append(f'  <text x="{na_x}" y="{na_y + 30}" font-size="5.5px" font-weight="600" fill="#64748B" text-anchor="middle">TRUE NORTH</text>')
        svg_parts.append('</g>')

    # 3. Schedules (Door & Window for Plans)
    if view_type in ["PLAN", "ROOF_PLAN"]:
        svg_parts.append('<g id="schedules">')
        sch_x = 802.2
        sch_y = 210.0
        sch_w = 360.0

        # Door Schedule
        tags = assign_opening_tags(cbm.openings)
        doors = [o for o in cbm.openings if o.openingType == OpeningType.DOOR]
        doors_sorted = sorted(doors, key=lambda d: tags.get(d.openingId, ""))[:5]

        svg_parts.append(f'  <rect x="{sch_x}" y="{sch_y}" width="{sch_w}" height="16" fill="#F1F5F9" stroke="{COLORS["BORDER"]}" stroke-width="0.8"/>')
        svg_parts.append(f'  <text x="{sch_x + 8}" y="{sch_y + 11}" font-size="8px" font-weight="700" fill="{COLORS["BORDER"]}">DOOR SCHEDULE</text>')
        cur_y = sch_y + 16
        svg_parts.append(f'  <rect x="{sch_x}" y="{cur_y}" width="{sch_w}" height="14" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="0.5"/>')
        svg_parts.append(f'  <text class="label" x="{sch_x + 6}" y="{cur_y + 10}">TAG</text>')
        svg_parts.append(f'  <text class="label" x="{sch_x + 40}" y="{cur_y + 10}">TYPE</text>')
        svg_parts.append(f'  <text class="label" x="{sch_x + 150}" y="{cur_y + 10}">CLEAR WIDTH</text>')
        svg_parts.append(f'  <text class="label" x="{sch_x + 240}" y="{cur_y + 10}">HEIGHT</text>')
        svg_parts.append(f'  <text class="label" x="{sch_x + 300}" y="{cur_y + 10}">LEVEL</text>')
        cur_y += 14

        for d in doors_sorted:
            tag = tags.get(d.openingId, "D")
            svg_parts.append(f'  <rect x="{sch_x}" y="{cur_y}" width="{sch_w}" height="14" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="0.5"/>')
            svg_parts.append(f'  <text class="value" x="{sch_x + 6}" y="{cur_y + 10}">{tag}</text>')
            svg_parts.append(f'  <text class="value" x="{sch_x + 40}" y="{cur_y + 10}">FLUSH TIMBER DOOR</text>')
            svg_parts.append(f'  <text class="value" x="{sch_x + 150}" y="{cur_y + 10}">{format_dim_mm(d.widthM)} mm</text>')
            svg_parts.append(f'  <text class="value" x="{sch_x + 240}" y="{cur_y + 10}">{format_dim_mm(d.heightM)} mm</text>')
            svg_parts.append(f'  <text class="value" x="{sch_x + 300}" y="{cur_y + 10}">{d.levelId}</text>')
            cur_y += 14

        # Window Schedule
        cur_y += 8
        windows = [o for o in cbm.openings if o.openingType == OpeningType.WINDOW]
        windows_sorted = sorted(windows, key=lambda w: tags.get(w.openingId, ""))[:5]

        svg_parts.append(f'  <rect x="{sch_x}" y="{cur_y}" width="{sch_w}" height="16" fill="#F1F5F9" stroke="{COLORS["BORDER"]}" stroke-width="0.8"/>')
        svg_parts.append(f'  <text x="{sch_x + 8}" y="{cur_y + 11}" font-size="8px" font-weight="700" fill="{COLORS["BORDER"]}">WINDOW SCHEDULE</text>')
        cur_y += 16
        svg_parts.append(f'  <rect x="{sch_x}" y="{cur_y}" width="{sch_w}" height="14" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="0.5"/>')
        svg_parts.append(f'  <text class="label" x="{sch_x + 6}" y="{cur_y + 10}">TAG</text>')
        svg_parts.append(f'  <text class="label" x="{sch_x + 40}" y="{cur_y + 10}">TYPE</text>')
        svg_parts.append(f'  <text class="label" x="{sch_x + 150}" y="{cur_y + 10}">WIDTH</text>')
        svg_parts.append(f'  <text class="label" x="{sch_x + 240}" y="{cur_y + 10}">HEIGHT</text>')
        svg_parts.append(f'  <text class="label" x="{sch_x + 300}" y="{cur_y + 10}">LEVEL</text>')
        cur_y += 14

        for w_elem in windows_sorted:
            tag = tags.get(w_elem.openingId, "W")
            svg_parts.append(f'  <rect x="{sch_x}" y="{cur_y}" width="{sch_w}" height="14" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="0.5"/>')
            svg_parts.append(f'  <text class="value" x="{sch_x + 6}" y="{cur_y + 10}">{tag}</text>')
            svg_parts.append(f'  <text class="value" x="{sch_x + 40}" y="{cur_y + 10}">ALUMINUM SLIDING</text>')
            svg_parts.append(f'  <text class="value" x="{sch_x + 150}" y="{cur_y + 10}">{format_dim_mm(w_elem.widthM)} mm</text>')
            svg_parts.append(f'  <text class="value" x="{sch_x + 240}" y="{cur_y + 10}">{format_dim_mm(w_elem.heightM)} mm</text>')
            svg_parts.append(f'  <text class="value" x="{sch_x + 300}" y="{cur_y + 10}">{w_elem.levelId}</text>')
            cur_y += 14

        svg_parts.append('</g>')

    # 4. Mandatory Disclaimers Block (Bottom Left)
    svg_parts.append('<g id="disclaimers">')
    disc_x = 70.0
    disc_y = 745.0
    svg_parts.append(f'  <text x="{disc_x}" y="{disc_y}" font-size="6.5px" font-weight="700" fill="#475569">PROFESSIONAL DRAWING STATUS NOTICE:</text>')
    svg_parts.append(f'  <text x="{disc_x}" y="{disc_y + 10}" font-size="5.5px" fill="{COLORS["DISCLAIMER_TEXT"]}">{DISCLAIMER_PRELIMINARY[:105]}</text>')
    svg_parts.append(f'  <text x="{disc_x}" y="{disc_y + 18}" font-size="5.5px" fill="{COLORS["DISCLAIMER_TEXT"]}">{DISCLAIMER_PRELIMINARY[105:]}</text>')
    svg_parts.append(f'  <text x="{disc_x}" y="{disc_y + 28}" font-size="5.5px" fill="{COLORS["DISCLAIMER_TEXT"]}">{DISCLAIMER_STRUCTURAL[:105]}</text>')
    svg_parts.append(f'  <text x="{disc_x}" y="{disc_y + 36}" font-size="5.5px" fill="{COLORS["DISCLAIMER_TEXT"]}">{DISCLAIMER_STRUCTURAL[105:]}</text>')
    svg_parts.append(f'  <text x="{disc_x}" y="{disc_y + 48}" font-size="6px" font-weight="700" fill="#DC2626">NOT FOR CONSTRUCTION — SUBJECT TO STATUTORY SANCTION &amp; PE REVIEW</text>')
    svg_parts.append('</g>')

    # 5. Title Block (ISO 7200 / Bottom Right)
    tb_x = 802.20
    tb_y = 668.54
    tb_w = 360.00
    tb_h = 145.00

    svg_parts.append('<g id="title-block">')
    svg_parts.append(
        f'  <rect x="{tb_x}" y="{tb_y}" width="{tb_w}" height="{tb_h}" '
        f'fill="{COLORS["TITLE_BLOCK_BG"]}" stroke="{COLORS["BORDER"]}" stroke-width="{LINE_WEIGHTS["BORDER_HEAVY"]}"/>'
    )

    # Title block header: Planwise Enterprise
    svg_parts.append(f'  <line x1="{tb_x}" y1="{tb_y + 28}" x2="{tb_x + tb_w}" y2="{tb_y + 28}" stroke="{COLORS["BORDER"]}" stroke-width="0.8"/>')
    svg_parts.append(f'  <text x="{tb_x + 12}" y="{tb_y + 18}" font-size="12px" font-weight="800" fill="#0F172A">PLANWISE ENTERPRISE</text>')
    svg_parts.append(f'  <text x="{tb_x + tb_w - 12}" y="{tb_y + 18}" font-size="7.5px" font-weight="700" fill="#2563EB" text-anchor="end">AUTONOMOUS ARCHITECTURAL BIM</text>')

    # Project Information
    svg_parts.append(f'  <line x1="{tb_x}" y1="{tb_y + 60}" x2="{tb_x + tb_w}" y2="{tb_y + 60}" stroke="{COLORS["BORDER"]}" stroke-width="0.5"/>')
    svg_parts.append(f'  <text class="label" x="{tb_x + 12}" y="{tb_y + 38}">PROJECT</text>')
    svg_parts.append(f'  <text class="value" x="{tb_x + 12}" y="{tb_y + 51}">{project_meta.get("projectName", "Bandra West Residential Development")}</text>')
    svg_parts.append(f'  <text class="label" x="{tb_x + 240}" y="{tb_y + 38}">PROJECT ID</text>')
    svg_parts.append(f'  <text class="value" x="{tb_x + 240}" y="{tb_y + 51}">{project_meta.get("projectId", "proj-mumbai-real-1100")}</text>')

    # Drawing Title
    svg_parts.append(f'  <line x1="{tb_x}" y1="{tb_y + 96}" x2="{tb_x + tb_w}" y2="{tb_y + 96}" stroke="{COLORS["BORDER"]}" stroke-width="0.5"/>')
    svg_parts.append(f'  <text class="label" x="{tb_x + 12}" y="{tb_y + 72}">DRAWING TITLE</text>')
    svg_parts.append(f'  <text x="{tb_x + 12}" y="{tb_y + 88}" font-size="11px" font-weight="800" fill="#0F172A">{spec["drawingTitle"]}</text>')

    # Grid details: Drawing No, Rev, Scale, Date, Status
    svg_parts.append(f'  <line x1="{tb_x + 100}" y1="{tb_y + 96}" x2="{tb_x + 100}" y2="{tb_y + tb_h}" stroke="{COLORS["BORDER"]}" stroke-width="0.5"/>')
    svg_parts.append(f'  <line x1="{tb_x + 180}" y1="{tb_y + 96}" x2="{tb_x + 180}" y2="{tb_y + tb_h}" stroke="{COLORS["BORDER"]}" stroke-width="0.5"/>')
    svg_parts.append(f'  <line x1="{tb_x + 260}" y1="{tb_y + 96}" x2="{tb_x + 260}" y2="{tb_y + tb_h}" stroke="{COLORS["BORDER"]}" stroke-width="0.5"/>')

    svg_parts.append(f'  <text class="label" x="{tb_x + 12}" y="{tb_y + 108}">DRAWING NO.</text>')
    svg_parts.append(f'  <text class="value" x="{tb_x + 12}" y="{tb_y + 122}" font-size="11px">{spec["drawingId"]}</text>')

    svg_parts.append(f'  <text class="label" x="{tb_x + 108}" y="{tb_y + 108}">REV</text>')
    svg_parts.append(f'  <text class="value" x="{tb_x + 108}" y="{tb_y + 122}">R0</text>')

    svg_parts.append(f'  <text class="label" x="{tb_x + 188}" y="{tb_y + 108}">SCALE</text>')
    svg_parts.append(f'  <text class="value" x="{tb_x + 188}" y="{tb_y + 122}">{spec["scale"]}</text>')

    svg_parts.append(f'  <text class="label" x="{tb_x + 268}" y="{tb_y + 108}">SHEET</text>')
    svg_parts.append(f'  <text class="value" x="{tb_x + 268}" y="{tb_y + 122}">{spec["sheetNumber"]}</text>')

    svg_parts.append(f'  <line x1="{tb_x}" y1="{tb_y + 128}" x2="{tb_x + tb_w}" y2="{tb_y + 128}" stroke="{COLORS["BORDER"]}" stroke-width="0.5"/>')
    svg_parts.append(f'  <text class="label" x="{tb_x + 12}" y="{tb_y + 138}">STATUS:</text>')
    svg_parts.append(f'  <text x="{tb_x + 55}" y="{tb_y + 138}" font-size="7px" font-weight="700" fill="#DC2626">PRELIMINARY / FOR PROFESSIONAL REVIEW</text>')
    svg_parts.append(f'  <text class="label" x="{tb_x + 268}" y="{tb_y + 138}">DATE: 2026-10-02</text>')

    svg_parts.append('</g>')

    svg_parts.append('</svg>')
    return '\n'.join(svg_parts)


# =============================================================================
# PDF Generator (ReportLab Standalone Vector A3 Sheet)
# =============================================================================

def generate_pdf_sheet(
    spec: Dict[str, Any],
    view_data: Dict[str, Any],
    cbm: CanonicalBuildingModel,
    project_meta: Dict[str, Any],
    deterministic_seed: str
) -> bytes:
    """
    Generates a standalone, publication-grade vector PDF sheet (A3 landscape).
    Ensures 100% byte-for-byte determinism across repeated compilation.
    """
    sheet = SHEET_SIZES["A3_LANDSCAPE"]
    w = sheet["widthPt"]
    h = sheet["heightPt"]

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=landscape(A3))

    # Strict Byte-for-Byte Determinism:
    # Fix PDF Document ID from MD5 digest of seed, eliminating random/time-based variations.
    md5_digest = hashlib.md5(deterministic_seed.encode("utf-8")).digest()
    c._doc.ID = lambda: (md5_digest, md5_digest)
    c.setTitle(f"Planwise - {spec['drawingId']} {spec['drawingTitle']}")
    c.setAuthor("Planwise Enterprise Platform")
    c.setSubject(f"Architectural Drawing {spec['drawingId']}")

    # Setup Viewport Transformer
    view_type = spec["viewType"]
    if view_type in ["PLAN", "ROOF_PLAN"]:
        env_w = cbm.buildingEnvelope.get("widthM", 10.0)
        env_l = cbm.buildingEnvelope.get("lengthM", 10.0)
        transformer = ViewportTransformer((0.0, env_w), (0.0, env_l), w, h, spec["scale"])
    elif view_type == "ELEVATION":
        b = view_data["bounds"]
        transformer = ViewportTransformer((b["uMin"], b["uMax"]), (b["zMin"], b["zMax"]), w, h, spec["scale"])
    else:  # SECTION
        b = view_data["bounds"]
        transformer = ViewportTransformer((b["xMin"], b["xMax"]), (b["zMin"], b["zMax"]), w, h, spec["scale"])

    # 1. Sheet Outer Border
    c.saveState()
    c.setStrokeColor(HexColor(COLORS["BORDER"]))
    c.setLineWidth(LINE_WEIGHTS["BORDER_HEAVY"])
    c.rect(56.69, 28.35, 1105.51, 785.19, fill=0, stroke=1)
    c.restoreState()

    # 2. Viewport Geometry
    c.saveState()
    if view_type in ["PLAN", "ROOF_PLAN"]:
        # Slab background
        c.setStrokeColor(HexColor(COLORS["SLAB_EDGE"]))
        c.setFillColor(HexColor("#F8FAFC"))
        c.setLineWidth(LINE_WEIGHTS["VISIBLE_MAJOR"])
        p1 = transformer.to_pdf(0.0, 0.0)
        p2 = transformer.to_pdf(cbm.buildingEnvelope.get("widthM", 8.0), cbm.buildingEnvelope.get("lengthM", 8.0))
        sx = min(p1[0], p2[0])
        sy = min(p1[1], p2[1])
        sw = abs(p2[0] - p1[0])
        sh = abs(p2[1] - p1[1])
        c.rect(sx, sy, sw, sh, fill=1, stroke=1)

        # Structural Grid Lines
        if cbm.structuralGrid:
            c.setStrokeColor(HexColor(COLORS["BORDER"]))
            c.setLineWidth(LINE_WEIGHTS["GRID_LINE"])
            c.setDash([8, 3, 2, 3])
            for gl in cbm.structuralGrid.gridLinesX:
                p_start = transformer.to_pdf(gl.coordinate, -0.6)
                p_end = transformer.to_pdf(gl.coordinate, cbm.buildingEnvelope.get("lengthM", 8.0) + 0.6)
                c.line(p_start[0], p_start[1], p_end[0], p_end[1])
                bp = transformer.to_pdf(gl.coordinate, -0.9)
                c.circle(bp[0], bp[1], 7, fill=0, stroke=1)
                c.setFont("Helvetica-Bold", 8)
                c.drawCentredString(bp[0], bp[1] - 3, gl.tag)

            for gl in cbm.structuralGrid.gridLinesY:
                p_start = transformer.to_pdf(-0.6, gl.coordinate)
                p_end = transformer.to_pdf(cbm.buildingEnvelope.get("widthM", 8.0) + 0.6, gl.coordinate)
                c.line(p_start[0], p_start[1], p_end[0], p_end[1])
                bp = transformer.to_pdf(-0.9, gl.coordinate)
                c.circle(bp[0], bp[1], 7, fill=0, stroke=1)
                c.setFont("Helvetica-Bold", 8)
                c.drawCentredString(bp[0], bp[1] - 3, gl.tag)
            c.setDash([])

        # Rooms
        for room in view_data.get("spaces", []):
            b = room["bounds"]
            p_bl = transformer.to_pdf(b["x"], b["y"])
            p_tr = transformer.to_pdf(b["x"] + b["width"], b["y"] + b["height"])
            rx = min(p_bl[0], p_tr[0])
            ry = min(p_bl[1], p_tr[1])
            rw = abs(p_tr[0] - p_bl[0])
            rh = abs(p_tr[1] - p_bl[1])
            c.setStrokeColor(HexColor("#E2E8F0"))
            c.setFillColor(HexColor("#F8FAFC"))
            c.setLineWidth(0.5)
            c.rect(rx, ry, rw, rh, fill=1, stroke=1)

            # Room labels
            cx = rx + rw / 2.0
            cy = ry + rh / 2.0
            c.setFont("Helvetica-Bold", 8)
            c.setFillColor(HexColor(COLORS["ROOM_NAME"]))
            c.drawCentredString(cx, cy + 2, room["name"].upper())
            c.setFont("Helvetica", 6.8)
            c.setFillColor(HexColor(COLORS["ROOM_AREA"]))
            c.drawCentredString(cx, cy - 8, f"{room['areaSqm']:.2f} m²")

        # Walls
        for wall in view_data.get("walls", []):
            c_line = wall.get("centerline", [])
            th = wall.get("thicknessM", 0.20)
            is_ext = wall.get("wallType") == "EXTERNAL"
            fill_c = COLORS["CUT_WALL_FILL"] if is_ext else COLORS["INTERNAL_WALL_FILL"]
            stroke_w = LINE_WEIGHTS["CUT_WALL"] if is_ext else LINE_WEIGHTS["VISIBLE_MAJOR"]

            if len(c_line) >= 2:
                x1, y1 = c_line[0][0], c_line[0][1]
                x2, y2 = c_line[1][0], c_line[1][1]
                dx = x2 - x1
                dy = y2 - y1
                length = math.hypot(dx, dy)
                if length > 0.001:
                    nx = -dy / length * (th / 2.0)
                    ny = dx / length * (th / 2.0)
                    poly_pts = [
                        transformer.to_pdf(x1 + nx, y1 + ny),
                        transformer.to_pdf(x2 + nx, y2 + ny),
                        transformer.to_pdf(x2 - nx, y2 - ny),
                        transformer.to_pdf(x1 - nx, y1 - ny)
                    ]
                    path = c.beginPath()
                    path.moveTo(poly_pts[0][0], poly_pts[0][1])
                    for pt in poly_pts[1:]:
                        path.lineTo(pt[0], pt[1])
                    path.close()
                    c.setFillColor(HexColor(fill_c))
                    c.setStrokeColor(HexColor(COLORS["CUT_WALL_STROKE"]))
                    c.setLineWidth(stroke_w)
                    c.drawPath(path, fill=1, stroke=1)

        # Columns
        for col in view_data.get("columns", []):
            cx = col.get("x", 0.0)
            cy = col.get("y", 0.0)
            w_m = col.get("widthM", 0.3)
            d_m = col.get("depthM", 0.45)
            p1 = transformer.to_pdf(cx - w_m / 2.0, cy - d_m / 2.0)
            p2 = transformer.to_pdf(cx + w_m / 2.0, cy + d_m / 2.0)
            c_x = min(p1[0], p2[0])
            c_y = min(p1[1], p2[1])
            c_w = abs(p2[0] - p1[0])
            c_h = abs(p2[1] - p1[1])
            c.setFillColor(HexColor(COLORS["COLUMN_FILL"]))
            c.setStrokeColor(HexColor(COLORS["BORDER"]))
            c.setLineWidth(LINE_WEIGHTS["VISIBLE_MAJOR"])
            c.rect(c_x, c_y, c_w, c_h, fill=1, stroke=1)

        # Stairs
        for st in view_data.get("stairs", []):
            fp = st.get("footprintPolygon", [])
            if len(fp) >= 4:
                xs = [p[0] for p in fp]
                ys = [p[1] for p in fp]
                p1 = transformer.to_pdf(min(xs), min(ys))
                p2 = transformer.to_pdf(max(xs), max(ys))
                st_x = min(p1[0], p2[0])
                st_y = min(p1[1], p2[1])
                st_w = abs(p2[0] - p1[0])
                st_h = abs(p2[1] - p1[1])
                c.setFillColor(HexColor("#F8FAFC"))
                c.setStrokeColor(HexColor(COLORS["STAIR_TREAD"]))
                c.setLineWidth(LINE_WEIGHTS["VISIBLE_MINOR"])
                c.rect(st_x, st_y, st_w, st_h, fill=1, stroke=1)

                num_treads = min(st.get("numberOfRisers", 18) // 2, 9)
                tread_step = st_h / float(num_treads)
                for tidx in range(1, num_treads):
                    ty = st_y + tidx * tread_step
                    c.line(st_x, ty, st_x + st_w, ty)

                mid_x = st_x + st_w / 2.0
                c.setStrokeColor(HexColor(COLORS["STAIR_ARROW"]))
                c.setFillColor(HexColor(COLORS["STAIR_ARROW"]))
                c.line(mid_x, st_y + 4, mid_x, st_y + st_h - 10)
                # Arrow head
                draw_pdf_polygon(c, [(mid_x, st_y + st_h - 4), (mid_x - 3, st_y + st_h - 10), (mid_x + 3, st_y + st_h - 10)], fill=1, stroke=0)
                c.setFont("Helvetica-Bold", 6)
                c.drawString(mid_x + 5, st_y + st_h - 10, "UP")

        # Openings & Tags
        tags = assign_opening_tags(cbm.openings)
        for door in view_data.get("doors", []):
            tag = tags.get(door["openingId"], "D")
            pos = door.get("positionM", [0.0, 0.0])
            p = transformer.to_pdf(pos[0], pos[1])
            c.setFillColor(HexColor("#EFF6FF"))
            c.setStrokeColor(HexColor(COLORS["DOOR_SWING"]))
            c.setLineWidth(0.8)
            c.circle(p[0], p[1], 6, fill=1, stroke=1)
            c.setFont("Helvetica-Bold", 6)
            c.setFillColor(HexColor(COLORS["DOOR_SWING"]))
            c.drawCentredString(p[0], p[1] - 2, tag)

        for win in view_data.get("windows", []):
            tag = tags.get(win["openingId"], "W")
            pos = win.get("positionM", [0.0, 0.0])
            p = transformer.to_pdf(pos[0], pos[1])
            c.setFillColor(HexColor("#F0F9FF"))
            c.setStrokeColor(HexColor(COLORS["WINDOW_FRAME"]))
            c.setLineWidth(0.8)
            c.circle(p[0], p[1], 6, fill=1, stroke=1)
            c.setFont("Helvetica-Bold", 6)
            c.setFillColor(HexColor(COLORS["WINDOW_FRAME"]))
            c.drawCentredString(p[0], p[1] - 2, tag)

        # Dimensions
        env_w = cbm.buildingEnvelope.get("widthM", 8.0)
        env_l = cbm.buildingEnvelope.get("lengthM", 8.0)
        c.setStrokeColor(HexColor(COLORS["DIMENSION_LINE"]))
        c.setLineWidth(LINE_WEIGHTS["DIMENSION"])

        # Width dimension
        p_w1 = transformer.to_pdf(0.0, -1.8)
        p_w2 = transformer.to_pdf(env_w, -1.8)
        c.line(p_w1[0], p_w1[1], p_w2[0], p_w2[1])
        c.line(p_w1[0], p_w1[1] - 4, p_w1[0], p_w1[1] + 4)
        c.line(p_w2[0], p_w2[1] - 4, p_w2[0], p_w2[1] + 4)
        c.setFont("Helvetica", 6.5)
        c.setFillColor(HexColor(COLORS["DIMENSION_TEXT"]))
        c.drawCentredString((p_w1[0] + p_w2[0]) / 2.0, p_w1[1] + 3, format_dim(env_w))

        # Depth dimension
        p_d1 = transformer.to_pdf(-1.8, 0.0)
        p_d2 = transformer.to_pdf(-1.8, env_l)
        c.line(p_d1[0], p_d1[1], p_d2[0], p_d2[1])
        c.line(p_d1[0] - 4, p_d1[1], p_d1[0] + 4, p_d1[1])
        c.line(p_d2[0] - 4, p_d2[1], p_d2[0] + 4, p_d2[1])
        c.drawCentredString(p_d1[0] - 12, (p_d1[1] + p_d2[1]) / 2.0, format_dim(env_l))

    elif view_type == "ELEVATION":
        # Ground line
        gl = view_data["groundLine"]
        p_g1 = transformer.to_pdf(gl["u1"], gl["z"])
        p_g2 = transformer.to_pdf(gl["u2"], gl["z"])
        c.setStrokeColor(HexColor(COLORS["BORDER"]))
        c.setLineWidth(LINE_WEIGHTS["BORDER_HEAVY"])
        c.line(p_g1[0], p_g1[1], p_g2[0], p_g2[1])

        # Wall masses
        for wall in view_data.get("walls", []):
            u, z = wall["u"], wall["z"]
            uw, zh = wall["width"], wall["height"]
            p_bl = transformer.to_pdf(u, z)
            p_tr = transformer.to_pdf(u + uw, z + zh)
            wx = min(p_bl[0], p_tr[0])
            wy = min(p_bl[1], p_tr[1])
            ww = abs(p_tr[0] - p_bl[0])
            wh = abs(p_tr[1] - p_bl[1])
            c.setFillColor(HexColor("#F1F5F9"))
            c.setStrokeColor(HexColor(COLORS["CUT_WALL_STROKE"]))
            c.setLineWidth(LINE_WEIGHTS["VISIBLE_MAJOR"])
            c.rect(wx, wy, ww, wh, fill=1, stroke=1)

        # Slab bands
        for band in view_data.get("slabBands", []):
            u, z = band["u"], band["z"]
            uw, th = band["width"], band["thickness"]
            p_bl = transformer.to_pdf(u, z)
            p_tr = transformer.to_pdf(u + uw, z + th)
            bx = min(p_bl[0], p_tr[0])
            by = min(p_bl[1], p_tr[1])
            bw = abs(p_tr[0] - p_bl[0])
            bh = abs(p_tr[1] - p_bl[1])
            c.setFillColor(HexColor("#CBD5E1"))
            c.setStrokeColor(HexColor(COLORS["BORDER"]))
            c.setLineWidth(LINE_WEIGHTS["VISIBLE_MINOR"])
            c.rect(bx, by, bw, bh, fill=1, stroke=1)

        # Openings
        for op in view_data.get("openings", []):
            u, z = op["u"], op["z"]
            ow, oh = op["width"], op["height"]
            p_bl = transformer.to_pdf(u, z)
            p_tr = transformer.to_pdf(u + ow, z + oh)
            ox = min(p_bl[0], p_tr[0])
            oy = min(p_bl[1], p_tr[1])
            ow_pt = abs(p_tr[0] - p_bl[0])
            oh_pt = abs(p_tr[1] - p_bl[1])
            fill_c = COLORS["WINDOW_GLASS"] if op["openingType"] == OpeningType.WINDOW.value else "#E2E8F0"
            stroke_c = COLORS["WINDOW_FRAME"] if op["openingType"] == OpeningType.WINDOW.value else COLORS["DOOR_LEAF"]
            c.setFillColor(HexColor(fill_c))
            c.setStrokeColor(HexColor(stroke_c))
            c.setLineWidth(LINE_WEIGHTS["VISIBLE_MINOR"])
            c.rect(ox, oy, ow_pt, oh_pt, fill=1, stroke=1)

        # Level markers
        for lm in view_data.get("levelMarkers", []):
            p1 = transformer.to_pdf(lm["u1"], lm["elevationM"])
            p2 = transformer.to_pdf(lm["u2"], lm["elevationM"])
            c.setStrokeColor(HexColor(COLORS["LEVEL_DATUM"]))
            c.setLineWidth(0.6)
            c.setDash([4, 2])
            c.line(p1[0], p1[1], p2[0], p2[1])
            c.setDash([])
            sign = "±" if abs(lm["elevationM"]) < 0.01 else ("+" if lm["elevationM"] > 0 else "")
            c.setFont("Helvetica-Bold", 7)
            c.setFillColor(HexColor(COLORS["LEVEL_DATUM"]))
            c.drawString(p2[0] + 6, p2[1] - 2, f"{lm['name']} ({sign}{lm['elevationM']:.3f})")

    else:  # SECTION
        gl = view_data["groundLine"]
        p_g1 = transformer.to_pdf(gl["x1"], gl["z"])
        p_g2 = transformer.to_pdf(gl["x2"], gl["z"])
        c.setStrokeColor(HexColor(COLORS["BORDER"]))
        c.setLineWidth(LINE_WEIGHTS["BORDER_HEAVY"])
        c.line(p_g1[0], p_g1[1], p_g2[0], p_g2[1])

        # Slabs
        for slab in view_data.get("slabs", []):
            x1, x2 = slab["x1"], slab["x2"]
            z, th = slab["z"], slab["thickness"]
            p_bl = transformer.to_pdf(x1, z)
            p_tr = transformer.to_pdf(x2, z + th)
            sx = min(p_bl[0], p_tr[0])
            sy = min(p_bl[1], p_tr[1])
            sw = abs(p_tr[0] - p_bl[0])
            sh = abs(p_tr[1] - p_bl[1])
            c.setFillColor(HexColor(COLORS["CUT_WALL_FILL"]))
            c.setStrokeColor(HexColor(COLORS["BORDER"]))
            c.setLineWidth(LINE_WEIGHTS["CUT_WALL"])
            c.rect(sx, sy, sw, sh, fill=1, stroke=1)

        # Cut Walls
        for wall in view_data.get("cutWalls", []):
            x, z = wall["x"], wall["z"]
            th, ht = wall["thickness"], wall["height"]
            p_bl = transformer.to_pdf(x, z)
            p_tr = transformer.to_pdf(x + th, z + ht)
            wx = min(p_bl[0], p_tr[0])
            wy = min(p_bl[1], p_tr[1])
            ww = abs(p_tr[0] - p_bl[0])
            wh = abs(p_tr[1] - p_bl[1])
            c.setFillColor(HexColor(COLORS["INTERNAL_WALL_FILL"]))
            c.setStrokeColor(HexColor(COLORS["BORDER"]))
            c.setLineWidth(LINE_WEIGHTS["CUT_WALL"])
            c.rect(wx, wy, ww, wh, fill=1, stroke=1)

        # Cut Spaces
        for sp in view_data.get("cutSpaces", []):
            x1, x2 = sp["x1"], sp["x2"]
            p1 = transformer.to_pdf(x1, 1.2)
            p2 = transformer.to_pdf(x2, 1.2)
            cx = (p1[0] + p2[0]) / 2.0
            c.setFont("Helvetica-Bold", 8)
            c.setFillColor(HexColor(COLORS["ROOM_NAME"]))
            c.drawCentredString(cx, p1[1] + 2, sp["name"].upper())
            c.setFont("Helvetica", 6.8)
            c.setFillColor(HexColor(COLORS["ROOM_AREA"]))
            c.drawCentredString(cx, p1[1] - 8, f"CLR HT: {sp['clearHeightM']:.2f} m")

        # Level markers
        for lm in view_data.get("levels", []):
            p1 = transformer.to_pdf(lm["x1"], lm["elevationM"])
            p2 = transformer.to_pdf(lm["x2"], lm["elevationM"])
            c.setStrokeColor(HexColor(COLORS["LEVEL_DATUM"]))
            c.setLineWidth(0.6)
            c.setDash([4, 2])
            c.line(p1[0], p1[1], p2[0], p2[1])
            c.setDash([])
            sign = "±" if abs(lm["elevationM"]) < 0.01 else ("+" if lm["elevationM"] > 0 else "")
            c.setFont("Helvetica-Bold", 7)
            c.setFillColor(HexColor(COLORS["LEVEL_DATUM"]))
            c.drawString(p2[0] + 6, p2[1] - 2, f"{lm['name']} ({sign}{lm['elevationM']:.3f})")

    c.restoreState()

    # 3. North Arrow (for Plans)
    if view_type in ["PLAN", "ROOF_PLAN"]:
        c.saveState()
        na_x = 1110.0
        na_y = 730.0
        c.setFillColor(HexColor("#FFFFFF"))
        c.setStrokeColor(HexColor(COLORS["BORDER"]))
        c.setLineWidth(1.2)
        c.circle(na_x, na_y, 22, fill=1, stroke=1)
        c.setFillColor(HexColor(COLORS["NORTH_ARROW_DARK"]))
        draw_pdf_polygon(c, [(na_x, na_y + 18), (na_x - 6, na_y - 12), (na_x, na_y - 6)], fill=1, stroke=0)
        c.setFillColor(HexColor(COLORS["NORTH_ARROW_LIGHT"]))
        draw_pdf_polygon(c, [(na_x, na_y + 18), (na_x + 6, na_y - 12), (na_x, na_y - 6)], fill=1, stroke=1)
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(HexColor(COLORS["BORDER"]))
        c.drawCentredString(na_x, na_y + 21, "N")
        c.setFont("Helvetica-Bold", 5.5)
        c.setFillColor(HexColor("#64748B"))
        c.drawCentredString(na_x, na_y - 30, "TRUE NORTH")
        c.restoreState()

    # 4. Schedules (Door & Window for Plans)
    if view_type in ["PLAN", "ROOF_PLAN"]:
        c.saveState()
        sch_x = 802.2
        sch_y = 600.0
        sch_w = 360.0

        tags = assign_opening_tags(cbm.openings)
        doors = [o for o in cbm.openings if o.openingType == OpeningType.DOOR]
        doors_sorted = sorted(doors, key=lambda d: tags.get(d.openingId, ""))[:5]

        # Door Schedule Table
        c.setFillColor(HexColor("#F1F5F9"))
        c.setStrokeColor(HexColor(COLORS["BORDER"]))
        c.setLineWidth(0.8)
        c.rect(sch_x, sch_y, sch_w, 16, fill=1, stroke=1)
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(HexColor(COLORS["BORDER"]))
        c.drawString(sch_x + 8, sch_y + 4, "DOOR SCHEDULE")

        cur_y = sch_y - 14
        c.setFillColor(HexColor("#F8FAFC"))
        c.setStrokeColor(HexColor("#CBD5E1"))
        c.setLineWidth(0.5)
        c.rect(sch_x, cur_y, sch_w, 14, fill=1, stroke=1)
        c.setFont("Helvetica-Bold", 7)
        c.setFillColor(HexColor("#64748B"))
        c.drawString(sch_x + 6, cur_y + 4, "TAG")
        c.drawString(sch_x + 40, cur_y + 4, "TYPE")
        c.drawString(sch_x + 150, cur_y + 4, "CLEAR WIDTH")
        c.drawString(sch_x + 240, cur_y + 4, "HEIGHT")
        c.drawString(sch_x + 300, cur_y + 4, "LEVEL")

        for d in doors_sorted:
            cur_y -= 14
            tag = tags.get(d.openingId, "D")
            c.setFillColor(HexColor("#FFFFFF"))
            c.setStrokeColor(HexColor("#E2E8F0"))
            c.rect(sch_x, cur_y, sch_w, 14, fill=1, stroke=1)
            c.setFont("Helvetica-Bold", 7.5)
            c.setFillColor(HexColor("#0F172A"))
            c.drawString(sch_x + 6, cur_y + 4, tag)
            c.setFont("Helvetica", 7)
            c.drawString(sch_x + 40, cur_y + 4, "FLUSH TIMBER DOOR")
            c.drawString(sch_x + 150, cur_y + 4, f"{format_dim_mm(d.widthM)} mm")
            c.drawString(sch_x + 240, cur_y + 4, f"{format_dim_mm(d.heightM)} mm")
            c.drawString(sch_x + 300, cur_y + 4, d.levelId)

        # Window Schedule Table
        windows = [o for o in cbm.openings if o.openingType == OpeningType.WINDOW]
        windows_sorted = sorted(windows, key=lambda w: tags.get(w.openingId, ""))[:5]
        cur_y -= 22
        c.setFillColor(HexColor("#F1F5F9"))
        c.setStrokeColor(HexColor(COLORS["BORDER"]))
        c.setLineWidth(0.8)
        c.rect(sch_x, cur_y, sch_w, 16, fill=1, stroke=1)
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(HexColor(COLORS["BORDER"]))
        c.drawString(sch_x + 8, cur_y + 4, "WINDOW SCHEDULE")

        cur_y -= 14
        c.setFillColor(HexColor("#F8FAFC"))
        c.setStrokeColor(HexColor("#CBD5E1"))
        c.setLineWidth(0.5)
        c.rect(sch_x, cur_y, sch_w, 14, fill=1, stroke=1)
        c.setFont("Helvetica-Bold", 7)
        c.setFillColor(HexColor("#64748B"))
        c.drawString(sch_x + 6, cur_y + 4, "TAG")
        c.drawString(sch_x + 40, cur_y + 4, "TYPE")
        c.drawString(sch_x + 150, cur_y + 4, "WIDTH")
        c.drawString(sch_x + 240, cur_y + 4, "HEIGHT")
        c.drawString(sch_x + 300, cur_y + 4, "LEVEL")

        for w_elem in windows_sorted:
            cur_y -= 14
            tag = tags.get(w_elem.openingId, "W")
            c.setFillColor(HexColor("#FFFFFF"))
            c.setStrokeColor(HexColor("#E2E8F0"))
            c.rect(sch_x, cur_y, sch_w, 14, fill=1, stroke=1)
            c.setFont("Helvetica-Bold", 7.5)
            c.setFillColor(HexColor("#0F172A"))
            c.drawString(sch_x + 6, cur_y + 4, tag)
            c.setFont("Helvetica", 7)
            c.drawString(sch_x + 40, cur_y + 4, "ALUMINUM SLIDING")
            c.drawString(sch_x + 150, cur_y + 4, f"{format_dim_mm(w_elem.widthM)} mm")
            c.drawString(sch_x + 240, cur_y + 4, f"{format_dim_mm(w_elem.heightM)} mm")
            c.drawString(sch_x + 300, cur_y + 4, w_elem.levelId)

        c.restoreState()

    # 5. Mandatory Disclaimers (Bottom Left)
    c.saveState()
    disc_x = 70.0
    disc_y = 90.0
    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(HexColor("#475569"))
    c.drawString(disc_x, disc_y, "PROFESSIONAL DRAWING STATUS NOTICE:")
    c.setFont("Helvetica", 5.5)
    c.setFillColor(HexColor(COLORS["DISCLAIMER_TEXT"]))
    c.drawString(disc_x, disc_y - 9, DISCLAIMER_PRELIMINARY[:105])
    c.drawString(disc_x, disc_y - 17, DISCLAIMER_PRELIMINARY[105:])
    c.drawString(disc_x, disc_y - 27, DISCLAIMER_STRUCTURAL[:105])
    c.drawString(disc_x, disc_y - 35, DISCLAIMER_STRUCTURAL[105:])
    c.setFont("Helvetica-Bold", 6)
    c.setFillColor(HexColor("#DC2626"))
    c.drawString(disc_x, disc_y - 47, "NOT FOR CONSTRUCTION — SUBJECT TO STATUTORY SANCTION & PE REVIEW")
    c.restoreState()

    # 6. Title Block (ISO 7200 / Bottom Right)
    tb_x = 802.20
    tb_y = 28.35
    tb_w = 360.00
    tb_h = 145.00

    c.saveState()
    c.setFillColor(HexColor(COLORS["TITLE_BLOCK_BG"]))
    c.setStrokeColor(HexColor(COLORS["BORDER"]))
    c.setLineWidth(LINE_WEIGHTS["BORDER_HEAVY"])
    c.rect(tb_x, tb_y, tb_w, tb_h, fill=1, stroke=1)

    # Header
    c.line(tb_x, tb_y + tb_h - 28, tb_x + tb_w, tb_y + tb_h - 28)
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(HexColor("#0F172A"))
    c.drawString(tb_x + 12, tb_y + tb_h - 20, "PLANWISE ENTERPRISE")
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(HexColor("#2563EB"))
    c.drawRightString(tb_x + tb_w - 12, tb_y + tb_h - 20, "AUTONOMOUS ARCHITECTURAL BIM")

    # Project Information
    c.setLineWidth(0.5)
    c.line(tb_x, tb_y + tb_h - 60, tb_x + tb_w, tb_y + tb_h - 60)
    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(HexColor("#64748B"))
    c.drawString(tb_x + 12, tb_y + tb_h - 38, "PROJECT")
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(HexColor("#0F172A"))
    c.drawString(tb_x + 12, tb_y + tb_h - 50, project_meta.get("projectName", "Bandra West Residential Development"))
    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(HexColor("#64748B"))
    c.drawString(tb_x + 240, tb_y + tb_h - 38, "PROJECT ID")
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(HexColor("#0F172A"))
    c.drawString(tb_x + 240, tb_y + tb_h - 50, project_meta.get("projectId", "proj-mumbai-real-1100"))

    # Drawing Title
    c.line(tb_x, tb_y + tb_h - 96, tb_x + tb_w, tb_y + tb_h - 96)
    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(HexColor("#64748B"))
    c.drawString(tb_x + 12, tb_y + tb_h - 72, "DRAWING TITLE")
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(HexColor("#0F172A"))
    c.drawString(tb_x + 12, tb_y + tb_h - 88, spec["drawingTitle"])

    # Partitions
    c.line(tb_x + 100, tb_y + 16, tb_x + 100, tb_y + tb_h - 96)
    c.line(tb_x + 180, tb_y + 16, tb_x + 180, tb_y + tb_h - 96)
    c.line(tb_x + 260, tb_y + 16, tb_x + 260, tb_y + tb_h - 96)

    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(HexColor("#64748B"))
    c.drawString(tb_x + 12, tb_y + tb_h - 108, "DRAWING NO.")
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(HexColor("#0F172A"))
    c.drawString(tb_x + 12, tb_y + tb_h - 124, spec["drawingId"])

    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(HexColor("#64748B"))
    c.drawString(tb_x + 108, tb_y + tb_h - 108, "REV")
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(HexColor("#0F172A"))
    c.drawString(tb_x + 108, tb_y + tb_h - 122, "R0")

    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(HexColor("#64748B"))
    c.drawString(tb_x + 188, tb_y + tb_h - 108, "SCALE")
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(HexColor("#0F172A"))
    c.drawString(tb_x + 188, tb_y + tb_h - 122, spec["scale"])

    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(HexColor("#64748B"))
    c.drawString(tb_x + 268, tb_y + tb_h - 108, "SHEET")
    c.setFont("Helvetica-Bold", 8.5)
    c.setFillColor(HexColor("#0F172A"))
    c.drawString(tb_x + 268, tb_y + tb_h - 122, spec["sheetNumber"])

    # Bottom status bar
    c.line(tb_x, tb_y + 16, tb_x + tb_w, tb_y + 16)
    c.setFont("Helvetica-Bold", 6)
    c.setFillColor(HexColor("#64748B"))
    c.drawString(tb_x + 12, tb_y + 5, "STATUS:")
    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColor(HexColor("#DC2626"))
    c.drawString(tb_x + 45, tb_y + 5, "PRELIMINARY / FOR PROFESSIONAL REVIEW")
    c.setFont("Helvetica-Bold", 6)
    c.setFillColor(HexColor("#64748B"))
    c.drawRightString(tb_x + tb_w - 12, tb_y + 5, "DATE: 2026-10-02")

    c.restoreState()

    c.save()
    return buf.getvalue()


# =============================================================================
# Drawing Compiler Orchestrator
# =============================================================================

class DrawingCompiler:
    """
    Deterministic Architectural Drawing Compiler for Planwise Enterprise.
    Compiles complete 9-view publication-grade drawing set from Canonical Building Model.
    """
    def __init__(self, cbm: CanonicalBuildingModel, project_meta: Optional[Dict[str, Any]] = None):
        self.cbm = cbm
        self.project_meta = project_meta or {
            "projectName": "Bandra West Residential Development",
            "projectId": "proj-mumbai-real-1100",
            "releaseId": "rel-pilot-20261002-aedf9830",
            "designVersionId": "DV-OPT-B-9be0a983"
        }
        self.compiler_version = "1.0.0"

    def compile_view(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts deterministic projection data for the given drawing specification."""
        view_type = spec["viewType"]

        if view_type in ["PLAN", "ROOF_PLAN"]:
            lvl_id = spec["levelId"]
            level_obj = next((lvl for lvl in self.cbm.levels if lvl.levelId == lvl_id), None)
            if not level_obj:
                raise DrawingSourceDataMissingError(f"Level '{lvl_id}' not found in Canonical Building Model.")
            return generate_floor_plan(self.cbm, level_id=lvl_id)

        elif view_type == "ELEVATION":
            direction = spec.get("direction", "SOUTH")
            return generate_elevation(self.cbm, facade_direction=direction)

        elif view_type == "SECTION":
            cut_axis = spec.get("cutAxis", "Y")
            cut_plane = spec.get("cutPlane", "A-A")
            return generate_section(self.cbm, cut_plane=cut_plane, cut_axis=cut_axis)

        else:
            raise DrawingGenerationFailedError(spec["drawingId"], f"Unsupported view type: {view_type}")

    def compile_sheet_svg(self, spec: Dict[str, Any]) -> str:
        """Compiles a standalone, publication-grade SVG drawing sheet."""
        view_data = self.compile_view(spec)
        return generate_svg_sheet(spec, view_data, self.cbm, self.project_meta)

    def compile_sheet_pdf(self, spec: Dict[str, Any]) -> bytes:
        """Compiles a standalone, publication-grade vector PDF sheet with byte-for-byte determinism."""
        view_data = self.compile_view(spec)
        seed = f"{spec['drawingId']}:{self.cbm.metadata.modelHash}:{spec['sheetNumber']}"
        return generate_pdf_sheet(spec, view_data, self.cbm, self.project_meta, deterministic_seed=seed)

    def compile_drawing_set(self, output_dir: str) -> Dict[str, Any]:
        """
        Compiles the complete 9-drawing publication set and writes SVGs, PDFs, and drawing_manifest.json.
        Guarantees byte-for-byte determinism and immutability.
        """
        target_path = Path(output_dir)
        target_path.mkdir(parents=True, exist_ok=True)

        # Prohibit writing directly to pilot handoff directory
        if "artifacts/pilot_handoff" in str(target_path.resolve()):
            raise DrawingCompilerError(
                code="PILOT_RELEASE_MUTATION_FORBIDDEN",
                message="Cannot write test drawings into immutable artifacts/pilot_handoff/."
            )

        manifest_drawings: List[Dict[str, Any]] = []

        for spec in DRAWING_SPECS:
            drawing_id = spec["drawingId"]
            svg_content = self.compile_sheet_svg(spec)
            pdf_bytes = self.compile_sheet_pdf(spec)

            svg_filename = f"{drawing_id}_{spec['drawingTitle'].lower().replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_')}.svg"
            pdf_filename = f"{drawing_id}_{spec['drawingTitle'].lower().replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_')}.pdf"

            svg_file_path = target_path / svg_filename
            pdf_file_path = target_path / pdf_filename

            # Write files
            with open(svg_file_path, "w", encoding="utf-8") as f:
                f.write(svg_content)

            with open(pdf_file_path, "wb") as f:
                f.write(pdf_bytes)

            svg_hash = hashlib.sha256(svg_content.encode("utf-8")).hexdigest()
            pdf_hash = hashlib.sha256(pdf_bytes).hexdigest()

            # Collect source elements associated with this drawing
            source_elements = [e.elementId for e in self.cbm.elements]
            if spec.get("levelId"):
                source_elements = [e.elementId for e in self.cbm.elements if getattr(e, "levelId", None) == spec["levelId"]]

            manifest_drawings.append({
                "drawingId": drawing_id,
                "drawingTitle": spec["drawingTitle"],
                "viewType": spec["viewType"],
                "sheetNumber": spec["sheetNumber"],
                "scale": spec["scale"],
                "sheetSize": "A3_LANDSCAPE",
                "svgArtifact": svg_filename,
                "pdfArtifact": pdf_filename,
                "svgHash": f"sha256:{svg_hash}",
                "pdfHash": f"sha256:{pdf_hash}",
                "sourceElementIds": source_elements[:15]
            })

        # Generate drawing manifest
        manifest_data = {
            "projectId": self.project_meta.get("projectId", "proj-mumbai-real-1100"),
            "releaseId": self.project_meta.get("releaseId", "rel-pilot-20261002-aedf9830"),
            "designVersionId": self.project_meta.get("designVersionId", "DV-OPT-B-9be0a983"),
            "cbmHash": self.cbm.metadata.modelHash,
            "compilerVersion": self.compiler_version,
            "generationTimestamp": "2026-10-02T12:00:00Z",  # Deterministic compilation timestamp matching pilot
            "totalSheets": len(manifest_drawings),
            "drawings": manifest_drawings
        }

        manifest_canonical = json.dumps(manifest_data, indent=2, sort_keys=True)
        manifest_hash = hashlib.sha256(manifest_canonical.encode("utf-8")).hexdigest()
        manifest_data["manifestHash"] = f"sha256:{manifest_hash}"

        manifest_file_path = target_path / "drawing_manifest.json"
        with open(manifest_file_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2)

        return manifest_data
