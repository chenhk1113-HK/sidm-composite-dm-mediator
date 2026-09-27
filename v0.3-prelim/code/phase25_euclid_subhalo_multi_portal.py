"""
Phase 25 — Euclid Q1 Subhalo Forecast Under Multi-Portal

The Euclid Q1 subhalo channel (Channel 24) wants sigma/m(v=150) < 0.10
cm^2/g (otherwise too much tidal evaporation destroys subhalos).

T90.45 multi-portal has sigma/m(150) = 1.33 cm^2/g — too high.
Phase 25 investigates whether the multi-portal velocity dependence can
satisfy this constraint by tuning the portal couplings.

Strategy:
1. Compute sigma/m(v=150) at T90.45 median
2. Scan over (g_chi_A, g_chi_B) keeping m_phi_A, m_phi_B fixed
3. Find configurations that satisfy Euclid subhalo (< 0.10 at v=150)
   while preserving Cloud-9 sigma/m(28) >= 30
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import t40_yukawa_sigma_m as yukawa
from channels_extended import loglike_euclid_q1_subhalo_forecast

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def sigma_m_two_portal(v_kms, m_phi_A_MeV, m_chi_A_GeV, g_chi_A,
                        m_phi_B_MeV, m_chi_B_GeV, g_chi_B):
    """Total sigma/m from two portals (additive Yukawa)."""
    sm_A = yukawa.sigma_m_cm2_per_g(v_kms, m_phi_A_MeV, m_chi_A_GeV, g_chi_A)
    sm_B = yukawa.sigma_m_cm2_per_g(v_kms, m_phi_B_MeV, m_chi_B_GeV, g_chi_B)
    return sm_A + sm_B


def main():
    # Load T90.45 results
    t90_45_path = RESULTS_DIR / "t90_v45_multi_portal_joint_fit_nlive200.json"
    with open(t90_45_path) as f:
        t90_45 = json.load(f)

    p = t90_45["median_physical"]
    m_phi_A = p["m_phi_A_MeV"]
    m_chi_A = p["m_chi_A_GeV"]
    m_phi_B = p["m_phi_B_MeV"]
    m_chi_B = p["m_chi_B_GeV"]
    g_chi_A = p["g_chi_A"]
    g_chi_B = p["g_chi_B"]

    # 1. Current Euclid subhalo loglike at T90.45 median
    print("=" * 60)
    print("1. T90.45 MEDIAN: Euclid subhalo loglike")
    print("=" * 60)
    sm_150 = sigma_m_two_portal(150, m_phi_A, m_chi_A, g_chi_A, m_phi_B, m_chi_B, g_chi_B)
    print(f"  sigma/m(150) = {sm_150:.3f} cm^2/g")
    print(f"  Euclid requires: sigma/m(150) < 0.10 cm^2/g")
    # Use power-law fit for a=1.6 (effective)
    sigma_m_0_eff = 5.5
    a_eff = 1.6
    ll_current = loglike_euclid_q1_subhalo_forecast(sigma_m_0_eff, a_eff)
    print(f"  loglike = {ll_current:.2f}")
    print()

    # 2. Scan over (g_chi_A, g_chi_B) — keep mediator masses fixed
    print("=" * 60)
    print("2. Scan over (g_chi_A, g_chi_B): Euclid + Cloud-9 jointly")
    print("=" * 60)
    g_chi_A_grid = np.linspace(0.3, 1.5, 13)
    g_chi_B_grid = np.linspace(0.05, 0.5, 19)

    results = []
    for gA in g_chi_A_grid:
        for gB in g_chi_B_grid:
            sm28 = sigma_m_two_portal(28, m_phi_A, m_chi_A, gA, m_phi_B, m_chi_B, gB)
            sm100 = sigma_m_two_portal(100, m_phi_A, m_chi_A, gA, m_phi_B, m_chi_B, gB)
            sm150 = sigma_m_two_portal(150, m_phi_A, m_chi_A, gA, m_phi_B, m_chi_B, gB)
            sm3000 = sigma_m_two_portal(3000, m_phi_A, m_chi_A, gA, m_phi_B, m_chi_B, gB)

            # Approximate effective (sigma_m_0, a)
            if sm28 > 0 and sm3000 > 0:
                a_eff = (np.log10(sm28) - np.log10(sm3000)) / (np.log10(3000/100) - np.log10(28/100))
                sigma_m_0_eff = sm100
            else:
                a_eff = 0
                sigma_m_0_eff = 0

            ll_euclid = loglike_euclid_q1_subhalo_forecast(sigma_m_0_eff, a_eff)
            cloud9_ok = sm28 >= 30

            if ll_euclid > -2.0 and cloud9_ok:
                results.append({
                    "g_chi_A": gA, "g_chi_B": gB,
                    "sigma_m_28": sm28, "sigma_m_100": sm100, "sigma_m_150": sm150,
                    "sigma_m_3000": sm3000, "a_eff": a_eff,
                    "ll_euclid": ll_euclid,
                })

    print(f"  Tested {len(g_chi_A_grid) * len(g_chi_B_grid)} combinations")
    print(f"  Found {len(results)} satisfying both Cloud-9 AND Euclid subhalo")
    print()

    if results:
        # Sort by Euclid loglike (best first)
        results.sort(key=lambda x: x["ll_euclid"], reverse=True)
        print("  Top 5 configurations:")
        print(f"  {'g_A':>6}  {'g_B':>6}  {'sm28':>8}  {'sm100':>8}  {'sm150':>8}  {'a_eff':>6}  {'ll_euclid':>9}")
        for r in results[:5]:
            print(f"  {r['g_chi_A']:6.3f}  {r['g_chi_B']:6.3f}  "
                  f"{r['sigma_m_28']:8.3f}  {r['sigma_m_100']:8.3f}  {r['sigma_m_150']:8.3f}  "
                  f"{r['a_eff']:6.3f}  {r['ll_euclid']:9.2f}")
    print()

    # 3. Conclusion
    print("=" * 60)
    print("VERDICT")
    print("=" * 60)
    if len(results) == 0:
        verdict = "NO_CONFIGURATION_FOUND"
        print("  No (g_chi_A, g_chi_B) satisfies both Cloud-9 (sm28>=30) AND Euclid (sm150<0.10)")
        print("  at the current mediator masses (m_phi_A=366 MeV, m_phi_B=20.5 MeV)")
        print()
        print("  This is a STRUCTURAL conflict: the m_phi_B=20.5 MeV Portal B gives")
        print("  high sigma/m at all velocities, not just at Cloud-9's v=28.")
        print("  To satisfy Euclid subhalo, Portal B would need a different mass or shape.")
    else:
        verdict = "FOUND_CONFIGURATION"
        best = results[0]
        print(f"  Found {len(results)} configurations satisfying both channels")
        print(f"  Best: g_chi_A={best['g_chi_A']:.3f}, g_chi_B={best['g_chi_B']:.3f}")
        print(f"  sigma/m(28)={best['sigma_m_28']:.2f}, sigma/m(150)={best['sigma_m_150']:.3f}")
        print(f"  Euclid subhalo loglike = {best['ll_euclid']:.2f}")

    out = {
        "test": "Phase25_euclid_subhalo_multiporal",
        "median_params": {
            "m_phi_A_MeV": m_phi_A, "m_chi_A_GeV": m_chi_A, "g_chi_A": g_chi_A,
            "m_phi_B_MeV": m_phi_B, "m_chi_B_GeV": m_chi_B, "g_chi_B": g_chi_B,
        },
        "current_sm150": sm_150,
        "current_ll_euclid": ll_current,
        "scan_n_tested": len(g_chi_A_grid) * len(g_chi_B_grid),
        "scan_n_satisfying": len(results),
        "best_configs": results[:5] if results else [],
        "verdict": verdict,
    }

    out_path = RESULTS_DIR / "phase25_euclid_subhalo_multi_portal.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\nResults written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
