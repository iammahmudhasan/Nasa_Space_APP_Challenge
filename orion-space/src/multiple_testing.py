"""
multiple_testing.py
===================
Benjamini-Hochberg (BH) False Discovery Rate (FDR) Multiple-Testing Correction.

Part of Orion Space - NASA Earth System Trend Detective.

Statistical Framework & Methodology:
- Raw p-values are subject to multiple testing inflation when evaluating
  multiple spatial grid cells and calendar months simultaneously.
- Family Definition:
  * For Trends: Testing family is defined per (variable x calendar month),
    comprising m = 34 spatial grid tests across mainland Bangladesh.
    FDR correction was performed within each variable-month spatial testing family,
    rather than across all spatial-month-variable hypotheses globally.
  * For Relationships: Testing family is defined per (variable pair x calendar month),
    comprising m = 34 spatial correlation tests across mainland Bangladesh.
- Statistical Caveat:
  * BH-FDR was applied to each spatial family; the interpretation should
    account for possible spatial dependence among neighboring cells.
- Parametric (OLS / Pearson) and Non-Parametric (Mann-Kendall / Spearman) p-values
  are corrected separately into their respective q-values (adjusted p-values).
- Retains all raw statistics alongside corrected q-values and significance flags
  to maintain complete scientific provenance and reproducibility.
"""

from pathlib import Path
from typing import Optional, Union, List
import numpy as np
import pandas as pd


def adjust_pvalues_bh(p_values: Union[np.ndarray, List[float]]) -> np.ndarray:
    """
    Adjust p-values using the Benjamini-Hochberg (1995) step-up procedure
    to control the False Discovery Rate (FDR).

    Formula:
        For ordered p-values p_(1) <= p_(2) <= ... <= p_(m):
        q_(i) = min_{k >= i} [ min(1, (m / k) * p_(k)) ]

    Parameters
    ----------
    p_values : array-like
        Array or list of raw p-values (in range [0, 1]).

    Returns
    -------
    np.ndarray
        Array of BH-adjusted p-values (q-values) with monotonicity preserved.
    """
    p = np.asarray(p_values, dtype=float)
    if p.size == 0:
        return p

    nan_mask = np.isnan(p)
    valid_p = p[~nan_mask]
    m = len(valid_p)

    if m == 0:
        return p

    try:
        from scipy.stats import false_discovery_control
        q_valid = false_discovery_control(valid_p, method='bh')
    except (ImportError, AttributeError):
        order = np.argsort(valid_p)
        ranks = np.empty(m, dtype=int)
        ranks[order] = np.arange(1, m + 1)

        q_raw = valid_p * float(m) / ranks
        q_raw = np.clip(q_raw, 0.0, 1.0)

        # Enforce step-up monotonicity: cumulative min from the highest rank
        q_sorted = q_raw[order]
        q_sorted_mono = np.minimum.accumulate(q_sorted[::-1])[::-1]

        q_valid = np.empty(m, dtype=float)
        q_valid[order] = q_sorted_mono

    q_out = np.full_like(p, fill_value=np.nan, dtype=float)
    q_out[~nan_mask] = q_valid
    return q_out


