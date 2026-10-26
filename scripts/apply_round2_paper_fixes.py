"""Round 2 paper-text fixes — 5 confirmed defects from the 5-loop dual review.

Every replacement value is recomputed here BEFORE it is written, and every
replacement asserts its expected hit count. If any assert fails, NOTHING is
written (the script writes only after all asserts pass).

Defects fixed:
  F1  L36/L2153/L2210  Horigome limit mislabelled: 0.2 cm^2/g is the
      "decisive CDM-preference threshold" (Abstract), NOT the w->inf
      velocity-independent UPPER LIMIT (which is 0.04, Eq. 7 Table 1).
  F2  L11  abstract calls the Horigome excess "sigma_eff ... above 0.8 by
      3.6-23.7x"; the paper's own sigma_eff(15) = 0.251 is BELOW 0.8.
      The 3.6-23.7x is sigma/m / 0.8.
  F3  L117  exp[-(15-29.4)^2/(2*3.0^2)] = 9.93e-6, not ~8e-5.
  F4  L143/L144/L145  hierarchy ratios are ~10^22 too large (the m_chi
      factor was dropped) AND the direction claim is backwards.
  F5  L57  the printed v^2-space Breit-Wigner peaks at 1/v_t^2, not 1.
"""
import math
import pathlib
import re

PAPER = pathlib.Path(
    r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator"
    r"\v0.3-prelim\docs\PAPER_V1_DRAFT.md"
)

# ---------------------------------------------------------------- compute
m_chi_g = 1.78e-24      # g      (paper L2096)
sig_SI = 9.4e-48        # cm^2   (paper L2103)
def hier(sigma_m):
    ratio = sigma_m * m_chi_g / sig_SI
    return ratio, 1.0 / math.sqrt(ratio)

r100, g100 = hier(0.052)      # L143's stated anchor: v=100, background only
# L144's anchor: v=28 at sigma_1 = 1.0. The canonical value is 65.91085
# (data/results/t235_d5_width_test.json, sigma_1=1.0 -> Cloud-9). It was
# previously 65.49, which embedded the RETRACTED a_slope=1.0 baseline term --
# fixed as F23 (see report section 17.7).
SIGMA_M_V28_SIGMA1_1 = 65.91085124460028
r28d5, g28d5 = hier(SIGMA_M_V28_SIGMA1_1)
r28can, g28can = hier(174.0)  # headline anchor: sigma_peak = 174 (L38 / L2104-2107)

# sanity asserts on the computed values (these are the paper's own anchors)
assert abs(r28can / 3.295e25 - 1) < 1e-3, "headline ratio must match L2104 (3.3e25)"
assert abs(g28can / 1.742e-13 - 1) < 1e-2, "headline g must match L2107 (1.7e-13)"
assert abs(math.exp(-(15 - 29.4) ** 2 / (2 * 3.0 ** 2)) - 9.9295e-06) < 1e-9
assert abs(1 / 29.4 ** 2 - 0.001156925355) < 1e-9
# the D-5 v=28 bound must be LOOSER than the headline (the paper claims the opposite)
assert g28d5 > g28can, "D-5 v=28 bound must be looser than the headline"

txt = PAPER.read_text(encoding="utf-8")
orig_len = len(txt)

FIXES = []

# ---------------------------------------------------------------- F1
# L36: "against their velocity-independent limit (0.2 cm^2/g, w -> infinity)"
old = ("by 27\u201349\u00d7 at v = 9\u201340 km/s (excluding v=28 where \u03c3/m is resonantly 830\u00d7) "
       "against their velocity-independent limit (0.2 cm\u00b2/g, w \u2192 \u221e)")
new = ("by 27\u201349\u00d7 at v = 9\u201340 km/s (excluding v=28 where \u03c3/m is resonantly 830\u00d7) "
       "against their decisive CDM-preference threshold (0.2 cm\u00b2/g, Abstract)")
FIXES.append(("F1 L36", old, new, 1))

# L2153
old = ("(against the velocity-independent limit of 0.2 cm\u00b2/g, w \u2192 \u221e); 830\u00d7 at v = 28 km/s")
new = ("(against their decisive CDM-preference threshold of 0.2 cm\u00b2/g, Abstract); 830\u00d7 at v = 28 km/s")
FIXES.append(("F1 L2153", old, new, 1))

# L2210
old = "27\u201349\u00d7 at w\u2192\u221e (R88(30) corrected from 10-49\u00d7)"
new = ("27\u201349\u00d7 at their decisive CDM-preference threshold of 0.2 cm\u00b2/g "
       "(R88(30) corrected from 10-49\u00d7)")
FIXES.append(("F1 L2210", old, new, 1))

# ---------------------------------------------------------------- F2
old = ("a physically-derived f_H(r) drives \u03c3_eff at dSph velocities above "
       "Horigome+ 2025's 0.8 cm\u00b2/g limit by 3.6\u201323.7\u00d7")
new = ("a physically-derived f_H(r) drives the microphysical \u03c3/m at dSph velocities above "
       "Horigome+ 2025's 0.8 cm\u00b2/g limit by 3.6\u201323.7\u00d7 "
       "(\u03c3_eff = f_H\u00b2\u00b7\u03c3/m is 0.251 cm\u00b2/g at v = 15, i.e. BELOW that ceiling; "
       "the excess is in \u03c3/m)")
FIXES.append(("F2 L11 abstract", old, new, 1))

