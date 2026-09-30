"""
Multi-Variable Data Loader & Ingestion Engine
Project: Orion Space - NASA Earth System Trend Detective
Target: Step 5A - Multi-variable Earth-System Data Ingestion & Standardization

NASA POWER Monthly Regional API Endpoint:
https://power.larc.nasa.gov/api/temporal/monthly/regional

Configured Earth-System Variables:
1. T2M               : Air Temperature at 2 Meters (°C)
2. PRECTOTCORR       : Precipitation Corrected (mm/day)
3. GWETTOP           : Top-layer Soil Wetness (0-1 fraction, dimensionless)
4. ALLSKY_SFC_SW_DWN : All-sky Surface Downwelling Shortwave Flux (MJ/m^2/day)

Responsibilities (Step 5A):
- Maintain parameter configurations (API keys, units, metadata, filenames)
- Fetch regional data per parameter in separate, rate-friendly HTTP requests
- Cache raw GeoJSON responses locally in data/
- Validate completeness across coordinates, temporal range (2001–2025), and monthly keys
"""

import os
import sys
import json
import time
import shutil
import requests
import numpy as np
import pandas as pd

NASA_POWER_REGIONAL_URL = "https://power.larc.nasa.gov/api/temporal/monthly/regional"

# Standard Bounding Box for Bangladesh (covering 20.5°N - 26.5°N, 88.0°E - 92.8°E)
DEFAULT_LAT_MIN = 20.5
DEFAULT_LAT_MAX = 26.5
DEFAULT_LON_MIN = 88.0
DEFAULT_LON_MAX = 92.8
DEFAULT_START_YEAR = "2001"
DEFAULT_END_YEAR = "2025"

VARIABLE_CONFIGS = {
    "T2M": {
        "parameter": "T2M",
        "name": "Air Temperature at 2 Meters",
        "category": "Thermal",
        "unit": "deg C",
        "source": "NASA GMAO MERRA-2",
        "raw_filename": "bangladesh_t2m_regional_raw.json",
        "description": "Surface air temperature at 2 meters altitude."
    },
    "PRECTOTCORR": {
        "parameter": "PRECTOTCORR",
        "name": "Corrected Precipitation",
        "category": "Hydro-climate",
        "unit": "mm/day",
        "source": "NASA GMAO MERRA-2",
        "raw_filename": "bangladesh_precip_regional_raw.json",
        "description": "Bias-corrected total precipitation rate."
    },
    "GWETTOP": {
        "parameter": "GWETTOP",
        "name": "Top-layer Soil Wetness",
        "category": "Land-Surface Hydrology",
        "unit": "dimensionless (0-1 fraction)",
        "source": "NASA GMAO MERRA-2 Land Model",
        "raw_filename": "bangladesh_soil_moisture_regional_raw.json",
        "description": "Surface (0-5 cm) soil moisture saturation index."
    },
    "ALLSKY_SFC_SW_DWN": {
        "parameter": "ALLSKY_SFC_SW_DWN",
        "name": "All-Sky Surface Solar Irradiance",
        "category": "Radiative Energy",
        "unit": "MJ/m^2/day",
        "source": "NASA CERES / FLASHFlux",
        "raw_filename": "bangladesh_solar_regional_raw.json",
        "description": "Total downwelling solar radiation reaching Earth's surface."
    }
}


