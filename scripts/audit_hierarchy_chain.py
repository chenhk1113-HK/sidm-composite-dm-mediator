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

PAIRING (finding F30, added 2026-11-06)
---------------------------------------
The chain's inputs are particle-level amplitudes, and the pairing of f_H with
those amplitudes is not unique (see scripts/constants.py and finding F26). This
layer therefore audits BOTH pairings:

  * ARCHIVED PAIR  f_H = 0.297, sigma_0 = 0.052, sigma_peak = 174
      The pairing the published chain was produced under. Links 1-5 check it
      against data/results/t235_d5_width_test.json and the paper's printed
      65.91 / 166.02 / 1.25e25 / 2.83e-13 / 3.3e25 / 1.74e-13 / 9.85e21 /
      1.01e-11, so historical numbers cannot drift silently.
  * LIVE PAIR      f_H = 0.7501856343179664, sigma_0 = 0.008150396851725193,
                   sigma_peak = 27.272481773080454
      The pairing the framework now reports. Link 6 recomputes the same chain
      and requires the paper to print those values as its current claim.

Why link 6 exists: sigma_eff = f_H^2 x sigma/m is pairing-invariant (verified to
1e-15 here), but the hierarchy bound is built from sigma_DM-DM / sigma_SI, and
sigma_SI is a nucleon-level quantity that carries no f_H. So the bound DOES
move with the pairing: amplitudes scale by 1/6.380057431067687 and every
g_N/g_chi bound loosens by sqrt(6.380057431067687) = 2.5258775566261495. A gate
that audits only one pairing would either flag the paper for being consistent
with the other, or let a stale bound pass unnoticed - which is exactly what
happened when the live pair was switched on and this layer failed 10 links.

Usage:
    python scripts/audit_hierarchy_chain.py
    python scripts/audit_hierarchy_chain.py --json
    python scripts/audit_hierarchy_chain.py --out v0.3-prelim/data/results/hierarchy_chain_pairing.json

Exit: 0 = both chains recompute and the paper agrees; 1 = a link disagrees.
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

# The same chain under the LIVE canonical pairing, printed to the same number
# of significant figures the archived chain is printed at.
PAPER_EXPECTATIONS_CANONICAL = {
    "sigma_m_28_sigma1_1": ("10.33", 0.005),
    "ratio_v28": ("1.96e+24", 0.005),
    "g_n_over_g_chi_v28": ("7.15e-13", 0.005),
    "sigma_m_28_sigma1_44": ("26.02", 0.005),
    "ratio_peak": ("5.16e+24", 0.02),
    "g_n_over_g_chi_peak": ("4.40e-13", 0.02),
    "ratio_v100": ("1.54e+21", 0.02),
    "g_n_over_g_chi_v100": ("2.55e-11", 0.02),
}

