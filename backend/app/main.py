from flask import Flask, jsonify
from flask_cors import CORS
from .config import settings
from .db.database import init_db, get_engine, get_session_factory
from .db.repository import Repository

from .api.routes.datasets import datasets_bp
from .api.routes.geospatial import geospatial_bp
from .api.routes.engines import engines_bp
from .api.routes.alerts import alerts_bp
from .api.routes.safe_sites import safe_sites_bp
from .api.routes.capacity import capacity_bp
from .api.routes.necessity import necessity_bp
from .api.routes.optimizer import optimizer_bp
from .api.routes.dashboard import dashboard_bp
from .api.routes.tracking import tracking_bp
from .api.routes.simulation import simulation_bp
from .api.routes.reports import reports_bp
from .api.routes.ml import ml_bp
from .api.routes.habitations import habitations_bp
from .api.routes.sites import sites_bp
from .api.routes.field_verification import field_verification_bp

app = Flask(settings.app_name)
CORS(app, resources={r"/api/*": {"origins": "*"}})

app.register_blueprint(datasets_bp, url_prefix=settings.api_prefix + "/datasets")
app.register_blueprint(geospatial_bp, url_prefix=settings.api_prefix + "/geospatial")
app.register_blueprint(engines_bp, url_prefix=settings.api_prefix + "/engines")
app.register_blueprint(alerts_bp, url_prefix=settings.api_prefix + "/alerts")
app.register_blueprint(safe_sites_bp, url_prefix=settings.api_prefix + "/safe-sites")
app.register_blueprint(capacity_bp, url_prefix=settings.api_prefix + "/capacity")
app.register_blueprint(necessity_bp, url_prefix=settings.api_prefix + "/necessity")
app.register_blueprint(optimizer_bp, url_prefix=settings.api_prefix + "/optimizer")
app.register_blueprint(dashboard_bp, url_prefix=settings.api_prefix + "/dashboard")
app.register_blueprint(tracking_bp, url_prefix=settings.api_prefix + "/tracking")
app.register_blueprint(simulation_bp, url_prefix=settings.api_prefix + "/simulation")
app.register_blueprint(reports_bp, url_prefix=settings.api_prefix + "/reports")
app.register_blueprint(ml_bp, url_prefix=settings.api_prefix + "/ml")
app.register_blueprint(habitations_bp, url_prefix=settings.api_prefix + "/habitations")
app.register_blueprint(sites_bp, url_prefix=settings.api_prefix + "/sites")
app.register_blueprint(field_verification_bp, url_prefix=settings.api_prefix + "/field-verification")

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "app": settings.app_name})


def _init_and_seed():
    """Initialize DB schema and auto-seed if empty."""
    from .db.database import get_engine
    init_db()
    Session = get_session_factory()
    session = Session()
    try:
        count = Repository.count_habitations(session)
        if count == 0:
            print("[STARTUP] Database is empty — seeding with synthetic data...")
            from .db.seed import seed_database
            seed_database(session)
        else:
            print(f"[STARTUP] Database already has {count} habitations. Skipping seed.")

        # Ensure synthetic baseline datasets are registered in the dataset metadata registry
        if len(Repository.get_all_datasets(session)) == 0:
            Repository.save_dataset(session, {
                "name": "Ramgarh_Habitations_Baseline",
                "source": "State Disaster Management Authority (Synthetic Baseline)",
                "original_filename": "habitations.geojson",
                "category": "habitations",
                "format": "geojson",
                "geometry_type": "Point",
                "record_count": count or 20,
                "valid_count": count or 20,
                "invalid_count": 0,
                "missing_values_count": 0,
                "validation_status": "READY",
                "processing_status": "Completed",
                "is_real": False,
                "confidence": "SYNTHETIC",
                "projected_crs": "EPSG:4326",
            })
            Repository.save_dataset(session, {
                "name": "Ramgarh_Hazards_Baseline",
                "source": "Geological Survey & Central Water Commission (Synthetic)",
                "original_filename": "hazards.geojson",
                "category": "hazards",
                "format": "geojson",
                "geometry_type": "Polygon",
                "record_count": Repository.count_hazards(session) or 10,
                "valid_count": Repository.count_hazards(session) or 10,
                "invalid_count": 0,
                "missing_values_count": 0,
                "validation_status": "READY",
                "processing_status": "Completed",
                "is_real": False,
                "confidence": "SYNTHETIC",
                "projected_crs": "EPSG:4326",
            })
            Repository.save_dataset(session, {
                "name": "Ramgarh_Relocation_Sites_Baseline",
                "source": "Land Revenue Department (Synthetic)",
                "original_filename": "candidate_sites.geojson",
                "category": "candidate_sites",
                "format": "geojson",
                "geometry_type": "Point",
                "record_count": Repository.count_sites(session) or 7,
                "valid_count": Repository.count_sites(session) or 7,
                "invalid_count": 0,
                "missing_values_count": 0,
                "validation_status": "READY",
                "processing_status": "Completed",
                "is_real": False,
                "confidence": "SYNTHETIC",
                "projected_crs": "EPSG:4326",
            })
            session.commit()
    finally:
        session.close()


# Run on import (Flask dev server reloads will re-trigger)
_init_and_seed()
