"""
Planwise Enterprise — Deterministic Statutory Rule Engine & Execution Tracer
Delta Specification M1 — §5, §6, §7, §8, §9

Orchestrates the authoritative statutory feasibility pipeline:
SITE -> PARCEL -> ROAD CONTEXT -> LAND USE -> ROAD WIDENING -> BUILDABLE AREA -> SETBACKS -> FSI/FAR -> GROUND COVERAGE -> HEIGHT -> PARKING -> FINAL FEASIBILITY

Every step is deterministic, mathematical, and produces a complete RuleExecutionTrace.
"""

from typing import List, Dict, Any, Tuple, Optional
import math
import json
from pathlib import Path
from datetime import datetime
from shapely.geometry import Polygon, LineString, MultiPolygon, box
from shapely.ops import transform

from packages.schemas.regulation_rules import (
    RulePack,
    StatutoryRule,
    RuleCategory,
    RuleSeverity,
    RuleStatus,
    EdgeClassification,
    ClassifiedEdge,
    RuleExecutionTrace,
    FeasibilityExplainabilityBreakdown
)
from packages.schemas.coordinates import SiteReferenceFrame
from workers.geometry.crs_engine import (
    polygon_wgs84_to_secs,
    polygon_secs_to_wgs84,
    calculate_secs_polygon_area,
    calculate_secs_polygon_perimeter
)

# Rule pack cache
RULE_PACKS_CACHE: Dict[str, RulePack] = {}
RULES_DIR = Path(__file__).resolve().parent.parent.parent / "packages" / "rules"


def load_rule_pack(rule_pack_id: str = "MUMBAI-DCPR-2034-V1") -> RulePack:
    """Loads and validates a declarative RulePack from disk or cache (§5, §9)."""
    norm_id = rule_pack_id.upper().replace(" ", "_")
    if norm_id in RULE_PACKS_CACHE:
        return RULE_PACKS_CACHE[norm_id]

    file_mapping = {
        "MUMBAI-DCPR-2034-V1": RULES_DIR / "mumbai_dcpr_2034_v1.json",
        "MUMBAI_DCPR_2034": RULES_DIR / "mumbai_dcpr_2034_v1.json",
        "MUMBAI_DCPR_2034_V1": RULES_DIR / "mumbai_dcpr_2034_v1.json",
        "BBMP-RES-2026-01": RULES_DIR / "bbmp_bengaluru_2026.json",
        "BBMP-BENGALURU-2026-V1": RULES_DIR / "bbmp_bengaluru_2026.json",
        "BBMP_BENGALURU_2026_V1": RULES_DIR / "bbmp_bengaluru_2026.json",
        "BBMP_BENGALURU_2026": RULES_DIR / "bbmp_bengaluru_2026.json"
    }

    target_file = file_mapping.get(norm_id, RULES_DIR / "mumbai_dcpr_2034_v1.json")
    if not target_file.exists():
        # Fallback to standard mumbai json if exists
        target_file = RULES_DIR / "mumbai_dcpr_2034.json"

    with open(target_file, "r") as f:
        data = json.load(f)

    # Convert to RulePack
    if "rulePackId" in data:
        pack = RulePack(**data)
    else:
        # Synthesize from legacy format
        pack = RulePack(
            rulePackId="MUMBAI-DCPR-2034-V1",
            jurisdiction="MCGM",
            authority="Municipal Corporation of Greater Mumbai",
            name="Mumbai DCPR 2034 Legacy Adapter",
            version="1.0.0",
            effectiveFrom="2026-01-01",
            rules=[]
        )

    RULE_PACKS_CACHE[norm_id] = pack
    RULE_PACKS_CACHE[pack.rulePackId] = pack
    return pack


