# Volume XXI — Security Findings, Risks, and Remediation Plan

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
