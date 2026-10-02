"""
Planwise Enterprise — Cost Engine & Deterministic BOQ Generator
Delta Specification & M3 Master Specification §8, §9, §10, §11, §12, §13, §16

Generates structured Bill of Quantities (BOQ), itemized cost waterfalls,
and comprehensive design-to-cost traceability explanations.
"""

from typing import Dict, List, Any, Optional
import hashlib
import json
from datetime import datetime

from packages.schemas.building_model import CanonicalBuildingModel
from packages.schemas.qto_model import TakeoffRecord, QTOConfidence, QuantitySourceType
from packages.schemas.cost_model import (
    BOQLineItem,
    CostWaterfall,
    CostEstimate,
    CostExplanation,
    CostRateSnapshot
)
from workers.qto.measurement_engine import get_measurement_rule
from workers.qto.assembly_engine import CONSTRUCTION_ASSEMBLIES_REGISTRY
from workers.qto.rate_snapshot_engine import get_rate_snapshot
from workers.qto.qto_engine import ModelLinkedQTOEngine


TIER_MULTIPLIERS = {
    "ECONOMY": 0.88,
    "STANDARD": 1.00,
    "PREMIUM": 1.25,
    "LUXURY": 1.60
}

# Mapping from TakeoffRecord category/elementType to trade section & code
TAKEOFF_TRADE_MAPPING = {
    "TO-EXC": {
        "section": "01 Site / Earthwork",
        "itemCode": "EXC-01",
        "rateKey": "RATE_EXCAVATION",
        "description": "Foundation trench excavation in ordinary soil including shoring, dewatering buffer & disposal",
        "specification": "IS 1200 Part 1 / CPWD DSR Item 2.8"
    },
    "TO-COL": {
        "section": "02 RCC Structural Works",
        "itemCode": "RCC-COL-01",
        "rateKey": "RATE_RCC_M25",
        "description": "Reinforced Cement Concrete M25 grade in columns including formwork, vibration & Fe500D rebar",
        "specification": "IS 456:2000 / IS 1200 Part 2"
    },
    "TO-SLAB": {
        "section": "02 RCC Structural Works",
        "itemCode": "RCC-SLAB-01",
        "rateKey": "RATE_RCC_M25",
        "description": "Reinforced Cement Concrete M25 in suspended floor & roof slabs net of stair cutouts",
        "specification": "IS 456:2000 / IS 1200 Part 2"
    },
    "TO-STAIR": {
        "section": "02 RCC Structural Works",
        "itemCode": "RCC-STAIR-01",
        "rateKey": "RATE_RCC_M25",
        "description": "Reinforced Cement Concrete M25 in stair flights, waist slabs, risers, treads & landings",
        "specification": "IS 456:2000 / IS 1200 Part 2"
    },
    "TO-WALL-EXT": {
        "section": "03 Masonry",
        "itemCode": "MAS-EXT-01",
        "rateKey": "RATE_BRICK_MASONRY",
        "description": "230mm external brick masonry in cement mortar 1:6 net of door and window openings",
        "specification": "IS 2212 / IS 1200 Part 3"
    },
    "TO-WALL-INT": {
        "section": "03 Masonry",
        "itemCode": "MAS-INT-01",
        "rateKey": "RATE_AAC_BLOCK",
        "description": "100mm/115mm AAC block partition masonry with polymer thin-bed adhesive net of openings",
        "specification": "IS 2185 Part 3 / IS 1200 Part 3"
    },
    "TO-PLAST-INT": {
        "section": "04 Plaster",
        "itemCode": "PL-INT-01",
        "rateKey": "RATE_PLASTER_INT",
        "description": "12mm smooth cement plaster 1:4 to internal wall faces and room ceiling soffits",
        "specification": "IS 1661 / IS 1200 Part 12"
    },
    "TO-PLAST-EXT": {
        "section": "04 Plaster",
        "itemCode": "PL-EXT-01",
        "rateKey": "RATE_PLASTER_EXT",
        "description": "20mm double-coat sand-faced waterproof cement plaster 1:4 on external exposed walls",
        "specification": "IS 1661 / IS 1200 Part 12"
    },
    "TO-FL": {
        "section": "05 Flooring",
        "itemCode": "FL-TILE-01",
        "rateKey": "RATE_FLOOR_TILES",
        "description": "800x800mm double-charged nano vitrified tile flooring with polymer adhesive & epoxy grout",
        "specification": "IS 15622 / IS 1200 Part 11"
    },
    "TO-SKIRT": {
        "section": "05 Flooring",
        "itemCode": "FL-SKIRT-01",
        "rateKey": "RATE_SKIRTING",
        "description": "100mm matching vitrified tile skirting along room perimeters less doorway openings",
        "specification": "IS 15622 / IS 1200 Part 11"
    },
    "TO-DR": {
        "section": "06 Doors & Windows",
        "itemCode": "DR-01",
        "rateKey": "RATE_DOORS",
        "description": "Pre-hung engineered wooden flush doors (35mm BWP) with hardwood frames & SS mortise hardware",
        "specification": "IS 2202 / IS 1200 Part 15"
    },
    "TO-WIN": {
        "section": "06 Doors & Windows",
        "itemCode": "WIN-01",
        "rateKey": "RATE_WINDOWS",
        "description": "UPVC 3-track sliding window units with mosquito screens, hardware & 5mm toughened clear glass",
        "specification": "IS 1200 Part 15"
    },
    "TO-PNT": {
        "section": "07 Painting & Finishes",
        "itemCode": "PNT-01",
        "rateKey": "RATE_PAINTING",
        "description": "Interior premium low-VOC emulsion (2 coats over primer/putty) and exterior silicon weather-shield",
        "specification": "IS 15489 / IS 1200 Part 13"
    },
    "TO-WP": {
        "section": "08 Waterproofing",
        "itemCode": "WP-01",
        "rateKey": "RATE_WATERPROOFING",
        "description": "Elastomeric polymer-modified cementitious waterproofing on terrace roof and wet areas with coving",
        "specification": "IS 1200 Part 8"
    },
    "TO-ELE": {
        "section": "09 Electrical (Preliminary)",
        "itemCode": "ELE-01",
        "rateKey": "RATE_ELECTRICAL_POINT",
        "description": "Concealed copper FRLS wiring with PVC conduits, modular switches, DB, MCBs & earthing pit",
        "specification": "IS 732 / Preliminary Engineering Allowance"
    },
    "TO-PLB": {
        "section": "10 Plumbing (Preliminary)",
        "itemCode": "PLB-01",
        "rateKey": "RATE_PLUMBING_STACK",
        "description": "CPVC/SWR water supply & drainage lines with CP sanitary fittings, EWC, basin & overhead tank",
        "specification": "IS 1200 Part 16 / Preliminary Engineering Allowance"
    }
}


