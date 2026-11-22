"""Reviewer auth. Applicants submit without logging in; reviewers must be authenticated.

AUTH_MODE=none      open (local dev only)
AUTH_MODE=key       header  X-Reviewer-Key: <REVIEWER_KEY>
AUTH_MODE=supabase  header  Authorization: Bearer <Supabase access token>; the email must be in REVIEWER_EMAILS
"""
import hmac
import time

import httpx
from fastapi import HTTPException, Request

_TOKEN_CACHE: dict[str, tuple[float, str]] = {}
_TTL = 60.0


def _supabase_email(request: Request, token: str) -> str:
    c = request.app.state.c
    s = c.settings
    now = time.time()
    hit = _TOKEN_CACHE.get(token)
    if hit and now - hit[0] < _TTL:
        return hit[1]
    http = getattr(c, "auth_http", None) or httpx
    try:
        r = http.get(
            f"{s.supabase_url}/auth/v1/user",
            headers={"apikey": s.supabase_anon_key or s.supabase_service_key, "Authorization": f"Bearer {token}"},
            timeout=10.0,
        )
    except httpx.HTTPError:
        raise HTTPException(503, "Could not reach Supabase to verify the login.")
    if r.status_code != 200:
        raise HTTPException(401, "Invalid or expired login.")
    email = (r.json().get("email") or "").lower()
    _TOKEN_CACHE[token] = (now, email)
    return email


def require_reviewer(request: Request) -> str:
    """FastAPI dependency. Returns a reviewer label."""
    s = request.app.state.c.settings
    if s.auth_mode == "none":
        return "dev"
    if s.auth_mode == "key":
        given = request.headers.get("x-reviewer-key", "")
        if s.reviewer_key and hmac.compare_digest(given, s.reviewer_key):
            return "reviewer"
        raise HTTPException(401, "Missing or wrong reviewer key.")
    if s.auth_mode == "supabase":
        authz = request.headers.get("authorization", "")
        if not authz.lower().startswith("bearer "):
            raise HTTPException(401, "Missing login.")
        if not s.reviewer_emails:
            raise HTTPException(403, "REVIEWER_EMAILS is not configured on the server.")
        email = _supabase_email(request, authz[7:].strip())
        if email not in s.reviewer_emails:
            raise HTTPException(403, "This account is not allowed to review applications.")
        return email
    raise HTTPException(500, f"Unknown AUTH_MODE '{s.auth_mode}'.")
