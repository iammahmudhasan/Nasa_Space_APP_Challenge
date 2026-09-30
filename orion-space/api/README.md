# Orion Space Intelligence Interface — API Contract & Architecture Specification

**Project:** Orion Space — NASA Earth System Trend Detective  
**Target:** Step 7 Architecture Contract  
**Protocol:** RESTful JSON over HTTP  
**Runtime:** Python FastAPI (Backend) + Next.js / React (Frontend) + Local Scientific Datasets  

---

## 1. System Architecture & "Ground Truth First" Philosophy

To eliminate AI hallucinations and ensure 100% reproducible scientific rigor, Orion Space employs a **Ground Truth First** query-engine architecture. 

The Large Language Model (LLM) **never calculates or guesses raw climate metrics**. Instead, a deterministic query engine retrieves exact, pre-computed statistics from the NASA MERRA-2 / POWER scientific pipeline, passes a structured JSON contract to the LLM, and the LLM synthesizes natural-language explanations strictly bound to the verified numbers.

```
                           ORION SPACE SYSTEM ARCHITECTURE
                           
 [ User Question ]
        │  "Which parts of Bangladesh experienced significant temperature increases in September?"
        ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ 1. Intent & Entity Extraction Layer (FastAPI Parser)        │
 │    - Identifies: Variable (T2M), Month (Sep), Location (All)│
 └──────────────────────────────┬──────────────────────────────┘
                                │ Structured Parameters
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ 2. Deterministic Scientific Ground Truth Engine             │
 │    - Queries: bangladesh_multivariable_trends.csv           │
 │    - Queries: bangladesh_variable_relationships.csv         │
 │    - Computes: Summary statistics, significance counts,     │
 │                OLS & Mann-Kendall test verifications        │
 └──────────────┬───────────────────────────────┬──────────────┘
                │ Verified JSON                 │ GeoJSON / Plotly Config
                ▼                               ▼
 ┌──────────────────────────────┐ ┌────────────────────────────┐
 │ 3. LLM Grounded Explanation  │ │ 4. Interactive Visualizer  │
 │    (Zero Hallucination)      │ │    (Leaflet / Plotly Spec) │
 └──────────────┬───────────────┘ └─────────────┬──────────────┘
                │                               │
                └───────────────┬───────────────┘
                                ▼
              [ Unified RESTful JSON Response ]
                                │
                                ▼
              [ Next.js Interactive Dashboard UI ]
```

---

## 2. API Endpoints Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/variables` | Returns catalog of 4 Earth-system parameters, units, and NASA provenance. |
| `GET` | `/api/v1/months` | Returns 12 calendar months with climatological seasonal groupings. |
| `GET` | `/api/v1/locations` | Returns 34 retained Bangladesh mainland grid cells with divisional metadata. |
| `POST` | `/api/v1/analyze` | **Primary Intelligence Endpoint:** Natural language question $\rightarrow$ parsed query $\rightarrow$ scientific retrieval $\rightarrow$ visual spec $\rightarrow$ grounded explanation. |
| `GET` | `/api/v1/trends/spatial` | Direct query of spatial trends filtered by variable and month. |
| `GET` | `/api/v1/relationships` | Direct query of pairwise cross-variable correlations (Pearson/Spearman). |

---

## 3. Detailed Endpoint Contracts

### 3.1. `GET /api/v1/variables`
Returns the metadata and catalog of all monitored Earth-system variables.

