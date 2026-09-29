# 🛰️ Orion Space: Earth System Trend Detective

**NASA Space Apps Challenge 2026**  
**Challenge Track:** Be An Earth System Trend Detective! (Advanced Earth Science)  
**Investigative Focus:** Decadal Surface Air Temperature (`T2M`) Shifts over Bangladesh  
**Data Provenance:** NASA Goddard Modeling and Assimilation Office (GMAO) MERRA-2 Assimilation Model via NASA POWER API  

---

## 🔍 Scientific Challenge Overview

Earth’s environmental system is an interconnected web where variables can fluctuate, rise, fall, and trend in divergent directions across different spatial and temporal scales. 

The NASA challenge charges us with answering four fundamental scientific questions:
1. **What is changing?** (Surface Air Temperature at 2m, `T2M`)
2. **Where is it changing?** (Dhaka, Bangladesh: 23.8103°N, 90.4125°E — Phase 1 Point Analysis)
3. **By how much is it changing?** (Rate of change in °C/year, °C/decade, and total 25-year cumulative change)
4. **Is the change Statistically Significant or a Statistical Illusion?** (Validated via Parametric OLS Regression and Non-Parametric Mann-Kendall Trend Test with Sen's Slope Estimator)

---

## 📁 Project Architecture

```
orion-space/
│
├── data/
│   ├── dhaka_t2m_2001_2025.csv          <- 9,131 daily observations cached from NASA POWER
│   └── dhaka_t2m_trend_analysis.png     <- High-resolution scientific publication figure
│
├── notebooks/
│   └── 01_nasa_temperature_analysis.ipynb <- Executable Jupyter Notebook (A-F Steps)
│
├── scripts/
│   ├── make_notebook.py                 <- Automated notebook builder
│   └── execute_notebook.py              <- Execution and output capture runner
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py                   <- NASA POWER API ingestion & data cleaning
│   └── trend_analysis.py                <- OLS, Mann-Kendall, Sen's Slope & reporting
│
├── requirements.txt                     <- Pinned scientific dependencies
└── README.md                            <- Scientific documentation & methodology
```

---

## 🔬 Phase 1 Scientific Findings (Dhaka, Bangladesh: 2001–2025)

### 1. Annual Mean Analysis (25-Year Aggregate)

| Metric | Parametric (OLS) | Non-Parametric (Mann-Kendall / Sen's) |
| :--- | :--- | :--- |
| **Trend Direction** | Increasing | Increasing |
| **Slope** | `+0.0026 °C / year` (`+0.026 °C / decade`) | `+0.0036 °C / year` (`+0.036 °C / decade`) |
| **Total Cumulative Change** | `+0.06 °C` | `+0.09 °C` |
| **Percentage Change** | `+0.24 %` | `+0.35 %` |
| **Model Fit ($R^2$)** | `0.0042` | — |
| **Test Statistic** | $t = 0.313$ | $S = +30, Z = +0.40$ |
| **p-value** | **`p = 0.7571`** | **`p = 0.6913`** |
| **Statistical Significance ($\alpha=0.05$)** | **NO (Statistical Illusion / Noise)** | **NO (Statistical Illusion / Noise)** |

> **Detective Insight #1:** If an analyst only looked at the annual mean, they would conclude there is no significant warming in Dhaka over the last 25 years. But this is where true Earth System Detectives investigate deeper!

---

### 2. The Detective's Breakthrough: Seasonal Deconstruction

When the daily time series is decomposed into monthly climate segments, the annual masking effect disappears, revealing **severe, statistically significant late-monsoon and post-monsoon warming**:

| Month | Decadal Rate (°C/decade) | 25-Year Total Change (°C) | p-value | Statistically Significant? |
| :--- | :---: | :---: | :---: | :---: |
| **January** | $+0.098$ | $+0.24$ | $0.7437$ | No |
| **February** | $-0.305$ | $-0.76$ | $0.3589$ | No |
| **March** | $-0.235$ | $-0.59$ | $0.3695$ | No |
| **April** | $-0.155$ | $-0.39$ | $0.6339$ | No |
| **May** | $-0.353$ | $-0.88$ | $0.1274$ | No |
| **June** | $-0.024$ | $-0.06$ | $0.8602$ | No |
| **July** | **$+0.167$** | **$+0.42$** | **$0.0207$** | **YES ✅ ($p < 0.05$)** |
| **August** | $+0.075$ | $+0.19$ | $0.3305$ | No |
| **September** | **$+0.361$** | **$+0.90$** | **$< 0.0001$** | **YES ✅ ($p < 0.001$)** |
| **October** | **$+0.452$** | **$+1.13$** | **$0.0062$** | **YES ✅ ($p < 0.01$)** |
| **November** | $+0.195$ | $+0.49$ | $0.3347$ | No |
| **December** | $+0.016$ | $+0.04$ | $0.9504$ | No |

### 🎯 Climatological Conclusion:
1. **The Annual Buffer:** Mild cooling in early months (Feb–May) mathematically cancelled out sharp warming in late months, producing an deceptively flat annual average ($p = 0.757$).
2. **The Real Crisis:** Post-monsoon months (September & October) have warmed by **$+0.90^\circ\text{C}$ to $+1.13^\circ\text{C}$** with extreme statistical significance ($p < 0.01$), indicating extended summer/monsoon heat duration and delayed winter onset over central Bangladesh.

---

## 🚀 How to Run the Pipeline

### 1. Environment Setup
```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1   # (Windows)
# or source .venv/bin/activate  # (Linux/macOS)

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Notebook
Launch Jupyter to explore `01_nasa_temperature_analysis.ipynb`:
```bash
jupyter notebook notebooks/01_nasa_temperature_analysis.ipynb
```

---

## 🗺️ Roadmap: Phase 2 (Regional Grid Analysis)
In Phase 2, we will expand this verified single-point engine to a spatial grid covering all 8 administrative divisions of Bangladesh ($20.5^\circ\text{N} - 26.5^\circ\text{N}, 88.0^\circ\text{E} - 92.8^\circ\text{E}$) to map:
- Spatial distribution of warming rates
- Division-by-division statistical significance heatmaps
- Divergent regional trends (Coastal Bay of Bengal vs. Northern Himalayan Foothills)
