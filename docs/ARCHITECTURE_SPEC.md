# 🛰️ NASA Earth Intelligence Agent (NEIA)
## System Design & Technical Specification (V1.0)
**Project Title:** NASA Earth Intelligence Agent  
**Hackathon:** NASA International Space Apps Challenge 2026  
**Target Domain:** Earth Environmental Change Intelligence & Autonomous Scientific Reasoning  
**Flagship Demo Benchmark:** Coastal Bangladesh Mangrove & Salinity Stress Detection (2020–2025)

---

## 1. Product Specification

### 1.1 Problem Statement
Earth observation satellites generate petabytes of data daily (NASA EOSDIS, Earthdata, GIBS, Landsat, MODIS, Sentinel). However:
- **High Technical Barrier:** Policy makers, climate scientists, journalists, and local communities cannot readily extract actionable insights without mastering complex GIS software, NetCDF/HDF formats, and scientific python libraries.
- **LLM Hallucination Hazard:** General-purpose AI chatbots (e.g. ChatGPT, Gemini without grounding) frequently hallucinate numerical trends, guess temperature anomalies, or fabricate scientific citations when queried about climate change.
- **Lack of Reproducibility:** Conventional climate dashboards present static pre-rendered charts rather than providing transparent, reproducible scientific code that underpins the conclusions.

### 1.2 The NEIA Solution
**NASA Earth Intelligence Agent (NEIA)** is an autonomous scientific research system that takes high-level natural language questions about Earth and dynamically translates them into reproducible scientific workflows:
$$\text{Natural Language Inquiry} \xrightarrow{\text{AI Agent Planner}} \text{NASA Discovery} \xrightarrow{\text{Data Retrieval}} \text{Deterministic Math/ML Engine} \xrightarrow{\text{Evidence Dossier}} \text{Interactive Visualization + Citations}$$

### 1.3 Key Guarantees
1. **Zero Numerical Hallucination:** The Large Language Model (LLM) is strictly an *orchestrator and scientific communicator*. All metrics ($\Delta \text{NDVI}$, standard deviations, $p$-values, hectares lost/gained) are computed by deterministic Python routines.
2. **Provenance & Auditability:** Every statement is backed by an authoritative NASA Earthdata DOI, sensor ID (MODIS Terra/Aqua, VIIRS SNPP/NOAA-20), platform, and temporal window.
3. **Reproducibility Recipe:** Every agent execution generates a JSON recipe and an executable Python script enabling any independent researcher to recreate the analysis bit-for-bit.

### 1.4 Foundational Principle: Scientific Engine First, AI Agent Second
A foundational rule of this architecture is:
$$\text{If the underlying analysis tool is mathematically flawed, no LLM—regardless of intelligence—can produce a correct result.}$$

Therefore, development and validation strictly follow a two-tier hierarchy:
```
STAGE 1: Deterministic Scientific Engine (Pure Python / Standalone)
   NASA Data -> Python -> Read Data -> Analyze Data -> Result

STAGE 2: Autonomous Agent Abstraction Layer
   Python Analysis -> Tool Interface -> LLM Orchestration
```
The scientific engine is completely decoupled from the LLM, enabling independent unit testing, CLI execution (`standalone_science_pipeline.py`), and peer-reviewed verification.

---

## 2. Exact V1 Scope & Boundaries

### 2.1 Domain Focus: Earth Environmental Change Intelligence
To achieve world-class hackathon execution, V1 deliberately avoids attempting "all Earth science problems" and instead masters **Vegetation & Land Cover Dynamics Under Climate Stress**.

