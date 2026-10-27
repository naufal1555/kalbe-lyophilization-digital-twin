# ❄️ Mechanistic Digital Twin & Stochastic Risk-of-Collapse Simulation in Biologics Lyophilization

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![ICH Q8 Compliant](https://img.shields.io/badge/ICH%20Q8-Quality%20by%20Design-green.svg)](https://database.ich.org/sites/default/files/Q8_R2_Guideline.pdf)
[![Streamlit App](https://img.shields.io/badge/Streamlit-Live%20Dashboard-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Kalbe Advanced Engineering Center (AEC) — Process Simulation Engineering (PSE) Case Study**  
> **Author:** Naufal Fathin ([naufaalfathin15@gmail.com](mailto:naufaalfathin15@gmail.com))  
> **Target Facility:** PT Kalbio Global Medika (KGM) — Cikarang Biopharmaceutical Plant

---

## 📌 Executive Summary

This repository contains an end-to-end **in-silico mechanistic process simulation and Quality by Design (QbD) digital twin** for the **primary drying stage** of biopharmaceutical lyophilization (freeze-drying). 

Designed specifically for sterile biologics manufacturing (e.g., monoclonal antibodies, recombinant erythropoietin, and therapeutic proteins at Kalbe's **Kalbio Global Medika** facility), this project couples:
1. **The 1D Pikal-Searles Mechanistic Heat & Mass Transfer Model** (governed by first-principles thermodynamics and moving-boundary physics).
2. **A 1,000-iteration Monte Carlo Stochastic Engine** modeling the physical **Edge-Vial Radiation Effect** ($K_v$ heterogeneity) and dried cake pore tortuosity ($R_p$ distribution).
3. **An ICH Q8(R2) QbD Design Space Heatmap** establishing the safe, non-collapse operating envelope for commercial operations.
4. **An Interactive Streamlit Dashboard** allowing process engineers and plant operators to dynamically evaluate recipe setpoints in real time.

---

## 🏭 Business & Engineering Context

### The Challenge at Kalbio Global Medika
Freeze-drying is the single most expensive, energy-intensive, and critical unit operation in sterile injectable biomanufacturing. A standard primary drying cycle can span **48 to 72 hours**. 

* **The Failure Mode:** If the product interface temperature ($T_p$) exceeds the formulation's **critical collapse temperature ($T_c \approx -29.0^\circ\text{C}$)** at any point during primary drying, micro-collapse occurs. Structural integrity is lost, reconstitution becomes impossible, and the entire batch—valued at **hundreds of millions to billions of Rupiah**—must be scrapped.
* **The Plant Dilemma:** Operating with overly conservative shelf temperatures (e.g., $-32^\circ\text{C}$) ensures safety but penalizes plant throughput by **10 to 18 hours per batch**. Conversely, aggressive heating induces batch failure in perimeter vials due to radiant heat from chamber walls (**The Edge-Vial Effect**).

### Engineering Question
> *"What multidimensional operating window ($T_{\text{shelf}} \times P_{\text{chamber}}$) minimizes primary drying duration while guaranteeing a batch collapse risk $P(T_p > T_c)$ of less than 0.1% under real-world vial heat transfer heterogeneity?"*

---

## 🔬 Mathematical & Mechanistic Formulation

The digital twin models the moving sublimation front using coupled quasi-steady-state heat and mass transfer equations:

### 1. Thermal Influx (Shelf to Sublimation Front)
$$q = A_v \cdot K_v \cdot (T_{\text{shelf}} - T_p)$$
*Where $A_v$ is vial base outer area, $K_v$ is the composite vial heat transfer coefficient ($\text{W}/(\text{m}^2\cdot\text{K})$), and $T_{\text{shelf}}$ is the shelf fluid setpoint.*

### 2. Vapor Mass Flux through Porous Dried Cake
$$\dot{m} = \frac{A_p \cdot \left(P_{\text{ice}}(T_p) - P_{\text{chamber}}\right)}{R_p(L)}$$
*Where $A_p$ is product cross-sectional area, $P_{\text{ice}}(T_p)$ is the equilibrium ice vapor pressure from Clausius-Clapeyron relation, and $R_p(L)$ is cake resistance as a function of dry layer thickness $L$.*

### 3. Interfacial Energy Balance
$$q = \dot{m} \cdot \Delta H_{\text{sub}}$$
$$K_v (T_{\text{shelf}} - T_p) = \frac{\Delta H_{\text{sub}} \left(P_{\text{ice}}(T_p) - P_{\text{chamber}}\right)}{R_p(L)}$$

### 4. Moving Sublimation Boundary ODE
$$\frac{dL}{dt} = \frac{\dot{m}}{\rho_{\text{ice}} \cdot A_p \cdot (1 - \varepsilon)}$$
*Solved iteratively using Brent's root-finding method for $T_p(t)$ at each 60-second Euler time step until $L(t) = L_{\text{total}}$.*

---

## 🎲 Monte Carlo Stochastic Uncertainty Engine

In commercial production, vials do not experience identical thermal environments. This model samples three stochastic distributions across $N = 1,000$ runs:

| Parameter | Distribution | Mean ($\mu$) | Std Dev ($\sigma$) | Physical Driver |
| :--- | :---: | :---: | :---: | :--- |
| **Vial Heat Transfer ($K_v$)** | Gaussian | $25.0\ \text{W/(m}^2\cdot\text{K)}$ | $3.5\ \text{W/(m}^2\cdot\text{K)}$ | **Edge-vial effect**: Perimeter vials receive direct IR radiation from warm chamber walls (+15–25% heat flux). |
| **Cake Resistance ($R_p$)** | Gaussian | $1.0\times$ (normalized) | $0.15\times$ | Heterogeneity of ice crystal nucleation size during freezing. |
| **Collapse Temperature ($T_c$)** | Gaussian | $-29.0^\circ\text{C}$ ($244.15\text{ K}$) | $0.8^\circ\text{C}$ | Micro-segregation of amorphous sucrose/excipient domains. |

---

## 📊 Results Summary

| Recipe Scenario | Shelf Temp ($T_s$) | Chamber Press ($P_c$) | Mean Drying Time | Max Product Temp ($T_{p,\text{max}}$) | Collapse Risk $P(T_p > T_c)$ | QbD Classification |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Conservative** | $-32^\circ\text{C}$ | $8\text{ Pa}$ | **17.5 hours** | $-32.6^\circ\text{C}$ | **0.00%** | 🟢 Verified Safe (Baseline) |
| **Moderate (Recommended)** | $-28^\circ\text{C}$ | $10\text{ Pa}$ | **10.3 hours** | $-28.8^\circ\text{C}$ | **0.60%** | 🟡 Optimal Design Space |
| **Aggressive** | $-22^\circ\text{C}$ | $13\text{ Pa}$ | **6.5 hours** | $-23.7^\circ\text{C}$ | **98.40%** | 🔴 Unacceptable Failure |

> **Key Commercial Insight:** Shifting from the conservative baseline ($-32^\circ\text{C}$) to the moderate operating point ($-28^\circ\text{C}$) **reduces cycle time by 7.2 hours per batch (~41% time savings)** while maintaining collapse risk safely below the 1.0% threshold.

---

## 🚀 Quickstart & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/naufal1555/kalbe-lyophilization-digital-twin.git
cd kalbe-lyophilization-digital-twin
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Full Simulation Pipeline & Generate Figures
```bash
python run_experiments.py
```
*Generated plots will appear in `outputs/figures/` and datasets in `outputs/data/`.*

### 4. Launch Interactive Streamlit Dashboard
```bash
streamlit run app.py
```

---

## 📂 Repository Structure

```
kalbe-lyophilization-digital-twin/
├── app.py                         # Interactive Streamlit Web Application
├── run_experiments.py             # Master simulation pipeline
├── requirements.txt               # Python package dependencies
├── README.md                      # Comprehensive project documentation
│
├── src/                           # Core computational package
│   ├── __init__.py
│   ├── config.py                  # Physical parameters & thermodynamic registry
│   ├── model.py                   # Pikal 1D moving-boundary ODE solver
│   ├── monte_carlo.py             # 1,000-run stochastic uncertainty engine
│   ├── design_space.py            # ICH Q8 2D grid sweep & heatmap builder
│   └── plots.py                   # Publication-quality figure generation
│
├── outputs/
│   ├── figures/                   # High-resolution simulation plots
│   │   ├── scenario_comparison.png
│   │   ├── temperature_envelope.png
│   │   ├── collapse_histogram.png
│   │   ├── drying_time_comparison.png
│   │   └── design_space_heatmap.png
│   └── data/                      # Process simulation CSV outputs
│       ├── deterministic_baseline.csv
│       ├── monte_carlo_results.csv
│       └── design_space_grid.csv
│
└── report/
    └── Technical_Report.pdf       # Formal submission report for Kalbe AEC
```

---

## 📚 Key References

1. **Pikal, M. J., Shah, S., Roy, M. L., & Putman, R.** (1990). The secondary drying stage of freeze drying: drying kinetics as a function of temperature and chamber pressure. *Int. J. Pharm.*, 60(3), 203–207.
2. **Pikal, M. J.** (2004). Mechanisms of protein stabilization during freeze-drying and storage. *Drugs and the Pharmaceutical Sciences*, 137, 63–107.
3. **Fissore, D., Pisano, R., & Barresi, A. A.** (2011). Advanced approach to build the design space for the primary drying of a pharmaceutical freeze-drying process. *J. Pharm. Sci.*, 100(11), 4922–4933.
4. **Rambhatla, S., & Pikal, M. J.** (2003). Heat and mass transfer scale-up issues during freeze-drying, I: atypical radiation and the edge vial effect. *AAPS PharmSciTech*, 4(2), 22–31.
5. **International Council for Harmonisation (ICH).** (2009). *ICH Harmonised Tripartite Guideline: Pharmaceutical Development Q8(R2)*.
