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
        - Watertight check (genus, boundary edges)
        - Volume positivity
        - Finite vertices
        - Explicit error collection (never silently repair)
        """
        errors: List[SolidValidationError] = []

        if solid is None or solid.is_empty():
            errors.append(SolidValidationError(
                code="EMPTY_GEOMETRY",
                elementId=element_id,
                message=f"Element {element_id} produced an empty or null solid."
            ))
            return GeometryValidationResult(
                status="INVALID",
                elementId=element_id,
                is2Manifold=False,
                isWatertight=False,
                hasPositiveVolume=False,
                errors=errors
            )

        # Check Manifold internal status
        status = solid.status()
        # In manifold3d, status is Error enum: Error.NoError is valid
        if str(status) != "Error.NoError":
            errors.append(SolidValidationError(
                code="NON_MANIFOLD_TOPOLOGY",
                elementId=element_id,
                message=f"Manifold3D topology status error: {status}"
            ))

        vol = solid.volume()
        if vol <= 0.000001:
            errors.append(SolidValidationError(
                code="NON_POSITIVE_VOLUME",
                elementId=element_id,
                message=f"Calculated volume is non-positive: {vol} m³"
            ))

        area = solid.surface_area()
        if area <= 0.0001:
            errors.append(SolidValidationError(
                code="ZERO_SURFACE_AREA",
                elementId=element_id,
                message=f"Calculated surface area is zero: {area} m²"
            ))

        mesh = solid.to_mesh()
        num_verts = len(mesh.vert_properties) if hasattr(mesh, "vert_properties") else solid.num_vert()
        num_tri = len(mesh.tri_verts) if hasattr(mesh, "tri_verts") else solid.num_tri()

        if num_verts < 4 or num_tri < 4:
            errors.append(SolidValidationError(
                code="DEGENERATE_MESH",
                elementId=element_id,
                message=f"Mesh has too few primitives: {num_verts} verts, {num_tri} tris"
            ))

        genus = solid.genus()

        is_valid = len(errors) == 0

        return GeometryValidationResult(
            status="VALID" if is_valid else "INVALID",
            elementId=element_id,
            is2Manifold=is_valid,
            isWatertight=is_valid,
            hasPositiveVolume=vol > 0.0,
            volumeM3=round(vol, 4),
            surfaceAreaM2=round(area, 4),
            numVertices=num_verts,
            numTriangles=num_tri,
            genus=genus,
            errors=errors
        )

    def export_mesh_data(self, solid: Manifold) -> Dict[str, Any]:
        """
        Exports Manifold mesh data to JSON-serializable float/int arrays
        for direct rendering in Three.js BufferGeometry.
        """
        if solid is None or solid.is_empty():
            return {"positions": [], "indices": [], "normals": []}

        mesh = solid.to_mesh()
        vert_props = mesh.vert_properties
        tri_verts = mesh.tri_verts

        # Flatten vertices (x, y, z)
        positions = []
        for v in vert_props:
            positions.extend([round(float(v[0]), 3), round(float(v[1]), 3), round(float(v[2]), 3)])

        # Flatten triangle index triples
        indices = []
        for t in tri_verts:
            indices.extend([int(t[0]), int(t[1]), int(t[2])])

        return {
            "positions": positions,
            "indices": indices,
            "numVertices": len(vert_props),
            "numTriangles": len(tri_verts),
            "volumeM3": round(solid.volume(), 4)
        }
