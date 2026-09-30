"""
Multi-Variable Earth-System Trend Analysis Engine
Project: Orion Space - NASA Earth System Trend Detective
Target: Step 5B - Interconnected Multi-Variable Trend & Co-Occurrence Analysis
File: multivariable_analysis.py

Earth-System Variables Analyzed:
1. T2M               : Air Temperature at 2 Meters (°C)
2. PRECTOTCORR       : Precipitation Corrected (mm/day)
3. GWETTOP           : Top-layer Soil Wetness (0-1 fraction, dimensionless)
4. ALLSKY_SFC_SW_DWN : All-sky Surface Downwelling Solar Irradiance (MJ/m^2/day)

Target Spatial Grid: 34 Bangladesh Mainland Points (Point-in-Polygon Filtered)
Temporal Window:     2001 - 2025 (25 Years, Monthly Resolution)

Output Dataset:
data/bangladesh_multivariable_trends.csv

Core Functions:
1. extract_monthly_series(...)
2. analyze_variable_grid(...)
3. run_multivariable_analysis(...)
"""

import sys
import os
import json
import shutil
import numpy as np
import pandas as pd

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from src.trend_analysis import compute_linear_trend, mann_kendall_test
    from src.multivariable_data_loader import VARIABLE_CONFIGS, find_target_path
except ImportError:
    from trend_analysis import compute_linear_trend, mann_kendall_test
    from multivariable_data_loader import VARIABLE_CONFIGS, find_target_path

MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}


def load_retained_inland_coordinates(filtered_csv_path: str = None) -> list[tuple[float, float]]:
    """
    Loads ordered list of 34 mainland Bangladesh (latitude, longitude) coordinates.
    """
    if filtered_csv_path is None:
        filtered_csv_path = find_target_path("bangladesh_t2m_spatial_trends_filtered.csv")
        
    df = pd.read_csv(filtered_csv_path)
    coords = []
    for _, row in df.iterrows():
        coords.append((round(float(row["latitude"]), 4), round(float(row["longitude"]), 4)))
        
    print(f"[GRID] Loaded {len(coords)} retained Bangladesh mainland grid coordinates.")
    return coords


def extract_monthly_series(
    parameter_dict: dict,
    month_num: int,
    start_year: int = 2001,
    end_year: int = 2025
) -> tuple[np.ndarray, np.ndarray]:
    """
    Core Function 1:
    Extracts 25-year time series for a specific calendar month from NASA POWER parameter dictionary.
    
    Parameters:
        parameter_dict (dict): Dictionary of monthly values (keys formatted as YYYYMM).
        month_num (int): Calendar month (1 to 12).
        start_year (int): First year of observation (default: 2001).
        end_year (int): Last year of observation (default: 2025).
        
    Returns:
        tuple[np.ndarray, np.ndarray]: (years_array, values_array)
    """
    suffix = f"{month_num:02d}"
    years = []
    values = []
    
    for yr in range(start_year, end_year + 1):
        key = f"{yr}{suffix}"
        val = parameter_dict.get(key, None)
        
        # NASA fill value is -999.0
        if val is None or val == -999.0:
            val = np.nan
            
        years.append(yr)
        values.append(float(val) if val is not None else np.nan)
        
    return np.array(years, dtype=int), np.array(values, dtype=float)


