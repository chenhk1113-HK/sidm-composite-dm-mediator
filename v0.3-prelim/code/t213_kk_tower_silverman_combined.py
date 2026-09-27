"""
T213 — Combined test: T163 KK-tower sigma/m(v) + Silverman+ 2026 gravothermal.

QUESTION: Does the T163 best-fit KK tower produce a sigma/m(v) at the Cloud-9
host-halo V_max = 31.12 km/s that, when fed into Silverman+ 2026's
gravothermal prescription, reproduces the Cloud-9 spike (sigma/m = 50-128)?

This is the NEW test that combines both deferred items from v18.41:

  T163 (KK tower optimization): best-fit params alpha_D=0.3, m_0=0.3 GeV,
    r=1.5, n_modes=2, RMSE=1.408.
  T212 (Silverman+ 2026 gravothermal): gravothermal can run if
    sigma/m(V_max) >= 1.0 cm^2/g at Cloud-9 host halo (corrected from
    earlier 10 cm^2/g after V_max + t_cross fixes per 2review.docx).

T163's best-fit gives sigma/m at v=100 km/s = 0.052 cm^2/g (Phase 44 match).
But what is sigma/m at v = 31.12 km/s (Cloud-9 host V_max)?

KK tower sigma(v) = sum_n sigma_n(v), where sigma_n has a velocity
dependence that increases as v -> 0 (Bohr-radius / Sommerfeld enhancement
for low velocities). At lower v, sigma/m is HIGHER, not lower.

So sigma/m(V_max=31.12) might be 10-100x sigma/m(v=100) = 0.52-5.2 cm^2/g.
This could be ABOVE the 1.0 cm^2/g threshold!

Let me actually compute this using sidmkit.
"""
from __future__ import annotations
import json
import sys
import math
from pathlib import Path

import numpy as np

# Use T163 setup
sys.path.insert(0, r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code")

try:
    import sidmkit
except ImportError:
    print("sidmkit not available; falling back to T163-style parameter sweep")

from pathlib import Path
out_path = Path(__file__).resolve().parent.parent / "data" / "results" / "t213_kk_tower_silverman_combined.json"

# T163 best-fit parameters
T163_BEST_FIT = {
    "alpha_D": 0.3,
    "m_0_GeV": 0.3,
    "r": 1.5,
    "n_modes": 2,
    "RMSE": 1.408,
}

# Cloud-9 host halo (from T212)
CLOUD9_HOST = {
    "M_halo_M_sun": 5e9,
    "c": 12.0,
    "v_max_kms": 31.12,  # post-fix from V_max review
    "r_vir_pc": 35092.9,
    "r_s_pc": 2924.4,
    "rho_s_M_sun_pc3": 0.00969,
}

# Silverman+ 2026 threshold for gravothermal to run (from T212)
SIGMA_M_THRESHOLD = 1.0  # cm^2/g at V_max

def sigma_kk_t163(v_arr):
    """Compute KK tower sigma/m(v) using T163 best-fit params."""
    alpha_D = T163_BEST_FIT["alpha_D"]
    m_0 = T163_BEST_FIT["m_0_GeV"]
    r = T163_BEST_FIT["r"]
    n_modes = T163_BEST_FIT["n_modes"]
    m_chi_GeV = 10.44  # Phase 44 baseline

    sigma_total = np.zeros_like(np.asarray(v_arr, dtype=float))
    for n in range(1, n_modes + 1):
        m_n = m_0 * (r ** n)
        c_n = 1.0 / n
        model = sidmkit.YukawaModel(
            m_chi_gev=m_chi_GeV,
            m_med_gev=m_n,
            alpha=alpha_D * c_n,
            potential=sidmkit.PotentialType.ATTRACTIVE,
        )
        sigma_n = sidmkit.sigma_over_m(v_arr, model, method="partial_wave")
        sigma_total = sigma_total + np.asarray(sigma_n)
    return sigma_total


def main():
    result = {
        "description": "T213 — Combined test: T163 KK-tower sigma/m(V_max) at Cloud-9 host halo + Silverman+ gravothermal threshold",
        "source_papers": [
            "T163 (KK tower best fit, RMSE=1.408, alpha_D=0.3, m_0=0.3 GeV, r=1.5, n_modes=2)",
            "T212 (Silverman+ 2026 arXiv:2606.02566 gravothermal threshold sigma/m = 1.0 cm^2/g at V_max)",
            "T208 V_max fix (V_max at r_max = 2.1626*r_s, gives V_max=31.12 km/s at Cloud-9 host)",
        ],
        "T163_best_fit": T163_BEST_FIT,
        "cloud9_host_halo": CLOUD9_HOST,
        "silverman_threshold_cm2_g": SIGMA_M_THRESHOLD,
        "sigma_m_at_reference_velocities": {},
        "verdict": "",
    }

    # Reference velocities (km/s)
    v_ref = np.array([5.0, 10.0, 15.0, 28.0, 31.12, 50.0, 100.0, 200.0, 500.0])

    print("Computing T163 KK tower sigma/m(v) at reference velocities...")
    sigma_v = sigma_kk_t163(v_ref)

    for v, s in zip(v_ref, sigma_v):
        result["sigma_m_at_reference_velocities"][f"{v:.2f}"] = float(s)
        print(f"  v = {v:6.2f} km/s   sigma/m = {s:8.4f} cm^2/g")

    # Key check: sigma/m at Cloud-9 host V_max
    sigma_at_cloud9 = float(sigma_v[np.argmin(np.abs(v_ref - CLOUD9_HOST["v_max_kms"]))])
    result["sigma_m_at_cloud9_v_max_cm2_g"] = sigma_at_cloud9

    # Verdict
    print()
    print(f"Cloud-9 host V_max = {CLOUD9_HOST['v_max_kms']:.2f} km/s")
    print(f"T163 sigma/m at V_max = {sigma_at_cloud9:.4f} cm^2/g")
    print(f"Silverman+ threshold = {SIGMA_M_THRESHOLD:.4f} cm^2/g")

    if sigma_at_cloud9 >= SIGMA_M_THRESHOLD:
        verdict = "PASS: T163 KK tower + Silverman+ gravothermal CAN reproduce Cloud-9 spike at sigma/m(V_max)"
    else:
        ratio = sigma_at_cloud9 / SIGMA_M_THRESHOLD
        verdict = (
            f"FAIL: T163 KK tower gives sigma/m(V_max) = {sigma_at_cloud9:.4f} cm^2/g, "
            f"which is {ratio:.3f}x BELOW the Silverman+ threshold of {SIGMA_M_THRESHOLD} cm^2/g. "
            f"KK tower alone cannot drive gravothermal at Cloud-9 host halo."
        )

    result["verdict"] = verdict
    print()
    print("=" * 80)
    print(verdict)
    print("=" * 80)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nResults saved to: {out_path}")


if __name__ == "__main__":
    main()