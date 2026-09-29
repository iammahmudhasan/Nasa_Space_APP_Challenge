"""
Geospatial Boundary Masking Module
Project: Orion Space - NASA Earth System Trend Detective
Target: Bangladesh Administrative Land Boundary Masking
Module: geospatial.py

Responsibilities:
1. Load official Bangladesh country boundary (GeoJSON / Shapefile)
2. Load spatial trends CSV (bounding box grid)
3. Construct Shapely Point geometry for each latitude/longitude coordinate
4. Perform Point-in-Polygon (PIP) intersection test
5. Mask out external points (India, Myanmar, Bay of Bengal offshore)
6. Export filtered dataset to data/bangladesh_t2m_spatial_trends_filtered.csv
"""

import os
import requests
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

GEOBOUNDARIES_BGD_URL = "https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/BGD/ADM0/geoBoundaries-BGD-ADM0.geojson"
DEFAULT_BOUNDARY_PATH = "data/bangladesh_boundary.geojson"
DEFAULT_SPATIAL_CSV = "data/bangladesh_t2m_spatial_trends.csv"
DEFAULT_FILTERED_CSV = "data/bangladesh_t2m_spatial_trends_filtered.csv"


def ensure_bangladesh_boundary(boundary_path: str = DEFAULT_BOUNDARY_PATH) -> gpd.GeoDataFrame:
    """
    Ensures Bangladesh boundary GeoJSON exists locally.
    Downloads the official geoBoundaries ADM0 polygon if not found.
    
    Returns:
        gpd.GeoDataFrame: Boundary GeoDataFrame in EPSG:4326.
    """
    if not os.path.exists(boundary_path):
        print(f"[BOUNDARY] Local boundary file not found. Downloading from geoBoundaries...")
        os.makedirs(os.path.dirname(boundary_path), exist_ok=True)
        response = requests.get(GEOBOUNDARIES_BGD_URL, timeout=45)
        response.raise_for_status()
        with open(boundary_path, "wb") as f:
            f.write(response.content)
        print(f"[BOUNDARY] Downloaded and saved boundary to: {boundary_path}")
    else:
        print(f"[BOUNDARY] Loading boundary from local file: {boundary_path}")
        
    gdf = gpd.read_file(boundary_path)
    if gdf.crs is None:
        gdf.set_crs("EPSG:4326", inplace=True)
    elif gdf.crs.to_string() != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")
        
    return gdf


def filter_points_by_boundary(
    spatial_csv_path: str = DEFAULT_SPATIAL_CSV,
    boundary_path: str = DEFAULT_BOUNDARY_PATH,
    output_filtered_csv: str = DEFAULT_FILTERED_CSV,
    buffer_degree: float = 0.0
) -> pd.DataFrame:
    """
    Applies Point-in-Polygon (PIP) spatial filtering.
    Identifies which NASA grid coordinates lie strictly within Bangladesh.
    
    Parameters:
        spatial_csv_path (str): Path to input spatial CSV containing (latitude, longitude).
        boundary_path (str): Path to Bangladesh boundary GeoJSON.
        output_filtered_csv (str): Path to save filtered CSV.
        buffer_degree (float): Optional buffer distance in degrees for coastal margin inclusion.
        
    Returns:
        pd.DataFrame: Filtered DataFrame containing only points inside Bangladesh.
    """
    if not os.path.exists(spatial_csv_path):
        raise FileNotFoundError(f"Spatial CSV not found at: {spatial_csv_path}. Run spatial_analysis.py first.")
        
    # 1. Load boundary
    boundary_gdf = ensure_bangladesh_boundary(boundary_path)
    boundary_poly = boundary_gdf.union_all()
    if buffer_degree > 0:
        boundary_poly = boundary_poly.buffer(buffer_degree)
        
    # 2. Load spatial trends CSV
    df = pd.read_csv(spatial_csv_path)
    print(f"[DATA] Loaded {len(df)} total grid points from: {spatial_csv_path}")
    
    # 3. Build Point geometries
    geometry = [Point(xy) for xy in zip(df["longitude"], df["latitude"])]
    points_gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    
    # 4. Point-in-Polygon test (contains or intersects)
    df["inside_bangladesh"] = points_gdf.geometry.apply(
        lambda p: bool(boundary_poly.contains(p) or boundary_poly.intersects(p))
    )
    
    # 5. Filter to strictly Bangladesh points
    df_filtered = df[df["inside_bangladesh"]].copy()
    df_filtered.reset_index(drop=True, inplace=True)
    
    # 6. Save filtered CSV
    os.makedirs(os.path.dirname(output_filtered_csv), exist_ok=True)
    df_filtered.to_csv(output_filtered_csv, index=False)
    print(f"[EXPORT] Saved {len(df_filtered)} filtered Bangladesh points to: {output_filtered_csv}")
    
    # Summary report
    n_total = len(df)
    n_inside = len(df_filtered)
    n_outside = n_total - n_inside
    n_sig = df_filtered["is_significant"].sum()
    n_inc = (df_filtered["trend_direction"] == "Increasing").sum()
    n_dec = (df_filtered["trend_direction"] == "Decreasing").sum()
    
    print("\n" + "=" * 70)
    print("GEOSPATIAL BOUNDARY FILTERING REPORT")
    print("=" * 70)
    print(f"Total Bounding Box Grid Points:        {n_total}")
    print(f"Points Masked Out (Outside Country):    {n_outside} ({(n_outside/n_total)*100:.1f}%)")
    print(f"Points Retained (Inside Bangladesh):   {n_inside} ({(n_inside/n_total)*100:.1f}%)")
    print("-" * 70)
    print(f"Inside Bangladesh Points Summary:")
    print(f"  • Increasing Trend:                   {n_inc} ({(n_inc/n_inside)*100:.1f}%)")
    print(f"  • Decreasing Trend:                   {n_dec} ({(n_dec/n_inside)*100:.1f}%)")
    print(f"  • Statistically Significant (p < 0.05): {n_sig} ({(n_sig/n_inside)*100:.1f}%)")
    print(f"  • Mean Decadal Rate:                  {df_filtered['slope_c_per_decade'].mean():+.4f} deg C / decade")
    print("=" * 70)
    
    return df_filtered


if __name__ == "__main__":
    filter_points_by_boundary()
