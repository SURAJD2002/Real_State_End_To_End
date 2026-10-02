"""
Planwise Enterprise — Deterministic Canonical Building Model Compiler
Delta Specification §1, §7, §8, §10, §12, §13, §14, §26

Compiles high-level room programs & CP-SAT layouts into the Authoritative
Planwise Canonical Building Model. All geometric coordinates, topology,
elements, openings, levels, materials, and structural grids are synthesized
deterministically.
"""

from typing import List, Dict, Any, Tuple, Optional
import math
import hashlib
from datetime import datetime

from packages.schemas.building_model import (
    CanonicalBuildingModel,
    BuildingLevel,
    Space,
    Bounds2D,
    SpaceZone,
    BuildingElement,
    ElementType,
    WallType,
    StructuralRole,
    SlabType,
    StairType,
    ElementGeometry,
    Opening,
    OpeningType,
    StructuralGrid,
    GridLine,
    Material,
    MaterialAssignment,
    BuildingSystem,
    SystemComponent,
    ModelMetadata,
    BUILDING_MODEL_SCHEMA_VERSION
)
from workers.generation.validation_engine import validate_building_model


def get_standard_material_catalog() -> List[Material]:
    """Returns the versioned canonical material catalog for Q3 2026."""
    return [
        Material(
            materialId="AAC_BLOCK_200",
            catalogVersion="2026.Q3",
            category="MASONRY",
            name="Autoclaved Aerated Concrete (AAC) Block 200mm",
            grade="Grade 1 IS 2185-3",
            unit="m²",
            baseUnitRateInr=1850.0
        ),
        Material(
            materialId="AAC_BLOCK_100",
            catalogVersion="2026.Q3",
            category="MASONRY",
            name="Internal AAC Partition Block 100mm",
            grade="Grade 1 IS 2185-3",
            unit="m²",
            baseUnitRateInr=1250.0
        ),
        Material(
            materialId="RCC_M25_FE500",
            catalogVersion="2026.Q3",
            category="CONCRETE",
            name="Design Mix Concrete M25 with Fe500D TMT Reinforcement",
            grade="M25 / Fe500D",
            unit="m³",
            baseUnitRateInr=7200.0
        ),
        Material(
            materialId="VITRIFIED_TILE_800",
            catalogVersion="2026.Q3",
            category="FINISHES",
            name="Double Charged Vitrified Tiles (800x800mm nano-sealed)",
            grade="Class 1 Heavy Duty",
            unit="m²",
            baseUnitRateInr=1850.0
        ),
        Material(
            materialId="CERAMIC_ANTI_SKID",
            catalogVersion="2026.Q3",
            category="FINISHES",
            name="Anti-Skid Matte Ceramic Floor Tiles (300x300mm)",
            grade="Group 4 Anti-Slip",
            unit="m²",
            baseUnitRateInr=1350.0
        ),
        Material(
            materialId="FLUSH_DOOR_35MM",
            catalogVersion="2026.Q3",
            category="JOINERY",
            name="Solid Core BWP Wooden Flush Door (35mm) with Mortise Hardware",
            grade="IS 2202 BWP",
            unit="no.",
            baseUnitRateInr=11500.0
        ),
        Material(
            materialId="UPVC_WINDOW_3TRACK",
            catalogVersion="2026.Q3",
            category="JOINERY",
            name="UPVC 3-Track Sliding/Casement Window with Toughened Glass",
            grade="Class A Heavy uPVC",
            unit="no.",
            baseUnitRateInr=9500.0
        ),
        Material(
            materialId="CEMENT_PLASTER_EXT",
            catalogVersion="2026.Q3",
            category="FINISHES",
            name="20mm Double Coat Sand-Faced Waterproof Cement Plaster",
            grade="1:4 Cement Sand",
            unit="m²",
            baseUnitRateInr=420.0
        ),
        Material(
            materialId="CEMENT_PLASTER_INT",
            catalogVersion="2026.Q3",
            category="FINISHES",
            name="12mm Single Coat Smooth Neeru Cement Plaster",
            grade="1:3 Cement Sand",
            unit="m²",
            baseUnitRateInr=310.0
        )
    ]


