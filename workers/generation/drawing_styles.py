"""
Planwise Enterprise — ISO 128 Architectural Drawing Style Standards
Milestone 2 — Professional Drawing Pipeline

Centralizes all graphic standards, line weights, line types, text sizes,
color palettes, dimension styles, and scale conversion factors.
Never scatter styling constants throughout renderers.
"""

from typing import Dict, Any, List

# -----------------------------------------------------------------------------
# Paper Sheet Dimensions (points: 1 pt = 1/72 inch; 25.4 mm = 72 pt)
# -----------------------------------------------------------------------------
SHEET_SIZES = {
    "A3_LANDSCAPE": {
        "widthPt": 1190.55,    # 420 mm
        "heightPt": 841.89,    # 297 mm
        "widthMm": 420.0,
        "heightMm": 297.0,
        "marginLeftMm": 20.0,  # 20mm filing/binding margin
        "marginRightMm": 10.0,
        "marginTopMm": 10.0,
        "marginBottomMm": 10.0
    },
    "A2_LANDSCAPE": {
        "widthPt": 1683.78,    # 594 mm
        "heightPt": 1190.55,   # 420 mm
        "widthMm": 594.0,
        "heightMm": 420.0,
        "marginLeftMm": 25.0,
        "marginRightMm": 15.0,
        "marginTopMm": 15.0,
        "marginBottomMm": 15.0
    }
}

# -----------------------------------------------------------------------------
# Architectural Line Weights (ISO 128 / Bureau of Indian Standards SP 46)
# -----------------------------------------------------------------------------
# Line weight hierarchy: CUT / PRIMARY > VISIBLE > OPENING > SECONDARY > DIMENSION / GRID
LINE_WEIGHTS = {
    "CUT_WALL": 1.42,          # 0.50 mm (Heavy bold cut line)
    "VISIBLE_MAJOR": 0.99,     # 0.35 mm (Columns, boundary, slab edges)
    "VISIBLE_MINOR": 0.71,     # 0.25 mm (Doors, windows, stairs, fittings)
    "SECONDARY": 0.50,         # 0.18 mm (Tile patterns, fixtures, swings)
    "DIMENSION": 0.35,         # 0.13 mm (Dimension lines & leaders)
    "EXTENSION": 0.28,         # 0.10 mm (Dimension witness lines)
    "GRID_LINE": 0.42,         # 0.15 mm (Centerlines and structural grids)
    "BORDER_HEAVY": 1.70,      # 0.60 mm (Sheet border outer line)
    "BORDER_LIGHT": 0.71       # 0.25 mm (Inner title block partitions)
}

# -----------------------------------------------------------------------------
# Architectural Color Palette (Neutral Architectural Monochrome + Accents)
# -----------------------------------------------------------------------------
COLORS = {
    "SHEET_BG": "#FFFFFF",
    "VIEWPORT_BG": "#FAFAFA",
    "BORDER": "#0F172A",
    "CUT_WALL_FILL": "#1E293B",        # Deep Charcoal solid cut fill
    "CUT_WALL_STROKE": "#0F172A",
    "INTERNAL_WALL_FILL": "#334155",
    "SLAB_EDGE": "#0F172A",
    "COLUMN_FILL": "#0F172A",          # Solid black structural column
    "DOOR_SWING": "#2563EB",           # Planwise Blue for door arcs
    "DOOR_LEAF": "#1E293B",
    "WINDOW_FRAME": "#0284C7",         # Sky Blue for glazing
    "WINDOW_GLASS": "#E0F2FE",
    "STAIR_TREAD": "#475569",
    "STAIR_ARROW": "#2563EB",
    "DIMENSION_LINE": "#1E293B",
    "DIMENSION_TEXT": "#0F172A",
    "GRID_BUBBLE_BG": "#FFFFFF",
    "GRID_BUBBLE_STROKE": "#2563EB",
    "GRID_TEXT": "#1E293B",
    "ROOM_TAG_BG": "rgba(255, 255, 255, 0.85)",
    "ROOM_NAME": "#0F172A",
    "ROOM_AREA": "#475569",
    "NORTH_ARROW_DARK": "#0F172A",
    "NORTH_ARROW_LIGHT": "#E2E8F0",
    "LEVEL_DATUM": "#DC2626",          # Red level markers
    "TITLE_BLOCK_BG": "#FFFFFF",
    "TITLE_BLOCK_HEADER": "#0F172A",
    "TITLE_BLOCK_TEXT": "#334155",
    "TITLE_BLOCK_MUTED": "#64748B",
    "DISCLAIMER_TEXT": "#94A3B8"
}

# -----------------------------------------------------------------------------
# Text Sizes (Points)
# -----------------------------------------------------------------------------
FONT_SIZES = {
    "TITLE_SHEET": 14.0,
    "TITLE_VIEW": 11.0,
    "SECTION_HEADER": 9.0,
    "ROOM_NAME": 8.0,
    "ROOM_AREA": 6.8,
    "DIMENSION": 6.5,
    "TAG_DOOR_WINDOW": 6.0,
    "GRID_LABEL": 8.0,
    "LEVEL_LABEL": 7.5,
    "TITLE_BLOCK_LABEL": 6.5,
    "TITLE_BLOCK_VALUE": 8.5,
    "DISCLAIMER": 5.5
}

# -----------------------------------------------------------------------------
# Scale Factors (1:Scale -> Points per meter on paper)
# -----------------------------------------------------------------------------
# At 1:100 scale: 1 meter in reality = 10 mm on paper = 10 / 25.4 * 72 pt = 28.3465 pt
SCALE_POINTS_PER_METER = {
    "1:50": 56.6929,
    "1:100": 28.3465,
    "1:200": 14.1732,
    "1:500": 5.6693
}

DISCLAIMER_PRELIMINARY = (
    "Computational drawing generated from the Planwise Canonical Building Model. "
    "This document is preliminary and requires review, coordination, and certification "
    "by the appropriate licensed professional before statutory submission or construction."
)

DISCLAIMER_STRUCTURAL = (
    "Structural representation shown is preliminary and derived from the Planwise canonical model. "
    "Final structural design and certification remain subject to licensed structural engineer review."
)
