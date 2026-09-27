"""
Phase 17 — Probe: Do core-collapsed halos prefer different g_D?

The SIDM literature distinguishes between two regimes:
  - "Uncollapsed" halos: σ/m ~ 1 cm²/g, gravothermal fluid is stable
  - "Core-collapsed" halos: σ/m ~ 0.1 cm²/g, gravothermal instability triggered

For the Majorana reframe, σ_inel is a separate cross-section from σ_elastic
in the SIDM fluid. Question: if the gravothermal collapse is governed by
σ_elastic, while the direct-detection channel is σ_inel, can the model
naturally produce different σ/m regimes at the same g_D?

The current pipeline uses σ/m at v=100 as a single "effective" quantity.
Phase 17 explores whether gravothermal core-collapse in the
Majorana reframe prefers g_D > 0.16 (the value allowed by Fermi).
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config
import t8_v03_joint_fit as t8
import channels_v03 as ch_v03
from t40_yukawa_sigma_m import sigma_m_cm2_per_g
from t32_real_likelihood import loglike_fermi_real
from phase8d_majorana_alpha_consistent import sigma_v_majorana_cm3_per_s

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Time parameter (gravothermal evolution)
# τ_core = characteristic time to core collapse for σ/m at v=100
# Depends on halo concentration; for typical MW-like, τ ~ 10 Gyr at σ/m ~ 0.1


def tau_core_collapse_gyr(sigma_m_at_v100: float) -> float:
    """
    Core-collapse time as a function of σ/m at v=100 km/s.

    Balberg+ 2002 / Koda+ 2011: τ_core ~ 10 Gyr for σ/m ~ 0.1 cm²/g
    Power-law scaling: τ ∝ (σ/m)^-1 (more scattering = faster collapse)
    """
    return 10.0 * (0.1 / sigma_m_at_v100)


def main():
    print("=" * 80)
    print("Phase 17 — Probe: Core-collapse time vs g_D in Majorana reframe")
    print("=" * 80)
    print(f"M_CHI_GEV = 45 GeV, m_A' = 200 MeV, scan g_D = 0.05 to 1.0")
    print()

    out = {"test": "Phase17_core_collapse_gD",
           "direction": "Find g_D that gives τ_core ~ 10 Gyr (matches observed collapsed halos)"}

    m_chi = 45.0
    m_phi = 200.0
    g_D_values = [0.05, 0.10, 0.15, 0.16, 0.20, 0.30, 0.50, 0.70, 1.00]

    print(f"{'g_D':<8} {'σ/m(v=100)':<14} {'τ_core [Gyr]':<14} {'Fermi LL':<14} {'verdict'}")
    for g_D in g_D_values:
        sm = sigma_m_cm2_per_g(100, m_phi, m_chi, g_D)
        tau = tau_core_collapse_gyr(sm)

        # Compute loglike_fermi at this g_D (constrained)
        sigma_v = sigma_v_majorana_cm3_per_s(g_D)
        ll_fermi = loglike_fermi_real(m_chi, sigma_v, channel="bb", use_J_prior=True)

        # Verdict: σ/m=0.1 is the "core-collapsed" benchmark
        # g_D that gives τ ~ 10 Gyr is the natural one
        if 0.5 < tau < 20:
            verdict = "MATCH (10 Gyr)"
        elif tau < 5:
            verdict = "TOO FAST (collapses early)"
        elif tau > 30:
            verdict = "TOO SLOW (no collapse)"
        else:
            verdict = "EDGE"

        print(f"{g_D:<8.3f} {sm:<14.4f} {tau:<14.2f} {ll_fermi:<14.2f} {verdict}")
        out[f"gD_{g_D:.2f}"] = {
            "sigma_m_at_v100": float(sm),
            "tau_core_Gyr": float(tau),
            "loglike_fermi": float(ll_fermi),
            "verdict": verdict,
        }

    # Find natural g_D
    print()
    print("=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    # The natural g_D is the one where τ_core ~ 10 Gyr
    target_g_D = 0.16  # current Fermi-constrained value
    sm_at_target = sigma_m_cm2_per_g(100, m_phi, m_chi, target_g_D)
    tau_at_target = tau_core_collapse_gyr(sm_at_target)
    print(f"At g_D = 0.16 (Fermi limit):")
    print(f"  σ/m(v=100) = {sm_at_target:.3f} cm²/g")
    print(f"  τ_core = {tau_at_target:.1f} Gyr")

    # For τ = 10 Gyr
    sm_target = 0.1
    print(f"\nFor τ = 10 Gyr (core-collapse benchmark):")
    print(f"  σ/m = 0.1 cm²/g")
    # Solve for g_D that gives σ/m = 0.1
    g_low, g_high = 0.01, 5.0
    for _ in range(50):
        g_mid = 0.5 * (g_low + g_high)
        if sigma_m_cm2_per_g(100, m_phi, m_chi, g_mid) > sm_target:
            g_high = g_mid
        else:
            g_low = g_mid
    g_D_for_collapse = 0.5 * (g_low + g_high)
    print(f"  Required g_D = {g_D_for_collapse:.3f}")
    sigma_v_for_collapse = sigma_v_majorana_cm3_per_s(g_D_for_collapse)
    ll_fermi_collapse = loglike_fermi_real(m_chi, sigma_v_for_collapse, channel="bb", use_J_prior=True)
    print(f"  σv at g_D = {g_D_for_collapse:.3f}: {sigma_v_for_collapse:.2e} cm³/s")
    print(f"  Fermi loglike: {ll_fermi_collapse:.2f}")

    if g_D_for_collapse > 0.16:
        print(f"\n→ Core-collapsed halos PREFER g_D > 0.16 (by factor {g_D_for_collapse/0.16:.1f}×)")
        print("  This would EXPLAIN the σ/m drop: core-collapsed halos")
        print("  exist at a different g_D than the bulk SIDM halo population")
    else:
        print(f"\n→ Core-collapse consistent with current g_D ~ 0.16")

    out["natural_gD_for_collapse"] = float(g_D_for_collapse)
    out["sigma_m_at_fermi_gD"] = float(sm_at_target)
    out["tau_at_fermi_gD"] = float(tau_at_target)
    out["verdict"] = ("COLLAPSE_REQUIRES_LARGER_gD" if g_D_for_collapse > 0.16
                      else "FERMI_LIMIT_CONSISTENT")

    out_path = RESULTS_DIR / "phase17_core_collapse_gD.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\nResults written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
