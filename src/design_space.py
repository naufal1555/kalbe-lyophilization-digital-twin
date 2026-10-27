"""
design_space.py — QbD Design Space Construction (ICH Q8)
=========================================================
Sweeps a 2D grid of (T_shelf, P_chamber) setpoints,
running Monte Carlo at each point to compute P(collapse).
Outputs a Design Space heatmap.

Reference: ICH Q8(R2) — Pharmaceutical Development (2009)
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass

from . import config as cfg
from .monte_carlo import run_monte_carlo


@dataclass
class DesignSpaceResult:
    """Container for Design Space grid results."""
    T_shelf_grid: np.ndarray         # Shelf temp values [K]
    T_shelf_C_grid: np.ndarray       # Shelf temp values [°C]
    Pc_grid: np.ndarray              # Chamber pressure values [Pa]
    risk_matrix: np.ndarray          # P(collapse) matrix [%]  (shape: len(Pc) x len(Ts))
    drying_time_matrix: np.ndarray   # Mean drying time [hours]
    T_max_matrix: np.ndarray         # Mean T_max [°C]


def build_design_space(
    T_range: tuple = cfg.DS_T_SHELF_RANGE,
    T_step: float = cfg.DS_T_SHELF_STEP,
    Pc_range: tuple = cfg.DS_PC_RANGE,
    Pc_step: float = cfg.DS_PC_STEP,
    N_mc: int = cfg.DS_N_MC,
    seed: int = cfg.SEED,
    verbose: bool = True,
) -> DesignSpaceResult:
    """
    Construct the Design Space by sweeping T_shelf × P_chamber.

    Parameters
    ----------
    T_range : tuple
        (min, max) shelf temperature [K]
    T_step : float
        Temperature step [K]
    Pc_range : tuple
        (min, max) chamber pressure [Pa]
    Pc_step : float
        Pressure step [Pa]
    N_mc : int
        Monte Carlo runs per grid point
    seed : int
        Base random seed
    verbose : bool
        Print progress

    Returns
    -------
    DesignSpaceResult
    """
    T_shelf_vals = np.arange(T_range[0], T_range[1] + T_step/2, T_step)
    Pc_vals = np.arange(Pc_range[0], Pc_range[1] + Pc_step/2, Pc_step)

    n_T = len(T_shelf_vals)
    n_P = len(Pc_vals)
    total = n_T * n_P

    risk_matrix = np.zeros((n_P, n_T))
    drying_time_matrix = np.zeros((n_P, n_T))
    T_max_matrix = np.zeros((n_P, n_T))

    count = 0
    for j, Ts in enumerate(T_shelf_vals):
        for i, Pc in enumerate(Pc_vals):
            mc = run_monte_carlo(
                T_shelf=Ts,
                P_chamber=Pc,
                N=N_mc,
                seed=seed + count,
                store_runs=False,
            )
            risk_matrix[i, j] = mc.risk_of_collapse_pct
            drying_time_matrix[i, j] = mc.t_dry_mean
            T_max_matrix[i, j] = mc.T_max_mean

            count += 1
            if verbose and count % 20 == 0:
                print(f"  Design Space: {count}/{total} points completed "
                      f"({count/total*100:.0f}%)")

    if verbose:
        print(f"  Design Space: {total}/{total} points completed (100%)")

    return DesignSpaceResult(
        T_shelf_grid=T_shelf_vals,
        T_shelf_C_grid=T_shelf_vals - 273.15,
        Pc_grid=Pc_vals,
        risk_matrix=risk_matrix,
        drying_time_matrix=drying_time_matrix,
        T_max_matrix=T_max_matrix,
    )


def design_space_to_dataframe(ds: DesignSpaceResult) -> pd.DataFrame:
    """Flatten Design Space grid into a DataFrame."""
    rows = []
    for j, Ts in enumerate(ds.T_shelf_grid):
        for i, Pc in enumerate(ds.Pc_grid):
            rows.append({
                "T_shelf_K": Ts,
                "T_shelf_C": Ts - 273.15,
                "P_chamber_Pa": Pc,
                "risk_pct": ds.risk_matrix[i, j],
                "drying_time_hr": ds.drying_time_matrix[i, j],
                "T_max_mean_C": ds.T_max_matrix[i, j],
            })
    return pd.DataFrame(rows)
