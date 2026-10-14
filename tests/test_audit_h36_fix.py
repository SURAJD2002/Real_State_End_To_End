"""
Regression test verifying fix for H36:
Eliminates silent fallback in request_build to proj-mumbai-real-1100.
Missing options must return 404 Not Found rather than fabricating a default pilot release.
"""

import unittest
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "apps" / "api-gateway"))
sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient
from main import app


class TestH36SilentFallback(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_request_build_rejects_missing_option_without_silent_fallback(self):
        payload = {
            "designVersionId": "DV-NON-EXISTENT",
            "optionId": "opt-does-not-exist",
            "requestedQualityTier": "STANDARD",
            "customerAcknowledgements": ["ESTIMATE_RANGE", "SITE_VERIFICATION", "PROFESSIONAL_DELIVERY"]
        }
        r = self.client.post("/api/v1/design-versions/DV-NON-EXISTENT/build-request", json=payload)
        self.assertEqual(r.status_code, 404, f"Expected 404 Not Found, but got {r.status_code}: {r.text}")


if __name__ == "__main__":
    unittest.main()
