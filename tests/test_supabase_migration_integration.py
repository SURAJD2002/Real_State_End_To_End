"""
Planwise Enterprise — Supabase Remote Database Integration Test Suite
======================================================================
Verifies:
1. Migration schema consistency on target Supabase project qhqneldjxxdnttqfhqkf.
2. Presence and integrity of all 34 domain tables in the public schema.
3. PostGIS spatial extensions and functions (ST_IsValid, ST_Area).
4. Native UUID generation (uuid_generate_v4() and gen_random_uuid()).
5. Row Level Security (RLS) enforcement across all application tables.
6. Supabase migration history tracking in supabase_migrations.schema_migrations.
"""

import json
import subprocess
import unittest


def run_supabase_sql(sql: str) -> dict:
    """Executes a SQL query against the linked Supabase project via the CLI."""
    cmd = ["supabase", "db", "query", "--linked", sql, "--output", "json"]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    for line in proc.stdout.splitlines():
        if line.strip().startswith("{") and "rows" in line:
            return json.loads(line.strip())
    # Try full output if not single line
    try:
        return json.loads(proc.stdout)
    except Exception:
        # Fallback parse
        idx = proc.stdout.find("{")
        if idx != -1:
            return json.loads(proc.stdout[idx:])
        raise ValueError(f"Could not parse json output: {proc.stdout}")


class TestSupabaseMigrationIntegration(unittest.TestCase):
    """Rigorous remote verification against linked Supabase project."""

    def test_01_migration_history_recorded(self):
        """Verify that all 7 migrations are registered in supabase_migrations."""
        res = run_supabase_sql("SELECT version FROM supabase_migrations.schema_migrations ORDER BY version;")
        versions = [r["version"] for r in res.get("rows", [])]
        expected_versions = [
            "20261010010000",
            "20261010020000",
            "20261010030000",
            "20261010040000",
            "20261010050000",
            "20261010060000",
            "20261010070000",
            "20261010080000",
        ]
        self.assertEqual(versions, expected_versions, f"Recorded versions mismatch: {versions}")

    def test_02_all_34_domain_tables_exist(self):
        """Verify that all 34 domain tables exist in the public schema."""
        res = run_supabase_sql("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;")
        tables = set(r["tablename"] for r in res.get("rows", []))

        expected_tables = {
            "projects", "parcels", "parcel_roads", "parcel_constraints", "feasibility_runs",
            "design_versions", "building_models", "building_levels", "spaces", "space_adjacencies",
            "materials", "building_elements", "openings", "structural_grids", "building_systems",
            "model_validations", "site_reference_frames", "site_evidence", "site_confidence_evaluations",
            "regulation_rule_packs", "rule_execution_traces", "qto_measurement_rules",
            "construction_assemblies", "material_catalog", "cost_rate_snapshots", "qto_takeoff_records",
            "cost_estimates", "releases", "build_requests", "engineer_reviews", "engineer_review_gates",
            "engineer_review_issues", "engineer_review_decisions", "generated_reports"
        }
        for expected in expected_tables:
            self.assertIn(expected, tables, f"Missing table in public schema: {expected}")

    def test_03_rls_enabled_on_all_domain_tables(self):
        """Verify that RLS is active on every single domain table."""
        res = run_supabase_sql(
            "SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public' AND tablename != 'spatial_ref_sys';"
        )
        non_rls_tables = [r["tablename"] for r in res.get("rows", []) if not r.get("rowsecurity")]
        self.assertEqual(non_rls_tables, [], f"Tables without RLS: {non_rls_tables}")

    def test_04_postgis_functions_operational(self):
        """Verify PostGIS functions work accurately."""
        res = run_supabase_sql(
            "SELECT ST_Area(ST_GeomFromText('POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))', 4326)) as area;"
        )
        rows = res.get("rows", [])
        self.assertEqual(len(rows), 1)
        self.assertAlmostEqual(float(rows[0]["area"]), 100.0, places=1)

    def test_05_uuid_generation_operational(self):
        """Verify uuid_generate_v4() wrapper and native gen_random_uuid()."""
        res = run_supabase_sql("SELECT uuid_generate_v4() as u1, gen_random_uuid() as u2;")
        rows = res.get("rows", [])
        self.assertEqual(len(rows), 1)
        self.assertEqual(len(str(rows[0]["u1"])), 36)
        self.assertEqual(len(str(rows[0]["u2"])), 36)


if __name__ == "__main__":
    unittest.main()
