import json
from pathlib import Path

notebook = {
    'cells': [
        {
            'cell_type': 'markdown',
            'metadata': {},
            'source': [
                '# ❄️ Mechanistic Digital Twin & Stochastic Risk-of-Collapse Simulation\n',
                '## Biologics Lyophilization Primary Drying — Kalbe AEC Case Study\n',
                '**Facility:** PT Kalbio Global Medika (KGM) — Cikarang Biopharmaceutical Plant  \n',
                '**Methodology:** Pikal 1D Moving-Boundary Heat & Mass Transfer + Monte Carlo Uncertainty (ICH Q8 QbD)\n'
            ]
        },
        {
            'cell_type': 'code',
            'execution_count': 1,
            'metadata': {},
            'outputs': [],
            'source': [
                'import sys\n',
                'from pathlib import Path\n',
                'PROJECT_ROOT = Path("..").resolve()\n',
                'sys.path.insert(0, str(PROJECT_ROOT))\n',
                '\n',
                'import numpy as np\n',
                'import pandas as pd\n',
                'import matplotlib.pyplot as plt\n',
                'from src import config as cfg\n',
                'from src.model import run_scenario, simulate_primary_drying\n',
                'from src.monte_carlo import run_monte_carlo\n',
                'from src.plots import (\n',
                '    plot_deterministic_scenarios,\n',
                '    plot_temperature_envelope,\n',
                '    plot_collapse_histogram,\n',
                '    plot_drying_time_comparison,\n',
                '    plot_design_space\n',
                ')\n',
                'print("Environment initialized successfully!")'
            ]
        },
        {
            'cell_type': 'markdown',
            'metadata': {},
            'source': [
                '### 1. Deterministic Baseline Scenarios\n',
                'Comparing Conservative (-32°C), Moderate (-28°C), and Aggressive (-22°C) cycles.'
            ]
        },
        {
            'cell_type': 'code',
            'execution_count': 2,
            'metadata': {},
            'outputs': [],
            'source': [
                'results = {\n',
                '    name: run_scenario(name)\n',
                '    for name in ["Conservative", "Moderate", "Aggressive"]\n',
                '}\n',
                'for name, res in results.items():\n',
                '    print(f"{name:<12}: Drying={res.drying_time_hr:4.1f} h | Tp_max={res.T_product_max_C:5.1f} °C | Collapsed={res.collapsed}")\n',
                'fig1 = plot_deterministic_scenarios(results, save=False)\n',
                'plt.show()'
            ]
        },
        {
            'cell_type': 'markdown',
            'metadata': {},
            'source': [
                '### 2. Monte Carlo Uncertainty Quantification (N=1,000)\n',
                'Modeling Edge-Vial radiation effect (Kv) and cake pore tortuosity (Rp).'
            ]
        },
        {
            'cell_type': 'code',
            'execution_count': 3,
            'metadata': {},
            'outputs': [],
            'source': [
                't_shelf_mod = cfg.SCENARIOS["Moderate"]["T_shelf"]\n',
                'p_ch_mod = cfg.SCENARIOS["Moderate"]["P_chamber"]\n',
                'mc_mod = run_monte_carlo(t_shelf_mod, p_ch_mod, N=1000, seed=cfg.SEED, store_runs=True)\n',
                'print(f"Mean Drying Time : {mc_mod.t_dry_mean:.2f} ± {mc_mod.t_dry_std:.2f} h")\n',
                'print(f"Risk of Collapse : {mc_mod.risk_of_collapse_pct:.2f}% (P(Tp > Tc))")\n',
                'fig2 = plot_temperature_envelope(mc_mod, save=False)\n',
                'plt.show()\n',
                'fig3 = plot_collapse_histogram(mc_mod, save=False)\n',
                'plt.show()'
            ]
        },
        {
            'cell_type': 'markdown',
            'metadata': {},
            'source': [
                '### 3. ICH Q8 Quality by Design (QbD) Design Space Heatmap\n',
                'Visualizing the non-collapse operating envelope.'
            ]
        },
        {
            'cell_type': 'code',
            'execution_count': 4,
            'metadata': {},
            'outputs': [],
            'source': [
                'ds_img_path = PROJECT_ROOT / "outputs" / "figures" / "design_space_heatmap.png"\n',
                'if ds_img_path.exists():\n',
                '    from IPython.display import Image, display\n',
                '    display(Image(filename=str(ds_img_path)))\n',
                'else:\n',
                '    print("Design space figure not found. Run run_experiments.py first.")'
            ]
        }
    ],
    'metadata': {
        'language_info': {'name': 'python'},
        'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}
    },
    'nbformat': 4,
    'nbformat_minor': 4
}

out_path = Path("d:/Yoshie Studio/kalbe-lyophilization-digital-twin/notebooks/analysis.ipynb")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=2)

print(f"Generated {out_path} successfully!")
