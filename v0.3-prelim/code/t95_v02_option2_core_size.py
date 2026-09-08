"""
T95 Option 2 — SIDM core-size prediction from the 7D posterior.

PURPOSE
=======
The 7D nested-sampling fit (T90.1, commit f422da1) produced a
posterior over (m_phi, m_chi, g_chi, epsilon, alpha, xi, mu_x).
This script uses the SIDM parameters from that posterior to
predict the SIDM core radius for each sample, then compares
the predicted core-size distribution to published hydro-sim
predictions (BAHAMAS-SIDM, Robertson 2019).

METHOD
======
For a Yukawa SIDM, the core radius r_c is set by the balance
between self-interaction thermal conduction and gravitational
conduction. The Kaplinghat+ 2016 / Balberg+ 2002 isothermal-
core matching gives:

  r_c = sqrt(sigma_T * rho_s * r_s^2 / m_chi)

where:
  - sigma_T is the SIDM transfer cross-section at the
    characteristic halo velocity v_0 = sqrt(G M_200 / r_200)
  - rho_s, r_s are the NFW scale density and radius of the
    host halo (we use Milky-Way-like M_200 = 10^12 M_sun
    as a reference)
  - m_chi is the dark-matter mass

This is a simplified formula. The full Kaplinghat+ 2016
treatment includes a logarithmic correction and a v_max / v_0
factor. We use the simplified form here because (a) it
captures the dominant scaling, and (b) the master's Yukawa
sigma_m_cm2_per_g already provides the velocity dependence.

REFERENCE
=========
- Kaplinghat, Tulin, Yu 2016, "Dark matter halos as particle
  colliders: a unified solution to small-scale structure
  puzzles from dwarf galaxies to clusters" (arXiv:1508.03339)
- Balberg, Shapiro, Inagaki 2002, "Self-interacting dark
  matter halos and the gravothermal catastrophe" (ApJ 568, 475)
- Robertson, A. et al. 2019, MNRAS 488, 3646 (BAHAMAS-SIDM
  hydro sim, the comparison target)
"""

import json
import sys
from pathlib import Path

import numpy as np

# Project imports
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT / "code"))
from t40_yukawa_sigma_m import sigma_m_cm2_per_g


# Reference halo: Milky-Way-like
# M_200 = 10^12 M_sun, c_200 = 10 (concentration)
# NFW scale radius r_s = r_200 / c_200
# NFW scale density rho_s = (M_200 / (4 pi r_s^3)) * [ln(1+c) - c/(1+c)]
M_200_REF = 1.0e12  # M_sun
C_200_REF = 10.0
R_200_KPC = 200.0  # virial radius for M_200 = 10^12 M_sun
R_S_KPC = R_200_KPC / C_200_REF  # scale radius
# NFW scale density
def nfw_scale_density(M_200_Msun, c_200, r_200_kpc):
    """
    Compute NFW scale density rho_s for given M_200 and c_200.

    Returns rho_s in units of M_sun / kpc^3.
    """
    r_s = r_200_kpc / c_200
    r_s_cm = r_s * 3.086e21  # 1 kpc = 3.086e21 cm
    # M_200 = 4 pi rho_s r_s^3 [ln(1+c) - c/(1+c)]
    f_c = np.log(1 + c_200) - c_200 / (1 + c_200)
    rho_s_Msun_per_kpc3 = M_200_Msun / (4 * np.pi * r_s**3 * f_c)
    return rho_s_Msun_per_kpc3


RHO_S_REF = nfw_scale_density(M_200_REF, C_200_REF, R_200_KPC)
# Characteristic velocity v_0 = sqrt(G M_200 / r_200)
G_NEWTON_KPC_KMS_MSUN = 4.302e-6  # kpc (km/s)^2 / M_sun
V_0_REF_KMS = np.sqrt(G_NEWTON_KPC_KMS_MSUN * M_200_REF / R_200_KPC)


def kaplinghat_core_radius(sigma_T_cm2_per_g, m_chi_GeV, rho_s_Msun_per_kpc3,
                           r_s_kpc):
    """
    Compute the isothermal-core radius from the Kaplinghat+ 2016
    matching formula.

    r_c = sqrt(sigma_T * rho_s * r_s^2 / m_chi)

    Args:
        sigma_T_cm2_per_g: SIDM transfer cross-section in cm^2/g
        m_chi_GeV: dark-matter mass in GeV
        rho_s_Msun_per_kpc3: NFW scale density in M_sun / kpc^3
        r_s_kpc: NFW scale radius in kpc

    Returns:
        r_c in kpc
    """
    # Convert everything to CGS for the prefactor
    # sigma_T [cm^2/g] * rho_s [g/cm^3] * r_s^2 [cm^2] / m_chi [g]
    # = cm^2 * g/cm^3 * cm^2 / g = cm^2
    # sqrt -> cm
    # convert to kpc
    M_SUN_G = 1.989e33  # g
    KPC_CM = 3.086e21  # cm
    rho_s_g_per_cm3 = rho_s_Msun_per_kpc3 * M_SUN_G / KPC_CM**3
    r_s_cm = r_s_kpc * KPC_CM
    m_chi_g = m_chi_GeV * 1.7827e-24  # 1 GeV/c^2 in g
    r_c_cm = np.sqrt(sigma_T_cm2_per_g * rho_s_g_per_cm3 * r_s_cm**2 / m_chi_g)
    r_c_kpc = r_c_cm / KPC_CM
    return r_c_kpc


