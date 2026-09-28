import httpx
import logging
from typing import List, Dict, Any
from app.config import FIRMS_MAP_KEY

logger = logging.getLogger(__name__)

async def get_active_fires_for_region(
    bbox: List[float] = [88.0, 20.0, 93.0, 27.0], 
    days: int = 1
) -> List[Dict[str, Any]]:
    """
    Fetches real-time active fire anomalies from NASA FIRMS (VIIRS S-NPP)
    using the authenticated NASA FIRMS API key.
    """
    if not FIRMS_MAP_KEY:
        logger.warning("NASA FIRMS Map Key not configured.")
        return []

    # Format: min_lon, min_lat, max_lon, max_lat
    min_lon, min_lat, max_lon, max_lat = bbox
    area_str = f"{min_lon},{min_lat},{max_lon},{max_lat}"
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{FIRMS_MAP_KEY}/VIIRS_SNPP_NRT/{area_str}/{days}"

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            res = await client.get(url)
            if res.status_code == 200:
                lines = res.text.strip().split("\n")
                if len(lines) <= 1:
                    return []
                
                headers = lines[0].split(",")
                records = []
                for line in lines[1:]:
                    vals = line.split(",")
                    if len(vals) == len(headers):
                        record = dict(zip(headers, vals))
                        records.append({
                            "latitude": float(record.get("latitude", 0)),
                            "longitude": float(record.get("longitude", 0)),
                            "brightness": float(record.get("bright_ti4", 0)),
                            "acquisition_date": record.get("acq_date"),
                            "confidence": record.get("confidence"),
                            "frp": float(record.get("frp", 0))
                        })
                return records
    except Exception as e:
        logger.warning(f"Failed fetching FIRMS data: {e}")
    return []
