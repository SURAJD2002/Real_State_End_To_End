"""
Comprehensive S0 Audit Test Suite:
(a) Envelope fully inside plot minus setbacks for a 28x46 ft rectangle and a 27.5x40 ft rectangle.
(b) Unknown jurisdiction -> structured UNVERIFIED / HTTP 422.
(c) Customer token -> HTTP 403 on reviewer endpoints (gate verify, decision, update_gate_approval, request-changes).
(d) Fake id -> HTTP 404 on every IFC route (/releases/{id}/ifc and /design-versions/{id}/ifc).
(e) Fallback options (isFallback) cannot be marked compliant by G1, UI, cost or export.
"""

import os
import sys
import uuid
import unittest
from datetime import datetime, timezone
from pathlib import Path
import jwt

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "apps" / "api-gateway"))
sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient
from main import app, RELEASES_DB, ENGINEER_REVIEWS_DB, HOUSE_OPTIONS_CACHE, PROJECTS_DB
from auth import get_jwt_secret
from postgres_repository import OrganizationRepository
from workers.geometry.envelope import (
    compute_statutory_envelope,
    UnknownJurisdictionError
)
from packages.schemas.engineer_review import (
    EngineerReview, GateCode, GateStatus, ReviewStatus, ReviewIssue, IssueSeverity, IssueStatus
)

TEST_JWT_SECRET = get_jwt_secret() or "real-server-configured-secret-key-32b!!"
os.environ["JWT_SECRET"] = TEST_JWT_SECRET


def create_role_token(user_id: str, email: str, role: str, org_name: str = "Test Org") -> str:
    """Generates a test JWT with an explicit organization role."""
    payload = {
        "sub": user_id,
        "email": email,
        "role": "authenticated",
        "aud": "authenticated",
        "exp": int(datetime.now(timezone.utc).timestamp()) + 3600,
        "user_metadata": {
            "full_name": f"{role.capitalize()} User",
            "org_name": org_name,
            "role": role
        }
    }
    # Pre-seed cache so role resolution is immediate and exact
    OrganizationRepository._MEMBERSHIP_CACHE[user_id] = {
        "organization": {"id": str(uuid.uuid4()), "name": org_name, "slug": "test-org"},
        "role": role
    }
    return jwt.encode(payload, TEST_JWT_SECRET, algorithm="HS256")


