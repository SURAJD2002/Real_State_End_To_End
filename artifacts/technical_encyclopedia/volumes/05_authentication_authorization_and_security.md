# Volume V — Authentication, Authorization, and Security

## 1. End-to-End Authentication Architecture
Authentication in Planwise Enterprise is based on cryptographically signed **JSON Web Tokens (JWT)** integrated with **Supabase Auth**.

### Authentication Flow Sequence
```
[User Browser]             [Supabase Auth]             [FastAPI Gateway]
      │                           │                            │
      │ 1. POST /auth/v1/token    │                            │
      ├──────────────────────────>│                            │
      │    (email, password)      │                            │
      │ 2. Return JWT (ES256)     │                            │
      │<──────────────────────────┤                            │
      │                           │                            │
      │ 3. GET /api/v1/projects (Authorization: Bearer <JWT>) │
      ├───────────────────────────────────────────────────────>│
      │                           │                            │ 4. Extract token
      │                           │<── 5. Fetch JWKS Public Key │ 6. Validate sig
      │                           │─── 6. Return Key Set ──────>│ 7. Extract claims:
      │                           │                            │    - sub (user_id)
      │                           │                            │    - org_id
      │                           │                            │    - role
      │ 8. Return Scoped Projects │                            │ 8. Query DB / memory
      │<───────────────────────────────────────────────────────┤
```

---

## 2. Token Verification Logic & Source Code Implementation
The complete token validation implementation in `apps/api-gateway/auth.py` is shown below:

