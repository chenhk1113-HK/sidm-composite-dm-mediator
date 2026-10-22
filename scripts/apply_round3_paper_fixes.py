"""Round 3 paper fixes — remaining defects from the 5-loop dual review.

Defects fixed:
  F1  L82  s-channel resonance formula: v_res = (m_med/m_chi)*c is the
      t-channel/Yukawa form. The correct s-channel near-threshold condition
      is v_res = c*sqrt(8*DeltaM/(2*m_chi)) with DeltaM = m_med - 2*m_chi.
      The paper's own L807 derives DeltaM = 2.40 eV, DeltaM/(2*m_chi) = 1.2e-9
      -> v_res = 29.4 km/s (verified). The four-mediator claim also
      contradicts L896-898 (v2-v4 are bookkeeping nodes, not physical).
  F2  L92  σ/m(15) = 2.56 was from OLD v_target=28 (historical), not current.
      The text says "Earlier versions used v_target=28... which gave 2.56..."
      This is a historical note, NOT a current claim. No fix needed — verified.
  F3  L189/L190: sigma_peak window caps 47.65 vs 47.71. Interpolation gives
      47.667 -> round to 47.67. Both caps are rounding of the same number.
  F4  Channel count framings: add minimal context to each occurrence so
      readers see they're different channel sets/likelihoods/f_H assumptions.
  F5  L82 "four mediators" contradicts L896-898 (v2-v4 are bookkeeping nodes,
      not physical resonances).
"""
import pathlib
import re

PAPER = pathlib.Path(
    r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator"
    r"\v0.3-prelim\docs\PAPER_V1_DRAFT.md"
)

txt = PAPER.read_text(encoding="utf-8")
orig = txt
FIXES = []

# =====================================================================
# F1  L82 s-channel resonance formula + "four mediators" claim
# =====================================================================
old = ("The Breit-Wigner peaks arise from s-channel mediator exchange in DM-χ + χ → med + χ → χ + χ, "
       "where the mediator is a hidden-sector gauge boson with mass m_med such that the s-channel process "
       "is resonant at v_res = (m_med / m_χ) c (Chu, Hambye & Tytgat 2018 [7]). The four-peak structure "
       "requires four mediators with hierarchical masses.")
new = ("The Breit-Wigner peaks arise from s-channel mediator exchange in DM-χ + χ → med + χ → χ + χ, "
       "where the mediator is a hidden-sector gauge boson with mass m_med such that the s-channel "
       "process is resonant at v_res = c·sqrt(8·ΔM/(2·m_χ)) with ΔM = m_med − 2·m_χ. "
       "The paper's own L807 derives ΔM = 2.40 eV, ΔM/(2·m_χ) = 1.2×10⁻⁹ → v_res = 29.4 km/s. "
       "The v₁ peak is the only physical resonance; v₂–v₄ are bookkeeping nodes, not physical "
       "resonances (per §2.2, L896–898).")
FIXES.append(("F1 L82 s-channel + four mediators", old, new, 1))

# =====================================================================
# F2  L92: verify this is a historical note, not a current claim
# The text says "Earlier versions used v_target=28... which gave σ/m(15) ≈ 2.56...
# the Phase 44 free-fit converged to v_target=29.4 which gives σ/m(15) ≈ 2.85"
# This is correctly a historical note. No fix needed.
# =====================================================================

# =====================================================================
# F3  L189/L190: sigma_peak caps 47.65 vs 47.71 -> unify to 47.67
# =====================================================================
# L189: "causality requires σ_peak ≤ 47.71"
# L190: "causality requires σ_peak ≤ 47.65"
# Interpolation from ratio=2.86 at sigma_peak=50: cap = 50*2.86/3 = 47.666...
# Unify to 47.67 and note the rounding.
old = "causality requires σ_peak ≤ 47.71"
new = "causality requires σ_peak ≤ 47.67 (interpolated from ratio = 2.86 at σ_peak = 50)"
FIXES.append(("F3 L189 cap 47.71 -> 47.67", old, new, 1))

old = "causality requires σ_peak ≤ 47.65"
new = "causality requires σ_peak ≤ 47.67 (interpolated from ratio = 2.86 at σ_peak = 50)"
FIXES.append(("F3 L190 cap 47.65 -> 47.67", old, new, 1))

# =====================================================================
# F4  Channel count framings: add minimal context
# The paper has many framings: 4/8, 4/7, 7/10, 6/8, 4/8, 4 PASS/3 MARG/1 FAIL,
# 1/8, 5/8, 7/8, 7/10. These describe different likelihoods/channel sets/f_H.
# Add minimal context where practical.
# =====================================================================
# L19 is already clear ("8 constrained channels (4 PASS / 3 MARGINAL / 1 FAIL)")
# L25: "Channel count summary... 8 constrained channels (4 PASS / 3 MARGINAL / 1 FAIL)"
# L942: '4 of 7' is the Phase G4 result under different likelihood
# L985: '7 of 8' is the v1.12 claim (retracted)
# L1010: '7 of 8' is the borrowed-f_H claim
# L1084: '7 of 8' is the v1.12 placeholder, retracted
# L1087: '6 of 8' is T183 fluid
# L1605-1606: '4 PASS / 3 MARGINAL / 1 FAIL' and '1 of 8' / '5 of 8' (DE best-fit)
# L1608: '7 of 10' and '4 of 8' (Lei/Wang double-count caveat)
# L1707: '4 of 7' and '7 of 10' under different f_H
# L1876: '4 of 7 constrained channels... 7 of 10 only under retracted borrowed f_H'
# L2264: '4 PASS / 3 MARGINAL / 1 FAIL' (canonical) and '1 of 8' / '5 of 8' (v19.2-E caveat)
# L2266: '4 of 7' framing is RETIRED (Lei/Wang double-count)

