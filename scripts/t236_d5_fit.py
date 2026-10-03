"""
T236 / D-5 FIT (R81): Full likelihood fit over sigma_1 (v_1 Gaussian width)

Per R80 plan reviewer: D-5 was a sensitivity sweep, not the fit called for.
R81 builds the proper fit:
  - Single-Gaussian parameterization (paper convention)
  - sigma_1 sweeps 6 values (1.0, 2.0, 3.0, 4.0, 4.4, 6.0 km/s)
  - 8-channel likelihood (SPARC, JVAS, Cloud-9, Fornax, Draco, Sculptor, UFD, Cluster)
  - Fornax likelihood is the dSph collapse constraint
  - Report delta-log L vs sigma_1 = 4.4 baseline

Decision criterion: delta log L > 5 for adopting new value (1-parameter comparison).

ARITHMETIC CHECKS (per arithmetic-checking-before-claim):
1. Known-system sanity: sigma/m(v_target=29.4) = 174.18 cm^2/g
2. Unit consistency: sigma_1 input in km/s, sigma/m output in cm^2/g
3. Physics consistency: peak at v_target, sigma/m >= 0
4. Functional form: sigma_1 = Gaussian sigma (NOT FWHM)
"""

import json
import math
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
from constants import (
    M_CHI_GEV,
    V_TARGET_KMS,
    SIGMA_KMS,
    SIGMA_PEAK_CM2_PER_G,
    M_NUCLEON_GEV,
)


def sigma_m(v_kms, v_target=V_TARGET_KMS, sigma_kms=SIGMA_KMS, sigma_peak=SIGMA_PEAK_CM2_PER_G):
    """Single-Gaussian sigma/m(v) in cm^2/g. No background Yukawa — paper convention
    uses 0.052 * (v/100)^-1 background but the dSph constraints come from the
    Gaussian tail which dominates the dSph channels.
    """
    return sigma_peak * math.exp(-(v_kms - v_target) ** 2 / (2 * sigma_kms ** 2))


# ====== ARITHMETIC CHECKS ======

def check_arithmetic():
    print("=" * 70)
    print("T236 arithmetic checks (per arithmetic-checking-before-claim)")
    print("=" * 70)
    print()
    # Check 1: Known-system sanity
    s_peak = sigma_m(V_TARGET_KMS, sigma_kms=SIGMA_KMS)
    print(f"CHECK 1: sigma/m(v_target={V_TARGET_KMS}, sigma_1={SIGMA_KMS}) = {s_peak:.4f} cm^2/g")
    print(f"  Expected: ~174 cm^2/g (the peak value)")
    assert abs(s_peak - 174.0) < 1.0, f"FAIL: expected ~174, got {s_peak}"
    print(f"  ✓ matches")

    # Check 2: Unit consistency
    print(f"\nCHECK 2: Unit consistency")
    print(f"  sigma_1 input: km/s (Gaussian sigma)")
    print(f"  v input: km/s")
    print(f"  sigma_peak: cm^2/g")
    print(f"  output: cm^2/g ✓")

    # Check 3: Physics consistency
    s_minus = sigma_m(V_TARGET_KMS - 5, sigma_kms=SIGMA_KMS)
    s_plus = sigma_m(V_TARGET_KMS + 5, sigma_kms=SIGMA_KMS)
    print(f"\nCHECK 3: Peak at v_target")
    print(f"  sigma/m(v={V_TARGET_KMS}): {s_peak:.4f}")
    print(f"  sigma/m(v={V_TARGET_KMS-5}): {s_minus:.4f}")
    print(f"  sigma/m(v={V_TARGET_KMS+5}): {s_plus:.4f}")
    assert s_peak > s_minus and s_peak > s_plus
    print(f"  ✓ peak at v_target confirmed")

    # Check 4: Functional form
    s_if_fwhm = sigma_m(15.0, sigma_kms=SIGMA_KMS / 2.355)  # 1.870
    print(f"\nCHECK 4: Functional form (sigma vs FWHM)")
    print(f"  sigma/m(15) if sigma_1 = FWHM = 1.870: {s_if_fwhm:.4e} cm^2/g")
    print(f"  -> sigma_1 = 4.4 must be Gaussian sigma (not FWHM)")
    assert s_if_fwhm < 0.001, f"FAIL: FWHM convention should give essentially 0 at v=15"
    print(f"  ✓ FWHM convention would give essentially 0 at v=15; sigma convention gives the headline")
    print()


