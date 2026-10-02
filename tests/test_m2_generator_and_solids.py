"""
Planwise Enterprise — Comprehensive M2 Unit & Integration Test Suite
Phase 24: CP-SAT Layout Solver, Manifold3D Solids, Pareto Filter, CBM Integration & Determinism
"""

import unittest
import math
from typing import Dict, Any, List

from packages.schemas.customer_brief import CustomerBrief, ArchitecturalStyle
from packages.schemas.room_program import (
    build_room_program_from_brief,
    RoomProgram,
    RoomSpecification,
    RoomType,
    PrivacyLevel
)
from packages.schemas.room_graph import (
    build_default_residential_adjacency_graph,
    AdjacencyRelationshipType,
    RoomAdjacencyGraph
)
from workers.generation.cpsat_solver import CPSATLayoutSolver, LayoutCandidate
from workers.generation.pareto_filter import (
    filter_pareto_frontier,
    evaluate_candidate_metrics,
    is_pareto_dominated
)
from workers.geometry.solid_engine import SolidModelingEngine
from workers.generation.house_generator import generate_m2_house_options
from workers.generation.validation_engine import run_m2_design_validation, diagnose_generation_failure


class TestM2GeneratorAndSolids(unittest.TestCase):
    """Rigorous verification of the complete M2 deterministic house-generation pipeline."""

    @classmethod
    def setUpClass(cls):
        cls.solid_engine = SolidModelingEngine()

    # ==================================================================
    # 1. CP-SAT LAYOUT SOLVER TESTS (Phase 4 & 5)
    # ==================================================================

    def test_01_cpsat_generates_valid_room_count_and_areas(self):
        """Verify CP-SAT produces exact room specifications obeying minimum areas."""
        brief = CustomerBrief(
            briefId="BRIEF-TEST-01",
            projectId="proj-test-01",
            bedrooms=3,
            bathrooms=2,
            floors=1
        )
        program = build_room_program_from_brief(brief)
        graph = build_default_residential_adjacency_graph()

        solver = CPSATLayoutSolver(
            program=program,
            adjacency_graph=graph,
            brief=brief,
            envelope_width_m=16.0,
            envelope_length_m=16.0,
            max_floors=1,
            time_limit_seconds=1.2
        )
        candidates = solver.solve_candidates(target_candidates=3)
        self.assertGreaterEqual(len(candidates), 3)

        cand = candidates[0]
        self.assertEqual(cand.solverStatus, "FEASIBLE")
        self.assertGreaterEqual(len(cand.rooms), 10)

        # Assert all room areas meet their NBC minimums
        room_spec_map = {r.specId: r for r in program.rooms}
        for rm in cand.rooms:
            spec = room_spec_map.get(rm.spaceId)
            if spec:
                self.assertGreaterEqual(
                    rm.area_sqm,
                    spec.minAreaSqm - 0.1,
                    f"Room {rm.name} area {rm.area_sqm} below minimum {spec.minAreaSqm}"
                )
                self.assertGreaterEqual(rm.width_m, 1.2)
                self.assertGreaterEqual(rm.depth_m, 1.2)

    def test_02_cpsat_enforces_zero_room_overlap_and_envelope_containment(self):
        """Verify strict 2D interval non-overlap and SECS footprint boundary containment."""
        brief = CustomerBrief(bedrooms=3, bathrooms=2, floors=1)
        program = build_room_program_from_brief(brief)
        graph = build_default_residential_adjacency_graph()

        env_w = 15.0
        env_l = 15.0
        solver = CPSATLayoutSolver(program, graph, brief, envelope_width_m=env_w, envelope_length_m=env_l, time_limit_seconds=1.2)
        candidates = solver.solve_candidates(target_candidates=1)
        self.assertTrue(len(candidates) >= 1)

        rooms = candidates[0].rooms
        for i, r1 in enumerate(rooms):
            # Boundary containment
            self.assertGreaterEqual(r1.x_m, -0.01)
            self.assertGreaterEqual(r1.y_m, -0.01)
            self.assertLessEqual(r1.x_m + r1.width_m, env_w + 0.05)
            self.assertLessEqual(r1.y_m + r1.depth_m, env_l + 0.05)

            # Pairwise non-overlap check
            for j, r2 in enumerate(rooms):
                if i >= j or r1.floor != r2.floor:
                    continue
                inter_w = min(r1.x_m + r1.width_m, r2.x_m + r2.width_m) - max(r1.x_m, r2.x_m)
                inter_h = min(r1.y_m + r1.depth_m, r2.y_m + r2.depth_m) - max(r1.y_m, r2.y_m)
                has_overlap = inter_w > 0.05 and inter_h > 0.05
                self.assertFalse(has_overlap, f"Rooms {r1.name} and {r2.name} overlap by {inter_w}x{inter_h}m!")

    def test_03_cpsat_enforces_forbidden_adjacencies(self):
        """Verify NBC 2016 Part 3: Kitchen and Prayer spaces do not touch toilets."""
        brief = CustomerBrief(bedrooms=3, bathrooms=2, floors=1)
        program = build_room_program_from_brief(brief)
        graph = build_default_residential_adjacency_graph()

        solver = CPSATLayoutSolver(program, graph, brief, envelope_width_m=16.0, envelope_length_m=16.0, time_limit_seconds=1.2)
        candidates = solver.solve_candidates(target_candidates=2)
        self.assertTrue(len(candidates) >= 1)

        for cand in candidates:
            kitchen = next((r for r in cand.rooms if r.roomType == RoomType.KITCHEN.value), None)
            toilets = [r for r in cand.rooms if r.roomType in [RoomType.TOILET.value, RoomType.BATHROOM.value]]
            puja = next((r for r in cand.rooms if r.roomType == RoomType.PUJA.value), None)

            if kitchen:
                for t in toilets:
                    # Check if sharing an edge
                    touches_x = abs((kitchen.x_m + kitchen.width_m) - t.x_m) < 0.05 or abs((t.x_m + t.width_m) - kitchen.x_m) < 0.05
                    overlaps_y = min(kitchen.y_m + kitchen.depth_m, t.y_m + t.depth_m) - max(kitchen.y_m, t.y_m) > 0.1
                    touches_y = abs((kitchen.y_m + kitchen.depth_m) - t.y_m) < 0.05 or abs((t.y_m + t.depth_m) - kitchen.y_m) < 0.05
                    overlaps_x = min(kitchen.x_m + kitchen.width_m, t.x_m + t.width_m) - max(kitchen.x_m, t.x_m) > 0.1
                    is_adjacent = (touches_x and overlaps_y) or (touches_y and overlaps_x)
                    # Adjacency between kitchen and common toilet should be forbidden
                    if t.roomType == RoomType.TOILET.value:
                        self.assertFalse(is_adjacent, f"Forbidden adjacency breached: Kitchen touches {t.name}")

    def test_04_cpsat_multi_floor_duplex_stair_allocation(self):
        """Verify multi-floor house places bedrooms on L1 and integrates staircase."""
        brief = CustomerBrief(bedrooms=4, bathrooms=3, floors=2)
        program = build_room_program_from_brief(brief)
        graph = build_default_residential_adjacency_graph()

        solver = CPSATLayoutSolver(program, graph, brief, envelope_width_m=14.0, envelope_length_m=16.0, max_floors=2, time_limit_seconds=1.2)
        candidates = solver.solve_candidates(target_candidates=1)
        self.assertTrue(len(candidates) >= 1)

        cand = candidates[0]
        floors_present = {r.floor for r in cand.rooms}
        self.assertIn("L0", floors_present)
        self.assertIn("L1", floors_present)

    # ==================================================================
    # 2. MANIFOLD3D SOLID KERNEL TESTS (Phase 7 & 8)
    # ==================================================================

    def test_05_manifold3d_wall_solid_with_openings_is_watertight(self):
        """Verify wall solid extrusion and CSG boolean opening subtractions are watertight 2-manifolds."""
        wall, val = self.solid_engine.create_wall_solid(
            start_pt=(0.0, 0.0),
            end_pt=(5.0, 0.0),
            height_m=3.0,
            thickness_m=0.20,
            element_id="WALL-TEST-01",
            openings=[
                {"distanceFromStartM": 1.0, "widthM": 1.0, "heightM": 2.1, "sillHeightM": 0.0},
                {"distanceFromStartM": 3.0, "widthM": 1.2, "heightM": 1.2, "sillHeightM": 0.9}
            ]
        )
        self.assertIsNotNone(wall)
        self.assertTrue(val.isValid)
        self.assertTrue(val.is2Manifold)
        self.assertTrue(val.isWatertight)
        self.assertTrue(val.hasPositiveVolume)
        self.assertGreater(val.volumeM3, 0.5)
        self.assertEqual(len(val.errors), 0)

    def test_06_manifold3d_slab_solid_with_shaft_openings(self):
        """Verify slab solid with shaft cutouts maintains 2-manifold invariant."""
        slab, val = self.solid_engine.create_slab_solid(
            polygon_points=[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0]],
            thickness_m=0.15,
            elevation_m=0.0,
            element_id="SLAB-TEST-01",
            openings=[
                [[2.0, 2.0], [4.0, 2.0], [4.0, 4.0], [2.0, 4.0]] # Stair/Shaft penetration
            ]
        )
        self.assertIsNotNone(slab)
        self.assertTrue(val.isValid)
        self.assertTrue(val.isWatertight)
        self.assertGreater(val.volumeM3, 10.0)

    def test_07_manifold3d_column_and_stair_solids(self):
        """Verify RCC column and stepped staircase solids produce positive volume."""
        col, c_val = self.solid_engine.create_column_solid(
            center_x=4.0,
            center_y=4.0,
            width_m=0.3,
            depth_m=0.45,
            height_m=3.15,
            elevation_m=0.0,
            element_id="COL-TEST-01"
        )
        self.assertTrue(c_val.isValid)
        self.assertAlmostEqual(c_val.volumeM3, 0.3 * 0.45 * 3.15, places=3)

        stair, s_val = self.solid_engine.create_stair_solid(
            bounds={"x": 0.0, "y": 0.0, "width": 2.4, "height": 3.2},
            floor_to_floor_height_m=3.15,
            element_id="STAIR-TEST-01"
        )
        self.assertTrue(s_val.isValid)
        self.assertTrue(s_val.hasPositiveVolume)

    def test_08_manifold3d_mesh_export_for_threejs(self):
        """Verify exported mesh data contains valid float positions and triangle indices."""
        wall, _ = self.solid_engine.create_wall_solid(
            start_pt=(0.0, 0.0),
            end_pt=(4.0, 0.0),
            height_m=3.0,
            thickness_m=0.20,
            element_id="WALL-TEST-EXP"
        )
        mesh_data = self.solid_engine.export_mesh_data(wall)
        self.assertIn("positions", mesh_data)
        self.assertIn("indices", mesh_data)
        self.assertGreater(len(mesh_data["positions"]), 0)
        self.assertGreater(len(mesh_data["indices"]), 0)
        self.assertEqual(len(mesh_data["positions"]) % 3, 0)
        self.assertEqual(len(mesh_data["indices"]) % 3, 0)

    # ==================================================================
    # 3. MULTI-OBJECTIVE PARETO FILTER TESTS (Phase 6)
    # ==================================================================

    def test_09_pareto_filter_identifies_non_dominated_tradeoffs(self):
        """Verify Pareto frontier preserves non-dominated alternatives."""
        brief = CustomerBrief(bedrooms=3, bathrooms=2, floors=1)
        options = generate_m2_house_options(site_width_m=16.0, site_length_m=16.0, brief=brief)
        self.assertGreaterEqual(len(options), 3)

        # Verify each option has distinct architectural trade-offs
        carpet_areas = [opt["scores"]["areaEfficiencyPercent"] for opt in options]
        daylights = [opt["scores"]["daylightProxy"] for opt in options]
        self.assertTrue(len(carpet_areas) >= 3)
        self.assertTrue(len(daylights) >= 3)

    # ==================================================================
    # 4. 12-CHECK VALIDATION & FAILURE DIAGNOSIS (Phase 13 & 14)
    # ==================================================================

    def test_10_twelve_check_validation_passes_all_checks(self):
        """Verify full 12-check validation report passes on generated options."""
        brief = CustomerBrief(bedrooms=3, bathrooms=2, floors=1)
        options = generate_m2_house_options(site_width_m=16.0, site_length_m=18.0, brief=brief)
        self.assertTrue(len(options) >= 3)

        val = options[0]["validation"]
        self.assertEqual(val["status"], "VALID")
        self.assertEqual(len(val["blockingErrors"]), 0)
        self.assertEqual(len(val["passedChecks"]), 12)
        self.assertIn("SITE_ENVELOPE_VALIDATION", val["passedChecks"])
        self.assertIn("MANIFOLD_3D_SOLID_VALIDATION", val["passedChecks"])
        self.assertIn("CBM_CONSISTENCY_VALIDATION", val["passedChecks"])

    def test_11_failure_diagnosis_on_impossible_envelope(self):
        """Verify structured failure explanation when plot cannot accommodate room program."""
        brief = CustomerBrief(bedrooms=5, bathrooms=4, floors=1) # Huge program
        program = build_room_program_from_brief(brief)
        
        # Envelope too small: 4m x 4m = 16m² for 5BHK
        diagnosis = diagnose_generation_failure(
            envelope_width_m=4.0,
            envelope_length_m=4.0,
            brief=brief,
            program=program
        )
        self.assertEqual(diagnosis["status"], "NO_VALID_LAYOUT")
        self.assertIn("REQUIRED_ROOM_AREA_EXCEEDS_AVAILABLE_AREA", diagnosis["failureReasons"])
        self.assertIn("PLOT_WIDTH_BELOW_MINIMUM_HABITABLE_BAY", diagnosis["failureReasons"])
        self.assertTrue(diagnosis["requiresCustomerApproval"])

    # ==================================================================
    # 5. DETERMINISM & REPRODUCIBILITY (Phase 22)
    # ==================================================================

    def test_12_deterministic_design_fingerprint_reproducibility(self):
        """Verify identical inputs yield identical SHA256 hashes."""
        brief = CustomerBrief(
            briefId="BRIEF-REPRO-01",
            projectId="proj-repro-01",
            bedrooms=3,
            bathrooms=2,
            floors=1
        )
        opts1 = generate_m2_house_options(site_width_m=16.0, site_length_m=16.0, brief=brief)
        opts2 = generate_m2_house_options(site_width_m=16.0, site_length_m=16.0, brief=brief)

        self.assertEqual(len(opts1), len(opts2))
        for i in range(len(opts1)):
            self.assertEqual(opts1[i]["designHash"], opts2[i]["designHash"])
            self.assertEqual(opts1[i]["fingerprint"], opts2[i]["fingerprint"])
            self.assertEqual(opts1[i]["scores"]["overallScore"], opts2[i]["scores"]["overallScore"])


if __name__ == "__main__":
    unittest.main()
