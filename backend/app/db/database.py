"""
SQLAlchemy engine, session factory, and Base declarative class.
All tables are created from the ORM models on init_db().
Includes automatic lightweight column migrations for SQLite.
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
    """Create all tables from the ORM models and migrate columns if needed."""
    from . import models  # noqa – ensure models are imported so Base.metadata is populated
    engine = get_engine()
    Base.metadata.create_all(bind=engine)

    # SQLite migration: check if tables have all Phase 5 and Phase 8 required columns
    with engine.connect() as conn:
        try:
            # 1. Datasets migration
            res = conn.exec_driver_sql("PRAGMA table_info(datasets)")
            existing_cols = {row[1] for row in res.fetchall()}
            dataset_cols = [
                ("source", "VARCHAR DEFAULT 'Uploaded File'"),
                ("original_filename", "VARCHAR"),
                ("geometry_type", "VARCHAR DEFAULT 'Point'"),
                ("missing_values_count", "INTEGER DEFAULT 0"),
                ("validation_status", "VARCHAR DEFAULT 'READY'"),
                ("processing_status", "VARCHAR DEFAULT 'Completed'"),
                ("is_real", "BOOLEAN DEFAULT 0"),
            ]
            for col_name, col_def in dataset_cols:
                if col_name not in existing_cols:
                    conn.exec_driver_sql(f"ALTER TABLE datasets ADD COLUMN {col_name} {col_def}")

            # 2. Habitations migration (Phase 8 fields)
            res_hab = conn.exec_driver_sql("PRAGMA table_info(habitations)")
            existing_hab_cols = {row[1] for row in res_hab.fetchall()}
            hab_cols = [
                ("road_accessible", "BOOLEAN DEFAULT 1"),
                ("road_status", "VARCHAR DEFAULT 'OPEN'"),
                ("water_availability", "VARCHAR DEFAULT 'ADEQUATE'"),
                ("housing_condition", "VARCHAR DEFAULT 'PUCCA_GOOD'"),
                ("healthcare_accessible", "BOOLEAN DEFAULT 1"),
                ("hazard_observation", "VARCHAR DEFAULT 'NONE'"),
                ("verification_status", "VARCHAR DEFAULT 'NEEDS_VERIFICATION'"),
            ]
            for col_name, col_def in hab_cols:
                if col_name not in existing_hab_cols:
                    conn.exec_driver_sql(f"ALTER TABLE habitations ADD COLUMN {col_name} {col_def}")

            # 3. Field Verifications migration (Phase 8 fields)
            res_fv = conn.exec_driver_sql("PRAGMA table_info(field_verifications)")
            existing_fv_cols = {row[1] for row in res_fv.fetchall()}
            fv_cols = [
                ("verifier_name", "VARCHAR DEFAULT 'Field Officer'"),
                ("verified_at", "DATETIME"),
                ("latitude", "FLOAT"),
                ("longitude", "FLOAT"),
                ("road_accessible", "BOOLEAN DEFAULT 1"),
                ("road_status", "VARCHAR DEFAULT 'OPEN'"),
                ("water_availability", "VARCHAR DEFAULT 'ADEQUATE'"),
                ("housing_condition", "VARCHAR DEFAULT 'PUCCA_GOOD'"),
                ("healthcare_accessible", "BOOLEAN DEFAULT 1"),
                ("hazard_observation", "VARCHAR DEFAULT 'NONE'"),
                ("verification_status", "VARCHAR DEFAULT 'VERIFIED'"),
                ("notes", "TEXT"),
                ("previous_state_snapshot", "TEXT"),
                ("updated_state_snapshot", "TEXT"),
                ("recalculation_diff", "TEXT"),
            ]
            for col_name, col_def in fv_cols:
                if col_name not in existing_fv_cols:
                    conn.exec_driver_sql(f"ALTER TABLE field_verifications ADD COLUMN {col_name} {col_def}")

            # 4. Alerts migration (Phase 10 fields)
            res_alr = conn.exec_driver_sql("PRAGMA table_info(alerts)")
            existing_alr_cols = {row[1] for row in res_alr.fetchall()}
            alr_cols = [
                ("type", "VARCHAR DEFAULT 'SYSTEM_EVENT'"),
                ("title", "VARCHAR DEFAULT 'System Alert'"),
                ("description", "TEXT DEFAULT ''"),
                ("site_id", "VARCHAR"),
                ("site_name", "VARCHAR"),
                ("source_event", "VARCHAR DEFAULT 'SYSTEM_EVENT'"),
                ("is_acknowledged", "BOOLEAN DEFAULT 0"),
                ("acknowledged_at", "DATETIME"),
                ("is_resolved", "BOOLEAN DEFAULT 0"),
                ("resolved_at", "DATETIME"),
            ]
            for col_name, col_def in alr_cols:
                if col_name not in existing_alr_cols:
                    conn.exec_driver_sql(f"ALTER TABLE alerts ADD COLUMN {col_name} {col_def}")

            conn.commit()
        except Exception:
            pass

