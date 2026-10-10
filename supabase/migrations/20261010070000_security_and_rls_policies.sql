-- ============================================================================
-- Planwise Enterprise — Migration 07: Comprehensive RLS & Tenant Isolation
-- Phase 7 Security Hardening & Zero-Trust Access Control
-- ============================================================================

-- 1. Helper function for tenant resolution from JWT claims
CREATE OR REPLACE FUNCTION current_user_org_id()
RETURNS UUID AS $$
BEGIN
    RETURN NULLIF(current_setting('request.jwt.claims', true)::jsonb->>'org_id', '')::uuid;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql STABLE;

-- 2. Helper function to check if current connection is administrative/service role
CREATE OR REPLACE FUNCTION is_admin_or_service()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN (
        current_user IN ('postgres', 'supabase_admin') OR
        current_setting('request.jwt.claims', true)::jsonb->>'role' = 'service_role' OR
        current_setting('role', true) = 'service_role'
    );
EXCEPTION
    WHEN OTHERS THEN
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- 3. Enable Row Level Security (RLS) on all 34 Domain Tables
-- ============================================================================

-- Phase 1 Domain Tables
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE parcels ENABLE ROW LEVEL SECURITY;
ALTER TABLE parcel_roads ENABLE ROW LEVEL SECURITY;
ALTER TABLE parcel_constraints ENABLE ROW LEVEL SECURITY;
ALTER TABLE feasibility_runs ENABLE ROW LEVEL SECURITY;

-- Phase 2 Canonical Building Model Tables
ALTER TABLE design_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE building_models ENABLE ROW LEVEL SECURITY;
ALTER TABLE building_levels ENABLE ROW LEVEL SECURITY;
ALTER TABLE spaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE space_adjacencies ENABLE ROW LEVEL SECURITY;
ALTER TABLE materials ENABLE ROW LEVEL SECURITY;
ALTER TABLE building_elements ENABLE ROW LEVEL SECURITY;
ALTER TABLE openings ENABLE ROW LEVEL SECURITY;
ALTER TABLE structural_grids ENABLE ROW LEVEL SECURITY;
ALTER TABLE building_systems ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_validations ENABLE ROW LEVEL SECURITY;

-- Phase 3 Site Evidence & Statutory Engine Tables
ALTER TABLE site_reference_frames ENABLE ROW LEVEL SECURITY;
ALTER TABLE site_evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE site_confidence_evaluations ENABLE ROW LEVEL SECURITY;
ALTER TABLE regulation_rule_packs ENABLE ROW LEVEL SECURITY;
ALTER TABLE rule_execution_traces ENABLE ROW LEVEL SECURITY;

-- Phase 4 QTO, BOQ & Cost Engine Tables
ALTER TABLE qto_measurement_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE construction_assemblies ENABLE ROW LEVEL SECURITY;
ALTER TABLE material_catalog ENABLE ROW LEVEL SECURITY;
ALTER TABLE cost_rate_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE qto_takeoff_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE cost_estimates ENABLE ROW LEVEL SECURITY;

-- Phase 5 Engineer Review & Releases Ledger Tables
ALTER TABLE releases ENABLE ROW LEVEL SECURITY;
ALTER TABLE build_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE engineer_reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE engineer_review_gates ENABLE ROW LEVEL SECURITY;
ALTER TABLE engineer_review_issues ENABLE ROW LEVEL SECURITY;
ALTER TABLE engineer_review_decisions ENABLE ROW LEVEL SECURITY;

-- Phase 6 Generated Reports Ledger Table
ALTER TABLE generated_reports ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- 4. Full Administrative / Service-Role Policies (Fail-safe for backend services)
-- ============================================================================

DO $$
DECLARE
    tbl TEXT;
    all_tables TEXT[] := ARRAY[
        'projects', 'parcels', 'parcel_roads', 'parcel_constraints', 'feasibility_runs',
        'design_versions', 'building_models', 'building_levels', 'spaces', 'space_adjacencies',
        'materials', 'building_elements', 'openings', 'structural_grids', 'building_systems',
        'model_validations', 'site_reference_frames', 'site_evidence', 'site_confidence_evaluations',
        'regulation_rule_packs', 'rule_execution_traces', 'qto_measurement_rules',
        'construction_assemblies', 'material_catalog', 'cost_rate_snapshots', 'qto_takeoff_records',
        'cost_estimates', 'releases', 'build_requests', 'engineer_reviews', 'engineer_review_gates',
        'engineer_review_issues', 'engineer_review_decisions', 'generated_reports'
    ];
BEGIN
    FOREACH tbl IN ARRAY all_tables LOOP
        EXECUTE format('
            DROP POLICY IF EXISTS %I ON %I;
            CREATE POLICY %I ON %I
                FOR ALL
                TO authenticated, service_role, postgres
                USING (is_admin_or_service())
                WITH CHECK (is_admin_or_service());
        ', 'admin_full_access_' || tbl, tbl, 'admin_full_access_' || tbl, tbl);
    END LOOP;
END $$;

-- ============================================================================
-- 5. Read-Only Public Catalog Policies (Statutory Packs, Standard Materials, QTO Rules)
-- ============================================================================

CREATE POLICY "public_read_materials" ON materials
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "public_read_regulation_rule_packs" ON regulation_rule_packs
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "public_read_qto_measurement_rules" ON qto_measurement_rules
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "public_read_construction_assemblies" ON construction_assemblies
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "public_read_material_catalog" ON material_catalog
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "public_read_cost_rate_snapshots" ON cost_rate_snapshots
    FOR SELECT TO authenticated USING (true);

-- ============================================================================
-- 6. Tenant-Isolated Organization Policies (When JWT Contains org_id)
-- ============================================================================

-- Projects tenant policy
CREATE POLICY "tenant_projects_select" ON projects
    FOR SELECT TO authenticated
    USING (organization_id = current_user_org_id());

CREATE POLICY "tenant_projects_insert" ON projects
    FOR INSERT TO authenticated
    WITH CHECK (organization_id = current_user_org_id());

CREATE POLICY "tenant_projects_update" ON projects
    FOR UPDATE TO authenticated
    USING (organization_id = current_user_org_id())
    WITH CHECK (organization_id = current_user_org_id());

-- Parcels tenant policy (Inherited via project_id)
CREATE POLICY "tenant_parcels_select" ON parcels
    FOR SELECT TO authenticated
    USING (EXISTS (SELECT 1 FROM projects WHERE projects.id = parcels.project_id AND projects.organization_id = current_user_org_id()));

CREATE POLICY "tenant_parcels_insert" ON parcels
    FOR INSERT TO authenticated
    WITH CHECK (EXISTS (SELECT 1 FROM projects WHERE projects.id = parcels.project_id AND projects.organization_id = current_user_org_id()));

-- Feasibility Runs tenant policy
CREATE POLICY "tenant_feasibility_runs_select" ON feasibility_runs
    FOR SELECT TO authenticated
    USING (EXISTS (SELECT 1 FROM projects WHERE projects.id = feasibility_runs.project_id AND projects.organization_id = current_user_org_id()));

-- Generated Reports tenant policy
CREATE POLICY "tenant_generated_reports_select" ON generated_reports
    FOR SELECT TO authenticated
    USING (EXISTS (SELECT 1 FROM projects WHERE projects.id = (generated_reports.project_id)::uuid AND projects.organization_id = current_user_org_id()));
