"""
Regulation Engine Evaluator
Declarative AST/Table evaluator for Mumbai DCPR 2034 rules,
computing statutory FSI, TDR allowances, height caps, and parking quotas.
"""

from typing import Dict, Any


def evaluate_mumbai_dcpr_2034(
    net_developable_area_sqm: float,
    effective_road_width_m: float = 18.0,
    zoning: str = "R2_RESIDENTIAL"
) -> Dict[str, Any]:
    """
    Evaluates Mumbai DCPR 2034 Regulation 30 & 33 for Residential/Commercial development.
    """
    base_fsi = 1.0

    # Road width tiers per DCPR 2034 Reg 30 Table 12
    if effective_road_width_m < 9.0:
        premium_fsi = 0.0
        tdr_fsi = 0.0
        max_height_m = 16.0
        front_setback_m = 3.0
    elif effective_road_width_m < 12.0:
        premium_fsi = 0.5
        tdr_fsi = 0.5
        max_height_m = 32.0
        front_setback_m = 4.5
    elif effective_road_width_m < 18.0:
        premium_fsi = 0.5
        tdr_fsi = 0.75
        max_height_m = 50.0
        front_setback_m = 6.0
    elif effective_road_width_m < 27.0:
        premium_fsi = 0.5
        tdr_fsi = 1.0
        max_height_m = 70.0
        front_setback_m = 7.5
    else:
        premium_fsi = 0.5
        tdr_fsi = 1.25
        max_height_m = 120.0
        front_setback_m = 9.0

    total_permissible_fsi = round(base_fsi + premium_fsi + tdr_fsi, 3)
    permissible_bua_sqm = round(net_developable_area_sqm * total_permissible_fsi, 2)

    # Approximate 70% carpet efficiency
    carpet_area_sqm = permissible_bua_sqm * 0.70

    # Parking Standards: 1 stall per 70 sqm residential carpet
    standard_parking_stalls = max(4, int(carpet_area_sqm / 70.0))
    accessible_parking_stalls = max(1, int(standard_parking_stalls * 0.04))

    return {
        "regulationVersionId": "MUMBAI_DCPR_2034_V1",
        "effectiveRoadWidthM": effective_road_width_m,
        "baseFSI": base_fsi,
        "premiumFSI": premium_fsi,
        "tdrFSI": tdr_fsi,
        "totalPermissibleFSI": total_permissible_fsi,
        "permissibleBUASqm": permissible_bua_sqm,
        "carpetAreaSqm": round(carpet_area_sqm, 2),
        "maxBuildingHeightM": max_height_m,
        "frontSetbackM": front_setback_m,
        "standardParkingStalls": standard_parking_stalls,
        "accessibleParkingStalls": accessible_parking_stalls
    }
