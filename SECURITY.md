# Security Policy & Responsible Disclosure

Planwise Enterprise takes security, data isolation, and cryptographic integrity seriously. We appreciate the responsible disclosure of security issues by researchers, engineers, and community members.

---

## 1. Supported Versions

Security updates and patches are actively maintained on the following branches:

| Version / Branch | Supported | Notes |
| :--- | :---: | :--- |
| `main` | ✅ Yes | Stable release branch |
| `feature/complete-project-documentation` | ✅ Yes | Active development branch |
| Releases `< v0.7.0` | ❌ No | Deprecated development prototypes |

---

## 2. Core Security Architecture & Invariants

Planwise Enterprise implements strict zero-trust principles across its services:

1. **Cryptographic Token Verification:**
   - Server-side JWT signature verification is mandatory (`verify_signature = True`).
   - Asymmetric **ES256** access tokens issued by Supabase Auth are validated against the project's public JSON Web Key Set (JWKS) with automatic key caching and rotation.
   - Unsigned tokens (`alg=none`), forged tokens, and tokens with invalid audiences (`aud != 'authenticated'`) or expired timestamps are rejected with HTTP 401.
2. **Tenant Isolation & Zero-Trust RBAC:**
   - User identity is resolved strictly from verified token claims (`sub`).
   - Organization membership and permissions are read from PostgreSQL `public.organization_memberships`.
   - Client-provided roles in request bodies, query parameters, or JWT metadata are strictly ignored.
   - Cross-tenant read/write attempts to projects, parcels, feasibility evaluations, or reports are blocked with HTTP 403.
3. **Database Row Level Security (RLS):**
   - All 34 public domain tables enforce `rowsecurity = true`.
   - Security-definer helper functions (e.g. `public.get_user_organization_ids()`) strictly pin `search_path = pg_catalog, public`.
   - Anonymous access (`anon` role) is default-denied across all tenant and project tables.
4. **Credential & Secret Protection:**
   - Production secrets, service-role keys, and database passwords must never be stored in Git.
   - Pre-commit hygiene scans verify that `.env` and sensitive configurations remain uncommitted.

---

## 3. Reporting a Vulnerability

If you discover a potential security vulnerability, please do **NOT** open a public issue, discussion, or pull request.

Instead, please submit a confidential report following these guidelines:

1. **Contact:** Email the engineering security lead or submit a GitHub Private Vulnerability Advisory at:
   - Repository: [https://github.com/SURAJD2002/Real_State_End_To_End/security/advisories](https://github.com/SURAJD2002/Real_State_End_To_End/security/advisories)
2. **Information to Include:**
   - Clear description of the vulnerability and affected component (e.g., API Gateway, RLS Policy, Frontend Auth Guard).
   - Minimal proof-of-concept (PoC) code or step-by-step reproduction instructions.
   - Assessment of potential impact (e.g., cross-tenant data leak, privilege escalation, unauthenticated bypass).
   - Any suggested remediations or mitigations.
3. **Safe Disclosure Guidelines:**
   - Do not attempt to access, modify, or destroy real customer data.
   - Do not perform denial-of-service (DoS) attacks against hosted infrastructure.
   - Never print or include real secrets, access tokens, or private user data in bug reports.

---

## 4. Response & Remediation Timelines

- **Acknowledgement:** Within 48 hours of initial report receipt.
- **Triage & Assessment:** Severity assessment (P0 Critical, P1 High, P2 Moderate) within 3 business days.
- **Fix & Patch Deployment:** Critical vulnerabilities (P0) are remediated and verified within 7 business days.
- **Public Disclosure:** Coordinated disclosure occurs only after patches are tested and deployed.