def classify_parcel_edges(
    polygon_coords_secs: List[List[float]],
    road_frontage_edge_indices: Optional[List[int]] = None,
    primary_road_width_m: float = 12.0
) -> List[ClassifiedEdge]:
    """
    Deterministically classifies all boundary edges of a parcel polygon (§6).
    Classifications: FRONT, REAR, LEFT_SIDE, RIGHT_SIDE, or REQUIRES_REVIEW.
    """
    n = len(polygon_coords_secs)
    if n > 0 and polygon_coords_secs[0] == polygon_coords_secs[-1]:
        coords = polygon_coords_secs[:-1]
    else:
        coords = polygon_coords_secs

    num_vertices = len(coords)
    classified: List[ClassifiedEdge] = []
    if num_vertices < 3:
        return classified

    # Calculate centroid
    cx = sum(p[0] for p in coords) / num_vertices
    cy = sum(p[1] for p in coords) / num_vertices

    # Determine front edge: default to edge 0 if unspecified
    front_indices = set(road_frontage_edge_indices if road_frontage_edge_indices else [0])

    for i in range(num_vertices):
        p1 = coords[i]
        p2 = coords[(i + 1) % num_vertices]
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        length = math.sqrt(dx**2 + dy**2)
        bearing = (math.degrees(math.atan2(dx, dy)) + 360.0) % 360.0

        is_front = i in front_indices
        edge_id = f"EDGE-{i+1:03d}"

        if is_front:
            cls = EdgeClassification.FRONT
            rw = primary_road_width_m
        elif (i - list(front_indices)[0]) % num_vertices == 2:
            cls = EdgeClassification.REAR
            rw = None
        elif (i - list(front_indices)[0]) % num_vertices == 1:
            cls = EdgeClassification.RIGHT_SIDE
            rw = None
        elif (i - list(front_indices)[0]) % num_vertices == num_vertices - 1:
            cls = EdgeClassification.LEFT_SIDE
            rw = None
        else:
            cls = EdgeClassification.SIDE_1
            rw = None

        classified.append(ClassifiedEdge(
            edgeId=edge_id,
            startIndex=i,
            endIndex=(i + 1) % num_vertices,
            startCoordSECS=p1,
            endCoordSECS=p2,
            lengthM=round(length, 3),
            bearingDeg=round(bearing, 2),
            classification=cls,
            adjacentRoadWidthM=rw,
            isRoadFrontage=is_front
        ))

    return classified


