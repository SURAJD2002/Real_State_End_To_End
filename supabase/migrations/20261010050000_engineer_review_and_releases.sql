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

CREATE INDEX IF NOT EXISTS idx_engineer_reviews_project ON engineer_reviews(project_id);
CREATE INDEX IF NOT EXISTS idx_engineer_reviews_release ON engineer_reviews(release_id);
CREATE INDEX IF NOT EXISTS idx_engineer_reviews_build_req ON engineer_reviews(build_request_id);

-- 4. Engineer Review Gates Table (Independent Verification Gates G0–G6)
CREATE TABLE IF NOT EXISTS engineer_review_gates (
    id VARCHAR(64) PRIMARY KEY,
    engineer_review_id VARCHAR(64) NOT NULL REFERENCES engineer_reviews(id) ON DELETE CASCADE,
    gate_code VARCHAR(16) NOT NULL,
    title VARCHAR(128) NOT NULL,
    status VARCHAR(64) NOT NULL DEFAULT 'PENDING',
    reviewed_by VARCHAR(64),
    reviewed_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_review_gate UNIQUE (engineer_review_id, gate_code)
);

CREATE INDEX IF NOT EXISTS idx_review_gates_review ON engineer_review_gates(engineer_review_id);
CREATE INDEX IF NOT EXISTS idx_review_gates_code ON engineer_review_gates(gate_code);

-- 5. Engineer Review Issues Table (Structured Findings with Severity & Action)
CREATE TABLE IF NOT EXISTS engineer_review_issues (
    id VARCHAR(64) PRIMARY KEY,
    engineer_review_id VARCHAR(64) NOT NULL REFERENCES engineer_reviews(id) ON DELETE CASCADE,
    gate_code VARCHAR(16) NOT NULL,
    severity VARCHAR(32) NOT NULL DEFAULT 'WARNING',
    category VARCHAR(128) NOT NULL,
    description TEXT NOT NULL,
    required_action TEXT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'OPEN',
    created_by VARCHAR(64) NOT NULL DEFAULT 'ENG-MH-48201',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_review_issues_review ON engineer_review_issues(engineer_review_id);
CREATE INDEX IF NOT EXISTS idx_review_issues_severity ON engineer_review_issues(severity);

-- 6. Engineer Review Decisions Table (Attributable Professional Decisions)
CREATE TABLE IF NOT EXISTS engineer_review_decisions (
    id VARCHAR(64) PRIMARY KEY,
    engineer_review_id VARCHAR(64) NOT NULL REFERENCES engineer_reviews(id) ON DELETE CASCADE,
    decision VARCHAR(64) NOT NULL,
    decided_by VARCHAR(64) NOT NULL,
    decided_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reason TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_review_decisions_review ON engineer_review_decisions(engineer_review_id);
