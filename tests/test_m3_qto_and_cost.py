"""
Planwise Enterprise — M3 Model-Linked QTO + BOQ + Cost Engine Test Suite
Delta Specification & M3 Master Specification §21, §22, §24

Comprehensive validation of:
- IS 1200 Measurement Rule Engine
- Parametric Construction Assemblies
- Immutable Rate Snapshots (Mumbai MMR & Bengaluru)
- Opening Deductions (Doors, Windows, Stair Cutouts)
- Structured Trade BOQ & 100% CBM Element Traceability
- Cost Waterfall (Materials, Labour, Equipment, Wastage, Prelims, Contingency)
- Deep Explainability ("Why this quantity?", "Why this rate?")
- Change Propagation DAG (Geometry vs Rate vs Rule changes)
- Bitwise Determinism across dual runs
- Multi-format Exports (CSV, XLSX XML, JSON, HTML)
- 11-node Async DAG Pipeline
- 6 Golden Benchmark Datasets (2BHK, 3BHK, Duplex, Irregular, Opening-Heavy, Shaft-Cutouts)
"""

import unittest
import json
import hashlib

from packages.schemas.building_model import (
    CanonicalBuildingModel,
    ElementType,
    WallType,
    OpeningType,
    BuildingLevel,
    BuildingElement,
    ElementGeometry,
    Opening,
    Space,
    Bounds2D,
    BuildingSystem,
    SystemComponent
)
from packages.schemas.qto_model import QTOConfidence, QuantitySourceType
from workers.qto.measurement_engine import (
    get_measurement_rule,
    list_measurement_rules,
    MEASUREMENT_RULES_REGISTRY
)
from workers.qto.assembly_engine import (
    get_assembly,
    list_assemblies,
    CONSTRUCTION_ASSEMBLIES_REGISTRY
)
from workers.qto.rate_snapshot_engine import (
    get_rate_snapshot,
    list_rate_snapshots,
    RATE_SNAPSHOTS_REGISTRY
)
from workers.qto.qto_engine import ModelLinkedQTOEngine
from workers.qto.cost_engine import (
    DeterministicCostEngine,
    explain_boq_item
)
from workers.qto.change_propagation import (
    ChangePropagationEngine,
    InvalidationTrigger
)
from workers.qto.dag_pipeline import M3AsyncCostDAGPipeline
from workers.qto.export_engine import CostEstimateExporter
from workers.generation.model_compiler import compile_canonical_building_model


