"""
Planwise Enterprise — Multi-Objective Pareto Filter
M2 Milestone — Phase 6

Computes transparent architectural objective vectors for each generated candidate:
- Usable Carpet Area (maximize)
- Room Efficiency / Circulation Waste (maximize)
- Daylight Proxy Score (maximize)
- Ventilation Proxy Score (maximize)
- Constructability Proxy Score (maximize)
- Customer Brief Fit Score (maximize)
- Wall & Plumbing Complexity (minimize)

Identifies non-dominated alternatives on the Pareto frontier and provides
deterministic trade-off explanations.
"""

from typing import List, Dict, Any, Tuple, Optional
import math
from pydantic import BaseModel, Field

from workers.generation.cpsat_solver import LayoutCandidate
from packages.schemas.customer_brief import CustomerBrief
from packages.schemas.room_program import RoomType


class CandidateObjectiveMetrics(BaseModel):
    """Normalized objective vector for a candidate layout."""
    usableCarpetAreaSqm: float = Field(..., description="Net carpet area inside rooms")
    totalBuiltAreaSqm: float = Field(..., description="Gross built-up area including walls")
    footprintAreaSqm: float = Field(..., description="Ground coverage footprint")
    circulationAreaSqm: float = Field(..., description="Corridor, stair, and circulation area")
    roomEfficiency: float = Field(..., description="Carpet-to-BUA efficiency percentage (0-100)")
    daylightProxyScore: float = Field(..., description="DAYLIGHT_PROXY: percentage of rooms with exterior perimeter exposure")
    ventilationProxyScore: float = Field(..., description="VENTILATION_PROXY: cross-ventilation potential score")
    constructabilityProxyScore: float = Field(..., description="CONSTRUCTABILITY_PROXY: structural grid regularity & wall alignment")
    customerFitScore: float = Field(..., description="Alignment with requested brief parameters (0-100)")
    parkingFitScore: float = Field(..., description="Parking accommodation compliance score")
    externalWallComplexity: float = Field(..., description="Perimeter-to-area ratio proxy (lower is more efficient)")
    wetAreaComplexity: float = Field(..., description="Plumbing stack dispersion penalty (lower is better)")
    overallWeightedScore: float = Field(..., description="Weighted composite score for ranking")


class ParetoFrontierReport(BaseModel):
    """Comprehensive Pareto frontier analysis across candidate options."""
    totalCandidatesEvaluated: int
    nonDominatedCandidatesCount: int
    paretoOptions: List[Dict[str, Any]]
    dominatedOptions: List[Dict[str, Any]]
    tradeoffSummary: List[str]


