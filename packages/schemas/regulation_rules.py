"""
Planwise Enterprise — Declarative Statutory Rule Pack & Execution Trace Schema
Delta Specification M1 — §5, §6, §7, §8, §9

Defines:
- Versioned RulePack and Rule models
- Explicit Edge classification for parcels
- Comprehensive RuleExecutionTrace for complete regulatory explainability
- Rule status and severity enumerations
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class RuleCategory(str, Enum):
    PLOT = "PLOT"
    ROAD = "ROAD"
    ROAD_WIDENING = "ROAD_WIDENING"
    SETBACK = "SETBACK"
    FSI = "FSI"
    FAR = "FAR"
    GROUND_COVERAGE = "GROUND_COVERAGE"
    HEIGHT = "HEIGHT"
    PARKING = "PARKING"
    OPEN_SPACE = "OPEN_SPACE"
    FIRE_ACCESS = "FIRE_ACCESS"
    LIGHT_VENTILATION = "LIGHT_VENTILATION"
    STAIR = "STAIR"
    ACCESS = "ACCESS"
    BUILDING_ENVELOPE = "BUILDING_ENVELOPE"
    SPECIAL_RESTRICTION = "SPECIAL_RESTRICTION"


class RuleSeverity(str, Enum):
    INFO = "INFO"
    ADVISORY = "ADVISORY"
    WARNING = "WARNING"
    MANDATORY = "MANDATORY"
    BLOCKER = "BLOCKER"


class RuleStatus(str, Enum):
    CALCULATED = "CALCULATED"
    VERIFIED = "VERIFIED"
    ESTIMATED = "ESTIMATED"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"
    BLOCKED = "BLOCKED"
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    SUPERSEDED = "SUPERSEDED"


class EdgeClassification(str, Enum):
    FRONT = "FRONT"
    REAR = "REAR"
    LEFT_SIDE = "LEFT_SIDE"
    RIGHT_SIDE = "RIGHT_SIDE"
    SIDE_1 = "SIDE_1"
    SIDE_2 = "SIDE_2"
    CORNER_FRONT_SECONDARY = "CORNER_FRONT_SECONDARY"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"


class ClassifiedEdge(BaseModel):
    """Explicitly classified boundary edge of a parcel (§6)."""
    edgeId: str = Field(..., description="e.g. EDGE-001")
    startIndex: int
    endIndex: int
    startCoordSECS: List[float] # [east, north]
    endCoordSECS: List[float]   # [east, north]
    lengthM: float
    bearingDeg: float
    classification: EdgeClassification
    adjacentRoadWidthM: Optional[float] = None
    isRoadFrontage: bool = False
    confidence: str = "HIGH"
    notes: str = ""


class StatutoryRule(BaseModel):
    """Individual declarative statutory rule within a RulePack."""
    ruleId: str = Field(..., description="e.g. DCPR-REG30-FSI-01 or BBMP-SETBACK-FRONT-02")
    name: str
    category: RuleCategory
    priority: int = 1
    description: str
    citation: str = Field(..., description="Legal Gazette reference, e.g. 'DCPR 2034 Regulation 30 Table 12'")
    severity: RuleSeverity = RuleSeverity.MANDATORY
    parameters: Dict[str, Any] = Field(default_factory=dict)


class RulePack(BaseModel):
    """
    Authoritative Versioned Declarative Rule Pack (§5, §9).
    Immutable once referenced by a released design version.
    """
    rulePackId: str = Field(..., description="e.g. MUMBAI-DCPR-2034-V1 or BBMP-RES-2026-01")
    jurisdiction: str = Field(..., description="e.g. MCGM (Mumbai) or BBMP (Bengaluru)")
    authority: str = Field(..., description="Municipal Corporation / Planning Authority")
    name: str = Field(..., description="Human readable regulation name")
    version: str = Field(..., description="e.g. 1.0.0 or 2026.Q1")
    effectiveFrom: str = Field(..., description="ISO date of statutory gazette enactment")
    effectiveTo: Optional[str] = Field(None, description="ISO date of sunset / supersession")
    applicableTypologies: List[str] = Field(default_factory=lambda: ["RESIDENTIAL_LOW_RISE", "RESIDENTIAL_VILLA", "COMMERCIAL_RETAIL"])
    applicableZoning: List[str] = Field(default_factory=lambda: ["R2_RESIDENTIAL", "R1_RESIDENTIAL", "COMMERCIAL"])
    rules: List[StatutoryRule] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    isLocked: bool = Field(False)


class RuleExecutionTrace(BaseModel):
    """
    Authoritative trace explaining how every single regulatory output was calculated (§7).
    Provides 100% mathematical auditability.
    """
    traceId: str = Field(..., description="Unique trace identifier e.g. TRC-FSI-001")
    rulePackId: str
    ruleId: str
    ruleVersion: str
    category: RuleCategory
    ruleName: str
    citation: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    
    # Mathematical Inputs & Outputs
    inputs: Dict[str, Any] = Field(..., description="Exact numerical & geometric inputs passed to rule")
    calculationFormula: str = Field(..., description="Human and machine readable formula applied")
    outputs: Dict[str, Any] = Field(..., description="Calculated values produced by rule")
    
    status: RuleStatus = RuleStatus.CALCULATED
    severity: RuleSeverity = RuleSeverity.MANDATORY
    evidenceReferences: List[str] = Field(default_factory=list, description="IDs of site evidence records backing inputs")
    explanation: str = Field(..., description="Plain-English explanation of why this constraint exists")


class FeasibilityExplainabilityBreakdown(BaseModel):
    """
    Explainability breakdown answering: 'Why is my buildable area only X m²?' (§7)
    """
    grossParcelAreaSqm: float
    roadWideningDeductionSqm: float
    amenityReservationSqm: float
    netParcelAreaSqm: float
    
    frontSetbackDeductionSqm: float
    rearSetbackDeductionSqm: float
    sideSetbacksDeductionSqm: float
    
    rawSetbackEnvelopeAreaSqm: float
    maxGroundCoveragePercent: float
    maxGroundCoverageAreaSqm: float
    effectivePermittedFootprintSqm: float
    
    baseFSI: float
    premiumFSI: float
    tdrFSI: float
    totalPermissibleFSI: float
    permissibleBUASqm: float
    carpetAreaSqm: float
    maxBuildingHeightM: float
    parkingStallsRequired: int
    rulePackId: str = "MUMBAI-DCPR-2034-V1"
    rulePackVersion: str = "1.0.0"
    
    traces: List[RuleExecutionTrace] = Field(default_factory=list)
