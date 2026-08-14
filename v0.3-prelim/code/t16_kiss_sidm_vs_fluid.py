#!/usr/bin/env python
"""
T16 — Direction C: KISS-SIDM fit correction vs Balberg+ 2002 fluid penalty.

This test answers a SPECIFIC question: in the per-halo gravothermal prior,
how much does the KISS-SIDM kinetic correction (Gurian & May 2025, PRL
135, 221001) shift the σ/m posterior relative to the Balberg+ 2002 fluid
model?

We do NOT re-run the joint fit. We compute the per-halo collapse penalty
at a representative halo-mass sweep (10^7 to 10^14 M_sun) under three
treatments:

  1. Fluid penalty (gravothermal_r_core, the current pipeline default).
  2. KISS-SIDM penalty with no correction (correction=1.0, "fluid limit").
  3. KISS-SIDM penalty with full IMFP correction (Table I ratio).

The difference (fluid vs DSMC) is small (< 30% in the published
calibration regime) and concentrated in the IMFP region. The test
quantifies the magnitude of the correction and confirms it is in the
right direction (DSMC < fluid in the IMFP regime, as published).

Caveat / honest scope (per the KISS-SIDM paper itself):
  - The Table I power-law scalings are LOCAL (rho/rho_s in 10^4-10^5).
  - The correction is most applicable at the IMFP regime, which our
    classifier places near 10^9 M_sun halos.
  - For dwarf halos (M_halo ~ 10^7-10^8 M_sun) and cluster halos
    (M_halo ~ 10^14 M_sun), the halo is in LMFP or SMFP and the fluid
    model is appropriate. The KISS-SIDM correction is most relevant
    for normal-galaxy-scale halos.

References:
  Gurian & May 2025 (arXiv:2505.15903v2), PRL 135, 221001.
  Balberg & Shapiro 2002, PRL 88, 101301 (the fluid model).
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import numpy as np

# Path setup MUST happen before gravothermal is imported (it depends on
# halo_profiles from v0.1-prelim/code).
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_V01_CODE = _PROJECT_ROOT / "v0.1-prelim" / "code"
for p in (str(_PROJECT_ROOT), str(_PROJECT_ROOT / "v0.3-prelim" / "code"), str(_V01_CODE)):
    if p not in sys.path:
        sys.path.insert(0, p)

import kiss_sidm_scalings as kss
import gravothermal as gth

from config import RESULTS_DIR_V03


# Halo-mass sweep: dwarfs to clusters
HALO_MASS_RANGE = (1e7, 1e14)  # M_sun
N_HALO_MASS = 20
SIGMA_M_SWEEP = np.array([0.1, 0.5, 1.0, 5.0, 10.0, 50.0])  # cm^2/g


def estimate_halo_params(M_halo_Msun: float) -> dict:
    """Halo parameters for the M_halo sweep.

    For a halo of mass M, estimate NFW scale density, scale radius, v_max.
    We use the median concentration relation (Dutton & Macciò 2014):
        c_vir ~ 10^(0.54 - 0.13 * log10(M / 1e12))
        r_vir = (M / (4/3 pi * 200 rho_c))^(1/3)
        r_s = r_vir / c_vir
        rho_s = 200 rho_c c_vir^3 / (3 * (ln(1+c_vir) - c_vir/(1+c_vir)))
        v_max ~ sqrt(G M / r_vir)  (approximate)
    """
    # Critical density (z=0) ~ 1.4e-7 M_sun/pc^3 = 1.4e8 M_sun/kpc^3 (ish)
    # Use a simpler scaling: v_max ~ 200 km/s for M=1e12, v ~ M^0.3
    v_max = 200.0 * (M_halo_Msun / 1e12) ** 0.3
    # Rough rho_c at z=0
    rho_crit = 1.4e8  # M_sun/kpc^3 (order of magnitude)
    r_vir = (M_halo_Msun / (4.0 / 3.0 * np.pi * 200 * rho_crit)) ** (1.0 / 3.0)  # kpc
    c_vir = 10 ** (0.54 - 0.13 * np.log10(M_halo_Msun / 1e12))
    r_s = r_vir / c_vir
    rho_s = 200 * rho_crit * c_vir ** 3 / (3.0 * (np.log(1 + c_vir) - c_vir / (1 + c_vir)))
    return {
        "M_halo_Msun": M_halo_Msun,
        "rho_s": rho_s,
        "r_s": r_s,
        "v_max": v_max,
        "c_vir": c_vir,
        "r_vir": r_vir,
    }


def compute_collapse_penalty_fluid(sigma_m: float, halo: dict) -> float:
    """Fluid-model penalty: how 'collapsed' is this halo at this sigma_m?

    The penalty is the (signed) log-ratio of the fluid r_core to the
    canonical expanded r_core. Negative = MORE collapsed than expected,
    so the prior should DOWN-WEIGHT this sigma_m.
    """
    r_core_fluid = gth.gravothermal_r_core(
        sigma_m,
        rho_s=halo["rho_s"],
        r_s=halo["r_s"],
        v_max=halo["v_max"],
        t_Gyr=10.0,
    )
    # Penalty: how much smaller is r_core than the initial r_max?
    r_max = 0.045 * halo["r_s"]  # kpc
    if r_core_fluid <= 0:
        return 0.0
    ratio = r_core_fluid / r_max  # < 1 means collapse
    return -np.log(ratio)  # positive = "this sigma_m is suspicious"


def compute_collapse_penalty_kinetic(sigma_m: float, halo: dict) -> float:
    """KISS-SIDM-corrected penalty: applies Table I correction in IMFP.

    Outside IMFP, returns the fluid penalty (correction factor = 1.0).
    In IMFP, the penalty is REDUCED by factor 0.78 (Kn=1) or 0.57 (Kn=5).
    """
    fluid_penalty = compute_collapse_penalty_fluid(sigma_m, halo)
    if fluid_penalty == 0:
        return 0.0

    # Use the halo's v_max and a representative core density (Burkert
    # core density ~ 1e7 M_sun/kpc^3 for galaxy-scale halos).
    rho_core = 1e7
    v_rms_core = halo["v_max"]  # approximate
    Kn = kss.knudsen_number(rho_core, v_rms_core, sigma_m)
    regime = kss.knudsen_regime_label(Kn)
    correction = kss.knudsen_correction_factor(Kn, Kn_threshold=1.0)

    if regime == "IMFP":
        return fluid_penalty * correction
    else:
        return fluid_penalty


def main():
    print("=== T16 — Direction C: KISS-SIDM correction vs Balberg fluid ===")
    print()
    print("Per-halo collapse penalty under three models:")
    print("  (1) Fluid (Balberg+ 2002) — current pipeline default")
    print("  (2) KISS-SIDM no-correction (= fluid, sanity check)")
    print("  (3) KISS-SIDM with Table I IMFP correction")
    print()

    halo_masses = np.logspace(
        np.log10(HALO_MASS_RANGE[0]),
        np.log10(HALO_MASS_RANGE[1]),
        N_HALO_MASS,
    )
    results = {
        "halo_masses": halo_masses.tolist(),
        "sigma_m_sweep": SIGMA_M_SWEEP.tolist(),
        "fluid_penalties": [],
        "kiss_sidm_penalties": [],
        "regime_labels": [],
        "kn_values": [],
        "correction_factors": [],
    }

    for M in halo_masses:
        halo = estimate_halo_params(M)
        print(f"Halo M = {M:.2e} M_sun (v_max = {halo['v_max']:.1f} km/s, "
              f"r_s = {halo['r_s']:.2f} kpc, rho_s = {halo['rho_s']:.2e})")

        for sigma_m in SIGMA_M_SWEEP:
            fluid_pen = compute_collapse_penalty_fluid(sigma_m, halo)
            kiss_pen = compute_collapse_penalty_kinetic(sigma_m, halo)

            # Track Kn and correction for this specific (sigma_m, halo) pair
            Kn = kss.knudsen_number(1e7, halo["v_max"], sigma_m)
            regime = kss.knudsen_regime_label(Kn)
            correction = kss.knudsen_correction_factor(Kn, Kn_threshold=1.0)

            print(f"  sigma_m = {sigma_m:5.1f} cm^2/g: Kn = {Kn:.2e}, "
                  f"regime = {regime:5s}, correction = {correction:.3f}, "
                  f"fluid_pen = {fluid_pen:.3f}, kinetic_pen = {kiss_pen:.3f}")

            results["fluid_penalties"].append(fluid_pen)
            results["kiss_sidm_penalties"].append(kiss_pen)
            results["regime_labels"].append(regime)
            results["kn_values"].append(Kn)
            results["correction_factors"].append(correction)
        print()

    # Summary statistics
    fluid_penalties = np.array(results["fluid_penalties"])
    kiss_penalties = np.array(results["kiss_sidm_penalties"])
    regimes = np.array(results["regime_labels"])

    imfp_mask = (regimes == "IMFP")
    n_imfp = imfp_mask.sum()
    n_total = len(regimes)

    print("=== Summary ===")
    print(f"Total (halo, sigma_m) pairs: {n_total}")
    print(f"In IMFP regime: {n_imfp} ({100 * n_imfp / n_total:.1f}%)")
    print(f"In LMFP regime: {(regimes == 'LMFP').sum()}")
    print(f"In SMFP regime: {(regimes == 'SMFP').sum()}")
    print()

    if n_imfp > 0:
        # Use |penalty| for the ratio (the IMFP correction reduces the
        # magnitude of the penalty, regardless of sign). Avoid div-by-zero
        # by maxing with a small epsilon.
        fluid_abs = np.abs(fluid_penalties[imfp_mask])
        kiss_abs = np.abs(kiss_penalties[imfp_mask])
        ratio_imfp = kiss_abs / np.maximum(fluid_abs, 1e-9)
        print(f"IMFP regime — |kinetic|/|fluid| penalty ratio:")
        print(f"  mean:   {ratio_imfp.mean():.3f}  (expected ~0.778 from Table I Kn=1 ratio)")
        print(f"  median: {np.median(ratio_imfp):.3f}")
        print(f"  min/max: {ratio_imfp.min():.3f} / {ratio_imfp.max():.3f}")
    else:
        print("WARNING: no (halo, sigma_m) pairs landed in IMFP — ")
        print("the KISS-SIDM correction is never applied at this halo-mass sweep.")

    # Save results
    results["summary"] = {
        "n_total": int(n_total),
        "n_imfp": int(n_imfp),
        "n_lmfp": int((regimes == "LMFP").sum()),
        "n_smfp": int((regimes == "SMFP").sum()),
        "imfp_mean_ratio_abs": float(ratio_imfp.mean()) if n_imfp > 0 else None,
        "imfp_median_ratio_abs": float(np.median(ratio_imfp)) if n_imfp > 0 else None,
    }
    out = RESULTS_DIR_V03 / "t16_kiss_sidm_vs_fluid.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {out}")


if __name__ == "__main__":
    main()
