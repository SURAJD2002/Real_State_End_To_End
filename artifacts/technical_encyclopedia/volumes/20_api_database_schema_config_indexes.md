# Volume XX — API, Database, Schema, and Configuration Indexes

## 1. Master REST API Endpoint Index (73 Endpoints)

| Method | Path | Handler Function | File | Auth | Role |
| :---: | :--- | :--- | :--- | :---: | :---: |
| `GET` | `/api/health` | `health_check` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/auth/session` | `get_auth_session` | `apps/api-gateway/main.py` | True | False |
| `GET` | `/api/v1/projects` | `list_projects` | `apps/api-gateway/main.py` | True | False |
| `POST` | `/api/v1/projects` | `create_project` | `apps/api-gateway/main.py` | True | False |
| `GET` | `/api/v1/projects/{project_id}` | `get_project` | `apps/api-gateway/main.py` | True | False |
| `PUT` | `/api/v1/projects/{project_id}/geometries` | `auto_save_geometries` | `apps/api-gateway/main.py` | True | False |
| `POST` | `/api/v1/projects/{project_id}/calculate-feasibility` | `run_feasibility_dag` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/projects/{project_id}/house-options` | `get_house_options` | `apps/api-gateway/main.py` | False | False |
| `POST` | `/api/v1/design-versions/{design_version_id}/build-request` | `request_build` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/releases/{release_id}/handoff-package` | `get_handoff_package` | `apps/api-gateway/main.py` | False | False |
| `POST` | `/api/v1/releases/{release_id}/approvals` | `update_gate_approval` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/releases/{release_id}/ifc` | `download_ifc_model` | `apps/api-gateway/main.py` | False | False |
| `POST` | `/api/v1/build-requests/{build_request_id}/engineer-review` | `create_or_get_engineer_review` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/engineer-reviews/{review_id}` | `get_engineer_review` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/engineer-reviews/{review_id}/gates` | `get_engineer_review_gates` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/engineer-reviews/{review_id}/issues` | `get_engineer_review_issues` | `apps/api-gateway/main.py` | False | False |
| `POST` | `/api/v1/engineer-reviews/{review_id}/gates/{gate_code}/verify` | `verify_review_gate` | `apps/api-gateway/main.py` | False | False |
| `POST` | `/api/v1/engineer-reviews/{review_id}/issues` | `create_review_issue` | `apps/api-gateway/main.py` | False | False |
| `POST` | `/api/v1/engineer-reviews/{review_id}/decision` | `record_review_decision` | `apps/api-gateway/main.py` | False | False |
| `POST` | `/api/v1/engineer-reviews/{review_id}/request-changes` | `request_review_changes` | `apps/api-gateway/main.py` | False | False |
| `POST` | `/api/v1/projects/load-golden-dataset` | `load_golden_dataset` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/regulations/MUMBAI_DCPR_2034` | `get_mumbai_regulations` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/design-versions/{design_version_id}/building-model` | `get_canonical_building_model_endpoint` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/design-versions/{design_version_id}/validation` | `get_model_validation_endpoint` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/design-versions/{design_version_id}/floor-plan` | `get_model_floor_plan_endpoint` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/design-versions/{design_version_id}/elevation` | `get_model_elevation_endpoint` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/design-versions/{design_version_id}/section` | `get_model_section_endpoint` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/design-versions/{design_version_id}/3d` | `get_model_3d_endpoint` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/design-versions/{design_version_id}/ifc` | `get_model_ifc_endpoint` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/design-versions/{design_version_id}/drawings` | `list_design_drawings_endpoint` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/design-versions/{design_version_id}/drawings/{drawing_id}` | `get_design_drawing_details_endpoint` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/design-versions/{design_version_id}/drawings/{drawing_id}/pdf` | `get_drawing_pdf_endpoint` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/design-versions/{design_version_id}/drawings/{drawing_id}/svg` | `get_drawing_svg_endpoint` | `apps/api-gateway/main.py` | False | False |
| `POST` | `/api/v1/design-versions/{design_version_id}/drawings/compile` | `compile_design_drawings_endpoint` | `apps/api-gateway/main.py` | False | False |
| `POST` | `/api/v1/projects/{project_id}/design-options/{option_id}/compile` | `compile_design_option_endpoint` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/sites/{site_id}/evidence` | `get_site_evidence_endpoint` | `apps/api-gateway/main.py` | False | False |
| `POST` | `/api/v1/sites/{site_id}/evidence` | `create_site_evidence_endpoint` | `apps/api-gateway/main.py` | False | False |
| `POST` | `/api/v1/sites/{site_id}/evidence/{evidence_id}/verify` | `verify_site_evidence_endpoint` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/sites/{site_id}/confidence` | `get_site_confidence_endpoint` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/sites/{site_id}/reference-frame` | `get_site_reference_frame_endpoint` | `apps/api-gateway/main.py` | False | False |
| `POST` | `/api/v1/sites/{site_id}/reference-frame` | `set_site_reference_frame_endpoint` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/regulation/rule-packs` | `list_rule_packs_endpoint` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/regulation/rule-packs/{rule_pack_id}` | `get_rule_pack_endpoint` | `apps/api-gateway/main.py` | False | False |
| `POST` | `/api/v1/sites/{site_id}/feasibility/evaluate` | `evaluate_site_statutory_feasibility_endpoint` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/sites/{site_id}/feasibility/explain` | `get_feasibility_explainability_endpoint` | `apps/api-gateway/main.py` | False | False |
| `POST` | `/api/v1/sites/{site_id}/design-options/generate` | `generate_design_options_endpoint` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/design-options/{design_option_id}` | `get_design_option_endpoint` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/design-options/{design_option_id}/validation` | `get_design_option_validation_endpoint` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/design-options/{design_option_id}/geometry` | `get_design_option_geometry_endpoint` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/design-options/{design_option_id}/metrics` | `get_design_option_metrics_endpoint` | `apps/api-gateway/main.py` | False | False |
| `POST` | `/api/v1/design-options/{design_option_id}/compile` | `compile_design_option_endpoint` | `apps/api-gateway/main.py` | False | False |
| `POST` | `/api/v1/design-options/{design_option_id}/freeze` | `freeze_design_option_endpoint` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/generation-jobs/{job_id}` | `get_generation_job_endpoint` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/rates/snapshots` | `get_rate_snapshots_endpoint` | `apps/api-gateway/main.py` | False | False |
| `POST` | `/api/v1/design-versions/{design_version_id}/qto/generate` | `generate_qto_endpoint` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/design-versions/{design_version_id}/qto` | `get_qto_endpoint` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/design-versions/{design_version_id}/boq` | `get_boq_endpoint` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/design-versions/{design_version_id}/cost` | `get_cost_endpoint` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/design-versions/{design_version_id}/cost/explain/{boq_item_id}` | `explain_cost_endpoint` | `apps/api-gateway/main.py` | False | False |
| `POST` | `/api/v1/design-versions/{design_version_id}/cost/recalculate` | `recalculate_cost_endpoint` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/design-versions/{design_version_id}/cost/export` | `export_cost_endpoint` | `apps/api-gateway/main.py` | False | False |
| `POST` | `/api/v1/design-versions/{design_version_id}/cost/jobs` | `start_cost_job_endpoint` | `apps/api-gateway/main.py` | False | False |
| `POST` | `/api/v1/intake/validate` | `validate_real_plot_intake_endpoint` | `apps/api-gateway/main.py` | False | False |
| `POST` | `/api/v1/intake/real-plot` | `execute_real_plot_pipeline_endpoint` | `apps/api-gateway/main.py` | False | False |
| `POST` | `/api/v1/design-versions/{design_version_id}/reports/home` | `generate_customer_home_report_endpoint` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/design-versions/{design_version_id}/reports/home/{report_id}` | `get_customer_home_report_metadata_endpoint` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/design-versions/{design_version_id}/reports/home/{report_id}/download` | `download_customer_home_report_endpoint` | `apps/api-gateway/main.py` | False | False |
| `POST` | `/api/v1/design-versions/{design_version_id}/reports/complete-package` | `generate_complete_package_endpoint` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/design-versions/{design_version_id}/reports/{report_id}/download` | `download_generic_report_endpoint` | `apps/api-gateway/main.py` | False | False |
| `GET` | `/api/v1/design-versions/{design_version_id}/reports` | `list_reports_endpoint` | `apps/api-gateway/main.py` | False | False |
| `POST` | `/api/v1/design-versions/{design_version_id}/reports/technical` | `generate_technical_report_endpoint` | `apps/api-gateway/main.py` | False | False |
| `POST` | `/api/v1/design-versions/{design_version_id}/reports/cost-boq` | `generate_cost_boq_report_endpoint` | `apps/api-gateway/main.py` | False | False |
| `POST` | `/api/v1/design-versions/{design_version_id}/reports/professional` | `generate_professional_report_endpoint` | `apps/api-gateway/main.py` | False | False |

---

## 2. Master Database Migration & Table Index (34 Tables)

| Directory | Migration File | Tables Created | RLS Enabled Tables | Lines |
| :--- | :--- | :--- | :--- | :---: |
| `supabase/migrations` | `20261010010000_init_postgis_schema.sql` | `projects; parcels; parcel_roads; parcel_constraints; feasibility_runs` | `` | 146 |
| `supabase/migrations` | `20261010020000_canonical_building_model.sql` | `design_versions; building_models; building_levels; spaces; space_adjacencies; materials; building_elements; openings; structural_grids; building_systems; model_validations` | `` | 233 |
| `supabase/migrations` | `20261010030000_site_evidence_and_rule_engine.sql` | `site_reference_frames; site_evidence; site_confidence_evaluations; regulation_rule_packs; rule_execution_traces` | `` | 188 |
| `supabase/migrations` | `20261010040000_qto_boq_and_cost_engine.sql` | `qto_measurement_rules; construction_assemblies; material_catalog; cost_rate_snapshots; qto_takeoff_records; cost_estimates` | `` | 111 |
| `supabase/migrations` | `20261010050000_engineer_review_and_releases.sql` | `releases; build_requests; engineer_reviews; engineer_review_gates; engineer_review_issues; engineer_review_decisions` | `` | 104 |
| `supabase/migrations` | `20261010060000_generated_reports.sql` | `generated_reports` | `` | 27 |
| `supabase/migrations` | `20261010070000_security_and_rls_policies.sql` | `` | `projects; parcels; parcel_roads; parcel_constraints; feasibility_runs; design_versions; building_models; building_levels; spaces; space_adjacencies; materials; building_elements; openings; structural_grids; building_systems; model_validations; site_reference_frames; site_evidence; site_confidence_evaluations; regulation_rule_packs; rule_execution_traces; qto_measurement_rules; construction_assemblies; material_catalog; cost_rate_snapshots; qto_takeoff_records; cost_estimates; releases; build_requests; engineer_reviews; engineer_review_gates; engineer_review_issues; engineer_review_decisions; generated_reports` | 169 |
| `supabase/migrations` | `20261010080000_organization_membership_mapping.sql` | `public.organizations; public.organization_memberships` | `public.organizations; public.organization_memberships` | 106 |
| `database/migrations` | `01_init_postgis_schema.sql` | `projects; parcels; parcel_roads; parcel_constraints; feasibility_runs` | `` | 140 |
| `database/migrations` | `02_canonical_building_model.sql` | `design_versions; building_models; building_levels; spaces; space_adjacencies; materials; building_elements; openings; structural_grids; building_systems; model_validations` | `` | 233 |
| `database/migrations` | `03_site_evidence_and_rule_engine.sql` | `site_reference_frames; site_evidence; site_confidence_evaluations; regulation_rule_packs; rule_execution_traces` | `` | 188 |
| `database/migrations` | `04_qto_boq_and_cost_engine.sql` | `qto_measurement_rules; construction_assemblies; material_catalog; cost_rate_snapshots; qto_takeoff_records; cost_estimates` | `` | 111 |
| `database/migrations` | `05_engineer_review_and_releases.sql` | `releases; build_requests; engineer_reviews; engineer_review_gates; engineer_review_issues; engineer_review_decisions` | `` | 104 |
| `database/migrations` | `06_generated_reports.sql` | `generated_reports` | `` | 27 |

---

## 3. Master Configuration & Secrets Management Index (65 Variables)

| Configuration File | Variable Name | Redacted Value | Secret | Purpose |
| :--- | :--- | :--- | :---: | :--- |
| `.env` | `POSTGRES_USER` | `postgres` | False | Runtime Configuration |
| `.env` | `POSTGRES_PASSWORD` | `[REDACTED_SECRET]` | True | Runtime Configuration |
| `.env` | `POSTGRES_DB` | `realestate_feasibility` | False | Runtime Configuration |
| `.env` | `POSTGRES_PORT` | `5432` | False | Runtime Configuration |
| `.env` | `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/realestate_feasibility` | False | Runtime Configuration |
| `.env` | `REDIS_HOST` | `localhost` | False | Runtime Configuration |
| `.env` | `REDIS_PORT` | `6379` | False | Runtime Configuration |
| `.env` | `REDIS_URL` | `redis://localhost:6379/0` | False | Runtime Configuration |
| `.env` | `SUPABASE_URL` | `https://qhqneldjxxdnttqfhqkf.supabase.co` | False | Runtime Configuration |
| `.env` | `SUPABASE_ANON_KEY` | `[REDACTED_SECRET]` | True | Runtime Configuration |
| `.env` | `SUPABASE_SERVICE_ROLE_KEY` | `[REDACTED_SECRET]` | True | Runtime Configuration |
| `.env` | `S3_ENDPOINT` | `http://localhost:9000` | False | Runtime Configuration |
| `.env` | `S3_PORT` | `9000` | False | Runtime Configuration |
| `.env` | `S3_CONSOLE_PORT` | `9001` | False | Runtime Configuration |
| `.env` | `S3_ACCESS_KEY` | `[REDACTED_SECRET]` | True | Runtime Configuration |
| `.env` | `S3_SECRET_KEY` | `[REDACTED_SECRET]` | True | Runtime Configuration |
| `.env` | `S3_BUCKET` | `feasibility-reports` | False | Runtime Configuration |
| `.env` | `API_PORT` | `5001` | False | Runtime Configuration |
| `.env` | `API_HOST` | `0.0.0.0` | False | Runtime Configuration |
| `.env` | `JWT_SECRET` | `[REDACTED_SECRET]` | True | Runtime Configuration |
| `.env` | `JWT_EXPIRY_HOURS` | `24` | False | Runtime Configuration |
| `.env` | `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000` | False | Runtime Configuration |
| `.env` | `VITE_API_BASE_URL` | `http://localhost:5001/api/v1` | False | Runtime Configuration |
| `.env` | `VITE_MAP_DEFAULT_LAT` | `19.0760` | False | Runtime Configuration |
| `.env` | `VITE_MAP_DEFAULT_LNG` | `72.8777` | False | Runtime Configuration |
| `.env` | `VITE_MAP_DEFAULT_ZOOM` | `14` | False | Runtime Configuration |
| `.env` | `VITE_MAPBOX_ACCESS_TOKEN` | `[REDACTED_SECRET]` | True | Runtime Configuration |
| `.env` | `VITE_SUPABASE_URL` | `https://qhqneldjxxdnttqfhqkf.supabase.co` | False | Runtime Configuration |
| `.env` | `VITE_SUPABASE_ANON_KEY` | `[REDACTED_SECRET]` | True | Runtime Configuration |
| `.env.example` | `POSTGRES_USER` | `postgres` | False | Runtime Configuration |
| `.env.example` | `POSTGRES_PASSWORD` | `[REDACTED_SECRET]` | True | Runtime Configuration |
| `.env.example` | `POSTGRES_DB` | `realestate_feasibility` | False | Runtime Configuration |
| `.env.example` | `POSTGRES_PORT` | `5432` | False | Runtime Configuration |
| `.env.example` | `DATABASE_URL` | `postgresql://postgres:your_postgres_password_here@localhost:5432/realestate_feasibility` | False | Runtime Configuration |
| `.env.example` | `SUPABASE_URL` | `https://your-project-ref.supabase.co` | False | Runtime Configuration |
| `.env.example` | `SUPABASE_ANON_KEY` | `[REDACTED_SECRET]` | True | Runtime Configuration |
| `.env.example` | `SUPABASE_SERVICE_ROLE_KEY` | `[REDACTED_SECRET]` | True | Runtime Configuration |
| `.env.example` | `REDIS_HOST` | `localhost` | False | Runtime Configuration |
| `.env.example` | `REDIS_PORT` | `6379` | False | Runtime Configuration |
| `.env.example` | `REDIS_URL` | `redis://localhost:6379/0` | False | Runtime Configuration |
| `.env.example` | `S3_ENDPOINT` | `http://localhost:9000` | False | Runtime Configuration |
| `.env.example` | `S3_PORT` | `9000` | False | Runtime Configuration |
| `.env.example` | `S3_CONSOLE_PORT` | `9001` | False | Runtime Configuration |
| `.env.example` | `S3_ACCESS_KEY` | `[REDACTED_SECRET]` | True | Runtime Configuration |
| `.env.example` | `S3_SECRET_KEY` | `[REDACTED_SECRET]` | True | Runtime Configuration |
| `.env.example` | `S3_BUCKET` | `feasibility-reports` | False | Runtime Configuration |
| `.env.example` | `API_PORT` | `5001` | False | Runtime Configuration |
| `.env.example` | `API_HOST` | `0.0.0.0` | False | Runtime Configuration |
| `.env.example` | `JWT_SECRET` | `[REDACTED_SECRET]` | True | Runtime Configuration |
| `.env.example` | `JWT_EXPIRY_HOURS` | `24` | False | Runtime Configuration |
| `.env.example` | `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000` | False | Runtime Configuration |
| `.env.example` | `VITE_API_BASE_URL` | `http://localhost:5001/api/v1` | False | Runtime Configuration |
| `.env.example` | `VITE_SUPABASE_URL` | `https://your-project-ref.supabase.co` | False | Runtime Configuration |
| `.env.example` | `VITE_SUPABASE_ANON_KEY` | `[REDACTED_SECRET]` | True | Runtime Configuration |
| `.env.example` | `VITE_MAP_DEFAULT_LAT` | `19.0760` | False | Runtime Configuration |
| `.env.example` | `VITE_MAP_DEFAULT_LNG` | `72.8777` | False | Runtime Configuration |
| `.env.example` | `VITE_MAP_DEFAULT_ZOOM` | `14` | False | Runtime Configuration |
| `.env.example` | `VITE_MAPBOX_ACCESS_TOKEN` | `[REDACTED_SECRET]` | True | Runtime Configuration |
| `apps/web/.env` | `VITE_API_BASE_URL` | `/api/v1` | False | Runtime Configuration |
| `apps/web/.env` | `VITE_MAP_DEFAULT_LAT` | `19.0760` | False | Runtime Configuration |
| `apps/web/.env` | `VITE_MAP_DEFAULT_LNG` | `72.8777` | False | Runtime Configuration |
| `apps/web/.env` | `VITE_MAP_DEFAULT_ZOOM` | `14` | False | Runtime Configuration |
| `apps/web/.env` | `VITE_MAPBOX_ACCESS_TOKEN` | `[REDACTED_SECRET]` | True | Runtime Configuration |
| `apps/web/.env` | `VITE_SUPABASE_URL` | `https://qhqneldjxxdnttqfhqkf.supabase.co` | False | Runtime Configuration |
| `apps/web/.env` | `VITE_SUPABASE_ANON_KEY` | `[REDACTED_SECRET]` | True | Runtime Configuration |

---

## 4. Technical Glossary & Abbreviation Index
- **B-rep:** Boundary Representation (geometric modeling technique representing solids by their bounding surfaces).
- **BOQ:** Bill of Quantities (itemized schedule of construction works and materials).
- **CBM:** Canonical Building Model (Planwise authoritative domain schema).
- **CP-SAT:** Constraint Programming - Satisfiability (Google OR-Tools solver).
- **DCPR:** Development Control and Promotion Regulations (Mumbai urban zoning bye-laws).
- **BBMP:** Bruhat Bengaluru Mahanagara Palike (Bengaluru municipal corporation).
- **FAR / FSI:** Floor Area Ratio / Floor Space Index (ratio of built-up area to plot area).
- **IFC:** Industry Foundation Classes (ISO 16739 open BIM data standard).
- **QTO:** Quantity Takeoff (computational extraction of material quantities from models).
- **RLS:** Row-Level Security (PostgreSQL fine-grained multi-tenant access control).
- **SPF:** STEP Physical File (ASCII text serialization for ISO 10303 / IFC models).
- **JWKS:** JSON Web Key Set (cryptographic public key set for verifying JWT signatures).
