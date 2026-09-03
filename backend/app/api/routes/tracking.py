from flask import Blueprint, jsonify, request
from app.engines.tracking.post_relocation import PostRelocationTracker

tracking_bp = Blueprint('tracking', __name__)

@tracking_bp.route('/post-relocation', methods=['POST'])
def get_post_relocation_status():
    """
    POST endpoint to get post-relocation tracking data.
    Body can optionally contain a list of relocated habitations.
    If none provided, it generates a demo synthetic set.
    """
    data = request.get_json() or {}
    habitations = data.get("habitations")
    
    if not habitations:
        # Mock some relocated habitations for demo
        habitations = [
            {"id": "hab-1", "name": "Riverbank Alpha", "households": 120, "assigned_site_id": "site-1", "assigned_site_name": "Highland Haven"},
            {"id": "hab-2", "name": "Valley Beta", "households": 45, "assigned_site_id": "site-2", "assigned_site_name": "Plateau Heights"},
            {"id": "hab-3", "name": "Cliffside Gamma", "households": 80, "assigned_site_id": "site-3", "assigned_site_name": "Temporary Shelter C"},
            {"id": "hab-4", "name": "Delta Delta", "households": 210, "assigned_site_id": "site-4", "assigned_site_name": "Inland Colony"},
        ]
        
    result = PostRelocationTracker.track_households(habitations)
    return jsonify(result), 200
