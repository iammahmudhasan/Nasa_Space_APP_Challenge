"""
Spatial Trend Analysis Engine for Bangladesh
Project: Orion Space - NASA Earth System Trend Detective
Variable: T2M (Air Temperature at 2 Meters, deg C)
Data Source: NASA GMAO MERRA-2 via NASA POWER Regional API
Time Period: 2001 - 2025

Responsibilities:
- Part A: Generate Bangladesh geographic grid (20.5 - 26.5 N, 88.0 - 92.8 E)
- Part B: Efficient regional data retrieval strategy from NASA POWER API
- Part C: Statistical trend & significance testing for each coordinate
- Part D: Structured DataFrame assembly and CSV export
"""

import os
import json
import requests
import numpy as np
import pandas as pd
from scipy import stats

from src.trend_analysis import compute_linear_trend, mann_kendall_test

NASA_POWER_REGIONAL_URL = "https://power.larc.nasa.gov/api/temporal/monthly/regional"

def generate_bangladesh_grid(
    lat_min: float = 20.5,
    lat_max: float = 26.5,
    lon_min: float = 88.0,
    lon_max: float = 92.8,
    step: float = 0.5
) -> list[tuple[float, float]]:
    """
    Part A: Generate a synthetic coarse geographic grid covering Bangladesh bounding box.
    
    Returns:
        list of (latitude, longitude) tuples.
    """
    lats = np.arange(lat_min, lat_max + step / 2, step)
    lons = np.arange(lon_min, lon_max + step / 2, step)
    
    grid = []
    for lat in lats:
        for lon in lons:
            grid.append((round(float(lat), 4), round(float(lon), 4)))
            
    return grid


def fetch_or_load_regional_data(
    cache_path: str = "data/bangladesh_t2m_regional_raw.json",
    lat_min: float = 20.5,
    lat_max: float = 26.5,
    lon_min: float = 88.0,
    lon_max: float = 92.8,
    start_year: str = "2001",
    end_year: str = "2025",
    force_fetch: bool = False
) -> dict:
    """
    Part B: Optimized Regional Retrieval Strategy.
    Fetches multi-decadal monthly/annual data across all grid points in a single request.
    Caches the raw GeoJSON response locally to prevent duplicate network calls.
    """
    if os.path.exists(cache_path) and not force_fetch:
        print(f"[CACHE] Loading regional dataset from: {cache_path}")
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)
            
    print(f"[FETCH] Requesting NASA POWER Regional API for Bangladesh Bounding Box:")
    print(f"        Lat: [{lat_min}, {lat_max}], Lon: [{lon_min}, {lon_max}], Years: [{start_year} - {end_year}]...")
    
    params = {
        "parameters": "T2M",
        "community": "AG",
        "latitude-min": lat_min,
        "latitude-max": lat_max,
        "longitude-min": lon_min,
        "longitude-max": lon_max,
        "start": start_year,
        "end": end_year,
        "format": "JSON"
    }
    
    response = requests.get(NASA_POWER_REGIONAL_URL, params=params, timeout=90)
    response.raise_for_status()
    data = response.json()
    
    features = data.get("features", [])
    print(f"[SUCCESS] Retrieved {len(features)} regional grid points from NASA POWER API.")
    
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    print(f"[SAVED] Cached regional raw data to: {cache_path}")
    
    return data


def parse_regional_annual_series(feature: dict) -> tuple[float, float, np.ndarray, np.ndarray]:
    """
    Extracts coordinates and annual temperature series from a GeoJSON feature.
    NASA POWER monthly format stores annual mean with key 'YYYY13'.
    
    Returns:
        tuple: (latitude, longitude, years_array, annual_temps_array)
    """
    coords = feature["geometry"]["coordinates"]
    lon = float(coords[0])
    lat = float(coords[1])
    
    t2m_dict = feature["properties"]["parameter"]["T2M"]
    
    # Extract keys ending in '13' (e.g., '200113' -> year 2001)
    annual_keys = sorted([k for k in t2m_dict.keys() if k.endswith("13")])
    
    years = []
    temps = []
    for k in annual_keys:
        yr = int(k[:4])
        val = t2m_dict[k]
        # Treat NASA fill value (-999.0) as NaN
        if val == -999.0 or val is None:
            val = np.nan
        years.append(yr)
        temps.append(val)
        
    return lat, lon, np.array(years, dtype=int), np.array(temps, dtype=float)


