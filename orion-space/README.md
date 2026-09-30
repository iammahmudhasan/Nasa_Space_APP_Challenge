# 🛰️ Orion Space: Earth System Trend Detective

**NASA Space Apps Challenge 2026**  
**Challenge Track:** Be An Earth System Trend Detective! (Advanced Earth Science)  
**Investigative Focus:** Decadal Multi-Variable Earth-System Shifts & Statistical Coupling over Bangladesh (2001–2025)  
**Data Provenance:** NASA Goddard Modeling and Assimilation Office (GMAO) MERRA-2 & CERES/FLASHFlux via NASA POWER API  
**Statistical Rigor:** Benjamini–Hochberg (1995) False Discovery Rate (FDR) Multiple-Testing Correction  

---

## 🔍 Scientific Challenge Overview

Earth’s environmental system is an interconnected web where variables fluctuate, rise, fall, and trend in divergent directions across space and time. 

The NASA challenge charges us with answering four fundamental scientific questions:
1. **What is changing?** (4 Key Earth-System Variables: Surface Air Temperature `T2M`, Precipitation `PRECTOTCORR`, Surface Soil Moisture `GWETTOP`, Downwelling Solar Radiation `ALLSKY_SFC_SW_DWN`)
2. **Where is it changing?** (National 34-Grid Network covering all 8 administrative divisions of Bangladesh, filtered by geoBoundaries ADM0 Point-in-Polygon intersection)
3. **By how much is it changing?** (Rate of change per decade, evaluated via OLS linear regression and non-parametric Mann-Kendall Sen's slope)
4. **Is the change Statistically Significant?** (Rigorous hypothesis testing with Benjamini–Hochberg False Discovery Rate correction at $q < 0.05$ across 48 trend testing families and 72 bivariate relationship testing families)

---

## 📁 Project Architecture

```
orion-space/
│
├── api/                                  <- Production FastAPI Backend & Intelligence Router
│   ├── main.py                           <- API application with /analyze, catalogs, and spatial endpoints
│   └── README.md                         <- Official RESTful API specification & contract
│
├── data/                                 <- Canonical Analysis-Ready Datasets
│   ├── bangladesh_multivariable_trends_fdr.csv      <- 1,632 spatial trend records with BH FDR q-values
│   ├── bangladesh_variable_relationships_fdr.csv    <- 2,448 bivariate relationship records with FDR
│   ├── bangladesh_precip_regional_raw.json          <- MERRA-2 precipitation raw cache
│   ├── bangladesh_soil_moisture_regional_raw.json   <- MERRA-2 Land soil moisture raw cache
│   └── bangladesh_solar_regional_raw.json           <- CERES solar irradiance raw cache
│
├── frontend/                             <- Interactive Web Dashboard (Vite + React + Leaflet)
│   ├── public/
│   │   ├── bangladesh_adm0.geojson       <- Official geoBoundaries Bangladesh ADM0 boundary
│   │   └── nasa-logo.gif                 <- NASA meatball logo
│   ├── src/
│   │   ├── components/                   <- SpatialMap, CouplingMatrix, SeasonalCharts, AIExplainerCard
│   │   ├── services/api.js               <- API client with offline canonical fallbacks
│   │   ├── App.jsx                       <- Dashboard layout & state orchestrator
│   │   └── index.css / App.css           <- NASA dark glassmorphism design system
│   └── vite.config.js                    <- Proxy configured to port 8000
│
├── notebooks/                            <- Executable Scientific Notebooks
│   ├── 01_nasa_temperature_analysis.ipynb           <- Phase 1: Dhaka T2M point analysis (2001-2025)
│   └── 02_nasa_earth_system_multivariable_fdr.ipynb <- Phase 2: Multi-Variable 34-cell network with BH FDR
│
├── scripts/
│   ├── make_notebook.py                  <- Phase 1 notebook generator
│   ├── make_phase2_notebook.py           <- Phase 2 notebook generator
│   ├── execute_phase2_notebook.py        <- Headless notebook execution & plot embedding
│   └── test_api_endpoints.py             <- 11-test automated API test suite
│
├── src/                                  <- Scientific Core & Intelligence Layer
│   ├── multivariable_data_loader.py      <- NASA POWER API multi-variable fetcher
│   ├── multivariable_analysis.py         <- 34-cell OLS & Mann-Kendall trend computation
│   ├── relationship_analysis.py          <- 6-pair bivariate Pearson & Spearman correlation
│   ├── multiple_testing.py               <- Benjamini-Hochberg FDR implementation
│   ├── query_models.py                   <- Pydantic v2 discriminated union query schemas
│   ├── query_parser.py                   <- Rule-based natural language parser
│   ├── query_retriever.py                <- Deterministic scientific evidence retriever
│   └── llm_explainer.py                  <- Evidence-grounded LLM layer with strict guardrails
│
├── requirements.txt                      <- Pinned Python scientific & backend dependencies
└── README.md                             <- Scientific documentation & challenge report
```

---

## 🔬 Scientific Findings Summary

### Phase 1: Point Trend Analysis (Dhaka, 2001–2025)
- **Annual Aggregate:** Inter-annual noise dominates on an annual scale ($p = 0.757$, not significant).
- **Seasonal Deconstruction:** Concentrated late-monsoon / post-monsoon warming in July ($+0.167^\circ\text{C}$/dec, $p=0.021$), September ($+0.361^\circ\text{C}$/dec, $p<0.001$), and October ($+0.452^\circ\text{C}$/dec, $p=0.006$).

### Phase 2: Multi-Variable Grid & FDR Significance (34 Grid Cells, National)
1. **Ubiquitous September Warming:** Across all 34 mainland cells, national mean warming in September reached $+0.3452^\circ\text{C}/\text{decade}$.
2. **National Extreme Warming Peak:** Sylhet Division (`24.5°N, 91.875°E`) experienced the fastest rate of change:
   - **OLS Slope:** $+0.4214^\circ\text{C}/\text{decade}$ ($R^2 = 0.5130$, $p = 5.7 \times 10^{-5}$, $q_{\text{FDR}} = 0.000121$)
   - **Sen's Median Slope:** $+0.4063^\circ\text{C}/\text{decade}$ ($p_{\text{MK}} = 7.8 \times 10^{-5}$, $q_{\text{MK, FDR}} = 0.000292$)
3. **FDR Multiple-Testing Control:** **33 of 34 cells** remained statistically significant after Benjamini–Hochberg FDR correction at $q < 0.05$ (maximum $q = 0.017$). Zero false discoveries were screened for September T2M, confirming an unequivocal climate signal.
4. **Earth-System Coupling & Feedbacks:**
   - `T2M ↔ GWETTOP` (May Pre-Monsoon): Strong negative correlation (mean Pearson $r = -0.485$, 28 of 34 cells FDR significant), demonstrating land-atmosphere drying feedbacks prior to monsoon onset.
   - `PRECTOTCORR ↔ GWETTOP`: Strong positive infiltration coupling (mean Pearson $r = +0.642$, 34 of 34 cells FDR significant).
   - `PRECTOTCORR ↔ ALLSKY_SFC_SW_DWN`: Cloud albedo shading effect (mean Pearson $r = -0.590$).

---

## 🚀 How to Run the System

### 1. Environment Setup
```bash
# Clone the repository
git clone https://github.com/iammahmudhasan/Nasa_Space_APP_Challenge.git
cd Nasa_Space_APP_Challenge

# Activate Python virtual environment
.\.venv\Scripts\Activate.ps1   # (Windows)
# or source .venv/bin/activate  # (Linux/macOS)

# Install backend dependencies
pip install -r requirements.txt
```

### 2. Launch the FastAPI Intelligence Backend
```bash
cd orion-space
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```
- API Metadata & Docs: `http://127.0.0.1:8000/docs`

### 3. Launch the Interactive Web Dashboard
```bash
cd orion-space/frontend
npm install
npm run dev
```
- Open your browser at: `http://localhost:3000/`

### 4. Explore the Scientific Notebooks
```bash
# Phase 1: Single-Point Analysis (Dhaka)
jupyter notebook orion-space/notebooks/01_nasa_temperature_analysis.ipynb

# Phase 2: Multi-Variable Earth-System Dynamics & BH-FDR Multiple Testing
jupyter notebook orion-space/notebooks/02_nasa_earth_system_multivariable_fdr.ipynb
```
*(Both notebooks contain fully pre-computed figures, tables, and execution outputs embedded directly in the files for immediate offline review.)*
