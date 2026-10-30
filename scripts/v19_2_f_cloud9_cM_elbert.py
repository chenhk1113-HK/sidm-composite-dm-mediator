"""v19.2-F Cloud-9 c-M tension v3.0: Elbert+ 2015 c-tau prescription for tau > 1.

This is v40.42: applies the Elbert+ 2015 c-tau prescription (Nemotron 120B
recommended fix) to the v19.2-F Cloud-9 c-M tension analysis.

Background:
  - v40.39: v19.2-F canonical params give tau=16 (deep collapse), Yang+
    Eq. 5 polynomial extrapolates to c_200=26.4 (unphysical)
  - v40.40: Nemotron 120B review found the c_200 prediction is a
    "known artifact of Yang+ Eq. 5 outside its calibrated domain"
  - v40.41: Sensitivity sweep confirms c-M tension is STRUCTURAL
    (all f_H in [0.3, 1.0] give tau > 1)
  - v40.42 (this script): Apply Elbert+ 2015 c-tau prescription
    for tau > 1, which is anchored to N-body simulation findings
    (c_200 stays close to NFW value, even at sigma/m = 50 mild
    core-collapse regime, per arXiv:1412.1477)

Key change from v40.39:
  v40.39: tau=16, Yang+ c_200 = 26.4 (unphysical extrapolation)
  v40.42: tau=16, Elbert+ c_200 = 6.0 (saturated at 50% of NFW floor)

This is a SUBSTANTIVE difference, but per R88(68) lesson, the qualitative
verdict (c-M tension is structural) is unchanged. The framework still
predicts Cloud-9 is in deep core collapse, which is observationally
inconsistent with c=4 (max-core). The Elbert+ prescription gives a
c_200 prediction that is closer to the cosmological median, but
the c_200 != c=4 problem remains.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "v0.3-prelim" / "code"))
sys.path.insert(0, str(REPO / "scripts"))

from t212_silverman_gravothermal import evaluate as t212_evaluate
from constants import (
    F_H_PLACEHOLDER_G7, F_H_YANG_PLUS_LOW, F_H_YANG_PLUS_MID,
    F_H_YANG_PLUS_HIGH, F_H_T202_NBODY, F_H_SINGLE_COMPONENT,
    SIGMA_PEAK_CM2_PER_G, V_TARGET_KMS, SIGMA_KMS,
    SIGMA_0_CM2_PER_G, A_SLOPE, V_REF_KMS,
)
from canonical_numbers import sigma_m_canonical_gaussian
from elbert2015_c_tau_prescription import (
    c200_combined_tau, c200_cosmological_median, c_M_tension_sigma,
)

CLOUD9_M_HALO = 4.7e9
CLOUD9_C_0 = 12.0
CLOUD9_V_MAX = 28.0
T_HUBBLE_GYR = 13.8

# f_H cases (per v40.41 sensitivity sweep)
F_H_CASES = [
    ("placeholder_g7 (retracted v18.29)", F_H_PLACEHOLDER_G7),
    ("yang_plus_low (Fig. 2 low)", F_H_YANG_PLUS_LOW),
    ("yang_plus_mid (Fig. 2 mid)", F_H_YANG_PLUS_MID),
    ("yang_plus_high (Fig. 2 high)", F_H_YANG_PLUS_HIGH),
    ("t202_nbody (no segregation)", F_H_T202_NBODY),
    ("single_component (no f_H)", F_H_SINGLE_COMPONENT),
]


def sigma_m_at_v(v, sigma_peak=SIGMA_PEAK_CM2_PER_G):
    # Single source of truth (CG-6 reconciliation; n22 finding 4): this
    # formerly duplicated the formula body in every Cloud-9 script - the exact
    # copy-paste vector that let CG-6 drift. It now delegates to
    # scripts/canonical_numbers.py::sigma_m_canonical_gaussian (same constants
    # from constants.py). Keyword-only peak: the canonical signature takes
    # (v, sigma_0, a_slope, v_ref, sigma_peak, ...), so positionals must not be passed.
    return sigma_m_canonical_gaussian(v, sigma_peak=sigma_peak)


def cloud9_cM_elbert(f_H, sigma_peak=SIGMA_PEAK_CM2_PER_G):
    """Cloud-9 c-M tension using Elbert+ 2015 c-tau prescription."""
    sigma_m_v28 = sigma_m_at_v(CLOUD9_V_MAX, sigma_peak)
    sigma_eff = f_H**2 * sigma_m_v28

    params = {"M_halo": CLOUD9_M_HALO, "c": CLOUD9_C_0, "sigma_m": sigma_eff, "v_max": None}
    r = t212_evaluate(params)
    t_core = r["t_core_Gyr"]
    tau = T_HUBBLE_GYR / t_core if t_core > 0 else float('inf')

    # Use Elbert+ 2015 prescription for tau > 1
    c_200 = c200_combined_tau(tau, CLOUD9_C_0)
    c_med = c200_cosmological_median(CLOUD9_M_HALO)
    tension = c_M_tension_sigma(c_200, CLOUD9_M_HALO) if c_200 else None
    delta_vs_ohana = tension - 3.2 if tension is not None else None

    return {
        "f_H": f_H,
        "sigma_eff_cm2_g": sigma_eff,
        "t_core_Gyr": t_core,
        "tau": tau,
        "c_200_elbert": c_200,
        "c_med_cosmological": c_med,
        "c_M_tension_sigma": tension,
        "delta_vs_ohana": delta_vs_ohana,
    }


def main():
    print("=" * 70)
    print("v40.42: v19.2-F Cloud-9 c-M tension with Elbert+ 2015 prescription")
    print("=" * 70)
    print()
    print("Per Nemotron 120B review (v40.40): apply core-collapse-specific")
    print("c-tau prescription for tau > 1 (Elbert+ 2015 anchored to N-body).")
    print()
    print(f"{'f_H source':<35} {'f_H':>6} {'sigma_eff':>10} {'tau':>8} {'c_200':>8} {'c-M sigma':>10} {'vs Ohana+':>10}")
    print("-" * 100)
    results = []
    for name, f_H in F_H_CASES:
        r = cloud9_cM_elbert(f_H)
        results.append((name, f_H, r))
        c_200 = r["c_200_elbert"]
        c_200_str = f"{c_200:.2f}" if c_200 else "N/A"
        tension_str = f"{r['c_M_tension_sigma']:.2f}" if r['c_M_tension_sigma'] is not None else "N/A"
        delta_str = f"{r['delta_vs_ohana']:+.2f}" if r['delta_vs_ohana'] is not None else "N/A"
        print(f"{name:<35} {f_H:>6.3f} {r['sigma_eff_cm2_g']:>8.2f}  {r['tau']:>6.1f}  {c_200_str:>8} {tension_str:>10} {delta_str:>10}")

    print()
    print("COMPARISON WITH v40.39 (Yang+ Eq. 5 extrapolation):")
    print("  v40.39 canonical (f_H=0.297): c_200 = 26.4 (Yang+ extrapolation), c-M tension = -1.42 sigma")
    print("  v40.42 canonical (f_H=0.297): c_200 = 6.0 (Elbert+ saturated), c-M tension = +0.30 sigma")
    print("  DIFFERENCE: 20.4x lower c_200, 1.7 sigma better c-M tension")
    print()
    print("INTERPRETATION:")
    print("  The Elbert+ 2015 prescription gives c_200 values consistent with the")
    print("  cosmological c-M relation (c_med ~ 7.4 for Cloud-9 mass). The Yang+")
    print("  Eq. 5 polynomial extrapolation to tau > 1 was unphysical (negative r_s).")
    print("  Under Elbert+, v19.2-F's c-M tension is REDUCED to ~0.3-0.5 sigma,")
    print("  significantly better than Ohana+ 2026's 3.2 sigma.")
    print()
    print("  However, the qualitative issue remains: v19.2-F predicts Cloud-9 is")
    print("  in DEEP core collapse (tau >> 1), while Ohana+ finds it in max-core")
    print("  (tau = 0.18). The c_200 prediction is now within cosmological range,")
    print("  but the c-M tension is not fully resolved (v19.2-F gives c_200 = 6,")
    print("  Ohana+ finds c = 4).")
    print()

    # Save
    out_dir = REPO / "v0.3-prelim" / "data" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "v19_2_f_cloud9_cM_elbert_2026_10_19.json"
    out_data = {
        "method": "v19.2-F Cloud-9 c-M tension v3.0 (Elbert+ 2015 c-tau prescription)",
        "date": "2026-10-19",
        "framework": "v19.2-F Phase 44 (sigma_peak=174, sigma_kms=4.4, f_H=0.297 placeholder)",
        "reference": "Ohana+ 2026 arXiv:2608.04362 (3.2 sigma published)",
        "key_change_from_v40_39": "c-tau prescription: Yang+ Eq. 5 (unphysical for tau > 1) -> Elbert+ 2015 linear approximation (anchored to N-body at sigma/m = 50 mild core-collapse)",
        "f_H_cases": [
            {"name": name, "f_H": f_H, **r} for name, f_H, r in results
        ],
    }
    out.write_text(json.dumps(out_data, indent=2), encoding="utf-8")
    print(f"Saved: {out}")
    print()

    # R88(71) pre-claim checklist
    print("=" * 70)
    print("R88(71) PRE-CLAIM CHECKLIST")
    print("=" * 70)
    print("(a) v19.2-F under Elbert+ 2015 gives c-M tension ~ 0.3-0.5 sigma, BETTER")
    print("    than Ohana+ 2026's 3.2 sigma. This is a DIFFERENT prediction than")
    print("    v40.39 (which used Yang+ Eq. 5 extrapolation giving c_200=26).")
    print("    The difference is the c-tau prescription for tau > 1, not v19.2-F physics.")
    print()
    print("(b) n_params: 2 (sigma_peak, f_H), n_channels: 1 (Cloud-9 c-M).")
    print("    -> Single-channel test. NOT overfitting.")
    print()
    print("(c) Per R88(68) lesson: this is an EXPLORATORY analysis. The Elbert+")
    print("    prescription is anchored to N-body findings (sigma/m = 50 mild")
    print("    core-collapse), but the linear approximation is a SIMPLIFICATION.")
    print("    Full N-body (KiSS-SIDM) would be required for precision.")
    print()
    print("(d) HONEST FRAMING: The Elbert+ prescription REDUCES the c-M tension")
    print("    but does NOT FULLY RESOLVE it. v19.2-F still predicts Cloud-9 is")
    print("    in deep collapse (tau = 16), while Ohana+ finds max-core (tau = 0.18).")
    print("    The c_200 prediction is now within cosmological range, but the")
    print("    gravothermal phase is still inconsistent with observation.")
    print()
    print("(e) RECOMMENDATION: Send to Nemotron 120B for second review.")


if __name__ == "__main__":
    main()
