"""
Planwise Enterprise — Phase 8.1 Persistent Review & Release Ledger Test Suite
=============================================================================
Delta Specification §6.3, §12, §13, §14 & Phase 8.1 Specification

Verifies:
1. PostgreSQL persistence for Engineer Reviews, Gates (G0–G6), Issues, Decisions, and Releases.
2. Independent PostgreSQL verification (verifying raw tables directly).
3. Process restart persistence (clearing all in-memory caches, re-fetching and verifying state).
4. Release immutability (frozen design & deterministic fingerprint).
5. Fail-closed behavior (database unavailable returns controlled error, never silent fallback).
6. Security and credential privacy (no secrets in error messages or logs).
"""

import os
import unittest
import uuid
import importlib.util
from pathlib import Path
from fastapi import HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor

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
    ReviewStatus
)
from workers.release.manifest_engine import generate_release_fingerprint

# Dynamically load apps/api-gateway/main.py
SPEC_PATH = Path(__file__).resolve().parent.parent / "apps" / "api-gateway" / "main.py"
spec = importlib.util.spec_from_file_location("api_gateway_main", str(SPEC_PATH))
api_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api_mod)

import sys
from pathlib import Path
REPO_DIR = Path(__file__).resolve().parent.parent / "apps" / "api-gateway"
sys.path.insert(0, str(REPO_DIR))

import ledger_repository as ledger_repo
from ledger_repository import (
    DatabaseLedgerError,
    ReleaseImmutabilityError,
    get_db_connection,
    get_db_url
)


