# Volume VI — Database, Persistence, and Data Lineage

## 1. Database Architecture & Migration Topology
The persistent storage layer is built on **PostgreSQL 16** with relational tables, foreign key constraints, and JSONB document columns.


<div class="diagram-container">
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 275" width="100%" height="275px" class="svg-diagram" style="max-height:275px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;">
<defs>
  <marker id="arr" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
    <path d="M0,0 L6,3 L0,6 Z" fill="#2563eb" />
  </marker>
  <marker id="arr-gray" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
    <path d="M0,0 L6,3 L0,6 Z" fill="#64748b" />
  </marker>
</defs>

<text x="350" y="24" text-anchor="middle" font-size="13" font-weight="bold" fill="#0f172a">DIAGRAM 7: DEPENDENCY DAG & REACTIVE CACHE INVALIDATION PIPELINE</text>
<rect x="260" y="45" width="180" height="35" rx="3" fill="#2563eb"/>
<text x="350" y="67" text-anchor="middle" font-size="9.5" font-weight="bold" fill="#ffffff">PARCEL / BRIEF MUTATION</text>

<!-- Invalidation Arrows -->
<line x1="350" y1="80" x2="160" y2="105" stroke="#ef4444" stroke-width="1.2" marker-end="url(#arr)"/>
<line x1="350" y1="80" x2="350" y2="105" stroke="#ef4444" stroke-width="1.2" marker-end="url(#arr)"/>
<line x1="350" y1="80" x2="540" y2="105" stroke="#ef4444" stroke-width="1.2" marker-end="url(#arr)"/>

<rect x="90" y="105" width="140" height="35" rx="3" fill="#fee2e2" stroke="#ef4444"/>
<text x="160" y="127" text-anchor="middle" font-size="8.5" font-weight="bold" fill="#991b1b">FEASIBILITY [INVALID]</text>

<rect x="280" y="105" width="140" height="35" rx="3" fill="#fee2e2" stroke="#ef4444"/>
<text x="350" y="127" text-anchor="middle" font-size="8.5" font-weight="bold" fill="#991b1b">CBM MODEL [INVALID]</text>

<rect x="470" y="105" width="140" height="35" rx="3" fill="#fee2e2" stroke="#ef4444"/>
<text x="540" y="127" text-anchor="middle" font-size="8.5" font-weight="bold" fill="#991b1b">QTO TAKEOFF [INVALID]</text>

<line x1="540" y1="140" x2="540" y2="165" stroke="#ef4444" stroke-width="1.2" marker-end="url(#arr)"/>

<rect x="470" y="165" width="140" height="35" rx="3" fill="#fee2e2" stroke="#ef4444"/>
<text x="540" y="187" text-anchor="middle" font-size="8.5" font-weight="bold" fill="#991b1b">BOQ & COST [INVALID]</text>

<line x1="540" y1="200" x2="540" y2="225" stroke="#ef4444" stroke-width="1.2" marker-end="url(#arr)"/>

<rect x="470" y="225" width="140" height="35" rx="3" fill="#fee2e2" stroke="#ef4444"/>
<text x="540" y="247" text-anchor="middle" font-size="8.5" font-weight="bold" fill="#991b1b">RELEASE / IFC [STALE]</text>

<rect x="40" y="170" width="380" height="85" rx="3" fill="#f8fafc" stroke="#cbd5e1"/>
<text x="50" y="188" font-size="8.5" font-weight="bold" fill="#0f172a">DAG Invalidation Invariants (workers/qto/change_propagation.py):</text>
<text x="50" y="204" font-size="7.5" fill="#334155">• When Room Dimension changes: invalidates parent Space bounds and adjoining Walls</text>
<text x="50" y="218" font-size="7.5" fill="#334155">• Invalidation cascades to: QTO TakeoffRecords → BOQ LineItems → CostWaterfall</text>
<text x="50" y="232" font-size="7.5" fill="#334155">• If a Release was locked: release_fingerprint mismatch triggers 409 Conflict rejection</text>
<text x="50" y="246" font-size="7.5" fill="#334155">• Fail-closed safety: No stale cost estimate can ever be certified for construction handoff</text>

