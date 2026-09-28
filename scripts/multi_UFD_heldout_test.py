#!/usr/bin/env python3
"""
multi_UFD_heldout_test.py — Task B (ReviPath priority 1).

Apply Path 2 and Path 3 fits to 4 additional ultra-faint dwarfs:
  - Ursa Minor (UMi, classical dSph)
  - Bootes I (UFD)
  - Hercules (UFD)
  - Canes Venatici I (CVn I, classical dSph)

Use FROZEN parameters (no refitting). Report pass rate and median
tension factor.

Kinematics from Simon 2019 review (arXiv:1901.05465) + Pace 2020 (DR2
proper motions). V_max approximated as 2*sigma_v (dispersion-supported
NFW limit) or from M_half published.
"""
import json
import numpy as np
from pathlib import Path

REPO = Path(__file__).parent.parent
RESULTS = REPO / "v0.3-prelim" / "data" / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

import sys
sys.path.insert(0, str(Path(__file__).parent))
from build_population_sigma_eff_map import (
    load_phase44_params, yukawa_bg, gaussian_resonance, f_H_at_r,
)
from smoke_test_continuous_E import E_proxy


def _sigma_species_func(v, v_targets, sigma_peaks, w_list, sigma_0, a_slope):
    """Generic sigma(v): Yukawa bg + Gaussian peaks."""
    bg = yukawa_bg(v, sigma_0, a_slope)
    peaks = sum(gaussian_resonance(v, vt, sp, w)
                for vt, sp, w in zip(v_targets, sigma_peaks, w_list))
    return bg + peaks


def _sigma_eff_3species(v, f_H, HL_offset, LL_offset, p44):
    """Two-component DM: sigma_eff = f_H^2 sigma_HH + 2 f_H f_L sigma_HL + f_L^2 sigma_LL.
    HL/LL peaks are at Phase 44 positions + HL/LL offset."""
    v_targets_HH = p44["v_targets"]
    v_targets_HL = [vt + HL_offset for vt in v_targets_HH]
    v_targets_LL = [vt + LL_offset for vt in v_targets_HH]

    sHH = _sigma_species_func(v, v_targets_HH, p44["sigma_peaks"], p44["w_list"],
                              p44["sigma_0"], p44["a_slope"])
    sHL = _sigma_species_func(v, v_targets_HL, p44["sigma_peaks"], p44["w_list"],
                              p44["sigma_0"], p44["a_slope"])
    sLL = _sigma_species_func(v, v_targets_LL, p44["sigma_peaks"], p44["w_list"],
                              p44["sigma_0"], p44["a_slope"])
    f_L = 1 - f_H
    return f_H * f_H * sHH + 2 * f_H * f_L * sHL + f_L * f_L * sLL


# ============================================================================
# UFD dataset (Simon 2019 review + Pace 2020)
# ============================================================================
# Format: (name, V_max, sigma_obs_upper_bound_cm2_per_g, f_b, host_ratio,
#          t_over_t_core, f_H)
# sigma_obs are conservative upper bounds from published SIDM analyses.
UFD_DATASET = [
    # V_max from V_max ~= 2*sigma_v for dispersion-supported systems
    # (Wolf+ 2010; sigma_v from Simon 2019 Table 1)
    # sigma_obs_upper: sigma/m < X cm^2/g from published SIDM constraints
    # f_b from Read+ 2019 stellar-to-halo mass relation
    # host_ratio: 1.0 for isolated UFDs, 1000+ for satellites
    # Segue 1 included for direct comparison with §10.4g.2 (continuous) and §10.4g.3 (species-dep).
    # Values from Martinez+ 2011 (sigma_v ~3.7 km/s), Read+ 2019 (sigma/m < 1), Fritz+ 2018 (orbit).
    # (V_max, sigma_obs, f_b, host_ratio, t_tc, f_H) match build_continuous_E_predictive.py held-out row:
    # V_max=12, f_b=1e-4, host_ratio=1.0, t_tc=0.03, f_H=1.0 (treated as pure-HH, matches the
    # log_sigma_p44=0.478 baseline used in §10.4g.2 → predicted 2.376 → FAIL).
    ("Segue 1 (UFD, isolated, V_max from Martinez 2011)", 12.0, 1.0, 1e-4, 1.0, 0.03, 1.0),
    ("Ursa Minor (classical dSph, satellite)", 22.0, 1.0, 2e-3, 1000.0, 0.20, 0.20),
    ("Bootes I (UFD, isolated)", 14.0, 2.0, 1e-4, 1.0, 0.10, 0.10),
    ("Hercules (UFD, isolated)", 13.0, 2.0, 1e-4, 1.0, 0.10, 0.10),
    ("CVn I (classical dSph, satellite)", 18.0, 1.0, 3e-3, 1000.0, 0.20, 0.20),
]


