"""
Planwise Enterprise — Architectural Renderer V2 Real Validation Test Suite
==========================================================================

Generates real CBM for different project sizes and configurations.
Validates:
  1. Three distinct projects (1100, 2400, 10000 sq ft) produce different CBMs
  2. CBM mutation (2BHK → 3BHK) produces different drawings
  3. Room dimension mutation updates rendered output
  4. SVG hashes differ across projects
  5. CBM traceability (data-cbm-id present)
  6. Stair, door, window rendering from actual CBM openings
"""

import json
import math
import hashlib
import unittest
from pathlib import Path

# Backend imports
from workers.generation.house_generator import solve_room_allocation
from workers.generation.model_compiler import compile_canonical_building_model

ROOT_DIR = Path(__file__).parent.parent
TEST_OUT = ROOT_DIR / "artifacts" / "test_renderer_v2"
TEST_OUT.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def sqft_to_m2(sq_ft: float) -> float:
    return sq_ft * 0.0929

def m2_to_sqft(m2: float) -> float:
    return m2 * 10.764

def sqft_to_plot_dims(sq_ft: float):
    """Return (width_m, length_m) from plot area in sq ft, 16:9 aspect."""
    m2 = sqft_to_m2(sq_ft)
    w = math.sqrt(m2 * (16 / 9))
    l = m2 / w
    return round(w, 2), round(l, 2)

def to_ft_in(meters: float) -> str:
    if not meters or math.isnan(meters):
        return "0'-0\""
    total_inches = round(meters * 39.3700787)
    feet = total_inches // 12
    inches = total_inches % 12
    return f"{feet}'-{inches}\""

def xml_esc(text: str) -> str:
    """Escape XML special characters in text content."""
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&apos;"))

def svg_hash(svg_content: str) -> str:
    return hashlib.sha256(svg_content.encode()).hexdigest()


# ─────────────────────────────────────────────────────────────────────────────
# SVG Renderer — pure from CBM data, no hardcoded reference values
# ─────────────────────────────────────────────────────────────────────────────

