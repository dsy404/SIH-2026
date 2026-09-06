# Canonical API Contract

To replace the scattered API design, we will enforce these standardized schemas during the FastAPI migration. All endpoints will return strict JSON validation matching these contracts.

### Habitations & Sites
- **`GET /api/habitations`**: `[{ "id": "string", "name": "string", "block_id": "string", "coordinates": { "lat": "float", "lng": "float" } }]`
- **`GET /api/habitations/{id}`**: `{ "id": "string", "name": "string", "population": "int", "terrain": {...}, "infrastructure": {...} }`
- **`GET /api/habitations/{id}/risk`**: `{ "hazard_score": "float", "vulnerability_score": "float", "exposure_score": "float", "total_risk": "float", "category": "string" }`
- **`GET /api/safe-sites`**: `[{ "id": "string", "name": "string", "coordinates": { "lat": "float", "lng": "float" }, "infrastructure_score": "float" }]`
- **`GET /api/safe-sites/{id}/capacity`**: `{ "baseline_capacity": "int", "adjusted_capacity": "int", "current_occupancy": "int", "available": "int" }`

### Relocation & Action Plan
- **`GET /api/red-zones`**: `[{ "habitation_id": "string", "risk_score": "float", "necessity": "string" }]` (Filtered where risk > threshold)
- **`POST /api/relocation/analyze`**: Body: `{ "habitation_ids": ["string"] }` -> Triggers async optimizer.
- **`GET /api/relocation/recommendations`**: `[{ "habitation_id": "string", "recommended_site_id": "string", "confidence_score": "float", "constraints": ["string"] }]`
- **`GET /api/dashboard/summary`**: `{ "total_vulnerable_population": "int", "red_zones_count": "int", "capacity_deficit": "int", "top_priorities": [...] }`

### Operations
- **`POST /api/datasets/upload`**: Body: `FormData(file)` -> `{ "job_id": "string", "status": "string" }`
- **`GET /api/datasets`**: `[{ "id": "string", "type": "string", "uploaded_at": "datetime", "status": "string" }]`
- **`POST /api/field-verification`**: Body: `{ "habitation_id": "string", "verification_data": {...} }` -> `{ "status": "Recalculation Triggered" }`
- **`POST /api/simulation/run`**: Body: `{ "hazard_multiplier": "float", "scenarios": [...] }` -> `{ "simulated_impact": [...] }`