</svg>
  <div class="diagram-caption">Diagram 7: Change Propagation DAG and Dependency Cascade</div>
</div>


The repository contains **14 SQL migration files** across two directories:
1. `supabase/migrations/` (8 Active Migrations):
   - `20261010010000_initial_schema.sql` — Core tables (`organizations`, `users`, `projects`, `plots`).
   - `20261010020000_statutory_and_feasibility.sql` — Feasibility records and statutory rule packs.
   - `20261010030000_cbm_and_designs.sql` — Canonical Building Model storage (`designs`, `floors`, `rooms`).
   - `20261010040000_qto_and_cost.sql` — Bill of quantities and itemized rate catalogs.
   - `20261010050000_engineer_review_and_releases.sql` — Engineering review gates and release ledger.
   - `20261010060000_audit_logs.sql` — Immutable event audit logging.
   - `20261010070000_security_and_rls_policies.sql` — Enables RLS on 34 tables and declares access policies.
   - `20261010080000_organization_membership_mapping.sql` — Multi-tenant organization member relations.
2. `database/migrations/` (6 Legacy Migrations):
   - Mirror migrations `01` through `06` used for standalone PostgreSQL container deployments without Supabase extensions.

---

## 2. Inventory of Tables and Row-Level Security Enablement
All 34 application tables have `ALTER TABLE ... ENABLE ROW LEVEL SECURITY;` executed in migration `07`:

| Table Name | Primary Key | Foreign Keys | RLS Enabled | Core Purpose |
| :--- | :--- | :--- | :---: | :--- |
| `organizations` | `id (UUID)` | None | Yes | Multi-tenant organization boundaries |
| `users` | `id (UUID)` | `organizations(id)` | Yes | User identity, credentials, and enterprise roles |
| `organization_members`| `id (UUID)`| `org_id`, `user_id` | Yes | Organization membership mapping |
| `projects` | `id (UUID)` | `org_id`, `user_id` | Yes | Top-level project entity and plot reference |
| `plots` | `id (UUID)` | `projects(id)` | Yes | Boundary coordinates, road width, jurisdiction |
| `feasibility_reports` | `id (UUID)` | `plots(id)` | Yes | Setback envelopes, permissible FSI, coverage |
| `designs` | `id (UUID)` | `projects(id)` | Yes | Canonical Building Model JSON and metadata |
| `floors` | `id (UUID)` | `designs(id)` | Yes | Floor level definitions and elevation heights |
| `rooms` | `id (UUID)` | `floors(id)` | Yes | Room dimensions, usage types, boundary vectors |
| `wall_segments` | `id (UUID)` | `floors(id)` | Yes | Centerline wall coordinates, thickness, materials |
| `openings` | `id (UUID)` | `wall_segments(id)` | Yes | Doors and windows dimensions and schedules |
| `boq_records` | `id (UUID)` | `designs(id)` | Yes | Itemized IS 1200 quantity takeoffs |
| `cost_estimates` | `id (UUID)` | `boq_records(id)` | Yes | Rate catalogs, markups, and cost waterfall |
| `engineer_reviews` | `id (UUID)` | `projects(id)` | Yes | G0–G6 sign-off status, comments, timestamps |
| `releases` | `id (UUID)` | `projects(id)` | Yes | Immutable release ledger and manifest hashes |
| `audit_logs` | `id (UUID)` | `organizations(id)` | Yes | Append-only event ledger |

---

## 3. Complete DDL Specification of Active Supabase SQL Migrations

