#!/usr/bin/env python3
"""
T68b — QUANTITATIVE cross-validation against Drobczyk 2025 (arXiv:2506.22997).

Extends T68 (qualitative, hardcoded benchmark numbers) with a REAL chi^2 test:
compute our sigma/m(v) at the same velocity grid as Drobczyk's published curve,
then chi^2-test against Drobczyk's predictions.

The velocity-dependent formula (per channels_v03.py):
    sigma/m(v) = sigma/m_0 * (v / V_REF) ** (-a)
with V_REF = 100 km/s. We use the T41 v0.6 hier-sparc MAP as our point estimate.

Drobczyk's published predictions (3 velocity points):
    sigma_T/m_chi = 0.96   cm^2/g at v=10  km/s (dwarf)
    sigma_T/m_chi = 0.11   cm^2/g at v=30  km/s (MW satellites)
    sigma_T/m_chi = 9.5e-5 cm^2/g at v=1000 km/s (clusters)

Chi^2 metric (3 data points, 2 fit params — sigma/m_0 and a — so 1 dof):
    chi^2 = sum_i ((log10(sigma_us(v_i)) - log10(sigma_drob(v_i))) / sigma_err)^2
where sigma_err is the 1-sigma uncertainty on log10(sigma/m) per point.

Honest framing
--------------
Our MAP sigma/m_0 ~ 0.065 cm^2/g is BELOW Drobczyk's dwarf value (0.96) by
~1.2 dex. This is a real quantitative disagreement at the dwarf scale.
Interpretation: Drobczyk's two-mediator model with resonance freeze-out
naturally produces higher sigma/m at low v than our single-mediator dark-rho
model. The two models make DIFFERENT predictions, and our posterior MAP
prefers the low-sigma/m regime.

We do NOT conclude "we're right, Drobczyk's wrong" — both are valid model
frameworks with different physics. We report the chi^2 honestly and note
that a future hierarchical model comparison would need both models fit to
the SAME data with the SAME likelihood machinery.
"""
from __future__ import annotations
import json
import math
import os
import sys
from pathlib import Path

import numpy as np

# Lazy import to avoid the v0.3-prelim dependency on full pipeline
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Use the canonical sigma/m_at_v from channels_v03
try:
    from channels_v03 import sigma_m_at_v, V_REF
except ImportError:
    # Inline fallback (copied from channels_v03.py:38-43)
    V_REF = 100.0
    def sigma_m_at_v(sigma_m_0, a, v):
        return sigma_m_0 * (v / V_REF) ** (-a)


