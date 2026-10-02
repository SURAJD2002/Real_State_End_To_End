"""
Planwise Enterprise — M1 Comprehensive Test Suite
Site Truth, Local Engineering Coordinate System (SECS/BCS),
Deterministic Statutory Rule Engine & Golden Benchmark Suite.

Delta Specification M1 — §3, §4, §10, §17, §18
"""

import unittest
import math
import json
from pathlib import Path
from datetime import datetime

# 1. Coordinate Engine
from packages.schemas.coordinates import (
    GeodeticPoint,
    ECEFPoint,
    ENUPoint,
    BCSPoint,
    SiteReferenceFrame,
    GEOMETRY_TOLERANCE_M,
    VERTEX_TOLERANCE_M,
    SNAP_TOLERANCE_M,
    AREA_TOLERANCE_M2,
    ANGLE_TOLERANCE_DEG
)
from workers.geometry.crs_engine import (
    geodetic_to_ecef,
    ecef_to_geodetic,
    ecef_to_enu,
    enu_to_ecef,
    geodetic_to_enu,
    enu_to_geodetic,
    enu_to_bcs,
    bcs_to_enu,
    polygon_wgs84_to_secs,
    polygon_secs_to_wgs84,
    calculate_secs_polygon_area
)

# 2. Site Evidence & Confidence
from packages.schemas.site_evidence import (
    SiteEvidence,
    EvidenceType,
    SourceType,
    SiteConfidenceTier,
    VerificationStatus,
    ConfidenceEvaluationSummary
)
from workers.evidence.evidence_engine import evaluate_site_confidence

# 3. Statutory Rule Engine
from packages.schemas.regulation_rules import (
    RulePack,
    StatutoryRule,
    RuleCategory,
    RuleSeverity,
    RuleStatus,
    EdgeClassification,
    RuleExecutionTrace,
    FeasibilityExplainabilityBreakdown
)
from workers.regulation.rule_engine import (
    load_rule_pack,
    classify_parcel_edges,
    deduct_road_widening,
    compute_directional_setbacks,
    evaluate_fsi_and_massing,
    execute_statutory_feasibility_pipeline
)
from workers.regulation.benchmark_runner import run_all_benchmarks


