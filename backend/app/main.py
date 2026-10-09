
from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pwdlib import PasswordHash
from pydantic import BaseModel
from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from .database import Base, engine, get_db

app = FastAPI(title="BizPilot AI Backend", version="0.1.0")

# Development defaults only. Set BIZPILOT_SECRET_KEY in your
# environment before using this beyond local development.
SECRET_KEY = "dev-only-change-this-secret-before-deployment"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60

password_hash = PasswordHash.recommended()
bearer_scheme = HTTPBearer()

ROLES = ("Owner", "Manager", "Warehouse", "Viewer")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String(80), unique=True, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="Viewer")


Base.metadata.create_all(bind=engine)


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    role: str


class RoleUpdate(BaseModel):
    role: Literal["Owner", "Manager", "Warehouse", "Viewer"]


def user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        role=user.role,
    )


def create_token(user_id: int) -> str:
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(
        {"sub": str(user_id), "exp": expires},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        user_id = int(payload["sub"])
    except (JWTError, ValueError, TypeError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def require_owner(user: User = Depends(get_current_user)) -> User:
    if user.role != "Owner":
        raise HTTPException(status_code=403, detail="Owner access required")
    return user


@app.get("/health")
def health():
    return {"status": "ok", "service": "BizPilot AI Backend"}


@app.post("/auth/register", response_model=UserResponse)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    username = request.username.strip()

    if len(username) < 3 or len(username) > 80:
        raise HTTPException(
            status_code=400,
            detail="Username must be 3 to 80 characters",
        )

    if len(request.password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters",
        )

    if db.scalar(select(User).where(User.username == username)):
        raise HTTPException(status_code=409, detail="Username already exists")

    # Local-demo bootstrap: first registered account becomes Owner.
    # Every subsequent account is a Viewer until an Owner changes its role.
    first_user = db.scalar(select(User.id).limit(1)) is None
    user = User(
        username=username,
        password_hash=password_hash.hash(request.password),
        role="Owner" if first_user else "Viewer",
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user_response(user)


@app.post("/auth/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    user = db.scalar(
        select(User).where(User.username == request.username.strip())
    )

    if user is None or not password_hash.verify(
        request.password, user.password_hash
    ):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {
        "access_token": create_token(user.id),
        "token_type": "bearer",
        "expires_in": TOKEN_EXPIRE_MINUTES * 60,
    }


@app.get("/auth/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    return user_response(user)


@app.get("/admin/users", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    owner: User = Depends(require_owner),
):
    users = db.scalars(select(User).order_by(User.id)).all()
    return [user_response(user) for user in users]


@app.patch("/admin/users/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    request: RoleUpdate,
    db: Session = Depends(get_db),
    owner: User = Depends(require_owner),
):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Do not allow the current Owner to accidentally remove their own role.
    if user.id == owner.id and request.role != "Owner":
        raise HTTPException(
            status_code=400,
            detail="You cannot remove your own Owner role",
        )

    user.role = request.role
    db.commit()
    db.refresh(user)
    return user_response(user)

from .api.inventory import router as inventory_router

app.include_router(inventory_router)
from .api.procurement import router as procurement_router

app.include_router(procurement_router)