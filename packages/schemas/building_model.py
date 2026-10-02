"""
Planwise Enterprise — Canonical Building Model Schema
Delta Specification §1, §7, §8, §10, §12, §13, §14, §26

The Authoritative Domain Object Model for Land-to-Home Digital Delivery.
All floor plans, elevations, sections, 3D models, IFC4 BIM files, QTO takeoffs,
and BOQ cost schedules are deterministic projections of this canonical model.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
import hashlib
import json
from datetime import datetime


BUILDING_MODEL_SCHEMA_VERSION = "1.0.0"


class ElementType(str, Enum):
    WALL = "WALL"
    COLUMN = "COLUMN"
    BEAM = "BEAM"
    SLAB = "SLAB"
    STAIR = "STAIR"
    ROOF = "ROOF"
    FOUNDATION = "FOUNDATION"
    PARAPET = "PARAPET"


class WallType(str, Enum):
    EXTERNAL = "EXTERNAL"
    INTERNAL = "INTERNAL"
    PARTITION = "PARTITION"
    RETAINING = "RETAINING"
    PARAPET = "PARAPET"


class OpeningType(str, Enum):
    DOOR = "DOOR"
    WINDOW = "WINDOW"
    OPENING_VOID = "OPENING_VOID"


class StructuralRole(str, Enum):
    LOADBEARING = "LOADBEARING"
    NON_LOADBEARING = "NON_LOADBEARING"
    PRIMARY_FRAME = "PRIMARY_FRAME"
    FOUNDATION = "FOUNDATION"


class SlabType(str, Enum):
    PLINTH = "PLINTH"
    FLOOR = "FLOOR"
    ROOF = "ROOF"
    TERRACE = "TERRACE"


class StairType(str, Enum):
    STRAIGHT = "STRAIGHT"
    L_SHAPE = "L_SHAPE"
    U_SHAPE = "U_SHAPE"


class SpaceZone(str, Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    SERVICE = "SERVICE"
    CIRCULATION = "CIRCULATION"
    SEMI_OUTDOOR = "SEMI_OUTDOOR"
    OUTDOOR = "OUTDOOR"


class DesignVersionStatus(str, Enum):
    DRAFT = "DRAFT"
    GENERATED = "GENERATED"
    VALIDATING = "VALIDATING"
    VALID = "VALID"
    SELECTED = "SELECTED"
    BUILD_REQUESTED = "BUILD_REQUESTED"
    RELEASED = "RELEASED"
    SUPERSEDED = "SUPERSEDED"


class ValidationSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    BLOCKER = "BLOCKER"


# -------------------------------------------------------------
# Base Geometry Primitives
# -------------------------------------------------------------

class Point2D(BaseModel):
    x: float
    y: float


class Bounds2D(BaseModel):
    x: float
    y: float
    width: float
    height: float


# -------------------------------------------------------------
# Building Levels (Storeys)
# -------------------------------------------------------------

class BuildingLevel(BaseModel):
    levelId: str = Field(..., description="Stable level ID, e.g. LVL-000")
    levelIndex: int = Field(..., description="0 for Ground, 1 for First Floor, etc.")
    name: str = Field(..., description="e.g. GROUND, FIRST, TERRACE")
    elevationM: float = Field(..., description="Level floor elevation relative to project datum (m)")
    floorToFloorHeightM: float = Field(3.15, description="Floor to floor clear structural height (m)")
    usage: str = Field("RESIDENTIAL", description="Level usage classification")


# -------------------------------------------------------------
# Spaces (Rooms)
# -------------------------------------------------------------

class Space(BaseModel):
    spaceId: str = Field(..., description="Stable space ID, e.g. SPACE-001")
    levelId: str = Field(..., description="Reference to parent BuildingLevel.levelId")
    spaceType: str = Field(..., description="Canonical room type: LIVING_ROOM, KITCHEN, MASTER_BEDROOM, etc.")
    name: str = Field(..., description="Display room label")
    zone: SpaceZone = Field(SpaceZone.PUBLIC, description="Zoning categorization")
    floor: str = Field("L0", description="Storey reference e.g. L0, L1")
    color: str = Field("#60a5fa", description="Display color for CAD/2D rendering")
    bounds: Bounds2D = Field(..., description="Axis-aligned bounding box [x, y, width, height] in meters")
    polygon: List[List[float]] = Field(..., description="Closed 2D polygon vertices [[x, y], ...] in meters")
    areaSqm: float = Field(..., description="Net carpet usable floor area in m²")
    perimeterM: float = Field(..., description="Perimeter in meters")
    centroid: List[float] = Field(..., description="[x, y] room center in meters")
    heightM: float = Field(3.0, description="Clear room ceiling height in meters")
    daylightRequirement: str = Field("DIRECT_WINDOW", description="Daylight requirement per NBC 2016 Part 3")
    ventilationRequirement: str = Field("NATURAL_CROSS", description="Ventilation requirement")
    privacyRating: str = Field("MEDIUM", description="Acoustic & visual privacy buffer")
    adjacentSpaceIds: List[str] = Field(default_factory=list, description="IDs of topologically adjacent spaces")
    boundaryWallIds: List[str] = Field(default_factory=list, description="IDs of enclosing wall segments")


# -------------------------------------------------------------
# Openings (Doors & Windows)
# -------------------------------------------------------------

class Opening(BaseModel):
    openingId: str = Field(..., description="Stable opening ID, e.g. DOOR-001 or WIN-001")
    openingType: OpeningType = Field(..., description="DOOR, WINDOW, or OPENING_VOID")
    hostWallId: str = Field(..., description="Reference to the host Wall.elementId")
    levelId: str = Field(..., description="Reference to parent BuildingLevel.levelId")
    name: str = Field(..., description="Display label, e.g. Main Entry Door D1")
    widthM: float = Field(..., description="Opening clear width in meters")
    heightM: float = Field(..., description="Opening clear height in meters")
    sillHeightM: float = Field(0.0, description="Sill height above level floor in meters (0 for doors)")
    positionRatio: float = Field(0.5, description="Relative placement along host wall centerline (0.0 to 1.0)")
    positionM: List[float] = Field(default_factory=list, description="Calculated [x, y] point along wall in meters")
    swing: Optional[str] = Field(None, description="Door swing direction: LEFT_INWARD, RIGHT_INWARD, SLIDING")
    orientation: Optional[str] = Field(None, description="Compass orientation: NORTH, SOUTH, EAST, WEST")
    materialId: str = Field("FLUSH_DOOR_35MM", description="Reference to Material.materialId")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Hardware, acoustic rating, glass specs")


# -------------------------------------------------------------
# Building Elements (Walls, Columns, Slabs, Stairs, etc.)
# -------------------------------------------------------------

class ElementGeometry(BaseModel):
    centerline: Optional[List[List[float]]] = Field(None, description="Linear centerline for walls [[x1, y1], [x2, y2]]")
    footprintPolygon: List[List[float]] = Field(..., description="Closed 2D polygon in meters [[x, y], ...]")
    baseZ: float = Field(0.0, description="Base elevation in meters")
    topZ: float = Field(3.15, description="Top elevation in meters")
    thicknessM: Optional[float] = Field(None, description="Thickness in meters (e.g. 0.20 for external wall)")
    heightM: Optional[float] = Field(None, description="Clear height in meters")
    widthM: Optional[float] = Field(None, description="Width in meters")
    depthM: Optional[float] = Field(None, description="Depth in meters")


class BuildingElement(BaseModel):
    elementId: str = Field(..., description="Stable element ID, e.g. WALL-EXT-001, COL-A1, SLAB-L0")
    elementType: ElementType = Field(..., description="WALL, COLUMN, SLAB, STAIR, BEAM, ROOF")
    levelId: str = Field(..., description="Reference to parent BuildingLevel.levelId")
    name: str = Field(..., description="Human-readable label")
    geometry: ElementGeometry = Field(..., description="Authoritative geometric parameters")
    materialId: str = Field(..., description="Reference to Material.materialId")
    structuralRole: StructuralRole = Field(StructuralRole.NON_LOADBEARING, description="Structural classification")
    hostId: Optional[str] = Field(None, description="Parent host element if sub-component")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Element-specific metadata")

    # Specific convenience fields for Wall subtype
    wallType: Optional[WallType] = None
    openingIds: List[str] = Field(default_factory=list, description="IDs of hosted Openings")
    connectedSpaceIds: List[str] = Field(default_factory=list, description="IDs of bounded Spaces")

    # Specific convenience fields for Column subtype
    gridReference: Optional[str] = None # e.g. "A-1", "B-2"


# -------------------------------------------------------------
# Structural Grid System
# -------------------------------------------------------------

class GridLine(BaseModel):
    tag: str = Field(..., description="Grid line label, e.g. 'A', 'B', '1', '2'")
    coordinate: float = Field(..., description="Position in meters along primary axis")
    direction: str = Field("X", description="'X' for vertical grid lines, 'Y' for horizontal")


class StructuralGrid(BaseModel):
    gridLinesX: List[GridLine] = Field(default_factory=list, description="Grid lines along X axis")
    gridLinesY: List[GridLine] = Field(default_factory=list, description="Grid lines along Y axis")
    baySpacingXM: float = Field(4.0, description="Nominal structural bay spacing in X (m)")
    baySpacingYM: float = Field(4.0, description="Nominal structural bay spacing in Y (m)")


# -------------------------------------------------------------
# Materials & Catalogs
# -------------------------------------------------------------

class Material(BaseModel):
    materialId: str = Field(..., description="Stable material identifier, e.g. AAC_BLOCK_150")
    catalogVersion: str = Field("2026.Q3", description="Version of the authoritative rate catalog")
    category: str = Field("MASONRY", description="CONCRETE, MASONRY, FINISHES, JOINERY, STEEL, MEP")
    name: str = Field(..., description="Descriptive specification")
    grade: str = Field(..., description="e.g. M25, Fe500D, Grade 1")
    unit: str = Field("m³", description="Takeoff unit: m³, m², no., rmt, points")
    baseUnitRateInr: float = Field(..., description="Base statutory/market unit rate in INR")


class MaterialAssignment(BaseModel):
    assignmentId: str
    elementId: str
    materialId: str
    layerThicknessMm: Optional[float] = None
    fraction: float = 1.0


# -------------------------------------------------------------
# MEP Preliminary Systems
# -------------------------------------------------------------

class SystemComponent(BaseModel):
    componentId: str
    componentType: str # LIGHT_POINT, SOCKET_POINT, TAP, EWC, DRAIN_TRAP, DISTRIBUTION_BOARD
    levelId: str
    spaceId: Optional[str] = None
    position: List[float] # [x, y, z] in meters
    specification: str


class BuildingSystem(BaseModel):
    systemId: str
    systemType: str # ELECTRICAL, PLUMBING, DRAINAGE, HVAC, FIRE
    components: List[SystemComponent] = Field(default_factory=list)


# -------------------------------------------------------------
# Validation Rules & Diagnostic Results
# -------------------------------------------------------------

class ValidationIssue(BaseModel):
    ruleId: str = Field(..., description="Unique validation rule code, e.g. ARCH-NBC-001")
    category: str = Field(..., description="MODEL_INTEGRITY, GEOMETRY, TOPOLOGY, ARCHITECTURE, REGULATION, STRUCTURE_PRELIM")
    severity: ValidationSeverity = Field(..., description="INFO, WARNING, ERROR, BLOCKER")
    status: str = Field("FAIL", description="PASS or FAIL")
    message: str = Field(..., description="Clear explanation of the rule evaluation")
    objectIds: List[str] = Field(default_factory=list, description="IDs of affected elements or spaces")


class ValidationSummary(BaseModel):
    isValid: bool = Field(..., description="True if no BLOCKER or ERROR issues exist")
    totalIssues: int = 0
    blockersCount: int = 0
    errorsCount: int = 0
    warningsCount: int = 0
    infoCount: int = 0
    issues: List[ValidationIssue] = Field(default_factory=list)


# -------------------------------------------------------------
# Canonical Building Model Root Container
# -------------------------------------------------------------

class ModelMetadata(BaseModel):
    engineName: str = "planwise-model-compiler"
    engineVersion: str = "1.0.0"
    compilationTimestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    modelHash: str = Field("", description="Cryptographic SHA-256 fingerprint of the canonical model")
    isLocked: bool = Field(False, description="True once locked in a BUILD release")


class CanonicalBuildingModel(BaseModel):
    schemaVersion: str = Field(BUILDING_MODEL_SCHEMA_VERSION, description="Authoritative schema version")
    modelId: str = Field(..., description="Stable model identity, e.g. BLDG-2BHK-001")
    designVersionId: str = Field(..., description="Reference to parent DesignVersion.designVersionId")
    projectId: str = Field(..., description="Reference to Project.id")
    siteGeometryVersionId: str = Field(..., description="Reference to authoritative site parcel geometry version, e.g. PV-002")
    regulationVersionId: str = Field("MUMBAI_DCPR_2034_V1", description="Statutory rule set reference")
    
    name: str = Field(..., description="Design archetype name")
    archetype: str = Field(..., description="compact_2bhk, family_3bhk, duplex_3bhk")
    description: str = Field("", description="Architectural summary")

    buildingEnvelope: Dict[str, float] = Field(
        ..., description="Overall building bounding box: widthM, lengthM, heightM"
    )
    totalGrossBUASqm: float = Field(..., description="Total Gross Built-Up Area in m²")
    totalUsableAreaSqm: float = Field(..., description="Total Net Usable Carpet Area in m²")
    floorsCount: int = Field(1, description="Number of above-ground storeys")

    levels: List[BuildingLevel] = Field(default_factory=list, description="All building storeys")
    spaces: List[Space] = Field(default_factory=list, description="All architectural room spaces")
    elements: List[BuildingElement] = Field(default_factory=list, description="All walls, columns, slabs, stairs")
    openings: List[Opening] = Field(default_factory=list, description="All doors and windows hosted by walls")
    structuralGrid: StructuralGrid = Field(default_factory=StructuralGrid, description="Structural column grid")
    materials: List[Material] = Field(default_factory=list, description="Versioned material catalog")
    materialAssignments: List[MaterialAssignment] = Field(default_factory=list)
    systems: List[BuildingSystem] = Field(default_factory=list, description="MEP preliminary systems")
    
    validation: Optional[ValidationSummary] = None
    metadata: ModelMetadata = Field(default_factory=ModelMetadata)

    def compute_hash(self) -> str:
        """
        Computes a deterministic cryptographic SHA-256 fingerprint over canonical structure.
        """
        snapshot = {
            "schemaVersion": self.schemaVersion,
            "modelId": self.modelId,
            "designVersionId": self.designVersionId,
            "siteGeometryVersionId": self.siteGeometryVersionId,
            "archetype": self.archetype,
            "totalGrossBUASqm": self.totalGrossBUASqm,
            "levels": [lvl.dict() for lvl in self.levels],
            "spaces": [
                {
                    "id": s.spaceId,
                    "type": s.spaceType,
                    "area": s.areaSqm,
                    "bounds": s.bounds.dict(),
                    "polygon": s.polygon
                }
                for s in self.spaces
            ],
            "elements": [
                {
                    "id": e.elementId,
                    "type": e.elementType,
                    "material": e.materialId,
                    "footprint": e.geometry.footprintPolygon,
                    "baseZ": e.geometry.baseZ,
                    "topZ": e.geometry.topZ
                }
                for e in self.elements
            ],
            "openings": [
                {
                    "id": o.openingId,
                    "type": o.openingType,
                    "host": o.hostWallId,
                    "w": o.widthM,
                    "h": o.heightM,
                    "pos": o.positionM
                }
                for o in self.openings
            ]
        }
        serialized = json.dumps(snapshot, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
