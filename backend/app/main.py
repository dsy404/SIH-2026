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
    finally:
        session.close()


# Run on import (Flask dev server reloads will re-trigger)
_init_and_seed()
