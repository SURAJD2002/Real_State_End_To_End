# Planwise Enterprise — Comprehensive Integration & Security Test Report

**Execution Timestamp:** 2026-10-10T09:10:00+05:30
**Environment:** Python 3.14.4 (`./.venv`), Node.js v20.x, Supabase CLI v2.101.0
**Target Database:** Linked Remote Supabase (`qhqneldjxxdnttqfhqkf`)
**Overall Result:** ALL TEST SUITES PASSING (0 Failures, 0 Errors)

---

## 1. Test Execution Summary

| Test Suite File | Domain / Focus | Tests Run | Result | Duration | Exit Code |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `tests/test_cross_tenant_isolation.py` | Multi-Tenant Database RLS Isolation & Role Boundary | 7 | **PASS** | 89.59s | `0` |
| `tests/test_persistence_and_auth_workflow.py` | E2E Auth, Tenant Isolation, CAD Persistence, DAG & API Restart | 6 | **PASS** | 104.45s | `0` |
| `tests/test_phase8_1_persistence.py` | Engineer Reviews, Verification Gates & Release Immutability | 7 | **PASS** | 1.25s | `0` |
| `tests/test_plot_area_regression.py` | 1,100 sq ft Bandra Plot Integrity & API Dataflow | 4 | **PASS** | 43.36s | `0` |
| `tests/test_m1_site_and_rules.py` + `tests/test_canonical_building_model.py` + `tests/test_drawing_compiler.py` + `tests/test_pilot_handoff_integrity.py` | Site Evidence, CBM Compiler, Architectural Renderer & Handoff Cryptography | 73 | **PASS** | 4.22s | `0` |
| `apps/web: npm run build` | Frontend TypeScript Type-Checking & Vite Production Bundle | 1 build | **PASS** | 4.22s | `0` |
| **Total** | **Combined Pilot-Readiness Verification Suite** | **97 Tests** | **PASS** | **~247s** | **`0`** |

---

## 2. Evidence-Based Test Suite Details

### 2.1 Cross-Tenant Isolation Suite (`test_cross_tenant_isolation.py`)
- **Command:** `./.venv/bin/python -m unittest tests/test_cross_tenant_isolation.py`
- **Output:**
  ```text
  .......
  ----------------------------------------------------------------------
  Ran 7 tests in 89.589s

  OK
  ```
- **Verified Invariants:**
  1. `anon` role receives 0 rows across `projects` and `generated_reports`.
  2. Authenticated user for Organization A can see Project A and is strictly blocked from seeing Project B.
  3. User A cross-tenant `UPDATE` on Project B is rejected with 0 rows updated.
  4. User A cross-tenant `INSERT` into Organization B is rejected by `WITH CHECK` constraint.
  5. User A cannot view generated reports of Organization B.
  6. Service role retains full administrative access for backend asynchronous workers.

### 2.2 Persistence and Auth Workflow Suite (`test_persistence_and_auth_workflow.py`)
- **Command:** `./.venv/bin/python -m unittest tests/test_persistence_and_auth_workflow.py`
- **Output:**
  ```text
  ......
  ----------------------------------------------------------------------
  Ran 6 tests in 104.452s

  OK
  ```
- **Verified Invariants:**
  1. `test_01_unauthenticated_session`: Unauthenticated requests to `/api/v1/auth/session` return `{ authenticated: false }`.
  2. `test_02_authenticated_session_and_org_provisioning`: Valid JWT token provisions organization and assigns `OWNER` role.
  3. `test_03_tenant_project_creation_and_isolation`: Organization A project cannot be listed by Organization B. Cross-tenant GET returns `403 Forbidden`.
  4. `test_04_cad_geometry_auto_save_and_persistence`: CAD parcel coordinates persist with PostGIS polygon geometry and version progression.
  5. `test_05_feasibility_dag_execution_and_persistence`: Statutory feasibility DAG executes Mumbai DCPR 2034 rules, transitions project to `COMPLETED`, and saves traces.
  6. `test_06_process_restart_persistence_resilience`: In-memory volatile caches purged (`del PROJECTS_DB[proj_id]`); subsequent request successfully rehydrates project and parcel from PostgreSQL.

### 2.3 Phase 8.1 Engineer Review & Release Ledger Suite (`test_phase8_1_persistence.py`)
- **Command:** `./.venv/bin/python -m unittest tests/test_phase8_1_persistence.py`
- **Output:**
  ```text
  .......
  ----------------------------------------------------------------------
  Ran 7 tests in 1.245s

  OK
  ```
- **Verified Invariants:**
  1. Review creation and G0–G6 gate evaluation persistence in PostgreSQL.
  2. Raw database table integrity verification without relying on memory state.
  3. Process restart persistence for engineer reviews and release fingerprints.
  4. Release immutability (frozen design & deterministic cryptographic hash).
  5. Fail-closed error handling when database operations are interrupted.

### 2.4 Plot Area & Downstream Regression Suite (`test_plot_area_regression.py`)
- **Command:** `./.venv/bin/python -m unittest tests/test_plot_area_regression.py`
- **Output:**
  ```text
  ....
  ----------------------------------------------------------------------
  Ran 4 tests in 43.364s

  OK
  ```
- **Verified Invariants:**
  1. 1,100 sq ft plot area preserved end-to-end without rounding distortion.
  2. Ground coverage and setback evaluations remain mathematically consistent.
  3. Direct Python function invocation of API gateway endpoints functions cleanly with `isinstance(current_user, dict)` safeguards.

### 2.5 Core Domain Engine & Architectural Regressions
- **Command:** `./.venv/bin/python -m unittest tests/test_m1_site_and_rules.py tests/test_canonical_building_model.py tests/test_drawing_compiler.py tests/test_pilot_handoff_integrity.py`
- **Output:**
  ```text
  .........................................................................
  ----------------------------------------------------------------------
  Ran 73 tests in 4.224s

  OK
  ```

### 2.6 Web Application Production Compilation
- **Command:** `npm run build` (in `apps/web`)
- **Output:**
  ```text
  > @feasibility/web@1.0.0 build
  > tsc && vite build

  vite v6.4.4 building for production...
  ✓ 1996 modules transformed.
  dist/index.html                     1.36 kB │ gzip:   0.72 kB
  dist/assets/index-ng7c5cdE.css     66.75 kB │ gzip:   9.84 kB
  dist/assets/index-cI4LXPvE.js   2,775.97 kB │ gzip: 746.26 kB
  ✓ built in 4.22s
  ```