def apply_trend_fdr(
    df_trends: pd.DataFrame,
    alpha: float = 0.05
) -> pd.DataFrame:
    """
    Apply Benjamini-Hochberg FDR correction to multi-variable trend dataset.

    Testing Families:
        Grouping by (variable, month_num) -> 34 spatial tests per family.
        Total families = 4 variables * 12 months = 48 families.

    Columns Added:
        - q_value_ols: BH-adjusted p-value for OLS linear regression
        - q_value_mk: BH-adjusted p-value for Mann-Kendall test
        - is_significant_ols_fdr: Boolean flag (q_value_ols < alpha)
        - is_significant_mk_fdr: Boolean flag (q_value_mk < alpha)

    Parameters
    ----------
    df_trends : pd.DataFrame
        DataFrame from bangladesh_multivariable_trends.csv
    alpha : float, default 0.05
        Significance threshold for FDR q-values.

    Returns
    -------
    pd.DataFrame
        DataFrame with FDR-adjusted q-values and significance flags.
    """
    df = df_trends.copy()

    # Pre-allocate new columns
    df["q_value_ols"] = np.nan
    df["q_value_mk"] = np.nan
    df["is_significant_ols_fdr"] = False
    df["is_significant_mk_fdr"] = False

    group_cols = ["variable", "month_num"]
    grouped = df.groupby(group_cols, sort=False)

    for (var, month_n), indices in grouped.groups.items():
        sub = df.loc[indices]

        # Adjust OLS p-values
        if "p_value_ols" in sub.columns:
            p_ols = sub["p_value_ols"].values
        elif "p_value" in sub.columns:
            p_ols = sub["p_value"].values
        else:
            raise KeyError("Neither 'p_value_ols' nor 'p_value' found in trends DataFrame.")

        q_ols = adjust_pvalues_bh(p_ols)
        df.loc[indices, "q_value_ols"] = np.round(q_ols, 6)
        df.loc[indices, "is_significant_ols_fdr"] = q_ols < alpha

        # Adjust Mann-Kendall p-values
        if "p_value_mk" in sub.columns:
            p_mk = sub["p_value_mk"].values
            q_mk = adjust_pvalues_bh(p_mk)
            df.loc[indices, "q_value_mk"] = np.round(q_mk, 6)
            df.loc[indices, "is_significant_mk_fdr"] = q_mk < alpha
        else:
            # Fallback if Mann-Kendall p-value not present
            df.loc[indices, "q_value_mk"] = np.nan
            df.loc[indices, "is_significant_mk_fdr"] = False

    return df


def apply_relationship_fdr(
    df_rel: pd.DataFrame,
    alpha: float = 0.05
) -> pd.DataFrame:
    """
    Apply Benjamini-Hochberg FDR correction to cross-variable relationship dataset.

    Testing Families:
        Grouping by (variable_a, variable_b, month_num) -> 34 spatial correlation tests.
        Total families = 6 pairs * 12 months = 72 families.

    Columns Added:
        - pearson_q: BH-adjusted p-value for Pearson correlation
        - spearman_q: BH-adjusted p-value for Spearman rank correlation
        - pearson_significant_fdr: Boolean flag (pearson_q < alpha)
        - spearman_significant_fdr: Boolean flag (spearman_q < alpha)

    Parameters
    ----------
    df_rel : pd.DataFrame
        DataFrame from bangladesh_variable_relationships.csv
    alpha : float, default 0.05
        Significance threshold for FDR q-values.

    Returns
    -------
    pd.DataFrame
        DataFrame with FDR-adjusted q-values and significance flags.
    """
    df = df_rel.copy()

    # Pre-allocate new columns
    df["pearson_q"] = np.nan
    df["spearman_q"] = np.nan
    df["pearson_significant_fdr"] = False
    df["spearman_significant_fdr"] = False

    group_cols = ["variable_a", "variable_b", "month_num"]
    grouped = df.groupby(group_cols, sort=False)

    for (var_a, var_b, month_n), indices in grouped.groups.items():
        sub = df.loc[indices]

        # Adjust Pearson p-values
        if "pearson_p" in sub.columns:
            p_pearson = sub["pearson_p"].values
            q_pearson = adjust_pvalues_bh(p_pearson)
            df.loc[indices, "pearson_q"] = np.round(q_pearson, 6)
            df.loc[indices, "pearson_significant_fdr"] = q_pearson < alpha

        # Adjust Spearman p-values
        if "spearman_p" in sub.columns:
            p_spearman = sub["spearman_p"].values
            q_spearman = adjust_pvalues_bh(p_spearman)
            df.loc[indices, "spearman_q"] = np.round(q_spearman, 6)
            df.loc[indices, "spearman_significant_fdr"] = q_spearman < alpha

    return df


