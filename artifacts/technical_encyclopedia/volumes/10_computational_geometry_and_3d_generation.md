# Volume X — Computational Geometry and 3D Model Generation

## 1. Watertight 3D Solids Modeling with Manifold3D
3D physical geometry in Planwise is synthesized using the **Manifold3D** C++ computational geometry kernel (`workers/geometry/solid_engine.py`).

### The 2-Manifold Topological Invariant
A surface mesh is a **watertight 2-manifold** if and only if:
1. Every edge is shared by exactly two adjacent faces.
2. The neighbourhood of every vertex is topologically equivalent to an open 2D disk.
3. No self-intersections or non-manifold edges exist.
4. The **Euler characteristic** satisfies:
   $$\chi = V - E + F = 2(1 - g)$$
   For closed genus-0 solids without through-holes, $\chi = 2$.


<div class="diagram-container">
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 155" width="100%" height="155px" class="svg-diagram" style="max-height:155px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;">
<defs>
  <marker id="arr" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
    <path d="M0,0 L6,3 L0,6 Z" fill="#2563eb" />
  </marker>
  <marker id="arr-gray" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
    <path d="M0,0 L6,3 L0,6 Z" fill="#64748b" />
  </marker>
</defs>

<text x="350" y="24" text-anchor="middle" font-size="13" font-weight="bold" fill="#0f172a">DIAGRAM 5: MANIFOLD3D WATERTIGHT SOLID CSG PIPELINE</text>
<rect x="30" y="45" width="140" height="90" rx="3" fill="#ffffff" stroke="#3b82f6"/>
<text x="100" y="65" text-anchor="middle" font-size="9" font-weight="bold" fill="#1e40af">1. 2D Polygons</text>
<text x="40" y="82" font-size="7.8" fill="#334155">Shapely 2.1.2</text>
<text x="40" y="96" font-size="7.8" fill="#334155">Room Boundaries</text>
<text x="40" y="110" font-size="7.8" fill="#334155">Wall Footprints</text>
<text x="40" y="124" font-size="7.8" fill="#059669">No Self-Intersection</text>

<line x1="170" y1="90" x2="195" y2="90" stroke="#2563eb" stroke-width="1.2" marker-end="url(#arr)"/>

<rect x="195" y="45" width="145" height="90" rx="3" fill="#ffffff" stroke="#8b5cf6"/>
<text x="267" y="65" text-anchor="middle" font-size="9" font-weight="bold" fill="#6d28d9">2. Linear Extrusion</text>
<text x="205" y="82" font-size="7.8" fill="#334155">Manifold.cube(L, T, H)</text>
<text x="205" y="96" font-size="7.8" fill="#334155">translate & rotate</text>
<text x="205" y="110" font-size="7.8" fill="#334155">Base Wall Solid</text>
<text x="205" y="124" font-size="7.8" fill="#059669">2-Manifold Primitives</text>

<line x1="340" y1="90" x2="365" y2="90" stroke="#2563eb" stroke-width="1.2" marker-end="url(#arr)"/>

<rect x="365" y="45" width="150" height="90" rx="3" fill="#ffffff" stroke="#f59e0b"/>
<text x="440" y="65" text-anchor="middle" font-size="9" font-weight="bold" fill="#b45309">3. CSG Difference</text>
<text x="375" y="82" font-size="7.8" fill="#334155">Cutters: Door/Window</text>
<text x="375" y="96" font-size="7.8" fill="#334155">cutter_thk = 1.5 * wall</text>
<text x="375" y="110" font-size="7.8" fill="#334155">solid_wall - cutters</text>
<text x="375" y="124" font-size="7.8" fill="#059669">Clean Void Subtraction</text>

<line x1="515" y1="90" x2="540" y2="90" stroke="#2563eb" stroke-width="1.2" marker-end="url(#arr)"/>

<rect x="540" y="45" width="130" height="90" rx="3" fill="#ffffff" stroke="#10b981"/>
<text x="605" y="65" text-anchor="middle" font-size="9" font-weight="bold" fill="#047857">4. Validation</text>
<text x="550" y="82" font-size="7.8" fill="#334155">is_manifold() == True</text>
<text x="550" y="96" font-size="7.8" fill="#334155">genus = num_openings</text>
<text x="550" y="110" font-size="7.8" fill="#334155">volume > 0.0</text>
<text x="550" y="124" font-size="7.8" fill="#059669">Watertight Mesh Export</text>

</svg>
  <div class="diagram-caption">Diagram 5: Manifold3D Watertight Mesh Boolean CSG Pipeline</div>
</div>


---

