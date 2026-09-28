from typing import Dict, Any

NASA_GIBS_LAYERS = {
    "MODIS_Terra_TrueColor": {
        "title": "NASA GIBS Terra / MODIS Corrected Reflectance (True Color)",
        "url_template": "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/{time}/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg",
        "format": "image/jpeg",
        "max_zoom": 9,
        "attribution": "NASA EOSDIS GIBS / Worldview"
    },
    "MODIS_Terra_NDVI_16Day": {
        "title": "NASA GIBS Terra / MODIS 16-Day NDVI Vegetation Index",
        "url_template": "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_NDVI_16Day/default/{time}/GoogleMapsCompatible_Level8/{z}/{y}/{x}.png",
        "format": "image/png",
        "max_zoom": 8,
        "attribution": "NASA EOSDIS GIBS / LP DAAC"
    },
    "VIIRS_SNPP_TrueColor": {
        "title": "NASA GIBS Suomi NPP / VIIRS Corrected Reflectance (True Color)",
        "url_template": "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_SNPP_CorrectedReflectance_TrueColor/default/{time}/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg",
        "format": "image/jpeg",
        "max_zoom": 9,
        "attribution": "NASA EOSDIS GIBS"
    }
}

def get_gibs_layer_config(layer_key: str = "MODIS_Terra_NDVI_16Day", observation_date: str = "2024-01-01") -> Dict[str, Any]:
    layer = NASA_GIBS_LAYERS.get(layer_key, NASA_GIBS_LAYERS["MODIS_Terra_NDVI_16Day"])
    return {
        **layer,
        "time": observation_date,
        "resolved_url": layer["url_template"].replace("{time}", observation_date)
    }
