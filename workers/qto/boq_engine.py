"""
Planwise Enterprise — Traceable Quantity Takeoff (QTO) & BOQ Cost Engine
Delta Specification §10, §14, §26, §34, §35 & M3 Master Specification

Every BOQ line item is directly traceable to Canonical Building Model elements:
Canonical Model → QTO Rules (IS 1200) → BOQ Line Items → Rate Snapshot → Cost Estimate
"""

from typing import Dict, Any, List, Optional
from packages.schemas.building_model import CanonicalBuildingModel
from workers.qto.qto_engine import ModelLinkedQTOEngine
from workers.qto.cost_engine import DeterministicCostEngine, explain_boq_item
from workers.qto.rate_snapshot_engine import get_rate_snapshot


def compute_traceable_boq(
    house_option_or_model: Any,
    quality_tier: str = "STANDARD",
    rate_snapshot_id: str = "INDIA-MUMBAI-2026-Q4-V1"
) -> Dict[str, Any]:
    """
    Computes deterministic, fully traceable BOQ lines, cost waterfall, and hashes
    directly from Canonical Building Model elements using the M3 IS 1200 QTO engine.
    Maintains 100% backward compatibility with M0-M2 callers.
    """
    from workers.generation.model_compiler import compile_canonical_building_model

    # Resolve CanonicalBuildingModel
    if isinstance(house_option_or_model, CanonicalBuildingModel):
        model = house_option_or_model
    elif isinstance(house_option_or_model, dict) and "buildingModel" in house_option_or_model and isinstance(house_option_or_model["buildingModel"], CanonicalBuildingModel):
        model = house_option_or_model["buildingModel"]
    elif isinstance(house_option_or_model, dict) and "buildingModel" in house_option_or_model and isinstance(house_option_or_model["buildingModel"], dict):
        model = CanonicalBuildingModel(**house_option_or_model["buildingModel"])
    else:
        # Fallback compile from house option layout
        layout = house_option_or_model.get("layout", house_option_or_model) if isinstance(house_option_or_model, dict) else {}
        model = compile_canonical_building_model(layout, design_version_id="DV-001")

    # Run M3 Model-Linked QTO Takeoff
    qto_engine = ModelLinkedQTOEngine(model)
    takeoff_records = qto_engine.run_full_takeoff()

    # Run M3 Deterministic Cost Engine
    cost_engine = DeterministicCostEngine(
        model=model,
        rate_snapshot_id=rate_snapshot_id,
        quality_tier=quality_tier
    )
    estimate = cost_engine.calculate_cost_estimate(takeoff_records)

    # Format lines for full backward-compatibility + M3 rich data
    lines_formatted = []
    for line in estimate.boqLines:
        lines_formatted.append({
            "code": line.itemCode,
            "itemCode": line.itemCode,
            "boqItemId": line.boqItemId,
            "section": line.section,
            "description": line.description,
            "specification": line.specification,
            "quantity": line.quantity,
            "unit": line.unit,
            "unitRate": line.unitRate,
            "amount": line.amount,
            "materialRate": line.materialRate,
            "labourRate": line.labourRate,
            "equipmentRate": line.equipmentRate,
            "materialAmount": line.materialAmount,
            "labourAmount": line.labourAmount,
            "equipmentAmount": line.equipmentAmount,
            "wastageAmount": line.wastageAmount,
            "designVersionId": model.designVersionId,
            "takeoffRuleVersion": "IS-1200-METHOD-OF-MEASUREMENT-2026.Q3",
            "measurementRuleId": line.measurementRuleId,
            "canonicalElementIds": line.sourceElementIds,
            "sourceElementIds": line.sourceElementIds,
            "sourceRefs": f"{len(line.sourceElementIds)} CBM elements",
            "wastePolicy": "Standard allowance (4-5%)",
            "confidence": line.confidence.value if hasattr(line.confidence, "value") else str(line.confidence),
            "sourceType": line.sourceType.value if hasattr(line.sourceType, "value") else str(line.sourceType),
            "rateSnapshotId": line.rateSnapshotId,
            "assemblyId": line.assemblyId,
            "status": line.status
        })

    wf = estimate.costWaterfall
    direct_hard_cost = wf.grossHardCost
    contingency = wf.contingency
    contractor_prelims = wf.overheadAndPrelims
    total_base_estimate = wf.totalConstructionCost

    low_estimate = round(total_base_estimate * 0.95, 2)
    high_estimate = round(total_base_estimate * 1.10, 2)

    return {
        "designVersionId": model.designVersionId,
        "buildingModelId": model.modelId,
        "modelHash": model.metadata.modelHash,
        "rateSnapshotId": estimate.rateSnapshotId,
        "qualityTier": quality_tier,
        "currency": "INR",
        "directHardCost": direct_hard_cost,
        "contingency": contingency,
        "contractorPrelims": contractor_prelims,
        "totalBaseEstimate": total_base_estimate,
        "estimateRange": {
            "low": low_estimate,
            "expected": total_base_estimate,
            "high": high_estimate
        },
        "costPerSqmBUA": wf.costPerSqmBUA,
        "costPerSqFtBUA": wf.costPerSqFtBUA,
        "costWaterfall": wf.dict(),
        "lines": lines_formatted,
        "takeoffRecords": [r.dict() for r in takeoff_records],
        "qtoHash": estimate.qtoHash,
        "boqHash": estimate.boqHash,
        "costHash": estimate.costHash,
        "confidenceSummary": estimate.confidenceSummary,
        "disclaimer": estimate.disclaimer,
        "calculatedAt": estimate.calculatedAt
    }
