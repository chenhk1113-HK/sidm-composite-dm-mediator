"""
T239 (D-17 figure 2): Hierarchy constraint g_N/g_chi

Per R83: g_N/g_chi < ~10^-13 (Cloud-9 v=28 anchor, σ/m = 166 cm²/g)
Per R86: with a_slope = 1.93, σ/m at v = 28 = 166.0 cm²/g
"""
import sys
import math
from pathlib import Path

sys.path.insert(0, r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\scripts")

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


M_CHI_GEV = 1.0  # framework
M_CHI_G = M_CHI_GEV * 1.783e-24  # grams
LZ_BOUND_CM2 = 1e-46

# Anchor velocities (R86 v=28 anchor)
def sigma_m_framework(v):
    SIGMA_0 = 0.0516
    A_SLOPE = 1.93
    SIGMA_PEAK = 174.0
    V_TARGET = 29.4
    SIGMA_1 = 4.4
    V_REF = 100.0
    bg = SIGMA_0 * (V_REF / v) ** A_SLOPE
    res = SIGMA_PEAK * math.exp(-(v - V_TARGET) ** 2 / (2 * SIGMA_1 ** 2))
    return bg + res


def hierarchy_constraint(v_anchor, label=""):
    """Compute g_N/g_chi < sqrt(sigma_SI / sigma_DM-DM_per_particle) at given v."""
    sm = sigma_m_framework(v_anchor)
    sigma_dm_dm = sm * M_CHI_G  # cm^2 per particle
    ratio = sigma_dm_dm / LZ_BOUND_CM2
    sqrt_ratio = math.sqrt(ratio)
    g_n_over_g_chi = 1.0 / sqrt_ratio
    return sm, sigma_dm_dm, ratio, sqrt_ratio, g_n_over_g_chi


def main():
    # Test anchors
    anchors = [
        (15, "v=15 (Fornax paper)", 2.01),
        (28, "v=28 (Cloud-9, R83)", 1.06),
        (100, "v=100 (R72 empirical)", 3.04),
    ]

    print(f"{'Anchor':<25}{'σ/m':<10}{'σ_DM-DM':<15}{'ratio':<15}{'√ratio':<12}{'g_N/g_χ'}")
    print("-" * 90)
    for v, label, sqrt_check in anchors:
        sm, sigma_dm_dm, ratio, sqrt_ratio, g_n_over_g_chi = hierarchy_constraint(v, label)
        print(f"{label:<25}{sm:<10.3f}{sigma_dm_dm:<15.3e}{ratio:<15.3e}{sqrt_ratio:<12.3e}{g_n_over_g_chi:.3e}")

    # Figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot g_N/g_chi vs anchor velocity
    v_arr = np.linspace(5, 100, 100)
    g_n_g_chi_arr = []
    for v in v_arr:
        sm = sigma_m_framework(v)
        sigma_dm_dm = sm * M_CHI_G
        ratio = sigma_dm_dm / LZ_BOUND_CM2
        sqrt_ratio = math.sqrt(ratio)
        g_n_over_g_chi = 1.0 / sqrt_ratio
        g_n_g_chi_arr.append(g_n_over_g_chi)

    ax.loglog(v_arr, g_n_g_chi_arr, 'b-', lw=2, label='g_N/g_χ (R83 v=28 anchor convention)')

    # Mark the R72 / R83 anchors
    ax.axhline(7.5e-12, color='purple', linestyle='--', lw=1,
               label='R72 headline (7.5×10^-12, σ/m ~1 cm²/g anchor)')
    ax.axhline(1e-13, color='green', linestyle='--', lw=1,
               label='R83 headline (~10^-13, v=28 framework anchor)')
    ax.axhline(3e-11, color='orange', linestyle='--', lw=1,
               label='R57 historical (3×10^-11)')

    # Mark specific velocities
    for v, label in [(15, 'v=15 (Fornax)'), (28, 'v=28 (R83)'), (100, 'v=100 (R72)')]:
        sm = sigma_m_framework(v)
        sigma_dm_dm = sm * M_CHI_G
        g_n_over_g_chi = 1.0 / math.sqrt(sigma_dm_dm / LZ_BOUND_CM2)
        ax.plot(v, g_n_over_g_chi, 'ko', markersize=8)
        ax.annotate(f'{label}\n{g_n_over_g_chi:.2e}',
                    xy=(v, g_n_over_g_chi), xytext=(v*1.5, g_n_over_g_chi*1.5),
                    fontsize=9, ha='left',
                    arrowprops=dict(arrowstyle='->', color='black', alpha=0.5))

    ax.set_xlabel('Anchor velocity v (km/s)', fontsize=12)
    ax.set_ylabel('g_N/g_χ (hierarchy constraint)', fontsize=12)
    ax.set_title('Hierarchy constraint g_N/g_χ < 1/√(σ_DM-DM/σ_SI)\nR88 corrected: a_slope=1.93, σ/m at v=28 = 166.0 cm²/g (per-particle = 2.96×10^-22 cm²)',
                 fontsize=10)
    ax.legend(loc='best', fontsize=9)
    ax.grid(True, alpha=0.3, which='both')
    ax.set_xlim(5, 100)
    ax.set_ylim(1e-15, 1e-9)

    plt.tight_layout()
    output_path = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\docs\FIG_HIERARCHY_R88.png")
    plt.savefig(output_path, dpi=120, bbox_inches='tight')
    print(f"\nFigure saved to: {output_path}")
    print(f"Size: {output_path.stat().st_size} bytes")


if __name__ == "__main__":
    main()