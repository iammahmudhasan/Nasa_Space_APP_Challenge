"""
Spatial Visualization Engine for Bangladesh Climate Trends
Project: Orion Space - NASA Earth System Trend Detective
Target: Publication-grade Scientific Trend Map
File: spatial_visualization.py

Responsibilities:
1. Load retained Bangladesh grid points (from filtered CSV)
2. Load official country polygon boundary (GeoJSON)
3. Plot cartographic base with country outline and reference cities
4. Map decadal rate of change (°C / decade) using centered diverging colormap
5. Map trend direction using distinct geometric markers (^ for Increasing, v for Decreasing)
6. Scale marker size proportional to decadal trend magnitude
7. Highlight and test statistical significance (p < 0.05)
8. Export high-resolution 300 DPI publication PNG to data/bangladesh_t2m_trend_map.png
"""

import os
import shutil
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.lines import Line2D


def find_data_file(filename: str) -> str:
    """
    Search for a data file across common project locations:
    1. ./data/<filename>
    2. ./orion-space/data/<filename>
    3. ../data/<filename> relative to this script
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join("data", filename),
        os.path.join("orion-space", "data", filename),
        os.path.join(script_dir, "..", "data", filename),
        os.path.join(script_dir, "..", "..", "data", filename),
    ]
    for path in candidates:
        if os.path.exists(path):
            return os.path.abspath(path)
    # Default fallback
    return os.path.abspath(candidates[1])


# Reference administrative divisional centers for geographical orientation
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


def plot_bangladesh_trend_map(
    filtered_csv_path: str = None,
    boundary_path: str = None,
    output_png_path: str = None,
    dpi: int = 300,
    alpha_significance: float = 0.05
) -> str:
    """
    Renders and exports the official Bangladesh Temperature Trend Map.
    
    Parameters:
        filtered_csv_path (str): CSV of points inside Bangladesh boundary.
        boundary_path (str): GeoJSON of country polygon.
        output_png_path (str): Destination path for the high-res PNG.
        dpi (int): Image resolution (default: 300).
        alpha_significance (float): Statistical significance cutoff (default: 0.05).
        
    Returns:
        str: Absolute path to the generated map image.
    """
    if filtered_csv_path is None:
        filtered_csv_path = find_data_file("bangladesh_t2m_spatial_trends_filtered.csv")
    if boundary_path is None:
        boundary_path = find_data_file("bangladesh_boundary.geojson")
    if output_png_path is None:
        # Default destination in orion-space/data
        output_png_path = os.path.join(
            os.path.dirname(filtered_csv_path), "bangladesh_t2m_trend_map.png"
        )

    if not os.path.exists(filtered_csv_path):
        raise FileNotFoundError(f"Filtered CSV not found at: {filtered_csv_path}")
    if not os.path.exists(boundary_path):
        raise FileNotFoundError(f"Boundary GeoJSON not found at: {boundary_path}")

    # 1. Load data
    df = pd.read_csv(filtered_csv_path)
    boundary_gdf = gpd.read_file(boundary_path)
    if boundary_gdf.crs != "EPSG:4326":
        boundary_gdf = boundary_gdf.to_crs("EPSG:4326")

    # 2. Setup Figure & Axes
    fig, ax = plt.subplots(figsize=(11.5, 12.5), dpi=dpi)
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f1f5f9")  # Subtle background for ocean/surrounding territory

    # 3. Draw Bangladesh Landmass
    boundary_gdf.plot(
        ax=ax,
        color="#ffffff",
        edgecolor="#1e293b",
        linewidth=1.6,
        zorder=2,
        label="National Boundary"
    )

    # 4. Color Scale Setup (Two-Slope Diverging around 0.0 °C/decade)
    rates = df["slope_c_per_decade"].values
    v_max = max(abs(rates.min()), abs(rates.max()), 0.18)
    norm = mcolors.TwoSlopeNorm(vmin=-v_max, vcenter=0.0, vmax=v_max)
    cmap = plt.cm.RdBu_r  # Deep Blue (Cooling) -> White/Neutral -> Deep Red (Warming)

    # 5. Marker Size Scaling based on magnitude of trend
    # Larger absolute trend = visibly larger marker
    abs_rates = np.abs(rates)
    sizes = 120 + 350 * (abs_rates / v_max)

    # 6. Partition by Direction and Statistical Significance
    df["calculated_size"] = sizes
    df["sig_flag"] = df["p_value"] < alpha_significance

    df_inc = df[df["slope_c_per_decade"] >= 0]
    df_dec = df[df["slope_c_per_decade"] < 0]
    df_sig = df[df["sig_flag"]]

    # 7. Plot Increasing Trends (Upward Triangle ^)
    sc_inc = ax.scatter(
        df_inc["longitude"],
        df_inc["latitude"],
        c=df_inc["slope_c_per_decade"],
        cmap=cmap,
        norm=norm,
        s=df_inc["calculated_size"],
        marker="^",
        edgecolor="#1e293b",
        linewidth=1.2,
        alpha=0.92,
        zorder=4,
        label=f"Increasing Trend (n={len(df_inc)})"
    )

    # 8. Plot Decreasing Trends (Downward Triangle v)
    sc_dec = ax.scatter(
        df_dec["longitude"],
        df_dec["latitude"],
        c=df_dec["slope_c_per_decade"],
        cmap=cmap,
        norm=norm,
        s=df_dec["calculated_size"],
        marker="v",
        edgecolor="#1e293b",
        linewidth=1.2,
        alpha=0.92,
        zorder=4,
        label=f"Decreasing Trend (n={len(df_dec)})"
    )

    # 9. Highlight Statistically Significant Points (p < 0.05) if any
    if len(df_sig) > 0:
        ax.scatter(
            df_sig["longitude"],
            df_sig["latitude"],
            s=df_sig["calculated_size"] + 80,
            marker="o",
            facecolors="none",
            edgecolors="#fbbf24",
            linewidth=2.5,
            zorder=5,
            label=f"Significant (p < {alpha_significance})*"
        )

    # 10. Annotate Each Grid Point with its Trend Rate (°C/decade)
    for _, row in df.iterrows():
        lat = row["latitude"]
        lon = row["longitude"]
        rate = row["slope_c_per_decade"]
        is_sig = row["sig_flag"]

        sig_mark = "*" if is_sig else ""
        label_text = f"{rate:+.2f}{sig_mark}"

        # Place label based on triangle direction so it doesn't touch the tip
        if rate >= 0:
            # Upward triangle: place label below flat base
            y_offset = -17
        else:
            # Downward triangle: place label above flat top base
            y_offset = 12

        ax.annotate(
            label_text,
            (lon, lat),
            textcoords="offset points",
            xytext=(0, y_offset),
            ha="center",
            va="center",
            fontsize=7.2,
            fontweight="bold" if is_sig else "normal",
            color="#0f172a",
            bbox=dict(
                boxstyle="round,pad=0.18",
                facecolor="#ffffff",
                alpha=0.85,
                edgecolor="#cbd5e1",
                linewidth=0.6
            ),
            zorder=6
        )

    # 11. Plot Reference Cities for Context (Custom non-overlapping offsets)
    city_offsets = {
        "Dhaka": (-38, -6),
        "Chattogram": (8, -8),
        "Sylhet": (10, 2),
        "Rajshahi": (-46, 2),
        "Khulna": (-42, 2),
        "Barishal": (8, -6),
        "Rangpur": (8, 4),
        "Mymensingh": (-54, -12),
    }

    for city in REFERENCE_CITIES:
        ax.plot(city["lon"], city["lat"], marker="o", markersize=4.5, color="#0f172a", zorder=7)
        offset = city_offsets.get(city["name"], (6, 4))
        ax.annotate(
            city["name"],
            (city["lon"], city["lat"]),
            textcoords="offset points",
            xytext=offset,
            fontsize=8.5,
            fontweight="bold",
            color="#0f172a",
            zorder=7,
            bbox=dict(boxstyle="square,pad=0.15", facecolor="#ffffff", alpha=0.75, edgecolor="none")
        )

    # 12. Map Extents, Grids, and Coordinates
    bounds = boundary_gdf.total_bounds  # [minx, miny, maxx, maxy]
    x_pad = (bounds[2] - bounds[0]) * 0.08
    y_pad = (bounds[3] - bounds[1]) * 0.08
    ax.set_xlim(bounds[0] - x_pad, bounds[2] + x_pad)
    ax.set_ylim(bounds[1] - y_pad, bounds[3] + y_pad)

    ax.set_xlabel("Longitude (°E)", fontsize=11, fontweight="bold", labelpad=8)
    ax.set_ylabel("Latitude (°N)", fontsize=11, fontweight="bold", labelpad=8)
    ax.grid(color="#cbd5e1", linestyle="--", linewidth=0.6, alpha=0.75, zorder=1)

    # 13. Horizontal Colorbar
    cbar = fig.colorbar(
        sc_inc,
        ax=ax,
        orientation="horizontal",
        fraction=0.045,
        pad=0.07,
        shrink=0.75,
        aspect=28
    )
    cbar.set_label("Surface Air Temperature (T2M) Trend Rate (°C / decade)", fontsize=10, fontweight="bold")
    cbar.ax.tick_params(labelsize=9)

    # 14. Header Titles & Subtitles
    plt.suptitle(
        "NASA GMAO MERRA-2 — Bangladesh Temperature Trend Map (2001–2025)",
        fontsize=14.5,
        fontweight="bold",
        y=0.965,
        color="#0f172a"
    )
    ax.set_title(
        "Annual Mean Surface Air Temperature (T2M) Rate of Change & Direction across 34 Mainland Grid Points",
        fontsize=10.0,
        pad=10,
        color="#475569"
    )

    # 15. Scientific Inset Information Box
    n_total = len(df)
    n_sig_count = len(df_sig)
    mean_rate = df["slope_c_per_decade"].mean()
    min_rate = df["slope_c_per_decade"].min()
    max_rate = df["slope_c_per_decade"].max()
    min_p = df["p_value"].min()

    stats_text = (
        "SCIENTIFIC METRICS (ANNUAL MEAN):\n"
        f"• Period: 2001–2025 (25 Years)\n"
        f"• Retained Inland Points: {n_total}\n"
        f"• Warming (Rate > 0): {len(df_inc)} cells (max {max_rate:+.3f} °C/dec)\n"
        f"• Cooling (Rate < 0): {len(df_dec)} cells (min {min_rate:+.3f} °C/dec)\n"
        f"• National Mean Rate: {mean_rate:+.4f} °C/dec\n"
        f"• Significant (p < {alpha_significance}): {n_sig_count} cells (0.0%)\n"
        f"• Lowest p-value: {min_p:.4f} (at 24.5°N, 91.88°E)\n"
        "• Model: NASA GMAO MERRA-2 (T2M)\n"
        "• Boundary: geoBoundaries ADM0 (PIP Filtered)"
    )

    ax.text(
        0.02,
        0.14,
        stats_text,
        transform=ax.transAxes,
        fontsize=8.2,
        verticalalignment="bottom",
        fontfamily="monospace",
        bbox=dict(boxstyle="round,pad=0.6", facecolor="#ffffff", edgecolor="#94a3b8", alpha=0.94),
        zorder=8
    )

    # 16. Custom Legend for Markers, Directions & Significance
    legend_elements = [
        Line2D([0], [0], marker="^", color="w", label=f"Increasing Trend (n={len(df_inc)})",
               markerfacecolor="#e11d48", markeredgecolor="#1e293b", markersize=10),
        Line2D([0], [0], marker="v", color="w", label=f"Decreasing Trend (n={len(df_dec)})",
               markerfacecolor="#2563eb", markeredgecolor="#1e293b", markersize=10),
        Line2D([0], [0], marker="o", color="w", label="Size ∝ Trend Magnitude",
               markerfacecolor="#94a3b8", markeredgecolor="#1e293b", markersize=8),
        Line2D([0], [0], marker="o", color="w", label=f"p < {alpha_significance} Significant (None in annual)",
               markerfacecolor="none", markeredgecolor="#f59e0b", markeredgewidth=2, markersize=10),
    ]
    ax.legend(
        handles=legend_elements,
        loc="lower right",
        fontsize=8.2,
        framealpha=0.95,
        facecolor="#ffffff",
        edgecolor="#cbd5e1"
    )

    # 17. Export High-Resolution PNG
    os.makedirs(os.path.dirname(output_png_path), exist_ok=True)
    plt.savefig(output_png_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"[MAP] High-resolution trend map exported to: {output_png_path}")

    # Also mirror to project root data/ if desired
    root_data_png = os.path.abspath(os.path.join("data", "bangladesh_t2m_trend_map.png"))
    try:
        os.makedirs(os.path.dirname(root_data_png), exist_ok=True)
        shutil.copyfile(output_png_path, root_data_png)
        print(f"[MAP] Mirrored trend map to root data: {root_data_png}")
    except Exception as e:
        pass

    return os.path.abspath(output_png_path)


if __name__ == "__main__":
    generated_path = plot_bangladesh_trend_map()
    print(f"[SUCCESS] Spatial visualization complete: {generated_path}")
