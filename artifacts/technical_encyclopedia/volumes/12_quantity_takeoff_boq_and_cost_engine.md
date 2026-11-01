# Volume XII — Quantity Takeoff, BOQ, and Cost Engine

## 1. Indian Standard IS 1200 Measurement Principles
Quantity extraction in Planwise (`workers/qto/qto_engine.py`) strictly adheres to **IS 1200: Methods of Measurement of Building Works**:

### 1.1 IS 1200 Part 2: Concrete Work
- Plinth beams, columns, lintels, and floor slabs measured net in cubic meters ($m^3$).
- Slab volume: $V_{\text{slab}} = A_{\text{slab}} \times T_{\text{slab}}$ ($T = 0.15\text{ m}$).
- Column volume: $V_{\text{col}} = N_{\text{col}} \times W \times D \times H$.

### 1.2 IS 1200 Part 3: Brick and Block Masonry
- Wall masonry volume calculated net in cubic meters ($m^3$):
  $$V_{\text{masonry}} = L_{\text{wall}} \times T_{\text{wall}} \times H_{\text{wall}} - V_{\text{openings}} - V_{\text{lintels}}$$

### 1.3 IS 1200 Part 12: Plastering Opening Deduction Rules
Strict opening deduction logic implemented in `workers/qto/qto_engine.py`:
- **Opening Area $< 0.5\text{ m}^2$:** No deduction made; no addition for jambs/sills.
- **Opening Area $0.5\text{ m}^2 \le A \le 3.0\text{ m}^2$:** Deduction made for **one face only**; no addition for jambs or sills.
- **Opening Area $> 3.0\text{ m}^2$:** Deductions made for **both faces** of the wall; additions made for jambs, sills, and soffits.

---

## 2. Model-Linked QTO Engine Implementation (`workers/qto/qto_engine.py`)

