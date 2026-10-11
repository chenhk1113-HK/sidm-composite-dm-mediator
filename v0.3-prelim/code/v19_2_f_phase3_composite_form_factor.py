"""
v19_2_f_phase3_composite_form_factor.py — Priority 4: Composite form factor F²(q)

Project-premise extension: if DM is composite (Cloud-9 = composite dark matter
from the project's reference dataset), then the Yukawa propagator is NOT point-like
but has a form factor F(q) that suppresses at high momentum transfer q.

Hypothesis: a composite form factor could reshape sigma/m(v) to peak at
v = 29.4 km/s, where a point-like Yukawa cannot.

Simple ansatz: F(q) = 1 / (1 + q²/Λ_D²)  (dipole form factor)
                F(q) = exp(-q²/Λ_D²)        (Gaussian)

q in the CM frame: q = mu * v_rel (for elastic scattering)
At v = 29.4 km/s: q = 0.5 * 9.8e-5 = 4.9e-5 GeV = 49 keV
At v = 1000 km/s: q = 0.5 * 3.3e-3 = 1.7e-3 GeV = 1.7 MeV

So if Lambda_D ~ 50 keV, F(q=29.4 km/s) ~ 1/sqrt(2), F(q=1000 km/s) ~ 1/1000
This SHOULD give a peak at v ~ Lambda_D / m_chi ~ 50 keV / 1 GeV = 50,000 km/s
That's TOO HIGH. Need Lambda_D much smaller.

For Lambda_D ~ 1 keV: F(q=29.4) ~ 1 (still ~ 1), F(q=1000) ~ 1/100
Peak somewhere around 1 keV / 1 GeV * c = 300 km/s? No, that's not right.

Actually the form factor doesn't directly give a v-peak; it gives a q-suppression.
The peak in sigma/m(v) would come from the interplay between
  - the underlying Yukawa cross section (decreasing with v)
  - the form factor (also decreasing with v, but with different power)

Let me just compute it and see.
"""
import os
import math
import json
import sys
import numpy as np
from scipy.linalg import eigh_tridiagonal

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS_DIR)
sys.path.insert(0, os.path.dirname(_THIS_DIR))  # for constants.py
from constants import (
    M_CHI_GEV, MU_RED_GEV, C_KMS, HBAR_C_GEV_CM, compute_kappa,
    KAPPA_C_ANALYTIC, ALPHA_D,
)
from clawsgo_phase3_check import sigma_m_cm2_g
from constants import compute_kappa as compute_kappa_fn

OUTPUT_DIR = _THIS_DIR

V_TARGET_KMS = 29.4
TARGET_SIGMA = 174.0  # cm^2/g


def sigma_m_with_form_factor(v_kms, alpha_D, m_ap_GeV, Lambda_D_GeV,
                              form='dipole', m_chi_GeV=1.0):
    """
    sigma/m with a composite form factor F^2(q) applied.

    sigma_with_FF = sigma_point * F^2(q)

    where q = mu * v_rel (CM momentum transfer for elastic scattering).
    """
    # Compute point-like Yukawa sigma/m at this velocity
    v_c = v_kms / C_KMS
    sigT = None
    try:
        from clawsgo_phase3_check import sigma_T_partialwave
        sigT = sigma_T_partialwave(alpha_D, m_ap_GeV, v_c)
    except (ValueError, OverflowError, FloatingPointError):
        return None
    if sigT is None or math.isnan(sigT):
        return None
    sigma_point = sigma_m_cm2_g(sigT)

    # Form factor
    q = m_chi_GeV / 2.0 * v_kms / C_KMS  # GeV, CM momentum transfer
    if form == 'dipole':
        F2 = 1.0 / (1.0 + (q / Lambda_D_GeV)**2)**2
    elif form == 'gaussian':
        F2 = math.exp(-2.0 * (q / Lambda_D_GeV)**2)
    elif form == 'none':
        F2 = 1.0
    else:
        F2 = 1.0

    return sigma_point * F2


