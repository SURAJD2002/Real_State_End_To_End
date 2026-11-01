"""
Planwise Enterprise — Phase S1 Verification Test Suite
Tests for:
1. QTO deduction threshold (< 0.1 m2 ignored, >= 0.1 m2 deducted; net_vol has no max(1.0) floor)
2. Material wastage conservation across cost waterfall
3. Room touch adjacency requiring interval overlap (rejects non-overlapping corner touch)
4. Multi-floor stair vertical alignment (exact x/y equality across storeys)
5. CORS configuration rejecting untrusted origins
6. Deterministic CBM designHash equality across repeated runs
"""

import unittest
import sys
from pathlib import Path
from shapely.geometry import Polygon

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "apps" / "api-gateway"))
sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient
from main import app

from packages.schemas.building_model import (
    CanonicalBuildingModel, ElementType, WallType, OpeningType,
    BuildingElement, ElementGeometry, Opening, ModelMetadata, BuildingLevel
)
from packages.schemas.customer_brief import CustomerBrief, ArchitecturalStyle
from packages.schemas.room_program import RoomProgram, RoomSpecification, RoomType, build_room_program_from_brief
from packages.schemas.room_graph import RoomAdjacencyGraph, AdjacencyEdge, AdjacencyRelationshipType
from workers.qto.qto_engine import ModelLinkedQTOEngine
from workers.qto.cost_engine import DeterministicCostEngine
from workers.generation.cpsat_solver import CPSATLayoutSolver
from workers.generation.house_generator import generate_m2_house_options
from tests.test_m3_qto_and_cost import make_test_canonical_model


