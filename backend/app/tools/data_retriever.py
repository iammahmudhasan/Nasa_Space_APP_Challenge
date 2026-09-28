import logging
from typing import List, Dict, Any, Tuple
from app.models.schemas import TimeSeriesPoint
from app.services.nasa_cmr import search_cmr_granules, search_nasa_cmr, VERIFIED_NASA_DATASETS
from app.services.nasa_observations import fetch_real_nasa_observations
from app.tools.geospatial import COASTAL_BANGLADESH_REGIONS

logger = logging.getLogger(__name__)

# Supported V1 Scientific Observation Parameters
V1_SUPPORTED_METRICS = {
    "NDVI": {
        "dataset": "MOD13Q1",
        "description": "Normalized Difference Vegetation Index (Canopy greenness & photosynthetic activity)",
        "sensor": "MODIS/Terra",
        "unit": "NDVI [-0.2 to 1.0]",
        "spatial_res": "250m"
    },
    "EVI": {
        "dataset": "MOD13Q1",
        "description": "Enhanced Vegetation Index (Optimized for high-biomass mangrove forest)",
        "sensor": "MODIS/Terra",
        "unit": "EVI [-0.2 to 1.0]",
        "spatial_res": "250m"
    },
    "LST": {
        "dataset": "MOD11A2",
        "description": "Land Surface Temperature (Thermal anomaly detection)",
        "sensor": "MODIS/Terra",
        "unit": "Kelvin / Celsius",
        "spatial_res": "1000m"
    },
    "GPM_RAIN": {
        "dataset": "GPM_3IMERGM",
        "description": "Precipitation & Monsoon Flooding Dynamics",
        "sensor": "GPM Core Observatory",
        "unit": "mm/month",
        "spatial_res": "0.1 degree (~10km)"
    }
}

def validate_scientific_scope(query: str, metric: str = "NDVI") -> Dict[str, Any]:
    """
    Constrains the agent to a strictly defensible scientific domain (V1: Environmental Change).
    Active primary variable: Vegetation / NDVI.
    Roadmap: NDVI -> EVI -> Land Surface Temperature -> Precipitation -> Flood / Drought -> Multi-variable analysis.
    Blocks out-of-scope non-scientific queries to prevent hallucinations.
    """
    query_lower = query.lower()
    
    # Supported environmental keywords for V1
    environmental_keywords = [
        "vegetation", "ndvi", "evi", "mangrove", "forest", "canopy", 
        "salinity", "cyclone", "greenness", "degradation", "deforestation", 
        "tree", "environment", "environmental", "ecosystem", "biomass", 
        "plant", "chlorophyll", "phenology", "dieback", "polder", 
        "sundarbans", "khulna", "bhola", "estuary", "bangladesh", "coastal",
        "delta", "satellite", "earth observation", "modis", "terra", "remal", "amphan",
        "climate", "erosion", "accretion", "land", "soil", "drought", "flood", "change"
    ]
    
    is_in_scope = any(kw in query_lower for kw in environmental_keywords)
    
    if not is_in_scope:
        return {
            "valid": False,
            "domain": "Environmental Change",
            "active_variable": "Vegetation / NDVI",
            "reason": (
                "Query is outside the constrained V1 Scientific Domain of NEIA. "
                "The agent is strictly restricted to Planetary Environmental Change to ensure "
                "deterministic, hallucination-free empirical analysis."
            ),
            "roadmap": [
                "1. Vegetation / NDVI (Active in V1)",
                "2. EVI (Enhanced Vegetation Index)",
                "3. Land Surface Temperature (MODIS MOD11A2)",
                "4. Precipitation & Monsoons (GPM IMERG)",
                "5. Flood & Drought Dynamics",
                "6. Multi-variable Analysis"
            ],
            "suggested_queries": [
                "How has vegetation changed in coastal Bangladesh from 2020 to 2025?",
                "Analyze mangrove canopy loss and cyclonic shock in Sundarbans West.",
                "Quantify agricultural vegetation shift vs brackish aquaculture in Khulna.",
                "Detect vegetation stability anomalies in Bhola Island."
            ]
        }
    
    return {
        "valid": True,
        "domain": "Environmental Change",
        "active_variable": "Vegetation / NDVI",
        "metric": "NDVI",
        "dataset": "MOD13Q1"
    }

async def retrieve_satellite_data(
    region_id: str = "sundarbans_west",
    start_year: int = 2020,
    end_year: int = 2025,
    metric: str = "NDVI"
) -> Dict[str, Any]:
    """
    Data Retriever Tool:
    Bridges NASA CMR Granule Discovery and Empirical Observation Array.
    
    Pipeline:
      NASA CMR (Collections & Granules)
            ↓
      Data Retriever (Bounding Box Filter + Tile h26v06 + QA Masking)
            ↓
      Scientific Observation Series
    """
    region = COASTAL_BANGLADESH_REGIONS.get(region_id, COASTAL_BANGLADESH_REGIONS["sundarbans_west"])
    center = region["center"]
    bbox_str = f"{center[1] - 0.5},{center[0] - 0.5},{center[1] + 0.5},{center[0] + 0.5}"

    logger.info(f"[DataRetriever] Querying real NASA observations for {region['name']} ({start_year}-{end_year})")

    # Fetch real observations grounded in NASA CMR granules
    timeseries, cmr_granules, metadata = await fetch_real_nasa_observations(
        region_id=region_id,
        start_year=start_year,
        end_year=end_year,
        bounding_box=bbox_str
    )

    return {
        "region_id": region_id,
        "region_name": region["name"],
        "metric": metric,
        "dataset_short_name": "MOD13Q1",
        "sinusoidal_tile": "h26v06",
        "total_composites": len(timeseries),
        "granules_found_in_cmr": len(cmr_granules),
        "cmr_granules_sample": cmr_granules[:5],
        "timeseries": timeseries,
        "metadata": metadata
    }
