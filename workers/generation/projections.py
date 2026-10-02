"""
Planwise Enterprise — Deterministic Building Model Projections Engine
Delta Specification §28, §29, §30, §31, §32

Generates authoritative architectural projections directly from the Canonical Building Model:
1. 2D Floor Plan (spaces, walls, doors, windows, columns, grid)
2. Elevation (North, South, East, West facades, level datums, fenestration)
3. Section (Cut walls, slabs, stairs, heights, spatial voids)
4. 3D BIM Scene (Meshes tagged with canonicalElementId for Three.js)

Single Source of Truth (§Critical Principle):
Projections are purely mathematical derivations and NEVER invent independent geometry.
"""

from typing import Dict, Any, List, Optional
import math

from packages.schemas.building_model import (
    CanonicalBuildingModel,
    ElementType,
    WallType,
    OpeningType
)


def generate_floor_plan(
    model: CanonicalBuildingModel,
    level_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    §29 Floor Plan Projection:
    Extracts spaces, walls, openings, columns, and grid lines for a specific level.
    Defaults to the lowest residential level (LVL-000).
    """
    target_level = level_id or (model.levels[0].levelId if model.levels else "LVL-000")
    level_obj = next((lvl for lvl in model.levels if lvl.levelId == target_level), None)
    
    # 1. Filter Spaces
    level_spaces = [
        {
            "spaceId": s.spaceId,
            "name": s.name,
            "spaceType": s.spaceType,
            "zone": s.zone.value if hasattr(s.zone, "value") else str(s.zone),
            "floor": s.floor,
            "color": s.color,
            "bounds": s.bounds.dict(),
            "polygon": s.polygon,
            "areaSqm": s.areaSqm,
            "perimeterM": s.perimeterM,
            "centroid": s.centroid,
            "heightM": s.heightM,
            "adjacentSpaceIds": s.adjacentSpaceIds
        }
        for s in model.spaces
        if s.levelId == target_level
    ]

    # 2. Filter Walls
    level_walls = [
        {
            "elementId": e.elementId,
            "elementType": e.elementType.value,
            "wallType": e.wallType.value if e.wallType else "PARTITION",
            "name": e.name,
            "materialId": e.materialId,
            "thicknessM": (e.geometry.thicknessM if e.geometry else 0.20) or 0.20,
            "heightM": (e.geometry.heightM if e.geometry else 3.15) or 3.15,
            "centerline": e.geometry.centerline if e.geometry else [],
            "footprintPolygon": e.geometry.footprintPolygon if e.geometry else [],
            "openingIds": e.openingIds,
            "connectedSpaceIds": e.connectedSpaceIds,
            "properties": e.properties
        }
        for e in model.elements
        if e.elementType == ElementType.WALL and e.levelId == target_level
    ]

    # 3. Filter Columns
    level_columns = [
        {
            "elementId": e.elementId,
            "gridReference": e.properties.get("gridRef", ""),
            "x": e.properties.get("x", 0.0),
            "y": e.properties.get("y", 0.0),
            "widthM": round(e.properties.get("widthMm", 300) / 1000.0, 3),
            "depthM": round(e.properties.get("depthMm", 450) / 1000.0, 3),
            "materialId": e.materialId,
            "structuralRole": e.structuralRole.value if e.structuralRole else "PRIMARY_FRAME"
        }
        for e in model.elements
        if e.elementType == ElementType.COLUMN and e.levelId == target_level
    ]

    # 4. Filter Openings (Doors & Windows)
    level_openings = [
        {
            "openingId": o.openingId,
            "openingType": o.openingType.value,
            "hostWallId": o.hostWallId,
            "widthM": o.widthM,
            "heightM": o.heightM,
            "sillHeightM": o.sillHeightM,
            "positionM": o.positionM,
            "swing": o.properties.get("swing", "LEFT_90"),
            "clearWidthMm": o.properties.get("clearWidthMm", int(o.widthM * 1000)),
            "windowType": o.properties.get("windowType", "SLIDING_2_TRACK")
        }
        for o in model.openings
        if o.levelId == target_level
    ]

    doors = [op for op in level_openings if op["openingType"] == OpeningType.DOOR.value]
    windows = [op for op in level_openings if op["openingType"] == OpeningType.WINDOW.value]

    # 5. Stairs (if present on level)
    stairs = [
        {
            "elementId": e.elementId,
            "stairType": e.properties.get("stairType", "STRAIGHT"),
            "footprintPolygon": e.geometry.footprintPolygon if e.geometry else [],
            "riserMm": e.properties.get("riserMm", 175),
            "treadMm": e.properties.get("treadMm", 250),
            "numberOfRisers": e.properties.get("numberOfRisers", 18)
        }
        for e in model.elements
        if e.elementType == ElementType.STAIR and e.levelId == target_level
    ]

    return {
        "designVersionId": model.designVersionId,
        "modelId": model.modelId,
        "modelHash": model.metadata.modelHash,
        "level": {
            "levelId": target_level,
            "name": level_obj.name if level_obj else "GROUND",
            "elevationM": level_obj.elevationM if level_obj else 0.0,
            "floorToFloorHeightM": level_obj.floorToFloorHeightM if level_obj else 3.15
        },
        "buildingEnvelope": model.buildingEnvelope,
        "structuralGrid": model.structuralGrid.dict() if model.structuralGrid else {},
        "spaces": level_spaces,
        "walls": level_walls,
        "doors": doors,
        "windows": windows,
        "columns": level_columns,
        "stairs": stairs,
        "statistics": {
            "totalSpaces": len(level_spaces),
            "totalWalls": len(level_walls),
            "totalDoors": len(doors),
            "totalWindows": len(windows),
            "totalColumns": len(level_columns)
        }
    }


def generate_elevation(
    model: CanonicalBuildingModel,
    facade_direction: str = "SOUTH"
) -> Dict[str, Any]:
    """
    §30 Elevation Projection:
    Computes deterministic facade projection for North, South, East, or West.
    Transforms 3D wall footprints and openings into a 2D orthographic elevation view.
    """
    direction = facade_direction.upper()
    env_w = model.buildingEnvelope.get("widthM", 14.0)
    env_l = model.buildingEnvelope.get("lengthM", 14.0)
    total_h = model.buildingEnvelope.get("heightM", 3.6)

    # Elevation axis bounds: (u is horizontal coordinate on facade, z is vertical elevation)
    u_max = env_w if direction in ["SOUTH", "NORTH"] else env_l

    # Collect visible level marker lines
    level_markers = [
        {
            "levelId": lvl.levelId,
            "name": lvl.name,
            "elevationM": lvl.elevationM,
            "u1": -0.5,
            "u2": round(u_max + 0.5, 2)
        }
        for lvl in model.levels
    ]

    # Collect facade exterior walls
    facade_walls = []
    for elem in model.elements:
        if elem.elementType == ElementType.WALL and elem.wallType == WallType.EXTERNAL:
            orient = elem.properties.get("orientation", "")
            if orient == direction:
                c_line = elem.geometry.centerline if elem.geometry else []
                if len(c_line) >= 2:
                    # In South/North facade, horizontal axis is X
                    # In East/West facade, horizontal axis is Y
                    if direction in ["SOUTH", "NORTH"]:
                        u1 = min(c_line[0][0], c_line[1][0])
                        u2 = max(c_line[0][0], c_line[1][0])
                    else:
                        u1 = min(c_line[0][1], c_line[1][1])
                        u2 = max(c_line[0][1], c_line[1][1])

                    facade_walls.append({
                        "elementId": elem.elementId,
                        "name": elem.name,
                        "u": round(u1, 2),
                        "z": round(elem.geometry.baseZ if elem.geometry else 0.0, 2),
                        "width": round(u2 - u1, 2),
                        "height": round(elem.geometry.heightM if elem.geometry else 3.15, 2),
                        "materialId": elem.materialId
                    })

    # Collect openings hosted by these facade walls
    facade_wall_ids = {w["elementId"] for w in facade_walls}
    facade_openings = []

    for op in model.openings:
        if op.hostWallId in facade_wall_ids:
            host = next((w for w in facade_walls if w["elementId"] == op.hostWallId), None)
            if host:
                u_pos = round(host["u"] + op.positionM, 2)
                z_pos = round(host["z"] + op.sillHeightM, 2)
                facade_openings.append({
                    "openingId": op.openingId,
                    "openingType": op.openingType.value,
                    "hostWallId": op.hostWallId,
                    "u": u_pos,
                    "z": z_pos,
                    "width": op.widthM,
                    "height": op.heightM,
                    "sillHeightM": op.sillHeightM,
                    "glazing": op.properties.get("glass", "TINTED_TOUGHENED_5MM")
                })

    # Slab bands across facade
    slab_bands = []
    for lvl in model.levels:
        slab_bands.append({
            "name": f"{lvl.name} Slab Band",
            "u": 0.0,
            "z": lvl.elevationM,
            "width": round(u_max, 2),
            "thickness": 0.15
        })

    return {
        "designVersionId": model.designVersionId,
        "modelId": model.modelId,
        "modelHash": model.metadata.modelHash,
        "facadeDirection": direction,
        "bounds": {
            "uMin": 0.0,
            "uMax": round(u_max, 2),
            "zMin": 0.0,
            "zMax": round(total_h + 1.0, 2)
        },
        "levelMarkers": level_markers,
        "walls": facade_walls,
        "openings": facade_openings,
        "slabBands": slab_bands,
        "groundLine": {"z": 0.0, "u1": -1.0, "u2": round(u_max + 1.0, 2)}
    }


def generate_section(
    model: CanonicalBuildingModel,
    cut_plane: str = "A-A",
    cut_y: Optional[float] = None
) -> Dict[str, Any]:
    """
    §31 Section Projection:
    Computes deterministic transverse section cut along plane Y = cut_y.
    Determines intersecting walls, slabs, rooms, ceiling heights, and stairs.
    """
    env_w = model.buildingEnvelope.get("widthM", 14.0)
    env_l = model.buildingEnvelope.get("lengthM", 14.0)
    total_h = model.buildingEnvelope.get("heightM", 3.6)
    
    # Default cut plane passes through mid-building or staircase
    y_cut = cut_y if cut_y is not None else round(env_l * 0.45, 2)

    # 1. Level Datums
    levels = [
        {
            "levelId": lvl.levelId,
            "name": lvl.name,
            "elevationM": lvl.elevationM,
            "x1": -0.5,
            "x2": round(env_w + 0.5, 2)
        }
        for lvl in model.levels
    ]

    # 2. Intersecting Cut Walls
    cut_walls = []
    background_walls = []

    for elem in model.elements:
        if elem.elementType == ElementType.WALL and elem.geometry:
            c_line = elem.geometry.centerline
            if len(c_line) >= 2:
                # Check if wall intersects y_cut
                y_min = min(c_line[0][1], c_line[1][1])
                y_max = max(c_line[0][1], c_line[1][1])
                th = elem.geometry.thicknessM or 0.20
                ht = elem.geometry.heightM or 3.15
                base_z = elem.geometry.baseZ

                if y_min - 0.05 <= y_cut <= y_max + 0.05:
                    # Wall is cut
                    cut_x = c_line[0][0] if abs(c_line[0][1] - c_line[1][1]) > 0.01 else c_line[0][0]
                    cut_walls.append({
                        "elementId": elem.elementId,
                        "name": elem.name,
                        "x": round(cut_x - th / 2.0, 2),
                        "z": round(base_z, 2),
                        "thickness": round(th, 2),
                        "height": round(ht, 2),
                        "materialId": elem.materialId,
                        "hatchPattern": "AAC_BLOCK_HATCH" if "AAC" in (elem.materialId or "") else "CONCRETE_HATCH"
                    })
                elif y_min > y_cut:
                    # Wall is in the background looking North
                    pass

    # 3. Cut Slabs
    slabs = [
        {
            "elementId": elem.elementId,
            "name": elem.name,
            "x1": 0.0,
            "x2": round(env_w, 2),
            "z": elem.geometry.baseZ if elem.geometry else 0.0,
            "thickness": elem.geometry.thicknessM if elem.geometry else 0.15,
            "materialId": elem.materialId
        }
        for elem in model.elements
        if elem.elementType == ElementType.SLAB
    ]

    # 4. Cut Spaces / Rooms
    cut_spaces = []
    for s in model.spaces:
        b = s.bounds
        if b.y <= y_cut <= b.y + b.height:
            cut_spaces.append({
                "spaceId": s.spaceId,
                "name": s.name,
                "spaceType": s.spaceType,
                "x1": b.x,
                "x2": round(b.x + b.width, 2),
                "clearHeightM": s.heightM,
                "floor": s.floor
            })

    return {
        "designVersionId": model.designVersionId,
        "modelId": model.modelId,
        "modelHash": model.metadata.modelHash,
        "cutPlane": cut_plane,
        "cutY": y_cut,
        "bounds": {
            "xMin": 0.0,
            "xMax": round(env_w, 2),
            "zMin": -0.6,
            "zMax": round(total_h + 1.2, 2)
        },
        "levels": levels,
        "cutWalls": cut_walls,
        "slabs": slabs,
        "cutSpaces": cut_spaces,
        "groundLine": {"z": 0.0, "x1": -1.0, "x2": round(env_w + 1.0, 2)}
    }


def generate_3d(model: CanonicalBuildingModel) -> Dict[str, Any]:
    """
    §32 3D Model Derivation:
    Produces clean volumetric mesh representations for Three.js rendering.
    Every mesh is explicitly tagged with `canonicalElementId` and `elementType`.
    """
    meshes: List[Dict[str, Any]] = []

    # 1. Walls
    for elem in model.elements:
        if elem.elementType == ElementType.WALL and elem.geometry:
            fp = elem.geometry.footprintPolygon
            base_z = elem.geometry.baseZ
            top_z = elem.geometry.topZ
            ht = elem.geometry.heightM or (top_z - base_z)
            is_ext = elem.wallType == WallType.EXTERNAL

            color = "#cbd5e1" if is_ext else "#e2e8f0"
            meshes.append({
                "canonicalElementId": elem.elementId,
                "elementType": "WALL",
                "wallType": elem.wallType.value if elem.wallType else "INTERNAL",
                "levelId": elem.levelId,
                "geometryType": "EXTRUDED_POLYGON",
                "polygon": fp,
                "baseZ": base_z,
                "topZ": top_z,
                "height": round(ht, 2),
                "thickness": elem.geometry.thicknessM or 0.20,
                "material": {
                    "materialId": elem.materialId,
                    "color": color,
                    "roughness": 0.85,
                    "metalness": 0.1,
                    "opacity": 1.0
                },
                "userData": {
                    "elementId": elem.elementId,
                    "name": elem.name,
                    "material": elem.materialId,
                    "levelId": elem.levelId
                }
            })

    # 2. Columns
    for elem in model.elements:
        if elem.elementType == ElementType.COLUMN:
            x = elem.properties.get("x", 0.0)
            y = elem.properties.get("y", 0.0)
            w = round(elem.properties.get("widthMm", 300) / 1000.0, 3)
            d = round(elem.properties.get("depthMm", 450) / 1000.0, 3)
            ht = elem.geometry.heightM if elem.geometry else 3.15
            base_z = elem.geometry.baseZ if elem.geometry else 0.0

            meshes.append({
                "canonicalElementId": elem.elementId,
                "elementType": "COLUMN",
                "levelId": elem.levelId,
                "geometryType": "BOX",
                "position": [x, y, round(base_z + ht / 2.0, 2)],
                "dimensions": [w, d, round(ht, 2)],
                "material": {
                    "materialId": elem.materialId,
                    "color": "#64748b",
                    "roughness": 0.6,
                    "metalness": 0.2,
                    "opacity": 1.0
                },
                "userData": {
                    "elementId": elem.elementId,
                    "name": elem.name,
                    "gridRef": elem.properties.get("gridRef", ""),
                    "material": elem.materialId
                }
            })

    # 3. Slabs
    for elem in model.elements:
        if elem.elementType == ElementType.SLAB and elem.geometry:
            meshes.append({
                "canonicalElementId": elem.elementId,
                "elementType": "SLAB",
                "levelId": elem.levelId,
                "geometryType": "SLAB_PLATE",
                "polygon": elem.geometry.footprintPolygon,
                "elevation": elem.geometry.baseZ,
                "thickness": elem.geometry.thicknessM or 0.15,
                "material": {
                    "materialId": elem.materialId,
                    "color": "#94a3b8",
                    "roughness": 0.7,
                    "metalness": 0.1,
                    "opacity": 0.95
                },
                "userData": {
                    "elementId": elem.elementId,
                    "name": elem.name,
                    "material": elem.materialId
                }
            })

    # 4. Openings (Doors & Windows leaves/frames)
    for op in model.openings:
        is_door = op.openingType == OpeningType.DOOR
        color = "#b45309" if is_door else "#38bdf8"
        opacity = 1.0 if is_door else 0.45

        meshes.append({
            "canonicalElementId": op.openingId,
            "elementType": op.openingType.value,
            "hostWallId": op.hostWallId,
            "levelId": op.levelId,
            "geometryType": "OPENING_PANEL",
            "width": op.widthM,
            "height": op.heightM,
            "sillHeight": op.sillHeightM,
            "material": {
                "color": color,
                "roughness": 0.3,
                "metalness": 0.5,
                "opacity": opacity,
                "transparent": not is_door
            },
            "userData": {
                "openingId": op.openingId,
                "hostWallId": op.hostWallId,
                "type": op.openingType.value
            }
        })

    # 5. Space Volumes (transparent bounding boxes)
    for s in model.spaces:
        b = s.bounds
        meshes.append({
            "canonicalElementId": s.spaceId,
            "elementType": "SPACE_VOLUME",
            "levelId": s.levelId,
            "geometryType": "SPACE_BOX",
            "position": [round(b.x + b.width / 2.0, 2), round(b.y + b.height / 2.0, 2), round(s.heightM / 2.0, 2)],
            "dimensions": [b.width, b.height, s.heightM],
            "material": {
                "color": s.color,
                "opacity": 0.15,
                "transparent": True
            },
            "userData": {
                "spaceId": s.spaceId,
                "name": s.name,
                "areaSqm": s.areaSqm,
                "zone": s.zone.value if hasattr(s.zone, "value") else str(s.zone)
            }
        })

    return {
        "designVersionId": model.designVersionId,
        "modelId": model.modelId,
        "modelHash": model.metadata.modelHash,
        "meshesCount": len(meshes),
        "meshes": meshes,
        "buildingEnvelope": model.buildingEnvelope
    }