#### Response (`200 OK`):
```json
{
  "status": "success",
  "count": 4,
  "data": [
    {
      "id": "T2M",
      "name": "Air Temperature at 2 Meters",
      "category": "Thermal",
      "unit": "°C",
      "rate_unit": "°C/decade",
      "source": "NASA GMAO MERRA-2",
      "resolution": "0.5° x 0.625°",
      "description": "Surface air temperature at 2 meters altitude."
    },
    {
      "id": "PRECTOTCORR",
      "name": "Corrected Precipitation",
      "category": "Hydro-climate",
      "unit": "mm/day",
      "rate_unit": "mm/day/decade",
      "source": "NASA GMAO MERRA-2",
      "resolution": "0.5° x 0.625°",
      "description": "Bias-corrected total precipitation rate."
    },
    {
      "id": "GWETTOP",
      "name": "Top-layer Soil Wetness",
      "category": "Land Hydrology",
      "unit": "0-1 fraction",
      "rate_unit": "fraction/decade",
      "source": "NASA GMAO MERRA-2 Land Model",
      "resolution": "0.5° x 0.625°",
      "description": "Surface 0-5 cm soil moisture saturation index."
    },
    {
      "id": "ALLSKY_SFC_SW_DWN",
      "name": "All-Sky Surface Solar Irradiance",
      "category": "Radiative Energy",
      "unit": "MJ/m²/day",
      "rate_unit": "MJ/m²/day/decade",
      "source": "NASA CERES / FLASHFlux",
      "resolution": "1.0° x 1.0° (Nearest-neighbor mapped to 34 mainland points)",
      "description": "Total downwelling solar radiation reaching Earth's surface."
    }
  ]
}
```

---

### 3.2. `GET /api/v1/months`
Returns calendar months and Bangladesh climatological seasonal clusters.

#### Response (`200 OK`):
```json
{
  "status": "success",
  "count": 12,
  "seasons": {
    "Winter": [12, 1, 2],
    "Pre-Monsoon": [3, 4, 5],
    "Monsoon": [6, 7, 8],
    "Post-Monsoon": [9, 10, 11]
  },
  "data": [
    {"month_num": 1, "name": "January", "season": "Winter"},
    {"month_num": 2, "name": "February", "season": "Winter"},
    {"month_num": 3, "name": "March", "season": "Pre-Monsoon"},
    {"month_num": 4, "name": "April", "season": "Pre-Monsoon"},
    {"month_num": 5, "name": "May", "season": "Pre-Monsoon"},
    {"month_num": 6, "name": "June", "season": "Monsoon"},
    {"month_num": 7, "name": "July", "season": "Monsoon"},
    {"month_num": 8, "name": "August", "season": "Monsoon"},
    {"month_num": 9, "name": "September", "season": "Post-Monsoon"},
    {"month_num": 10, "name": "October", "season": "Post-Monsoon"},
    {"month_num": 11, "name": "November", "season": "Post-Monsoon"},
    {"month_num": 12, "name": "December", "season": "Winter"}
  ]
}
```

---

### 3.3. `GET /api/v1/locations`
Returns the 34 mainland Bangladesh grid coordinates with nearest administrative divisions.

#### Response (`200 OK`):
```json
{
  "status": "success",
  "count": 34,
  "boundary_source": "geoBoundaries-BGD-ADM0.geojson",
  "filtering_method": "Point-in-Polygon (PIP) intersection test",
  "data": [
    {
      "cell_id": "BGD_01",
      "latitude": 24.0,
      "longitude": 90.0,
      "nearest_division": "Dhaka",
      "distance_to_city_km": 42.5
    },
    {
      "cell_id": "BGD_02",
      "latitude": 22.5,
      "longitude": 91.875,
      "nearest_division": "Chattogram",
      "distance_to_city_km": 18.2
    }
  ]
}
```

---

### 3.4. `POST /api/v1/analyze` (Primary Intelligence Endpoint)

#### Request Schema:
```json
{
  "question": "Which areas of Bangladesh had significant temperature increases in September?",
  "override_filters": {
    "variable": "T2M",
    "month": "September",
    "alpha": 0.05
  }
}
```

