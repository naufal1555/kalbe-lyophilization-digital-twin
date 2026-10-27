"""
model.py — Pikal 1D Mechanistic Lyophilization Solver
======================================================
Implements the quasi-steady-state coupled heat & mass transfer model
for the primary drying phase of pharmaceutical freeze-drying.

Governing Equations:
    1. Heat transfer:   q = Kv · Av · (T_shelf - T_p)
    2. Mass transfer:   ṁ = Ap · (P_ice(T_p) - P_c) / Rp(L)
    3. Energy balance:  q = ṁ · ΔH_sub
    4. Ice vapor:       P_ice(T) = exp(A - B/T)
    5. Cake resistance: Rp(L) = R0 + A1·L
    6. Front movement:  dL/dt = ṁ / (ρ_ice · Ap · (1 - ε))

References:
    Pikal, M.J. (2004); Fissore, D. et al. (2011)
"""

import numpy as np
from scipy.optimize import brentq
from dataclasses import dataclass, field
from typing import Optional

from . import config as cfg


def ice_vapor_pressure(T: float) -> float:
    """
    Clausius-Clapeyron ice vapor pressure.

    Parameters
    ----------
    T : float
        Temperature [K]

    Returns
    -------
    float
        Equilibrium vapor pressure of ice [Pa]
    """
    return np.exp(cfg.A_CC - cfg.B_CC / T)


def cake_resistance(L: float, R0: float = None, A1: float = None) -> float:
    """
    Dry layer mass transfer resistance as a function of thickness.

    Rp(L) = R0 + A1 · L   [Pa·s·m²/kg]

    Parameters
    ----------
    L : float
        Dry layer thickness [m]
    R0 : float, optional
        Initial resistance [Pa·s·m²/kg]. Defaults to config value.
    A1 : float, optional
        Resistance slope [Pa·s·m/kg]. Defaults to config value.

    Returns
    -------
    float
        Dry layer resistance [Pa·s·m²/kg]
    """
    if R0 is None:
        R0 = cfg.RP_R0
    if A1 is None:
        A1 = cfg.RP_A1
    return R0 + A1 * L


def solve_product_temperature(
    T_shelf: float,
    P_chamber: float,
    L: float,
    Kv: float,
    R0: float = None,
    A1: float = None,
) -> float:
    """
    Solve for product temperature T_p at the sublimation front.

    The energy balance equation is solved implicitly:
        Kv · Av · (T_shelf - T_p) = [Ap · (P_ice(T_p) - P_c) / Rp(L)] · ΔH_sub

    Uses Brent's method for robust root-finding.

    Parameters
    ----------
    T_shelf : float
        Shelf temperature [K]
    P_chamber : float
        Chamber pressure [Pa]
    L : float
        Current dry layer thickness [m]
    Kv : float
        Vial heat transfer coefficient [W/(m²·K)]
    R0, A1 : float, optional
        Cake resistance parameters

    Returns
    -------
    float
        Product temperature at sublimation front [K]
    """
    Rp = cake_resistance(L, R0, A1)

    def residual(Tp):
        # Left side: heat input from shelf
        q_in = Kv * cfg.A_VIAL * (T_shelf - Tp)
        # Right side: heat consumed by sublimation
        P_ice = ice_vapor_pressure(Tp)
        delta_P = max(P_ice - P_chamber, 0.0)
        m_dot = cfg.A_PRODUCT * delta_P / Rp
        q_sub = m_dot * cfg.DELTA_H_SUB
        return q_in - q_sub

    # Bracket: T_p must be between some low temp and T_shelf
    T_low = cfg.TP_BRACKET[0]
    T_high = min(T_shelf - 0.01, cfg.TP_BRACKET[1])

    try:
        Tp = brentq(residual, T_low, T_high, xtol=1e-6, maxiter=200)
    except ValueError:
        # If root-finding fails, return the shelf temp (no sublimation)
        Tp = T_shelf

    return Tp


@dataclass
class DryingResult:
    """Container for simulation results."""
    time: np.ndarray            # Time array [s]
    time_hours: np.ndarray      # Time array [hours]
    T_product: np.ndarray       # Product temperature profile [K]
    T_product_C: np.ndarray     # Product temperature profile [°C]
    L_dry: np.ndarray           # Dry layer thickness profile [m]
    m_dot: np.ndarray           # Sublimation rate profile [kg/s]
    drying_time_s: float        # Total primary drying time [s]
    drying_time_hr: float       # Total primary drying time [hours]
    T_product_max: float        # Maximum product temperature [K]
    T_product_max_C: float      # Maximum product temperature [°C]
    collapsed: bool             # Whether T_p exceeded T_c
    collapse_time_hr: float     # Time of first collapse [hours], or inf
    # Input parameters (for traceability)
    T_shelf: float = 0.0
    P_chamber: float = 0.0
    Kv: float = 0.0
    Tc: float = cfg.TC_MEAN


