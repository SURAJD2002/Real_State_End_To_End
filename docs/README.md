# Planwise Enterprise — Engineering Documentation & Architecture Index

This index provides direct navigation to the authoritative engineering documentation, milestone delivery reports, database migration audits, mathematical formula matrices, and architecture specifications across Planwise Enterprise.

---

## 1. Pilot Readiness, Security & Authorization

- **[PLANWISE_PILOT_READINESS_REPORT.md](../PLANWISE_PILOT_READINESS_REPORT.md)**: Authoritative controlled-pilot readiness evaluation, gate-by-gate security status, P0 JWT remediation evidence, and test execution outcomes.
- **[PLANWISE_AUTHENTICATION_AND_AUTHORIZATION.md](../PLANWISE_AUTHENTICATION_AND_AUTHORIZATION.md)**: Deep dive into Supabase Auth integration, asymmetric ES256 JWKS token verification, and organization-based RBAC.
- **[SUPABASE_SECURITY_RLS_AUDIT.md](../SUPABASE_SECURITY_RLS_AUDIT.md)**: Zero-trust Row Level Security (RLS) audit across all 34 domain tables, security-definer helper functions, and search_path pinning.
- **[PLANWISE_INTEGRATION_TEST_REPORT.md](../PLANWISE_INTEGRATION_TEST_REPORT.md)**: Comprehensive multi-tenant regression, CAD persistence, and statutory feasibility test log.

---

## 2. Database Migrations & Production Persistence

- **[PLANWISE_PERSISTENCE_MAPPING.md](../PLANWISE_PERSISTENCE_MAPPING.md)**: Complete endpoint-to-repository-to-table persistence mapping demonstrating zero unpersisted customer data.
- **[PLANWISE_MIGRATION_PLAN.md](../PLANWISE_MIGRATION_PLAN.md)**: Migration blueprint and reconciliation strategy for PostgreSQL 16 + PostGIS schema.
- **[SUPABASE_MIGRATION_AUDIT.md](../SUPABASE_MIGRATION_AUDIT.md)**: Audit of migrations 01 through 08, table definitions, foreign keys, and indexes.
- **[SUPABASE_MIGRATION_RECONCILIATION.md](../SUPABASE_MIGRATION_RECONCILIATION.md)**: Synchronization log between local migration files and remote Supabase project.
- **[SUPABASE_POST_MIGRATION_VALIDATION.md](../SUPABASE_POST_MIGRATION_VALIDATION.md)**: Integrity validation of applied database schemas and spatial constraints.

---

## 3. Computational Engines, BIM & Drawing Pipelines

- **[PHASE_9_M1_IFC_PROFESSIONALIZATION_REPORT.md](../PHASE_9_M1_IFC_PROFESSIONALIZATION_REPORT.md)**: Open-standard IFC4 STEP physical file export, semantic classification, and georeferencing.
- **[PHASE_9_M2_PROFESSIONAL_DRAWING_PIPELINE_REPORT.md](../PHASE_9_M2_PROFESSIONAL_DRAWING_PIPELINE_REPORT.md)**: Automated 9-sheet publication-grade architectural drawing compilation engine (Floor Plans, Elevations, Sections).
- **[ARCHITECTURAL_RENDERER_V2_REPORT.md](../ARCHITECTURAL_RENDERER_V2_REPORT.md)**: Vector rendering pipeline, SVG styling, layer hierarchy, and dimension annotations.
- **[ARCHITECTURAL_FLOOR_PLAN_RENDERER_AUDIT.md](../ARCHITECTURAL_FLOOR_PLAN_RENDERER_AUDIT.md)**: Architectural layout diagnostics and room graph validation.
- **[FORMULA_VERIFICATION_MATRIX.md](../FORMULA_VERIFICATION_MATRIX.md)**: Statutory regulation formula matrix for Mumbai MCGM DCPR 2034 and Bangalore BBMP rules.
- **[FORMULA_AUDIT_REPORT.md](../FORMULA_AUDIT_REPORT.md)**: Mathematical audit of FSI calculations, buildable footprint clipping, and setback enforcement.

---

## 4. User Experience, Client Guides & Delivery Manuals

- **[PLANWISE_ENTERPRISE_USER_GUIDE.md](../PLANWISE_ENTERPRISE_USER_GUIDE.md)**: End-to-end customer manual covering plot intake, CAD auto-save, design options, BOQ explorer, and engineer review.
- **[PLANWISE_USER_GUIDE_EVIDENCE_MATRIX.md](../PLANWISE_USER_GUIDE_EVIDENCE_MATRIX.md)**: Cross-functional evidence matrix tying each user guide chapter to verified code lines and UI screenshots.
- **[FRONTEND_2_0_CUSTOMER_UX_REPORT.md](../FRONTEND_2_0_CUSTOMER_UX_REPORT.md)**: Audit of frontend React 19 views, dark-mode glassmorphic styling, and interactive HUDs.
- **[FRONTEND_2_0_API_REQUIREMENTS_AUDIT.md](../FRONTEND_2_0_API_REQUIREMENTS_AUDIT.md)**: API endpoint audit ensuring all frontend requests map to active FastAPI route handlers.

---

## 5. Milestone Delivery Reports (Phases 1–8)

- **[PHASE_8_CONTROLLED_PILOT_REPORT.md](../PHASE_8_CONTROLLED_PILOT_REPORT.md)**: Controlled pilot handoff, commercial lock, and deterministic delivery package.
- **[PHASE_8_PILOT_HANDOFF_QA.md](../PHASE_8_PILOT_HANDOFF_QA.md)**: Pilot quality assurance verification and invariant checks.
- **[PHASE_8_PREMIUM_UI_UX_REPORT.md](../PHASE_8_PREMIUM_UI_UX_REPORT.md)**: Design system tokens, micro-animations, and visual excellence audit.
- **[PHASE_7_ENGINEER_REVIEW_REPORT.md](../PHASE_7_ENGINEER_REVIEW_REPORT.md)**: Authoritative Phase 7 report covering G0–G8 verification gates, cryptographic fingerprints, and IFC4 BIM exports.
- **[M3_DEVELOPMENT_REPORT.md](../M3_DEVELOPMENT_REPORT.md)**: Milestone 3 report on model-linked QTO, CPWD DSR rate snapshots, and CPM scheduling.
- **[M2_DEVELOPMENT_REPORT.md](../M2_DEVELOPMENT_REPORT.md)**: Milestone 2 report on CP-SAT discrete floor plan generation and Pareto ranking.
- **[REAL_WORLD_DATA_TEST_REPORT.md](../REAL_WORLD_DATA_TEST_REPORT.md)**: Real-world boundary coordinates, zoning regulations, and integration test results for the canonical 1,100 sq ft plot.

---

## 6. Architecture & Reference Blueprints (PDF)

- `Real Estate Feasibility Platform Architecture.pdf`: Institutional architecture topology and data contract definitions.
- `Land Feasibility Platform Blueprint.pdf`: High-level platform functional blueprint.
- `real-estate-platform-engineering-masterplan_260923_072638.pdf`: Engineering master plan and lifecycle milestone gates.
- `Planwise Site Development Masterclass.pdf`: Standard operating procedures for plot intake and zoning compliance.