### Migration File: `20261010010000_init_postgis_schema.sql`
```sql
-- PostGIS & Extensions Initialization
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "btree_gist";

-- Compatibility wrapper for UUID v4 generation across all PostgreSQL / Supabase environments
CREATE OR REPLACE FUNCTION uuid_generate_v4()
RETURNS uuid AS $$
    SELECT gen_random_uuid();
$$ LANGUAGE sql;

-- Custom Domain Enums
DO $$ BEGIN
    CREATE TYPE land_tenure_type AS ENUM (
        'PRIVATE_FREEHOLD',
        'COLLECTOR_CLASS_2',
        'COLLECTOR_LEASEHOLD',
        'GOVERNMENT_LEASEHOLD',
        'MHADA_REDEVELOPMENT',
        'MUNICIPAL_ALLOTMENT'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE constraint_severity_type AS ENUM (
        'HARD_ABSOLUTE_EXCLUSION',
        'CONDITIONAL_NOC_REQUIRED',
        'HEIGHT_RESTRICTION_SURFACE',
        'SETBACK_OFFSET_MODIFIER'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE project_status_type AS ENUM (
        'DRAFT',
        'FEASIBILITY_RUNNING',
        'COMPLETED',
        'ARCHIVED'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE unit_typology_type AS ENUM (
        'STUDIO',
        '1BHK',
        '2BHK',
        '3BHK',
        '4BHK',
        'RETAIL',
        'OFFICE'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- 1. Projects Table
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(256) NOT NULL,
    description TEXT,
    organization_id UUID NOT NULL DEFAULT uuid_generate_v4(),
    jurisdiction VARCHAR(64) NOT NULL DEFAULT 'MUMBAI_DCPR_2034',
    status project_status_type NOT NULL DEFAULT 'DRAFT',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Parcels Table
CREATE TABLE IF NOT EXISTS parcels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    cadastral_survey_number VARCHAR(128) NOT NULL DEFAULT 'CTS-DEMO-101',
    tenure_type land_tenure_type NOT NULL DEFAULT 'PRIVATE_FREEHOLD',
    srid_projected INT NOT NULL DEFAULT 32643, -- UTM Zone 43N (Mumbai)
    boundary_wgs84 GEOMETRY(Polygon, 4326) NOT NULL,
    boundary_projected GEOMETRY(Polygon, 32643),
    gross_area_sqm NUMERIC(14, 4),
    version INT NOT NULL DEFAULT 1,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NO
-- [truncated for display] ...
```

### Migration File: `20261010020000_canonical_building_model.sql`
```sql
-- Planwise Enterprise — Canonical Building Model Relational Schema
-- Migration 02: Canonical Building Model & Authoritative Projections
-- Delta Specification §2, §3, §4, §5, §6, §7, §8, §9, §11, §12, §13, §14, §15, §16, §18, §19, §20, §39

-- 1. Custom Domain Enums for Canonical Model
DO $$ BEGIN
    CREATE TYPE design_version_status_type AS ENUM (
        'DRAFT',
        'GENERATED',
        'VALIDATING',
        'VALID',
        'SELECTED',
        'BUILD_REQUESTED',
        'RELEASED',
        'SUPERSEDED'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE building_element_type AS ENUM (
        'WALL',
        'COLUMN',
        'BEAM',
        'SLAB',
        'STAIR',
        'ROOF',
        'FOUNDATION',
        'PARAPET'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE opening_type AS ENUM (
        'DOOR',
        'WINDOW',
        'OPENING_VOID'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE space_zone_type AS ENUM (
        'PUBLIC',
        'PRIVATE',
        'SERVICE',
        'CIRCULATION',
        'SEMI_OUTDOOR',
        'OUTDOOR'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- 2. Design Versions Table (§5)
CREATE TABLE IF NOT EXISTS design_versions (
    id VARCHAR(64) PRIMARY KEY, -- e.g. DV-001 or dv-hash
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    site_geometry_version_id VARCHAR(64) NOT NULL DEFAULT 'PV-001',
    regulation_version_id VARCHAR(64) NOT NULL DEFAULT 'MUMBAI_DCPR_2034_V1',
    customer_brief_version_id VARCHAR(64) DEFAULT 'BRIEF-2026-01',
    status design_version_status_type NOT NULL DEFAULT 'DRAFT',
    is_locked BOOLEAN NOT NULL DEFAULT FALSE,
    release_fingerprint VARCHAR(128),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_design_versions_project ON design_versions(project_id);

-- 3. Building Models Table (§6)
CREATE TABLE IF NOT EXISTS building_models (
    id VARCHAR(64) PRIMARY KEY, -- e.g. BLDG-COMPACT_2BHK-001
    design_version_id VARCHAR(64) NOT NULL REFERENCES design_versions(id) ON DELETE CASCADE,
    schema_version VARCHAR(16) NOT NULL DEFAULT '1.0.0',
    archetype VARCHAR(64) NOT NULL,
    name VARCHAR(256) NOT NULL,
    description TEXT,
    envelope_width_m NUMERIC(8, 2) NOT NULL,
    envelope_length_m NUMERIC(8, 2) NOT NULL,
    envelope_height_m NUMERIC(
-- [truncated for display] ...
```

