"""
T238 (D-17 figures): Generate sigma/m multi-channel figure for v19.2-D paper

Per R88: framework's σ/m at all dSph velocities exceeds Horigome's threshold.
This figure shows the σ/m(v) profile and the Horigome exclusion.
"""
import sys
import math
from pathlib import Path

# Use the venv
sys.path.insert(0, r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\scripts")

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


# Framework parameters (R88 corrected)
SIGMA_0 = 0.0516  # Phase 44 best fit
A_SLOPE = 1.93  # R88 fix
V_TARGET = 29.4  # R74 fix (was 28)
SIGMA_PEAK = 174.0  # causality cap
SIGMA_1 = 4.4  # Gaussian σ width
V_REF = 100.0

HORIGOME_THRESHOLD = 0.2  # cm²/g


def framework_sigma_m(v, sigma_1=SIGMA_1):
    """Framework's σ/m(v) — Phase 44 best fit + Gaussian resonance."""
    bg = SIGMA_0 * (V_REF / v) ** A_SLOPE
    res = SIGMA_PEAK * math.exp(-(v - V_TARGET) ** 2 / (2 * sigma_1 ** 2))
    return bg + res


def main():
    # Velocity range
    v_arr = np.logspace(0.5, 3, 200)  # 3 to 1000 km/s
    sigma_arr = np.array([framework_sigma_m(v) for v in v_arr])

    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot σ/m(v)
    ax.loglog(v_arr, sigma_arr, 'b-', lw=2, label='Framework σ/m(v) — R88 corrected (a_slope=1.93)')

    # Horigome threshold
    ax.axhline(HORIGOME_THRESHOLD, color='r', linestyle='--', lw=1.5,
               label=f'Horigome+ 2025 threshold (σ/m > {HORIGOME_THRESHOLD} cm²/g excluded)')

    # Mark dSph channels
    dSph_marks = [
        (9, "Sculptor"),
        (10, "Draco"),
        (15, "Fornax (paper)"),
        (18, "Fornax (canonical)"),
        (25, "UFD scale"),
    ]
    for v, name in dSph_marks:
        s = framework_sigma_m(v)
        ax.plot(v, s, 'ro', markersize=8)
        ax.annotate(f'{name}\nσ/m = {s:.1f}\n({s/HORIGOME_THRESHOLD:.0f}× threshold)',
                    xy=(v, s), xytext=(v*1.5, s*1.5),
                    fontsize=8, ha='left',
                    arrowprops=dict(arrowstyle='->', color='red', alpha=0.5))

    # Mark Cloud-9
    s_cloud9 = framework_sigma_m(28)
    ax.plot(28, s_cloud9, 'g*', markersize=20, label=f'Cloud-9 (σ/m = {s_cloud9:.0f}, {s_cloud9/HORIGOME_THRESHOLD:.0f}× threshold)')

    # Shade exclusion region
    ax.fill_between([3, 100], HORIGOME_THRESHOLD, 1000, alpha=0.15, color='red',
                    label=f'Excluded by Horigome+ 2025 (Path B)')

    ax.set_xlabel('Velocity v (km/s)', fontsize=12)
    ax.set_ylabel('σ/m (cm²/g)', fontsize=12)
    ax.set_title('Framework σ/m(v) at dSph + Cloud-9 velocities\nR88 corrected: a_slope=1.93 (Phase 44 fit), v_target=29.4 km/s, σ_peak=174 cm²/g',
                 fontsize=11)
    ax.legend(loc='upper left', fontsize=9)
    ax.grid(True, alpha=0.3, which='both')
    ax.set_xlim(3, 100)
    ax.set_ylim(0.01, 1000)

    plt.tight_layout()
    output_path = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\docs\FIG_SIGMA_M_V_HORIGOME_R88.png")
    plt.savefig(output_path, dpi=120, bbox_inches='tight')
    print(f"Figure saved to: {output_path}")
    print(f"Size: {output_path.stat().st_size} bytes")


if __name__ == "__main__":
    main()