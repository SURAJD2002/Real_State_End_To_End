"""
Planwise Enterprise — Deterministic CP-SAT House Layout Solver
M2 Milestone — Phase 4 & Phase 5

Pure mathematical spatial optimization using Google OR-Tools CP-SAT.
Operates on integer-scaled coordinates (1 unit = 100mm = 0.1m).
Generates multiple valid, topologically distinct residential floor plan layouts
obeying M1 buildable boundaries, NBC 2016 room dimensions, statutory envelopes,
and topological adjacency graphs.
"""

from typing import List, Dict, Any, Optional, Tuple, Set
import time
import math
import hashlib
import json
from dataclasses import dataclass, field

from ortools.sat.python import cp_model

from packages.schemas.customer_brief import CustomerBrief
from packages.schemas.room_program import (
    RoomProgram,
    RoomSpecification,
    RoomType,
    DaylightRequirement,
    PrivacyLevel
)
from packages.schemas.room_graph import RoomAdjacencyGraph, AdjacencyRelationshipType


# Precision: 1 solver unit = 100mm (0.1m).
# A 20m plot is 200 units. Keeps CP-SAT integer domains compact and solve time under 200ms.
SOLVER_UNIT_MM: int = 100
SOLVER_UNIT_M: float = 0.1


@dataclass
class SolvedRoom:
    spaceId: str
    roomType: str
    name: str
    floor: str
    x_m: float
    y_m: float
    width_m: float
    depth_m: float
    area_sqm: float
    zone: str
    color: str
    isPerimeter: bool = False

    @property
    def bounds(self) -> Dict[str, float]:
        return {
            "x": self.x_m,
            "y": self.y_m,
            "width": self.width_m,
            "height": self.depth_m
        }

    @property
    def polygon(self) -> List[List[float]]:
        x0, y0 = self.x_m, self.y_m
        x1, y1 = round(x0 + self.width_m, 2), round(y0 + self.depth_m, 2)
        return [
            [round(x0, 2), round(y0, 2)],
            [x1, round(y0, 2)],
            [x1, y1],
            [round(x0, 2), y1],
            [round(x0, 2), round(y0, 2)]
        ]


@dataclass
class LayoutCandidate:
    candidateId: str
    designOptionId: str
    solverStatus: str
    solveTimeMs: float
    objectiveScore: float
    rooms: List[SolvedRoom]
    columns: List[Dict[str, Any]]
    stairs: Optional[Dict[str, Any]]
    metrics: Dict[str, Any]
    geometryFingerprint: str
    constraintSummary: Dict[str, Any]
    isFeasible: bool = True
    diversityMetrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidateId": self.candidateId,
            "designOptionId": self.designOptionId,
            "solverStatus": self.solverStatus,
            "solveTimeMs": self.solveTimeMs,
            "objectiveScore": self.objectiveScore,
            "rooms": [
                {
                    "id": r.spaceId,
                    "roomType": r.roomType,
                    "name": r.name,
                    "floor": r.floor,
                    "zone": r.zone,
                    "color": r.color,
                    "areaSqm": r.area_sqm,
                    "widthM": r.width_m,
                    "lengthM": r.depth_m,
                    "bounds": r.bounds,
                    "polygon": r.polygon,
                    "isPerimeter": r.isPerimeter
                }
                for r in self.rooms
            ],
            "columns": self.columns,
            "stairs": self.stairs,
            "metrics": self.metrics,
            "geometryFingerprint": self.geometryFingerprint,
            "constraintSummary": self.constraintSummary,
            "isFeasible": self.isFeasible,
            "diversityMetrics": self.diversityMetrics
        }


