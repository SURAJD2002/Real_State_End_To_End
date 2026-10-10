# Planwise Enterprise — Supabase Security & RLS Audit

## Executive Summary
This document provides an in-depth security and access control audit of the Planwise Enterprise database architecture on Supabase project `qhqneldjxxdnttqfhqkf`. It outlines the Row Level Security (RLS) enforcement model, tenant isolation strategy, role access matrices, and identified prerequisites.

---

## 1. Table Classification & Tenant Ownership

The database comprises 34 relational tables divided into three distinct security categories:

### A. Customer & Project Domain Tables (Tenant-Isolated)
These tables hold sensitive project, geometry, design, review, and financial data belonging to specific client organizations:
- `projects` (Contains `organization_id UUID`)
- `parcels` (Linked via `project_id`)
- `parcel_roads` (Linked via `parcel_id`)
- `parcel_constraints` (Linked via `parcel_id`)
- `feasibility_runs` (Linked via `project_id`)
- `design_versions` (Linked via `project_id`)
- `building_models` (Linked via `design_version_id`)
- `building_levels` (Linked via `building_model_id`)
- `spaces` (Linked via `building_model_id`)
- `space_adjacencies` (Linked via `space_id`)
- `building_elements` (Linked via `building_model_id`)
- `openings` (Linked via `building_model_id`)
- `structural_grids` (Linked via `building_model_id`)
- `building_systems` (Linked via `building_model_id`)
- `model_validations` (Linked via `building_model_id`)
- `site_reference_frames` (Linked via `project_id`)
- `site_evidence` (Linked via `project_id`)
- `site_confidence_evaluations` (Linked via `project_id`)
- `rule_execution_traces` (Linked via `project_id`)
- `qto_takeoff_records` (Linked via `project_id`)
- `cost_estimates` (Linked via `project_id`)
- `releases` (Linked via `project_id`)
- `build_requests` (Linked via `release_id`)
- `engineer_reviews` (Linked via `project_id`)
- `engineer_review_gates` (Linked via `engineer_review_id`)
- `engineer_review_issues` (Linked via `engineer_review_id`)
- `engineer_review_decisions` (Linked via `engineer_review_id`)
- `generated_reports` (Linked via `project_id`)

### B. Shared Statutory & Reference Catalogs (Read-Only for Authenticated Users)
These tables store standardized building codes, rate schedules, and material definitions:
- `materials` (Standard construction material properties)
- `regulation_rule_packs` (Immutable statutory building regulations like DCPR 2034)
- `qto_measurement_rules` (IS 1200 / SMM7 measurement standards)
- `construction_assemblies` (Standard assembly definitions)
- `material_catalog` (Material master catalog)
- `cost_rate_snapshots` (Immutable market rate benchmarks)

### C. System & Migration Tables (Platform Internal)
- `supabase_migrations.schema_migrations` (Managed exclusively by Supabase CLI)

---

## 2. Row Level Security (RLS) Policy Design

### Default Deny Posture
All 34 application tables have RLS explicitly enabled:
```sql
ALTER TABLE <table_name> ENABLE ROW LEVEL SECURITY;
```
By default in PostgreSQL, when RLS is enabled and no policies permit access, all operations from non-superusers/non-bypass roles evaluate to `false` (fail-closed).

### Administrative & Service-Role Policy
The Planwise Enterprise backend services (FastAPI API Gateway, Celery workers) connect using either PostgreSQL superuser credentials or Supabase `service_role`. To guarantee uninterrupted server-side operation while blocking browser-level bypass:
```sql
CREATE POLICY admin_full_access_<table_name> ON <table_name>
    FOR ALL
    TO authenticated, service_role, postgres
    USING (is_admin_or_service())
    WITH CHECK (is_admin_or_service());
```
Where `is_admin_or_service()` validates:
1. `current_user IN ('postgres', 'supabase_admin')`, OR
2. JWT claim `role = 'service_role'`, OR
3. Session setting `role = 'service_role'`.

### Shared Catalog Read Access
Authenticated users are granted read access to reference data:
```sql
CREATE POLICY "public_read_<catalog>" ON <catalog>
    FOR SELECT TO authenticated USING (true);
```
Mutations (`INSERT`, `UPDATE`, `DELETE`) are strictly forbidden to standard users and require administrative role.

### Multi-Tenant Isolation Policies
For tenant-owned resources, access is governed by the user's organization claim:
```sql
CREATE POLICY "tenant_projects_select" ON projects
    FOR SELECT TO authenticated
    USING (organization_id = current_user_org_id());
```

---

## 3. Security Findings & Prerequisites

> [!IMPORTANT]
> **Tenant Membership Prerequisite**:
> The `projects` table defines an `organization_id UUID` column. However, the current repository does not yet define an `organization_memberships` table in PostgreSQL linking Supabase `auth.users (id)` to `organizations (id)`.
>
> Therefore:
> 1. Complete tenant isolation is presently enforced via server-side API Gateway authorization logic and JWT `org_id` claim extraction.
> 2. Direct browser-to-Supabase PostgREST access should remain disabled or restricted until a dedicated `organization_memberships` table and mapping trigger are implemented in a future milestone.
> 3. Anonymous (`anon`) role access is completely denied across all application tables.

---

## 4. Credential & Secret Management Verification
- No database passwords, JWT secrets, or service-role keys are hardcoded in source code or committed to git.
- The root `.gitignore` and `supabase/.gitignore` properly exclude `.env`, `.temp`, and credential dumps.