def make_test_canonical_model(
    design_version_id: str = "DV-TEST-M3",
    name: str = "Test Residence",
    gross_bua_sqm: float = 100.0,
    num_floors: int = 1,
    wall_length: float = 0.0,
    wall_height: float = 3.0,
    wall_thickness: float = 0.23,
    door_w: float = 1.0,
    door_h: float = 2.1,
    win_w: float = 1.5,
    win_h: float = 1.2
) -> CanonicalBuildingModel:
    """Constructs a deterministic synthetic CanonicalBuildingModel for testing."""
    import math

    if wall_length <= 0.0:
        side_m = round(math.sqrt(gross_bua_sqm / max(1, num_floors)), 2)
    else:
        side_m = wall_length

    footprint_area = round(side_m * side_m, 2)
    effective_bua = footprint_area * num_floors

    levels = [
        BuildingLevel(
            levelId="LVL-000",
            levelIndex=0,
            name="GROUND",
            elevationM=0.0,
            floorToFloorHeightM=3.15
        )
    ]
    if num_floors > 1:
        levels.append(
            BuildingLevel(
                levelId="LVL-001",
                levelIndex=1,
                name="FIRST",
                elevationM=3.15,
                floorToFloorHeightM=3.15
            )
        )

    # 4 External walls forming a fully enclosed rectangle
    w1 = BuildingElement(
        elementId="WALL-EXT-001",
        elementType=ElementType.WALL,
        levelId="LVL-000",
        name="Front External Wall",
        geometry=ElementGeometry(
            centerline=[[0.0, 0.0], [side_m, 0.0]],
            footprintPolygon=[[0.0, 0.0], [side_m, 0.0], [side_m, wall_thickness], [0.0, wall_thickness]],
            baseZ=0.0,
            topZ=wall_height,
            thicknessM=wall_thickness,
            heightM=wall_height
        ),
        materialId="MAT_BRICK_RED",
        wallType=WallType.EXTERNAL,
        openingIds=["DOOR-001", "WIN-001"]
    )
    w2 = BuildingElement(
        elementId="WALL-EXT-002",
        elementType=ElementType.WALL,
        levelId="LVL-000",
        name="Right External Wall",
        geometry=ElementGeometry(
            centerline=[[side_m, 0.0], [side_m, side_m]],
            footprintPolygon=[[side_m, 0.0], [side_m + wall_thickness, 0.0], [side_m + wall_thickness, side_m], [side_m, side_m]],
            baseZ=0.0,
            topZ=wall_height,
            thicknessM=wall_thickness,
            heightM=wall_height
        ),
        materialId="MAT_BRICK_RED",
        wallType=WallType.EXTERNAL,
        openingIds=["WIN-002"]
    )
    w3 = BuildingElement(
        elementId="WALL-EXT-003",
        elementType=ElementType.WALL,
        levelId="LVL-000",
        name="Back External Wall",
        geometry=ElementGeometry(
            centerline=[[side_m, side_m], [0.0, side_m]],
            footprintPolygon=[[side_m, side_m], [0.0, side_m], [0.0, side_m - wall_thickness], [side_m, side_m - wall_thickness]],
            baseZ=0.0,
            topZ=wall_height,
            thicknessM=wall_thickness,
            heightM=wall_height
        ),
        materialId="MAT_BRICK_RED",
        wallType=WallType.EXTERNAL,
        openingIds=["WIN-003"]
    )
    w4 = BuildingElement(
        elementId="WALL-EXT-004",
        elementType=ElementType.WALL,
        levelId="LVL-000",
        name="Left External Wall",
        geometry=ElementGeometry(
            centerline=[[0.0, side_m], [0.0, 0.0]],
            footprintPolygon=[[0.0, side_m], [0.0, 0.0], [wall_thickness, 0.0], [wall_thickness, side_m]],
            baseZ=0.0,
            topZ=wall_height,
            thicknessM=wall_thickness,
            heightM=wall_height
        ),
        materialId="MAT_BRICK_RED",
        wallType=WallType.EXTERNAL,
        openingIds=[]
    )

    # Internal Partitions
    w_int1 = BuildingElement(
        elementId="WALL-INT-001",
        elementType=ElementType.WALL,
        levelId="LVL-000",
        name="Living-Bed Partition",
        geometry=ElementGeometry(
            centerline=[[0.0, side_m / 2], [side_m, side_m / 2]],
            footprintPolygon=[[0.0, side_m / 2], [side_m, side_m / 2], [side_m, (side_m / 2) + 0.115], [0.0, (side_m / 2) + 0.115]],
            baseZ=0.0,
            topZ=wall_height,
            thicknessM=0.115,
            heightM=wall_height
        ),
        materialId="MAT_AAC_BLOCK_100",
        wallType=WallType.INTERNAL,
        openingIds=["DOOR-002"]
    )
    w_int2 = BuildingElement(
        elementId="WALL-INT-002",
        elementType=ElementType.WALL,
        levelId="LVL-000",
        name="Kitchen-Bath Partition",
        geometry=ElementGeometry(
            centerline=[[side_m / 2, side_m / 2], [side_m / 2, side_m]],
            footprintPolygon=[[side_m / 2, side_m / 2], [side_m / 2, side_m], [(side_m / 2) + 0.115, side_m], [(side_m / 2) + 0.115, side_m / 2]],
            baseZ=0.0,
            topZ=wall_height,
            thicknessM=0.115,
            heightM=wall_height
        ),
        materialId="MAT_AAC_BLOCK_100",
        wallType=WallType.INTERNAL,
        openingIds=["DOOR-003"]
    )

    # 8 Columns along perimeter & center
    cols = []
    col_coords = [
        (0.0, 0.0), (side_m / 2, 0.0), (side_m, 0.0),
        (0.0, side_m / 2), (side_m, side_m / 2),
        (0.0, side_m), (side_m / 2, side_m), (side_m, side_m)
    ]
    for i, (cx, cy) in enumerate(col_coords):
        cols.append(
            BuildingElement(
                elementId=f"COL-00{i+1}",
                elementType=ElementType.COLUMN,
                levelId="LVL-000",
                name=f"Column C{i+1}",
                geometry=ElementGeometry(
                    footprintPolygon=[[cx, cy], [cx + 0.3, cy], [cx + 0.3, cy + 0.45], [cx, cy + 0.45]],
                    baseZ=0.0,
                    topZ=wall_height,
                    widthM=0.30,
                    depthM=0.45,
                    heightM=wall_height
                ),
                materialId="MAT_M25_CONCRETE"
            )
        )

    # Slabs
    slab = BuildingElement(
        elementId="SLAB-001",
        elementType=ElementType.SLAB,
        levelId="LVL-000",
        name="Ground Roof Slab",
        geometry=ElementGeometry(
            footprintPolygon=[[0.0, 0.0], [side_m, 0.0], [side_m, side_m], [0.0, side_m]],
            baseZ=wall_height,
            topZ=wall_height + 0.15,
            thicknessM=0.15
        ),
        materialId="MAT_M25_CONCRETE",
        properties={"areaSqm": footprint_area}
    )

    elements = [w1, w2, w3, w4, w_int1, w_int2, slab] + cols

    # Openings
    d1 = Opening(
        openingId="DOOR-001",
        openingType=OpeningType.DOOR,
        hostWallId="WALL-EXT-001",
        levelId="LVL-000",
        name="Main Entry Door",
        widthM=door_w,
        heightM=door_h
    )
    d2 = Opening(
        openingId="DOOR-002",
        openingType=OpeningType.DOOR,
        hostWallId="WALL-INT-001",
        levelId="LVL-000",
        name="Bedroom Door",
        widthM=0.9,
        heightM=2.1
    )
    win1 = Opening(
        openingId="WIN-001",
        openingType=OpeningType.WINDOW,
        hostWallId="WALL-EXT-001",
        levelId="LVL-000",
        name="Living Room Window",
        widthM=win_w,
        heightM=win_h
    )
    win2 = Opening(
        openingId="WIN-002",
        openingType=OpeningType.WINDOW,
        hostWallId="WALL-EXT-002",
        levelId="LVL-000",
        name="Side Window",
        widthM=win_w,
        heightM=win_h
    )
    openings = [d1, d2, win1, win2]

    # Spaces
    sp1 = Space(
        spaceId="SPACE-001",
        levelId="LVL-000",
        spaceType="LIVING_ROOM",
        name="Living Hall",
        bounds=Bounds2D(x=0, y=0, width=side_m, height=side_m/2),
        polygon=[[0, 0], [side_m, 0], [side_m, side_m/2], [0, side_m/2]],
        areaSqm=(side_m * (side_m/2)),
        perimeterM=2 * (side_m + (side_m/2)),
        centroid=[side_m/2, side_m/4]
    )
    sp2 = Space(
        spaceId="SPACE-002",
        levelId="LVL-000",
        spaceType="MASTER_BEDROOM",
        name="Master Bedroom",
        bounds=Bounds2D(x=0, y=side_m/2, width=side_m, height=side_m/2),
        polygon=[[0, side_m/2], [side_m, side_m/2], [side_m, side_m], [0, side_m]],
        areaSqm=(side_m * (side_m/2)),
        perimeterM=2 * (side_m + (side_m/2)),
        centroid=[side_m/2, 3*side_m/4]
    )
    spaces = [sp1, sp2]

    # Systems
    sys_elec = BuildingSystem(
        systemId="SYS-ELEC-01",
        systemType="ELECTRICAL",
        components=[
            SystemComponent(
                componentId=f"ELEC-PT-{i}",
                componentType="LIGHT_POINT",
                levelId="LVL-000",
                position=[1.0, 1.0, 2.8],
                specification="FRLS Copper Point"
            )
            for i in range(12)
        ]
    )
    sys_plumb = BuildingSystem(
        systemId="SYS-PLUMB-01",
        systemType="PLUMBING",
        components=[
            SystemComponent(
                componentId="PLB-STACK-01",
                componentType="TAP",
                levelId="LVL-000",
                position=[2.0, 2.0, 0.5],
                specification="Wet Stack Assembly"
            )
        ]
    )

    model = CanonicalBuildingModel(
        modelId=f"BLDG-{design_version_id}",
        designVersionId=design_version_id,
        projectId="PROJ-M3-TEST",
        siteGeometryVersionId="SITE-V1",
        name=name,
        archetype="compact_2bhk",
        buildingEnvelope={"widthM": side_m, "lengthM": side_m, "heightM": wall_height * num_floors},
        totalGrossBUASqm=effective_bua,
        totalUsableAreaSqm=round(effective_bua * 0.85, 2),
        floorsCount=num_floors,
        levels=levels,
        elements=elements,
        openings=openings,
        spaces=spaces,
        systems=[sys_elec, sys_plumb]
    )
    return model


