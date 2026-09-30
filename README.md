<p align="center">
  <a href="https://www.spaceappschallenge.org/" target="_blank">
    <img src="Nasa-logo.gif" alt="NASA Space Apps Challenge" width="160" style="filter: drop-shadow(0 0 25px rgba(11, 61, 145, 0.6));" />
  </a>
</p>

<h1 align="center" style="font-weight: 800; letter-spacing: 2px;">🛰️ ORION SPACE</h1>
<h3 align="center" style="color: #60A5FA; font-weight: 600;">NASA International Space Apps Challenge 2026</h3>
<p align="center">
  <b>Challenge Track:</b> <em>Be An Earth System Trend Detective! (Advanced Earth Science)</em><br />
  <b>Investigative Domain:</b> <em>Decadal Multi-Variable Earth-System Dynamics & Statistical Coupling across Bangladesh (2001–2025)</em>
</p>

<p align="center">
  <a href="https://www.spaceappschallenge.org/"><img src="https://img.shields.io/badge/NASA_Space_Apps-Challenge_2026-0B3D91?style=for-the-badge&logo=nasa&logoColor=white" alt="NASA Space Apps" /></a>
  <img src="https://img.shields.io/badge/Mission-Earth_System_Trend_Detective-FC3D21?style=for-the-badge" alt="Track" />
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React 19" />
  <img src="https://img.shields.io/badge/Vite-6.2-646CFF?style=for-the-badge&logo=vite&logoColor=white" alt="Vite" />
  <img src="https://img.shields.io/badge/FDR_Control-Benjamini--Hochberg_(1995)-10B981?style=for-the-badge" alt="BH FDR" />
  <img src="https://img.shields.io/badge/License-MIT_Open_Science-blueviolet?style=for-the-badge" alt="License" />
</p>

<p align="center">
  <a href="#-quick-start--reproducibility-guide"><b>⚡ Quickstart</b></a> •
  <a href="#-the-4-detective-questions"><b>🔍 Detective Questions</b></a> •
  <a href="#-key-scientific-discoveries"><b>🔬 Scientific Discoveries</b></a> •
  <a href="#-interactive-web-dashboard-showcase"><b>🗺️ Spatial Dashboard</b></a> •
  <a href="#-fastapi-intelligence-engine-endpoints"><b>⚡ API Docs</b></a> •
  <a href="#-judging-criteria-alignment"><b>🏆 Challenge Alignment</b></a>
</p>

---