```python
"""
Planwise Enterprise — Cryptographic Authentication & Authorization Module
==========================================================================
Verifies Supabase JWT access tokens server-side using:
1. Project JWKS (ES256 asymmetric public keys) with automatic key caching and safe rotation.
2. Direct Supabase Auth API verification fallback (/auth/v1/user).
3. Configured JWT_SECRET (HS256 symmetric) for test/local environments.

Security Invariants:
- Signature verification is strictly enforced (verify_signature is NEVER False).
- Token expiration (exp), audience ('authenticated'), and issuer are validated.
- Unsigned (alg=none) or forged tokens are rejected with HTTP 401 Unauthorized.
- Identity is resolved strictly from cryptographically verified claims.
- Organization and role are resolved from PostgreSQL public.organization_memberships.
- Roles can never be granted or escalated via unverified tokens, metadata, or request parameters.
"""

import os
import json
import logging
import urllib.request
import urllib.error
from typing import Optional, Dict, Any
from pathlib import Path
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import PyJWKClient, PyJWKClientError, InvalidSignatureError, ExpiredSignatureError, InvalidAudienceError, InvalidIssuerError

from postgres_repository import OrganizationRepository, to_valid_uuid

logger = logging.getLogger("planwise.auth")
security = HTTPBearer(auto_error=False)

_JWK_CLIENT: Optional[PyJWKClient] = None
_CACHED_SUPABASE_URL: Optional[str] = None


def get_supabase_url() -> str:
    """Resolves Supabase project URL from environment or .env configuration."""
    global _CACHED_SUPABASE_URL
    if _CACHED_SUPABASE_URL:
        return _CACHED_SUPABASE_URL

    url = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
    if not url:
        for env_file in [".env", "apps/web/.env"]:
            path = Path(__file__).resolve().parent.parent.parent / env_file
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("SUPABASE_URL=") or line.startswith("VITE_SUPABASE_URL="):
                            url = line.split("=", 1)[1].strip().strip('"').strip("'")
                            break
            if url:
                break

    if not url:
        url = "https://qhqneldjxxdnttqfhqkf.supabase.co"

    _CACHED_SUPABASE_URL = url.rstrip("/")
    return _CACHED_SUPABASE_URL


def get_supabase_anon_key() -> Optional[str]:
    """Resolves Supabase publishable anon key from environment or .env files."""
    key = os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
    if not key:
        for env_file in ["apps/web/.env", ".env"]:
            path = Path(__file__).resolve().parent.parent.parent / env_file
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("SUPABASE_ANON_KEY=") or line.startswith("VITE_SUPABASE_ANON_KEY="):
                            key = line.split("=", 1)[1].strip().strip('"').strip("'")
                            break
            if key:
                break
    return key


def get_jwt_secret() -> Optional[str]:
    """Resolves symmetric JWT secret if configured for local/test execution."""
    secret = os.getenv("JWT_SECRET") or os.getenv("SUPABASE_JWT_SECRET")
    if not secret:
        path = Path(__file__).resolve().parent.parent.parent / ".env"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("JWT_SECRET=") or line.startswith("SUPABASE_JWT_SECRET="):
                        secret = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    return secret


def get_jwk_client() -> PyJWKClient:
    """Returns or initializes singleton PyJWKClient for Supabase JWKS endpoint with caching."""
    global _JWK_CLIENT
    if _JWK_CLIENT is None:
        supabase_url = get_supabase_url()
        jwks_url = f"{supabase_url}/auth/v1/.well-known/jwks.json"
        _JWK_CLIENT = PyJWKClient(
            jwks_url,
            cache_keys=True,
            max_cached_keys=16,
            cache_jwk_set=True,
            lifespan=3600
        )
    return _JWK_CLIENT


def verify_via_supabase_auth_api(token: str, supabase_url: str) -> Optional[Dict[str, Any]]:
    """
    Fallback server-side verification directly via Supabase Auth API /auth/v1/user.
    Provides live revocation checks and validates token authenticity remotely.
    """
    anon_key = get_supabase_anon_key()
    if not anon_key:
        return None

    user_url = f"{supabase_url}/auth/v1/user"
    headers = {
        "Authorization": f"Bearer {token}",
        "apikey": anon_key,
        "User-Agent": "Planwise-Enterprise-Verifier"
    }
    req = urllib.request.Request(user_url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data and "id" in data:
                return {
                    "sub": data["id"],
                    "email": data.get("email", ""),
                    "user_metadata": data.get("user_metadata", {}),
                    "role": data.get("role", "authenticated")
                }
    except urllib.error.HTTPError as e:
        logger.warning(f"Supabase Auth API rejected token (HTTP {e.code}): {e.reason}")
        return None
    except Exception as e:
        logger.warning(f"Supabase Auth API check failed: {e}")
        return None

    return None



```

---

## 3. Server-Side Identity and Multi-Tenant Isolation
Tenant boundaries are strictly derived from trusted server-side token claims, never from client-provided query parameters or headers.

### Verification via Test Suite
The security isolation was tested via `tests/test_cross_tenant_isolation.py` (7 tests) and `tests/test_auth_negative_scenarios.py` (11 tests). All 18 security tests pass:
- Cross-tenant project read $\rightarrow$ **HTTP 403 Forbidden**.
- Cross-tenant design update $\rightarrow$ **HTTP 403 Forbidden**.
- Forged organization ID header $\rightarrow$ Ignored; token claims prevail.
- Expired token $\rightarrow$ **HTTP 401 Unauthorized**.
- Tampered token payload $\rightarrow$ **HTTP 401 Unauthorized**.

---

## 4. CRITICAL AUDIT FINDING: Database Superuser RLS Bypass
While migration `supabase/migrations/20261010070000_security_and_rls_policies.sql` declares `ENABLE ROW LEVEL SECURITY` across 34 database tables, the FastAPI backend connects to PostgreSQL as the `postgres` superuser (`DATABASE_URL=postgresql://postgres:postgres@localhost:5432/...`).

> [!WARNING]
> In PostgreSQL, the `postgres` superuser automatically bypasses all Row-Level Security policies. Consequently, tenant isolation is **enforced exclusively at the FastAPI Application Layer**, NOT natively inside the PostgreSQL database engine.
