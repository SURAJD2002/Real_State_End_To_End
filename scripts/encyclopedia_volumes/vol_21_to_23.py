"""
Planwise Enterprise — Technical Encyclopedia Volumes XXI - XXIII
Volume XXI: Security Findings, Risks, and Remediation Plan
Volume XXII: Developer Onboarding and Change Impact
Volume XXIII: Roadmap and Final Readiness Verdict
"""

def get_volume_21() -> dict:
    md = """# Volume XXI — Security Findings, Risks, and Remediation Plan

## 1. Prioritized Security Risk Register

| Risk ID | Severity | Subsystem Affected | Vulnerability Description & Finding | Business & Operational Impact | Remediation Action Required |
| :---: | :---: | :--- | :--- | :--- | :--- |
| **SEC-01** | **CRITICAL** | Database Layer | **PostgreSQL Superuser Connection Bypasses RLS:** API Gateway connects via `postgres` superuser, disabling native RLS on 34 tables. | Malicious SQL injection or compromised backend can read across all enterprise tenants. | Create unprivileged app user (`planwise_app`) and inject `SET LOCAL request.jwt.claims` per session. |
| **SEC-02** | **HIGH** | Persistence | **In-Memory Store Data Loss Risk:** API Gateway uses in-memory dictionaries (`PROJECTS_DB`, `RELEASES_DB`) alongside PostgreSQL. | Server restart or container re-deployment resets unpersisted project state. | Refactor all CRUD operations to execute exclusively through PostgreSQL repository pattern. |
| **SEC-03** | **HIGH** | Authentication | **Offline Fallback Secret in Config Templates:** Staging configurations contain local fallback symmetric secrets for HS256. | Compromise of symmetric secret permits forgeable JWT tokens across organizations. | Enforce mandatory asymmetric ES256 JWKS validation in production mode with zero local fallback. |
| **SEC-04** | **MEDIUM** | Review Gates | **G7 & G8 Gates Missing in API:** Documentation references G0–G8, but API and schema enforce only G0–G6. | Confusion regarding statutory completion sign-off and site release authority. | Implement dedicated G7/G8 review endpoints or formally clarify CPM scheduling scope in docs. |
| **SEC-05** | **MEDIUM** | Municipal Auto-Filing| **Lack of PreDCR / AutoDCR API Integration:** Platform cannot automatically submit plans to municipal portals. | Liasoning consultants must manually transcribe generated drawings into municipal CAD portals. | Build municipal CAD export filter conforming to municipal PreDCR layer and polyline standards. |
| **SEC-06** | **LOW** | Engineering Scope | **Lack of 3D Finite Element Analysis (FEA):** System sizes columns by thumb rules, not dynamic FEA simulation. | Structural engineering certification cannot be automated; requires registered PE review. | Maintain explicit statutory disclaimer in all release manifests and client contracts. |

---

## 2. In-Depth Threat Modeling & Exploit Scenarios

### 2.1 Threat Scenario SEC-01: Native Database RLS Bypass
- **Vulnerability:** Migration `07` declares `CREATE POLICY tenant_isolation_policy ON projects USING (org_id = current_user_org_id());`. However, because the backend pool connects as the superuser `postgres`, PostgreSQL internal rule evaluation skips RLS checks completely.
- **Proof of Concept:** If an attacker executes a SQL injection through a vulnerable reporting query, `SELECT * FROM projects;` will return all projects across all enterprise tenants rather than raising a permission denied error.
- **Remediation SQL:**
  ```sql
  -- Step 1: Create restricted application user
  CREATE ROLE planwise_app WITH LOGIN PASSWORD 'strong_password' NOBYPASSRLS;
  GRANT USAGE ON SCHEMA public TO planwise_app;
  GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO planwise_app;

  -- Step 2: Session middleware
  -- On every connection checkout:
  SET LOCAL "request.jwt.claims" = '{"sub": "user-uuid", "org_id": "org-uuid"}';
  ```

### 2.2 Threat Scenario SEC-02: State Loss via Container Cycling
- **Vulnerability:** `PROJECTS_DB` in `main.py` is a Python dictionary in the process heap.
- **Consequence:** In a Kubernetes cluster where pods cycle or scale up/down, projects created in Pod A do not exist in Pod B, leading to intermittent 404 errors for enterprise users.
- **Remediation:** Remove in-memory fallback dictionaries and ensure every project mutation commits to the PostgreSQL `projects` table within an ACID transaction.

---

## 3. Actionable Zero-Trust Remediation Roadmap
1. **Phase 1 (Immediate P0):** Create unprivileged PostgreSQL role `planwise_app` with `NOBYPASSRLS`. Configure session pooling to execute `SET LOCAL "request.jwt.claims" = %s`.
2. **Phase 2 (Immediate P0):** Eliminate in-memory dictionary state (`PROJECTS_DB`) in `apps/api-gateway/main.py`. Ensure all mutations execute in database transactions with rollback support.
3. **Phase 3 (P1):** Disallow symmetric HS256 token verification in production environment profiles.
"""
    return {"title": "Volume XXI — Security Findings, Risks, and Remediation Plan", "md": md}


