# Planwise Enterprise — Supabase Migration Audit

## Executive Summary
This document provides a comprehensive audit of all local SQL schemas, migration scripts, extensions, triggers, functions, and database settings for the Planwise Enterprise repository prior to connecting and migrating to the remote Supabase project (`qhqneldjxxdnttqfhqkf`).

---

## 1. Supabase Environment & CLI Verification

- **Supabase CLI Version**: `v2.101.0` installed at `/opt/homebrew/bin/supabase`.
- **Target Project Reference**: `qhqneldjxxdnttqfhqkf` (Organization ID: `ftbfyrekodvunboelxti`, Project Name: `shop14812@gmail.com's Project`, Region: `Oceania (Sydney)`).
- **Authentication & Link Status**: Verified active and linked via Supabase Management API (`supabase link --project-ref qhqneldjxxdnttqfhqkf`).
- **Supabase Project Configuration**: Initialized at `supabase/config.toml` (API port 54321, DB port 54322, Studio port 54323).
- **Backend Connection Discovery**:
  - The API Gateway (`apps/api-gateway/ledger_repository.py`) uses `DATABASE_URL` resolved from environment variables or root `.env`.
  - Fallback local DSN: `postgresql://postgres:postgres@localhost:5432/realestate_feasibility`.
  - Remote Supabase connection target: `postgresql://postgres:[PASSWORD]@db.qhqneldjxxdnttqfhqkf.supabase.co:5432/postgres` (or port 6543 pooler).
  - Credentials remain strictly outside git tracking in accordance with zero-leak policy.

---

## 2. Local SQL Schema & Migration Catalog

All authoritative local migration scripts were discovered in `database/migrations/` and have been synchronized to `supabase/migrations/` using timestamped version prefixes.

| # | Local Migration File | Canonical Supabase Migration | Purpose & Domain | Key Relational Objects |
|---|----------------------|------------------------------|------------------|------------------------|
| **01** | `01_init_postgis_schema.sql` | `20261010010000_init_postgis_schema.sql` | PostGIS spatial extensions, domain enums, core projects, parcels, cadastral road frontage, zoning constraints, deterministic feasibility DAG runs. | Extensions: `uuid-ossp`, `postgis`, `btree_gist`<br>Tables: `projects`, `parcels`, `parcel_roads`, `parcel_constraints`, `feasibility_runs` |
| **02** | `02_canonical_building_model.sql` | `20261010020000_canonical_building_model.sql` | Canonical Building Model (CBM) relational schema, design versioning, architectural hierarchy, 3D solids, materials, structural grids, MEP building systems, diagnostic audits. | Tables: `design_versions`, `building_models`, `building_levels`, `spaces`, `space_adjacencies`, `materials`, `building_elements`, `openings`, `structural_grids`, `building_systems`, `model_validations` |
| **03** | `03_site_evidence_and_rule_engine.sql` | `20261010030000_site_evidence_and_rule_engine.sql` | Site truth reference frames (SECS_ENU local origin), multi-source evidence provenance, confidence tier evaluations (L0–L4), statutory rule packs, explainable execution traces. | Tables: `site_reference_frames`, `site_evidence`, `site_confidence_evaluations`, `regulation_rule_packs`, `rule_execution_traces` |
| **04** | `04_qto_boq_and_cost_engine.sql` | `20261010040000_qto_boq_and_cost_engine.sql` | Quantity Takeoff (QTO) measurement rules, construction assemblies, material catalog, immutable cost rate snapshots, takeoff records, BOQ cost waterfalls. | Tables: `qto_measurement_rules`, `construction_assemblies`, `material_catalog`, `cost_rate_snapshots`, `qto_takeoff_records`, `cost_estimates` |
| **05** | `05_engineer_review_and_releases.sql` | `20261010050000_engineer_review_and_releases.sql` | Persistent review and release ledger, immutable handoff packages, build requests, independent verification gates (G0–G6), structured review issues, professional decisions. | Tables: `releases`, `build_requests`, `engineer_reviews`, `engineer_review_gates`, `engineer_review_issues`, `engineer_review_decisions` |
| **06** | `06_generated_reports.sql` | `20261010060000_generated_reports.sql` | Authoritative customer documentation, home reports, cryptographic output hash tracking, staleness detection. | Tables: `generated_reports` |
| **07** | *New Security Layer* | `20261010070000_security_and_rls_policies.sql` | Row Level Security (RLS) activation on all 34 public tables, administrative fail-safe policies for backend/service role, public read-only access for catalogs, multi-tenant organization isolation. | Policies: 34 table RLS enforcements, service-role admin policies, catalog select policies, tenant isolation policies |

---

## 3. Remote Database State Prior to Migration

A read-only inspection was executed using `supabase db query --linked` against `qhqneldjxxdnttqfhqkf`:

1. **System Schemas**: Standard Supabase managed schemas present: `auth`, `realtime`, `storage`, `vault`, `extensions`, `public`.
2. **Public Schema Tables**: **0 tables**. Remote database is in a clean, pristine state.
3. **Existing Extensions**:
   - `pg_stat_statements` (v1.11)
   - `pgcrypto` (v1.3)
   - `plpgsql` (v1.0)
   - `supabase_vault` (v0.3.1)
   - `uuid-ossp` (v1.1)
4. **Required Extensions Available in Remote Postgres**:
   - `postgis` (v3.3.7 available, not yet enabled)
   - `btree_gist` (v1.7 available, not yet enabled)
5. **Existing Remote Migrations**: **0 migrations** recorded (`supabase_migrations.schema_migrations` does not exist yet).
6. **Production Data Dependencies**: None. No production data exists on the remote database, guaranteeing zero risk of data loss.

---

## 4. Authoritative Source & Directory Policy

- The authoritative migration directory for Supabase deployments is **`supabase/migrations/`**.
- Local `database/migrations/` files are preserved for backwards compatibility with local standalone Docker PostgreSQL setups.
- Migration filenames in `supabase/migrations/` follow the standard format: `<YYYYMMDDHHMMSS>_<name>.sql`.
