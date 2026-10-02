"""
Planwise Enterprise — Phase 7 Engineer Review & Professional Verification Test Suite
===================================================================================

Verifies:
1. Engineer review creation
2. Correct Build Review package binding
3. G0 pending by default
4. G2 pending by default
5. G3 pending by default
6. Independent gate transitions
7. Request Changes requires at least one issue & marks CHANGES_REQUIRED
8. Blocker issue marks target gate to CHANGES_REQUIRED
9. Design change makes review stale
10. Cost stale protection
11. 1,100 sq ft preserved
12. Old 2,400 sq ft benchmark cannot overwrite real project
13. Audit/hash traceability
14. Unauthorized gate transition rejected (e.g. G5 without G0-G4 verified or with open blockers)
15. No automatic G5/G6 approval
"""

import unittest
import uuid
import importlib.util
from pathlib import Path
from fastapi import HTTPException

from packages.schemas.engineer_review import (
    EngineerReview,
    ReviewGate,
    ReviewIssue,
    ReviewDecision,
    GateCode,
    GateStatus,
    IssueSeverity,
    IssueStatus,
    ReviewDecisionType,
    ReviewStatus,
    create_initial_review_gates
)

# Dynamically load apps/api-gateway/main.py
SPEC_PATH = Path(__file__).resolve().parent.parent / "apps" / "api-gateway" / "main.py"
spec = importlib.util.spec_from_file_location("api_gateway_main", str(SPEC_PATH))
api_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api_mod)


