"""
Planwise Enterprise — Cost Model & Rate Snapshot Schema
Delta Specification & M3 Master Specification §7, §8, §9, §10, §11, §12, §13

Authoritative schema for:
- Versioned Material Catalog
- Immutable Cost Rate Snapshots (jurisdiction & time-anchored)
- Structured BOQ lines with CBM provenance and confidence
- Cost Waterfall accounting
- Explainable cost breakdown records
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
import hashlib
import json
from datetime import datetime
from packages.schemas.qto_model import QTOConfidence, QuantitySourceType


class MaterialCatalogItem(BaseModel):
    materialId: str = Field(..., description="Unique material identifier, e.g. MAT_M25_RCC")
    name: str = Field(..., description="Display name")
    category: str = Field(..., description="CONCRETE, MASONRY, FINISHES, STEEL, JOINERY, MEP, EARTHWORK")
    unit: str = Field(..., description="Unit of supply: m³, m², kg, bag, no., m")
    specification: str = Field(..., description="Technical standard specification")
    wastagePercent: float = Field(0.0, description="Standard statutory wastage allowance %")
    source: str = Field("CPWD_DSR_2026", description="Source specification authority")
    version: str = Field("2026.Q4", description="Catalog version")
    activeFrom: str = Field("2026-01-01", description="Validity start date")
    activeTo: Optional[str] = Field("2026-12-31", description="Validity expiry date")


class CostRateItem(BaseModel):
    rateId: str = Field(..., description="Rate lookup identifier, e.g. RATE-RCC-M25")
    materialId: str = Field(..., description="Reference to material ID")
    category: str = Field(..., description="Trade category")
    description: str = Field(..., description="Item rate scope description")
    unit: str = Field(..., description="Rate measurement unit: m³, m², m, no., points")
    materialRateInr: float = Field(0.0, description="Direct material component cost per unit in INR")
    labourRateInr: float = Field(0.0, description="Direct labour component cost per unit in INR")
    equipmentRateInr: float = Field(0.0, description="Plant & machinery component cost per unit in INR")
    baseUnitRateInr: float = Field(..., description="Total direct unit rate = material + labour + equipment")
    source: str = Field("DSR_ANALYSIS", description="Basis of rate determination")


class CostRateSnapshot(BaseModel):
    rateSnapshotId: str = Field(..., description="Immutable snapshot ID, e.g. INDIA-MUMBAI-2026-Q4-V1")
    jurisdiction: str = Field(..., description="Statutory jurisdiction, e.g. MAHARASHTRA_MUMBAI")
    location: str = Field(..., description="City or district context, e.g. Mumbai Metropolitan Region")
    source: str = Field(..., description="Data source authority, e.g. MCGM / CPWD DSR / Market Index")
    sourceDate: str = Field(..., description="Effective date: YYYY-MM-DD")
    currency: str = Field("INR", description="Currency code")
    version: str = Field("1.0.0", description="Snapshot revision")
    rates: Dict[str, CostRateItem] = Field(default_factory=dict, description="Itemized rate library")
    hash: str = Field("", description="Cryptographic SHA-256 digest of rates content")

    def compute_hash(self) -> str:
        serialized = json.dumps({
            "rateSnapshotId": self.rateSnapshotId,
            "jurisdiction": self.jurisdiction,
            "location": self.location,
            "sourceDate": self.sourceDate,
            "currency": self.currency,
            "version": self.version,
            "rates": {k: v.dict() for k, v in sorted(self.rates.items())}
        }, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


class BOQLineItem(BaseModel):
    boqItemId: str = Field(..., description="Unique line identifier, e.g. BOQ-MAS-001")
    section: str = Field(..., description="Trade section, e.g. '03 Masonry'")
    itemCode: str = Field(..., description="Standard schedule item code, e.g. MAS-01")
    description: str = Field(..., description="Detailed trade scope description")
    specification: str = Field(..., description="Technical specification reference")
    unit: str = Field(..., description="Measurement unit: m³, m², no., m, points")
    quantity: float = Field(..., description="Calculated bill quantity")
    materialRate: float = Field(0.0, description="Material rate in INR")
    labourRate: float = Field(0.0, description="Labour rate in INR")
    equipmentRate: float = Field(0.0, description="Equipment rate in INR")
    unitRate: float = Field(..., description="Total unit rate in INR")
    amount: float = Field(..., description="Total line amount in INR")
    materialAmount: float = Field(0.0, description="Material cost in INR")
    labourAmount: float = Field(0.0, description="Labour cost in INR")
    equipmentAmount: float = Field(0.0, description="Equipment cost in INR")
    wastageAmount: float = Field(0.0, description="Allowance for material wastage in INR")
    sourceElementIds: List[str] = Field(default_factory=list, description="IDs of source CBM elements")
    measurementRuleId: str = Field(..., description="Applied IS 1200 measurement rule ID")
    assemblyId: Optional[str] = Field(None, description="Applied construction assembly ID")
    rateSnapshotId: str = Field(..., description="Rate snapshot ID used for pricing")
    confidence: QTOConfidence = Field(QTOConfidence.HIGH, description="Confidence classification")
    sourceType: QuantitySourceType = Field(QuantitySourceType.MODEL_COMPUTED, description="Provenance")
    status: str = Field("CALCULATED", description="CALCULATED, ESTIMATED, PLACEHOLDER")


class CostWaterfall(BaseModel):
    grossHardCost: float = Field(..., description="Direct hard construction cost in INR")
    directMaterialCost: float = Field(..., description="Net raw materials cost in INR")
    directLabourCost: float = Field(..., description="Net site labour & skilled crafts cost in INR")
    directEquipmentCost: float = Field(..., description="Machinery, shuttering & staging plant cost in INR")
    materialWastageCost: float = Field(..., description="Statutory material cutting & handling wastage in INR")
    overheadAndPrelims: float = Field(..., description="Contractor preliminary expenses & site overheads (8%)")
    contingency: float = Field(..., description="Unforeseen physical contingency buffer (5%)")
    statutoryTaxes: float = Field(0.0, description="Applicable statutory tax buffer if configured (e.g. GST @ 18% on works contract)")
    totalConstructionCost: float = Field(..., description="Total projected preliminary construction cost in INR")
    costPerSqFtBUA: float = Field(..., description="Cost per sq.ft of Gross Built-Up Area in INR")
    costPerSqmBUA: float = Field(..., description="Cost per sq.m of Gross Built-Up Area in INR")
    costPerCarpetSqFt: float = Field(..., description="Cost per sq.ft of Net Carpet Area in INR")
    costPerCarpetSqm: float = Field(..., description="Cost per sq.m of Net Carpet Area in INR")
    areaBasis: Dict[str, float] = Field(
        default_factory=dict,
        description="Authoritative areas: grossBUASqm, grossBUASqFt, carpetAreaSqm, carpetAreaSqFt"
    )


class CostExplanation(BaseModel):
    boqItemId: str
    itemCode: str
    description: str
    quantity: float
    unit: str
    measurementRuleId: str
    measurementFormula: str
    standardReference: str
    sourceElementsCount: int
    sourceElementIds: List[str]
    deductions: List[Dict[str, Any]]
    assemblyId: Optional[str]
    assemblyComponents: List[Dict[str, Any]]
    rateId: str
    rateSnapshotId: str
    jurisdiction: str
    location: str
    sourceDate: str
    rateBreakdown: Dict[str, float]
    costBreakdown: Dict[str, float]
    confidence: str
    sourceType: str


class CostEstimate(BaseModel):
    estimateId: str = Field(..., description="Unique estimate ID, e.g. EST-2026-001")
    designVersionId: str = Field(..., description="Parent DesignVersion ID")
    projectId: str = Field(..., description="Parent Project ID")
    rateSnapshotId: str = Field(..., description="Applied immutable rate snapshot ID")
    qualityTier: str = Field("STANDARD", description="ECONOMY, STANDARD, PREMIUM, LUXURY")
    status: str = Field("PRELIMINARY", description="PRELIMINARY / VERIFIED / RELEASED")
    costWaterfall: CostWaterfall = Field(..., description="Itemized cost waterfall")
    boqLines: List[BOQLineItem] = Field(default_factory=list, description="Structured BOQ line items")
    qtoHash: str = Field("", description="SHA-256 fingerprint of all takeoff records")
    boqHash: str = Field("", description="SHA-256 fingerprint of the BOQ table")
    costHash: str = Field("", description="SHA-256 fingerprint of the complete cost calculation")
    confidenceSummary: Dict[str, int] = Field(default_factory=dict, description="Count of items by confidence level")
    calculatedAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    disclaimer: str = Field(
        "Preliminary Cost Estimate based on algorithmic model takeoff. Professional structural, architectural, "
        "and quantity surveying verification is required prior to commercial commitment or contractor bidding.",
        description="Statutory non-quotation safety disclosure"
    )
