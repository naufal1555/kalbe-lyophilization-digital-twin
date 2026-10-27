"""
app.py — Kalbe AEC Biologics Lyophilization Digital Twin Console
================================================================================
Modern Enterprise Bio-Industrial Dashboard (BorderFlow Aesthetic + Kalbe Green)
Target Facility: PT Kalbio Global Medika (KGM) — Cikarang Biologics Cleanroom
Author: Naufal Fathin (Process Simulation Engineering Intern Assessment)
"""

import sys
from pathlib import Path
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# Setup path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src import config as cfg
from src.model import simulate_primary_drying, solve_product_temperature
from src.monte_carlo import run_monte_carlo

# Page Configuration
st.set_page_config(
    page_title="Kalbe AEC | Lyo Digital Twin Dashboard",
    page_icon="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Kalbe_Farma_logo.svg/1200px-Kalbe_Farma_logo.svg.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# BESPOKE CSS: BORDERFLOW AESTHETIC + KALBE FARMA GREEN GRADIENT
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    /* Global Body & Background */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background-color: #F8FAFC;
        color: #0F172A;
    }

    /* Remove default streamlit top padding */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1380px !important;
    }

    /* Top Navigation Search & Profile Bar */
    .top-nav-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 10px 20px;
        margin-bottom: 22px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
    }

    .search-input-box {
        display: flex;
        align-items: center;
        background: #F1F5F9;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 6px 14px;
        width: 380px;
        color: #64748B;
        font-size: 0.85rem;
    }

    .search-input-box span.shortcut {
        margin-left: auto;
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 4px;
        padding: 2px 6px;
        font-size: 0.7rem;
        font-family: 'JetBrains Mono', monospace;
        color: #94A3B8;
    }

    .nav-profile-block {
        display: flex;
        align-items: center;
        gap: 16px;
    }

    .nav-icon-btn {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #64748B;
        cursor: pointer;
        position: relative;
    }

    .nav-icon-btn .badge-dot {
        position: absolute;
        top: 6px;
        right: 6px;
        width: 8px;
        height: 8px;
        background: #00A859;
        border: 2px solid #FFFFFF;
        border-radius: 50%;
    }

    .user-profile-card {
        display: flex;
        align-items: center;
        gap: 10px;
        padding-left: 8px;
        border-left: 1px solid #E2E8F0;
    }

    .user-avatar-img {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: linear-gradient(135deg, #008837 0%, #00B14F 100%);
        color: #FFFFFF;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.85rem;
    }

    .user-name-text {
        font-size: 0.85rem;
        font-weight: 700;
        color: #0F172A;
        line-height: 1.2;
    }

    .user-role-text {
        font-size: 0.72rem;
        color: #64748B;
        font-weight: 500;
    }

    /* Greeting Header */
    .greeting-container {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        margin-bottom: 20px;
    }

    .greeting-title {
        font-size: 1.75rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #0F172A;
        margin: 0;
    }

    .greeting-subtitle {
        font-size: 0.88rem;
        color: #64748B;
        margin-top: 4px;
        margin-bottom: 0;
    }

    .greeting-pill-bar {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .filter-chip {
        display: flex;
        align-items: center;
        gap: 6px;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 6px 14px;
        font-size: 0.82rem;
        font-weight: 600;
        color: #334155;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
    }

    /* BorderFlow KPI Metric Cards */
    .kpi-metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 18px 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03), 0 1px 2px rgba(0, 0, 0, 0.02);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        position: relative;
    }

    .kpi-metric-card:hover {
        box-shadow: 0 4px 12px rgba(0, 136, 55, 0.08);
        border-color: #CBD5E1;
    }

    .card-top-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }

    .card-icon-bubble {
        width: 38px;
        height: 38px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
    }

    .card-title-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
        margin-left: 10px;
    }

    .kpi-main-num {
        font-size: 1.9rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: #0F172A;
        line-height: 1.1;
    }

    .badge-pill-green {
        display: inline-flex;
        align-items: center;
        gap: 3px;
        background: #DCFCE7;
        color: #15803D;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        margin-left: 8px;
    }

    .badge-pill-blue {
        display: inline-flex;
        align-items: center;
        gap: 3px;
        background: #EFF6FF;
        color: #1D4ED8;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        margin-left: 8px;
    }

    .badge-pill-red {
        display: inline-flex;
        align-items: center;
        gap: 3px;
        background: #FEF2F2;
        color: #B91C1C;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        margin-left: 8px;
    }

    .card-subtext {
        font-size: 0.78rem;
        color: #94A3B8;
        margin-top: 6px;
    }

    /* White Content Card Panels */
    .white-panel {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 22px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
        margin-bottom: 20px;
    }

    .panel-header-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
    }

    .panel-heading {
        font-size: 1.05rem;
        font-weight: 700;
        color: #0F172A;
        margin: 0;
    }

    /* List Item Row for Benchmarks & Quick Actions */
    .list-item-row {
        display: flex;
        align-items: center;
        padding: 12px 14px;
        border-radius: 12px;
        border: 1px solid #F1F5F9;
        margin-bottom: 8px;
        background: #FAFAFA;
        transition: background 0.15s ease, border-color 0.15s ease;
    }

    .list-item-row:hover {
        background: #F0FDF4;
        border-color: #BBF7D0;
    }

    .list-icon-pill {
        width: 36px;
        height: 36px;
        border-radius: 8px;
        background: #E8F5E9;
        color: #008837;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.9rem;
        margin-right: 12px;
    }

    .list-title {
        font-size: 0.86rem;
        font-weight: 700;
        color: #0F172A;
        line-height: 1.2;
    }

    .list-subtitle {
        font-size: 0.74rem;
        color: #64748B;
    }

    .list-value-bold {
        font-size: 0.9rem;
        font-weight: 700;
        color: #0F172A;
        font-family: 'JetBrains Mono', monospace;
        margin-left: auto;
        margin-right: 12px;
    }

    /* Sidebar Clean Styling */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0;
    }

    .sidebar-brand-block {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 0 20px 0;
        border-bottom: 1px solid #F1F5F9;
        margin-bottom: 16px;
    }

    .kalbe-brand-text {
        font-size: 1.15rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #008837 0%, #00B14F 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .sidebar-category-header {
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #94A3B8;
        margin-top: 18px;
        margin-bottom: 10px;
    }

    .sidebar-promo-banner {
        background: linear-gradient(135deg, #008837 0%, #00B14F 100%);
        border-radius: 14px;
        padding: 18px;
        color: #FFFFFF;
        margin-top: 24px;
    }

    .sidebar-promo-banner h4 {
        color: #FFFFFF;
        font-size: 0.95rem;
        font-weight: 700;
        margin: 0 0 6px 0;
    }

    .sidebar-promo-banner p {
        color: #E8F5E9;
        font-size: 0.75rem;
        line-height: 1.4;
        margin: 0 0 12px 0;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SIDEBAR NAVIGATION (BORDERFLOW LEFT DRAWER)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand-block">
        <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
            <rect width="32" height="32" rx="8" fill="url(#kalbe-grad)"/>
            <path d="M9 16C9 12.134 12.134 9 16 9C19.866 9 23 12.134 23 16C23 19.866 19.866 23 16 23" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
            <circle cx="16" cy="16" r="3" fill="white"/>
            <defs>
                <linearGradient id="kalbe-grad" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
                    <stop stop-color="#008837"/>
                    <stop offset="1" stop-color="#00B14F"/>
                </linearGradient>
            </defs>
        </svg>
        <div>
            <div class="kalbe-brand-text">Kalbe Biologics</div>
            <div style="font-size:0.7rem; color:#94A3B8; font-weight:600;">AEC CDT // Lyo Digital Twin</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-category-header">PROCESS NAVIGATION</div>', unsafe_allow_html=True)

    nav_tab = st.radio(
        "Navigation",
        ["Dashboard Overview", "ICH Q8 Design Space", "Physical P&ID Formulation", "Batch Run Datasets"],
        label_visibility="collapsed"
    )

    st.markdown('<div class="sidebar-category-header">CRITICAL PROCESS PARAMETERS (CPPs)</div>', unsafe_allow_html=True)

    preset = st.selectbox(
        "Operational Recipe Preset:",
        [
            "Moderate QbD Sweet Spot (-28°C, 10 Pa)",
            "Conservative Baseline (-32°C, 8 Pa)",
            "Aggressive High-Yield (-22°C, 12 Pa)",
            "Custom Manual Calibration"
        ],
        index=0
    )

    if preset == "Conservative Baseline (-32°C, 8 Pa)":
        init_ts = -32.0
        init_pc = 8.0
    elif preset == "Moderate QbD Sweet Spot (-28°C, 10 Pa)":
        init_ts = -28.0
        init_pc = 10.0
    elif preset == "Aggressive High-Yield (-22°C, 12 Pa)":
        init_ts = -22.0
        init_pc = 12.0
    else:
        init_ts = -28.0
        init_pc = 10.0

    T_shelf_C = st.slider(
        "Shelf Temperature (T_shelf) [°C]:",
        min_value=-35.0,
        max_value=-10.0,
        value=init_ts,
        step=1.0,
        help="Primary drying shelf temperature fluid setpoint."
    )

    P_chamber_Pa = st.slider(
        "Chamber Vacuum (P_c) [Pa]:",
        min_value=4.0,
        max_value=25.0,
        value=init_pc,
        step=1.0,
        help="Chamber total vacuum pressure via sterile N2 bleed."
    )
    st.caption(f"Vacuum: **{P_chamber_Pa * 7.50062:.1f} mTorr** | Sublimation Sat: **{solve_product_temperature(T_shelf_C+273.15, P_chamber_Pa, 0.0, 25.0)-273.15:.1f} °C**")

    st.markdown('<div class="sidebar-category-header">UNCERTAINTY & SHIELDING</div>', unsafe_allow_html=True)

    deploy_guard_rings = st.toggle(
        "Deploy Guard Ring Radiation Shields",
        value=False,
        help="Suppresses edge-vial radiation from chamber walls, mitigating Kv from 31 to 24 W/(m²·K)."
    )

    N_mc = st.select_slider(
        "Monte Carlo Population (Vials):",
        options=[100, 250, 500, 1000],
        value=500,
        help="Number of stochastic realizations for tray non-uniformity."
    )

    T_c_C = st.number_input(
        "Formulation Collapse Temp (T_c) [°C]:",
        value=-29.0,
        step=0.5,
        help="Critical product interface temperature for sucrose/mannitol matrix."
    )

    # Promo / Report Download Banner in Sidebar
    pdf_report_path = PROJECT_ROOT / "report" / "Technical_Report.pdf"
    st.markdown("""
    <div class="sidebar-promo-banner">
        <h4>Technical Report Dossier</h4>
        <p>Download the audited 4-page formal PDF report formatted for Kalbe AEC assessment.</p>
    </div>
    """, unsafe_allow_html=True)

    if pdf_report_path.exists():
        with open(pdf_report_path, "rb") as f:
            pdf_bytes = f.read()
        st.download_button(
            label="Download Technical Report (PDF)",
            data=pdf_bytes,
            file_name="Kalbe_AEC_PSE_Technical_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

# -----------------------------------------------------------------------------
# CORE SIMULATION ENGINE EXECUTION
# -----------------------------------------------------------------------------
T_shelf_K = T_shelf_C + 273.15
Tc_K = T_c_C + 273.15
include_edge = not deploy_guard_rings

with st.spinner("Executing Implicit Moving-Boundary ODE Solver & Monte Carlo Engine..."):
    # Deterministic simulation
    det_run = simulate_primary_drying(T_shelf=T_shelf_K, P_chamber=P_chamber_Pa, Tc=Tc_K)

    # Stochastic Monte Carlo simulation
    mc_run = run_monte_carlo(
        T_shelf=T_shelf_K,
        P_chamber=P_chamber_Pa,
        N=N_mc,
        seed=42,
        store_runs=True,
        include_edge_vials=include_edge
    )

# -----------------------------------------------------------------------------
# TOP NAVIGATION BAR (BORDERFLOW STYLE)
# -----------------------------------------------------------------------------
current_hour = datetime.now().hour
time_greeting = "Good morning" if current_hour < 12 else ("Good afternoon" if current_hour < 18 else "Good evening")

st.markdown(f"""
<div class="top-nav-bar">
    <div class="search-input-box">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" stroke-width="2" style="margin-right:8px;"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
        <span>Search batch ID, recipe CPPs, or sensor tag...</span>
        <span class="shortcut">Ctrl+K</span>
    </div>
    <div class="nav-profile-block">
        <div class="nav-icon-btn" title="Cikarang Sterile Suite Status">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>
        </div>
        <div class="nav-icon-btn" title="Plant Telemetry Alerts">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
            <span class="badge-dot"></span>
        </div>
        <div class="user-profile-card">
            <div class="user-avatar-img">NF</div>
            <div>
                <div class="user-name-text">Naufal Fathin</div>
                <div class="user-role-text">Process Simulation Engineer (PSE) | Kalbe AEC</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# GREETING HEADER WITH DATE & CAMPAIGN FILTER CHIPS
# -----------------------------------------------------------------------------
st.markdown(f"""
<div class="greeting-container">
    <div>
        <h1 class="greeting-title">{time_greeting}, Naufal</h1>
        <p class="greeting-subtitle">Here is the real-time simulation overview and ICH Q8 QbD control space for Lyo Unit 02 (KGM Cikarang).</p>
    </div>
    <div class="greeting-pill-bar">
        <div class="filter-chip">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#008837" stroke-width="2"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/></svg>
            <span>Batch Campaign 2026.Q4</span>
        </div>
        <div class="filter-chip" style="background:#F0FDF4; border-color:#BBF7D0; color:#008837;">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#008837" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
            <span>Cleanroom Grade A / cGMP</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4 BORDERFLOW KPI METRIC CARDS (ROW OF 4)
# -----------------------------------------------------------------------------
k1, k2, k3, k4 = st.columns(4)

time_saved = max(0.0, 17.2 - mc_run.t_dry_mean)
pct_saved = (time_saved / 17.2) * 100
margin = T_c_C - mc_run.T_max_mean
risk_pct = mc_run.risk_of_collapse_pct
capacity_gain_hr = time_saved * 50
batches_gain = int(capacity_gain_hr / 17.2)

with k1:
    st.markdown(f"""
    <div class="kpi-metric-card">
        <div class="card-top-row">
            <div style="display:flex; align-items:center;">
                <div class="card-icon-bubble" style="background:#E8F5E9; color:#008837;">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                </div>
                <span class="card-title-label">Primary Drying Time</span>
            </div>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
        </div>
        <div style="display:flex; align-items:baseline;">
            <span class="kpi-main-num">{mc_run.t_dry_mean:.1f}<span style="font-size:1.0rem; color:#64748B; font-weight:600;"> hrs</span></span>
            <span class="badge-pill-green">↑ {pct_saved:.0f}%</span>
        </div>
        <div class="card-subtext">vs. baseline recipe (-32°C, 17.2 h)</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-metric-card">
        <div class="card-top-row">
            <div style="display:flex; align-items:center;">
                <div class="card-icon-bubble" style="background:#EFF6FF; color:#1D4ED8;">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/></svg>
                </div>
                <span class="card-title-label">Peak Product Temp (T_p)</span>
            </div>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
        </div>
        <div style="display:flex; align-items:baseline;">
            <span class="kpi-main-num">{mc_run.T_max_mean:.1f}<span style="font-size:1.0rem; color:#64748B; font-weight:600;"> °C</span></span>
            <span class="{"badge-pill-green" if margin>=0.2 else ("badge-pill-blue" if margin>=-0.2 else "badge-pill-red")}">{margin:+.2f}°C</span>
        </div>
        <div class="card-subtext">Safety margin to collapse threshold ({T_c_C:.1f}°C)</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-metric-card">
        <div class="card-top-row">
            <div style="display:flex; align-items:center;">
                <div class="card-icon-bubble" style="background:#F0FDF4; color:#00B14F;">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
                </div>
                <span class="card-title-label">Cleanroom Uptime Recovered</span>
            </div>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
        </div>
        <div style="display:flex; align-items:baseline;">
            <span class="kpi-main-num">+{capacity_gain_hr:.0f}<span style="font-size:1.0rem; color:#64748B; font-weight:600;"> h/yr</span></span>
            <span class="badge-pill-green">+{batches_gain} Batches</span>
        </div>
        <div class="card-subtext">Est. Value: IDR 10.0–25.0 Billion</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    pill_c = "badge-pill-green" if risk_pct < 0.1 else ("badge-pill-blue" if risk_pct < 2.0 else "badge-pill-red")
    st.markdown(f"""
    <div class="kpi-metric-card">
        <div class="card-top-row">
            <div style="display:flex; align-items:center;">
                <div class="card-icon-bubble" style="background:#FEF2F2; color:#DC2626;">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                </div>
                <span class="card-title-label">Batch Collapse Risk P(T_p &gt; T_c)</span>
            </div>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
        </div>
        <div style="display:flex; align-items:baseline;">
            <span class="kpi-main-num">{risk_pct:.2f}<span style="font-size:1.0rem; color:#64748B; font-weight:600;"> %</span></span>
            <span class="{pill_c}">{"ICH Q8 Compliant" if risk_pct<0.1 else ("QbD Transition" if risk_pct<2.0 else "Failure Zone")}</span>
        </div>
        <div class="card-subtext">{int(np.sum(mc_run.collapse_arr))} of {N_mc} simulated vials breached limit</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MAIN CONTENT LAYOUT (SPLIT 68% WIDE LEFT / 32% RIGHT)
# -----------------------------------------------------------------------------
col_main, col_side = st.columns([0.68, 0.32])

with col_main:
    # 1. Main Chart Card (BorderFlow style: "Transfers & Volume")
    st.markdown("""
    <div class="white-panel">
        <div class="panel-header-row">
            <div>
                <h3 class="panel-heading">Sublimation Dynamics & Thermal Envelope</h3>
                <p style="font-size:0.8rem; color:#64748B; margin:2px 0 0 0;">Product Interface Temperature Trajectory vs. Formulation Collapse Limit</p>
            </div>
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-size:0.75rem; color:#008837; font-weight:700;">● Median Trajectory</span>
                <span style="font-size:0.75rem; color:#10B981; font-weight:600;">● 5th–95th Confidence Ribbon</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Plotly Combination Chart with BorderFlow light aesthetic & Kalbe Green accents
    fig_main = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.70, 0.30]
    )

    # Shaded confidence band (5th - 95th percentile)
    fig_main.add_trace(go.Scatter(
        x=np.concatenate([mc_run.time_common, mc_run.time_common[::-1]]),
        y=np.concatenate([mc_run.Tp_p95, mc_run.Tp_p5[::-1]]),
        fill='toself',
        fillcolor='rgba(0, 177, 79, 0.12)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        name='5th–95th Percentile Envelope'
    ), row=1, col=1)

    # Median product interface temperature
    fig_main.add_trace(go.Scatter(
        x=mc_run.time_common,
        y=mc_run.Tp_median,
        mode='lines',
        line=dict(color='#008837', width=3),
        name='Median T_p(t)',
        hovertemplate="Time: %{x:.2f} h<br>T_p: %{y:.2f} °C<extra></extra>"
    ), row=1, col=1)

    # Shelf temperature line
    fig_main.add_trace(go.Scatter(
        x=[0, max(mc_run.time_common)],
        y=[T_shelf_C, T_shelf_C],
        mode='lines',
        line=dict(color='#64748B', width=1.5, dash='dot'),
        name=f'Shelf Setpoint ({T_shelf_C:.1f} °C)'
    ), row=1, col=1)

    # Collapse limit line
    fig_main.add_trace(go.Scatter(
        x=[0, max(mc_run.time_common)],
        y=[T_c_C, T_c_C],
        mode='lines',
        line=dict(color='#EF4444', width=2, dash='dash'),
        name=f'Collapse Limit T_c ({T_c_C:.1f} °C)'
    ), row=1, col=1)

    # Dry layer thickness progress (bottom sub-chart)
    fig_main.add_trace(go.Scatter(
        x=det_run.time_hours,
        y=det_run.L_dry * 1000,
        mode='lines',
        line=dict(color='#00B14F', width=2),
        name='Dry Layer L(t) [mm]',
        hovertemplate="Time: %{x:.2f} h<br>Dry Layer: %{y:.2f} mm<extra></extra>"
    ), row=2, col=1)

    fig_main.add_trace(go.Scatter(
        x=[0, max(mc_run.time_common)],
        y=[cfg.L_TOTAL * 1000, cfg.L_TOTAL * 1000],
        mode='lines',
        line=dict(color='#CBD5E1', width=1, dash='dot'),
        name='Total Cake (8.19 mm)'
    ), row=2, col=1)

    fig_main.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        font=dict(family='Plus Jakarta Sans', color='#64748B', size=11),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    fig_main.update_xaxes(gridcolor='#F1F5F9', row=1, col=1)
    fig_main.update_xaxes(title_text="Primary Drying Time [hours]", gridcolor='#F1F5F9', row=2, col=1)
    fig_main.update_yaxes(title_text="Temp [°C]", gridcolor='#F1F5F9', row=1, col=1)
    fig_main.update_yaxes(title_text="Layer [mm]", gridcolor='#F1F5F9', row=2, col=1)

    st.plotly_chart(fig_main, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. Bottom Row Split: Donut Chart + Heat Transfer Breakdown (BorderFlow style)
    b_col1, b_col2 = st.columns(2)

    with b_col1:
        st.markdown("""
        <div class="white-panel" style="height:360px;">
            <div class="panel-header-row">
                <h4 class="panel-heading">Tray Population Status</h4>
                <span class="badge-pill-green">N = 1,000 Vials</span>
            </div>
        """, unsafe_allow_html=True)

        n_safe = N_mc - int(np.sum(mc_run.collapse_arr))
        n_fail = int(np.sum(mc_run.collapse_arr))

        fig_donut = go.Figure(data=[go.Pie(
            labels=['Structurally Sound Vials', 'Perimeter Risk Vials'],
            values=[n_safe, n_fail],
            hole=0.68,
            marker_colors=['#008837', '#EF4444'],
            textinfo='percent',
            hoverinfo='label+value+percent'
        )])

        fig_donut.update_layout(
            height=250,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='#FFFFFF',
            plot_bgcolor='#FFFFFF',
            font=dict(family='Plus Jakarta Sans', color='#334155'),
            annotations=[dict(text=f'<b>{N_mc}</b><br><span style="font-size:11px;color:#94A3B8;">Vials</span>', x=0.5, y=0.5, font_size=16, showarrow=False)],
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
        )

        st.plotly_chart(fig_donut, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with b_col2:
        st.markdown("""
        <div class="white-panel" style="height:360px;">
            <div class="panel-header-row">
                <h4 class="panel-heading">Heat Transfer Breakdown (Kv)</h4>
                <span style="font-size:0.75rem; color:#64748B; font-weight:600;">Energy Influx</span>
            </div>
            <div style="margin-top:14px;">
                <div style="display:flex; justify-content:space-between; font-size:0.83rem; font-weight:600; margin-bottom:4px;">
                    <span>Gas Conduction (Rarefied)</span>
                    <span style="font-family:'JetBrains Mono'; font-weight:700;">58%</span>
                </div>
                <div style="width:100%; height:8px; background:#F1F5F9; border-radius:99px; margin-bottom:14px; overflow:hidden;">
                    <div style="width:58%; height:100%; background:linear-gradient(90deg, #008837, #00B14F); border-radius:99px;"></div>
                </div>

                <div style="display:flex; justify-content:space-between; font-size:0.83rem; font-weight:600; margin-bottom:4px;">
                    <span>Direct Vial-to-Shelf Contact</span>
                    <span style="font-family:'JetBrains Mono'; font-weight:700;">25%</span>
                </div>
                <div style="width:100%; height:8px; background:#F1F5F9; border-radius:99px; margin-bottom:14px; overflow:hidden;">
                    <div style="width:25%; height:100%; background:#00A859; border-radius:99px;"></div>
                </div>

                <div style="display:flex; justify-content:space-between; font-size:0.83rem; font-weight:600; margin-bottom:4px;">
                    <span>Chamber Wall Radiation (Edge Effect)</span>
                    <span style="font-family:'JetBrains Mono'; font-weight:700; color:#EF4444;">17%</span>
                </div>
                <div style="width:100%; height:8px; background:#F1F5F9; border-radius:99px; margin-bottom:14px; overflow:hidden;">
                    <div style="width:17%; height:100%; background:#EF4444; border-radius:99px;"></div>
                </div>

                <p style="font-size:0.75rem; color:#94A3B8; line-height:1.4; margin-top:12px;">
                    Perimeter edge vials absorb +15% to +25% supplementary radiant heat flux from warmer chamber walls, elevating failure risk unless shielded.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

with col_side:
    # 1. Right Card: Comparative Recipe Benchmarks (BorderFlow "Recent Transfers" style)
    st.markdown("""
    <div class="white-panel">
        <div class="panel-header-row">
            <h3 class="panel-heading">Recipe Benchmarks</h3>
            <span style="font-size:0.75rem; color:#008837; font-weight:700; cursor:pointer;">Compare All</span>
        </div>
        <div class="list-item-row">
            <div class="list-icon-pill">CB</div>
            <div>
                <div class="list-title">Conservative Baseline</div>
                <div class="list-subtitle">-32°C Shelf | 8 Pa Vacuum</div>
            </div>
            <div class="list-value-bold">17.2 h</div>
            <span class="badge-pill-green">Safe</span>
        </div>
        <div class="list-item-row" style="background:#F0FDF4; border-color:#BBF7D0;">
            <div class="list-icon-pill" style="background:#008837; color:#FFFFFF;">QbD</div>
            <div>
                <div class="list-title">Moderate Sweet Spot</div>
                <div class="list-subtitle">-28°C Shelf | 10 Pa Vacuum</div>
            </div>
            <div class="list-value-bold" style="color:#008837;">11.2 h</div>
            <span class="badge-pill-green">Optimal</span>
        </div>
        <div class="list-item-row">
            <div class="list-icon-pill" style="background:#FEF2F2; color:#DC2626;">AG</div>
            <div>
                <div class="list-title">Aggressive High-Yield</div>
                <div class="list-subtitle">-22°C Shelf | 12 Pa Vacuum</div>
            </div>
            <div class="list-value-bold" style="color:#DC2626;">6.3 h</div>
            <span class="badge-pill-red">Collapsed</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Right Card: Quick Actions & Engineering Controls (BorderFlow "Quick Actions" style)
    st.markdown("""
    <div class="white-panel">
        <div class="panel-header-row">
            <h3 class="panel-heading">Quick Actions</h3>
        </div>
    """, unsafe_allow_html=True)

    # Interactive action items
    st.markdown("""
    <div class="list-item-row">
        <div class="list-icon-pill">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
        </div>
        <div>
            <div class="list-title">Edge-Vial Shielding State</div>
            <div class="list-subtitle">{"Guard Rings Deployed (0.00% Risk)" if deploy_guard_rings else "Unshielded Vials (Edge Radiating)"}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="list-item-row">
        <div class="list-icon-pill">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
        </div>
        <div>
            <div class="list-title">Audit Dossier PDF</div>
            <div class="list-subtitle">4-Page publication technical report</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if pdf_report_path.exists():
        with open(pdf_report_path, "rb") as f:
            pdf_bytes = f.read()
        st.download_button(
            label="Download Full Technical Report (PDF)",
            data=pdf_bytes,
            file_name="Kalbe_AEC_PSE_Technical_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DETAILED SECONDARY VIEW: ICH Q8 DESIGN SPACE HEATMAP
# -----------------------------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div class="white-panel">
    <div class="panel-header-row">
        <div>
            <h3 class="panel-heading">ICH Q8(R2) Quality by Design (QbD) Design Space</h3>
            <p style="font-size:0.83rem; color:#64748B; margin:2px 0 0 0;">Multidimensional operating space of Shelf Temperature (T_shelf) vs. Chamber Pressure (P_c)</p>
        </div>
        <span class="badge-pill-green">BPOM / ICH Regulatory Framework</span>
    </div>
""", unsafe_allow_html=True)

ds_img_path = PROJECT_ROOT / "outputs" / "figures" / "design_space_heatmap.png"
if ds_img_path.exists():
    st.image(str(ds_img_path), use_container_width=True)
else:
    st.info("Design Space matrix calculation completed. Refresh page.")

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# FOOTER (BORDERFLOW STYLE)
# -----------------------------------------------------------------------------
st.markdown("""
<div style="display:flex; justify-content:space-between; align-items:center; padding:16px 0; border-top:1px solid #E2E8F0; margin-top:20px; font-size:0.8rem; color:#94A3B8;">
    <div>© 2026 PT Kalbe Farma Tbk • Corporate Digital Transformation (CDT) • Advanced Engineering Center (AEC)</div>
    <div style="font-family:'JetBrains Mono';">CANDIDATE: NAUFAL FATHIN (naufaalfathin15@gmail.com)</div>
</div>
""", unsafe_allow_html=True)
