"""
NASA POWER Data Loader Module
Project: Orion Space - Earth System Trend Detective
Variable: T2M (Air Temperature at 2 Meters, °C)
Data Source: NASA GMAO MERRA-2 assimilation model via NASA POWER API
"""

import os
import json
import requests
import pandas as pd

NASA_POWER_BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

def fetch_nasa_power_point_data(
    latitude: float = 23.8103,
    longitude: float = 90.4125,
    parameters: list[str] = None,
    start_date: str = "20010101",
    end_date: str = "20251231",
    community: str = "RE"
) -> dict:
    """
    Fetch daily time series point data from NASA POWER API.
    
    Parameters:
        latitude (float): Latitude of the target location.
        longitude (float): Longitude of the target location.
        parameters (list): List of parameter codes (e.g. ['T2M']).
        start_date (str): Start date in YYYYMMDD format.
        end_date (str): End date in YYYYMMDD format.
        community (str): Community code ('RE', 'AG', or 'SB').
        
    Returns:
        dict: Full JSON response from NASA POWER API.
    """
    if parameters is None:
        parameters = ["T2M"]
        
    query_params = {
        "parameters": ",".join(parameters),
        "community": community,
        "longitude": longitude,
        "latitude": latitude,
        "start": start_date,
        "end": end_date,
        "format": "JSON"
    }
    
    print(f"[FETCH] Fetching NASA POWER data for Lat: {latitude}, Lon: {longitude} ({start_date} -> {end_date})...")
    response = requests.get(NASA_POWER_BASE_URL, params=query_params, timeout=60)
    response.raise_for_status()
    print("[SUCCESS] Successfully retrieved data from NASA POWER API!")
    return response.json()


def parse_power_json_to_df(json_data: dict, fill_value: float = -999.0) -> pd.DataFrame:
    """
    Convert NASA POWER API JSON response to a clean pandas DataFrame.
    
    Parameters:
        json_data (dict): NASA POWER API JSON response.
        fill_value (float): Missing value marker in NASA POWER (default: -999.0).
        
    Returns:
        pd.DataFrame: Clean DataFrame indexed by date with proper datatypes.
    """
    properties = json_data.get("properties", {})
    parameter_data = properties.get("parameter", {})
    
    if not parameter_data:
        raise ValueError("No parameter data found in NASA POWER JSON response.")
        
    df = pd.DataFrame(parameter_data)
    
    # Parse date index (format: YYYYMMDD)
    df.index = pd.to_datetime(df.index, format="%Y%m%d")
    df.index.name = "date"
    
    # Clean fill values (replace -999.0 with NaN)
    df.replace(fill_value, pd.NA, inplace=True)
    
    # Convert numeric columns to float64
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        
    return df


def load_or_fetch_dhaka_temperature(
    cache_path: str = "data/dhaka_t2m_2001_2025.csv",
    force_fetch: bool = False
) -> pd.DataFrame:
    """
    Loads Dhaka T2M temperature data from local CSV cache if available,
    otherwise fetches from NASA POWER API and caches it.
    """
    if os.path.exists(cache_path) and not force_fetch:
        print(f"[CACHE] Loading cached data from: {cache_path}")
        df = pd.read_csv(cache_path, index_col="date", parse_dates=True)
        return df
        
    # Fetch from API
    raw_json = fetch_nasa_power_point_data(
        latitude=23.8103,
        longitude=90.4125,
        parameters=["T2M"],
        start_date="20010101",
        end_date="20251231"
    )
    
    # Parse to DataFrame
    df = parse_power_json_to_df(raw_json)
    
    # Ensure directory exists and cache to CSV
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    df.to_csv(cache_path)
    print(f"[SAVED] Saved {len(df)} daily records to cache: {cache_path}")
    
    return df
