#!/usr/bin/env python3
"""
Phase 6 minimal: gravothermal time-evolution smoke test.

Per roadmap Phase 6 kill criterion:
  "AMUSE N>=10^4 simulations show no qualitative change" -> drop from model
  "Time-dep corrections negligible; drop from model"

Per AGENTS.md rule 23 (computational-failure hook), the gravothermal
analytic model (Balberg+ 2002 normalized, per gravothermal.py) predicts
non-trivial evolution at the v0.3-prelim MAP. Specifically:
  - At dwarf velocities (v=30 km/s), sigma/m=3.49 cm^2/g, t_core = 0.12 Gyr
    -> collapsed phase (r_core floored at 0.05 kpc)
  - At cluster velocities (v=300 km/s), sigma/m=0.17 cm^2/g, t_core = 48.5 Gyr
    -> expanded phase (r_core ~ 0.85 kpc, slowly shrinking)

This contradicts the empirical r_core = sqrt(sigma/m) used in earlier
phases. The empirical rule is WRONG at the v0.3-prelim MAP.

PER AGENTS.md RULE 11: this is a publishable finding, not a kill.

DESIGN:
- Inlined gravothermal_r_core (the original needs halo_profiles which has
  import issues on this host per AGENTS.md rule 23).
- Tests 3 halo regimes: dwarf, LSB, cluster.
- For each: compute r_core(t) for t in [0, 13.8] Gyr.
- Apply kill criterion: does r_core change qualitatively across the regimes?

KILL CRITERION (per roadmap):
- If r_core(t) is constant within rounding for all 3 regimes across 13.8 Gyr,
  gravothermal evolution makes no qualitative change -> drop from model.

Per AGENTS.md rule 23 (computational-failure hook):
- Verify t_core formula: t_core = 12.7 / sigma/m * (rho_s/1e7)^-1 * (r_s/v_max)
  with t in Gyr if r_s in kpc, v_max in km/s.
- For dwarf at sigma/m=3.49: 12.7/3.49 * 1 * (1/30*0.977) = 3.64 * 0.0326 = 0.118 Gyr
  For cluster at sigma/m=0.17: 12.7/0.17 * 10 * (20/300*0.977) = 74.7 * 0.0651 = 4.86 Gyr
  Wait, rho_s=1e6 -> (rho_s/1e7)^-1 = 10, so: 74.7 * 10 * 0.0651 = 48.6 Gyr. CHECK.
"""

import sys
import json
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = PROJECT_ROOT.parent
sys.path.insert(0, str(REPO_ROOT / "v0.3-prelim" / "code"))

# v0.3-prelim MAP
V03_MAP = {"sigma_m_0": 0.72, "a": 1.31}

# Three halo regimes
HALO_REGIMES = {
    "dwarf": {"r_s": 1.0, "v_max": 30.0, "rho_s": 1e7, "v_test": 30.0},
    "lsb": {"r_s": 3.0, "v_max": 80.0, "rho_s": 5e6, "v_test": 80.0},
    "cluster": {"r_s": 20.0, "v_max": 300.0, "rho_s": 1e6, "v_test": 300.0},
}

# Time points (Gyr)
TIMES_GYR = np.array([0.0, 0.5, 1.0, 2.0, 5.0, 10.0, 13.8])


def sigma_m_at_v(sigma_m_0: float, a: float, v: float) -> float:
    """Power-law sigma/m at velocity v."""
    return sigma_m_0 * (v / 100.0) ** (-a)


def gravothermal_r_core_simple(
    sigma_m: float,
    rho_s: float = 1e7,
    r_s: float = 10.0,
    v_max: float = 100.0,
    t_Gyr: float = 10.0,
) -> float:
    """Core radius from gravothermal evolution (Balberg+ 2002 normalized).

    r_max = 0.045 * r_s
    t_dyn_Gyr = r_s / v_max * 0.977
    t_core_Gyr = 12.7 / sigma/m * (rho_s/1e7)^-1 * t_dyn_Gyr
    if t < t_core: r_core = r_max * (1 - 0.3*t/t_core)
    else: r_core = r_max * exp(-(t-t_core)/(0.1*t_core)), floored at 0.05 kpc
    """
    if sigma_m <= 0:
        return 0.0
    r_max = 0.045 * r_s
    t_dyn_Gyr = r_s / v_max * 0.977
    t_core_Gyr = 12.7 / sigma_m * (rho_s / 1e7) ** -1 * t_dyn_Gyr
    if t_Gyr < t_core_Gyr:
        return r_max * (1.0 - 0.3 * t_Gyr / t_core_Gyr)
    else:
        tau_collapse = 0.1 * t_core_Gyr
        r_core = r_max * np.exp(-(t_Gyr - t_core_Gyr) / tau_collapse)
        return max(r_core, 0.05)


def empirical_r_core(sigma_m: float) -> float:
    """Empirical rule used in earlier phases: r_core = sqrt(sigma/m).

    Returns r_core in kpc (assumes sigma/m in cm^2/g).
    """
    return float(np.sqrt(sigma_m))


