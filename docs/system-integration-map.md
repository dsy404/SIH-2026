# System Integration Map

This document maps out the current (pre-migration) data flow across the Flask/Next.js application, identifying exactly how frontend calls map to backend engines and the sources of truth they rely on.

| Frontend Page | Frontend API Call | Backend Route | Backend Engine | Data Source |
|---|---|---|---|---|
| Dashboard (`/action-plan`) | None (Calculates on load) | `/api/dashboard/action-plan` (`dashboard.py`) | `RelocationOptimizer` | `get_demo_data()` (Hardcoded lists) |
| Geospatial Map (`/risk-map`) | `fetch('http://localhost:5000/api/engines/master')` | `/api/engines/master` (`engines.py`) | `master_engine.py` | POSTs `/data/habitations.geojson` from frontend `public/` |
| Safe Sites (`/safe-sites`) | `fetch('http://localhost:5000/api/safe-sites/compare')` | `/api/safe-sites/compare` (`safe_sites.py`) | None | Hardcoded `DEMO_HABITATION_ID` |
| Capacity (`/capacity`) | `fetch('/api/capacity/analyze')` | `/api/capacity/analyze` (`capacity.py`) | `carrying_capacity.py` | Random hash-based fake values |
| Necessity (`/necessity`) | `fetch('http://localhost:5000/api/necessity/evaluate')` | `/api/necessity/evaluate` (`necessity.py`) | `NecessityEngine` | Random pseudo-hash based on ID |
| Optimizer (`/optimizer`) | `fetch('http://localhost:5000/api/optimizer/run')` | `/api/optimizer/run` (`optimizer.py`) | `RelocationOptimizer` | Static Demo Generators |
| Alerts (`/notifications`) | `fetch('http://localhost:5000/api/alerts/list')` | `/api/alerts/list` (`alerts.py`) | `alert_engine.py` | Local static JSON files |
| Tracking (`/post-relocation`) | `fetch('http://localhost:8000/api/tracking/post-relocation')`| `/api/tracking/post-relocation` (`tracking.py`) | `post_relocation.py` | Hardcoded mock demographics |
| Simulation (`/simulation`) | `fetch('http://localhost:8000/api/simulation/run')` | `/api/simulation/run` (`simulation.py`) | `simulation_service.py` | Basic multiplier logic |
| ML Evaluation (`/ml-evaluation`)| `fetch('http://localhost:8000/api/ml/feature-importance')` | `/api/ml/feature-importance` (`ml.py`) | `risk_classifier.py` | Fixed dictionary array |