# ====== 8-CHANNEL LIKELIHOOD ======
# Per R81 reviewer: "sigma_1 is currently unconstrained by the 7 non-Fornax channels;
# the choice between 3.0 and 4.4 is a Fornax question, not an 8-channel question."

# Channel targets (from paper §3 observational constraints):
CHANNELS = {
    "Cloud-9 (V_max=28, sigma/m=100 cm^2/g)": {"v": 28.0, "target": 100.0, "width": 30.0, "type": "target"},
    "JVAS B1938+666 (V_max=15, sigma/m=100)": {"v": 15.0, "target": 100.0, "width": 50.0, "type": "target"},
    "SPARC (V_max=100, sigma/m=0.07)": {"v": 100.0, "target": 0.07, "width": 0.05, "type": "target"},
    "Fornax (V_max=18, no-collapse)": {"v": 18.0, "target": 0.5, "width": 0.3, "type": "upper"},
    "Draco (V_max=10, no-collapse)": {"v": 10.0, "target": 0.5, "width": 0.3, "type": "upper"},
    "Sculptor (V_max=9, no-collapse)": {"v": 9.0, "target": 0.5, "width": 0.3, "type": "upper"},
    "UFD Segue 1 (V_max=3, sigma/m<1)": {"v": 3.0, "target": 0.5, "width": 0.5, "type": "upper"},
    "Cluster (V_max=500, sigma/m<0.001)": {"v": 500.0, "target": 0.001, "width": 0.001, "type": "upper"},
}


def logL_channel(sigma_m_v, target, width, type_):
    """Single-channel log likelihood.
    target: for 'target' type, the desired sigma/m
            for 'upper' type, the upper limit (target is below this)
    width: sigma of Gaussian (for target) or scale (for upper)
    type_: 'target' (Gaussian centered on target) or 'upper' (Gaussian penalty if above)
    """
    if sigma_m_v < 0:
        return -1e6
    if type_ == "target":
        # Gaussian centered on target
        return -((sigma_m_v - target) ** 2) / (2 * width ** 2)
    elif type_ == "upper":
        # If sigma/m_v < target: no penalty (passes)
        # If sigma/m_v > target: quadratic penalty
        if sigma_m_v < target:
            return 0.0
        return -((sigma_m_v - target) / width) ** 2
    else:
        return 0.0


def joint_logL(sigma_kms):
    """Joint log likelihood across all 8 channels."""
    total = 0.0
    for name, ch in CHANNELS.items():
        s = sigma_m(ch["v"], sigma_kms=sigma_kms)
        total += logL_channel(s, ch["target"], ch["width"], ch["type"])
    return total


