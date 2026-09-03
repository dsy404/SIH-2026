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

app = Flask(settings.app_name)
CORS(app, resources={r"/api/*": {"origins": "*"}})

app.register_blueprint(datasets_bp, url_prefix=settings.api_prefix + "/datasets")
app.register_blueprint(geospatial_bp, url_prefix=settings.api_prefix + "/geospatial")
app.register_blueprint(engines_bp, url_prefix=settings.api_prefix + "/engines")
app.register_blueprint(alerts_bp, url_prefix=settings.api_prefix + "/alerts")
app.register_blueprint(safe_sites_bp, url_prefix=settings.api_prefix + "/safe-sites")
app.register_blueprint(capacity_bp, url_prefix=settings.api_prefix + "/capacity")
app.register_blueprint(necessity_bp, url_prefix=settings.api_prefix + "/necessity")

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "app": settings.app_name})

