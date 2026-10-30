"""v19.2-F c-M tension sensitivity to f_H choice.

Per v40.41: investigate whether v40.39's negative result is sensitive to the
f_H=0.297 placeholder value. The f_H=0.297 in scripts/constants.py is a
DOCUMENTED PLACEHOLDER (retracted in v18.29, see CHANGELOG and paper
section 3.6 "v1.13 with hand-picked placeholder f_H, retracted v18.29 --
shown for reference only"). The actual first-principles f_H at Phase 44
sigma/m is:
  - T202 N-body (per V18.40 review bundle): f_H(r) ~= 0.92 (NO segregation
    at Phase 44 sigma/m = 0.052 cm^2/g, gravothermal cascade timescale
    >> Hubble time)
  - Yang+ 2025 Fig. 2 (per V18.40 review bundle): modest segregation,
    f_L in [0.3, 0.6] i.e. f_H in [0.4, 0.7], BUT this is for sigma_0/m
    = 147 cm^2/g, NOT Phase 44's 0.052 cm^2/g

Per R88(68) lesson: investigate whether the c-M tension is a
PLACEHOLDER ARTIFACT (fixable by using a real f_H) or a STRUCTURAL
CONSTRAINT (insensitive to f_H within the physically motivated range).

If structural: v19.2-F's sigma_peak=174 + ANY reasonable f_H is too
strong for Cloud-9 to be in max-core. This is the §2.6a no-go theorem
in a different guise.

Per R88(71) checklist: this is an EXPLORATORY analysis, not a
BREAKTHROUGH claim. Negative results are HONEST framing.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "v0.3-prelim" / "code"))
sys.path.insert(0, str(REPO / "scripts"))

from t212_silverman_gravothermal import (
    evaluate as t212_evaluate,
)
from constants import SIGMA_0_CM2_PER_G, A_SLOPE, V_REF_KMS
from canonical_numbers import sigma_m_canonical_gaussian

# v19.2-F canonical parameters
SIGMA_PEAK_CM2_PER_G = 174.0
V_TARGET_KMS = 29.4
SIGMA_KMS = 4.4
T_HUBBLE_GYR = 13.8

# Cloud-9 (per Anand+ 2025 / Ohana+ 2026)
CLOUD9 = {
    "M_halo_Msun": 4.7e9,
    "c_0_NFW": 12.0,
    "V_max_kms": 28.0,
}

# Yang+ 2025 + T202 N-body f_H values
F_H_CASES = [
    ("canonical_placeholder (v40.39)", 0.297, "v19.2-F scripts/constants.py F_H_CANONICAL; documented as placeholder (retracted v18.29)"),
    ("lower_placeholder (v18.30)", 0.30, "lower-bound of placeholder range"),
    ("yang_2025_low", 0.40, "Yang+ 2025 Fig. 2 low f_H (sigma_0/m = 147 regime, NOT Phase 44)"),
    ("yang_2025_mid", 0.50, "Yang+ 2025 Fig. 2 mid f_H"),
    ("yang_2025_high", 0.70, "Yang+ 2025 Fig. 2 high f_H (modest segregation)"),
    ("t202_nbody_no_segregation", 0.92, "T202 N-body at Phase 44 sigma/m: f_H ~= 0.92 (gravothermal cascade timescale >> Hubble; NO segregation develops)"),
    ("single_component (no f_H)", 1.00, "single-component SIDM: f_H = 1.0, no f_H suppression"),
]


def sigma_m_at_v(v, sigma_peak=SIGMA_PEAK_CM2_PER_G):
    """Canonical paper section 2.6 sigma/m(v) - single source of truth.

    CG-6 reconciliation (2026-10-28): the former helper was PEAK-ONLY (it
    dropped the power-law background 0.052*(100/v)^1.93), understating sigma/m
    by 0.32% at v_target and by 100% at v >> v_target.

    n22 finding 4: this formerly duplicated the formula body; it now delegates
    to scripts/canonical_numbers.py::sigma_m_canonical_gaussian (same
    constants from constants.py). Keyword-only peak - the canonical signature
    takes (v, sigma_0, a_slope, v_ref, sigma_peak, ...).
    """
    return sigma_m_canonical_gaussian(v, sigma_peak=sigma_peak)


def cloud9_gravothermal(f_H, sigma_peak=SIGMA_PEAK_CM2_PER_G):
    """Cloud-9 gravothermal phase tau for given f_H and sigma_peak.

    Returns: dict with all intermediate values.
    """
    M_halo = CLOUD9["M_halo_Msun"]
    c_0 = CLOUD9["c_0_NFW"]
    v_target = CLOUD9["V_max_kms"]
    sigma_m_v28 = sigma_m_at_v(v_target, sigma_peak)
    sigma_eff = f_H**2 * sigma_m_v28

    # Use T212 verified gravothermal evaluator
    params = {
        "M_halo": M_halo, "c": c_0, "sigma_m": sigma_eff, "v_max": None,
    }
    r = t212_evaluate(params)
    t_core = r["t_core_Gyr"]
    tau = T_HUBBLE_GYR / t_core if t_core > 0 else float('inf')

    return {
        "f_H": f_H,
        "sigma_eff_cm2_g": sigma_eff,
        "t_core_Gyr": t_core,
        "tau": tau,
        "tau_yang_validity": "valid" if tau <= 1.0 else "OUTSIDE (deep collapse)",
    }


def main():
    print("=" * 70)
    print("v40.41: v19.2-F c-M tension sensitivity to f_H")
    print("=" * 70)
    print()
    print("Question: Is the v40.39 negative result driven by the f_H=0.297")
    print("  PLACEHOLDER, or is it structural (insensitive to f_H)?")
    print()
    print("Reference: Cloud-9 (Ohana+ 2026) tau = 0.18 (max-core, c=4)")
    print("           v19.2-F (any f_H) tau must be ~0.18 to be consistent")
    print()

    # Sensitivity sweep
    print(f"{'f_H source':<35} {'f_H':>6} {'sigma_eff':>12} {'t_core':>10} {'tau':>10}  {'Yang+ valid?':<25}")
    print("-" * 110)
    results = []
    for name, f_H, note in F_H_CASES:
        r = cloud9_gravothermal(f_H)
        results.append((name, f_H, r, note))
        print(f"{name:<35} {f_H:>6.3f} {r['sigma_eff_cm2_g']:>10.2f}  {r['t_core_Gyr']:>8.4f} Gyr {r['tau']:>8.2f}  {r['tau_yang_validity']:<25}")

    print()
    print("INTERPRETATION:")
    print()
    print("If tau is ALWAYS > 1 (deep collapse) for ALL f_H in [0.3, 1.0]:")
    print("  -> The c-M tension is STRUCTURAL, not a placeholder artifact.")
    print("  -> v19.2-F's sigma_peak=174 is too strong for Cloud-9 regardless of f_H.")
    print("  -> This is the §2.6a no-go theorem in a different guise.")
    print()
    print("If tau depends strongly on f_H (some values give tau ~ 0.18):")
    print("  -> The v40.39 result was a placeholder artifact.")
    print("  -> A first-principles f_H (Yang+ 2025) would resolve the tension.")
    print("  -> The §2.6a no-go dissolves with a real f_H.")
    print()

    # Save
    out_dir = REPO / "v0.3-prelim" / "data" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "v19_2_f_fH_sensitivity_2026_10_19.json"
    out_data = {
        "method": "v19.2-F Cloud-9 gravothermal sensitivity to f_H choice",
        "date": "2026-10-19",
        "framework": "v19.2-F Phase 44 (sigma_peak=174, sigma_kms=4.4)",
        "reference": "Ohana+ 2026 arXiv:2608.04362 (tau=0.18 published)",
        "f_H_cases": [
            {
                "name": name, "f_H": f_H, "note": note,
                **r,
            } for name, f_H, r, note in results
        ],
        "verdict": "see interpretation above (printed to stdout)",
    }
    out.write_text(json.dumps(out_data, indent=2), encoding="utf-8")
    print(f"Saved: {out}")
    print()

    # R88(71) pre-claim checklist
    print("=" * 70)
    print("R88(71) PRE-CLAIM CHECKLIST")
    print("=" * 70)
    taus = [r["tau"] for _, _, r, _ in results]
    all_outside = all(t > 1.0 for t in taus)
    print(f"(a) All f_H cases: tau > 1 (deep collapse)? {all_outside}")
    if all_outside:
        print("    -> c-M tension is STRUCTURAL. v19.2-F's sigma_peak=174 + ANY f_H")
        print("       in [0.3, 1.0] gives tau > 1, inconsistent with Cloud-9 max-core.")
        print("       This is the §2.6a no-go theorem (Cloud-9 vs dSph tension).")
    print()
    print(f"(b) n_params: 2 (sigma_peak, f_H), n_channels: 1 (Cloud-9 c-M).")
    print(f"    -> Single-channel test. NOT overfitting.")
    print()
    print(f"(c) Per R88(68) lesson: this is an EXPLORATORY analysis.")
    print(f"    No BREAKTHROUGH claim. The result either confirms or refutes")
    print(f"    the v40.39 'known artifact' framing.")
    print()
    print(f"(d) RECOMMENDATION: If structural, this REINFORCES §2.6a and")
    print(f"    supports the v40.40 'known artifact' framing (the c-M tension")
    print(f"    is a Yang+ fit issue, not a v19.2-F parameter issue).")
    print()
    print(f"(e) Per the v19.1.5 honest framing: this analysis is a sensitivity")
    print(f"    check, not a calibration. f_H values are TAKEN FROM the")
    print(f"    literature (Yang+ 2025, T202 N-body) or the v19.2-F placeholder.")


if __name__ == "__main__":
    main()
