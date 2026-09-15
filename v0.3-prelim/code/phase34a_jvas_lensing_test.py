"""
Phase 34a — JVAS B1938+666 lensing test.

Paper 2 (arXiv:2606.12909) interprets the 10^6 M_sun lensing perturber as
a SIDM halo in DEEP gravothermal core collapse. Their required parameters:
  - Progenitor: M_200 = 1.5e8 M_sun, c_200 = 50 (or higher)
  - sigma/m ~ 100 cm^2/g at v_max ~ 15 km/s
  - sigma/m ~ 100 cm^2/g is the regime where core collapse occurs

For the model to explain JVAS B1938+666, it must produce:
  sigma/m(v=15 km/s) ~ 100 cm^2/g

We evaluate our Phase 32b posterior median at v=15 km/s and compare.

If our sigma/m(15) ~ 100 cm^2/g: PASS — model can explain the lensing perturber
If our sigma/m(15) ~ 1 cm^2/g:  FAIL — model CANNOT explain the perturber
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from t90_v70_multi_resonant_darkqcd import (
    sigma_m_multi_resonant,
    velocity_dependent_background,
)
from t90_v50_resonant_sidm import kinetic_energy_eV

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"


def get_best_posterior():
    """Load best sample from Phase 32b joint fit."""
    with open(RESULTS_DIR / "phase32b_multi_resonant_joint_fit.json") as f:
        data = json.load(f)
    return data["best_sample"]


def build_resonances(best):
    """Build resonance list from best sample."""
    resonances = []
    names = ["R1_Cloud9", "R2_SPARC", "R3_Stream", "R4_Cluster"]
    sigma_peaks = [100.0, 0.07, 0.1, 0.01]
    widths = best.get("width_fractions", [0.05, 0.05, 0.05, 0.10])
    for i in range(4):
        v_t = best["v_targets_kms"][i]
        E_R = kinetic_energy_eV(v_t, best["m_chi_GeV"])
        Gamma = widths[i] * E_R
        resonances.append({
            "name": names[i],
            "E_R_eV": E_R,
            "Gamma_eV": Gamma,
            "sigma_peak_cm2_per_g": sigma_peaks[i],
            "v_target_kms": v_t,
        })
    return resonances


def evaluate_sigma_m(best, resonances, v):
    """Evaluate sigma/m at velocity v."""
    sigma_0_v = velocity_dependent_background(v, best["sigma_0_dwarf"], best["a_slope"])
    result = sigma_m_multi_resonant(v, best["m_chi_GeV"], resonances, sigma_0_v, 0.0)
    return result["sigma_m_total"]


def core_collapse_timescale(sigma_m_at_v15, r_s_kpc=0.22, rho_s_Msun_kpc3=3.7e8):
    """Estimate gravothermal core-collapse timescale.

    Per Paper 2 Eq. 3 and Balberg+ 2002:
      t_c ~ 200 / (r_s * rho_s * sigma_eff/m) * 1/sqrt(4 * pi * G * rho_s)

    With G in M_sun^-1 kpc^3 Gyr^-2 units: G = 4.5e-6
    """
    G = 4.5e-6  # kpc^3 / (M_sun * Gyr^2)
    rho_s = rho_s_Msun_kpc3  # M_sun / kpc^3
    r_s = r_s_kpc  # kpc
    sigma_eff_m = sigma_m_at_v15  # cm^2/g

    # Convert sigma/m from cm^2/g to kpc^2/M_sun
    # 1 cm^2/g = 1e-4 m^2 / 1e-3 kg = 0.1 m^2/kg
    # 1 kpc = 3.086e19 m, 1 M_sun = 1.989e30 kg
    # 1 cm^2/g = 0.1 * (3.086e19)^-2 / 1e-3 * 1.989e30 kpc^2/M_sun
    # = 0.1 / 9.52e38 * 1.989e30 kpc^2/M_sun
    # = 2.09e-10 kpc^2/M_sun
    CM2G_TO_KPC2_MSUN = 2.09e-10
    sigma_eff_kpc = sigma_eff_m * CM2G_TO_KPC2_MSUN

    t_c = 200 / (r_s * rho_s * sigma_eff_kpc) / np.sqrt(4 * np.pi * G * rho_s)
    return t_c  # in Gyr


def main():
    print("=" * 70)
    print("Phase 34a — JVAS B1938+666 lensing test (arXiv:2606.12909)")
    print("=" * 70)
    print()

    # Paper 2 requirements
    print("Paper 2 (arXiv:2606.12909) requirements for JVAS B1938+666 perturber:")
    print(f"  sigma/m(v=15 km/s) ~ 100 cm^2/g  [required for deep core collapse]")
    print(f"  Progenitor: M_200 = 1.5e8 M_sun, c_200 = 50")
    print(f"  Result: forms secondary dense core 3e5 M_sun within 10 pc")
    print()

    # Load model
    best = get_best_posterior()
    resonances = build_resonances(best)

    print(f"Our model (Phase 32b posterior median):")
    print(f"  m_chi = {best['m_chi_GeV']:.2f} GeV")
    print(f"  sigma_0_dwarf = {best['sigma_0_dwarf']:.3f} cm^2/g")
    print(f"  a_slope = {best['a_slope']:.3f}")
    print(f"  v_targets = {[f'{v:.1f}' for v in best['v_targets_kms']]}")
    print()

    # Evaluate sigma/m at multiple velocities
    test_v = [10, 12, 15, 20, 28, 50, 100, 200]
    print(f"{'v (km/s)':>10} {'sigma/m':>12} {'regime':>20}")
    print("-" * 50)
    sigma_m_values = {}
    for v in test_v:
        sm = evaluate_sigma_m(best, resonances, v)
        sigma_m_values[v] = sm
        if v == 15:
            regime = "<-- JVAS regime"
        elif v == 28:
            regime = "(Cloud-9)"
        else:
            regime = ""
        print(f"{v:>10} {sm:>12.4f} {regime:>20}")

    print()

    # Key test
    sigma_m_15 = sigma_m_values[15]
    required_15 = 100.0  # cm^2/g from Paper 2
    ratio_15 = sigma_m_15 / required_15
    deficit = required_15 / sigma_m_15 if sigma_m_15 > 0 else float('inf')

    print("=" * 70)
    print(f"KEY TEST: sigma/m at v=15 km/s")
    print("=" * 70)
    print()
    print(f"  Paper 2 requirement: {required_15:.1f} cm^2/g")
    print(f"  Our model:           {sigma_m_15:.4f} cm^2/g")
    print(f"  Ratio:               {ratio_15:.4f}")
    print(f"  Deficit:             {deficit:.1f}x TOO LOW")
    print()

    # Core collapse timescale
    t_c = core_collapse_timescale(sigma_m_15)
    print(f"  Estimated core-collapse timescale:")
    print(f"    t_c ~ {t_c:.2f} Gyr (Hubble time ~ 13.8 Gyr)")
    if t_c > 13.8:
        print(f"    → Core collapse would take LONGER than the age of the universe")
        print(f"    → JVAS B1938+666 perturber CANNOT have formed via this mechanism")
    else:
        print(f"    → Core collapse can occur within a Hubble time")
    print()

    # Verdict
    if ratio_15 > 0.5:  # Within factor 2
        verdict = "JVAS_PASS"
        msg = "Model produces enough sigma/m(15) for JVAS-like core collapse"
    elif ratio_15 > 0.1:  # Within factor 10
        verdict = "JVAS_MARGINAL"
        msg = "Model is factor 2-10 below requirement — could explain if parameters adjusted"
    else:
        verdict = "JVAS_FAIL"
        msg = f"Model is {deficit:.0f}x too low for JVAS-like core collapse"

    print(f"Verdict: {verdict}")
    print(f"  {msg}")
    print()

    # Implications
    print("=" * 70)
    print("IMPLICATIONS")
    print("=" * 70)
    print()
    print("If JVAS B1938+666 interpretation is correct:")
    print(f"  - SIDM at v=15 km/s MUST have sigma/m ~ 100 cm^2/g")
    print(f"  - Our model gives {sigma_m_15:.2f} cm^2/g (factor {deficit:.0f} too low)")
    print(f"  - Our model CANNOT explain JVAS-like perturbers")
    print()
    print("If JVAS B1938+666 is NOT representative:")
    print(f"  - Most SIDM lenses may have lower concentration progenitors")
    print(f"  - Sigma/m ~ 1-10 cm^2/g could suffice for core collapse with c ~ 80+")
    print(f"  - Model could still be viable for OTHER lensing tests")
    print()
    print("Path forward:")
    print("  - Add JVAS B1938+666 to the test suite as a discriminator")
    print("  - If we want to match Paper 2, retune R1 to be wider (would affect dwarfs)")
    print("  - OR explicitly state: model explains Cloud-9 + SPARC but NOT JVAS")
    print()

    # Save results
    out = {
        "test": "Phase34a_jvas_b1938_lensing",
        "paper_reference": "arXiv:2606.12909",
        "required_sigma_m_at_v15_cm2_per_g": required_15,
        "our_sigma_m_at_v15_cm2_per_g": float(sigma_m_15),
        "ratio": float(ratio_15),
        "deficit_factor": float(deficit),
        "core_collapse_timescale_Gyr": float(t_c),
        "core_collapse_feasible": bool(t_c < 13.8),
        "verdict": verdict,
        "all_sigma_m_evaluated": {str(k): float(v) for k, v in sigma_m_values.items()},
        "model_parameters": best,
        "interpretation": {
            "sigma_m_at_v15_too_low_by": float(deficit),
            "would_need_to_increase_by": float(deficit),
            "retune_options": [
                "Widen R1 resonance (would over-shoot dwarfs)",
                "Add R0 resonance at v=10-15 (would break Cloud-9 v_target)",
                "Increase sigma_0_dwarf to ~80 cm^2/g (would break dwarf core tests)",
                "Accept that model cannot explain JVAS B1938+666",
            ],
        },
    }

    out_path = RESULTS_DIR / "phase34a_jvas_lensing_test.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"Results written to: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())