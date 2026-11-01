"""
Authoritative Statutory Building Envelope Engine.
Replaces area-only calculations with Shapely geometric polygon clipping:
- Accepts plot polygon or dimensions (in meters or feet)
- Resolves jurisdiction rule pack (MCGM Mumbai DCPR 2034, BBMP Bengaluru 2026)
- Computes buildable polygon = plot minus statutory setbacks
- Enforces statutory ground coverage cap from jurisdiction rule pack
- Rejects unknown jurisdictions with structured UNVERIFIED / 422 error
"""

import json
import math
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, Union, List
from shapely.geometry import Polygon, box, mapping
import shapely.affinity

RULES_DIR = Path(__file__).resolve().parent.parent.parent / "packages" / "rules"


class UnknownJurisdictionError(Exception):
    """Raised when no verified statutory rule pack exists for the requested jurisdiction."""
    def __init__(self, jurisdiction: str):
        self.jurisdiction = jurisdiction
        self.detail = {
            "status": "UNVERIFIED",
            "jurisdiction": jurisdiction,
            "verified": False,
            "message": f"Statutory rule pack for jurisdiction '{jurisdiction}' is not verified or supported. Manual municipal scrutiny required."
        }
        super().__init__(self.detail["message"])


RULE_PACK_FILE_MAP = {
    "MUMBAI_DCPR_2034": "mumbai_dcpr_2034_v1.json",
    "MUMBAI_DCPR_2034_V1": "mumbai_dcpr_2034_v1.json",
    "MUMBAI-DCPR-2034-V1": "mumbai_dcpr_2034_v1.json",
    "MCGM": "mumbai_dcpr_2034_v1.json",
    "BBMP_BENGALURU_2026": "bbmp_bengaluru_2026.json",
    "BBMP_BENGALURU_2026_V1": "bbmp_bengaluru_2026.json",
    "BBMP-RES-2026-01": "bbmp_bengaluru_2026.json",
    "BBMP": "bbmp_bengaluru_2026.json"
}


def load_jurisdiction_rules(jurisdiction: str) -> Dict[str, Any]:
    """Loads declarative rules for jurisdiction or raises UnknownJurisdictionError."""
    norm_id = (jurisdiction or "").strip().upper().replace(" ", "_").replace("-", "_")
    matched_file = None
    for k, v in RULE_PACK_FILE_MAP.items():
        if k.replace("-", "_") == norm_id:
            matched_file = v
            break

    if not matched_file:
        raise UnknownJurisdictionError(jurisdiction)

    file_path = RULES_DIR / matched_file
    if not file_path.exists():
        raise UnknownJurisdictionError(jurisdiction)

    with open(file_path, "r") as f:
        return json.load(f)


def extract_statutory_parameters(
    rule_data: Dict[str, Any],
    plot_area_sqm: float,
    road_width_m: float = 9.0
) -> Tuple[float, float, float, float]:
    """
    Extracts front, rear, side setbacks and max ground coverage percent from rule pack.
    Returns: (front_setback_m, rear_setback_m, side_setback_m, max_coverage_percent)
    """
    front_setback = 3.0
    rear_setback = 2.0
    side_setback = 1.5
    max_coverage_pct = 50.0

    rules = rule_data.get("rules", [])
    for r in rules:
        cat = r.get("category", "")
        params = r.get("parameters", {})

        if cat == "GROUND_COVERAGE":
            if "maxGroundCoveragePercent" in params:
                max_coverage_pct = float(params["maxGroundCoveragePercent"])
            elif "tiers" in params:
                for tier in params["tiers"]:
                    if plot_area_sqm <= tier.get("maxPlotAreaSqm", 999999.0):
                        max_coverage_pct = float(tier.get("coveragePercent", 50.0))
                        break

        elif cat == "SETBACK":
            if "frontSetbacks" in params:
                for fs in params["frontSetbacks"]:
                    if road_width_m <= fs.get("maxRoadWidthM", 999.0):
                        front_setback = float(fs.get("frontSetbackM", 3.0))
                        break
                rear_setback = float(params.get("rearSetbackM", 2.0))
                side_setback = float(params.get("sideSetbackM", 1.5))
            elif "tiers" in params:
                for tier in params["tiers"]:
                    if plot_area_sqm <= tier.get("maxPlotAreaSqm", 999999.0):
                        front_setback = float(tier.get("frontSetbackM", 1.5))
                        rear_setback = float(tier.get("rearSetbackM", 1.0))
                        side_setback = float(tier.get("sideSetbackM", 1.0))
                        break

    return front_setback, rear_setback, side_setback, max_coverage_pct


