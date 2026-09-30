"""
Cross-Variable Relationship & Co-Occurrence Analysis Engine
Project: Orion Space - NASA Earth System Trend Detective
Target: Step 6 - Inter-Variable Coupling, Correlation, and Trend Co-Occurrence
File: relationship_analysis.py

Evaluated Variable Pairs:
1. T2M ↔ PRECTOTCORR       : Thermal - Precipitation Coupling
2. T2M ↔ GWETTOP           : Thermal - Soil Moisture Coupling (Evaporative Feedback)
3. T2M ↔ ALLSKY_SFC_SW_DWN : Thermal - Radiative Energy Coupling
4. PRECTOTCORR ↔ GWETTOP   : Hydro-climate - Land Surface Wetness Coupling
5. PRECTOTCORR ↔ ALLSKY_SFC_SW_DWN : Cloud/Precipitation - Radiative Shading Coupling
6. GWETTOP ↔ ALLSKY_SFC_SW_DWN     : Soil Moisture - Radiation Energy Coupling

Target Grid: 34 Retained Bangladesh Mainland Coordinates
Temporal Window: 2001 - 2025 (25 Paired Observations per Calendar Month)

Output:
data/bangladesh_variable_relationships.csv
"""

import sys
import os
import json
import shutil
import numpy as np
import pandas as pd
from scipy import stats

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from src.multivariable_data_loader import VARIABLE_CONFIGS, find_target_path
    from src.multivariable_analysis import load_retained_inland_coordinates, extract_monthly_series
except ImportError:
    from multivariable_data_loader import VARIABLE_CONFIGS, find_target_path
    from multivariable_analysis import load_retained_inland_coordinates, extract_monthly_series

MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}

VARIABLE_PAIRS = [
    ("T2M", "PRECTOTCORR"),
    ("T2M", "GWETTOP"),
    ("T2M", "ALLSKY_SFC_SW_DWN"),
    ("PRECTOTCORR", "GWETTOP"),
    ("PRECTOTCORR", "ALLSKY_SFC_SW_DWN"),
    ("GWETTOP", "ALLSKY_SFC_SW_DWN"),
]


def load_all_raw_datasets() -> dict[str, dict]:
    """
    Loads raw GeoJSON datasets for all 4 Earth-system variables from cache.
    """
    datasets = {}
    for var_key, cfg in VARIABLE_CONFIGS.items():
        json_path = find_target_path(cfg["raw_filename"])
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Raw dataset for '{var_key}' missing at: {json_path}")
        with open(json_path, "r", encoding="utf-8") as f:
            datasets[var_key] = json.load(f)
    return datasets


def build_spatial_feature_lookup(regional_json: dict) -> tuple[dict, list[tuple[float, float]]]:
    """
    Builds coordinate lookup dictionary for a GeoJSON feature collection.
    """
    lookup = {}
    coords = []
    for feat in regional_json.get("features", []):
        c = feat["geometry"]["coordinates"]
        c_lon = round(float(c[0]), 4)
        c_lat = round(float(c[1]), 4)
        lookup[(c_lat, c_lon)] = feat
        coords.append((c_lat, c_lon))
    return lookup, coords


def get_feature_for_coordinate(
    target_lat: float,
    target_lon: float,
    lookup: dict,
    available_coords: list[tuple[float, float]]
) -> dict:
    """
    Retrieves feature matching exact coordinate or nearest neighbor.
    """
    if (target_lat, target_lon) in lookup:
        return lookup[(target_lat, target_lon)]
        
    # Nearest neighbor fallback (used for 1.0 deg solar radiation)
    dists = [np.hypot(target_lat - ac[0], target_lon - ac[1]) for ac in available_coords]
    min_idx = int(np.argmin(dists))
    return lookup[available_coords[min_idx]]


def load_trend_slopes_lookup(multivar_csv_path: str = None) -> dict[tuple[float, float, str, int], float]:
    """
    Loads pre-calculated slopes from Step 5B dataset to evaluate trend co-occurrence.
    """
    if multivar_csv_path is None:
        multivar_csv_path = find_target_path("bangladesh_multivariable_trends.csv")
        
    slope_lookup = {}
    if os.path.exists(multivar_csv_path):
        df_trends = pd.read_csv(multivar_csv_path)
        for _, row in df_trends.iterrows():
            key = (
                round(float(row["latitude"]), 4),
                round(float(row["longitude"]), 4),
                str(row["variable"]),
                int(row["month_num"])
            )
            slope_lookup[key] = float(row["slope_per_decade"])
    return slope_lookup