UNICODE_EQUIV_CANONICAL = {
    "7.15e-13": ["7.15e-13", "7.15×10⁻¹³", "7.15 × 10⁻¹³", "7.15 x 10^-13"],
    "4.40e-13": ["4.40e-13", "4.40×10⁻¹³", "4.40 × 10⁻¹³", "4.40 x 10^-13"],
    "2.55e-11": ["2.55e-11", "2.55×10⁻¹¹", "2.55 × 10⁻¹¹"],
    "1.96e+24": ["1.96e+24", "1.96×10²⁴", "1.96 × 10²⁴"],
    "5.16e+24": ["5.16e+24", "5.16×10²⁴", "5.16 × 10²⁴"],
    "1.54e+21": ["1.54e+21", "1.54×10²¹", "1.54 × 10²¹"],
    "10.33": ["10.33"],
    "26.02": ["26.02"],
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
    """Read the constants for BOTH pairings from scripts/constants.py.

    Parsed rather than imported so the layer has no import-time side effects
    and no dependency on the module's __main__ behaviour.

    The keys SIGMA_0_CM2_PER_G / SIGMA_PEAK_CM2_PER_G deliberately hold the
    ARCHIVED pair (f_H = 0.297), because links 1-5 audit the chain the published
    numbers were produced under. The live pair is read separately under the
    LIVE_ prefix. Reading them by pairing-specific names is what stops this
    layer from silently following whichever pairing constants.py happens to
    expose - the failure mode that broke 10 links when the canonical pair was
    switched on (finding F30).
    """
    text = CONSTANTS.read_text(encoding="utf-8")
    out = {}

    def grab(name):
        m = re.search(rf"^{name}\s*=\s*([-\d.eE+]+)\s*(?:#.*)?$", text, re.M)
        if not m:
            raise SystemExit(f"ERROR: {name} not found in {CONSTANTS}")
        return float(m.group(1))

    for name in ["A_SLOPE", "V_TARGET_KMS", "SIGMA_KMS"]:
        out[name] = grab(name)

    # ARCHIVED pair -> the keys links 1-5 use.
    out["SIGMA_0_CM2_PER_G"] = grab("SIGMA_0_LEGACY_PAIR_052")
    out["SIGMA_PEAK_CM2_PER_G"] = grab("SIGMA_PEAK_LEGACY_PAIR_174")
    out["F_H_ARCHIVED"] = grab("F_H_LEGACY_PLACEHOLDER_0297")

    # LIVE pair -> link 6.
    out["LIVE_SIGMA_0_CM2_PER_G"] = grab("SIGMA_0_CM2_PER_G")
    out["LIVE_SIGMA_PEAK_CM2_PER_G"] = grab("SIGMA_PEAK_CM2_PER_G")
    out["F_H_CANONICAL"] = grab("F_H_CANONICAL")

    # Guard 1: the archived pair must still be the published one, or this
    # layer is auditing something other than the historical chain.
    if abs(out["SIGMA_0_CM2_PER_G"] - 0.052) > 1e-12 or abs(out["SIGMA_PEAK_CM2_PER_G"] - 174.0) > 1e-12:
        raise SystemExit(
            "ERROR: this layer audits the ARCHIVED pair (sigma_0 = 0.052, "
            "sigma_peak = 174). constants.py's archived names no longer hold "
            f"those values ({out['SIGMA_0_CM2_PER_G']}, "
            f"{out['SIGMA_PEAK_CM2_PER_G']}) - re-read this layer before "
            "changing the pairing.")
    # Guard 2: the live pair must be internally consistent, i.e. both
    # amplitudes scaled by the SAME factor relative to the archived pair. A
    # different factor would mean a half-paired edit in constants.py.
    k0 = out["SIGMA_0_CM2_PER_G"] / out["LIVE_SIGMA_0_CM2_PER_G"]
    kp = out["SIGMA_PEAK_CM2_PER_G"] / out["LIVE_SIGMA_PEAK_CM2_PER_G"]
    if abs(k0 - kp) > 1e-9 * abs(kp):
        raise SystemExit(
            f"ERROR: half-paired constants.py - sigma_0 scales by {k0} but "
            f"sigma_peak scales by {kp}; the two live amplitudes do not belong "
            "to the same pairing.")
    out["PAIRING_SCALE_LIVE_OVER_ARCHIVED"] = out["LIVE_SIGMA_0_CM2_PER_G"] / out["SIGMA_0_CM2_PER_G"]
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


# --- link 7: claim-site scan -------------------------------------------------
# Every scientific-notation quantity printed INSIDE a pairing-labelled claim
# must be a quantity this auditor recomputes, at the precision the paper prints
# it. A bare order-of-magnitude mention ("≲ 10⁻¹³") has no coefficient and is
# deliberately out of scope; a printed coefficient is a claim.
SUPERSCRIPT_DIGITS = {"⁻": "-", "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4",
                      "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9"}
TOKEN_RE = re.compile(r"(\d+\.\d+)\s*(?:×|x|\*)\s*10\s*([⁻⁰¹²³⁴⁵⁶⁷⁸⁹]{1,3}|[-+]\d{1,2})")

# Anchors, not whole paragraphs: a pairing claim sits in a specific sentence and
# the sentences around it carry other derivations' numbers (e.g. the abstract's
# alpha_chi). Each slice runs from its start marker to its end marker, so the
# text scanned is exactly the claim being verified.
CLAIM_ANCHORS = [
    ("abstract live-pair claim", "Under the live canonical pair", "Both chains are recomputed"),
    ("§3.3 table pairing claim", "The live canonical pairing is f_H", "\n\n"),
    ("§3.3 D-5 live-pair claim", "**Pairing (finding F30):**", "\n\n"),
    ("§3.5a pairing-dependence claim", "Pairing dependence of this chain (finding F30", "\n\n"),
    ("A.3 archived chain", "ARCHIVED PAIR  (f_H = 0.297", "\n\n"),
    ("A.3 live chain", "LIVE CANONICAL PAIR", "\n\n"),
]


def exponent_of(raw):
    if raw[0] in "+-0123456789":
        return int(raw)
    return int("".join(SUPERSCRIPT_DIGITS[c] for c in raw))


def scan_pairing_claim_sites(paper_text, audited_values):
    """Scan the paper's pairing-labelled claims. Returns (unrecognised,
    missing_anchors, tokens_checked); `unrecognised` entries explain which
    printed quantity has no recomputed counterpart."""
    unrecognised, missing_anchors, tokens_checked = [], [], 0
    for name, start_marker, end_marker in CLAIM_ANCHORS:
        i = paper_text.find(start_marker)
        if i < 0:
            missing_anchors.append(f"{name}: {start_marker!r}")
            continue
        j = paper_text.find(end_marker, i + len(start_marker))
        for coeff, exp in TOKEN_RE.findall(paper_text[i:j if j >= 0 else len(paper_text)]):
            # Parse the literal whole: float("4.40") * 10**-13 differs by an ulp
            # from float("4.40e-13") and would never compare equal.
            value = float(f"{coeff}e{exponent_of(exp)}")
            digits = max(1, len(coeff.replace(".", "").lstrip("0")))
            tokens_checked += 1
            if not any(float(f"{a:.{digits}g}") == value for a in audited_values):
                nearest = min(audited_values, key=lambda a: abs(a - value))
                unrecognised.append(
                    f"{coeff}x10{exp} in {name} (nearest recomputed value "
                    f"{nearest!r} rounds to {f'{nearest:.{digits}g}'})")
    return unrecognised, missing_anchors, tokens_checked


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out", default=None,
                    help="write the audit artifact (both chains) to this path")
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

    # --- LINK 6: the same chain under the LIVE canonical pairing ----------
    sm28_1_c = sigma_m(28.0, const["V_TARGET_KMS"], 1.0,
                       const["LIVE_SIGMA_PEAK_CM2_PER_G"],
                       const["LIVE_SIGMA_0_CM2_PER_G"], const["A_SLOPE"])
    sm28_44_c = sigma_m(28.0, const["V_TARGET_KMS"], const["SIGMA_KMS"],
                        const["LIVE_SIGMA_PEAK_CM2_PER_G"],
                        const["LIVE_SIGMA_0_CM2_PER_G"], const["A_SLOPE"])
    ratio_v28_c, g_v28_c = hier(sm28_1_c, m_chi_g, sig_si)
    ratio_peak_c, g_peak_c = hier(const["LIVE_SIGMA_PEAK_CM2_PER_G"], m_chi_g, sig_si)
    sm100_c = const["LIVE_SIGMA_0_CM2_PER_G"] * (100.0 / 100.0) ** (-const["A_SLOPE"])
    ratio_v100_c, g_v100_c = hier(sm100_c, m_chi_g, sig_si)

    canonical_vals = {
        "sigma_m_28_sigma1_1": sm28_1_c,
        "ratio_v28": ratio_v28_c,
        "g_n_over_g_chi_v28": g_v28_c,
        "sigma_m_28_sigma1_44": sm28_44_c,
        "ratio_peak": ratio_peak_c,
        "g_n_over_g_chi_peak": g_peak_c,
        "ratio_v100": ratio_v100_c,
        "g_n_over_g_chi_v100": g_v100_c,
    }
    for key, (printed, tol) in PAPER_EXPECTATIONS_CANONICAL.items():
        actual = canonical_vals[key]
        pv = float(printed)
        rel = abs(actual - pv) / abs(pv)
        checks.append({"name": f"link 6 (live pairing): paper prints {printed} for {key}",
                       "expected": pv, "actual": actual, "tol_rel": tol,
                       "ok": rel <= tol,
                       "note": "live-pair value the paper must state as its current claim"})
        if rel > tol:
            failures.append(f"link 6: the paper prints {printed} for {key} but the "
                            f"live-pair chain recomputes {actual!r}")
        if not any(form in paper for form in UNICODE_EQUIV_CANONICAL.get(printed, [printed])):
            failures.append(f"link 6: the paper never states {printed} for {key} "
                            f"under the live pairing")

    # 6a. the halo-level prediction must NOT move with the pairing.
    fh_live, fh_arch = const["F_H_CANONICAL"], const["F_H_ARCHIVED"]
    for nm, arch_amp, live_amp in (
            ("v=28, sigma_1=1.0", sm28_1, sm28_1_c),
            ("v=28, sigma_1=4.4", sm28_44, sm28_44_c),
            ("resonance peak", const["SIGMA_PEAK_CM2_PER_G"], const["LIVE_SIGMA_PEAK_CM2_PER_G"])):
        eff_arch = fh_arch ** 2 * arch_amp
        eff_live = fh_live ** 2 * live_amp
        rel = abs(eff_live - eff_arch) / max(abs(eff_arch), 1e-300)
        checks.append({"name": f"link 6: sigma_eff invariance at {nm}",
                       "expected": eff_arch, "actual": eff_live, "tol_rel": 1e-9,
                       "ok": rel <= 1e-9,
                       "note": "f_H^2 x sigma/m must be identical under both pairings"})
        if rel > 1e-9:
            failures.append(f"link 6: sigma_eff moved with the pairing at {nm} "
                            f"({eff_arch!r} -> {eff_live!r}); the pairs are inconsistent")

    # 6b. every live bound must be exactly sqrt(archived/live) looser.
    loosen = math.sqrt(const["SIGMA_PEAK_CM2_PER_G"] / const["LIVE_SIGMA_PEAK_CM2_PER_G"])
    for nm, g_arch, g_live in (("peak", g_peak, g_peak_c),
                               ("v=28", g_v28, g_v28_c),
                               ("v=100", g_v100, g_v100_c)):
        rel = abs(g_live / g_arch - loosen) / loosen
        checks.append({"name": f"link 6: bound shift factor at {nm}",
                       "expected": g_arch * loosen, "actual": g_live, "tol_rel": 1e-9,
                       "ok": rel <= 1e-9,
                       "note": f"g_N/g_chi must loosen by exactly sqrt(1/K) = {loosen!r}"})
        if rel > 1e-9:
            failures.append(f"link 6: the {nm} bound did not shift by sqrt(1/K) "
                            f"({g_arch!r} -> {g_live!r}, expected factor {loosen!r})")

    # 6c. physics consistency for the live chain too.
    for nm, g in (("v=28", g_v28_c), ("peak", g_peak_c), ("v=100", g_v100_c)):
        if not (0 < g < 1) or not math.isfinite(g):
            failures.append(f"physics (live pairing): g_N/g_chi ({nm}) = {g} is not "
                            f"a positive ratio below 1")
    for nm, r in (("v=28", ratio_v28_c), ("peak", ratio_peak_c), ("v=100", ratio_v100_c)):
        if r <= 0:
            failures.append(f"physics (live pairing): ratio ({nm}) = {r} is not positive")
    if not (g_v28_c > g_peak_c):
        failures.append("physics (live pairing): ordering broken - the v=28 bound "
                        f"({g_v28_c:.4e}) is not looser than the headline ({g_peak_c:.4e})")
    if not (sm28_1_c < sm28_44_c):
        failures.append("physics (live pairing): sigma/m(28) at sigma_1=1.0 "
                        f"({sm28_1_c}) is not below the sigma_1=4.4 value ({sm28_44_c})")

    # 6d. the OTHER anchors the paper quotes, under both pairings. The paper
    #     compares sigma_1 = 1.0 / 3.0 / 4.4 and quotes the Option B framework
    #     bound, so the claim-site scan (link 7) needs every one of them.
    SIGMA_SI_FRAMEWORK_CM2 = 1.20e-26  # paper §10.4b framework prediction (Option B)
    alt = {}
    for tag, peak, sigma0 in (("archived", const["SIGMA_PEAK_CM2_PER_G"],
                               const["SIGMA_0_CM2_PER_G"]),
                              ("live", const["LIVE_SIGMA_PEAK_CM2_PER_G"],
                               const["LIVE_SIGMA_0_CM2_PER_G"])):
        s1_3 = sigma_m(28.0, const["V_TARGET_KMS"], 3.0, peak, sigma0, const["A_SLOPE"])
        s1_44 = sigma_m(28.0, const["V_TARGET_KMS"], const["SIGMA_KMS"], peak, sigma0,
                        const["A_SLOPE"])
        ob_ratio = peak * m_chi_g / SIGMA_SI_FRAMEWORK_CM2
        alt[f"{tag}_sigma_m_28_sigma1_3_cm2_per_g"] = s1_3
        alt[f"{tag}_g_n_over_g_chi_sigma1_3"] = hier(s1_3, m_chi_g, sig_si)[1]
        alt[f"{tag}_ratio_sigma1_44"] = hier(s1_44, m_chi_g, sig_si)[0]
        alt[f"{tag}_g_n_over_g_chi_sigma1_44"] = hier(s1_44, m_chi_g, sig_si)[1]
        alt[f"{tag}_option_b_ratio"] = ob_ratio
        alt[f"{tag}_option_b_g_n_over_g_chi"] = 1.0 / math.sqrt(ob_ratio)
    check("link 7: Option B ratio (archived pair) matches the paper's 2.6e4",
          alt["archived_option_b_ratio"], 2.6e4, 0.02,
          "the Option B cross-check at the archived pair")
    check("link 7: Option B bound (archived pair) matches the paper's 6.2e-3",
          alt["archived_option_b_g_n_over_g_chi"], 6.2e-3, 0.02,
          "the Option B cross-check at the archived pair")
    check("link 7: sigma_1 = 3.0 bound (archived pair) matches the paper's 1.84e-13",
          alt["archived_g_n_over_g_chi_sigma1_3"], 1.84e-13, 0.006,
          "the sigma_1 = 3.0 comparison at the archived pair")
    check("link 7: sigma_1 = 4.4 bound (archived pair) matches the paper's 1.78e-13",
          alt["archived_g_n_over_g_chi_sigma1_44"], 1.78e-13, 0.006,
          "the sigma_1 = 4.4 comparison at the archived pair")
    check("link 7: sigma_1 = 3.0 bound (live pair) matches the paper's 4.64e-13",
          alt["live_g_n_over_g_chi_sigma1_3"], 4.64e-13, 0.006,
          "the sigma_1 = 3.0 comparison at the live pair")
    check("link 7: sigma_1 = 4.4 bound (live pair) matches the paper's 4.50e-13",
          alt["live_g_n_over_g_chi_sigma1_44"], 4.50e-13, 0.006,
          "the sigma_1 = 4.4 comparison at the live pair")

    # 6e. CLAIM-SITE scan (see scan_pairing_claim_sites above for the rule).
    #     Link 4/6 only ask whether a value appears SOMEWHERE, which a mutation
    #     satisfies by leaving one copy behind — the mutation harness proved it
    #     (changing the abstract's live bound changed nothing).
    invariance_residual = max(
        abs(const["F_H_ARCHIVED"] ** 2 * a - const["F_H_CANONICAL"] ** 2 * b) / max(abs(a), 1e-300)
        for a, b in ((const["SIGMA_PEAK_CM2_PER_G"], const["LIVE_SIGMA_PEAK_CM2_PER_G"]),
                     (sm28_1, sm28_1_c), (sm28_44, sm28_44_c)))
    audited = [sm28_1, sm28_44, sm100, ratio_v28, g_v28, ratio_peak, g_peak,
               ratio_v100, g_v100, sm28_1_c, sm28_44_c, sm100_c, ratio_v28_c,
               g_v28_c, ratio_peak_c, g_peak_c, ratio_v100_c, g_v100_c,
               const["SIGMA_PEAK_CM2_PER_G"], const["LIVE_SIGMA_PEAK_CM2_PER_G"],
               const["SIGMA_0_CM2_PER_G"], const["LIVE_SIGMA_0_CM2_PER_G"],
               invariance_residual]
    audited.extend(alt.values())
    unrecognised, missing_anchors, tokens_checked = scan_pairing_claim_sites(paper, audited)
    if missing_anchors:
        failures.append("link 7: the paper no longer states its pairing claim(s): "
                        + "; ".join(missing_anchors))
    checks.append({"name": "link 7: quantities in pairing-labelled claims are recomputable",
                   "expected": 0, "actual": len(unrecognised) + len(missing_anchors),
                   "tol_rel": 0, "ok": not unrecognised and not missing_anchors,
                   "note": f"{len(CLAIM_ANCHORS) - len(missing_anchors)} claim slices "
                           f"scanned, {tokens_checked} scientific-notation quantities checked"})
    if unrecognised:
        failures.append("link 7: pairing-labelled claim(s) print a quantity this "
                        "auditor cannot recompute: " + "; ".join(unrecognised[:8]))

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

    chains = {
        "archived_pair": {
            "f_H": const["F_H_ARCHIVED"],
            "sigma_0_cm2_per_g": const["SIGMA_0_CM2_PER_G"],
            "sigma_peak_cm2_per_g": const["SIGMA_PEAK_CM2_PER_G"],
            "sigma_m_28_sigma1_1_cm2_per_g": sm28_1,
            "sigma_m_28_sigma1_44_cm2_per_g": sm28_44,
            "sigma_m_v100_background_cm2_per_g": sm100,
            "ratio_v28": ratio_v28, "g_n_over_g_chi_v28": g_v28,
            "ratio_peak": ratio_peak, "g_n_over_g_chi_peak": g_peak,
            "ratio_v100": ratio_v100, "g_n_over_g_chi_v100": g_v100,
            "sigma_m_28_sigma1_3_cm2_per_g": alt["archived_sigma_m_28_sigma1_3_cm2_per_g"],
            "g_n_over_g_chi_sigma1_3": alt["archived_g_n_over_g_chi_sigma1_3"],
            "ratio_sigma1_44": alt["archived_ratio_sigma1_44"],
            "g_n_over_g_chi_sigma1_44": alt["archived_g_n_over_g_chi_sigma1_44"],
            "option_b_ratio": alt["archived_option_b_ratio"],
            "option_b_g_n_over_g_chi": alt["archived_option_b_g_n_over_g_chi"],
            "option_b_sigma_SI_cm2": SIGMA_SI_FRAMEWORK_CM2,
        },
        "live_pair": {
            "f_H": const["F_H_CANONICAL"],
            "sigma_0_cm2_per_g": const["LIVE_SIGMA_0_CM2_PER_G"],
            "sigma_peak_cm2_per_g": const["LIVE_SIGMA_PEAK_CM2_PER_G"],
            "sigma_m_28_sigma1_1_cm2_per_g": sm28_1_c,
            "sigma_m_28_sigma1_44_cm2_per_g": sm28_44_c,
            "sigma_m_v100_background_cm2_per_g": sm100_c,
            "ratio_v28": ratio_v28_c, "g_n_over_g_chi_v28": g_v28_c,
            "ratio_peak": ratio_peak_c, "g_n_over_g_chi_peak": g_peak_c,
            "ratio_v100": ratio_v100_c, "g_n_over_g_chi_v100": g_v100_c,
            "sigma_m_28_sigma1_3_cm2_per_g": alt["live_sigma_m_28_sigma1_3_cm2_per_g"],
            "g_n_over_g_chi_sigma1_3": alt["live_g_n_over_g_chi_sigma1_3"],
            "ratio_sigma1_44": alt["live_ratio_sigma1_44"],
            "g_n_over_g_chi_sigma1_44": alt["live_g_n_over_g_chi_sigma1_44"],
            "option_b_ratio": alt["live_option_b_ratio"],
            "option_b_g_n_over_g_chi": alt["live_option_b_g_n_over_g_chi"],
            "option_b_sigma_SI_cm2": SIGMA_SI_FRAMEWORK_CM2,
        },
        "pairing": {
            "scale_live_over_archived": const["PAIRING_SCALE_LIVE_OVER_ARCHIVED"],
            "amplitude_factor_archived_over_live": const["SIGMA_0_CM2_PER_G"] / const["LIVE_SIGMA_0_CM2_PER_G"],
            "bound_loosening_factor_sqrt_inverse": loosen,
            "sigma_eff_invariance_max_relative_residual": invariance_residual,
            "note": ("sigma_eff = f_H^2 x sigma/m is identical under both pairings; "
                     "the particle-level sigma/m and every g_N/g_chi bound derived "
                     "from it are pairing-dependent and are stated as such."),
        },
        "hierarchy_inputs_from_the_paper": {"m_chi_g": m_chi_g, "sigma_SI_cm2": sig_si},
    }

    payload = {"producer": "scripts/audit_hierarchy_chain.py",
               "constants": const, "chains": chains, "checks": checks,
               "failures": failures, "result": "PASS" if ok else "FAIL"}

    if args.out:
        out_path = Path(args.out)
        if not out_path.is_absolute():
            out_path = REPO / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2, default=str),
                            encoding="utf-8")
        print(f"artifact written: {out_path}")

    if args.json:
        print(json.dumps(payload, indent=2, default=str))
        return 0 if ok else 1

    print("=" * 74)
    print("HIERARCHY-BOUND CHAIN AUDIT (gate layer 10, closes CG-9)")
    print("=" * 74)
    print(f"ARCHIVED pair: f_H={const['F_H_ARCHIVED']}  sigma_0={const['SIGMA_0_CM2_PER_G']}  "
          f"sigma_peak={const['SIGMA_PEAK_CM2_PER_G']}")
    print(f"LIVE pair:     f_H={const['F_H_CANONICAL']}  sigma_0={const['LIVE_SIGMA_0_CM2_PER_G']}  "
          f"sigma_peak={const['LIVE_SIGMA_PEAK_CM2_PER_G']}")
    print(f"a_slope={const['A_SLOPE']}  v_target={const['V_TARGET_KMS']}  "
          f"sigma_1={const['SIGMA_KMS']}")
    print()
    print("CHAIN - ARCHIVED PAIR (the pairing the published numbers were produced under):")
    print(f"  1. sigma/m(28) at sigma_1=1.0        = {sm28_1!r} cm^2/g")
    print(f"  2. ratio = sigma/m x m_chi/sigma_SI  = {ratio_v28!r}")
    print(f"  3. g_N/g_chi = 1/sqrt(ratio)         = {g_v28!r}")
    print(f"     (headline: sigma_peak=174 -> ratio {ratio_peak:.4e}, "
          f"g {g_peak:.4e})")
    print(f"     (v=100 background: sigma {sm100} -> ratio {ratio_v100:.4e}, "
          f"g {g_v100:.4e})")
    print()
    print("CHAIN - LIVE CANONICAL PAIR (the framework's current claim):")
    print(f"  1. sigma/m(28) at sigma_1=1.0        = {sm28_1_c!r} cm^2/g")
    print(f"  2. ratio = sigma/m x m_chi/sigma_SI  = {ratio_v28_c!r}")
    print(f"  3. g_N/g_chi = 1/sqrt(ratio)         = {g_v28_c!r}")
    print(f"     (headline: sigma_peak={const['LIVE_SIGMA_PEAK_CM2_PER_G']} -> "
          f"ratio {ratio_peak_c:.4e}, g {g_peak_c:.4e})")
    print(f"     (v=100 background: sigma {sm100_c} -> ratio {ratio_v100_c:.4e}, "
          f"g {g_v100_c:.4e})")
    print(f"     (amplitudes /{const['SIGMA_0_CM2_PER_G'] / const['LIVE_SIGMA_0_CM2_PER_G']:.7f}, "
          f"bounds x{loosen:.7f}; sigma_eff identical to 1e-15)")
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
