"""
Planwise Enterprise — Negative Security & Cryptographic Verification Test Suite
================================================================================
Strict verification that all insecure, unsigned, forged, expired, and cross-tenant
access attempts are rejected with appropriate HTTP 401 or 403 status codes.

Gates Tested:
1. Unsigned JWT (alg=none) -> 401 Unauthorized
2. Forged Symmetric Signature (wrong HS256 secret) -> 401 Unauthorized
3. Forged Asymmetric Signature (attacker EC key) -> 401 Unauthorized
4. Tampered Payload (signature mismatch) -> 401 Unauthorized
5. Expired Token (exp in the past) -> 401 Unauthorized
6. Invalid Audience (aud != 'authenticated') -> 401 Unauthorized
7. Invalid Issuer (iss != project issuer) -> 401 Unauthorized
8. Privilege Escalation Prevention (arbitrary role injection ignored)
9. Cross-Tenant Read Attempt -> 403 Forbidden
10. Cross-Tenant Write Attempt -> 403 Forbidden
11. Genuine Supabase Token Cryptographic Verification (ES256 JWKS)
"""

import os
import sys
import uuid
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path
import jwt
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "apps" / "api-gateway"))

import main as api_main
from auth import get_jwt_secret, get_supabase_url, verify_supabase_jwt

client = TestClient(api_main.app)

TEST_JWT_SECRET = get_jwt_secret() or "real-server-configured-secret-key-32b!!"
os.environ["JWT_SECRET"] = TEST_JWT_SECRET


def create_valid_hs256_token(user_id: str, email: str, org_name: str = "Test Org") -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "role": "authenticated",
        "aud": "authenticated",
        "exp": int(datetime.now(timezone.utc).timestamp()) + 3600,
        "user_metadata": {
            "full_name": "Legitimate User",
            "org_name": org_name
        }
    }
    return jwt.encode(payload, TEST_JWT_SECRET, algorithm="HS256")


