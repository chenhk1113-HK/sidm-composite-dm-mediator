"""Round 3 paper fixes — remaining defects from the 5-loop dual review.
Each fix verifies the old string's count before replacement."""
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
# The text correctly says "Earlier versions used v_target=28... which gave 2.56...
# the Phase 44 free-fit converged to v_target=29.4 which gives 2.85"
# This is correctly a historical note. No fix needed.
# =====================================================================

# =====================================================================
# F3  L189/L190: sigma_peak caps 47.71 vs 47.65 -> unify to 47.67
# =====================================================================
# L189: "causality requires σ_peak ≤ 47.71"
# L190: "causality requires σ_peak ≤ 47.65"
# Interpolation: K = 50*2.86 = 143, cap = 143/3 = 47.667 -> 47.67
old = "causality requires σ_peak ≤ 47.71"
new = "causality requires σ_peak ≤ 47.67 (interpolated from ratio = 2.86 at σ_peak = 50)"
FIXES.append(("F3 L189 cap 47.71 -> 47.67", old, new, 1))

old = "causality requires σ_peak ≤ 47.65"
new = "causality requires σ_peak ≤ 47.67 (interpolated from ratio = 2.86 at σ_peak = 50)"
FIXES.append(("F3 L190 cap 47.65 -> 47.67", old, new, 1))

# =====================================================================
# F4  Channel count framings: add minimal context
# =====================================================================
# L1707: "4 of 7 ... 7 of 10" -> add "different f_H assumptions" clarification
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

# L942: '4 of 7' is Phase G4 under real likelihood
old = ("the framework's verdict from \"4 of 5 constrained channels pass\" to \"**4 of 7 constrained channels "
       "pass**\" (assuming the 3 placeholder channels — UFD, LMC, Boötes — remain unconstrai")
new = ("the framework's verdict from \"4 of 5 constrained channels pass\" to \"**4 of 7 constrained channels "
       "pass**\" (Phase G4 under the T205 real-likelihood, adding 3 placeholder channels — "
       "UFD, LMC, Boötes — which remain unconstrained)")
FIXES.append(("F4 L942 '4 of 7' context", old, new, 1))

# L1605-1606: clarify the '1 of 8' / '5 of 8' are under different priors
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

# L1084: v1.12 placeholder - already bolded in Round 2 part 2, verify
# "v1.12 placeholder, **retracted in v18.29**" - already bolded, skip

# L1087: T183 count context
old = ("| T183 fluid (f_H(core) ≈ 0.61) | ~6 of 8 (Cloud-9 marginal) | T183, see caveat in §9.5 |")
new = ("| T183 fluid (f_H(core) ≈ 0.61) | ~6 of 8 (Cloud-9 marginal) | T183, see caveat in §9.5 |  "
       "(~6/8 reflects this specific f_H model)")
FIXES.append(("F4 L1087 T183 count", old, new, 1))

# L1084: v1.12 placeholder already bolded in part 2, verify
# "| Borrowed (hand-picked 0.85/0.30/0.10) | 7 of 8 | v1.12 placeholder, **retracted in v18.29** |" - OK

# =====================================================================
# F5  L82 "four mediators" already handled in F1 (removed from the sentence)
# =====================================================================

# =====================================================================
# F6  L2155-2157 already fixed in part 2, verify
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