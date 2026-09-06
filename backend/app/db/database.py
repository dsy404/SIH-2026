"""
SQLAlchemy engine, session factory, and Base declarative class.
All tables are created from the ORM models on init_db().
"""
import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

_engine = None
_SessionLocal = None


def get_engine(db_path: str = None):
    global _engine
    if _engine is None:
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(__file__), '..', '..', 'disaster_relocation.db'
            )
        db_url = f"sqlite:///{os.path.abspath(db_path)}"
        _engine = create_engine(db_url, echo=False, connect_args={"check_same_thread": False})
        # Enable foreign key enforcement for SQLite
        @event.listens_for(_engine, "connect")
        def _set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    return _engine


def get_session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)
    return _SessionLocal


def get_db():
    """Yields a DB session, closing it after use."""
    Session = get_session_factory()
    session = Session()
    try:
        yield session
    finally:
        session.close()


def init_db():
    """Create all tables from the ORM models."""
    from . import models  # noqa – ensure models are imported so Base.metadata is populated
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
