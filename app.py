"""
app.py — Kalbe AEC Biologics Lyophilization Digital Twin Console
================================================================================
Industrial-Grade Process Simulation & ICH Q8(R2) Quality by Design (QbD) Console
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

# Setup path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src import config as cfg
from src.model import simulate_primary_drying, solve_product_temperature
from src.monte_carlo import run_monte_carlo

# Page Configuration
st.set_page_config(
    page_title="Kalbe AEC | Lyo Digital Twin Console",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# HIGH-END INDUSTRIAL STYLING & BESPOKE TYPOGRAPHY
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Global Background & Contrast */
    .stApp {
        background-color: #0B0F17;
        color: #E2E8F0;
    }

    /* Top Industrial Telemetry Header */
    .top-header-strip {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 20px;
        background: #111827;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        margin-bottom: 20px;
    }

    .brand-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.15rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #F8FAFC;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .brand-tag {
        background: rgba(0, 163, 255, 0.12);
        color: #00A3FF;
        border: 1px solid rgba(0, 163, 255, 0.3);
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-family: 'JetBrains Mono', monospace;
    }

    .telemetry-status {
        display: flex;
        align-items: center;
        gap: 8px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #94A3B8;
    }

    .pulse-dot {
        width: 8px;
        height: 8px;
        background-color: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 8px #10B981;
        display: inline-block;
        animation: pulse-ring 2s infinite;
    }

    @keyframes pulse-ring {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    /* Subtitle Banner */
    .header-sub {
        font-size: 0.85rem;
        color: #64748B;
        margin-top: -12px;
        margin-bottom: 20px;
    }

    /* Double-Bezel Hardware KPI Card */
    .hardware-card {
        background: #111827;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 16px 18px;
        position: relative;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
        transition: border-color 0.2s ease;
    }

    .hardware-card:hover {
        border-color: rgba(0, 163, 255, 0.4);
    }

    .tag-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #64748B;
        margin-bottom: 6px;
    }

    .kpi-mono-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2.0rem;
        font-weight: 700;
        color: #F8FAFC;
        line-height: 1.1;
    }

    .kpi-unit {
        font-size: 0.9rem;
        font-weight: 500;
        color: #94A3B8;
        margin-left: 4px;
    }

    .pill-badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
        margin-top: 8px;
    }

    .pill-safe {
        background: rgba(16, 185, 129, 0.12);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.25);
    }

    .pill-warn {
        background: rgba(245, 158, 11, 0.12);
        color: #F59E0B;
        border: 1px solid rgba(245, 158, 11, 0.25);
    }

    .pill-danger {
        background: rgba(239, 68, 68, 0.12);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.25);
    }

    .caption-meta {
        font-size: 0.75rem;
        color: #64748B;
        margin-top: 6px;
    }

    /* Sidebar Clean Styling */
    section[data-testid="stSidebar"] {
        background-color: #0D121F;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    .sidebar-section-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #00A3FF;
        margin-top: 14px;
        margin-bottom: 8px;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #0D121F;
        padding: 6px;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }

    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
        color: #94A3B8;
        border: none !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: #1E293B !important;
        color: #F8FAFC !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TOP TELEMETRY BAR
# -----------------------------------------------------------------------------
st.markdown("""
<div class="top-header-strip">
    <div class="brand-title">
        <span>PT KALBIO GLOBAL MEDIKA</span>
        <span class="brand-tag">LYO-02 DIGITAL TWIN</span>
        <span style="font-size:0.75rem; color:#64748B; font-weight:500;">| Cikarang Biologics Manufacturing</span>
    </div>
    <div class="telemetry-status">
        <span class="pulse-dot"></span>
        <span>ENGINE STATUS: <strong>QUASI-STEADY ODE SOLVER ACTIVE</strong></span>
        <span style="margin-left:12px; color:#475569;">|</span>
        <span style="margin-left:12px;">REGULATORY: <strong>ICH Q8(R2) QbD</strong></span>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SIDEBAR CONTROLS (OPERATING CONSOLE)
# -----------------------------------------------------------------------------
st.sidebar.markdown('<div class="sidebar-section-title">CONTROL DECK // RECIPE SELECTION</div>', unsafe_allow_html=True)

