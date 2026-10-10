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
    envelope_height_m NUMERIC(8, 2) NOT NULL,
    total_gross_bua_sqm NUMERIC(10, 2) NOT NULL,
    total_usable_area_sqm NUMERIC(10, 2) NOT NULL,
    floors_count INT NOT NULL DEFAULT 1,
    model_hash VARCHAR(128) NOT NULL, -- Deterministic SHA-256 fingerprint
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_bldg_models_design_ver ON building_models(design_version_id);
CREATE INDEX IF NOT EXISTS idx_bldg_models_hash ON building_models(model_hash);

-- 4. Building Levels Table (§8)
CREATE TABLE IF NOT EXISTS building_levels (
    id VARCHAR(64) PRIMARY KEY, -- e.g. LVL-000, LVL-001
    building_model_id VARCHAR(64) NOT NULL REFERENCES building_models(id) ON DELETE CASCADE,
    level_index INT NOT NULL,
    name VARCHAR(64) NOT NULL,
    elevation_m NUMERIC(8, 2) NOT NULL DEFAULT 0.00,
    floor_to_floor_height_m NUMERIC(8, 2) NOT NULL DEFAULT 3.15,
    usage VARCHAR(64) NOT NULL DEFAULT 'RESIDENTIAL',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_levels_bldg ON building_levels(building_model_id);

-- 5. Spaces Table (§9)
CREATE TABLE IF NOT EXISTS spaces (
    id VARCHAR(64) PRIMARY KEY, -- e.g. SPACE-FOYER, SPACE-LIVING_DINING
    building_model_id VARCHAR(64) NOT NULL REFERENCES building_models(id) ON DELETE CASCADE,
    level_id VARCHAR(64) NOT NULL REFERENCES building_levels(id) ON DELETE CASCADE,
    space_type VARCHAR(64) NOT NULL,
    name VARCHAR(128) NOT NULL,
    zone space_zone_type NOT NULL DEFAULT 'PUBLIC',
    floor VARCHAR(16) NOT NULL DEFAULT 'L0',
    color VARCHAR(32) NOT NULL DEFAULT '#60a5fa',
    area_sqm NUMERIC(8, 2) NOT NULL,
    perimeter_m NUMERIC(8, 2) NOT NULL,
    centroid_x NUMERIC(8, 2) NOT NULL,
    centroid_y NUMERIC(8, 2) NOT NULL,
    clear_height_m NUMERIC(6, 2) NOT NULL DEFAULT 3.00,
    bounds_x NUMERIC(8, 2) NOT NULL,
    bounds_y NUMERIC(8, 2) NOT NULL,
    bounds_width NUMERIC(8, 2) NOT NULL,
    bounds_height NUMERIC(8, 2) NOT NULL,
    polygon_coords JSONB NOT NULL, -- [[x, y], ...]
    daylight_requirement VARCHAR(64) DEFAULT 'DIRECT_WINDOW',
    ventilation_requirement VARCHAR(64) DEFAULT 'NATURAL_CROSS',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_spaces_model ON spaces(building_model_id);
CREATE INDEX IF NOT EXISTS idx_spaces_level ON spaces(level_id);

-- 6. Space Adjacency Topology (§10)
CREATE TABLE IF NOT EXISTS space_adjacencies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    space_id VARCHAR(64) NOT NULL REFERENCES spaces(id) ON DELETE CASCADE,
    adjacent_space_id VARCHAR(64) NOT NULL REFERENCES spaces(id) ON DELETE CASCADE,
    relationship_type VARCHAR(64) NOT NULL DEFAULT 'SPACE_ADJACENT_TO',
    shared_wall_length_m NUMERIC(8, 2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_space_adjacency UNIQUE (space_id, adjacent_space_id)
);

-- 7. Materials Catalog (§18)
CREATE TABLE IF NOT EXISTS materials (
    id VARCHAR(64) PRIMARY KEY, -- e.g. AAC_BLOCK_200, RCC_M25_FE500
    catalog_version VARCHAR(32) NOT NULL DEFAULT '2026.Q3',
    category VARCHAR(64) NOT NULL,
    name VARCHAR(256) NOT NULL,
    grade VARCHAR(64) NOT NULL,
    unit VARCHAR(16) NOT NULL,
    base_unit_rate_inr NUMERIC(12, 2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 8. Building Elements Table (§11, §12, §14, §16, §17)
CREATE TABLE IF NOT EXISTS building_elements (
    id VARCHAR(64) PRIMARY KEY, -- e.g. WALL-EXT-001, COL-A1, SLAB-L0
    building_model_id VARCHAR(64) NOT NULL REFERENCES building_models(id) ON DELETE CASCADE,
    level_id VARCHAR(64) NOT NULL REFERENCES building_levels(id) ON DELETE CASCADE,
    element_type building_element_type NOT NULL,
    name VARCHAR(128) NOT NULL,
    wall_type VARCHAR(32), -- EXTERNAL, INTERNAL, PARTITION
    material_id VARCHAR(64) REFERENCES materials(id),
    structural_role VARCHAR(32) NOT NULL DEFAULT 'NON_LOADBEARING',
    base_z NUMERIC(8, 2) NOT NULL DEFAULT 0.00,
    top_z NUMERIC(8, 2) NOT NULL DEFAULT 3.15,
    thickness_m NUMERIC(6, 3),
    height_m NUMERIC(6, 2),
    centerline_coords JSONB, -- [[x1, y1], [x2, y2]]
    footprint_polygon JSONB NOT NULL, -- [[x, y], ...]
    properties JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_elements_bldg ON building_elements(building_model_id);
CREATE INDEX IF NOT EXISTS idx_elements_level ON building_elements(level_id);
CREATE INDEX IF NOT EXISTS idx_elements_type ON building_elements(element_type);

-- 9. Openings Table (§13)
CREATE TABLE IF NOT EXISTS openings (
    id VARCHAR(64) PRIMARY KEY, -- e.g. DOOR-001, WIN-001
    building_model_id VARCHAR(64) NOT NULL REFERENCES building_models(id) ON DELETE CASCADE,
    level_id VARCHAR(64) NOT NULL REFERENCES building_levels(id) ON DELETE CASCADE,
    host_wall_id VARCHAR(64) NOT NULL REFERENCES building_elements(id) ON DELETE CASCADE,
    opening_type opening_type NOT NULL,
    width_m NUMERIC(6, 2) NOT NULL,
    height_m NUMERIC(6, 2) NOT NULL,
    sill_height_m NUMERIC(6, 2) NOT NULL DEFAULT 0.00,
    position_m NUMERIC(6, 2) NOT NULL, -- Position along host wall centerline
    properties JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_openings_host_wall ON openings(host_wall_id);
CREATE INDEX IF NOT EXISTS idx_openings_bldg ON openings(building_model_id);

-- 10. Structural Grid System Table (§15)
CREATE TABLE IF NOT EXISTS structural_grids (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    building_model_id VARCHAR(64) NOT NULL REFERENCES building_models(id) ON DELETE CASCADE,
    grid_lines_x JSONB NOT NULL, -- [{"tag": "A", "coordinate": 0.0}, ...]
    grid_lines_y JSONB NOT NULL, -- [{"tag": "1", "coordinate": 0.0}, ...]
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 11. Building Systems Table (§20)
CREATE TABLE IF NOT EXISTS building_systems (
    id VARCHAR(64) PRIMARY KEY, -- e.g. SYS-ELEC-01, SYS-PLUMB-01
    building_model_id VARCHAR(64) NOT NULL REFERENCES building_models(id) ON DELETE CASCADE,
    system_type VARCHAR(64) NOT NULL, -- ELECTRICAL, PLUMBING, DRAINAGE
    components JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 12. Model Validation Diagnostic Audit Table (§26, §27)
CREATE TABLE IF NOT EXISTS model_validations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    building_model_id VARCHAR(64) NOT NULL REFERENCES building_models(id) ON DELETE CASCADE,
    is_valid BOOLEAN NOT NULL,
    total_issues INT NOT NULL DEFAULT 0,
    blockers_count INT NOT NULL DEFAULT 0,
    errors_count INT NOT NULL DEFAULT 0,
    warnings_count INT NOT NULL DEFAULT 0,
    info_count INT NOT NULL DEFAULT 0,
    diagnostic_issues JSONB NOT NULL DEFAULT '[]'::jsonb,
    validated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_model_validations_bldg ON model_validations(building_model_id);
