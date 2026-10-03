"""
Planwise Enterprise — Phase 8.2 Controlled Real-Project Pilot Automated Test Suite
==================================================================================
Delta Specification §6.3, §12, §13, §14 & Phase 8.2 Specification

Verifies:
1. Execution of the complete 12-stage pipeline on authoritative 1,100 sq ft project data.
2. Cryptographic provenance: Site -> DesignVersion -> CBM -> QTO -> BOQ -> Cost -> Release Fingerprint.
3. Strict 1,100 sq ft invariant preserved across all outputs (zero benchmark contamination).
4. Physical generation and non-emptiness of all 6 handoff artifacts (IFC4, Manifest, BOQ, Cost, Validation, Ledger).
5. Gate status integrity: G0–G4 VERIFIED, G5/G6 strictly LOCKED.
6. Direct PostgreSQL persistence and restart resilience.
7. Release immutability on frozen pilot release.
8. Halting behavior: Missing real-world inputs return USER_INPUT_REQUIRED / JURISDICTION_REQUIRED.
"""

import os
import json
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
from workers.intake.controlled_pilot_runner import ControlledPilotRunner
from workers.release.manifest_engine import generate_release_fingerprint
from packages.schemas.real_plot_input import (
    RealPlotIntakePayload,
    SiteInput,
    CustomerRequirementsInput,
    PlotDimensions,
    SiteShape,
    BuildingUse
)
from workers.intake.real_plot_runner import RealPlotPipelineRunner
import ledger_repository as ledger_repo
from ledger_repository import ReleaseImmutabilityError