### 2.2 Flagship Benchmark Case Study
- **Geographic Area:** Coastal Bangladesh (Sundarbans Biosphere Reserve, Khulna, Satkhira, Bagerhat, Bhola, Cox's Bazar).
  - Bounding Box: `[88.8°E, 21.5°N, 92.4°E, 23.0°N]`
- **Temporal Window:** 2020 to 2025 (Annual & Seasonal Climatology).
- **Core Scientific Phenomemon:**
  - Cyclonic damage (e.g. Cyclone Amphan 2020, Cyclone Remal 2024).
  - Salinity intrusion causing mangrove canopy thinning.
  - Mangrove regeneration vs. shrimp farming aquaculture conversion.
- **Reference Natural Language Prompt:**
  > *"Analyze vegetation changes in coastal Bangladesh between 2020 and 2025 and detect significant environmental anomalies."*

---

## 3. NASA Datasets Selection & Integration Strategy

| NASA Dataset | Short Name | Resolution | Cadence | Source API | Usage in NEIA |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **MODIS/Terra Vegetation Indices** | `MOD13Q1` | 250m | 16-day | NASA CMR / LP DAAC | Longitudinal NDVI & EVI time-series (2000–Present) |
| **VIIRS/S-NPP Surface Reflectance & Veg** | `VNP13A1` | 500m | 16-day | NASA CMR | Cross-sensor validation & recent high-resolution continuity |
| **NASA GIBS True Color (Terra/MODIS)** | `MODIS_Terra_CorrectedReflectance_TrueColor` | 250m | Daily | GIBS WMTS Tile API | Base satellite imagery visual context |
| **NASA GIBS NDVI 16-Day (Terra/MODIS)** | `MODIS_Terra_NDVI_16Day` | 250m | 16-day | GIBS WMTS Tile API | Pre/post change overlay maps |
| **NASA FIRMS Active Fire Data** | `FIRMS_VIIRS` | 375m | Real-time | FIRMS REST API | Correlation check for agricultural burn / fire anomalies |

---

## 4. Agent Architecture: Autonomous Scientific Planner

```
                          ┌───────────────────────────┐
                          │   Natural Language User   │
                          │   Query / Inquiry Console │
                          └─────────────┬─────────────┘
                                        │
                                        ▼
                          ┌───────────────────────────┐
                          │  Agent Intent Decomposer  │
                          │  • Target Region / Bounding Box
                          │  • Temporal Baseline & Range
                          │  • Phenomenon (NDVI, LST) │
                          └─────────────┬─────────────┘
                                        │
                                        ▼
             ╔═════════════════════════════════════════════════════╗
             ║            NEIA Tool Execution Pipeline             ║
             ╠═════════════════════════════════════════════════════╣
             ║ 1. search_datasets(query, topic, bbox)              ║
             ║    ↳ NASA CMR collection match                      ║
             ║ 2. get_dataset_metadata(dataset_id)                 ║
             ║    ↳ Sensor resolution, QA flags, DOI validation    ║
             ║ 3. retrieve_earth_data(dataset_id, bbox, timerange) ║
             ║    ↳ Ingest satellite time-series & spatial grid    ║
             ║ 4. execute_scientific_analysis(data, method)        ║
             ║    ↳ NumPy/SciPy Trend (Theil-Sen / Mann-Kendall)   ║
             ║ 5. detect_spatial_anomalies(baseline, target)       ║
             ║    ↳ Z-score raster & pixel degradation masks       ║
             ║ 6. verify_scientific_guardrails(results)            ║
             ║    ↳ Confidence interval & sanity check             ║
             ║ 7. build_evidence_dossier(run_id)                   ║
             ║    ↳ NASA DOIs, provenance hash, code recipe        ║
             ╚═════════════════════════════════════════════════════╝
                                        │
                                        ▼
                          ┌───────────────────────────┐
                          │  Synthesized Response &   │
                          │  Multi-Layer Visual UI    │
                          └───────────────────────────┘
```

---

## 5. Tool Definitions & Scientific Contracts

### Tool 1: `search_datasets`
- **Input:** `query: str`, `category: str`, `bbox: list[float]`, `temporal_range: tuple[str, str]`
- **Action:** Queries NASA CMR (Common Metadata Repository) REST API `https://cmr.earthdata.nasa.gov/search/collections.json`.
- **Output:** Ranked list of NASA dataset records (ShortName, Title, DOI, Version, SpatialExtents, TemporalCoverage).

### Tool 2: `get_dataset_metadata`
- **Input:** `concept_id: str` or `short_name: str`
- **Action:** Fetches landing page metadata, sensor specifications, and data quality flags.
- **Output:** Structured dictionary containing spatial resolution, unit of measurement, valid ranges, and citation info.

### Tool 3: `retrieve_earth_data`
- **Input:** `dataset_id: str`, `bbox: list[float]`, `start_date: str`, `end_date: str`
- **Action:** Extracts spatial raster slices and aggregated time-series vectors. Supports both live NASA Earthdata API querying and high-speed local geospatial raster caching for reliable live hackathon demonstrations.
- **Output:** Multidimensional data structure containing dates, mean values, spatial matrices, and cloud cover quality masks.

### Tool 4: `analyze_timeseries`
- **Input:** `timeseries: list[dict]`, `metric: str`
- **Action:** Runs statistical trend estimation:
  - Linear regression ($y = \beta x + \alpha$)
  - Sen's slope and Mann-Kendall monotonic trend test ($p$-value, tau)
  - Seasonal climatological anomaly decomposition ($Z = \frac{X - \mu}{\sigma}$)
- **Output:** `slope`, `percentage_change`, `p_value`, `trend_significance: bool`, `confidence_interval_95`.

### Tool 5: `detect_change`
- **Input:** `baseline_matrix: ndarray`, `target_matrix: ndarray`, `threshold: float`
- **Action:** Computes spatial difference map $\Delta \text{NDVI} = \text{Target} - \text{Baseline}$. Categorizes pixels into:
  - Severe Degradation ($\Delta \text{NDVI} < -0.20$)
  - Moderate Degradation ($-0.20 \le \Delta \text{NDVI} < -0.08$)
  - Stable ($-0.08 \le \Delta \text{NDVI} \le +0.08$)
  - Significant Greening / Recovery ($\Delta \text{NDVI} > +0.08$)
- **Output:** Area statistics (hectares, percentage by class), bounding centroids of hotspots, and GeoJSON polygon vectors for map overlay.

### Tool 6: `generate_evidence_dossier`
- **Input:** `execution_state: dict`
- **Action:** Assembles cryptographic provenance hash (SHA-256), exact NASA dataset DOIs, attribution guidelines, and a standalone executable Python script (`recipe.py`).

---

## 6. Mathematical & Scientific Methodology

### 6.1 Normalized Difference Vegetation Index (NDVI)
$$\text{NDVI} = \frac{\text{NIR} - \text{Red}}{\text{NIR} + \text{Red}}$$
Where $\text{NIR}$ is MODIS Band 2 ($841–876\,\text{nm}$) and $\text{Red}$ is MODIS Band 1 ($620–670\,\text{nm}$).
Values range from $-1.0$ (water) to $+1.0$ (dense healthy vegetation canopy).

### 6.2 Climatological Anomaly (Z-Score)
To distinguish temporary seasonal fluctuations from true environmental distress:
$$Z_t = \frac{\text{NDVI}_t - \mu_{\text{clim}}}{\sigma_{\text{clim}}}$$
Where $\mu_{\text{clim}}$ and $\sigma_{\text{clim}}$ represent the 20-year historical baseline mean and standard deviation for the same calendar month. $|Z| > 2.0$ represents a statistically significant environmental anomaly ($p < 0.05$).

### 6.3 Mann-Kendall Trend Test
Non-parametric test for monotonic trends:
$$S = \sum_{k=1}^{n-1}\sum_{j=k+1}^{n}\operatorname{sgn}(x_j - x_k)$$
$$\operatorname{Var}(S) = \frac{n(n-1)(2n+5)}{18}$$
$$Z_{MK} = \begin{cases} \frac{S-1}{\sqrt{\operatorname{Var}(S)}} & \text{if } S > 0 \\ 0 & \text{if } S = 0 \\ \frac{S+1}{\sqrt{\operatorname{Var}(S)}} & \text{if } S < 0 \end{cases}$$

---

## 7. Reliability & Scientific Guardrails Layer

Before presenting conclusions to the user, NEIA runs a 5-point verification matrix:
1. **Temporal Completeness:** Verifies that no more than 10% of observation epochs are obscured by monsoon cloud contamination.
2. **Dynamic Range Sanity:** Confirms that all NDVI indices fall strictly within $[ -1.0, +1.0 ]$.
3. **Statistical Significance Check:** If the calculated trend has $p \ge 0.05$, the agent explicitly flags the trend as *statistically inconclusive* rather than making unwarranted assertions.
4. **Attribution Integrity:** Rejects generic responses; every claim must cite the specific dataset DOI and satellite sensor.
5. **No Hallucinated Numbers:** Compares LLM natural-language output against the scientific engine's JSON output; blocks any generation where numerical values differ by $> 0.1\%$.

---

## 8. Technology Stack

### 8.1 Backend
- **Core Runtime:** Python 3.14 / 3.11+
- **Framework:** FastAPI with asynchronous streaming (Server-Sent Events)
- **Scientific Computing:** NumPy, Pandas, SciPy, Scikit-learn
- **Geospatial Processing:** GeoPandas, Shapely
- **NASA Interfaces:** NASA CMR REST API, NASA GIBS WMTS/WMS tile endpoints
- **AI Agent Engine:** Python-based Structured Planning Loop with Tool Calling

### 8.2 Frontend
- **Framework:** React 19 + Vite
- **Styling:** Custom Vanilla CSS & Modern Space Glassmorphism Design System (Obsidian `#080b11`, Orbital Cyan `#00f0ff`, Emerald `#00ff9d`, Warning Crimson `#ff3366`)
- **Mapping:** Leaflet.js with NASA GIBS real-time satellite tile layers and GeoJSON polygon overlays
- **Charts:** Canvas / SVG High-Performance Time-Series charts with confidence interval envelopes
- **Streaming:** EventSource SSE client for real-time agent thought streaming

---

## 9. NASA Space Apps Challenge 2026 Evaluation Alignment

| Judging Criteria | How NEIA Scores Maximum Points |
| :--- | :--- |
| **Impact** | Solves high-priority climate resilience problem for 170M+ people in Bengal Delta; provides actionable intelligence for mangrove conservation and salinity mitigation. |
| **Creativity / Novelty** | Shifts the paradigm from passive chatbots to an active Scientific Research Agent that refuses to hallucinate and outputs auditable proof. |
| **Validity / Science** | Uses peer-reviewed scientific methodologies (Mann-Kendall, Sen's Slope, Z-Score Climatology) backed directly by NASA EOSDIS/MODIS datasets. |
| **Relevance** | Direct utilization of NASA Open Data APIs (CMR, GIBS, Earthdata). |
| **Presentation** | Mission Control dashboard aesthetic with real-time thought transparency, interactive geospatial maps, and one-click code reproducibility. |
