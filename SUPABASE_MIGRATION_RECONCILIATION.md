# Planwise Enterprise — Supabase Migration Reconciliation Matrix

## Executive Summary
This reconciliation matrix tracks the exact alignment between local migration definitions and the target remote Supabase project (`qhqneldjxxdnttqfhqkf`).

---

## 1. Reconciliation Matrix

| Migration ID / Version | Canonical File Path | Domain / Purpose | Objects Created / Modified | Reflected Remotely? | Safely Executable? | Dependencies | Risk Level | Recommended Action |
|:---|:---|:---|:---|:---:|:---:|:---|:---:|:---|
| **20261010010000** | `supabase/migrations/20261010010000_init_postgis_schema.sql` | PostGIS Spatial & Core Feasibility Schema | Extensions: `postgis`, `btree_gist`, `uuid-ossp`<br>Enums: `land_tenure_type`, `constraint_severity_type`, `project_status_type`, `unit_typology_type`<br>Tables: `projects`, `parcels`, `parcel_roads`, `parcel_constraints`, `feasibility_runs` | **NO** (0 / 5 tables exist) | **YES** (Dry run validated) | None (Foundational) | **Low** | Apply via Supabase CLI push |
| **20261010020000** | `supabase/migrations/20261010020000_canonical_building_model.sql` | Canonical Building Model (CBM) Relational Store | Enums: `design_version_status_type`, `building_element_type`, `opening_type`, `space_zone_type`<br>Tables: `design_versions`, `building_models`, `building_levels`, `spaces`, `space_adjacencies`, `materials`, `building_elements`, `openings`, `structural_grids`, `building_systems`, `model_validations` | **NO** (0 / 11 tables exist) | **YES** (Dry run validated) | `20261010010000` (`projects`) | **Low** | Apply via Supabase CLI push |
| **20261010030000** | `supabase/migrations/20261010030000_site_evidence_and_rule_engine.sql` | Site Evidence Provenance & Statutory Rule Traces | Enums: `site_evidence_type`, `evidence_source_type`, `site_confidence_tier_type`, `evidence_verification_status_type`, `rule_trace_status_type`<br>Tables: `site_reference_frames`, `site_evidence`, `site_confidence_evaluations`, `regulation_rule_packs`, `rule_execution_traces` | **NO** (0 / 5 tables exist) | **YES** (Dry run validated) | `20261010010000` (`projects`, `feasibility_runs`) | **Low** | Apply via Supabase CLI push |
| **20261010040000** | `supabase/migrations/20261010040000_qto_boq_and_cost_engine.sql` | QTO, BOQ & Cost Waterfall Engine | Tables: `qto_measurement_rules`, `construction_assemblies`, `material_catalog`, `cost_rate_snapshots`, `qto_takeoff_records`, `cost_estimates` | **NO** (0 / 6 tables exist) | **YES** (Dry run validated) | None (Self-contained) | **Low** | Apply via Supabase CLI push |
| **20261010050000** | `supabase/migrations/20261010050000_engineer_review_and_releases.sql` | Engineer Review (G0–G6) & Release Ledger | Tables: `releases`, `build_requests`, `engineer_reviews`, `engineer_review_gates`, `engineer_review_issues`, `engineer_review_decisions` | **NO** (0 / 6 tables exist) | **YES** (Dry run validated) | None (Self-contained) | **Low** | Apply via Supabase CLI push |
| **20261010060000** | `supabase/migrations/20261010060000_generated_reports.sql` | Generated Home Documentation & Reports Ledger | Tables: `generated_reports` | **NO** (0 / 1 table exists) | **YES** (Dry run validated) | None (Self-contained) | **Low** | Apply via Supabase CLI push |
| **20261010070000** | `supabase/migrations/20261010070000_security_and_rls_policies.sql` | Zero-Trust Row Level Security (RLS) & Tenant Isolation | Functions: `current_user_org_id()`, `is_admin_or_service()`<br>RLS Activation: All 34 public tables<br>Policies: Admin/Service role pass-through, catalog public select, tenant isolation | **NO** (0 / 34 policies exist) | **YES** (Dry run validated) | All preceding migrations (`01`–`06`) | **Low** | Apply via Supabase CLI push |

---

## 2. Divergence Analysis

- **Historical Divergence**: None. The remote database has not had any prior migrations applied through Supabase CLI or manual DDL scripts.
- **Destructive Statements**: None. All migrations utilize additive DDL (`CREATE EXTENSION IF NOT EXISTS`, `CREATE TABLE IF NOT EXISTS`, `CREATE INDEX IF NOT EXISTS`, idempotent `DO $$ BEGIN ... EXCEPTION WHEN duplicate_object THEN NULL; END $$;`).
- **Data Risk**: Zero data loss risk. No production records exist on the remote database.