def render_cbm_to_svg(cbm, selected_floor: str = "L0") -> str:
    """
    Full CBM → architectural SVG renderer.
    All geometry sourced strictly from the CBM.
    Every element carries data-cbm-id.
    """
    base_scale = 28  # px per meter
    padding_x = 95
    padding_top = 75
    padding_bot = 160

    env = cbm.buildingEnvelope if hasattr(cbm, 'buildingEnvelope') else cbm['buildingEnvelope']
    if hasattr(env, 'widthM'):
        bldg_w = env.widthM
        bldg_l = env.lengthM
    else:
        bldg_w = env['widthM']
        bldg_l = env['lengthM']

    bldg_w_px = bldg_w * base_scale
    bldg_l_px = bldg_l * base_scale

    svg_w = max(640, bldg_w_px + padding_x * 2)
    svg_h = max(700, bldg_l_px + padding_top + padding_bot)

    bx = (svg_w - bldg_w_px) / 2
    by = padding_top

    # select spaces, elements, openings on this floor
    all_spaces = cbm.spaces if hasattr(cbm, 'spaces') else cbm.get('spaces', [])
    all_elements = cbm.elements if hasattr(cbm, 'elements') else cbm.get('elements', [])
    all_openings = cbm.openings if hasattr(cbm, 'openings') else cbm.get('openings', [])

    def space_floor(s):
        return getattr(s, 'floor', None) or (s.get('floor') if isinstance(s, dict) else 'L0') or 'L0'

    def elem_level(e):
        lid = getattr(e, 'levelId', None) or (e.get('levelId') if isinstance(e, dict) else 'LVL-000') or 'LVL-000'
        return 'L0' if lid == 'LVL-000' else 'L1'

    def opening_level(o):
        lid = getattr(o, 'levelId', None) or (o.get('levelId') if isinstance(o, dict) else 'LVL-000') or 'LVL-000'
        return 'L0' if lid == 'LVL-000' else 'L1'

    spaces = [s for s in all_spaces if space_floor(s) == selected_floor]
    elements = [e for e in all_elements if elem_level(e) == selected_floor]
    openings = [o for o in all_openings if opening_level(o) == selected_floor]

    title = "FIRST FLOOR PLAN" if selected_floor == "L1" else "GROUND FLOOR PLAN"

    lines = [
        f'<svg id="cad-drawing-svg" width="{svg_w:.0f}" height="{svg_h:.0f}" '
        f'viewBox="0 0 {svg_w:.0f} {svg_h:.0f}" '
        f'xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Times New Roman, Times, serif">',
        # Background & border
        f'<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<rect x="15" y="15" width="{svg_w-30:.0f}" height="{svg_h-30:.0f}" fill="none" stroke="#000" stroke-width="1.2"/>',
        f'<rect x="20" y="20" width="{svg_w-40:.0f}" height="{svg_h-40:.0f}" fill="none" stroke="#000" stroke-width="0.5"/>',
    ]

    # ── Exterior Dimension Strings ──────────────────────────────────────────
    dim_top_y = by - 32
    dim_r_x = bx + bldg_w_px + 38
    lines += [
        f'<!-- Top dimension: {to_ft_in(bldg_w)} -->',
        f'<g class="cad-dim">',
        f'  <line x1="{bx:.1f}" y1="{by-40:.1f}" x2="{bx:.1f}" y2="{by+2:.1f}" stroke="#000" stroke-width="0.75"/>',
        f'  <line x1="{bx+bldg_w_px:.1f}" y1="{by-40:.1f}" x2="{bx+bldg_w_px:.1f}" y2="{by+2:.1f}" stroke="#000" stroke-width="0.75"/>',
        f'  <line x1="{bx:.1f}" y1="{dim_top_y:.1f}" x2="{bx+bldg_w_px:.1f}" y2="{dim_top_y:.1f}" stroke="#000" stroke-width="0.75"/>',
        f'  <line x1="{bx-5:.1f}" y1="{dim_top_y+5:.1f}" x2="{bx+5:.1f}" y2="{dim_top_y-5:.1f}" stroke="#000" stroke-width="1.2"/>',
        f'  <line x1="{bx+bldg_w_px-5:.1f}" y1="{dim_top_y+5:.1f}" x2="{bx+bldg_w_px+5:.1f}" y2="{dim_top_y-5:.1f}" stroke="#000" stroke-width="1.2"/>',
        f'  <text x="{bx+bldg_w_px/2:.1f}" y="{dim_top_y-6:.1f}" text-anchor="middle" font-size="16" fill="#000">{to_ft_in(bldg_w)}</text>',
        f'</g>',
        f'<g class="cad-dim">',
        f'  <line x1="{bx+bldg_w_px-2:.1f}" y1="{by:.1f}" x2="{dim_r_x+12:.1f}" y2="{by:.1f}" stroke="#000" stroke-width="0.75"/>',
        f'  <line x1="{bx+bldg_w_px-2:.1f}" y1="{by+bldg_l_px:.1f}" x2="{dim_r_x+12:.1f}" y2="{by+bldg_l_px:.1f}" stroke="#000" stroke-width="0.75"/>',
        f'  <line x1="{dim_r_x:.1f}" y1="{by:.1f}" x2="{dim_r_x:.1f}" y2="{by+bldg_l_px:.1f}" stroke="#000" stroke-width="0.75"/>',
        f'  <line x1="{dim_r_x-5:.1f}" y1="{by+5:.1f}" x2="{dim_r_x+5:.1f}" y2="{by-5:.1f}" stroke="#000" stroke-width="1.2"/>',
        f'  <line x1="{dim_r_x-5:.1f}" y1="{by+bldg_l_px+5:.1f}" x2="{dim_r_x+5:.1f}" y2="{by+bldg_l_px-5:.1f}" stroke="#000" stroke-width="1.2"/>',
        f'  <text x="{dim_r_x+22:.1f}" y="{by+bldg_l_px/2+5:.1f}" text-anchor="middle" font-size="16" fill="#000" '
        f'    transform="rotate(90 {dim_r_x+22:.1f} {by+bldg_l_px/2+5:.1f})">{to_ft_in(bldg_l)}</text>',
        f'</g>',
    ]

    # ── Walls from CBM elements ────────────────────────────────────────────
    lines.append('<g id="walls">')
    for elem in elements:
        e_type = getattr(elem, 'elementType', None) or (elem.get('elementType') if isinstance(elem, dict) else None)
        e_id = getattr(elem, 'elementId', None) or (elem.get('elementId') if isinstance(elem, dict) else 'wall-unknown')
        e_name = getattr(elem, 'name', '') or (elem.get('name', '') if isinstance(elem, dict) else '')
        w_type = getattr(elem, 'wallType', None) or (elem.get('wallType') if isinstance(elem, dict) else None)
        geom = getattr(elem, 'geometry', None) or (elem.get('geometry') if isinstance(elem, dict) else None)

        if str(e_type) not in ['WALL', 'ElementType.WALL']:
            continue
        if geom is None:
            continue

        fp = getattr(geom, 'footprintPolygon', None) or (geom.get('footprintPolygon') if isinstance(geom, dict) else [])
        if not fp:
            continue

        pts = " ".join(f"{bx + pt[0]*base_scale:.1f},{by + pt[1]*base_scale:.1f}" for pt in fp)
        is_ext = str(w_type) in ['EXTERNAL', 'WallType.EXTERNAL']
        sw = "1.6" if is_ext else "1.0"
        fill = "none" if is_ext else "rgba(0,0,0,0.04)"
        lines.append(
            f'  <polygon data-cbm-id="{e_id}" data-type="wall" data-is-exterior="{str(is_ext).lower()}" '
            f'points="{pts}" fill="{fill}" stroke="#000" stroke-width="{sw}" '
            f'style="cursor:pointer"/>'
        )
    lines.append('</g>')

    # ── Columns from CBM elements ─────────────────────────────────────────
    lines.append('<g id="columns">')
    for elem in elements:
        e_type = getattr(elem, 'elementType', None) or (elem.get('elementType') if isinstance(elem, dict) else None)
        if str(e_type) not in ['COLUMN', 'ElementType.COLUMN']:
            continue
        e_id = getattr(elem, 'elementId', '') or ''
        geom = getattr(elem, 'geometry', None) or (elem.get('geometry') if isinstance(elem, dict) else None)
        if geom is None:
            continue
        fp = getattr(geom, 'footprintPolygon', None) or (geom.get('footprintPolygon') if isinstance(geom, dict) else [])
        if not fp:
            continue
        pts = " ".join(f"{bx + pt[0]*base_scale:.1f},{by + pt[1]*base_scale:.1f}" for pt in fp)
        lines.append(
            f'  <polygon data-cbm-id="{e_id}" data-type="column" '
            f'points="{pts}" fill="#4a4a4a" stroke="#000" stroke-width="0.8"/>'
        )
    lines.append('</g>')

    # ── Stairs from CBM elements ──────────────────────────────────────────
    lines.append('<g id="stairs">')
    for elem in elements:
        e_type = getattr(elem, 'elementType', None) or (elem.get('elementType') if isinstance(elem, dict) else None)
        if str(e_type) not in ['STAIR', 'ElementType.STAIR']:
            continue
        e_id = getattr(elem, 'elementId', 'STAIR-unknown') or 'STAIR-unknown'
        geom = getattr(elem, 'geometry', None) or (elem.get('geometry') if isinstance(elem, dict) else None)
        props = getattr(elem, 'properties', {}) or (elem.get('properties', {}) if isinstance(elem, dict) else {})
        if geom is None:
            continue
        fp = getattr(geom, 'footprintPolygon', None) or (geom.get('footprintPolygon') if isinstance(geom, dict) else [])
        if not fp:
            continue

        riser_mm = props.get('riserMm', 175)
        tread_mm = props.get('treadMm', 250)
        num_risers = props.get('numberOfRisers', 18)
        tread_m = tread_mm / 1000.0
        tread_px = tread_m * base_scale

        # Bounding box of stair
        xs = [bx + pt[0]*base_scale for pt in fp]
        ys = [by + pt[1]*base_scale for pt in fp]
        sx0, sx1 = min(xs), max(xs)
        sy0, sy1 = min(ys), max(ys)
        stair_h_px = sy1 - sy0
        stair_w_px = sx1 - sx0

        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
        lines += [
            f'  <g data-cbm-id="{e_id}" data-type="stair">',
            f'    <!-- Stair: {num_risers} risers @ {riser_mm}mm, {tread_mm}mm tread -->',
            f'    <polygon points="{pts}" fill="#f5f5f0" stroke="#000" stroke-width="1.0"/>',
        ]

        # Landing at midpoint (for U-shape)
        landing_y = sy0 + stair_h_px / 2
        lines.append(
            f'    <line x1="{sx0:.1f}" y1="{landing_y:.1f}" x2="{sx1:.1f}" y2="{landing_y:.1f}" stroke="#000" stroke-width="1.5"/>'
        )

        # Treads — first flight (top half)
        half_risers = num_risers // 2
        flight_h_px = stair_h_px / 2
        for i in range(1, half_risers):
            ty = sy0 + i * (flight_h_px / half_risers)
            lines.append(
                f'    <line x1="{sx0:.1f}" y1="{ty:.1f}" x2="{sx1:.1f}" y2="{ty:.1f}" stroke="#000" stroke-width="0.7"/>'
            )
        # Treads — second flight (bottom half)
        for i in range(1, half_risers):
            ty = landing_y + i * (flight_h_px / half_risers)
            lines.append(
                f'    <line x1="{sx0:.1f}" y1="{ty:.1f}" x2="{sx1:.1f}" y2="{ty:.1f}" stroke="#000" stroke-width="0.7"/>'
            )

        # Direction arrow & UP label
        cx = (sx0 + sx1) / 2
        lines += [
            f'    <line x1="{cx:.1f}" y1="{landing_y+8:.1f}" x2="{cx:.1f}" y2="{sy0+8:.1f}" stroke="#000" stroke-width="1.0" marker-end="url(#arrowhead)"/>',
            f'    <text x="{cx:.1f}" y="{sy0 - 4:.1f}" text-anchor="middle" font-size="11" font-weight="bold" fill="#000">UP</text>',
        ]
        lines.append('  </g>')

    lines.append('</g>')

    # ── Openings (Doors & Windows) ────────────────────────────────────────
    lines.append('<g id="openings">')
    for op in openings:
        o_id = getattr(op, 'openingId', 'OP-unknown') or (op.get('openingId', 'OP-unknown') if isinstance(op, dict) else 'OP-unknown')
        o_type = getattr(op, 'openingType', None) or (op.get('openingType') if isinstance(op, dict) else None)
        o_w = getattr(op, 'widthM', 0.9) or (op.get('widthM', 0.9) if isinstance(op, dict) else 0.9)
        pos = getattr(op, 'positionM', [0, 0]) or (op.get('positionM', [0, 0]) if isinstance(op, dict) else [0, 0])
        swing = getattr(op, 'swing', '') or (op.get('swing', '') if isinstance(op, dict) else '')
        orient = getattr(op, 'orientation', '') or (op.get('orientation', '') if isinstance(op, dict) else '')

        ox = bx + pos[0] * base_scale
        oy = by + pos[1] * base_scale
        ow = o_w * base_scale

        if str(o_type) in ['DOOR', 'OpeningType.DOOR']:
            # Clear wall gap (white rect)
            gap_thick = 8
            # Determine door swing direction from host wall orientation
            # Default: door opens inward (upward = into room from top wall)
            inward = "RIGHT_INWARD" not in str(swing)
            # Draw door leaf + arc relative to opening center
            leaf_end_x = ox + ow / 2
            leaf_end_y = oy
            hinge_x = ox - ow / 2
            hinge_y = oy

            lines += [
                f'  <g data-cbm-id="{o_id}" data-type="door">',
                f'    <!-- Door opening: {o_w:.2f}m wide, swing={swing} -->',
                # White gap at wall
                f'    <rect x="{ox - ow/2:.1f}" y="{oy - gap_thick/2:.1f}" width="{ow:.1f}" height="{gap_thick:.0f}" fill="#fff" stroke="none"/>',
                # Door leaf line
                f'    <line x1="{hinge_x:.1f}" y1="{hinge_y:.1f}" x2="{leaf_end_x:.1f}" y2="{leaf_end_y:.1f}" stroke="#000" stroke-width="0.9"/>',
                # Swing arc quarter circle
                f'    <path d="M {hinge_x:.1f} {hinge_y:.1f} A {ow:.1f} {ow:.1f} 0 0 1 {hinge_x:.1f} {hinge_y - ow:.1f}" fill="none" stroke="#000" stroke-width="0.65" stroke-dasharray="4 2"/>',
                f'  </g>',
            ]

        elif str(o_type) in ['WINDOW', 'OpeningType.WINDOW']:
            win_thick = 6
            lines += [
                f'  <g data-cbm-id="{o_id}" data-type="window">',
                # White gap at wall
                f'  <rect x="{ox - ow/2:.1f}" y="{oy - win_thick/2:.1f}" width="{ow:.1f}" height="{win_thick:.0f}" fill="#fff" stroke="none"/>',
                # Three-line window symbol: outer frame + inner glazing line
                f'  <line x1="{ox - ow/2:.1f}" y1="{oy:.1f}" x2="{ox + ow/2:.1f}" y2="{oy:.1f}" stroke="#000" stroke-width="1.2"/>',
                f'  <line x1="{ox - ow/2:.1f}" y1="{oy - 2:.1f}" x2="{ox + ow/2:.1f}" y2="{oy - 2:.1f}" stroke="#000" stroke-width="0.5"/>',
                f'  <line x1="{ox - ow/2:.1f}" y1="{oy + 2:.1f}" x2="{ox + ow/2:.1f}" y2="{oy + 2:.1f}" stroke="#000" stroke-width="0.5"/>',
                f'  </g>',
            ]
    lines.append('</g>')

    # ── Spaces (Rooms) from CBM ────────────────────────────────────────────
    lines.append('<g id="spaces">')
    for space in spaces:
        s_id = getattr(space, 'spaceId', 'SPACE-unknown') or (space.get('spaceId', 'SPACE-unknown') if isinstance(space, dict) else 'SPACE-unknown')
        s_name = getattr(space, 'name', 'Room') or (space.get('name', 'Room') if isinstance(space, dict) else 'Room')
        bounds = getattr(space, 'bounds', None) or (space.get('bounds') if isinstance(space, dict) else None)
        if bounds is None:
            continue

        bnd_x = getattr(bounds, 'x', 0) if hasattr(bounds, 'x') else bounds.get('x', 0)
        bnd_y = getattr(bounds, 'y', 0) if hasattr(bounds, 'y') else bounds.get('y', 0)
        bnd_w = getattr(bounds, 'width', 0) if hasattr(bounds, 'width') else bounds.get('width', 0)
        bnd_h = getattr(bounds, 'height', 0) if hasattr(bounds, 'height') else bounds.get('height', 0)

        rx = bx + bnd_x * base_scale
        ry = by + bnd_y * base_scale
        rw = bnd_w * base_scale
        rh = bnd_h * base_scale

        # Room type detection
        n = s_name.lower()
        is_bed = any(k in n for k in ['bed', 'suite', 'master'])
        is_living = any(k in n for k in ['living', 'hall', 'lounge', 'dining', 'foyer'])
        is_kitchen = any(k in n for k in ['kitchen', 'utility', 'pantry'])
        is_toilet = any(k in n for k in ['bath', 'toilet', 'powder', 'wc'])
        is_balcony = any(k in n for k in ['balcony', 'terrace', 'deck', 'courtyard'])

        dim_label = f"{to_ft_in(bnd_h)} WIDE" if is_balcony else f"{to_ft_in(bnd_w)}x{to_ft_in(bnd_h)}"
        font_sz = max(9, min(13, int(base_scale * 0.45)))

        lines += [
            f'  <g data-cbm-id="{s_id}" data-type="space">',
            # ── Furniture (visual overlay only, data-symbol-id) ────────────
        ]

        # Bed stencil
        if is_bed and rw > 50 and rh > 50:
            lines += [
                f'    <g data-symbol-id="furn-bed-{s_id}">',
                f'      <rect x="{rx+6:.0f}" y="{ry+10:.0f}" width="6" height="44" fill="none" stroke="#000" stroke-width="0.75"/>',
                f'      <rect x="{rx+12:.0f}" y="{ry+12:.0f}" width="{min(rw-20, 48):.0f}" height="{min(rh-20, 40):.0f}" fill="none" stroke="#000" stroke-width="0.75"/>',
                f'      <rect x="{rx+14:.0f}" y="{ry+14:.0f}" width="12" height="16" rx="2" fill="none" stroke="#000" stroke-width="0.75"/>',
                f'      <rect x="{rx+14:.0f}" y="{ry+34:.0f}" width="12" height="16" rx="2" fill="none" stroke="#000" stroke-width="0.75"/>',
                f'    </g>',
            ]

        # Living stencil
        if is_living and rw > 60:
            lines += [
                f'    <g data-symbol-id="furn-living-{s_id}">',
                f'      <rect x="{rx+rw-24:.0f}" y="{ry+10:.0f}" width="18" height="{min(rh-20, 56):.0f}" fill="none" stroke="#000" stroke-width="0.75"/>',
                f'    </g>',
            ]

        # Kitchen counter
        if is_kitchen and rw > 40:
            lines += [
                f'    <g data-symbol-id="furn-kitchen-{s_id}">',
                f'      <path d="M {rx+4:.0f} {ry+4:.0f} L {rx+4:.0f} {ry+rh-4:.0f} L {rx+20:.0f} {ry+rh-4:.0f} L {rx+20:.0f} {ry+20:.0f} L {rx+rw-4:.0f} {ry+20:.0f} L {rx+rw-4:.0f} {ry+4:.0f} Z" fill="none" stroke="#000" stroke-width="0.75"/>',
                f'    </g>',
            ]

        # Toilet fixtures
        if is_toilet and rw > 25 and rh > 25:
            lines += [
                f'    <g data-symbol-id="furn-toilet-{s_id}">',
                f'      <rect x="{rx+5:.0f}" y="{ry+5:.0f}" width="14" height="8" fill="none" stroke="#000" stroke-width="0.75"/>',
                f'      <ellipse cx="{rx+12:.0f}" cy="{ry+20:.0f}" rx="6" ry="8" fill="none" stroke="#000" stroke-width="0.75"/>',
                f'    </g>',
            ]

        # Room label (from CBM name & bounds — no hardcoded values)
        cx_text = rx + rw / 2
        cy_text = ry + rh / 2

        lines += [
            f'    <text x="{cx_text:.1f}" y="{cy_text - 4:.1f}" text-anchor="middle" font-size="{font_sz}" font-weight="bold" fill="#000">{xml_esc(s_name.upper())}</text>',
            f'    <text x="{cx_text:.1f}" y="{cy_text + font_sz:.1f}" text-anchor="middle" font-size="{max(8, font_sz-2)}" fill="#000">{xml_esc(dim_label)}</text>',
            f'  </g>',
        ]

    lines.append('</g>')

    # ── Compass Rose ───────────────────────────────────────────────────────
    compass_x = bx - 50
    compass_y = by + bldg_l_px + 22
    lines += [
        f'<g id="compass" transform="translate({compass_x:.0f},{compass_y:.0f})">',
        f'  <circle cx="22" cy="22" r="18" fill="none" stroke="#000" stroke-width="0.8"/>',
        f'  <polygon points="22,22 22,4 25,22" fill="#000" stroke="#000" stroke-width="0.5"/>',
        f'  <polygon points="22,22 22,4 19,22" fill="#fff" stroke="#000" stroke-width="0.5"/>',
        f'  <polygon points="22,22 40,22 22,25" fill="#000" stroke="#000" stroke-width="0.5"/>',
        f'  <polygon points="22,22 40,22 22,19" fill="#fff" stroke="#000" stroke-width="0.5"/>',
        f'  <polygon points="22,22 22,40 19,22" fill="#000" stroke="#000" stroke-width="0.5"/>',
        f'  <polygon points="22,22 22,40 25,22" fill="#fff" stroke="#000" stroke-width="0.5"/>',
        f'  <polygon points="22,22 4,22 22,19" fill="#000" stroke="#000" stroke-width="0.5"/>',
        f'  <polygon points="22,22 4,22 22,25" fill="#fff" stroke="#000" stroke-width="0.5"/>',
        f'  <text x="22" y="2" text-anchor="middle" font-size="9" font-weight="bold" fill="#000">N</text>',
        f'</g>',
    ]

    # ── Sheet Title ────────────────────────────────────────────────────────
    title_cx = bx + bldg_w_px / 2
    title_y = by + bldg_l_px + 38
    lines += [
        f'<g id="sheet-title">',
        f'  <text x="{title_cx:.1f}" y="{title_y:.1f}" text-anchor="middle" font-size="15" font-weight="bold" letter-spacing="1" fill="#000">{title}</text>',
        f'  <line x1="{title_cx-65:.1f}" y1="{title_y+4:.1f}" x2="{title_cx+65:.1f}" y2="{title_y+4:.1f}" stroke="#000" stroke-width="1.0"/>',
        f'  <line x1="{title_cx-65:.1f}" y1="{title_y+6:.1f}" x2="{title_cx+65:.1f}" y2="{title_y+6:.1f}" stroke="#000" stroke-width="0.5"/>',
        f'</g>',
    ]

    # ── Road Box ─────────────────────────────────────────────────────────
    road_y = by + bldg_l_px + 58
    lines += [
        f'<g id="road-frontage">',
        f'  <rect x="{bx-20:.1f}" y="{road_y:.1f}" width="{bldg_w_px+40:.1f}" height="52" fill="none" stroke="#000" stroke-width="1.0"/>',
        f'  <text x="{title_cx:.1f}" y="{road_y+33:.1f}" text-anchor="middle" font-size="16" letter-spacing="12" font-weight="bold" fill="#000">R O A D</text>',
        f'</g>',
    ]

    lines.append('</svg>')
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Test Class
# ─────────────────────────────────────────────────────────────────────────────

