"""
Optimizer API — reads habitations and sites from DB, saves assignments back.
"""
from flask import Blueprint, jsonify
from app.db.database import get_session_factory
from app.db.repository import Repository
from app.engines.relocation.optimizer import RelocationOptimizer
from app.engines.alert_engine import AlertEngine

optimizer_bp = Blueprint('optimizer', __name__)



@optimizer_bp.route("/run", methods=["POST", "GET"])
def run_optimization():
    """
    Executes the relocation optimizer using canonical DB data.
    Saves assignments back to the database.
    """
    Session = get_session_factory()
    session = Session()
    try:
        habitations = Repository.get_all_habitations(session)
        sites = Repository.get_all_sites(session)

        # Convert to dicts for the engine
        hab_dicts = []
        for h in habitations:
            d = Repository.habitation_to_dict(h)
            d["risk_score"] = h.risk_assessment.rpi if h.risk_assessment else 0
            hab_dicts.append(d)

        site_dicts = [Repository.site_to_dict(s) for s in sites]

        # Run optimization
        plan = RelocationOptimizer.run_optimization(hab_dicts, site_dicts)

        # Clear old assignments and save new ones
        Repository.clear_assignments(session)

        for a in plan.get("assignments", []):
            Repository.save_assignment(session, {
                "habitation_id": a["habitation_id"],
                "site_id": a["assigned_site_id"],
                "population": a["population"],
                "necessity_category": a["necessity"],
                "reason": a["reason"],
                "status": "pending",
            })

        for u in plan.get("unassigned", []):
            Repository.save_assignment(session, {
                "habitation_id": u["habitation_id"],
                "site_id": None,
                "population": u["population"],
                "necessity_category": u["necessity"],
                "reason": u["reason"],
                "status": "unassigned",
            })

        Repository.log_action(session, "optimize", details="Optimizer run completed")

        # Automated System Event Alert Triggers
        try:
            # 1. Check for unassigned population / deficit
            unassigned_list = plan.get("unassigned", [])
            total_deficit = plan.get("summary", {}).get("total_capacity_deficit", 0)
            if unassigned_list and total_deficit > 0:
                hab_names = [u.get("habitation_name") or u.get("habitation_id") for u in unassigned_list]
                AlertEngine.trigger_no_feasible_capacity(
                    session,
                    unassigned_count=len(unassigned_list),
                    total_deficit=total_deficit,
                    habitation_names=hab_names,
                    source_event="OPTIMIZER_RUN"
                )

            # 2. Check for candidate sites with critically low remaining headroom
            site_name_map = {s.id: s.name for s in sites}
            for sc in plan.get("site_capacity_summary", []):
                s_id = sc["site_id"]
                init_cap = sc.get("initial_capacity", 0)
                rem_cap = sc.get("remaining_capacity", 0)
                if init_cap > 0 and (rem_cap < 500 or (rem_cap / init_cap) < 0.15):
                    s_name = site_name_map.get(s_id, f"Site {s_id}")
                    AlertEngine.trigger_site_capacity_low(
                        session,
                        site_id=s_id,
                        site_name=s_name,
                        remaining_capacity=rem_cap,
                        initial_capacity=init_cap,
                        source_event="OPTIMIZER_RUN"
                    )
        except Exception as e:
            print(f"[AlertEngine Hook Warning] Optimizer alert trigger error: {e}")

        session.commit()

        return jsonify(plan)
    finally:
        session.close()


@optimizer_bp.route("/plan", methods=["GET"])
def get_current_plan():
    """
    Returns the latest relocation optimization plan based on current database state.
    """
    return run_optimization()


@optimizer_bp.route("/vectors", methods=["GET"])
def get_relocation_vectors():
    """
    Returns GeoJSON LineStrings from each assigned habitation to its designated safe site.
    Enables map visualization of relocation corridors and logistics pathways.
    """
    Session = get_session_factory()
    session = Session()
    try:
        assignments = Repository.get_all_assignments(session)
        if not assignments:
            # Run optimizer if not yet executed
            run_optimization()
            assignments = Repository.get_all_assignments(session)

        hab_map = {h.id: h for h in Repository.get_all_habitations(session)}
        site_map = {s.id: s for s in Repository.get_all_sites(session)}

        features = []
        for a in assignments:
            if not a.site_id or a.site_id not in site_map or a.habitation_id not in hab_map:
                continue

            hab = hab_map[a.habitation_id]
            site = site_map[a.site_id]

            if hab.latitude is None or hab.longitude is None or site.latitude is None or site.longitude is None:
                continue

            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [float(hab.longitude), float(hab.latitude)],
                        [float(site.longitude), float(site.latitude)]
                    ]
                },
                "properties": {
                    "habitation_id": hab.id,
                    "habitation_name": hab.name,
                    "site_id": site.id,
                    "site_name": site.name,
                    "population": a.population,
                    "urgency": a.necessity_category,
                    "reason": a.reason
                }
            }
            features.append(feature)

        return jsonify({
            "type": "FeatureCollection",
            "features": features
        })
    finally:
        session.close()

