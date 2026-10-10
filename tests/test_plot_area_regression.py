"""
Regression Test Suite: End-to-End Plot Area Propagation and Pilot Isolation
=============================================================================
Requirements:
1. Entering 1,500 sq ft must preserve 1,500 sq ft end-to-end.
2. The design generator must receive 1,500 sq ft, not 1,100.
3. CBM must preserve declaredPlotAreaSqFt = 1,500.
4. Feasibility calculations must reflect 1,500 sq ft.
5. Generated geometry must differ from 1,100 pilot geometry.
6. Verify 1100 -> 1100, 1500 -> 1500, 2400 -> 2400, 10000 -> 10000.
7. Verify absence of silent fallbacks to 1100.
"""

import unittest
import importlib.util
from pathlib import Path

# Backend generation imports
from workers.generation.house_generator import generate_m2_house_options
from workers.generation.model_compiler import compile_canonical_building_model

# Dynamically import apps/api-gateway/main.py
SPEC_PATH = Path(__file__).resolve().parent.parent / "apps" / "api-gateway" / "main.py"
spec = importlib.util.spec_from_file_location("api_gateway_main", str(SPEC_PATH))
api_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api_mod)


class TestPlotAreaRegression(unittest.TestCase):

    def test_01_cbm_declared_plot_area_preservation_and_geometry_divergence(self):
        """Verify CBM preserves declaredPlotAreaSqFt and generated geometry differs between 1100 and 1500 sq ft."""
        # Baseline 1100 pilot
        opts_1100 = generate_m2_house_options(
            site_width_m=8.38,
            site_length_m=12.19,
            declared_plot_area_sqft=1100.0
        )
        self.assertTrue(len(opts_1100) > 0)
        cbm_1100 = opts_1100[0]["buildingModel"]
        self.assertEqual(cbm_1100.get("declaredPlotAreaSqFt"), 1100.0)

        # 1500 sq ft customer project
        opts_1500 = generate_m2_house_options(
            declared_plot_area_sqft=1500.0
        )
        self.assertTrue(len(opts_1500) > 0)
        cbm_1500 = opts_1500[0]["buildingModel"]
        self.assertEqual(cbm_1500.get("declaredPlotAreaSqFt"), 1500.0)

        # Assert geometry of 1500 does NOT match 1100 pilot geometry
        footprint_1100 = (cbm_1100["buildingEnvelope"]["widthM"], cbm_1100["buildingEnvelope"]["lengthM"])
        footprint_1500 = (cbm_1500["buildingEnvelope"]["widthM"], cbm_1500["buildingEnvelope"]["lengthM"])
        self.assertNotEqual(
            footprint_1100, footprint_1500,
            f"1500 sq ft geometry {footprint_1500} must not equal 1100 sq ft geometry {footprint_1100}"
        )
        self.assertNotEqual(cbm_1100["metadata"]["modelHash"], cbm_1500["metadata"]["modelHash"])

    def test_02_all_specified_plot_sizes_remain_exact(self):
        """Test: 1100 -> 1100, 1500 -> 1500, 2400 -> 2400, 10000 -> 10000."""
        sizes = [1100.0, 1500.0, 2400.0, 10000.0]
        hashes = set()
        footprints = set()

        for sz in sizes:
            opts = generate_m2_house_options(declared_plot_area_sqft=sz)
            self.assertTrue(len(opts) > 0, f"Options must be generated for {sz} sq ft")
            cbm = opts[0]["buildingModel"]
            self.assertEqual(
                cbm.get("declaredPlotAreaSqFt"), sz,
                f"Expected CBM declaredPlotAreaSqFt={sz}, got {cbm.get('declaredPlotAreaSqFt')}"
            )
            hashes.add(cbm["metadata"]["modelHash"])
            bounds = cbm["buildingEnvelope"]
            footprints.add((bounds["widthM"], bounds["lengthM"]))

        # All 4 sizes must produce unique model hashes and unique footprints
        self.assertEqual(len(hashes), 4, "All 4 plot sizes must produce distinct model hashes")
        self.assertEqual(len(footprints), 4, "All 4 plot sizes must produce distinct building envelopes")

    def test_03_api_gateway_end_to_end_data_flow(self):
        """Simulate Land Input -> Project State -> Feasibility -> Design Generation via API Gateway."""
        proj_id = "proj-e2e-customer-1500"

        # 1. Land Input: auto-save geometries with declaredPlotAreaSqFt = 1500
        geom_payload = api_mod.GeometryAutoSavePayload(
            version=1,
            coordinates=[
                [72.82950, 19.05960],
                [72.82962, 19.05960],
                [72.82962, 19.05975],
                [72.82950, 19.05975],
                [72.82950, 19.05960]
            ],
            existingRoadWidthM=6.0,
            proposedRoadWidthM=12.0,
            tenureType="PRIVATE_FREEHOLD",
            cadastralSurveyNumber="CTS-1500-TEST",
            declaredPlotAreaSqFt=1500.0
        )
        geom_res = api_mod.auto_save_geometries(proj_id, geom_payload)
        self.assertEqual(geom_res.get("declaredPlotAreaSqFt"), 1500.0)

        # Verify project state preserved 1500 in backend
        self.assertIn(proj_id, api_mod.PROJECTS_DB)
        self.assertEqual(api_mod.PROJECTS_DB[proj_id].get("declaredPlotAreaSqFt"), 1500.0)

        # 2. Feasibility DAG run
        feas_res = api_mod.run_feasibility_dag(proj_id)
        self.assertEqual(feas_res.get("declaredPlotAreaSqFt"), 1500.0)

        # 3. Design Options Generation
        gen_payload = api_mod.GenerateDesignOptionsPayload(
            bedrooms=2,
            bathrooms=2,
            floors=2,
            parkingRequired=True,
            preferredStyle="MODERN",
            budgetInr=5000000,
            qualityTier="STANDARD",
            declaredPlotAreaSqFt=1500.0
        )
        gen_res = api_mod.generate_design_options_endpoint(proj_id, gen_payload)
        self.assertEqual(gen_res.get("status"), "COMPLETED")
        options = gen_res.get("options", [])
        self.assertTrue(len(options) > 0)
        cbm = options[0].get("buildingModel")
        self.assertEqual(cbm.get("declaredPlotAreaSqFt"), 1500.0)

    def test_04_no_silent_fallback_to_1100_for_unknown_project(self):
        """Unknown or unconfigured project must NOT silently default to 1100 sq ft."""
        unknown_proj_id = "proj-empty-custom-unknown"
        api_mod.PROJECTS_DB[unknown_proj_id] = {
            "id": unknown_proj_id,
            "name": "Custom Empty",
            "parcel": {
                "coordinates": [[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]
            }
        }
        options = api_mod.get_house_options(unknown_proj_id)
        if options:
            cbm = options[0].get("buildingModel")
            # Must NOT be 1100.0
            self.assertNotEqual(cbm.get("declaredPlotAreaSqFt"), 1100.0)


if __name__ == "__main__":
    unittest.main()