def run_multiple_testing_correction(
    trends_csv_path: Optional[Union[str, Path]] = None,
    rel_csv_path: Optional[Union[str, Path]] = None,
    output_dir: Optional[Union[str, Path]] = None,
    alpha: float = 0.05
) -> dict:
    """
    Execute Benjamini-Hochberg FDR correction on both trend and relationship datasets.
    Preserves raw CSV files and writes new *_fdr.csv files to both root data/
    and orion-space/data/ directories.

    Returns
    -------
    dict
        Summary audit dictionary with counts of raw vs corrected discoveries.
    """
    base_dir = Path(__file__).resolve().parent.parent.parent  # Workspace root
    data_dir_root = base_dir / "data"
    data_dir_orion = base_dir / "orion-space" / "data"

    # Resolve trend input path
    if trends_csv_path is not None:
        trends_in = Path(trends_csv_path)
    else:
        trends_in = data_dir_root / "bangladesh_multivariable_trends.csv"
        if not trends_in.exists():
            trends_in = data_dir_orion / "bangladesh_multivariable_trends.csv"

    # Resolve relationship input path
    if rel_csv_path is not None:
        rel_in = Path(rel_csv_path)
    else:
        rel_in = data_dir_root / "bangladesh_variable_relationships.csv"
        if not rel_in.exists():
            rel_in = data_dir_orion / "bangladesh_variable_relationships.csv"

    if not trends_in.exists():
        raise FileNotFoundError(f"Trends input CSV not found at: {trends_in}")
    if not rel_in.exists():
        raise FileNotFoundError(f"Relationships input CSV not found at: {rel_in}")

    print(f"\n========================================================")
    print(f"STEP 8: BENJAMINI-HOCHBERG FDR CORRECTION ENGINE")
    print(f"========================================================")
    print(f"Input Trends:        {trends_in}")
    print(f"Input Relationships: {rel_in}")
    print(f"Significance Level:  alpha = {alpha}")

    # Load data
    df_trends_raw = pd.read_csv(trends_in)
    df_rel_raw = pd.read_csv(rel_in)

    print(f"\n[1/4] Processing Trends FDR Correction...")
    print(f"  Total records: {len(df_trends_raw)}")
    n_trend_families = len(df_trends_raw.groupby(["variable", "month_num"]))
    print(f"  Statistical families: {n_trend_families} (each with m=34 spatial tests)")

    df_trends_fdr = apply_trend_fdr(df_trends_raw, alpha=alpha)

    # Trend audit stats
    raw_ols_sig = int(df_trends_fdr["is_significant_ols"].sum())
    fdr_ols_sig = int(df_trends_fdr["is_significant_ols_fdr"].sum())
    raw_mk_sig = int(df_trends_fdr["is_significant_mk"].sum())
    fdr_mk_sig = int(df_trends_fdr["is_significant_mk_fdr"].sum())

    print(f"  Trends Audit:")
    print(f"    - OLS Linear Trend:    Raw sig (p < {alpha}): {raw_ols_sig} | FDR sig (q < {alpha}): {fdr_ols_sig}")
    print(f"    - Mann-Kendall Trend:  Raw sig (p < {alpha}): {raw_mk_sig} | FDR sig (q < {alpha}): {fdr_mk_sig}")

    print(f"\n[2/4] Processing Relationships FDR Correction...")
    print(f"  Total records: {len(df_rel_raw)}")
    n_rel_families = len(df_rel_raw.groupby(["variable_a", "variable_b", "month_num"]))
    print(f"  Statistical families: {n_rel_families} (each with m=34 spatial tests)")

    df_rel_fdr = apply_relationship_fdr(df_rel_raw, alpha=alpha)

    # Relationship audit stats
    raw_p_sig = int(df_rel_fdr["is_pearson_sig"].sum())
    fdr_p_sig = int(df_rel_fdr["pearson_significant_fdr"].sum())
    raw_s_sig = int(df_rel_fdr["is_spearman_sig"].sum())
    fdr_s_sig = int(df_rel_fdr["spearman_significant_fdr"].sum())

    print(f"  Relationships Audit:")
    print(f"    - Pearson Correlation:  Raw sig (p < {alpha}): {raw_p_sig} | FDR sig (q < {alpha}): {fdr_p_sig}")
    print(f"    - Spearman Correlation: Raw sig (p < {alpha}): {raw_s_sig} | FDR sig (q < {alpha}): {fdr_s_sig}")

    # Save destinations (supports custom output_dir or defaults to root and orion-space)
    if output_dir is not None:
        destinations = [(Path(output_dir), f"custom directory ({output_dir})")]
    else:
        destinations = [
            (data_dir_root, "root data/"),
            (data_dir_orion, "orion-space/data/")
        ]

    print(f"\n[3/4] Exporting Corrected Datasets (Preserving Raw Provenance)...")
    for d_path, d_label in destinations:
        d_path.mkdir(parents=True, exist_ok=True)
        t_out = d_path / "bangladesh_multivariable_trends_fdr.csv"
        r_out = d_path / "bangladesh_variable_relationships_fdr.csv"

        df_trends_fdr.to_csv(t_out, index=False)
        df_rel_fdr.to_csv(r_out, index=False)
        print(f"  Saved to {d_label}:")
        print(f"    - {t_out.name} ({len(df_trends_fdr)} rows, {len(df_trends_fdr.columns)} cols)")
        print(f"    - {r_out.name} ({len(df_rel_fdr)} rows, {len(df_rel_fdr.columns)} cols)")

    # Detailed variable-level breakdown
    print(f"\n[4/4] Breakdown by Variable / Pair (Sample Audit):")
    print(f"  --- Trends by Variable (FDR vs Raw OLS) ---")
    for var, grp in df_trends_fdr.groupby("variable"):
        raw_s = grp["is_significant_ols"].sum()
        fdr_s = grp["is_significant_ols_fdr"].sum()
        raw_mk = grp["is_significant_mk"].sum()
        fdr_mk = grp["is_significant_mk_fdr"].sum()
        print(f"    {var:<20}: OLS Raw={raw_s:3d} -> FDR={fdr_s:3d} | MK Raw={raw_mk:3d} -> FDR={fdr_mk:3d}")

    # September T2M specific highlight
    t2m_sep = df_trends_fdr[(df_trends_fdr["variable"] == "T2M") & (df_trends_fdr["month"] == "September")]
    t2m_sep_raw = t2m_sep["is_significant_ols"].sum()
    t2m_sep_fdr = t2m_sep["is_significant_ols_fdr"].sum()
    print(f"\n  Key Query Check: T2M in September (34 cells):")
    print(f"    - Raw OLS significant: {t2m_sep_raw}/34 cells")
    print(f"    - FDR OLS significant: {t2m_sep_fdr} of 34 cells remained significant after Benjamini-Hochberg FDR correction at q < {alpha} (q-values: {t2m_sep['q_value_ols'].min():.4f} - {t2m_sep['q_value_ols'].max():.4f})")

    summary = {
        "trends": {
            "total_records": len(df_trends_fdr),
            "families": n_trend_families,
            "raw_ols_sig": raw_ols_sig,
            "fdr_ols_sig": fdr_ols_sig,
            "raw_mk_sig": raw_mk_sig,
            "fdr_mk_sig": fdr_mk_sig,
        },
        "relationships": {
            "total_records": len(df_rel_fdr),
            "families": n_rel_families,
            "raw_pearson_sig": raw_p_sig,
            "fdr_pearson_sig": fdr_p_sig,
            "raw_spearman_sig": raw_s_sig,
            "fdr_spearman_sig": fdr_s_sig,
        }
    }
    print(f"\nStep 8 BH-FDR Multiple-Testing Correction Completed Successfully.")
    return summary


if __name__ == "__main__":
    run_multiple_testing_correction()