```python
"""
Planwise Enterprise — Model-Linked Quantity Takeoff (QTO) Engine
Delta Specification & M3 Master Specification §1, §4, §5, §10, §16

Extracts deterministic, fully traceable takeoff records from CanonicalBuildingModel elements.
Every takeoff record:
- Points to specific CBM element IDs (sourceElementIds)
- Computes gross, geometric deductions, and net quantities
- References a versioned IS 1200 measurement rule
- Produces deterministic cryptographic SHA-256 fingerprints
- Carries rigorous confidence and provenance metadata
"""

import math
from typing import Dict, List, Any, Optional, Tuple
from shapely.geometry import Polygon

from packages.schemas.building_model import (
    CanonicalBuildingModel,
    ElementType,
    WallType,
    OpeningType,
    BuildingElement,
    Opening,
    Space
)
from packages.schemas.qto_model import (
    TakeoffRecord,
    DeductionItem,
    DeductionType,
    QTOConfidence,
    QuantitySourceType
)
from workers.qto.measurement_engine import get_measurement_rule


def compute_polygon_area(coords: List[List[float]]) -> float:
    """Computes exact 2D planar polygon area using Shapely or shoelace formula."""
    if not coords or len(coords) < 3:
        return 0.0
    try:
        poly = Polygon(coords)
        if poly.is_valid:
            return abs(poly.area)
    except Exception:
        pass
    # Shoelace fallback
    area = 0.0
    n = len(coords)
    for i in range(n):
        j = (i + 1) % n
        area += coords[i][0] * coords[j][1]
        area -= coords[j][0] * coords[i][1]
    return abs(area) / 2.0


def compute_polygon_perimeter(coords: List[List[float]]) -> float:
    """Computes perimeter length of polygon."""
    if not coords or len(coords) < 2:
        return 0.0
    perimeter = 0.0
    n = len(coords)
    for i in range(n):
        j = (i + 1) % n
        dx = coords[j][0] - coords[i][0]
        dy = coords[j][1] - coords[i][1]
        perimeter += math.sqrt(dx*dx + dy*dy)
    return perimeter


class ModelLinkedQTOEngine:
    """
    Authoritative QTO Engine for Planwise Enterprise.
    Converts CanonicalBuildingModel into a collection of validated TakeoffRecords.
    """

    def __init__(self, model: CanonicalBuildingModel):
        self.model = model
        self.design_version_id = model.designVersionId
        self.project_id = model.projectId
        self.elements_by_id: Dict[str, BuildingElement] = {e.elementId: e for e in model.elements}
        self.openings_by_id: Dict[str, Opening] = {o.openingId: o for o in model.openings}
        self.spaces_by_id: Dict[str, Space] = {s.spaceId: s for s in model.spaces}

        # Index openings by host wall
        self.openings_by_wall: Dict[str, List[Opening]] = {}
        for o in model.openings:
            self.openings_by_wall.setdefault(o.hostWallId, []).append(o)

    def run_full_takeoff(self) -> List[TakeoffRecord]:
        """Runs complete deterministic takeoff across all model disciplines."""
        records: List[TakeoffRecord] = []

        # 1. Earthwork Excavation (Preliminary)
        rec_exc = self._takeoff_earthwork()
        if rec_exc:
            records.append(rec_exc)

        # 2. Structural Column Concrete
        rec_col = self._takeoff_columns()
        if rec_col:
            records.append(rec_col)

        # 3. Structural Slab Concrete
        rec_slab = self._takeoff_slabs()
        if rec_slab:
            records.append(rec_slab)

        # 4. Staircase Concrete
        rec_stair = self._takeoff_stairs()
        if rec_stair:
            records.append(rec_stair)

        # 5. External Brick Masonry (230mm) with Opening Deductions
        rec_ext_wall = self._takeoff_external_walls()
        if rec_ext_wall:
            records.append(rec_ext_wall)

        # 6. Internal Partition Blockwork (100/115mm) with Opening Deductions
        rec_int_wall = self._takeoff_internal_walls()
        if rec_int_wall:
            records.append(rec_int_wall)

        # 7. Internal Plaster
        rec_plaster_int = self._takeoff_internal_plaster()
        if rec_plaster_int:
            records.append(rec_plaster_int)

        # 8. External Plaster
        rec_plaster_ext = self._takeoff_external_plaster()
        if rec_plaster_ext:
            records.append(rec_plaster_ext)

        # 9. Floor Tiling Finishes
        rec_floor = self._takeoff_flooring()
        if rec_floor:
            records.append(rec_floor)

        # 10. Skirting Length (Perimeter minus door widths)
        rec_skirting = self._takeoff_skirting()
        if rec_skirting:
            records.append(rec_skirting)

        # 11. Doors Count
        rec_doors = self._takeoff_doors()
        if rec_doors:
            records.append(rec_doors)

        # 12. Windows Count
        rec_windows = self._takeoff_windows()
        if rec_windows:
            records.append(rec_windows)

        # 13. Waterproofing
        rec_wp = self._takeoff_waterproofing()
        if rec_wp:
            records.append(rec_wp)

        # 14. Painting
        rec_paint = self._takeoff_painting(rec_plaster_int, rec_plaster_ext)
        if rec_paint:
            records.append(rec_paint)

        # 15. Preliminary MEP (Electrical & Plumbing)
        rec_elec, rec_plumb = self._takeoff_preliminary_mep()
        if rec_elec:
            records.append(rec_elec)
        if rec_plumb:
            records.append(rec_plumb)

        return records

    # -------------------------------------------------------------
    # Trade Takeoff Implementations
    # -------------------------------------------------------------

    def _takeoff_earthwork(self) -> Optional[TakeoffRecord]:
        cols = [e for e in self.model.elements if e.elementType == ElementType.COLUMN]
        count_cols = len(cols)
        if count_cols == 0:
            count_cols = max(4, int(self.model.totalGrossBUASqm / 16.0))

        # Nominal 1.8m x 1.8m x 1.5m footing pit + 10% working space allowance per column
        nominal_pit_vol = 1.8 * 1.8 * 1.5 * 1.10
        gross_qty = round(count_cols * nominal_pit_vol, 3)

        source_ids = [c.elementId for c in cols] if cols else [e.elementId for e in self.model.elements[:4]]
        if not source_ids:
            source_ids = [s.spaceId for s in self.model.spaces[:4]]

        rule = get_measurement_rule("QTO-EXC-001")
        rec = TakeoffRecord(
            takeoffId=f"TO-EXC-{self.design_version_id}",
            designVersionId=self.design_version_id,
            projectId=self.project_id,
            discipline="CIVIL_STRUCTURAL",
            category="EARTHWORK",
            elementType="FOUNDATION",
            assemblyId="EARTHWORK_EXCAVATION",
            grossQuantity=gross_qty,
            deductions=[],
            netQuantity=gross_qty,
            quantity=gross_qty,
            unit="m³",
            measurementRuleId=rule.ruleId,
            sourceElementIds=source_ids,
            geometryFingerprint=f"col_count_{count_cols}_depth_1.5m",
            confidence=QTOConfidence.PRELIMINARY,
            sourceType=QuantitySourceType.PROFESSIONAL_REVIEW_REQUIRED
        )
        rec.compute_hashes({"col_count": count_cols, "pit_vol": nominal_pit_vol})
        return rec

    def _takeoff_columns(self) -> Optional[TakeoffRecord]:
        cols = [e for e in self.model.elements if e.elementType == ElementType.COLUMN]
        if not cols:
            return None

        total_vol = 0.0
        col_ids = []
        for c in cols:
            col_ids.append(c.elementId)
            w = c.geometry.widthM or (c.properties.get("widthMm", 300) / 1000.0)
            d = c.geometry.depthM or (c.properties.get("depthMm", 450) / 1000.0)
            h = c.geometry.heightM or (c.geometry.topZ - c.geometry.baseZ) or 3.15
            total_vol += (w * d * h)

        total_vol = round(total_vol, 3)
        rule = get_measurement_rule("QTO-COL-001")
        rec = TakeoffRecord(
            takeoffId=f"TO-COL-{self.design_version_id}",
            designVersionId=self.design_version_id,
            projectId=self.project_id,
            discipline="CIVIL_STRUCTURAL",
            category="CONCRETE",
            elementType="COLUMN",
            assemblyId="RCC_COLUMN_M25",
            grossQuantity=total_vol,
            deductions=[],
            netQuantity=total_vol,
            quantity=total_vol,
            unit="m³",
            measurementRuleId=rule.ruleId,
            sourceElementIds=col_ids,
            geometryFingerprint=f"columns_{len(cols)}_vol_{total_vol}",
            confidence=QTOConfidence.HIGH,
            sourceType=QuantitySourceType.MODEL_COMPUTED
        )
        rec.compute_hashes({"cols": col_ids, "vol": total_vol})
        return rec

```

---

## 3. Deterministic Cost Engine Implementation (`workers/qto/cost_engine.py`)

```python
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

```

---

## 4. Traceable BOQ Controller Interface (`workers/qto/boq_engine.py`)

```python
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

```

---

## 5. Comprehensive Cost Waterfall Architecture
The financial calculation structures project expenditure into a transparent multi-tiered waterfall:
```
  Base Direct Material Cost
+ Direct Skilled & Unskilled Labour
─────────────────────────────────────────────────
= Subtotal Prime Cost (Direct Works)
+ Site Contractor Overhead (10.0%)
+ Contractor Margin & Profit (15.0%)
─────────────────────────────────────────────────
= Subtotal Base Construction Cost
+ Unforeseen Contingency Reserve (5.0%)
─────────────────────────────────────────────────
= Total Pre-Tax Project Estimate
+ Statutory GST Tax (18.0%)
─────────────────────────────────────────────────
= FINAL GROSS BUDGET ESTIMATE
```
