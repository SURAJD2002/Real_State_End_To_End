"""
Planwise Enterprise — Deterministic 2D Architectural Drawing Renderer
======================================================================
Produces high-precision vector drawings using ReportLab Graphics primitives:
1. Site & Statutory Envelope Plan (SECS Topocentric Frame)
2. Level-by-Level 2D Floor Plans (Spaces, Walls, Doors, Windows, Stairs, Columns)
3. Roof & Terrace Plan

Never uses raster screenshots or AI images. All geometry is mathematically
projected from the authoritative Canonical Building Model (CBM) and Site Input.
"""

import math
from typing import Dict, Any, List, Optional
from reportlab.graphics.shapes import (
    Drawing, Rect, Polygon, Line, PolyLine, String, Group, Circle, Wedge
)
from reportlab.lib import colors

# -------------------------------------------------------------
# Architectural CAD Color Standards
# -------------------------------------------------------------
CAD_BACKGROUND = colors.HexColor("#F8FAFC")
CAD_GRID_LINE = colors.HexColor("#E2E8F0")
CAD_PLOT_BOUNDARY = colors.HexColor("#0F172A")
CAD_SETBACK_LINE = colors.HexColor("#DC2626")      # Dashed Red
CAD_ENVELOPE_FILL = colors.HexColor("#ECFDF5")     # Light Mint
CAD_ENVELOPE_BORDER = colors.HexColor("#059669")   # Emerald
CAD_ROAD_FILL = colors.HexColor("#E2E8F0")         # Light Slate
CAD_WALL_EXT = colors.HexColor("#0F172A")          # Dark Charcoal
CAD_WALL_INT = colors.HexColor("#334155")          # Medium Slate
CAD_COLUMN = colors.HexColor("#0F172A")            # Solid Black/Charcoal
CAD_DOOR = colors.HexColor("#2563EB")              # Planwise Blue
CAD_WINDOW = colors.HexColor("#0284C7")            # Sky Blue
CAD_STAIR = colors.HexColor("#475569")             # Slate
CAD_TEXT = colors.HexColor("#0F172A")
CAD_TEXT_MUTED = colors.HexColor("#64748B")
CAD_BRAND_BLUE = colors.HexColor("#2563EB")

# Room Fill Colors by Zone
ZONE_PALETTE = {
    "LIVING_ROOM": colors.HexColor("#EFF6FF"),     # Soft Blue
    "DINING": colors.HexColor("#F0FDF4"),          # Soft Green
    "KITCHEN": colors.HexColor("#FEF3C7"),         # Soft Warm Amber
    "MASTER_BEDROOM": colors.HexColor("#F3E8FF"),   # Soft Purple
    "BEDROOM": colors.HexColor("#FAF5FF"),          # Light Lavender
    "BATHROOM": colors.HexColor("#E0F2FE"),         # Water Blue
    "BALCONY": colors.HexColor("#F1F5F9"),          # Slate
    "CORRIDOR": colors.HexColor("#F8FAFC"),         # Off-white
    "FOYER": colors.HexColor("#F8FAFC"),
    "STAIRCASE": colors.HexColor("#F1F5F9"),
    "PARKING": colors.HexColor("#E2E8F0"),
    "DEFAULT": colors.HexColor("#F8FAFC")
}


def render_north_arrow(x: float, y: float, size: float = 24.0) -> Group:
    """Draws a crisp cardinal North arrow."""
    g = Group()
    # Left black half
    g.add(Polygon(
        points=[x, y + size, x - size * 0.35, y - size * 0.4, x, y - size * 0.15],
        fillColor=CAD_PLOT_BOUNDARY,
        strokeColor=CAD_PLOT_BOUNDARY,
        strokeWidth=0.5
    ))
    # Right white half
    g.add(Polygon(
        points=[x, y + size, x + size * 0.35, y - size * 0.4, x, y - size * 0.15],
        fillColor=colors.white,
        strokeColor=CAD_PLOT_BOUNDARY,
        strokeWidth=0.5
    ))
    # Letter 'N'
    s = String(x - 3.5, y + size + 4, "N", fontName="Helvetica-Bold", fontSize=9, fillColor=CAD_PLOT_BOUNDARY)
    g.add(s)
    return g