def get_volume_22() -> dict:
    md = """# Volume XXII — Developer Onboarding and Change Impact

## 1. Practical Developer Modification Guides

### 1.1 How to Add a New REST API Endpoint
1. Open `apps/api-gateway/main.py`.
2. Define the route handler with appropriate Pydantic input/output schemas:
   ```python
   @app.post("/api/v1/projects/{project_id}/custom-analysis", response_model=AnalysisResponse)
   async def run_custom_analysis(
       project_id: str,
       payload: AnalysisRequest,
       current_user: dict = Depends(get_current_user)
   ):
       project = await get_project_by_id(project_id, current_user["organization_id"])
       result = compute_analysis(project, payload)
       return result
   ```
3. Add a corresponding test in `tests/test_api_gateway.py` verifying status codes, schema validation, and cross-tenant isolation.
4. Run tests: `.venv/bin/python3 -m unittest tests/test_api_gateway.py`.

### 1.2 How to Add a Field to the Canonical Building Model (CBM)
1. Open `packages/schemas/building_model.py`.
2. Add the field to the relevant Pydantic model with a default value to maintain backward compatibility:
   ```python
   class Room(BaseModel):
       id: str
       name: str
       type: RoomType
       polygon_2d: List[Point2D]
       finish_material: Optional[str] = "vitrified_tiles" # New field
   ```
3. Update `workers/qto/qto_engine.py` if the field affects quantity takeoff or cost calculations.
4. Update `tests/test_cbm_schema_validation.py` to assert correct serialization and SHA-256 hashing.

### 1.3 How to Add a New Municipal Statutory Rule Pack
1. Create a new JSON definition in `packages/rules/` (e.g. `pune_pmc_2026.json`).
2. Register the rule pack in `workers/regulation/rule_engine.py`:
   ```python
   RULE_PACK_MAPPINGS["PUNE_PMC_2026"] = RULES_DIR / "pune_pmc_2026.json"
   ```
3. Add unit tests in `tests/test_statutory_rules.py` covering boundary plot sizes under Pune regulations.
"""
    return {"title": "Volume XXII — Developer Onboarding and Change Impact", "md": md}


def get_volume_23() -> dict:
    md = """# Volume XXIII — Roadmap and Final Readiness Verdict

## 1. Final Operational Readiness Assessment

| Evaluation Dimension | Assessed Maturity | Production Readiness Status | Primary Grounding Evidence |
| :--- | :---: | :---: | :--- |
| **Computational Algorithms** | Production Grade | **READY FOR PRODUCTION** | 230 passing tests; deterministic CP-SAT & Manifold3D kernels |
| **Architectural Generation** | Production Grade | **READY FOR PRODUCTION** | 9-sheet vector drawing compiler; verified PDF artifacts |
| **Quantity Takeoff (QTO)** | Production Grade | **READY FOR PRODUCTION** | IS 1200 opening deduction logic; deterministic BOQ JSON |
| **BIM Interoperability** | Production Grade | **READY FOR PRODUCTION** | ISO 16739-1 IFC4 SPF model emission; validated syntax |
| **Frontend User Experience** | Staging Grade | **READY FOR PILOT DEPLOYMENT** | 12-phase headless Chrome E2E verified; 13 screenshots |
| **Authentication & RBAC** | Staging Grade | **READY FOR PILOT DEPLOYMENT** | JWT validation; role enforcement; server-side org claims |
| **Database Tenancy (RLS)** | Development / Pilot | **BLOCKED FOR ZERO-TRUST PROD**| Superuser connection bypasses PostgreSQL native RLS |
| **State Persistence** | Development / Pilot | **BLOCKED FOR CLOUD HORIZONTAL SCALE**| In-memory hybrid lookup dictionaries coexisting with DB |

---

## 2. Definitive Audit Verdict
**Planwise Enterprise is VERIFIED and APPROVED for Controlled Staging, Internal Engineering Pilots, and Customer Demonstrations.**

Full enterprise zero-trust production release is conditionally withheld pending the remediation of two core architectural blockers:
1. Migrating database connection pooling to an unprivileged role to activate native PostgreSQL Row-Level Security.
2. Complete elimination of in-memory dictionary state (`PROJECTS_DB`) in favor of pure database repository transactions.

---

## 3. Statutory Engineering and Legal Liability Disclaimer
Planwise Enterprise is an advanced computational architectural and civil engineering optimization platform. All floor plans, statutory setback envelopes, quantity estimates, and 3D building models generated by the system constitute **advisory preliminary engineering data**. 

In accordance with the National Building Code of India (NBC 2016), the Council of Architecture (CoA) regulations, and municipal bye-laws:
- All generated drawings and calculations must be formally reviewed, approved, and stamped with physical or certified digital wet-ink signatures by a licensed Architect and registered Chartered Structural Engineer prior to physical site groundbreaking or construction execution.
- Planwise Enterprise and its maintainers assume no legal liability for physical construction defects, municipal approval rejections, or site accidents arising from the direct execution of uncertified preliminary models.
"""
    return {"title": "Volume XXIII — Roadmap and Final Readiness Verdict", "md": md}