## 2. Geometry Kernel Implementation Code Listing (`workers/geometry/solid_engine.py`)

```python
"""
Planwise Enterprise — Manifold3D Solid Modeling & Geometry Kernel
M2 Milestone — Phase 7 & Phase 8

Integrates Manifold3D (libmanifold) as the authoritative 3D solid geometry engine.
Generates watertight 2-manifold representations of all building elements:
- Structural walls with parametric door & window cutouts (Boolean Difference)
- Floor & roof slabs with shaft / stair openings
- RCC column grids
- Volumetric staircases
- Strict validation: rejects non-manifold edges, self-intersections, zero volume.
"""

from typing import List, Dict, Any, Optional, Tuple
import math
from pydantic import BaseModel, Field

try:
    import manifold3d
    from manifold3d import Manifold, Mesh
    HAS_MANIFOLD = True
except ImportError:
    HAS_MANIFOLD = False
    Manifold = None
    Mesh = None


class SolidValidationError(BaseModel):
    """Specific geometry failure code and explanation."""
    code: str = Field(..., description="Error code e.g. NON_MANIFOLD_EDGE, NEGATIVE_VOLUME, OPENING_OUT_OF_BOUNDS")
    elementId: str = Field(..., description="ID of the invalid building element")
    message: str = Field(..., description="Human-readable architectural diagnosis")


class GeometryValidationResult(BaseModel):
    """Authoritative validation result for a compiled 3D solid element or building model."""
    status: str = Field(..., description="VALID or INVALID")
    elementId: str = Field(..., description="Target element ID")
    is2Manifold: bool = Field(default=True, description="Strict 2-manifold topological condition")
    isWatertight: bool = Field(default=True, description="No boundary holes / zero boundary edges")
    hasPositiveVolume: bool = Field(default=True, description="Strict positive volume > 0")
    volumeM3: float = Field(default=0.0, description="Computed manifold volume in cubic meters")
    surfaceAreaM2: float = Field(default=0.0, description="Surface area in square meters")
    numVertices: int = Field(default=0)
    numTriangles: int = Field(default=0)
    genus: int = Field(default=0, description="Topological genus (number of holes/openings)")
    errors: List[SolidValidationError] = Field(default_factory=list)

    @property
    def isValid(self) -> bool:
        return self.status == "VALID" and len(self.errors) == 0


class SolidModelingEngine:
    """
    Authoritative Solid Modeling Engine using Manifold3D.
    Performs constructive solid geometry (CSG) operations: union, difference, intersection.
    """

    def __init__(self):
        if not HAS_MANIFOLD:
            raise RuntimeError("manifold3d library is not installed in current environment.")

    def create_wall_solid(
        self,
        start_pt: Tuple[float, float],
        end_pt: Tuple[float, float],
        height_m: float,
        thickness_m: float,
        element_id: str,
        elevation_m: float = 0.0,
        openings: Optional[List[Dict[str, Any]]] = None
    ) -> Tuple[Optional[Manifold], GeometryValidationResult]:
        """
        Creates an extruded wall solid and subtracts doors and windows using CSG difference.
        start_pt and end_pt are 2D coordinates in meters.
        """
        x0, y0 = start_pt
        x1, y1 = end_pt
        dx = x1 - x0
        dy = y1 - y0
        wall_len = math.hypot(dx, dy)

        if wall_len < 0.01:
            err = SolidValidationError(
                code="ZERO_LENGTH_WALL",
                elementId=element_id,
                message=f"Wall {element_id} has zero or near-zero length ({wall_len}m)."
            )
            return None, GeometryValidationResult(
                status="INVALID",
                elementId=element_id,
                is2Manifold=False,
                isWatertight=False,
                hasPositiveVolume=False,
                errors=[err]
            )

        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)

        # Base wall box aligned with X axis: length x thickness x height
        # Centered on Y axis by thickness / 2
        base_wall = Manifold.cube([wall_len, thickness_m, height_m])
        # Center wall thickness around line
        base_wall = base_wall.translate([0.0, -thickness_m / 2.0, 0.0])

        # Boolean subtraction for openings
        if openings:
            for op in openings:
                op_dist = op.get("distanceFromStartM", 0.5)
                op_width = op.get("widthM", 0.9)
                op_height = op.get("heightM", 2.1)
                sill_height = op.get("sillHeightM", 0.0)

                # Ensure opening cutter is slightly thicker than wall to guarantee clean manifold subtraction
                cutter_thickness = thickness_m * 1.5
                cutter = Manifold.cube([op_width, cutter_thickness, op_height])
                cutter = cutter.translate([
                    op_dist,
                    -cutter_thickness / 2.0,
                    sill_height
                ])

                # Boolean Difference: Wall - Cutter
                base_wall = base_wall - cutter

        # Rotate to wall orientation and translate to starting point
        wall_solid = base_wall.rotate([0.0, 0.0, angle_deg]).translate([x0, y0, elevation_m])

        validation = self.validate_solid(wall_solid, element_id)
        return wall_solid, validation

    def create_slab_solid(
        self,
        polygon_points: List[List[float]],
        thickness_m: float,
        elevation_m: float,
        element_id: str,
        openings: Optional[List[List[List[float]]]] = None
    ) -> Tuple[Optional[Manifold], GeometryValidationResult]:
        """
        Creates a floor or roof slab solid by bounding box or extrusion and cuts shaft openings.
        polygon_points: 2D polygon vertices in meters [[x0, y0], [x1, y1], ...]
        """
        if len(polygon_points) < 3:
            err = SolidValidationError(
                code="DEGENERATE_SLAB_POLYGON",
                elementId=element_id,
                message=f"Slab {element_id} has fewer than 3 vertices."
            )
            return None, GeometryValidationResult(
                status="INVALID",
                elementId=element_id,
                is2Manifold=False,
                isWatertight=False,
                hasPositiveVolume=False,
                errors=[err]
            )

        # Find axis-aligned bounding box of slab polygon
        xs = [p[0] for p in polygon_points]
        ys = [p[1] for p in polygon_points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        w = max_x - min_x
        d = max_y - min_y

        slab_solid = Manifold.cube([w, d, thickness_m]).translate([min_x, min_y, elevation_m])

        # Cut any shaft or stair openings
        if openings:
            for op_pts in openings:
                oxs = [p[0] for p in op_pts]
                oys = [p[1] for p in op_pts]
                ow = max(oxs) - min(oxs)
                od = max(oys) - min(oys)
                cutter = Manifold.cube([ow, od, thickness_m * 2.0]).translate([
                    min(oxs), min(oys), elevation_m - (thickness_m * 0.5)
                ])
                slab_solid = slab_solid - cutter

        validation = self.validate_solid(slab_solid, element_id)
        return slab_solid, validation

    def create_column_solid(
        self,
        center_x: float,
        center_y: float,
        width_m: float,
        depth_m: float,
        height_m: float,
        elevation_m: float,
        element_id: str
    ) -> Tuple[Optional[Manifold], GeometryValidationResult]:
        """Creates an RCC structural column solid."""
        col = Manifold.cube([width_m, depth_m, height_m])
        col = col.translate([
            center_x - (width_m / 2.0),
            center_y - (depth_m / 2.0),
            elevation_m
        ])

        validation = self.validate_solid(col, element_id)
        return col, validation

    def create_stair_solid(
        self,
        bounds: Dict[str, float],
        floor_to_floor_height_m: float,
        element_id: str,
        riser_mm: int = 150,
        tread_mm: int = 280,
        elevation_m: float = 0.0
    ) -> Tuple[Optional[Manifold], GeometryValidationResult]:
        """Creates a volumetric stepped staircase solid."""
        x0 = bounds.get("x", 0.0)
        y0 = bounds.get("y", 0.0)
        w = bounds.get("width", 2.4)
        d = bounds.get("height", 3.2)

        riser_m = riser_mm / 1000.0
        tread_m = tread_mm / 1000.0
        num_risers = max(2, int(round(floor_to_floor_height_m / riser_m)))

        # Construct stepped solid as union of step blocks
        step_depth = d / (num_risers / 2.0)
        flight_width = w / 2.1

        steps = []
        for i in range(num_risers // 2):
            step_box = Manifold.cube([flight_width, step_depth, riser_m * (i + 1)])
            step_box = step_box.translate([
                x0,
                y0 + (i * step_depth),
                elevation_m
            ])
            steps.append(step_box)

        stair_solid = steps[0]
        for s in steps[1:]:
            stair_solid = stair_solid + s

        validation = self.validate_solid(stair_solid, element_id)
        return stair_solid, validation

    def validate_solid(self, solid: Manifold, element_id: str) -> GeometryValidationResult:
        """
        Rigorous manifold validation per Delta Spec M2 Phase 8:
        - 2-manifold check

```

---

## 3. Verification via Test Suite
The 3D kernel is verified by `tests/test_geometry_invariants.py`:
- Watertightness check returns `True`.
- Euler characteristic $\chi = 2$ strictly confirmed.
- Volume is strictly positive ($V > 0$).
- Total surface area matches analytical polygon sum.
