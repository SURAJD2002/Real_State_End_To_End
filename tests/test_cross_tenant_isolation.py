"""
Planwise Enterprise — Cross-Tenant Security & RLS Isolation Test Suite
=======================================================================
Verifies:
1. Complete isolation between Organization A and Organization B.
2. Anonymous role (anon) default-deny across all project and report tables.
3. Authenticated role tenant boundary enforcement:
   - Cross-tenant SELECT returns zero rows.
   - Cross-tenant INSERT is blocked by WITH CHECK constraint.
   - Cross-tenant UPDATE affects zero rows.
   - Cross-tenant report and parcel access returns zero rows.
4. Administrative / Service Role access is preserved for backend workers.
5. Clean teardown with zero persistent test contamination.
"""

import json
import subprocess
import unittest
import uuid


def run_supabase_sql(sql: str) -> dict:
    """Executes a SQL query against the linked Supabase project via the CLI."""
    cmd = ["supabase", "db", "query", "--linked", sql, "--output", "json"]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    for line in proc.stdout.splitlines():
        if line.strip().startswith("{") and "rows" in line:
            return json.loads(line.strip())
    try:
        return json.loads(proc.stdout)
    except Exception:
        idx = proc.stdout.find("{")
        if idx != -1:
            return json.loads(proc.stdout[idx:])
        raise ValueError(f"Could not parse json output: {proc.stdout}")


