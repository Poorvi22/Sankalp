from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordRequestForm,
)
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.auth import (
    create_access_token,
    decode_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from backend.app.database import get_db
from backend.app.models import RevokedToken, User


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)

# HTTP Bearer authentication for logout.
bearer_scheme = HTTPBearer(auto_error=False)


# --------------------------------------------------
# REQUEST AND RESPONSE MODELS
# --------------------------------------------------

class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# --------------------------------------------------
# REGISTER
# --------------------------------------------------

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    username = request.username.strip()
    email = str(request.email).strip().lower()

    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username cannot be empty.",
        )

    existing_user = db.scalar(
        select(User).where(
            (User.username == username)
            | (User.email == email)
        )
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email is already registered.",
        )

    try:
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(request.password),
            role="user",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    except Exception:
        db.rollback()
        raise

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
    )


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@router.post(
    "/login",
    response_model=LoginResponse,
)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.scalar(
        select(User).where(
            User.username == form.username
        )
    )

    if (
        user is None
        or not verify_password(
            form.password,
            user.password_hash,
        )
        or not user.is_active
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.role not in ("user", "manager"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has an invalid role.",
        )

    access_token = create_access_token(
        user_id=str(user.id),
        username=user.username,
        role=user.role,
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
        ),
    )


# --------------------------------------------------
# CURRENT USER PROFILE
# --------------------------------------------------

@router.get(
    "/me",
    response_model=UserResponse,
)
def get_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = int(current_user["sub"])
    user = db.get(User, user_id)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is unavailable.",
        )

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
    )


# --------------------------------------------------
# LOGOUT AND TOKEN REVOCATION
# --------------------------------------------------

@router.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Decode the token supplied in the Authorization header.
    payload = decode_access_token(
        credentials.credentials
    )

    # Ensure the token belongs to the authenticated user.
    if payload["sub"] != current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token identity mismatch.",
        )

    token_id = payload["jti"]

    existing_token = db.scalar(
        select(RevokedToken).where(
            RevokedToken.jti == token_id
        )
    )

    if existing_token is None:
        expires_at = datetime.fromtimestamp(
            payload["exp"],
            tz=timezone.utc,
        )

        try:
            revoked_token = RevokedToken(
                jti=token_id,
                expires_at=expires_at,
            )

            db.add(revoked_token)
            db.commit()

        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to revoke access token.",
            )

    return {
        "message": "Logout successful. Access token revoked.",
        "user_id": current_user["sub"],
    }