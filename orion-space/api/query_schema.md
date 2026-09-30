# Orion Space Query Engine — Step 9 Query Schema & Contract Specification

**Project:** Orion Space — NASA Earth System Trend Detective (NASA Space Apps Challenge 2026)  
**Document:** Step 9 Query Engine Architecture & Contract Specification  
**Status:** PRODUCTION SPECIFICATION  
**Core Rule:** **Ground Truth First** — Zero LLM statistical hallucination. The LLM never reads raw CSV files directly, never calculates metrics, and never performs statistical tests.

---

## 1. Ground Truth First Architecture

```
                       NATURAL LANGUAGE QUERY FLOW
                       
                    User Natural Language Question
         "Which areas in Bangladesh had significant warming in September?"
                                  │
                                  ▼
                    ┌────────────────────────────┐
                    │     1. QUERY PARSER        │
                    │   (Rule-based + Intent)    │
                    └─────────────┬──────────────┘
                                  │
                                  ▼
                    ┌────────────────────────────┐
                    │    2. STRUCTURED QUERY     │
                    │   (Deterministic Schema)   │
                    └─────────────┬──────────────┘
                                  │
                                  ▼
                    ┌────────────────────────────┐
                    │ 3. DETERMINISTIC RETRIEVER │
                    │   (Pandas / SQL on FDR)    │
                    └─────────────┬──────────────┘
                                  │
               ┌──────────────────┴──────────────────┐
               ▼                                     ▼
 ┌───────────────────────────┐         ┌───────────────────────────┐
 │   4A. EVIDENCE PAYLOAD    │         │ 4B. VISUALIZATION PAYLOAD │
 │   (Pure Verified Stats)   │         │ (GeoJSON / Plotly Spec)   │
 └─────────────┬─────────────┘         └─────────────┬─────────────┘
               │                                     │
               ▼                                     │
 ┌───────────────────────────┐                       │
 │  5. GROUNDED LLM EXPLAIN  │                       │
 │ (Strict synthesis of 4A)  │                       │
 └─────────────┬─────────────┘                       │
               │                                     │
               └──────────────────┬──────────────────┘
                                  ▼
                      UNIFIED API JSON RESPONSE
                                  │
                                  ▼
                   Next.js Interactive Dashboard UI
```

---

## 2. Supported Query Intents

| Intent ID | Description | Example Natural Query | Required Scientific Inputs |
| :--- | :--- | :--- | :--- |
| `trend` | Spatial distribution of 25-yr trends for 1 variable in a given month. | *"Which areas had significant warming in September?"* | `variable`, `month`, optional `direction`, `test_type` |
| `relationship` | Spatial correlation / coupling between 2 variables in a given month. | *"Is temperature correlated with soil wetness in May?"* | `variable_a`, `variable_b`, `month`, `test_type` |
| `location_profile` | Full Earth-system profile (all 4 variables + coupling) for a single coordinate / division. | *"Show climate trends for Sylhet (or 24.5°N, 91.875°E)."* | `location` (division name or `lat, lon`) |
| `seasonal_cycle` | 12-month annual cycle of trends across Bangladesh or a specific region. | *"How does temperature trend vary across months?"* | `variable`, optional `location` |
| `comparative_extremes` | Identify which month or region experienced the maximum change. | *"Which month has the strongest nationwide warming rate?"* | `variable`, optional `metric` (`max_rate`, `most_significant`) |

---

## 3. Structured Query Schema (Parser Output Contract)

