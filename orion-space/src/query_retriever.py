"""
query_retriever.py
==================
Deterministic Scientific Retriever for Orion Space.

Step 9C: Scientific Data Retrieval & Evidence Payload Generation.

Architecture:
- Consumes typed, validated Pydantic queries from query_models.py.
- Queries canonical FDR-corrected datasets:
    * bangladesh_multivariable_trends_fdr.csv
    * bangladesh_variable_relationships_fdr.csv
- Executes purely deterministic filtering and aggregation (no guesswork, zero hallucinations).
- Produces:
    1. Scientific Evidence JSON (verified numbers, counts, locations, claims).
    2. GeoJSON Visualization Payload (points, values, popups, and color scales).
- Formats underflow/finite-precision p-values (p < 1e-6) and enforces standard scientific caveats.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
import pandas as pd

try:
    from .query_models import (
        Variable,
        TrendDirection,
        SignificanceFilter,
        TrendTest,
        CorrelationTest,
        LocationScope,
        DivisionName,
        ExtremesMetric,
        LocationFilter,
        TrendQuery,
        RelationshipQuery,
        LocationProfileQuery,
        SeasonalCycleQuery,
        ComparativeExtremesQuery,
        OrionQuery,
    )
    from .query_parser import parse_natural_query, ParsedQueryResult
except ImportError:
    from query_models import (
        Variable,
        TrendDirection,
        SignificanceFilter,
        TrendTest,
        CorrelationTest,
        LocationScope,
        DivisionName,
        ExtremesMetric,
        LocationFilter,
        TrendQuery,
        RelationshipQuery,
        LocationProfileQuery,
        SeasonalCycleQuery,
        ComparativeExtremesQuery,
        OrionQuery,
    )
    from query_parser import parse_natural_query, ParsedQueryResult


# ==============================================================================
# 1. Constants & Reference Metadata
# ==============================================================================

REFERENCE_CITIES = [
    {"name": "Dhaka", "lat": 23.8103, "lon": 90.4125},
    {"name": "Chattogram", "lat": 22.3569, "lon": 91.7832},
    {"name": "Sylhet", "lat": 24.8949, "lon": 91.8687},
    {"name": "Rajshahi", "lat": 24.3745, "lon": 88.6042},
    {"name": "Khulna", "lat": 22.8456, "lon": 89.5403},
    {"name": "Barishal", "lat": 22.7010, "lon": 90.3535},
    {"name": "Rangpur", "lat": 25.7439, "lon": 89.2752},
    {"name": "Mymensingh", "lat": 24.7471, "lon": 90.4203},
]

VARIABLE_METADATA = {
    "T2M": {
        "name": "Air Temperature at 2 Meters",
        "unit": "°C",
        "rate_unit": "°C/decade",
        "colormap": "RdBu_r",
        "default_domain": [-0.5, 0.5],
    },
    "PRECTOTCORR": {
        "name": "Corrected Precipitation Rate",
        "unit": "mm/day",
        "rate_unit": "mm/day/decade",
        "colormap": "BrBG",
        "default_domain": [-5.0, 5.0],
    },
    "GWETTOP": {
        "name": "Top-layer 0-5cm Soil Wetness",
        "unit": "0-1 fraction",
        "rate_unit": "fraction/decade",
        "colormap": "YlGnBu",
        "default_domain": [-0.08, 0.08],
    },
    "ALLSKY_SFC_SW_DWN": {
        "name": "All-Sky Surface Solar Irradiance",
        "unit": "MJ/m²/day",
        "rate_unit": "MJ/m²/day/decade",
        "colormap": "YlOrRd",
        "default_domain": [-1.5, 1.5],
    },
}

MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}

STANDARD_CAVEATS = [
    "FDR correction was performed within each variable-month spatial testing family (m=34), rather than across all spatial-month-variable hypotheses globally.",
    "BH-FDR was applied to each spatial family; interpretation accounts for possible spatial dependence among neighboring grid cells.",
]


# ==============================================================================
# 2. Data Loading & Helper Utilities
# ==============================================================================

def find_data_file(filename: str) -> Path:
    """Locate dataset file across workspace directories."""
    base_dir = Path(__file__).resolve().parent.parent.parent
    candidates = [
        base_dir / "data" / filename,
        base_dir / "orion-space" / "data" / filename,
    ]
    for c in candidates:
        if c.exists():
            return c
    raise FileNotFoundError(f"Required scientific dataset '{filename}' not found in candidates: {candidates}")


def get_nearest_division(lat: float, lon: float) -> str:
    """Compute nearest administrative division by Euclidean distance."""
    dists = [((lat - c["lat"]) ** 2 + (lon - c["lon"]) ** 2, c["name"]) for c in REFERENCE_CITIES]
    return min(dists, key=lambda x: x[0])[1]


def format_p_value(p: float) -> str:
    """Format very small or underflow p-values cleanly."""
    if np.isnan(p):
        return "NaN"
    if p < 1e-6 or p == 0.0:
        return "p < 1e-6"
    if p < 1e-4:
        return f"{p:.1e}"
    return f"{p:.6f}"


class ScientificDataLoader:
    """Singleton-style cache for FDR scientific datasets."""
    _instance = None

    def __init__(self):
        trends_path = find_data_file("bangladesh_multivariable_trends_fdr.csv")
        rel_path = find_data_file("bangladesh_variable_relationships_fdr.csv")

        self.df_trends = pd.read_csv(trends_path)
        self.df_rel = pd.read_csv(rel_path)

        # Ensure nearest_division is present
        if "nearest_division" not in self.df_trends.columns:
            self.df_trends["nearest_division"] = self.df_trends.apply(
                lambda r: get_nearest_division(r["latitude"], r["longitude"]), axis=1
            )
        if "nearest_division" not in self.df_rel.columns:
            self.df_rel["nearest_division"] = self.df_rel.apply(
                lambda r: get_nearest_division(r["latitude"], r["longitude"]), axis=1
            )

    @classmethod
    def get_loader(cls) -> "ScientificDataLoader":
        if cls._instance is None:
            cls._instance = ScientificDataLoader()
        return cls._instance


# ==============================================================================
# 3. Intent Query Executors
# ==============================================================================

def execute_trend_query(query: TrendQuery, df_trends: pd.DataFrame) -> Dict[str, Any]:
    """Execute spatial trend query on multivariable trends dataset."""
    var_str = query.variable.value
    month_n = query.month
    sub = df_trends[(df_trends["variable"] == var_str) & (df_trends["month_num"] == month_n)].copy()

    total_family_cells = len(sub)

    # 1. Spatial Scope Filtering
    loc = query.location
    if loc.scope == LocationScope.DIVISION and loc.division_name:
        sub = sub[sub["nearest_division"] == loc.division_name.value]
    elif loc.scope == LocationScope.COORDINATE and loc.latitude is not None and loc.longitude is not None:
        # Nearest single cell
        dists = (sub["latitude"] - loc.latitude) ** 2 + (sub["longitude"] - loc.longitude) ** 2
        nearest_idx = dists.idxmin()
        sub = sub.loc[[nearest_idx]]

    evaluated_cells = len(sub)

    # 2. Direction Filtering
    if query.direction == TrendDirection.INCREASING:
        sub_filtered = sub[sub["slope_per_decade"] > 0]
    elif query.direction == TrendDirection.DECREASING:
        sub_filtered = sub[sub["slope_per_decade"] < 0]
    else:
        sub_filtered = sub

    # 3. Significance Filtering
    alpha = query.alpha
    if query.significance_filter == SignificanceFilter.FDR:
        if query.test_type == TrendTest.OLS:
            sub_sig = sub_filtered[sub_filtered["is_significant_ols_fdr"] == True]
        elif query.test_type == TrendTest.MANN_KENDALL:
            sub_sig = sub_filtered[sub_filtered["is_significant_mk_fdr"] == True]
        else:
            sub_sig = sub_filtered[
                (sub_filtered["is_significant_ols_fdr"] == True) &
                (sub_filtered["is_significant_mk_fdr"] == True)
            ]
    elif query.significance_filter == SignificanceFilter.RAW:
        if query.test_type == TrendTest.OLS:
            sub_sig = sub_filtered[sub_filtered["is_significant_ols"] == True]
        elif query.test_type == TrendTest.MANN_KENDALL:
            sub_sig = sub_filtered[sub_filtered["is_significant_mk"] == True]
        else:
            sub_sig = sub_filtered[
                (sub_filtered["is_significant_ols"] == True) &
                (sub_filtered["is_significant_mk"] == True)
            ]
    else:
        sub_sig = sub_filtered

    # 4. Compute Aggregate Statistics
    raw_sig_ols = int(sub["is_significant_ols"].sum())
    fdr_sig_ols = int(sub["is_significant_ols_fdr"].sum())
    raw_sig_mk = int(sub["is_significant_mk"].sum())
    fdr_sig_mk = int(sub["is_significant_mk_fdr"].sum())
    warming_count = int((sub["slope_per_decade"] > 0).sum())
    cooling_count = int((sub["slope_per_decade"] < 0).sum())

    mean_slope = float(sub["slope_per_decade"].mean()) if evaluated_cells > 0 else 0.0
    min_slope = float(sub["slope_per_decade"].min()) if evaluated_cells > 0 else 0.0
    max_slope = float(sub["slope_per_decade"].max()) if evaluated_cells > 0 else 0.0

    min_loc_row = sub.loc[sub["slope_per_decade"].idxmin()] if evaluated_cells > 0 else None
    max_loc_row = sub.loc[sub["slope_per_decade"].idxmax()] if evaluated_cells > 0 else None

    # Precise verified claim
    test_label = "OLS" if query.test_type == TrendTest.OLS else "Mann-Kendall"
    sig_count = fdr_sig_ols if query.test_type == TrendTest.OLS else fdr_sig_mk
    claim = f"{sig_count} of {evaluated_cells} cells remained significant after Benjamini-Hochberg FDR correction at q < {alpha}."

    v_meta = VARIABLE_METADATA.get(var_str, {})

    # Detailed cell records
    cells_list = []
    features_list = []

    for idx, row in sub_sig.iterrows():
        cell_dict = {
            "latitude": float(row["latitude"]),
            "longitude": float(row["longitude"]),
            "nearest_division": str(row["nearest_division"]),
            "slope_per_decade": round(float(row["slope_per_decade"]), 4),
            "p_value_ols": round(float(row["p_value_ols"]), 6),
            "p_value_ols_formatted": format_p_value(float(row["p_value_ols"])),
            "q_value_ols": round(float(row["q_value_ols"]), 6),
            "p_value_mk": round(float(row["p_value_mk"]), 6),
            "p_value_mk_formatted": format_p_value(float(row["p_value_mk"])),
            "q_value_mk": round(float(row["q_value_mk"]), 6),
            "sen_slope_per_decade": round(float(row["sen_slope_per_decade"]), 4),
            "r_squared": round(float(row["r_squared"]), 4),
            "is_significant_ols_fdr": bool(row["is_significant_ols_fdr"]),
            "is_significant_mk_fdr": bool(row["is_significant_mk_fdr"]),
            "trend_direction": str(row["trend_direction"]),
        }
        cells_list.append(cell_dict)

        # GeoJSON Feature for Mapbox / Leaflet
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(row["longitude"]), float(row["latitude"])],
            },
            "properties": {
                "value": round(float(row["slope_per_decade"]), 4),
                "is_significant": bool(row["is_significant_ols_fdr"] if query.test_type == TrendTest.OLS else row["is_significant_mk_fdr"]),
                "q_value": round(float(row["q_value_ols"] if query.test_type == TrendTest.OLS else row["q_value_mk"]), 6),
                "direction": str(row["trend_direction"]),
                "division": str(row["nearest_division"]),
                "popup_html": (
                    f"<b>{row['nearest_division']} ({row['latitude']}°N, {row['longitude']}°E)</b><br>"
                    f"Rate: {row['slope_per_decade']:+.4f} {v_meta.get('rate_unit', '')}<br>"
                    f"FDR q-value: {row['q_value_ols']:.5f} ({'Significant' if row['is_significant_ols_fdr'] else 'Not Significant'})"
                ),
            },
        }
        features_list.append(feature)

    evidence_payload = {
        "evidence_id": f"ev_trend_{var_str}_m{month_n:02d}_{query.test_type.value.lower()}",
        "query_metadata": {
            "intent": "trend",
            "variable": var_str,
            "variable_name": v_meta.get("name", var_str),
            "unit": v_meta.get("unit", ""),
            "rate_unit": v_meta.get("rate_unit", ""),
            "month_num": month_n,
            "month_name": MONTH_NAMES.get(month_n, ""),
            "time_period": "2001 - 2025 (25 Years)",
        },
        "family_scope": {
            "family_definition": "variable_by_month_spatial",
            "family_size_m": total_family_cells,
            "correction_method": "Benjamini-Hochberg (1995) FDR",
            "alpha": alpha,
        },
        "summary_statistics": {
            "total_cells_evaluated": evaluated_cells,
            "matching_cells_count": len(sub_sig),
            "warming_cells_count": warming_count,
            "cooling_cells_count": cooling_count,
            "raw_significant_ols_count": raw_sig_ols,
            "fdr_significant_ols_count": fdr_sig_ols,
            "raw_significant_mk_count": raw_sig_mk,
            "fdr_significant_mk_count": fdr_sig_mk,
            "raw_discoveries_removed_after_fdr": max(0, raw_sig_ols - fdr_sig_ols),
            "national_mean_slope": round(mean_slope, 4),
            "min_slope": round(min_slope, 4),
            "max_slope": round(max_slope, 4),
            "min_slope_location": {
                "latitude": float(min_loc_row["latitude"]) if min_loc_row is not None else None,
                "longitude": float(min_loc_row["longitude"]) if min_loc_row is not None else None,
                "division": str(min_loc_row["nearest_division"]) if min_loc_row is not None else None,
            },
            "max_slope_location": {
                "latitude": float(max_loc_row["latitude"]) if max_loc_row is not None else None,
                "longitude": float(max_loc_row["longitude"]) if max_loc_row is not None else None,
                "division": str(max_loc_row["nearest_division"]) if max_loc_row is not None else None,
            },
            "formatted_significance_claim": claim,
        },
        "cells": cells_list,
        "methodological_caveats": STANDARD_CAVEATS,
    }

    visualization_payload = {
        "visualization_type": "spatial_scatter_map",
        "spatial_layer": {
            "type": "FeatureCollection",
            "features": features_list,
        },
        "color_scale": {
            "palette": v_meta.get("colormap", "RdBu_r"),
            "domain": v_meta.get("default_domain", [-0.5, 0.5]),
            "unit": v_meta.get("rate_unit", ""),
        },
    }

    return {
        "evidence": evidence_payload,
        "visualization": visualization_payload,
    }


def execute_relationship_query(query: RelationshipQuery, df_rel: pd.DataFrame) -> Dict[str, Any]:
    """Execute cross-variable relationship / coupling query on relationships dataset."""
    v1 = query.variable.value
    v2 = query.secondary_variable.value
    month_n = query.month

    # Filter pair in either order
    mask = (
        ((df_rel["variable_a"] == v1) & (df_rel["variable_b"] == v2)) |
        ((df_rel["variable_a"] == v2) & (df_rel["variable_b"] == v1))
    ) & (df_rel["month_num"] == month_n)
    sub = df_rel[mask].copy()

    total_family_cells = len(sub)

    # Spatial filter
    loc = query.location
    if loc.scope == LocationScope.DIVISION and loc.division_name:
        sub = sub[sub["nearest_division"] == loc.division_name.value]
    elif loc.scope == LocationScope.COORDINATE and loc.latitude is not None and loc.longitude is not None:
        dists = (sub["latitude"] - loc.latitude) ** 2 + (sub["longitude"] - loc.longitude) ** 2
        nearest_idx = dists.idxmin()
        sub = sub.loc[[nearest_idx]]

    evaluated_cells = len(sub)
    alpha = query.alpha

    # Filter by significance if requested
    if query.significance_filter == SignificanceFilter.FDR:
        if query.test_type == CorrelationTest.PEARSON:
            sub_sig = sub[sub["pearson_significant_fdr"] == True]
        elif query.test_type == CorrelationTest.SPEARMAN:
            sub_sig = sub[sub["spearman_significant_fdr"] == True]
        else:
            sub_sig = sub[(sub["pearson_significant_fdr"] == True) & (sub["spearman_significant_fdr"] == True)]
    elif query.significance_filter == SignificanceFilter.RAW:
        if query.test_type == CorrelationTest.PEARSON:
            sub_sig = sub[sub["is_pearson_sig"] == True]
        elif query.test_type == CorrelationTest.SPEARMAN:
            sub_sig = sub[sub["is_spearman_sig"] == True]
        else:
            sub_sig = sub[(sub["is_pearson_sig"] == True) & (sub["is_spearman_sig"] == True)]
    else:
        sub_sig = sub

    # Summary metrics
    mean_pearson = float(sub["pearson_r"].mean()) if evaluated_cells > 0 else 0.0
    fdr_sig_pearson = int(sub["pearson_significant_fdr"].sum())
    raw_sig_pearson = int(sub["is_pearson_sig"].sum())
    mean_spearman = float(sub["spearman_rho"].mean()) if evaluated_cells > 0 else 0.0
    fdr_sig_spearman = int(sub["spearman_significant_fdr"].sum())
    raw_sig_spearman = int(sub["is_spearman_sig"].sum())

    # Co-occurrence counts
    co_occur_counts = sub["co_occurrence_type"].value_counts().to_dict()

    test_label = "Pearson" if query.test_type == CorrelationTest.PEARSON else "Spearman"
    sig_count = fdr_sig_pearson if query.test_type == CorrelationTest.PEARSON else fdr_sig_spearman
    claim = f"Observed statistical correlation in {sig_count} of {evaluated_cells} cells remained significant under Benjamini-Hochberg FDR correction (q < {alpha})."

    cells_list = []
    features_list = []

    for idx, row in sub_sig.iterrows():
        cell_dict = {
            "latitude": float(row["latitude"]),
            "longitude": float(row["longitude"]),
            "nearest_division": str(row["nearest_division"]),
            "pearson_r": round(float(row["pearson_r"]), 4),
            "pearson_p": round(float(row["pearson_p"]), 6),
            "pearson_p_formatted": format_p_value(float(row["pearson_p"])),
            "pearson_q": round(float(row["pearson_q"]), 6),
            "spearman_rho": round(float(row["spearman_rho"]), 4),
            "spearman_p": round(float(row["spearman_p"]), 6),
            "spearman_p_formatted": format_p_value(float(row["spearman_p"])),
            "spearman_q": round(float(row["spearman_q"]), 6),
            "is_pearson_sig_fdr": bool(row["pearson_significant_fdr"]),
            "is_spearman_sig_fdr": bool(row["spearman_significant_fdr"]),
            "co_occurrence_type": str(row["co_occurrence_type"]),
        }
        cells_list.append(cell_dict)

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(row["longitude"]), float(row["latitude"])],
            },
            "properties": {
                "value": round(float(row["pearson_r"] if query.test_type == CorrelationTest.PEARSON else row["spearman_rho"]), 4),
                "is_significant": bool(row["pearson_significant_fdr"] if query.test_type == CorrelationTest.PEARSON else row["spearman_significant_fdr"]),
                "q_value": round(float(row["pearson_q"] if query.test_type == CorrelationTest.PEARSON else row["spearman_q"]), 6),
                "division": str(row["nearest_division"]),
                "co_occurrence": str(row["co_occurrence_type"]),
                "popup_html": (
                    f"<b>{row['nearest_division']} Coupling</b><br>"
                    f"{v1} ↔ {v2}<br>"
                    f"Pearson r: {row['pearson_r']:.3f} (q = {row['pearson_q']:.4f})<br>"
                    f"Co-occurrence: {row['co_occurrence_type']}"
                ),
            },
        }
        features_list.append(feature)

    evidence_payload = {
        "evidence_id": f"ev_rel_{v1}_{v2}_m{month_n:02d}",
        "query_metadata": {
            "intent": "relationship",
            "variable_a": v1,
            "variable_b": v2,
            "variable_a_name": VARIABLE_METADATA.get(v1, {}).get("name", v1),
            "variable_b_name": VARIABLE_METADATA.get(v2, {}).get("name", v2),
            "month_num": month_n,
            "month_name": MONTH_NAMES.get(month_n, ""),
            "time_period": "2001 - 2025 (25 Years)",
        },
        "family_scope": {
            "family_definition": "variable_pair_by_month_spatial",
            "family_size_m": total_family_cells,
            "correction_method": "Benjamini-Hochberg (1995) FDR",
            "alpha": alpha,
        },
        "summary_statistics": {
            "total_cells_evaluated": evaluated_cells,
            "matching_cells_count": len(sub_sig),
            "mean_pearson_r": round(mean_pearson, 4),
            "fdr_significant_pearson_count": fdr_sig_pearson,
            "raw_significant_pearson_count": raw_sig_pearson,
            "mean_spearman_rho": round(mean_spearman, 4),
            "fdr_significant_spearman_count": fdr_sig_spearman,
            "raw_significant_spearman_count": raw_sig_spearman,
            "co_occurrence_breakdown": co_occur_counts,
            "formatted_significance_claim": claim,
        },
        "cells": cells_list,
        "methodological_caveats": STANDARD_CAVEATS + [
            "Statistical association and empirical co-occurrence do not imply physical or causal causation without dynamical atmospheric boundary layer modeling."
        ],
    }

    visualization_payload = {
        "visualization_type": "spatial_correlation_map",
        "spatial_layer": {
            "type": "FeatureCollection",
            "features": features_list,
        },
        "color_scale": {
            "palette": "coolwarm",
            "domain": [-1.0, 1.0],
            "unit": "Correlation coefficient",
        },
    }

    return {
        "evidence": evidence_payload,
        "visualization": visualization_payload,
    }


def execute_location_profile_query(
    query: LocationProfileQuery, df_trends: pd.DataFrame, df_rel: pd.DataFrame
) -> Dict[str, Any]:
    """Execute location profile query for a specific division or coordinate."""
    loc = query.location
    if loc.scope == LocationScope.DIVISION and loc.division_name:
        div_name = loc.division_name.value
        t_sub = df_trends[df_trends["nearest_division"] == div_name].copy()
        r_sub = df_rel[df_rel["nearest_division"] == div_name].copy()
        profile_title = f"{div_name} Division Climate Profile"
    elif loc.scope == LocationScope.COORDINATE and loc.latitude is not None and loc.longitude is not None:
        # Find nearest point
        dists = (df_trends["latitude"] - loc.latitude) ** 2 + (df_trends["longitude"] - loc.longitude) ** 2
        nearest_lat = df_trends.loc[dists.idxmin(), "latitude"]
        nearest_lon = df_trends.loc[dists.idxmin(), "longitude"]
        t_sub = df_trends[(df_trends["latitude"] == nearest_lat) & (df_trends["longitude"] == nearest_lon)].copy()
        r_sub = df_rel[(df_rel["latitude"] == nearest_lat) & (df_rel["longitude"] == nearest_lon)].copy()
        profile_title = f"Grid Cell ({nearest_lat}°N, {nearest_lon}°E) Profile"
    else:
        raise ValueError("LocationProfileQuery requires division or coordinate scope.")

    # Optional month filter
    if query.month is not None:
        t_sub = t_sub[t_sub["month_num"] == query.month]
        r_sub = r_sub[r_sub["month_num"] == query.month]

    # Optional variable filter
    if query.variable is not None:
        t_sub = t_sub[t_sub["variable"] == query.variable.value]

    # Aggregate summaries by variable
    var_summaries = {}
    for var_id, grp in t_sub.groupby("variable"):
        var_summaries[var_id] = {
            "variable_name": VARIABLE_METADATA.get(var_id, {}).get("name", var_id),
            "mean_slope": round(float(grp["slope_per_decade"].mean()), 4),
            "rate_unit": VARIABLE_METADATA.get(var_id, {}).get("rate_unit", ""),
            "fdr_significant_count": int(grp["is_significant_ols_fdr"].sum()),
            "total_records": len(grp),
        }

    evidence_payload = {
        "evidence_id": f"ev_profile_{loc.scope.value}",
        "query_metadata": {
            "intent": "location_profile",
            "profile_title": profile_title,
            "location": loc.model_dump(),
            "month_num": query.month,
            "time_period": "2001 - 2025 (25 Years)",
        },
        "variable_trends_summary": var_summaries,
        "sample_trend_records": t_sub.head(12).to_dict(orient="records"),
        "methodological_caveats": STANDARD_CAVEATS,
    }

    visualization_payload = {
        "visualization_type": "location_profile_summary",
        "chart_data": var_summaries,
    }

    return {"evidence": evidence_payload, "visualization": visualization_payload}


def execute_seasonal_cycle_query(query: SeasonalCycleQuery, df_trends: pd.DataFrame) -> Dict[str, Any]:
    """Execute seasonal cycle query across all 12 months for a single variable."""
    var_str = query.variable.value
    sub = df_trends[df_trends["variable"] == var_str].copy()

    # Spatial filter if division/coord specified
    loc = query.location
    if loc.scope == LocationScope.DIVISION and loc.division_name:
        sub = sub[sub["nearest_division"] == loc.division_name.value]
    elif loc.scope == LocationScope.COORDINATE and loc.latitude is not None and loc.longitude is not None:
        dists = (sub["latitude"] - loc.latitude) ** 2 + (sub["longitude"] - loc.longitude) ** 2
        nearest_lat = sub.loc[dists.idxmin(), "latitude"]
        nearest_lon = sub.loc[dists.idxmin(), "longitude"]
        sub = sub[(sub["latitude"] == nearest_lat) & (sub["longitude"] == nearest_lon)]

    monthly_stats = []
    for m in range(1, 13):
        m_sub = sub[sub["month_num"] == m]
        if len(m_sub) == 0:
            continue
        monthly_stats.append({
            "month_num": m,
            "month_name": MONTH_NAMES.get(m, ""),
            "mean_slope": round(float(m_sub["slope_per_decade"].mean()), 4),
            "min_slope": round(float(m_sub["slope_per_decade"].min()), 4),
            "max_slope": round(float(m_sub["slope_per_decade"].max()), 4),
            "fdr_significant_ols_count": int(m_sub["is_significant_ols_fdr"].sum()),
            "fdr_significant_mk_count": int(m_sub["is_significant_mk_fdr"].sum()),
            "total_cells": len(m_sub),
        })

    # Find peak months
    peak_warming_month = max(monthly_stats, key=lambda x: x["mean_slope"])
    peak_cooling_month = min(monthly_stats, key=lambda x: x["mean_slope"])

    evidence_payload = {
        "evidence_id": f"ev_seasonal_{var_str}",
        "query_metadata": {
            "intent": "seasonal_cycle",
            "variable": var_str,
            "variable_name": VARIABLE_METADATA.get(var_str, {}).get("name", var_str),
            "rate_unit": VARIABLE_METADATA.get(var_str, {}).get("rate_unit", ""),
        },
        "seasonal_cycle": monthly_stats,
        "peak_positive_month": peak_warming_month,
        "peak_negative_month": peak_cooling_month,
        "methodological_caveats": STANDARD_CAVEATS,
    }

    visualization_payload = {
        "visualization_type": "seasonal_cycle_chart",
        "chart_data": monthly_stats,
        "x_field": "month_name",
        "y_field": "mean_slope",
    }

    return {"evidence": evidence_payload, "visualization": visualization_payload}


def execute_comparative_extremes_query(
    query: ComparativeExtremesQuery, df_trends: pd.DataFrame
) -> Dict[str, Any]:
    """Execute comparative extremes query across months and locations."""
    var_str = query.variable.value
    sub = df_trends[df_trends["variable"] == var_str].copy()

    loc = query.location
    if loc.scope == LocationScope.DIVISION and loc.division_name:
        sub = sub[sub["nearest_division"] == loc.division_name.value]

    metric = query.metric

    if metric in (ExtremesMetric.MAX_RATE, ExtremesMetric.MAX_WARMING):
        extreme_row = sub.loc[sub["slope_per_decade"].idxmax()]
        title = f"Maximum Positive Trend Rate for {var_str}"
    elif metric in (ExtremesMetric.MIN_RATE, ExtremesMetric.MAX_COOLING):
        extreme_row = sub.loc[sub["slope_per_decade"].idxmin()]
        title = f"Maximum Negative Trend Rate for {var_str}"
    else:
        # Highest significance (lowest q-value)
        extreme_row = sub.loc[sub["q_value_ols"].idxmin()]
        title = f"Highest Significance Point for {var_str}"

    extreme_dict = {
        "month_num": int(extreme_row["month_num"]),
        "month_name": str(extreme_row["month"]),
        "latitude": float(extreme_row["latitude"]),
        "longitude": float(extreme_row["longitude"]),
        "nearest_division": str(extreme_row["nearest_division"]),
        "slope_per_decade": round(float(extreme_row["slope_per_decade"]), 4),
        "q_value_ols": round(float(extreme_row["q_value_ols"]), 6),
        "is_significant_ols_fdr": bool(extreme_row["is_significant_ols_fdr"]),
        "rate_unit": str(extreme_row["unit"]),
    }

    evidence_payload = {
        "evidence_id": f"ev_extreme_{var_str}_{metric.value}",
        "query_metadata": {
            "intent": "comparative_extremes",
            "metric": metric.value,
            "variable": var_str,
            "title": title,
        },
        "extreme_record": extreme_dict,
        "methodological_caveats": STANDARD_CAVEATS,
    }

    visualization_payload = {
        "visualization_type": "extreme_point_highlight",
        "record": extreme_dict,
    }

    return {"evidence": evidence_payload, "visualization": visualization_payload}


# ==============================================================================
# 4. Universal Retriever Interface
# ==============================================================================

def retrieve_scientific_evidence(query: OrionQuery) -> Dict[str, Any]:
    """
    Universal retrieval entry point for any validated OrionQuery model.

    Parameters
    ----------
    query : OrionQuery
        A validated instance of TrendQuery, RelationshipQuery, etc.

    Returns
    -------
    dict
        Dictionary containing 'evidence' and 'visualization' payloads.
    """
    loader = ScientificDataLoader.get_loader()

    if isinstance(query, TrendQuery):
        return execute_trend_query(query, loader.df_trends)
    elif isinstance(query, RelationshipQuery):
        return execute_relationship_query(query, loader.df_rel)
    elif isinstance(query, LocationProfileQuery):
        return execute_location_profile_query(query, loader.df_trends, loader.df_rel)
    elif isinstance(query, SeasonalCycleQuery):
        return execute_seasonal_cycle_query(query, loader.df_trends)
    elif isinstance(query, ComparativeExtremesQuery):
        return execute_comparative_extremes_query(query, loader.df_trends)
    else:
        raise TypeError(f"Unknown query model type: {type(query)}")


def query_and_retrieve(
    question: str,
    override_filters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    End-to-end pipeline: natural language question -> parser -> deterministic retriever.

    Parameters
    ----------
    question : str
        User's natural language question.
    override_filters : dict, optional
        Explicit overrides from frontend forms.

    Returns
    -------
    dict
        Combined response containing query metadata, evidence payload, and visualization payload.
    """
    parsed = parse_natural_query(question, override_filters=override_filters)
    result = retrieve_scientific_evidence(parsed.query_object)

    return {
        "status": "success",
        "parsed_query": {
            "raw_question": parsed.raw_question,
            "intent": parsed.intent,
            "structured_query": parsed.query_object.model_dump(),
            "confidence": parsed.confidence,
        },
        "evidence": result["evidence"],
        "visualization": result["visualization"],
    }