class TestPhase81Persistence(unittest.TestCase):
    """Rigorous verification of Phase 8.1 Persistent Ledger, Restart Safety & Immutability."""

    def setUp(self):
        self.test_release_id = f"rel-p81-{uuid.uuid4().hex[:8]}"
        self.test_build_req_id = f"br-p81-{uuid.uuid4().hex[:8]}"
        self.test_dv_id = f"DV-P81-{uuid.uuid4().hex[:8]}"
        self.test_fp = "sha256:release_fingerprint_phase81_authoritative"
        self.test_design_hash = "sha256:design_hash_phase81_1100sqft"

        # Create release record
        self.release_data = {
            "releaseId": self.test_release_id,
            "projectId": "proj-mumbai-real-1100",
            "designVersionId": self.test_dv_id,
            "fingerprint": self.test_fp,
            "lifecycleState": "SUBMITTED_FOR_REVIEW",
            "status": "BUILD_REQUESTED",
            "houseOption": {
                "optionId": "opt-compact_2bhk",
                "designVersionId": self.test_dv_id,
                "designHash": self.test_design_hash,
                "boq": {
                    "totalBaseEstimate": 4250000,
                    "qualityTier": "STANDARD",
                    "qtoHash": "sha256:qto_p81_valid"
                }
            },
            "handoffPackage": {
                "releaseId": self.test_release_id,
                "lifecycleState": "SUBMITTED_FOR_REVIEW",
                "humanVerificationGates": [
                    {"gate": "G0", "status": "PENDING"},
                    {"gate": "G1", "status": "PENDING"},
                    {"gate": "G2", "status": "PENDING"},
                    {"gate": "G3", "status": "PENDING"}
                ]
            }
        }
        api_mod.RELEASES_DB[self.test_release_id] = self.release_data
        api_mod.BUILD_REQUESTS_MAP[self.test_build_req_id] = self.test_release_id

    def tearDown(self):
        # Clean up database records created for test
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM releases WHERE id = %s", (self.test_release_id,))
        except Exception:
            pass

    # 1. Verify Create and Raw PostgreSQL Persistence
    def test_01_create_review_persists_to_postgresql(self):
        review = api_mod.create_or_get_engineer_review(self.test_build_req_id)
        review_id = review["id"]

        # Add an issue
        issue_payload = api_mod.CreateIssuePayload(
            gateCode=GateCode.G0,
            severity=IssueSeverity.WARNING,
            category="Site Survey",
            description="Survey benchmark alignment check recommended.",
            requiredAction="Surveyor signoff required."
        )
        api_mod.create_review_issue(review_id, issue_payload)

        # Directly query PostgreSQL raw tables bypassing API objects
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Check releases table
                cur.execute("SELECT * FROM releases WHERE id = %s", (self.test_release_id,))
                rel_row = cur.fetchone()
                self.assertIsNotNone(rel_row)
                self.assertEqual(rel_row["release_fingerprint"], self.test_fp)
                self.assertEqual(rel_row["design_version_id"], self.test_dv_id)

                # Check engineer_reviews table
                cur.execute("SELECT * FROM engineer_reviews WHERE id = %s", (review_id,))
                rev_row = cur.fetchone()
                self.assertIsNotNone(rev_row)
                self.assertEqual(rev_row["project_id"], "proj-mumbai-real-1100")
                self.assertEqual(rev_row["status"], "IN_REVIEW")
                self.assertEqual(float(rev_row["declared_plot_area_sqft"]), 1100.0)

                # Check engineer_review_gates table
                cur.execute("SELECT COUNT(*) FROM engineer_review_gates WHERE engineer_review_id = %s", (review_id,))
                gate_count = cur.fetchone()["count"]
                self.assertEqual(gate_count, 7)

                # Check engineer_review_issues table
                cur.execute("SELECT * FROM engineer_review_issues WHERE engineer_review_id = %s", (review_id,))
                issues = cur.fetchall()
                self.assertEqual(len(issues), 1)
                self.assertEqual(issues[0]["category"], "Site Survey")
                self.assertEqual(issues[0]["severity"], "WARNING")

    # 2. Restart Persistence Test (Process Restart Simulation)
    def test_02_process_restart_persistence(self):
        # Step A: Create and mutate review state
        review = api_mod.create_or_get_engineer_review(self.test_build_req_id)
        review_id = review["id"]

        # Verify G0 gate
        verify_payload = api_mod.GateVerificationPayload(
            status=GateStatus.VERIFIED,
            reviewerId="ENG-MH-99999",
            notes="Physical boundary stones verified on site."
        )
        api_mod.verify_review_gate(review_id, "G0", verify_payload)

        # Add structured issue on G2
        issue_payload = api_mod.CreateIssuePayload(
            gateCode=GateCode.G2,
            severity=IssueSeverity.WARNING,
            category="Structural",
            description="Check column alignment on grid line B.",
            requiredAction="Provide rebar detail."
        )
        api_mod.create_review_issue(review_id, issue_payload)

        # Record decision
        decision_payload = api_mod.ReviewDecisionPayload(
            decision=ReviewDecisionType.APPROVE_STAGE,
            reason="Preliminary verification passed with non-blocking notes.",
            reviewerId="ENG-MH-99999"
        )
        api_mod.record_review_decision(review_id, decision_payload)

        # Step B: SIMULATE PROCESS RESTART
        # Clear all in-memory caches completely
        api_mod.RELEASES_DB._session_cache.clear()
        api_mod.ENGINEER_REVIEWS_DB._session_cache.clear()
        api_mod.BUILD_REQUESTS_MAP._session_cache.clear()
        api_mod.ENGINEER_REVIEWS_BY_RELEASE._session_cache.clear()

        # Step C: Re-fetch review from newly initialized process state
        restarted_review = api_mod.get_engineer_review(review_id)
        self.assertIsNotNone(restarted_review)
        self.assertEqual(restarted_review["id"], review_id)
        self.assertEqual(restarted_review["status"], ReviewStatus.APPROVED.value)
        self.assertEqual(restarted_review["declaredPlotAreaSqFt"], 1100.0)

        # Verify gates after restart
        gates = api_mod.get_engineer_review_gates(review_id)
        self.assertEqual(len(gates), 7)
        g0 = next(g for g in gates if g["gateCode"] == "G0")
        self.assertEqual(g0["status"], GateStatus.VERIFIED.value)
        self.assertEqual(g0["reviewedBy"], "ENG-MH-99999")
        self.assertIn("Physical boundary stones", g0["notes"])

        # Verify issues after restart
        issues = api_mod.get_engineer_review_issues(review_id)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["category"], "Structural")
        self.assertEqual(issues[0]["severity"], IssueSeverity.WARNING.value)

        # Verify decisions after restart
        self.assertEqual(len(restarted_review["decisions"]), 1)
        self.assertEqual(restarted_review["decisions"][0]["decision"], ReviewDecisionType.APPROVE_STAGE.value)
        self.assertEqual(restarted_review["decisions"][0]["decidedBy"], "ENG-MH-99999")

        # Verify release handoff package after restart
        pkg = api_mod.get_handoff_package(self.test_release_id)
        self.assertIsNotNone(pkg)
        self.assertEqual(pkg["releaseId"], self.test_release_id)

    # 3. Release Immutability & Deterministic Fingerprint
    def test_03_release_immutability_and_fingerprint_determinism(self):
        # A: Deterministic fingerprint
        fp1 = generate_release_fingerprint(
            geometry_hash="sha256:geo_hash_real_1100",
            regulation_hash="sha256:dcpr_2034_mumbai",
            customer_brief_hash="sha256:brief_std",
            design_hash=self.test_design_hash,
            boq_hash="sha256:boq_hash_std",
            schedule_hash="sha256:sch_hash_std"
        )
        fp2 = generate_release_fingerprint(
            geometry_hash="sha256:geo_hash_real_1100",
            regulation_hash="sha256:dcpr_2034_mumbai",
            customer_brief_hash="sha256:brief_std",
            design_hash=self.test_design_hash,
            boq_hash="sha256:boq_hash_std",
            schedule_hash="sha256:sch_hash_std"
        )
        self.assertEqual(fp1, fp2, "Fingerprint must be deterministic for identical inputs")

        # Altering design hash changes fingerprint
        fp3 = generate_release_fingerprint(
            geometry_hash="sha256:geo_hash_real_1100",
            regulation_hash="sha256:dcpr_2034_mumbai",
            customer_brief_hash="sha256:brief_std",
            design_hash="sha256:different_design_hash",
            boq_hash="sha256:boq_hash_std",
            schedule_hash="sha256:sch_hash_std"
        )
        self.assertNotEqual(fp1, fp3, "Fingerprint must change when design changes")

        # B: Release Immutability Enforcement
        # Attempt to mutate design version or fingerprint of an already frozen release
        mutated_release = dict(self.release_data)
        mutated_release["fingerprint"] = "sha256:tampered_fingerprint"
        with self.assertRaises(ReleaseImmutabilityError):
            ledger_repo.save_release(mutated_release, enforce_immutability=True)

        mutated_dv_release = dict(self.release_data)
        mutated_dv_release["designVersionId"] = "DV-TAMPERED-NEW"
        with self.assertRaises(ReleaseImmutabilityError):
            ledger_repo.save_release(mutated_dv_release, enforce_immutability=True)

    # 4. Fail-Closed Behavior (Database Unavailable Returns Controlled Error)
    def test_04_database_unavailable_returns_controlled_error(self):
        orig_url = os.environ.get("DATABASE_URL")
        try:
            # Set unreachable database URL (non-existent port)
            os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:59999/non_existent_db"

            # Fresh stores simulating broken DB connection
            broken_reviews_store = ledger_repo.PersistentEngineerReviewsStore()

            # Accessing or creating must fail closed with DatabaseLedgerError
            with self.assertRaises(DatabaseLedgerError):
                _ = broken_reviews_store[self.test_release_id]

            # Verifying DB connection raises DatabaseLedgerError
            with self.assertRaises(DatabaseLedgerError):
                with ledger_repo.get_db_connection():
                    pass

        finally:
            if orig_url:
                os.environ["DATABASE_URL"] = orig_url
            else:
                os.environ.pop("DATABASE_URL", None)

    # 5. Security & Credential Privacy
    def test_05_security_no_credentials_leaked_in_exceptions(self):
        try:
            bad_dsn = "postgresql://secret_user:super_secret_password@localhost:59998/db"
            os.environ["DATABASE_URL"] = bad_dsn
            with ledger_repo.get_db_connection():
                pass
        except DatabaseLedgerError as e:
            error_msg = str(e)
            # Ensure super_secret_password is NOT in error message
            self.assertNotIn("super_secret_password", error_msg, "Raw database password must not leak in errors")
        finally:
            orig_url = "postgresql://postgres:postgres@localhost:5432/realestate_feasibility"
            os.environ["DATABASE_URL"] = orig_url


    # 6. Independent Gate Transitions Persisted
    def test_06_independent_gate_transitions_persisted(self):
        review = api_mod.create_or_get_engineer_review(self.test_build_req_id)
        review_id = review["id"]

        # Update only G2
        payload = api_mod.GateVerificationPayload(
            status=GateStatus.VERIFIED,
            reviewerId="ENG-MH-48201",
            notes="Column spans IS 456 compliant."
        )
        api_mod.verify_review_gate(review_id, "G2", payload)

        # Clear session cache to force reload from PostgreSQL
        api_mod.ENGINEER_REVIEWS_DB._session_cache.clear()

        gates = api_mod.get_engineer_review_gates(review_id)
        g2 = next(g for g in gates if g["gateCode"] == "G2")
        self.assertEqual(g2["status"], GateStatus.VERIFIED.value)
        self.assertEqual(g2["notes"], "Column spans IS 456 compliant.")

        # Ensure G0 is STILL PENDING (independent transition)
        g0 = next(g for g in gates if g["gateCode"] == "G0")
        self.assertEqual(g0["status"], GateStatus.PENDING.value)

    # 7. Anti-Bypass G5/G6 Protection Persisted
    def test_07_anti_bypass_g5_g6_protection_persisted(self):
        review = api_mod.create_or_get_engineer_review(self.test_build_req_id)
        review_id = review["id"]

        # Attempt to verify G5 while G0, G2, G3 are still PENDING -> Must be rejected HTTP 400
        payload = api_mod.GateVerificationPayload(
            status=GateStatus.VERIFIED,
            reviewerId="ENG-MH-48201",
            notes="Attempting premature authorization."
        )
        with self.assertRaises(HTTPException) as ctx:
            api_mod.verify_review_gate(review_id, "G5", payload)
        self.assertEqual(ctx.exception.status_code, 400)

        # Ensure G5 in PostgreSQL remains LOCKED
        api_mod.ENGINEER_REVIEWS_DB._session_cache.clear()
        gates = api_mod.get_engineer_review_gates(review_id)
        g5 = next(g for g in gates if g["gateCode"] == "G5")
        self.assertEqual(g5["status"], GateStatus.LOCKED.value)


if __name__ == "__main__":
    unittest.main()