def compute_cross_variable_relationships(
    alpha: float = 0.05
) -> pd.DataFrame:
    """
    Core Function:
    Calculates Pearson and Spearman correlations across all 34 grid points,
    12 calendar months, and 6 variable pairs over the 2001-2025 time-series.
    
    Returns:
        pd.DataFrame: 2,448 structured relationship records.
    """
    inland_coords = load_retained_inland_coordinates()
    raw_datasets = load_all_raw_datasets()
    slope_lookup = load_trend_slopes_lookup()
    
    # Pre-build coordinate lookup per variable
    lookups = {}
    avail_coords = {}
    for var_key, data in raw_datasets.items():
        l_dict, c_list = build_spatial_feature_lookup(data)
        lookups[var_key] = l_dict
        avail_coords[var_key] = c_list
        
    records = []
    
    for lat, lon in inland_coords:
        # Pre-extract features for all 4 variables at this location
        feats = {}
        param_dicts = {}
        for var_key in VARIABLE_CONFIGS.keys():
            feat = get_feature_for_coordinate(lat, lon, lookups[var_key], avail_coords[var_key])
            feats[var_key] = feat
            param_dicts[var_key] = feat["properties"]["parameter"].get(var_key, {})
            
        for m in range(1, 13):
            month_name = MONTH_NAMES[m]
            
            # Extract 2001-2025 time series for all 4 variables
            series = {}
            for var_key in VARIABLE_CONFIGS.keys():
                _, vals = extract_monthly_series(param_dicts[var_key], month_num=m, start_year=2001, end_year=2025)
                series[var_key] = vals
                
            # Compute correlations for all 6 variable pairs
            for var_a, var_b in VARIABLE_PAIRS:
                vals_a = series[var_a]
                vals_b = series[var_b]
                
                # Pearson Linear Correlation
                r_val, p_pearson = stats.pearsonr(vals_a, vals_b)
                
                # Spearman Rank Correlation (Non-parametric)
                rho_val, p_spearman = stats.spearmanr(vals_a, vals_b)
                
                # Trend Co-occurrence assessment
                slope_a = slope_lookup.get((lat, lon, var_a, m), 0.0)
                slope_b = slope_lookup.get((lat, lon, var_b, m), 0.0)
                
                if slope_a > 0 and slope_b > 0:
                    co_occur = "Both Increasing"
                elif slope_a < 0 and slope_b < 0:
                    co_occur = "Both Decreasing"
                else:
                    co_occur = "Opposite Directions"
                    
                records.append({
                    "latitude": lat,
                    "longitude": lon,
                    "month": month_name,
                    "month_num": m,
                    "variable_a": var_a,
                    "variable_b": var_b,
                    "pearson_r": round(float(r_val), 4),
                    "pearson_p": round(float(p_pearson), 6),
                    "spearman_rho": round(float(rho_val), 4),
                    "spearman_p": round(float(p_spearman), 6),
                    "is_pearson_sig": bool(p_pearson < alpha),
                    "is_spearman_sig": bool(p_spearman < alpha),
                    "trend_a_slope": round(float(slope_a), 4),
                    "trend_b_slope": round(float(slope_b), 4),
                    "co_occurrence_type": co_occur
                })
                
    df_rel = pd.DataFrame(records)
    print(f"[SUCCESS] Calculated relationships across {len(inland_coords)} cells x 12 months x {len(VARIABLE_PAIRS)} pairs = {len(df_rel)} records.")
    return df_rel


def generate_relationship_synthesis(df_rel: pd.DataFrame, alpha: float = 0.05):
    """
    Renders an executive climatological synthesis table of cross-variable coupling.
    """
    print("\n" + "=" * 94)
    print("EARTH-SYSTEM CROSS-VARIABLE RELATIONSHIP SYNTHESIS (NATIONAL MEAN PEARSON R)")
    print("=" * 94)
    
    header = (
        f"{'Month':<10} | "
        f"{'T2M-Precip':<12} | "
        f"{'T2M-Soil':<12} | "
        f"{'T2M-Solar':<12} | "
        f"{'Precip-Soil':<13} | "
        f"{'Precip-Solar':<13} | "
        f"{'Soil-Solar':<12}"
    )
    print(header)
    print("-" * 94)
    
    for m in range(1, 13):
        m_name = MONTH_NAMES[m]
        sub_m = df_rel[df_rel["month_num"] == m]
        
        pair_strs = []
        for v_a, v_b in VARIABLE_PAIRS:
            sub_pair = sub_m[(sub_m["variable_a"] == v_a) & (sub_m["variable_b"] == v_b)]
            mean_r = sub_pair["pearson_r"].mean()
            sig_cnt = (sub_pair["pearson_p"] < alpha).sum()
            pair_strs.append(f"{mean_r:+5.2f} ({sig_cnt:2d}*)")
            
        print(f"{m_name:<10} | " + " | ".join(pair_strs))
        
    print("=" * 94)
    print("* Notes: (n*) indicates number of Bangladesh grid cells with Pearson p < 0.05 (out of 34).")
    print("  Reported values represent observed empirical correlations over 25 paired years (2001-2025).")
    print("  No causal mechanisms are claimed without full hydrodynamic modeling.")
    print("=" * 94 + "\n")


def run_relationship_analysis(
    output_csv_path: str = None,
    alpha: float = 0.05
) -> pd.DataFrame:
    """
    Master pipeline execution for Step 6.
    """
    print("\n" + "=" * 80)
    print("ORION SPACE - CROSS-VARIABLE RELATIONSHIP ENGINE (STEP 6)")
    print("Variable Pairs: 6 Interconnected Earth-System Combinations")
    print("Period:         2001 - 2025 (25 Paired Observations / Month)")
    print("=" * 80)
    
    df_rel = compute_cross_variable_relationships(alpha=alpha)
    
    # Target output paths
    if output_csv_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_csv_path = os.path.join(script_dir, "..", "data", "bangladesh_variable_relationships.csv")
        
    output_csv_path = os.path.abspath(output_csv_path)
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    df_rel.to_csv(output_csv_path, index=False)
    print(f"\n[EXPORT] Successfully saved cross-variable relationship dataset: {output_csv_path}")
    print(f"         Total records: {len(df_rel)} (34 cells x 12 months x 6 pairs)")
    
    # Mirror to root data/
    root_csv_path = os.path.abspath(os.path.join("data", "bangladesh_variable_relationships.csv"))
    try:
        os.makedirs(os.path.dirname(root_csv_path), exist_ok=True)
        shutil.copyfile(output_csv_path, root_csv_path)
        print(f"[MIRROR] Mirrored relationship dataset to root data directory: {root_csv_path}")
    except Exception:
        pass
        
    # Print Executive Climatological Synthesis Table
    generate_relationship_synthesis(df_rel, alpha=alpha)
    
    return df_rel


if __name__ == "__main__":
    run_relationship_analysis()