def evaluate_candidate_metrics(candidate: LayoutCandidate, brief: Optional[CustomerBrief] = None) -> CandidateObjectiveMetrics:
    """
    Deterministically computes objective metrics for a layout candidate.
    Labels all proxies explicitly per Delta Spec §7.3.
    """
    rooms = candidate.rooms
    total_carpet = sum(r.area_sqm for r in rooms)
    total_bua = candidate.metrics.get("totalBuiltUpAreaSqm", round(total_carpet * 1.15, 2))
    footprint = candidate.metrics.get("footprintSqm", round(total_carpet, 2))

    # Circulation area
    circ_rooms = [r for r in rooms if r.roomType in [RoomType.CORRIDOR.value, RoomType.STAIR.value, RoomType.ENTRY.value]]
    circ_area = round(sum(r.area_sqm for r in circ_rooms), 2)

    # Room efficiency
    efficiency = round((total_carpet / total_bua) * 100.0, 1) if total_bua > 0 else 85.0

    # DAYLIGHT_PROXY: percentage of habitable rooms touching perimeter
    habitable_types = [
        RoomType.LIVING.value, RoomType.MASTER_BEDROOM.value,
        RoomType.BEDROOM.value, RoomType.GUEST_BEDROOM.value,
        RoomType.KITCHEN.value, RoomType.DINING.value, RoomType.STUDY.value
    ]
    habitable_rooms = [r for r in rooms if r.roomType in habitable_types]
    if habitable_rooms:
        daylight_count = sum(1 for r in habitable_rooms if r.isPerimeter)
        daylight_score = round((daylight_count / len(habitable_rooms)) * 100.0, 1)
    else:
        daylight_score = 90.0

    # VENTILATION_PROXY: check opposing perimeter exposure
    perimeter_rooms = [r for r in rooms if r.isPerimeter]
    ventilation_score = round(min(98.0, 70.0 + (len(perimeter_rooms) / max(1, len(rooms))) * 28.0), 1)

    # CONSTRUCTABILITY_PROXY: based on column count and bay regularity
    col_count = len(candidate.columns)
    if col_count <= 12:
        constructability = 94.0
    elif col_count <= 18:
        constructability = 88.0
    else:
        constructability = 80.0

    # CUSTOMER_FIT: check requested bedrooms and bathrooms
    requested_beds = brief.bedrooms if brief else 3
    requested_baths = brief.bathrooms if brief else 2
    actual_beds = sum(1 for r in rooms if r.roomType in [RoomType.MASTER_BEDROOM.value, RoomType.BEDROOM.value, RoomType.GUEST_BEDROOM.value])
    actual_baths = sum(1 for r in rooms if r.roomType in [RoomType.BATHROOM.value, RoomType.TOILET.value])

    bed_fit = min(1.0, actual_beds / max(1, requested_beds))
    bath_fit = min(1.0, actual_baths / max(1, requested_baths))
    customer_fit = round(((bed_fit * 0.6) + (bath_fit * 0.4)) * 100.0, 1)

    # PARKING_FIT
    has_parking = any(r.roomType == RoomType.PARKING.value for r in rooms)
    parking_fit = 100.0 if has_parking else (90.0 if not (brief and brief.parkingRequired) else 60.0)

    # External wall complexity (Perimeter / sqrt(Area))
    max_x = max(r.x_m + r.width_m for r in rooms)
    max_y = max(r.y_m + r.depth_m for r in rooms)
    bounding_perimeter = 2 * (max_x + max_y)
    sqrt_area = math.sqrt(max(1.0, total_carpet))
    wall_complexity = round(bounding_perimeter / sqrt_area, 2)

    # Wet area clustering complexity (average distance between wet areas)
    wet_rooms = [r for r in rooms if r.roomType in [RoomType.BATHROOM.value, RoomType.TOILET.value, RoomType.KITCHEN.value, RoomType.UTILITY.value]]
    if len(wet_rooms) > 1:
        total_dist = 0.0
        pairs = 0
        for i in range(len(wet_rooms)):
            for j in range(i + 1, len(wet_rooms)):
                ra, rb = wet_rooms[i], wet_rooms[j]
                dist = math.hypot((ra.x_m + ra.width_m/2) - (rb.x_m + rb.width_m/2), (ra.y_m + ra.depth_m/2) - (rb.y_m + rb.depth_m/2))
                total_dist += dist
                pairs += 1
        avg_wet_dist = round(total_dist / pairs, 2)
    else:
        avg_wet_dist = 2.0

    # Overall weighted score
    overall = round(
        (0.20 * efficiency) +
        (0.18 * daylight_score) +
        (0.16 * ventilation_score) +
        (0.16 * constructability) +
        (0.20 * customer_fit) +
        (0.10 * parking_fit) -
        (1.5 * max(0.0, wall_complexity - 4.0)) -
        (1.0 * max(0.0, avg_wet_dist - 4.0))
    , 1)

    return CandidateObjectiveMetrics(
        usableCarpetAreaSqm=round(total_carpet, 2),
        totalBuiltAreaSqm=round(total_bua, 2),
        footprintAreaSqm=round(footprint, 2),
        circulationAreaSqm=round(circ_area, 2),
        roomEfficiency=efficiency,
        daylightProxyScore=daylight_score,
        ventilationProxyScore=ventilation_score,
        constructabilityProxyScore=constructability,
        customerFitScore=customer_fit,
        parkingFitScore=parking_fit,
        externalWallComplexity=wall_complexity,
        wetAreaComplexity=avg_wet_dist,
        overallWeightedScore=overall
    )