# ============================================================================
# Frozen parameters from Path 2 and Path 3
# ============================================================================
# Path 2: beta = -3.40 (continuous E-proxy)
# Path 3: HL_offset = -113.47 km/s, LL_offset = +1.32 km/s
# Per-bin offsets from §10.4g.1 best-fit (categorical)
PATH2_BETA = -3.40
PATH3_HL_OFFSET = -113.47
PATH3_LL_OFFSET = 1.32
DELTAS_CATEGORICAL = {
    "RELHIC": 0.0,
    "field_dSph": np.log10(0.35),  # field dSph x 0.35
    "satellite": np.log10(0.30),   # satellite dSph x 0.30
    "cluster": 0.0,
}

# Three-state verdict scheme (per 2Review.docx, revi12.docx):
#   PASS        — pred <= bound AND pred >= PATHOLOGICAL_FLOOR
#   FAIL        — pred > bound (model predicts too much self-interaction)
#   PATHOLOGICAL — pred < PATHOLOGICAL_FLOOR (zero SIDM, excluded by cores)
# Reporting threshold, not a measured lower bound.
PATHOLOGICAL_FLOOR = 0.001  # cm^2/g


def classify_verdict(pred, bound):
    """Three-state verdict (PASS / FAIL / PATHOLOGICAL)."""
    if pred > bound:
        return "FAIL"
    if pred < PATHOLOGICAL_FLOOR:
        return "PATHOLOGICAL"
    return "PASS"


p44 = load_phase44_params()


def sigma_eff_baseline(v, f_H):
    """Phase 44 baseline (sigma_HH only)."""
    sHH = _sigma_species_func(v, p44["v_targets"], p44["sigma_peaks"],
                              p44["w_list"], p44["sigma_0"], p44["a_slope"])
    f_L = 1 - f_H
    return f_H * f_H * sHH + 2 * f_H * f_L * 0.0 + f_L * f_L * 0.0


def compute_path2_prediction(V, f_b, host_ratio, t_tc, f_H):
    """Path 2: continuous E-proxy with frozen beta = -3.40, all deltas = 0."""
    logE = E_proxy(f_b, host_ratio, t_tc)
    s_eff = sigma_eff_baseline(V, f_H)
    if s_eff <= 0:
        s_eff = 1e-10
    log_pred = np.log10(s_eff) + PATH2_BETA * logE
    return 10 ** log_pred


def compute_path3_prediction(V, f_b, host_ratio, t_tc, f_H):
    """Path 3: species-dep sigma with frozen HL/LL offsets, Path 2 E."""
    logE = E_proxy(f_b, host_ratio, t_tc)
    s_eff = _sigma_eff_3species(V, f_H, PATH3_HL_OFFSET, PATH3_LL_OFFSET, p44)
    if s_eff <= 0:
        s_eff = 1e-10
    log_pred = np.log10(s_eff) + PATH2_BETA * logE
    return 10 ** log_pred


def compute_categorical_prediction(V, f_b, host_ratio, t_tc, f_H, is_satellite):
    """Categorical E (§10.4g.1) with frozen per-bin offsets."""
    logE = E_proxy(f_b, host_ratio, t_tc)
    s_eff = sigma_eff_baseline(V, f_H)
    if s_eff <= 0:
        s_eff = 1e-10
    log_pred = np.log10(s_eff) + PATH2_BETA * logE
    # Apply categorical offset
    if is_satellite:
        delta = DELTAS_CATEGORICAL["satellite"]
    else:
        delta = DELTAS_CATEGORICAL["field_dSph"]
    log_pred_final = log_pred + delta
    return 10 ** log_pred_final


