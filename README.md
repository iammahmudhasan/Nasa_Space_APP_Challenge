# 🌍 NASA Earth Intelligence Agent (NEIA)
### *Autonomous Scientific Research Agent for Planetary Environmental Change*
**NASA Space Apps Challenge 2026 Submission Track: Earth Environmental Intelligence**

[![NASA Space Apps Challenge](https://img.shields.io/badge/NASA%20Space%20Apps-2026-blue.svg?style=for-the-badge&logo=nasa)](https://www.spaceappschallenge.org/)
[![Scientific Verification](https://img.shields.io/badge/Integrity-Zero--Hallucination%20Evidence-00ff9d.svg?style=for-the-badge)](https://earthdata.nasa.gov/)
[![Architecture](https://img.shields.io/badge/Architecture-Autonomous%20Agent%20%2B%20Science%20Engine-cyan.svg?style=for-the-badge)]()

---

## 🚀 1. The Vision

Traditional AI chatbots often hallucinate numerical values, invent citations, and generate unsubstantiated claims when asked complex questions about Earth observation data.

**NASA Earth Intelligence Agent (NEIA)** bridges the gap between natural-language user queries and verified, reproducible scientific Earth science pipelines. It is **not** a simple chatbot; it is an **autonomous scientific agent**:
1. **Understands** natural language environmental inquiries across space and time.
2. **Discovers & selects** appropriate NASA Earth observation products (CMR API, MODIS, VIIRS, Landsat, GPM).
3. **Retrieves & validates** raw spatio-temporal satellite observations.
4. **Executes deterministic scientific ML & statistical algorithms** (trend estimation, Mann-Kendall tests, z-score anomaly detection, spatial change classification).
5. **Enforces strict zero-hallucination guardrails**: the LLM never invents numbers; all quantitative claims are mathematically derived by the Scientific Analysis Engine.
6. **Outputs interactive geospatial maps, temporal trend charts, and an auditable Evidence & Provenance Dossier** with dataset DOIs and a downloadable reproducibility recipe.

---

## 🎯 2. V1 Focus: Coastal Environmental Change

For NASA Space Apps Challenge 2026, V1 specializes in **Earth Environmental Change Intelligence**, with a flagship validation benchmark on **Coastal Bangladesh (2020–2025)**—one of the most vulnerable and dynamic ecological ecosystems on Earth (Sundarbans mangrove degradation, salinity intrusion, cyclone recovery, and coastal accretion/erosion).

```
"Analyze vegetation changes in coastal Bangladesh between 2020 and 2025"
                                  │
                                  ▼
           ┌──────────────────────────────────────────────┐
           │        NASA Earth Intelligence Agent         │
           │  • Location: Coastal Bangladesh              │
           │  • Period: 2020 - 2025                       │
           │  • Metric: NDVI (Vegetation Index)           │
           │  • Target: Anomaly & Change Detection        │
           └──────────────────────┬───────────────────────┘
                                  │
      ┌───────────────────────────┴───────────────────────────┐
      ▼                                                       ▼
[ NASA CMR & GIBS API ]                               [ Scientific Engine ]
MODIS MOD13Q1 / VIIRS VNP13A1                         • ΔNDVI Calculation
Granule search & WMS tile feeds                       • Z-Score Anomaly Detection
                                                      • Mann-Kendall Trend (p < 0.05)
      └───────────────────────────┬───────────────────────────┘
                                  │
                                  ▼
 ╔═════════════════════════════════════════════════════════════════════╗
 ║                     VERIFIED SCIENTIFIC DOSSIER                     ║
 ║  • Mean NDVI Shift: -14.2% in critical saline zones                 ║
 ║  • Statistical Confidence: p = 0.0032 (Significant loss)           ║
 ║  • Spatial Layers: Interactive ΔNDVI GeoJSON + GIBS imagery         ║
 ║  • Evidence: NASA Earthdata DOI: 10.5067/MODIS/MOD13Q1.061         ║
 ║  • Reproducibility: Downloadable Python Recipe & Hash               ║
 ╚═════════════════════════════════════════════════════════════════════╝
```

---

## 🏛️ 3. Repository Architecture

```
Nasa_Space_APP_Challenge/
├── docs/                               # System specifications & challenge docs
│   ├── ARCHITECTURE_SPEC.md            # In-depth architectural blueprint
│   ├── SCIENTIFIC_METHODOLOGY.md       # Statistical & ML formulas & references
│   └── NASA_DATASETS_CATALOG.md        # NASA Earthdata products catalog
├── backend/                            # Python FastAPI + Agent Engine
│   ├── app/
│   │   ├── agent/                      # AI Planner & Orchestrator
│   │   │   ├── planner.py              # LLM agent with structured tool execution
│   │   │   ├── prompts.py              # Guardrailed scientific prompt templates
│   │   │   └── validator.py            # Evidence & sanity verification layer
│   │   ├── tools/                      # Scientific tools callable by Agent
│   │   │   ├── dataset_discovery.py    # NASA CMR search & metadata resolver
│   │   │   ├── data_retriever.py       # Satellite granule & time-series fetcher
│   │   │   ├── scientific_engine.py    # NumPy/Pandas/Scipy trend & anomaly analysis
│   │   │   ├── geospatial.py           # GeoJSON masking, bounding box, spatial stats
│   │   │   └── visualizer.py           # Map layers & chart data generation
│   │   ├── services/                   # External NASA service integrations
│   │   │   ├── nasa_cmr.py             # NASA Common Metadata Repository API client
│   │   │   └── nasa_gibs.py            # NASA Global Imagery Browse Services (GIBS)
│   │   ├── models/                     # Pydantic data contracts & schemas
│   │   │   └── schemas.py              # Query, Analysis, Evidence Dossier models
│   │   ├── data/                       # Ground truth & benchmark data for Coastal BD
│   │   └── main.py                     # FastAPI entrypoint with SSE stream
│   ├── requirements.txt                # Python dependencies
│   └── test_agent.py                   # Automated tests for toolchain
├── frontend/                           # Modern React / Vite Mission Control UI
│   ├── src/
│   │   ├── components/                 # UI components
│   │   │   ├── MapViewer.jsx           # Leaflet/MapLibre satellite & change layer
│   │   │   ├── TimeSeriesChart.jsx     # Trendline & confidence interval visualizer
│   │   │   ├── AgentThoughtFeed.jsx    # Real-time multi-step agent reasoning trace
│   │   │   ├── EvidenceDossier.jsx     # Scientific citations, DOIs, reproducibility
│   │   │   └── QueryInput.jsx          # Natural language mission query console
│   │   ├── styles/                     # Dark space glassmorphism design system
│   │   ├── App.jsx                     # Root application view
│   │   └── main.jsx                    # Entry point
│   ├── package.json
│   └── vite.config.js
└── README.md
```

---

## ⚡ 4. Core Capabilities (The 6 Pillars)

1. **Question Understanding:** Dissects user queries into `Location`, `Time Range`, `Earth Phenomenon`, and `Hypothesis/Task`.
2. **Autonomous Dataset Discovery:** Matches intent with NASA Earthdata collections (MODIS, VIIRS, Landsat, GPM) without manual dataset lookup.
3. **Spatio-Temporal Retrieval:** Gathers satellite imagery, surface reflectance, and vegetation indices over designated bounding boxes.
4. **Deterministic Scientific Analysis:** Computes spatial change matrices ($\Delta \text{NDVI}$, Land Cover transitions), temporal anomalies ($Z\text{-score}$ against multi-year baseline), and significance ($p$-value).
5. **Dynamic Geospatial Visualization:** Renders interactive dual-layer maps (pre vs. post change) and trend charts with standard deviations.
6. **Zero-Hallucination Evidence Dossier:** Compiles an auditable report referencing exact NASA data sources, sensor names, observation intervals, processing algorithms, and limitations.

---

## 🌟 5. Quickstart

### Backend Setup:
```bash
cd backend
python -m venv venv
venv\Scripts\activate   # On Windows
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend Setup:
```bash
cd frontend
npm install
npm run dev
```

---

## 🏆 NASA Space Apps 2026 Deliverables
- **Live Interactive Demo Web App** with real-time agent execution stream.
- **Reproducible Scientific Jupyter Notebook** replicating the agent's findings on Coastal Bangladesh.
- **Project Pitch Deck & Video Script** outlining social impact for climate adaptation.