def deduct_road_widening(
    parcel_poly_secs: Polygon,
    classified_edges: List[ClassifiedEdge],
    existing_road_width_m: float,
    proposed_road_width_m: float,
    rule_pack: RulePack,
    traces: List[RuleExecutionTrace]
) -> Tuple[Polygon, float, List[List[float]]]:
    """
    Explicitly computes and deducts the statutory road widening strip (§6).
    Subtracts widening buffer along FRONT edge(s) from parcel geometry.
    """
    gross_area = float(parcel_poly_secs.area)
    widening_delta = max(0.0, (proposed_road_width_m - existing_road_width_m) / 2.0)
    
    front_edges = [e for e in classified_edges if e.classification == EdgeClassification.FRONT]
    if widening_delta <= 0.0 or not front_edges:
        # Zero widening
        traces.append(RuleExecutionTrace(
            traceId=f"TRC-RW-{len(traces)+1:03d}",
            rulePackId=rule_pack.rulePackId,
            ruleId="ROAD-WIDENING-001",
            ruleVersion=rule_pack.version,
            category=RuleCategory.ROAD_WIDENING,
            ruleName="Road Widening Exemption / Zero Delta",
            citation="DCPR 2034 Reg 14 / Master Plan Access",
            inputs={"existingRoadWidthM": existing_road_width_m, "proposedRoadWidthM": proposed_road_width_m},
            calculationFormula="wideningDelta = max(0, (proposedRoadWidth - existingRoadWidth)/2) = 0.0m",
            outputs={"wideningDeductionAreaSqm": 0.0, "wideningDepthM": 0.0},
            status=RuleStatus.CALCULATED,
            explanation=f"Existing road width ({existing_road_width_m}m) matches or exceeds proposed road width ({proposed_road_width_m}m). No land surrender required."
        ))
        return parcel_poly_secs, 0.0, []

    # Construct frontage linestring in SECS
    front_lines = []
    total_frontage_len = 0.0
    for fe in front_edges:
        ls = LineString([fe.startCoordSECS, fe.endCoordSECS])
        front_lines.append(ls)
        total_frontage_len += fe.lengthM

    # Buffer frontage line into parcel to form widening cut polygon
    from shapely.ops import unary_union
    front_union = unary_union(front_lines)
    widening_strip = front_union.buffer(widening_delta, cap_style=2, join_style=2)

    # Intersect with parcel to get exact deducted area
    actual_deduction_geom = parcel_poly_secs.intersection(widening_strip)
    deducted_area = float(round(actual_deduction_geom.area, 2))

    # Subtract widening from parcel
    remaining_parcel = parcel_poly_secs.difference(widening_strip)
    if remaining_parcel.is_empty or not remaining_parcel.is_valid:
        remaining_parcel = parcel_poly_secs.buffer(-0.1)

    widening_coords = []
    if hasattr(actual_deduction_geom, "exterior"):
        widening_coords = [list(pt) for pt in actual_deduction_geom.exterior.coords]

    traces.append(RuleExecutionTrace(
        traceId=f"TRC-RW-{len(traces)+1:03d}",
        rulePackId=rule_pack.rulePackId,
        ruleId="ROAD-WIDENING-001",
        ruleVersion=rule_pack.version,
        category=RuleCategory.ROAD_WIDENING,
        ruleName="Statutory Master Plan Road Widening Line Surrender",
        citation="DCPR 2034 Reg 14 / KTCP Act Sec 14B",
        inputs={
            "existingRoadWidthM": existing_road_width_m,
            "proposedRoadWidthM": proposed_road_width_m,
            "wideningDepthM": widening_delta,
            "frontageLengthM": round(total_frontage_len, 2),
            "grossParcelAreaSqm": round(gross_area, 2)
        },
        calculationFormula=f"wideningDepth = ({proposed_road_width_m} - {existing_road_width_m}) / 2 = {widening_delta}m along {round(total_frontage_len, 2)}m frontage",
        outputs={
            "wideningDeductionAreaSqm": deducted_area,
            "remainingParcelAreaSqm": round(remaining_parcel.area, 2)
        },
        status=RuleStatus.CALCULATED,
        explanation=f"Deducted {deducted_area} m² along {round(total_frontage_len, 2)}m road frontage for proposed {proposed_road_width_m}m master plan road widening (surrender depth {widening_delta}m)."
    ))

    return remaining_parcel, deducted_area, widening_coords