def find_target_path(filename: str, subfolder: str = "data") -> str:
    """
    Resolves data file path prioritizing orion-space/data then data/.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(script_dir, "..", subfolder, filename),
        os.path.join(subfolder, filename),
        os.path.join("orion-space", subfolder, filename),
        os.path.join(script_dir, "..", "..", subfolder, filename),
    ]
    for p in candidates:
        if os.path.exists(p):
            return os.path.abspath(p)
    return os.path.abspath(candidates[0])


def fetch_regional_parameter(
    parameter_key: str,
    lat_min: float = DEFAULT_LAT_MIN,
    lat_max: float = DEFAULT_LAT_MAX,
    lon_min: float = DEFAULT_LON_MIN,
    lon_max: float = DEFAULT_LON_MAX,
    start_year: str = DEFAULT_START_YEAR,
    end_year: str = DEFAULT_END_YEAR,
    force_fetch: bool = False
) -> dict:
    """
    Retrieves and caches NASA POWER regional monthly data for a single Earth-system parameter.
    
    Parameters:
        parameter_key (str): Variable identifier (T2M, PRECTOTCORR, GWETTOP, ALLSKY_SFC_SW_DWN).
        lat_min, lat_max, lon_min, lon_max (float): Bounding box coordinates.
        start_year, end_year (str): 4-digit years (e.g. '2001', '2025').
        force_fetch (bool): If True, bypasses local cache and fetches fresh from API.
        
    Returns:
        dict: Raw GeoJSON data from NASA POWER API.
    """
    if parameter_key not in VARIABLE_CONFIGS:
        raise ValueError(f"Unknown parameter '{parameter_key}'. Allowed: {list(VARIABLE_CONFIGS.keys())}")
        
    cfg = VARIABLE_CONFIGS[parameter_key]
    filename = cfg["raw_filename"]
    local_path = find_target_path(filename)
    
    # 1. Check local cache
    if os.path.exists(local_path) and not force_fetch:
        print(f"[CACHE] Loading {parameter_key} ({cfg['name']}) from: {local_path}")
        with open(local_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
        
    # 2. Issue dedicated regional API request
    print(f"[FETCH] Querying NASA POWER Regional API for '{parameter_key}' ({cfg['name']})...")
    print(f"        Bounds: Lat [{lat_min}, {lat_max}], Lon [{lon_min}, {lon_max}] | Window: {start_year}-{end_year}")
    
    params = {
        "parameters": parameter_key,
        "community": "AG",
        "latitude-min": lat_min,
        "latitude-max": lat_max,
        "longitude-min": lon_min,
        "longitude-max": lon_max,
        "start": start_year,
        "end": end_year,
        "format": "JSON"
    }
    
    t0 = time.time()
    response = requests.get(NASA_POWER_REGIONAL_URL, params=params, timeout=120)
    elapsed = time.time() - t0
    
    if response.status_code != 200:
        raise RuntimeError(
            f"NASA POWER API error for parameter {parameter_key} (status {response.status_code}):\n{response.text[:500]}"
        )
        
    data = response.json()
    features = data.get("features", [])
    print(f"[SUCCESS] Retrieved {parameter_key} in {elapsed:.2f}s ({len(features)} regional grid cells).")
    
    # 3. Cache to primary and mirror locations
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    with open(local_path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    print(f"[SAVED] Cached to: {local_path}")
    
    # Mirror to root data/
    root_mirror = os.path.abspath(os.path.join("data", filename))
    if os.path.abspath(local_path) != root_mirror:
        try:
            os.makedirs(os.path.dirname(root_mirror), exist_ok=True)
            shutil.copyfile(local_path, root_mirror)
            print(f"[MIRROR] Copied to: {root_mirror}")
        except Exception:
            pass
            
    return data


def validate_regional_dataset(data: dict, parameter_key: str) -> dict:
    """
    Validates structural integrity, key coverage, and absence of fill values across all cells.
    
    Strict Criteria:
    - Non-empty features list
    - Every feature has exactly 325 keys (25 years x 13 values: 12 months + 1 annual mean)
    - Zero missing / fill values (-999.0)
    - Full continuous coverage for 2001 - 2025
    
    Returns:
        dict: Validation metrics.
    """
    features = data.get("features", [])
    if not features:
        raise ValueError(f"Dataset for {parameter_key} contains zero features.")
        
    all_cells_have_325 = True
    total_values = 0
    missing_fill_count = 0
    years_seen = set()
    
    for feat in features:
        p_dict = feat.get("properties", {}).get("parameter", {}).get(parameter_key, {})
        if len(p_dict) != 325:
            all_cells_have_325 = False
        for k, v in p_dict.items():
            total_values += 1
            years_seen.add(k[:4])
            if v == -999.0 or v is None:
                missing_fill_count += 1
                
    years_sorted = sorted(list(years_seen))
    is_valid = bool(
        len(features) > 0
        and len(years_sorted) == 25
        and all_cells_have_325
        and missing_fill_count == 0
    )
    
    metrics = {
        "parameter": parameter_key,
        "grid_cells_count": len(features),
        "total_values_checked": total_values,
        "all_cells_325_keys": all_cells_have_325,
        "missing_fill_count": missing_fill_count,
        "first_year": min(years_sorted) if years_sorted else None,
        "last_year": max(years_sorted) if years_sorted else None,
        "valid": is_valid
    }
    return metrics


def fetch_all_variables(force_fetch: bool = False) -> dict[str, dict]:
    """
    Ingests all 4 Earth-system parameters sequentially.
    
    Returns:
        dict[str, dict]: Mapping of parameter_key -> GeoJSON data.
    """
    datasets = {}
    print("\n" + "=" * 80)
    print("ORION SPACE - MULTI-VARIABLE INGESTION ENGINE (STEP 5A)")
    print("Parameters: T2M, PRECTOTCORR, GWETTOP, ALLSKY_SFC_SW_DWN")
    print("Window:     2001 - 2025 (25 Years)")
    print("=" * 80)
    
    validation_reports = []
    
    for key, cfg in VARIABLE_CONFIGS.items():
        print(f"\n--- Ingesting {key} [{cfg['name']}] ---")
        data = fetch_regional_parameter(key, force_fetch=force_fetch)
        datasets[key] = data
        
        # Validation
        v_meta = validate_regional_dataset(data, key)
        validation_reports.append({
            "Variable": key,
            "Name": cfg["name"],
            "Category": cfg["category"],
            "Unit": cfg["unit"],
            "Cells": v_meta["grid_cells_count"],
            "Years": f"{v_meta['first_year']}-{v_meta['last_year']}",
            "Keys/Cell": v_meta["total_keys_per_cell"],
            "Status": "PASSED" if v_meta["valid"] else "FAILED"
        })
        
    df_val = pd.DataFrame(validation_reports)
    print("\n" + "=" * 80)
    print("MULTI-VARIABLE INGESTION VALIDATION REPORT (STEP 5A)")
    print("=" * 80)
    print(df_val.to_string(index=False))
    print("=" * 80 + "\n")
    
    return datasets


if __name__ == "__main__":
    fetch_all_variables()
