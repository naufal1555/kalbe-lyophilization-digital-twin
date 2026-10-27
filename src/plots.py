"""
plots.py — Publication-Quality Visualization Generator
=======================================================
Creates all figures for the Technical Report and Dashboard.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from pathlib import Path

from . import config as cfg
from .model import DryingResult
from .monte_carlo import MonteCarloResult
from .design_space import DesignSpaceResult

# Global style
sns.set_theme(style="whitegrid", font_scale=1.1)
plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
    "font.family": "sans-serif",
})

OUTPUT_DIR = Path(__file__).parent.parent / "outputs" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TC_DISPLAY = cfg.kelvin_to_celsius(cfg.TC_MEAN)  # -32.0°C


def plot_deterministic_scenarios(results: dict[str, DryingResult], save: bool = True):
    """
    Plot temperature profiles for multiple deterministic scenarios.

    Parameters
    ----------
    results : dict[str, DryingResult]
        Scenario name → result mapping
    save : bool
        Whether to save to disk
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    colors = {"Conservative": "#1565C0", "Moderate": "#F57F17", "Aggressive": "#C62828"}

    # — Left: Product Temperature Profile —
    ax1 = axes[0]
    for name, res in results.items():
        ax1.plot(res.time_hours, res.T_product_C, color=colors.get(name, "#333"),
                 linewidth=2, label=f"{name} (Ts={res.T_shelf-273.15:.0f}°C)")

    ax1.axhline(y=TC_DISPLAY, color="#D32F2F", linestyle="--", linewidth=1.5,
                label=f"Tc = {TC_DISPLAY:.0f}°C (Collapse Limit)")
    ax1.fill_between(ax1.get_xlim(), TC_DISPLAY, TC_DISPLAY + 15,
                     alpha=0.08, color="red", zorder=0)

    ax1.set_xlabel("Time [hours]")
    ax1.set_ylabel("Product Temperature [°C]")
    ax1.set_title("Product Temperature Profile — Primary Drying")
    ax1.legend(fontsize=9, loc="lower right")
    ax1.set_ylim(top=TC_DISPLAY + 10)

    # — Right: Dry Layer Progression —
    ax2 = axes[1]
    for name, res in results.items():
        ax2.plot(res.time_hours, res.L_dry * 1000, color=colors.get(name, "#333"),
                 linewidth=2, label=f"{name}")

    ax2.axhline(y=cfg.L_TOTAL * 1000, color="#666", linestyle=":",
                linewidth=1, label=f"L_total = {cfg.L_TOTAL*1000:.1f} mm")
    ax2.set_xlabel("Time [hours]")
    ax2.set_ylabel("Dry Layer Thickness [mm]")
    ax2.set_title("Sublimation Front Progression")
    ax2.legend(fontsize=9)

    plt.tight_layout()
    if save:
        fig.savefig(OUTPUT_DIR / "scenario_comparison.png")
    return fig


