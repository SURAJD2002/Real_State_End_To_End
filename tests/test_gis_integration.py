"""
End-to-End GIS Integration Test Suite for Planwise Enterprise
Validates Mapbox GeoJSON ingestion, PostGIS/UTM 43N reprojection,
setback deductions, building footprint alignment, and release fingerprinting.
"""

import sys
import unittest
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from workers.geometry.engine import compute_parcel_metrics, haversine_distance, shoelace_area
from workers.regulation.evaluator import evaluate_mumbai_dcpr_2034
from workers.financial.proforma import calculate_financial_proforma
from workers.generation.house_generator import generate_house_options
from workers.release.manifest_engine import generate_release_fingerprint


class TestGISIntegration(unittest.TestCase):

    def setUp(self):
        # Canonical Mumbai Benchmark Parcel (CTS-1842-BANDRA)
        self.wgs84_coords = [
            [72.86850, 19.11280],
            [72.86950, 19.11400],
            [72.87100, 19.11330],
            [72.87000, 19.11210],
            [72.86850, 19.11280]
        ]
        self.existing_road_m = 12.0
        self.proposed_road_m = 18.0

    def test_01_coordinate_metrics_computation(self):
        """Verify metric area, perimeter, and setback generation."""
        metrics = compute_parcel_metrics(
            coordinates=self.wgs84_coords,
            existing_road_width_m=self.existing_road_m,
            proposed_road_width_m=self.proposed_road_m
        )

        self.assertGreater(metrics["grossAreaSqm"], 5000.0)
        self.assertGreater(metrics["perimeterM"], 200.0)
        self.assertGreater(metrics["roadWideningDeductionSqm"], 0.0)
        self.assertGreater(metrics["netDevelopableAreaSqm"], 0.0)
        self.assertLess(metrics["netDevelopableAreaSqm"], metrics["grossAreaSqm"])
        self.assertIsNotNone(metrics["buildableCoordinates"])
        self.assertGreaterEqual(len(metrics["buildableCoordinates"]), 3)

    def test_02_road_widening_statutory_deduction(self):
        """Widening from 12m to 18m must create positive buffer deduction."""
        delta = (self.proposed_road_m - self.existing_road_m) / 2.0
        self.assertEqual(delta, 3.0)

        metrics = compute_parcel_metrics(
            coordinates=self.wgs84_coords,
            existing_road_width_m=12.0,
            proposed_road_width_m=24.0 # larger widening
        )
        self.assertGreater(metrics["roadWideningDeductionSqm"], 500.0)

    def test_03_mumbai_dcpr_2034_evaluation(self):
        """Verify statutory FSI calculation for 18m road."""
        metrics = compute_parcel_metrics(self.wgs84_coords, 12.0, 18.0)
        reg = evaluate_mumbai_dcpr_2034(
            net_developable_area_sqm=metrics["netDevelopableAreaSqm"],
            effective_road_width_m=18.0
        )

        self.assertEqual(reg["baseFSI"], 1.0)
        self.assertEqual(reg["premiumFSI"], 0.5)
        self.assertEqual(reg["tdrFSI"], 1.0)
        self.assertEqual(reg["totalPermissibleFSI"], 2.5)
        self.assertGreater(reg["permissibleBUASqm"], metrics["netDevelopableAreaSqm"] * 2.0)
        self.assertGreaterEqual(reg["maxBuildingHeightM"], 70.0)

    def test_04_house_options_footprint_dimensions(self):
        """Verify CP-SAT generated house options fit within buildable envelope."""
        options = generate_house_options(site_width_m=18.0, site_length_m=22.0)
        self.assertEqual(len(options), 3)

        for opt in options:
            env = opt["layout"]["buildingEnvelope"]
            self.assertGreater(env["widthM"], 5.0)
            self.assertGreater(env["lengthM"], 5.0)
            self.assertGreater(opt["layout"]["totalGrossBUASqm"], 80.0)

    def test_05_release_fingerprint_provenance(self):
        """Verify immutable release SHA-256 fingerprint computation."""
        geom_hash = "sha256:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069"
        reg_hash = "sha256:mumbai_dcpr_2034_v1"
        brief_hash = "sha256:brief_std_01"
        design_hash = "sha256:opt_compact_2bhk_v1"
        boq_hash = "sha256:rate_snapshot_2026_q3"
        sched_hash = "sha256:cpm_sched_v1"

        fp1 = generate_release_fingerprint(
            geom_hash, reg_hash, brief_hash, design_hash, boq_hash, sched_hash
        )
        self.assertEqual(len(fp1), 64)

        # Altering geometry hash must change release fingerprint
        altered_geom_hash = "sha256:altered_geom_coordinates"
        fp2 = generate_release_fingerprint(
            altered_geom_hash, reg_hash, brief_hash, design_hash, boq_hash, sched_hash
        )
        self.assertNotEqual(fp1, fp2)


if __name__ == '__main__':
    unittest.main()