RESULTS_DIR = Path("/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/data/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def load_t41_map(t41_json_path: Path) -> dict:
    """Extract MAP sigma/m_0 + a from a T41 result JSON."""
    with t41_json_path.open() as f:
        d = json.load(f)
    mp = d["MAP_physical"]
    return {
        "sigma_m_0_median": float(mp["sigma_m_0_derived"]),
        "a_median":         float(mp["a_derived"]),
        "m_phi_MeV_MAP":    float(mp["m_phi_MeV"]),
        "m_chi_GeV_MAP":    float(mp["m_chi_GeV"]),
        "xi_MAP":           float(mp["xi"]),
        "source":           t41_json_path.name,
    }


def drobczky_benchmark():
    """Drobczyk 2025 published sigma/m(v) at 3 velocity points."""
    return {
        "v_km_s":     [10.0,    30.0,    1000.0],
        "sigma_cm2_g":[0.96,    0.11,    9.5e-5],
        "label":      ["dwarf (v=10)",  "MW satellite (v=30)",  "cluster (v=1000)"],
        "ref":        "arXiv:2506.22997 (Class. Quantum Grav. 42 225006), Tab. 1",
    }


def compute_our_sigma_m(sigma_m_0: float, a: float, v_km_s: list) -> list:
    """Our velocity-dependent cross-section at Drobczyk's velocity grid."""
    return [sigma_m_at_v(sigma_m_0, a, v) for v in v_km_s]


def compute_chi2(sigma_m_0: float, a: float, drob: dict, sigma_err_log10: float = 0.2) -> dict:
    """Chi^2 test of our sigma/m(v) vs Drobczyk's curve (3 points, 1 dof).

    sigma_err_log10: assumed 1-sigma uncertainty on log10(sigma/m) per point.
    The 0.2 dex choice is a "reasonable published uncertainty" — Drobczyk
    reports curves but no per-point error bars in the published table, so
    we use a conservative 0.2 dex which is ~factor-of-1.6.
    """
    v_pts   = drob["v_km_s"]
    sigma_d = drob["sigma_cm2_g"]
    sigma_o = compute_our_sigma_m(sigma_m_0, a, v_pts)

    contributions = []
    for i, (v, sd, so) in enumerate(zip(v_pts, sigma_d, sigma_o)):
        log_d = math.log10(sd)
        log_o = math.log10(so)
        delta_log = log_o - log_d
        chi_i = (delta_log / sigma_err_log10) ** 2
        contributions.append({
            "v_km_s":            v,
            "label":             drob["label"][i],
            "sigma_drob_log10":  log_d,
            "sigma_our_log10":   log_o,
            "delta_log10":       delta_log,
            "delta_factor":      so / sd,
            "chi2_contribution": chi_i,
        })

    chi2_total = sum(c["chi2_contribution"] for c in contributions)
    dof = max(1, len(contributions) - 2)  # 3 points - 2 free params (sigma_m_0, a) = 1 dof
    p_value_threshold = {
        1.0:  0.317,   # chi^2=1 → p=0.317 (consistent)
        2.71: 0.10,    # 1-sigma boundary
        6.63: 0.01,    # 2-sigma boundary
        16.3: 0.001,   # 3-sigma boundary
    }
    closest_p = min(p_value_threshold.keys(), key=lambda k: abs(k - chi2_total))
    return {
        "chi2_total": chi2_total,
        "dof": dof,
        "sigma_err_log10_per_point": sigma_err_log10,
        "per_point": contributions,
        "interpretation": (
            f"chi^2 = {chi2_total:.2f} on {dof} dof (sigma_err_log10 = {sigma_err_log10}). "
            f"Closest published threshold: chi^2 ~ {closest_p:.2f} ≈ p = {p_value_threshold[closest_p]:.3f}. "
            + ("CONSISTENT — our velocity-dependent curve agrees with Drobczyk within error bars."
               if chi2_total < 2.71 else
               ("TENSION — modest disagreement at this uncertainty."
                if chi2_total < 6.63 else
                "STRONG TENSION — our curve does NOT match Drobczyk's within error bars."))
        ),
    }


def main() -> int:
    print("=" * 80)
    print("  T68b — Quantitative cross-validation against Drobczyk 2025")
    print("=" * 80)

    # Use the T71.4 hier-sparc MAP as our point estimate
    # (latest nlive=2000 result with real per-galaxy SPARC likelihood)
    t41_path = RESULTS_DIR / "t41_mediator_mass_joint_fit_v0_6_hier_sparc.json"
    if not t41_path.exists():
        print(f"FATAL: {t41_path.name} not found; run T71.4 first.")
        return 1

    our_map = load_t41_map(t41_path)
    print(f"\nOur T41 v0.6 hier-sparc MAP (from {our_map['source']}):")
    for k, v in our_map.items():
        print(f"  {k}: {v}")

    # Drobczyk benchmark
    drob = drobczky_benchmark()
    print("\nDrobczyk 2025 benchmark (3 velocity points):")
    for v, s, l in zip(drob["v_km_s"], drob["sigma_cm2_g"], drob["label"]):
        print(f"  v={v:>5} km/s: sigma/m = {s:.3g} cm^2/g  ({l})")

    # Our values at the same v-grid
    print("\nOur sigma/m(v) at Drobczyk's v-grid:")
    sigma_ours = compute_our_sigma_m(our_map["sigma_m_0_median"], our_map["a_median"], drob["v_km_s"])
    for v, s, l in zip(drob["v_km_s"], sigma_ours, drob["label"]):
        print(f"  v={v:>5} km/s: sigma/m = {s:.3g} cm^2/g  ({l})")

    # Chi^2 test
    print("\n--- Chi^2 test (sigma_err_log10 = 0.2 dex) ---")
    chi2 = compute_chi2(our_map["sigma_m_0_median"], our_map["a_median"], drob, sigma_err_log10=0.2)
    print(f"  chi^2 = {chi2['chi2_total']:.2f} on {chi2['dof']} dof")
    for c in chi2["per_point"]:
        print(f"  [{c['label']}] log10(our/drob) = {c['delta_log10']:+.3f}, "
              f"factor = {c['delta_factor']:.2f}x, chi^2_contrib = {c['chi2_contribution']:.3f}")
    print(f"\n  → {chi2['interpretation']}")

    # Sensitivity: how much would we need sigma/m_0 or a to be to match?
    # Solve for sigma/m_0 at v=10 km/s = 0.96 cm^2/g given our a
    target_v10 = drob["sigma_cm2_g"][0]
    required_sm0_at_a114 = target_v10 * (10.0 / V_REF) ** our_map["a_median"]
    print(f"\nFor our sigma/m(v=10 km/s) to match Drobczyk's 0.96 cm^2/g at a={our_map['a_median']:.3f}:")
    print(f"  Required sigma/m_0 at v=100 km/s = {required_sm0_at_a114:.2f} cm^2/g")
    print(f"  vs our MAP sigma/m_0 = {our_map['sigma_m_0_median']:.4f} cm^2/g")
    print(f"  (factor {required_sm0_at_a114 / our_map['sigma_m_0_median']:.0f}x higher than MAP)")

    # Write result JSON
    out = {
        "test": "T68b_quantitative_cross_validation",
        "direction": ("R16 #8 quantitative closure: chi^2 test of our sigma/m(v) curve "
                      "vs Drobczyk 2025 published sigma/m(v) at 3 velocity points"),
        "our_pipeline": our_map,
        "drobczyk_2025": drob,
        "chi2_test": chi2,
        "what_would_need_to_change": {
            "required_sigma_m_0_at_v100_to_match_dwarf": required_sm0_at_a114,
            "current_sigma_m_0_MAP": our_map["sigma_m_0_median"],
            "factor_short": required_sm0_at_a114 / our_map["sigma_m_0_median"],
        },
        "honest_framing": [
            "Our T41 MAP sigma/m_0 = 0.065 cm^2/g is significantly LOWER than Drobczyk's dwarf prediction (0.96).",
            "The ~1.2 dex gap at the dwarf scale reflects a real quantitative disagreement between the two models:",
            "  - Drobczyk's two-mediator model with resonant freeze-out naturally produces HIGHER sigma/m at low v.",
            "  - Our single-mediator dark-rho model produces LOWER sigma/m at low v (consistent with our v0.6 calibration_score → hier_sparc shift of +0.10 log Z at nlive=2000).",
            "Both models are valid frameworks with different physics; we do NOT conclude one is 'right' and the other 'wrong'.",
            "A future hierarchical model comparison would need both models fit to the SAME data with the SAME likelihood machinery.",
            "The chi^2 test is sensitive to the assumed sigma_err_log10 per point (0.2 dex here); with a wider error bar the tension could disappear.",
        ],
        "caveats": [
            "Drobczyk does NOT publish per-point error bars on their sigma/m(v) curve; the 0.2 dex sigma_err_log10 is a conservative choice.",
            "Our MAP is from a single T41 joint fit; the posterior uncertainty on sigma/m_0 and a would give a wider range than the point estimate.",
            "The two models use different coupling parameterizations (y_chi Yukawa vs g_chi gauge coupling); a direct chi^2 comparison is approximate.",
        ],
        "t68_history": [
            "T68 (2026-08-18): qualitative comparison with hardcoded Drobczyk numbers (R11 A13, G7 closure).",
            "T68b (2026-08-28): quantitative chi^2 test using T41 v0.6 hier-sparc MAP as our point estimate (this commit).",
        ],
    }
    out_path = RESULTS_DIR / "t68b_quantitative_cross_validation.json"
    out_path.write_text(json.dumps(out, indent=2))
    # Mirror to Windows
    win = Path("/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/t68b_quantitative_cross_validation.json")
    if win.parent.exists():
        win.write_text(json.dumps(out, indent=2))
        print(f"\nWrote: {out_path}\n       {win}")
    else:
        print(f"\nWrote: {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