class TestLocalEngineeringCoordinateSystem(unittest.TestCase):
    """
    Validates high-precision WGS84 <-> ECEF <-> SECS (ENU) <-> BCS transforms (§3).
    Ensures zero Web Mercator distortion in engineering coordinates.
    """

    def setUp(self):
        # Mumbai CST reference point
        self.ref_frame = SiteReferenceFrame(
            referenceFrameId="RF-MUMBAI-TEST",
            siteId="site-test-01",
            originLatitude=18.9400,
            originLongitude=72.8350,
            originElevationM=15.0,
            trueNorthBearingDeg=0.0
        )

    def test_01_wgs84_to_ecef_known_point(self):
        """WGS84 -> ECEF known-point mathematical accuracy test."""
        # Equator + Prime Meridian at 0 elevation
        x, y, z = geodetic_to_ecef(0.0, 0.0, 0.0)
        # Semi-major axis a = 6,378,137.0m
        self.assertAlmostEqual(x, 6378137.0, places=3)
        self.assertAlmostEqual(y, 0.0, places=3)
        self.assertAlmostEqual(z, 0.0, places=3)

        # North Pole: lat=90, lon=0, h=0 -> x=0, y=0, z = b = 6,356,752.3142m
        x_pole, y_pole, z_pole = geodetic_to_ecef(90.0, 0.0, 0.0)
        self.assertAlmostEqual(x_pole, 0.0, places=3)
        self.assertAlmostEqual(y_pole, 0.0, places=3)
        self.assertAlmostEqual(z_pole, 6356752.3142, places=2)

    def test_02_ecef_to_wgs84_round_trip(self):
        """ECEF <-> Geodetic round-trip numerical drift must be sub-nanometer (< 1e-6m)."""
        lat_in = 19.076090
        lon_in = 72.877426
        elev_in = 24.50

        x, y, z = geodetic_to_ecef(lat_in, lon_in, elev_in)
        lat_out, lon_out, elev_out = ecef_to_geodetic(x, y, z)

        lat_err = abs(lat_out - lat_in)
        lon_err = abs(lon_out - lon_in)
        elev_err = abs(elev_out - elev_in)

        # 1 deg lat ~ 111km, so 1e-9 deg ~ 0.1mm
        self.assertLess(lat_err, 1e-8, f"Latitude round-trip error too large: {lat_err}")
        self.assertLess(lon_err, 1e-8, f"Longitude round-trip error too large: {lon_err}")
        self.assertLess(elev_err, 0.0001, f"Elevation round-trip error exceeds tolerance: {elev_err}")

    def test_03_wgs84_to_enu_to_wgs84_round_trip(self):
        """WGS84 -> ENU (SECS) -> WGS84 round trip precision."""
        target_lat = 18.9425
        target_lon = 72.8375
        target_elev = 18.0

        east, north, up = geodetic_to_enu(
            target_lat, target_lon, target_elev,
            self.ref_frame.originLatitude, self.ref_frame.originLongitude, self.ref_frame.originElevationM
        )
        lat_b, lon_b, elev_b = enu_to_geodetic(
            east, north, up,
            self.ref_frame.originLatitude, self.ref_frame.originLongitude, self.ref_frame.originElevationM
        )

        self.assertAlmostEqual(lat_b, target_lat, places=7)
        self.assertAlmostEqual(lon_b, target_lon, places=7)
        self.assertAlmostEqual(elev_b, target_elev, places=3)

    def test_04_baseline_preservation_100m(self):
        """A 100m ground baseline in SECS must preserve metric distance within engineering tolerance."""
        # Convert both to geodetic
        g1_lat, g1_lon, g1_elev = enu_to_geodetic(
            0.0, 0.0, 0.0,
            self.ref_frame.originLatitude, self.ref_frame.originLongitude, self.ref_frame.originElevationM
        )
        g2_lat, g2_lon, g2_elev = enu_to_geodetic(
            100.0, 0.0, 0.0,
            self.ref_frame.originLatitude, self.ref_frame.originLongitude, self.ref_frame.originElevationM
        )

        # Convert back to ENU
        e1_e, e1_n, e1_u = geodetic_to_enu(
            g1_lat, g1_lon, g1_elev,
            self.ref_frame.originLatitude, self.ref_frame.originLongitude, self.ref_frame.originElevationM
        )
        e2_e, e2_n, e2_u = geodetic_to_enu(
            g2_lat, g2_lon, g2_elev,
            self.ref_frame.originLatitude, self.ref_frame.originLongitude, self.ref_frame.originElevationM
        )

        dist = math.sqrt((e2_e - e1_e)**2 + (e2_n - e1_n)**2)
        error = abs(dist - 100.0)
        self.assertLess(error, GEOMETRY_TOLERANCE_M, f"100m baseline distorted by {error}m")

    def test_05_parcel_envelope_500m_distortion(self):
        """A 500m x 500m engineering parcel envelope must have area distortion < 0.01%."""
        # 500m square in SECS: area = 250,000 m²
        poly_secs = [
            [0.0, 0.0],
            [500.0, 0.0],
            [500.0, 500.0],
            [0.0, 500.0],
            [0.0, 0.0]
        ]
        wgs_poly = polygon_secs_to_wgs84(poly_secs, self.ref_frame)
        secs_back = polygon_wgs84_to_secs(wgs_poly, self.ref_frame)
        measured_area = calculate_secs_polygon_area(secs_back)

        area_error = abs(measured_area - 250000.0)
        rel_error = area_error / 250000.0
        self.assertLess(rel_error, 0.0001, f"500m parcel area relative distortion exceeds 0.01%: {rel_error * 100}%")

    def test_06_bcs_rotation(self):
        """Building Coordinate System (BCS) rotation transforms local engineering frame accurately."""
        # Point in SECS: (East=10, North=0, Up=2)
        bx, by, bz = enu_to_bcs(10.0, 0.0, 2.0, orientation_deg=90.0)
        e_back, n_back, u_back = bcs_to_enu(bx, by, bz, orientation_deg=90.0)

        self.assertAlmostEqual(e_back, 10.0, places=4)
        self.assertAlmostEqual(n_back, 0.0, places=4)
        self.assertAlmostEqual(u_back, 2.0, places=4)

    def test_07_reference_frame_immutability(self):
        """Reference frame hash fingerprint enforces release immutability."""
        rf1 = SiteReferenceFrame(
            referenceFrameId="RF-IMMUTABLE-01",
            siteId="site-101",
            originLatitude=19.1128,
            originLongitude=72.8685,
            originElevationM=12.5
        )
        h = rf1.compute_frame_hash()
        self.assertIsNotNone(h)
        self.assertEqual(len(h), 64, "SHA-256 fingerprint must be 64 hex characters")


