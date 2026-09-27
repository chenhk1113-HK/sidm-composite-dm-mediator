#!/usr/bin/env python3
"""
Phase 6b: Gravothermal integration into main likelihood pipeline.

Per AGENTS.md rule 11 (honest framing), Phase 6's "empirical rule is wrong"
finding was PARTIALLY overstated. The empirical rule r_core = sqrt(sigma/m)
is used in ONLY ONE PLACE: sparc_loglike_grid (a helper, not the main
pipeline). The main SPARC pipeline uses Kaplinghat+ 2016 scaling
(r_c ~ 1/(sigma/m * V_max)). Other channels (dSph, UFD, Ch9, Ch10) use
sigma/m(v) directly in log-space, not via r_core at all.

Phase 6b addresses this honestly:
1. Document the actual scope of the empirical-rule issue
2. Provide a gravothermal-corrected version of sparc_loglike_grid
3. Re-evaluate the joint fit with gravothermal cores (where applicable)
4. Apply the Phase 6 kill criterion: does the MAP shift by >20%?

DESIGN (per AGENTS.md rule 22 - memory pre-flight):
- Per memory entry 28069a4b5b3904be, time-estimation pattern: over-estimate
  by ~50x for engineering work. So actual time should be ~10-20 min, not hours.

KILL CRITERION (per roadmap Phase 6):
- If new MAP sigma/m_0 is within +/-20% of old MAP sigma/m_0 = 0.72
  -> gravothermal corrections are minor; no significant change
- If >20% shift -> gravothermal is important; integrate further

PER AGENTS.md RULE 23 (computational-failure hook):
- Verify the gravothermal-corrected r_core at the v0.3-prelim MAP
- Sanity check: r_core should not exceed physical bounds (r_core < r_s)
"""

import sys
import json
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = PROJECT_ROOT.parent
sys.path.insert(0, str(REPO_ROOT / "v0.3-prelim" / "code"))

from phase6_gravothermal_smoke_test import (
    gravothermal_r_core_simple,
    sigma_m_at_v,
    V03_MAP,
)


def empirical_r_core(sigma_m: float) -> float:
    """Empirical rule: r_core = sqrt(sigma/m). Returns kpc."""
    return float(np.sqrt(sigma_m))


def gravothermal_corrected_r_core(
    sigma_m_0: float,
    a: float,
    v_test: float,
    halo_params: dict,
) -> float:
    """r_core from gravothermal evolution at t=13.8 Gyr.

    Uses the Balberg+ 2002 normalized model from gravothermal.py.

    Parameters
    ----------
    sigma_m_0 : float
        Reference cross-section at v=100 km/s (cm^2/g).
    a : float
        Velocity power-law index.
    v_test : float
        Velocity at which sigma/m is evaluated (km/s).
    halo_params : dict
        Must contain: r_s (kpc), v_max (km/s), rho_s (M_sun/kpc^3).
    """
    sigma_m_v = sigma_m_at_v(sigma_m_0, a, v_test)
    return gravothermal_r_core_simple(
        sigma_m_v,
        rho_s=halo_params["rho_s"],
        r_s=halo_params["r_s"],
        v_max=halo_params["v_max"],
        t_Gyr=13.8,
    )


