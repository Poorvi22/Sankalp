import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


# Store the database outside the source-code directory.
DATABASE_URL = os.getenv(
    "BIZPILOT_DATABASE_URL",
    "sqlite:///./bizpilot.db",
)

connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


def get_db():
    """Provide a database session to a FastAPI endpoint."""
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()