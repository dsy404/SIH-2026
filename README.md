# 🏛️ Disaster Relocation Decision Support System (DSS)

**Intelligent Identification of Hazard-Based Red Zones & Relocation Priority Assessment**

> Built for **Smart India Hackathon (SIH) 2026** — A comprehensive platform that aggregates demographic, topographic, and hazard data to calculate Relocation Priority Indices (RPI) for vulnerable habitations using a multi-engine risk assessment pipeline.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Running the Application](#running-the-application)
- [Core Features](#core-features)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Methodology](#methodology)

---

## 🎯 Overview

The Disaster Relocation DSS helps government agencies identify habitations at high risk from natural hazards (floods, landslides) and prioritize them for relocation. The system implements a **multi-engine pipeline** following IPCC risk assessment standards:

```
DETECT → ASSESS → SCORE → PRIORITIZE → VISUALIZE
```

Each habitation receives a **Relocation Priority Index (RPI)** score from 0–100, categorized into:

| Category | RPI Range | Action |
|----------|-----------|--------|
| 🔴 **CRITICAL PRIORITY** | > 75 | Immediate relocation required |
| 🟠 **HIGH PRIORITY** | 50–75 | Urgent relocation planning |
| 🟡 **MODERATE PRIORITY** | 25–50 | Monitoring & contingency planning |
| 🟢 **LOW PRIORITY** | < 25 | Routine monitoring |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js 16)                   │
│  ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌──────────────┐  │
│  │Dashboard │ │ Risk Map  │ │ Engines  │ │ML Evaluation │  │
│  │  Home    │ │ (Leaflet) │ │ Testing  │ │  Dashboard   │  │
│  └────┬─────┘ └─────┬─────┘ └────┬─────┘ └──────┬───────┘  │
│       └─────────────┼────────────┼───────────────┘          │
│                     │   REST API Calls                      │
└─────────────────────┼───────────────────────────────────────┘
                      │
┌─────────────────────┼───────────────────────────────────────┐
│              BACKEND (Flask + Python)                        │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                 Master Engine (RPI)                     │  │
│  │  ┌─────────────┐ ┌──────────────┐ ┌─────────────────┐ │  │
│  │  │   Hazard    │ │   Exposure   │ │  Vulnerability  │ │  │
│  │  │   Engine    │ │   Engine     │ │     Engine      │ │  │
│  │  │  (40% wt)   │ │  (30% wt)    │ │   (30% wt)      │ │  │
│  │  └─────────────┘ └──────────────┘ └─────────────────┘ │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐  │
│  │ Data Ingest  │ │  Geospatial  │ │   SQLite Document    │  │
│  │  Pipeline    │ │  Utilities   │ │      Store           │  │
│  └──────────────┘ └──────────────┘ └──────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Frontend
| Technology | Purpose |
|------------|---------|
| Next.js 16 | React framework with App Router |
| TypeScript | Type-safe development |
| Tailwind CSS 4 | Utility-first styling |
| React Leaflet | Interactive geospatial maps |
| Playwright | End-to-end testing |

### Backend
| Technology | Purpose |
|------------|---------|
| Flask | REST API framework |
| Shapely | Geospatial point-in-polygon calculations |
| SQLite | Lightweight document store |
| Python 3.10+ | Backend runtime |

---

## 📁 Project Structure

```
SIH 2026 FINAL/
├── frontend/                    # Next.js 16 application
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx              # Dashboard home
│   │   │   ├── layout.tsx            # Root layout with Sidebar + Header
│   │   │   ├── risk-map/page.tsx     # Interactive geospatial risk map
│   │   │   ├── data-management/      # Data ingestion pipeline UI
│   │   │   ├── engines/page.tsx      # Engine testing interface
│   │   │   └── ml-evaluation/page.tsx # ML model performance dashboard
│   │   ├── components/
│   │   │   ├── layout/              # Sidebar, Header
│   │   │   ├── map/                 # MapComponent, DynamicMap
│   │   │   └── data-management/     # Upload forms
│   │   └── config/app.ts           # App configuration
│   ├── public/data/                # GeoJSON datasets
│   ├── e2e/app.spec.ts            # Playwright E2E tests
│   └── playwright.config.ts       # Playwright configuration
│
├── backend/                     # Flask API application
│   ├── app/
│   │   ├── main.py                  # Flask app + route registration
│   │   ├── config.py                # Settings
│   │   ├── engines/                 # Risk calculation engines
│   │   │   ├── master_engine.py     # Orchestrator (weighted RPI)
│   │   │   ├── hazard_engine.py     # Hazard zone intersection
│   │   │   ├── exposure_engine.py   # Elevation/slope scoring
│   │   │   └── vulnerability_engine.py # Socio-economic scoring
│   │   ├── api/routes/              # API blueprints
│   │   ├── data_ingestion/          # CSV, GeoJSON, raster providers
│   │   ├── geospatial/             # Bounding box, distance, CRS
│   │   └── db/                     # SQLite repository layer
│   ├── data/                       # Synthetic data + generator
│   ├── run.py                      # Entry point
│   └── requirements.txt            # Python dependencies
│
└── README.md                    # This file
```

---

## 🚀 Setup & Installation

### Prerequisites

- **Node.js** ≥ 18.x
- **Python** ≥ 3.10
- **npm** (comes with Node.js)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd "SIH 2026 FINAL"
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Install Playwright (for E2E tests)
npx playwright install
```

---

## ▶️ Running the Application

### Start Backend (Terminal 1)

```bash
cd backend
venv\Scripts\activate    # Windows
python run.py
```

Backend runs at: **http://localhost:8000**

### Start Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

Frontend runs at: **http://localhost:3000**

### Verify Both Services

- **Frontend**: Open http://localhost:3000 — you should see the DSS dashboard
- **Backend Health**: Open http://localhost:8000/api/health — should return `{"status": "ok"}`
- **Risk Map**: Navigate to http://localhost:3000/risk-map — map should load with color-coded markers

---

## ✨ Core Features

### 1. Geospatial Risk Map (`/risk-map`)
Interactive Leaflet map displaying habitation markers color-coded by RPI score. Supports OpenStreetMap and satellite base layers, flood hazard zone overlays, and candidate relocation site markers. Clicking a marker shows a popup with the full score breakdown.

### 2. Data Management Pipeline (`/data-management`)
Multi-format data ingestion supporting CSV, GeoJSON, Shapefile, and raster uploads. Includes automatic data validation, cleaning, and confidence scoring.

### 3. Engine Testing UI (`/engines`)
Direct API testing interface for all four calculation engines (Hazard, Exposure, Vulnerability, Master). Loads synthetic GeoJSON data and displays scored results.

### 4. ML Evaluation Dashboard (`/ml-evaluation`)
Model performance analysis showing pipeline architecture, IPCC weight configuration, feature importance rankings, risk score distribution across all habitations, and a full ranked table.

### 5. Multi-Engine Risk Pipeline
- **Hazard Engine** — Point-in-polygon geospatial analysis against flood/landslide zones
- **Exposure Engine** — Elevation and slope-based physical vulnerability assessment
- **Vulnerability Engine** — Socio-economic scoring (population density, household overcrowding)
- **Master Engine** — Weighted aggregation (40% Hazard / 30% Exposure / 30% Vulnerability)

---

## 📡 API Reference

Base URL: `http://localhost:8000`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/engines/hazard` | Run Hazard Engine on input habitations + hazard zones |
| `POST` | `/api/engines/exposure` | Run Exposure Engine on input habitations |
| `POST` | `/api/engines/vulnerability` | Run Vulnerability Engine on input habitations |
| `POST` | `/api/engines/master` | Run full pipeline (Hazard → Exposure → Vulnerability → RPI) |
| `POST` | `/api/datasets/upload` | Upload CSV/GeoJSON datasets |
| `GET` | `/api/geospatial/bbox` | Calculate bounding box for dataset |

### Example: Master Engine Request

```bash
curl -X POST http://localhost:8000/api/engines/master \
  -H "Content-Type: application/json" \
  -d '{
    "habitations": [
      {
        "id": "hab-1",
        "name": "Village Alpha",
        "longitude": 82.1,
        "latitude": 25.05,
        "elevation": 80,
        "slope": 20,
        "population": 1200,
        "households": 150,
        "geom_geojson": "{\"type\":\"Point\",\"coordinates\":[82.1,25.05]}"
      }
    ],
    "hazards": [],
    "weights": { "hazard": 0.40, "exposure": 0.30, "vulnerability": 0.30 }
  }'
```

### Response

```json
{
  "results": [
    {
      "id": "hab-1",
      "name": "Village Alpha",
      "hazard_score": 0,
      "exposure_score": 75,
      "vulnerability_score": 60,
      "rpi": 40.5,
      "risk_category": "MODERATE PRIORITY",
      "rpi_explanation": {
        "engine": "MasterEngine",
        "weights_used": { "hazard": 0.4, "exposure": 0.3, "vulnerability": 0.3 },
        "calculation": "(0 * 0.4) + (75 * 0.3) + (60 * 0.3)"
      }
    }
  ]
}
```

---

## 🧪 Testing

### E2E Tests (Playwright)

```bash
cd frontend

# Run all E2E tests
npx playwright test

# Run with headed browser (visible)
npx playwright test --headed

# View HTML test report
npx playwright show-report
```

### Backend API Tests

```bash
cd backend
python -m pytest tests/ -v
```

---

## 📐 Methodology

The system follows the **IPCC Risk Assessment Framework**:

```
Risk = f(Hazard, Exposure, Vulnerability)

RPI = (Hazard_Score × 0.40) + (Exposure_Score × 0.30) + (Vulnerability_Score × 0.30)
```

### Hazard Assessment
- Uses **Shapely** for point-in-polygon geospatial analysis
- Habitations are checked against digitized flood/landslide hazard zones
- Severity levels: High (100), Moderate (50), Low (25)

### Exposure Assessment
- **Elevation**: < 100m → +50, 100–150m → +25 (flood exposure)
- **Slope**: > 25° → +50, 15–25° → +25 (landslide exposure)

### Vulnerability Assessment
- **Population**: > 1000 → +40, 500–1000 → +20 (evacuation burden)
- **Household density**: > 7 persons/HH → +40, 5–7 → +20 (overcrowding)

---

## 📝 Demo Region

This prototype uses **synthetic data** for the Ramgarh District (demonstration study region). The dataset includes:
- **25 habitations** with demographic and topographic attributes
- **Flood hazard zones** (GeoJSON polygons)
- **5 candidate relocation sites** with infrastructure scores

---

## 📄 License

Built for **Smart India Hackathon 2026**. All rights reserved.