# ==============================================================================
# Self-Test Validation Suite
# ==============================================================================

if __name__ == "__main__":
    print("Testing Orion Space Deterministic Scientific Retriever...")

    # Test 1: Trend Query (September T2M Warming)
    q1 = "Which areas in Bangladesh had significant temperature increases in September?"
    res1 = query_and_retrieve(q1)
    ev1 = res1["evidence"]
    stats1 = ev1["summary_statistics"]
    assert ev1["query_metadata"]["variable"] == "T2M"
    assert ev1["query_metadata"]["month_num"] == 9
    assert stats1["total_cells_evaluated"] == 34
    assert stats1["fdr_significant_ols_count"] == 33
    assert stats1["max_slope"] == 0.4214
    assert stats1["max_slope_location"]["division"] == "Sylhet"
    assert "33 of 34 cells remained significant" in stats1["formatted_significance_claim"]
    print("  [PASS] Test 1: September T2M warming evidence verified against FDR dataset.")

    # Test 2: Relationship Query (T2M vs GWETTOP in May)
    q2 = "Is temperature correlated with soil wetness in May?"
    res2 = query_and_retrieve(q2)
    ev2 = res2["evidence"]
    assert ev2["query_metadata"]["variable_a"] == "T2M"
    assert ev2["query_metadata"]["variable_b"] == "GWETTOP"
    assert ev2["query_metadata"]["month_num"] == 5
    assert ev2["summary_statistics"]["total_cells_evaluated"] == 34
    print("  [PASS] Test 2: Temperature vs Soil Wetness relationship evidence verified.")

    # Test 3: Location Profile (Sylhet Division)
    q3 = "Show climate profile for Sylhet division"
    res3 = query_and_retrieve(q3)
    ev3 = res3["evidence"]
    assert "Sylhet" in ev3["query_metadata"]["profile_title"]
    assert "T2M" in ev3["variable_trends_summary"]
    print("  [PASS] Test 3: Sylhet location profile evidence verified.")

    # Test 4: Seasonal Cycle (Precipitation across months)
    q4 = "How does rainfall trend vary across months in Bangladesh?"
    res4 = query_and_retrieve(q4)
    ev4 = res4["evidence"]
    assert len(ev4["seasonal_cycle"]) == 12
    assert ev4["query_metadata"]["variable"] == "PRECTOTCORR"
    print("  [PASS] Test 4: 12-month precipitation seasonal cycle verified.")

    # Test 5: Comparative Extremes (Strongest warming rate)
    q5 = "Which month has the strongest warming rate?"
    res5 = query_and_retrieve(q5)
    ev5 = res5["evidence"]
    assert ev5["extreme_record"]["slope_per_decade"] > 0
    print(f"  [PASS] Test 5: Comparative extreme point identified: {ev5['extreme_record']['month_name']} in {ev5['extreme_record']['nearest_division']} ({ev5['extreme_record']['slope_per_decade']:+.4f} °C/decade).")

    print("\nAll Orion Space Scientific Retriever tests passed with 100% verification!")
