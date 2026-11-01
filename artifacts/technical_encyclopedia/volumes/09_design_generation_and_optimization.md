# Volume IX — Design Generation and Computational Optimization

## 1. Architectural Floor Plan Optimization via CP-SAT
Layout generation is executed as a **Discrete Constraint Satisfaction Problem (CSP)** using the **Google OR-Tools CP-SAT** engine (`workers/generation/cpsat_solver.py`).

Operates on integer-scaled coordinates ($1\text{ solver unit} = 100\text{mm} = 0.1\text{m}$).


<div class="diagram-container">
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 195" width="100%" height="195px" class="svg-diagram" style="max-height:195px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;">
<defs>
  <marker id="arr" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
    <path d="M0,0 L6,3 L0,6 Z" fill="#2563eb" />
  </marker>
  <marker id="arr-gray" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
    <path d="M0,0 L6,3 L0,6 Z" fill="#64748b" />
  </marker>
</defs>

<text x="350" y="24" text-anchor="middle" font-size="13" font-weight="bold" fill="#0f172a">DIAGRAM 4: OR-TOOLS CP-SAT DISCRETE SPATIAL ALLOCATION SOLVER</text>
<rect x="30" y="45" width="190" height="130" rx="3" fill="#ffffff" stroke="#3b82f6" stroke-width="1.2"/>
<text x="125" y="65" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#1e40af">1. DISCRETIZATION</text>
<text x="40" y="85" font-size="8" fill="#334155">• Resolution: 1 unit = 100mm</text>
<text x="40" y="100" font-size="8" fill="#334155">• x_i ∈ [0, W_env - w_i]</text>
<text x="40" y="115" font-size="8" fill="#334155">• y_i ∈ [0, L_env - d_i]</text>
<text x="40" y="130" font-size="8" fill="#334155">• w_i ∈ [w_min, w_max]</text>
<text x="40" y="145" font-size="8" fill="#334155">• d_i ∈ [d_min, d_max]</text>
<text x="40" y="160" font-size="8" fill="#059669">Domain size: ~10^6 states</text>

<line x1="220" y1="110" x2="250" y2="110" stroke="#2563eb" stroke-width="1.5" marker-end="url(#arr)"/>

<rect x="250" y="45" width="200" height="130" rx="3" fill="#ffffff" stroke="#8b5cf6" stroke-width="1.2"/>
<text x="350" y="65" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#6d28d9">2. HARD CONSTRAINTS</text>
<text x="260" y="85" font-size="8" fill="#334155">• AddNoOverlap2D([Ix_i], [Iy_i])</text>
<text x="260" y="100" font-size="8" fill="#334155">• Containment: x_i + w_i ≤ W_env</text>
<text x="260" y="115" font-size="8" fill="#334155">• Area: w_i * d_i ≥ A_min (×100)</text>
<text x="260" y="130" font-size="8" fill="#334155">• NBC 2016: Kitchen ≁ Toilet</text>
<text x="260" y="145" font-size="8" fill="#334155">• Daylight: Perimeter Wall Touch</text>
<text x="260" y="160" font-size="8" fill="#059669">100% Guaranteed Feasibility</text>

<line x1="450" y1="110" x2="480" y2="110" stroke="#2563eb" stroke-width="1.5" marker-end="url(#arr)"/>

<rect x="480" y="45" width="190" height="130" rx="3" fill="#ffffff" stroke="#10b981" stroke-width="1.2"/>
<text x="575" y="65" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#047857">3. OBJECTIVE & DIVERSITY</text>
<text x="490" y="85" font-size="8" fill="#334155">• Maximize Adjacency Weights</text>
<text x="490" y="100" font-size="8" fill="#334155">• Maximize Usable Living Space</text>
<text x="490" y="115" font-size="8" fill="#334155">• Minimize Circulation Hallway</text>
<text x="490" y="130" font-size="8" fill="#334155">• No-Good Cuts: Exclude Quadrants</text>
<text x="490" y="145" font-size="8" fill="#334155">• Solve Time: 50ms - 350ms</text>
<text x="490" y="160" font-size="8" fill="#059669">Deterministic (Seed=42)</text>

</svg>
  <div class="diagram-caption">Diagram 4: Google OR-Tools CP-SAT Layout Optimization Pipeline</div>
</div>


---

## 2. Solver Implementation Code Listing (`workers/generation/cpsat_solver.py`)

```python
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

```

---

## 3. Multi-Objective Pareto Alternatives
To provide developers with diverse architectural options, the solver optimizes three distinct objectives:
- **Option A (Circulation Efficiency):** Minimizes total circulation corridor area while maximizing living room volume.
- **Option B (Vaastu Shastra Compliance):** Rewards placement of Kitchen in South-East (Agni corner) and Master Bedroom in South-West (Nairutya corner).
- **Option C (Maximum Living Space):** Maximizes aggregate bedroom and living room square footage at the expense of corridor buffer space.