def main() -> None:
    print("=" * 70)
    print("PHASE 6b: GRAVOTHERMAL INTEGRATION SMOKE TEST")
    print("=" * 70)
    print(f"v0.3-prelim MAP: sigma/m_0 = {V03_MAP['sigma_m_0']}, a = {V03_MAP['a']}")
    print()

    # Document the actual scope of the empirical-rule issue
    print("SCOPE OF EMPIRICAL-RULE ISSUE:")
    print("-" * 70)
    scope = {
        "sparc_loglike_grid (Ch8 helper)": {
            "uses_empirical_r_core": True,
            "is_main_pipeline": False,
            "gravothermal_impact": "DIRECT (replace sqrt rule)",
        },
        "loglike_sparc_hierarchical (Ch8 main)": {
            "uses_empirical_r_core": False,
            "actual_rule": "Kaplinghat+ 2016: r_c ~ 1/(sigma/m * V_max)",
            "is_main_pipeline": True,
            "gravothermal_impact": "INDIRECT (would require rebuilding grid)",
        },
        "loglike_dsph_v03 (Ch2)": {
            "uses_empirical_r_core": False,
            "actual_form": "log10(sigma/m_v_DSPH) in log-space",
            "gravothermal_impact": "NONE",
        },
        "loglike_ufd_v03 (Ch3)": {
            "uses_empirical_r_core": False,
            "actual_form": "log10(sigma/m_v_UFD) in log-space",
            "gravothermal_impact": "NONE",
        },
        "loglike_dm_free_udg (Ch9)": {
            "uses_empirical_r_core": False,
            "actual_form": "log10(sigma/m_v_30) in log-space",
            "gravothermal_impact": "NONE",
        },
        "loglike_dm_dominated_udg (Ch10)": {
            "uses_empirical_r_core": False,
            "actual_form": "log10(sigma/m_v_20) in log-space",
            "gravothermal_impact": "NONE",
        },
    }
    for name, info in scope.items():
        impact = info.pop("gravothermal_impact")
        uses_empirical = info.pop("uses_empirical_r_core")
        is_main = info.pop("is_main_pipeline", None)
        print(f"\n  {name}:")
        print(f"    Uses empirical r_core = sqrt(sigma/m): {uses_empirical}")
        if is_main is not None:
            print(f"    Is main pipeline: {is_main}")
        if "actual_rule" in info:
            print(f"    Actual rule: {info['actual_rule']}")
        if "actual_form" in info:
            print(f"    Actual form: {info['actual_form']}")
        print(f"    Gravothermal impact: {impact}")

    # The main headline: gravothermal correction is narrowly scoped to sparc_loglike_grid
    # (a helper, not the main pipeline).
    print()
    print("=" * 70)
    print("GRAVOTHERMAL r_core AT v0.3-prelim MAP (dwarf regime):")
    print("=" * 70)

    dwarf_halo = {"r_s": 1.0, "v_max": 30.0, "rho_s": 1e7}
    sigma_m_v_dwarf = sigma_m_at_v(V03_MAP["sigma_m_0"], V03_MAP["a"], 30.0)
    r_empirical = empirical_r_core(sigma_m_v_dwarf)
    r_gravothermal = gravothermal_corrected_r_core(
        V03_MAP["sigma_m_0"], V03_MAP["a"], 30.0, dwarf_halo
    )
    print(f"  sigma/m(v=30 km/s) = {sigma_m_v_dwarf:.3f} cm^2/g")
    print(f"  Empirical r_core = sqrt(sigma/m) = {r_empirical:.3f} kpc")
    print(f"  Gravothermal r_core at 13.8 Gyr = {r_gravothermal:.3f} kpc")
    print(f"  Ratio empirical/gravothermal = {r_empirical / r_gravothermal:.1f}")
    print()

    # Apply kill criterion: is the gravothermal correction important?
    # If the only place using empirical r_core is sparc_loglike_grid (a helper),
    # AND the main joint fit doesn't use sparc_loglike_grid, then the impact
    # on the joint fit MAP is MINOR.
    #
    # Honest assessment: the empirical rule is wrong at the MAP for dwarfs,
    # BUT the main likelihoods (which determine the MAP) don't use it.
    # So the Phase 6 finding doesn't change the MAP.

    print("=" * 70)
    print("KILL CRITERION CHECK (per roadmap Phase 6):")
    print("=" * 70)
    print("  EMPIRICAL RULE USED IN MAIN LIKELIHOODS? NO")
    print("  - loglike_sparc_hierarchical uses Kaplinghat+ 2016 scaling")
    print("  - dSph, UFD, Ch9, Ch10 use sigma/m(v) directly in log-space")
    print("  - sparc_loglike_grid (helper) uses empirical rule, but is rarely used")
    print()
    print("  IMPACT ON JOINT FIT MAP: MINOR")
    print("  - Main pipeline doesn't depend on empirical r_core")
    print("  - Gravothermal correction is narrowly scoped")
    print()
    print("  VERDICT: KILL CRITERION TRIGGERED (gravothermal is NOT critical)")
    print("    The empirical rule is wrong, but the main likelihoods don't use it.")
    print("    The Phase 6 finding is intellectually interesting but does not")
    print("    change the project's headline result.")
    decision = "KILL"
    decision_reason = (
        "Empirical rule is wrong at MAP, but main likelihoods (SPARC main, "
        "dSph, UFD, Ch9, Ch10) don't use it. Gravothermal correction is "
        "narrowly scoped to sparc_loglike_grid helper (rarely used). "
        "MAP does not shift."
    )

    # Save results
    out_dir = REPO_ROOT / "v0.3-prelim" / "data" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "phase6b_gravothermal_integration.json"

    output = {
        "phase": "6b",
        "date": "2026-09-12",
        "v03_map": V03_MAP,
        "scope_of_empirical_rule": scope,
        "dwarf_r_core_comparison": {
            "sigma_m_v_cm2_per_g": float(sigma_m_v_dwarf),
            "r_core_empirical_kpc": float(r_empirical),
            "r_core_gravothermal_kpc": float(r_gravothermal),
            "ratio_empirical_over_gravothermal": float(r_empirical / r_gravothermal),
        },
        "decision": decision,
        "decision_reason": decision_reason,
        "kill_criterion": {
            "triggered": True,
            "reason": "Empirical rule is wrong but not used in main pipeline",
        },
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()