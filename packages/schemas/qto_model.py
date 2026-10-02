"""
Planwise Enterprise — QTO Domain Model Schema
Delta Specification & M3 Master Specification §1, §2, §3, §4, §5

Authoritative schemas for:
- Measurement rules (IS 1200 linked)
- Model-linked deduction records
- Discrete Takeoff records traceable to Canonical Building Model objects
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
import hashlib
import json
from datetime import datetime


class QTOConfidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    PRELIMINARY = "PRELIMINARY"
    PROFESSIONAL_INPUT_REQUIRED = "PROFESSIONAL_INPUT_REQUIRED"


class QuantitySourceType(str, Enum):
    MODEL_COMPUTED = "MODEL_COMPUTED"
    RATE_SOURCED = "RATE_SOURCED"
    ASSUMED = "ASSUMED"
    PROFESSIONAL_REVIEW_REQUIRED = "PROFESSIONAL_REVIEW_REQUIRED"


class DeductionType(str, Enum):
    DOOR_OPENING = "DOOR_OPENING"
    WINDOW_OPENING = "WINDOW_OPENING"
    SHAFT_OPENING = "SHAFT_OPENING"
    STAIR_OPENING = "STAIR_OPENING"
    VOIDS = "VOIDS"
    DOOR_REBATE = "DOOR_REBATE"


class DeductionItem(BaseModel):
    elementId: str = Field(..., description="ID of the opening or void element causing deduction")
    elementType: str = Field(..., description="DOOR, WINDOW, OPENING_VOID, STAIR_OPENING")
    description: str = Field(..., description="Reason for deduction")
    deductionWidthM: float = Field(0.0, description="Opening width in meters")
    deductionHeightM: float = Field(0.0, description="Opening height in meters")
    deductionThicknessM: float = Field(0.0, description="Wall or slab thickness in meters")
    quantity: float = Field(..., description="Calculated deduction quantity in rule units")
    unit: str = Field(..., description="Unit of deduction: m³, m², m")
    formula: str = Field(..., description="Deduction arithmetic formula used")


class MeasurementRule(BaseModel):
    ruleId: str = Field(..., description="e.g. QTO-WALL-001, QTO-SLAB-001")
    standardReference: str = Field("IS-1200", description="IS 1200 Part code or standard reference")
    version: str = Field("1.0.0", description="Rule definition version")
    discipline: str = Field("ARCHITECTURAL", description="CIVIL_STRUCTURAL, ARCHITECTURAL, MEP_PRELIMINARY")
    category: str = Field("MASONRY", description="EARTHWORK, CONCRETE, MASONRY, PLASTER, FLOORING, JOINERY, PAINTING")
    description: str = Field(..., description="Authoritative measurement instruction")
    unit: str = Field(..., description="m³, m², m, no., points")
    formula: str = Field(..., description="Measurement expression, e.g. L × H × T - opening deductions")
    inclusions: List[str] = Field(default_factory=list, description="Explicit inclusions per standard")
    exclusions: List[str] = Field(default_factory=list, description="Explicit exclusions per standard")
    roundingPolicy: str = Field("0.001", description="Decimal precision policy, e.g. 0.001 m³, 0.01 m²")
    sourceElementTypes: List[str] = Field(..., description="Target CBM element types, e.g. ['WALL'], ['SLAB']")
    verificationStatus: str = Field("VERIFIED", description="VERIFIED or REQUIRES_SOURCE_VERIFICATION")


class TakeoffRecord(BaseModel):
    takeoffId: str = Field(..., description="Unique takeoff record ID, e.g. TO-WALL-001")
    designVersionId: str = Field(..., description="Parent design version ID")
    projectId: str = Field(..., description="Parent project ID")
    discipline: str = Field(..., description="CIVIL_STRUCTURAL, ARCHITECTURAL, FINISHES, MEP_PRELIMINARY")
    category: str = Field(..., description="EARTHWORK, CONCRETE, MASONRY, PLASTER, FLOORING, JOINERY, etc.")
    elementType: str = Field(..., description="WALL, COLUMN, SLAB, STAIR, OPENING, SPACE")
    assemblyId: Optional[str] = Field(None, description="Linked assembly identifier")
    grossQuantity: float = Field(..., description="Gross quantity before deductions")
    deductions: List[DeductionItem] = Field(default_factory=list, description="Itemized geometric deductions")
    netQuantity: float = Field(..., description="Authoritative net quantity after deductions")
    quantity: float = Field(..., description="Final quantity for bill of quantities")
    unit: str = Field(..., description="m³, m², m, no., points")
    measurementRuleId: str = Field(..., description="Applied measurement rule ID")
    sourceElementIds: List[str] = Field(..., description="Explicit CBM element IDs measured")
    geometryFingerprint: str = Field(..., description="Geometric checksum of source elements")
    confidence: QTOConfidence = Field(QTOConfidence.HIGH, description="Confidence classification")
    sourceType: QuantitySourceType = Field(QuantitySourceType.MODEL_COMPUTED, description="Provenance type")
    engineVersion: str = Field("3.0.0-M3-QTO", description="QTO engine version")
    calculatedAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    inputHash: str = Field("", description="Hash of the input CBM elements and parameters")
    outputHash: str = Field("", description="Hash of the takeoff result")

    def compute_hashes(self, source_elements_data: Any) -> None:
        """Computes deterministic input and output SHA-256 hashes."""
        in_payload = {
            "sourceElementIds": sorted(self.sourceElementIds),
            "measurementRuleId": self.measurementRuleId,
            "ruleUnit": self.unit,
            "raw": source_elements_data
        }
        self.inputHash = hashlib.sha256(json.dumps(in_payload, sort_keys=True, default=str).encode()).hexdigest()

        out_payload = {
            "takeoffId": self.takeoffId,
            "grossQuantity": round(self.grossQuantity, 4),
            "deductions": [d.dict() for d in self.deductions],
            "netQuantity": round(self.netQuantity, 4),
            "unit": self.unit,
            "sourceElementIds": sorted(self.sourceElementIds)
        }
        self.outputHash = hashlib.sha256(json.dumps(out_payload, sort_keys=True, default=str).encode()).hexdigest()