def compute_statutory_envelope(
    plot_input: Union[Polygon, Dict[str, float], Tuple[float, float], List[List[float]]],
    jurisdiction: str = "MUMBAI_DCPR_2034_V1",
    road_width_m: float = 9.0
) -> Dict[str, Any]:
    """
    Computes buildable polygon = plot minus setbacks, capped by statutory coverage.
    
    Args:
        plot_input: Shapely Polygon, or {"width_ft": 28, "length_ft": 46}, or (width_m, length_m),
                    or list of coordinate pairs [[x, y], ...].
        jurisdiction: Statutory rule pack identifier.
        road_width_m: Access road width in meters.
        
    Returns:
        Structured envelope dictionary with Shapely geometry, dimensions, coverage, and verification.
    """
    # 1. Resolve Jurisdiction Rules
    rule_data = load_jurisdiction_rules(jurisdiction)

    # 2. Reconstruct Plot Polygon
    if isinstance(plot_input, Polygon):
        plot_poly = plot_input
    elif isinstance(plot_input, dict):
        if "width_ft" in plot_input and "length_ft" in plot_input:
            w_m = float(plot_input["width_ft"]) * 0.3048
            l_m = float(plot_input["length_ft"]) * 0.3048
        elif "width_m" in plot_input and "length_m" in plot_input:
            w_m = float(plot_input["width_m"])
            l_m = float(plot_input["length_m"])
        elif "declaredPlotAreaSqFt" in plot_input:
            sqft = float(plot_input["declaredPlotAreaSqFt"])
            sqm = sqft * 0.092903
            w_m = round(math.sqrt(sqm / 1.45), 2)
            l_m = round(sqm / w_m, 2)
        else:
            raise ValueError(f"Invalid plot input dict: {plot_input}")
        plot_poly = box(0.0, 0.0, w_m, l_m)
    elif isinstance(plot_input, (tuple, list)):
        if len(plot_input) == 2 and isinstance(plot_input[0], (int, float)):
            w_m = float(plot_input[0])
            l_m = float(plot_input[1])
            plot_poly = box(0.0, 0.0, w_m, l_m)
        else:
            plot_poly = Polygon(plot_input)
    else:
        raise ValueError(f"Unsupported plot input type: {type(plot_input)}")

    if not plot_poly.is_valid:
        plot_poly = plot_poly.buffer(0)

    plot_area_sqm = float(plot_poly.area)

    # 3. Extract Statutory Setbacks & Coverage Limit
    front_sb, rear_sb, side_sb, max_cov_pct = extract_statutory_parameters(
        rule_data, plot_area_sqm, road_width_m=road_width_m
    )

    # 4. Compute Plot Minus Setbacks
    minx, miny, maxx, maxy = plot_poly.bounds
    plot_width = maxx - minx
    plot_length = maxy - miny

    buildable_minx = minx + side_sb
    buildable_maxx = maxx - side_sb
    buildable_miny = miny + front_sb
    buildable_maxy = maxy - rear_sb

    if buildable_maxx <= buildable_minx or buildable_maxy <= buildable_miny:
        # Plot too narrow or short for standard setbacks — fallback inward buffer
        plot_minus_setbacks = plot_poly.buffer(-min(side_sb, front_sb, rear_sb))
    else:
        setback_box = box(buildable_minx, buildable_miny, buildable_maxx, buildable_maxy)
        plot_minus_setbacks = plot_poly.intersection(setback_box)

    if plot_minus_setbacks.is_empty or not plot_minus_setbacks.is_valid:
        raise ValueError("Buildable area is empty after applying statutory setbacks.")

    # 5. Cap Coverage from Jurisdiction Rule Pack
    max_coverage_sqm = plot_area_sqm * (max_cov_pct / 100.0)
    buildable_area = float(plot_minus_setbacks.area)

    if buildable_area > max_coverage_sqm:
        scale_factor = math.sqrt(max_coverage_sqm / buildable_area)
        envelope_poly = shapely.affinity.scale(
            plot_minus_setbacks,
            xfact=scale_factor,
            yfact=scale_factor,
            origin="center"
        )
    else:
        envelope_poly = plot_minus_setbacks

    env_minx, env_miny, env_maxx, env_maxy = envelope_poly.bounds
    envelope_width = round(env_maxx - env_minx, 2)
    envelope_length = round(env_maxy - env_miny, 2)
    envelope_area = float(envelope_poly.area)

    # Verify containment inside plot minus setbacks
    is_inside = plot_minus_setbacks.buffer(1e-5).contains(envelope_poly)

    # Check if rule pack has licensed professional statutory certification
    is_rule_pack_certified = bool(rule_data.get("isStatutoryCertified", False) or rule_data.get("legallyVerified", False))
    verification_status = "VERIFIED" if is_rule_pack_certified else "RULES_UNVERIFIED"

    return {
        "status": verification_status,
        "verificationStatus": verification_status,
        "jurisdiction": jurisdiction,
        "rulePackId": rule_data.get("rulePackId", jurisdiction),
        "plotAreaSqm": round(plot_area_sqm, 2),
        "setbacks": {
            "frontM": front_sb,
            "rearM": rear_sb,
            "sideM": side_sb
        },
        "maxGroundCoveragePercent": max_cov_pct,
        "maxPermissibleFootprintSqm": round(max_coverage_sqm, 2),
        "envelopeWidthM": envelope_width,
        "envelopeLengthM": envelope_length,
        "footprintAreaSqm": round(envelope_area, 2),
        "actualCoveragePercent": round((envelope_area / plot_area_sqm) * 100.0, 2),
        "isFullyInsidePlotMinusSetbacks": is_inside,
        "plotCoordinates": [list(pt) for pt in plot_poly.exterior.coords],
        "buildableCoordinates": [list(pt) for pt in envelope_poly.exterior.coords]
    }