#### Detailed Response Schema (`200 OK`):
```json
{
  "status": "success",
  "query_intent": {
    "raw_question": "Which areas of Bangladesh had significant temperature increases in September?",
    "resolved_variable": "T2M",
    "variable_name": "Air Temperature at 2 Meters",
    "unit": "°C/decade",
    "resolved_month": "September",
    "month_num": 9,
    "season": "Post-Monsoon",
    "query_type": "spatial_significance"
  },
  
  "scientific_metrics": {
    "temporal_period": "2001 - 2025 (25 Years)",
    "total_inland_cells": 34,
    "warming_cells_count": 34,
    "cooling_cells_count": 0,
    "significant_cells_ols_fdr": 33,
    "significant_cells_mk_fdr": 33,
    "raw_significant_cells_ols": 33,
    "percentage_significant_fdr": 97.1,
    "national_mean_rate": 0.3452,
    "min_rate": 0.2017,
    "max_rate": 0.4211,
    "dominant_direction": "Increasing"
  },

  "locations": [
    {
      "latitude": 24.5,
      "longitude": 91.875,
      "nearest_division": "Sylhet",
      "rate_per_decade": 0.4211,
      "p_value_ols": 0.000008,
      "p_value_ols_formatted": "p < 1e-5",
      "q_value_ols": 0.000008,
      "p_value_mk": 0.000021,
      "q_value_mk": 0.000045,
      "sen_slope_per_decade": 0.4180,
      "is_significant_ols_fdr": true,
      "is_significant_mk_fdr": true,
      "trend_direction": "Increasing"
    },
    {
      "latitude": 24.0,
      "longitude": 90.0,
      "nearest_division": "Dhaka",
      "rate_per_decade": 0.3402,
      "p_value_ols": 0.000048,
      "p_value_ols_formatted": "0.000048",
      "q_value_ols": 0.000054,
      "p_value_mk": 0.000321,
      "q_value_mk": 0.000412,
      "sen_slope_per_decade": 0.3563,
      "is_significant_ols_fdr": true,
      "is_significant_mk_fdr": true,
      "trend_direction": "Increasing"
    }
  ],

  "co_occurrence_context": {
    "secondary_variables": [
      {
        "variable": "PRECTOTCORR",
        "national_mean_rate": "+3.033 mm/day/decade",
        "significant_cells_fdr": 17,
        "coupling_r_with_primary": 0.22
      },
      {
        "variable": "GWETTOP",
        "national_mean_rate": "+0.0371 fraction/decade",
        "significant_cells_fdr": 34,
        "coupling_r_with_primary": 0.23
      },
      {
        "variable": "ALLSKY_SFC_SW_DWN",
        "national_mean_rate": "-0.153 MJ/m²/day/decade",
        "significant_cells_fdr": 0,
        "coupling_r_with_primary": 0.09
      }
    ]
  },

  "visualization": {
    "map_type": "spatial_choropleth_scatter",
    "center": [23.8103, 90.4125],
    "zoom": 7,
    "colormap": {
      "palette": "RdBu_r",
      "vmin": -0.5,
      "vcenter": 0.0,
      "vmax": 0.5,
      "label": "T2M Trend Rate (°C / decade)"
    },
    "geojson_overlay": "/api/v1/static/bangladesh_boundary.geojson",
    "chart_type": "plotly_json",
    "chart_spec": {
      "type": "scattergeo",
      "latitudes": [24.5, 24.0],
      "longitudes": [91.875, 90.0],
      "values": [0.4211, 0.3402],
      "markers": {"size": [16, 14], "symbol": "triangle-up"}
    }
  },

  "explanation": {
    "headline": "Nationwide Significant Post-Monsoon Warming in September (+0.35 °C/decade)",
    "key_findings": [
      "33 of 34 cells remained significant after Benjamini-Hochberg FDR correction at q < 0.05.",
      "Warming rates range from +0.20 °C/decade (southwest coast) to +0.42 °C/decade (northeast Sylhet).",
      "Non-parametric Mann-Kendall tests confirm this pattern with 33 of 34 cells showing significant positive trends at q < 0.05.",
      "Concurrently, top-layer soil moisture (GWETTOP) exhibited statistically significant increases in all 34 cells (+0.037/decade)."
    ],
    "scientific_caution": "These numbers represent empirical statistical trends from NASA GMAO MERRA-2 (2001–2025). FDR correction was performed within each variable-month spatial testing family; interpretation accounts for possible spatial dependence among neighboring grid cells. Correlation does not prove causation without full atmospheric boundary layer modeling."
  }
}
```

