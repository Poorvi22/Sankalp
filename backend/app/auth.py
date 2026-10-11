import os
from datetime import datetime, timedelta, timezone

from uuid import uuid4
from typing import Callable

import jwt
from pwdlib import PasswordHash

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import User, RevokedToken


# =========================================================
# CONFIGURATION
# =========================================================

JWT_SECRET = os.getenv("BIZPILOT_JWT_SECRET")

if not JWT_SECRET or len(JWT_SECRET) < 32:
    raise RuntimeError(
        "Set BIZPILOT_JWT_SECRET to a randomly generated secret "
        "of at least 32 characters before starting the backend."
    )

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 30

password_hasher = PasswordHash.recommended()
bearer_scheme = HTTPBearer(auto_error=False)


# =========================================================
# PASSWORD SECURITY
# =========================================================

def hash_password(password: str) -> str:
    """Return a secure password hash."""

    if len(password) < 12:
        raise ValueError(
            "Password must contain at least 12 characters."
        )

    return password_hasher.hash(password)


def verify_password(
    password: str,
    hashed_password: str,
) -> bool:
    """Verify a password against its stored hash."""

    try:
        return password_hasher.verify(
            password,
            hashed_password,
        )
    except (ValueError, TypeError):
        return False


# =========================================================
# JWT TOKEN CREATION
# =========================================================

def create_access_token(
    user_id: str,
    username: str,
    role: str,
) -> str:
    """Create a signed, time-limited access token."""

    if role not in ("user", "manager"):
        raise ValueError("Invalid authentication role.")

    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "jti": str(uuid4()),
        "iat": now,
        "exp": now + timedelta(
            minutes=ACCESS_TOKEN_MINUTES
        ),
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )


# =========================================================
# JWT TOKEN VALIDATION
# =========================================================

def decode_access_token(token: str) -> dict:
    """Validate and decode a signed access token."""

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            options={
                "require": [
                    "sub",
                    "username",
                    "role",
                    "jti",
                    "iat",
                    "exp",
                ]
            },
        )

        if payload["role"] not in ("user", "manager"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication role.",
                headers={
                    "WWW-Authenticate": "Bearer"
                },
            )

        return payload

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        ) from None


# =========================================================
# CURRENT USER AUTHENTICATION
# =========================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db),
) -> dict:
    """
    Validate the token, check revocation, and retrieve
    the current account and role from the database.
    """

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    # Validate the signature and expiration.
    payload = decode_access_token(
        credentials.credentials
    )

    # Reject a token revoked during logout.
    revoked = (
        db.query(RevokedToken)
        .filter(
            RevokedToken.jti == payload["jti"]
        )
        .first()
    )

    if revoked is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revoked. Please log in again.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    # Validate the user identifier.
    try:
        user_id = int(payload["sub"])
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identity.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        ) from None

    # Check the current database account.
    user = db.get(User, user_id)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is unavailable.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    # Do not trust a role supplied by the client.
    if user.role not in ("user", "manager"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid account role.",
        )

    # Use the current database role rather than a stale JWT role.
    return {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role,
        "jti": payload["jti"],
    }


# =========================================================
# ROLE-BASED AUTHORIZATION
# =========================================================

def require_roles(*allowed_roles: str) -> Callable:
    """
    Create a FastAPI dependency that permits only
    explicitly authorized roles.
    """

    valid_roles = {"user", "manager"}

    if not allowed_roles:
        raise ValueError(
            "At least one permitted role must be specified."
        )

    if not set(allowed_roles).issubset(valid_roles):
        raise ValueError(
            "One or more permitted roles are invalid."
        )

    def role_checker(
        current_user: dict = Depends(get_current_user),
    ) -> dict:
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You do not have permission "
                    "to perform this operation."
                ),
            )

        return current_user

    return role_checker