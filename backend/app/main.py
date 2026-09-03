from flask import Flask, jsonify
from flask_cors import CORS
from .config import settings

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

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "app": settings.app_name})