### Migration File: `20261010030000_site_evidence_and_rule_engine.sql`
```sql
-- ============================================================================
-- M1 — SITE TRUTH, LOCAL ENGINEERING COORDINATE SYSTEM &
-- DETERMINISTIC STATUTORY RULE ENGINE SCHEMA
-- ============================================================================

-- 1. Custom Domain Types
DO $$ BEGIN
    CREATE TYPE site_evidence_type AS ENUM (
        'PARCEL_BOUNDARY',
        'SURVEY_PLAN',
        'SALE_DEED',
        'LAND_RECORD',
        'ROAD_EDGE',
        'ROAD_WIDTH',
        'ROAD_LEVEL',
        'SITE_LEVEL',
        'TOPOGRAPHY',
        'TREE',
        'UTILITY',
        'EASEMENT',
        'ROAD_WIDENING',
        'SOIL_REPORT',
        'GEOTECHNICAL',
        'SATELLITE_REFERENCE',
        'DRONE_SURVEY',
        'TOTAL_STATION',
        'GNSS_SURVEY',
        'OTHER'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE evidence_source_type AS ENUM (
        'GIS_DERIVED',
        'CUSTOMER_DOCUMENT',
        'REMOTE_VERIFIED',
        'LICENSED_SURVEY',
        'GEOTECHNICAL_UTILITY_SURVEY',
        'GOVERNMENT_RECORD'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE site_confidence_tier_type AS ENUM (
        'L0_GIS_ESTIMATE',
        'L1_CUSTOMER_DOCUMENT',
        'L2_REMOTE_VERIFIED',
        'L3_LICENSED_SURVEY',
        'L4_ENGINEERING_READY'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE evidence_verification_status_type AS ENUM (
        'DRAFT',
        'SUBMITTED',
        'VERIFIED',
        'REJECTED',
        'SUPERSEDED'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE rule_trace_status_type AS ENUM (
        'CALCULATED',
        'VERIFIED',
        'ESTIMATED',
        'REQUIRES_REVIEW',
        'BLOCKED',
        'DRAFT',
        'APPROVED',
        'SUPERSEDED'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- 2. Site Reference Frames Table (Local Engineering Coordinate System Origin)
CREATE TABLE IF NOT EXISTS site_reference_frames (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    site_id UUID NOT NULL,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    version INT NOT NULL DEFAULT 1,
    origin_latitude NUMERIC(12, 9) NOT NULL,
    origin_longitude NUMERIC(12, 9) NOT NULL,
    origin_elevation_m NUMERIC(8, 3) NOT NULL DEFAULT 0.0,
    true_north_bearing_deg NUMERIC(8, 4) NOT NULL DEFAULT 0.0,
    ellipsoid VARCHAR(32) NOT NULL DEFAULT
-- [truncated for display] ...
```

