# 🌌 NASA Space Apps Challenge 2026
## 🛰️ Project: Orion Space — Earth System Trend Detective

<p align="center">
  <img src="Nasa-logo.gif" alt="NASA Logo" width="160" />
</p>

### **Challenge:** *Be An Earth System Trend Detective!*  
**Category:** Advanced Earth Science, Climatology, Statistical Multiple Testing & AI Intelligence  
**Data Provenance:** NASA Goddard Modeling and Assimilation Office (GMAO) MERRA-2 & CERES/FLASHFlux via NASA POWER API  
**Investigation Window:** 2001-01-01 to 2025-12-31 (25 Continuous Years)  
**Spatial Network:** 34 Mainland Bangladesh Grid Cells (geoBoundaries ADM0 Point-in-Polygon Filtered)  
**Statistical Rigor:** Benjamini–Hochberg (1995) False Discovery Rate (FDR) Multiple-Testing Correction  

---

## 🎯 The Detective Question
> *"How are interconnected Earth-system variables (surface air temperature, precipitation, soil moisture, and solar radiation) co-evolving across Bangladesh over 2001–2025, which spatial warming and drying trends remain robustly significant after Benjamini–Hochberg False Discovery Rate (FDR) correction, and what physical feedbacks link these variables?"*

---

## 🔬 Core Scientific Findings Summary

### 1. Phase 1: Dhaka Single-Point Baseline (2001–2025)
- **Annual Aggregate:** Inter-annual weather noise dominates on an annual aggregate scale ($p = 0.757$, not statistically significant).
- **Seasonal Deconstruction:** Concentrated, statistically significant warming in late-monsoon / post-monsoon months:
  - **July:** `+0.167 °C/decade` ($p = 0.0207$) — **Significant ✅ ($p < 0.05$)**
  - **September:** `+0.361 °C/decade` ($p < 0.0001$) — **Significant ✅ ($p < 0.001$)**
  - **October:** `+0.452 °C/decade` ($p = 0.0062$) — **Significant ✅ ($p < 0.01$, +1.13°C Total)**

### 2. Phase 2: National Multi-Variable 34-Grid Network & BH-FDR Correction
- **Ubiquitous September Warming:** Across all 34 mainland grid cells, the national mean warming rate reached **`+0.3452 °C/decade`**.
- **National Extreme Warming Peak:** Sylhet Division (`24.5°N, 91.875°E`) recorded the fastest warming slope in Bangladesh:
  - **OLS Linear Slope:** **`+0.4214 °C/decade`** ($R^2 = 0.5130$, $p = 5.7 \times 10^{-5}$, $q_{\text{FDR}} = 0.000121$)
  - **Sen's Median Slope:** **`+0.4063 °C/decade`** ($p_{\text{MK}} = 7.8 \times 10^{-5}$, $q_{\text{MK, FDR}} = 0.000292$)
- **Benjamini–Hochberg FDR Multiple-Testing Control:**
  - Tested across 48 spatial trend families ($m = 34$ hypotheses per family).
  - For September T2M: **33 of 34 cells** remained statistically significant after Benjamini–Hochberg FDR correction at $q < 0.05$ (Maximum $q = 0.017$). Zero false discoveries were screened, confirming an unequivocal climate signal.
- **Earth-System Bivariate Coupling (6 Pairs, 72 Families):**
  - `T2M ↔ GWETTOP` (May Pre-Monsoon): Strong negative correlation (mean Pearson $r = -0.485$, 28 of 34 cells FDR significant), demonstrating land-atmosphere desiccation and heat-drought feedback before monsoon onset.
  - `PRECTOTCORR ↔ GWETTOP`: Direct infiltration and soil moisture recharge (mean Pearson $r = +0.642$, 34 of 34 cells FDR significant).
  - `PRECTOTCORR ↔ ALLSKY_SFC_SW_DWN`: Cloud albedo shading effect (mean Pearson $r = -0.590$).

---

## 📁 Repository Structure

```
Nasa_Space_APP_Challenge/
├── README.md                             <- Master challenge overview & scientific documentation
├── requirements.txt                      <- Global Python dependencies
├── data/                                 <- Canonical multi-variable & FDR datasets
│   ├── bangladesh_multivariable_trends_fdr.csv      <- 1,632 trend records with BH FDR q-values
│   ├── bangladesh_variable_relationships_fdr.csv    <- 2,448 bivariate relationship records with FDR
│   ├── bangladesh_precip_regional_raw.json          <- MERRA-2 precipitation raw cache
│   ├── bangladesh_soil_moisture_regional_raw.json   <- MERRA-2 Land soil moisture raw cache
│   └── bangladesh_solar_regional_raw.json           <- CERES solar irradiance raw cache
│
└── orion-space/
    ├── api/                              <- Production FastAPI Intelligence Backend
    │   ├── main.py                       <- Endpoints: /analyze, /trends/spatial, /relationships, catalogs
    │   └── README.md                     <- RESTful API contract & JSON schemas
    │
    ├── frontend/                         <- Interactive Web Dashboard (Vite + React + Leaflet)
    │   ├── public/
    │   │   ├── bangladesh_adm0.geojson   <- Official geoBoundaries Bangladesh boundary
    │   │   └── nasa-logo.gif             <- NASA meatball logo
    │   ├── src/                          <- SpatialMap, CouplingMatrix, SeasonalCharts, AIExplainerCard
    │   └── index.css / App.css           <- NASA dark space glassmorphism design system
    │
    ├── notebooks/                        <- Executable Scientific Notebooks (Pre-computed Figures)
    │   ├── 01_nasa_temperature_analysis.ipynb           <- Phase 1: Dhaka T2M point analysis (2001-2025)
    │   └── 02_nasa_earth_system_multivariable_fdr.ipynb <- Phase 2: National 34-cell network with BH FDR
    │
    ├── scripts/                          <- Automation & Verification Test Suites
    │   ├── make_notebook.py              <- Phase 1 notebook generator
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

## 💻 Quick Start & Execution

### 1. Setup Virtual Environment
```bash
# Clone the repository
git clone https://github.com/iammahmudhasan/Nasa_Space_APP_Challenge.git
cd Nasa_Space_APP_Challenge

# Activate virtual environment
.\.venv\Scripts\Activate.ps1   # (Windows)
# or source .venv/bin/activate  # (Linux/macOS)

# Install dependencies
pip install -r requirements.txt
```

### 2. Launch FastAPI Intelligence Backend
```bash
cd orion-space
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```
- Interactive OpenAPI Docs: `http://127.0.0.1:8000/docs`

### 3. Launch Interactive Web Dashboard
```bash
cd orion-space/frontend
npm install
npm run dev
```
- Dashboard URL: `http://localhost:3000/`

### 4. Explore Scientific Jupyter Notebooks
```bash
# Phase 1 Notebook: Dhaka Baseline Analysis
jupyter notebook orion-space/notebooks/01_nasa_temperature_analysis.ipynb

# Phase 2 Notebook: Multi-Variable Earth-System Dynamics & BH FDR Correction
jupyter notebook orion-space/notebooks/02_nasa_earth_system_multivariable_fdr.ipynb
```
*(Both notebooks contain fully pre-computed figures, tables, and execution outputs embedded directly in the files for immediate offline review.)*
