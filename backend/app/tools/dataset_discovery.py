from typing import Dict, Any, List
from app.services.nasa_cmr import search_nasa_cmr, VERIFIED_NASA_DATASETS
from app.models.schemas import DatasetMetadata

async def discover_dataset_for_query(query: str, metric: str = "NDVI") -> DatasetMetadata:
    """
    Intelligently maps natural language scientific query to appropriate NASA Earth observation dataset.
    """
    keyword = "MOD13Q1"
    query_lower = query.lower()
    
    if "viirs" in query_lower:
        keyword = "VNP13A1"
    elif "temp" in query_lower or "thermal" in query_lower or "heat" in query_lower:
        keyword = "MOD11A2"
    elif "rain" in query_lower or "precip" in query_lower or "flood" in query_lower:
        keyword = "GPM_3IMERGM"
    elif "vegetation" in query_lower or "mangrove" in query_lower or "forest" in query_lower or "green" in query_lower or "ndvi" in query_lower:
        keyword = "MOD13Q1"

    # Search NASA CMR
    results = await search_nasa_cmr(keyword, limit=3)
    entry = results[0] if results else VERIFIED_NASA_DATASETS["MOD13Q1"]
    
    return DatasetMetadata(
        id=entry.get("id", "MOD13Q1-061"),
        short_name=entry.get("short_name", "MOD13Q1"),
        title=entry.get("title", "MODIS/Terra Vegetation Indices 16-Day L3 Global 250m SIN Grid V061"),
        doi=entry.get("doi", "10.5067/MODIS/MOD13Q1.061"),
        doi_url=entry.get("doi_url", "https://doi.org/10.5067/MODIS/MOD13Q1.061"),
        sensor=entry.get("sensor", "MODIS"),
        platform=entry.get("platform", "Terra"),
        spatial_resolution=entry.get("spatial_resolution", "250 meters"),
        temporal_resolution=entry.get("temporal_resolution", "16-day"),
        data_provider=entry.get("data_provider", "NASA LP DAAC"),
        collection_concept_id=entry.get("collection_concept_id", "C1621073801-LPDAAC_ECS")
    )