def plot_temperature_envelope(mc: MonteCarloResult, save: bool = True):
    """
    Plot Monte Carlo temperature envelope with percentile bands.

    Parameters
    ----------
    mc : MonteCarloResult
    save : bool
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # 5-95 percentile band
    ax.fill_between(mc.time_common, mc.Tp_p5, mc.Tp_p95,
                    alpha=0.15, color="#1565C0", label="5th–95th percentile")
    # 25-75 percentile band
    ax.fill_between(mc.time_common, mc.Tp_p25, mc.Tp_p75,
                    alpha=0.3, color="#1565C0", label="25th–75th percentile")
    # Median
    ax.plot(mc.time_common, mc.Tp_median, color="#0D47A1", linewidth=2,
            label="Median")
    # Min/Max envelope
    ax.plot(mc.time_common, mc.Tp_min, color="#90CAF9", linewidth=0.5,
            alpha=0.5)
    ax.plot(mc.time_common, mc.Tp_max_env, color="#90CAF9", linewidth=0.5,
            alpha=0.5)

    # Collapse line
    ax.axhline(y=TC_DISPLAY, color="#D32F2F", linestyle="--", linewidth=2,
               label=f"Tc = {TC_DISPLAY:.0f}°C")
    ax.fill_between(ax.get_xlim(), TC_DISPLAY, TC_DISPLAY + 15,
                    alpha=0.08, color="red", zorder=0)

    Ts_C = mc.T_shelf - 273.15
    ax.set_xlabel("Time [hours]")
    ax.set_ylabel("Product Temperature [°C]")
    ax.set_title(
        f"Monte Carlo Temperature Envelope (N={mc.N_mc})\n"
        f"T_shelf = {Ts_C:.0f}°C, P_chamber = {mc.P_chamber:.0f} Pa | "
        f"Risk of Collapse = {mc.risk_of_collapse_pct:.1f}%"
    )
    ax.legend(fontsize=9, loc="lower right")
    max_y = max(TC_DISPLAY + 8, float(np.nanmax(mc.Tp_p95)) + 3)
    ax.set_ylim(top=max_y)

    plt.tight_layout()
    if save:
        fig.savefig(OUTPUT_DIR / "temperature_envelope.png")
    return fig


def plot_collapse_histogram(mc: MonteCarloResult, save: bool = True):
    """
    Plot histogram of maximum product temperatures across MC runs.

    Parameters
    ----------
    mc : MonteCarloResult
    save : bool
    """
    fig, ax = plt.subplots(figsize=(9, 5.5))

    # Histogram
    n_bins = 40
    counts, bins, patches = ax.hist(mc.T_max_C_arr, bins=n_bins, edgecolor="white",
                                     linewidth=0.5, alpha=0.85, color="#1565C0")

    # Color bars above Tc as red
    for patch, left_edge in zip(patches, bins[:-1]):
        if left_edge >= TC_DISPLAY:
            patch.set_facecolor("#D32F2F")

    # Collapse line
    ax.axvline(x=TC_DISPLAY, color="#D32F2F", linestyle="--", linewidth=2,
               label=f"Tc = {TC_DISPLAY:.0f}°C")

    # Annotations
    n_collapsed = int(np.sum(mc.collapse_arr))
    Ts_C = mc.T_shelf - 273.15
    ax.annotate(
        f"Collapsed: {n_collapsed}/{mc.N_mc}\n"
        f"Risk = {mc.risk_of_collapse_pct:.1f}%",
        xy=(0.97, 0.95), xycoords="axes fraction",
        fontsize=11, fontweight="bold", ha="right", va="top",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#FFCDD2" if n_collapsed > 0 else "#C8E6C9",
                  alpha=0.9)
    )

    ax.set_xlabel("Maximum Product Temperature [°C]")
    ax.set_ylabel("Count")
    ax.set_title(
        f"Distribution of T_product_max (N={mc.N_mc})\n"
        f"T_shelf = {Ts_C:.0f}°C, P_chamber = {mc.P_chamber:.0f} Pa"
    )
    ax.legend(fontsize=10)

    plt.tight_layout()
    if save:
        fig.savefig(OUTPUT_DIR / "collapse_histogram.png")
    return fig


def plot_design_space(ds: DesignSpaceResult, save: bool = True):
    """
    Plot QbD Design Space heatmap.

    Parameters
    ----------
    ds : DesignSpaceResult
    save : bool
    """
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # Custom colormap: green → yellow → red
    from matplotlib.colors import LinearSegmentedColormap
    colors_risk = ["#1B5E20", "#4CAF50", "#FFEB3B", "#FF9800", "#F44336", "#B71C1C"]
    cmap_risk = LinearSegmentedColormap.from_list("risk", colors_risk, N=256)

    # — Left: Risk of Collapse Heatmap —
    ax1 = axes[0]
    im1 = ax1.imshow(
        ds.risk_matrix,
        extent=[ds.T_shelf_C_grid[0], ds.T_shelf_C_grid[-1],
                ds.Pc_grid[0], ds.Pc_grid[-1]],
        origin="lower", aspect="auto",
        cmap=cmap_risk, vmin=0, vmax=max(50, float(np.max(ds.risk_matrix)))
    )
    cb1 = fig.colorbar(im1, ax=ax1, label="Risk of Collapse [%]", pad=0.02)

    # Contour lines for risk levels
    X, Y = np.meshgrid(ds.T_shelf_C_grid, ds.Pc_grid)
    contour_levels = [0.1, 1.0, 5.0, 10.0, 25.0]
    valid_levels = [l for l in contour_levels if l <= np.max(ds.risk_matrix)]
    if valid_levels:
        cs1 = ax1.contour(X, Y, ds.risk_matrix, levels=valid_levels,
                          colors="white", linewidths=1.0, linestyles="--")
        ax1.clabel(cs1, fmt="%.1f%%", fontsize=8)

    ax1.set_xlabel("Shelf Temperature [°C]")
    ax1.set_ylabel("Chamber Pressure [Pa]")
    ax1.set_title("Design Space — Risk of Collapse (ICH Q8 QbD)")

    # — Right: Drying Time Heatmap —
    ax2 = axes[1]
    im2 = ax2.imshow(
        ds.drying_time_matrix,
        extent=[ds.T_shelf_C_grid[0], ds.T_shelf_C_grid[-1],
                ds.Pc_grid[0], ds.Pc_grid[-1]],
        origin="lower", aspect="auto",
        cmap="YlOrBr_r"
    )
    cb2 = fig.colorbar(im2, ax=ax2, label="Mean Drying Time [hours]", pad=0.02)

    # Iso-time contours
    if np.ptp(ds.drying_time_matrix) > 1:
        t_levels = np.linspace(
            np.min(ds.drying_time_matrix) + 2,
            np.max(ds.drying_time_matrix) - 2,
            5
        )
        cs2 = ax2.contour(X, Y, ds.drying_time_matrix, levels=t_levels,
                          colors="black", linewidths=0.8)
        ax2.clabel(cs2, fmt="%.0f hr", fontsize=8)

    ax2.set_xlabel("Shelf Temperature [°C]")
    ax2.set_ylabel("Chamber Pressure [Pa]")
    ax2.set_title("Design Space — Mean Primary Drying Time")

    plt.tight_layout()
    if save:
        fig.savefig(OUTPUT_DIR / "design_space_heatmap.png")
    return fig


def plot_drying_time_comparison(mc_results: dict[str, MonteCarloResult], save: bool = True):
    """
    Box plot comparing drying times across scenarios.

    Parameters
    ----------
    mc_results : dict[str, MonteCarloResult]
    save : bool
    """
    fig, ax = plt.subplots(figsize=(8, 5))

    data = []
    labels = []
    colors = ["#1565C0", "#F57F17", "#C62828"]

    for i, (name, mc) in enumerate(mc_results.items()):
        data.append(mc.drying_time_arr)
        labels.append(f"{name}\n(Ts={mc.T_shelf-273.15:.0f}°C)")

    try:
        bp = ax.boxplot(data, tick_labels=labels, patch_artist=True, widths=0.5)
    except TypeError:
        bp = ax.boxplot(data, labels=labels, patch_artist=True, widths=0.5)
    for patch, color in zip(bp["boxes"], colors[:len(data)]):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)

    ax.set_ylabel("Primary Drying Time [hours]")
    ax.set_title("Drying Time Distribution by Scenario (Monte Carlo)")

    # Add risk annotation
    for i, (name, mc) in enumerate(mc_results.items()):
        ax.annotate(
            f"Risk: {mc.risk_of_collapse_pct:.1f}%",
            xy=(i + 1, np.median(mc.drying_time_arr)),
            xytext=(0, 20), textcoords="offset points",
            ha="center", fontsize=9, fontweight="bold",
            color="#D32F2F" if mc.risk_of_collapse_pct > 1 else "#2E7D32"
        )

    plt.tight_layout()
    if save:
        fig.savefig(OUTPUT_DIR / "drying_time_comparison.png")
    return fig