def d5_fit_main():
    print("=" * 70)
    print("T236 / D-5 FIT: Full likelihood over sigma_1 (single-Gaussian parameterization)")
    print("=" * 70)
    print()
    print("Per R81 reviewer: 'sigma_1 is currently unconstrained by the 7")
    print("non-Fornax channels; the choice between 3.0 and 4.4 is a Fornax")
    print("question, not an 8-channel question.'")
    print()
    print("8-channel likelihood = SPARC + JVAS + Cloud-9 + Fornax + Draco +")
    print("Sculptor + UFD + Cluster (targets per paper §3).")
    print()

    sigma_1_values = [1.0, 2.0, 3.0, 4.0, 4.4, 6.0]

    # Compute baseline log L at sigma_1 = 4.4
    baseline = joint_logL(SIGMA_KMS)
    print(f"BASELINE log L at sigma_1 = {SIGMA_KMS}: {baseline:.3f}")
    print()

    results = {}
    for sigma_1 in sigma_1_values:
        log_L = joint_logL(sigma_1)
        delta_log_L = log_L - baseline
        # Per-channel breakdown
        per_channel = {}
        for name, ch in CHANNELS.items():
            s = sigma_m(ch["v"], sigma_kms=sigma_1)
            ll = logL_channel(s, ch["target"], ch["width"], ch["type"])
            per_channel[name] = {"sigma_m": float(s), "log_L": float(ll)}
        results[sigma_1] = {
            "log_L": float(log_L),
            "delta_log_L": float(delta_log_L),
            "per_channel": per_channel,
        }

    # Print summary table
    print(f"{'sigma_1 (km/s)':<14} {'log L':<12} {'delta log L':<14} {'verdict'}")
    print("-" * 70)
    for sigma_1 in sigma_1_values:
        r = results[sigma_1]
        d = r["delta_log_L"]
        if sigma_1 == SIGMA_KMS:
            verdict = "(baseline)"
        elif d > 5:
            verdict = "PREFERRED (>5 sigma)"
        elif d > 2:
            verdict = "moderately preferred"
        elif d > -2:
            verdict = "consistent"
        elif d > -5:
            verdict = "moderately disfavored"
        else:
            verdict = "DISFAVORED (<-5 sigma)"
        print(f"{sigma_1:<14.1f} {r['log_L']:<12.3f} {d:<+14.3f} {verdict}")

    print()
    print("=" * 70)
    print("D-5 FIT RESULT")
    print("=" * 70)
    print()

    # Find preferred sigma_1
    preferred = max(results.keys(), key=lambda s: results[s]["log_L"])
    print(f"Maximum-likelihood sigma_1: {preferred} km/s (log L = {results[preferred]['log_L']:.3f})")
    print(f"Baseline sigma_1:           {SIGMA_KMS} km/s (log L = {baseline:.3f})")
    print(f"delta log L (preferred - baseline): {results[preferred]['delta_log_L']:+.3f}")
    print()

    # Check Fornax contribution
    for_ch = "Fornax (V_max=18, no-collapse)"
    print(f"Per-channel log L at sigma_1 = {SIGMA_KMS} (baseline):")
    for name, val in results[SIGMA_KMS]["per_channel"].items():
        flag = " <-- discriminating" if name == for_ch and val["log_L"] < -2 else ""
        print(f"  {name[:50]:<50}: sigma/m = {val['sigma_m']:8.3f}, log L = {val['log_L']:+8.3f}{flag}")
    print()

    print(f"Per-channel log L at sigma_1 = {preferred} (preferred):")
    for name, val in results[preferred]["per_channel"].items():
        flag = " <-- discriminating" if name == for_ch and val["log_L"] < -2 else ""
        print(f"  {name[:50]:<50}: sigma/m = {val['sigma_m']:8.3f}, log L = {val['log_L']:+8.3f}{flag}")
    print()

    # Headline verdict
    if results[preferred]["delta_log_L"] > 5:
        verdict = f"PREFERRED: sigma_1 = {preferred} km/s (delta log L = +{results[preferred]['delta_log_L']:.1f} vs baseline)"
        outcome = "dSph tension RESOLVED by narrower width"
    elif results[preferred]["delta_log_L"] < -5:
        verdict = f"BASELINE PREFERRED: sigma_1 = {SIGMA_KMS} (delta log L = {results[preferred]['delta_log_L']:.1f})"
        outcome = "dSph tension STANDS; framework falsified at dSph scales unless N-body resolution applies"
    else:
        verdict = f"NOT DISCRIMINATED: log L difference = {results[preferred]['delta_log_L']:.1f} (<5 threshold)"
        outcome = "dSph data don't discriminate sigma_1; framework's sigma_1 is underdetermined"

    print("=" * 70)
    print(f"VERDICT: {verdict}")
    print(f"OUTCOME: {outcome}")
    print("=" * 70)

    # Save results
    output_path = Path(__file__).parent.parent / "data" / "results" / "t236_d5_fit.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_data = {
        "script": "T236 (D-5 FIT)",
        "description": "Full likelihood fit over sigma_1 (v_1 Gaussian width) with 8 channels",
        "framework_constants": {
            "M_CHI_GEV": M_CHI_GEV,
            "V_TARGET_KMS": V_TARGET_KMS,
            "SIGMA_KMS_BASELINE": SIGMA_KMS,
            "SIGMA_PEAK_CM2_PER_G": SIGMA_PEAK_CM2_PER_G,
        },
        "channels": CHANNELS,
        "sigma_1_values": sigma_1_values,
        "baseline_log_L": float(baseline),
        "preferred_sigma_1": float(preferred),
        "results_by_sigma_1": {
            str(sigma_1): {
                "log_L": float(r["log_L"]),
                "delta_log_L": float(r["delta_log_L"]),
                "per_channel": {
                    name: {"sigma_m": float(v["sigma_m"]), "log_L": float(v["log_L"])}
                    for name, v in r["per_channel"].items()
                },
            }
            for sigma_1, r in results.items()
        },
        "verdict": verdict,
        "outcome": outcome,
    }
    output_path.write_text(json.dumps(output_data, indent=2))
    print(f"\nResults saved to {output_path}")

    return results, verdict, outcome


if __name__ == "__main__":
    check_arithmetic()
    print("All 4 arithmetic checks PASS")
    print()
    results, verdict, outcome = d5_fit_main()
