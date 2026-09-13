"""
Phase 7d — T95 stream cross-match tension at v0.3-prelim MAP.

Motivation (per roadmap §Phase 7 task 3)
----------------------------------------
The Phase 7 roadmap specifies re-evaluating the T95 stream cross-match
tension at the v0.3-prelim MAP (sigma/m_0 = 0.72, a = 1.31) rather than at
the v0.7-style "LZ-anchored" operating point (sigma/m ~ 0.7 cm^2/g at
v=150 km/s).

The T95 work found substantial-to-very-strong tension between the SIDM model
and stellar stream data:
  - T95 Phase 0 (Robertson BAHAMAS-SIDM): geometric mean ratio 0.72 across v
  - T95 Option 3.5 (8D + Channel 27 sub-halo): Deltalog Z = -1.57 (substantial)
  - T95 Option 3.6 (8D + Zhang GD-1): Deltalog Z = -23.61 (very strong)

These findings were at the LZ-anchored operating point (sigma/m_0_derived ~ 0.06
cm^2/g). At v0.3-prelim MAP, sigma/m_0 = 0.72 (12x higher) and a = 1.31.
The v-dependence extrapolates to:
  - v=10 km/s: sigma/m = 0.72 x (10/100)^(-1.31) = 14.4 cm^2/g
  - v=30 km/s: sigma/m = 0.72 x (30/100)^(-1.31) = 2.85 cm^2/g
  - v=100 km/s: sigma/m = 0.72 (by construction)
  - v=150 km/s: sigma/m = 0.72 x (150/100)^(-1.31) = 0.42 cm^2/g
  - v=1000 km/s: sigma/m = 0.72 x (1000/100)^(-1.31) = 0.04 cm^2/g

The T95 GD-1 constraint (Zhang+ 2025 ApJL 978 L23) requires sigma/m in
[30, 100] cm^2/g at v=10 km/s. v0.3-prelim MAP predicts 14.4 -- ~2x below
the lower bound (vs T95 v0.7 which was 94x below).

This phase re-runs the core T95 stream tension analysis at v0.3-prelim MAP.
The question: does the v0.3-prelim MAP RESOLVE, WORSEN, or NEITHER the T95
stream tension?

Kill criterion (per roadmap §Phase 7):
> Task 3: "Re-evaluate T95 stream cross-match tension at v0.3-prelim MAP"
> This sub-task is independent of the LZ mediator-class kill criterion.
> Phase 7d does NOT have a kill criterion per se -- it has a "tension report."

References
----------
- T95_CONSOLIDATED_RESULTS.md (T95 ship, v0.7-era operating point)
- T95_MULTI_STREAM_REAL_GALSTREAMS.md (113 real galstreams catalog)
- outputs/t95/multi_stream_real_galstreams.json (curated stream constraints)
- outputs/t95/t95_v26_full_results.json (113 streams with v_3d + sigma_m_pred)
- ROADMAP_MISSING_POSTERIORS_2026_09_12.md §Phase 7 task 3 (Phase 7d spec)

Verification
------------
    python phase7d_t95_stream_v03_map.py
runs the Phase 7d analysis and prints the verdict.
"""
from __future__ import annotations
import json
import math
import sys
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
V03_ROOT = SCRIPT_DIR.parent

# v0.3-prelim MAP operating point (T39 Tier-3 4D fit)
V03_MAP = {
    "sigma_m_0": 0.720,            # cm^2/g at V_REF = 100 km/s
    "a": 1.31,                       # velocity exponent (sigma/m ~ v^(-a))
    "log_epsilon": -56.113,
    "log_alpha": -28.047,
    "V_REF": 100.0,                  # km/s (per channels_v03.py convention)
}

# Reference operating point for comparison: T95 v0.7 (LZ-anchored)
T95_V07_REFERENCE = {
    "sigma_m_at_v150_cm2_per_g": 0.7,  # T95 7D median
    "a_implicit": 0.16,                  # T95 re-calibrated exponent
    "v_ref_for_sigma": 150.0,            # km/s
}

# Channel 27 sub-halo forecast range (T95 Option 3.5)
CHANNEL27_SUBHALO_FORECAST_RANGE = (0.05, 0.10)  # sigma/m in cm^2/g