def simulate_primary_drying(
    T_shelf: float,
    P_chamber: float,
    Kv: float = cfg.KV_MEAN,
    Rp_scale: float = 1.0,
    Tc: float = cfg.TC_MEAN,
    dt: float = cfg.DT,
    t_max: float = cfg.T_MAX,
) -> DryingResult:
    """
    Run a single deterministic primary drying simulation.

    Parameters
    ----------
    T_shelf : float
        Shelf temperature setpoint [K]
    P_chamber : float
        Chamber pressure setpoint [Pa]
    Kv : float
        Vial heat transfer coefficient [W/(m²·K)]
    Rp_scale : float
        Scale factor for Rp (1.0 = baseline). Models cake heterogeneity.
    Tc : float
        Critical collapse temperature [K]
    dt : float
        Euler timestep [s]
    t_max : float
        Maximum simulation time [s]

    Returns
    -------
    DryingResult
        Comprehensive results container
    """
    # Scale Rp parameters
    R0 = cfg.RP_R0 * Rp_scale
    A1 = cfg.RP_A1 * Rp_scale

    # Pre-allocate arrays (estimate max steps)
    max_steps = int(t_max / dt) + 1
    time_arr = np.zeros(max_steps)
    Tp_arr = np.zeros(max_steps)
    L_arr = np.zeros(max_steps)
    mdot_arr = np.zeros(max_steps)

    # Initial conditions
    L = 0.0           # Dry layer thickness [m]
    t = 0.0           # Time [s]
    step = 0
    collapsed = False
    collapse_time = float('inf')

    while L < cfg.L_TOTAL and t < t_max:
        # 1. Solve for product temperature
        Tp = solve_product_temperature(T_shelf, P_chamber, L, Kv, R0, A1)

        # 2. Calculate sublimation rate
        Rp = cake_resistance(L, R0, A1)
        P_ice = ice_vapor_pressure(Tp)
        delta_P = max(P_ice - P_chamber, 0.0)
        m_dot = cfg.A_PRODUCT * delta_P / Rp

        # 3. Store results
        time_arr[step] = t
        Tp_arr[step] = Tp
        L_arr[step] = L
        mdot_arr[step] = m_dot

        # 4. Check collapse
        if Tp > Tc and not collapsed:
            collapsed = True
            collapse_time = t / 3600.0

        # 5. Advance dry layer front (Euler explicit)
        dL_dt = m_dot / (cfg.RHO_ICE * cfg.A_PRODUCT * (1 - cfg.EPSILON))
        L += dL_dt * dt
        L = min(L, cfg.L_TOTAL)
        t += dt
        step += 1

        if step >= max_steps:
            break

    # Trim arrays
    time_arr = time_arr[:step]
    Tp_arr = Tp_arr[:step]
    L_arr = L_arr[:step]
    mdot_arr = mdot_arr[:step]

    # Compute summary statistics
    T_product_max = float(np.max(Tp_arr)) if len(Tp_arr) > 0 else T_shelf
    drying_time_s = time_arr[-1] if len(time_arr) > 0 else 0.0

    return DryingResult(
        time=time_arr,
        time_hours=time_arr / 3600.0,
        T_product=Tp_arr,
        T_product_C=Tp_arr - 273.15,
        L_dry=L_arr,
        m_dot=mdot_arr,
        drying_time_s=drying_time_s,
        drying_time_hr=drying_time_s / 3600.0,
        T_product_max=T_product_max,
        T_product_max_C=T_product_max - 273.15,
        collapsed=collapsed,
        collapse_time_hr=collapse_time,
        T_shelf=T_shelf,
        P_chamber=P_chamber,
        Kv=Kv,
        Tc=Tc,
    )


def run_scenario(scenario_name: str) -> DryingResult:
    """
    Run a named scenario from config.SCENARIOS.

    Parameters
    ----------
    scenario_name : str
        One of 'Conservative', 'Moderate', 'Aggressive'

    Returns
    -------
    DryingResult
    """
    s = cfg.SCENARIOS[scenario_name]
    return simulate_primary_drying(
        T_shelf=s["T_shelf"],
        P_chamber=s["P_chamber"],
    )