def analyze_variable_grid(
    variable_key: str,
    regional_json: dict,
    target_inland_coords: list[tuple[float, float]],
    alpha: float = 0.05
) -> list[dict]:
    """
    Core Function 2:
    Executes parametric (OLS) and non-parametric (Mann-Kendall & Sen's slope)
    trend analysis across all 34 Bangladesh grid cells and all 12 calendar months.
    
    Parameters:
        variable_key (str): Identifier (T2M, PRECTOTCORR, GWETTOP, ALLSKY_SFC_SW_DWN).
        regional_json (dict): GeoJSON data loaded from NASA POWER cache.
        target_inland_coords (list): 34 target (lat, lon) mainland tuples.
        alpha (float): Statistical significance cutoff (default: 0.05).
        
    Returns:
        list[dict]: List of structured trend records for every cell and month.
    """
    cfg = VARIABLE_CONFIGS[variable_key]
    features = regional_json.get("features", [])
    unit_str = cfg["unit"]
    
    # Build spatial lookup dictionary: (round(lat, 4), round(lon, 4)) -> feature
    feature_lookup = {}
    available_coords = []
    for feat in features:
        coords = feat["geometry"]["coordinates"]
        c_lon = round(float(coords[0]), 4)
        c_lat = round(float(coords[1]), 4)
        feature_lookup[(c_lat, c_lon)] = feat
        available_coords.append((c_lat, c_lon))
        
    records = []
    
    for target_lat, target_lon in target_inland_coords:
        # Direct lookup for matching resolution (MERRA-2: T2M, PRECTOTCORR, GWETTOP)
        if (target_lat, target_lon) in feature_lookup:
            target_feat = feature_lookup[(target_lat, target_lon)]
        else:
            # Nearest-neighbor matching for coarser resolution (e.g. 1.0 deg Solar Radiation)
            dists = [
                np.hypot(target_lat - ac[0], target_lon - ac[1])
                for ac in available_coords
            ]
            nearest_idx = int(np.argmin(dists))
            nearest_coord = available_coords[nearest_idx]
            target_feat = feature_lookup[nearest_coord]
            
        p_dict = target_feat["properties"]["parameter"].get(variable_key, {})
        
        # Analyze each of the 12 calendar months
        for m in range(1, 13):
            month_name = MONTH_NAMES[m]
            years, vals = extract_monthly_series(p_dict, month_num=m, start_year=2001, end_year=2025)
            
            # 1. Parametric OLS Regression
            ols_res = compute_linear_trend(years, vals)
            slope_yr = ols_res["slope"]
            slope_dec = slope_yr * 10.0
            p_val_ols = ols_res["p_value"]
            r_sq = ols_res["r_squared"]
            
            # 2. Non-Parametric Mann-Kendall & Sen's Slope
            mk_res = mann_kendall_test(vals)
            sen_yr = mk_res["sens_slope"]
            sen_dec = sen_yr * 10.0
            p_val_mk = mk_res["p_value"]
            
            # 3. Categorization & Significance
            direction = "Increasing" if slope_dec > 0 else ("Decreasing" if slope_dec < 0 else "No Trend")
            is_sig_ols = bool(p_val_ols < alpha)
            is_sig_mk = bool(p_val_mk < alpha)
            
            records.append({
                "latitude": target_lat,
                "longitude": target_lon,
                "variable": variable_key,
                "month": month_name,
                "month_num": m,
                "slope_per_decade": round(slope_dec, 4),
                "p_value": round(p_val_ols, 6),
                "sen_slope_per_decade": round(sen_dec, 4),
                "r_squared": round(r_sq, 4),
                "trend_direction": direction,
                "is_significant": is_sig_ols,
                "p_value_ols": round(p_val_ols, 6),
                "p_value_mk": round(p_val_mk, 6),
                "is_significant_ols": is_sig_ols,
                "is_significant_mk": is_sig_mk,
                "unit": f"{unit_str}/decade"
            })
            
    print(f"[ANALYSIS] {variable_key:<17}: Processed {len(target_inland_coords)} cells x 12 months = {len(records)} records.")
    return records