def build_wall_polygon(p1: List[float], p2: List[float], thickness_m: float) -> List[List[float]]:
    """
    Computes a 2D closed polygon for a wall segment given its centerline and thickness.
    """
    x1, y1 = p1
    x2, y2 = p2
    dx = x2 - x1
    dy = y2 - y1
    length = math.hypot(dx, dy)
    if length == 0:
        return [[x1, y1], [x2, y2], [x2, y2], [x1, y1], [x1, y1]]

    # Normal vector perpendicular to centerline
    nx = -dy / length * (thickness_m / 2.0)
    ny = dx / length * (thickness_m / 2.0)

    return [
        [round(x1 + nx, 3), round(y1 + ny, 3)],
        [round(x2 + nx, 3), round(y2 + ny, 3)],
        [round(x2 - nx, 3), round(y2 - ny, 3)],
        [round(x1 - nx, 3), round(y1 - ny, 3)],
        [round(x1 + nx, 3), round(y1 + ny, 3)]
    ]


def compile_canonical_building_model(
    layout_data: Optional[Dict[str, Any]] = None,
    design_version_id: str = "DV-001",
    project_id: str = "proj-mumbai-default-01",
    site_geometry_version_id: str = "PV-001",
    regulation_version_id: str = "MUMBAI_DCPR_2034_V1",
    archetype: Optional[str] = None
) -> CanonicalBuildingModel:
    """
    Deterministic compiler: Transforms raw layout data / room program
    into the full Canonical Building Model.
    """
    if layout_data is None:
        layout_data = {}
    if archetype:
        layout_data["archetype"] = archetype
    archetype = layout_data.get("archetype", archetype or "compact_2bhk")
    envelope = layout_data.get("buildingEnvelope", {"widthM": 14.0, "lengthM": 14.0, "heightM": 3.6})
    total_bua = layout_data.get("totalGrossBUASqm", 95.0)
    total_usable = layout_data.get("totalUsableAreaSqm", 82.0)
    floors_count = layout_data.get("floors", 1)
    label = layout_data.get("label", "Compact 2BHK Contemporary")
    description = layout_data.get("description", "Architectural model compiled from layout intent")

    if not layout_data.get("rooms"):
        from workers.generation.house_generator import solve_room_allocation
        solved = solve_room_allocation(archetype, envelope.get("widthM", 14.0), envelope.get("lengthM", 14.0))
        layout_data.update(solved)
        envelope = layout_data.get("buildingEnvelope", envelope)
        total_bua = layout_data.get("totalGrossBUASqm", total_bua)
        total_usable = layout_data.get("totalUsableAreaSqm", total_usable)
        floors_count = layout_data.get("floors", floors_count)
        label = layout_data.get("label", label)
        description = layout_data.get("description", description)

    model_id = f"BLDG-{archetype.upper()}-{design_version_id[:8]}"

    # 1. Building Levels
    floor_height = 3.15
    levels = [
        BuildingLevel(
            levelId="LVL-000",
            levelIndex=0,
            name="GROUND",
            elevationM=0.0,
            floorToFloorHeightM=floor_height,
            usage="RESIDENTIAL"
        )
    ]
    if floors_count > 1:
        levels.append(
            BuildingLevel(
                levelId="LVL-001",
                levelIndex=1,
                name="FIRST",
                elevationM=floor_height,
                floorToFloorHeightM=floor_height,
                usage="RESIDENTIAL"
            )
        )
    levels.append(
        BuildingLevel(
            levelId="LVL-ROOF",
            levelIndex=floors_count,
            name="TERRACE",
            elevationM=round(floors_count * floor_height, 2),
            floorToFloorHeightM=1.0,
            usage="TERRACE_PARAPET"
        )
    )

    # 2. Spaces (Rooms)
    raw_rooms = layout_data.get("rooms", [])
    spaces: List[Space] = []

    for idx, r in enumerate(raw_rooms):
        b = r["bounds"]
        x, y, w, h = b["x"], b["y"], b["width"], b["height"]
        polygon = [
            [round(x, 2), round(y, 2)],
            [round(x + w, 2), round(y, 2)],
            [round(x + w, 2), round(y + h, 2)],
            [round(x, 2), round(y + h, 2)],
            [round(x, 2), round(y, 2)]
        ]
        perimeter = round(2 * (w + h), 2)
        centroid = [round(x + w / 2.0, 2), round(y + h / 2.0, 2)]
        floor_ref = r.get("floor", "L0")
        lvl_id = "LVL-001" if floor_ref == "L1" else "LVL-000"

        zone_str = r.get("zone", "PUBLIC")
        zone_map = {
            "PUBLIC": SpaceZone.PUBLIC,
            "PRIVATE": SpaceZone.PRIVATE,
            "SERVICE": SpaceZone.SERVICE,
            "CIRCULATION": SpaceZone.CIRCULATION,
            "SEMI_OUTDOOR": SpaceZone.SEMI_OUTDOOR,
            "OUTDOOR": SpaceZone.OUTDOOR
        }

        s_id = f"SPACE-{str(r['id']).upper().replace(' ', '_')}"

        spaces.append(
            Space(
                spaceId=s_id,
                levelId=lvl_id,
                spaceType=r['id'].upper(),
                name=r["name"],
                zone=zone_map.get(zone_str, SpaceZone.PUBLIC),
                floor=floor_ref,
                color=r.get("color", "#60a5fa"),
                bounds=Bounds2D(x=round(x, 2), y=round(y, 2), width=round(w, 2), height=round(h, 2)),
                polygon=polygon,
                areaSqm=round(w * h, 2),
                perimeterM=perimeter,
                centroid=centroid,
                heightM=3.0,
                daylightRequirement="DIRECT_NATURAL" if zone_str in ["PUBLIC", "PRIVATE"] else "VENT_SHAFT",
                ventilationRequirement="CROSS_VENT" if zone_str in ["PUBLIC", "PRIVATE"] else "MECHANICAL_OR_LOUVER",
                privacyRating="HIGH" if zone_str == "PRIVATE" else "LOW",
                adjacentSpaceIds=[],
                boundaryWallIds=[]
            )
        )

    # Compute Space Adjacencies (Topological neighbor graph)
    for i, s1 in enumerate(spaces):
        b1 = s1.bounds
        for j, s2 in enumerate(spaces):
            if i >= j or s1.levelId != s2.levelId:
                continue
            b2 = s2.bounds
            # Check if boundaries touch (within 0.05m tolerance)
            touches_x = abs(b1.x + b1.width - b2.x) < 0.05 or abs(b2.x + b2.width - b1.x) < 0.05
            overlaps_y = min(b1.y + b1.height, b2.y + b2.height) - max(b1.y, b2.y) > 0.1

            touches_y = abs(b1.y + b1.height - b2.y) < 0.05 or abs(b2.y + b2.height - b1.y) < 0.05
            overlaps_x = min(b1.x + b1.width, b2.x + b2.width) - max(b1.x, b2.x) > 0.1

            if (touches_x and overlaps_y) or (touches_y and overlaps_x):
                s1.adjacentSpaceIds.append(s2.spaceId)
                s2.adjacentSpaceIds.append(s1.spaceId)

    # 3. Building Elements: Walls
    elements: List[BuildingElement] = []
    openings: List[Opening] = []
    wall_counter = 1

    # Exterior Envelope Walls (200mm AAC blocks)
    ew_width = envelope["widthM"]
    ew_length = envelope["lengthM"]
    ext_wall_thickness = 0.20
    int_wall_thickness = 0.10

    exterior_edges = [
        ("EXT-N", [[0.0, 0.0], [ew_width, 0.0]], "NORTH"),
        ("EXT-E", [[ew_width, 0.0], [ew_width, ew_length]], "EAST"),
        ("EXT-S", [[ew_width, ew_length], [0.0, ew_length]], "SOUTH"),
        ("EXT-W", [[0.0, ew_length], [0.0, 0.0]], "WEST")
    ]

    for edge_tag, c_line, orient in exterior_edges:
        wall_id = f"WALL-EXT-{wall_counter:03d}"
        wall_counter += 1
        fp = build_wall_polygon(c_line[0], c_line[1], ext_wall_thickness)

        elements.append(
            BuildingElement(
                elementId=wall_id,
                elementType=ElementType.WALL,
                levelId="LVL-000",
                name=f"Exterior Envelope Wall ({orient})",
                geometry=ElementGeometry(
                    centerline=c_line,
                    footprintPolygon=fp,
                    baseZ=0.0,
                    topZ=floor_height,
                    thicknessM=ext_wall_thickness,
                    heightM=floor_height
                ),
                materialId="AAC_BLOCK_200",
                structuralRole=StructuralRole.LOADBEARING,
                wallType=WallType.EXTERNAL,
                properties={"orientation": orient, "fireRatingHours": 2.0}
            )
        )

    # Interior Partition Walls (100mm AAC blocks) derived from space boundaries
    for s in spaces:
        b = s.bounds
        # Internal horizontal divide
        if b.y > 0.01:
            w_id = f"WALL-INT-{wall_counter:03d}"
            wall_counter += 1
            c_line = [[b.x, b.y], [b.x + b.width, b.y]]
            fp = build_wall_polygon(c_line[0], c_line[1], int_wall_thickness)

            elements.append(
                BuildingElement(
                    elementId=w_id,
                    elementType=ElementType.WALL,
                    levelId=s.levelId,
                    name=f"Internal Partition Wall ({s.name})",
                    geometry=ElementGeometry(
                        centerline=c_line,
                        footprintPolygon=fp,
                        baseZ=0.0 if s.levelId == "LVL-000" else floor_height,
                        topZ=floor_height if s.levelId == "LVL-000" else floor_height * 2,
                        thicknessM=int_wall_thickness,
                        heightM=floor_height
                    ),
                    materialId="AAC_BLOCK_100",
                    structuralRole=StructuralRole.NON_LOADBEARING,
                    wallType=WallType.PARTITION,
                    connectedSpaceIds=[s.spaceId],
                    properties={"soundTransmissionClass": 45}
                )
            )
            s.boundaryWallIds.append(w_id)

    # 4. Openings (Doors & Windows) Hosted by Walls
    opening_counter = 1
    ext_walls = [e for e in elements if e.elementType == ElementType.WALL and e.wallType == WallType.EXTERNAL]
    int_walls = [e for e in elements if e.elementType == ElementType.WALL and e.wallType == WallType.PARTITION]

    # Main Entrance Door on South or North external wall
    if ext_walls:
        host_w = ext_walls[0]
        d_id = f"DOOR-{opening_counter:03d}"
        opening_counter += 1
        pos_x = host_w.geometry.centerline[0][0] + 2.0
        pos_y = host_w.geometry.centerline[0][1]

        openings.append(
            Opening(
                openingId=d_id,
                openingType=OpeningType.DOOR,
                hostWallId=host_w.elementId,
                levelId="LVL-000",
                name="Main Entrance Door (D1)",
                widthM=1.05,
                heightM=2.10,
                sillHeightM=0.0,
                positionRatio=0.25,
                positionM=[pos_x, pos_y],
                swing="RIGHT_INWARD",
                materialId="FLUSH_DOOR_35MM",
                properties={"type": "ENTRANCE_TEAK_FINISH"}
            )
        )
        host_w.openingIds.append(d_id)

    # Interior Doors for each room
    for s in spaces:
        b = s.bounds
        matching_wall = None
        for w in int_walls:
            if s.spaceId in w.connectedSpaceIds:
                matching_wall = w
                break
        if not matching_wall and int_walls:
            matching_wall = int_walls[0]

        if matching_wall:
            d_id = f"DOOR-{opening_counter:03d}"
            opening_counter += 1
            is_toilet = "bath" in s.spaceType.lower() or "toilet" in s.spaceType.lower()
            door_w = 0.80 if is_toilet else 0.90

            openings.append(
                Opening(
                    openingId=d_id,
                    openingType=OpeningType.DOOR,
                    hostWallId=matching_wall.elementId,
                    levelId=s.levelId,
                    name=f"Door to {s.name}",
                    widthM=door_w,
                    heightM=2.10,
                    sillHeightM=0.0,
                    positionRatio=0.5,
                    positionM=[round(b.x + b.width / 2.0, 2), round(b.y, 2)],
                    swing="LEFT_INWARD",
                    materialId="FLUSH_DOOR_35MM"
                )
            )
            matching_wall.openingIds.append(d_id)

    # Windows on Exterior Envelope Walls for daylight & ventilation
    win_counter = 1
    for s in spaces:
        b = s.bounds
        # Check if room touches exterior boundary
        touches_left = b.x <= 0.05
        touches_right = abs(b.x + b.width - ew_width) <= 0.05
        touches_top = b.y <= 0.05
        touches_bottom = abs(b.y + b.height - ew_length) <= 0.05

        if touches_left or touches_right or touches_top or touches_bottom:
            w_id = f"WIN-{win_counter:03d}"
            win_counter += 1
            is_service = s.zone == SpaceZone.SERVICE
            win_w = 0.60 if is_service else 1.50
            win_h = 0.60 if is_service else 1.20
            sill_h = 1.50 if is_service else 0.90

            # Determine position along wall
            if touches_left:
                pos = [0.0, round(b.y + b.height / 2.0, 2)]
                host_wall = next((w for w in ext_walls if "WEST" in w.name), ext_walls[0])
            elif touches_right:
                pos = [ew_width, round(b.y + b.height / 2.0, 2)]
                host_wall = next((w for w in ext_walls if "EAST" in w.name), ext_walls[0])
            elif touches_top:
                pos = [round(b.x + b.width / 2.0, 2), 0.0]
                host_wall = next((w for w in ext_walls if "NORTH" in w.name), ext_walls[0])
            else:
                pos = [round(b.x + b.width / 2.0, 2), ew_length]
                host_wall = next((w for w in ext_walls if "SOUTH" in w.name), ext_walls[0])

            openings.append(
                Opening(
                    openingId=w_id,
                    openingType=OpeningType.WINDOW,
                    hostWallId=host_wall.elementId,
                    levelId=s.levelId,
                    name=f"Window for {s.name}",
                    widthM=win_w,
                    heightM=win_h,
                    sillHeightM=sill_h,
                    positionRatio=0.5,
                    positionM=pos,
                    materialId="UPVC_WINDOW_3TRACK",
                    properties={"glazing": "5mm_TOUGHENED_CLEAR", "mosquitoMesh": True}
                )
            )
            host_wall.openingIds.append(w_id)

    # 5. Structural Grid & Reinforced Concrete Columns
    col_spacing = 4.0
    num_gx = max(2, int(ew_width / col_spacing) + 1)
    num_gy = max(2, int(ew_length / col_spacing) + 1)

    grid_letters = ["A", "B", "C", "D", "E", "F", "G"]
    grid_lines_x = [GridLine(tag=grid_letters[ix % len(grid_letters)], coordinate=round(min(ew_width, ix * col_spacing), 2), direction="X") for ix in range(num_gx)]
    grid_lines_y = [GridLine(tag=str(iy + 1), coordinate=round(min(ew_length, iy * col_spacing), 2), direction="Y") for iy in range(num_gy)]

    structural_grid = StructuralGrid(
        gridLinesX=grid_lines_x,
        gridLinesY=grid_lines_y,
        baySpacingXM=col_spacing,
        baySpacingYM=col_spacing
    )

    col_counter = 1
    for gx in grid_lines_x:
        for gy in grid_lines_y:
            col_id = f"COL-{gx.tag}{gy.tag}"
            col_counter += 1
            cx, cy = gx.coordinate, gy.coordinate
            cw_m = 0.30
            cd_m = 0.45

            col_poly = [
                [round(cx - cw_m / 2.0, 3), round(cy - cd_m / 2.0, 3)],
                [round(cx + cw_m / 2.0, 3), round(cy - cd_m / 2.0, 3)],
                [round(cx + cw_m / 2.0, 3), round(cy + cd_m / 2.0, 3)],
                [round(cx - cw_m / 2.0, 3), round(cy + cd_m / 2.0, 3)],
                [round(cx - cw_m / 2.0, 3), round(cy - cd_m / 2.0, 3)]
            ]

            elements.append(
                BuildingElement(
                    elementId=col_id,
                    elementType=ElementType.COLUMN,
                    levelId="LVL-000",
                    name=f"Structural RCC Column ({gx.tag}-{gy.tag})",
                    geometry=ElementGeometry(
                        footprintPolygon=col_poly,
                        baseZ=0.0,
                        topZ=floor_height * floors_count,
                        widthM=cw_m,
                        depthM=cd_m,
                        heightM=floor_height * floors_count
                    ),
                    materialId="RCC_M25_FE500",
                    structuralRole=StructuralRole.PRIMARY_FRAME,
                    gridReference=f"{gx.tag}-{gy.tag}",
                    properties={
                        "rebarSchedule": "8-T16_Fe500D", 
                        "tieSpacingMm": 150,
                        "widthMm": int(cw_m * 1000),
                        "depthMm": int(cd_m * 1000),
                        "x": cx,
                        "y": cy
                    }
                )
            )

    # 6. Reinforced Concrete Floor & Roof Slabs
    slab_polygon = [
        [0.0, 0.0],
        [ew_width, 0.0],
        [ew_width, ew_length],
        [0.0, ew_length],
        [0.0, 0.0]
    ]

    # Plinth Slab (Ground Plate)
    elements.append(
        BuildingElement(
            elementId="SLAB-PLINTH",
            elementType=ElementType.SLAB,
            levelId="LVL-000",
            name="Ground Floor Plinth Beam & Slab",
            geometry=ElementGeometry(
                footprintPolygon=slab_polygon,
                baseZ=-0.15,
                topZ=0.0,
                thicknessM=0.15,
                heightM=0.15
            ),
            materialId="RCC_M25_FE500",
            structuralRole=StructuralRole.FOUNDATION,
            properties={"slabType": SlabType.PLINTH}
        )
    )

    # Intermediate Floor Slab (if multi-storey)
    if floors_count > 1:
        elements.append(
            BuildingElement(
                elementId="SLAB-L1",
                elementType=ElementType.SLAB,
                levelId="LVL-001",
                name="First Floor Two-Way Suspended RCC Slab",
                geometry=ElementGeometry(
                    footprintPolygon=slab_polygon,
                    baseZ=floor_height - 0.15,
                    topZ=floor_height,
                    thicknessM=0.15,
                    heightM=0.15
                ),
                materialId="RCC_M25_FE500",
                structuralRole=StructuralRole.PRIMARY_FRAME,
                properties={"slabType": SlabType.FLOOR}
            )
        )

    # Roof & Terrace Slab
    top_elevation = round(floors_count * floor_height, 2)
    elements.append(
        BuildingElement(
            elementId="SLAB-ROOF",
            elementType=ElementType.SLAB,
            levelId="LVL-ROOF",
            name="Terrace RCC Roof Slab with Waterproofing",
            geometry=ElementGeometry(
                footprintPolygon=slab_polygon,
                baseZ=top_elevation - 0.15,
                topZ=top_elevation,
                thicknessM=0.15,
                heightM=0.15
            ),
            materialId="RCC_M25_FE500",
            structuralRole=StructuralRole.PRIMARY_FRAME,
            properties={"slabType": SlabType.ROOF, "insulation": "BRICK_BAT_COBA"}
        )
    )

    # 7. Stairs (for multi-level duplex)
    if floors_count > 1:
        stair_poly = [
            [ew_width * 0.45, 0.0],
            [ew_width * 0.45 + 2.40, 0.0],
            [ew_width * 0.45 + 2.40, 3.60],
            [ew_width * 0.45, 3.60],
            [ew_width * 0.45, 0.0]
        ]
        elements.append(
            BuildingElement(
                elementId="STAIR-001",
                elementType=ElementType.STAIR,
                levelId="LVL-000",
                name="Dog-Legged Reinforced Concrete Staircase",
                geometry=ElementGeometry(
                    footprintPolygon=stair_poly,
                    baseZ=0.0,
                    topZ=floor_height,
                    widthM=1.05,
                    heightM=floor_height
                ),
                materialId="RCC_M25_FE500",
                structuralRole=StructuralRole.PRIMARY_FRAME,
                properties={
                    "riserMm": 175,
                    "treadMm": 250,
                    "numberOfRisers": 18,
                    "landingCount": 1,
                    "stairType": StairType.U_SHAPE
                }
            )
        )

    # 8. Preliminary MEP Systems
    elec_components = []
    plumb_components = []

    for s in spaces:
        c = s.centroid
        elec_components.append(
            SystemComponent(
                componentId=f"ELEC-LT-{s.spaceId}",
                componentType="LIGHT_POINT",
                levelId=s.levelId,
                spaceId=s.spaceId,
                position=[c[0], c[1], 2.80],
                specification="LED Downlight 15W Concealed"
            )
        )
        elec_components.append(
            SystemComponent(
                componentId=f"ELEC-SK-{s.spaceId}",
                componentType="SOCKET_POINT",
                levelId=s.levelId,
                spaceId=s.spaceId,
                position=[round(s.bounds.x + 0.30, 2), round(s.bounds.y + 0.30, 2), 0.45],
                specification="6A/16A Modular Universal Socket"
            )
        )

        if s.zone == SpaceZone.SERVICE:
            plumb_components.append(
                SystemComponent(
                    componentId=f"PLB-DRAIN-{s.spaceId}",
                    componentType="DRAIN_TRAP",
                    levelId=s.levelId,
                    spaceId=s.spaceId,
                    position=[c[0], c[1], 0.0],
                    specification="Nahani Trap with Stainless Steel Grating"
                )
            )

    systems = [
        BuildingSystem(systemId="SYS-ELEC-01", systemType="ELECTRICAL", components=elec_components),
        BuildingSystem(systemId="SYS-PLUMB-01", systemType="PLUMBING", components=plumb_components)
    ]

    materials = get_standard_material_catalog()

    model = CanonicalBuildingModel(
        schemaVersion=BUILDING_MODEL_SCHEMA_VERSION,
        modelId=model_id,
        designVersionId=design_version_id,
        projectId=project_id,
        siteGeometryVersionId=site_geometry_version_id,
        regulationVersionId=regulation_version_id,
        name=label,
        archetype=archetype,
        description=description,
        buildingEnvelope=envelope,
        totalGrossBUASqm=total_bua,
        totalUsableAreaSqm=total_usable,
        floorsCount=floors_count,
        levels=levels,
        spaces=spaces,
        elements=elements,
        openings=openings,
        structuralGrid=structural_grid,
        materials=materials,
        systems=systems,
        metadata=ModelMetadata(
            engineName="planwise-canonical-compiler",
            engineVersion="1.0.0",
            compilationTimestamp=datetime.utcnow().isoformat(),
            modelHash="",
            isLocked=False
        )
    )

    # Validate canonical model (§26, §27)
    model.validation = validate_building_model(model)

    # Compute deterministic fingerprint (§36, §37)
    model.metadata.modelHash = f"sha256:{model.compute_hash()}"
    return model


compile_building_model = compile_canonical_building_model
