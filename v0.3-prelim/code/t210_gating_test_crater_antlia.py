"""
T210 Gating Test — Crater II + Antlia II pass/fail under Path F1.

Per the Cloud-9alternate.docx memo (2026-09-25), the strategic question is:
- Does the current model (Path F1 three-term sigma_eff, borrowed prescription)
  pass Crater II and Antlia II at their V_max velocity scale?
- This is the gating test for whether multi-probe reframing is viable.

Critical caveat from the memo: V_max for Crater II/Antlia II may be 10-15 km/s,
which would put them at the SAME velocity scale as dSph (where sigma/m <= 0.8
cm^2/g). In that case, Crater II/Antlia II CONFIRM the tension rather than
relax it.

This script:
1. Computes sigma_eff(v) at v = 5, 10, 15, 28 km/s (candidate V_max scales)
2. Under the borrowed prescription (f_H_cf = 0.85, f_H_cc = 0.5)
3. Compares each sigma_eff to:
   - Crater II: sigma/m ~ 60 cm^2/g (favored)
   - Antlia II: sigma/m ~ similar (favored, similar to Crater II)
   - dSph ceiling: sigma/m <= 0.8 cm^2/g
   - Cloud-9 floor: sigma/m >= 50 cm^2/g
4. Reports pass/fail per (V_max candidate) per (system)

Velocity literature references:
- Crater II: sigma_los = 2.3 km/s. SIDM interpretation in [Vargas et al. or
  Read+ 2018 for UDGs; specific Crater II SIDM analysis likely Yang+ or
  Sameie+ 2020-era].
- Antlia II: sigma_los = 5.7 km/s. Similar SIDM interpretation.
- For a UDG with r_1/2 ~ 1-3 kpc, V_max estimates are typically 10-30 km/s
  depending on the assumed mass profile.
- Crater II inferred M_halo: ~ 5e8 M_sun (some estimates higher).
- Antlia II inferred M_halo: ~ 8e8 M_sun (some estimates higher).

Three candidate V_max scenarios:
A. V_max = sigma_los (conservative, velocity dispersion IS the relevant scale)
   - Crater II: v = 2.3 km/s
   - Antlia II: v = 5.7 km/s
B. V_max = sqrt(3) * sigma_los (isotropic Jeans)
   - Crater II: v = 4.0 km/s
   - Antlia II: v = 9.9 km/s
C. V_max = 10-30 km/s (full halo circular velocity at r_max)
   - For both: v ~ 15-25 km/s (cluster of estimates)
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np

from T207_three_term_fit import (
    sigma_eff_three_term, BOUNDS,
)

# =============================================================================
# Borrowed prescription parameters (Path F1 best fit, from T207)
# =============================================================================
# These are the "borrowed" mode params from the v18.38 standing result.
# f_H_cf = 0.85 (heavy-favored in core-forming regime)
# f_H_cc = 0.5 (moderate heavy fraction in core-collapsed regime)
# The other 7 params are the borrowed emcee median:
# sigma_0 = 0.005, sigma_peak_HH_1 = 84.4, sigma_0_HL = 0.0001,
# sigma_peak_HL = 0.318, v_HL = 98.2, sigma_0_LL = 0.0006, a_slope = 1.0
BORROWED_PARAMS = {
    "sigma_0": 0.005,
    "sigma_peak_HH_1": 84.4,
    "sigma_0_HL": 0.0001,
    "sigma_peak_HL": 0.318,
    "v_HL": 98.2,
    "sigma_0_LL": 0.0006,
    "a_slope": 1.0,
}
F_H_CF_BORROWED = 0.85
F_H_CC_BORROWED = 0.5

# =============================================================================
# Crater II and Antlia II observational constraints
# =============================================================================
CRATER_II = {
    "name": "Crater II",
    "sigma_los": 2.3,           # km/s, stellar line-of-sight velocity dispersion
    "r_half": 1066,             # pc, half-light radius
    "distance": 117.5,          # kpc
    "M_v": -8.2,                # absolute magnitude
    "inferred_sigma_m": 60.0,   # cm^2/g, SIDM-favored
    "halo_class": "core_collapsed",  # Per T207 framework, satellite dwarfs use f_H_cc
}

ANTLIA_II = {
    "name": "Antlia II",
    "sigma_los": 5.7,           # km/s
    "r_half": 2301,             # pc
    "distance": 132,            # kpc
    "M_v": -9.03,
    "inferred_sigma_m": 60.0,   # cm^2/g, similar to Crater II (favored)
    "halo_class": "core_collapsed",
}

# =============================================================================
# Three candidate V_max scenarios from the memo
# =============================================================================
SCENARIOS = [
    ("A: V_max = sigma_los", {
        "Crater II": 2.3,
        "Antlia II": 5.7,
    }),
    ("B: V_max = sqrt(3) * sigma_los (Jeans isotropic)", {
        "Crater II": 2.3 * np.sqrt(3),
        "Antlia II": 5.7 * np.sqrt(3),
    }),
    ("C: V_max ~ 15 km/s (full halo circular velocity)", {
        "Crater II": 15.0,
        "Antlia II": 15.0,
    }),
    ("D: V_max ~ 28 km/s (Cloud-9 host-halo scale)", {
        "Crater II": 28.0,
        "Antlia II": 28.0,
    }),
]

# Reference observations / ceilings / floors
CEILINGS = {
    "dSph v=15": 0.8,
    "UFD v=10": 0.155,
    "Cluster v=500": 0.00025,
}
FLOORS = {
    "Cloud-9 v=28": 50.0,
    "Crater II": 30.0,       # memo: ~ 60 cm^2/g favored; lower bound = 30 (half of favored)
    "Antlia II": 30.0,       # similar
}


def evaluate_sigma_eff(v: float) -> float:
    """Compute sigma_eff at velocity v under borrowed prescription.

    Note on width_HL (per Reviewer 2 2review.docx section 2.3): the
    hardcoded value 50.0 km/s is INCONSISTENT with the Path A2 scan script
    (which uses width_HL as a free parameter in [0.5, 5] km/s). For the
    gating test specifically, we use the wider width (50.0 km/s) because
    it represents the BROAD feature of the borrowed-prescription sigma_HL
    (peak at v_HL = 100 km/s, slow rolloff over the v = 28-100 km/s range)
    rather than the narrow resonance being scanned in Path A2. If the
    Path A2 narrow resonance (width = 0.5-5 km/s) is more physically
    motivated, the result is even worse for Crater/Antlia (the resonance
    misses their velocity scale entirely).
    """
    return sigma_eff_three_term(
        v,
        f_H=F_H_CC_BORROWED,  # UDG-like, use f_H_cc
        sigma_0=BORROWED_PARAMS["sigma_0"],
        a_slope=BORROWED_PARAMS["a_slope"],
        sigma_peak_HH_1=BORROWED_PARAMS["sigma_peak_HH_1"],
        sigma_0_HL=BORROWED_PARAMS["sigma_0_HL"],
        sigma_peak_HL=BORROWED_PARAMS["sigma_peak_HL"],
        v_HL=BORROWED_PARAMS["v_HL"],
        width_HL=50.0,  # see note above; broader than Path A2 scan
        sigma_0_LL=BORROWED_PARAMS["sigma_0_LL"],
    )


def verdict(sigma_eff_val: float, target_value: float, target_type: str, sigma_unc: float = 5.0) -> dict:
    """Check pass/fail against floor/ceiling/gaussian.

    Note on sigma_unc (per Reviewer 2 2review.docx section 2.3): the default
    of 5.0 cm^2/g is an exploratory convention for cross-system consistency
    tests. For Crater II / Antlia II we override to 10.0 (call sites below)
    to reflect the larger kinematic-inference uncertainty for these systems
    (sigma/m ~ 60 cm^2/g at V_max ~ 26 km/s from Zhang+ 2024; the +/-10
    reflects the kinematic-inference systematic uncertainty in the published
    sigma/m value, NOT observational scatter). For systems with published
    sigma_unc values (e.g., SPARC, dSph), we use the published values.
    """
    if target_type == "floor":
        # Need sigma_eff >= target_value
        if sigma_eff_val >= target_value:
            return {"verdict": "PASS", "z": (target_value - sigma_eff_val) / sigma_unc}
        else:
            return {"verdict": "FAIL", "z": (target_value - sigma_eff_val) / sigma_unc}
    elif target_type == "ceiling":
        # Need sigma_eff <= target_value
        if sigma_eff_val <= target_value:
            return {"verdict": "PASS", "z": (sigma_eff_val - target_value) / sigma_unc}
        else:
            return {"verdict": "FAIL", "z": (sigma_eff_val - target_value) / sigma_unc}
    elif target_type == "gaussian":
        z = (sigma_eff_val - target_value) / sigma_unc
        if abs(z) <= 1.0:
            return {"verdict": "PASS", "z": z}
        elif abs(z) <= 2.0:
            return {"verdict": "MARGINAL", "z": z}
        else:
            return {"verdict": "FAIL", "z": z}


def main():
    results = {
        "borrowed_params": BORROWED_PARAMS,
        "f_H_cf_borrowed": F_H_CF_BORROWED,
        "f_H_cc_borrowed": F_H_CC_BORROWED,
        "scenarios": {},
        "reference_observations": {
            "Crater II": {
                "sigma_los_km_s": CRATER_II["sigma_los"],
                "inferred_sigma_m_cm2_g": CRATER_II["inferred_sigma_m"],
                "r_half_pc": CRATER_II["r_half"],
            },
            "Antlia II": {
                "sigma_los_km_s": ANTLIA_II["sigma_los"],
                "inferred_sigma_m_cm2_g": ANTLIA_II["inferred_sigma_m"],
                "r_half_pc": ANTLIA_II["r_half"],
            },
        },
    }

    print("=" * 78)
    print("T210 Gating Test: Crater II + Antlia II under Path F1 borrowed prescription")
    print("=" * 78)

    for scenario_name, v_dict in SCENARIOS:
        print(f"\n--- Scenario {scenario_name} ---")
        scenario_result = {}
        for system_name, v in v_dict.items():
            sigma_eff_val = evaluate_sigma_eff(v)
            print(f"\n{system_name} at V_max = {v:.1f} km/s:")
            print(f"  sigma_eff = {sigma_eff_val:.4f} cm^2/g")
            if system_name == "Crater II":
                target = CRATER_II["inferred_sigma_m"] / 2  # floor = 30 cm^2/g (favored 60, lower bound)
                v_cr = verdict(sigma_eff_val, target, "floor", sigma_unc=10.0)
                print(f"  Crater II requirement: sigma/m >= {target:.0f} cm^2/g (floor, sigma_unc=10)")
                print(f"  z = {v_cr['z']:.2f}, verdict = {v_cr['verdict']}")
            elif system_name == "Antlia II":
                target = ANTLIA_II["inferred_sigma_m"] / 2
                v_an = verdict(sigma_eff_val, target, "floor", sigma_unc=10.0)
                print(f"  Antlia II requirement: sigma/m >= {target:.0f} cm^2/g (floor, sigma_unc=10)")
                print(f"  z = {v_an['z']:.2f}, verdict = {v_an['verdict']}")
            scenario_result[system_name] = {
                "v_max_km_s": v,
                "sigma_eff_cm2_g": sigma_eff_val,
                "target_cm2_g": target,
                "verdict": v_cr["verdict"] if system_name == "Crater II" else v_an["verdict"],
                "z": v_cr["z"] if system_name == "Crater II" else v_an["z"],
            }
        results["scenarios"][scenario_name] = scenario_result

    # Also evaluate sigma_eff at dSph v=15 to confirm baseline
    print("\n" + "=" * 78)
    print("Reference: sigma_eff at dSph v=15 (already in T207 channels)")
    print("=" * 78)
    sigma_eff_dsph = evaluate_sigma_eff(15.0)
    v_dsph = verdict(sigma_eff_dsph, 0.8, "ceiling", sigma_unc=0.04)
    print(f"dSph v=15: sigma_eff = {sigma_eff_dsph:.4f} cm^2/g, ceiling = 0.8 cm^2/g")
    print(f"  z = {v_dsph['z']:.2f}, verdict = {v_dsph['verdict']}")

    sigma_eff_cloud9 = evaluate_sigma_eff(28.0)
    v_c9 = verdict(sigma_eff_cloud9, 128.0, "floor", sigma_unc=30.0)
    print(f"\nCloud-9 v=28: sigma_eff = {sigma_eff_cloud9:.4f} cm^2/g, floor = 128 cm^2/g (obs = 128)")
    print(f"  z = {v_c9['z']:.2f}, verdict = {v_c9['verdict']}")

    # Summary verdict
    print("\n" + "=" * 78)
    print("Summary: under borrowed prescription (f_H_cf=0.85, f_H_cc=0.5):")
    print("=" * 78)
    for scenario_name, scenario_result in results["scenarios"].items():
        print(f"\n{scenario_name}:")
        for system_name, r in scenario_result.items():
            print(f"  {system_name}: sigma_eff = {r['sigma_eff_cm2_g']:.3f} cm^2/g, "
                  f"verdict = {r['verdict']} (z={r['z']:.2f})")

    # Write JSON
    out_path = Path(__file__).resolve().parent.parent / "data" / "results" / "t210_gating_test_crater_antlia.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_path}")
    return results


if __name__ == "__main__":
    main()