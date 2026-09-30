"""
main.py
=======
FastAPI Application Backend for Orion Space Intelligence Interface.

Step 9D: End-to-End API Integration & Grounded Query Execution.

Implements the official API contract from orion-space/api/README.md:
- GET  /api/v1/health          - Data pipeline and cache health check
- GET  /api/v1/variables       - Catalog of 4 NASA Earth-system variables
- GET  /api/v1/months          - 12 calendar months & climatological seasons
- GET  /api/v1/locations       - 34 retained Bangladesh mainland cells
- POST /api/v1/analyze         - Primary Intelligence Endpoint (Question -> Parser -> Retriever -> LLM)
- GET  /api/v1/trends/spatial  - Direct access to spatial trend data
- GET  /api/v1/relationships   - Direct access to cross-variable coupling data
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure src modules are resolvable
API_DIR = Path(__file__).resolve().parent
ORION_DIR = API_DIR.parent
SRC_DIR = ORION_DIR / "src"
for p in [str(SRC_DIR), str(ORION_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from src.query_models import (
        Variable,
        TrendDirection,
        SignificanceFilter,
        TrendTest,
        CorrelationTest,
        LocationScope,
        DivisionName,
        TrendQuery,
        RelationshipQuery,
    )
    from src.query_parser import parse_natural_query
    from src.query_retriever import (
        ScientificDataLoader,
        retrieve_scientific_evidence,
        execute_trend_query,
        execute_relationship_query,
        VARIABLE_METADATA,
        MONTH_NAMES,
        REFERENCE_CITIES,
    )
    from src.llm_explainer import generate_grounded_explanation
except ImportError:
    from query_models import (
        Variable,
        TrendDirection,
        SignificanceFilter,
        TrendTest,
        CorrelationTest,
        LocationScope,
        DivisionName,
        TrendQuery,
        RelationshipQuery,
    )
    from query_parser import parse_natural_query
    from query_retriever import (
        ScientificDataLoader,
        retrieve_scientific_evidence,
        execute_trend_query,
        execute_relationship_query,
        VARIABLE_METADATA,
        MONTH_NAMES,
        REFERENCE_CITIES,
    )
    from llm_explainer import generate_grounded_explanation


# ==============================================================================
# FastAPI App Initialization
# ==============================================================================

app = FastAPI(
    title="Orion Space Intelligence API",
    description="NASA Earth System Trend Detective API for Bangladesh (2001–2025)",
    version="1.0.0",
)

# Enable CORS for Next.js / frontend dashboards
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# Request & Response Contracts
# ==============================================================================

class AnalysisRequest(BaseModel):
    """Payload for POST /api/v1/analyze."""
    question: str = Field(..., min_length=2, description="Natural language question.")
    override_filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional manual filter overrides from UI (e.g. variable, month, alpha).",
    )


# ==============================================================================
# Endpoints
# ==============================================================================

@app.get("/", tags=["System"])
def root_metadata():
    """Root metadata and system information."""
    return {
        "project": "Orion Space — NASA Earth System Trend Detective",
        "challenge": "NASA Space Apps Challenge 2026",
        "version": "1.0.0",
        "api_docs": "/docs",
        "endpoints": {
            "health": "/api/v1/health",
            "variables": "/api/v1/variables",
            "months": "/api/v1/months",
            "locations": "/api/v1/locations",
            "analyze": "POST /api/v1/analyze",
            "spatial_trends": "/api/v1/trends/spatial",
            "relationships": "/api/v1/relationships",
        },
    }


@app.get("/api/v1/health", tags=["System"])
def health_check():
    """Verify backend and scientific dataset cache availability."""
    try:
        loader = ScientificDataLoader.get_loader()
        return {
            "status": "healthy",
            "datasets": {
                "multivariable_trends_fdr": {
                    "records": len(loader.df_trends),
                    "variables": sorted(loader.df_trends["variable"].unique().tolist()),
                },
                "variable_relationships_fdr": {
                    "records": len(loader.df_rel),
                    "pairs_count": len(loader.df_rel.groupby(["variable_a", "variable_b"])),
                },
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scientific dataset loader failed: {str(e)}",
        )


@app.get("/api/v1/variables", tags=["Catalog"])
def get_variables_catalog():
    """Returns catalog of the 4 monitored NASA Earth-system variables."""
    catalog = [
        {
            "id": "T2M",
            "name": "Air Temperature at 2 Meters",
            "category": "Thermal",
            "unit": "°C",
            "rate_unit": "°C/decade",
            "source": "NASA GMAO MERRA-2",
            "resolution": "0.5° x 0.625°",
            "description": "Surface air temperature at 2 meters altitude.",
        },
        {
            "id": "PRECTOTCORR",
            "name": "Corrected Precipitation",
            "category": "Hydro-climate",
            "unit": "mm/day",
            "rate_unit": "mm/day/decade",
            "source": "NASA GMAO MERRA-2",
            "resolution": "0.5° x 0.625°",
            "description": "Bias-corrected total precipitation rate.",
        },
        {
            "id": "GWETTOP",
            "name": "Top-layer Soil Wetness",
            "category": "Land Hydrology",
            "unit": "0-1 fraction",
            "rate_unit": "fraction/decade",
            "source": "NASA GMAO MERRA-2 Land Model",
            "resolution": "0.5° x 0.625°",
            "description": "Surface 0-5 cm soil moisture saturation index.",
        },
        {
            "id": "ALLSKY_SFC_SW_DWN",
            "name": "All-Sky Surface Solar Irradiance",
            "category": "Radiative Energy",
            "unit": "MJ/m²/day",
            "rate_unit": "MJ/m²/day/decade",
            "source": "NASA CERES / FLASHFlux",
            "resolution": "1.0° x 1.0° (Nearest-neighbor mapped)",
            "description": "Total downwelling solar radiation reaching Earth's surface.",
        },
    ]
    return {
        "status": "success",
        "count": len(catalog),
        "data": catalog,
    }


@app.get("/api/v1/months", tags=["Catalog"])
def get_months_catalog():
    """Returns calendar months and Bangladesh climatological seasonal clusters."""
    return {
        "status": "success",
        "count": 12,
        "seasons": {
            "Winter": [12, 1, 2],
            "Pre-Monsoon": [3, 4, 5],
            "Monsoon": [6, 7, 8],
            "Post-Monsoon": [9, 10, 11],
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
            {"month_num": 12, "name": "December", "season": "Winter"},
        ],
    }


@app.get("/api/v1/locations", tags=["Catalog"])
def get_locations_catalog():
    """Returns the 34 retained Bangladesh mainland grid cells with divisional metadata."""
    loader = ScientificDataLoader.get_loader()
    unique_cells = (
        loader.df_trends[["latitude", "longitude", "nearest_division"]]
        .drop_duplicates()
        .sort_values(by=["latitude", "longitude"], ascending=[False, True])
    )

    cells_data = []
    for idx, row in enumerate(unique_cells.itertuples(index=False), start=1):
        cells_data.append({
            "cell_id": f"BGD_{idx:02d}",
            "latitude": float(row.latitude),
            "longitude": float(row.longitude),
            "nearest_division": str(row.nearest_division),
        })

    return {
        "status": "success",
        "count": len(cells_data),
        "boundary_source": "geoBoundaries-BGD-ADM0.geojson",
        "filtering_method": "Point-in-Polygon (PIP) intersection test",
        "data": cells_data,
    }


@app.post("/api/v1/analyze", tags=["Intelligence"])
def analyze_query(request: AnalysisRequest):
    """
    Primary Intelligence Endpoint:
    Natural language question -> Rule-Based Parser -> Deterministic Retriever -> Grounded LLM Explainer.
    """
    try:
        # Step 1: Parse natural query into validated Pydantic model
        parsed = parse_natural_query(
            question=request.question,
            override_filters=request.override_filters,
        )

        # Step 2: Retrieve verified scientific evidence and visualization payload
        retrieval_bundle = retrieve_scientific_evidence(parsed.query_object)
        evidence = retrieval_bundle["evidence"]
        visualization = retrieval_bundle["visualization"]

        # Step 3: Synthesize evidence-grounded explanation
        explanation_obj = generate_grounded_explanation(evidence)

        # Determine resolved variable label for display
        q_meta = evidence.get("query_metadata", {})
        res_var = q_meta.get("variable")
        if not res_var and "variable_a" in q_meta and "variable_b" in q_meta:
            res_var = f"{q_meta['variable_a']} ↔ {q_meta['variable_b']}"
        elif not res_var and "variable" in q_meta:
            res_var = q_meta.get("variable")
        query_location = getattr(parsed.query_object, "location", None)
        division_name = getattr(getattr(query_location, "division_name", None), "value", None)
        resolved_test_type = getattr(getattr(parsed.query_object, "test_type", None), "value", None)
        resolved_significance = getattr(getattr(parsed.query_object, "significance_filter", None), "value", None)
        resolved_variables = [q_meta.get("variable_a"), q_meta.get("variable_b")]
        resolved_variables = [item for item in resolved_variables if item]

        # Assemble unified response matching official API contract
        response_payload = {
            "status": "success",
            "query_intent": {
                "raw_question": parsed.raw_question,
                "intent": parsed.intent,
                "resolved_variable": res_var or "",
                "variable_name": q_meta.get("variable_name") or res_var or "",
                "unit": q_meta.get("rate_unit") or q_meta.get("unit", ""),
                "resolved_month": q_meta.get("month_name", ""),
                "month_num": q_meta.get("month_num"),
                "variable_a": q_meta.get("variable_a"),
                "variable_b": q_meta.get("variable_b"),
                "resolved_variables": resolved_variables,
                "resolved_division": division_name or "All Bangladesh",
                "resolved_test_type": resolved_test_type,
                "resolved_significance_filter": resolved_significance,
            },
            "scientific_metrics": evidence.get("summary_statistics", {}),
            "locations": evidence.get("cells", []),
            "visualization": visualization,
            "explanation": explanation_obj.model_dump(),
            "evidence_id": evidence.get("evidence_id"),
            "methodological_caveats": evidence.get("methodological_caveats", []),
        }

        return response_payload

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis pipeline error: {str(e)}",
        )


@app.get("/api/v1/trends/spatial", tags=["Scientific Data"])
def get_spatial_trends(
    variable: str = Query("T2M", description="Earth-system parameter (T2M, PRECTOTCORR, GWETTOP, ALLSKY_SFC_SW_DWN)"),
    month: int = Query(9, ge=1, le=12, description="Calendar month (1..12)"),
    alpha: float = Query(0.05, ge=0.001, le=0.1, description="FDR significance threshold"),
):
    """Direct query of spatial trend records for a variable and month."""
    try:
        query = TrendQuery(
            intent="trend",
            variable=Variable(variable),
            month=month,
            alpha=alpha,
        )
        loader = ScientificDataLoader.get_loader()
        return execute_trend_query(query, loader.df_trends)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/api/v1/relationships", tags=["Scientific Data"])
def get_variable_relationships(
    variable_a: str = Query("T2M", description="Primary variable"),
    variable_b: str = Query("GWETTOP", description="Secondary variable"),
    month: int = Query(5, ge=1, le=12, description="Calendar month (1..12)"),
    alpha: float = Query(0.05, ge=0.001, le=0.1, description="FDR significance threshold"),
):
    """Direct query of cross-variable spatial correlation records."""
    try:
        query = RelationshipQuery(
            intent="relationship",
            variable=Variable(variable_a),
            secondary_variable=Variable(variable_b),
            month=month,
            alpha=alpha,
        )
        loader = ScientificDataLoader.get_loader()
        return execute_relationship_query(query, loader.df_rel)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ==============================================================================
# Development Server Runner
# ==============================================================================

if __name__ == "__main__":
    import uvicorn
    print("Starting Orion Space Intelligence API Server on http://localhost:8000 ...")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