def compute_directional_setbacks(
    net_parcel_poly_secs: Polygon,
    classified_edges: List[ClassifiedEdge],
    road_width_m: float,
    rule_pack: RulePack,
    traces: List[RuleExecutionTrace]
) -> Tuple[Polygon, Dict[str, float]]:
    """
    Computes directional building setback insets: FRONT, REAR, SIDES (§6).
    Produces the authoritative buildable envelope polygon in SECS.
    """
    parcel_area = float(net_parcel_poly_secs.area)

    # 1. Lookup rule pack setback standards
    front_setback_m = 4.5
    rear_setback_m = 3.0
    side_setback_m = 1.5

    if "BBMP" in rule_pack.rulePackId.upper():
        # BBMP Schedule II Table 3: Area-graduated
        if parcel_area <= 120.0:
            front_setback_m, rear_setback_m, side_setback_m = 1.5, 1.0, 0.0
        elif parcel_area <= 240.0:
            front_setback_m, rear_setback_m, side_setback_m = 2.0, 1.5, 1.0
        elif parcel_area <= 500.0:
            front_setback_m, rear_setback_m, side_setback_m = 3.0, 2.0, 1.5
        elif parcel_area <= 1000.0:
            front_setback_m, rear_setback_m, side_setback_m = 4.5, 3.0, 2.5
        else:
            front_setback_m, rear_setback_m, side_setback_m = 6.0, 4.0, 3.0
    else:
        # Mumbai DCPR 2034 Reg 41 & 43: Road-width graduated
        if road_width_m < 9.0:
            front_setback_m = 3.0
        elif road_width_m < 12.0:
            front_setback_m = 4.5
        elif road_width_m < 18.0:
            front_setback_m = 6.0
        elif road_width_m < 27.0:
            front_setback_m = 7.5
        else:
            front_setback_m = 9.0
        rear_setback_m = 3.0
        side_setback_m = 1.5

    # Geometric setback inset:
    # Buffer each edge inward according to its specific classification
    # For a robust polygon inset, we compute directional edge buffers
    front_lines = [LineString([e.startCoordSECS, e.endCoordSECS]) for e in classified_edges if e.classification == EdgeClassification.FRONT]
    rear_lines = [LineString([e.startCoordSECS, e.endCoordSECS]) for e in classified_edges if e.classification == EdgeClassification.REAR]
    side_lines = [LineString([e.startCoordSECS, e.endCoordSECS]) for e in classified_edges if e.classification in [EdgeClassification.LEFT_SIDE, EdgeClassification.RIGHT_SIDE, EdgeClassification.SIDE_1, EdgeClassification.SIDE_2]]

    envelope = net_parcel_poly_secs
    from shapely.ops import unary_union

    if front_lines:
        f_strip = unary_union(front_lines).buffer(front_setback_m, cap_style=2, join_style=2)
        envelope = envelope.difference(f_strip)
    if rear_lines:
        r_strip = unary_union(rear_lines).buffer(rear_setback_m, cap_style=2, join_style=2)
        envelope = envelope.difference(r_strip)
    if side_lines and side_setback_m > 0:
        s_strip = unary_union(side_lines).buffer(side_setback_m, cap_style=2, join_style=2)
        envelope = envelope.difference(s_strip)

    # In case difference produces degenerate or empty polygon, fallback to safe proportional inward buffer
    if envelope.is_empty or envelope.area < 10.0:
        avg_setback = (front_setback_m + rear_setback_m + side_setback_m * 2) / 4.0
        envelope = net_parcel_poly_secs.buffer(-avg_setback)
        if envelope.is_empty:
            envelope = net_parcel_poly_secs.buffer(-1.0)

    envelope_area = float(round(envelope.area, 2))
    total_setback_deduction = float(round(parcel_area - envelope_area, 2))

    # Apportion approximate setback areas for explainability
    f_area_approx = round(total_setback_deduction * 0.45, 2)
    r_area_approx = round(total_setback_deduction * 0.30, 2)
    s_area_approx = round(total_setback_deduction * 0.25, 2)

    # Record Front Setback Trace
    traces.append(RuleExecutionTrace(
        traceId=f"TRC-SETBACK-F-{len(traces)+1:03d}",
        rulePackId=rule_pack.rulePackId,
        ruleId="SETBACK-FRONT-001",
        ruleVersion=rule_pack.version,
        category=RuleCategory.SETBACK,
        ruleName="Mandatory Front Marginal Open Space",
        citation="DCPR 2034 Reg 41 Table 18 / BBMP Table 3",
        inputs={"effectiveRoadWidthM": road_width_m, "plotAreaSqm": parcel_area},
        calculationFormula=f"FrontSetback = {front_setback_m}m",
        outputs={"requiredFrontSetbackM": front_setback_m, "approximateAreaDeductionSqm": f_area_approx},
        status=RuleStatus.CALCULATED,
        explanation=f"Front setback of {front_setback_m}m required based on access road width of {road_width_m}m."
    ))

    # Record Rear Setback Trace
    traces.append(RuleExecutionTrace(
        traceId=f"TRC-SETBACK-R-{len(traces)+1:03d}",
        rulePackId=rule_pack.rulePackId,
        ruleId="SETBACK-REAR-001",
        ruleVersion=rule_pack.version,
        category=RuleCategory.SETBACK,
        ruleName="Mandatory Rear Marginal Open Space",
        citation="DCPR 2034 Reg 43 / BBMP Table 3",
        inputs={"plotAreaSqm": parcel_area},
        calculationFormula=f"RearSetback = {rear_setback_m}m",
        outputs={"requiredRearSetbackM": rear_setback_m, "approximateAreaDeductionSqm": r_area_approx},
        status=RuleStatus.CALCULATED,
        explanation=f"Rear setback of {rear_setback_m}m required for light, ventilation, and fire separation."
    ))

    # Record Side Setback Trace
    traces.append(RuleExecutionTrace(
        traceId=f"TRC-SETBACK-S-{len(traces)+1:03d}",
        rulePackId=rule_pack.rulePackId,
        ruleId="SETBACK-SIDE-001",
        ruleVersion=rule_pack.version,
        category=RuleCategory.SETBACK,
        ruleName="Mandatory Lateral Side Marginal Open Spaces",
        citation="DCPR 2034 Reg 43 / BBMP Table 3",
        inputs={"plotAreaSqm": parcel_area},
        calculationFormula=f"SideSetback = {side_setback_m}m",
        outputs={"requiredSideSetbackM": side_setback_m, "approximateAreaDeductionSqm": s_area_approx},
        status=RuleStatus.CALCULATED,
        explanation=f"Side setbacks of {side_setback_m}m each required along property boundaries."
    ))

    return envelope, {
        "frontSetbackM": front_setback_m,
        "rearSetbackM": rear_setback_m,
        "sideSetbackM": side_setback_m,
        "frontDeductionSqm": f_area_approx,
        "rearDeductionSqm": r_area_approx,
        "sideDeductionSqm": s_area_approx,
        "envelopeAreaSqm": envelope_area
    }


