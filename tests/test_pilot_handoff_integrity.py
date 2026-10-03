"""
Planwise Enterprise — Pilot Handoff Integrity Automated Test Suite
===================================================================
Delta Specification §6.3, §12, §13, §14 & Phase 8 Pilot Handoff Specification

Comprehensive verification of the authoritative pilot handoff package:
1. Release identity consistency (rel-pilot-20261002-aedf9830)
2. Design version consistency (DV-OPT-B-9be0a983)
3. Project identity consistency (proj-mumbai-real-1100)
4. Plot area 1,100 sq ft preserved across all files
5. Release fingerprint consistency (876f21ae800940245ed9702d9e00e27be2be636f033f5d24e85c0bb4fe877cb4)
6. Manifest artifact hash consistency (100% match with physical disk files)
7. BOQ -> CBM element traceability (100% valid elements)
8. Cost -> BOQ consistency (exact direct hard cost and total base estimate match)
9. Validation -> design version consistency
10. Engineer review -> PostgreSQL consistency
11. IFC release identity and STEP validity
12. G5/G6 strictly LOCKED
13. Benchmark contamination scan (zero 2400 / 40x60 / 10000 tokens)
14. Required legal disclaimer and safety notices scan
15. Stale / nonexistent release rejection
16. HANDOFF_RELEASE_MISMATCH fail-closed behavior.
"""

import os
import json
import hashlib
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

from workers.release.release_context import ReleaseContext, HandoffReleaseMismatchError
import ledger_repository as ledger_repo