When the **Query Parser** analyzes user input, it produces a validated, deterministic JSON object adhering to this schema:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "OrionStructuredQuery",
  "type": "object",
  "properties": {
    "intent": {
      "type": "string",
      "enum": ["trend", "relationship", "location_profile", "seasonal_cycle", "comparative_extremes"],
      "description": "Primary analytical intent identified from user prompt."
    },
    "variable": {
      "type": "string",
      "enum": ["T2M", "PRECTOTCORR", "GWETTOP", "ALLSKY_SFC_SW_DWN"],
      "description": "Primary NASA Earth-system variable."
    },
    "secondary_variable": {
      "type": ["string", "null"],
      "enum": ["T2M", "PRECTOTCORR", "GWETTOP", "ALLSKY_SFC_SW_DWN", null],
      "default": null,
      "description": "Secondary variable for cross-variable relationship queries."
    },
    "month": {
      "type": ["integer", "null"],
      "minimum": 1,
      "maximum": 12,
      "description": "Calendar month (1 = Jan, ..., 12 = Dec). Null if analyzing entire seasonal cycle."
    },
    "location": {
      "type": "object",
      "properties": {
        "scope": {
          "type": "string",
          "enum": ["national", "division", "coordinate"],
          "default": "national"
        },
        "division_name": {
          "type": ["string", "null"],
          "enum": ["Dhaka", "Chattogram", "Sylhet", "Rajshahi", "Khulna", "Barishal", "Rangpur", "Mymensingh", null],
          "default": null
        },
        "latitude": {
          "type": ["number", "null"],
          "minimum": 20.5,
          "maximum": 26.5,
          "default": null
        },
        "longitude": {
          "type": ["number", "null"],
          "minimum": 88.0,
          "maximum": 92.8,
          "default": null
        }
      },
      "required": ["scope"]
    },
    "direction": {
      "type": "string",
      "enum": ["increasing", "decreasing", "all"],
      "default": "all",
      "description": "Filter by trend direction."
    },
    "significance_filter": {
      "type": "string",
      "enum": ["fdr", "raw", "all"],
      "default": "fdr",
      "description": "Statistical significance filter. Defaults strictly to BH-corrected FDR."
    },
    "test_type": {
      "type": "string",
      "enum": ["OLS", "Mann-Kendall", "Pearson", "Spearman", "both"],
      "default": "OLS",
      "description": "Statistical test to evaluate for trends or relationships."
    },
    "alpha": {
      "type": "number",
      "minimum": 0.001,
      "maximum": 0.1,
      "default": 0.05,
      "description": "Significance threshold (alpha or q-threshold)."
    }
  },
  "required": ["intent", "variable", "significance_filter", "test_type", "alpha"]
}
```

### Example Structured Query (September T2M Warming)
```json
{
  "intent": "trend",
  "variable": "T2M",
  "secondary_variable": null,
  "month": 9,
  "location": {
    "scope": "national",
    "division_name": null,
    "latitude": null,
    "longitude": null
  },
  "direction": "increasing",
  "significance_filter": "fdr",
  "test_type": "OLS",
  "alpha": 0.05
}
```

---

## 4. Deterministic Scientific Retriever Operations

The **Scientific Data Retriever** executes purely deterministic relational lookups on the FDR datasets:
- **Trends:** [`data/bangladesh_multivariable_trends_fdr.csv`](file:///c:/Users/mah54/Desktop/Nasa_Space_APP_Challenge/data/bangladesh_multivariable_trends_fdr.csv)
- **Relationships:** [`data/bangladesh_variable_relationships_fdr.csv`](file:///c:/Users/mah54/Desktop/Nasa_Space_APP_Challenge/data/bangladesh_variable_relationships_fdr.csv)

### Filtering Logic
1. Filter by `variable == query.variable` and `month_num == query.month` (extracts the exact family of 34 spatial tests).
2. If `location.scope == "division"`: filter cells where nearest division matches `query.location.division_name`.
3. If `location.scope == "coordinate"`: find nearest grid cell using Euclidean or Haversine distance.
4. If `direction == "increasing"`: filter `slope_per_decade > 0`.
5. If `direction == "decreasing"`: filter `slope_per_decade < 0`.
6. If `significance_filter == "fdr"`:
   - For `test_type == "OLS"`: filter `is_significant_ols_fdr == True` (i.e. `q_value_ols < alpha`).
   - For `test_type == "Mann-Kendall"`: filter `is_significant_mk_fdr == True` (i.e. `q_value_mk < alpha`).
   - For `test_type == "both"`: filter `is_significant_ols_fdr == True` and `is_significant_mk_fdr == True`.

### Scientific Formatting Rules
1. **Finite Precision underflow:** If $p < 1\times 10^{-6}$ or stored as `0.0`, the scientific evidence formats the string representation as `"p < 1e-6"` or `"q < 1e-6"`, preventing mathematical misinterpretation of exact zero probability.
2. **Standard Claim Phrasing:** The retriever generates verified claim fragments:
   - *"33 of 34 cells remained significant after Benjamini–Hochberg FDR correction at q < 0.05."*
   - Never use "false positives screened"; use *"Raw discoveries removed after FDR: X"*.
3. **Caveat Inclusion:** Always includes standard spatial dependence caveat:
   - *"FDR correction was performed within each variable-month spatial testing family (m=34); interpretation accounts for possible spatial dependence among neighboring grid cells."*

---

## 5. Scientific Evidence Payload (Retriever Output Contract)

This structured evidence is produced deterministically and served to both the frontend and the LLM explanation generator:

```json
{
  "evidence_id": "ev_trend_T2M_m09_fdr_ols",
  "query_metadata": {
    "variable": "T2M",
    "variable_name": "Air Temperature at 2 Meters",
    "unit": "°C",
    "rate_unit": "°C/decade",
    "month_num": 9,
    "month_name": "September",
    "season": "Post-Monsoon",
    "time_period": "2001 - 2025 (25 Years)"
  },
  "family_scope": {
    "family_definition": "variable_by_month_spatial",
    "family_size_m": 34,
    "correction_method": "Benjamini-Hochberg (1995) FDR",
    "alpha": 0.05
  },
  "summary_statistics": {
    "total_cells_evaluated": 34,
    "warming_cells_count": 34,
    "cooling_cells_count": 0,
    "raw_significant_ols_count": 33,
    "fdr_significant_ols_count": 33,
    "raw_significant_mk_count": 34,
    "fdr_significant_mk_count": 33,
    "raw_discoveries_removed_after_fdr": 0,
    "national_mean_slope": 0.3452,
    "min_slope": 0.2017,
    "max_slope": 0.4211,
    "min_slope_location": {"lat": 22.0, "lon": 89.375, "division": "Khulna"},
    "max_slope_location": {"lat": 24.5, "lon": 91.875, "division": "Sylhet"},
    "formatted_significance_claim": "33 of 34 cells remained significant after Benjamini-Hochberg FDR correction at q < 0.05."
  },
  "cells": [
    {
      "cell_index": 1,
      "latitude": 24.5,
      "longitude": 91.875,
      "nearest_division": "Sylhet",
      "slope_per_decade": 0.4211,
      "p_value_ols_formatted": "p < 1e-6",
      "q_value_ols": 0.000008,
      "p_value_mk_formatted": "0.000021",
      "q_value_mk": 0.000045,
      "is_significant_ols_fdr": true,
      "is_significant_mk_fdr": true,
      "trend_direction": "Increasing"
    }
  ],
  "methodological_caveats": [
    "FDR correction was performed within each variable-month spatial testing family, rather than across all spatial-month-variable hypotheses globally.",
    "BH-FDR was applied to each spatial family; interpretation accounts for possible spatial dependence among neighboring grid cells."
  ]
}
```

---

## 6. Visualization Payload Contract

Designed for instant rendering in Mapbox GL / Leaflet (GeoJSON) and Plotly (interactive charts):

```json
{
  "visualization_type": "spatial_map_and_distribution",
  "spatial_layer": {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "geometry": {
          "type": "Point",
          "coordinates": [91.875, 24.5]
        },
        "properties": {
          "value": 0.4211,
          "is_significant": true,
          "q_value": 0.000008,
          "direction": "Increasing",
          "division": "Sylhet",
          "popup_html": "<b>Sylhet Grid Cell</b><br>Rate: +0.42 °C/decade<br>q-value: &lt; 0.0001 (Significant)"
        }
      }
    ]
  },
  "color_scale": {
    "palette": "RdBu_r",
    "domain": [-0.5, 0.5],
    "unit": "°C/decade"
  }
}
```

---

## 7. LLM Grounding Guardrails & Prompt Contract

The LLM is invoked **only after** the Scientific Evidence JSON has been computed. It receives a strict system prompt forbidding numerical calculation:

### System Prompt Guardrail:
```text
You are Orion Space, an expert Earth-system scientific explainer for NASA Space Apps Challenge 2026.
You are given a deterministic Scientific Evidence JSON verified against NASA MERRA-2 and POWER datasets.