def evaluate_fsi_and_massing(
    net_developable_area_sqm: float,
    effective_road_width_m: float,
    rule_pack: RulePack,
    candidate_footprint_sqm: Optional[float] = None,
    candidate_height_m: Optional[float] = None,
    traces: Optional[List[RuleExecutionTrace]] = None
) -> Dict[str, Any]:
    """
    Evaluates FSI/FAR, Ground Coverage limits, Height Caps, and Parking Quotas (§6).
    Produces complete RuleExecutionTrace records.
    """
    if traces is None:
        traces = []

    # 1. FSI / FAR Calculation
    if "BBMP" in rule_pack.rulePackId.upper():
        if effective_road_width_m <= 9.0:
            base_fsi = 1.50
            premium_fsi = 0.0
            tdr_fsi = 0.0
            max_height_m = 11.5
        elif effective_road_width_m <= 12.0:
            base_fsi = 1.75
            premium_fsi = 0.40
            tdr_fsi = 0.0
            max_height_m = 15.0
        elif effective_road_width_m <= 15.0:
            base_fsi = 2.00
            premium_fsi = 0.50
            tdr_fsi = 0.0
            max_height_m = 24.0
        else:
            base_fsi = 2.25
            premium_fsi = 0.60
            tdr_fsi = 0.0
            max_height_m = 30.0
    else:
        # Mumbai DCPR 2034
        base_fsi = 1.0
        if effective_road_width_m < 9.0:
            premium_fsi = 0.0
            tdr_fsi = 0.0
            max_height_m = 16.0
        elif effective_road_width_m < 12.0:
            premium_fsi = 0.50
            tdr_fsi = 0.50
            max_height_m = 32.0
        elif effective_road_width_m < 18.0:
            premium_fsi = 0.50
            tdr_fsi = 0.75
            max_height_m = 50.0
        elif effective_road_width_m < 27.0:
            premium_fsi = 0.50
            tdr_fsi = 1.00
            max_height_m = 70.0
        else:
            premium_fsi = 0.50
            tdr_fsi = 1.25
            max_height_m = 120.0

    total_fsi = round(base_fsi + premium_fsi + tdr_fsi, 3)
    permissible_bua_sqm = round(net_developable_area_sqm * total_fsi, 2)
    carpet_area_sqm = round(permissible_bua_sqm * 0.70, 2)

    # Trace FSI
    traces.append(RuleExecutionTrace(
        traceId=f"TRC-FSI-{len(traces)+1:03d}",
        rulePackId=rule_pack.rulePackId,
        ruleId="FSI-EVAL-001",
        ruleVersion=rule_pack.version,
        category=RuleCategory.FSI,
        ruleName="Statutory Floor Space Index Determination",
        citation="DCPR 2034 Reg 30/33 / BBMP Bye-Law 6.2",
        inputs={"effectiveRoadWidthM": effective_road_width_m, "netParcelAreaSqm": net_developable_area_sqm},
        calculationFormula=f"TotalFSI = {base_fsi} (Base) + {premium_fsi} (Premium) + {tdr_fsi} (TDR) = {total_fsi}",
        outputs={
            "baseFSI": base_fsi,
            "premiumFSI": premium_fsi,
            "tdrFSI": tdr_fsi,
            "totalPermissibleFSI": total_fsi,
            "permissibleBUASqm": permissible_bua_sqm,
            "carpetAreaSqm": carpet_area_sqm
        },
        status=RuleStatus.CALCULATED,
        explanation=f"Access road of {effective_road_width_m}m qualifies for base FSI {base_fsi}, premium FSI {premium_fsi}, and TDR allowance {tdr_fsi}, yielding total FSI {total_fsi}."
    ))

    # 2. Maximum Ground Coverage
    coverage_pct = 50.0
    if "BBMP" in rule_pack.rulePackId.upper():
        coverage_pct = 75.0 if net_developable_area_sqm <= 120 else (65.0 if net_developable_area_sqm <= 240 else 60.0)
    max_coverage_sqm = round(net_developable_area_sqm * (coverage_pct / 100.0), 2)

    footprint_status = "PASS"
    if candidate_footprint_sqm and candidate_footprint_sqm > max_coverage_sqm:
        footprint_status = "BLOCKED"

    traces.append(RuleExecutionTrace(
        traceId=f"TRC-COV-{len(traces)+1:03d}",
        rulePackId=rule_pack.rulePackId,
        ruleId="COVERAGE-001",
        ruleVersion=rule_pack.version,
        category=RuleCategory.GROUND_COVERAGE,
        ruleName="Maximum Ground Coverage Limitation",
        citation="DCPR 2034 Reg 31 / BBMP Table 2",
        inputs={"netParcelAreaSqm": net_developable_area_sqm, "maxCoveragePercent": coverage_pct},
        calculationFormula=f"maxCoverage = {net_developable_area_sqm} * {coverage_pct}% = {max_coverage_sqm} m²",
        outputs={"maxCoveragePercent": coverage_pct, "maxCoverageAreaSqm": max_coverage_sqm, "status": footprint_status},
        status=RuleStatus.CALCULATED,
        explanation=f"Maximum building footprint coverage is capped at {coverage_pct}% ({max_coverage_sqm} m²) to preserve percolation and statutory light."
    ))

    # 3. Maximum Building Height
    height_status = "PASS"
    if candidate_height_m and candidate_height_m > max_height_m:
        height_status = "BLOCKED"

    traces.append(RuleExecutionTrace(
        traceId=f"TRC-HT-{len(traces)+1:03d}",
        rulePackId=rule_pack.rulePackId,
        ruleId="HEIGHT-001",
        ruleVersion=rule_pack.version,
        category=RuleCategory.HEIGHT,
        ruleName="Maximum Permissible Building Height Cap",
        citation="DCPR 2034 Reg 30 Table 12 / BBMP Bye-Law 6.2",
        inputs={"effectiveRoadWidthM": effective_road_width_m},
        calculationFormula=f"MaxHeight = {max_height_m}m",
        outputs={"maxPermissibleHeightM": max_height_m, "status": height_status},
        status=RuleStatus.CALCULATED,
        explanation=f"Building height capped at {max_height_m}m corresponding to access road width of {effective_road_width_m}m."
    ))

    # 4. Mandatory Parking Standards
    stalls = max(2, int(carpet_area_sqm / 70.0))
    accessible = max(1, int(stalls * 0.04))

    traces.append(RuleExecutionTrace(
        traceId=f"TRC-PRK-{len(traces)+1:03d}",
        rulePackId=rule_pack.rulePackId,
        ruleId="PARKING-001",
        ruleVersion=rule_pack.version,
        category=RuleCategory.PARKING,
        ruleName="Off-Street Vehicular Parking Quota",
        citation="DCPR 2034 Reg 44 Table 21 / BBMP Table 8",
        inputs={"carpetAreaSqm": carpet_area_sqm, "ratio": "1 stall per 70 sqm carpet"},
        calculationFormula=f"Stalls = ceil({carpet_area_sqm} / 70) = {stalls}",
        outputs={"standardStalls": stalls, "accessibleStalls": accessible},
        status=RuleStatus.CALCULATED,
        explanation=f"Mandatory requirement of {stalls} vehicular parking stalls (including {accessible} accessible stall) calculated for {carpet_area_sqm} m² carpet area."
    ))

    return {
        "baseFSI": base_fsi,
        "premiumFSI": premium_fsi,
        "tdrFSI": tdr_fsi,
        "totalPermissibleFSI": total_fsi,
        "permissibleBUASqm": permissible_bua_sqm,
        "carpetAreaSqm": carpet_area_sqm,
        "maxGroundCoveragePercent": coverage_pct,
        "maxGroundCoverageAreaSqm": max_coverage_sqm,
        "maxBuildingHeightM": max_height_m,
        "parkingStalls": stalls,
        "accessibleParkingStalls": accessible
    }