# ============================================================================
# Main
# ============================================================================
def main():
    print("=" * 70)
    print("Multi-UFD held-out test (Task B, ReviPath priority 1)")
    print("=" * 70)
    print(f"Frozen params: beta = {PATH2_BETA}, HL = {PATH3_HL_OFFSET} km/s, LL = {PATH3_LL_OFFSET} km/s")
    print()

    results = {"metadata": {
        "description": "Multi-UFD held-out test under frozen Path 2 and Path 3 parameters",
        "frozen_params": {
            "path2_beta": PATH2_BETA,
            "path3_HL_offset_km_s": PATH3_HL_OFFSET,
            "path3_LL_offset_km_s": PATH3_LL_OFFSET,
        },
        "tested_systems": [u[0] for u in UFD_DATASET],
        "source_for_kinematics": "Simon 2019 review (arXiv:1901.05465) + Pace 2020 (DR2)",
        "frozen_no_refit": True,
    }}

    print(f"{'System':<35} {'V_max':>6} {'f_H':>5} {'Path2_pred':>10} {'Path3_pred':>10} "
          f"{'Cat_pred':>10} {'bound':>7}")
    print("-" * 95)

    path2_pass = 0
    path3_pass = 0
    cat_pass = 0
    path2_pathological = 0
    path3_pathological = 0
    cat_pathological = 0

    for name, V, sigma_obs, f_b, host_ratio, t_tc, f_H in UFD_DATASET:
        is_satellite = host_ratio > 10.0

        p2 = compute_path2_prediction(V, f_b, host_ratio, t_tc, f_H)
        p3 = compute_path3_prediction(V, f_b, host_ratio, t_tc, f_H)
        cat = compute_categorical_prediction(V, f_b, host_ratio, t_tc, f_H, is_satellite)

        # Three-state verdicts
        v2 = classify_verdict(p2, sigma_obs)
        v3 = classify_verdict(p3, sigma_obs)
        vc = classify_verdict(cat, sigma_obs)

        # Strict pass counter (pred <= bound, includes pathological)
        if v2 == "PASS" or v2 == "PATHOLOGICAL":
            path2_pass += 1
        if v3 == "PASS" or v3 == "PATHOLOGICAL":
            path3_pass += 1
        if vc == "PASS" or vc == "PATHOLOGICAL":
            cat_pass += 1

        if v2 == "PATHOLOGICAL":
            path2_pathological += 1
        if v3 == "PATHOLOGICAL":
            path3_pathological += 1
        if vc == "PATHOLOGICAL":
            cat_pathological += 1

        print(f"{name:<35} {V:>6.1f} {f_H:>5.2f} {p2:>10.3g} {p3:>10.3g} "
              f"{cat:>10.3g} {sigma_obs:>7.2f} {v2:>11} {v3:>11} {vc:>11}")

        results[name] = {
            "V_max": V, "f_H": f_H, "f_b": f_b, "host_ratio": host_ratio,
            "t_tc": t_tc, "sigma_obs_upper_bound": sigma_obs,
            "path2_pred": float(p2), "path2_pass": bool(v2 != "FAIL"),
            "path2_pathological": bool(v2 == "PATHOLOGICAL"),
            "path2_verdict": v2,
            "path3_pred": float(p3), "path3_pass": bool(v3 != "FAIL"),
            "path3_pathological": bool(v3 == "PATHOLOGICAL"),
            "path3_verdict": v3,
            "cat_pred": float(cat), "cat_pass": bool(vc != "FAIL"),
            "cat_pathological": bool(vc == "PATHOLOGICAL"),
            "cat_verdict": vc,
        }

    print()
    # Strict (includes pathological)
    print(f"Path 2 strict pass (incl. pathological): {path2_pass}/{len(UFD_DATASET)}")
    print(f"Path 3 strict pass (incl. pathological): {path3_pass}/{len(UFD_DATASET)}")
    print(f"Categorical strict pass (incl. pathological): {cat_pass}/{len(UFD_DATASET)}")
    print()
    # Meaningful (excludes pathological)
    p2_meaningful = path2_pass - path2_pathological
    p3_meaningful = path3_pass - path3_pathological
    cat_meaningful = cat_pass - cat_pathological
    n_test = len(UFD_DATASET)
    print(f"Path 2 meaningful pass: {p2_meaningful}/{n_test - path2_pathological} "
          f"({path2_pathological}/{n_test} PATHOLOGICAL)")
    print(f"Path 3 meaningful pass: {p3_meaningful}/{n_test - path3_pathological} "
          f"({path3_pathological}/{n_test} PATHOLOGICAL)")
    print(f"Categorical meaningful pass: {cat_meaningful}/{n_test - cat_pathological} "
          f"({cat_pathological}/{n_test} PATHOLOGICAL)")
    print()
    print("=" * 70)
    print("VERDICT")
    print("=" * 70)
    if path2_pass == 0 and path3_pass == 0:
        print("All 4 UFDs fail under frozen Path 2 and Path 3 fits.")
        print("Missing parameter is in the low-f_b, low-v regime (UFDs fail uniformly).")
    elif path2_pass >= 3 or path3_pass >= 3:
        print("Most UFDs PASS under frozen fits.")
        print("Missing parameter is NOT in the UFD class; the Segue 1 FAIL is a one-off.")
    else:
        print("Mixed pass rate.")
        print("Some UFDs generalize, others don't. The 'missing parameter' is")
        print("in a specific subset of UFDs (segregation by another variable).")

    results["verdict"] = {
        # Strict counts (pred <= bound, includes pathological as PASS)
        "path2_strict_pass": path2_pass,
        "path2_strict_total": n_test,
        "path3_strict_pass": path3_pass,
        "path3_strict_total": n_test,
        "cat_strict_pass": cat_pass,
        "cat_strict_total": n_test,
        # Meaningful counts (excludes pathological)
        "path2_meaningful_pass": p2_meaningful,
        "path2_meaningful_fail": n_test - p2_meaningful - path2_pathological,
        "path2_pathological": path2_pathological,
        "path3_meaningful_pass": p3_meaningful,
        "path3_meaningful_fail": n_test - p3_meaningful - path3_pathological,
        "path3_pathological": path3_pathological,
        "cat_meaningful_pass": cat_meaningful,
        "cat_meaningful_fail": n_test - cat_meaningful - cat_pathological,
        "cat_pathological": cat_pathological,
        "pathological_floor": PATHOLOGICAL_FLOOR,
    }

    def _convert(o):
        if isinstance(o, (np.bool_,)):
            return bool(o)
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")

    out_path = RESULTS / "phase4e_multi_UFD_heldout.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=_convert)
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()