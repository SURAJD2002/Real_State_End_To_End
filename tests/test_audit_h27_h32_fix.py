"""
Regression tests verifying fixes for H27 and H32:
- H27: Unapproved releases must block IFC export and handoff package download with 403 Forbidden.
- H32: Engineer review gates and decisions must reject anonymous requests with 401 Unauthorized.
"""

import unittest
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "apps" / "api-gateway"))
sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient
from main import app, RELEASES_DB


class TestH27H32GatingAndAuth(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_unauthenticated_gate_verify_rejected(self):
        # Must return 401 Unauthorized if no auth token provided
        r = self.client.post(
            "/api/v1/engineer-reviews/rev-61004703af/gates/G0/verify",
            json={"status": "VERIFIED", "reviewerId": "ANONYMOUS", "notes": "none"}
        )
        self.assertEqual(r.status_code, 401, f"Expected 401 Unauthorized, got {r.status_code}")

    def test_unauthenticated_decision_rejected(self):
        # Must return 401 Unauthorized if no auth token provided
        r = self.client.post(
            "/api/v1/engineer-reviews/rev-61004703af/decision",
            json={"decision": "APPROVE_STAGE", "reason": "none", "reviewerId": "ANONYMOUS"}
        )
        self.assertEqual(r.status_code, 401, f"Expected 401 Unauthorized, got {r.status_code}")

    def test_unapproved_release_ifc_forbidden(self):
        rel_id = "rel-unapproved-test-suite"
        RELEASES_DB[rel_id] = {
            "releaseId": rel_id,
            "lifecycleState": "PROFESSIONAL_REVIEW",
            "houseOption": {"id": "opt-1"},
            "handoffPackage": {"status": "PENDING"}
        }
        r = self.client.get(f"/api/v1/releases/{rel_id}/ifc")
        self.assertEqual(r.status_code, 403, f"Expected 403 Forbidden for unapproved release IFC, got {r.status_code}")

        r_pkg = self.client.get(f"/api/v1/releases/{rel_id}/handoff-package")
        self.assertEqual(r_pkg.status_code, 403, f"Expected 403 Forbidden for unapproved release handoff package, got {r_pkg.status_code}")


if __name__ == "__main__":
    unittest.main()