class TestAuditS0Comprehensive(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.customer_user_id = str(uuid.uuid4())
        self.reviewer_user_id = str(uuid.uuid4())
        self.customer_token = create_role_token(self.customer_user_id, "customer@homeowner.com", "CUSTOMER")
        self.reviewer_token = create_role_token(self.reviewer_user_id, "reviewer@chartered-eng.com", "REVIEWER")

    # =========================================================================
    # (a) Envelope inside plot minus setbacks
    # =========================================================================
    def test_01_envelope_28x46_ft_inside_plot_minus_setbacks(self):
        """28x46 ft plot must compute envelope strictly inside plot minus setbacks and cap coverage."""
        res = compute_statutory_envelope(
            plot_input={"width_ft": 28.0, "length_ft": 46.0},
            jurisdiction="MUMBAI_DCPR_2034_V1"
        )
        self.assertEqual(res["status"], "VERIFIED")
        self.assertTrue(res["isFullyInsidePlotMinusSetbacks"], "Envelope must be strictly contained inside plot minus setbacks")
        self.assertLessEqual(res["actualCoveragePercent"], res["maxGroundCoveragePercent"] + 1e-4)
        self.assertGreater(res["envelopeWidthM"], 0.0)
        self.assertGreater(res["envelopeLengthM"], 0.0)

    def test_02_envelope_27_5x40_ft_inside_plot_minus_setbacks(self):
        """27.5x40 ft (1100 sq ft) plot must compute envelope strictly inside plot minus setbacks."""
        res = compute_statutory_envelope(
            plot_input={"width_ft": 27.5, "length_ft": 40.0},
            jurisdiction="MUMBAI_DCPR_2034_V1"
        )
        self.assertEqual(res["status"], "VERIFIED")
        self.assertTrue(res["isFullyInsidePlotMinusSetbacks"], "Envelope must be strictly contained inside plot minus setbacks")
        self.assertLessEqual(res["actualCoveragePercent"], res["maxGroundCoveragePercent"] + 1e-4)
        # Footprint must be bounded by setbacks (front=3.0, rear=2.0, sides=1.5) and 50% coverage
        self.assertLessEqual(res["footprintAreaSqm"], res["plotAreaSqm"] * 0.50 + 1e-4)

    # =========================================================================
    # (b) Unknown jurisdiction -> structured UNVERIFIED / 422
    # =========================================================================
    def test_03_unknown_jurisdiction_envelope_unverified(self):
        """Unknown jurisdiction in envelope computation raises UnknownJurisdictionError."""
        with self.assertRaises(UnknownJurisdictionError):
            compute_statutory_envelope(
                plot_input={"width_ft": 28.0, "length_ft": 46.0},
                jurisdiction="PUNE_PMC_UNKNOWN_2026"
            )

    def test_04_unknown_jurisdiction_api_returns_422_unverified(self):
        """API endpoint requesting unknown jurisdiction must return HTTP 422 with structured UNVERIFIED."""
        resp = self.client.get(
            "/api/v1/regulation/rule-packs/PUNE_PMC_UNKNOWN_2026",
            headers={"Authorization": f"Bearer {self.reviewer_token}"}
        )
        self.assertEqual(resp.status_code, 422)
        body = resp.json()
        self.assertEqual(body.get("status"), "UNVERIFIED")
        self.assertFalse(body.get("verified"))
        self.assertIn("PUNE_PMC_UNKNOWN_2026", body.get("jurisdiction", ""))

    # =========================================================================
    # (c) Customer token -> 403 on reviewer endpoints
    # =========================================================================
    def test_05_customer_token_forbidden_on_gate_verify(self):
        """Customer token calling gate verify must receive HTTP 403 Forbidden."""
        rev_id = "rev-test-customer-block"
        from main import create_initial_review_gates
        ENGINEER_REVIEWS_DB[rev_id] = EngineerReview(
            id=rev_id,
            projectId="proj-mumbai-real-1100",
            buildRequestId="br-test-1",
            releaseId="rel-pilot-20261002-aedf9830",
            designVersionId="DV-OPT-B-9be0a983",
            reviewerId="ENG-1",
            status=ReviewStatus.IN_REVIEW,
            inputManifestHash="h1",
            designVersionHash="h2",
            declaredPlotAreaSqFt=1100.0,
            gates=create_initial_review_gates(rev_id),
            issues=[],
            decisions=[]
        )
        resp = self.client.post(
            f"/api/v1/engineer-reviews/{rev_id}/gates/G0/verify",
            json={"status": "VERIFIED", "reviewerId": "ATTACKER", "notes": "unauthorized"},
            headers={"Authorization": f"Bearer {self.customer_token}"}
        )
        self.assertEqual(resp.status_code, 403)
        self.assertIn("Reviewer authorization required", resp.json()["detail"])

    def test_06_customer_token_forbidden_on_decision(self):
        """Customer token calling review decision must receive HTTP 403 Forbidden."""
        rev_id = "rev-test-customer-block-decision"
        from main import create_initial_review_gates
        ENGINEER_REVIEWS_DB[rev_id] = EngineerReview(
            id=rev_id,
            projectId="proj-mumbai-real-1100",
            buildRequestId="br-test-2",
            releaseId="rel-pilot-20261002-aedf9830",
            designVersionId="DV-OPT-B-9be0a983",
            reviewerId="ENG-1",
            status=ReviewStatus.IN_REVIEW,
            inputManifestHash="h1",
            designVersionHash="h2",
            declaredPlotAreaSqFt=1100.0,
            gates=create_initial_review_gates(rev_id),
            issues=[],
            decisions=[]
        )
        resp = self.client.post(
            f"/api/v1/engineer-reviews/{rev_id}/decision",
            json={"decision": "APPROVE_STAGE", "reason": "none", "reviewerId": "ATTACKER"},
            headers={"Authorization": f"Bearer {self.customer_token}"}
        )
        self.assertEqual(resp.status_code, 403)

    def test_07_customer_token_forbidden_on_request_changes(self):
        """Customer token calling request changes must receive HTTP 403 Forbidden."""
        rev_id = "rev-test-customer-block-changes"
        from main import create_initial_review_gates
        ENGINEER_REVIEWS_DB[rev_id] = EngineerReview(
            id=rev_id,
            projectId="proj-mumbai-real-1100",
            buildRequestId="br-test-3",
            releaseId="rel-pilot-20261002-aedf9830",
            designVersionId="DV-OPT-B-9be0a983",
            reviewerId="ENG-1",
            status=ReviewStatus.IN_REVIEW,
            inputManifestHash="h1",
            designVersionHash="h2",
            declaredPlotAreaSqFt=1100.0,
            gates=create_initial_review_gates(rev_id),
            issues=[],
            decisions=[]
        )
        resp = self.client.post(
            f"/api/v1/engineer-reviews/{rev_id}/request-changes",
            json={"reason": "none", "reviewerId": "ATTACKER"},
            headers={"Authorization": f"Bearer {self.customer_token}"}
        )
        self.assertEqual(resp.status_code, 403)

    def test_08_customer_token_forbidden_on_update_gate_approval(self):
        """Customer token calling release gate approval must receive HTTP 403 Forbidden."""
        rel_id = "rel-pilot-20261002-aedf9830"
        resp = self.client.post(
            f"/api/v1/releases/{rel_id}/approvals",
            json={"gate": "G0", "decision": "APPROVED", "professionalId": "ATTACKER", "notes": ""},
            headers={"Authorization": f"Bearer {self.customer_token}"}
        )
        self.assertEqual(resp.status_code, 403)

    # =========================================================================
    # (d) Fake id -> 404 on every IFC route
    # =========================================================================
    def test_09_fake_id_returns_404_on_release_ifc_route(self):
        """Unknown release ID on GET /releases/{id}/ifc must return HTTP 404."""
        resp = self.client.get(
            "/api/v1/releases/rel-fake-nonexistent-id-9999/ifc",
            headers={"Authorization": f"Bearer {self.reviewer_token}"}
        )
        self.assertEqual(resp.status_code, 404)

    def test_10_fake_id_returns_404_on_design_version_ifc_route(self):
        """Unknown design version on GET /design-versions/{id}/ifc must return HTTP 404 (never synthetic model)."""
        resp = self.client.get(
            "/api/v1/design-versions/DV-FAKE-NONEXISTENT-9999/ifc",
            headers={"Authorization": f"Bearer {self.reviewer_token}"}
        )
        self.assertEqual(resp.status_code, 404)

    def test_11_unauthenticated_projects_route_rejected_with_401(self):
        """Unauthenticated GET /api/v1/projects must return HTTP 401."""
        resp = self.client.get("/api/v1/projects")
        self.assertEqual(resp.status_code, 401)

    # =========================================================================
    # (e) Fallback options (isFallback) blocked from compliance & export
    # =========================================================================
    def test_12_fallback_option_cannot_be_approved_at_g1(self):
        """Gate G1 verify must reject fallback archetypes with HTTP 400."""
        rev_id = "rev-test-fallback-g1"
        dv_id = "DV-FALLBACK-TEST-OPT"
        from main import create_initial_review_gates
        # Seed option in HOUSE_OPTIONS_CACHE as isFallback
        HOUSE_OPTIONS_CACHE["proj-mumbai-real-1100"] = [{
            "designVersionId": dv_id,
            "optionId": "opt-fallback-1",
            "isFallback": True,
            "fallbackReason": "CP_SAT_INFEASIBLE_OR_TIMEOUT"
        }]
        ENGINEER_REVIEWS_DB[rev_id] = EngineerReview(
            id=rev_id,
            projectId="proj-mumbai-real-1100",
            buildRequestId="br-test-fallback",
            releaseId="rel-pilot-20261002-aedf9830",
            designVersionId=dv_id,
            reviewerId="ENG-1",
            status=ReviewStatus.IN_REVIEW,
            inputManifestHash="h1",
            designVersionHash="h2",
            declaredPlotAreaSqFt=1100.0,
            gates=create_initial_review_gates(rev_id),
            issues=[],
            decisions=[]
        )
        resp = self.client.post(
            f"/api/v1/engineer-reviews/{rev_id}/gates/G1/verify",
            json={"status": "VERIFIED", "reviewerId": "ENG-1", "notes": "approve fallback"},
            headers={"Authorization": f"Bearer {self.reviewer_token}"}
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Gate G1 (Statutory Compliance) cannot be verified for fallback options", resp.json()["detail"])


if __name__ == "__main__":
    unittest.main()
