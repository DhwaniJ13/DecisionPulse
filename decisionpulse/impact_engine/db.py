"""Database setup. Works with SQLite (solo testing) and PostgreSQL (team)."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

DEFAULT_URL = "sqlite:///decisionpulse.db"


def make_engine(url: str | None = None):
    url = url or os.getenv("DATABASE_URL", DEFAULT_URL)
    if url.startswith("sqlite") and ":memory:" in url:
        return create_engine(url, connect_args={"check_same_thread": False}, poolclass=StaticPool)
    return create_engine(url, future=True)


engine = make_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_session() -> Session:
    """FastAPI usage:  def endpoint(db: Session = Depends(get_db))  -> see get_db()."""
    return SessionLocal()


def get_db():
    """FastAPI dependency (Member 3): yields a session and closes it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(eng=None):
    from .models import Base
    Base.metadata.create_all(eng or engine)