class TestAuthSecurityNegative(unittest.TestCase):
    """Negative security test suite for authentication and multi-tenant authorization."""

    @classmethod
    def setUpClass(cls):
        cls.legit_user_a = str(uuid.uuid4())
        cls.legit_user_b = str(uuid.uuid4())
        cls.token_a = create_valid_hs256_token(cls.legit_user_a, "tenant.a@enterprise.com", "Tenant A Corp")
        cls.token_b = create_valid_hs256_token(cls.legit_user_b, "tenant.b@enterprise.com", "Tenant B Corp")

        # Create Tenant B project to test cross-tenant read/write
        resp = client.post(
            "/api/v1/projects",
            json={"name": "Tenant B Confidential Site", "description": "Strictly confidential"},
            headers={"Authorization": f"Bearer {cls.token_b}"}
        )
        assert resp.status_code == 201, f"Failed to setup fixture project: {resp.text}"
        cls.proj_b_id = resp.json()["id"]

    def test_01_unsigned_token_rejected_with_401(self):
        """Unsigned token (alg=none) must be strictly rejected with HTTP 401."""
        unsigned_token = jwt.encode(
            {"sub": str(uuid.uuid4()), "role": "authenticated", "aud": "authenticated"},
            key="",
            algorithm="none"
        )
        resp = client.get(
            "/api/v1/auth/session",
            headers={"Authorization": f"Bearer {unsigned_token}"}
        )
        self.assertEqual(resp.status_code, 401)
        self.assertIn("rejected", resp.json()["detail"].lower())

    def test_02_forged_symmetric_key_rejected_with_401(self):
        """Token signed with wrong HS256 key must be rejected with HTTP 401."""
        attacker_secret = "attacker-unauthorized-secret-key-32b!!"
        forged_token = jwt.encode(
            {
                "sub": str(uuid.uuid4()),
                "email": "attacker@evil.com",
                "role": "authenticated",
                "aud": "authenticated",
                "exp": int(datetime.now(timezone.utc).timestamp()) + 3600
            },
            attacker_secret,
            algorithm="HS256"
        )
        resp = client.get(
            "/api/v1/auth/session",
            headers={"Authorization": f"Bearer {forged_token}"}
        )
        self.assertEqual(resp.status_code, 401)
        self.assertIn("token", resp.json()["detail"].lower())

    def test_03_forged_es256_asymmetric_key_rejected_with_401(self):
        """ES256 token signed by attacker's private key must fail JWKS verification with HTTP 401."""
        attacker_key = ec.generate_private_key(ec.SECP256R1())
        forged_es256_token = jwt.encode(
            {
                "sub": str(uuid.uuid4()),
                "email": "forger@attacker.com",
                "role": "authenticated",
                "aud": "authenticated",
                "iss": f"{get_supabase_url()}/auth/v1",
                "exp": int(datetime.now(timezone.utc).timestamp()) + 3600
            },
            attacker_key,
            algorithm="ES256",
            headers={"kid": "4da63cd4-0e46-401e-9335-32883b347dc4"}
        )
        resp = client.get(
            "/api/v1/auth/session",
            headers={"Authorization": f"Bearer {forged_es256_token}"}
        )
        self.assertEqual(resp.status_code, 401)
        self.assertIn("verification failed", resp.json()["detail"].lower())

    def test_04_tampered_payload_rejected_with_401(self):
        """Modifying payload bytes of a valid token destroys signature and triggers HTTP 401."""
        parts = self.token_a.split(".")
        # Tamper middle payload component
        tampered_token = f"{parts[0]}.eyJuZXdfc3ViIjoiZmFrZSJ9.{parts[2]}"
        resp = client.get(
            "/api/v1/auth/session",
            headers={"Authorization": f"Bearer {tampered_token}"}
        )
        self.assertEqual(resp.status_code, 401)

    def test_05_expired_token_rejected_with_401(self):
        """Expired token must be rejected with HTTP 401."""
        expired_payload = {
            "sub": str(uuid.uuid4()),
            "email": "user@expired.com",
            "role": "authenticated",
            "aud": "authenticated",
            "exp": int(datetime.now(timezone.utc).timestamp()) - 3600  # 1 hour ago
        }
        expired_token = jwt.encode(expired_payload, TEST_JWT_SECRET, algorithm="HS256")
        resp = client.get(
            "/api/v1/auth/session",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        self.assertEqual(resp.status_code, 401)
        self.assertIn("expired", resp.json()["detail"].lower())

    def test_06_invalid_audience_rejected_with_401(self):
        """Token with aud != 'authenticated' must be rejected with HTTP 401."""
        bad_aud_payload = {
            "sub": str(uuid.uuid4()),
            "email": "user@other.com",
            "role": "authenticated",
            "aud": "attacker-client-id",
            "exp": int(datetime.now(timezone.utc).timestamp()) + 3600
        }
        bad_aud_token = jwt.encode(bad_aud_payload, TEST_JWT_SECRET, algorithm="HS256")
        resp = client.get(
            "/api/v1/auth/session",
            headers={"Authorization": f"Bearer {bad_aud_token}"}
        )
        self.assertEqual(resp.status_code, 401)
        self.assertIn("audience", resp.json()["detail"].lower())

    def test_07_invalid_issuer_rejected_with_401(self):
        """ES256 Token claiming wrong issuer must be rejected."""
        attacker_key = ec.generate_private_key(ec.SECP256R1())
        wrong_iss_token = jwt.encode(
            {
                "sub": str(uuid.uuid4()),
                "email": "user@attacker.com",
                "role": "authenticated",
                "aud": "authenticated",
                "iss": "https://malicious-issuer.com/auth/v1",
                "exp": int(datetime.now(timezone.utc).timestamp()) + 3600
            },
            attacker_key,
            algorithm="ES256",
            headers={"kid": "4da63cd4-0e46-401e-9335-32883b347dc4"}
        )
        resp = client.get(
            "/api/v1/auth/session",
            headers={"Authorization": f"Bearer {wrong_iss_token}"}
        )
        self.assertEqual(resp.status_code, 401)

    def test_08_role_escalation_attempt_prevented(self):
        """Client trying to self-assign SUPERADMIN or bypass DB membership cannot escalate."""
        escalation_payload = {
            "sub": str(uuid.uuid4()),
            "email": "escalate@attacker.com",
            "role": "SUPERADMIN",
            "aud": "authenticated",
            "exp": int(datetime.now(timezone.utc).timestamp()) + 3600,
            "user_metadata": {
                "role": "GLOBAL_ROOT_ADMIN",
                "org_name": "Tenant B Corp"  # Attempting to hijack Tenant B
            }
        }
        token = jwt.encode(escalation_payload, TEST_JWT_SECRET, algorithm="HS256")
        resp = client.get(
            "/api/v1/auth/session",
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        # Role must NOT be GLOBAL_ROOT_ADMIN or SUPERADMIN
        self.assertEqual(data["role"], "OWNER")
        # Organization must be an isolated fresh tenant, NOT Tenant B Corp
        resp_b = client.get("/api/v1/auth/session", headers={"Authorization": f"Bearer {self.token_b}"})
        self.assertNotEqual(data["organization"]["id"], resp_b.json()["organization"]["id"])

    def test_09_cross_tenant_read_rejected_with_403(self):
        """Tenant A attempting to read Tenant B's confidential project must receive HTTP 403."""
        resp = client.get(
            f"/api/v1/projects/{self.proj_b_id}",
            headers={"Authorization": f"Bearer {self.token_a}"}
        )
        self.assertEqual(resp.status_code, 403)
        self.assertIn("Cross-tenant access denied", resp.json()["detail"])

    def test_10_cross_tenant_write_rejected_with_403(self):
        """Tenant A attempting to modify Tenant B's parcel geometries must receive HTTP 403."""
        resp = client.put(
            f"/api/v1/projects/{self.proj_b_id}/geometries",
            json={
                "coordinates": [
                    [72.82950, 19.05960],
                    [72.82958, 19.05960],
                    [72.82958, 19.05971],
                    [72.82950, 19.05971],
                    [72.82950, 19.05960]
                ],
                "cadastralSurveyNumber": "CTS-FORGED",
                "tenureType": "PRIVATE_FREEHOLD",
                "existingRoadWidthM": 9.0,
                "proposedRoadWidthM": 12.0,
                "version": 1
            },
            headers={"Authorization": f"Bearer {self.token_a}"}
        )
        self.assertEqual(resp.status_code, 403)
    def test_11_real_supabase_auth_token_verified_successfully(self):
        """Genuine ES256 token issued by Supabase Auth passes cryptographic JWKS verification."""
        import urllib.request
        from auth import get_supabase_anon_key

        supabase_url = get_supabase_url()
        anon_key = get_supabase_anon_key()
        if not anon_key:
            self.skipTest("SUPABASE_ANON_KEY not configured for live cloud token acquisition")

        test_email = "planwise.pilot.tester@gmail.com"
        test_password = "SecurePilotPassword2026!"

        # Acquire real token directly from Supabase Auth
        req_data = json.dumps({"email": test_email, "password": test_password}).encode("utf-8")
        headers = {"apikey": anon_key, "Content-Type": "application/json"}
        signin_req = urllib.request.Request(f"{supabase_url}/auth/v1/token?grant_type=password", data=req_data, headers=headers)
        try:
            with urllib.request.urlopen(signin_req, timeout=10) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                real_token = res["access_token"]
        except Exception as e:
            self.skipTest(f"Could not reach Supabase Auth endpoint: {e}")

        # Check that algorithm is genuine ES256
        header = jwt.get_unverified_header(real_token)
        self.assertEqual(header.get("alg"), "ES256")
        self.assertIsNotNone(header.get("kid"))

        # Verify against our API Gateway endpoint
        api_resp = client.get(
            "/api/v1/auth/session",
            headers={"Authorization": f"Bearer {real_token}"}
        )
        self.assertEqual(api_resp.status_code, 200)
        data = api_resp.json()
        self.assertTrue(data["authenticated"])
        self.assertEqual(data["user"]["email"], test_email)
        self.assertIsNotNone(data["organization"]["id"])


if __name__ == "__main__":
    unittest.main()
