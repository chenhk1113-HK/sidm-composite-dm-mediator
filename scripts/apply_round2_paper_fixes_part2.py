"""Round 2 paper fixes, part 2 — the instances the post-fix stale-string audit caught.

The audit (per the reviewer-checklist-processor skill) greps for the OLD value
after the fix; these three survived the first pass:

  1. L145  — the "5.2e44 / 6.5e47" strings survive INSIDE my own correction
              note, which is intentional (the note explains what was wrong).
              No change needed; verified here rather than silently ignored.
  2. L958  — still calls the 0.2 cm^2/g value the "velocity-independent
              limit" in the historical note. Per the verified KB
              (docs/papers/verified/2503.13650_horigome_2025.md):
                0.8  = w = 10 km/s velocity-dependent limit   (Eq. 7, Table 1)
                0.2  = decisive CDM-preference threshold      (Abstract)
                       AND the w = 30 km/s velocity-dependent limit (Eq. 13)
                0.04 = w -> infinity velocity-independent limit (Eq. 7, Table 1)
              So the ONLY wrong label is "velocity-independent (w -> inf)".
  3. L2155 — says the 0.2 threshold "assumes a velocity-independent
              cross-section". Per the KB the 0.2 in the Abstract is the
              decisive-preference threshold; the w=30 limit of 0.2 comes from
              Eq. 13. The sentence's INTENT (the comparison is an upper
              bound) is correct; only the label needs fixing.
"""
import pathlib

PAPER = pathlib.Path(
    r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator"
    r"\v0.3-prelim\docs\PAPER_V1_DRAFT.md"
)

txt = PAPER.read_text(encoding="utf-8")
orig = txt
FIXES = []

# ---- L958 historical note: the label only -------------------------------
old = ("v1.6\u2013v1.9 of this paper applied the velocity-independent limit (0.2 cm\u00b2/g) at v=30 km/s, "
       "giving a \"800\u00d7 violation\"")
new = ("v1.6\u2013v1.9 of this paper applied the w = 30 km/s velocity-dependent limit (0.2 cm\u00b2/g, "
       "Eq. 13 of [27]) at v=30 km/s, giving a \"800\u00d7 violation\"")
FIXES.append(("L958 historical label", old, new, 1))

# ---- L2155: the threshold's provenance -----------------------------------
old = ("- Horigome+'s \u03c3/m > 0.2 cm\u00b2/g threshold assumes a **velocity-independent** cross-section")
new = ("- The 0.2 cm\u00b2/g reference used above is Horigome+'s **decisive CDM-preference threshold** "
       "(Abstract), which applies to a velocity-independent cross-section")
FIXES.append(("L2155 threshold provenance", old, new, 1))

# ---- L2157: keep the upper-bound statement, name the right limit --------
old = ("- The factors above use the velocity-independent threshold applied to a velocity-dependent "
       "\u03c3/m(v); this is an **upper bound** on the true tension")
new = ("- The factors above apply the velocity-independent-decision threshold to a velocity-dependent "
       "\u03c3/m(v); this is an **upper bound** on the true tension")
FIXES.append(("L2157 upper-bound statement", old, new, 1))

print("=" * 78)
print("ROUND 2 PAPER FIXES (part 2)")
print("=" * 78)
for name, o, n, exp in FIXES:
    got = txt.count(o)
    assert got == exp, f"{name}: expected {exp}, found {got}"
    print(f"  \u2713 {name}: {got} occurrence(s) matched")
    txt = txt.replace(o, n)

# L145's stale strings are inside an intentional correction note -> verify
assert "5.2\u00d710\u2074\u2074 / 6.5\u00d710\u2074\u2077 dropped the m_\u03c7" in txt, \
    "L145 correction note must remain (it documents the old values)"

# structure preservation
assert txt.count("\n## ") == orig.count("\n## ")
assert txt.count("\n### ") == orig.count("\n### ")
assert txt.count("```") == orig.count("```")

PAPER.write_text(txt, encoding="utf-8")
print()
print(f"  paper: {len(orig)} -> {len(txt)} chars")
print("  ALL PART-2 FIXES APPLIED")