### Migration File: `20261010040000_qto_boq_and_cost_engine.sql`
```sql
-- ====================================================================
-- Planwise Enterprise — Migration 04: QTO, BOQ & Cost Engine
-- Delta Specification & M3 Master Specification
-- ====================================================================

-- 1. Measurement Rules
CREATE TABLE IF NOT EXISTS qto_measurement_rules (
    rule_id VARCHAR(64) PRIMARY KEY,
    standard_reference VARCHAR(128) NOT NULL,
    version VARCHAR(32) NOT NULL,
    discipline VARCHAR(64) NOT NULL,
    category VARCHAR(64) NOT NULL,
    description TEXT NOT NULL,
    unit VARCHAR(16) NOT NULL,
    formula TEXT NOT NULL,
    inclusions JSONB DEFAULT '[]'::jsonb,
    exclusions JSONB DEFAULT '[]'::jsonb,
    rounding_policy VARCHAR(16) DEFAULT '0.001',
    source_element_types JSONB NOT NULL,
    verification_status VARCHAR(32) DEFAULT 'VERIFIED',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Construction Assemblies
CREATE TABLE IF NOT EXISTS construction_assemblies (
    assembly_id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    discipline VARCHAR(64) NOT NULL,
    category VARCHAR(64) NOT NULL,
    base_unit VARCHAR(16) NOT NULL,
    version VARCHAR(32) NOT NULL,
    specification TEXT NOT NULL,
    components JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Material Catalog
CREATE TABLE IF NOT EXISTS material_catalog (
    material_id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    category VARCHAR(64) NOT NULL,
    unit VARCHAR(16) NOT NULL,
    specification TEXT NOT NULL,
    wastage_percent NUMERIC(5, 2) DEFAULT 0.0,
    source VARCHAR(64) NOT NULL,
    version VARCHAR(32) NOT NULL,
    active_from DATE NOT NULL,
    active_to DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Cost Rate Snapshots (Immutable)
CREATE TABLE IF NOT EXISTS cost_rate_snapshots (
    rate_snapshot_id VARCHAR(64) PRIMARY KEY,
    jurisdiction VARCHAR(64) NOT NULL,
    location VARCHAR(128) NOT NULL,
    source VARCHAR(128) NOT NULL,
    source_date DATE NOT NULL,
    currency VARCHAR(8) DEFAULT 'INR',
    version VARCHAR(32) NOT NULL,
    rates JSONB NOT NULL,
    snapshot_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Takeoff Records
CREATE TABLE IF NOT EXISTS qto_takeoff_records (
    takeoff_id VARCHAR(64) PRIMARY KEY,
    design_version_id VARCHAR(64) NOT NULL,
    project_id VARCHAR(64) NOT NULL,
    discipline VARCHAR(64) NOT NULL,
    category VARCHAR(64) NOT NULL,
    element_type 
-- [truncated for display] ...
```

### Migration File: `20261010050000_engineer_review_and_releases.sql`
```sql
-- ============================================================================
-- Planwise Enterprise — Migration 05: Persistent Review & Release Ledger
-- Delta Specification §6.3, §12, §13, §14 & Phase 8.1 Specification
-- ============================================================================

-- 1. Releases Table (Immutable Handoff Package & Frozen Design Fingerprint)
CREATE TABLE IF NOT EXISTS releases (
    id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    design_version_id VARCHAR(64) NOT NULL,
    release_fingerprint VARCHAR(128) NOT NULL,
    lifecycle_state VARCHAR(64) NOT NULL DEFAULT 'SUBMITTED_FOR_REVIEW',
    status VARCHAR(64) NOT NULL DEFAULT 'BUILD_REQUESTED',
    requested_quality_tier VARCHAR(32) NOT NULL DEFAULT 'STANDARD',
    customer_acknowledgements JSONB NOT NULL DEFAULT '[]'::jsonb,
    house_option JSONB NOT NULL DEFAULT '{}'::jsonb,
    handoff_package JSONB NOT NULL DEFAULT '{}'::jsonb,
    locked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_releases_project ON releases(project_id);
CREATE INDEX IF NOT EXISTS idx_releases_design_version ON releases(design_version_id);
CREATE INDEX IF NOT EXISTS idx_releases_fingerprint ON releases(release_fingerprint);

-- 2. Build Requests Mapping Table
CREATE TABLE IF NOT EXISTS build_requests (
    id VARCHAR(64) PRIMARY KEY,
    release_id VARCHAR(64) NOT NULL REFERENCES releases(id) ON DELETE CASCADE,
    design_version_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_build_requests_release ON build_requests(release_id);

-- 3. Engineer Reviews Table (G0–G8 Professional Verification Ledger)
CREATE TABLE IF NOT EXISTS engineer_reviews (
    id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    build_request_id VARCHAR(64) NOT NULL,
    release_id VARCHAR(64) NOT NULL REFERENCES releases(id) ON DELETE CASCADE,
    design_version_id VARCHAR(64) NOT NULL,
    reviewer_id VARCHAR(64) NOT NULL DEFAULT 'ENG-MH-48201',
    status VARCHAR(64) NOT NULL DEFAULT 'IN_REVIEW',
    input_manifest_hash VARCHAR(128) NOT NULL,
    design_version_hash VARCHAR(128) NOT NULL,
    declared_plot_area_sqft NUMERIC(10, 2) NOT NULL DEFAULT 1100.0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_enginee
-- [truncated for display] ...
```