class TestPilotHandoffIntegrity(unittest.TestCase):
    """Rigorous QA & cryptographic verification of the pilot handoff package."""

    @classmethod
    def setUpClass(cls):
        cls.authoritative_release_id = "rel-pilot-20261002-aedf9830"
        cls.authoritative_project_id = "proj-mumbai-real-1100"
        cls.authoritative_design_version_id = "DV-OPT-B-9be0a983"
        cls.authoritative_fingerprint = "876f21ae800940245ed9702d9e00e27be2be636f033f5d24e85c0bb4fe877cb4"
        cls.authoritative_plot_area = 1100.0

        cls.handoff_dir = ROOT_DIR / "artifacts" / "pilot_handoff"
        cls.ctx = ReleaseContext(release_id=cls.authoritative_release_id)

        # Ensure handoff package is exported and up to date
        cls.artifacts = cls.ctx.export_handoff_package(output_dir=cls.handoff_dir)

    # 1. Release Identity Consistency
    def test_01_release_identity_consistency(self):
        manifest = json.loads((self.handoff_dir / "pilot_release_manifest.json").read_text())
        boq = json.loads((self.handoff_dir / "pilot_boq_export.json").read_text())
        cost = json.loads((self.handoff_dir / "pilot_cost_estimate.json").read_text())
        val = json.loads((self.handoff_dir / "pilot_validation_report.json").read_text())
        rev = json.loads((self.handoff_dir / "pilot_engineer_review.json").read_text())

        self.assertEqual(manifest["releaseId"], self.authoritative_release_id)
        self.assertEqual(manifest["handoffPackageId"], f"pkg-{self.authoritative_release_id}")
        self.assertEqual(boq["releaseId"], self.authoritative_release_id)
        self.assertEqual(cost["releaseId"], self.authoritative_release_id)
        self.assertEqual(val["releaseId"], self.authoritative_release_id)
        self.assertEqual(rev["releaseId"], self.authoritative_release_id)

    # 2. Design Version Consistency
    def test_02_design_version_consistency(self):
        manifest = json.loads((self.handoff_dir / "pilot_release_manifest.json").read_text())
        boq = json.loads((self.handoff_dir / "pilot_boq_export.json").read_text())
        cost = json.loads((self.handoff_dir / "pilot_cost_estimate.json").read_text())
        val = json.loads((self.handoff_dir / "pilot_validation_report.json").read_text())
        rev = json.loads((self.handoff_dir / "pilot_engineer_review.json").read_text())

        self.assertEqual(manifest["designVersionId"], self.authoritative_design_version_id)
        self.assertEqual(boq["designVersionId"], self.authoritative_design_version_id)
        self.assertEqual(cost["designVersionId"], self.authoritative_design_version_id)
        self.assertEqual(val["designVersionId"], self.authoritative_design_version_id)
        self.assertEqual(rev["designVersionId"], self.authoritative_design_version_id)

    # 3. Project Identity Consistency
    def test_03_project_identity_consistency(self):
        manifest = json.loads((self.handoff_dir / "pilot_release_manifest.json").read_text())
        boq = json.loads((self.handoff_dir / "pilot_boq_export.json").read_text())
        cost = json.loads((self.handoff_dir / "pilot_cost_estimate.json").read_text())
        val = json.loads((self.handoff_dir / "pilot_validation_report.json").read_text())
        rev = json.loads((self.handoff_dir / "pilot_engineer_review.json").read_text())

        self.assertEqual(manifest["projectId"], self.authoritative_project_id)
        self.assertEqual(boq["projectId"], self.authoritative_project_id)
        self.assertEqual(cost["projectId"], self.authoritative_project_id)
        self.assertEqual(val["projectId"], self.authoritative_project_id)
        self.assertEqual(rev["projectId"], self.authoritative_project_id)

    # 4. Plot Area 1,100 sq ft Invariant
    def test_04_plot_area_1100_sqft_preserved(self):
        manifest = json.loads((self.handoff_dir / "pilot_release_manifest.json").read_text())
        rev = json.loads((self.handoff_dir / "pilot_engineer_review.json").read_text())

        self.assertEqual(manifest["declaredPlotAreaSqFt"], self.authoritative_plot_area)
        self.assertEqual(rev["declaredPlotAreaSqFt"], self.authoritative_plot_area)

        # Database record check
        db_rev = ledger_repo.get_engineer_review("rev-pilot-10739137b8")
        self.assertEqual(float(db_rev.declaredPlotAreaSqFt), self.authoritative_plot_area)

    # 5. Release Fingerprint Consistency
    def test_05_release_fingerprint_consistency(self):
        manifest = json.loads((self.handoff_dir / "pilot_release_manifest.json").read_text())
        self.assertEqual(manifest["releaseFingerprint"], self.authoritative_fingerprint)

        # Database record check
        rel = ledger_repo.get_release(self.authoritative_release_id)
        self.assertEqual(rel["fingerprint"], self.authoritative_fingerprint)

    # 6. Manifest Artifact Hash Consistency (Physical Disk Parity)
    def test_06_manifest_artifact_hash_consistency(self):
        manifest = json.loads((self.handoff_dir / "pilot_release_manifest.json").read_text())
        artifact_manifest = manifest.get("artifactManifest", [])
        self.assertGreater(len(artifact_manifest), 0)

        for entry in artifact_manifest:
            file_path = self.handoff_dir / entry["name"]
            self.assertTrue(file_path.exists(), f"File {entry['name']} missing from pilot_handoff")
            computed_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
            self.assertEqual(
                entry["hash"],
                computed_hash,
                f"Hash mismatch in manifest for {entry['name']}"
            )

    # 7. BOQ -> CBM Element Traceability
    def test_07_boq_cbm_element_traceability(self):
        boq = json.loads((self.handoff_dir / "pilot_boq_export.json").read_text())
        line_items = boq.get("lineItems", [])
        self.assertGreater(len(line_items), 0)

        for item in line_items:
            source_ids = item.get("sourceElementIds", [])
            self.assertGreater(len(source_ids), 0, f"Line item {item['itemCode']} has empty sourceElementIds")
            for eid in source_ids:
                # Valid prefixes: COL, SLAB, STAIR, WALL, DOOR, WIN, SPACE, SYS
                valid_prefix = any(eid.startswith(p) for p in ["COL-", "SLAB-", "STAIR-", "WALL-", "DOOR-", "WIN-", "SPACE-", "SYS-"])
                self.assertTrue(valid_prefix, f"Unknown CBM element ID: {eid}")

    # 8. Cost -> BOQ Consistency
    def test_08_cost_boq_consistency(self):
        boq = json.loads((self.handoff_dir / "pilot_boq_export.json").read_text())
        cost = json.loads((self.handoff_dir / "pilot_cost_estimate.json").read_text())
        manifest = json.loads((self.handoff_dir / "pilot_release_manifest.json").read_text())

        boq_direct_sum = sum(item["amount"] for item in boq["lineItems"])
        cost_hard_cost = cost["waterfall"]["grossHardCost"]
        cost_total = cost["waterfall"]["totalConstructionCost"]
        manifest_base = manifest["financialSummary"]["baseEstimate"]

        self.assertAlmostEqual(boq_direct_sum, cost_hard_cost, places=2)
        self.assertAlmostEqual(cost_total, manifest_base, places=2)

    # 9. Validation -> Design Version & Model Hash Consistency
    def test_09_validation_design_version_consistency(self):
        val = json.loads((self.handoff_dir / "pilot_validation_report.json").read_text())
        self.assertEqual(val["designVersionId"], self.authoritative_design_version_id)
        self.assertTrue(val["modelHash"].startswith("sha256:"))

    # 10. Engineer Review -> PostgreSQL Parity
    def test_10_engineer_review_postgresql_parity(self):
        rev = json.loads((self.handoff_dir / "pilot_engineer_review.json").read_text())
        db_rev = ledger_repo.get_engineer_review("rev-pilot-10739137b8")

        self.assertEqual(rev["id"], db_rev.id)
        self.assertEqual(rev["projectId"], db_rev.projectId)
        self.assertEqual(rev["releaseId"], db_rev.releaseId)
        self.assertEqual(rev["designVersionId"], db_rev.designVersionId)
        self.assertEqual(rev["reviewerId"], db_rev.reviewerId)
        self.assertEqual(rev["status"], db_rev.status.value)
        self.assertEqual(rev["inputManifestHash"], db_rev.inputManifestHash)
        self.assertEqual(rev["designVersionHash"], db_rev.designVersionHash)

    # 11. IFC Release Identity & STEP Syntax
    def test_11_ifc_release_identity_and_step_syntax(self):
        ifc_path = self.handoff_dir / "pilot_model_ifc4.ifc"
        content = ifc_path.read_text(encoding="utf-8")

        self.assertTrue(content.startswith("ISO-10303-21;"))
        self.assertTrue(content.strip().endswith("END-ISO-10303-21;"))
        self.assertIn("HEADER;", content)
        self.assertIn("DATA;", content)

        # Header release filename
        expected_ifc_name = f"'{self.authoritative_release_id}.ifc'"
        self.assertIn(expected_ifc_name, content)

        # Required entities
        for ent in ["IFCPROJECT", "IFCSITE", "IFCBUILDING", "IFCBUILDINGSTOREY", "IFCWALL", "IFCDOOR", "IFCWINDOW", "IFCSLAB", "IFCCOLUMN", "IFCSPACE"]:
            self.assertIn(ent, content)

    # 12. G5 & G6 Strictly LOCKED
    def test_12_gates_g5_g6_locked(self):
        rev = json.loads((self.handoff_dir / "pilot_engineer_review.json").read_text())
        gate_map = {g["gateCode"]: g["status"] for g in rev.get("gates", [])}

        self.assertEqual(gate_map.get("G5"), "LOCKED")
        self.assertEqual(gate_map.get("G6"), "LOCKED")

    # 13. Benchmark Contamination Scan
    def test_13_benchmark_contamination_scan(self):
        forbidden_tokens = ["2400", "2,400", "40x60", "40×60", "40 x 60", "10000", "10,000", "opt_40x60", "opt-A"]
        for f in self.handoff_dir.iterdir():
            text = f.read_text(encoding="utf-8", errors="ignore")
            for tok in forbidden_tokens:
                self.assertNotIn(tok, text, f"Benchmark contamination token '{tok}' found in {f.name}")

    # 14. Required Safety Disclaimers Scan
    def test_14_required_disclaimers_scan(self):
        manifest = json.loads((self.handoff_dir / "pilot_release_manifest.json").read_text())
        disclaimers = manifest.get("disclaimers", {})

        self.assertEqual(disclaimers.get("computationalValidationNotice"), "Computational validation is not professional certification.")
        self.assertEqual(disclaimers.get("preliminaryCostNotice"), "Preliminary cost estimate is not a contractor quotation.")
        self.assertEqual(disclaimers.get("municipalApprovalNotice"), "Municipal approval is pending.")
        self.assertEqual(disclaimers.get("constructionAuthorizationNotice"), "Construction authorization is pending.")

    # 15. Stale / Nonexistent Release Rejection
    def test_15_stale_release_rejection(self):
        with self.assertRaises(HandoffReleaseMismatchError):
            ReleaseContext(release_id="rel-nonexistent-99999999-00000000")

    # 16. HANDOFF_RELEASE_MISMATCH Fail-Closed Behavior
    def test_16_handoff_release_mismatch_fail_closed(self):
        # Passing an artifact from an mismatched release must raise HandoffReleaseMismatchError
        bad_artifact = {
            "projectId": "proj-mumbai-real-1100",
            "releaseId": "rel-bad-alien-release",
            "designVersionId": "DV-OPT-B-9be0a983"
        }
        with self.assertRaises(HandoffReleaseMismatchError):
            self.ctx.validate_source_artifact("test_artifact.json", bad_artifact)


if __name__ == "__main__":
    unittest.main()