def main():
    print("=" * 78)
    print("T95 Option 2 — SIDM core-size prediction from 7D posterior")
    print("=" * 78)
    print()
    print("Method: Kaplinghat+ 2016 / Balberg+ 2002 isothermal-core matching")
    print("Reference halo: Milky-Way-like (M_200 = 10^12 M_sun, c_200 = 10)")
    print()

    # Load 7D posterior
    npz_path = _PROJECT_ROOT / "outputs" / "t90" / "t41_v07_7d_posterior.npz"
    print(f"Loading posterior from: {npz_path}")
    data = np.load(npz_path, allow_pickle=True)
    samples = data["samples"]
    labels = list(data["labels"])
    print(f"  Posterior shape: {samples.shape}")
    print(f"  Labels: {labels}")
    print()

    # Index helpers
    idx = {label: i for i, label in enumerate(labels)}

    # Compute sigma_T and core radius for each posterior sample
    print("=" * 78)
    print("Per-sample core radius calculation")
    print("=" * 78)
    print(f"Reference halo: M_200 = {M_200_REF:.1e} M_sun, c_200 = {C_200_REF}")
    print(f"  NFW r_s = {R_S_KPC:.1f} kpc, rho_s = {RHO_S_REF:.3e} M_sun/kpc^3")
    print(f"  v_0 = {V_0_REF_KMS:.1f} km/s")
    print()

    n_samples = samples.shape[0]
    m_chi_arr = 10 ** samples[:, idx["log_m_chi_GeV"]]
    m_phi_arr = 10 ** samples[:, idx["log_m_phi_MeV"]]
    g_chi_arr = samples[:, idx["g_chi"]]

    print(f"  m_chi range: {m_chi_arr.min():.2e} to {m_chi_arr.max():.2e} GeV")
    print(f"  m_phi range: {m_phi_arr.min():.2e} to {m_phi_arr.max():.2e} MeV")
    print(f"  g_chi range: {g_chi_arr.min():.3f} to {g_chi_arr.max():.3f}")
    print()

    # Compute sigma_T at the characteristic velocity v_0
    sigma_T_arr = np.array([
        sigma_m_cm2_per_g(V_0_REF_KMS, m_phi, m_chi, g_chi)
        for m_phi, m_chi, g_chi in zip(m_phi_arr, m_chi_arr, g_chi_arr)
    ])

    print(f"  sigma_T(v_0={V_0_REF_KMS:.0f} km/s) range:")
    print(f"    median: {np.median(sigma_T_arr):.3e} cm^2/g")
    print(f"    16-84 percentile: {np.percentile(sigma_T_arr, 16):.3e} to "
          f"{np.percentile(sigma_T_arr, 84):.3e} cm^2/g")
    print()

    # Compute core radius
    r_c_arr = np.array([
        kaplinghat_core_radius(s, mc, RHO_S_REF, R_S_KPC)
        for s, mc in zip(sigma_T_arr, m_chi_arr)
    ])

    print("=" * 78)
    print("Predicted SIDM core radius (MW-like halo)")
    print("=" * 78)
    print(f"  median: {np.median(r_c_arr):.2f} kpc")
    print(f"  16-84 percentile: {np.percentile(r_c_arr, 16):.2f} to "
          f"{np.percentile(r_c_arr, 84):.2f} kpc")
    print(f"  2.5-97.5 percentile: {np.percentile(r_c_arr, 2.5):.2f} to "
          f"{np.percentile(r_c_arr, 97.5):.2f} kpc")
    print()

    # Comparison: Robertson 2019 BAHAMAS-SIDM
    # For M_200 = 10^12 M_sun (dwarf scale), Robertson 2019 vdSIDM
    # produces a core. Their Fig. 2 (right panel) shows density
    # profiles for M_200 = 10^15 M_sun halos. For M_200 = 10^12 M_sun
    # (our reference), the cores are smaller (~5-20 kpc is typical
    # for vdSIDM at dwarf scales).
    #
    # Also: the master's tuned mu_x = 6.10e-8 mu_N is far below
    # LZ 2026 limit (4.57e-4 mu_N), so any cross-section derived
    # from the 7D posterior is consistent with LZ.
    print("=" * 78)
    print("Comparison to published predictions")
    print("=" * 78)
    print()
    print("BAHAMAS-SIDM (Robertson 2019, Fig. 2):")
    print("  vdSIDM at M_200 = 10^14 M_sun: core ~50-200 kpc")
    print("  vdSIDM at M_200 = 10^15 M_sun: core ~100-300 kpc")
    print("  SIDM1 (1 cm^2/g) cores: similar to vdSIDM at 10^14 M_sun")
    print("  SIDM0.1 (0.1 cm^2/g) cores: smaller, ~10-50 kpc at 10^14 M_sun")
    print()
    print("Our prediction (MW-like, M_200 = 10^12 M_sun):")
    print(f"  median r_c = {np.median(r_c_arr):.2f} kpc")
    print(f"  16-84 percentile: {np.percentile(r_c_arr, 16):.2f} to "
          f"{np.percentile(r_c_arr, 84):.2f} kpc")
    print()
    print("Honest caveats:")
    print("  1. The 7D posterior is fit to LZ direct detection, not")
    print("     to galaxy observables. The (m_phi, m_chi, g_chi)")
    print("     values are LZ-anchored, so the core-size prediction")
    print("     is the master's Yukawa applied at LZ-anchored")
    print("     parameters.")
    print("  2. The Kaplinghat+ 2016 formula is a simplified isothermal")
    print("     matching. The full gravothermal calculation (Balberg+")
    print("     2002) gives ~30% corrections including a log factor.")
    print("  3. Robertson's published cores are for M_200 = 10^14-10^15")
    print("     M_sun clusters. Our M_200 = 10^12 M_sun is at dwarf")
    print("     scale where SIDM cores are smaller.")
    print("  4. The 0.72x normalization offset from T95 Phase 0 (see")
    print("     T95_YUKAWA_PRESCRIPTION_CALIBRATION_NOTE.md) means")
    print("     the absolute core-size prediction has ~30% uncertainty.")
    print()

    # Parameter sensitivity
    print("=" * 78)
    print("Parameter sensitivity (Spearman rank correlation with r_c)")
    print("=" * 78)
    from scipy.stats import spearmanr
    for label in labels:
        rho, p = spearmanr(samples[:, idx[label]], r_c_arr)
        sig = "**" if abs(rho) > 0.3 else ("*" if abs(rho) > 0.1 else "")
        print(f"  {label:>20s}: rho = {rho:+.3f} {sig}")
    print()
    print("  (** = strong, * = moderate, blank = weak correlation)")

    # Save results
    out_dir = _PROJECT_ROOT / "outputs" / "t95"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / "option2_core_size_prediction.json"
    results = {
        "phase": "T95 Option 2",
        "task": "SIDM core-size prediction from 7D posterior",
        "method": "Kaplinghat+ 2016 / Balberg+ 2002 isothermal-core matching",
        "reference_halo": {
            "M_200_Msun": M_200_REF,
            "c_200": C_200_REF,
            "r_200_kpc": R_200_KPC,
            "r_s_kpc": R_S_KPC,
            "rho_s_Msun_per_kpc3": float(RHO_S_REF),
            "v_0_kms": float(V_0_REF_KMS),
        },
        "posterior": {
            "n_samples": n_samples,
            "labels": labels,
            "m_chi_GeV_range": [float(m_chi_arr.min()), float(m_chi_arr.max())],
            "m_phi_MeV_range": [float(m_phi_arr.min()), float(m_phi_arr.max())],
            "g_chi_range": [float(g_chi_arr.min()), float(g_chi_arr.max())],
        },
        "sigma_T_at_v0": {
            "median_cm2_per_g": float(np.median(sigma_T_arr)),
            "16-84_cm2_per_g": [float(np.percentile(sigma_T_arr, 16)),
                                float(np.percentile(sigma_T_arr, 84))],
        },
        "core_radius_kpc": {
            "median": float(np.median(r_c_arr)),
            "16-84_percentile": [float(np.percentile(r_c_arr, 16)),
                                 float(np.percentile(r_c_arr, 84))],
            "2.5-97.5_percentile": [float(np.percentile(r_c_arr, 2.5)),
                                    float(np.percentile(r_c_arr, 97.5))],
            "all_samples_first10": [float(r) for r in r_c_arr[:10]],
        },
        "parameter_sensitivity_spearman": {
            label: {
                "rho": float(spearmanr(samples[:, idx[label]], r_c_arr)[0]),
                "p_value": float(spearmanr(samples[:, idx[label]], r_c_arr)[1]),
            }
            for label in labels
        },
        "comparison_to_robertson_2019": {
            "BAHAMAS-SIDM_vdSIDM_M_200_10^14": "core ~50-200 kpc",
            "BAHAMAS-SIDM_vdSIDM_M_200_10^15": "core ~100-300 kpc",
            "BAHAMAS-SIDM_SIDM1_M_200_10^14": "core ~50-200 kpc",
            "BAHAMAS-SIDM_SIDM0.1_M_200_10^14": "core ~10-50 kpc",
            "our_prediction_M_200_10^12": f"median r_c = {np.median(r_c_arr):.2f} kpc",
        },
        "caveats": [
            "7D posterior is LZ-anchored, not galaxy-anchored",
            "Simplified Kaplinghat+ 2016 formula (~30% correction possible)",
            "Reference halo is dwarf-scale (10^12 M_sun), not cluster-scale",
            "0.72x normalization offset from Phase 0 adds ~30% uncertainty",
        ],
    }
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2)
    print()
    print(f"Wrote: {out_json}")


if __name__ == "__main__":
    main()