preset = st.sidebar.selectbox(
    "Recipe Presets:",
    [
        "Conservative Baseline (-32°C, 8 Pa)",
        "Moderate QbD Sweet Spot (-28°C, 10 Pa)",
        "Aggressive High-Yield (-22°C, 12 Pa)",
        "Custom Manual Calibration"
    ],
    index=1
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

st.sidebar.markdown('<div class="sidebar-section-title">CRITICAL PROCESS PARAMETERS (CPPs)</div>', unsafe_allow_html=True)

T_shelf_C = st.sidebar.slider(
    "Shelf Temperature (T_shelf) [°C]:",
    min_value=-35.0,
    max_value=-10.0,
    value=init_ts,
    step=1.0,
    help="Primary drying shelf temperature fluid setpoint."
)

P_chamber_Pa = st.sidebar.slider(
    "Chamber Vacuum Pressure (P_c) [Pa]:",
    min_value=4.0,
    max_value=25.0,
    value=init_pc,
    step=1.0,
    help="Chamber total gas pressure controlled via sterile N2 bleed (10 Pa ≈ 75 mTorr)."
)
st.sidebar.caption(f"Equivalent Vacuum: {P_chamber_Pa * 7.50062:.1f} mTorr | Sublimation Saturation: {solve_product_temperature(T_shelf_C+273.15, P_chamber_Pa, 0.0, 25.0)-273.15:.1f} °C")

st.sidebar.markdown('<div class="sidebar-section-title">UNCERTAINTY & EDGE-VIAL MITIGATION</div>', unsafe_allow_html=True)

deploy_guard_rings = st.sidebar.toggle(
    "Deploy Edge-Vial Radiation Shields (Guard Rings)",
    value=False,
    help="When active, models physical thermal radiation cages or sacrificial dummy vials surrounding the tray perimeter, suppressing edge Kv from 31 to 24 W/(m²·K)."
)

N_mc = st.sidebar.select_slider(
    "Monte Carlo Population (Vials):",
    options=[100, 250, 500, 1000],
    value=500,
    help="Number of stochastic realizations evaluating tray thermal non-uniformity."
)

T_c_C = st.sidebar.number_input(
    "Formulation Collapse Temp (T_c) [°C]:",
    value=-29.0,
    step=0.5,
    help="Critical product interface temperature above which amorphous sucrose cake loses structural pore channels."
)

st.sidebar.markdown("---")

# Download report button in sidebar
pdf_report_path = PROJECT_ROOT / "report" / "Technical_Report.pdf"
if pdf_report_path.exists():
    with open(pdf_report_path, "rb") as f:
        pdf_bytes = f.read()
    st.sidebar.download_button(
        label="Download Full Technical Report (PDF)",
        data=pdf_bytes,
        file_name="Kalbe_AEC_PSE_Technical_Report.pdf",
        mime="application/pdf",
        use_container_width=True
    )

st.sidebar.caption("Kalbe AEC Process Simulation Engineering Assessment | Candidate: Naufal Fathin")

# -----------------------------------------------------------------------------
# CORE SIMULATION EXECUTION
# -----------------------------------------------------------------------------
T_shelf_K = T_shelf_C + 273.15
Tc_K = T_c_C + 273.15
include_edge = not deploy_guard_rings

with st.spinner("Executing Implicit Moving-Boundary ODE Solver & Monte Carlo Engine..."):
    # Deterministic run
    det_run = simulate_primary_drying(T_shelf=T_shelf_K, P_chamber=P_chamber_Pa, Tc=Tc_K)

    # Stochastic Monte Carlo run
    mc_run = run_monte_carlo(
        T_shelf=T_shelf_K,
        P_chamber=P_chamber_Pa,
        N=N_mc,
        seed=42,
        store_runs=True,
        include_edge_vials=include_edge
    )

# -----------------------------------------------------------------------------
# HARDWARE TELEMETRY CARDS (TOP ROW)
# -----------------------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown('<div class="hardware-card">', unsafe_allow_html=True)
    st.markdown('<div class="tag-label">[TM-01] PRIMARY DRYING DURATION</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-mono-val">{mc_run.t_dry_mean:.1f}<span class="kpi-unit">hours</span></div>', unsafe_allow_html=True)
    time_saved = max(0.0, 17.2 - mc_run.t_dry_mean)
    pct_saved = (time_saved / 17.2) * 100
    st.markdown(f'<div class="pill-badge pill-safe">-{time_saved:.1f} h ({pct_saved:.0f}%) vs Baseline</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="caption-meta">95% CI: [{mc_run.t_dry_mean - 1.96*mc_run.t_dry_std:.1f}, {mc_run.t_dry_mean + 1.96*mc_run.t_dry_std:.1f}] h</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="hardware-card">', unsafe_allow_html=True)
    st.markdown('<div class="tag-label">[TE-101] PEAK PRODUCT TEMP (T_p,max)</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-mono-val">{mc_run.T_max_mean:.1f}<span class="kpi-unit">°C</span></div>', unsafe_allow_html=True)
    margin = T_c_C - mc_run.T_max_mean
    pill_class = "pill-safe" if margin >= 0.5 else ("pill-warn" if margin >= -0.2 else "pill-danger")
    st.markdown(f'<div class="pill-badge {pill_class}">Safety Margin: {margin:+.2f} °C</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="caption-meta">Formulation Collapse Threshold: {T_c_C:.1f} °C</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c3:
    st.markdown('<div class="hardware-card">', unsafe_allow_html=True)
    st.markdown('<div class="tag-label">[QA-01] BATCH COLLAPSE RISK P(T_p > T_c)</div>', unsafe_allow_html=True)
    risk_pct = mc_run.risk_of_collapse_pct
    pill_risk = "pill-safe" if risk_pct < 0.1 else ("pill-warn" if risk_pct < 2.0 else "pill-danger")
    st.markdown(f'<div class="kpi-mono-val" style="color:{"#10B981" if risk_pct<0.1 else ("#F59E0B" if risk_pct<2.0 else "#EF4444")}">{risk_pct:.2f}<span class="kpi-unit">%</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="pill-badge {pill_risk}">{"ICH Q8 COMPLIANT" if risk_pct<0.1 else ("QbD TRANSITION" if risk_pct<2.0 else "UNACCEPTABLE RISK")}</div>', unsafe_allow_html=True)
    n_collapsed = int(np.sum(mc_run.collapse_arr))
    st.markdown(f'<div class="caption-meta">{n_collapsed} of {N_mc} simulated vials breached limit</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c4:
    st.markdown('<div class="hardware-card">', unsafe_allow_html=True)
    st.markdown('<div class="tag-label">[OPS-02] COMMERCIAL CAPACITY RECOVERY</div>', unsafe_allow_html=True)
    capacity_gain_hr = time_saved * 50
    st.markdown(f'<div class="kpi-mono-val">+{capacity_gain_hr:.0f}<span class="kpi-unit">h/year</span></div>', unsafe_allow_html=True)
    batches_gain = int(capacity_gain_hr / 17.2)
    st.markdown(f'<div class="pill-badge pill-safe">+{batches_gain} Production Batches / Yr</div>', unsafe_allow_html=True)
    st.markdown('<div class="caption-meta">Est. Cleanroom Value: IDR 10–25 Billion</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# WORKSTATION INTERACTIVE TABS
# -----------------------------------------------------------------------------
tab_traj, tab_risk, tab_ds, tab_physics = st.tabs([
    "DYNAMICS // Thermal Envelope & Front Trajectory",
    "HETEROGENEITY // Edge-Vial Distribution",
    "QUALITY BY DESIGN // ICH Q8 Design Space",
    "FIRST PRINCIPLES // P&ID & Governing Equations"
])

# -----------------------------------------------------------------------------
# TAB 1: DYNAMICS (INTERACTIVE PLOTLY)
# -----------------------------------------------------------------------------
with tab_traj:
    fig_dyn = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=(
            "Product Interface Temperature Trajectory vs Critical Collapse Boundary T_c",
            "Sublimation Front Progression (Moving Boundary L(t))"
        ),
        row_heights=[0.65, 0.35]
    )

    # 5th-95th confidence ribbon
    fig_dyn.add_trace(go.Scatter(
        x=np.concatenate([mc_run.time_common, mc_run.time_common[::-1]]),
        y=np.concatenate([mc_run.Tp_p95, mc_run.Tp_p5[::-1]]),
        fill='toself',
        fillcolor='rgba(0, 163, 255, 0.15)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        name='5th–95th Percentile Envelope'
    ), row=1, col=1)

    # Median trajectory
    fig_dyn.add_trace(go.Scatter(
        x=mc_run.time_common,
        y=mc_run.Tp_median,
        mode='lines',
        line=dict(color='#00A3FF', width=2.5),
        name='Median T_p(t)',
        hovertemplate="Time: %{x:.2f} h<br>T_p: %{y:.2f} °C<extra></extra>"
    ), row=1, col=1)

    # Shelf Temperature setpoint line
    fig_dyn.add_trace(go.Scatter(
        x=[0, max(mc_run.time_common)],
        y=[T_shelf_C, T_shelf_C],
        mode='lines',
        line=dict(color='#64748B', width=1.5, dash='dot'),
        name=f'Shelf Temp ({T_shelf_C:.1f} °C)'
    ), row=1, col=1)

    # Collapse Limit line
    fig_dyn.add_trace(go.Scatter(
        x=[0, max(mc_run.time_common)],
        y=[T_c_C, T_c_C],
        mode='lines',
        line=dict(color='#EF4444', width=2, dash='dash'),
        name=f'Collapse Limit T_c ({T_c_C:.1f} °C)'
    ), row=1, col=1)

    # Dry layer thickness
    fig_dyn.add_trace(go.Scatter(
        x=det_run.time_hours,
        y=det_run.L_dry * 1000,
        mode='lines',
        line=dict(color='#10B981', width=2.5),
        name='Dry Layer Thickness L(t)',
        hovertemplate="Time: %{x:.2f} h<br>Thickness: %{y:.2f} mm<extra></extra>"
    ), row=2, col=1)

    # Total cake height line
    fig_dyn.add_trace(go.Scatter(
        x=[0, max(mc_run.time_common)],
        y=[cfg.L_TOTAL * 1000, cfg.L_TOTAL * 1000],
        mode='lines',
        line=dict(color='#94A3B8', width=1, dash='dot'),
        name=f'Total Cake L_total ({cfg.L_TOTAL*1000:.1f} mm)'
    ), row=2, col=1)

    fig_dyn.update_layout(
        height=580,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='#111827',
        font=dict(family='Plus Jakarta Sans', color='#94A3B8'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    fig_dyn.update_xaxes(gridcolor='rgba(255,255,255,0.06)', row=1, col=1)
    fig_dyn.update_xaxes(title_text="Time [hours]", gridcolor='rgba(255,255,255,0.06)', row=2, col=1)
    fig_dyn.update_yaxes(title_text="Temperature [°C]", gridcolor='rgba(255,255,255,0.06)', row=1, col=1)
    fig_dyn.update_yaxes(title_text="Thickness [mm]", gridcolor='rgba(255,255,255,0.06)', row=2, col=1)

    st.plotly_chart(fig_dyn, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 2: HETEROGENEITY & EDGE VIALS (INTERACTIVE PLOTLY)
# -----------------------------------------------------------------------------
with tab_risk:
    col_r1, col_r2 = st.columns([0.65, 0.35])

    with col_r1:
        # Histogram of T_max
        fig_hist = go.Figure()

        safe_temps = mc_run.T_max_C_arr[~mc_run.collapse_arr]
        fail_temps = mc_run.T_max_C_arr[mc_run.collapse_arr]

        fig_hist.add_trace(go.Histogram(
            x=safe_temps,
            name='Structurally Intact Vials (T_p ≤ T_c)',
            marker_color='#10B981',
            opacity=0.85,
            nbinsx=30
        ))

        if len(fail_temps) > 0:
            fig_hist.add_trace(go.Histogram(
                x=fail_temps,
                name='Collapsed Perimeter Vials (T_p > T_c)',
                marker_color='#EF4444',
                opacity=0.85,
                nbinsx=15
            ))

        fig_hist.add_vline(
            x=T_c_C,
            line_width=2,
            line_dash="dash",
            line_color="#EF4444",
            annotation_text=f"Collapse Limit ({T_c_C:.1f}°C)",
            annotation_position="top right"
        )

        fig_hist.update_layout(
            barmode='stack',
            title="Population Distribution of Peak Sublimation Temperature (T_p,max)",
            xaxis_title="Peak Product Temperature [°C]",
            yaxis_title="Vial Count",
            height=440,
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='#111827',
            font=dict(family='Plus Jakarta Sans', color='#94A3B8'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_hist.update_xaxes(gridcolor='rgba(255,255,255,0.06)')
        fig_hist.update_yaxes(gridcolor='rgba(255,255,255,0.06)')

        st.plotly_chart(fig_hist, use_container_width=True)

    with col_r2:
        st.markdown("""
        <div class="hardware-card" style="height:100%;">
            <div class="tag-label">PHYSICAL MECHANISM // EDGE-VIAL RADIATION</div>
            <p style="font-size:0.83rem; line-height:1.5; color:#CBD5E1; margin-top:8px;">
                In industrial lyophilizers, vials situated along tray borders and corners absorb diffuse infrared radiation from warmer chamber walls and doors.
            </p>
            <ul style="font-size:0.8rem; color:#94A3B8; padding-left:16px;">
                <li><strong>Perimeter Vials:</strong> K_v elevated by +15% to +25% (up to 31 W/m²·K).</li>
                <li><strong>Center Vials:</strong> K_v tightly clustered near 22 W/m²·K.</li>
                <li><strong>The Consequence:</strong> Cake collapse is <em>strictly localized</em> to the outer perimeter rows rather than evenly distributed.</li>
            </ul>
            <div style="margin-top:14px; padding:10px; background:rgba(0,163,255,0.06); border:1px solid rgba(0,163,255,0.2); border-radius:8px;">
                <span style="font-size:0.75rem; font-weight:700; color:#00A3FF; font-family:'JetBrains Mono';">RECOMMENDED MITIGATION:</span>
                <p style="font-size:0.78rem; color:#E2E8F0; margin:4px 0 0 0;">
                    Surround commercial batches with 1 border row of empty 'dummy' vials or deploy stainless-steel thermal radiation shields (guard rings). This reduces collapse risk from 57% to 0.00% without reducing shelf temperature.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 3: QUALITY BY DESIGN (ICH Q8 HEATMAP)
# -----------------------------------------------------------------------------
with tab_ds:
    st.markdown("""
    <div style="margin-bottom:12px;">
        <span class="tag-label">ICH Q8(R2) REGULATORY COMPLIANCE // DESIGN SPACE MULTIDIMENSIONAL MATRIX</span>
        <p style="font-size:0.85rem; color:#94A3B8; margin-top:4px;">
            The multidimensional combination of shelf temperature setpoint and chamber vacuum pressure that has been demonstrated to provide quality assurance. Operating anywhere inside the green envelope constitutes an approved state under BPOM / EMA regulations.
        </p>
    </div>
    """, unsafe_allow_html=True)

    ds_img_path = PROJECT_ROOT / "outputs" / "figures" / "design_space_heatmap.png"
    if ds_img_path.exists():
        st.image(str(ds_img_path), use_container_width=True)
    else:
        st.info("Computing Design Space Matrix... Refreshing...")

    col_q1, col_q2, col_q3 = st.columns(3)
    with col_q1:
        st.markdown("""
        <div class="hardware-card">
            <span class="pill-badge pill-safe">GREEN ENVELOPE: PROVEN SAFE</span>
            <p style="font-size:0.8rem; color:#CBD5E1; margin-top:8px;">
                <strong>Ts ≤ -30°C across 6–16 Pa:</strong> Risk of collapse P(collapse) &lt; 0.1%. Guaranteed structural preservation for commercial batch release.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_q2:
        st.markdown("""
        <div class="hardware-card">
            <span class="pill-badge pill-warn">YELLOW: TRANSITION SWEET SPOT</span>
            <p style="font-size:0.8rem; color:#CBD5E1; margin-top:8px;">
                <strong>Ts = -28°C:</strong> Maximum cycle acceleration. Requires either in-line PAT monitoring (TDLAS/MTM) or physical perimeter guard ring shielding.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_q3:
        st.markdown("""
        <div class="hardware-card">
            <span class="pill-badge pill-danger">RED ENVELOPE: UNACCEPTABLE</span>
            <p style="font-size:0.8rem; color:#CBD5E1; margin-top:8px;">
                <strong>Ts &gt; -26°C:</strong> Catastrophic bulk melt-back. Cake structure seals, producing un-reconstitutable commercial product rejected by QC.
            </p>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 4: PROCESS PHYSICS & FIRST PRINCIPLES
# -----------------------------------------------------------------------------
with tab_physics:
    col_p1, col_p2 = st.columns([0.45, 0.55])

    with col_p1:
        st.markdown("""
        <div class="hardware-card">
            <div class="tag-label">P&ID SCHEMATIC // CONTROL VOLUME MODEL</div>
            <div style="text-align:center; padding:15px 0;">
                <svg width="280" height="220" viewBox="0 0 280 220" style="background:#0D121F; border-radius:8px; border:1px solid rgba(255,255,255,0.08);">
                    <!-- Heated Shelf -->
                    <rect x="20" y="190" width="240" height="18" fill="#1E293B" stroke="#00A3FF" stroke-width="1.5" rx="3"/>
                    <text x="140" y="203" fill="#00A3FF" font-size="10" font-family="JetBrains Mono" text-anchor="middle">SHELF FLUID [T_shelf = -28°C]</text>
                    
                    <!-- Vial Glass -->
                    <rect x="70" y="30" width="140" height="150" fill="none" stroke="#64748B" stroke-width="2" rx="4"/>
                    
                    <!-- Frozen Layer -->
                    <rect x="72" y="110" width="136" height="68" fill="rgba(0, 163, 255, 0.25)" stroke="#00A3FF" stroke-dasharray="3,3"/>
                    <text x="140" y="150" fill="#F8FAFC" font-size="11" font-family="JetBrains Mono" font-weight="bold" text-anchor="middle">FROZEN ICE CORE</text>
                    
                    <!-- Sublimation Front -->
                    <line x1="72" y1="110" x2="208" y2="110" stroke="#EF4444" stroke-width="2.5"/>
                    <text x="140" y="104" fill="#EF4444" font-size="10" font-family="JetBrains Mono" font-weight="bold" text-anchor="middle">INTERFACE [T_p]</text>
                    
                    <!-- Dry Cake -->
                    <rect x="72" y="32" width="136" height="76" fill="rgba(245, 158, 11, 0.15)"/>
                    <text x="140" y="65" fill="#F59E0B" font-size="10" font-family="JetBrains Mono" text-anchor="middle">POROUS DRY CAKE [Rp(L)]</text>
                    
                    <!-- Vapor Flux Arrows -->
                    <path d="M 140 50 L 140 20" stroke="#E2E8F0" stroke-width="2" marker-end="url(#arrow)"/>
                    <text x="140" y="15" fill="#E2E8F0" font-size="10" font-family="JetBrains Mono" text-anchor="middle">dm/dt [CHAMBER VACUUM P_c]</text>
                </svg>
            </div>
            <p style="font-size:0.75rem; color:#94A3B8; margin-top:8px; line-height:1.4;">
                Quasi-steady 1D formulation balancing conductive-radiant heat input (q_in) against latent heat sublimation removal (q_sub) through porous Darcy-Knudsen vapor diffusion.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_p2:
        st.markdown('<div class="tag-label">CALIBRATED THERMODYNAMIC PARAMETERS (SI UNITS)</div>', unsafe_allow_html=True)
        param_table = pd.DataFrame([
            {"Parameter": "Latent Heat of Sublimation (ΔH_sub)", "Value": "2.839 × 10⁶ J/kg", "Literature Reference": "CRC Handbook of Chemistry & Physics"},
            {"Parameter": "Ice Density & Porosity (ρ_ice, ε)", "Value": "917 kg/m³, 0.92", "Literature Reference": "Pikal et al. (2004)"},
            {"Parameter": "Mean Vial Heat Transfer (Kv)", "Value": "25.0 ± 3.5 W/(m²·K)", "Literature Reference": "Rambhatla & Pikal (2003)"},
            {"Parameter": "Initial Cake Resistance (R0)", "Value": "3.60 × 10⁵ Pa·s·m²/kg", "Literature Reference": "Fissore, Pisano, & Barresi (2011)"},
            {"Parameter": "Resistance Growth Slope (A1)", "Value": "4.20 × 10⁸ Pa·s·m/kg", "Literature Reference": "Pisano et al. (2011)"},
            {"Parameter": "Formulation Collapse Temp (Tc)", "Value": "-29.0 ± 0.8 °C", "Literature Reference": "Freeze-Drying Microscopy Benchmark"},
            {"Parameter": "Standard Tubing Vial", "Value": "Schott 10R (OD 24mm, 3mL Fill)", "Literature Reference": "KGM Commercial Packaging Spec"}
        ])
        st.dataframe(param_table, hide_index=True, use_container_width=True)

st.markdown("---")
st.markdown("""
<div style="display:flex; justify-content:space-between; align-items:center; font-size:0.75rem; color:#64748B; font-family:'JetBrains Mono';">
    <div>PT KALBE FARMA TBK | CORPORATE DIGITAL TRANSFORMATION (CDT) | ADVANCED ENGINEERING CENTER (AEC)</div>
    <div>CANDIDATE: NAUFAL FATHIN (naufaalfathin15@gmail.com)</div>
</div>
""", unsafe_allow_html=True)