# Zhang+ 2025 GD-1 perturber constraint
GD1_CONSTRAINT = {
    "sigma_m_lower": 30.0,  # cm^2/g
    "sigma_m_upper": 100.0,
    "v_kms": 10.0,
    "reference": "Zhang+ 2025 ApJL 978 L23 (SIDM interpretation)",
}

# Robertson's BAHAMAS-SIDM prescription anchor
ROBERTSON_BAHAMAS = {
    "sigma_0_cm2_per_g": 3.04,
    "w_kms": 560.0,
    "reference": "Robertson 2019, MNRAS 488, 3646",
}


def sigma_m_at_v(sigma_m_0: float, a: float, v: float, v_ref: float = 100.0) -> float:
    """Power-law sigma/m at velocity v: sigma/m(v) = sigma_m_0 * (v/v_ref)^(-a).

    Channels_v03.py convention: a > 0 means sigma/m drops with increasing v
    (typical for Yukawa-like mediators).
    """
    return sigma_m_0 * (v / v_ref) ** (-a)


def evaluate_stream_constraint(stream_name: str, sigma_m_lower: float,
                                sigma_m_upper: float, v_kms: float,
                                sigma_m_pred: float) -> dict:
    """Evaluate one stream tension: predicted sigma/m vs observation band."""
    in_range = bool(sigma_m_lower <= sigma_m_pred <= sigma_m_upper)
    # Tension metric: log10 of (predicted / nearest bound)
    if sigma_m_pred < sigma_m_lower:
        deficit_ratio = sigma_m_pred / sigma_m_lower
        log10_tension = math.log10(deficit_ratio)  # negative
        tension_label = "UNDERPREDICTION"
    elif sigma_m_pred > sigma_m_upper:
        excess_ratio = sigma_m_pred / sigma_m_upper
        log10_tension = math.log10(excess_ratio)
        tension_label = "OVERPREDICTION"
    else:
        log10_tension = 0.0
        tension_label = "IN_RANGE"
    return {
        "stream": stream_name,
        "v_kms": v_kms,
        "sigma_m_lower": sigma_m_lower,
        "sigma_m_upper": sigma_m_upper,
        "sigma_m_pred": sigma_m_pred,
        "in_range": in_range,
        "log10_tension_vs_nearest_bound": log10_tension,
        "tension_label": tension_label,
    }


