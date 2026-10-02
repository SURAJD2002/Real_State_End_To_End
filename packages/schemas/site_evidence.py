"""
Planwise Enterprise — Site Evidence & Provenance Data Schema
Delta Specification M1 — §1, §2

Defines:
- Site Evidence items with complete provenance, accuracy, and verification states
- Confidence tiers L0 through L4
- Evaluation summaries explaining release-blocking evidence gaps
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class SiteConfidenceTier(str, Enum):
    """
    Standardized Site Confidence Tiers (§2).
    L0: GIS-derived only (unverified public / satellite basemap)
    L1: Customer-provided documentation (title deed / sketch / unverified PDF)
    L2: Remote verification (satellite cross-check / municipal GIS ledger matching)
    L3: Licensed land survey (field stamped DGPS / Total Station boundary & levels)
    L4: Comprehensive engineering survey (L3 + geotechnical borehole soil report + subsurface utilities)
    """
    L0_GIS_ESTIMATE = "L0_GIS_ESTIMATE"
    L1_CUSTOMER_DOCUMENT = "L1_CUSTOMER_DOCUMENT"
    L2_REMOTE_VERIFIED = "L2_REMOTE_VERIFIED"
    L3_LICENSED_SURVEY = "L3_LICENSED_SURVEY"
    L4_ENGINEERING_READY = "L4_ENGINEERING_READY"


class EvidenceType(str, Enum):
    PARCEL_BOUNDARY = "PARCEL_BOUNDARY"
    SURVEY_PLAN = "SURVEY_PLAN"
    SALE_DEED = "SALE_DEED"
    LAND_RECORD = "LAND_RECORD"
    ROAD_EDGE = "ROAD_EDGE"
    ROAD_WIDTH = "ROAD_WIDTH"
    ROAD_LEVEL = "ROAD_LEVEL"
    SITE_LEVEL = "SITE_LEVEL"
    TOPOGRAPHY = "TOPOGRAPHY"
    TREE = "TREE"
    UTILITY = "UTILITY"
    EASEMENT = "EASEMENT"
    ROAD_WIDENING = "ROAD_WIDENING"
    SOIL_REPORT = "SOIL_REPORT"
    GEOTECHNICAL = "GEOTECHNICAL"
    SATELLITE_REFERENCE = "SATELLITE_REFERENCE"
    DRONE_SURVEY = "DRONE_SURVEY"
    TOTAL_STATION = "TOTAL_STATION"
    GNSS_SURVEY = "GNSS_SURVEY"
    OTHER = "OTHER"


class SourceType(str, Enum):
    GIS_SATELLITE = "GIS_SATELLITE"
    CUSTOMER_UPLOAD = "CUSTOMER_UPLOAD"
    GOVERNMENT_PORTAL = "GOVERNMENT_PORTAL"
    REMOTE_ANALYST = "REMOTE_ANALYST"
    LICENSED_SURVEYOR = "LICENSED_SURVEYOR"
    GEOTECHNICAL_ENGINEER = "GEOTECHNICAL_ENGINEER"
    UTILITY_PROVIDER = "UTILITY_PROVIDER"


class VerificationStatus(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    PENDING_REVIEW = "PENDING_REVIEW"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"


class SiteEvidence(BaseModel):
    """
    Authoritative Site Evidence Record (§1).
    Answers: WHO provided it? WHEN? From WHAT source? How ACCURATE? Has it been VERIFIED? By WHOM?
    """
    siteEvidenceId: str = Field(..., description="Unique evidence ID, e.g. EVID-BND-001")
    siteId: str = Field(..., description="Reference to Site / Parcel ID")
    evidenceType: EvidenceType = Field(..., description="Categorical type of evidence")
    sourceType: SourceType = Field(..., description="Channel / origin of evidence")
    sourceDocumentId: Optional[str] = Field(None, description="External file or scan reference ID")
    provider: str = Field(..., description="Organization or person who supplied the evidence")
    capturedAt: str = Field(..., description="ISO-8601 timestamp of data capture in field")
    
    # Accuracy & Confidence
    accuracyM: float = Field(..., description="Reported spatial accuracy tolerance in meters (e.g. ±0.02m for Total Station)")
    confidenceLevel: SiteConfidenceTier = Field(..., description="Assigned confidence tier for this evidence")
    
    # Geometry & CRS
    geometry: Optional[Dict[str, Any]] = Field(None, description="GeoJSON geometry or spatial feature representation")
    coordinateReference: str = Field("EPSG:4326", description="Spatial reference system e.g. EPSG:4326 or SECS")
    
    # Provenance Audit Trail
    verificationStatus: VerificationStatus = Field(VerificationStatus.UNVERIFIED, description="Current verification state")
    verifiedBy: Optional[str] = Field(None, description="Licensed Engineer or Surveyor ID who stamped the evidence")
    verifiedAt: Optional[str] = Field(None, description="ISO-8601 timestamp of formal verification")
    notes: str = Field("", description="Engineering observation notes")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Flexible parameters e.g. soil bearing capacity")
    createdAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ConfidenceEvaluationSummary(BaseModel):
    """
    Deterministic Site Confidence Assessment (§2).
    Determines whether a site possesses adequate provenance to permit a BUILD release.
    """
    siteId: str
    overallConfidence: SiteConfidenceTier
    isBlockingForBuildRelease: bool
    highestVerifiedTier: SiteConfidenceTier
    totalEvidenceCount: int
    verifiedEvidenceCount: int
    missingEvidenceForL3: List[str]
    missingEvidenceForL4: List[str]
    explanation: str
    evaluatedAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
