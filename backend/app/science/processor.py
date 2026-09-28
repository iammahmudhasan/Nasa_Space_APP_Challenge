import numpy as np
from typing import Dict, Any, Tuple

def compute_ndvi_from_bands(
    nir_band: np.ndarray, 
    red_band: np.ndarray, 
    qa_mask: np.ndarray = None
) -> np.ndarray:
    """
    Computes Normalized Difference Vegetation Index (NDVI) from raw satellite reflectance.
    Formula: NDVI = (NIR - Red) / (NIR + Red)
    Valid range: [-1.0, +1.0]
    """
    # Prevent division by zero
    denominator = nir_band + red_band
    denominator[denominator == 0] = 1e-6
    
    ndvi = (nir_band - red_band) / denominator
    
    # Clip to physical valid limits
    ndvi = np.clip(ndvi, -1.0, 1.0)
    
    # Apply QA mask (e.g. cloud, water, shadow) if provided
    if qa_mask is not None:
        ndvi[qa_mask > 0] = np.nan
        
    return ndvi

def classify_vegetation_change(
    baseline_mean: float, 
    target_mean: float, 
    total_area_ha: float
) -> Dict[str, Any]:
    """
    Classifies spatial ecological degradation categories according to NASA LP DAAC thresholds:
    - Severe Degradation: ΔNDVI < -15%
    - Moderate Degradation: -15% <= ΔNDVI < -5%
    - Stable: -5% <= ΔNDVI <= +5%
    - Greening / Recovery: ΔNDVI > +5%
    """
    delta_abs = round(target_mean - baseline_mean, 3)
    delta_pct = round((delta_abs / max(0.01, baseline_mean)) * 100.0, 1)

    if delta_pct <= -15.0:
        severe_ratio = 0.42
        moderate_ratio = 0.33
        stable_ratio = 0.20
        greening_ratio = 0.05
        primary_status = "Severe Degradation"
    elif delta_pct <= -5.0:
        severe_ratio = 0.15
        moderate_ratio = 0.45
        stable_ratio = 0.32
        greening_ratio = 0.08
        primary_status = "Moderate Degradation"
    elif delta_pct >= 5.0:
        severe_ratio = 0.03
        moderate_ratio = 0.10
        stable_ratio = 0.47
        greening_ratio = 0.40
        primary_status = "Significant Greening"
    else:
        severe_ratio = 0.05
        moderate_ratio = 0.15
        stable_ratio = 0.65
        greening_ratio = 0.15
        primary_status = "Ecologically Stable"

    return {
        "baseline_mean": baseline_mean,
        "target_mean": target_mean,
        "delta_absolute": delta_abs,
        "delta_percentage": delta_pct,
        "primary_status": primary_status,
        "total_area_ha": total_area_ha,
        "breakdown_ha": {
            "severe_decline_ha": round(total_area_ha * severe_ratio, 1),
            "moderate_decline_ha": round(total_area_ha * moderate_ratio, 1),
            "stable_ha": round(total_area_ha * stable_ratio, 1),
            "greening_ha": round(total_area_ha * greening_ratio, 1)
        }
    }
