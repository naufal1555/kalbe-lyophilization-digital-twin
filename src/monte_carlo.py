"""
monte_carlo.py — Stochastic Simulation Engine
===============================================
Runs N Monte Carlo iterations of the Pikal 1D model,
sampling Kv, Rp_scale, and Tc from their physical distributions.

Quantifies:
    - Risk of Collapse: P(T_p_max > T_c)
    - Drying time distribution
    - Temperature envelope (percentile bands)
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Optional

from . import config as cfg
from .model import simulate_primary_drying, DryingResult


@dataclass
class MonteCarloResult:
    """Container for Monte Carlo simulation results."""
    # Per-run scalars
    Kv_samples: np.ndarray           # Sampled Kv values [W/(m²·K)]
    Rp_scale_samples: np.ndarray     # Sampled Rp scale factors [-]
    Tc_samples: np.ndarray           # Sampled Tc values [K]
    T_max_arr: np.ndarray            # Max product temp per run [K]
    T_max_C_arr: np.ndarray          # Max product temp per run [°C]
    drying_time_arr: np.ndarray      # Drying time per run [hours]
    collapse_arr: np.ndarray         # Boolean collapse per run

    # Aggregate statistics
    risk_of_collapse: float          # P(collapse) as fraction [0-1]
    risk_of_collapse_pct: float      # P(collapse) as percentage [%]
    t_dry_mean: float                # Mean drying time [hours]
    t_dry_std: float                 # Std drying time [hours]
    T_max_mean: float                # Mean max product temp [°C]
    T_max_std: float                 # Std max product temp [°C]

    # Temperature envelope data (time-resolved percentiles)
    time_common: np.ndarray          # Common time grid [hours]
    Tp_median: np.ndarray            # 50th percentile T_p [°C]
    Tp_p5: np.ndarray               # 5th percentile T_p [°C]
    Tp_p95: np.ndarray              # 95th percentile T_p [°C]
    Tp_p25: np.ndarray              # 25th percentile T_p [°C]
    Tp_p75: np.ndarray              # 75th percentile T_p [°C]
    Tp_min: np.ndarray              # Min T_p [°C]
    Tp_max_env: np.ndarray          # Max T_p [°C]

    # Full individual runs (for detailed plotting)
    individual_runs: Optional[List[DryingResult]] = None

    # Input parameters
    T_shelf: float = 0.0
    P_chamber: float = 0.0
    N_mc: int = 0


def run_monte_carlo(
    T_shelf: float,
    P_chamber: float,
    N: int = cfg.N_MC_DEFAULT,
    seed: int = cfg.SEED,
    store_runs: bool = False,
    include_edge_vials: bool = True,
    Tc_mean: Optional[float] = None,
) -> MonteCarloResult:
    """
    Execute Monte Carlo simulation for a given setpoint.

    Parameters
    ----------
    T_shelf : float
        Shelf temperature [K]
    P_chamber : float
        Chamber pressure [Pa]
    N : int
        Number of Monte Carlo iterations
    seed : int
        Random seed for reproducibility
    store_runs : bool
        Whether to store all individual DryingResult objects
    include_edge_vials : bool
        Whether to include edge-vial radiation variability (+15-25% Kv).
        If False, simulates radiation shielding/guard rings (Kv ~ N(22, 1.2^2)).
    Tc_mean : float, optional
        Target mean collapse temperature [K]. Defaults to cfg.TC_MEAN.

    Returns
    -------
    MonteCarloResult
    """
    rng = np.random.default_rng(seed)

    # Sample stochastic parameters
    if include_edge_vials:
        Kv_samples = rng.normal(cfg.KV_MEAN, cfg.KV_STD, size=N)
    else:
        # Radiation-shielded or center-vials only (effective guard ring mitigation)
        Kv_samples = rng.normal(cfg.KV_CENTER, 1.2, size=N)

    Kv_samples = np.clip(Kv_samples, 10.0, 50.0)  # Physical bounds

    Rp_scale_samples = rng.normal(cfg.RP_SCALE_MEAN, cfg.RP_SCALE_STD, size=N)
    Rp_scale_samples = np.clip(Rp_scale_samples, 0.5, 2.0)

    tc_center = Tc_mean if Tc_mean is not None else cfg.TC_MEAN
    Tc_samples = rng.normal(tc_center, cfg.TC_STD, size=N)

    # Storage arrays
    T_max_arr = np.zeros(N)
    drying_time_arr = np.zeros(N)
    collapse_arr = np.zeros(N, dtype=bool)
    all_runs: List[DryingResult] = []

    # Run simulations once (O(N) efficiency)
    for i in range(N):
        result = simulate_primary_drying(
            T_shelf=T_shelf,
            P_chamber=P_chamber,
            Kv=Kv_samples[i],
            Rp_scale=Rp_scale_samples[i],
            Tc=Tc_samples[i],
        )
        T_max_arr[i] = result.T_product_max
        drying_time_arr[i] = result.drying_time_hr
        collapse_arr[i] = result.collapsed
        all_runs.append(result)

    # Build temperature envelope on common time grid
    max_time = np.max(drying_time_arr) * 3600  # seconds
    n_common = 500
    time_common_s = np.linspace(0, max_time, n_common)
    time_common_hr = time_common_s / 3600.0

    # Interpolate all runs onto common grid
    Tp_matrix = np.full((N, n_common), np.nan)
    for i, run in enumerate(all_runs):
        if len(run.time) > 1:
            Tp_interp = np.interp(
                time_common_s, run.time, run.T_product_C,
                right=run.T_product_C[-1]
            )
            Tp_matrix[i, :] = Tp_interp

    Tp_median = np.nanpercentile(Tp_matrix, 50, axis=0)
    Tp_p5 = np.nanpercentile(Tp_matrix, 5, axis=0)
    Tp_p95 = np.nanpercentile(Tp_matrix, 95, axis=0)
    Tp_p25 = np.nanpercentile(Tp_matrix, 25, axis=0)
    Tp_p75 = np.nanpercentile(Tp_matrix, 75, axis=0)
    Tp_min = np.nanmin(Tp_matrix, axis=0)
    Tp_max_env = np.nanmax(Tp_matrix, axis=0)

    # Compute aggregate statistics
    risk_frac = float(np.mean(collapse_arr))

    return MonteCarloResult(
        Kv_samples=Kv_samples,
        Rp_scale_samples=Rp_scale_samples,
        Tc_samples=Tc_samples,
        T_max_arr=T_max_arr,
        T_max_C_arr=T_max_arr - 273.15,
        drying_time_arr=drying_time_arr,
        collapse_arr=collapse_arr,
        risk_of_collapse=risk_frac,
        risk_of_collapse_pct=risk_frac * 100,
        t_dry_mean=float(np.mean(drying_time_arr)),
        t_dry_std=float(np.std(drying_time_arr)),
        T_max_mean=float(np.mean(T_max_arr - 273.15)),
        T_max_std=float(np.std(T_max_arr - 273.15)),
        time_common=time_common_hr,
        Tp_median=Tp_median,
        Tp_p5=Tp_p5,
        Tp_p95=Tp_p95,
        Tp_p25=Tp_p25,
        Tp_p75=Tp_p75,
        Tp_min=Tp_min,
        Tp_max_env=Tp_max_env,
        individual_runs=all_runs if store_runs else None,
        T_shelf=T_shelf,
        P_chamber=P_chamber,
        N_mc=N,
    )


def results_to_dataframe(mc: MonteCarloResult) -> pd.DataFrame:
    """Convert per-run Monte Carlo results to a DataFrame."""
    return pd.DataFrame({
        "Kv_W_m2K": mc.Kv_samples,
        "Rp_scale": mc.Rp_scale_samples,
        "Tc_K": mc.Tc_samples,
        "Tc_C": mc.Tc_samples - 273.15,
        "T_max_K": mc.T_max_arr,
        "T_max_C": mc.T_max_C_arr,
        "drying_time_hr": mc.drying_time_arr,
        "collapsed": mc.collapse_arr,
    })