def is_pareto_dominated(
    metrics_a: CandidateObjectiveMetrics,
    metrics_b: CandidateObjectiveMetrics
) -> bool:
    """
    Returns True if Candidate A is strictly dominated by Candidate B.
    B dominates A if B is >= A across all objectives and strictly better in at least one.
    If Candidate A is superior in even one objective (e.g. higher constructability,
    simpler plumbing, or lower wall complexity), A is NOT dominated.
    """
    # Tolerances to avoid floating-point noise
    tol = 0.1

    # Checks if B is >= A on maximization objectives
    b_ge_a = (
        (metrics_b.usableCarpetAreaSqm >= metrics_a.usableCarpetAreaSqm - tol) and
        (metrics_b.roomEfficiency >= metrics_a.roomEfficiency - tol) and
        (metrics_b.daylightProxyScore >= metrics_a.daylightProxyScore - tol) and
        (metrics_b.ventilationProxyScore >= metrics_a.ventilationProxyScore - tol) and
        (metrics_b.constructabilityProxyScore >= metrics_a.constructabilityProxyScore - tol) and
        (metrics_b.customerFitScore >= metrics_a.customerFitScore - tol) and
        (metrics_b.parkingFitScore >= metrics_a.parkingFitScore - tol) and
        # Minimization objectives: B must be <= A
        (metrics_b.externalWallComplexity <= metrics_a.externalWallComplexity + tol) and
        (metrics_b.wetAreaComplexity <= metrics_a.wetAreaComplexity + tol)
    )

    if not b_ge_a:
        return False

    # Strictly better in at least one objective
    b_strictly_better = (
        (metrics_b.usableCarpetAreaSqm > metrics_a.usableCarpetAreaSqm + 1.0) or
        (metrics_b.roomEfficiency > metrics_a.roomEfficiency + 1.0) or
        (metrics_b.daylightProxyScore > metrics_a.daylightProxyScore + 2.0) or
        (metrics_b.constructabilityProxyScore > metrics_a.constructabilityProxyScore + 2.0) or
        (metrics_b.customerFitScore > metrics_a.customerFitScore + 2.0) or
        (metrics_b.externalWallComplexity < metrics_a.externalWallComplexity - 0.2) or
        (metrics_b.wetAreaComplexity < metrics_a.wetAreaComplexity - 0.3)
    )

    return b_strictly_better


def filter_pareto_frontier(
    candidates: List[LayoutCandidate],
    brief: Optional[CustomerBrief] = None
) -> ParetoFrontierReport:
    """
    Filters candidates to find the non-dominated Pareto frontier.
    Returns structured report with Pareto set, dominated set, and trade-off rationales.
    """
    if not candidates:
        return ParetoFrontierReport(
            totalCandidatesEvaluated=0,
            nonDominatedCandidatesCount=0,
            paretoOptions=[],
            dominatedOptions=[],
            tradeoffSummary=["No candidates provided for Pareto analysis."]
        )

    # Compute metrics for all candidates
    cand_metrics: List[Tuple[LayoutCandidate, CandidateObjectiveMetrics]] = []
    for c in candidates:
        m = evaluate_candidate_metrics(c, brief)
        cand_metrics.append((c, m))

    non_dominated: List[Dict[str, Any]] = []
    dominated: List[Dict[str, Any]] = []

    for i, (cand_a, met_a) in enumerate(cand_metrics):
        is_dom = False
        dominator_id = None
        for j, (cand_b, met_b) in enumerate(cand_metrics):
            if i != j and is_pareto_dominated(met_a, met_b):
                is_dom = True
                dominator_id = cand_b.designOptionId
                break

        cand_data = {
            "candidateId": cand_a.candidateId,
            "designOptionId": cand_a.designOptionId,
            "metrics": met_a.dict(),
            "objectiveScore": met_a.overallWeightedScore,
            "geometryFingerprint": cand_a.geometryFingerprint,
            "candidate": cand_a
        }

        if is_dom:
            cand_data["dominatedBy"] = dominator_id
            dominated.append(cand_data)
        else:
            non_dominated.append(cand_data)

    # Sort non-dominated by overallWeightedScore descending with stable tie-breaker
    non_dominated.sort(key=lambda x: (-x["objectiveScore"], x["designOptionId"]))

    # Generate architectural trade-off summary
    tradeoffs = []
    for opt in non_dominated:
        m = opt["metrics"]
        opt_id = opt["designOptionId"]
        tradeoffs.append(
            f"Option {opt_id}: Carpet={m['usableCarpetAreaSqm']}m² | Efficiency={m['roomEfficiency']}% | "
            f"Daylight={m['daylightProxyScore']}% | Constructability={m['constructabilityProxyScore']}%"
        )

    return ParetoFrontierReport(
        totalCandidatesEvaluated=len(candidates),
        nonDominatedCandidatesCount=len(non_dominated),
        paretoOptions=non_dominated,
        dominatedOptions=dominated,
        tradeoffSummary=tradeoffs
    )