class DeterministicCostEngine:
    """
    Principal Cost Engine for Model-Linked BOQ & Cost Estimates.
    Consumes validated TakeoffRecords and an immutable CostRateSnapshot.
    """

    def __init__(
        self,
        model: CanonicalBuildingModel,
        rate_snapshot_id: str = "INDIA-MUMBAI-2026-Q4-V1",
        quality_tier: str = "STANDARD",
        include_taxes: bool = False
    ):
        self.model = model
        self.rate_snapshot = get_rate_snapshot(rate_snapshot_id)
        self.quality_tier = quality_tier if quality_tier in TIER_MULTIPLIERS else "STANDARD"
        self.tier_multiplier = TIER_MULTIPLIERS[self.quality_tier]
        self.include_taxes = include_taxes

    def calculate_cost_estimate(
        self,
        takeoff_records: Optional[List[TakeoffRecord]] = None
    ) -> CostEstimate:
        """
        Executes full deterministic calculation:
        Takeoffs → BOQ Line Items → Unit Rates → Cost Waterfall → Hashes.
        """
        if takeoff_records is None:
            qto_engine = ModelLinkedQTOEngine(self.model)
            takeoff_records = qto_engine.run_full_takeoff()

        boq_lines: List[BOQLineItem] = []
        confidence_counts: Dict[str, int] = {
            QTOConfidence.HIGH.value: 0,
            QTOConfidence.MEDIUM.value: 0,
            QTOConfidence.LOW.value: 0,
            QTOConfidence.PRELIMINARY.value: 0,
            QTOConfidence.PROFESSIONAL_INPUT_REQUIRED.value: 0
        }

        for rec in takeoff_records:
            # Determine mapping based on prefix of takeoffId
            prefix = "-".join(rec.takeoffId.split("-")[:2])
            if prefix not in TAKEOFF_TRADE_MAPPING:
                prefix = "-".join(rec.takeoffId.split("-")[:3])
            mapping = TAKEOFF_TRADE_MAPPING.get(prefix, {
                "section": "12 Miscellaneous",
                "itemCode": f"MISC-{rec.category}",
                "rateKey": "RATE_BRICK_MASONRY",
                "description": f"Trade item for {rec.category}",
                "specification": "General Building Specification"
            })

            rate_item = self.rate_snapshot.rates.get(mapping["rateKey"])
            if not rate_item:
                # Fallback to first available rate
                rate_item = list(self.rate_snapshot.rates.values())[0]

            # Apply quality tier multiplier to rates
            mat_rate = round(rate_item.materialRateInr * self.tier_multiplier, 2)
            lab_rate = round(rate_item.labourRateInr * self.tier_multiplier, 2)
            eqp_rate = round(rate_item.equipmentRateInr * self.tier_multiplier, 2)
            unit_rate = round(mat_rate + lab_rate + eqp_rate, 2)

            # Quantities
            qty = round(rec.quantity, 3)
            amount = round(qty * unit_rate, 2)
            mat_amt = round(qty * mat_rate, 2)
            lab_amt = round(qty * lab_rate, 2)
            eqp_amt = round(qty * eqp_rate, 2)

            # Material wastage allowance (standard 4%)
            wastage_amt = round(mat_amt * 0.04, 2)

            boq_line = BOQLineItem(
                boqItemId=f"BOQ-{rec.takeoffId}",
                section=mapping["section"],
                itemCode=mapping["itemCode"],
                description=mapping["description"],
                specification=mapping["specification"],
                unit=rec.unit,
                quantity=qty,
                materialRate=mat_rate,
                labourRate=lab_rate,
                equipmentRate=eqp_rate,
                unitRate=unit_rate,
                amount=amount,
                materialAmount=mat_amt,
                labourAmount=lab_amt,
                equipmentAmount=eqp_amt,
                wastageAmount=wastage_amt,
                sourceElementIds=rec.sourceElementIds,
                measurementRuleId=rec.measurementRuleId,
                assemblyId=rec.assemblyId,
                rateSnapshotId=self.rate_snapshot.rateSnapshotId,
                confidence=rec.confidence,
                sourceType=rec.sourceType,
                status="CALCULATED"
            )
            boq_lines.append(boq_line)
            confidence_counts[rec.confidence.value] = confidence_counts.get(rec.confidence.value, 0) + 1

        # -------------------------------------------------------------
        # Cost Waterfall Calculation
        # -------------------------------------------------------------
        gross_hard_cost = round(sum(l.amount for l in boq_lines), 2)
        direct_mat_cost = round(sum(l.materialAmount for l in boq_lines), 2)
        direct_lab_cost = round(sum(l.labourAmount for l in boq_lines), 2)
        direct_eqp_cost = round(sum(l.equipmentAmount for l in boq_lines), 2)
        mat_wastage_cost = round(sum(l.wastageAmount for l in boq_lines), 2)

        prelims = round(gross_hard_cost * 0.08, 2)    # 8% Contractor Prelims & Site Overheads
        contingency = round(gross_hard_cost * 0.05, 2) # 5% Physical Contingency Buffer

        subtotal = gross_hard_cost + prelims + contingency
        taxes = round(subtotal * 0.18, 2) if self.include_taxes else 0.0
        total_construction_cost = round(subtotal + taxes, 2)

        bua_sqm = self.model.totalGrossBUASqm or 100.0
        bua_sqft = bua_sqm * 10.7639
        carpet_sqm = self.model.totalUsableAreaSqm or (bua_sqm * 0.85)
        carpet_sqft = carpet_sqm * 10.7639

        waterfall = CostWaterfall(
            grossHardCost=gross_hard_cost,
            directMaterialCost=direct_mat_cost,
            directLabourCost=direct_lab_cost,
            directEquipmentCost=direct_eqp_cost,
            materialWastageCost=mat_wastage_cost,
            overheadAndPrelims=prelims,
            contingency=contingency,
            statutoryTaxes=taxes,
            totalConstructionCost=total_construction_cost,
            costPerSqFtBUA=round(total_construction_cost / bua_sqft, 2),
            costPerSqmBUA=round(total_construction_cost / bua_sqm, 2),
            costPerCarpetSqFt=round(total_construction_cost / carpet_sqft, 2),
            costPerCarpetSqm=round(total_construction_cost / carpet_sqm, 2),
            areaBasis={
                "grossBUASqm": round(bua_sqm, 2),
                "grossBUASqFt": round(bua_sqft, 2),
                "carpetAreaSqm": round(carpet_sqm, 2),
                "carpetAreaSqFt": round(carpet_sqft, 2)
            }
        )

        # -------------------------------------------------------------
        # Deterministic Hashes
        # -------------------------------------------------------------
        qto_serialized = json.dumps([r.outputHash for r in takeoff_records], sort_keys=True)
        qto_hash = hashlib.sha256(qto_serialized.encode()).hexdigest()

        boq_serialized = json.dumps([
            {
                "id": l.boqItemId,
                "code": l.itemCode,
                "qty": l.quantity,
                "rate": l.unitRate,
                "amt": l.amount
            }
            for l in boq_lines
        ], sort_keys=True)
        boq_hash = hashlib.sha256(boq_serialized.encode()).hexdigest()

        cost_serialized = json.dumps({
            "waterfall": waterfall.dict(),
            "qtoHash": qto_hash,
            "boqHash": boq_hash,
            "rateSnapshotId": self.rate_snapshot.rateSnapshotId,
            "qualityTier": self.quality_tier
        }, sort_keys=True)
        cost_hash = hashlib.sha256(cost_serialized.encode()).hexdigest()

        estimate_id = f"EST-{self.model.designVersionId}-{self.rate_snapshot.rateSnapshotId[-6:]}"

        return CostEstimate(
            estimateId=estimate_id,
            designVersionId=self.model.designVersionId,
            projectId=self.model.projectId,
            rateSnapshotId=self.rate_snapshot.rateSnapshotId,
            qualityTier=self.quality_tier,
            status="PRELIMINARY",
            costWaterfall=waterfall,
            boqLines=boq_lines,
            qtoHash=qto_hash,
            boqHash=boq_hash,
            costHash=cost_hash,
            confidenceSummary=confidence_counts,
            calculatedAt=datetime.utcnow().isoformat()
        )