def main():
    print("=" * 70)
    print("=== Priority 4: Composite form factor F^2(q) ===")
    print("=" * 70)
    print(f"Target: sigma/m(v={V_TARGET_KMS} km/s) = {TARGET_SIGMA} cm^2/g as a PEAK")
    print(f"Form factor ansatz: dipole F(q) = 1/(1 + q^2/Lambda_D^2)")
    print(f"Convention: alpha_D = g^2/(4*pi) [LOCKED]")
    print()

    # Scan over Lambda_D and alpha_D, m_A'
    # Goal: find a parameter set where sigma/m(v=29.4) is a local maximum
    # in [5, 100] km/s

    print("Scanning Lambda_D in [1e-9, 1e-3] GeV (1 eV to 1 MeV)")
    print("Scanning alpha_D in [1e-6, 1e-2]")
    print("Scanning m_A' in [1e-9, 1e-3] GeV (1 keV to 1 MeV)")
    print()

    results = []
    Lambda_D_grid = np.logspace(-9, -3, 7)  # 7 points
    alpha_grid = np.logspace(-6, -2, 5)     # 5 points
    m_ap_grid = np.logspace(-9, -3, 7)      # 7 points
    v_test = [5.0, 10.0, 20.0, 29.4, 50.0, 100.0, 200.0]

    # Scan
    n_total = len(Lambda_D_grid) * len(alpha_grid) * len(m_ap_grid)
    n_done = 0
    for Lambda_D in Lambda_D_grid:
        for alpha_D in alpha_grid:
            for m_ap in m_ap_grid:
                n_done += 1
                sigma_v = []
                for v in v_test:
                    s = sigma_m_with_form_factor(v, alpha_D, m_ap, Lambda_D, form='dipole')
                    if s is None:
                        sigma_v.append(None)
                    else:
                        sigma_v.append(s)
                # Skip if any None
                if any(s is None for s in sigma_v):
                    continue
                # Check if v = 29.4 is a local maximum
                idx_29 = v_test.index(29.4)
                is_peak = all(sigma_v[idx_29] >= sigma_v[i] for i in range(len(sigma_v)) if i != idx_29)
                if is_peak and abs(sigma_v[idx_29] - TARGET_SIGMA) / TARGET_SIGMA < 0.3:
                    results.append({
                        "Lambda_D_eV": Lambda_D * 1e9,
                        "alpha_D": alpha_D,
                        "m_ap_eV": m_ap * 1e9,
                        "sigma_at_v": {f"v_{v}_kms": s for v, s in zip(v_test, sigma_v)},
                        "sigma_v29": sigma_v[idx_29],
                        "ratio_to_target": sigma_v[idx_29] / TARGET_SIGMA,
                        "kappa": compute_kappa_fn(alpha_D, M_CHI_GEV, m_ap),
                    })
                if n_done % 50 == 0:
                    print(f"  Progress: {n_done}/{n_total}, found {len(results)} peaks so far")

    print()
    print(f"Scan complete: tested {n_total} combinations, found {len(results)} with peak at v=29.4")
    print()

    if results:
        print("PEAK PARAMETER SETS:")
        for r in results[:10]:  # first 10
            print(f"  Lambda_D = {r['Lambda_D_eV']:.2e} eV, alpha_D = {r['alpha_D']:.2e}, m_ap = {r['m_ap_eV']:.2e} eV")
            print(f"    kappa = {r['kappa']:.3f}, sigma/m(29.4) = {r['sigma_v29']:.2f} cm^2/g")
    else:
        print("NO peak at v=29.4 found with composite form factor + dipole ansatz.")
        print("Try Gaussian form factor or different parameter range?")

    # Save results
    out_path = os.path.join(OUTPUT_DIR, "data", "results", "v19_2_f_phase3_composite_form_factor.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump({
            "_meta": {
                "description": "v19.2-F Phase 3 composite form factor scan (Priority 4)",
                "form": "dipole F(q) = 1/(1 + q^2/Lambda_D^2)",
                "target_velocity_kms": V_TARGET_KMS,
                "target_sigma_cm2_per_g": TARGET_SIGMA,
                "convention": "alpha_D = g^2/(4*pi) [LOCKED]",
            },
            "peaks_found": results,
        }, f, indent=2, default=str)
    print(f"\nResults saved: {out_path}")


if __name__ == "__main__":
    main()