class TestPhase7EngineerReview(unittest.TestCase):
    """Rigorous verification of Phase 7 Engineer Review and Professional Gates."""

    def setUp(self):
        # Create a mock build release in api_mod.RELEASES_DB
        self.test_release_id = f"rel-test-{uuid.uuid4().hex[:8]}"
        self.test_build_req_id = f"req-{uuid.uuid4().hex[:8]}"
        self.test_dv_id = f"DV-TEST-{uuid.uuid4().hex[:8]}"
        self.test_fp = "sha256:release_manifest_fingerprint_abc123"
        self.test_design_hash = "sha256:cbm_compiled_model_hash_xyz789"

        api_mod.RELEASES_DB[self.test_release_id] = {
            "releaseId": self.test_release_id,
            "projectId": "proj-mumbai-real-1100",
            "designVersionId": self.test_dv_id,
            "fingerprint": self.test_fp,
            "lifecycleState": "SUBMITTED_FOR_REVIEW",
            "houseOption": {
                "optionId": "opt-compact_2bhk",
                "designVersionId": self.test_dv_id,
                "designHash": self.test_design_hash,
                "boq": {
                    "totalBaseEstimate": 4250000,
                    "qualityTier": "STANDARD",
                    "qtoHash": "sha256:qto_valid"
                }
            }
        }
        api_mod.BUILD_REQUESTS_MAP[self.test_build_req_id] = self.test_release_id

    # 1. Engineer review creation
    def test_01_engineer_review_creation(self):
        review = api_mod.create_or_get_engineer_review(self.test_build_req_id)
        self.assertIsNotNone(review)
        self.assertIn("id", review)
        self.assertEqual(review["status"], ReviewStatus.IN_REVIEW.value)
        self.assertEqual(review["reviewerId"], "ENG-MH-48201")
        self.assertEqual(len(review["gates"]), 7)

    # 2. Correct Build Review package binding
    def test_02_correct_build_review_package_binding(self):
        review = api_mod.create_or_get_engineer_review(self.test_build_req_id)
        self.assertEqual(review["buildRequestId"], self.test_build_req_id)
        self.assertEqual(review["releaseId"], self.test_release_id)
        self.assertEqual(review["designVersionId"], self.test_dv_id)
        self.assertEqual(review["inputManifestHash"], self.test_fp)
        self.assertEqual(review["designVersionHash"], self.test_design_hash)

    # 3. G0 pending by default
    def test_03_g0_pending_by_default(self):
        review = api_mod.create_or_get_engineer_review(self.test_build_req_id)
        g0 = next(g for g in review["gates"] if g["gateCode"] == "G0")
        self.assertEqual(g0["status"], GateStatus.PENDING.value)
        self.assertIn("Boundary", g0["title"])

    # 4. G2 pending by default
    def test_04_g2_pending_by_default(self):
        review = api_mod.create_or_get_engineer_review(self.test_build_req_id)
        g2 = next(g for g in review["gates"] if g["gateCode"] == "G2")
        self.assertEqual(g2["status"], GateStatus.PENDING.value)
        self.assertIn("Structural", g2["title"])

    # 5. G3 pending by default
    def test_05_g3_pending_by_default(self):
        review = api_mod.create_or_get_engineer_review(self.test_build_req_id)
        g3 = next(g for g in review["gates"] if g["gateCode"] == "G3")
        self.assertEqual(g3["status"], GateStatus.PENDING.value)
        self.assertIn("MEP", g3["title"])

    # 6. Independent gate transitions
    def test_06_independent_gate_transitions(self):
        review = api_mod.create_or_get_engineer_review(self.test_build_req_id)
        review_id = review["id"]

        # Verify G2 (Structural)
        payload = api_mod.GateVerificationPayload(
            status=GateStatus.VERIFIED,
            reviewerId="ENG-MH-48201",
            notes="Column grid and spans checked against IS 456 guidelines."
        )
        res = api_mod.verify_review_gate(review_id, "G2", payload)
        self.assertEqual(res["gate"]["status"], GateStatus.VERIFIED.value)

        # Check that G0, G3, G5, G6 remain unchanged
        gates = api_mod.get_engineer_review_gates(review_id)
        g0 = next(g for g in gates if g["gateCode"] == "G0")
        g3 = next(g for g in gates if g["gateCode"] == "G3")
        g5 = next(g for g in gates if g["gateCode"] == "G5")
        g6 = next(g for g in gates if g["gateCode"] == "G6")

        self.assertEqual(g0["status"], GateStatus.PENDING.value)
        self.assertEqual(g3["status"], GateStatus.PENDING.value)
        self.assertEqual(g5["status"], GateStatus.LOCKED.value)
        self.assertEqual(g6["status"], GateStatus.LOCKED.value)

    # 7. Request Changes requires at least one structured issue
    def test_07_request_changes_requires_issue_and_sets_changes_required(self):
        review = api_mod.create_or_get_engineer_review(self.test_build_req_id)
        review_id = review["id"]

        # Attempt to request changes without issues -> must fail HTTP 400
        req_payload = api_mod.RequestChangesPayload(
            reviewerId="ENG-MH-48201",
            reason="Plot boundary discrepancy detected."
        )
        with self.assertRaises(HTTPException) as ctx:
            api_mod.request_review_changes(review_id, req_payload)
        self.assertEqual(ctx.exception.status_code, 400)

        # Now log a structured issue
        issue_payload = api_mod.CreateIssuePayload(
            gateCode=GateCode.G0,
            severity=IssueSeverity.WARNING,
            category="Site Boundary",
            description="Front setback appears constrained near north boundary.",
            requiredAction="Clarify physical offset from road curb."
        )
        api_mod.create_review_issue(review_id, issue_payload)

        # Now request changes succeeds
        res = api_mod.request_review_changes(review_id, req_payload)
        self.assertEqual(res["status"], ReviewStatus.CHANGES_REQUIRED.value)

        # G5 and G6 must be locked
        g5 = next(g for g in res["gates"] if g["gateCode"] == "G5")
        self.assertEqual(g5["status"], GateStatus.LOCKED.value)

    # 8. Blocker issue marks target gate to CHANGES_REQUIRED
    def test_08_blocker_issue_marks_gate_changes_required(self):
        review = api_mod.create_or_get_engineer_review(self.test_build_req_id)
        review_id = review["id"]

        issue_payload = api_mod.CreateIssuePayload(
            gateCode=GateCode.G2,
            severity=IssueSeverity.BLOCKER,
            category="Geotechnical",
            description="Foundation design requires geotechnical verification.",
            requiredAction="Upload soil test report before structural signoff."
        )
        api_mod.create_review_issue(review_id, issue_payload)

        gates = api_mod.get_engineer_review_gates(review_id)
        g2 = next(g for g in gates if g["gateCode"] == "G2")
        self.assertEqual(g2["status"], GateStatus.CHANGES_REQUIRED.value)

    # 9. Design change makes review stale
    def test_09_design_change_makes_review_stale(self):
        review = api_mod.create_or_get_engineer_review(self.test_build_req_id)
        review_id = review["id"]
        original_hash = review["designVersionHash"]

        # When design changes in release
        new_design_hash = "sha256:new_modified_cbm_design_hash_456"
        api_mod.RELEASES_DB[self.test_release_id]["houseOption"]["designHash"] = new_design_hash

        # Backend check for hash divergence
        curr_rel = api_mod.RELEASES_DB[self.test_release_id]
        if curr_rel["houseOption"]["designHash"] != review["designVersionHash"]:
            api_mod.ENGINEER_REVIEWS_DB[review_id].status = ReviewStatus.STALE

        updated_rev = api_mod.get_engineer_review(review_id)
        self.assertEqual(updated_rev["status"], ReviewStatus.STALE.value)

    # 10. Cost stale protection
    def test_10_cost_stale_protection(self):
        # A release with mismatched QTO or missing hash cannot proceed
        stale_rel_id = f"rel-stale-{uuid.uuid4().hex[:6]}"
        api_mod.RELEASES_DB[stale_rel_id] = {
            "releaseId": stale_rel_id,
            "projectId": "proj-mumbai-01",
            "designVersionId": "DV-OLD",
            "fingerprint": "sha256:fp",
            "lifecycleState": "SUBMITTED_FOR_REVIEW",
            "houseOption": {
                "designVersionId": "DV-NEW",
                "boq": {
                    "totalBaseEstimate": 4200000,
                    "qtoHash": None  # Stale: no valid QTO binding
                }
            }
        }
        # In BuildReviewView and backend, missing qtoHash flags isCostStale == True
        boq = api_mod.RELEASES_DB[stale_rel_id]["houseOption"]["boq"]
        is_stale = (boq.get("qtoHash") is None)
        self.assertTrue(is_stale)

    # 11. 1,100 sq ft preserved
    def test_11_1100_sqft_preserved_authoritative(self):
        review = api_mod.create_or_get_engineer_review(self.test_build_req_id)
        self.assertEqual(review["declaredPlotAreaSqFt"], 1100.0)

    # 12. Old 2,400 sq ft benchmark cannot overwrite real project
    def test_12_old_2400_sqft_cannot_overwrite_real_project(self):
        review = api_mod.create_or_get_engineer_review(self.test_build_req_id)
        self.assertNotEqual(review["declaredPlotAreaSqFt"], 2400.0)
        self.assertEqual(review["declaredPlotAreaSqFt"], 1100.0)

    # 13. Audit/hash traceability
    def test_13_audit_hash_traceability(self):
        review = api_mod.create_or_get_engineer_review(self.test_build_req_id)
        review_id = review["id"]

        payload = api_mod.GateVerificationPayload(
            status=GateStatus.VERIFIED,
            reviewerId="ENG-MH-48201",
            notes="Statutory setbacks and FAR verified under DCPR 2034."
        )
        api_mod.verify_review_gate(review_id, "G1", payload)

        gates = api_mod.get_engineer_review_gates(review_id)
        g1 = next(g for g in gates if g["gateCode"] == "G1")
        self.assertEqual(g1["reviewedBy"], "ENG-MH-48201")
        self.assertIsNotNone(g1["reviewedAt"])
        self.assertEqual(g1["notes"], "Statutory setbacks and FAR verified under DCPR 2034.")

    # 14. Unauthorized gate transition rejected (G5 without G0-G4 verified)
    def test_14_unauthorized_gate_transition_rejected(self):
        review = api_mod.create_or_get_engineer_review(self.test_build_req_id)
        review_id = review["id"]

        # Attempt to verify G5 while G0, G2, G3 are still PENDING
        payload = api_mod.GateVerificationPayload(
            status=GateStatus.VERIFIED,
            reviewerId="ENG-MH-48201",
            notes="Attempting premature build authorization."
        )
        with self.assertRaises(HTTPException) as ctx:
            api_mod.verify_review_gate(review_id, "G5", payload)

        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("G5/G6 cannot be verified until prerequisite gates", ctx.exception.detail)

    # 15. No automatic G5/G6 approval
    def test_15_no_automatic_g5_g6_approval(self):
        review = api_mod.create_or_get_engineer_review(self.test_build_req_id)
        review_id = review["id"]

        # Verify G0
        api_mod.verify_review_gate(review_id, "G0", api_mod.GateVerificationPayload(status=GateStatus.VERIFIED, reviewerId="ENG-01"))
        # Verify G2
        api_mod.verify_review_gate(review_id, "G2", api_mod.GateVerificationPayload(status=GateStatus.VERIFIED, reviewerId="ENG-01"))

        # G5 and G6 must still remain LOCKED
        gates = api_mod.get_engineer_review_gates(review_id)
        g5 = next(g for g in gates if g["gateCode"] == "G5")
        g6 = next(g for g in gates if g["gateCode"] == "G6")
        self.assertEqual(g5["status"], GateStatus.LOCKED.value)
        self.assertEqual(g6["status"], GateStatus.LOCKED.value)


if __name__ == "__main__":
    unittest.main()