def execute_statutory_feasibility_pipeline(
    coordinates_wgs84: List[List[float]],
    existing_road_width_m: float = 12.0,
    proposed_road_width_m: float = 18.0,
    rule_pack_id: str = "MUMBAI-DCPR-2034-V1",
    ref_frame: Optional[SiteReferenceFrame] = None,
    site_id: str = "site-001"
) -> Tuple[FeasibilityExplainabilityBreakdown, Dict[str, Any]]:
    """
    Executes the complete end-to-end statutory feasibility pipeline (§6, §7).
    Returns the full explainability breakdown and geometry payloads.
    """
    rule_pack = load_rule_pack(rule_pack_id)
    traces: List[RuleExecutionTrace] = []

    # 1. Establish Topocentric Reference Frame (SECS)
    if ref_frame is None:
        origin_lat = coordinates_wgs84[0][1]
        origin_lon = coordinates_wgs84[0][0]
        ref_frame = SiteReferenceFrame(
            referenceFrameId=f"RF-{site_id[:8]}",
            siteId=site_id,
            originLatitude=origin_lat,
            originLongitude=origin_lon,
            originElevationM=10.0
        )

    # 2. Transform WGS84 coordinates to local SECS [East, North]
    secs_coords = polygon_wgs84_to_secs(coordinates_wgs84, ref_frame)
    if len(secs_coords) > 0 and secs_coords[0] != secs_coords[-1]:
        secs_coords.append(secs_coords[0])

    parcel_poly_secs = Polygon(secs_coords)
    if not parcel_poly_secs.is_valid:
        parcel_poly_secs = parcel_poly_secs.buffer(0)

    gross_area_sqm = float(round(parcel_poly_secs.area, 2))

    # 3. Classify Boundary Edges
    classified_edges = classify_parcel_edges(secs_coords, primary_road_width_m=existing_road_width_m)

    # 4. Explicit Road Widening Deduction
    remaining_poly, widening_sqm, widening_poly_secs = deduct_road_widening(
        parcel_poly_secs=parcel_poly_secs,
        classified_edges=classified_edges,
        existing_road_width_m=existing_road_width_m,
        proposed_road_width_m=proposed_road_width_m,
        rule_pack=rule_pack,
        traces=traces
    )

    # 5. Amenity / Open Space Reservation
    amenity_pct = 0.0
    if gross_area_sqm >= 10000.0:
        amenity_pct = 15.0
    elif gross_area_sqm >= 4000.0:
        amenity_pct = 10.0
    elif gross_area_sqm >= 2000.0:
        amenity_pct = 5.0

    amenity_reservation_sqm = float(round((remaining_poly.area) * (amenity_pct / 100.0), 2))
    net_developable_sqm = float(round(remaining_poly.area - amenity_reservation_sqm, 2))

    if amenity_pct > 0.0:
        traces.append(RuleExecutionTrace(
            traceId=f"TRC-AMENITY-{len(traces)+1:03d}",
            rulePackId=rule_pack.rulePackId,
            ruleId="OPEN-SPACE-001",
            ruleVersion=rule_pack.version,
            category=RuleCategory.OPEN_SPACE,
            ruleName="Public Open Space / Layout Amenity Reservation",
            citation="DCPR 2034 Reg 27 Table 8",
            inputs={"grossPlotAreaSqm": gross_area_sqm, "reservationTierPercent": amenity_pct},
            calculationFormula=f"amenityArea = {round(remaining_poly.area, 2)} * {amenity_pct}% = {amenity_reservation_sqm} m²",
            outputs={"amenityReservationPercent": amenity_pct, "amenityReservationSqm": amenity_reservation_sqm},
            status=RuleStatus.CALCULATED,
            explanation=f"Plots exceeding {2000 if gross_area_sqm < 4000 else (4000 if gross_area_sqm < 10000 else 10000)} m² require a mandatory {amenity_pct}% layout open space reservation."
        ))

    # 6. Directional Setbacks & Buildable Envelope
    envelope_poly_secs, setback_metrics = compute_directional_setbacks(
        net_parcel_poly_secs=remaining_poly,
        classified_edges=classified_edges,
        road_width_m=proposed_road_width_m,
        rule_pack=rule_pack,
        traces=traces
    )

    # 7. Massing, FSI, Ground Coverage, Height & Parking
    massing = evaluate_fsi_and_massing(
        net_developable_area_sqm=net_developable_sqm,
        effective_road_width_m=proposed_road_width_m,
        rule_pack=rule_pack,
        candidate_footprint_sqm=envelope_poly_secs.area,
        candidate_height_m=7.2,
        traces=traces
    )

    # Effective permitted footprint is the minimum of setback envelope and ground coverage cap (§7)
    effective_footprint_sqm = round(min(envelope_poly_secs.area, massing["maxGroundCoverageAreaSqm"]), 2)

    # 8. Transform buildable envelope coordinates back to WGS84 for Mapbox display
    buildable_secs_coords = [list(pt) for pt in envelope_poly_secs.exterior.coords] if hasattr(envelope_poly_secs, "exterior") else secs_coords
    buildable_wgs84 = polygon_secs_to_wgs84(buildable_secs_coords, ref_frame)

    explainability = FeasibilityExplainabilityBreakdown(
        grossParcelAreaSqm=gross_area_sqm,
        roadWideningDeductionSqm=widening_sqm,
        amenityReservationSqm=amenity_reservation_sqm,
        netParcelAreaSqm=net_developable_sqm,
        frontSetbackDeductionSqm=setback_metrics["frontDeductionSqm"],
        rearSetbackDeductionSqm=setback_metrics["rearDeductionSqm"],
        sideSetbacksDeductionSqm=setback_metrics["sideDeductionSqm"],
        rawSetbackEnvelopeAreaSqm=setback_metrics["envelopeAreaSqm"],
        maxGroundCoveragePercent=massing["maxGroundCoveragePercent"],
        maxGroundCoverageAreaSqm=massing["maxGroundCoverageAreaSqm"],
        effectivePermittedFootprintSqm=effective_footprint_sqm,
        baseFSI=massing["baseFSI"],
        premiumFSI=massing["premiumFSI"],
        tdrFSI=massing["tdrFSI"],
        totalPermissibleFSI=massing["totalPermissibleFSI"],
        permissibleBUASqm=massing["permissibleBUASqm"],
        carpetAreaSqm=massing["carpetAreaSqm"],
        maxBuildingHeightM=massing["maxBuildingHeightM"],
        parkingStallsRequired=massing["parkingStalls"],
        rulePackId=rule_pack.rulePackId,
        rulePackVersion=rule_pack.version,
        traces=traces
    )

    geometry_payload = {
        "referenceFrame": ref_frame.dict(),
        "classifiedEdges": [e.dict() for e in classified_edges],
        "buildableCoordinatesSECS": buildable_secs_coords,
        "buildableCoordinatesWGS84": buildable_wgs84,
        "wideningCoordinatesSECS": widening_poly_secs
    }

    return explainability, geometry_payload
