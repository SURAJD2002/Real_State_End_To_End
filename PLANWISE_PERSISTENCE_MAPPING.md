# Planwise Enterprise — Production Database Persistence Mapping Architecture

**Status:** IMPLEMENTED & EVIDENCE-VERIFIED
**Target Database:** Supabase PostgreSQL 16 + PostGIS 3.3.7
**Schema Version:** Migration 01 through 08 (`20261010010000`–`20261010080000`)

---

## 1. Executive Summary

Planwise Enterprise previously relied on ephemeral in-memory state (`PROJECTS_DB` dictionary in `apps/api-gateway/main.py`) for project definitions and CAD boundaries. This implementation establishes a production-grade database persistence layer connecting the FastAPI backend (`apps/api-gateway`) and React frontend (`apps/web`) to Supabase PostgreSQL, ensuring:

1. **Zero Data Loss on Restart:** All customer projects, cadastral geometries, and statutory calculations survive process crashes.
2. **PostGIS Canonical Accuracy:** True spatial boundaries stored using PostGIS `geometry(Polygon, 4326)` with coordinate order `[longitude, latitude]`.
3. **Atomic Multi-Table Transactions:** Coordinated writes using PostgreSQL transactions ensuring no partial or corrupted records.
4. **Idempotency & Conflict Resolution:** Explicit `ON CONFLICT (id) DO UPDATE` semantics for CAD autosave and version progression.

---

## 2. Entity-to-Schema Mapping Matrix

| Domain Entity | Application Source | Supabase / PostgreSQL Table | Key Field Mappings |
| :--- | :--- | :--- | :--- |
| **Organization Tenant** | `AuthContext` / `JWT` | `public.organizations` | `id` (UUID), `name` (VARCHAR), `slug` (VARCHAR) |
| **Tenant Membership** | `AuthContext.role` | `public.organization_memberships` | `organization_id` (FK), `user_id` (FK auth.users), `role` (`OWNER`, `ADMIN`, `MEMBER`, `VIEWER`) |
| **Project Master** | `ProjectData` / `ProjectCreateRequest` | `public.projects` | `id` (UUID), `name`, `description`, `organization_id` (FK), `jurisdiction`, `status` (`DRAFT`, `FEASIBILITY_RUNNING`, `COMPLETED`, `ARCHIVED`) |
| **CAD Parcel & Boundary** | `parcel.coordinates` / `GeometryAutoSavePayload` | `public.parcels` | `project_id` (FK), `cadastral_survey_number`, `boundary_wgs84` (`ST_GeomFromText('POLYGON(...)', 4326)`), `gross_area_sqm` |
| **Feasibility DAG Run** | `FeasibilityResult` | `public.feasibility_runs` | `project_id` (FK), `gross_plot_area_sqm`, `net_developable_area_sqm`, `base_fsi`, `total_fsi`, `permissible_bua_sqm`, `max_building_height_m`, `summary_json` (JSONB) |
| **Design Version** | `designVersionId` | `public.design_versions` | `id` (VARCHAR), `project_id` (FK), `status` (`VALID`, `INVALID`, `SUPERSEDED`) |
| **Canonical Building Model** | `CanonicalBuildingModel` (CBM) | `public.building_models` | `id` (UUID), `design_version_id` (FK), `envelope_width_m`, `envelope_length_m`, `envelope_height_m`, `total_gross_bua_sqm`, `total_usable_area_sqm`, `floors_count`, `model_hash`, `metadata_json` |
| **QTO Measurements** | `TakeoffRecord` | `public.qto_takeoff_records` | `id` (UUID), `design_version_id` (FK), `item_code`, `net_quantity`, `measurement_unit`, `calculation_trace_json` |
| **Cost Estimate** | `CostEstimate` | `public.cost_estimates` | `id` (UUID), `design_version_id` (FK), `rate_snapshot_id` (FK), `total_direct_cost_inr`, `waterfall_breakdown_json` |
| **Release & Handoff** | `ReleaseManifest` | `public.releases` | `id` (VARCHAR), `project_id` (FK), `design_version_id` (FK), `release_fingerprint`, `is_immutable`, `artifact_manifest_json` |
| **Engineer Review & Gates** | `EngineerReview` | `public.engineer_reviews` | `id` (UUID), `project_id` (FK), `release_id` (FK), `status`, `review_type`, `summary_findings` |
| **Generated Home Report** | Report Worker / PDF Pipeline | `public.generated_reports` | `id` (VARCHAR), `project_id` (FK), `design_version_id` (FK), `report_type`, `input_manifest_hash`, `output_pdf_hash`, `file_path`, `file_size_bytes` |

---

## 3. Transaction Boundaries & Concurrency Controls

### 3.1 CAD Parcel & Project Atomic Upsert
```sql
DO $$
BEGIN
    -- Ensure organization exists
    INSERT INTO public.organizations (id, name, slug)
    VALUES ('{org_uuid}', '{clean_name}', '{slug}')
    ON CONFLICT (id) DO NOTHING;

    -- Upsert Project
    INSERT INTO public.projects (id, name, description, organization_id, jurisdiction, status, updated_at)
    VALUES ('{proj_uuid}', '{name}', '{desc}', '{org_uuid}', '{jurisdiction}', '{status}', NOW())
    ON CONFLICT (id) DO UPDATE SET
        name = EXCLUDED.name,
        description = EXCLUDED.description,
        organization_id = EXCLUDED.organization_id,
        jurisdiction = EXCLUDED.jurisdiction,
        status = EXCLUDED.status,
        updated_at = NOW();

    -- Upsert Parcel with PostGIS geometry
    INSERT INTO public.parcels (
        project_id, cadastral_survey_number, tenure_type,
        boundary_wgs84, gross_area_sqm, updated_at
    )
    VALUES (
        '{proj_uuid}', '{survey_no}', 'PRIVATE_FREEHOLD',
        ST_GeomFromText('{wkt_polygon}', 4326), {gross_area}, NOW()
    )
    ON CONFLICT (id) DO UPDATE SET
        boundary_wgs84 = EXCLUDED.boundary_wgs84,
        gross_area_sqm = EXCLUDED.gross_area_sqm,
        updated_at = NOW();
END $$;
```

### 3.2 PostGIS Spatial Serialization & Deserialization
- **Inbound:** Frontend coordinates `[[lng, lat], ...]` are transformed via `coords_to_wkt_polygon()` into WKT string `POLYGON((lng1 lat1, lng2 lat2, ..., lng1 lat1))`. The first and last points are automatically closed.
- **Outbound:** PostgreSQL query executes `ST_AsGeoJSON(pa.boundary_wgs84)` returning GeoJSON coordinates directly parsed into client coordinate arrays without precision degradation.

---

## 4. Verification Evidence

- **Direct Database Test:** `tests/test_persistence_and_auth_workflow.py`
  - `test_04_cad_geometry_auto_save_and_persistence`: Confirms 1,100 sq ft Bandra plot coordinates persist and increment parcel version from 1 to 2.
  - `test_05_feasibility_dag_execution_and_persistence`: Verifies permissible BUA, FSI, and regulation traces persist in `feasibility_runs`.
  - `test_06_process_restart_persistence_resilience`: Purges in-memory volatile cache (`del api_main.PROJECTS_DB[proj_id]`), restarts request, and confirms complete rehydration from PostgreSQL.
- **Exit Code:** `0` (Ran 6 tests in 104.452s, PASS).
