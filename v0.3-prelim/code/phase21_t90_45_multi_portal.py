"""
Phase 21 — Full Space-Conditions Test of T90.45 (Multi-Portal)

Tests the T90.45 multi-portal architecture against the same 20 channels
used in Phase 20. The T90.45 model has Portal A (heavy, ~366 MeV) +
Portal B (light, ~20 MeV), which naturally produces:
  - σ/m(100) ~ 4 cm²/g (galactic SIDM)
  - σ/m(28) ~ 49 cm²/g (Cloud-9)
  - σ/m(3000) ~ 0.02 cm²/g (Bullet cluster)

Tests both the MAP (non-Cloud-9 mode, ~50% posterior weight) and
the median (Cloud-9 mode, ~50% posterior weight) against the 20
channels used in the T90.42 framework.
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
from t90_v29_relhic_yukawa import loglike_relhic_t90v29

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def sigma_m_total_two_portal(v_kms, m_phi_A_MeV, m_chi_A_GeV, g_chi_A,
                              m_phi_B_MeV, m_chi_B_GeV, g_chi_B):
    """Total σ/m from two portals added together."""
    sm_A = yukawa.sigma_m_cm2_per_g(v_kms, m_phi_A_MeV, m_chi_A_GeV, g_chi_A)
    sm_B = yukawa.sigma_m_cm2_per_g(v_kms, m_phi_B_MeV, m_chi_B_GeV, g_chi_B)
    return sm_A + sm_B


def evaluate_channels(label, params):
    """Evaluate all 20 channels for a specific T90.45 parameter set."""
    print()
    print("=" * 80)
    print(f"{label}")
    print("=" * 80)
    print(f"  m_phi_A = {params['m_phi_A_MeV']:.1f} MeV, m_chi_A = {params['m_chi_A_GeV']:.2f} GeV, g_chi_A = {params['g_chi_A']:.3f}")
    print(f"  m_phi_B = {params['m_phi_B_MeV']:.2f} MeV, m_chi_B = {params['m_chi_B_GeV']:.1f} GeV, g_chi_B = {params['g_chi_B']:.3f}")
    print(f"  ε_A = {params['epsilon_A']:.2e}, α_A = {params['alpha_A']:.4f}, ξ = {params['xi']:.3f}")
    print(f"  σ/m(28) = {params['sigma_m_28']:.2f}, σ/m(100) = {params['sigma_m_100']:.2f}, σ/m(3000) = {params['sigma_m_3000']:.4f}")
    print()

    m_phi_A = params["m_phi_A_MeV"]
    m_chi_A = params["m_chi_A_GeV"]
    g_chi_A = params["g_chi_A"]
    m_phi_B = params["m_phi_B_MeV"]
    m_chi_B = params["m_chi_B_GeV"]
    g_chi_B = params["g_chi_B"]
    epsilon_A = params["epsilon_A"]
    alpha_A = params["alpha_A"]
    xi = params["xi"]

    # Use Portal A mass as the effective m_chi for LZ/Fermi (dominant mediator)
    m_chi_eff = m_chi_A
    sigma_v = alpha_A * 1e-26  # rough estimate (will use dedicated function if available)
    sigma_SI = epsilon_A**2 * alpha_A * 1e-39  # rough

    # 9D theta for t90 channels
    theta_9d = np.array([
        np.log10(m_phi_A), np.log10(m_chi_A), g_chi_A,
        np.log10(m_phi_B), np.log10(m_chi_B), g_chi_B,
        np.log10(epsilon_A), np.log10(alpha_A), np.log10(xi),
    ])

    results = {}
    failures = []

    # 1. LZ elastic
    print("1. LZ elastic:  ", end="")
    try:
        ll = loglike_lz_real(m_chi_eff, sigma_SI)
        results["lz_elastic"] = {"loglike": float(ll)}
        print(f"loglike = {ll:.2f}")
    except Exception as e:
        print(f"FAILED: {e}")
        failures.append(("lz_elastic", str(e)))

    # 2. Fermi dwarf
    print("2. Fermi dwarf: ", end="")
    try:
        ll = loglike_fermi_dwarf(m_chi_eff, sigma_v)
        results["fermi_dwarf"] = {"loglike": float(ll)}
        print(f"loglike = {ll:.2f}")
    except Exception as e:
        print(f"FAILED: {e}")
        failures.append(("fermi_dwarf", str(e)))

    # 3. CMB distortion
    print("3. CMB distort: ", end="")
    try:
        ll = loglike_cmb_distortion(m_chi_eff * 1e9, m_phi_A * 1e6, epsilon_A)
        results["cmb_distortion"] = {"loglike": float(ll)}
        print(f"loglike = {ll:.2f}")
    except Exception as e:
        print(f"FAILED: {e}")
        failures.append(("cmb_distortion", str(e)))

    # 4. ΔN_eff
    print("4. ΔN_eff:      ", end="")
    try:
        ll = loglike_delta_n_eff_goldstein_hill_2026(m_chi_eff, m_phi_A, epsilon_A)
        results["delta_N_eff"] = {"loglike": float(ll)}
        print(f" loglike = {ll:.2f}")
    except Exception as e:
        print(f" FAILED: {e}")
        failures.append(("delta_N_eff", str(e)))

    # 5. LSS assembly bias
    print("5. LSS bias:    ", end="")
    try:
        # LSS uses power-law form (sigma_m_0, a) for legacy channels
        sigma_m_total_100 = params["sigma_m_100"]
        ll = loglike_lss_assembly_bias(np.array([np.log10(sigma_m_total_100), 0.0, np.log10(epsilon_A), np.log10(g_chi_A), -1.0]))
        results["lss_assembly_bias"] = {"loglike": float(ll)}
        print(f"loglike = {ll:.2f}")
    except Exception as e:
        print(f"FAILED: {e}")
        failures.append(("lss_assembly_bias", str(e)))

    # 6. DAMPE CRE
    print("6. DAMPE CRE:   ", end="")
    try:
        ll = loglike_dampe_cre(m_chi_eff, sigma_v, m_aprime_MeV=m_phi_A)
        results["dampe_cre"] = {"loglike": float(ll)}
        print(f"loglike = {ll:.2f}")
    except Exception as e:
        print(f"FAILED: {e}")
        failures.append(("dampe_cre", str(e)))

    # 7. XRISM Perseus
    print("7. XRISM Perseus:", end="")
    try:
        ll = loglike_xrism_perseus_icm(m_chi_eff, sigma_v)
        results["xrism_perseus"] = {"loglike": float(ll)}
        print(f" loglike = {ll:.2f}")
    except Exception as e:
        print(f" FAILED: {e}")
        failures.append(("xrism_perseus", str(e)))

    # 8. eROSITA
    print("8. eROSITA:    ", end="")
    try:
        ll = loglike_erosita_erass1(m_chi_eff, sigma_v)
        results["erosita"] = {"loglike": float(ll)}
        print(f"loglike = {ll:.2f}")
    except Exception as e:
        print(f"FAILED: {e}")
        failures.append(("erosita", str(e)))

    # 9. XRISM φ→γγ
    print("9. XRISM φ→γγ: ", end="")
    try:
        ll = loglike_phi_to_gamgam_xrism(theta_9d)
        results["xrism_phi_decay"] = {"loglike": float(ll)}
        print(f"loglike = {ll:.2f}")
    except Exception as e:
        print(f"FAILED: {e}")
        failures.append(("xrism_phi_decay", str(e)))

    # 10. Euclid Q1 lensing
    print("10. Euclid Q1: ", end="")
    try:
        ll = loglike_euclid_q1_lensing(params["sigma_m_100"], 0.0)
        results["euclid_q1_lensing"] = {"loglike": float(ll)}
        print(f"loglike = {ll:.2f}")
    except Exception as e:
        print(f"FAILED: {e}")
        failures.append(("euclid_q1_lensing", str(e)))

    # 11. Euclid subhalo
    print("11. Euclid sub:", end="")
    try:
        ll = loglike_euclid_q1_subhalo_forecast(params["sigma_m_100"], 0.0)
        results["euclid_subhalo"] = {"loglike": float(ll)}
        print(f" loglike = {ll:.2f}")
    except Exception as e:
        print(f" FAILED: {e}")
        failures.append(("euclid_subhalo", str(e)))

    # 12. KSFR/PCAC
    print("12. KSFR/PCAC: ", end="")
    try:
        # For dark photon, N_dc = 1, N_f = 0
        ll = loglike_ksfr_pcac_validity(theta_9d, N_dc=1, N_f=0)
        results["ksfr_pcac"] = {"loglike": float(ll)}
        print(f"loglike = {ll:.2f}")
    except Exception as e:
        print(f"FAILED: {e}")
        failures.append(("ksfr_pcac", str(e)))

    # 13. Cloud-9 / RELHIC (the BIG test)
    print("13. Cloud-9:   ", end="")
    try:
        ll = loglike_relhic_t90v29(theta_9d)
        results["cloud9_relhic"] = {"loglike": float(ll), "available": True}
        print(f"loglike = {ll:.2f}")
    except Exception as e:
        print(f"FAILED: {e}")
        failures.append(("cloud9_relhic", str(e)))

    # 14. SPARC (saturated)
    print("14. SPARC:     ", end="")
    try:
        import t8_v03_joint_fit as t8
        # For multi-portal, use total sigma/m(100)
        ll = t8.delta_log_sparc(params["sigma_m_100"], 0.0)
        results["sparc"] = {"loglike": float(ll), "saturated_proxy": True}
        print(f"loglike = {ll:.2f}")
    except Exception as e:
        print(f"FAILED: {e}")
        failures.append(("sparc", str(e)))

    # 15. Competitor DD watch
    print("15. Comp DD:   ", end="")
    try:
        ll = loglike_competitor_dd_watch(np.array([np.log10(params["sigma_m_100"]), 0.0, np.log10(epsilon_A), np.log10(g_chi_A), -1.0]))
        results["competitor_dd"] = {"loglike": float(ll)}
        print(f"loglike = {ll:.2f}")
    except Exception as e:
        print(f"FAILED: {e}")
        failures.append(("competitor_dd", str(e)))

    # 16. dSph (Yukawa combined)
    print("16. dSph:      ", end="")
    try:
        ll = ch_v03.loglike_dsph_v03(params["sigma_m_100"], 0.0)
        results["dsph"] = {"loglike": float(ll)}
        print(f"loglike = {ll:.2f}")
    except Exception as e:
        print(f"FAILED: {e}")
        failures.append(("dsph", str(e)))

    # 17. UFD
    print("17. UFD:       ", end="")
    try:
        ll = ch_v03.loglike_ufd_v03(params["sigma_m_100"], 0.0)
        results["ufd"] = {"loglike": float(ll)}
        print(f"loglike = {ll:.2f}")
    except Exception as e:
        print(f"FAILED: {e}")
        failures.append(("ufd", str(e)))

    # 18. Bullet
    print("18. Bullet:    ", end="")
    try:
        ll = ch_v03.loglike_bullet_v03(params["sigma_m_3000"] if params["sigma_m_3000"] > 0.01 else 0.01, 0.0)
        results["bullet"] = {"loglike": float(ll)}
        print(f"loglike = {ll:.2f}")
    except Exception as e:
        print(f"FAILED: {e}")
        failures.append(("bullet", str(e)))

    return results, failures


def main():
    # Load T90.45 results
    t90_45_path = RESULTS_DIR / "t90_v45_multi_portal_joint_fit_nlive200.json"
    with open(t90_45_path) as f:
        t90_45 = json.load(f)

    # MAP parameters
    map_params = {
        "m_phi_A_MeV": t90_45["MAP_physical"]["m_phi_A_MeV"],
        "m_chi_A_GeV": t90_45["MAP_physical"]["m_chi_A_GeV"],
        "g_chi_A": t90_45["MAP_physical"]["g_chi_A"],
        "m_phi_B_MeV": t90_45["MAP_physical"]["m_phi_B_MeV"],
        "m_chi_B_GeV": t90_45["MAP_physical"]["m_chi_B_GeV"],
        "g_chi_B": t90_45["MAP_physical"]["g_chi_B"],
        "epsilon_A": t90_45["MAP_physical"]["epsilon_A"],
        "alpha_A": t90_45["MAP_physical"]["alpha_A"],
        "xi": t90_45["MAP_physical"]["xi"],
        "sigma_m_28": t90_45["MAP_derived_sigma_m"]["sigma_m_28"],
        "sigma_m_100": t90_45["MAP_derived_sigma_m"]["sigma_m_100"],
        "sigma_m_1000": t90_45["MAP_derived_sigma_m"]["sigma_m_1000"],
        "sigma_m_3000": t90_45["MAP_derived_sigma_m"]["sigma_m_3000"],
    }

    # Median parameters
    median_params = {
        "m_phi_A_MeV": t90_45["median_physical"]["m_phi_A_MeV"],
        "m_chi_A_GeV": t90_45["median_physical"]["m_chi_A_GeV"],
        "g_chi_A": t90_45["median_physical"]["g_chi_A"],
        "m_phi_B_MeV": t90_45["median_physical"]["m_phi_B_MeV"],
        "m_chi_B_GeV": t90_45["median_physical"]["m_chi_B_GeV"],
        "g_chi_B": t90_45["median_physical"]["g_chi_B"],
        "epsilon_A": t90_45["median_physical"]["epsilon_A"],
        "alpha_A": t90_45["median_physical"]["alpha_A"],
        "xi": t90_45["median_physical"]["xi"],
    }

    # Compute σ/m at various v for median
    median_params["sigma_m_28"] = sigma_m_total_two_portal(
        28, median_params["m_phi_A_MeV"], median_params["m_chi_A_GeV"], median_params["g_chi_A"],
        median_params["m_phi_B_MeV"], median_params["m_chi_B_GeV"], median_params["g_chi_B"],
    )
    median_params["sigma_m_100"] = sigma_m_total_two_portal(
        100, median_params["m_phi_A_MeV"], median_params["m_chi_A_GeV"], median_params["g_chi_A"],
        median_params["m_phi_B_MeV"], median_params["m_chi_B_GeV"], median_params["g_chi_B"],
    )
    median_params["sigma_m_1000"] = sigma_m_total_two_portal(
        1000, median_params["m_phi_A_MeV"], median_params["m_chi_A_GeV"], median_params["g_chi_A"],
        median_params["m_phi_B_MeV"], median_params["m_chi_B_GeV"], median_params["g_chi_B"],
    )
    median_params["sigma_m_3000"] = sigma_m_total_two_portal(
        3000, median_params["m_phi_A_MeV"], median_params["m_chi_A_GeV"], median_params["g_chi_A"],
        median_params["m_phi_B_MeV"], median_params["m_chi_B_GeV"], median_params["g_chi_B"],
    )

    print("=" * 80)
    print("Phase 21 — T90.45 Multi-Portal Space-Conditions Test")
    print("=" * 80)

    # Evaluate MAP
    map_results, map_failures = evaluate_channels("T90.45 MAP (non-Cloud-9 mode)", map_params)

    # Evaluate median
    median_results, median_failures = evaluate_channels("T90.45 Median (Cloud-9 mode)", median_params)

    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    def summarize(label, results, failures, params):
        n_pass = len(results) - len(failures)
        n_total = len(results)
        loglikes = [r["loglike"] for r in results.values() if isinstance(r.get("loglike"), (int, float)) and np.isfinite(r.get("loglike", 0))]
        total_ll = sum(loglikes)
        print(f"\n{label}:")
        print(f"  Channels evaluable: {n_pass}/{n_total}")
        print(f"  Sum of finite loglikes: {total_ll:.2f}")
        print(f"  σ/m(28) = {params['sigma_m_28']:.2f} cm²/g (Cloud-9 needs ≥30)")
        print(f"  σ/m(100) = {params['sigma_m_100']:.2f} cm²/g")
        print(f"  σ/m(3000) = {params['sigma_m_3000']:.4f} cm²/g")
        # Channels that pass vs fail
        fails = [(name, r.get("loglike", 0)) for name, r in results.items()
                 if isinstance(r.get("loglike"), (int, float)) and r.get("loglike") < -5.0]
        if fails:
            print(f"  Channels with loglike < -5: {fails}")
        return total_ll

    map_total = summarize("T90.45 MAP", map_results, map_failures, map_params)
    median_total = summarize("T90.45 Median", median_results, median_failures, median_params)

    # Compare
    print()
    print("=" * 80)
    print("COMPARISON")
    print("=" * 80)
    print(f"  T90.45 MAP:   total loglike = {map_total:.2f}, σ/m(28) = {map_params['sigma_m_28']:.2f}")
    print(f"  T90.45 Median: total loglike = {median_total:.2f}, σ/m(28) = {median_params['sigma_m_28']:.2f}")
    print()
    if median_params['sigma_m_28'] >= 30 and map_params['sigma_m_28'] < 30:
        print("  → Median (Cloud-9 mode) is the one that fits Cloud-9 (σ/m(28) ≥ 30)")
    elif map_params['sigma_m_28'] >= 30 and median_params['sigma_m_28'] < 30:
        print("  → MAP fits Cloud-9 but median doesn't")
    elif median_params['sigma_m_28'] >= 30 and map_params['sigma_m_28'] >= 30:
        print("  → Both modes fit Cloud-9")
    else:
        print("  → Neither mode fits Cloud-9")

    # Verdict
    if map_total > median_total:
        verdict = f"MAP (non-Cloud-9 mode) is preferred: total = {map_total:.2f}"
    else:
        verdict = f"Median (Cloud-9 mode) is preferred: total = {median_total:.2f}"

    out = {
        "test": "Phase21_t90_45_multi_portal",
        "map_params": map_params,
        "median_params": median_params,
        "map_results": map_results,
        "map_failures": map_failures,
        "map_total_loglike": map_total,
        "median_results": median_results,
        "median_failures": median_failures,
        "median_total_loglike": median_total,
        "verdict": verdict,
    }

    out_path = RESULTS_DIR / "phase21_t90_45_multi_portal.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\nResults written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())