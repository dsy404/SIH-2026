"""
Alerts & Notifications API Routes

Provides endpoints to:
- Generate alerts by running the Alert Engine against scored habitations
- List all alerts (with optional severity filter)
- Mark alerts as read
- List notifications (with count of unread)
- Mark notifications as read / mark all as read
- Get configured alert rules
"""

from flask import Blueprint, request, jsonify
from app.engines.alert_engine import AlertEngine
from app.engines.master_engine import MasterEngine

alerts_bp = Blueprint("alerts", __name__)

# In-memory store for demo (persists per server session)
_alerts_store: list = []
_notifications_store: list = []


@alerts_bp.route("/generate", methods=["POST"])
def generate_alerts():
    """
    Run the Alert Engine against scored habitations.
    Accepts the same payload as the Master Engine (habitations + hazards),
    or pre-scored habitations with 'rpi' fields already set.
    """
    data = request.json or {}

    habitations = data.get("habitations", [])
    hazards = data.get("hazards", [])

    # If habitations don't already have RPI scores, run the Master Engine first
    if habitations and "rpi" not in habitations[0]:
        master = MasterEngine()
        habitations = master.calculate_priority_index(habitations, hazards)

    # Run the Alert Engine
    engine = AlertEngine()
    result = engine.evaluate(habitations)

    # Store alerts and notifications (append, don't replace)
    global _alerts_store, _notifications_store
    _alerts_store = result["alerts"]  # Replace with latest run
    _notifications_store = result["notifications"]

    return jsonify(result)


@alerts_bp.route("/list", methods=["GET"])
def list_alerts():
    """List all generated alerts, optionally filtered by severity."""
    severity = request.args.get("severity")
    
    filtered = _alerts_store
    if severity:
        filtered = [a for a in filtered if a["severity"] == severity]

    return jsonify({
        "alerts": filtered,
        "total": len(filtered),
    })


@alerts_bp.route("/<alert_id>/read", methods=["PATCH"])
def mark_alert_read(alert_id: str):
    """Mark a specific alert as read."""
    for alert in _alerts_store:
        if alert["id"] == alert_id:
            alert["is_read"] = True
            return jsonify({"status": "ok", "alert": alert})

    return jsonify({"detail": f"Alert {alert_id} not found"}), 404


@alerts_bp.route("/rules", methods=["GET"])
def get_alert_rules():
    """Return all configured alert rules (metadata only)."""
    engine = AlertEngine()
    return jsonify({"rules": engine.get_rules()})


# ─── Notifications ────────────────────────────────────────────────────

@alerts_bp.route("/notifications", methods=["GET"])
def list_notifications():
    """List all notifications."""
    return jsonify({
        "notifications": _notifications_store,
        "total": len(_notifications_store),
        "unread": len([n for n in _notifications_store if not n["is_read"]]),
    })


@alerts_bp.route("/notifications/count", methods=["GET"])
def notification_count():
    """Get unread notification count (for badge in header)."""
    unread = len([n for n in _notifications_store if not n["is_read"]])
    return jsonify({"unread": unread, "total": len(_notifications_store)})


@alerts_bp.route("/notifications/<notification_id>/read", methods=["PATCH"])
def mark_notification_read(notification_id: str):
    """Mark a specific notification as read."""
    for notif in _notifications_store:
        if notif["id"] == notification_id:
            notif["is_read"] = True
            return jsonify({"status": "ok", "notification": notif})

    return jsonify({"detail": f"Notification {notification_id} not found"}), 404


@alerts_bp.route("/notifications/read-all", methods=["PATCH"])
def mark_all_notifications_read():
    """Mark all notifications as read."""
    for notif in _notifications_store:
        notif["is_read"] = True

    return jsonify({"status": "ok", "marked": len(_notifications_store)})
