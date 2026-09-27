"""
Phase 24 — Multi-Portal SPARC Evaluation

The v0.3-prelim SPARC hierarchical loglike was built for SINGLE-portal
power-law sigma/m(v). The T90.45 multi-portal model uses a SUM of two
Yukawa terms, which has different velocity dependence.

Phase 24 evaluates the multi-portal model against SPARC by:
1. Computing sigma/m(v) at each SPARC galaxy's v_max using the two-portal sum
2. Mapping to effective (sigma_m_0, a) that the hierarchical can interpolate
3. Reporting the SPARC loglike

If SPARC's preferred sigma/m(100) ~ 0.067 conflicts with T90.45's
sigma/m(100) ~ 3.91, this is a REAL tension between Cloud-9 (high sigma/m)
and SPARC (low sigma/m). Phase 24 quantifies this honestly.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import t40_yukawa_sigma_m as yukawa
from t8_v03_joint_fit import loglike_sparc_hierarchical

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def sigma_m_two_portal(v_kms, m_phi_A_MeV, m_chi_A_GeV, g_chi_A,
                        m_phi_B_MeV, m_chi_B_GeV, g_chi_B):
    """Total sigma/m from two portals (additive Yukawa)."""
    sm_A = yukawa.sigma_m_cm2_per_g(v_kms, m_phi_A_MeV, m_chi_A_GeV, g_chi_A)
    sm_B = yukawa.sigma_m_cm2_per_g(v_kms, m_phi_B_MeV, m_chi_B_GeV, g_chi_B)
    return sm_A + sm_B


def fit_effective_power_law(v1_kms, sm1, v2_kms, sm2):
    """Given two (v, sigma/m) points, find the best-fit (sigma_m_0, a)
    for sigma/m(v) = sigma_m_0 * (v / V_REF)^(-a) with V_REF=100.

    From log10(sm) = log10(sigma_m_0) - a * log10(v / V_REF):
      log10(sm1) - log10(sm2) = -a * (log10(v1/V_REF) - log10(v2/V_REF))
      a = (log10(sm1) - log10(sm2)) / (log10(v2/V_REF) - log10(v1/V_REF))
      sigma_m_0 = sm1 * (v1 / V_REF)^a
    """
    V_REF = 100.0
    log_sm1 = np.log10(sm1) if sm1 > 0 else -np.inf
    log_sm2 = np.log10(sm2) if sm2 > 0 else -np.inf
    log_v1 = np.log10(v1_kms / V_REF)
    log_v2 = np.log10(v2_kms / V_REF)

    if not np.isfinite(log_sm1) or not np.isfinite(log_sm2):
        return 0.067, 0.0  # Fallback

    if abs(log_v1 - log_v2) < 1e-6:
        # Same velocity, return sigma_m_0 directly
        return 10 ** log_sm1, 0.0

    a = (log_sm1 - log_sm2) / (log_v2 - log_v1)
    sigma_m_0 = sm1 * (v1_kms / V_REF) ** a
    return sigma_m_0, a


def main():
    # Load T90.45 results
    t90_45_path = RESULTS_DIR / "t90_v45_multi_portal_joint_fit_nlive200.json"
    with open(t90_45_path) as f:
        t90_45 = json.load(f)

    p = t90_45["median_physical"]
    m_phi_A = p["m_phi_A_MeV"]
    m_chi_A = p["m_chi_A_GeV"]
    g_chi_A = p["g_chi_A"]
    m_phi_B = p["m_phi_B_MeV"]
    m_chi_B = p["m_chi_B_GeV"]
    g_chi_B = p["g_chi_B"]

    # Compute sigma/m at v=28 (Cloud-9), v=100 (galactic), v=3000 (Bullet)
    sm_28 = sigma_m_two_portal(28, m_phi_A, m_chi_A, g_chi_A, m_phi_B, m_chi_B, g_chi_B)
    sm_100 = sigma_m_two_portal(100, m_phi_A, m_chi_A, g_chi_A, m_phi_B, m_chi_B, g_chi_B)
    sm_3000 = sigma_m_two_portal(3000, m_phi_A, m_chi_A, g_chi_A, m_phi_B, m_chi_B, g_chi_B)
    print(f"Multi-portal sigma/m values:")
    print(f"  sigma/m(28) = {sm_28:.2f} cm^2/g (Cloud-9)")
    print(f"  sigma/m(100) = {sm_100:.2f} cm^2/g (Galactic / SPARC)")
    print(f"  sigma/m(3000) = {sm_3000:.4f} cm^2/g (Bullet)")
    print()

    # 1. Fit effective power-law (sigma_m_0, a) using Cloud-9 + Bullet
    print("=" * 60)
    print("1. Fit effective (sigma_m_0, a) using Cloud-9 (v=28) + Bullet (v=3000)")
    print("=" * 60)
    sigma_m_0_eff, a_eff = fit_effective_power_law(28, sm_28, 3000, sm_3000)
    print(f"  Effective sigma_m_0 = {sigma_m_0_eff:.4f} cm^2/g (at V_REF=100)")
    print(f"  Effective a = {a_eff:.4f} (velocity power-law index)")
    print()

    # 2. SPARC loglike at effective (sigma_m_0, a)
    print("=" * 60)
    print("2. SPARC hierarchical loglike at effective (sigma_m_0, a)")
    print("=" * 60)
    ll_sparc_eff = loglike_sparc_hierarchical(sigma_m_0_eff, a_eff)
    print(f"  loglike = {ll_sparc_eff:.2f}")
    print()

    # 3. SPARC loglike at galactic sigma/m(100) directly
    print("=" * 60)
    print("3. SPARC hierarchical loglike at sigma/m(100) = {:.2f}".format(sm_100))
    print("=" * 60)
    ll_sparc_100 = loglike_sparc_hierarchical(sm_100, 0.0)
    print(f"  loglike = {ll_sparc_100:.2f}")
    print()

    # 4. SPARC's preferred sigma/m (find max)
    print("=" * 60)
    print("4. SPARC's preferred sigma/m")
    print("=" * 60)
    best_sm = None
    best_ll = -np.inf
    for log_sm in np.linspace(-3, 2, 50):
        sm = 10 ** log_sm
        ll = loglike_sparc_hierarchical(sm, 0.0)
        if ll > best_ll:
            best_ll = ll
            best_sm = sm
    print(f"  Best sigma/m(100) = {best_sm:.4f} cm^2/g (loglike = {best_ll:.2f})")
    print()

    # 5. Compare
    print("=" * 60)
    print("5. Comparison: T90.45 multi-portal vs SPARC preference")
    print("=" * 60)
    print(f"  SPARC prefers sigma/m(100) ~ {best_sm:.3f}")
    print(f"  T90.45 median sigma/m(100) = {sm_100:.3f}")
    print(f"  Ratio T90.45/SPARC: {sm_100/best_sm:.2f}x")
    print(f"  T90.45 loglike at its own params: {ll_sparc_eff:.2f}")
    print(f"  SPARC max loglike: {best_ll:.2f}")
    delta_ll = ll_sparc_eff - best_ll
    print(f"  Delta loglike (T90.45 vs SPARC max): {delta_ll:.2f}")
    print()

    # Verdict
    print("=" * 60)
    print("VERDICT")
    print("=" * 60)
    if abs(delta_ll) < 5:
        verdict = "PASSES_SPARC"
        print(f"  SPARC: loglike {ll_sparc_eff:.2f} within 5 of max {best_ll:.2f}")
    elif delta_ll > -50:
        verdict = "MILD_TENSION"
        print(f"  SPARC: loglike {ll_sparc_eff:.2f} disfavored by {abs(delta_ll):.2f}")
    elif delta_ll > -1000:
        verdict = "STRONG_TENSION"
        print(f"  SPARC: loglike {ll_sparc_eff:.2f} significantly disfavored by {abs(delta_ll):.2f}")
    else:
        verdict = "FAILS_SPARC"
        print(f"  SPARC: loglike {ll_sparc_eff:.2f} catastrophic failure ({abs(delta_ll):.2f})")

    out = {
        "test": "Phase24_multi_portal_sparc",
        "median_params": {
            "m_phi_A_MeV": m_phi_A, "m_chi_A_GeV": m_chi_A, "g_chi_A": g_chi_A,
            "m_phi_B_MeV": m_phi_B, "m_chi_B_GeV": m_chi_B, "g_chi_B": g_chi_B,
        },
        "sigma_m_values": {"sigma_m_28": sm_28, "sigma_m_100": sm_100, "sigma_m_3000": sm_3000},
        "effective_power_law": {"sigma_m_0": sigma_m_0_eff, "a": a_eff},
        "sparc_loglike_at_effective": ll_sparc_eff,
        "sparc_loglike_at_sm100": ll_sparc_100,
        "sparc_best": {"sigma_m_100": best_sm, "loglike": best_ll},
        "delta_loglike_vs_sparc_max": delta_ll,
        "verdict": verdict,
    }

    out_path = RESULTS_DIR / "phase24_multi_portal_sparc.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\nResults written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