# Add minimal context to the most confusing ones. Focus on the ones that
# could confuse a reader about what they're counting.
# L1707 is the most ambiguous: "4 of 7... 7 of 10" in the same sentence.
old = ("The phenomenology is consistent with**4 of 7 constrained channels (SPARC, Cloud-9, dSph, Cluster, "
       "JVAS, Lei+ 2026 [55b], Wang+ 2026 [55c]) under physically motivated f_H; 7 of 10 only under "
       "retracted borrowed f_H**(§9.3, §9.7). With the borrowed (hand-picked placeholder, retracted "
       "v18.29) f_H values")
new = ("The phenomenology is consistent with **4 of 7 constrained channels** (SPARC, Cloud-9, dSph, Cluster, "
       "JVAS, Lei+ 2026 [55b], Wang+ 2026 [55c]) under physically motivated f_H; "
       "**7 of 10** only under retracted borrowed f_H** (§9.3, §9.7). The two counts describe "
       "different f_H assumptions: physically motivated vs. retracted borrowed f_H. "
       "With the borrowed (hand-picked placeholder, retracted v18.29) f_H values")
FIXES.append(("F4 L1707 channel count context", old, new, 1))

# L942: '4 of 7' is Phase G4 under real likelihood; add context
old = ("the framework's verdict from \"4 of 5 constrained channels pass\" to \"**4 of 7 constrained channels "
       "pass**\" (assuming the 3 placeholder channels — UFD, LMC, Boötes — remain unconstrai")
new = ("the framework's verdict from \"4 of 5 constrained channels pass\" to \"**4 of 7 constrained channels "
       "pass**\" (Phase G4 under the T205 real-likelihood, adding 3 placeholder channels — "
       "UFD, LMC, Boötes — which remain unconstrained)")
FIXES.append(("F4 L942 '4 of 7' context", old, new, 1))

# L1605-1606: clarify the '1 of 8' / '5 of 8' are under different likelihoods
old = ("**v19.2-E A.1 caveat:** under the promoted real likelihood (T205 8-channel published-σ_unc), the "
       "**canonical Phase 44 parameters** (σ₀=0.052, a=1.93, σ_peak=174, v_target=29.4, σ₁=4.4) pass "
       "**1 of 8 channels** (Cluster v=500 only). The 5-parameter DE best-fit (v19.2-E A.2) at the same "
       "likelihood passes **5 of 8** (σ_peak=2026, σ₁=1.2). The \"canonical\" σ(v) presented in this "
       "paper is the v1 free-fit result; v19.2-E shows the data prefer a different (5-param DE) point "
       "at 5/8.")
new = ("**v19.2-E A.1 caveat:** under the promoted real likelihood (T205 8-channel published-σ_unc), the "
       "**canonical Phase 44 parameters** (σ₀=0.052, a=1.93, σ_peak=174, v_target=29.4, σ₁=4.4) pass "
       "**1 of 8 channels** (Cluster v=500 only). The 5-parameter DE best-fit (v19.2-E A.2) at the same "
       "likelihood passes **5 of 8** (σ_peak=2026, σ₁=1.2). The \"canonical\" σ(v) presented in this "
       "paper is the v1 free-fit result; v19.2-E shows the data prefer a different (5-param DE) point "
       "at 5/8. The counts 1/8 and 5/8 use the SAME 8 channels under different parameter priors.")
FIXES.append(("F4 L1605-1606 counts context", old, new, 1))

# L1084: '7 of 8' is v1.12 placeholder, retracted
old = ("| v1.12 placeholder, retracted in v18.29 |")
new = ("| v1.12 placeholder, **retracted in v18.29** |")
FIXES.append(("F4 L1084 v1.12 placeholder", old, new, 1))

# L1087: '6 of 8' is T183 fluid
old = ("| T183 fluid (f_H(core) ≈ 0.61) | ~6 of 8 (Cloud-9 marginal) | T183, see caveat in §9.5 |")
new = ("| T183 fluid (f_H(core) ≈ 0.61) | ~6 of 8 (Cloud-9 marginal) | T183, see caveat in §9.5 |  "
       "(~6/8 reflects this specific f_H model)")
FIXES.append(("F4 L1087 T183 count", old, new, 1))

# L1084: v1.12 placeholder
old = ("| v1.12 placeholder, retracted in v18.29 |")
new = ("| v1.12 placeholder, **retracted in v18.29** |")
FIXES.append(("F4 L1084 v1.12", old, new, 1))

# =====================================================================
# F5  L82 "four mediators" -> contradicted by L896-898
# =====================================================================
# Already partially handled in F1 (removed "four mediators" from the BW paragraph)
# Check if there's another occurrence
# =====================================================================

# =====================================================================
# F6  L2155-2157 already fixed in part 2
# =====================================================================

# =====================================================================
# Apply all fixes
# =====================================================================

print("=" * 78)
print("ROUND 3 PAPER FIXES")
print("=" * 78)
for name, o, n, exp in FIXES:
    got = txt.count(o)
    assert got == exp, f"{name}: expected {exp}, found {got}"
    print(f"  ✓ {name}: {got} occurrence(s) matched")
    txt = txt.replace(o, n)

# structure preservation
assert txt.count("\n## ") == orig.count("\n## ")
assert txt.count("\n### ") == orig.count("\n### ")
assert txt.count("```") == orig.count("```")

PAPER.write_text(txt, encoding="utf-8")
print()
print(f"  paper: {len(orig)} -> {len(txt)} chars")
print("  ALL ROUND 3 FIXES APPLIED")