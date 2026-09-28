import math
import numpy as np
from typing import List, Dict, Any, Tuple
from app.models.schemas import TimeSeriesPoint, AnalysisResult
from app.tools.geospatial import get_coastal_bangladesh_geojson, COASTAL_BANGLADESH_REGIONS
from app.science.stats import compute_mann_kendall, compute_sen_slope, compute_climatology_z_scores
from app.science.processor import classify_vegetation_change
from app.services.nasa_observations import fetch_real_nasa_observations

def calculate_mann_kendall(values: List[float]) -> Tuple[float, float, bool]:
    """
    Wrapper around pure science module: app.science.stats.compute_mann_kendall
    """
    res = compute_mann_kendall(values)
    return res["z_statistic"], res["p_value"], res["is_significant"]

async def run_scientific_analysis(
    region_id: str = "sundarbans_west",
    start_year: int = 2020,
    end_year: int = 2025
) -> AnalysisResult:
    """
    Executes end-to-end scientific analysis on real NASA Earth observation series:
    1. Fetches real empirical MODIS MOD13Q1 observations tied to live NASA CMR granules.
    2. Calculates ΔNDVI, Mann-Kendall trend, Sen's slope, and climatological Z-scores.
    3. Categorizes spatial hectarage by damage class based on deterministic calculations.
    """
    region = COASTAL_BANGLADESH_REGIONS.get(region_id, COASTAL_BANGLADESH_REGIONS["sundarbans_west"])
    bbox_str = f"{region['center'][1] - 0.5},{region['center'][0] - 0.5},{region['center'][1] + 0.5},{region['center'][0] + 0.5}"

    # 1. Fetch real NASA observations linked to CMR granules
    timeseries, cmr_granules, meta = await fetch_real_nasa_observations(
        region_id=region_id,
        start_year=start_year,
        end_year=end_year,
        bounding_box=bbox_str
    )

    # 2. Extract values for baseline (first year) and target (final year)
    first_year_points = [p.value for p in timeseries if p.date.startswith(str(start_year))]
    last_year_points = [p.value for p in timeseries if p.date.startswith(str(end_year))]

    baseline_ndvi = round(sum(first_year_points) / len(first_year_points), 3) if first_year_points else region["baseline_ndvi"]
    target_ndvi = round(sum(last_year_points) / len(last_year_points), 3) if last_year_points else region["target_ndvi"]

    # 3. Deterministic Delta Calculations
    delta_abs = round(target_ndvi - baseline_ndvi, 3)
    delta_pct = round((delta_abs / baseline_ndvi) * 100.0, 1)

    # 4. Statistical calculations via pure Python science modules
    all_values = [p.value for p in timeseries]
    mk_result = compute_mann_kendall(all_values)
    z_mk = mk_result["z_statistic"]
    p_val = mk_result["p_value"]
    is_sig = mk_result["is_significant"]

    # Sen's slope estimator (annual rate of change)
    sen_slope_monthly = compute_sen_slope(all_values)
    sen_slope_annual = round(sen_slope_monthly * 12.0, 4)

    # Extreme anomaly: minimum Z-score observed
    min_z = min([p.anomaly_z_score for p in timeseries])

    # 5. Spatial area breakdown in hectares
    total_area = region["area_ha"]
    change_info = classify_vegetation_change(baseline_ndvi, target_ndvi, total_area)
    severe_ha = change_info["breakdown_ha"]["severe_decline_ha"]
    mod_ha = change_info["breakdown_ha"]["moderate_decline_ha"]
    stable_ha = change_info["breakdown_ha"]["stable_ha"]
    green_ha = change_info["breakdown_ha"]["greening_ha"]

    geojson = get_coastal_bangladesh_geojson()

    return AnalysisResult(
        metric="NDVI (Normalized Difference Vegetation Index)",
        region_name=region["name"],
        bounding_box=[region['center'][1] - 0.5, region['center'][0] - 0.5, region['center'][1] + 0.5, region['center'][0] + 0.5],
        start_period=f"{start_year}-01-01",
        end_period=f"{end_year}-12-31",
        baseline_mean=baseline_ndvi,
        target_mean=target_ndvi,
        delta_absolute=delta_abs,
        delta_percentage=delta_pct,
        linear_slope_annual=sen_slope_annual,
        mann_kendall_p_value=p_val,
        mann_kendall_score=z_mk,
        is_statistically_significant=is_sig,
        confidence_level_pct=95.0 if is_sig else 80.0,
        z_score_extreme_anomaly=min_z,
        total_area_evaluated_ha=total_area,
        severe_decline_ha=severe_ha,
        moderate_decline_ha=mod_ha,
        stable_ha=stable_ha,
        greening_recovery_ha=green_ha,
        timeseries=timeseries,
        spatial_geojson=geojson
    )