RULES:
1. NEVER recalculate, guess, or modify any number, mean, percentage, or cell count.
2. Quote exact numbers from the evidence payload only.
3. Explicitly distinguish between raw p-values and Benjamini-Hochberg FDR q-values.
4. When reporting significance, use the verified phrasing:
   "X of 34 cells remained significant after Benjamini-Hochberg FDR correction at q < 0.05."
5. If reporting p-values below 1e-6 or stored as 0.0, format them as "p < 1e-6" rather than exact zero.
6. For cross-variable correlations, strictly avoid asserting causal mechanisms; describe observed statistical co-occurrences.
7. Always include the required spatial dependence caveats.
```

---

## 8. Summary of Steps for Step 9 Implementation

1. **Parser Implementation:** `orion-space/src/query_parser.py` (Rule-based regex + intent extractor producing `OrionStructuredQuery`).
2. **Retriever Implementation:** `orion-space/src/query_retriever.py` (Deterministic queries on `bangladesh_multivariable_trends_fdr.csv` & `bangladesh_variable_relationships_fdr.csv`).
3. **Payload Builder:** Generating `Scientific Evidence JSON` and `GeoJSON Visualization Payload`.
4. **LLM Explainer Service:** Integrating Gemini 2.5 Flash via `google-genai` SDK with strict grounding guardrails.
5. **FastAPI Route Binding:** Wire `POST /api/v1/analyze` to connect Parser $\rightarrow$ Retriever $\rightarrow$ Visualizer $\rightarrow$ LLM.
