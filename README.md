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
> *"How has surface air temperature changed over Bangladesh over the long term, and are the observed trends statistically significant under formal hypothesis testing?"*

---

## 🚀 Key Phase 1 Findings (Dhaka Baseline)

1. **Annual Aggregated Analysis:**
   - 25-Year Annual Mean Slope: **`+0.0026 °C / year`** (`+0.026 °C / decade`)
   - Ordinary Least Squares $p$-value: **`0.7571`** (Mann-Kendall: **`0.6913`**)
   - **Verdict:** On an annual aggregated basis, the trend is **not statistically significant** ($\alpha = 0.05$). This illustrates why formal statistical testing is essential to distinguish systematic shifts from background inter-annual variance.

2. **Seasonal Deconstruction Findings:**
   - When decomposing the 25-year daily record into monthly averages, distinct seasonal differences emerge:
   - **July:** **`+0.167 °C/decade`** ($p = 0.0207$) — **Statistically Significant ✅ ($p < 0.05$)**
   - **September:** **`+0.361 °C/decade`** ($p < 0.0001$) — **Statistically Significant ✅ ($p < 0.001$)**
   - **October:** **`+0.452 °C/decade`** ($p = 0.0062$) — **Statistically Significant ✅ ($p < 0.01$, +1.13°C Total Shift)**
   - **Conclusion:** Statistically significant warming is observed specifically in late-monsoon and post-monsoon months (July, September, October), whereas other months exhibit no statistically significant long-term trend, moderating the annual average.

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
