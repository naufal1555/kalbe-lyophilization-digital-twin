"""
app.py — Kalbe AEC Biologics Lyophilization Digital Twin (Interactive Dashboard)
================================================================================
An in-silico process simulation and Quality by Design (QbD / ICH Q8) web tool
for sterile biologics manufacturing (Kalbio Global Medika / Kalbe Farma).
"""

import sys
from pathlib import Path
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Setup path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src import config as cfg
from src.model import simulate_primary_drying, solve_product_temperature
from src.monte_carlo import run_monte_carlo
from src.plots import (
    plot_temperature_envelope,
    plot_collapse_histogram,
)

# Page configuration
st.set_page_config(
    page_title="Kalbe AEC | Lyophilization Digital Twin",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1565C0;
        margin-bottom: 0.1rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #455A64;
        margin-bottom: 1.2rem;
    }
    .kpi-card {
        background-color: #F8F9FA;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #1565C0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .kpi-val {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0D47A1;
    }
    .kpi-lbl {
        font-size: 0.85rem;
        color: #607D8B;
        text-transform: uppercase;
        font-weight: 600;
    }
    .status-safe {
        color: #2E7D32;
        font-weight: 700;
    }
    .status-danger {
        color: #C62828;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SIDEBAR CONTROLS
# -----------------------------------------------------------------------------
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Kalbe_Farma_logo.svg/1200px-Kalbe_Farma_logo.svg.png", width=180)
st.sidebar.markdown("### ⚙️ Operating Parameters")

# Preset selector
preset = st.sidebar.selectbox(
    "Recipe Presets:",
    ["Custom", "Conservative (Safe, -30°C)", "Moderate (Balanced, -25°C)", "Aggressive (Fast, -20°C)"]
)

if preset == "Conservative (Safe, -30°C)":
    default_ts = -30.0
    default_pc = 8.0
elif preset == "Moderate (Balanced, -25°C)":
    default_ts = -25.0
    default_pc = 10.0
elif preset == "Aggressive (Fast, -20°C)":
    default_ts = -20.0
    default_pc = 13.0
else:
    default_ts = -25.0
    default_pc = 10.0

T_shelf_C = st.sidebar.slider(
    "Shelf Temperature (T_shelf) [°C]:",
    min_value=-35.0,
    max_value=-5.0,
    value=default_ts,
    step=1.0,
    help="Primary drying shelf temperature setpoint."
)

P_chamber_Pa = st.sidebar.slider(
    "Chamber Pressure (P_chamber) [Pa]:",
    min_value=5.0,
    max_value=25.0,
    value=default_pc,
    step=1.0,
    help="Vacuum pressure setpoint in the drying chamber. 10 Pa ≈ 75 mTorr."
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎲 Uncertainty Engine (Monte Carlo)")

N_mc = st.sidebar.slider(
    "Monte Carlo Iterations:",
    min_value=100,
    max_value=1000,
    value=300,
    step=50,
    help="Number of stochastic runs evaluating vial-to-vial heat transfer heterogeneity."
)

include_edge_vials = st.sidebar.checkbox(
    "Include Edge-Vial Radiation Effect",
    value=True,
    help="Models perimeter vials receiving +15-25% radiative heat from chamber walls."
)

T_c_C = st.sidebar.number_input(
    "Critical Collapse Temp (T_c) [°C]:",
    value=-32.0,
    step=0.5,
    help="Formulation glass transition/collapse temperature. Sucrose matrix collapses above this."
)

# -----------------------------------------------------------------------------
# MAIN HEADER
# -----------------------------------------------------------------------------
st.markdown('<div class="main-title">❄️ Kalbe AEC — Biologics Lyophilization Digital Twin</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Mechanistic 1D Pikal Heat & Mass Transfer Simulation • ICH Q8 Quality by Design (QbD) • Sterile Biomanufacturing (PT Kalbio Global Medika)</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SIMULATION EXECUTION
# -----------------------------------------------------------------------------
T_shelf_K = T_shelf_C + 273.15
Tc_K = T_c_C + 273.15

with st.spinner("Executing Pikal 1D Mechanistic Solver & Monte Carlo Engine..."):
    # Run deterministic baseline
    det_run = simulate_primary_drying(T_shelf=T_shelf_K, P_chamber=P_chamber_Pa, Tc=Tc_K)

    # Run Monte Carlo
    mc_run = run_monte_carlo(
        T_shelf=T_shelf_K,
        P_chamber=P_chamber_Pa,
        N=N_mc,
        seed=42,
        store_runs=True
    )

# -----------------------------------------------------------------------------
# TOP KPI CARDS
# -----------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
    st.markdown('<div class="kpi-lbl">Mean Drying Time</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-val">{mc_run.t_dry_mean:.1f} <span style="font-size:1rem;color:#888;">hours</span></div>', unsafe_allow_html=True)
    st.caption(f"± {mc_run.t_dry_std:.2f} h (95% CI: [{mc_run.t_dry_mean-1.96*mc_run.t_dry_std:.1f}, {mc_run.t_dry_mean+1.96*mc_run.t_dry_std:.1f}])")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
    st.markdown('<div class="kpi-lbl">Peak Product Temp (T_p,max)</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-val">{mc_run.T_max_mean:.1f} <span style="font-size:1rem;color:#888;">°C</span></div>', unsafe_allow_html=True)
    margin = T_c_C - mc_run.T_max_mean
    st.caption(f"Safety Margin to T_c: {margin:+.1f} °C")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
    st.markdown('<div class="kpi-lbl">Risk of Collapse P(T_p > T_c)</div>', unsafe_allow_html=True)
    risk_color = "#2E7D32" if mc_run.risk_of_collapse_pct < 0.1 else ("#F57F17" if mc_run.risk_of_collapse_pct < 2.0 else "#C62828")
    st.markdown(f'<div class="kpi-val" style="color:{risk_color};">{mc_run.risk_of_collapse_pct:.2f}%</div>', unsafe_allow_html=True)
    n_failed = int(np.sum(mc_run.collapse_arr))
    st.caption(f"{n_failed} of {N_mc} simulated vials collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
    st.markdown('<div class="kpi-lbl">QbD Batch Status</div>', unsafe_allow_html=True)
    if mc_run.risk_of_collapse_pct < 0.1:
        st.markdown('<div class="kpi-val status-safe">🟢 VERIFIED SAFE</div>', unsafe_allow_html=True)
        st.caption("Inside ICH Q8 QbD Design Space")
    elif mc_run.risk_of_collapse_pct < 2.0:
        st.markdown('<div class="kpi-val" style="color:#F57F17;">🟡 CAUTION</div>', unsafe_allow_html=True)
        st.caption("Requires In-Line PAT Monitoring")
    else:
        st.markdown('<div class="kpi-val status-danger">🔴 HIGH RISK</div>', unsafe_allow_html=True)
        st.caption("Reject: Risk exceeds 2.0% threshold")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MAIN TABS
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Dynamic Temperature Trajectory",
    "📊 Stochastic Risk Distribution",
    "🗺️ ICH Q8 Design Space Heatmap",
    "🔬 Mechanistic Model & Parameter Registry"
])

with tab1:
    st.markdown("#### Primary Drying Thermal Trajectory & Sublimation Envelope")
    st.markdown("Showing 5th–95th percentile confidence bands generated across simulated vials under stochastic heat transfer variation.")

    fig_env = plot_temperature_envelope(mc_run, save=False)
    st.pyplot(fig_env)
    plt.close(fig_env)

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.info(f"**Deterministic Completion Time:** {det_run.drying_time_hr:.2f} hours")
    with col_t2:
        st.info(f"**Time Saved vs Conservative Baseline (-30°C):** {max(0, 48.0 - mc_run.t_dry_mean):.1f} hours per commercial batch")

with tab2:
    st.markdown("#### Vial Population Maximum Temperature Histogram")
    st.markdown("Frequency distribution of peak sublimation temperatures ($T_{p,\text{max}}$) across 1,000 vials. Red bars represent vials that crossed $T_c$.")

    fig_hist = plot_collapse_histogram(mc_run, save=False)
    st.pyplot(fig_hist)
    plt.close(fig_hist)

with tab3:
    st.markdown("#### Pre-computed QbD Design Space (T_shelf vs Chamber Pressure)")
    st.markdown("Maps the multidimensional operational window ensuring batch failure remains below the 0.1% Quality by Design threshold.")

    ds_fig_path = PROJECT_ROOT / "outputs" / "figures" / "design_space_heatmap.png"
    if ds_fig_path.exists():
        st.image(str(ds_fig_path), use_container_width=True)
    else:
        st.warning("Design Space heatmap is currently being pre-calculated by the background pipeline. Refresh in 1-2 minutes.")

with tab4:
    st.markdown("#### First-Principles Model Specification & Empirical Constants")
    st.markdown("""
    The digital twin solves the **Pikal-Searles 1D moving-boundary formulation** coupling thermal conduction, radiation, and porous gas dynamics:
    """)

    st.latex(r"q = A_v \cdot K_v \cdot (T_{\text{shelf}} - T_p)")
    st.latex(r"\dot{m} = \frac{A_p \cdot (P_{\text{ice}}(T_p) - P_c)}{R_p(L)}")
    st.latex(r"K_v (T_{\text{shelf}} - T_p) = \frac{\Delta H_{\text{sub}} \cdot (P_{\text{ice}}(T_p) - P_c)}{R_p(L)}")
    st.latex(r"\frac{dL}{dt} = \frac{\dot{m}}{\rho_{\text{ice}} A_p (1 - \varepsilon)}")

    st.markdown("##### Parameter Registry (5% w/v Sucrose Formulations):")
    param_data = [
        {"Parameter": "Latent Heat of Sublimation (ΔH_sub)", "Value": "2.839 × 10⁶ J/kg", "Reference": "CRC Handbook of Physics"},
        {"Parameter": "Ice Density (ρ_ice)", "Value": "917 kg/m³", "Reference": "Standard physical constant"},
        {"Parameter": "Cake Porosity (ε)", "Value": "0.92", "Reference": "Pikal et al. (2004)"},
        {"Parameter": "Mean Vial Heat Transfer Coeff (Kv)", "Value": "25.0 ± 3.5 W/(m²·K)", "Reference": "Rambhatla & Pikal (2003)"},
        {"Parameter": "Initial Cake Resistance (R0)", "Value": "1.44 × 10⁵ Pa·s·m²/kg", "Reference": "Pikal; Fissore et al. (2011)"},
        {"Parameter": "Resistance Slope Factor (A1)", "Value": "1.68 × 10⁸ Pa·s·m/kg", "Reference": "Pisano, Barresi, & Fissore"},
        {"Parameter": "Critical Collapse Temp (Tc)", "Value": "-32.0 ± 1.0 °C", "Reference": "Freeze-Dry Microscopy benchmark"},
    ]
    st.table(pd.DataFrame(param_data))

st.markdown("---")
st.caption("PT Kalbe Farma Tbk • Corporate Digital Transformation (CDT) • Advanced Engineering Center (AEC)")