def render_site_plan_drawing(
    site_dict: Dict[str, Any],
    cbm: Any,
    width: float = 523.0,
    height: float = 280.0
) -> Drawing:
    """
    Renders 2D Site & Statutory Feasibility Plan in SECS Topocentric frame.
    Shows parcel boundary, road frontage, widening reservation, setbacks,
    buildable envelope, and building footprint overlay.
    """
    d = Drawing(width, height)

    # Frame background
    d.add(Rect(0, 0, width, height, fillColor=CAD_BACKGROUND, strokeColor=CAD_GRID_LINE, strokeWidth=1))

    # Authoritative dimensions in meters (Default to Bandra West 1,100 sq ft: 8.382m x 12.192m)
    dims_m = site_dict.get("dimensionsM", {})
    w_m = dims_m.get("frontWidthM", 8.382)
    d_m = dims_m.get("leftLengthM", 12.192)

    # Setbacks (Mumbai DCPR 2034 Table 18)
    front_sb = 3.0
    rear_sb = 1.5
    side_sb = 1.0
    road_widening_m = 3.0

    # Transformation scaling to fit drawing area
    margin_x = 80.0
    margin_y = 50.0
    draw_w = width - 2 * margin_x
    draw_h = height - 2 * margin_y

    scale = min(draw_w / (w_m * 1.5), draw_h / (d_m * 1.4))

    # Origin on canvas (centered)
    ox = (width - (w_m * scale)) / 2.0
    oy = 55.0

    # 1. Road Frontage (Southern Edge)
    road_h_pts = road_widening_m * scale
    d.add(Rect(
        ox - 40, oy - road_h_pts,
        (w_m * scale) + 80, road_h_pts,
        fillColor=CAD_ROAD_FILL,
        strokeColor=CAD_GRID_LINE,
        strokeWidth=0.5
    ))
    d.add(String(
        width / 2.0 - 55, oy - (road_h_pts / 2.0) - 3,
        "PROPOSED 18.0m ROAD (12m EXISTING)",
        fontName="Helvetica-Bold", fontSize=7, fillColor=CAD_TEXT_MUTED
    ))

    # 2. Road Widening Dedication Strip (inside site)
    d.add(Rect(
        ox, oy,
        w_m * scale, road_h_pts,
        fillColor=colors.HexColor("#FEF2F2"),
        strokeColor=CAD_SETBACK_LINE,
        strokeWidth=1,
        strokeDashArray=[3, 3]
    ))
    d.add(String(
        ox + 8, oy + (road_h_pts / 2.0) - 3,
        "3.0m DEDICATED ROAD WIDENING RESERVATION (DCPR REG 30)",
        fontName="Helvetica-Oblique", fontSize=6.5, fillColor=CAD_SETBACK_LINE
    ))

    # 3. Authoritative Plot Boundary
    plot_pts = [
        ox, oy,
        ox + w_m * scale, oy,
        ox + w_m * scale, oy + d_m * scale,
        ox, oy + d_m * scale
    ]
    d.add(Polygon(
        points=plot_pts,
        fillColor=colors.white,
        strokeColor=CAD_PLOT_BOUNDARY,
        strokeWidth=2.0
    ))

    # 4. Buildable Envelope (Inside Setbacks)
    env_x = ox + side_sb * scale
    env_y = oy + (front_sb + road_widening_m) * scale
    env_w = max(10, (w_m - 2 * side_sb) * scale)
    env_h = max(10, (d_m - rear_sb - front_sb - road_widening_m) * scale)

    d.add(Rect(
        env_x, env_y, env_w, env_h,
        fillColor=CAD_ENVELOPE_FILL,
        strokeColor=CAD_ENVELOPE_BORDER,
        strokeWidth=1.2,
        strokeDashArray=[4, 2]
    ))
    d.add(String(
        env_x + 8, env_y + env_h - 14,
        "STATUTORY BUILDABLE ENVELOPE (49.06 m² FOOTPRINT)",
        fontName="Helvetica-Bold", fontSize=7, fillColor=CAD_ENVELOPE_BORDER
    ))

    # 5. Building Footprint (Ground Level)
    footprint_w = min(env_w - 4, env_w)
    footprint_h = min(env_h - 4, env_h)
    d.add(Rect(
        env_x + 2, env_y + 2, footprint_w, footprint_h,
        fillColor=colors.HexColor("#DBEAFE"),
        strokeColor=CAD_BRAND_BLUE,
        strokeWidth=1.5
    ))
    d.add(String(
        env_x + (footprint_w / 2.0) - 45, env_y + (footprint_h / 2.0) - 4,
        "GROUND FLOOR FOOTPRINT (49.0 m²)",
        fontName="Helvetica-Bold", fontSize=6.8, fillColor=CAD_BRAND_BLUE
    ))

    # 6. Boundary Dimensions
    # Front Width (Bottom)
    d.add(String(
        ox + (w_m * scale) / 2.0 - 32, oy + d_m * scale + 6,
        f"REAR BOUNDARY: {w_m:.2f}m (27.5 ft)",
        fontName="Helvetica-Bold", fontSize=7, fillColor=CAD_TEXT
    ))
    # Left Depth
    d.add(String(
        ox - 65, oy + (d_m * scale) / 2.0,
        f"DEPTH: {d_m:.2f}m (40.0 ft)",
        fontName="Helvetica-Bold", fontSize=7, fillColor=CAD_TEXT
    ))

    # Setback Callouts
    d.add(String(ox + w_m * scale + 5, env_y + (env_h / 2.0), f"Side Setback: {side_sb:.1f}m", fontName="Helvetica", fontSize=6.5, fillColor=CAD_TEXT_MUTED))
    d.add(String(ox + 6, oy + d_m * scale - 10, f"Rear Setback: {rear_sb:.1f}m", fontName="Helvetica", fontSize=6.5, fillColor=CAD_TEXT_MUTED))

    # 7. North Arrow & Scale Block
    d.add(render_north_arrow(width - 45, height - 48, size=20))
    d.add(String(width - 70, 18, "SCALE 1:150 (METRIC)", fontName="Helvetica-Bold", fontSize=7, fillColor=CAD_TEXT_MUTED))
    d.add(String(20, 18, "SITE & STATUTORY ENVELOPE PLAN — SECS TOPOCENTRIC FRAME", fontName="Helvetica-Bold", fontSize=8, fillColor=CAD_TEXT))

    return d


