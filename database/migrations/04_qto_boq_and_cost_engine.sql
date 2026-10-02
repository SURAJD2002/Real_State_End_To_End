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
    element_type VARCHAR(64) NOT NULL,
    assembly_id VARCHAR(64),
    gross_quantity NUMERIC(12, 4) NOT NULL,
    deductions JSONB DEFAULT '[]'::jsonb,
    net_quantity NUMERIC(12, 4) NOT NULL,
    unit VARCHAR(16) NOT NULL,
    measurement_rule_id VARCHAR(64) NOT NULL REFERENCES qto_measurement_rules(rule_id),
    source_element_ids JSONB NOT NULL,
    geometry_fingerprint VARCHAR(128) NOT NULL,
    confidence VARCHAR(32) NOT NULL,
    source_type VARCHAR(32) NOT NULL,
    input_hash VARCHAR(64) NOT NULL,
    output_hash VARCHAR(64) NOT NULL,
    calculated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_qto_dv ON qto_takeoff_records(design_version_id);
CREATE INDEX IF NOT EXISTS idx_qto_project ON qto_takeoff_records(project_id);

-- 6. Cost Estimates & BOQ
CREATE TABLE IF NOT EXISTS cost_estimates (
    estimate_id VARCHAR(64) PRIMARY KEY,
    design_version_id VARCHAR(64) NOT NULL,
    project_id VARCHAR(64) NOT NULL,
    rate_snapshot_id VARCHAR(64) NOT NULL REFERENCES cost_rate_snapshots(rate_snapshot_id),
    quality_tier VARCHAR(32) NOT NULL,
    status VARCHAR(32) NOT NULL,
    cost_waterfall JSONB NOT NULL,
    boq_lines JSONB NOT NULL,
    qto_hash VARCHAR(64) NOT NULL,
    boq_hash VARCHAR(64) NOT NULL,
    cost_hash VARCHAR(64) NOT NULL,
    confidence_summary JSONB NOT NULL,
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    disclaimer TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_est_dv ON cost_estimates(design_version_id);
CREATE INDEX IF NOT EXISTS idx_est_proj ON cost_estimates(project_id);