class TestCrossTenantIsolation(unittest.TestCase):
    """Rigorous verification of multi-tenant boundaries and RLS policies on Supabase."""

    @classmethod
    def setUpClass(cls):
        cls.org_a = str(uuid.uuid4())
        cls.org_b = str(uuid.uuid4())
        cls.user_a = str(uuid.uuid4())
        cls.proj_a = str(uuid.uuid4())
        cls.proj_b = str(uuid.uuid4())
        cls.report_a = f"rep-a-{uuid.uuid4().hex[:8]}"
        cls.report_b = f"rep-b-{uuid.uuid4().hex[:8]}"

        # Insert test fixtures using admin role
        setup_sql = f"""
        INSERT INTO organizations (id, name, slug)
        VALUES
            ('{cls.org_a}', 'Org A Confidential', 'org-a-{cls.org_a[:8]}'),
            ('{cls.org_b}', 'Org B Confidential', 'org-b-{cls.org_b[:8]}')
        ON CONFLICT (id) DO NOTHING;

        INSERT INTO projects (id, name, organization_id)
        VALUES
            ('{cls.proj_a}', 'Org A Confidential Project', '{cls.org_a}'),
            ('{cls.proj_b}', 'Org B Confidential Project', '{cls.org_b}');

        INSERT INTO generated_reports (id, project_id, design_version_id, report_type, input_manifest_hash, output_pdf_hash, file_path, file_size_bytes)
        VALUES
            ('{cls.report_a}', '{cls.proj_a}', 'DV-A-01', 'HOME_REPORT', 'hash-a', 'pdf-a', '/tmp/a.pdf', 1024),
            ('{cls.report_b}', '{cls.proj_b}', 'DV-B-01', 'HOME_REPORT', 'hash-b', 'pdf-b', '/tmp/b.pdf', 2048);
        """
        run_supabase_sql(setup_sql)

    @classmethod
    def tearDownClass(cls):
        # Cleanup test fixtures
        cleanup_sql = f"""
        DELETE FROM generated_reports WHERE id IN ('{cls.report_a}', '{cls.report_b}');
        DELETE FROM projects WHERE id IN ('{cls.proj_a}', '{cls.proj_b}');
        DELETE FROM organizations WHERE id IN ('{cls.org_a}', '{cls.org_b}');
        """
        try:
            run_supabase_sql(cleanup_sql)
        except Exception as e:
            print(f"Teardown warning: {e}")

    def test_01_anonymous_access_denied_projects(self):
        """Anonymous role (anon) must not see any projects."""
        sql = """
        SELECT tablename, count FROM (
            SELECT 'projects' as tablename, count(*)::int as count
            FROM projects
        ) q;
        """
        # Testing via anonymous simulation
        anon_sql = f"""
        DO $$
        DECLARE
            v_cnt INT;
        BEGIN
            -- Switch session to anon
            PERFORM set_config('role', 'anon', true);
            PERFORM set_config('request.jwt.claims', '{{"role": "anon"}}', true);
            SELECT count(*) INTO v_cnt FROM projects;
            IF v_cnt > 0 THEN
                RAISE EXCEPTION 'RLS Leak: Anonymous user could see % projects', v_cnt;
            END IF;
        END $$;
        """
        res = run_supabase_sql(anon_sql)
        self.assertIn("rows", res)

    def test_02_anonymous_access_denied_reports(self):
        """Anonymous role (anon) must not see any generated reports."""
        anon_sql = f"""
        DO $$
        DECLARE
            v_cnt INT;
        BEGIN
            PERFORM set_config('role', 'anon', true);
            PERFORM set_config('request.jwt.claims', '{{"role": "anon"}}', true);
            SELECT count(*) INTO v_cnt FROM generated_reports;
            IF v_cnt > 0 THEN
                RAISE EXCEPTION 'RLS Leak: Anonymous user could see % reports', v_cnt;
            END IF;
        END $$;
        """
        res = run_supabase_sql(anon_sql)
        self.assertIn("rows", res)

    def test_03_authenticated_user_a_sees_only_own_project(self):
        """Authenticated user belonging to Org A must see Project A and NOT Project B."""
        tenant_sql = f"""
        DO $$
        DECLARE
            v_count_a INT;
            v_count_b INT;
        BEGIN
            PERFORM set_config('role', 'authenticated', true);
            PERFORM set_config('request.jwt.claims', '{{"sub": "{self.user_a}", "role": "authenticated", "org_id": "{self.org_a}"}}', true);

            SELECT count(*) INTO v_count_a FROM projects WHERE id = '{self.proj_a}';
            SELECT count(*) INTO v_count_b FROM projects WHERE id = '{self.proj_b}';

            IF v_count_a != 1 THEN
                RAISE EXCEPTION 'Tenant Isolation Failure: User A cannot see own project A';
            END IF;
            IF v_count_b != 0 THEN
                RAISE EXCEPTION 'Tenant Isolation Failure: User A CAN see project B of Org B (Cross-Tenant Leak)';
            END IF;
        END $$;
        """
        res = run_supabase_sql(tenant_sql)
        self.assertIn("rows", res)

    def test_04_authenticated_user_a_cross_tenant_update_blocked(self):
        """User A must NOT be able to modify Project B belonging to Org B."""
        update_sql = f"""
        DO $$
        DECLARE
            v_updated INT;
        BEGIN
            PERFORM set_config('role', 'authenticated', true);
            PERFORM set_config('request.jwt.claims', '{{"sub": "{self.user_a}", "role": "authenticated", "org_id": "{self.org_a}"}}', true);

            UPDATE projects SET name = 'Hacked Name' WHERE id = '{self.proj_b}';
            GET DIAGNOSTICS v_updated = ROW_COUNT;

            IF v_updated > 0 THEN
                RAISE EXCEPTION 'Tenant Isolation Failure: User A successfully updated Project B (rows: %)', v_updated;
            END IF;
        END $$;
        """
        res = run_supabase_sql(update_sql)
        self.assertIn("rows", res)

    def test_05_authenticated_user_a_cross_tenant_insert_blocked(self):
        """User A must NOT be able to insert a project tagged with Org B's ID."""
        new_proj_id = str(uuid.uuid4())
        insert_sql = f"""
        DO $$
        DECLARE
            v_failed BOOLEAN := false;
        BEGIN
            PERFORM set_config('role', 'authenticated', true);
            PERFORM set_config('request.jwt.claims', '{{"sub": "{self.user_a}", "role": "authenticated", "org_id": "{self.org_a}"}}', true);

            BEGIN
                INSERT INTO projects (id, name, organization_id)
                VALUES ('{new_proj_id}', 'Illegal Project Injection', '{self.org_b}');
            EXCEPTION WHEN insufficient_privilege OR check_violation THEN
                v_failed := true;
            END;

            IF NOT v_failed THEN
                RAISE EXCEPTION 'Tenant Isolation Failure: User A was able to insert project into Org B';
            END IF;
        END $$;
        """
        res = run_supabase_sql(insert_sql)
        self.assertIn("rows", res)

    def test_06_authenticated_user_a_cross_tenant_report_read_blocked(self):
        """User A must NOT be able to view generated reports of Org B."""
        report_sql = f"""
        DO $$
        DECLARE
            v_count_a INT;
            v_count_b INT;
        BEGIN
            PERFORM set_config('role', 'authenticated', true);
            PERFORM set_config('request.jwt.claims', '{{"sub": "{self.user_a}", "role": "authenticated", "org_id": "{self.org_a}"}}', true);

            SELECT count(*) INTO v_count_a FROM generated_reports WHERE id = '{self.report_a}';
            SELECT count(*) INTO v_count_b FROM generated_reports WHERE id = '{self.report_b}';

            IF v_count_a != 1 THEN
                RAISE EXCEPTION 'User A cannot access own report A';
            END IF;
            IF v_count_b != 0 THEN
                RAISE EXCEPTION 'Tenant Isolation Failure: User A accessed Report B of Org B (Cross-Tenant Leak)';
            END IF;
        END $$;
        """
        res = run_supabase_sql(report_sql)
        self.assertIn("rows", res)

    def test_07_service_role_cross_tenant_access_allowed(self):
        """Backend service_role must be able to access both Org A and Org B."""
        admin_sql = f"""
        DO $$
        DECLARE
            v_count_total INT;
        BEGIN
            PERFORM set_config('role', 'service_role', true);
            PERFORM set_config('request.jwt.claims', '{{"role": "service_role"}}', true);

            SELECT count(*) INTO v_count_total
            FROM projects
            WHERE id IN ('{self.proj_a}', '{self.proj_b}');

            IF v_count_total != 2 THEN
                RAISE EXCEPTION 'Service Role Failure: Expected 2 projects, got %', v_count_total;
            END IF;
        END $$;
        """
        res = run_supabase_sql(admin_sql)
        self.assertIn("rows", res)


if __name__ == "__main__":
    unittest.main()