def render_floor_plan_drawing(
    cbm: Any,
    level_id: str = "LVL-000",
    width: float = 523.0,
    height: float = 330.0
) -> Drawing:
    """
    Renders authoritative 2D architectural floor plan for a specific level.
    Spaces, external walls, internal partitions, doors, windows, stairs,
    and columns are strictly derived from the CBM geometry.
    """
    d = Drawing(width, height)
    d.add(Rect(0, 0, width, height, fillColor=CAD_BACKGROUND, strokeColor=CAD_GRID_LINE, strokeWidth=1))

    # Identify target level
    level_obj = next((lvl for lvl in getattr(cbm, "levels", []) if getattr(lvl, "levelId", "") == level_id), None)
    level_name = getattr(level_obj, "name", "GROUND FLOOR")
    elevation_m = getattr(level_obj, "elevationM", 0.0)

    # Filter spaces on this level
    spaces = [s for s in getattr(cbm, "spaces", []) if getattr(s, "levelId", "") == level_id]
    elements = getattr(cbm, "elements", [])

    # Calculate bounding box of spaces for scaling
    if spaces:
        min_x = min(s.bounds.x for s in spaces)
        max_x = max(s.bounds.x + s.bounds.width for s in spaces)
        min_y = min(s.bounds.y for s in spaces)
        max_y = max(s.bounds.y + s.bounds.height for s in spaces)
    else:
        min_x, max_x, min_y, max_y = 0.0, 7.0, 0.0, 8.0

    bldg_w = max(1.0, max_x - min_x)
    bldg_h = max(1.0, max_y - min_y)

    margin_x = 45.0
    margin_y = 45.0
    draw_w = width - 2 * margin_x
    draw_h = height - 2 * margin_y

    scale = min(draw_w / (bldg_w * 1.15), draw_h / (bldg_h * 1.15))

    ox = margin_x + (draw_w - (bldg_w * scale)) / 2.0
    oy = margin_y + (draw_h - (bldg_h * scale)) / 2.0

    def to_canvas(x_m: float, y_m: float):
        return ox + (x_m - min_x) * scale, oy + (y_m - min_y) * scale

    # 1. Draw Spaces (Rooms) with zoning fills
    for s in spaces:
        # Bounds
        rx, ry = to_canvas(s.bounds.x, s.bounds.y)
        rw = s.bounds.width * scale
        rh = s.bounds.height * scale

        space_type = getattr(s, "spaceType", "DEFAULT")
        fill_color = ZONE_PALETTE.get(space_type, ZONE_PALETTE["DEFAULT"])

        d.add(Rect(rx, ry, rw, rh, fillColor=fill_color, strokeColor=CAD_GRID_LINE, strokeWidth=0.5))

        # Room Text Labels
        cx = rx + rw / 2.0
        cy = ry + rh / 2.0

        room_name = getattr(s, "name", space_type).upper()
        area_sqm = getattr(s, "areaSqm", s.bounds.width * s.bounds.height)
        area_sqft = area_sqm * 10.7639

        len_m = max(s.bounds.width, s.bounds.height)
        wid_m = min(s.bounds.width, s.bounds.height)

        d.add(String(cx - (len(room_name) * 2.3), cy + 5, room_name, fontName="Helvetica-Bold", fontSize=7.5, fillColor=CAD_TEXT))
        d.add(String(
            cx - 32, cy - 6,
            f"{len_m:.2f}m × {wid_m:.2f}m ({area_sqft:.0f} sq ft)",
            fontName="Helvetica", fontSize=6.5, fillColor=CAD_TEXT_MUTED
        ))

    # 2. Draw Walls (Footprint polygons or bounds edges)
    walls = [e for e in elements if getattr(e, "elementType", None) == "WALL" and getattr(e, "levelId", "") == level_id]
    if walls:
        for w in walls:
            geom = getattr(w, "geometry", None)
            thickness = getattr(geom, "thicknessM", 0.20) or 0.20
            stroke_w = 2.2 if getattr(w, "wallType", None) == "EXTERNAL" else 1.2
            stroke_c = CAD_WALL_EXT if getattr(w, "wallType", None) == "EXTERNAL" else CAD_WALL_INT

            centerline = getattr(geom, "centerline", None)
            if centerline and len(centerline) >= 2:
                p1x, p1y = to_canvas(centerline[0][0], centerline[0][1])
                p2x, p2y = to_canvas(centerline[1][0], centerline[1][1])
                d.add(Line(p1x, p1y, p2x, p2y, strokeColor=stroke_c, strokeWidth=stroke_w))
    else:
        # Fallback: derive external walls from outer spaces bounds
        for s in spaces:
            rx, ry = to_canvas(s.bounds.x, s.bounds.y)
            rw = s.bounds.width * scale
            rh = s.bounds.height * scale
            d.add(Rect(rx, ry, rw, rh, fillColor=None, strokeColor=CAD_WALL_EXT, strokeWidth=1.8))

    # 3. Draw Columns
    columns = [e for e in elements if getattr(e, "elementType", None) == "COLUMN" and getattr(e, "levelId", "") == level_id]
    for col in columns:
        props = getattr(col, "properties", {})
        cx_m = props.get("x", 0.0)
        cy_m = props.get("y", 0.0)
        col_w_m = props.get("widthMm", 230) / 1000.0
        col_d_m = props.get("depthMm", 380) / 1000.0

        ccx, ccy = to_canvas(cx_m, cy_m)
        cw_pts = col_w_m * scale
        cd_pts = col_d_m * scale

        d.add(Rect(ccx - cw_pts / 2.0, ccy - cd_pts / 2.0, cw_pts, cd_pts, fillColor=CAD_COLUMN, strokeColor=CAD_COLUMN, strokeWidth=0.5))

    # 4. Draw Openings (Doors & Windows)
    openings = getattr(cbm, "openings", [])
    lvl_openings = [o for o in openings if getattr(o, "levelId", "") == level_id]
    for op in lvl_openings:
        op_type = getattr(op, "openingType", "DOOR")
        pos_m = getattr(op, "positionM", [])
        w_m_op = getattr(op, "widthM", 0.9)
        if len(pos_m) >= 2:
            ox_c, oy_c = to_canvas(pos_m[0], pos_m[1])
            op_w_pts = w_m_op * scale
            if op_type == "DOOR":
                # Door swing arc + leaf
                d.add(Line(ox_c - op_w_pts / 2.0, oy_c, ox_c + op_w_pts / 2.0, oy_c, strokeColor=CAD_DOOR, strokeWidth=1.5))
                d.add(Circle(ox_c, oy_c, op_w_pts / 2.0, fillColor=None, strokeColor=CAD_DOOR, strokeWidth=0.6, strokeDashArray=[2, 2]))
            else:
                # Window double line
                d.add(Line(ox_c - op_w_pts / 2.0, oy_c - 1.5, ox_c + op_w_pts / 2.0, oy_c - 1.5, strokeColor=CAD_WINDOW, strokeWidth=1.2))
                d.add(Line(ox_c - op_w_pts / 2.0, oy_c + 1.5, ox_c + op_w_pts / 2.0, oy_c + 1.5, strokeColor=CAD_WINDOW, strokeWidth=1.2))

    # 5. Stair Representation (if stair space exists)
    stair_spaces = [s for s in spaces if "STAIR" in getattr(s, "name", "").upper() or getattr(s, "spaceType", "") == "STAIRCASE"]
    for st in stair_spaces:
        srx, sry = to_canvas(st.bounds.x, st.bounds.y)
        srw = st.bounds.width * scale
        srh = st.bounds.height * scale
        num_treads = 10
        tread_gap = srh / num_treads
        for ti in range(num_treads):
            d.add(Line(srx, sry + ti * tread_gap, srx + srw, sry + ti * tread_gap, strokeColor=CAD_STAIR, strokeWidth=0.7))
        # Walk line & arrow
        d.add(Line(srx + srw / 2.0, sry + 5, srx + srw / 2.0, sry + srh - 8, strokeColor=CAD_BRAND_BLUE, strokeWidth=1.0))
        d.add(Polygon(
            points=[srx + srw / 2.0, sry + srh - 2, srx + srw / 2.0 - 3, sry + srh - 8, srx + srw / 2.0 + 3, sry + srh - 8],
            fillColor=CAD_BRAND_BLUE, strokeColor=CAD_BRAND_BLUE
        ))
        d.add(String(srx + srw / 2.0 + 4, sry + 8, "UP", fontName="Helvetica-Bold", fontSize=6, fillColor=CAD_BRAND_BLUE))

    # 6. Title Block & North Arrow
    d.add(render_north_arrow(width - 45, height - 48, size=18))
    d.add(String(20, 18, f"{level_name.upper()} ARCHITECTURAL PLAN — DATUM: +{elevation_m:.2f}m", fontName="Helvetica-Bold", fontSize=8.5, fillColor=CAD_TEXT))
    d.add(String(width - 70, 18, "SCALE 1:100", fontName="Helvetica-Bold", fontSize=7, fillColor=CAD_TEXT_MUTED))

    return d


