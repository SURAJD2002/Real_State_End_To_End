"""
Planwise Enterprise — Room Program Model & NBC 2016 Dimensional Standards
Delta Specification M2 — Phase 2

Defines:
- Standardized room types and spatial specifications.
- NBC 2016 Part 3 compliant minimum/preferred dimensional thresholds.
- Centralized room program factory derived deterministically from CustomerBrief.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field


class RoomType(str, Enum):
    ENTRY = "ENTRY"
    LIVING = "LIVING"
    DINING = "DINING"
    KITCHEN = "KITCHEN"
    MASTER_BEDROOM = "MASTER_BEDROOM"
    BEDROOM = "BEDROOM"
    GUEST_BEDROOM = "GUEST_BEDROOM"
    BATHROOM = "BATHROOM"
    TOILET = "TOILET"
    PUJA = "PUJA"
    STUDY = "STUDY"
    UTILITY = "UTILITY"
    STORE = "STORE"
    STAIR = "STAIR"
    CORRIDOR = "CORRIDOR"
    PARKING = "PARKING"
    BALCONY = "BALCONY"
    TERRACE = "TERRACE"
    SHAFT = "SHAFT"


class DaylightRequirement(str, Enum):
    DIRECT_WINDOW = "DIRECT_WINDOW"
    SKYLIGHT_COURTYARD = "SKYLIGHT_COURTYARD"
    BORROWED_LIGHT = "BORROWED_LIGHT"
    NONE_ARTIFICIAL = "NONE_ARTIFICIAL"


class VentilationRequirement(str, Enum):
    NATURAL_CROSS = "NATURAL_CROSS"
    SHAFT_VENTILATED = "SHAFT_VENTILATED"
    MECHANICAL_EXHAUST = "MECHANICAL_EXHAUST"


class PrivacyLevel(str, Enum):
    PUBLIC = "PUBLIC"
    SEMI_PRIVATE = "SEMI_PRIVATE"
    PRIVATE = "PRIVATE"
    SERVICE = "SERVICE"


class RoomSpecification(BaseModel):
    """
    Authoritative specification for an individual room within the programmatic layout.
    Encodes dimensional, statutory, and environmental bounds.
    """
    specId: str
    roomType: RoomType
    displayName: str
    floorIndex: int = 0  # 0 for Ground, 1 for Level 1, etc.
    
    # Dimensional Thresholds (meters & square meters)
    minAreaSqm: float
    preferredAreaSqm: float
    maxAreaSqm: float
    minWidthM: float
    minLengthM: float
    preferredAspectRatio: float = 1.33 # Length / Width ratio
    
    # Requirement & Environmental Flags
    isRequired: bool = True
    daylight: DaylightRequirement = DaylightRequirement.DIRECT_WINDOW
    ventilation: VentilationRequirement = VentilationRequirement.NATURAL_CROSS
    privacy: PrivacyLevel = PrivacyLevel.PUBLIC
    isWetArea: bool = False
    isCirculation: bool = False
    displayColor: str = "#60a5fa"
    
    # Target centroid priority for Vastu / orientation soft optimization
    preferredCardinalSector: Optional[str] = None # "NE", "SE", "SW", "NW", "NORTH", "EAST"


# ----------------------------------------------------------------------
# Centralized NBC 2016 Architectural Standard Catalog
# ----------------------------------------------------------------------

STANDARD_ROOM_PROFILES: Dict[RoomType, Dict[str, Any]] = {
    RoomType.ENTRY: {
        "minArea": 3.5, "preferredArea": 5.0, "maxArea": 8.0,
        "minWidth": 1.5, "minLength": 2.0, "aspect": 1.3,
        "daylight": DaylightRequirement.BORROWED_LIGHT,
        "ventilation": VentilationRequirement.NATURAL_CROSS,
        "privacy": PrivacyLevel.PUBLIC, "wet": False, "circ": True,
        "color": "#93c5fd", "sector": "NORTH"
    },
    RoomType.LIVING: {
        "minArea": 16.0, "preferredArea": 24.0, "maxArea": 36.0,
        "minWidth": 3.6, "minLength": 4.5, "aspect": 1.33,
        "daylight": DaylightRequirement.DIRECT_WINDOW,
        "ventilation": VentilationRequirement.NATURAL_CROSS,
        "privacy": PrivacyLevel.PUBLIC, "wet": False, "circ": False,
        "color": "#38bdf8", "sector": "NORTH"
    },
    RoomType.DINING: {
        "minArea": 9.5, "preferredArea": 14.0, "maxArea": 20.0,
        "minWidth": 3.0, "minLength": 3.2, "aspect": 1.2,
        "daylight": DaylightRequirement.DIRECT_WINDOW,
        "ventilation": VentilationRequirement.NATURAL_CROSS,
        "privacy": PrivacyLevel.PUBLIC, "wet": False, "circ": False,
        "color": "#06b6d4", "sector": "EAST"
    },
    RoomType.KITCHEN: {
        "minArea": 6.5, "preferredArea": 10.0, "maxArea": 14.0,
        "minWidth": 2.4, "minLength": 2.7, "aspect": 1.25,
        "daylight": DaylightRequirement.DIRECT_WINDOW,
        "ventilation": VentilationRequirement.NATURAL_CROSS,
        "privacy": PrivacyLevel.SERVICE, "wet": True, "circ": False,
        "color": "#fb923c", "sector": "SE"
    },
    RoomType.MASTER_BEDROOM: {
        "minArea": 14.0, "preferredArea": 18.0, "maxArea": 26.0,
        "minWidth": 3.6, "minLength": 3.8, "aspect": 1.2,
        "daylight": DaylightRequirement.DIRECT_WINDOW,
        "ventilation": VentilationRequirement.NATURAL_CROSS,
        "privacy": PrivacyLevel.PRIVATE, "wet": False, "circ": False,
        "color": "#818cf8", "sector": "SW"
    },
    RoomType.BEDROOM: {
        "minArea": 11.5, "preferredArea": 14.0, "maxArea": 18.0,
        "minWidth": 3.0, "minLength": 3.5, "aspect": 1.2,
        "daylight": DaylightRequirement.DIRECT_WINDOW,
        "ventilation": VentilationRequirement.NATURAL_CROSS,
        "privacy": PrivacyLevel.PRIVATE, "wet": False, "circ": False,
        "color": "#a78bfa", "sector": "WEST"
    },
    RoomType.GUEST_BEDROOM: {
        "minArea": 10.5, "preferredArea": 13.0, "maxArea": 16.0,
        "minWidth": 3.0, "minLength": 3.2, "aspect": 1.2,
        "daylight": DaylightRequirement.DIRECT_WINDOW,
        "ventilation": VentilationRequirement.NATURAL_CROSS,
        "privacy": PrivacyLevel.SEMI_PRIVATE, "wet": False, "circ": False,
        "color": "#c084fc", "sector": "NW"
    },
    RoomType.BATHROOM: {
        "minArea": 3.6, "preferredArea": 4.8, "maxArea": 7.0,
        "minWidth": 1.5, "minLength": 2.1, "aspect": 1.4,
        "daylight": DaylightRequirement.DIRECT_WINDOW,
        "ventilation": VentilationRequirement.SHAFT_VENTILATED,
        "privacy": PrivacyLevel.PRIVATE, "wet": True, "circ": False,
        "color": "#f472b6", "sector": "WEST"
    },
    RoomType.TOILET: {
        "minArea": 2.2, "preferredArea": 3.0, "maxArea": 4.0,
        "minWidth": 1.2, "minLength": 1.8, "aspect": 1.5,
        "daylight": DaylightRequirement.BORROWED_LIGHT,
        "ventilation": VentilationRequirement.SHAFT_VENTILATED,
        "privacy": PrivacyLevel.SERVICE, "wet": True, "circ": False,
        "color": "#fb7185", "sector": "WEST"
    },
    RoomType.PUJA: {
        "minArea": 2.0, "preferredArea": 3.5, "maxArea": 5.0,
        "minWidth": 1.2, "minLength": 1.5, "aspect": 1.2,
        "daylight": DaylightRequirement.BORROWED_LIGHT,
        "ventilation": VentilationRequirement.NATURAL_CROSS,
        "privacy": PrivacyLevel.SEMI_PRIVATE, "wet": False, "circ": False,
        "color": "#facc15", "sector": "NE"
    },
    RoomType.UTILITY: {
        "minArea": 3.0, "preferredArea": 4.5, "maxArea": 6.5,
        "minWidth": 1.5, "minLength": 2.0, "aspect": 1.33,
        "daylight": DaylightRequirement.DIRECT_WINDOW,
        "ventilation": VentilationRequirement.NATURAL_CROSS,
        "privacy": PrivacyLevel.SERVICE, "wet": True, "circ": False,
        "color": "#fdba74", "sector": "SE"
    },
    RoomType.STAIR: {
        "minArea": 6.5, "preferredArea": 8.5, "maxArea": 11.0,
        "minWidth": 2.1, "minLength": 3.2, "aspect": 1.5,
        "daylight": DaylightRequirement.DIRECT_WINDOW,
        "ventilation": VentilationRequirement.NATURAL_CROSS,
        "privacy": PrivacyLevel.PUBLIC, "wet": False, "circ": True,
        "color": "#94a3b8", "sector": "SOUTH"
    },
    RoomType.BALCONY: {
        "minArea": 4.0, "preferredArea": 6.0, "maxArea": 10.0,
        "minWidth": 1.5, "minLength": 2.5, "aspect": 1.6,
        "daylight": DaylightRequirement.DIRECT_WINDOW,
        "ventilation": VentilationRequirement.NATURAL_CROSS,
        "privacy": PrivacyLevel.SEMI_PRIVATE, "wet": False, "circ": False,
        "color": "#4ade80", "sector": "NORTH"
    },
    RoomType.PARKING: {
        "minArea": 13.75, "preferredArea": 15.0, "maxArea": 20.0, # 2.5m x 5.5m standard car stall
        "minWidth": 2.5, "minLength": 5.5, "aspect": 2.2,
        "daylight": DaylightRequirement.DIRECT_WINDOW,
        "ventilation": VentilationRequirement.NATURAL_CROSS,
        "privacy": PrivacyLevel.PUBLIC, "wet": False, "circ": True,
        "color": "#64748b", "sector": "NW"
    }
}


class RoomProgram(BaseModel):
    """
    Complete programmatic inventory of spaces required for the house synthesis.
    """
    programId: str
    targetBuiltUpAreaSqm: float
    targetCarpetAreaSqm: float
    floorsCount: int = 1
    rooms: List[RoomSpecification] = Field(default_factory=list)

    def total_minimum_area_sqm(self) -> float:
        return sum(r.minAreaSqm for r in self.rooms if r.isRequired)

    def total_preferred_area_sqm(self) -> float:
        return sum(r.preferredAreaSqm for r in self.rooms if r.isRequired)


def build_room_program_from_brief(brief: Any) -> RoomProgram:
    """
    Deterministically synthesizes a RoomProgram from a CustomerBrief.
    Enforces room counts, floor distributions, and NBC 2016 room dimensions.
    """
    specs: List[RoomSpecification] = []
    r_idx = 1
    
    is_duplex = brief.floors > 1
    
    # 1. Entrance Foyer
    prof = STANDARD_ROOM_PROFILES[RoomType.ENTRY]
    specs.append(RoomSpecification(
        specId=f"SP-ENTRY-{r_idx}",
        roomType=RoomType.ENTRY,
        displayName="Entrance Foyer",
        floorIndex=0,
        minAreaSqm=prof["minArea"],
        preferredAreaSqm=prof["preferredArea"],
        maxAreaSqm=prof["maxArea"],
        minWidthM=prof["minWidth"],
        minLengthM=prof["minLength"],
        aspectRatio=prof["aspect"],
        isRequired=True,
        daylight=prof["daylight"],
        ventilation=prof["ventilation"],
        privacy=prof["privacy"],
        isWetArea=prof["wet"],
        isCirculation=prof["circ"],
        displayColor=prof["color"],
        preferredCardinalSector=prof["sector"]
    ))
    r_idx += 1

    # 2. Living Room
    prof = STANDARD_ROOM_PROFILES[RoomType.LIVING]
    specs.append(RoomSpecification(
        specId=f"SP-LIVING-{r_idx}",
        roomType=RoomType.LIVING,
        displayName="Living Room",
        floorIndex=0,
        minAreaSqm=prof["minArea"],
        preferredAreaSqm=prof["preferredArea"],
        maxAreaSqm=prof["maxArea"],
        minWidthM=prof["minWidth"],
        minLengthM=prof["minLength"],
        aspectRatio=prof["aspect"],
        isRequired=brief.livingRoomRequired,
        daylight=prof["daylight"],
        ventilation=prof["ventilation"],
        privacy=prof["privacy"],
        isWetArea=prof["wet"],
        isCirculation=prof["circ"],
        displayColor=prof["color"],
        preferredCardinalSector=prof["sector"]
    ))
    r_idx += 1

    # 3. Dining Space
    if brief.diningRequired:
        prof = STANDARD_ROOM_PROFILES[RoomType.DINING]
        specs.append(RoomSpecification(
            specId=f"SP-DINING-{r_idx}",
            roomType=RoomType.DINING,
            displayName="Dining Area",
            floorIndex=0,
            minAreaSqm=prof["minArea"],
            preferredAreaSqm=prof["preferredArea"],
            maxAreaSqm=prof["maxArea"],
            minWidthM=prof["minWidth"],
            minLengthM=prof["minLength"],
            aspectRatio=prof["aspect"],
            isRequired=True,
            daylight=prof["daylight"],
            ventilation=prof["ventilation"],
            privacy=prof["privacy"],
            isWetArea=prof["wet"],
            isCirculation=prof["circ"],
            displayColor=prof["color"],
            preferredCardinalSector=prof["sector"]
        ))
        r_idx += 1

    # 4. Kitchen
    prof = STANDARD_ROOM_PROFILES[RoomType.KITCHEN]
    specs.append(RoomSpecification(
        specId=f"SP-KITCHEN-{r_idx}",
        roomType=RoomType.KITCHEN,
        displayName="Modular Kitchen",
        floorIndex=0,
        minAreaSqm=prof["minArea"],
        preferredAreaSqm=prof["preferredArea"],
        maxAreaSqm=prof["maxArea"],
        minWidthM=prof["minWidth"],
        minLengthM=prof["minLength"],
        aspectRatio=prof["aspect"],
        isRequired=True,
        daylight=prof["daylight"],
        ventilation=prof["ventilation"],
        privacy=prof["privacy"],
        isWetArea=prof["wet"],
        isCirculation=prof["circ"],
        displayColor=prof["color"],
        preferredCardinalSector=prof["sector"]
    ))
    r_idx += 1

    # 5. Utility / Wash Area
    if brief.utilityRequired:
        prof = STANDARD_ROOM_PROFILES[RoomType.UTILITY]
        specs.append(RoomSpecification(
            specId=f"SP-UTILITY-{r_idx}",
            roomType=RoomType.UTILITY,
            displayName="Utility / Yard",
            floorIndex=0,
            minAreaSqm=prof["minArea"],
            preferredAreaSqm=prof["preferredArea"],
            maxAreaSqm=prof["maxArea"],
            minWidthM=prof["minWidth"],
            minLengthM=prof["minLength"],
            aspectRatio=prof["aspect"],
            isRequired=True,
            daylight=prof["daylight"],
            ventilation=prof["ventilation"],
            privacy=prof["privacy"],
            isWetArea=prof["wet"],
            isCirculation=prof["circ"],
            displayColor=prof["color"],
            preferredCardinalSector=prof["sector"]
        ))
        r_idx += 1

    # 6. Puja Alcove
    if brief.pujaRequired:
        prof = STANDARD_ROOM_PROFILES[RoomType.PUJA]
        specs.append(RoomSpecification(
            specId=f"SP-PUJA-{r_idx}",
            roomType=RoomType.PUJA,
            displayName="Puja Room",
            floorIndex=0,
            minAreaSqm=prof["minArea"],
            preferredAreaSqm=prof["preferredArea"],
            maxAreaSqm=prof["maxArea"],
            minWidthM=prof["minWidth"],
            minLengthM=prof["minLength"],
            aspectRatio=prof["aspect"],
            isRequired=True,
            daylight=prof["daylight"],
            ventilation=prof["ventilation"],
            privacy=prof["privacy"],
            isWetArea=prof["wet"],
            isCirculation=prof["circ"],
            displayColor=prof["color"],
            preferredCardinalSector=prof["sector"]
        ))
        r_idx += 1

    # 7. Master Bedroom Suite
    prof = STANDARD_ROOM_PROFILES[RoomType.MASTER_BEDROOM]
    master_floor = 1 if is_duplex else 0
    specs.append(RoomSpecification(
        specId=f"SP-MBED-{r_idx}",
        roomType=RoomType.MASTER_BEDROOM,
        displayName="Master Bedroom Suite",
        floorIndex=master_floor,
        minAreaSqm=prof["minArea"],
        preferredAreaSqm=prof["preferredArea"],
        maxAreaSqm=prof["maxArea"],
        minWidthM=prof["minWidth"],
        minLengthM=prof["minLength"],
        aspectRatio=prof["aspect"],
        isRequired=True,
        daylight=prof["daylight"],
        ventilation=prof["ventilation"],
        privacy=prof["privacy"],
        isWetArea=prof["wet"],
        isCirculation=prof["circ"],
        displayColor=prof["color"],
        preferredCardinalSector=prof["sector"]
    ))
    r_idx += 1

    # Master Ensuite Bath
    prof = STANDARD_ROOM_PROFILES[RoomType.BATHROOM]
    specs.append(RoomSpecification(
        specId=f"SP-MBATH-{r_idx}",
        roomType=RoomType.BATHROOM,
        displayName="Master Attached Bath",
        floorIndex=master_floor,
        minAreaSqm=prof["minArea"],
        preferredAreaSqm=prof["preferredArea"],
        maxAreaSqm=prof["maxArea"],
        minWidthM=prof["minWidth"],
        minLengthM=prof["minLength"],
        aspectRatio=prof["aspect"],
        isRequired=True,
        daylight=prof["daylight"],
        ventilation=prof["ventilation"],
        privacy=prof["privacy"],
        isWetArea=prof["wet"],
        isCirculation=prof["circ"],
        displayColor=prof["color"],
        preferredCardinalSector=prof["sector"]
    ))
    r_idx += 1

    # 8. Additional Bedrooms
    remaining_beds = max(0, brief.bedrooms - 1)
    for b_i in range(remaining_beds):
        # In a duplex, ensure ground bed exists if accessibility requested
        floor_assign = 0 if (b_i == 0 and is_duplex and brief.accessibilityGroundFloorBed) else (1 if is_duplex else 0)
        prof = STANDARD_ROOM_PROFILES[RoomType.BEDROOM]
        specs.append(RoomSpecification(
            specId=f"SP-BED-{r_idx}",
            roomType=RoomType.BEDROOM,
            displayName=f"Bedroom {b_i + 2}",
            floorIndex=floor_assign,
            minAreaSqm=prof["minArea"],
            preferredAreaSqm=prof["preferredArea"],
            maxAreaSqm=prof["maxArea"],
            minWidthM=prof["minWidth"],
            minLengthM=prof["minLength"],
            aspectRatio=prof["aspect"],
            isRequired=True,
            daylight=prof["daylight"],
            ventilation=prof["ventilation"],
            privacy=prof["privacy"],
            isWetArea=prof["wet"],
            isCirculation=prof["circ"],
            displayColor=prof["color"],
            preferredCardinalSector=prof["sector"]
        ))
        r_idx += 1

    # 9. Additional Bathrooms
    remaining_baths = max(0, brief.bathrooms - 1)
    for ba_i in range(remaining_baths):
        floor_assign = 1 if (ba_i > 0 and is_duplex) else 0
        prof = STANDARD_ROOM_PROFILES[RoomType.BATHROOM]
        specs.append(RoomSpecification(
            specId=f"SP-BATH-{r_idx}",
            roomType=RoomType.BATHROOM,
            displayName=f"Bathroom {ba_i + 2}",
            floorIndex=floor_assign,
            minAreaSqm=prof["minArea"],
            preferredAreaSqm=prof["preferredArea"],
            maxAreaSqm=prof["maxArea"],
            minWidthM=prof["minWidth"],
            minLengthM=prof["minLength"],
            aspectRatio=prof["aspect"],
            isRequired=True,
            daylight=prof["daylight"],
            ventilation=prof["ventilation"],
            privacy=prof["privacy"],
            isWetArea=prof["wet"],
            isCirculation=prof["circ"],
            displayColor=prof["color"],
            preferredCardinalSector=prof["sector"]
        ))
        r_idx += 1

    # 10. Staircase (if multi-floor duplex)
    if is_duplex:
        prof = STANDARD_ROOM_PROFILES[RoomType.STAIR]
        specs.append(RoomSpecification(
            specId=f"SP-STAIR-{r_idx}",
            roomType=RoomType.STAIR,
            displayName="Staircase Core",
            floorIndex=0,
            minAreaSqm=prof["minArea"],
            preferredAreaSqm=prof["preferredArea"],
            maxAreaSqm=prof["maxArea"],
            minWidthM=prof["minWidth"],
            minLengthM=prof["minLength"],
            aspectRatio=prof["aspect"],
            isRequired=True,
            daylight=prof["daylight"],
            ventilation=prof["ventilation"],
            privacy=prof["privacy"],
            isWetArea=prof["wet"],
            isCirculation=prof["circ"],
            displayColor=prof["color"],
            preferredCardinalSector=prof["sector"]
        ))
        r_idx += 1

    # 11. Balcony
    if brief.balconyRequired:
        prof = STANDARD_ROOM_PROFILES[RoomType.BALCONY]
        balc_floor = 1 if is_duplex else 0
        specs.append(RoomSpecification(
            specId=f"SP-BALC-{r_idx}",
            roomType=RoomType.BALCONY,
            displayName="Living Balcony",
            floorIndex=balc_floor,
            minAreaSqm=prof["minArea"],
            preferredAreaSqm=prof["preferredArea"],
            maxAreaSqm=prof["maxArea"],
            minWidthM=prof["minWidth"],
            minLengthM=prof["minLength"],
            aspectRatio=prof["aspect"],
            isRequired=True,
            daylight=prof["daylight"],
            ventilation=prof["ventilation"],
            privacy=prof["privacy"],
            isWetArea=prof["wet"],
            isCirculation=prof["circ"],
            displayColor=prof["color"],
            preferredCardinalSector=prof["sector"]
        ))
        r_idx += 1

    total_carpet = sum(r.preferredAreaSqm for r in specs)
    total_bua = total_carpet * 1.25 # Nominal 25% wall/circulation factor

    return RoomProgram(
        programId=f"PROG-{brief.briefId}",
        targetBuiltUpAreaSqm=round(total_bua, 2),
        targetCarpetAreaSqm=round(total_carpet, 2),
        floorsCount=brief.floors,
        rooms=specs
    )
