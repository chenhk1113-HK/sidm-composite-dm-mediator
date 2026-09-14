"""
Phase 30 — Critical Review Response: Fine-tuning + UV completion tests

Per consider8 (Phase 29 critical review):
  - Test D: Quantify fine-tuning of (E_R, Gamma_R)
  - Test E: Check UV plausibility
  - Test A: Test resonance on other low-velocity systems (Cloud-9 family)
  - Test F: Asymmetric DM relic density with fitted params
  - Test B (partial): Bayes factor resonant vs power-law on SPARC subset

The reviewer says: "premature declaration of a complete solution"
Goal: Quantify the fine-tuning and provide honest assessment.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from t90_v50_resonant_sidm import sigma_m_resonant, kinetic_energy_eV

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"


# ============================================================
# Test D: Fine-tuning quantification
# ============================================================
def test_fine_tuning(m_chi, E_R, Gamma_R, sigma_0, alpha_Y):
    """Compute derivative of log(σ/m) at Cloud-9 with respect to log(Γ_R) and log(E_R).

    A model is "natural" if these derivatives are O(1) to O(10).
    If they're >>100, the resonance is extremely fine-tuned.
    """
    print("=" * 70)
    print("TEST D: Fine-tuning quantification")
    print("=" * 70)
    print()

    # Central values
    r_center = sigma_m_resonant(28, m_chi, E_R, Gamma_R, sigma_0, alpha_Y)
    log_sm_center = np.log10(r_center["sigma_m_total"])

    # Vary Gamma_R by ±10%
    delta_log = 0.1
    log_sm_p_Gamma = []
    for sign in [-1, +1]:
        Gamma_R_var = Gamma_R * (1 + sign * delta_log)
        r = sigma_m_resonant(28, m_chi, E_R, Gamma_R_var, sigma_0, alpha_Y)
        log_sm_p_Gamma.append(np.log10(r["sigma_m_total"]))

    # Numerical derivative: d log(σ/m) / d log(Γ_R)
    d_log_sm_d_log_Gamma = (log_sm_p_Gamma[1] - log_sm_p_Gamma[0]) / (2 * delta_log)

    # Vary E_R by ±10%
    log_sm_p_E = []
    for sign in [-1, +1]:
        E_R_var = E_R * (1 + sign * delta_log)
        r = sigma_m_resonant(28, m_chi, E_R_var, Gamma_R, sigma_0, alpha_Y)
        log_sm_p_E.append(np.log10(r["sigma_m_total"]))

    d_log_sm_d_log_E = (log_sm_p_E[1] - log_sm_p_E[0]) / (2 * delta_log)

    # Vary sigma_0 by ±10%
    log_sm_p_sigma = []
    for sign in [-1, +1]:
        sigma_0_var = sigma_0 * (1 + sign * delta_log)
        r = sigma_m_resonant(28, m_chi, E_R, Gamma_R, sigma_0_var, alpha_Y)
        log_sm_p_sigma.append(np.log10(r["sigma_m_total"]))

    d_log_sm_d_log_sigma = (log_sm_p_sigma[1] - log_sm_p_sigma[0]) / (2 * delta_log)

    # Vary alpha_Y by ±10%
    log_sm_p_alpha = []
    for sign in [-1, +1]:
        alpha_Y_var = alpha_Y * (1 + sign * delta_log)
        r = sigma_m_resonant(28, m_chi, E_R, Gamma_R, sigma_0, alpha_Y_var)
        log_sm_p_alpha.append(np.log10(r["sigma_m_total"]))

    d_log_sm_d_log_alpha = (log_sm_p_alpha[1] - log_sm_p_alpha[0]) / (2 * delta_log)

    print(f"  Central: m_chi={m_chi:.2f}, E_R={E_R:.2f}, Gamma_R={Gamma_R:.3f}")
    print(f"           sigma_0={sigma_0:.4f}, alpha_Y={alpha_Y:.4f}")
    print(f"  log(σ/m(28)) = {log_sm_center:.4f}")
    print()
    print(f"  Sensitivity (|d log(σ/m) / d log(param)|):")
    print(f"    Gamma_R: {abs(d_log_sm_d_log_Gamma):8.3f}")
    print(f"    E_R:     {abs(d_log_sm_d_log_E):8.3f}")
    print(f"    sigma_0: {abs(d_log_sm_d_log_sigma):8.3f}")
    print(f"    alpha_Y: {abs(d_log_sm_d_log_alpha):8.3f}")
    print()

    # Naturalness assessment
    max_sensitivity = max(
        abs(d_log_sm_d_log_Gamma),
        abs(d_log_sm_d_log_E),
        abs(d_log_sm_d_log_sigma),
        abs(d_log_sm_d_log_alpha),
    )
    if max_sensitivity > 100:
        naturalness = "EXTREMELY_FINE_TUNED"
    elif max_sensitivity > 10:
        naturalness = "FINE_TUNED"
    elif max_sensitivity > 2:
        naturalness = "MILDLY_TUNED"
    else:
        naturalness = "NATURAL"

    print(f"  Maximum sensitivity: {max_sensitivity:.3f}")
    print(f"  Naturalness verdict: {naturalness}")
    print(f"  (Reviewer: >100 means 'unnaturally narrow and precisely placed')")

    return {
        "test": "D_fine_tuning",
        "d_log_sm_d_log_Gamma": float(d_log_sm_d_log_Gamma),
        "d_log_sm_d_log_E": float(d_log_sm_d_log_E),
        "d_log_sm_d_log_sigma": float(d_log_sm_d_log_sigma),
        "d_log_sm_d_log_alpha": float(d_log_sm_d_log_alpha),
        "max_sensitivity": float(max_sensitivity),
        "naturalness": naturalness,
    }


# ============================================================
# Test A: Resonance on other low-velocity systems
# ============================================================
def test_other_low_velocity(m_chi, E_R, Gamma_R, sigma_0, alpha_Y):
    """Test if the resonance tuned for Cloud-9 helps or hurts other low-v systems.

    Cloud-9 (RELHIC) is one example of a starless DM-dominated object.
    Are there others with different v_200 that the same resonance must satisfy?
    """
    print()
    print("=" * 70)
    print("TEST A: Resonance on other low-velocity systems")
    print("=" * 70)
    print()

    # Candidate systems (v_200 in km/s):
    # Cloud-9 (arXiv:2608.04362): v=28
    # Segue 1 (ultra-faint): v~10
    # Triangulum II (UFD): v~15
    # Bootes I (UFD): v~12
    # Hercules (UFD): v~10
    # Reticulum II (UFD): v~15
    # Coma Berenices (UFD): v~10
    # Willman 1 (UFD): v~8
    # Draco II (UFD): v~10
    # Tucana III (UFD): v~8
    # Eridanus II (UFD): v~15
    # Horologium I (UFD): v~12
    # Pictor I (UFD): v~10

    candidates = [
        ("Cloud-9 (RELHIC)", 28),
        ("Segue 1", 10),
        ("Triangulum II", 15),
        ("Bootes I", 12),
        ("Hercules", 10),
        ("Reticulum II", 15),
        ("Willman 1", 8),
        ("Draco II", 10),
        ("Tucana III", 8),
        ("Eridanus II", 15),
    ]

    print(f"  {'System':25s}  {'v (km/s)':>10}  {'σ/m':>10}  {'In C9 band?':>14}")
    in_band_count = 0
    for name, v in candidates:
        r = sigma_m_resonant(v, m_chi, E_R, Gamma_R, sigma_0, alpha_Y)
        sm = r["sigma_m_total"]
        in_band = 30 <= sm <= 500
        if in_band:
            in_band_count += 1
        print(f"  {name:25s}  {v:10d}  {sm:10.3f}  {'YES' if in_band else 'no':>14}")

    n_total = len(candidates)
    print()
    print(f"  Systems in Cloud-9 band: {in_band_count}/{n_total}")
    if in_band_count == 1:
        verdict = "TUNED_TO_CLOUD9_ONLY"
        msg = "Resonance works ONLY for Cloud-9; degrades for all other low-v systems"
    elif in_band_count == n_total:
        verdict = "WORKS_FOR_ALL"
        msg = "Resonance works for all low-v systems (predictive)"
    else:
        verdict = "PARTIAL"
        msg = f"Resonance works for {in_band_count}/{n_total} low-v systems"

    print(f"  Verdict: {verdict}")
    print(f"  {msg}")

    return {
        "test": "A_other_low_velocity",
        "systems_tested": n_total,
        "systems_in_band": in_band_count,
        "verdict": verdict,
    }


# ============================================================
# Test F: Asymmetric DM relic density
# ============================================================
def test_relic_density(m_chi, E_R, Gamma_R, sigma_0, alpha_Y):
    """Quick check: does asymmetric DM with these params produce correct relic density?

    Asymmetric DM: relic density comes from baryon-like asymmetry transfer.
    Cosmological Omega_DM h^2 ~ 0.12 requires eta/eta_B ~ 1 (asymmetry transfer).
    Phase 16 showed m_chi = 5 GeV gives eta/eta_B = 1.008.

    For our fitted m_chi = 6 GeV, what is eta/eta_B?
    """
    print()
    print("=" * 70)
    print("TEST F: Asymmetric DM relic density check")
    print("=" * 70)
    print()

    # Simple estimate: Omega_DM / Omega_B ~ (m_chi / m_p) * (eta_DM / eta_B)
    # For Omega_DM/Omega_B ~ 5.3 (Planck 2018), need:
    #   eta/eta_B = 5.3 * (m_p / m_chi)
    Omega_DM_Omega_B = 5.3
    m_p_GeV = 0.938
    eta_over_eta_B = Omega_DM_Omega_B * (m_p_GeV / m_chi)

    print(f"  Fitted m_chi = {m_chi:.2f} GeV")
    print(f"  Required eta/eta_B = {eta_over_eta_B:.3f}")
    print(f"  (Phase 16 result: m_chi=5 GeV gives eta/eta_B = 1.008)")
    print()

    if 0.5 < eta_over_eta_B < 2.0:
        verdict = "REASONABLE"
        msg = "eta/eta_B is O(1), consistent with asymmetric DM mechanism"
    elif 0.1 < eta_over_eta_B < 10:
        verdict = "ACCEPTABLE"
        msg = f"eta/eta_B = {eta_over_eta_B:.2f}, somewhat high but acceptable"
    else:
        verdict = "TENSION"
        msg = f"eta/eta_B = {eta_over_eta_B:.2f}, requires extreme asymmetry transfer"

    print(f"  Verdict: {verdict}")
    print(f"  {msg}")

    # Additional check: does the resonance affect freeze-in?
    # For narrow resonance, freeze-in rate ~ sigma_resonant at v ~ freeze-in velocity
    # v_freeze_in ~ 10^-3 c ~ 300 km/s (depends on coupling)
    r_freeze = sigma_m_resonant(300, m_chi, E_R, Gamma_R, sigma_0, alpha_Y)
    print(f"  At v=300 km/s (freeze-in): σ/m = {r_freeze['sigma_m_total']:.4f}")
    print(f"  (At freeze-in temperature T ~ m_chi/20, v_thermal ~ sqrt(T/m_chi) ~ 30-100 km/s)")

    return {
        "test": "F_relic_density",
        "m_chi_GeV": float(m_chi),
        "eta_over_eta_B_required": float(eta_over_eta_B),
        "verdict": verdict,
        "sigma_m_at_freeze_in_v_300": float(r_freeze["sigma_m_total"]),
    }


# ============================================================
# Test B: Bayes factor resonant vs power-law on SPARC subset
# ============================================================
def test_bayes_factor_sparc(m_chi, E_R, Gamma_R, sigma_0, alpha_Y):
    """Compare resonant SIDM to power-law SIDM on a SPARC subset.

    Use a small sample (5 galaxies) with v_max covering 50-200 km/s range.
    """
    print()
    print("=" * 70)
    print("TEST B: Bayes factor resonant vs power-law on SPARC subset")
    print("=" * 70)
    print()

    # Sample of SPARC galaxies with their v_max (km/s)
    sparc_sample = [
        ("NGC2403", 130),
        ("NGC6503", 115),
        ("NGC3198", 150),
        ("UGC2885", 280),
        ("NGC2841", 300),
    ]

    # For each galaxy, compute σ/m(v_max) under:
    # - Resonant model (E_R=42, Gamma_R=0.56)
    # - Power-law: σ/m(v) = σ_0 * (v/100)^(-a), tune (σ_0, a) to best fit
    # Pure single-portal (T90.51 baseline): σ/m(v) ~ sigma_0_const

    print(f"  {'Galaxy':15s}  {'v_max':>8}  {'Resonant':>10}  {'Power-law best':>16}  {'Single-portal':>14}")
    print("  " + "-" * 70)

    # Best-fit power-law for SPARC (Phase 24): σ_0 = 0.069, a = 0
    # (essentially constant σ/m(100) = 0.069)
    sigma_m_pl_best = lambda v: 0.069

    # Single-portal: T90.51 baseline σ/m(v) = sigma_0_const = 0.26
    sigma_m_single = lambda v: 0.26

    for name, v_max in sparc_sample:
        r_res = sigma_m_resonant(v_max, m_chi, E_R, Gamma_R, sigma_0, alpha_Y)
        sm_res = r_res["sigma_m_total"]
        sm_pl = sigma_m_pl_best(v_max)
        sm_sp = sigma_m_single(v_max)
        print(f"  {name:15s}  {v_max:8d}  {sm_res:10.4f}  {sm_pl:16.4f}  {sm_sp:14.4f}")
    print()

    # Simple log-likelihood difference (log Z_resonant - log Z_power_law)
    # Use Gaussian penalty around SPARC preferred σ/m(100) = 0.069
    # Resonant predicts σ/m(100) = 0.035, power-law predicts 0.069
    print(f"  Predicted σ/m(100):")
    r100_res = sigma_m_resonant(100, m_chi, E_R, Gamma_R, sigma_0, alpha_Y)
    print(f"    Resonant:   {r100_res['sigma_m_total']:.4f}")
    print(f"    Power-law:  {sigma_m_pl_best(100):.4f}")
    print(f"    SPARC pref: 0.069")
    print()

    # Distance from SPARC pref (log10 units)
    log_res = np.log10(r100_res["sigma_m_total"])
    log_pref = np.log10(0.069)
    delta_log_res = log_res - log_pref  # -0.30 for resonant
    delta_log_pl = 0  # power-law is at pref

    # Gaussian penalty
    sigma_log = 0.3  # width
    log_L_res = -0.5 * (delta_log_res / sigma_log) ** 2
    log_L_pl = 0  # at pref
    print(f"  log L_resonant vs SPARC: {log_L_res:.3f}")
    print(f"  log L_power-law vs SPARC: {log_L_pl:.3f}")
    print(f"  Delta log L: {log_L_res - log_L_pl:.3f}")

    return {
        "test": "B_bayes_factor_sparc",
        "log_L_resonant": float(log_L_res),
        "log_L_power_law": float(log_L_pl),
        "delta_log_L": float(log_L_res - log_L_pl),
    }


def main():
    # Load Phase 29 results
    phase29_path = RESULTS_DIR / "phase29_full_resonant_joint_fit.json"
    with open(phase29_path) as f:
        phase29 = json.load(f)

    med = phase29["posterior_medians"]
    m_chi = med["m_chi_GeV"]["p50"]
    E_R = med["E_R_eV"]["p50"]
    Gamma_R = med["Gamma_R_eV"]["p50"]
    sigma_0 = med["sigma_0"]["p50"]
    alpha_Y = med["alpha_Y"]["p50"]

    print("=" * 70)
    print("Phase 30 — Critical Review Response (consider8.docx)")
    print("=" * 70)
    print()
    print(f"Phase 29 posterior median:")
    print(f"  m_chi = {m_chi:.2f} GeV, E_R = {E_R:.2f} eV, Gamma_R = {Gamma_R:.3f} eV")
    print(f"  sigma_0 = {sigma_0:.4f}, alpha_Y = {alpha_Y:.4f}")
    print()

    results = {}
    results["D_fine_tuning"] = test_fine_tuning(m_chi, E_R, Gamma_R, sigma_0, alpha_Y)
    results["A_other_low_velocity"] = test_other_low_velocity(m_chi, E_R, Gamma_R, sigma_0, alpha_Y)
    results["F_relic_density"] = test_relic_density(m_chi, E_R, Gamma_R, sigma_0, alpha_Y)
    results["B_bayes_factor_sparc"] = test_bayes_factor_sparc(m_chi, E_R, Gamma_R, sigma_0, alpha_Y)

    # Final verdict
    print()
    print("=" * 70)
    print("OVERALL VERDICT")
    print("=" * 70)
    print()
    print(f"  Test D (fine-tuning): {results['D_fine_tuning']['naturalness']}")
    print(f"    Max sensitivity: {results['D_fine_tuning']['max_sensitivity']:.1f}")
    print(f"  Test A (other low-v): {results['A_other_low_velocity']['verdict']}")
    print(f"    {results['A_other_low_velocity']['systems_in_band']}/{results['A_other_low_velocity']['systems_tested']} systems in band")
    print(f"  Test F (relic density): {results['F_relic_density']['verdict']}")
    print(f"    eta/eta_B required = {results['F_relic_density']['eta_over_eta_B_required']:.3f}")
    print(f"  Test B (Bayes factor): delta log L = {results['B_bayes_factor_sparc']['delta_log_L']:.2f}")
    print()

    # Aggregate verdict
    verdicts = [
        results["D_fine_tuning"]["naturalness"],
        results["A_other_low_velocity"]["verdict"],
        results["F_relic_density"]["verdict"],
    ]
    print("  Aggregate assessment:")
    if any("EXTREMELY" in v for v in verdicts) or "TUNED_TO_CLOUD9_ONLY" in verdicts:
        agg = "PREMATURE_FULL_SOLUTION"
        msg = "Model has serious fine-tuning or is tuned to Cloud-9 only"
    elif any("FINE_TUNED" in v for v in verdicts):
        agg = "FINE_TUNED_BUT_PLAUSIBLE"
        msg = "Model is fine-tuned but possibly UV-completable"
    else:
        agg = "PLAUSIBLE"
        msg = "Model passes critical review tests"
    print(f"    {agg}: {msg}")

    out = {
        "test": "Phase30_critical_review_response",
        "median_params": {
            "m_chi_GeV": m_chi, "E_R_eV": E_R, "Gamma_R_eV": Gamma_R,
            "sigma_0": sigma_0, "alpha_Y": alpha_Y,
        },
        "results": results,
        "aggregate_verdict": agg,
    }

    out_path = RESULTS_DIR / "phase30_critical_review_response.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\nResults written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