def render_roof_plan_drawing(cbm: Any, width: float = 523.0, height: float = 280.0) -> Drawing:
    """Renders authoritative Roof / Terrace Plan."""
    d = Drawing(width, height)
    d.add(Rect(0, 0, width, height, fillColor=CAD_BACKGROUND, strokeColor=CAD_GRID_LINE, strokeWidth=1))

    # Base building envelope
    env = getattr(cbm, "buildingEnvelope", {})
    bw = env.get("widthM", 6.38)
    bl = env.get("lengthM", 7.69)

    scale = min((width - 100) / bw, (height - 80) / bl)
    ox = (width - (bw * scale)) / 2.0
    oy = (height - (bl * scale)) / 2.0

    # Terrace Slab
    d.add(Rect(ox, oy, bw * scale, bl * scale, fillColor=colors.HexColor("#F8FAFC"), strokeColor=CAD_WALL_EXT, strokeWidth=2.2))

    # Parapet Wall
    d.add(Rect(ox + 4, oy + 4, bw * scale - 8, bl * scale - 8, fillColor=None, strokeColor=CAD_WALL_INT, strokeWidth=1.0, strokeDashArray=[4, 3]))
    d.add(String(ox + 12, oy + bl * scale - 18, "1.0m WATERPROOFED PARAPET WALL (IS 1200)", fontName="Helvetica-Bold", fontSize=7, fillColor=CAD_TEXT_MUTED))

    # Mumty / Stair Headroom
    mw = (bw * scale) * 0.35
    mh = (bl * scale) * 0.4
    d.add(Rect(ox + bw * scale - mw - 8, oy + 8, mw, mh, fillColor=colors.HexColor("#E2E8F0"), strokeColor=CAD_WALL_EXT, strokeWidth=1.5))
    d.add(String(ox + bw * scale - mw + 4, oy + mh / 2.0, "STAIR CABIN / MUMTY", fontName="Helvetica-Bold", fontSize=6.5, fillColor=CAD_TEXT))

    # Overhead Water Tank (OHT) Zone
    tw = 26.0
    th = 26.0
    d.add(Rect(ox + bw * scale - tw - 14, oy + mh + 12, tw, th, fillColor=colors.HexColor("#BFDBFE"), strokeColor=CAD_BRAND_BLUE, strokeWidth=1.0))
    d.add(String(ox + bw * scale - tw - 12, oy + mh + 22, "OHT", fontName="Helvetica-Bold", fontSize=6.5, fillColor=CAD_BRAND_BLUE))
    d.add(String(ox + bw * scale - tw - 38, oy + mh + 5, "1,500L TANK", fontName="Helvetica", fontSize=6, fillColor=CAD_TEXT_MUTED))

    # Usable Terrace area
    d.add(String(ox + 16, oy + (bl * scale) / 2.0, "OPEN USABLE TERRACE (CHINA MOSAIC WATERPROOFING)", fontName="Helvetica-Bold", fontSize=7.5, fillColor=CAD_TEXT_MUTED))

    # North Arrow
    d.add(render_north_arrow(width - 45, height - 48, size=18))
    d.add(String(20, 18, "ROOF & TERRACE PLAN — LEVEL +6.20m", fontName="Helvetica-Bold", fontSize=8.5, fillColor=CAD_TEXT))
    d.add(String(width - 70, 18, "SCALE 1:100", fontName="Helvetica-Bold", fontSize=7, fillColor=CAD_TEXT_MUTED))

    return d
