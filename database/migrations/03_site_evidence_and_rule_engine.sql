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
    ellipsoid VARCHAR(32) NOT NULL DEFAULT 'WGS84',
    datum VARCHAR(32) NOT NULL DEFAULT 'WGS84',
    coordinate_system VARCHAR(32) NOT NULL DEFAULT 'SECS_ENU',
    is_locked BOOLEAN NOT NULL DEFAULT FALSE,
    hash_fingerprint VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_site_ref_frame_version UNIQUE (site_id, version)
);

CREATE INDEX IF NOT EXISTS idx_site_ref_frame_site ON site_reference_frames(site_id, version DESC);

-- 3. Site Evidence Table (Multi-Source Provenance & Verification)
CREATE TABLE IF NOT EXISTS site_evidence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    site_id UUID NOT NULL,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    evidence_type site_evidence_type NOT NULL,
    source_type evidence_source_type NOT NULL,
    source_document_id VARCHAR(128),
    provider VARCHAR(128) NOT NULL,
    captured_at TIMESTAMPTZ NOT NULL,
    accuracy_m NUMERIC(8, 4),
    confidence_level site_confidence_tier_type NOT NULL DEFAULT 'L0_GIS_ESTIMATE',
    geometry GEOMETRY(Geometry, 4326),
    coordinate_reference VARCHAR(64) NOT NULL DEFAULT 'EPSG:4326',
    verification_status evidence_verification_status_type NOT NULL DEFAULT 'DRAFT',
    verified_by VARCHAR(128),
    verified_at TIMESTAMPTZ,
    notes TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_site_evidence_site ON site_evidence(site_id) WHERE NOT is_deleted;
CREATE INDEX IF NOT EXISTS idx_site_evidence_geom ON site_evidence USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_site_evidence_type ON site_evidence(site_id, evidence_type);

-- 4. Site Confidence Evaluations Table
CREATE TABLE IF NOT EXISTS site_confidence_evaluations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    site_id UUID NOT NULL,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    evaluated_tier site_confidence_tier_type NOT NULL,
    blocking_for_build BOOLEAN NOT NULL DEFAULT TRUE,
    missing_requirements JSONB NOT NULL DEFAULT '[]'::jsonb,
    evidence_count INT NOT NULL DEFAULT 0,
    verified_evidence_count INT NOT NULL DEFAULT 0,
    explanation TEXT NOT NULL,
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_site_conf_eval_site ON site_confidence_evaluations(site_id, evaluated_at DESC);

-- 5. Regulation Rule Packs Table (Immutable, Versioned Statutory Definitions)
CREATE TABLE IF NOT EXISTS regulation_rule_packs (
    id VARCHAR(64) PRIMARY KEY,
    jurisdiction VARCHAR(64) NOT NULL,
    authority VARCHAR(128) NOT NULL,
    name VARCHAR(256) NOT NULL,
    version VARCHAR(32) NOT NULL,
    effective_from DATE NOT NULL,
    effective_to DATE,
    typologies JSONB NOT NULL DEFAULT '[]'::jsonb,
    rules_data JSONB NOT NULL,
    is_immutable BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rule_packs_jurisdiction ON regulation_rule_packs(jurisdiction, version);

-- 6. Rule Execution Traces Table (Explainable Statutory Audit Trail)
CREATE TABLE IF NOT EXISTS rule_execution_traces (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trace_id VARCHAR(64) NOT NULL,
    site_id UUID NOT NULL,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    design_version_id UUID,
    feasibility_run_id UUID REFERENCES feasibility_runs(id) ON DELETE SET NULL,
    rule_pack_id VARCHAR(64) NOT NULL REFERENCES regulation_rule_packs(id),
    rule_id VARCHAR(64) NOT NULL,
    rule_version VARCHAR(32) NOT NULL,
    category VARCHAR(64) NOT NULL,
    inputs JSONB NOT NULL DEFAULT '{}'::jsonb,
    calculation JSONB NOT NULL DEFAULT '{}'::jsonb,
    outputs JSONB NOT NULL DEFAULT '{}'::jsonb,
    status rule_trace_status_type NOT NULL DEFAULT 'CALCULATED',
    severity VARCHAR(32) NOT NULL DEFAULT 'INFO',
    evidence_references JSONB NOT NULL DEFAULT '[]'::jsonb,
    explanation TEXT NOT NULL,
    executed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rule_traces_site ON rule_execution_traces(site_id, executed_at DESC);
CREATE INDEX IF NOT EXISTS idx_rule_traces_feasibility ON rule_execution_traces(feasibility_run_id);
CREATE INDEX IF NOT EXISTS idx_rule_traces_rule_id ON rule_execution_traces(rule_pack_id, rule_id);
