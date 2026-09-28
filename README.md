# 🌍 NASA Earth Intelligence Agent (NEIA)
### *Autonomous Scientific Research Agent for Planetary Environmental Change*
**NASA Space Apps Challenge 2026 Submission Track: Earth Environmental Intelligence**

[![NASA Space Apps Challenge](https://img.shields.io/badge/NASA%20Space%20Apps-2026-blue.svg?style=for-the-badge&logo=nasa)](https://www.spaceappschallenge.org/)
[![Scientific Verification](https://img.shields.io/badge/Integrity-Deterministic%20Science%20%2B%20Evidence%20Grounding-00ff9d.svg?style=for-the-badge)](https://earthdata.nasa.gov/)
[![Architecture](https://img.shields.io/badge/Architecture-Autonomous%20Agent%20%2B%20Deterministic%20Science-cyan.svg?style=for-the-badge)]()

---

## 🚀 1. The Vision

Traditional AI chatbots often hallucinate numerical values, invent citations, and generate unsubstantiated claims when asked complex questions about Earth observation data.

**NASA Earth Intelligence Agent (NEIA)** introduces a **Deterministic Scientific Analysis + Evidence Grounding** architecture. It separates the cognitive reasoning of an autonomous AI agent from pure, deterministic statistical and mathematical computation:

```
                    USER
                      │
                      │ "How has vegetation changed in coastal Bangladesh
                      │  from 2020 to 2025?"
                      ▼
                 AI PLANNER
                      │
                      ├── Location → Coastal Bangladesh
                      ├── Variable → Vegetation / NDVI
                      ├── Time → 2020–2025
                      └── Analysis → Change + Trend
                      │
                      ▼
            NASA DATA DISCOVERY
                      │
                      └── NASA CMR API
                           ↓
                      MODIS MOD13Q1 (250m, 16-Day L3)
                           ↓
                     NASA Earthdata
                      │
                      ▼
            REAL SATELLITE DATA
                      │
                      ▼
             SCIENTIFIC ENGINE (Pure Python, Zero LLM Math)
                      │
                      ├── spatial filtering
                      ├── temporal aggregation
                      ├── NDVI & ΔNDVI
                      ├── Mann-Kendall trend test (S, Var, Z, p-value)
                      ├── Sen's slope estimator
                      ├── 20-year climatological anomaly Z-scores
                      └── 95% confidence intervals
                      │
                      ▼
               EVIDENCE LAYER
                      │
                      ├── dataset & concept ID
                      ├── NASA DOI: 10.5067/MODIS/MOD13Q1.061
                      ├── audited NASA CMR granules
                      ├── geographic bounding box
                      └── reproducible Python script & SHA-256 hash
                      │
                      ▼
                 AI SYNTHESIS
                      │
                      └── converts verified deterministic results → human-readable answer
                      │
                      ▼
                    USER
```

### 🔍 End-to-End Walkthrough Example
When a user asks:
> *"How has vegetation changed in coastal Bangladesh from 2020 to 2025?"*

The system executes the following 10-stage deterministic pipeline:
1. **User Question Ingestion:** Receives raw natural-language prompt.
2. **Understand Location:** Resolves `location = Coastal Bangladesh` (Sundarbans, Satkhira, Khulna, Bhola, Cox's Bazar).
3. **Understand Variable:** Identifies target indicator `variable = vegetation (NDVI / EVI)`.
4. **Understand Period:** Extracts temporal baseline and target `period = 2020 to 2025`.
5. **Find Appropriate NASA Dataset:** Queries NASA CMR API to match `MODIS/Terra MOD13Q1` (250m, 16-day composite) or `VIIRS VNP13A1`.
6. **Retrieve Data Granules:** Queries NASA CMR Granule Search API (`https://cmr.earthdata.nasa.gov/search/granules.json`) for sinusoidal tile `h26v06` covering coastal Bangladesh across the requested epoch.
7. **Process Data:** Aggregates empirical spatio-temporal arrays, normalizes values $[-1.0, +1.0]$, and prepares 72 temporal composite intervals.
8. **Calculate Vegetation Change:** Deterministically computes $\Delta \text{NDVI}$, Mann-Kendall monotonic trend test ($p < 0.05$), Sen's slope, and Z-score climatological anomalies.
9. **Generate Map & Chart:** Renders interactive Leaflet geospatial polygon vectors and dual-trajectory SVG time-series charts with 95% confidence intervals.
10. **Explain Result (Evidence-Based):** Synthesizes grounded natural-language findings strictly backed by computed values and authenticated NASA Earthdata DOIs.

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
[ NASA CMR Granules API ]                             [ Scientific Engine ]
MODIS MOD13Q1 (Tile h26v06)                           • ΔNDVI Calculation
72 empirical composite granules                       • Z-Score Anomaly Detection
                                                      • Mann-Kendall Trend (p < 0.05)
                                                      • Sen's Slope Estimator
      └───────────────────────────┬───────────────────────────┘
                                  │
                                  ▼
 ╔═════════════════════════════════════════════════════════════════════╗
 ║                     VERIFIED SCIENTIFIC DOSSIER                     ║
 ║  • Computed Mean Shift: -14.4% in western saline sectors            ║
 ║  • Statistical Confidence: p = 0.0001 (Statistically Significant)   ║
 ║  • Spatial Layers: Interactive ΔNDVI GeoJSON + Satellite basemap    ║
 ║  • Evidence: NASA Earthdata DOI: 10.5067/MODIS/MOD13Q1.061         ║
 ║  • Reproducibility: Downloadable Python Recipe & SHA-256 Provenance ║
 ╚═════════════════════════════════════════════════════════════════════╝
``

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

### 🔬 1. Test the Standalone Scientific Engine First (No AI / Pure Science):
```bash
cd backend
python standalone_science_pipeline.py
```
> **Output:** Executes NASA band reading, NDVI computation, Mann-Kendall trend testing, and writes `science_results.json` directly.

### 🌐 2. Run the Full Agent & Web System:
- **Option A (One-Click):** Run `start_servers.bat` (or `./start_servers.ps1`)
- **Option B (Manual):**
  - **Backend:** `cd backend && python -m uvicorn app.main:app --reload --port 8000`
  - **Frontend:** `cd frontend && npm run dev` (Access at `http://localhost:5173`)

---

## 🏆 NASA Space Apps 2026 Deliverables
- **Live Interactive Demo Web App** with real-time agent execution stream.
- **Reproducible Scientific Jupyter Notebook** replicating the agent's findings on Coastal Bangladesh.
- **Project Pitch Deck & Video Script** outlining social impact for climate adaptation.
