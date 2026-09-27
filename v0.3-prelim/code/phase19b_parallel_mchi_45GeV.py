"""
Phase 19b — Parallel run at m_chi = 45 GeV (Phase 8d reproduction)

Reproduces the Phase 8d results (m_chi = 45 GeV) using the EXACT SAME
code as Phase 19, to ensure the differences are purely m_chi and not
code differences.
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "v0.1-prelim" / "code"))

import dynesty
import config
import channels_v03 as ch_v03
from t30_lz_real_posterior import loglike_lz_real
from t32_real_likelihood import loglike_fermi_real
from phase8c_majorana_reframe_joint_fit import (
    sigma_SI_majorana_cm2, sigma_inel_majorana_cm2,
    M_A_PRIME_MEV_FIXED, LZ_248_KEV_EXPOSURE_TONNE_YEAR,
    LZ_248_KEV_RATE_TARGET, LZ_248_KEV_RATE_SIGMA, LZ_EVENT_RATE_COEFF,
)
from phase8d_majorana_alpha_consistent import sigma_v_majorana_cm3_per_s
from phase19_full_fit_mchi_5GeV import (
    loglike_full_mchi5, loglike_baseline_mchi5,
    prior_transform_5d, weighted_quantiles, run_fit,
)

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"

# Override m_chi to 45 GeV (Phase 8d value)
M_CHI_GEV_45 = 45.0

# Monkey-patch the module-level M_CHI_GEV_NEW
import phase19_full_fit_mchi_5GeV as p19

p19.M_CHI_GEV_NEW = M_CHI_GEV_45


def main():
    print("=" * 80)
    print("Phase 19b — Parallel run at m_chi = 45 GeV (Phase 8d reproduction)")
    print("=" * 80)
    print(f"Same code as Phase 19, but with m_chi = 45 GeV (Phase 8d value)")
    print()

    out = {
        "test": "Phase19b_parallel_mchi_45GeV",
        "m_chi_GeV": M_CHI_GEV_45,
        "direction": "Reproduce Phase 8d with Phase 19's code, for direct comparison",
    }

    results = {}
    results["baseline_no_LZ248"] = run_fit(loglike_baseline_mchi5, "Baseline (no LZ 248 keV)")
    results["full_with_LZ248"] = run_fit(loglike_full_mchi5, "Full (with LZ 248 keV)")

    delta_log_Z = results["full_with_LZ248"]["log_Z"] - results["baseline_no_LZ248"]["log_Z"]

    print()
    print("=" * 80)
    print("COMPARISON")
    print("=" * 80)
    print(f"Baseline log_Z: {results['baseline_no_LZ248']['log_Z']:.3f}")
    print(f"Full log_Z:      {results['full_with_LZ248']['log_Z']:.3f}")
    print(f"Δlog Z:         {delta_log_Z:+.3f}")
    print()
    print(f"MAP at m_chi = 45 GeV (Phase 8d reproduction):")
    print(f"  σ/m = {results['full_with_LZ248']['MAP_sigma_m']:.3f} cm²/g")
    print(f"  g_D  = {results['full_with_LZ248']['MAP_g_D']:.3f}")
    print(f"  f_H  = {results['full_with_LZ248']['MAP_f_H']:.3f}")
    print()
    print(f"Original Phase 8d at m_chi = 45 GeV: σ/m = 0.065, g_D = 0.146, f_H = 0.030, Δlog Z = +0.22")

    out["results"] = results
    out["delta_log_Z"] = delta_log_Z

    out_path = RESULTS_DIR / "phase19b_parallel_mchi_45GeV.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\nResults written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
