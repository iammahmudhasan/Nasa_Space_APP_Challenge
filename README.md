# 🌌 NASA Space Apps Challenge 2026
## 🛰️ Project: Orion Space — Earth System Trend Detective

<p align="center">
  <img src="Nasa-logo.gif" alt="NASA Logo" width="160" />
</p>

### **Challenge:** *Be An Earth System Trend Detective!*  
**Category:** Advanced Earth Science, Climatology & Software Intelligence  
**Focus Variable:** Surface Air Temperature at 2 Meters (`T2M`)  
**Data Provenance:** NASA Goddard Modeling and Assimilation Office (GMAO) MERRA-2 via NASA POWER API  
**Investigation Window:** 2001-01-01 to 2025-12-31 (25 Continuous Years, 9,131 Daily Observations)  

---

## 🎯 The Detective's Question
> *"How has surface air temperature changed over Bangladesh over the long term, and is the observed trend a scientifically proven reality or a statistical illusion?"*

---

## 🚀 Key Phase 1 Discoveries (Dhaka Baseline)

1. **The Annual Illusion:**
   - 25-Year Annual Mean Slope: **`+0.0026 °C / year`** (`+0.026 °C / decade`)
   - Ordinary Least Squares $p$-value: **`0.7571`** (Mann-Kendall: **`0.6913`**)
   - **Verdict:** On an annual aggregated basis, the trend is **NOT statistically significant** ($\alpha = 0.05$). This illustrates why rigorous significance testing is critical to avoid false assumptions.

2. **The Seasonal Deconstruction Breakthrough:**
   - When decomposing the daily data into monthly climate intervals, we uncover severe, hidden warming:
   - **July (Monsoon):** **`+0.167 °C/decade`** ($p = 0.0207$) — **Statistically Significant ✅**
   - **September (Late Monsoon):** **`+0.361 °C/decade`** ($p < 0.0001$) — **Extremely Statistically Significant ✅**
   - **October (Post-Monsoon):** **`+0.452 °C/decade`** ($p = 0.0062$) — **Highly Statistically Significant ✅ (+1.13°C Total Change)**
   - **Conclusion:** Late-season heatwaves have intensified dramatically over Bangladesh, while earlier seasonal fluctuations historically masked this signal in simple annual averages.

---

## 📁 Repository Structure

```
.
├── Nasa-logo.gif
├── README.md
├── requirements.txt
└── orion-space/
    ├── README.md
    ├── requirements.txt
    ├── data/
    │   ├── dhaka_t2m_2001_2025.csv          <- 9,131 daily records cached from NASA POWER
    │   └── dhaka_t2m_trend_analysis.png     <- High-resolution scientific publication figure
    ├── notebooks/
    │   └── 01_nasa_temperature_analysis.ipynb <- Complete executed Jupyter Notebook
    ├── scripts/
    │   ├── make_notebook.py                 <- Notebook builder
    │   └── execute_notebook.py              <- Output capture runner
    └── src/
        ├── __init__.py
        ├── data_loader.py                   <- NASA POWER API data fetching & cleaning
        └── trend_analysis.py                <- Parametric (OLS) & Non-Parametric (Mann-Kendall, Sen's) engine
```

---

## 💻 Quick Start

```bash
# Clone the repository
git clone https://github.com/iammahmudhasan/Nasa_Space_APP_Challenge.git
cd Nasa_Space_APP_Challenge

# Setup virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run the notebook
jupyter notebook orion-space/notebooks/01_nasa_temperature_analysis.ipynb
```

---

## 🗺️ Roadmap
- **Phase 1 (Complete):** Core Scientific Pipeline, Dhaka representative point validation, OLS & Mann-Kendall significance engine.
- **Phase 2 (Upcoming):** Spatial grid expansion across all 8 administrative divisions of Bangladesh.
- **Phase 3:** Multi-variable integration (Precipitation `PRECTOTCORR`, Soil Moisture `GWETTOP`, Surface Solar Radiation `ALLSKY_SFC_SW_DWN`).
