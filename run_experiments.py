"""
run_experiments.py — Master Simulation & Figure Generation Pipeline
=====================================================================
Executes:
  1. Deterministic baseline runs (Conservative, Moderate, Aggressive)
  2. Multi-scenario comparison plots & data export
  3. 1,000-run Monte Carlo uncertainty analysis on Moderate scenario
  4. Temperature envelope & collapse risk distribution plots
  5. Multi-scenario Monte Carlo comparison (box plots)
  6. QbD Design Space grid sweep (T_shelf × P_chamber) & heatmap export
"""

import os
import sys
import time
from pathlib import Path
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src import config as cfg
from src.model import run_scenario, simulate_primary_drying
from src.monte_carlo import run_monte_carlo, results_to_dataframe
from src.design_space import build_design_space, design_space_to_dataframe
from src.plots import (
    plot_deterministic_scenarios,
    plot_temperature_envelope,
    plot_collapse_histogram,
    plot_drying_time_comparison,
    plot_design_space,
)

DATA_DIR = PROJECT_ROOT / "outputs" / "data"
FIG_DIR = PROJECT_ROOT / "outputs" / "figures"
DATA_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)


def main():
    print("=" * 70)
    print("  KALBE AEC — LYOPHILIZATION DIGITAL TWIN EXPERIMENTAL PIPELINE")
    print("=" * 70)

    # -------------------------------------------------------------------------
    # 1. DETERMINISTIC BASELINE SCENARIOS
    # -------------------------------------------------------------------------
    print("\n[Step 1/4] Running Deterministic Baseline Scenarios...")
    start_time = time.time()
    det_results = {}
    det_records = []

    for name in ["Conservative", "Moderate", "Aggressive"]:
        res = run_scenario(name)
        det_results[name] = res
        det_records.append({
            "Scenario": name,
            "T_shelf_C": res.T_shelf - 273.15,
            "P_chamber_Pa": res.P_chamber,
            "Drying_Time_hr": round(res.drying_time_hr, 2),
            "Max_Product_Temp_C": round(res.T_product_max_C, 2),
            "Collapsed": res.collapsed,
            "Collapse_Time_hr": round(res.collapse_time_hr, 2) if res.collapsed else None,
        })
        print(f"  -> {name:<12}: Drying Time = {res.drying_time_hr:5.1f} h | "
              f"T_p,max = {res.T_product_max_C:6.2f} °C | Collapsed = {res.collapsed}")

    df_det = pd.DataFrame(det_records)
    df_det.to_csv(DATA_DIR / "deterministic_baseline.csv", index=False)
    print(f"  Saved baseline results to: {DATA_DIR / 'deterministic_baseline.csv'}")

    plot_deterministic_scenarios(det_results, save=True)
    print(f"  Saved figure: {FIG_DIR / 'scenario_comparison.png'}")

    # -------------------------------------------------------------------------
    # 2. MONTE CARLO UNCERTAINTY QUANTIFICATION (Moderate Scenario, N=1,000)
    # -------------------------------------------------------------------------
    print("\n[Step 2/4] Running 1,000-Iteration Monte Carlo Simulation (Moderate)...")
    t_shelf_mod = cfg.SCENARIOS["Moderate"]["T_shelf"]
    p_ch_mod = cfg.SCENARIOS["Moderate"]["P_chamber"]

    mc_mod = run_monte_carlo(t_shelf_mod, p_ch_mod, N=1000, seed=cfg.SEED, store_runs=True)
    print(f"  -> Monte Carlo Results (T_shelf = {t_shelf_mod-273.15:.0f}°C, P_c = {p_ch_mod:.0f} Pa):")
    print(f"     Mean Drying Time  : {mc_mod.t_dry_mean:.2f} ± {mc_mod.t_dry_std:.2f} h")
    print(f"     Mean Max Temp     : {mc_mod.T_max_mean:.2f} ± {mc_mod.T_max_std:.2f} °C")
    print(f"     Risk of Collapse  : {mc_mod.risk_of_collapse_pct:.2f}% (P(T_p > T_c))")

    df_mc = results_to_dataframe(mc_mod)
    df_mc.to_csv(DATA_DIR / "monte_carlo_results.csv", index=False)
    print(f"  Saved Monte Carlo data to: {DATA_DIR / 'monte_carlo_results.csv'}")

    plot_temperature_envelope(mc_mod, save=True)
    print(f"  Saved figure: {FIG_DIR / 'temperature_envelope.png'}")

    plot_collapse_histogram(mc_mod, save=True)
    print(f"  Saved figure: {FIG_DIR / 'collapse_histogram.png'}")

    # -------------------------------------------------------------------------
    # 3. MULTI-SCENARIO STOCHASTIC COMPARISON
    # -------------------------------------------------------------------------
    print("\n[Step 3/4] Running Monte Carlo across all 3 scenarios for comparison...")
    mc_cons = run_monte_carlo(
        cfg.SCENARIOS["Conservative"]["T_shelf"],
        cfg.SCENARIOS["Conservative"]["P_chamber"],
        N=500, seed=101
    )
    mc_agg = run_monte_carlo(
        cfg.SCENARIOS["Aggressive"]["T_shelf"],
        cfg.SCENARIOS["Aggressive"]["P_chamber"],
        N=500, seed=102
    )

    plot_drying_time_comparison({
        "Conservative": mc_cons,
        "Moderate": mc_mod,
        "Aggressive": mc_agg
    }, save=True)
    print(f"  Saved figure: {FIG_DIR / 'drying_time_comparison.png'}")

    # -------------------------------------------------------------------------
    # 4. QbD DESIGN SPACE GRID SWEEP (ICH Q8)
    # -------------------------------------------------------------------------
    print("\n[Step 4/4] Constructing ICH Q8 QbD Design Space Heatmap...")
    # Using optimized grid: T_shelf from -30°C to -10°C (step 2°C), P_c from 6 to 18 Pa (step 2 Pa), N_mc=150
    ds = build_design_space(
        T_range=(243.15, 263.15),  # -30°C to -10°C
        T_step=2.0,
        Pc_range=(6.0, 18.0),
        Pc_step=2.0,
        N_mc=150,
        seed=2026,
        verbose=True
    )

    df_ds = design_space_to_dataframe(ds)
    df_ds.to_csv(DATA_DIR / "design_space_grid.csv", index=False)
    print(f"  Saved Design Space data to: {DATA_DIR / 'design_space_grid.csv'}")

    plot_design_space(ds, save=True)
    print(f"  Saved figure: {FIG_DIR / 'design_space_heatmap.png'}")

    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print(f"  ALL EXPERIMENTS & ARTIFACTS COMPLETED SUCCESSFULLY in {elapsed:.1f} s!")
    print("=" * 70)


if __name__ == "__main__":
    main()
