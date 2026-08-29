from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class BaseEntity(BaseModel):
    id: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class District(BaseEntity):
    name: str
    state: str

class Block(BaseEntity):
    name: str
    district_id: str

class Habitation(BaseEntity):
    name: str
    block_id: str
    population: int
    households: int
    elevation: float
    slope: float
    aspect: float
    latitude: float
    longitude: float
    geom_geojson: str

class Hazard(BaseEntity):
    type: str # flood, landslide, rainfall
    severity: str
    geom_geojson: str

class CandidateSite(BaseEntity):
    name: str
    latitude: float
    longitude: float
    elevation: float
    slope: float
    aspect: float
    geom_geojson: str
    infrastructure_score: Optional[float] = None

# ... Other models for MVP (Population, Infrastructure, RiskScores, etc.)
