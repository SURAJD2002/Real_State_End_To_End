"""
Planwise Enterprise — Real Plot Structured Intake Schema
Delta Specification & Real Plot Data End-to-End Test

Defines:
- Authoritative input schema for manual plot dimensions and customer requirements
- ParcelGeometryVersion with rigorous provenance and geometric integrity
- Validation failure states: USER_INPUT_REQUIRED, JURISDICTION_REQUIRED
- Boundary reconstruction logic for regular and irregular parcels without guessing
"""

from typing import List, Dict, Any, Optional, Union
from enum import Enum
import math
from pydantic import BaseModel, Field
from datetime import datetime


class SiteShape(str, Enum):
    REGULAR = "regular"
    RECTANGULAR = "rectangular"
    TRAPEZOIDAL = "trapezoidal"
    IRREGULAR = "irregular"


class RoadFacingSide(str, Enum):
    NORTH = "NORTH"
    SOUTH = "SOUTH"
    EAST = "EAST"
    WEST = "WEST"
    FRONT = "FRONT"


class BuildingUse(str, Enum):
    RESIDENTIAL = "residential"
    MIXED_USE = "mixed_use"
    COMMERCIAL = "commercial"


class PlotDimensions(BaseModel):
    """
    Structured plot boundary dimensions.
    Can accept dimensions in feet or meters, or direct boundary coordinates.
    """
    front_width_ft: Optional[float] = Field(None, description="Width along road frontage (ft)")
    back_width_ft: Optional[float] = Field(None, description="Width along rear boundary (ft)")
    left_length_ft: Optional[float] = Field(None, description="Length of left lateral boundary (ft)")
    right_length_ft: Optional[float] = Field(None, description="Length of right lateral boundary (ft)")
    diagonal_ft: Optional[float] = Field(None, description="Internal diagonal measurement for quadrilateral closure (ft)")
    
    # Metric alternatives
    front_width_m: Optional[float] = Field(None, description="Front width in meters")
    back_width_m: Optional[float] = Field(None, description="Rear width in meters")
    left_length_m: Optional[float] = Field(None, description="Left length in meters")
    right_length_m: Optional[float] = Field(None, description="Right length in meters")
    diagonal_m: Optional[float] = Field(None, description="Diagonal length in meters")
    
    # Explicit vertex coordinates if surveyor/CAD data is entered directly
    coordinates_wgs84: Optional[List[List[float]]] = Field(None, description="Explicit WGS84 [[lon, lat], ...]")
    coordinates_secs: Optional[List[List[float]]] = Field(None, description="Explicit SECS [[east, north], ...]")


class SiteInput(BaseModel):
    """Structured Site intake data."""
    location: str = Field(..., description="Geographic locality e.g. Bandra West, Mumbai")
    city: Optional[str] = Field(None, description="City name e.g. Mumbai")
    state: Optional[str] = Field(None, description="State name e.g. Maharashtra")
    country: Optional[str] = Field("India", description="Country name")
    declared_area_sqft: Optional[float] = Field(None, description="Authoritative customer-declared plot area in sq ft")
    declared_area_sqm: Optional[float] = Field(None, description="Authoritative customer-declared plot area in sq m")
    jurisdiction: Optional[str] = Field(None, description="Statutory authority e.g. MUMBAI-DCPR-2034-V1 or BBMP-BENGALURU-2026-V1")
    road_width_ft: Optional[float] = Field(None, description="Existing abutting road width in feet")
    road_width_m: Optional[float] = Field(None, description="Existing abutting road width in meters")
    proposed_road_width_m: Optional[float] = Field(None, description="Development Plan proposed road width in meters")
    road_facing_side: RoadFacingSide = Field(RoadFacingSide.NORTH, description="Cardinal orientation facing abutting road")
    shape: SiteShape = Field(SiteShape.REGULAR, description="Geometric topology")
    orientation: str = Field("NORTH", description="Compass orientation e.g. NORTH, EAST")
    dimensions: Optional[PlotDimensions] = Field(None, description="Plot boundary measurements")


class CustomerRequirementsInput(BaseModel):
    """Customer building brief requirements."""
    use: BuildingUse = Field(BuildingUse.RESIDENTIAL, description="Intended occupancy")
    floors: int = Field(..., description="Requested storeys (e.g. 1, 2, 4)")
    ground_floor: Optional[str] = Field(None, description="Optional ground floor program e.g. commercial + parking")
    bedrooms: Optional[int] = Field(None, description="Target bedrooms (total or per residential floor)")
    bedrooms_per_residential_floor: Optional[int] = Field(None, description="Target bedrooms per residential floor")
    bathrooms: Optional[int] = Field(None, description="Target bathrooms (total or per residential floor)")
    bathrooms_per_residential_floor: Optional[int] = Field(None, description="Target bathrooms per residential floor")
    parking: Union[bool, int] = Field(True, description="Parking requirement (bool or stall count)")
    commercial_requirement: Optional[Union[bool, str]] = Field(None, description="Commercial area requirement")
    balcony: bool = Field(True, description="Balcony preference")
    terrace: bool = Field(True, description="Terrace preference")
    preferred_style: str = Field("modern", description="Architectural style preference")
    budget: Optional[float] = Field(None, description="Optional customer budget in INR")
    special_requirements: Optional[List[str]] = Field(default_factory=list, description="Special constraints")


class RealPlotIntakePayload(BaseModel):
    """Top-level intake payload for manual plot and customer brief entry."""
    site: SiteInput
    requirements: CustomerRequirementsInput
    reference_style_description: Optional[str] = Field(None, description="Optional customer text description")


class ParcelGeometryVersion(BaseModel):
    """
    Authoritative computational site geometry version (§1 Site Intake).
    Captures closed mathematical boundary representation with verified provenance.
    """
    versionId: str = Field(..., description="Unique version identifier, e.g. PGV-2026-001")
    siteId: str = Field(..., description="Site identifier")
    dimensions: Dict[str, float] = Field(..., description="Authoritative side lengths and diagonals")
    units: str = Field("METRIC", description="Primary computational unit (METRIC)")
    boundarySECS: List[List[float]] = Field(..., description="SECS Cartesian [East, North] closed polygon (m)")
    boundaryWGS84: List[List[float]] = Field(..., description="WGS84 Geodetic [Lon, Lat] closed polygon")
    areaSqm: float = Field(..., description="True planar area in m²")
    areaSqft: float = Field(..., description="True planar area in sqft")
    declaredAreaSqft: Optional[float] = Field(None, description="Authoritative customer-provided area in sq ft")
    declaredAreaSqm: Optional[float] = Field(None, description="Authoritative customer-provided area in sq m")
    perimeterM: float = Field(..., description="Perimeter in meters")
    perimeterFt: float = Field(..., description="Perimeter in feet")
    roadEdgeIndex: int = Field(0, description="Edge index abutting the road")
    roadWidthM: float = Field(..., description="Abutting road width in meters")
    orientation: str = Field(..., description="Cardinal orientation")
    source: str = Field("USER_PROVIDED", description="Authoritative intake channel")
    confidence: str = Field("USER_CONFIRMED", description="Customer confirmed state")
    createdAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
