"""
Scientific Trend Analysis & Statistical Significance Engine
Project: Orion Space - Earth System Trend Detective
Features:
- Time-series temporal aggregation (Daily -> Monthly -> Yearly)
- Parametric Linear Trend (OLS via SciPy)
- Non-Parametric Mann-Kendall Trend Test
- Sen's Slope Estimator (Theil-Sen estimator)
- Statistical significance evaluation (alpha = 0.05)
"""

import numpy as np
import pandas as pd
from scipy import stats

def aggregate_time_series(df: pd.DataFrame, column: str = "T2M") -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Aggregates daily series to monthly mean and yearly mean.
    
    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: (monthly_df, yearly_df)
    """
    # Monthly mean
    monthly_df = df[[column]].resample("ME").mean()
    monthly_df.rename(columns={column: f"{column}_monthly_mean"}, inplace=True)
    
    # Yearly mean
    yearly_df = df[[column]].resample("YE").mean()
    yearly_df.rename(columns={column: f"{column}_yearly_mean"}, inplace=True)
    yearly_df["year"] = yearly_df.index.year
    
    return monthly_df, yearly_df


def compute_linear_trend(years: np.ndarray, values: np.ndarray) -> dict:
    """
    Computes Ordinary Least Squares (OLS) linear regression trend and p-value.
    
    Parameters:
        years (np.ndarray): 1D array of time steps (e.g. years or continuous indices).
        values (np.ndarray): 1D array of observations (e.g. annual mean temperatures).
        
    Returns:
        dict: Slope, intercept, r_value, r_squared, p_value, std_err,
              total_change, percent_change, is_significant.
    """
    mask = ~np.isnan(values)
    x = years[mask]
    y = values[mask]
    
    res = stats.linregress(x, y)
    
    start_val = res.intercept + res.slope * x[0]
    end_val = res.intercept + res.slope * x[-1]
    total_change = end_val - start_val
    pct_change = (total_change / abs(start_val)) * 100 if start_val != 0 else np.nan
    
    return {
        "slope": float(res.slope),
        "intercept": float(res.intercept),
        "r_value": float(res.rvalue),
        "r_squared": float(res.rvalue ** 2),
        "p_value": float(res.pvalue),
        "std_err": float(res.stderr),
        "start_fitted": float(start_val),
        "end_fitted": float(end_val),
        "total_change": float(total_change),
        "pct_change": float(pct_change),
        "is_significant": bool(res.pvalue < 0.05),
        "trend_direction": "Increasing" if res.slope > 0 else ("Decreasing" if res.slope < 0 else "No Trend")
    }


def mann_kendall_test(values: np.ndarray) -> dict:
    """
    Computes the non-parametric Mann-Kendall Trend Test and Sen's Slope Estimator.
    This test does not assume normal distribution and is resilient to extreme weather outliers.
    
    Parameters:
        values (np.ndarray): 1D array of time-ordered observations.
        
    Returns:
        dict: S statistic, var_s, z_score, p_value, sens_slope, is_significant.
    """
    v = np.asarray(values, dtype=float)
    v = v[~np.isnan(v)]
    n = len(v)
    
    if n < 3:
        raise ValueError("Mann-Kendall test requires at least 3 valid observations.")
        
    # Calculate S statistic
    s = 0
    slopes = []
    for k in range(n - 1):
        for j in range(k + 1, n):
            diff = v[j] - v[k]
            s += np.sign(diff)
            slopes.append(diff / (j - k))
            
    # Sen's Slope is the median of all pairwise slopes
    sens_slope = float(np.median(slopes))
    
    # Calculate Variance of S accounting for ties
    unique_vals, counts = np.unique(v, return_counts=True)
    tie_term = np.sum(counts * (counts - 1) * (2 * counts + 5))
    var_s = (n * (n - 1) * (2 * n + 5) - tie_term) / 18.0
    
    # Calculate Z-score
    if s > 0:
        z = (s - 1) / np.sqrt(var_s)
    elif s < 0:
        z = (s + 1) / np.sqrt(var_s)
    else:
        z = 0.0
        
    # Two-tailed p-value from standard normal distribution
    p_value = 2.0 * (1.0 - stats.norm.cdf(abs(z)))
    
    return {
        "s_stat": int(s),
        "var_s": float(var_s),
        "z_score": float(z),
        "p_value": float(p_value),
        "sens_slope": float(sens_slope),
        "is_significant": bool(p_value < 0.05),
        "trend_direction": "Increasing" if s > 0 else ("Decreasing" if s < 0 else "No Trend")
    }


def format_scientific_summary(
    location: str,
    variable: str,
    period: str,
    ols_res: dict,
    mk_res: dict
) -> str:
    """
    Formats the analysis summary table matching NASA challenge criteria.
    """
    summary = f"""
================================================================================
ORION SPACE - NASA EARTH SYSTEM TREND DETECTIVE (PHASE 1)
================================================================================
Location:               {location}
Variable:               {variable}
Period:                 {period}
--------------------------------------------------------------------------------
STATISTICAL FINDINGS:
  - Trend Direction:       {ols_res['trend_direction']}
  - Linear Slope (OLS):    {ols_res['slope']:+.4f} deg C / year  ({ols_res['slope']*10:+.3f} deg C / decade)
  - Sen's Slope (Median):  {mk_res['sens_slope']:+.4f} deg C / year  ({mk_res['sens_slope']*10:+.3f} deg C / decade)
  - Total Change (25-yr):  {ols_res['total_change']:+.2f} deg C
  - Percentage Change:     {ols_res['pct_change']:+.2f} %
  - OLS Model Fit (R^2):   {ols_res['r_squared']:.4f}
  - OLS p-value:           {ols_res['p_value']:.4e}
  - Mann-Kendall p-value:  {mk_res['p_value']:.4e} (Z = {mk_res['z_score']:+.2f})
--------------------------------------------------------------------------------
VERDICT:
  - Statistically Significant (alpha = 0.05): {'YES (p < 0.05)' if (ols_res['is_significant'] or mk_res['is_significant']) else 'NO (p >= 0.05, Not Significant)'}
================================================================================
"""
    return summary