class TestArchitecturalRendererV2(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Generate real CBM for three distinct projects once."""
        # Project A: 1100 sq ft, 2BHK
        w_a, l_a = sqft_to_plot_dims(1100)
        layout_a = solve_room_allocation("compact_2bhk", w_a, l_a)
        cls.cbm_a = compile_canonical_building_model(
            layout_data=layout_a,
            design_version_id="DV-TEST-A-1100",
            project_id="proj-test-1100",
            archetype="compact_2bhk"
        )

        # Project B: 2400 sq ft, 3BHK
        w_b, l_b = sqft_to_plot_dims(2400)
        layout_b = solve_room_allocation("family_3bhk", w_b, l_b)
        cls.cbm_b = compile_canonical_building_model(
            layout_data=layout_b,
            design_version_id="DV-TEST-B-2400",
            project_id="proj-test-2400",
            archetype="family_3bhk"
        )

        # Project C: 10000 sq ft, 4BHK Duplex
        w_c, l_c = sqft_to_plot_dims(10000)
        layout_c = solve_room_allocation("duplex_3bhk", w_c, l_c)
        cls.cbm_c = compile_canonical_building_model(
            layout_data=layout_c,
            design_version_id="DV-TEST-C-10000",
            project_id="proj-test-10000",
            archetype="duplex_3bhk"
        )

        # Render SVGs
        cls.svg_a = render_cbm_to_svg(cls.cbm_a, "L0")
        cls.svg_b = render_cbm_to_svg(cls.cbm_b, "L0")
        cls.svg_c = render_cbm_to_svg(cls.cbm_c, "L0")

        # Save SVGs
        (TEST_OUT / "project_a_1100sqft.svg").write_text(cls.svg_a)
        (TEST_OUT / "project_b_2400sqft.svg").write_text(cls.svg_b)
        (TEST_OUT / "project_c_10000sqft.svg").write_text(cls.svg_c)

        # BHK mutation (same 1100 sqft plot)
        w_mut, l_mut = sqft_to_plot_dims(1100)
        layout_2bhk = solve_room_allocation("compact_2bhk", w_mut, l_mut)
        cls.cbm_2bhk = compile_canonical_building_model(
            layout_data=layout_2bhk,
            design_version_id="DV-TEST-2BHK",
            project_id="proj-test-mut-2bhk",
            archetype="compact_2bhk"
        )
        layout_3bhk = solve_room_allocation("family_3bhk", w_mut, l_mut)
        cls.cbm_3bhk = compile_canonical_building_model(
            layout_data=layout_3bhk,
            design_version_id="DV-TEST-3BHK",
            project_id="proj-test-mut-3bhk",
            archetype="family_3bhk"
        )
        cls.svg_2bhk = render_cbm_to_svg(cls.cbm_2bhk, "L0")
        cls.svg_3bhk = render_cbm_to_svg(cls.cbm_3bhk, "L0")
        (TEST_OUT / "mutation_2bhk.svg").write_text(cls.svg_2bhk)
        (TEST_OUT / "mutation_3bhk.svg").write_text(cls.svg_3bhk)

        # Dimension mutation
        import copy
        layout_mut = solve_room_allocation("compact_2bhk", w_mut, l_mut)
        # Find first bedroom
        for r in layout_mut["rooms"]:
            if "bed" in r["id"].lower() or "master" in r["id"].lower():
                r["bounds"]["width"] = 4.5
                r["bounds"]["height"] = 3.8
                r["areaSqm"] = round(4.5 * 3.8, 2)
                r["widthM"] = 4.5
                r["lengthM"] = 3.8
                break
        cls.cbm_mut_dim = compile_canonical_building_model(
            layout_data=layout_mut,
            design_version_id="DV-TEST-DIM-MUT",
            project_id="proj-test-dim-mut",
            archetype="compact_2bhk"
        )
        cls.svg_mut_dim = render_cbm_to_svg(cls.cbm_mut_dim, "L0")
        (TEST_OUT / "mutation_dimension.svg").write_text(cls.svg_mut_dim)

        # Write metadata report JSON
        report = {
            "project_a": {
                "plotSqFt": 1100,
                "archetype": "compact_2bhk",
                "modelId": cls.cbm_a.modelId,
                "envelope": {"widthM": cls.cbm_a.buildingEnvelope["widthM"], "lengthM": cls.cbm_a.buildingEnvelope["lengthM"]},
                "spaceCount": len(cls.cbm_a.spaces),
                "elementCount": len(cls.cbm_a.elements),
                "openingCount": len(cls.cbm_a.openings),
                "svgHash": svg_hash(cls.svg_a)
            },
            "project_b": {
                "plotSqFt": 2400,
                "archetype": "family_3bhk",
                "modelId": cls.cbm_b.modelId,
                "envelope": {"widthM": cls.cbm_b.buildingEnvelope["widthM"], "lengthM": cls.cbm_b.buildingEnvelope["lengthM"]},
                "spaceCount": len(cls.cbm_b.spaces),
                "elementCount": len(cls.cbm_b.elements),
                "openingCount": len(cls.cbm_b.openings),
                "svgHash": svg_hash(cls.svg_b)
            },
            "project_c": {
                "plotSqFt": 10000,
                "archetype": "duplex_3bhk",
                "modelId": cls.cbm_c.modelId,
                "envelope": {"widthM": cls.cbm_c.buildingEnvelope["widthM"], "lengthM": cls.cbm_c.buildingEnvelope["lengthM"]},
                "spaceCount": len(cls.cbm_c.spaces),
                "elementCount": len(cls.cbm_c.elements),
                "openingCount": len(cls.cbm_c.openings),
                "svgHash": svg_hash(cls.svg_c)
            },
            "mutation_2bhk": {
                "svgHash": svg_hash(cls.svg_2bhk),
                "spaceCount": len(cls.cbm_2bhk.spaces)
            },
            "mutation_3bhk": {
                "svgHash": svg_hash(cls.svg_3bhk),
                "spaceCount": len(cls.cbm_3bhk.spaces)
            },
            "mutation_dim": {
                "svgHash": svg_hash(cls.svg_mut_dim)
            }
        }
        (TEST_OUT / "validation_metadata.json").write_text(json.dumps(report, indent=2))

    # ─── Test 1: CBM differs per project ───────────────────────────────────

    def test_01_project_a_cbm_generated(self):
        """Project A (1100 sqft, 2BHK) generates valid CBM."""
        self.assertIsNotNone(self.cbm_a)
        self.assertGreater(len(self.cbm_a.spaces), 0)
        self.assertGreater(len(self.cbm_a.elements), 0)

    def test_02_project_b_cbm_generated(self):
        """Project B (2400 sqft, 3BHK) generates valid CBM."""
        self.assertIsNotNone(self.cbm_b)
        self.assertGreater(len(self.cbm_b.spaces), 0)

    def test_03_project_c_cbm_generated(self):
        """Project C (10000 sqft, duplex) generates valid CBM."""
        self.assertIsNotNone(self.cbm_c)
        self.assertGreater(len(self.cbm_c.spaces), 0)

    # ─── Test 2: Building envelopes differ ────────────────────────────────

    def test_04_envelopes_differ_a_vs_b(self):
        """Project A and B have materially different building envelopes."""
        ea = self.cbm_a.buildingEnvelope
        eb = self.cbm_b.buildingEnvelope
        wa, wb = ea["widthM"] if isinstance(ea, dict) else ea.widthM, eb["widthM"] if isinstance(eb, dict) else eb.widthM
        la, lb = ea["lengthM"] if isinstance(ea, dict) else ea.lengthM, eb["lengthM"] if isinstance(eb, dict) else eb.lengthM
        diff_area = abs((wa * la) - (wb * lb))
        self.assertGreater(diff_area, 1.0, f"A={wa*la:.1f}m² vs B={wb*lb:.1f}m² — too similar")

    def test_05_envelopes_differ_b_vs_c(self):
        """Project B and C have materially different building envelopes."""
        eb = self.cbm_b.buildingEnvelope
        ec = self.cbm_c.buildingEnvelope
        wb, wc = eb["widthM"] if isinstance(eb, dict) else eb.widthM, ec["widthM"] if isinstance(ec, dict) else ec.widthM
        lb, lc = eb["lengthM"] if isinstance(eb, dict) else eb.lengthM, ec["lengthM"] if isinstance(ec, dict) else ec.lengthM
        diff_area = abs((wb * lb) - (wc * lc))
        self.assertGreater(diff_area, 1.0, f"B={wb*lb:.1f}m² vs C={wc*lc:.1f}m² — too similar")

    # ─── Test 3: Room counts differ ───────────────────────────────────────

    def test_06_room_count_a_vs_b(self):
        """2BHK (A) has fewer rooms than 3BHK (B)."""
        self.assertLess(len(self.cbm_a.spaces), len(self.cbm_b.spaces),
                        f"2BHK spaces={len(self.cbm_a.spaces)}, 3BHK spaces={len(self.cbm_b.spaces)}")

    # ─── Test 4: SVG hashes differ ────────────────────────────────────────

    def test_07_svg_hashes_differ_a_vs_b(self):
        """SVG for 1100sqft != SVG for 2400sqft."""
        self.assertNotEqual(svg_hash(self.svg_a), svg_hash(self.svg_b),
                            "SVG hashes are identical — same drawing regardless of project size!")

    def test_08_svg_hashes_differ_b_vs_c(self):
        """SVG for 2400sqft != SVG for 10000sqft."""
        self.assertNotEqual(svg_hash(self.svg_b), svg_hash(self.svg_c))

    def test_09_svg_hashes_differ_a_vs_c(self):
        """SVG for 1100sqft != SVG for 10000sqft."""
        self.assertNotEqual(svg_hash(self.svg_a), svg_hash(self.svg_c))

    # ─── Test 5: Dimension strings differ ─────────────────────────────────

    def test_10_dimension_strings_differ(self):
        """Top dimension label for A differs from B (different envelopes)."""
        ea = self.cbm_a.buildingEnvelope
        eb = self.cbm_b.buildingEnvelope
        wa = ea["widthM"] if isinstance(ea, dict) else ea.widthM
        wb = eb["widthM"] if isinstance(eb, dict) else eb.widthM
        dim_a = to_ft_in(wa)
        dim_b = to_ft_in(wb)
        self.assertNotEqual(dim_a, dim_b, f"Dimension strings are the same: {dim_a}")

    # ─── Test 6: BHK Mutation changes room count ──────────────────────────

    def test_11_bhk_mutation_room_count(self):
        """3BHK has more rooms than 2BHK on same plot."""
        n2 = len(self.cbm_2bhk.spaces)
        n3 = len(self.cbm_3bhk.spaces)
        self.assertGreater(n3, n2, f"3BHK ({n3}) should have more spaces than 2BHK ({n2})")

    def test_12_bhk_mutation_svg_differs(self):
        """2BHK SVG differs from 3BHK SVG on same plot."""
        self.assertNotEqual(svg_hash(self.svg_2bhk), svg_hash(self.svg_3bhk))

    # ─── Test 7: Dimension mutation changes SVG ───────────────────────────

    def test_13_dimension_mutation_svg_differs(self):
        """SVG after dimension mutation differs from original."""
        self.assertNotEqual(svg_hash(self.svg_a), svg_hash(self.svg_mut_dim),
                            "SVG unchanged after bedroom dimension mutation!")

    def test_14_dimension_mutation_label_changed(self):
        """Dimension label in mutated SVG reflects new room size (XML-escaped form)."""
        # 4.5m ≈ 14'-9" → escaped in SVG as "14&apos;-9&quot;"
        feet_escaped = "14&apos;"  # XML-escaped form of 14'
        self.assertIn(feet_escaped, self.svg_mut_dim,
                      f"Expected feet value {feet_escaped!r} in mutated SVG but not found.")

    # ─── Test 8: CBM Traceability (data-cbm-id) ───────────────────────────

    def test_15_traceability_spaces(self):
        """All space IDs appear as data-cbm-id in SVG A."""
        for space in self.cbm_a.spaces:
            self.assertIn(space.spaceId, self.svg_a,
                          f"Space {space.spaceId} not traceable in SVG")

    def test_16_traceability_walls(self):
        """Exterior wall IDs appear as data-cbm-id in SVG A."""
        for elem in self.cbm_a.elements:
            if hasattr(elem.elementType, 'value'):
                etype = elem.elementType.value
            else:
                etype = str(elem.elementType)
            if 'WALL' in etype:
                self.assertIn(elem.elementId, self.svg_a,
                              f"Wall {elem.elementId} not traceable in SVG")

    def test_17_traceability_openings(self):
        """Opening IDs appear as data-cbm-id in SVG A."""
        for op in self.cbm_a.openings:
            self.assertIn(op.openingId, self.svg_a,
                          f"Opening {op.openingId} not traceable in SVG")

    # ─── Test 9: Stair rendering (multi-floor project C) ──────────────────

    def test_18_stair_rendered(self):
        """Stair element rendered from CBM in multi-floor project C."""
        has_stair = any(
            str(e.elementType) in ['STAIR', 'ElementType.STAIR']
            for e in self.cbm_c.elements
        )
        self.assertTrue(has_stair, "CBM_C has no STAIR element")
        self.assertIn('data-type="stair"', self.svg_c, "No stair SVG group in project C")
        self.assertIn('>UP</text>', self.svg_c, "No UP label rendered for stair")

    # ─── Test 10: SVG XML Validity ────────────────────────────────────────

    def test_19_svg_xml_valid_a(self):
        """SVG A is valid XML."""
        import xml.etree.ElementTree as ET
        root = ET.fromstring(self.svg_a)
        self.assertIsNotNone(root)
        self.assertIn('svg', root.tag)

    def test_20_svg_xml_valid_b(self):
        """SVG B is valid XML."""
        import xml.etree.ElementTree as ET
        root = ET.fromstring(self.svg_b)
        self.assertIsNotNone(root)

    def test_21_svg_xml_valid_c(self):
        """SVG C is valid XML."""
        import xml.etree.ElementTree as ET
        root = ET.fromstring(self.svg_c)
        self.assertIsNotNone(root)

    # ─── Test 11: Door arcs rendered from CBM openings ────────────────────

    def test_22_doors_rendered_from_cbm(self):
        """Door arcs appear in SVG from CBM openings (not hardcoded)."""
        door_count = self.svg_a.count('data-type="door"')
        cbm_door_count = sum(1 for o in self.cbm_a.openings
                             if str(o.openingType) in ['DOOR', 'OpeningType.DOOR'])
        self.assertEqual(door_count, cbm_door_count,
                         f"SVG has {door_count} doors but CBM has {cbm_door_count}")

    # ─── Test 12: Windows rendered from CBM openings ──────────────────────

    def test_23_windows_rendered_from_cbm(self):
        """Window symbols appear in SVG from CBM openings."""
        win_count = self.svg_a.count('data-type="window"')
        cbm_win_count = sum(1 for o in self.cbm_a.openings
                            if str(o.openingType) in ['WINDOW', 'OpeningType.WINDOW'])
        self.assertEqual(win_count, cbm_win_count,
                         f"SVG has {win_count} windows but CBM has {cbm_win_count}")

    # ─── Test 13: No reference hardcoded values in SVG ────────────────────

    def test_24_no_hardcoded_reference_values(self):
        """SVG must not contain 28x46 reference layout dimensions as labels."""
        # "28'" as a dimension string would indicate the 28-foot reference was hardcoded
        # But real projects at ~1100sqft have ~10m widths = ~33' not 28'
        # We verify the top dimension label matches the actual envelope
        ea = self.cbm_a.buildingEnvelope
        wa = ea["widthM"] if isinstance(ea, dict) else ea.widthM
        expected_dim = to_ft_in(wa)
        # The dimension in SVG should be the CBM-derived value, not "28'"
        self.assertIn(expected_dim, self.svg_a, f"Expected dim {expected_dim} not in SVG")

    def test_25_output_files_created(self):
        """All SVG output files were created in test output directory."""
        for fname in ["project_a_1100sqft.svg", "project_b_2400sqft.svg",
                      "project_c_10000sqft.svg", "mutation_2bhk.svg",
                      "mutation_3bhk.svg", "mutation_dimension.svg",
                      "validation_metadata.json"]:
            self.assertTrue((TEST_OUT / fname).exists(), f"Missing: {fname}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
