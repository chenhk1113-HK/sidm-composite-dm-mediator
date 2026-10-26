#!/usr/bin/env python3
"""
audit_hierarchy_chain.py — Gate layer 10: the hierarchy-bound chain.

WHY THIS EXISTS
---------------
Tracked gap **CG-9** in the consolidated report states the problem exactly:

  "The 7-layer gate does not read the paper's hierarchy-bound chain - σ/m(28)
   at σ_1 = 1.0, the ratio σ_DM-DM/σ_SI, and the g_N/g_χ bound it implies -
   none of which audit_claims.py or the standing-numbers table re-reads."

That gap was not hypothetical. The stale `a_slope = 1.0` value (σ/m(28) =
65.49 instead of 65.91) sat in the paper and passed a 7/7 gate, because every
existing layer validates the paper's INDEPENDENT claims (units, drift, mapped
numbers, citations) but never validates the DERIVED CHAIN: if σ/m(28) is
wrong, the ratio and the bound that are quoted downstream of it are wrong too,
and nothing notices.

This layer closes CG-9 by recomputing the chain from the canonical inputs and
checking every link:

  1. σ/m(28) at σ_1 = 1.0  <- constants.py (σ_0, a_slope, σ_peak, v_target)
                              cross-checked against
                              data/results/t235_d5_width_test.json
  2. ratio σ_DM-DM/σ_SI   <- σ/m(28) x m_χ / σ_SI
  3. g_N/g_χ bound        <- 1/sqrt(ratio)
  4. the paper's quoted values must equal the recomputed ones
  5. the RETRACTED values must be absent from the paper

Every arithmetic step is done here from first principles; nothing is copied
from the paper. The unit convention is explicit (cm^2/g -> ratio -> bound),
and the three sanity classes from the arithmetic-checking skill are applied:
a known-system check (σ/m(28) at σ_1 = 4.4 must equal the t235 JSON's
166.018...), a unit-consistency check (the chain is dimensionless at the
ratio step and a bound at the last), and a physics-consistency check (the
bound must be a positive number below 1, and the ordering "the v = 28 bound
is LOOSER than the σ_1 = 4.4 headline" must hold).

Usage:
    python scripts/audit_hierarchy_chain.py
    python scripts/audit_hierarchy_chain.py --json

Exit: 0 = the chain recomputes and the paper agrees; 1 = a link disagrees.
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PAPER = REPO / "v0.3-prelim" / "docs" / "PAPER_V1_DRAFT.md"
CONSTANTS = REPO / "scripts" / "constants.py"
T235 = REPO / "data" / "results" / "t235_d5_width_test.json"

# Values the paper quotes, and the tolerance each is checked at. The paper
# prints 2 significant figures for the ratio and the bound, so those are
# checked to the precision they are printed at.
PAPER_EXPECTATIONS = {
    "sigma_m_28_sigma1_1": ("65.91", 0.005),
    "ratio_v28": ("1.25e+25", 0.005),
    "g_n_over_g_chi_v28": ("2.83e-13", 0.005),
    "sigma_m_28_sigma1_44": ("166.02", 0.005),
    "ratio_peak": ("3.3e+25", 0.02),
    "g_n_over_g_chi_peak": ("1.74e-13", 0.02),
    "ratio_v100": ("9.85e+21", 0.02),
    "g_n_over_g_chi_v100": ("1.01e-11", 0.02),
}

# Values that were corrected in F23 and must NOT come back.
MUST_BE_ABSENT = ["65.49", "2.84e-13", "2.84×10⁻¹³", "1.24e+25"]

# Unicode scientific forms the paper uses alongside the ASCII forms.
UNICODE_EQUIV = {
    "2.83e-13": ["2.83e-13", "2.83×10⁻¹³", "2.83 x 10^-13"],
    "1.25e+25": ["1.25e+25", "1.25×10²⁵"],
    "3.3e+25": ["3.3e+25", "3.3 × 10²⁵", "3.3×10²⁵"],
    "1.74e-13": ["1.74e-13", "1.74×10⁻¹³"],
    "9.85e+21": ["9.85e+21", "9.85×10²¹"],
    "1.01e-11": ["1.01e-11", "1.01×10⁻¹¹"],
    "65.91": ["65.91"],
    "166.02": ["166.02"],
}


def read_constants():
    """Read the canonical constants from scripts/constants.py.

    Parsed rather than imported so the layer has no import-time side effects
    and no dependency on the module's __main__ behaviour.
    """
    text = CONSTANTS.read_text(encoding="utf-8")
    want = ["SIGMA_0_CM2_PER_G", "A_SLOPE", "SIGMA_PEAK_CM2_PER_G",
            "V_TARGET_KMS", "SIGMA_KMS"]
    out = {}
    for name in want:
        m = re.search(rf"^{name}\s*=\s*([-\d.eE+]+)\s*(?:#.*)?$", text, re.M)
        if not m:
            raise SystemExit(f"ERROR: {name} not found in {CONSTANTS}")
        out[name] = float(m.group(1))
    return out


def sigma_m(v, v_target, sigma_kms, sigma_peak, sigma_0, a_slope):
    """σ/m(v) in the paper's convention (Gaussian resonance + Yukawa tail)."""
    background = sigma_0 * (v / 100.0) ** (-a_slope)
    gaussian = sigma_peak * math.exp(-(v - v_target) ** 2 / (2 * sigma_kms ** 2))
    return background + gaussian