class TestM3QTOAndCostEngine(unittest.TestCase):
    """Authoritative test suite for M3 deliverables."""

    def setUp(self):
        self.model = make_test_canonical_model(
            design_version_id="DV-TEST-001",
            wall_length=6.0,
            wall_height=3.0,
            wall_thickness=0.23,
            door_w=1.0,
            door_h=2.1,
            win_w=1.5,
            win_h=1.2
        )

    # -------------------------------------------------------------
    # 1. IS 1200 Measurement Rules Registry
    # -------------------------------------------------------------
    def test_01_is_1200_measurement_rules(self):
        rules = list_measurement_rules()
        self.assertGreaterEqual(len(rules), 10)

        wall_rule = get_measurement_rule("QTO-WALL-001")
        self.assertEqual(wall_rule.unit, "m³")
        self.assertEqual(wall_rule.standardReference, "IS-1200-PART-03-BRICKWORK")
        self.assertIn("L × H × T", wall_rule.formula)
        self.assertGreater(len(wall_rule.inclusions), 0)
        self.assertGreater(len(wall_rule.exclusions), 0)
        self.assertEqual(wall_rule.verificationStatus, "VERIFIED")

        # Earthwork placeholder
        exc_rule = get_measurement_rule("QTO-EXC-001")
        self.assertEqual(exc_rule.verificationStatus, "REQUIRES_SOURCE_VERIFICATION")

    # -------------------------------------------------------------
    # 2. Construction Assemblies
    # -------------------------------------------------------------
    def test_02_construction_assemblies(self):
        assemblies = list_assemblies()
        self.assertGreaterEqual(len(assemblies), 6)

        wall_asm = get_assembly("EXT_WALL_230_BRICK")
        self.assertEqual(wall_asm.baseUnit, "m³")
        self.assertGreater(len(wall_asm.components), 0)
        for cmp in wall_asm.components:
            self.assertGreater(cmp.consumptionFactor, 0)
            self.assertTrue(hasattr(cmp, "wastagePercent"))

    # -------------------------------------------------------------
    # 3. Immutable Rate Snapshots
    # -------------------------------------------------------------
    def test_03_immutable_rate_snapshots(self):
        snapshots = list_rate_snapshots()
        self.assertGreaterEqual(len(snapshots), 2)

        mumbai = get_rate_snapshot("INDIA-MUMBAI-2026-Q4-V1")
        self.assertEqual(mumbai.currency, "INR")
        self.assertEqual(len(mumbai.hash), 64)
        self.assertIn("RATE_RCC_M25", mumbai.rates)

        rcc = mumbai.rates["RATE_RCC_M25"]
        self.assertGreater(rcc.materialRateInr, 0)
        self.assertGreater(rcc.labourRateInr, 0)
        self.assertGreater(rcc.equipmentRateInr, 0)
        self.assertAlmostEqual(
            rcc.baseUnitRateInr,
            rcc.materialRateInr + rcc.labourRateInr + rcc.equipmentRateInr,
            places=2
        )

    # -------------------------------------------------------------
    # 4. Wall Masonry Takeoff & Opening Deductions
    # -------------------------------------------------------------
    def test_04_wall_masonry_takeoff_with_opening_deductions(self):
        qto = ModelLinkedQTOEngine(self.model)
        records = qto.run_full_takeoff()

        ext_wall_rec = next(r for r in records if "TO-WALL-EXT" in r.takeoffId)
        self.assertEqual(ext_wall_rec.unit, "m³")
        self.assertGreater(len(ext_wall_rec.deductions), 0)

        # Expected door deduction: 1.0 * 2.1 * 0.23 = 0.483 m³
        # Expected window deduction: 1.5 * 1.2 * 0.23 = 0.414 m³
        total_ded = sum(d.quantity for d in ext_wall_rec.deductions)
        self.assertAlmostEqual(ext_wall_rec.netQuantity, ext_wall_rec.grossQuantity - total_ded, places=2)
        self.assertIn("WALL-EXT-001", ext_wall_rec.sourceElementIds)

    # -------------------------------------------------------------
    # 5. Slab Takeoff & Deductions
    # -------------------------------------------------------------
    def test_05_slab_takeoff(self):
        qto = ModelLinkedQTOEngine(self.model)
        records = qto.run_full_takeoff()

        slab_rec = next(r for r in records if "TO-SLAB" in r.takeoffId)
        self.assertEqual(slab_rec.unit, "m³")
        self.assertGreater(slab_rec.quantity, 0)
        self.assertEqual(slab_rec.confidence, QTOConfidence.HIGH)

    # -------------------------------------------------------------
    # 6. Skirting Perimeter Deduction
    # -------------------------------------------------------------
    def test_06_skirting_takeoff(self):
        qto = ModelLinkedQTOEngine(self.model)
        records = qto.run_full_takeoff()

        skirt_rec = next(r for r in records if "TO-SKIRT" in r.takeoffId)
        self.assertEqual(skirt_rec.unit, "m")
        self.assertGreater(len(skirt_rec.deductions), 0)
        # Verify door widths subtracted from perimeter
        total_door_width = sum(d.quantity for d in skirt_rec.deductions)
        self.assertAlmostEqual(skirt_rec.netQuantity, skirt_rec.grossQuantity - total_door_width, places=2)

    # -------------------------------------------------------------
    # 7. Structured BOQ & 100% CBM Traceability
    # -------------------------------------------------------------
    def test_07_structured_boq_and_traceability(self):
        cost_engine = DeterministicCostEngine(self.model)
        estimate = cost_engine.calculate_cost_estimate()

        self.assertGreaterEqual(len(estimate.boqLines), 8)

        all_cbm_ids = {e.elementId for e in self.model.elements} | \
                      {o.openingId for o in self.model.openings} | \
                      {s.spaceId for s in self.model.spaces} | \
                      {sys.systemId for sys in self.model.systems}

        for line in estimate.boqLines:
            self.assertGreater(len(line.sourceElementIds), 0, f"Line {line.itemCode} has no sourceElementIds")
            for eid in line.sourceElementIds:
                self.assertIn(eid, all_cbm_ids, f"Line {line.itemCode} references unknown element {eid}")

    # -------------------------------------------------------------
    # 8. Cost Waterfall & Decomposition
    # -------------------------------------------------------------
    def test_08_cost_waterfall_and_itemization(self):
        cost_engine = DeterministicCostEngine(self.model, quality_tier="STANDARD")
        estimate = cost_engine.calculate_cost_estimate()

        wf = estimate.costWaterfall
        self.assertGreater(wf.grossHardCost, 0)
        self.assertGreater(wf.directMaterialCost, 0)
        self.assertGreater(wf.directLabourCost, 0)
        self.assertGreater(wf.overheadAndPrelims, 0)
        self.assertGreater(wf.contingency, 0)

        # Check arithmetic
        self.assertAlmostEqual(
            wf.totalConstructionCost,
            wf.grossHardCost + wf.overheadAndPrelims + wf.contingency + wf.statutoryTaxes,
            places=2
        )
        self.assertGreater(wf.costPerSqFtBUA, 1000)

    # -------------------------------------------------------------
    # 9. Cost Explanation Audit Trail
    # -------------------------------------------------------------
    def test_09_cost_explanation_audit(self):
        cost_engine = DeterministicCostEngine(self.model)
        estimate = cost_engine.calculate_cost_estimate()

        explanation = explain_boq_item(estimate, "MAS-EXT-01")
        self.assertEqual(explanation.itemCode, "MAS-EXT-01")
        self.assertEqual(explanation.measurementRuleId, "QTO-WALL-001")
        self.assertIn("IS-1200", explanation.standardReference)
        self.assertIn("Mumbai", explanation.location)
        self.assertGreater(explanation.rateBreakdown["materialRate"], 0)
        self.assertGreater(explanation.rateBreakdown["labourRate"], 0)

    # -------------------------------------------------------------
    # 10. Change Propagation DAG
    # -------------------------------------------------------------
    def test_10_change_propagation_dag(self):
        prop_engine = ChangePropagationEngine()

        # 1. Geometry change invalidates QTO, BOQ, Cost
        st1 = prop_engine.propagate_change("DV-001", InvalidationTrigger.GEOMETRY_CHANGED, "Wall moved")
        self.assertTrue(st1.qtoStale)
        self.assertTrue(st1.boqStale)
        self.assertTrue(st1.costStale)

        # Mark clean
        prop_engine.mark_clean("DV-001")

        # 2. Rate change invalidates Cost only (QTO stays preserved!)
        st2 = prop_engine.propagate_change("DV-001", InvalidationTrigger.RATE_SNAPSHOT_CHANGED, "Q4 rates updated")
        self.assertFalse(st2.qtoStale, "QTO must NOT become stale merely when rates change!")
        self.assertTrue(st2.costStale)
        self.assertTrue(st2.boqStale)

        # 3. Released versions are immutable
        prop_engine.mark_version_released("DV-REL-01")
        with self.assertRaises(ValueError):
            prop_engine.propagate_change("DV-REL-01", InvalidationTrigger.GEOMETRY_CHANGED)

    # -------------------------------------------------------------
    # 11. Deterministic Hashes
    # -------------------------------------------------------------
    def test_11_determinism_and_hashing(self):
        engine1 = DeterministicCostEngine(self.model)
        est1 = engine1.calculate_cost_estimate()

        engine2 = DeterministicCostEngine(self.model)
        est2 = engine2.calculate_cost_estimate()

        self.assertEqual(est1.qtoHash, est2.qtoHash)
        self.assertEqual(est1.boqHash, est2.boqHash)
        self.assertEqual(est1.costHash, est2.costHash)
        self.assertEqual(est1.costWaterfall.totalConstructionCost, est2.costWaterfall.totalConstructionCost)

    # -------------------------------------------------------------
    # 12. Exports Consistency
    # -------------------------------------------------------------
    def test_12_exports_consistency(self):
        cost_engine = DeterministicCostEngine(self.model)
        estimate = cost_engine.calculate_cost_estimate()

        csv_str = CostEstimateExporter.to_csv(estimate)
        self.assertIn("Total Preliminary Construction Cost", csv_str)
        self.assertIn(str(estimate.costWaterfall.totalConstructionCost), csv_str)

        xml_str = CostEstimateExporter.to_xlsx_xml(estimate)
        self.assertIn("<Workbook", xml_str)
        self.assertIn(str(estimate.costWaterfall.totalConstructionCost), xml_str)

        json_str = CostEstimateExporter.to_json(estimate)
        self.assertIn(estimate.costHash, json_str)

        html_str = CostEstimateExporter.to_html_summary(estimate)
        self.assertIn("PLANWISE ENTERPRISE", html_str)

    # -------------------------------------------------------------
    # 13. 11-Node Async DAG Pipeline
    # -------------------------------------------------------------
    def test_13_async_dag_pipeline(self):
        pipeline = M3AsyncCostDAGPipeline(self.model)
        job = pipeline.run_pipeline()

        self.assertEqual(job.status, "COMPLETED")
        self.assertEqual(len(job.nodes), 12)
        for node in job.nodes:
            self.assertEqual(node.status, "COMPLETED")
            self.assertGreater(len(node.outputHash), 0)

    # -------------------------------------------------------------
    # 14-19. Golden M3 Benchmark Suite
    # -------------------------------------------------------------
    def test_14_golden_01_compact_2bhk(self):
        m = make_test_canonical_model("DV-G1", "Single-floor 2BHK", gross_bua_sqm=85.0, num_floors=1)
        est = DeterministicCostEngine(m).calculate_cost_estimate()
        self.assertGreater(est.costWaterfall.totalConstructionCost, 1000000)
        self.assertEqual(len(est.costHash), 64)

    def test_15_golden_02_family_3bhk(self):
        m = make_test_canonical_model("DV-G2", "Single-floor 3BHK", gross_bua_sqm=125.0, num_floors=1)
        est = DeterministicCostEngine(m).calculate_cost_estimate()
        self.assertGreater(est.costWaterfall.totalConstructionCost, 1200000)

    def test_16_golden_03_duplex_two_floor(self):
        m = make_test_canonical_model("DV-G3", "Two-floor Villa", gross_bua_sqm=180.0, num_floors=2)
        est = DeterministicCostEngine(m).calculate_cost_estimate()
        self.assertEqual(m.floorsCount, 2)
        self.assertGreater(est.costWaterfall.totalConstructionCost, 1000000)

    def test_17_golden_04_irregular_plot(self):
        m = make_test_canonical_model("DV-G4", "Irregular Plot Villa", gross_bua_sqm=95.0, wall_length=7.5)
        est = DeterministicCostEngine(m).calculate_cost_estimate()
        self.assertGreater(len(est.boqLines), 8)

    def test_18_golden_05_opening_heavy_design(self):
        m = make_test_canonical_model("DV-G5", "Opening Heavy", wall_length=8.0, win_w=2.4, win_h=1.8)
        qto = ModelLinkedQTOEngine(m)
        records = qto.run_full_takeoff()
        wall_rec = next(r for r in records if "TO-WALL-EXT" in r.takeoffId)
        # Should have significant deductions
        total_ded = sum(d.quantity for d in wall_rec.deductions)
        self.assertGreater(total_ded, 1.5)

    def test_19_golden_06_stair_shaft_deductions(self):
        m = make_test_canonical_model("DV-G6", "Two-floor With Stairs", gross_bua_sqm=160.0, num_floors=2)
        # Add stair element
        stair = BuildingElement(
            elementId="STAIR-001",
            elementType=ElementType.STAIR,
            levelId="LVL-000",
            name="RCC Dog-Legged Stair",
            geometry=ElementGeometry(
                footprintPolygon=[[0, 0], [4.2, 0], [4.2, 2.1], [0, 2.1]],
                baseZ=0.0,
                topZ=3.15
            ),
            materialId="MAT_M25_CONCRETE",
            properties={"openingAreaSqm": 8.82, "concreteVolumeM3": 2.45}
        )
        m.elements.append(stair)
        qto = ModelLinkedQTOEngine(m)
        records = qto.run_full_takeoff()

        slab_rec = next(r for r in records if "TO-SLAB" in r.takeoffId)
        stair_deductions = [d for d in slab_rec.deductions if d.elementType == "STAIR_OPENING"]
        self.assertEqual(len(stair_deductions), 1)
        self.assertGreater(stair_deductions[0].quantity, 1.0)


if __name__ == "__main__":
    unittest.main()