# ---------------------------------------------------------------- F3
old = ("exp(-(15-29.4)\u00b2/(2\u00d73.0\u00b2)) \u2248 8\u00d710\u207b\u2075")
new = ("exp(-(15-29.4)\u00b2/(2\u00d73.0\u00b2)) = 1.0\u00d710\u207b\u2075")
FIXES.append(("F3 L117 Gaussian tail", old, new, 1))

# ---------------------------------------------------------------- F4
old = ("- Using \u03c3_DM-DM at v = 100 (background only): ratio \u03c3_DM-DM/\u03c3_SI = 5.2\u00d710\u2074\u2074 "
       "\u2192 g_N/g_\u03c7 < 4.4\u00d710\u207b\u00b2\u00b3")
new = (f"- Using \u03c3_DM-DM at v = 100 (background only, \u03c3/m = 0.052 cm\u00b2/g): "
       f"ratio \u03c3_DM-DM/\u03c3_SI = {r100:.2e} \u2192 g_N/g_\u03c7 < {g100:.2e}")
FIXES.append(("F4 L143 v=100 hierarchy", old, new, 1))

old = ("- Using \u03c3_DM-DM at v = 28 (Cloud-9): ratio \u03c3_DM-DM/\u03c3_SI = 6.5\u00d710\u2074\u2077 "
       "\u2192 g_N/g_\u03c7 < 1.2\u00d710\u207b\u00b2\u2074")
new = (f"- Using \u03c3_DM-DM at v = 28 (Cloud-9, \u03c3/m = {SIGMA_M_V28_SIGMA1_1:.2f} cm\u00b2/g at \u03c3_1 = 1.0): "
       f"ratio \u03c3_DM-DM/\u03c3_SI = {r28d5:.2e} \u2192 g_N/g_\u03c7 < {g28d5:.2e}")
FIXES.append(("F4 L144 v=28 hierarchy", old, new, 1))

old = ("**7.5\u00d710\u207b\u00b9\u00b2 was anchored to \u03c3_DM-DM ~ 1 cm\u00b2/g; under \u03c3_1 = 1.0, the anchor "
       "shifts.**The hierarchy constraint becomes much more restrictive (~10\u207b\u00b2\u2074 instead of "
       "~10\u207b\u00b9\u00b9).")
new = (f"**The 7.5\u00d710\u207b\u00b9\u00b2 value was anchored to \u03c3_DM-DM ~ 1 cm\u00b2/g; under \u03c3_1 = 1.0 the "
       f"anchor shifts to \u03c3/m = {SIGMA_M_V28_SIGMA1_1:.2f} cm\u00b2/g at v = 28.**The hierarchy constraint is "
       f"g_N/g_\u03c7 < {g28d5:.2e} (v = 28) and < {g100:.2e} (v = 100, background only) \u2014 i.e. the "
       f"v = 28 bound is slightly LOOSER than the \u03c3_1 = 4.4 headline "
       f"g_N/g_\u03c7 < {g28can:.2e}, not more restrictive. (Corrected: the previously quoted ratios "
       f"5.2\u00d710\u2074\u2074 / 6.5\u00d710\u2074\u2077 dropped the m_\u03c7 = 1.78\u00d710\u207b\u00b2\u2074 g factor, so "
       f"they were ~10\u00b2\u00b2 too large and the direction of the shift was inverted.)")
FIXES.append(("F4 L145 direction", old, new, 1))

old = ("Both new values are more restrictive than the \u03c3_1 = 4.4 headline by factor 10\u00b9\u00b9-10\u00b9\u00b2.")
new = (f"Both new values are less restrictive than the \u03c3_1 = 4.4 headline "
       f"(g_N/g_\u03c7 < {g28d5:.2e} vs {g28can:.2e} at v = 28; {g100:.2e} at v = 100).")
FIXES.append(("F4 L145 'more restrictive' clause", old, new, 1))

# ---------------------------------------------------------------- F5
old = "BW(v; v_t, \u0393) = (\u0393/2)\u00b2 / [(v\u00b2 \u2212 v_t\u00b2)\u00b2 + (\u0393 \u00b7 v_t / 2)\u00b2]"
new = ("BW(v; v_t, \u0393) = (\u0393 \u00b7 v_t / 2)\u00b2 / [(v\u00b2 \u2212 v_t\u00b2)\u00b2 + (\u0393 \u00b7 v_t / 2)\u00b2] "
       "(unit peak at v = v_t)")
FIXES.append(("F5 L57 BW normalization", old, new, 1))

# ---------------------------------------------------------------- apply
print("=" * 78)
print("ROUND 2 PAPER FIXES — asserting every replacement before writing")
print("=" * 78)
for name, old, new, n_expect in FIXES:
    got = txt.count(old)
    assert got == n_expect, f"{name}: expected {n_expect} occurrence(s), found {got}"
    print(f"  ✓ {name}: {got} occurrence(s) matched")
    txt = txt.replace(old, new)

# structure preservation (skill: verify the doc survived the edit)
_orig = PAPER.read_text(encoding="utf-8")
assert txt.count("\n## ") == _orig.count("\n## "), "h2 heading count changed"
assert txt.count("\n### ") == _orig.count("\n### "), "h3 heading count changed"
assert txt.count("```") == _orig.count("```"), "code-fence count changed"
PAPER.write_text(txt, encoding="utf-8")
print()
print(f"  paper: {orig_len} -> {len(txt)} chars")
print(f"  structure preserved: h2={txt.count(chr(10)+'## ')}, h3={txt.count(chr(10)+'### ')}, "
      f"fences={txt.count('```')}")
print("  ALL FIXES APPLIED")