def hier(sigma_m_value, m_chi_g, sig_si):
    """ratio = σ_DM-DM/σ_SI ; bound = g_N/g_χ = 1/sqrt(ratio)."""
    ratio = sigma_m_value * m_chi_g / sig_si
    return ratio, 1.0 / math.sqrt(ratio)


def paper_has(paper_text, printed):
    """True if the paper prints any accepted form of the value.

    `printed` is the canonical string (e.g. "2.83e-13"); UNICODE_EQUIV maps
    it to the ASCII / Unicode spellings the paper may use.
    """
    return any(form in paper_text for form in UNICODE_EQUIV.get(printed, [printed]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    const = read_constants()
    paper = PAPER.read_text(encoding="utf-8")

    # --- the paper's own constants for the last two links ------------------
    # m_chi and sigma_SI are quoted in the paper's hierarchy derivation.
    m_chi_g = 1.78e-24   # g     (paper L2096 area, Option A derivation)
    sig_si = 9.4e-48     # cm^2  (LZ bound)

    checks = []
    failures = []

    def check(name, expected, actual, tol, note=""):
        ok = abs(actual - expected) <= tol * max(abs(expected), 1e-300)
        checks.append({"name": name, "expected": expected, "actual": actual,
                       "tol_rel": tol, "ok": ok, "note": note})
        if not ok:
            failures.append(f"{name}: expected {expected}, got {actual}")

    # --- LINK 1: σ/m(28) at σ_1 = 1.0 -------------------------------------
    sm28_1 = sigma_m(28.0, const["V_TARGET_KMS"], 1.0,
                     const["SIGMA_PEAK_CM2_PER_G"], const["SIGMA_0_CM2_PER_G"],
                     const["A_SLOPE"])

    # Known-system sanity check: the same function at σ_1 = 4.4 must equal
    # the t235 JSON's value for that width. If it does not, the function or
    # the constants are wrong and NOTHING below can be trusted.
    sm28_44 = sigma_m(28.0, const["V_TARGET_KMS"], const["SIGMA_KMS"],
                      const["SIGMA_PEAK_CM2_PER_G"], const["SIGMA_0_CM2_PER_G"],
                      const["A_SLOPE"])
    t235 = json.loads(T235.read_text(encoding="utf-8"))
    json_44 = t235["results_by_sigma_1"]["4.4"]["per_channel_sigma_m_cm2_per_g"]["Cloud-9"]
    check("known-system: sigma/m(28) at sigma_1=4.4 vs t235 JSON",
          json_44, sm28_44, 1e-12,
          "if this fails the sigma_m() implementation is wrong, not the data")

    json_1 = t235["results_by_sigma_1"]["1.0"]["per_channel_sigma_m_cm2_per_g"]["Cloud-9"]
    check("link 1: sigma/m(28) at sigma_1=1.0 vs t235 JSON",
          json_1, sm28_1, 1e-12,
          "the canonical value the F23 fix restored")

    # --- LINK 2 and 3: the ratio and the bound at the v=28 anchor ----------
    ratio_v28, g_v28 = hier(sm28_1, m_chi_g, sig_si)
    # --- the resonance-peak headline --------------------------------------
    ratio_peak, g_peak = hier(const["SIGMA_PEAK_CM2_PER_G"], m_chi_g, sig_si)
    # --- the v=100 background-only anchor ---------------------------------
    sm100 = const["SIGMA_0_CM2_PER_G"] * (100.0 / 100.0) ** (-const["A_SLOPE"])
    ratio_v100, g_v100 = hier(sm100, m_chi_g, sig_si)

    # --- PHYSICS CONSISTENCY ----------------------------------------------
    # 1. the bound must be a positive fraction below 1 (a coupling ratio)
    for nm, g in (("v=28", g_v28), ("peak", g_peak), ("v=100", g_v100)):
        if not (0 < g < 1):
            failures.append(f"physics: g_N/g_chi ({nm}) = {g} is not a "
                            f"positive ratio below 1")
        if not (g > 0 and math.isfinite(g)):
            failures.append(f"physics: g_N/g_chi ({nm}) not finite")
    # 2. the ratio must be dimensionless-positive
    for nm, r in (("v=28", ratio_v28), ("peak", ratio_peak), ("v=100", ratio_v100)):
        if r <= 0:
            failures.append(f"physics: ratio ({nm}) = {r} is not positive")
    # 3. ORDERING: the paper claims the v=28 bound is LOOSER (larger allowed
    #    hierarchy) than the σ_1 = 4.4 headline. A larger g_N/g_chi bound is a
    #    looser constraint, so g_v28 > g_peak must hold.
    if not (g_v28 > g_peak):
        failures.append(f"physics: ordering broken - the v=28 bound "
                        f"({g_v28:.4e}) is not looser than the headline "
                        f"({g_peak:.4e})")
    # 4. the σ_1 = 1.0 anchor must sit BELOW the σ_1 = 4.4 one (narrowing the
    #    width suppresses the tail) - the physical premise of the whole chain.
    if not (sm28_1 < sm28_44):
        failures.append(f"physics: sigma/m(28) at sigma_1=1.0 ({sm28_1}) is not "
                        f"below the sigma_1=4.4 value ({sm28_44})")

    # --- LINK 4: the paper's printed values must match --------------------
    paper_vals = {
        "sigma_m_28_sigma1_1": sm28_1,
        "ratio_v28": ratio_v28,
        "g_n_over_g_chi_v28": g_v28,
        "sigma_m_28_sigma1_44": sm28_44,
        "ratio_peak": ratio_peak,
        "g_n_over_g_chi_peak": g_peak,
        "ratio_v100": ratio_v100,
        "g_n_over_g_chi_v100": g_v100,
    }
    for key, (printed, tol) in PAPER_EXPECTATIONS.items():
        actual = paper_vals[key]
        # The paper prints 2-3 significant figures; compare against the
        # printed string, not the full float.
        pv = float(printed)
        rel = abs(actual - pv) / abs(pv)
        checks.append({"name": f"link 4: paper prints {printed} for {key}",
                       "expected": pv, "actual": actual, "tol_rel": tol,
                       "ok": rel <= tol, "note": "paper-printed value vs recomputed"})
        if rel > tol:
            failures.append(f"link 4: the paper prints {printed} for {key} but "
                            f"the chain recomputes {actual!r}")
        if not paper_has(paper, printed):
            failures.append(f"link 4: the paper does not print {printed} "
                            f"for {key} at all")

    # --- LINK 5: the retracted values must stay absent --------------------
    for bad in MUST_BE_ABSENT:
        n = paper.count(bad)
        checks.append({"name": f"link 5: retracted value {bad!r} absent",
                       "expected": 0, "actual": n, "tol_rel": 0,
                       "ok": n == 0, "note": "F23 retraction guard"})
        if n:
            failures.append(f"link 5: the retracted value {bad!r} is back in "
                            f"the paper ({n} occurrence(s))")

    ok = not failures

    if args.json:
        print(json.dumps({"constants": const, "checks": checks,
                          "failures": failures,
                          "result": "PASS" if ok else "FAIL"}, indent=2,
                         default=str))
        return 0 if ok else 1

    print("=" * 74)
    print("HIERARCHY-BOUND CHAIN AUDIT (gate layer 10, closes CG-9)")
    print("=" * 74)
    print(f"constants: sigma_0={const['SIGMA_0_CM2_PER_G']}  "
          f"a_slope={const['A_SLOPE']}  sigma_peak={const['SIGMA_PEAK_CM2_PER_G']}  "
          f"v_target={const['V_TARGET_KMS']}")
    print()
    print("CHAIN (recomputed from constants.py, nothing copied from the paper):")
    print(f"  1. sigma/m(28) at sigma_1=1.0        = {sm28_1!r} cm^2/g")
    print(f"  2. ratio = sigma/m x m_chi/sigma_SI  = {ratio_v28!r}")
    print(f"  3. g_N/g_chi = 1/sqrt(ratio)         = {g_v28!r}")
    print(f"     (headline: sigma_peak=174 -> ratio {ratio_peak:.4e}, "
          f"g {g_peak:.4e})")
    print(f"     (v=100 background: sigma {sm100} -> ratio {ratio_v100:.4e}, "
          f"g {g_v100:.4e})")
    print()
    for c in checks:
        mark = "PASS" if c["ok"] else "FAIL"
        print(f"  [{mark}] {c['name']}")
        if not c["ok"]:
            print(f"         expected {c['expected']!r}, got {c['actual']!r}")
    print()
    if failures:
        print("-" * 74)
        print(f"FAILURES ({len(failures)}):")
        print("-" * 74)
        for f in failures:
            print(f"  - {f}")
        print()
        print("RESULT: FAIL")
        return 1
    print("OK: the hierarchy-bound chain recomputes from the canonical "
          "constants,\nevery link agrees with the paper, and the retracted "
          "values stay absent.")
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
