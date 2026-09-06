from app.db.database import get_session_factory
from app.db.repository import Repository
from app.engines.relocation.necessity import NecessityEngine

Session = get_session_factory()
db = Session()

# Force HAB001 and HAB002 to have very high RPI
for hab_id in ["HAB001", "HAB002"]:
    ra = Repository.get_risk_assessment(db, hab_id)
    if ra:
        ra.rpi = 88.5
        ra.hazard_score = 95.0
        ra.exposure_score = 80.0
        ra.vulnerability_score = 85.0
        ra.risk_category = "CRITICAL"
        db.flush()
        
        # Re-evaluate necessity
        result = NecessityEngine.evaluate_necessity(hab_id, ra.rpi)
        Repository.save_necessity(db, {
            "habitation_id": hab_id,
            "risk_score": result["risk_score"],
            "category": result["category"],
            "color_code": result["color_code"],
            "action_timeline": result["action_timeline"],
            "reasons": "[]"
        })

db.commit()
db.close()
print("Updated HAB001 and HAB002 to be Red Zones.")
