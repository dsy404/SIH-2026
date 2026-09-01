from flask import Flask, jsonify
from flask_cors import CORS
from .config import settings

from .api.routes.datasets import datasets_bp
from .api.routes.geospatial import geospatial_bp
from .api.routes.engines import engines_bp
from .api.routes.alerts import alerts_bp

app = Flask(settings.app_name)
CORS(app, resources={r"/api/*": {"origins": "*"}})

app.register_blueprint(datasets_bp, url_prefix=settings.api_prefix + "/datasets")
app.register_blueprint(geospatial_bp, url_prefix=settings.api_prefix + "/geospatial")
app.register_blueprint(engines_bp, url_prefix=settings.api_prefix + "/engines")
app.register_blueprint(alerts_bp, url_prefix=settings.api_prefix + "/alerts")

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "app": settings.app_name})

