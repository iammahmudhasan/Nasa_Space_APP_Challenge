from typing import Dict, Any, List

# Realistic geographic boundaries for key ecological monitoring zones in Coastal Bangladesh
COASTAL_BANGLADESH_REGIONS = {
    "sundarbans_west": {
        "id": "sundarbans_west",
        "name": "Sundarbans Biosphere (Satkhira & West Division)",
        "type": "Mangrove Forest / High Salinity Risk",
        "coordinates": [
            [89.02, 21.65], [89.15, 21.60], [89.32, 21.72], [89.42, 21.85],
            [89.48, 22.15], [89.40, 22.38], [89.18, 22.35], [89.05, 22.18],
            [89.00, 21.85], [89.02, 21.65]
        ],
        "center": [22.05, 89.25],
        "baseline_ndvi": 0.74,
        "target_ndvi": 0.61,  # Significant loss due to salinity & storm surges
        "area_ha": 312000.0
    },
    "sundarbans_east": {
        "id": "sundarbans_east",
        "name": "Sundarbans Wildlife Sanctuary (Bagerhat / Sharankhola)",
        "type": "Freshwater Mangrove Zone",
        "coordinates": [
            [89.50, 21.75], [89.70, 21.70], [89.92, 21.80], [89.98, 22.15],
            [89.92, 22.42], [89.65, 22.40], [89.52, 22.18], [89.50, 21.75]
        ],
        "center": [22.10, 89.72],
        "baseline_ndvi": 0.78,
        "target_ndvi": 0.72,  # Moderate loss / cyclone recovery
        "area_ha": 289000.0
    },
    "khulna_coastal_belt": {
        "id": "khulna_coastal_belt",
        "name": "Khulna & Dacope Brackish Polder Zone",
        "type": "Agricultural / Shrimp Aquaculture Conversion",
        "coordinates": [
            [89.30, 22.40], [89.65, 22.42], [89.78, 22.65], [89.72, 22.88],
            [89.45, 22.90], [89.28, 22.68], [89.30, 22.40]
        ],
        "center": [22.62, 89.55],
        "baseline_ndvi": 0.58,
        "target_ndvi": 0.49,
        "area_ha": 195000.0
    },
    "bhola_island": {
        "id": "bhola_island",
        "name": "Bhola Island & Lower Meghna Estuary",
        "type": "Estuarine Alluvial Delta / Coastal Char",
        "coordinates": [
            [90.62, 21.85], [90.85, 21.92], [90.92, 22.35], [90.80, 22.78],
            [90.60, 22.80], [90.52, 22.38], [90.55, 22.05], [90.62, 21.85]
        ],
        "center": [22.35, 90.72],
        "baseline_ndvi": 0.62,
        "target_ndvi": 0.59,
        "area_ha": 340000.0
    },
    "cox_bazar_coast": {
        "id": "cox_bazar_coast",
        "name": "Cox's Bazar Coastal Forest Strip & Teknaf",
        "type": "Coastal Hill Forest & Shoreline",
        "coordinates": [
            [91.95, 20.85], [92.15, 20.88], [92.32, 21.25], [92.20, 21.65],
            [91.95, 21.60], [91.98, 21.25], [91.95, 20.85]
        ],
        "center": [21.25, 92.12],
        "baseline_ndvi": 0.69,
        "target_ndvi": 0.64,
        "area_ha": 215000.0
    }
}

def get_coastal_bangladesh_geojson() -> Dict[str, Any]:
    """
    Returns a unified FeatureCollection of all coastal Bangladesh ecological monitoring zones
    annotated with realistic delta contours and NDVI degradation status.
    """
    features = []
    for zone_id, data in COASTAL_BANGLADESH_REGIONS.items():
        delta = round(data["target_ndvi"] - data["baseline_ndvi"], 3)
        pct = round((delta / data["baseline_ndvi"]) * 100, 1)
        
        if pct <= -15.0:
            status = "Severe Degradation"
            color = "#ff3366"
        elif pct <= -5.0:
            status = "Moderate Degradation"
            color = "#ff9900"
        elif pct >= 5.0:
            status = "Greening / Recovery"
            color = "#00ff9d"
        else:
            status = "Stable"
            color = "#00e5ff"

        feature = {
            "type": "Feature",
            "id": zone_id,
            "properties": {
                "name": data["name"],
                "zone_id": zone_id,
                "ecosystem_type": data["type"],
                "baseline_ndvi": data["baseline_ndvi"],
                "target_ndvi": data["target_ndvi"],
                "delta_ndvi": delta,
                "percentage_change": pct,
                "status": status,
                "area_ha": data["area_ha"],
                "fill_color": color,
                "fill_opacity": 0.45,
                "stroke_color": color,
                "stroke_width": 2
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [data["coordinates"]]
            }
        }
        features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features
    }

def get_region_metadata(region_id: str = "sundarbans_west") -> Dict[str, Any]:
    return COASTAL_BANGLADESH_REGIONS.get(region_id, COASTAL_BANGLADESH_REGIONS["sundarbans_west"])
