"""
Planwise Enterprise — Customer Brief & Deterministic Constraint Model
Delta Specification M2 — Phase 1

Defines:
- Normalized, versioned CustomerBrief representation.
- Distinction between hard constraints (solver cuts) and soft preferences (objective weights).
- Provenance, source, and confidence tracking for all customer requirements.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class BriefSource(str, Enum):
    CUSTOMER_EXPLICIT = "CUSTOMER_EXPLICIT"
    ARCHITECT_RECOMMENDED = "ARCHITECT_RECOMMENDED"
    STATUTORY_DERIVED = "STATUTORY_DERIVED"
    DEFAULT_ASSUMPTION = "DEFAULT_ASSUMPTION"


class BriefConfidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ArchitecturalStyle(str, Enum):
    CONTEMPORARY = "CONTEMPORARY"
    MODERN_MINIMALIST = "MODERN_MINIMALIST"
    TRADITIONAL_COURTYARD = "TRADITIONAL_COURTYARD"
    COLONIAL_CLASSICAL = "COLONIAL_CLASSICAL"
    TROPICAL_MODERN = "TROPICAL_MODERN"


class KitchenType(str, Enum):
    CLOSED = "CLOSED"
    OPEN_PLAN = "OPEN_PLAN"
    ISLAND = "ISLAND"
    WET_AND_DRY = "WET_AND_DRY"


class StaircasePreference(str, Enum):
    INTERNAL_DOG_LEGGED = "INTERNAL_DOG_LEGGED"
    EXTERNAL_ACCESS = "EXTERNAL_ACCESS"
    FEATURE_OPEN_WELL = "FEATURE_OPEN_WELL"
    STRAIGHT_RUN = "STRAIGHT_RUN"
    NONE_SINGLE_STOREY = "NONE_SINGLE_STOREY"


class VastuOrientation(str, Enum):
    EAST = "EAST"
    NORTH = "NORTH"
    NORTH_EAST = "NORTH_EAST"
    SOUTH_EAST = "SOUTH_EAST"
    NO_PREFERENCE = "NO_PREFERENCE"


class ConstraintField(BaseModel):
    """Normalized constraint field with explicit provenance and hardness."""
    name: str
    requestedValue: Any
    normalizedValue: Any
    unit: Optional[str] = None
    hardConstraint: bool = True
    source: BriefSource = BriefSource.CUSTOMER_EXPLICIT
    confidence: BriefConfidence = BriefConfidence.HIGH
    notes: Optional[str] = None


class CustomerBrief(BaseModel):
    """
    Authoritative Customer Brief for Generative Layout Synthesis.
    Translates raw customer aspirations into machine-readable mathematical solver inputs.
    """
    briefId: str = Field(default_factory=lambda: f"BRIEF-{datetime.now().strftime('%Y%m%d%H%M%S')}", description="Unique brief ID e.g. BRIEF-2026-001")
    version: int = Field(1, description="Sequential brief version")
    projectId: str = Field(default="proj-default-01", description="Reference to parent project")
    title: str = Field("Modern Family Residence", description="Project brief title")
    
    # Core Habitable Space Requirements
    bedrooms: int = Field(3, description="Target bedroom count")
    bedroomsConstraint: ConstraintField = Field(
        default_factory=lambda: ConstraintField(
            name="bedrooms", requestedValue=3, normalizedValue=3, hardConstraint=True
        )
    )
    
    bathrooms: int = Field(3, description="Target bathroom count")
    bathroomsConstraint: ConstraintField = Field(
        default_factory=lambda: ConstraintField(
            name="bathrooms", requestedValue=3, normalizedValue=3, hardConstraint=True
        )
    )
    
    floors: int = Field(1, description="Requested number of storeys (1 for Villa, 2 for Duplex)")
    floorsConstraint: ConstraintField = Field(
        default_factory=lambda: ConstraintField(
            name="floors", requestedValue=1, normalizedValue=1, hardConstraint=True
        )
    )
    
    # Parking Requirements
    parkingRequired: bool = Field(True)
    parkingBaysCount: int = Field(1, description="Number of covered car parking bays")
    parkingType: str = Field("COVERED_SURFACE", description="COVERED_SURFACE, BASEMENT, STILT")
    
    # Family Demographics & Areas
    familySize: int = Field(4, description="Number of permanent residents")
    targetBuiltUpAreaSqm: Optional[float] = Field(None, description="Requested gross BUA in m²")
    targetCarpetAreaSqm: Optional[float] = Field(None, description="Requested net usable carpet in m²")
    budgetInr: Optional[float] = Field(None, description="Budget target in INR (soft constraint)")
    budgetConstraint: ConstraintField = Field(
        default_factory=lambda: ConstraintField(
            name="budget", requestedValue=7500000.0, normalizedValue=7500000.0, unit="INR", hardConstraint=False
        )
    )

    # Architectural Preferences
    preferredStyle: ArchitecturalStyle = ArchitecturalStyle.CONTEMPORARY
    kitchenType: KitchenType = KitchenType.CLOSED
    staircasePreference: StaircasePreference = StaircasePreference.INTERNAL_DOG_LEGGED
    
    # Room Existence Requirements
    livingRoomRequired: bool = True
    diningRequired: bool = True
    pujaRequired: bool = True
    utilityRequired: bool = True
    studyRequired: bool = False
    guestRoomRequired: bool = False
    masterBedroomRequired: bool = True
    balconyRequired: bool = True
    
    # Environmental & Functional Preferences
    daylightPreference: str = Field("MAXIMIZE", description="MAXIMIZE, STANDARD")
    ventilationPreference: str = Field("CROSS_VENTILATION", description="CROSS_VENTILATION, STANDARD")
    accessibilityGroundFloorBed: bool = Field(True, description="Ensure at least one elderly-accessible bedroom on ground")
    
    # Vastu Preference (Strictly a customer soft preference/weight, NEVER a statutory requirement)
    vastuPreference: VastuOrientation = Field(
        VastuOrientation.EAST, 
        description="Customer spatial orientation preference (weight only, NEVER statutory)"
    )
    futureExpansionPreference: bool = Field(
        False, 
        description="Whether upper slab should be pre-engineered for future vertical expansion"
    )

    metadata: Dict[str, Any] = Field(default_factory=dict)
    createdAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    def get_hard_constraints_summary(self) -> Dict[str, Any]:
        """Extracts purely the non-negotiable hard mathematical constraints for CP-SAT."""
        return {
            "bedrooms": self.bedrooms,
            "bathrooms": self.bathrooms,
            "floors": self.floors,
            "parkingBays": self.parkingBaysCount if self.parkingRequired else 0,
            "livingRequired": self.livingRoomRequired,
            "diningRequired": self.diningRequired,
            "pujaRequired": self.pujaRequired,
            "utilityRequired": self.utilityRequired,
            "masterBedRequired": self.masterBedroomRequired,
            "accessibilityGroundBed": self.accessibilityGroundFloorBed
        }