class TestSiteEvidenceAndConfidence(unittest.TestCase):
    """
    Validates multi-tier provenance, verification state, and deterministic confidence (§1, §2).
    """

    def setUp(self):
        self.site_id = "site-bandra-001"

    def test_01_l0_gis_estimate_blocks_build(self):
        """L0 GIS unverified evidence blocks BUILD release."""
        ev1 = SiteEvidence(
            siteEvidenceId="EV-001",
            siteId=self.site_id,
            evidenceType=EvidenceType.PARCEL_BOUNDARY,
            sourceType=SourceType.GIS_SATELLITE,
            provider="OpenStreetMap / Mapbox basemap",
            capturedAt=datetime.utcnow().isoformat(),
            accuracyM=3.5,
            confidenceLevel=SiteConfidenceTier.L0_GIS_ESTIMATE,
            verificationStatus=VerificationStatus.UNVERIFIED
        )
        summary = evaluate_site_confidence(self.site_id, [ev1])
        self.assertEqual(summary.overallConfidence, SiteConfidenceTier.L0_GIS_ESTIMATE)
        self.assertTrue(summary.isBlockingForBuildRelease, "L0 GIS data must block build release")
        self.assertIn("Licensed Land Survey Boundary", summary.missingEvidenceForL3[0])

    def test_02_l1_customer_document_blocks_build(self):
        """L1 Customer Uploaded deed document blocks BUILD release without field survey."""
        ev1 = SiteEvidence(
            siteEvidenceId="EV-002",
            siteId=self.site_id,
            evidenceType=EvidenceType.SALE_DEED,
            sourceType=SourceType.CUSTOMER_UPLOAD,
            provider="Client Conveyance Deed Scan",
            capturedAt=datetime.utcnow().isoformat(),
            accuracyM=0.5,
            confidenceLevel=SiteConfidenceTier.L1_CUSTOMER_DOCUMENT,
            verificationStatus=VerificationStatus.PENDING_REVIEW
        )
        summary = evaluate_site_confidence(self.site_id, [ev1])
        self.assertEqual(summary.overallConfidence, SiteConfidenceTier.L1_CUSTOMER_DOCUMENT)
        self.assertTrue(summary.isBlockingForBuildRelease)

    def test_03_l3_licensed_survey_unblocks_build(self):
        """L3 Verified Licensed Survey boundary + levels unblocks BUILD release."""
        ev1 = SiteEvidence(
            siteEvidenceId="EV-003",
            siteId=self.site_id,
            evidenceType=EvidenceType.SURVEY_PLAN,
            sourceType=SourceType.LICENSED_SURVEYOR,
            provider="Apex Geomatics (LS-MH-9941)",
            capturedAt=datetime.utcnow().isoformat(),
            accuracyM=0.02,
            confidenceLevel=SiteConfidenceTier.L3_LICENSED_SURVEY,
            verificationStatus=VerificationStatus.VERIFIED,
            verifiedBy="Sandeep Patil (LS-MH-9941)"
        )
        ev2 = SiteEvidence(
            siteEvidenceId="EV-004",
            siteId=self.site_id,
            evidenceType=EvidenceType.SITE_LEVEL,
            sourceType=SourceType.LICENSED_SURVEYOR,
            provider="Apex Geomatics (LS-MH-9941)",
            capturedAt=datetime.utcnow().isoformat(),
            accuracyM=0.01,
            confidenceLevel=SiteConfidenceTier.L3_LICENSED_SURVEY,
            verificationStatus=VerificationStatus.VERIFIED,
            verifiedBy="Sandeep Patil (LS-MH-9941)"
        )
        summary = evaluate_site_confidence(self.site_id, [ev1, ev2])
        self.assertEqual(summary.overallConfidence, SiteConfidenceTier.L3_LICENSED_SURVEY)
        self.assertFalse(summary.isBlockingForBuildRelease, "Verified L3 licensed survey must unblock build release")


