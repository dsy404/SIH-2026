from fastapi import APIRouter
from typing import List, Dict, Any
from pydantic import BaseModel
from ..engines.hazard_engine import HazardEngine

router = APIRouter(prefix="/engines", tags=["engines"])

class HazardRequest(BaseModel):
    habitations: List[Dict[str, Any]]
    hazards: List[Dict[str, Any]]

@router.post("/hazard")
def run_hazard_engine(request: HazardRequest):
    """Run the Hazard Engine to calculate risk scores."""
    engine = HazardEngine()
    scored_habitations = engine.calculate_hazard_scores(request.habitations, request.hazards)
    return {"results": scored_habitations}
