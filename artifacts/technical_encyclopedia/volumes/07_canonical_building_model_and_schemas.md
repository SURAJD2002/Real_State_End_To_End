# Volume VII — Canonical Building Model and Domain Schemas

## 1. The Canonical Building Model (CBM) Paradigm
The **Canonical Building Model (CBM)** is the authoritative, single-source-of-truth domain model in Planwise Enterprise. Implemented in `packages/schemas/building_model.py` using **Pydantic v2**, the CBM decouples spatial programming from geometry kernels, quantity takeoffs, drawing compilers, and IFC emissions.


<div class="diagram-container">
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 245" width="100%" height="245px" class="svg-diagram" style="max-height:245px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;">
<defs>
  <marker id="arr" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
    <path d="M0,0 L6,3 L0,6 Z" fill="#2563eb" />
  </marker>
  <marker id="arr-gray" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
    <path d="M0,0 L6,3 L0,6 Z" fill="#64748b" />
  </marker>
</defs>

<text x="350" y="24" text-anchor="middle" font-size="13" font-weight="bold" fill="#0f172a">DIAGRAM 3: CANONICAL BUILDING MODEL (CBM) SCHEMA HIERARCHY</text>
<rect x="260" y="45" width="180" height="45" rx="3" fill="#1e293b" stroke="#0f172a"/>
<text x="350" y="64" text-anchor="middle" font-size="10" font-weight="bold" fill="#ffffff">CanonicalBuildingModel</text>
<text x="350" y="78" text-anchor="middle" font-size="8" fill="#94a3b8">modelId • schemaVersion 1.0.0</text>

<!-- Child Objects -->
<line x1="350" y1="90" x2="350" y2="115" stroke="#64748b" stroke-width="1.2"/>
<line x1="80" y1="115" x2="620" y2="115" stroke="#64748b" stroke-width="1.2"/>

<!-- Levels -->
<line x1="80" y1="115" x2="80" y2="135" stroke="#64748b" stroke-width="1.2" marker-end="url(#arr-gray)"/>
<rect x="20" y="135" width="120" height="90" rx="3" fill="#ffffff" stroke="#3b82f6"/>
<text x="80" y="152" text-anchor="middle" font-size="9" font-weight="bold" fill="#1e40af">BuildingLevel</text>
<text x="28" y="168" font-size="7.5" fill="#334155">• levelId (LVL-000)</text>
<text x="28" y="180" font-size="7.5" fill="#334155">• levelIndex (0, 1)</text>
<text x="28" y="192" font-size="7.5" fill="#334155">• elevationM (0.0)</text>
<text x="28" y="204" font-size="7.5" fill="#334155">• floorHeight (3.15)</text>
<text x="28" y="216" font-size="7.5" fill="#334155">• usage (RESIDENTIAL)</text>

<!-- Spaces -->
<line x1="210" y1="115" x2="210" y2="135" stroke="#64748b" stroke-width="1.2" marker-end="url(#arr-gray)"/>
<rect x="150" y="135" width="120" height="90" rx="3" fill="#ffffff" stroke="#10b981"/>
<text x="210" y="152" text-anchor="middle" font-size="9" font-weight="bold" fill="#047857">Space (Room)</text>
<text x="158" y="168" font-size="7.5" fill="#334155">• spaceId (SPACE-01)</text>
<text x="158" y="180" font-size="7.5" fill="#334155">• spaceType (BED...)</text>
<text x="158" y="192" font-size="7.5" fill="#334155">• bounds (x,y,w,h)</text>
<text x="158" y="204" font-size="7.5" fill="#334155">• areaSqm, polygon</text>
<text x="158" y="216" font-size="7.5" fill="#334155">• floor (L0, L1)</text>

<!-- Elements -->
<line x1="350" y1="115" x2="350" y2="135" stroke="#64748b" stroke-width="1.2" marker-end="url(#arr-gray)"/>
<rect x="285" y="135" width="130" height="90" rx="3" fill="#ffffff" stroke="#8b5cf6"/>
<text x="350" y="152" text-anchor="middle" font-size="9" font-weight="bold" fill="#6d28d9">CanonicalElement</text>
<text x="293" y="168" font-size="7.5" fill="#334155">• WALL (EXT, INT)</text>
<text x="293" y="180" font-size="7.5" fill="#334155">• COLUMN (RCC)</text>
<text x="293" y="192" font-size="7.5" fill="#334155">• SLAB (FLOOR)</text>
<text x="293" y="204" font-size="7.5" fill="#334155">• STAIR (Parametric)</text>
<text x="293" y="216" font-size="7.5" fill="#334155">• geometry (footprint)</text>

<!-- Openings -->
<line x1="485" y1="115" x2="485" y2="135" stroke="#64748b" stroke-width="1.2" marker-end="url(#arr-gray)"/>
<rect x="425" y="135" width="120" height="90" rx="3" fill="#ffffff" stroke="#f59e0b"/>
<text x="485" y="152" text-anchor="middle" font-size="9" font-weight="bold" fill="#b45309">CanonicalOpening</text>
<text x="433" y="168" font-size="7.5" fill="#334155">• openingId</text>
<text x="433" y="180" font-size="7.5" fill="#334155">• openingType (DOOR/WIN)</text>
<text x="433" y="192" font-size="7.5" fill="#334155">• hostElementId (WALL)</text>
<text x="433" y="204" font-size="7.5" fill="#334155">• positionM, widthM</text>
<text x="433" y="216" font-size="7.5" fill="#334155">• heightM, sillHeight</text>

<!-- Envelope & Metadata -->
<line x1="620" y1="115" x2="620" y2="135" stroke="#64748b" stroke-width="1.2" marker-end="url(#arr-gray)"/>
<rect x="555" y="135" width="130" height="90" rx="3" fill="#ffffff" stroke="#ef4444"/>
<text x="620" y="152" text-anchor="middle" font-size="9" font-weight="bold" fill="#b91c1c">Envelope & Meta</text>
<text x="563" y="168" font-size="7.5" fill="#334155">• buildingEnvelope</text>
<text x="563" y="180" font-size="7.5" fill="#334155">• widthM, lengthM</text>
<text x="563" y="192" font-size="7.5" fill="#334155">• declaredPlotAreaSqFt</text>
<text x="563" y="204" font-size="7.5" fill="#334155">• validationSummary</text>
<text x="563" y="216" font-size="7.5" fill="#334155">• modelHash (SHA256)</text>

</svg>
  <div class="diagram-caption">Diagram 3: Canonical Building Model Topological Hierarchy</div>
</div>


---

## 2. Authoritative Domain Schema Code Listing (`packages/schemas/building_model.py`)

```python
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

```

---

## 3. Coordinate Conventions and Physical Units
- **Length:** International Standard Meters ($m$) rounded to 4 decimal places ($0.1\text{ mm}$ precision).
- **Area:** Square Meters ($m^2$) and Square Feet (sq ft) where $1\text{ m}^2 = 10.7639\text{ sq ft}$.
- **Volume:** Cubic Meters ($m^3$).
- **Mass:** Metric Tonnes (MT) or Kilograms (kg).
- **Coordinate System:** Right-handed Cartesian $(X, Y, Z)$:
  - $+X$: East / Width axis.
  - $+Y$: North / Depth axis.
  - $+Z$: Up / Vertical elevation axis ($Z = 0.0$ at Ground Plinth level).
