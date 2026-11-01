# Volume VIII — Land, GIS, and Statutory Feasibility

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

```

---

## 3. Municipal Rule Packs (Mumbai DCPR 2034 & BBMP 2026)
Planwise packages declarative JSON rule definitions:
- **Mumbai DCPR 2034:** `packages/rules/mumbai_dcpr_2034_v1.json` (Regulation 43 Marginal Open Spaces, Table 12, FSI 1.50).
- **BBMP Bengaluru 2026:** `packages/rules/bbmp_bengaluru_2026.json` (Table 7 Setbacks, FAR 1.25 to 1.75).
