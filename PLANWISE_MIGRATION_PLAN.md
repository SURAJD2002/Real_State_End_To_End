# Planwise Enterprise — Database Migration Plan & Applied Ledger

**Target Project:** `qhqneldjxxdnttqfhqkf`
**Applied Migrations Count:** 8 / 8 (100% Reconciled)
**Safety Protocol:** Non-destructive, incremental forward migration only. `db reset` strictly prohibited.

---

## 1. Migration History & Schema Baseline

The remote Supabase PostgreSQL schema has been fully reconciled and verified against `supabase_migrations.schema_migrations`.

| Version / Timestamp | Migration File | Description | Status |
| :--- | :--- | :--- | :--- |
| `20261010010000` | `20261010010000_core_spatial_schema.sql` | PostGIS extension, projects, parcels, and statutory zoning layers. | APPLIED |
| `20261010020000` | `20261010020000_feasibility_rules_engine.sql` | Feasibility runs, statutory rule traces, and Mumbai DCPR 2034 engine data. | APPLIED |
| `20261010030000` | `20261010030000_canonical_building_models.sql` | Design versions, Canonical Building Models (CBM), building levels, spaces, and elements. | APPLIED |
| `20261010040000` | `20261010040000_qto_and_cost_estimation.sql` | Model-linked QTO records, construction assemblies, material catalog, and deterministic cost models. | APPLIED |
| `20261010050000` | `20261010050000_immutable_releases_and_handoff.sql` | Immutable release ledger, build requests, and cryptographic handoff manifests. | APPLIED |
| `20261010060000` | `20261010060000_engineer_review_ledger.sql` | Professional engineer reviews, verification gates (G0–G6), audit issues, and decisions. | APPLIED |
| `20261010070000` | `20261010070000_security_and_rls_policies.sql` | Initial RLS policies, role grants, and security definer functions. | APPLIED |
| `20261010080000` | `20261010080000_organization_membership_mapping.sql` | Organizations, organization memberships, tenant isolation RBAC, and `get_user_organization_ids()`. | APPLIED |

---

## 2. Migration Execution Safety Protocol

1. **Pre-Migration Verification:**
   - Always run `supabase db diff --linked` or inspect table catalogs before creating new migration files.
   - Verify existing foreign key relationships to prevent orphan data or schema conflicts.
2. **Execution Boundary:**
   - Migrations are pushed using the official Supabase CLI pipeline: `supabase db push --linked`.
   - Never run `db reset` on a production or pilot database.
3. **Rollback & Disaster Recovery Strategy:**
   - All migrations maintain explicit forward compatibility.
   - For emergency rollbacks, specific down scripts are authored targeting reverse operations without dropping data tables.
   - Table alterations use `IF EXISTS` and `IF NOT EXISTS` guards.