### Migration File: `20261010060000_generated_reports.sql`
```sql
-- ============================================================================
-- Planwise Enterprise — Migration 06: Generated Home Documentation & Reports Ledger
-- Authoritative PDF generation, cryptographic binding, and staleness tracking
-- ============================================================================

CREATE TABLE IF NOT EXISTS generated_reports (
    id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    site_id VARCHAR(64),
    design_version_id VARCHAR(64) NOT NULL,
    report_type VARCHAR(64) NOT NULL,
    release_id VARCHAR(64),
    release_fingerprint VARCHAR(128),
    input_manifest_hash VARCHAR(128) NOT NULL,
    output_pdf_hash VARCHAR(128) NOT NULL,
    file_path TEXT NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    engine_version VARCHAR(32) NOT NULL DEFAULT '1.0.0',
    is_stale BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_reports_design_version ON generated_reports(design_version_id);
CREATE INDEX IF NOT EXISTS idx_reports_project ON generated_reports(project_id);
CREATE INDEX IF NOT EXISTS idx_reports_type ON generated_reports(report_type);
CREATE INDEX IF NOT EXISTS idx_reports_release ON generated_reports(release_id);

-- [truncated for display] ...
```

### Migration File: `20261010070000_security_and_rls_policies.sql`
```sql
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
ALTER TABLE regulation_rule_packs ENABLE ROW LE
-- [truncated for display] ...
```

### Migration File: `20261010080000_organization_membership_mapping.sql`
```sql
-- ============================================================================
-- Planwise Enterprise — Migration 08: Organization Membership & RBAC Mapping
-- Phase 5 Tenant Isolation & User Role Authorization
-- ============================================================================

-- 1. Organizations Table
CREATE TABLE IF NOT EXISTS public.organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(256) NOT NULL,
    slug VARCHAR(128) UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_organizations_slug ON public.organizations(slug);

-- 2. Organization Memberships Table (Linking auth.users to organizations)
CREATE TABLE IF NOT EXISTS public.organization_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role VARCHAR(32) NOT NULL DEFAULT 'MEMBER' CHECK (role IN ('OWNER', 'ADMIN', 'MEMBER', 'VIEWER')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_org_user_membership UNIQUE (organization_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_org_memberships_user ON public.organization_memberships(user_id);
CREATE INDEX IF NOT EXISTS idx_org_memberships_org ON public.organization_memberships(organization_id);

-- 3. Security-Definer Helper Function with Fixed search_path
CREATE OR REPLACE FUNCTION public.get_user_organization_ids()
RETURNS SETOF UUID
SECURITY DEFINER
SET search_path = pg_catalog, public
LANGUAGE plpgsql STABLE AS $$
BEGIN
    RETURN QUERY
    SELECT organization_id
    FROM public.organization_memberships
    WHERE user_id = auth.uid()
    UNION
    SELECT NULLIF(current_setting('request.jwt.claims', true)::jsonb->>'org_id', '')::uuid
    WHERE NULLIF(current_setting('request.jwt.claims', true)::jsonb->>'org_id', '') IS NOT NULL;
END;
$$;

-- 4. Enable Row Level Security (RLS)
ALTER TABLE public.organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.organization_memberships ENABLE ROW LEVEL SECURITY;

-- 5. Administrative / Service Role Full Access
CREATE POLICY "admin_all_organizations" ON public.organizations
    FOR ALL TO service_role, postgres
    USING (true) WITH CHECK (true);

CREATE POLICY "admin_all_memberships" ON public.organization_memberships
    FOR ALL TO
-- [truncated for display] ...
```

