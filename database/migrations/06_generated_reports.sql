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