class TestPhaseS1Comprehensive(unittest.TestCase):
    """Rigorous verification of Phase S1 audit items."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_qto_threshold_below_and_above_0_1_m2(self):
        """
        QTO Deduction Threshold:
        Openings < 0.1 m2 are ignored (not deducted).
        Openings >= 0.1 m2 are deducted.
        Net volume has no artificial max(1.0, ...) floor.
        """
        m = make_test_canonical_model("DV-THRESH-S1", "Threshold Test", wall_length=2.0, wall_height=1.0)
        # Retain single wall to test that net quantity is below 1.0 m3 (verifying no max(1.0) floor)
        m.elements = [m.elements[0]]
        wall_id = m.elements[0].elementId

        # Add one opening < 0.1 m2 (0.2 x 0.4 = 0.08 m2) and one >= 0.1 m2 (0.5 x 0.6 = 0.30 m2)
        small_op = Opening(
            openingId="OP-TINY-S1",
            name="Tiny Ventilation Slit",
            openingType=OpeningType.WINDOW,
            hostWallId=wall_id,
            levelId="LVL-000",
            widthM=0.2,
            heightM=0.4,
            sillHeightM=0.5
        )
        large_op = Opening(
            openingId="OP-LARGE-S1",
            name="Standard Window",
            openingType=OpeningType.WINDOW,
            hostWallId=wall_id,
            levelId="LVL-000",
            widthM=0.5,
            heightM=0.6,
            sillHeightM=0.3
        )
        m.openings = [small_op, large_op]

        qto = ModelLinkedQTOEngine(m)
        records = qto.run_full_takeoff()
        wall_rec = next(r for r in records if "TO-WALL-EXT" in r.takeoffId)

        deducted_ids = {d.elementId for d in wall_rec.deductions}
        self.assertNotIn("OP-TINY-S1", deducted_ids, "Openings < 0.1 m² must not be deducted")
        self.assertIn("OP-LARGE-S1", deducted_ids, "Openings >= 0.1 m² must be deducted")

        # Gross vol = 2.0 * 1.0 * 0.23 = 0.46 m3
        # Deduction vol = 0.5 * 0.6 * 0.23 = 0.069 m3
        # Net vol = 0.46 - 0.069 = 0.391 m3
        self.assertAlmostEqual(wall_rec.grossQuantity, 0.46, places=2)
        self.assertAlmostEqual(wall_rec.netQuantity, 0.391, places=2)
        # Net quantity strictly under 1.0 m3 confirms no max(1.0, ...) floor exists
        self.assertLess(wall_rec.netQuantity, 1.0)

    def test_wastage_conservation_in_waterfall(self):
        """
        Cost Waterfall Wastage Conservation:
        directMaterialCost + materialWastageCost + directLabourCost + directEquipmentCost == grossHardCost.
        """
        m = make_test_canonical_model("DV-WASTAGE-S1", "Wastage Test", wall_length=10.0, wall_height=3.0)
        cost_engine = DeterministicCostEngine(m)
        estimate = cost_engine.calculate_cost_estimate()
        wf = estimate.costWaterfall

        direct_sum = round(wf.directMaterialCost + wf.materialWastageCost + wf.directLabourCost + wf.directEquipmentCost, 2)
        self.assertEqual(wf.grossHardCost, direct_sum, "Direct components plus wastage must strictly equal grossHardCost")
        self.assertGreater(wf.materialWastageCost, 0.0, "Material wastage must be strictly positive and accounted for")

    def test_adjacency_non_overlap_pair_rejected(self):
        """
        Touch Adjacency Formulation:
        Requires both collinear edge contact AND positive interval overlap on orthogonal axis.
        Corner-touching or disjoint rooms cannot satisfy TOUCH adjacency.
        Forbidden adjacency pair cannot share a positive-length edge.
        """
        brief = CustomerBrief(briefId="B-TOUCH", projectId="P-TOUCH", bedrooms=1, bathrooms=1, floors=1)
        r1 = RoomSpecification(specId="r_kit", roomType=RoomType.KITCHEN, displayName="Kitchen", floorIndex=0, minAreaSqm=6.0, preferredAreaSqm=6.0, maxAreaSqm=6.0, minWidthM=2.0, minLengthM=3.0)
        r2 = RoomSpecification(specId="r_bath", roomType=RoomType.BATHROOM, displayName="Bathroom", floorIndex=0, minAreaSqm=4.0, preferredAreaSqm=4.0, maxAreaSqm=4.0, minWidthM=2.0, minLengthM=2.0)
        prog = RoomProgram(programId="PROG-T", briefId="B-TOUCH", rooms=[r1, r2], targetCarpetAreaSqm=10.0, targetBuiltUpAreaSqm=12.0)

        # Forbidden adjacency: Kitchen and Bathroom cannot touch edges
        graph = RoomAdjacencyGraph(graphId="G-FORB", briefId="B-TOUCH", edges=[
            AdjacencyEdge(fromRoom=RoomType.KITCHEN.value, toRoom=RoomType.BATHROOM.value, relationship=AdjacencyRelationshipType.FORBIDDEN_ADJACENCY, weight=100.0)
        ])
        solver = CPSATLayoutSolver(program=prog, adjacency_graph=graph, brief=brief, envelope_width_m=4.0, envelope_length_m=4.0, max_floors=1)
        cands = solver.solve_candidates(1)
        self.assertTrue(len(cands) >= 1, "Solver must find layout")

        c = cands[0]
        rooms = {r.roomType: r for r in c.rooms}
        k, b = rooms["KITCHEN"], rooms["BATHROOM"]
        pk = Polygon([(k.x_m, k.y_m), (k.x_m + k.width_m, k.y_m), (k.x_m + k.width_m, k.y_m + k.depth_m), (k.x_m, k.y_m + k.depth_m)])
        pb = Polygon([(b.x_m, b.y_m), (b.x_m + b.width_m, b.y_m), (b.x_m + b.width_m, b.y_m + b.depth_m), (b.x_m, b.y_m + b.depth_m)])
        inter = pk.intersection(pb)
        # Length of collinear edge contact must be strictly zero (at most corner touch point)
        self.assertEqual(getattr(inter, "length", 0.0), 0.0, "Forbidden pair must have zero edge contact overlap")

    def test_stair_xy_equality_across_floors(self):
        """
        Multi-Floor Stair Vertical Alignment:
        Staircase coordinates (x, y, width, depth) on L0 must match L1 exactly in CP-SAT solver.
        """
        brief = CustomerBrief(briefId="B-MULTI", projectId="P-MULTI", bedrooms=3, bathrooms=2, floors=2)
        r1 = RoomSpecification(specId="stair_l0", roomType=RoomType.STAIR, displayName="Stair L0", floorIndex=0, minAreaSqm=6.0, preferredAreaSqm=7.0, maxAreaSqm=8.0, minWidthM=2.0, minLengthM=3.0)
        r2 = RoomSpecification(specId="stair_l1", roomType=RoomType.STAIR, displayName="Stair L1", floorIndex=1, minAreaSqm=6.0, preferredAreaSqm=7.0, maxAreaSqm=8.0, minWidthM=2.0, minLengthM=3.0)
        r3 = RoomSpecification(specId="liv_l0", roomType=RoomType.LIVING, displayName="Living", floorIndex=0, minAreaSqm=15.0, preferredAreaSqm=16.0, maxAreaSqm=20.0, minWidthM=3.0, minLengthM=4.0)
        r4 = RoomSpecification(specId="bed_l1", roomType=RoomType.BEDROOM, displayName="Bed", floorIndex=1, minAreaSqm=12.0, preferredAreaSqm=14.0, maxAreaSqm=16.0, minWidthM=3.0, minLengthM=3.5)

        program = RoomProgram(programId="PROG-MULTI", briefId="B-MULTI", rooms=[r1, r2, r3, r4], targetCarpetAreaSqm=50.0, targetBuiltUpAreaSqm=60.0)
        graph = RoomAdjacencyGraph(graphId="G-MULTI", briefId="B-MULTI", edges=[])

        solver = CPSATLayoutSolver(program=program, adjacency_graph=graph, brief=brief, envelope_width_m=12.0, envelope_length_m=12.0, max_floors=2)
        candidates = solver.solve_candidates(target_candidates=1)
        self.assertTrue(len(candidates) >= 1)

        c = candidates[0]
        rooms = {r.name: r for r in c.rooms}
        s0 = rooms["Stair L0"]
        s1 = rooms["Stair L1"]
        self.assertEqual(s0.x_m, s1.x_m, "Stair x must match exactly across storeys")
        self.assertEqual(s0.y_m, s1.y_m, "Stair y must match exactly across storeys")
        self.assertEqual(s0.width_m, s1.width_m, "Stair width must match exactly across storeys")
        self.assertEqual(s0.depth_m, s1.depth_m, "Stair depth must match exactly across storeys")

    def test_cors_untrusted_origin_rejected(self):
        """
        CORS Origin Enforcement:
        Untrusted origin (e.g. evil-attacker.com) is rejected (no Access-Control-Allow-Origin header).
        Trusted origin (e.g. http://localhost:5173) is accepted.
        """
        # Untrusted origin
        resp_evil = self.client.options(
            "/api/v1/health",
            headers={
                "Origin": "https://evil-attacker.com",
                "Access-Control-Request-Method": "GET"
            }
        )
        self.assertNotIn("access-control-allow-origin", resp_evil.headers)

        # Trusted origin
        resp_good = self.client.options(
            "/api/v1/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET"
            }
        )
        self.assertEqual(resp_good.headers.get("access-control-allow-origin"), "http://localhost:5173")

    def test_cbm_design_hash_equality_across_runs(self):
        """
        CBM Design Hash Determinism:
        Generating options from identical inputs produces identical SHA-256 designHash and fingerprint.
        """
        brief = CustomerBrief(briefId="B-HASH-01", projectId="P-HASH", bedrooms=2, bathrooms=2, floors=1)
        opts1 = generate_m2_house_options(site_width_m=9.19, site_length_m=9.29, brief=brief)
        opts2 = generate_m2_house_options(site_width_m=9.19, site_length_m=9.29, brief=brief)

        self.assertEqual(len(opts1), len(opts2))
        for i in range(len(opts1)):
            self.assertEqual(opts1[i]["designHash"], opts2[i]["designHash"], f"Option {i} designHash must be identical across runs")
            self.assertEqual(opts1[i]["fingerprint"], opts2[i]["fingerprint"], f"Option {i} fingerprint must be identical across runs")


if __name__ == "__main__":
    unittest.main()