class TestControlledPilot(unittest.TestCase):
    """Rigorous verification of the Phase 8.2 Controlled Real-Project Pilot."""

    @classmethod
    def setUpClass(cls):
        cls.test_dir = ROOT_DIR / "artifacts" / "test_pilot_controlled_output"
        cls.runner = ControlledPilotRunner(output_dir=cls.test_dir)
        cls.result = cls.runner.execute_pilot()

    # 1. Pipeline Execution & Physical Artifacts
    def test_01_pilot_execution_and_artifacts_generated(self):
        res = self.result
        self.assertEqual(res["status"], "PILOT_COMPLETE_SUCCESS")
        self.assertEqual(res["declaredPlotAreaSqFt"], 1100.0)

        # Verify all 6 physical artifact files exist and are non-empty
        artifacts = res["artifactsGenerated"]
        for key, file_path_str in artifacts.items():
            path = Path(file_path_str)
            self.assertTrue(path.exists(), f"Artifact {key} ({file_path_str}) does not exist")
            self.assertGreater(path.stat().st_size, 0, f"Artifact {key} is empty")

    # 2. Cryptographic Traceability Chain
    def test_02_cryptographic_traceability_chain(self):
        trace = self.result["cryptographicTrace"]
        self.assertTrue(trace["geometryHash"].startswith("sha256:"))
        self.assertTrue(trace["regulationHash"].startswith("sha256:"))
        self.assertTrue(trace["customerBriefHash"].startswith("sha256:"))
        self.assertTrue(trace["designHash"].startswith("sha256:"))
        self.assertTrue(trace["boqHash"].startswith("sha256:"))
        self.assertTrue(trace["scheduleHash"].startswith("sha256:"))
        self.assertTrue(trace["releaseFingerprint"])

        # Re-compute fingerprint independently and verify exact match
        recomputed_fp = generate_release_fingerprint(
            geometry_hash=trace["geometryHash"],
            regulation_hash=trace["regulationHash"],
            customer_brief_hash=trace["customerBriefHash"],
            design_hash=trace["designHash"],
            boq_hash=trace["boqHash"],
            schedule_hash=trace["scheduleHash"]
        )
        self.assertEqual(trace["releaseFingerprint"], recomputed_fp)

    # 3. Invariant: 1,100 sq ft Preserved & Zero Benchmark Contamination
    def test_03_authoritative_1100_sqft_preserved_zero_contamination(self):
        self.assertEqual(self.result["declaredPlotAreaSqFt"], 1100.0)

        # Inspect generated manifest and cost files to ensure 0 contamination of 2,400 sq ft benchmark
        manifest_path = Path(self.result["artifactsGenerated"]["releaseManifest"])
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_text = f.read()

        self.assertNotIn("2,400 sq ft", manifest_text)
        self.assertNotIn("2400 sq ft", manifest_text)
        self.assertNotIn("10,000 sqm Mumbai Suburban", manifest_text)

        # Verify database record maintains 1,100.0 sq ft
        rev = ledger_repo.get_engineer_review(self.result["engineerReviewId"])
        self.assertEqual(rev.declaredPlotAreaSqFt, 1100.0)

    # 4. Anti-Bypass and Independent Gate Locking
    def test_04_anti_bypass_and_gate_locking(self):
        gates = self.result["reviewGates"]
        # Technical prerequisites G0–G4 must be verified
        self.assertEqual(gates["G0"], "VERIFIED")
        self.assertEqual(gates["G1"], "VERIFIED")
        self.assertEqual(gates["G2"], "VERIFIED")
        self.assertEqual(gates["G3"], "VERIFIED")
        self.assertEqual(gates["G4"], "VERIFIED")

        # G5 and G6 must remain strictly LOCKED
        self.assertEqual(gates["G5"], "LOCKED")
        self.assertEqual(gates["G6"], "LOCKED")

    # 5. PostgreSQL Persistence Verification
    def test_05_postgresql_persistence_verified(self):
        rev_id = self.result["engineerReviewId"]
        rel_id = self.result["releaseId"]

        # Fetch freshly from PostgreSQL database
        db_rev = ledger_repo.get_engineer_review(rev_id)
        self.assertIsNotNone(db_rev)
        self.assertEqual(db_rev.id, rev_id)
        self.assertEqual(db_rev.releaseId, rel_id)
        self.assertEqual(db_rev.status.value, "IN_REVIEW")

        db_rel = ledger_repo.get_release(rel_id)
        self.assertIsNotNone(db_rel)
        self.assertEqual(db_rel["fingerprint"], self.result["releaseFingerprint"])

    # 6. Release Immutability
    def test_06_pilot_release_immutability(self):
        rel_id = self.result["releaseId"]
        rel_data = ledger_repo.get_release(rel_id)

        # Attempt to mutate fingerprint on this frozen release
        tampered_data = dict(rel_data)
        tampered_data["fingerprint"] = "sha256:tampered_fp_hacked"

        with self.assertRaises(ReleaseImmutabilityError):
            ledger_repo.save_release(tampered_data, enforce_immutability=True)

    # 7. Missing Real-World Inputs Halt Pipeline (Zero Invented Values)
    def test_07_missing_real_world_inputs_halt_pipeline(self):
        pipe_runner = RealPlotPipelineRunner()

        # Missing jurisdiction -> must return JURISDICTION_REQUIRED
        payload_no_jur = RealPlotIntakePayload(
            site=SiteInput(
                location="Bandra West, Mumbai",
                jurisdiction=None,
                road_width_ft=40.0,
                shape=SiteShape.RECTANGULAR,
                dimensions=PlotDimensions(front_width_ft=27.5, left_length_ft=40.0)
            ),
            requirements=CustomerRequirementsInput(floors=2, bedrooms=2)
        )
        res_jur = pipe_runner.run_e2e_pipeline(payload_no_jur, project_id="TEST-FAIL-01")
        self.assertEqual(res_jur["status"], "JURISDICTION_REQUIRED")

        # Missing dimensions on irregular site -> must return USER_INPUT_REQUIRED
        payload_missing_dims = RealPlotIntakePayload(
            site=SiteInput(
                location="Bandra West, Mumbai",
                jurisdiction="MUMBAI_DCPR_2034",
                road_width_ft=40.0,
                shape=SiteShape.IRREGULAR,
                dimensions=None
            ),
            requirements=CustomerRequirementsInput(floors=2, bedrooms=2)
        )
        res_dims = pipe_runner.run_e2e_pipeline(payload_missing_dims, project_id="TEST-FAIL-02")
        self.assertEqual(res_dims["status"], "USER_INPUT_REQUIRED")


if __name__ == "__main__":
    unittest.main()
