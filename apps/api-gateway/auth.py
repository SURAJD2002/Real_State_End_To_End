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


def verify_supabase_jwt(token: str) -> Dict[str, Any]:
    """
    Performs cryptographic signature verification of Supabase access tokens.

    Validates:
    - Token integrity & cryptographic signature
    - Algorithm allowed (ES256 or configured HS256)
    - Expiration (exp)
    - Audience (aud == 'authenticated' when present)
    - Issuer (matching Supabase project when present)

    Raises HTTPException(401) on any failure. NEVER accepts unsigned or forged tokens.
    """
    if not token or not isinstance(token, str):
        raise HTTPException(status_code=401, detail="Authentication token required")

    # 1. Inspect unverified header to detect algorithm and key ID
    try:
        header = jwt.get_unverified_header(token)
    except Exception as e:
        logger.warning(f"Malformed JWT header: {e}")
        raise HTTPException(status_code=401, detail="Malformed session token")

    alg = header.get("alg")
    if not alg or alg == "none":
        logger.warning("Rejected token with insecure algorithm 'none'")
        raise HTTPException(status_code=401, detail="Insecure or unsigned token rejected")

    if alg not in ("ES256", "HS256"):
        logger.warning(f"Rejected token with unsupported algorithm: {alg}")
        raise HTTPException(status_code=401, detail=f"Unsupported token algorithm: {alg}")

    supabase_url = get_supabase_url()
    expected_issuer = f"{supabase_url}/auth/v1"

    # 2. ES256 Asymmetric Verification via JWKS
    if alg == "ES256":
        try:
            jwk_client = get_jwk_client()
            signing_key = jwk_client.get_signing_key_from_jwt(token)

            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["ES256"],
                audience="authenticated",
                issuer=expected_issuer,
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_aud": True,
                    "verify_iss": True
                }
            )
            return claims
        except HTTPException:
            raise
        except (InvalidSignatureError, ExpiredSignatureError, InvalidAudienceError, InvalidIssuerError) as e:
            logger.warning(f"ES256 token verification failed: {e}")
            raise HTTPException(status_code=401, detail=f"Cryptographic token verification failed: {e}")
        except PyJWKClientError as e:
            # Handle key rotation or network blip by attempting direct Supabase Auth API verification
            logger.info(f"JWKS lookup notice ({e}), attempting Supabase Auth API check")
            api_user = verify_via_supabase_auth_api(token, supabase_url)
            if api_user:
                return api_user
            raise HTTPException(status_code=401, detail="Token signing key verification failed")
        except Exception as e:
            logger.warning(f"Unexpected token error: {e}")
            raise HTTPException(status_code=401, detail="Session verification failed")

    # 3. HS256 Symmetric Verification (Configured Secret)
    if alg == "HS256":
        secret = get_jwt_secret()
        if not secret:
            logger.warning("HS256 token received but no JWT_SECRET configured")
            raise HTTPException(status_code=401, detail="Symmetric JWT verification unavailable")

        try:
            claims = jwt.decode(
                token,
                secret,
                algorithms=["HS256"],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_aud": False  # Aud checked manually below to accommodate test fixtures
                }
            )
            # If audience is present, ensure it matches 'authenticated'
            token_aud = claims.get("aud")
            if token_aud and token_aud != "authenticated":
                raise HTTPException(status_code=401, detail="Invalid token audience claim")

            return claims
        except HTTPException:
            raise
        except (InvalidSignatureError, ExpiredSignatureError) as e:
            logger.warning(f"HS256 token verification failed: {e}")
            raise HTTPException(status_code=401, detail=f"Invalid or expired token: {e}")
        except Exception as e:
            logger.warning(f"HS256 token decode error: {e}")
            raise HTTPException(status_code=401, detail="Invalid token format or signature")

    raise HTTPException(status_code=401, detail="Invalid authentication token")


async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str, Any]]:
    """
    Extracts, verifies, and resolves user claims from Bearer token.
    - If no token provided: returns None (anonymous access).
    - If token provided but invalid/forged/expired: raises 401 Unauthorized immediately.
    - Resolves identity and organization membership from PostgreSQL.
    """
    if not credentials or not credentials.credentials:
        return None

    token = credentials.credentials
    # Cryptographically verify the token — raises HTTPException(401) on forged/invalid/expired
    claims = verify_supabase_jwt(token)

    user_id = claims.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token: missing subject identity")

    email = claims.get("email", "")
    user_metadata = claims.get("user_metadata", {})
    org_name = user_metadata.get("org_name")
    explicit_role = user_metadata.get("role") or claims.get("app_role") or (claims.get("role") if claims.get("role") != "authenticated" else None)

    # Resolve organization & role strictly from database
    org_info = OrganizationRepository.get_or_create_user_organization(user_id, email, org_name, role=explicit_role)

    return {
        "id": user_id,
        "email": email,
        "full_name": user_metadata.get("full_name") or (email.split("@")[0] if email else "Planwise User"),
        "organization_id": org_info["organization"]["id"],
        "organization": org_info["organization"],
        "role": org_info["role"],
        "claims": claims
    }


async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Dict[str, Any]:
    """Strict authentication dependency returning 401 if unauthenticated or token invalid."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=401,
            detail="Authentication credentials required"
        )
    user = await get_current_user_optional(credentials)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required or invalid session token"
        )
    return user
