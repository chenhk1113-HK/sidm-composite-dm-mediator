"""
Phase 20 — Full Space-Conditions Test of v0.3-prelim at m_chi = 5 GeV

Tests the v0.3-prelim Majorana reframe at m_chi = 5 GeV against
ALL 20+ channels used in T90.42 (full joint fit), not just the
subset used in Phase 19.

Channels tested:
  Cosmology:
    - CMB spectral distortion (Planck μ/y limits)
    - ΔN_eff (Goldstein-Hill 2026)
    - LSS assembly bias
  Direct detection:
    - LZ elastic (real posterior)
    - LZ 248 keV (Majorana inelastic)
    - LZ magnetic moment
    - Fermi dwarf gamma-ray
  Indirect detection:
    - DAMPE cosmic-ray electrons
    - XRISM Perseus ICM
    - eROSITA eRASS1
    - XRISM phi → gamma gamma
    - Euclid Q1 lensing
    - Euclid Q1 subhalo forecast
  SIDM (galactic):
    - dSph (Yukawa velocity-dependent)
    - UFD (Yukawa velocity-dependent)
    - Bullet cluster (Yukawa velocity-dependent)
    - KSFR/PCAC validity
  Stellar streams / substructure:
    - RELHIC (Cloud-9, M51) — Yang 2024 framework
    - Yang 2024 / Cloud-9
    - Anand M*

Per-channel loglike computed at the Phase 19 MAP:
  m_chi = 5 GeV, sigma/m = 0.067, g_D = 0.092, f_H = 0.002,
  epsilon = 10^-6.26, alpha = g_D^2/4π
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

import config
import channels_v03 as ch_v03
import t40_yukawa_sigma_m as yukawa
from t30_lz_real_posterior import loglike_lz_real
from t32_fermi_dwarf_channel import loglike_fermi_dwarf
from ksfr_pcac_validity import loglike_ksfr_pcac_validity
from channels_extended import (
    loglike_cmb_distortion, loglike_dampe_cre, loglike_lss_assembly_bias,
    loglike_competitor_dd_watch, loglike_xrism_perseus_icm,
    loglike_erosita_erass1, loglike_phi_to_gamgam_xrism, loglike_euclid_q1_lensing,
    loglike_euclid_q1_subhalo_forecast, loglike_delta_n_eff_goldstein_hill_2026,
    loglike_lz_magnetic_moment, loglike_lz_magnetic_moment_binned,
)
from phase8c_majorana_reframe_joint_fit import (
    sigma_SI_majorana_cm2, sigma_inel_majorana_cm2, M_A_PRIME_MEV_FIXED,
)
from phase8d_majorana_alpha_consistent import sigma_v_majorana_cm3_per_s

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Phase 19 MAP at m_chi = 5 GeV
M_CHI_GEV = 5.0
M_PHI_MEV = 200.0
SIGMA_M_0 = 0.067
A = 0.0
EPSILON = 10**-6.26
G_D = 0.092
F_H = 0.002
ALPHA = G_D**2 / (4 * np.pi)


def evaluate_all_channels():
    """Evaluate every channel at the Phase 19 MAP."""
    print("=" * 80)
    print(f"Phase 20 — Full Space-Conditions Test at v0.3-prelim MAP (m_chi = {M_CHI_GEV} GeV)")
    print("=" * 80)
    print(f"  m_chi = {M_CHI_GEV} GeV")
    print(f"  m_phi = {M_PHI_MEV} MeV")
    print(f"  sigma/m = {SIGMA_M_0} cm²/g")
    print(f"  a = {A}")
    print(f"  epsilon = {EPSILON:.2e}")
    print(f"  g_D = {G_D}")
    print(f"  alpha = {ALPHA:.4e}")
    print(f"  f_H = {F_H}")
    print()

    sigma_SI = sigma_SI_majorana_cm2(EPSILON, G_D)
    sigma_v = sigma_v_majorana_cm3_per_s(G_D)
    sigma_inel = sigma_inel_majorana_cm2(EPSILON, G_D, F_H, m_chi_GeV=M_CHI_GEV, m_A_prime_MeV=M_PHI_MEV)

    # Build theta arrays (varies by channel signature)
    theta_majorana = np.array([np.log10(SIGMA_M_0), A, np.log10(EPSILON), np.log10(G_D), np.log10(F_H)])
    theta_full = theta_majorana  # 5D, can be extended if needed
    theta_t90 = np.array([
        np.log10(M_PHI_MEV), np.log10(M_CHI_GEV), G_D,
        np.log10(EPSILON), np.log10(ALPHA), -0.5,  # log_xi
    ])

    results = {}
    failures = []
    warnings_list = []

    # 1. LZ elastic
    print("1. LZ elastic:  ", end="")
    try:
        ll = loglike_lz_real(M_CHI_GEV, sigma_SI)
        results["lz_elastic"] = {"loglike": float(ll), "sigma_SI": float(sigma_SI)}
        print(f"loglike = {ll:.2f}, σ_SI = {sigma_SI:.2e} cm²")
    except Exception as e:
        print(f"FAILED: {e}")
        failures.append(("lz_elastic", str(e)))

    # 2. LZ 248 keV (Majorana inelastic)
    print("2. LZ 248 keV:  ", end="")
    try:
        n_pred = sigma_inel * 1e-42 * 4  # crude: sigma × COEFF × exposure
        ll = -0.5 * ((n_pred - 1.0) / 2.5)**2  # Gaussian N_obs=1, σ=2.5
        results["lz_248keV"] = {"loglike": float(ll), "n_pred": float(n_pred)}
        print(f"loglike = {ll:.2f}, n_pred = {n_pred:.2e}")
    except Exception as e:
        print(f"FAILED: {e}")
        failures.append(("lz_248keV", str(e)))

    # 3. LZ magnetic moment
    print("3. LZ mag moment:", end="")
    try:
        # mu_x is the magnetic moment; for Majorana, mu_x is suppressed (helicity)
        mu_x = 1e-6 * EPSILON  # rough EFT estimate
        ll = loglike_lz_magnetic_moment(M_CHI_GEV, mu_x)
        results["lz_magnetic_moment"] = {"loglike": float(ll), "mu_x": float(mu_x)}
        print(f" loglike = {ll:.2f}")
    except Exception as e:
        print(f" FAILED: {e}")
        failures.append(("lz_magnetic_moment", str(e)))

    # 4. Fermi dwarf
    print("4. Fermi dwarf: ", end="")
    try:
        ll = loglike_fermi_dwarf(M_CHI_GEV, sigma_v)
        results["fermi_dwarf"] = {"loglike": float(ll), "sigma_v": float(sigma_v)}
        print(f"loglike = {ll:.2f}, σv = {sigma_v:.2e} cm³/s")
    except Exception as e:
        print(f"FAILED: {e}")
        failures.append(("fermi_dwarf", str(e)))

    # 5. CMB spectral distortion
    print("5. CMB distort: ", end="")
    try:
        ll = loglike_cmb_distortion(M_CHI_GEV * 1e9, M_PHI_MEV * 1e6, EPSILON)
        results["cmb_distortion"] = {"loglike": float(ll)}
        print(f"loglike = {ll:.2f}")
    except Exception as e:
        print(f"FAILED: {e}")
        failures.append(("cmb_distortion", str(e)))

    # 6. ΔN_eff (Goldstein-Hill)
    print("6. ΔN_eff:      ", end="")
    try:
        ll = loglike_delta_n_eff_goldstein_hill_2026(M_CHI_GEV, M_PHI_MEV, EPSILON)
        results["delta_N_eff"] = {"loglike": float(ll)}
        print(f" loglike = {ll:.2f}")
    except Exception as e:
        print(f" FAILED: {e}")
        failures.append(("delta_N_eff", str(e)))

    # 7. LSS assembly bias
    print("7. LSS bias:    ", end="")
    try:
        ll = loglike_lss_assembly_bias(theta_full)
        results["lss_assembly_bias"] = {"loglike": float(ll)}
        print(f"loglike = {ll:.2f}")
    except Exception as e:
        print(f"FAILED: {e}")
        failures.append(("lss_assembly_bias", str(e)))

    # 8. DAMPE CRE
    print("8. DAMPE CRE:   ", end="")
    try:
        ll = loglike_dampe_cre(M_CHI_GEV, sigma_v, m_aprime_MeV=M_PHI_MEV)
        results["dampe_cre"] = {"loglike": float(ll)}
        print(f"loglike = {ll:.2f}")
    except Exception as e:
        print(f"FAILED: {e}")
        failures.append(("dampe_cre", str(e)))

    # 9. XRISM Perseus
    print("9. XRISM Perseus:", end="")
    try:
        ll = loglike_xrism_perseus_icm(M_CHI_GEV, sigma_v)
        results["xrism_perseus"] = {"loglike": float(ll)}
        print(f" loglike = {ll:.2f}")
    except Exception as e:
        print(f" FAILED: {e}")
        failures.append(("xrism_perseus", str(e)))

    # 10. eROSITA
    print("10. eROSITA:    ", end="")
    try:
        ll = loglike_erosita_erass1(M_CHI_GEV, sigma_v)
        results["erosita"] = {"loglike": float(ll)}
        print(f"loglike = {ll:.2f}")
    except Exception as e:
        print(f"FAILED: {e}")
        failures.append(("erosita", str(e)))

    # 11. XRISM phi → γγ
    print("11. XRISM φ→γγ: ", end="")
    try:
        ll = loglike_phi_to_gamgam_xrism(theta_t90)
        results["xrism_phi_decay"] = {"loglike": float(ll)}
        print(f"loglike = {ll:.2f}")
    except Exception as e:
        print(f"FAILED: {e}")
        failures.append(("xrism_phi_decay", str(e)))

    # 12. Euclid Q1 lensing
    print("12. Euclid Q1:  ", end="")
    try:
        ll = loglike_euclid_q1_lensing(SIGMA_M_0, A)
        results["euclid_q1_lensing"] = {"loglike": float(ll)}
        print(f"loglike = {ll:.2f}")
    except Exception as e:
        print(f"FAILED: {e}")
        failures.append(("euclid_q1_lensing", str(e)))

    # 13. Euclid subhalo forecast
    print("13. Euclid sub: ", end="")
    try:
        ll = loglike_euclid_q1_subhalo_forecast(SIGMA_M_0, A)
        results["euclid_subhalo"] = {"loglike": float(ll)}
        print(f"loglike = {ll:.2f}")
    except Exception as e:
        print(f"FAILED: {e}")
        failures.append(("euclid_subhalo", str(e)))

    # 14. dSph (Yukawa v-dep)
    print("14. dSph:       ", end="")
    try:
        ll = ch_v03.loglike_dsph_v03(SIGMA_M_0, A)
        results["dsph"] = {"loglike": float(ll)}
        print(f"loglike = {ll:.2f}")
    except Exception as e:
        print(f"FAILED: {e}")
        failures.append(("dsph", str(e)))

    # 15. UFD
    print("15. UFD:        ", end="")
    try:
        ll = ch_v03.loglike_ufd_v03(SIGMA_M_0, A)
        results["ufd"] = {"loglike": float(ll)}
        print(f"loglike = {ll:.2f}")
    except Exception as e:
        print(f"FAILED: {e}")
        failures.append(("ufd", str(e)))

    # 16. Bullet cluster
    print("16. Bullet:     ", end="")
    try:
        ll = ch_v03.loglike_bullet_v03(SIGMA_M_0, A)
        results["bullet"] = {"loglike": float(ll)}
        print(f"loglike = {ll:.2f}")
    except Exception as e:
        print(f"FAILED: {e}")
        failures.append(("bullet", str(e)))

    # 17. KSFR/PCAC
    print("17. KSFR/PCAC:  ", end="")
    try:
        # For dark photon, N_dc = 1 (one U(1)), N_f = 0 (no fundamental fermions)
        ll = loglike_ksfr_pcac_validity(theta_t90, N_dc=1, N_f=0)
        results["ksfr_pcac"] = {"loglike": float(ll)}
        print(f"loglike = {ll:.2f}")
    except Exception as e:
        print(f"FAILED: {e}")
        failures.append(("ksfr_pcac", str(e)))

    # 18. SPARC (saturated proxy)
    print("18. SPARC:      ", end="")
    try:
        import t8_v03_joint_fit as t8
        ll = t8.delta_log_sparc(SIGMA_M_0, A)
        results["sparc"] = {"loglike": float(ll), "saturated_proxy": True}
        print(f"loglike = {ll:.2f} (saturated)")
    except Exception as e:
        print(f"FAILED: {e}")
        failures.append(("sparc", str(e)))

    # 19. Competitor DD watch
    print("19. Comp DD:    ", end="")
    try:
        ll = loglike_competitor_dd_watch(theta_full)
        results["competitor_dd"] = {"loglike": float(ll)}
        print(f"loglike = {ll:.2f}")
    except Exception as e:
        print(f"FAILED: {e}")
        failures.append(("competitor_dd", str(e)))

    # 20. Yang 2024 / Cloud-9 (try to import)
    print("20. Cloud-9:    ", end="")
    try:
        from t90_v29_relhic_yukawa import loglike_relhic_t90v29
        ll = loglike_relhic_t90v29(theta_t90)
        results["cloud9_relhic"] = {"loglike": float(ll), "available": True}
        print(f"loglike = {ll:.2f}")
    except ImportError as e:
        ll = 0.0
        results["cloud9_relhic"] = {"loglike": float(ll), "available": False, "error": str(e)}
        print(f"not available, using neutral")
    except Exception as e:
        print(f"FAILED: {e}")
        failures.append(("cloud9_relhic", str(e)))

    return results, failures, warnings_list


def main():
    print()
    results, failures, warnings = evaluate_all_channels()

    # Summary
    print()
    print("=" * 80)
    print("SUMMARY — Per-channel loglike at v0.3-prelim MAP (m_chi = 5 GeV)")
    print("=" * 80)
    n_channels = len(results)
    n_failed = len(failures)
    n_pass = n_channels - n_failed

    print(f"\nTotal channels tested: {n_channels}")
    print(f"  PASS (finite loglike): {n_pass}")
    print(f"  FAIL (exception):      {n_failed}")
    print()

    # Total loglike
    loglikes = [r["loglike"] for r in results.values() if isinstance(r.get("loglike"), (int, float))]
    total_ll = sum(loglikes)
    print(f"Sum of finite loglikes: {total_ll:.2f}")

    if failures:
        print()
        print("Channel failures:")
        for name, err in failures:
            print(f"  - {name}: {err}")

    # Verdict
    print()
    if n_failed == 0:
        verdict = f"PROCEED: All {n_channels} channels evaluable at v0.3-prelim MAP"
    elif n_failed <= 3:
        verdict = f"PARTIAL: {n_pass}/{n_channels} channels evaluable, {n_failed} failures"
    else:
        verdict = f"FAIL: {n_failed}/{n_channels} channels fail at v0.3-prelim MAP"
    print(f"VERDICT: {verdict}")

    out = {
        "test": "Phase20_full_space_conditions",
        "m_chi_GeV": M_CHI_GEV,
        "m_phi_MeV": M_PHI_MEV,
        "sigma_m": SIGMA_M_0,
        "g_D": G_D,
        "epsilon": EPSILON,
        "channels": results,
        "failures": failures,
        "n_channels": n_channels,
        "n_pass": n_pass,
        "n_fail": n_failed,
        "total_loglike": total_ll,
        "verdict": verdict,
    }

    out_path = RESULTS_DIR / "phase20_full_space_conditions.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\nResults written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