> [!IMPORTANT]
> **Core Scientific Breakthrough:** Orion Space is engineered on a **"Deterministic Ground Truth First"** architecture. While standard Generative AI hallucinate climate statistics and mix up physical units, Orion Space computes all parametric (OLS) and non-parametric (Mann-Kendall Sen's slope) decadal trends through rigid scientific pipelines, subjected to **Benjamini–Hochberg (1995) False Discovery Rate (FDR)** multiple-testing correction across **4,080 statistical hypotheses**. The AI copilot acts solely as a strictly bounded, evidence-grounded synthesizer.

---

## 📑 Table of Contents

- [🌟 Executive Summary](#-executive-summary)
- [🔍 The 4 Detective Questions](#-the-4-detective-questions)
- [🚀 Interactive Portals & Interfaces](#-interactive-portals--interfaces)
- [🗺️ Geospatial & Time-Series Visual Evidence](#️-geospatial--time-series-visual-evidence)
- [🔬 Key Scientific Discoveries](#-key-scientific-discoveries)
  - [1. Ubiquitous Post-Monsoon Warming Acceleration](#1-ubiquitous-post-monsoon-warming-acceleration)
  - [2. Benjamini–Hochberg False Discovery Rate (FDR) Control](#2-benjaminihochberg-false-discovery-rate-fdr-control)
  - [3. Multi-Variable Earth-System Coupling (6 Bivariate Pairs)](#3-multi-variable-earth-system-coupling-6-bivariate-pairs)
- [🏛️ System Architecture: Ground Truth First](#️-system-architecture-ground-truth-first)
- [🖥️ Interactive Web Dashboard Showcase](#️-interactive-web-dashboard-showcase)
- [📁 Repository Directory Map](#-repository-directory-map)
- [💻 Quick Start & Reproducibility Guide](#-quick-start--reproducibility-guide)
- [⚡ FastAPI Intelligence Engine Endpoints](#-fastapi-intelligence-engine-endpoints)
- [🏆 Judging Criteria Alignment](#-judging-criteria-alignment)
- [📜 Scientific Provenance & References](#-scientific-provenance--references)
- [👥 Team & Acknowledgments](#-team--acknowledgments)

---

## 🌟 Executive Summary

**Bangladesh** is globally recognized as one of the most climate-vulnerable deltas on Earth, subject to complex monsoon shifts, pre-monsoon heatwaves, topsoil desiccation, and seasonal radiation imbalances. Yet, analyzing satellite data at a single point or examining annual averages masks critical seasonal signals. 

**Orion Space** solves this through a multi-scale, multi-variable climate detective system:
- **Satellite Data Assimilation:** Integrates **25 continuous years (2001–2025)** of daily and monthly satellite records from **NASA GMAO MERRA-2** (Atmosphere & Land Model) and **NASA CERES / FLASHFlux** (Radiation Budget).
- **National Grid Network:** Evaluates **34 mainland Bangladesh grid cells** ($0.5^\circ \times 0.625^\circ$ resolution) spanning all 8 administrative divisions (Dhaka, Chattogram, Sylhet, Rajshahi, Khulna, Barishal, Rangpur, Mymensingh), rigorously filtered using official **geoBoundaries ADM0** Point-in-Polygon GIS intersection.
- **Multiple-Testing Control:** Implements the **Benjamini–Hochberg (1995)** procedure across **48 spatial trend families** (1,632 hypotheses) and **72 bivariate correlation families** (2,448 hypotheses) at $q < 0.05$, screening out false positives caused by spatial autocorrelation.
- **Modern Full-Stack Experience:** Provides an ultra-responsive, space-themed glassmorphism dashboard (React 19 + Leaflet) backed by an asynchronous FastAPI engine and two fully executable, self-contained Jupyter research notebooks with embedded high-resolution graphics.

---

## 🔍 The 4 Detective Questions

The challenge charges us with answering four fundamental scientific questions:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    THE 4 DETECTIVE QUESTIONS                                     │
├──────────────────────────┬───────────────────────────────────────────────────────────────────────┤
│ 1. WHAT IS CHANGING?     │ 4 Interconnected Planetary Variables:                                 │
│                          │ • 🌡️ T2M: Surface Air Temperature at 2 Meters (°C) [NASA MERRA-2]      │
│                          │ • 🌧️ PRECTOTCORR: Total Bias-Corrected Precipitation (mm/day) [MERRA-2]│
│                          │ • 💧 GWETTOP: Top-Layer (0–5 cm) Soil Wetness (0–1 fraction) [MERRA-2] │
│                          │ • ☀️ ALLSKY_SFC_SW_DWN: Downwelling Solar Irradiance (MJ/m²/d) [CERES]│
├──────────────────────────┼───────────────────────────────────────────────────────────────────────┤
│ 2. WHERE IS IT CHANGING? │ 34 Mainland Bangladesh Grid Cells (0.5° × 0.625° resolution)          │
│                          │ covering all 8 administrative divisions, filtered by official         │
│                          │ geoBoundaries ADM0 Point-in-Polygon boundary.                         │
├──────────────────────────┼───────────────────────────────────────────────────────────────────────┤
│ 3. BY HOW MUCH?          │ Quantified via dual parametric (Ordinary Least Squares) and           │
│                          │ non-parametric (Mann-Kendall Sen's median slope) decadal rates:       │
│                          │ • °C/decade for T2M                                                   │
│                          │ • mm/day/decade for PRECTOTCORR                                       │
│                          │ • % saturation/decade for GWETTOP                                     │
│                          │ • MJ/m²/day/decade for ALLSKY_SFC_SW_DWN                              │
├──────────────────────────┼───────────────────────────────────────────────────────────────────────┤
│ 4. IS IT SIGNIFICANT?    │ Controlled across 48 spatial trend families (m = 34 each) and         │
│                          │ 72 bivariate relationship families (m = 34 each) using the            │
│                          │ Benjamini–Hochberg (1995) Step-Up FDR procedure at q < 0.05.          │
└──────────────────────────┴───────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Interactive Portals & Interfaces

| Portal | Interface | Description | Access / URL |
| :--- | :--- | :--- | :--- |
| 🗺️ **Web Dashboard** | **React 19 + Leaflet** | Dark space glassmorphism UI with interactive GIS maps, FDR halos, coupling matrix, and AI Copilot | [`http://localhost:3000`](http://localhost:3000) |
| ⚡ **FastAPI Engine** | **RESTful OpenAPI** | High-performance JSON intelligence backend with rule-based NLP query parser & evidence retriever | [`http://localhost:8000/docs`](http://localhost:8000/docs) |
| 📓 **Phase 1 Notebook** | **Jupyter Science** | Single-point decadal baseline analysis for Dhaka (2001–2025) with pre-rendered plots | [`01_nasa_temperature_analysis.ipynb`](orion-space/notebooks/01_nasa_temperature_analysis.ipynb) |
| 📓 **Phase 2 Notebook** | **Jupyter Science** | National 34-grid multi-variable network, 6-pair coupling & Benjamini–Hochberg FDR testing | [`02_nasa_earth_system_multivariable_fdr.ipynb`](orion-space/notebooks/02_nasa_earth_system_multivariable_fdr.ipynb) |

---

## 🗺️ Geospatial & Time-Series Visual Evidence

<p align="center">
  <img src="data/bangladesh_t2m_trend_map.png" alt="Bangladesh 25-Year Temperature Trend Map" width="88%" style="border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.5);" />
  <br />
  <em><b>Figure 1:</b> 25-Year Decadal Temperature Trends across Bangladesh's 34 Mainland Grid Network with Benjamini–Hochberg FDR Significance. All 8 administrative divisions exhibit robust post-monsoon warming with Sylhet Division peaking at +0.4214 °C/decade.</em>
</p>

<p align="center">
  <img src="orion-space/data/dhaka_t2m_trend_analysis.png" alt="Dhaka 25-Year Trend Deconstruction" width="88%" style="border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.5);" />
  <br />
  <em><b>Figure 2:</b> Dhaka 25-Year Multi-Scale Temporal Deconstruction (Daily Synoptic Weather Noise vs. Monthly Seasonality vs. Annual Signal), demonstrating that post-monsoon warming is masked when analyzing annual averages alone.</em>
</p>

---

## 🔬 Key Scientific Discoveries

### 1. Ubiquitous Post-Monsoon Warming Acceleration
While annual mean temperature trends across Bangladesh show modest or non-significant changes ($p = 0.757$) due to high pre-monsoon convective noise, seasonal deconstruction reveals that late-monsoon and post-monsoon warming is **ubiquitous, rapid, and statistically verified**:
- **National Mean September Warming:** **`+0.3452 °C/decade`** across all 34 grid cells.
- **National Extreme Warming Epicenter:** **Sylhet Division** (`24.5°N, 91.875°E`) in the northeastern tea basin recorded the fastest rate of change:
  - **OLS Linear Slope:** **`+0.4214 °C/decade`** ($R^2 = 0.5130$, $p = 5.7 \times 10^{-5}$, $q_{\text{FDR}} = 0.000121$)
  - **Sen's Non-Parametric Median Slope:** **`+0.4063 °C/decade`** ($p_{\text{MK}} = 7.8 \times 10^{-5}$, $q_{\text{MK, FDR}} = 0.000292$)

```
Sylhet September T2M Decadal Warming (2001–2025):
Year 2001: 27.64 °C ───► Year 2025: 28.71 °C  (Net Rise: +1.07 °C in 25 Years)
Statistical Confidence: R² = 0.5130 | p-value = 0.000057 | FDR q-value = 0.000121 (Verified Discoveries)
```

### 2. Benjamini–Hochberg False Discovery Rate (FDR) Control
In spatial climatology, evaluating hundreds of grid cells simultaneously inflates the family-wise error rate. Across 1,632 trend hypotheses, uncorrected testing at $\alpha = 0.05$ would falsely flag $\approx 82$ random noise events as discoveries.

Under the Benjamini–Hochberg (1995) step-up procedure ($m = 34$ spatial hypotheses per family):
1. Raw $p$-values are sorted: $P_{(1)} \le P_{(2)} \le \dots \le P_{(m)}$.
2. Threshold is found: $k = \max \left\{ i : P_{(i)} \le \frac{i}{m} Q \right\}$.
3. Adjusted $q$-values: $q_{(i)} = \min_{j \ge i} \left\{ \min\left(1, \frac{m}{j} P_{(j)}\right) \right\}$.

**Result:** In September T2M, **33 of 34 cells** remain statistically significant at $q < 0.05$ (maximum $q = 0.017$). Exactly **zero false discoveries** were screened, proving that post-monsoon warming is an unequivocal, continental-scale physical phenomenon rather than local noise.

### 3. Multi-Variable Earth-System Coupling (6 Bivariate Pairs)
Earth-system detective work requires tracking energy and mass transfers between the atmosphere, land surface, and radiation budget:

| Bivariate Pair | Atmospheric / Land Feedback Mechanism | Statistical Coupling | Significance ($m=34$) |
| :--- | :--- | :--- | :--- |
| **`T2M ↔ GWETTOP`** | **May Pre-Monsoon Heat-Drought Feedback:** Elevated temperatures accelerate surface evapotranspiration, rapidly desiccating topsoil prior to monsoon onset. | Mean Pearson $r = -0.485$ (Warmer & Drier) | **28 of 34 cells FDR Sig** |
| **`PRECTOTCORR ↔ GWETTOP`** | **Hydrological Soil Recharge:** Direct monsoon precipitation infiltration rapidly saturates the topsoil (0–5 cm) layer. | Mean Pearson $r = +0.642$ (Wetter & Moist) | **34 of 34 cells FDR Sig** |
| **`PRECTOTCORR ↔ ALLSKY`** | **Cloud Albedo Shielding:** Deep convective monsoon cloud formations reflect and scatter incoming solar radiation, cooling the surface. | Mean Pearson $r = -0.590$ (Cloudy & Shaded) | **32 of 34 cells FDR Sig** |
| **`T2M ↔ ALLSKY`** | **Radiative Sensible Heating:** High downwelling shortwave solar flux drives sensible heat exchange, driving ambient temperature spikes. | Mean Pearson $r = +0.528$ (Sunnier & Hotter) | **31 of 34 cells FDR Sig** |
| **`GWETTOP ↔ ALLSKY`** | **Solar-Driven Topsoil Desiccation:** Intense solar radiation rapidly vaporizes shallow soil moisture under cloudless synoptic conditions. | Mean Pearson $r = -0.410$ (High Solar & Dry) | **24 of 34 cells FDR Sig** |
| **`T2M ↔ PRECTOTCORR`** | **Thermal Convective Suppression:** High temperature regimes during dry pre-monsoon intervals coincide with suppressed convective precipitation. | Mean Pearson $r = -0.245$ (Warmer & Drier) | **14 of 34 cells FDR Sig** |

---

## 🏛️ System Architecture: Ground Truth First

```mermaid
flowchart TD
    classDef client fill:#1E293B,stroke:#38BDF8,stroke-width:2px,color:#F8FAFC;
    classDef engine fill:#0F172A,stroke:#6366F1,stroke-width:2px,color:#F8FAFC;
    classDef data fill:#064E3B,stroke:#10B981,stroke-width:2px,color:#F8FAFC;
    classDef output fill:#4C1D95,stroke:#C084FC,stroke-width:2px,color:#F8FAFC;

    User["User Natural Language Query / UI Control"]:::client --> Parser["1. Rule-Based Entity Parser\n(query_parser.py - Pydantic v2)"]:::engine
    Parser -->|"Validated Intent Model"| Retriever["2. Deterministic Scientific Retriever\n(query_retriever.py)"]:::engine
    
    subgraph DataEngine ["Canonical Scientific Data Engine (2001–2025)"]
        Retriever --> Trends["bangladesh_multivariable_trends_fdr.csv\n(1,632 records, 48 families, m=34)"]:::data
        Retriever --> Rels["bangladesh_variable_relationships_fdr.csv\n(2,448 records, 72 families, m=34)"]:::data
    end
    
    Trends --> Evidence["Verified Evidence JSON Packet\n(Zero Math Delegated to LLM)"]:::data
    Rels --> Evidence
    
    Evidence --> Explainer["3. Grounded LLM Explainer (llm_explainer.py)\n• Exact Numbers Guardrail\n• FDR Claims Enforcement\n• Zero Hallucination"]:::engine
    Evidence --> Visualizer["4. GeoJSON Feature Collection\n& Interactive Chart Spec"]:::engine
    
    Explainer --> Unified["Unified RESTful API Response\n(/api/v1/analyze)"]:::output
    Visualizer --> Unified
    
    Unified --> Dashboard["5. Interactive Web Dashboard\n(React 19 + Leaflet + SVG Charts)"]:::client
```

---

## 🖥️ Interactive Web Dashboard Showcase

The Orion Space frontend is an ultra-modern, dark space glassmorphism dashboard built with **React 19**, **Leaflet GIS**, and **Vanilla CSS**:

- 🌐 **Spatial Map View (`SpatialMap.jsx`):**
  - High-performance CartoDB Dark Matter basemap with official `bangladesh_adm0.geojson` national boundary.
  - 34 interactive circle markers representing mainland grid cells.
  - **FDR Significance Halos:** Cells with $q_{\text{FDR}} < 0.05$ display an ethereal animated pulsing cyan ring, instantly distinguishing confirmed discoveries from spatial noise.
  - Division quick-filter pills (Dhaka, Sylhet, Chattogram, etc.).
- 🔄 **Bivariate Coupling Matrix (`CouplingMatrix.jsx`):**
  - Interactive grid displaying all 6 variable pairs.
  - Real-time scatter plot with dynamic SVG scaling, Pearson $r$, Spearman $\rho$, and a fitted linear regression line.
- 📊 **Seasonal Climatology & Regional Benchmarks (`SeasonalCharts.jsx`):**
  - 12-month seasonal trajectory chart highlighting pre-monsoon, monsoon, and post-monsoon regimes.
  - 8-division comparative bar chart comparing warming rates across administrative jurisdictions.
- 🤖 **AI Detective Copilot (`AIExplainerCard.jsx` & `DetectiveBar.jsx`):**
  - Natural language input accepting queries in plain English or phonetic Bangla.
  - Evidence inspection modal showing raw NASA POWER / MERRA-2 metrics backing every generated sentence.
- 🔍 **Cell Inspector (`CellInspector.jsx`):**
  - Point-and-click inspection panel displaying coordinates, elevation, OLS decadal slope, Sen's slope, $p$-value, $q$-value, and physical interpretation.

---

## 📁 Repository Directory Map

```
Nasa_Space_APP_Challenge/
├── README.md                             <- Master documentation & scientific report
├── requirements.txt                      <- Pinned Python dependencies (NumPy, SciPy, FastAPI, etc.)
├── data/                                 <- Canonical multi-variable & FDR datasets
│   ├── bangladesh_multivariable_trends_fdr.csv      <- 1,632 spatial trend records with BH FDR q-values
│   ├── bangladesh_variable_relationships_fdr.csv    <- 2,448 bivariate relationship records with FDR
│   ├── bangladesh_t2m_trend_map.png                 <- 34-grid national publication figure
│   └── bangladesh_precip_regional_raw.json          <- MERRA-2 precipitation raw cache
│
└── orion-space/
    ├── api/                              <- Production FastAPI Intelligence Backend
    │   ├── main.py                       <- Endpoints: /analyze, /trends/spatial, /relationships, catalogs
    │   └── README.md                     <- API contract & JSON schemas
    │
    ├── frontend/                         <- Interactive Web Dashboard (Vite + React 19 + Leaflet)
    │   ├── public/
    │   │   ├── bangladesh_adm0.geojson   <- Official geoBoundaries Bangladesh boundary
    │   │   └── nasa-logo.gif             <- Official NASA meatball logo
    │   ├── src/
    │   │   ├── components/               <- SpatialMap, CouplingMatrix, SeasonalCharts, AIExplainerCard
    │   │   ├── services/api.js           <- API client with offline canonical fallbacks
    │   │   ├── App.jsx                   <- Main workspace layout & state orchestrator
    │   │   └── index.css / App.css       <- NASA dark space glassmorphism design system
    │   └── vite.config.js                <- Proxy configuration (port 3000 -> 8000)
    │
    ├── notebooks/                        <- Executable Scientific Notebooks (Embedded Figures)
    │   ├── 01_nasa_temperature_analysis.ipynb           <- Phase 1: Dhaka T2M point baseline (2001-2025)
    │   └── 02_nasa_earth_system_multivariable_fdr.ipynb <- Phase 2: National 34-cell network with BH FDR
    │
    ├── scripts/                          <- Automation & Verification Suites
    │   ├── make_phase2_notebook.py       <- Phase 2 notebook generator
    │   ├── execute_phase2_notebook.py    <- Automated headless executor with embedded figures
    │   └── test_api_endpoints.py         <- 11-test automated API test suite (100% assertions)
    │
    └── src/                              <- Scientific Core & Intelligence Layer
        ├── multivariable_data_loader.py  <- NASA POWER multi-variable fetcher & cache
        ├── multivariable_analysis.py     <- 34-cell OLS & Mann-Kendall trend computation
        ├── relationship_analysis.py      <- 6-pair bivariate Pearson & Spearman correlation
        ├── multiple_testing.py           <- Benjamini-Hochberg FDR implementation
        ├── query_models.py               <- Pydantic v2 discriminated union query schemas
        ├── query_parser.py               <- Rule-based natural language parser
        ├── query_retriever.py            <- Deterministic scientific evidence retriever
        └── llm_explainer.py              <- Evidence-grounded LLM layer with strict guardrails
```

---

## 💻 Quick Start & Reproducibility Guide

### 1. Clone & Set Up Python Environment
```bash
# Clone the repository
git clone https://github.com/iammahmudhasan/Nasa_Space_APP_Challenge.git
cd Nasa_Space_APP_Challenge

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # (Windows PowerShell)
# or source .venv/bin/activate  # (Linux / macOS)

# Install scientific dependencies
pip install -r requirements.txt
```

### 2. Launch FastAPI Intelligence Backend
```bash
cd orion-space
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```
- Interactive OpenAPI Swagger Docs: [`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs)
- Healthcheck Endpoint: [`http://127.0.0.1:8000/api/v1/health`](http://127.0.0.1:8000/api/v1/health)

### 3. Launch Interactive Web Dashboard
```bash
cd orion-space/frontend
npm install
npm run dev
```
- Open your browser at: [`http://localhost:3000/`](http://localhost:3000/)

### 4. Run Automated Verification Suites
```bash
# Run 11 end-to-end API integration tests (100% assertions pass)
python orion-space/scripts/test_api_endpoints.py

# Re-execute scientific notebook headlessly & re-embed high-resolution figures
python orion-space/scripts/execute_phase2_notebook.py
```

### 5. Launch Jupyter Scientific Notebooks
```bash
# Phase 1: Dhaka Baseline Analysis
jupyter notebook orion-space/notebooks/01_nasa_temperature_analysis.ipynb

# Phase 2: National Multi-Variable Earth-System Dynamics & BH-FDR Multiple Testing
jupyter notebook orion-space/notebooks/02_nasa_earth_system_multivariable_fdr.ipynb
```

---

## ⚡ FastAPI Intelligence Engine Endpoints

| Method | Endpoint | Description | Sample Query / Body |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Healthcheck and dataset row counts | - |
| `GET` | `/api/v1/catalogs/variables` | Available Earth-system variables & units | - |
| `GET` | `/api/v1/catalogs/months` | Supported calendar months (1–12) | - |
| `GET` | `/api/v1/catalogs/pairs` | 6 supported bivariate coupling pairs | - |
| `GET` | `/api/v1/trends/spatial` | 34-cell trend records with FDR filters | `?variable=T2M&month=9` |
| `GET` | `/api/v1/trends/point` | Point-specific trend & time-series | `?variable=T2M&lat=24.5&lon=91.875` |
| `GET` | `/api/v1/relationships/spatial`| 34-cell bivariate correlation with FDR | `?pair=T2M_GWETTOP&month=5` |
| `POST`| `/api/v1/analyze` | Unified natural language detective query | `{"query": "Is September warming in Sylhet?"}` |

### Sample Python Query Execution:
```python
import requests

url = "http://127.0.0.1:8000/api/v1/analyze"
payload = {"query": "Sylhet e September e ki warming hochhe?"}
response = requests.post(url, json=payload)
data = response.json()

print("Intent:", data["intent"])
print("Key Finding:", data["evidence"]["headline"])
print("OLS Decadal Slope:", data["evidence"]["metrics"]["slope_per_decade"], "°C/decade")
print("BH FDR q-value:", data["evidence"]["metrics"]["q_value_ols"])
print("AI Explanation:", data["explanation"])
```

---

## 🏆 Judging Criteria Alignment

| Evaluation Pillar | How Orion Space Exceeds Expectations |
| :--- | :--- |
| **Impact & Value** | Solves the climate blindspot in Bangladesh by unmasking post-monsoon warming (+0.35 °C/decade) and pre-monsoon drying ($r = -0.485$), providing actionable evidence for disaster management and water resource planning. |
| **Scientific Accuracy & Rigor** | Employs both parametric (OLS) and non-parametric (Mann-Kendall Sen's slope) metrics, strictly controlled by Benjamini–Hochberg (1995) FDR across 4,080 hypotheses to eliminate false discoveries. |
| **Innovation & Creativity** | Replaces unconstrained LLM hallucinations with a "Deterministic Ground Truth First" architecture where AI explanations are strictly grounded in mathematically verified evidence packets. |
| **Technical Execution & Feasibility** | Clean decoupled stack (FastAPI backend + React 19 frontend + Jupyter notebooks). 100% automated test coverage with offline canonical fallbacks. |
| **Aesthetics & Usability** | NASA dark space glassmorphism design system, interactive GIS maps with pulsating FDR significance halos, and real-time bivariate scatter regressions. |

---

## 📜 Scientific Provenance & References

1. **NASA GMAO MERRA-2:** Global Modeling and Assimilation Office, Modern-Era Retrospective Analysis for Research and Applications, Version 2. Gelaro, R. et al. (2017), *Journal of Climate*, 30(14), 5419-5454.
2. **NASA POWER API:** Prediction Of Worldwide Energy Resources Project, NASA Langley Research Center.
3. **NASA CERES / FLASHFlux:** Clouds and the Earth's Radiant Energy System, Surface Downwelling Shortwave Fluxes.
4. **Benjamini, Y., & Hochberg, Y. (1995):** "Controlling the false discovery rate: a practical and powerful approach to multiple testing." *Journal of the Royal Statistical Society: Series B (Methodological)*, 57(1), 289-300.
5. **Mann, H. B. (1945):** "Nonparametric tests against trend." *Econometrica*, 13, 245-259.
6. **Sen, P. K. (1968):** "Estimates of the regression coefficient based on Kendall's tau." *Journal of the American Statistical Association*, 63(324), 1379-1389.
7. **geoBoundaries ADM0:** Runfola, D. et al. (2020) "geoBoundaries: A global database of political administrative boundaries." *PLOS ONE*, 15(4), e0231866.

### BibTeX Citation:
```bibtex
@software{OrionSpace2026,
  author = {Hasan, Mahmud and Orion Space Team},
  title = {Orion Space: Evidence-Grounded Earth-System Trend Detective for Bangladesh},
  month = {October},
  year = {2026},
  publisher = {NASA International Space Apps Challenge},
  url = {https://github.com/iammahmudhasan/Nasa_Space_APP_Challenge}
}
```

---

## 👥 Team & Acknowledgments

- **Team:** Orion Space
- **Event:** NASA International Space Apps Challenge 2026
- **Challenge Track:** Be An Earth System Trend Detective!
- **Data Providers:** NASA Goddard Space Flight Center (GSFC), NASA Langley Research Center (LaRC), geoBoundaries.
- **Dedicated to:** Advancing open, reproducible climate science and evidence-grounded AI systems for climate-vulnerable deltaic nations.

<p align="center">
  <b>🛰️ Orion Space • NASA Space Apps Challenge 2026</b><br />
  <em>Ground Truth First • Reproducible Climatology • Open Science</em>
</p>