---

## 4. Frontend & Backend Type Declarations (TypeScript / Pydantic)

### 4.1. TypeScript Interface (Next.js Frontend Client)
> For complete Pydantic models, JSON schema, and deterministic retriever contract, see [query_schema.md](query_schema.md).

```typescript
export interface AnalysisRequest {
  question: string;
  override_filters?: {
    variable?: 'T2M' | 'PRECTOTCORR' | 'GWETTOP' | 'ALLSKY_SFC_SW_DWN';
    month?: string;
    alpha?: number;
  };
}

export interface LocationTrendRecord {
  latitude: number;
  longitude: number;
  nearest_division: string;
  rate_per_decade: number;
  p_value_ols: number;
  p_value_ols_formatted?: string;
  q_value_ols: number;
  p_value_mk: number;
  q_value_mk: number;
  sen_slope_per_decade: number;
  is_significant_ols_fdr: boolean;
  is_significant_mk_fdr: boolean;
  trend_direction: 'Increasing' | 'Decreasing' | 'No Trend';
}

export interface AnalysisResponse {
  status: 'success' | 'error';
  query_intent: {
    raw_question: string;
    resolved_variable: string;
    variable_name: string;
    unit: string;
    resolved_month: string;
    month_num: number;
    season: string;
    query_type: string;
  };
  scientific_metrics: {
    temporal_period: string;
    total_inland_cells: number;
    warming_cells_count: number;
    cooling_cells_count: number;
    significant_cells_ols: number;
    significant_cells_mk: number;
    percentage_significant_ols: number;
    national_mean_rate: number;
    min_rate: number;
    max_rate: number;
    dominant_direction: string;
  };
  locations: LocationTrendRecord[];
  visualization: {
    map_type: string;
    center: [number, number];
    zoom: number;
    colormap: {
      palette: string;
      vmin: number;
      vcenter: number;
      vmax: number;
      label: string;
    };
    chart_spec: Record<string, any>;
  };
  explanation: {
    headline: string;
    key_findings: string[];
    scientific_caution: string;
  };
}
```

---

## 5. Error Handling & HTTP Status Codes

| Code | Status | Cause | Example Response |
| :--- | :--- | :--- | :--- |
| `200` | OK | Successful query & synthesis. | Standard AnalysisResponse JSON. |
| `400` | Bad Request | Question is blank or incoherent. | `{"error": "Question cannot be empty"}` |
| `422` | Unprocessable Entity | Could not map query to any Earth-system parameter or month. | `{"error": "No matching Earth-system variable or temporal month detected in query. Please mention temperature, rain, soil, or solar radiation."}` |
| `500` | Internal Error | Missing scientific CSV cache or server error. | `{"error": "Scientific data pipeline cache unavailable."}` |

---

## 6. Anti-Hallucination LLM Prompting Standard

When generating the natural-language explanation, the backend will feed the retrieved deterministic JSON payload into the LLM with the following system prompt constraint:

```text
You are the Orion Space Earth-System Scientific Explainer.
You must adhere strictly to the following scientific rules:
1. ONLY quote numbers, rates, and p-values that are explicitly present in the verified JSON packet.
2. NEVER invent, extrapolate, or estimate numbers not in the input.
3. Distinguish between OLS and Mann-Kendall significance when reporting findings.
4. Report statistical co-occurrence and correlation without making unfounded causal claims.
5. If asked about a variable or month not in the dataset, state that empirical records are unavailable.
```