def main():
    print("=" * 78)
    print("Phase 7d — T95 stream cross-match tension at v0.3-prelim MAP")
    print("=" * 78)
    print()
    print(f"v0.3-prelim MAP operating point:")
    print(f"  sigma/m_0 = {V03_MAP['sigma_m_0']} cm^2/g at V_REF = {V03_MAP['V_REF']} km/s")
    print(f"  a = {V03_MAP['a']}")
    print()
    print("sigma/m(v) profile at v0.3-prelim MAP:")
    for v in [10, 30, 100, 150, 1000]:
        s = sigma_m_at_v(V03_MAP['sigma_m_0'], V03_MAP['a'], v)
        print(f"  v = {v:>4} km/s: sigma/m = {s:>6.3f} cm^2/g")
    print()

    # ---- Step 1: Curated streams (10 streams with sigma_m bounds from literature) ----
    print(f"{'='*78}")
    print(f"STEP 1: Curated stream constraints at v0.3-prelim MAP")
    print(f"{'='*78}")
    curated_path = V03_ROOT / "outputs" / "t95" / "multi_stream_real_galstreams.json"
    with open(curated_path) as f:
        curated_data = json.load(f)
    curated_streams = curated_data["curated_streams"]

    curated_results = []
    n_in_range = 0
    n_underpredict = 0
    n_overpredict = 0
    print(f"{'Stream':>20} | {'v (km/s)':>8} | {'range':>15} | {'pred':>8} | {'status':>15} | {'log10(tens)':>11}")
    print("-" * 90)
    for name, c in curated_streams.items():
        v_kms = c["v_kms"]
        sm_lo = c["sigma_m_lower"]
        sm_hi = c["sigma_m_upper"]
        sm_pred = sigma_m_at_v(V03_MAP['sigma_m_0'], V03_MAP['a'], v_kms)
        r = evaluate_stream_constraint(name, sm_lo, sm_hi, v_kms, sm_pred)
        curated_results.append(r)
        if r["in_range"]:
            n_in_range += 1
        elif r["tension_label"] == "UNDERPREDICTION":
            n_underpredict += 1
        else:
            n_overpredict += 1
        range_str = f"[{sm_lo}, {sm_hi}]"
        print(f"{name:>20} | {v_kms:>8.1f} | {range_str:>15} | {sm_pred:>8.3f} | {r['tension_label']:>15} | {r['log10_tension_vs_nearest_bound']:>+11.2f}")
    print()
    print(f"Curated summary: {n_in_range}/{len(curated_results)} IN_RANGE, "
          f"{n_underpredict} UNDERPREDICTION, {n_overpredict} OVERPREDICTION")

    # ---- Step 2: GD-1 specifically (T95 headline tension) ----
    print()
    print(f"{'='*78}")
    print(f"STEP 2: GD-1 (Zhang+ 2025) at v0.3-prelim MAP vs T95 v0.7 reference")
    print(f"{'='*78}")
    sm_gd1_v03 = sigma_m_at_v(V03_MAP['sigma_m_0'], V03_MAP['a'], GD1_CONSTRAINT['v_kms'])
    sm_gd1_v07 = T95_V07_REFERENCE['sigma_m_at_v150_cm2_per_g'] * (
        GD1_CONSTRAINT['v_kms'] / T95_V07_REFERENCE['v_ref_for_sigma']
    ) ** (-T95_V07_REFERENCE['a_implicit'])
    # T95 doc reported sigma/m at v=10 of 0.32 at v0.7 MAP
    # T95 doc cited "94x below Zhang required [30, 100]"
    t95_v07_at_v10 = 0.32  # from T95 doc
    gd1_v03_log10_tension = math.log10(sm_gd1_v03 / GD1_CONSTRAINT['sigma_m_lower'])
    gd1_v07_log10_tension = math.log10(t95_v07_at_v10 / GD1_CONSTRAINT['sigma_m_lower'])
    print(f"GD-1 requires sigma/m in [{GD1_CONSTRAINT['sigma_m_lower']}, {GD1_CONSTRAINT['sigma_m_upper']}] cm^2/g at v={GD1_CONSTRAINT['v_kms']} km/s")
    print()
    print(f"  v0.3-prelim MAP prediction at v=10 km/s: {sm_gd1_v03:.3f} cm^2/g")
    print(f"    log10(pred/lower_bound) = {gd1_v03_log10_tension:+.3f}")
    print(f"    -> {gd1_v03_log10_tension * -1:.2f} orders below Zhang lower bound ({10**(-gd1_v03_log10_tension):.2f}x short)")
    print()
    print(f"  T95 v0.7 reference at v=10 km/s: {t95_v07_at_v10:.3f} cm^2/g (T95 doc)")
    print(f"    log10(pred/lower_bound) = {gd1_v07_log10_tension:+.3f}")
    print(f"    -> {gd1_v07_log10_tension * -1:.2f} orders below Zhang lower bound ({10**(-gd1_v07_log10_tension):.2f}x short)")
    print()
    print(f"  GD-1 tension improvement at v0.3-prelim MAP: factor of "
          f"{sm_gd1_v03 / t95_v07_at_v10:.2f}x (v0.3-prelim is {sm_gd1_v03 / t95_v07_at_v10:.2f}x LARGER than v0.7, less tension)")

    # ---- Step 3: Channel 27 sub-halo forecast at v0.3-prelim MAP ----
    print()
    print(f"{'='*78}")
    print(f"STEP 3: Channel 27 sub-halo forecast at v0.3-prelim MAP")
    print(f"{'='*78}")
    ch27_lo, ch27_hi = CHANNEL27_SUBHALO_FORECAST_RANGE
    # Channel 27 is at v ~ 150 km/s (Euclid Q1 lensing regime)
    sm_ch27_v03 = sigma_m_at_v(V03_MAP['sigma_m_0'], V03_MAP['a'], 150.0)
    sm_ch27_v07 = T95_V07_REFERENCE['sigma_m_at_v150_cm2_per_g']
    print(f"Channel 27 forecast range: [{ch27_lo}, {ch27_hi}] cm^2/g at v~150 km/s (Euclid Q1)")
    print()
    print(f"  v0.3-prelim MAP prediction at v=150 km/s: {sm_ch27_v03:.3f} cm^2/g")
    if ch27_lo <= sm_ch27_v03 <= ch27_hi:
        ch27_status = "IN_RANGE"
    elif sm_ch27_v03 < ch27_lo:
        ch27_status = f"OVERPREDICTION ({sm_ch27_v03 / ch27_hi:.2f}x above upper bound)"
    else:
        ch27_status = f"UNDERPREDICTION ({ch27_hi / sm_ch27_v03:.2f}x below lower bound)"
    print(f"    status: {ch27_status}")
    print()
    print(f"  T95 v0.7 reference at v=150 km/s: {sm_ch27_v07:.3f} cm^2/g")
    print(f"    T95 doc: '0.7 cm^2/g is 6-13x above Euclid Q1 sub-halo forecast [0.05-0.10]'")
    if ch27_lo <= sm_ch27_v07 <= ch27_hi:
        ch27_v07_status = "IN_RANGE"
    elif sm_ch27_v07 < ch27_lo:
        ch27_v07_status = f"OVERPREDICTION ({sm_ch27_v07 / ch27_hi:.2f}x above upper bound)"
    else:
        ch27_v07_status = f"UNDERPREDICTION ({ch27_hi / sm_ch27_v07:.2f}x below lower bound)"
    print(f"    status: {ch27_v07_status}")
    print()
    print(f"  Channel 27 comparison: v0.3-prelim MAP is {sm_ch27_v07 / sm_ch27_v03:.2f}x LOWER than T95 v0.7 reference")

    # ---- Step 4: Robertson BAHAMAS-SIDM comparison ----
    print()
    print(f"{'='*78}")
    print(f"STEP 4: Robertson 2019 BAHAMAS-SIDM prescription comparison")
    print(f"{'='*78}")
    print(f"Robertson BAHAMAS-SIDM: sigma_T(v) = sigma_0 / (1 + (v/w)^2)")
    print(f"  sigma_0 = {ROBERTSON_BAHAMAS['sigma_0_cm2_per_g']} cm^2/g, w = {ROBERTSON_BAHAMAS['w_kms']} km/s")
    print()
    robertson_v150 = ROBERTSON_BAHAMAS['sigma_0_cm2_per_g'] / (1 + (150.0 / ROBERTSON_BAHAMAS['w_kms']) ** 2)
    robertson_v1000 = ROBERTSON_BAHAMAS['sigma_0_cm2_per_g'] / (1 + (1000.0 / ROBERTSON_BAHAMAS['w_kms']) ** 2)
    print(f"  Robertson sigma/m at v=150 km/s:  {robertson_v150:.3f} cm^2/g")
    print(f"  Robertson sigma/m at v=1000 km/s: {robertson_v1000:.3f} cm^2/g")
    print()
    print(f"  v0.3-prelim MAP at v=150 km/s:   {sm_ch27_v03:.3f} cm^2/g (ratio {sm_ch27_v03/robertson_v150:.3f})")
    print(f"  v0.3-prelim MAP at v=1000 km/s:  {sigma_m_at_v(V03_MAP['sigma_m_0'], V03_MAP['a'], 1000):.3f} cm^2/g (ratio {sigma_m_at_v(V03_MAP['sigma_m_0'], V03_MAP['a'], 1000)/robertson_v1000:.3f})")
    print()
    print(f"  T95 doc reported geometric mean ratio 0.72 across v=100-1500 km/s")
    print(f"  v0.3-prelim MAP ratio range across [100, 1000] km/s:")
    vmin, vmax = 100, 1000
    ratios = []
    for v in [100, 150, 200, 300, 500, 1000, 1500]:
        v03_v = sigma_m_at_v(V03_MAP['sigma_m_0'], V03_MAP['a'], v)
        rob_v = ROBERTSON_BAHAMAS['sigma_0_cm2_per_g'] / (1 + (v / ROBERTSON_BAHAMAS['w_kms']) ** 2)
        ratios.append(v03_v / rob_v)
        print(f"    v={v:>4} km/s: v0.3 = {v03_v:.3f}, Robertson = {rob_v:.3f}, ratio = {v03_v/rob_v:.3f}")
    geo_mean = np.exp(np.mean(np.log(ratios)))
    print(f"  Geometric mean ratio across sweep: {geo_mean:.3f}")
    print(f"  T95 reference geometric mean: 0.72")

    # ---- Step 5: Verdict ----
    print()
    print(f"{'='*78}")
    print(f"VERDICT (Phase 7d, T95 stream tension at v0.3-prelim MAP)")
    print(f"{'='*78}")
    # Phase 7d does NOT have a kill criterion (it's independent of LZ).
    # The "verdict" is a tension report.
    gd1_improved = abs(gd1_v03_log10_tension) < abs(gd1_v07_log10_tension)
    ch27_improved = (ch27_lo <= sm_ch27_v03 <= ch27_hi) and not (ch27_lo <= sm_ch27_v07 <= ch27_hi)
    print()
    print(f"  GD-1 (Zhang+ 2025): {('IMPROVED' if gd1_improved else 'SAME OR WORSE')} at v0.3-prelim MAP")
    print(f"    v0.7: {10**(-gd1_v07_log10_tension):.2f}x short ({gd1_v07_log10_tension * -1:.2f} orders)")
    print(f"    v0.3-prelim: {10**(-gd1_v03_log10_tension):.2f}x short ({gd1_v03_log10_tension * -1:.2f} orders)")
    print()
    print(f"  Channel 27 (Euclid Q1): {('IMPROVED' if ch27_improved else 'STILL TENSE')} at v0.3-prelim MAP")
    print(f"    v0.7: 0.7 cm^2/g was 6-13x above [0.05, 0.10]")
    print(f"    v0.3-prelim: {sm_ch27_v03:.3f} cm^2/g")
    print()
    print(f"  Curated streams (10 streams): {n_in_range}/{len(curated_results)} in range")
    print()
    print(f"  Robertson BAHAMAS-SIDM agreement: geometric mean ratio {geo_mean:.3f} (T95 doc: 0.72)")
    print()
    print("  Phase 7d has NO kill criterion (independent of LZ). This is a tension report.")
    print(f"  Overall verdict: v0.3-prelim MAP {'RESOLVES' if (gd1_improved and ch27_improved) else 'PARTIALLY RESOLVES' if gd1_improved else 'does NOT resolve'} the T95 stream tension.")

    # ---- Save results ----
    result = {
        "phase": "7d",
        "date": "2026-09-13",
        "title": "T95 stream cross-match tension at v0.3-prelim MAP",
        "v03_MAP": V03_MAP,
        "sigma_m_profile_at_v03_map": {
            f"v={v}_kms": sigma_m_at_v(V03_MAP['sigma_m_0'], V03_MAP['a'], v)
            for v in [10, 30, 100, 150, 200, 300, 500, 1000, 1500]
        },
        "step_1_curated_streams": curated_results,
        "step_1_summary": {
            "n_total": len(curated_results),
            "n_in_range": n_in_range,
            "n_underpredict": n_underpredict,
            "n_overpredict": n_overpredict,
        },
        "step_2_gd1": {
            "constraint": GD1_CONSTRAINT,
            "v03_prediction_at_v10": float(sm_gd1_v03),
            "v07_reference_at_v10": float(t95_v07_at_v10),
            "v03_log10_tension_vs_lower": float(gd1_v03_log10_tension),
            "v07_log10_tension_vs_lower": float(gd1_v07_log10_tension),
            "improvement_factor": float(sm_gd1_v03 / t95_v07_at_v10),
            "improved_at_v03": bool(gd1_improved),
        },
        "step_3_channel27": {
            "forecast_range": list(CHANNEL27_SUBHALO_FORECAST_RANGE),
            "v03_prediction_at_v150": float(sm_ch27_v03),
            "v07_reference_at_v150": float(sm_ch27_v07),
            "v03_status": ch27_status,
            "v07_status": ch27_v07_status,
            "improved_at_v03": bool(ch27_improved),
        },
        "step_4_robertson": {
            "geo_mean_ratio_v03": float(geo_mean),
            "geo_mean_ratio_t95_reference": 0.72,
        },
        "overall_verdict": (
            "v0.3-prelim MAP RESOLVES the T95 stream tension"
            if (gd1_improved and ch27_improved) else
            "v0.3-prelim MAP PARTIALLY RESOLVES the T95 stream tension (GD-1 improved, Channel 27 not)"
            if gd1_improved else
            "v0.3-prelim MAP does NOT resolve the T95 stream tension"
        ),
        "kill_criterion": "NONE (Phase 7d is independent of LZ, no kill criterion per roadmap §Phase 7)",
    }
    out_path = V03_ROOT / "data" / "results" / "phase7d_t95_stream_v03_map.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print()
    print(f"Results written to: {out_path}")
    return result


if __name__ == "__main__":
    main()