def compute_spatial_trends(
    regional_json: dict,
    alpha: float = 0.05
) -> pd.DataFrame:
    """
    Part C: Executes statistical trend analysis for each geographic coordinate.
    
    Calculates:
    - OLS Linear Regression slope
    - Mann-Kendall non-parametric test and Sen's slope
    - Decadal rate of change
    - Statistical significance at chosen alpha level
    """
    features = regional_json.get("features", [])
    if not features:
        raise ValueError("Regional JSON contains no features.")
        
    records = []
    
    for feat in features:
        lat, lon, years, annual_temps = parse_regional_annual_series(feat)
        
        # Check valid observation count
        valid_mask = ~np.isnan(annual_temps)
        if np.sum(valid_mask) < 5:
            continue
            
        # 1. Linear Regression (OLS)
        ols_res = compute_linear_trend(years, annual_temps)
        
        # 2. Mann-Kendall & Sen's Slope
        mk_res = mann_kendall_test(annual_temps)
        
        slope_c_per_year = ols_res["slope"]
        slope_c_per_decade = slope_c_per_year * 10.0
        p_val = ols_res["p_value"]
        sen_slope = mk_res["sens_slope"]
        
        # Direction determined by slope sign
        if slope_c_per_year > 0:
            trend_dir = "Increasing"
        elif slope_c_per_year < 0:
            trend_dir = "Decreasing"
        else:
            trend_dir = "No Trend"
            
        is_sig = bool(p_val < alpha)
        
        records.append({
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "slope_c_per_year": round(slope_c_per_year, 6),
            "slope_c_per_decade": round(slope_c_per_decade, 4),
            "p_value": round(p_val, 6),
            "sen_slope": round(sen_slope, 6),
            "trend_direction": trend_dir,
            "is_significant": is_sig
        })
        
    df_results = pd.DataFrame(records)
    
    # Sort by latitude descending, longitude ascending
    df_results.sort_values(by=["latitude", "longitude"], ascending=[False, True], inplace=True)
    df_results.reset_index(drop=True, inplace=True)
    
    return df_results


def run_spatial_pipeline(
    output_csv: str = "data/bangladesh_t2m_spatial_trends.csv",
    cache_json: str = "data/bangladesh_t2m_regional_raw.json",
    force_fetch: bool = False
) -> pd.DataFrame:
    """
    Part D: High-level execution function.
    Fetches/loads data, calculates trends, and saves structured results to CSV.
    """
    # 1. Fetch or load regional NASA data
    data = fetch_or_load_regional_data(cache_path=cache_json, force_fetch=force_fetch)
    
    # 2. Run spatial statistics
    print("[PROCESSING] Calculating statistical trends across all grid points...")
    df_trends = compute_spatial_trends(data)
    
    # 3. Save to CSV
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df_trends.to_csv(output_csv, index=False)
    print(f"[EXPORT] Successfully saved spatial trend table with {len(df_trends)} points to: {output_csv}")
    
    # Print summary statistics
    n_total = len(df_trends)
    n_sig = df_trends["is_significant"].sum()
    n_inc = (df_trends["trend_direction"] == "Increasing").sum()
    n_dec = (df_trends["trend_direction"] == "Decreasing").sum()
    
    print("\n" + "=" * 70)
    print("SPATIAL ANALYSIS SUMMARY (BANGLADESH T2M: 2001 - 2025)")
    print("=" * 70)
    print(f"Total Evaluated Grid Points:       {n_total}")
    print(f"Points with Increasing Trend:      {n_inc} ({(n_inc/n_total)*100:.1f}%)")
    print(f"Points with Decreasing Trend:      {n_dec} ({(n_dec/n_total)*100:.1f}%)")
    print(f"Statistically Significant (p<0.05): {n_sig} ({(n_sig/n_total)*100:.1f}%)")
    print(f"Mean Decadal Rate of Change:       {df_trends['slope_c_per_decade'].mean():+.4f} deg C / decade")
    print(f"Min Decadal Rate of Change:        {df_trends['slope_c_per_decade'].min():+.4f} deg C / decade")
    print(f"Max Decadal Rate of Change:        {df_trends['slope_c_per_decade'].max():+.4f} deg C / decade")
    print("=" * 70)
    
    return df_trends


if __name__ == "__main__":
    run_spatial_pipeline()