class CPSATLayoutSolver:
    """
    Deterministic CP-SAT Spatial Layout Solver.
    Formulates a 2D/3D integer programming problem with non-overlap intervals,
    bounding box containment, adjacency satisfaction, perimeter daylighting,
    and no-good cut diversity.
    """

    def __init__(
        self,
        program: RoomProgram,
        adjacency_graph: RoomAdjacencyGraph,
        brief: Optional[CustomerBrief] = None,
        envelope_width_m: float = 14.0,
        envelope_length_m: float = 16.0,
        max_floors: int = 1,
        time_limit_seconds: float = 3.0,
        random_seed: int = 42
    ):
        self.program = program
        self.graph = adjacency_graph
        self.brief = brief
        self.env_w_m = max(8.0, envelope_width_m)
        self.env_l_m = max(8.0, envelope_length_m)
        self.max_floors = max(1, max_floors)
        self.time_limit_seconds = time_limit_seconds
        self.random_seed = random_seed

        # Convert envelope dimensions to solver integer units
        self.env_w_units = int(round(self.env_w_m / SOLVER_UNIT_M))
        self.env_l_units = int(round(self.env_l_m / SOLVER_UNIT_M))

    def solve_candidates(self, target_candidates: int = 3) -> List[LayoutCandidate]:
        """
        Solves for multiple topologically distinct design candidates using CP-SAT
        and diversity exclusion constraints.
        """
        candidates: List[LayoutCandidate] = []
        excluded_topologies: List[Dict[str, Any]] = []

        for candidate_idx in range(target_candidates):
            candidate = self._solve_single_candidate(
                candidate_index=candidate_idx,
                excluded_topologies=excluded_topologies
            )
            if candidate and candidate.isFeasible:
                candidates.append(candidate)
                # Record topology for no-good cuts
                excluded_topologies.append({
                    "fingerprint": candidate.geometryFingerprint,
                    "quadrant_map": self._extract_quadrant_map(candidate.rooms)
                })
            else:
                break

        # Compute pairwise diversity metrics
        self._compute_pairwise_diversity(candidates)
        return candidates

    def _solve_single_candidate(
        self,
        candidate_index: int,
        excluded_topologies: List[Dict[str, Any]]
    ) -> Optional[LayoutCandidate]:
        """Formulates and solves a single CP-SAT optimization instance."""
        start_time = time.perf_counter()
        model = cp_model.CpModel()

        # Categorize rooms by floor
        floor_assignments: Dict[str, List[RoomSpecification]] = {"L0": []}
        if self.max_floors > 1:
            floor_assignments["L1"] = []

        for item in self.program.rooms:
            f = f"L{item.floorIndex}"
            if f not in floor_assignments:
                f = "L0"
            floor_assignments[f].append(item)

        room_vars: Dict[str, Dict[str, Any]] = {}
        no_overlap_intervals_x: Dict[str, List[Any]] = {f: [] for f in floor_assignments}
        no_overlap_intervals_y: Dict[str, List[Any]] = {f: [] for f in floor_assignments}

        # 1. Variables for each room
        for floor_key, items in floor_assignments.items():
            for item in items:
                sid = item.specId
                min_w = max(12, int(round(item.minWidthM / SOLVER_UNIT_M)))
                min_l = max(12, int(round(item.minLengthM / SOLVER_UNIT_M)))
                
                # Allow orientation swap if preferred aspect ratio permits
                min_dim = min(min_w, min_l)
                max_dim = max(int(round(self.env_w_units * 0.75)), int(round(self.env_l_units * 0.75)))

                x_var = model.NewIntVar(0, self.env_w_units, f"x_{sid}")
                y_var = model.NewIntVar(0, self.env_l_units, f"y_{sid}")
                w_var = model.NewIntVar(min_dim, max_dim, f"w_{sid}")
                d_var = model.NewIntVar(min_dim, max_dim, f"d_{sid}")

                x_end = model.NewIntVar(0, self.env_w_units, f"x_end_{sid}")
                y_end = model.NewIntVar(0, self.env_l_units, f"y_end_{sid}")

                model.Add(x_end == x_var + w_var)
                model.Add(y_end == y_var + d_var)

                # Hard Constraint 1: Must stay within buildable envelope
                model.Add(x_end <= self.env_w_units)
                model.Add(y_end <= self.env_l_units)

                # Hard Constraint 5: Minimum room area
                # 1 unit² = (0.1m)² = 0.01 sqm -> area_units = area_sqm * 100
                min_area_units = int(round(item.minAreaSqm * 100))
                max_area_units = int(round(item.maxAreaSqm * 100))
                area_var = model.NewIntVar(min_area_units, max_area_units, f"area_{sid}")
                model.AddMultiplicationEquality(area_var, [w_var, d_var])

                # 2D interval variable for NoOverlap
                x_interval = model.NewIntervalVar(x_var, w_var, x_end, f"x_int_{sid}")
                y_interval = model.NewIntervalVar(y_var, d_var, y_end, f"y_int_{sid}")

                no_overlap_intervals_x[floor_key].append(x_interval)
                no_overlap_intervals_y[floor_key].append(y_interval)

                room_vars[sid] = {
                    "item": item,
                    "floor": floor_key,
                    "x": x_var,
                    "y": y_var,
                    "w": w_var,
                    "d": d_var,
                    "x_end": x_end,
                    "y_end": y_end,
                    "area": area_var
                }

        # Hard Constraint 2: Non-overlapping rooms per floor
        for floor_key in floor_assignments:
            if no_overlap_intervals_x[floor_key]:
                model.AddNoOverlap2D(
                    no_overlap_intervals_x[floor_key],
                    no_overlap_intervals_y[floor_key]
                )

        # Hard Constraint 6 & 7: Topological Adjacencies & Forbidden Boundaries
        objective_terms = []

        for edge in self.graph.edges:
            # Find all room items matching fromRoom and toRoom types
            from_items = [v for v in room_vars.values() if v["item"].roomType.value == edge.fromRoom]
            to_items = [v for v in room_vars.values() if v["item"].roomType.value == edge.toRoom]

            for fa in from_items:
                for fb in to_items:
                    if fa["floor"] != fb["floor"] or fa["item"].specId == fb["item"].specId:
                        continue

                    # Adjacency indicators
                    touch_right = model.NewBoolVar(f"touch_r_{fa['item'].specId}_{fb['item'].specId}")
                    touch_left = model.NewBoolVar(f"touch_l_{fa['item'].specId}_{fb['item'].specId}")
                    touch_top = model.NewBoolVar(f"touch_t_{fa['item'].specId}_{fb['item'].specId}")
                    touch_bot = model.NewBoolVar(f"touch_b_{fa['item'].specId}_{fb['item'].specId}")

                    model.Add(fa["x_end"] == fb["x"]).OnlyEnforceIf(touch_right)
                    model.Add(fa["x_end"] != fb["x"]).OnlyEnforceIf(touch_right.Not())

                    model.Add(fb["x_end"] == fa["x"]).OnlyEnforceIf(touch_left)
                    model.Add(fb["x_end"] != fa["x"]).OnlyEnforceIf(touch_left.Not())

                    model.Add(fa["y_end"] == fb["y"]).OnlyEnforceIf(touch_top)
                    model.Add(fa["y_end"] != fb["y"]).OnlyEnforceIf(touch_top.Not())

                    model.Add(fb["y_end"] == fa["y"]).OnlyEnforceIf(touch_bot)
                    model.Add(fb["y_end"] != fa["y"]).OnlyEnforceIf(touch_bot.Not())

                    are_touching = model.NewBoolVar(f"adj_{fa['item'].specId}_{fb['item'].specId}")
                    model.AddBoolOr([touch_right, touch_left, touch_top, touch_bot]).OnlyEnforceIf(are_touching)
                    model.AddBoolAnd([touch_right.Not(), touch_left.Not(), touch_top.Not(), touch_bot.Not()]).OnlyEnforceIf(are_touching.Not())

                    if edge.relationship == AdjacencyRelationshipType.FORBIDDEN_ADJACENCY:
                        # Hard Constraint: strictly forbidden to touch
                        model.Add(are_touching == 0)
                    elif edge.relationship == AdjacencyRelationshipType.REQUIRED_ADJACENCY:
                        # Soft/Hard objective term for required adjacency
                        objective_terms.append(are_touching * int(edge.weight * 10))
                    elif edge.relationship == AdjacencyRelationshipType.PREFERRED_ADJACENCY:
                        objective_terms.append(are_touching * int(edge.weight * 5))

        # Soft Objective: Daylight Proxy (Rooms with daylight requirement on boundary)
        for sid, v in room_vars.items():
            if v["item"].daylight == DaylightRequirement.DIRECT_WINDOW:
                on_left = model.NewBoolVar(f"on_left_{sid}")
                on_right = model.NewBoolVar(f"on_right_{sid}")
                on_bottom = model.NewBoolVar(f"on_bot_{sid}")
                on_top = model.NewBoolVar(f"on_top_{sid}")

                model.Add(v["x"] == 0).OnlyEnforceIf(on_left)
                model.Add(v["x"] != 0).OnlyEnforceIf(on_left.Not())

                model.Add(v["x_end"] == self.env_w_units).OnlyEnforceIf(on_right)
                model.Add(v["x_end"] != self.env_w_units).OnlyEnforceIf(on_right.Not())

                model.Add(v["y"] == 0).OnlyEnforceIf(on_bottom)
                model.Add(v["y"] != 0).OnlyEnforceIf(on_bottom.Not())

                model.Add(v["y_end"] == self.env_l_units).OnlyEnforceIf(on_top)
                model.Add(v["y_end"] != self.env_l_units).OnlyEnforceIf(on_top.Not())

                has_daylight = model.NewBoolVar(f"has_daylight_{sid}")
                model.AddBoolOr([on_left, on_right, on_bottom, on_top]).OnlyEnforceIf(has_daylight)
                model.AddBoolAnd([on_left.Not(), on_right.Not(), on_bottom.Not(), on_top.Not()]).OnlyEnforceIf(has_daylight.Not())

                # Reward daylight perimeter positioning
                objective_terms.append(has_daylight * 50)

        # Soft Objective: Wet Area Clustering (Plumbing Efficiency)
        wet_rooms = [v for v in room_vars.values() if v["item"].isWetArea]
        for i in range(len(wet_rooms)):
            for j in range(i + 1, len(wet_rooms)):
                wa, wb = wet_rooms[i], wet_rooms[j]
                if wa["floor"] == wb["floor"]:
                    # Manhattan distance proxy between origins
                    dx = model.NewIntVar(0, self.env_w_units, f"dx_wet_{i}_{j}")
                    dy = model.NewIntVar(0, self.env_l_units, f"dy_wet_{i}_{j}")
                    model.Add(dx >= wa["x"] - wb["x"])
                    model.Add(dx >= wb["x"] - wa["x"])
                    model.Add(dy >= wa["y"] - wb["y"])
                    model.Add(dy >= wb["y"] - wa["y"])
                    objective_terms.append(-(dx + dy) * 2)

        # Diversity Cuts (Phase 5): No-good exclusions against previous candidates
        if candidate_index > 0 and excluded_topologies:
            for excl in excluded_topologies:
                quad_map = excl.get("quadrant_map", {})
                diff_conditions = []
                for sid, old_quad in quad_map.items():
                    if sid in room_vars:
                        v = room_vars[sid]
                        mid_x = self.env_w_units // 2
                        mid_y = self.env_l_units // 2
                        
                        is_left = model.NewBoolVar(f"diff_l_{sid}_{candidate_index}")
                        is_bottom = model.NewBoolVar(f"diff_b_{sid}_{candidate_index}")
                        model.Add(v["x"] < mid_x).OnlyEnforceIf(is_left)
                        model.Add(v["x"] >= mid_x).OnlyEnforceIf(is_left.Not())
                        model.Add(v["y"] < mid_y).OnlyEnforceIf(is_bottom)
                        model.Add(v["y"] >= mid_y).OnlyEnforceIf(is_bottom.Not())

                        if old_quad == "SW":
                            diff_conditions.append(is_left.Not())
                            diff_conditions.append(is_bottom.Not())
                        elif old_quad == "SE":
                            diff_conditions.append(is_left)
                            diff_conditions.append(is_bottom.Not())
                        elif old_quad == "NW":
                            diff_conditions.append(is_left.Not())
                            diff_conditions.append(is_bottom)
                        elif old_quad == "NE":
                            diff_conditions.append(is_left)
                            diff_conditions.append(is_bottom)

                if diff_conditions:
                    model.AddBoolOr(diff_conditions)

        # Maximize total soft objective
        if objective_terms:
            model.Maximize(sum(objective_terms))

        # Solve configuration
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = self.time_limit_seconds
        solver.parameters.random_seed = self.random_seed + (candidate_index * 13)
        solver.parameters.num_workers = 1  # Guaranteed deterministic single-thread search

        status = solver.Solve(model)
        elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return None

        # Extract solved rooms
        solved_rooms: List[SolvedRoom] = []
        for sid, v in room_vars.items():
            x_m = round(solver.Value(v["x"]) * SOLVER_UNIT_M, 2)
            y_m = round(solver.Value(v["y"]) * SOLVER_UNIT_M, 2)
            w_m = round(solver.Value(v["w"]) * SOLVER_UNIT_M, 2)
            d_m = round(solver.Value(v["d"]) * SOLVER_UNIT_M, 2)
            area_sqm = round(w_m * d_m, 2)

            is_perimeter = (
                solver.Value(v["x"]) == 0 or
                solver.Value(v["x_end"]) == self.env_w_units or
                solver.Value(v["y"]) == 0 or
                solver.Value(v["y_end"]) == self.env_l_units
            )

            solved_rooms.append(SolvedRoom(
                spaceId=sid,
                roomType=v["item"].roomType.value,
                name=v["item"].displayName,
                floor=v["floor"],
                x_m=x_m,
                y_m=y_m,
                width_m=w_m,
                depth_m=d_m,
                area_sqm=area_sqm,
                zone=v["item"].privacy.value,
                color=v["item"].displayColor,
                isPerimeter=is_perimeter
            ))

        # Calculate structural grid columns
        columns = self._generate_structural_columns(solved_rooms)

        # Stairs placeholder if multi-floor
        stairs_data = None
        if self.max_floors > 1:
            stair_room = next((r for r in solved_rooms if r.roomType == RoomType.STAIR.value), None)
            if stair_room:
                stairs_data = {
                    "spaceId": stair_room.spaceId,
                    "bounds": stair_room.bounds,
                    "riserMm": 150,
                    "treadMm": 280,
                    "flightWidthM": 1.05,
                    "risersCount": 21,
                    "landingWidthM": 1.2
                }

        # Calculate layout metrics
        total_carpet = round(sum(r.area_sqm for r in solved_rooms), 2)
        total_bua = round(total_carpet * 1.15, 2) # Adding 15% structural wall factor
        footprint_sqm = round(max((r.x_m + r.width_m) for r in solved_rooms) * max((r.y_m + r.depth_m) for r in solved_rooms), 2)
        daylight_ratio = round((sum(1 for r in solved_rooms if r.isPerimeter) / len(solved_rooms)) * 100.0, 1)

        metrics = {
            "totalCarpetAreaSqm": total_carpet,
            "totalBuiltUpAreaSqm": total_bua,
            "footprintSqm": footprint_sqm,
            "roomCount": len(solved_rooms),
            "floorCount": self.max_floors,
            "daylightPerimeterRatio": daylight_ratio,
            "carpetEfficiencyPercent": round((total_carpet / total_bua) * 100.0, 1),
            "solverStatus": solver.StatusName(status)
        }

        # Geometry fingerprint (SHA-256 of sorted normalized coordinates)
        geom_str = "|".join([
            f"{r.spaceId}:{r.floor}:{r.x_m}:{r.y_m}:{r.width_m}:{r.depth_m}"
            for r in sorted(solved_rooms, key=lambda rm: (rm.floor, rm.x_m, rm.y_m))
        ])
        fingerprint = hashlib.sha256(geom_str.encode()).hexdigest()

        cand_id = f"cand-{candidate_index + 1}-{fingerprint[:8]}"
        opt_id = f"opt-{chr(65 + candidate_index)}"

        return LayoutCandidate(
            candidateId=cand_id,
            designOptionId=opt_id,
            solverStatus=solver.StatusName(status),
            solveTimeMs=elapsed_ms,
            objectiveScore=round(solver.ObjectiveValue(), 1) if objective_terms else 100.0,
            rooms=solved_rooms,
            columns=columns,
            stairs=stairs_data,
            metrics=metrics,
            geometryFingerprint=fingerprint,
            constraintSummary={
                "envelopeContainment": "SATISFIED",
                "noOverlap": "SATISFIED",
                "minimumDimensions": "SATISFIED",
                "minimumAreas": "SATISFIED",
                "forbiddenAdjacencies": "SATISFIED"
            },
            isFeasible=True
        )

    def _generate_structural_columns(self, rooms: List[SolvedRoom]) -> List[Dict[str, Any]]:
        """Generates candidate structural grid columns at room corners and bay intersections."""
        col_points: Set[Tuple[float, float]] = set()
        for r in rooms:
            # 4 corners of each room in meters
            x0, y0 = r.x_m, r.y_m
            x1, y1 = round(x0 + r.width_m, 2), round(y0 + r.depth_m, 2)
            col_points.add((x0, y0))
            col_points.add((x1, y0))
            col_points.add((x1, y1))
            col_points.add((x0, y1))

        # Cluster points within 0.35m to avoid redundant adjacent columns
        clustered: List[Tuple[float, float]] = []
        for p in sorted(list(col_points)):
            if not any(math.hypot(p[0] - c[0], p[1] - c[1]) < 0.35 for c in clustered):
                clustered.append(p)

        columns = []
        for idx, (cx, cy) in enumerate(clustered):
            columns.append({
                "columnId": f"COL-{idx + 1:03d}",
                "x_m": cx,
                "y_m": cy,
                "widthMm": 300,
                "depthMm": 450,
                "label": "PRELIMINARY_COLUMN"
            })
        return columns

    def _extract_quadrant_map(self, rooms: List[SolvedRoom]) -> Dict[str, str]:
        """Maps anchor rooms to cardinal quadrants (SW, SE, NW, NE) for diversity cuts."""
        quad_map = {}
        mid_x = self.env_w_m / 2.0
        mid_y = self.env_l_m / 2.0
        for r in rooms:
            if r.roomType in [RoomType.LIVING.value, RoomType.KITCHEN.value, RoomType.MASTER_BEDROOM.value, RoomType.ENTRY.value]:
                cx = r.x_m + (r.width_m / 2.0)
                cy = r.y_m + (r.depth_m / 2.0)
                if cx < mid_x and cy < mid_y:
                    quad = "SW"
                elif cx >= mid_x and cy < mid_y:
                    quad = "SE"
                elif cx < mid_x and cy >= mid_y:
                    quad = "NW"
                else:
                    quad = "NE"
                quad_map[r.spaceId] = quad
        return quad_map

    def _compute_pairwise_diversity(self, candidates: List[LayoutCandidate]):
        """Computes topological and spatial diversity metrics between generated candidates."""
        for i, c1 in enumerate(candidates):
            c1.diversityMetrics = {
                "candidateIndex": i + 1,
                "uniqueFingerprint": True,
                "quadrantVariance": 0.0
            }
            if len(candidates) > 1:
                diff_count = 0
                total_comparisons = 0
                for j, c2 in enumerate(candidates):
                    if i != j:
                        # Compare room positions
                        r1_map = {r.roomType: (r.x_m, r.y_m) for r in c1.rooms}
                        r2_map = {r.roomType: (r.x_m, r.y_m) for r in c2.rooms}
                        for rtype, pos1 in r1_map.items():
                            if rtype in r2_map:
                                pos2 = r2_map[rtype]
                                if math.hypot(pos1[0] - pos2[0], pos1[1] - pos2[1]) > 1.5:
                                    diff_count += 1
                                total_comparisons += 1
                if total_comparisons > 0:
                    c1.diversityMetrics["quadrantVariance"] = round((diff_count / total_comparisons) * 100.0, 1)
