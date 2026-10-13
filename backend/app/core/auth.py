import os
import hmac
import hashlib
import time
import base64
import json
import logging
from typing import Optional, Dict, Any
from fastapi import Request, Response, Depends, HTTPException, status
from sqlalchemy.orm import Session
import httpx

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.services.user_service import user_service

logger = logging.getLogger(__name__)

COOKIE_NAME = "session_token"
TOKEN_MAX_AGE_SECONDS = 60 * 60 * 24 * 7  # 7 days


def hash_password(password: str) -> str:
    """
    Cryptographically hashes a learner password using PBKDF2-HMAC-SHA256 with random salt.
    """
    if not password:
        raise ValueError("Password cannot be empty.")
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return f"pbkdf2_sha256$100000${salt.hex()}${key.hex()}"


def verify_password(password: str, hashed: Optional[str]) -> bool:
    """
    Verifies a plain password against the stored PBKDF2-SHA256 hash.
    """
    if not hashed or not password:
        return False
    try:
        parts = hashed.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False
        iterations = int(parts[1])
        salt = bytes.fromhex(parts[2])
        expected_key = bytes.fromhex(parts[3])
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(key, expected_key)
    except Exception:
        return False


def verify_google_credential(credential: str) -> Dict[str, Any]:
    """
    Validates a Google OpenID Connect ID token from Google Identity Services (GIS).
    Extracts user identity (sub, email, name, picture).
    Tries google-auth library first, with fallback to Google tokeninfo endpoint.
    """
    if not credential:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google ID token credential is required.",
        )

    # 1. Try google-auth library
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests

        request = google_requests.Request()
        aud = settings.GOOGLE_CLIENT_ID if settings.GOOGLE_CLIENT_ID else None
        claims = id_token.verify_oauth2_token(credential, request, audience=aud)
        if claims:
            return claims
    except Exception as e:
        logger.debug(f"google-auth verify failed or client ID mismatch, trying tokeninfo endpoint: {e}")

    # 2. Direct verification via Google OAuth2 tokeninfo endpoint
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(
                "https://oauth2.googleapis.com/tokeninfo",
                params={"id_token": credential},
            )
            if resp.status_code == 200:
                claims = resp.json()
                if "error" in claims:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Google token rejected: {claims.get('error_description', claims.get('error'))}",
                    )
                if settings.GOOGLE_CLIENT_ID and claims.get("aud") != settings.GOOGLE_CLIENT_ID:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Google token audience does not match configured GOOGLE_CLIENT_ID.",
                    )
                return claims
            else:
                err_detail = resp.text
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid Google ID token: {err_detail}",
                )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to communicate with Google authentication services: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to verify identity with Google services. Please check your internet connection and try again.",
        )


def exchange_google_code(code: str, redirect_uri: Optional[str] = None) -> Dict[str, Any]:
    """
    Exchanges an OAuth2 authorization code with Google for an ID token and user claims.
    """
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth is not configured on the server (missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET).",
        )

    r_uri = redirect_uri or settings.GOOGLE_REDIRECT_URI
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": r_uri,
                    "grant_type": "authorization_code",
                },
            )
            if resp.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Google code exchange failed: {resp.text}",
                )
            data = resp.json()
            id_token_str = data.get("id_token")
            if not id_token_str:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Google did not return an ID token.",
                )
            return verify_google_credential(id_token_str)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during Google code exchange: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to exchange authorization code with Google.",
        )


def generate_session_token(user_id: int) -> str:
    """
    Generates a cryptographically signed session token.
    """
    payload = {
        "uid": int(user_id),
        "iat": int(time.time()),
    }
    payload_json = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(payload_json).decode("ascii").rstrip("=")
    sig = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        payload_b64.encode("ascii"),
        hashlib.sha256,
    ).hexdigest()
    return f"{payload_b64}.{sig}"


def verify_session_token(token: str) -> Optional[int]:
    """
    Verifies token signature and extracts authenticated user ID.
    """
    if not token or "." not in token:
        return None
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None
        payload_b64, sig = parts
        expected_sig = hmac.new(
            settings.SECRET_KEY.encode("utf-8"),
            payload_b64.encode("ascii"),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(sig, expected_sig):
            return None

        padded_b64 = payload_b64 + "=" * ((4 - len(payload_b64) % 4) % 4)
        payload_bytes = base64.urlsafe_b64decode(padded_b64.encode("ascii"))
        payload = json.loads(payload_bytes.decode("utf-8"))
        return int(payload.get("uid"))
    except Exception:
        return None


def set_auth_cookie(response: Response, token: str) -> None:
    """
    Sets an HTTP-only session cookie.
    """
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,  # False for local HTTP dev
        max_age=TOKEN_MAX_AGE_SECONDS,
        path="/",
    )


def clear_auth_cookie(response: Response) -> None:
    """
    Clears the session cookie on logout.
    """
    response.delete_cookie(
        key=COOKIE_NAME,
        path="/",
        samesite="lax",
    )


def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Resolves the authenticated learner from cookie or Authorization/X-Session-Token header.
    Returns None if not authenticated.
    """
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
    if not token:
        token = request.headers.get("X-Session-Token")

    if not token:
        return None

    user_id = verify_session_token(token)
    if not user_id:
        return None

    return user_service.get_user_by_id(db, user_id)


def require_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """
    Enforces authentication requirement for protected endpoints.
    Raises 401 Unauthorized if user is not authenticated.
    """
    user = get_current_user_optional(request, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please sign in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