def explain_boq_item(
    estimate: CostEstimate,
    boq_item_id: str,
    takeoff_records: Optional[List[TakeoffRecord]] = None
) -> CostExplanation:
    """
    Returns complete, auditable explanation for a specific BOQ item:
    BOQ ITEM → ASSEMBLY → TAKEOFF → FORMULA & DEDUCTIONS → CBM ELEMENTS → RATES.
    """
    # Find BOQ Line
    line: Optional[BOQLineItem] = None
    for l in estimate.boqLines:
        if l.boqItemId == boq_item_id or l.itemCode == boq_item_id:
            line = l
            break

    if not line:
        raise KeyError(f"BOQ item {boq_item_id} not found in estimate.")

    # Measurement Rule
    rule = get_measurement_rule(line.measurementRuleId)

    # Assembly
    assembly_id = line.assemblyId
    assembly_components = []
    if assembly_id and assembly_id in CONSTRUCTION_ASSEMBLIES_REGISTRY:
        asm = CONSTRUCTION_ASSEMBLIES_REGISTRY[assembly_id]
        assembly_components = [c.dict() for c in asm.components]

    # Deductions
    deductions_list = []
    if takeoff_records:
        for r in takeoff_records:
            if r.takeoffId in line.boqItemId:
                deductions_list = [d.dict() for d in r.deductions]
                break

    # Rate Snapshot
    snapshot = get_rate_snapshot(line.rateSnapshotId)

    return CostExplanation(
        boqItemId=line.boqItemId,
        itemCode=line.itemCode,
        description=line.description,
        quantity=line.quantity,
        unit=line.unit,
        measurementRuleId=rule.ruleId,
        measurementFormula=rule.formula,
        standardReference=rule.standardReference,
        sourceElementsCount=len(line.sourceElementIds),
        sourceElementIds=line.sourceElementIds,
        deductions=deductions_list,
        assemblyId=assembly_id,
        assemblyComponents=assembly_components,
        rateId=line.itemCode,
        rateSnapshotId=snapshot.rateSnapshotId,
        jurisdiction=snapshot.jurisdiction,
        location=snapshot.location,
        sourceDate=snapshot.sourceDate,
        rateBreakdown={
            "materialRate": line.materialRate,
            "labourRate": line.labourRate,
            "equipmentRate": line.equipmentRate,
            "unitRate": line.unitRate
        },
        costBreakdown={
            "materialAmount": line.materialAmount,
            "labourAmount": line.labourAmount,
            "equipmentAmount": line.equipmentAmount,
            "wastageAmount": line.wastageAmount,
            "totalAmount": line.amount
        },
        confidence=line.confidence.value if hasattr(line.confidence, "value") else str(line.confidence),
        sourceType=line.sourceType.value if hasattr(line.sourceType, "value") else str(line.sourceType)
    )
