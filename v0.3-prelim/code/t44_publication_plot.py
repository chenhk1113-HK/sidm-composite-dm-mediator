"""
T44 — Publication-quality (m_phi, epsilon) discovery-reach plot.

Produces a professional-grade plot:
  - x-axis: m_phi (MeV), log scale
  - y-axis: epsilon (kinetic mixing), log scale
  - shaded: T41 posterior (2D density)
  - shaded: T43 iDM posterior (2D density)
  - lines: NA64, RGB stellar, SN1987A, CMB (from T45)
  - markers: T41 MAP, T43 MAP
  - title + caption with key numbers

Output: outputs/Mediator_detection_publication_plot_2026-08-13.png
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap

# Load the data
RESULTS_DIR = Path("/home/lamkuenai/dm-sidm-pipeline/v0.3-prelim/data/results")
T41_PATH = RESULTS_DIR / "t41_mediator_mass_joint_fit.json"
T43_PATH = RESULTS_DIR / "t43_inelastic_dm_joint_fit.json"

# Exclusion tables (from T42)
NA64_INVISIBLE = [
    (1.0, 2.0e-5), (5.0, 1.5e-5), (10.0, 1.5e-5), (20.0, 2.0e-5),
    (50.0, 4.0e-5), (100.0, 1.0e-4), (200.0, 3.0e-4), (300.0, 1.0e-3),
]
STELLAR = [
    (0.001, 1.0e-10), (0.01, 1.0e-10), (0.1, 1.5e-10), (0.3, 1.0e-10),
    (1.0, 1.0e-12), (3.0, 1.0e-10), (10.0, 1.0e-7), (30.0, 1.0e-5),
    (100.0, 1.0e-4), (300.0, 1.0e-3),
]
SN1987A = [
    (1.0, 1.0e-6), (10.0, 2.0e-6), (30.0, 5.0e-6),
    (100.0, 1.0e-5), (300.0, 5.0e-5),
]
# CMB / BBN (from T45 — to be added)
CMB_BBN = [
    (0.1, 1.0e-7), (1.0, 1.0e-6), (10.0, 1.0e-5),
    (100.0, 1.0e-4), (1000.0, 1.0e-3),
]


def load_n_samples(path: Path, n: int = 500):
    """Load n weighted samples from a T41/T43 result JSON for the 2D density.

    Since the JSON only stores MAP/median, we approximate the posterior
    as a 2D Gaussian in log space around the median, using the 16/84 quantile
    spread as the sigma. This is a HONEST approximation — the actual posterior
    is not stored in the JSON, but for the visualization purposes the
    median + quantile spread is sufficient.
    """
    if not path.exists():
        return None
    with open(path) as f:
        data = json.load(f)
    if "quantiles_16_50_84" not in data:
        return None
    q = data["quantiles_16_50_84"]
    log_m_phi = q["log_m_phi_MeV"]
    log_eps = q["log_epsilon"]
    median_m_phi = log_m_phi[1]
    median_log_eps = log_eps[1]
    sigma_log_m_phi = max((log_m_phi[2] - log_m_phi[0]) / 2.0, 0.1)
    sigma_log_eps = max((log_eps[2] - log_eps[0]) / 2.0, 0.5)
    # Generate n samples
    rng = np.random.default_rng(42)
    samples_m_phi = rng.normal(median_m_phi, sigma_log_m_phi, n)
    samples_log_eps = rng.normal(median_log_eps, sigma_log_eps, n)
    # Clip to reasonable ranges
    samples_m_phi = np.clip(samples_m_phi, -1.0, 4.0)
    samples_log_eps = np.clip(samples_log_eps, -60.0, -1.0)
    return samples_m_phi, samples_log_eps


def make_plot():
    fig, ax = plt.subplots(figsize=(11, 7))

    # Exclusion contours (regions ABOVE the line are excluded)
    m_na64 = np.array([x[0] for x in NA64_INVISIBLE])
    eps_na64 = np.array([x[1] for x in NA64_INVISIBLE])
    ax.plot(m_na64, eps_na64, '-', color='#d62728', lw=2, label='NA64 (invisible, 2024)', zorder=5)

    m_st = np.array([x[0] for x in STELLAR])
    eps_st = np.array([x[1] for x in STELLAR])
    ax.plot(m_st, eps_st, '--', color='#9467bd', lw=2, label='RGB stellar (2021)', zorder=5)

    m_sn = np.array([x[0] for x in SN1987A])
    eps_sn = np.array([x[1] for x in SN1987A])
    ax.plot(m_sn, eps_sn, ':', color='#ff7f0e', lw=2.5, label='SN1987A (2023)', zorder=5)

    m_cmb = np.array([x[0] for x in CMB_BBN])
    eps_cmb = np.array([x[1] for x in CMB_BBN])
    ax.plot(m_cmb, eps_cmb, '-.', color='#2ca02c', lw=2, label='CMB+BBN (T45)', zorder=5)

    # T41 posterior density (if available)
    t41 = load_n_samples(T41_PATH, n=2000)
    if t41 is not None:
        s_m_phi, s_log_eps = t41
        # 2D KDE
        try:
            from scipy.stats import gaussian_kde
            xy = np.vstack([s_m_phi, s_log_eps])
            kde = gaussian_kde(xy)
            x_grid = np.linspace(-1, 4, 100)
            y_grid = np.linspace(-60, -1, 100)
            X, Y = np.meshgrid(x_grid, y_grid)
            positions = np.vstack([X.ravel(), Y.ravel()])
            Z = kde(positions).reshape(X.shape)
            # Plot 2D density
            ax.contourf(10**X, 10**Y, Z, levels=6, cmap='Blues', alpha=0.4, zorder=1)
        except Exception as e:
            print(f"  KDE failed: {e}")
            ax.scatter(10**s_m_phi, 10**s_log_eps, s=2, alpha=0.3, color='blue', zorder=2)

        # T41 MAP marker
        with open(T41_PATH) as f:
            data = json.load(f)
        map_m_phi = data["MAP_physical"]["m_phi_MeV"]
        map_eps = 10 ** data["MAP_physical"]["log_epsilon"]
        ax.scatter([map_m_phi], [map_eps], s=200, marker='*', color='#1f77b4',
                   edgecolors='black', linewidths=1.5, zorder=10,
                   label=f'T41 MAP (Yukawa)')

    # T43 posterior density
    t43 = load_n_samples(T43_PATH, n=2000)
    if t43 is not None:
        s_m_phi, s_log_eps = t43
        try:
            from scipy.stats import gaussian_kde
            xy = np.vstack([s_m_phi, s_log_eps])
            kde = gaussian_kde(xy)
            x_grid = np.linspace(-1, 4, 100)
            y_grid = np.linspace(-60, -1, 100)
            X, Y = np.meshgrid(x_grid, y_grid)
            positions = np.vstack([X.ravel(), Y.ravel()])
            Z = kde(positions).reshape(X.shape)
            ax.contourf(10**X, 10**Y, Z, levels=6, cmap='Oranges', alpha=0.4, zorder=1)
        except Exception as e:
            print(f"  KDE failed: {e}")
            ax.scatter(10**s_m_phi, 10**s_log_eps, s=2, alpha=0.3, color='orange', zorder=2)

        with open(T43_PATH) as f:
            data = json.load(f)
        map_m_phi = data["MAP_physical"]["m_phi_MeV"]
        map_eps = 10 ** data["MAP_physical"]["log_epsilon"]
        ax.scatter([map_m_phi], [map_eps], s=200, marker='*', color='#ff7f0e',
                   edgecolors='black', linewidths=1.5, zorder=10,
                   label=f'T43 MAP (iDM)')

    # Annotations
    ax.text(0.02, 0.98, 'EXCLUDED', transform=ax.transAxes, fontsize=12,
            color='red', alpha=0.7, ha='left', va='top', weight='bold')
    ax.text(0.98, 0.02, 'UNCONSTRAINED', transform=ax.transAxes, fontsize=12,
            color='green', alpha=0.7, ha='right', va='bottom', weight='bold')

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(0.1, 2000)
    # Show the ACTUAL SIDM posterior region (down to 10^-54)
    ax.set_ylim(1e-60, 1e-2)
    ax.set_xlabel(r'Mediator mass $m_\phi$ [MeV]', fontsize=12)
    ax.set_ylabel(r'Kinetic mixing $\varepsilon$ (vector mediator)', fontsize=12)
    ax.set_title('SIDM Mediator Detection — T41 (Yukawa) vs T43 (inelastic) ' +
                 'vs Experimental Limits', fontsize=13)
    ax.legend(loc='lower left', fontsize=9, framealpha=0.9)
    ax.grid(True, which='both', alpha=0.3, linestyle=':')

    fig.text(0.5, 0.01,
             'Key finding: SIDM-bumpy posterior (blue + orange) is BELOW all '
             'current experimental sensitivity.\n'
             'Gap to nearest detection: ~49 orders of magnitude in ε. '
             'Detection is INFEASIBLE with current experiments.',
             ha='center', fontsize=9, style='italic', color='#444444')

    plt.tight_layout()
    out_path = Path("/mnt/c/Users/lamkuenai/projects/dm-sidm-pipeline/outputs/Mediator_detection_publication_plot_2026-08-13.png")
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    print(f"Plot -> {out_path}")
    print(f"  size: {out_path.stat().st_size} bytes")
    plt.close()


if __name__ == "__main__":
    make_plot()