def run_multivariable_analysis(
    output_csv_path: str = None,
    alpha: float = 0.05
) -> pd.DataFrame:
    """
    Core Function 3:
    Master orchestration for Step 5B.
    Loads raw data for all 4 Earth-system variables, executes grid analysis,
    merges into a unified DataFrame, and exports the final dataset.
    """
    print("\n" + "=" * 80)
    print("ORION SPACE - MULTI-VARIABLE EARTH-SYSTEM ANALYSIS (STEP 5B)")
    print("Variables: T2M, PRECTOTCORR, GWETTOP, ALLSKY_SFC_SW_DWN")
    print("Period:    2001 - 2025 (25 Years)")
    print("=" * 80)
    
    inland_coords = load_retained_inland_coordinates()
    all_records = []
    
    for var_key, cfg in VARIABLE_CONFIGS.items():
        json_path = find_target_path(cfg["raw_filename"])
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Raw dataset for '{var_key}' missing at: {json_path}")
            
        with open(json_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            
        var_records = analyze_variable_grid(
            variable_key=var_key,
            regional_json=raw_data,
            target_inland_coords=inland_coords,
            alpha=alpha
        )
        all_records.extend(var_records)
        
    df_combined = pd.DataFrame(all_records)
    
    # Target output paths
    if output_csv_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_csv_path = os.path.join(script_dir, "..", "data", "bangladesh_multivariable_trends.csv")
        
    output_csv_path = os.path.abspath(output_csv_path)
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    df_combined.to_csv(output_csv_path, index=False)
    print(f"\n[EXPORT] Successfully saved unified multi-variable dataset: {output_csv_path}")
    print(f"         Total records: {len(df_combined)} (34 cells x 12 months x 4 variables)")
    
    # Mirror to root data/
    root_csv_path = os.path.abspath(os.path.join("data", "bangladesh_multivariable_trends.csv"))
    try:
        os.makedirs(os.path.dirname(root_csv_path), exist_ok=True)
        shutil.copyfile(output_csv_path, root_csv_path)
        print(f"[MIRROR] Mirrored dataset to root data directory: {root_csv_path}")
    except Exception:
        pass
        
    # Print Executive Climatological Co-occurrence Summary Table
    print_earth_system_synthesis(df_combined, alpha=alpha)
    
    return df_combined


def print_earth_system_synthesis(df: pd.DataFrame, alpha: float = 0.05):
    """
    Renders a comprehensive Earth-system co-occurrence synthesis table.
    """
    print("\n" + "=" * 90)
    print("EARTH-SYSTEM MULTI-VARIABLE CO-OCCURRENCE SYNTHESIS (NATIONAL AVERAGE BY MONTH)")
    print("=" * 90)
    
    header = (
        f"{'Month':<10} | "
        f"{'T2M (deg C/dec)':<18} | "
        f"{'Precip (mm/d/dec)':<18} | "
        f"{'Soil Moist (/dec)':<18} | "
        f"{'Solar (MJ/m^2/d/dec)':<20}"
    )
    print(header)
    print("-" * 94)
    
    for m in range(1, 13):
        m_name = MONTH_NAMES[m]
        sub = df[df["month_num"] == m]
        
        t2m_rate = sub[sub["variable"] == "T2M"]["slope_per_decade"].mean()
        t2m_sig = (sub[sub["variable"] == "T2M"]["p_value"] < alpha).sum()
        
        precip_rate = sub[sub["variable"] == "PRECTOTCORR"]["slope_per_decade"].mean()
        precip_sig = (sub[sub["variable"] == "PRECTOTCORR"]["p_value"] < alpha).sum()
        
        soil_rate = sub[sub["variable"] == "GWETTOP"]["slope_per_decade"].mean()
        soil_sig = (sub[sub["variable"] == "GWETTOP"]["p_value"] < alpha).sum()
        
        solar_rate = sub[sub["variable"] == "ALLSKY_SFC_SW_DWN"]["slope_per_decade"].mean()
        solar_sig = (sub[sub["variable"] == "ALLSKY_SFC_SW_DWN"]["p_value"] < alpha).sum()
        
        t2m_str = f"{t2m_rate:+6.3f} ({t2m_sig:2d}*)"
        precip_str = f"{precip_rate:+6.3f} ({precip_sig:2d}*)"
        soil_str = f"{soil_rate:+6.4f} ({soil_sig:2d}*)"
        solar_str = f"{solar_rate:+6.3f} ({solar_sig:2d}*)"
        
        print(f"{m_name:<10} | {t2m_str:<14} | {precip_str:<18} | {soil_str:<18} | {solar_str:<20}")
        
    print("=" * 90)
    print("* Notes: (n*) indicates number of Bangladesh grid cells with p < 0.05 (out of 34).")
    print("  Reported values represent observed statistical trend rates and co-occurrences.")
    print("  No causal inference is claimed without dedicated mechanistic simulation.")
    print("=" * 90 + "\n")


if __name__ == "__main__":
    run_multivariable_analysis()
