-- PostGIS & Extensions Initialization
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "btree_gist";

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
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_boundary_wgs84_valid CHECK (ST_IsValid(boundary_wgs84))
);

CREATE INDEX IF NOT EXISTS idx_parcels_boundary_wgs84 ON parcels USING GIST (boundary_wgs84);
CREATE INDEX IF NOT EXISTS idx_parcels_project_id ON parcels(project_id) WHERE NOT is_deleted;

-- 3. Parcel Road Frontages Table
CREATE TABLE IF NOT EXISTS parcel_roads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parcel_id UUID NOT NULL REFERENCES parcels(id) ON DELETE CASCADE,
    road_name VARCHAR(256),
    existing_width_m NUMERIC(6, 2) NOT NULL CHECK (existing_width_m > 0),
    proposed_width_m NUMERIC(6, 2) CHECK (proposed_width_m >= existing_width_m),
    road_boundary_edge GEOMETRY(LineString, 4326),
    road_centerline GEOMETRY(LineString, 4326),
    is_primary_access BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_parcel_roads_edge ON parcel_roads USING GIST (road_boundary_edge);

-- 4. Parcel Spatial Constraints Table
CREATE TABLE IF NOT EXISTS parcel_constraints (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parcel_id UUID NOT NULL REFERENCES parcels(id) ON DELETE CASCADE,
    constraint_name VARCHAR(128) NOT NULL,
    constraint_category VARCHAR(64) NOT NULL,
    severity constraint_severity_type NOT NULL DEFAULT 'HARD_ABSOLUTE_EXCLUSION',
    buffer_distance_m NUMERIC(6, 2) NOT NULL DEFAULT 0.0,
    vertical_clearance_limit_m NUMERIC(8, 2),
    footprint_wgs84 GEOMETRY(Geometry, 4326) NOT NULL,
    statutory_reference VARCHAR(256),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_parcel_constraints_geom ON parcel_constraints USING GIST (footprint_wgs84);

-- 5. Feasibility Runs Table (Deterministic DAG Results)
CREATE TABLE IF NOT EXISTS feasibility_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    parcel_id UUID NOT NULL REFERENCES parcels(id) ON DELETE CASCADE,
    regulation_version_id VARCHAR(64) NOT NULL DEFAULT 'DCPR_2034_V1_2026',
    engine_version VARCHAR(32) NOT NULL DEFAULT '1.0.0',
    gross_plot_area_sqm NUMERIC(14, 4) NOT NULL,
    road_deduction_sqm NUMERIC(14, 4) NOT NULL DEFAULT 0,
    amenity_reservation_sqm NUMERIC(14, 4) NOT NULL DEFAULT 0,
    net_developable_area_sqm NUMERIC(14, 4) NOT NULL,
    base_fsi NUMERIC(6, 3) NOT NULL,
    premium_fsi NUMERIC(6, 3) NOT NULL DEFAULT 0,
    tdr_fsi NUMERIC(6, 3) NOT NULL DEFAULT 0,
    total_fsi NUMERIC(6, 3) NOT NULL,
    permissible_bua_sqm NUMERIC(14, 4) NOT NULL,
    max_building_height_m NUMERIC(8, 2) NOT NULL,
    gross_development_value NUMERIC(16, 2) NOT NULL,
    total_development_cost NUMERIC(16, 2) NOT NULL,
    net_margin_percentage NUMERIC(6, 2) NOT NULL,
    equity_irr_percentage NUMERIC(6, 2) NOT NULL,
    dag_execution_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_feasibility_runs_project ON feasibility_runs(project_id, created_at DESC);