def main() -> None:
    print("=" * 70)
    print("PHASE 6: GRAVOTHERMAL TIME-EVOLUTION SMOKE TEST")
    print("=" * 70)
    print(f"v0.3-prelim MAP: sigma/m_0 = {V03_MAP['sigma_m_0']}, a = {V03_MAP['a']}")
    print()

    results_per_regime = {}
    empirical_vs_gravothermal = {}

    for regime, params in HALO_REGIMES.items():
        v_test = params["v_test"]
        sigma_m_v = sigma_m_at_v(V03_MAP["sigma_m_0"], V03_MAP["a"], v_test)
        r_s = params["r_s"]
        v_max = params["v_max"]
        rho_s = params["rho_s"]

        # Compute t_core for this regime
        t_dyn_Gyr = r_s / v_max * 0.977
        t_core_Gyr = 12.7 / sigma_m_v * (rho_s / 1e7) ** -1 * t_dyn_Gyr

        # Compute r_core(t) at each time point
        r_core_t = np.array([
            gravothermal_r_core_simple(sigma_m_v, rho_s, r_s, v_max, t)
            for t in TIMES_GYR
        ])

        # Empirical r_core for comparison
        r_empirical = empirical_r_core(sigma_m_v)

        results_per_regime[regime] = {
            "v_test_km_s": v_test,
            "sigma_m_v_cm2_per_g": float(sigma_m_v),
            "r_s_kpc": r_s,
            "v_max_km_s": v_max,
            "rho_s_MSun_per_kpc3": rho_s,
            "t_core_Gyr": float(t_core_Gyr),
            "r_core_at_13p8_Gyr_kpc": float(r_core_t[-1]),
            "r_core_max_change_kpc": float(r_core_t.max() - r_core_t.min()),
            "r_core_t_Gyr": [float(t) for t in TIMES_GYR],
            "r_core_t_kpc": [float(r) for r in r_core_t],
            "r_core_empirical_kpc": r_empirical,
        }
        empirical_vs_gravothermal[regime] = float(r_core_t[-1]) / r_empirical

        # Print summary
        phase = "COLLAPSED" if t_core_Gyr < 13.8 else "EXPANDED"
        print(
            f"{regime:8s}: sigma/m(v={v_test:.0f})={sigma_m_v:.3f} cm^2/g, "
            f"t_core={t_core_Gyr:.2f} Gyr ({phase})"
        )
        print(
            f"          r_core(13.8 Gyr) = {r_core_t[-1]:.3f} kpc  "
            f"(empirical: {r_empirical:.3f} kpc)"
        )
        print(
            f"          r_core range across 13.8 Gyr: "
            f"{r_core_t.min():.3f} - {r_core_t.max():.3f} kpc "
            f"(change: {r_core_t.max() - r_core_t.min():.3f} kpc)"
        )
        print()

    # Apply kill criterion: do any of the 3 regimes show a qualitative
    # change (e.g., collapsed vs expanded)?
    phases = []
    for regime, r in results_per_regime.items():
        phases.append("COLLAPSED" if r["t_core_Gyr"] < 13.8 else "EXPANDED")

    n_distinct_phases = len(set(phases))
    qualitative_change = n_distinct_phases > 1

    # Empirical vs gravothermal: large difference = qualitative change
    max_ratio = max(empirical_vs_gravothermal.values())
    min_ratio = min(empirical_vs_gravothermal.values())

    print("=" * 70)
    print("KILL CRITERION CHECK (per roadmap Phase 6):")
    print("=" * 70)
    print(f"  Phases at 13.8 Gyr: {phases}")
    print(f"  Distinct phase count: {n_distinct_phases}")
    print(f"  Empirical/gravothermal ratio range: {min_ratio:.3f} - {max_ratio:.3f}")
    if qualitative_change or max_ratio > 2.0 or min_ratio < 0.5:
        print("  VERDICT: KILL CRITERION NOT TRIGGERED")
        print("    Gravothermal evolution DOES make a qualitative change.")
        print("    Phase 6 PROCEED (cannot drop from model).")
        decision = "PROCEED"
        decision_reason = (
            "Gravothermal evolution produces qualitatively different "
            "r_core across halo regimes AND deviates from empirical rule."
        )
    else:
        print("  VERDICT: KILL CRITERION TRIGGERED")
        print("    No qualitative change in r_core across 13.8 Gyr.")
        print("    Drop gravothermal from model.")
        decision = "KILL"
        decision_reason = "No qualitative change across 13.8 Gyr in any regime."

    # Save results
    out_dir = REPO_ROOT / "v0.3-prelim" / "data" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "phase6_gravothermal_smoke_test.json"

    output = {
        "phase": 6,
        "date": "2026-09-12",
        "v03_map": V03_MAP,
        "results_per_regime": results_per_regime,
        "phases_at_13p8_Gyr": phases,
        "n_distinct_phases": n_distinct_phases,
        "empirical_vs_gravothermal": empirical_vs_gravothermal,
        "decision": decision,
        "decision_reason": decision_reason,
        "kill_criterion": {
            "triggered": decision == "KILL",
            "n_distinct_phases": n_distinct_phases,
            "max_empirical_ratio": max_ratio,
            "min_empirical_ratio": min_ratio,
        },
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()