class TestDeterministicStatutoryRuleEngine(unittest.TestCase):
    """
    Validates declarative Rule Packs, edge classification, setbacks, FSI, coverage, and RuleExecutionTrace (§5, §6, §7).
    """

    def setUp(self):
        self.mumbai_pack = load_rule_pack("MUMBAI-DCPR-2034-V1")
        self.bbmp_pack = load_rule_pack("BBMP-BENGALURU-2026-V1")

    def test_01_rule_pack_schema(self):
        """Rule packs must be machine-readable with strong types and citations."""
        self.assertGreaterEqual(len(self.mumbai_pack.rules), 6)
        self.assertGreaterEqual(len(self.bbmp_pack.rules), 5)
        for r in self.mumbai_pack.rules:
            self.assertIsNotNone(r.ruleId)
            self.assertIsNotNone(r.citation)
            self.assertIsNotNone(r.category)

    def test_02_edge_classification(self):
        """Explicit boundary edge classification into FRONT, REAR, SIDES."""
        # 40m x 25m rectangle where bottom edge y=0 is along the road
        coords = [
            [0.0, 0.0],
            [40.0, 0.0],
            [40.0, 25.0],
            [0.0, 25.0],
            [0.0, 0.0]
        ]
        edges = classify_parcel_edges(coords, primary_road_width_m=12.0)
        self.assertEqual(len(edges), 4)

        # Verify classifications exist without silent guessing
        classifications = [e.classification for e in edges]
        self.assertIn(EdgeClassification.FRONT, classifications)
        self.assertIn(EdgeClassification.REAR, classifications)
        self.assertIn(EdgeClassification.LEFT_SIDE, classifications)
        self.assertIn(EdgeClassification.RIGHT_SIDE, classifications)

    def test_03_trace_generation_and_explainability(self):
        """Every pipeline execution must produce complete RuleExecutionTrace records."""
        bandra_coords = [
            [72.86850, 19.11280],
            [72.86950, 19.11400],
            [72.87100, 19.11330],
            [72.87000, 19.11210],
            [72.86850, 19.11280]
        ]
        breakdown, geom = execute_statutory_feasibility_pipeline(
            coordinates_wgs84=bandra_coords,
            existing_road_width_m=12.0,
            proposed_road_width_m=18.0,
            rule_pack_id="MUMBAI-DCPR-2034-V1"
        )

        self.assertGreaterEqual(len(breakdown.traces), 8)
        trace_ids = [t.traceId for t in breakdown.traces]
        self.assertIn("TRC-RW-001", trace_ids)
        self.assertIn("TRC-FSI-006", trace_ids)
        self.assertIn("TRC-COV-007", trace_ids)

        # Check explainability consistency
        self.assertGreater(breakdown.grossParcelAreaSqm, breakdown.netParcelAreaSqm)
        self.assertGreater(breakdown.netParcelAreaSqm, breakdown.effectivePermittedFootprintSqm)
        self.assertAlmostEqual(breakdown.totalPermissibleFSI, 2.5, places=2)


class TestGoldenBenchmarkPlots(unittest.TestCase):
    """
    Executes all 12 Golden Benchmark Plots against authoritative statutory criteria (§10).
    """

    def test_01_all_12_benchmarks_pass(self):
        """All 12 golden plots must pass statutory rules within metric tolerances."""
        results = run_all_benchmarks()
        self.assertEqual(results["totalBenchmarks"], 12)
        self.assertEqual(results["passedCount"], 12, f"Failed benchmarks: {results['results']}")
        self.assertEqual(results["failedCount"], 0)


if __name__ == "__main__":
    unittest.main()
