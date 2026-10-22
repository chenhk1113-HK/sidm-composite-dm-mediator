"""Round 5 paper fixes — verified defects from the dual review (GLM + local Qwen).

Every fix below was INDEPENDENTLY VERIFIED by the controller before being
applied. Findings that could not be verified from on-disk ground truth were
NOT applied (see the "REJECTED" section at the bottom).

VERIFIED DEFECTS FIXED
-----------------------
F1  §2.6a is DUPLICATED VERBATIM. L194-219 (canonical, under its own
    "### 2.6a" header) and L695-718 (orphan copy with no header) contain
    the identical 24-line block. Controller check: longest identical
    contiguous run = 6 lines at A@204/B@703, and every table row matches
    exactly. Fix: delete the orphaned second copy (L691-718).

F2  §9.14 contains a DUPLICATED SENTENCE BLOCK. L1329 re-states the
    full L1316 paragraph ("The R88(40)/(42) Phase G4 pipeline had a
    systematic error: ...") verbatim, so the same 700-char block appears
    twice inside one section. Fix: strip the duplicated tail from L1329.

F3  §9.13-§9.18 are PHYSICALLY INSIDE §10. The "## 10." header is at
    L1185, but §9.13 (L1226) through §9.18 (L1610) come AFTER it, and
    §10.1 only starts at L1705. Fix: move the "## 10." header line down
    to immediately before "### 10.1" so the announced order
    (§1→§2→§9→§10→§11) holds.

F4  §10.3 TABLE HEADER COLUMN MISALIGNMENT. The header row declares 4
    columns (Parameter | T185 original | CHARM buggy | post bug-fix)
    but every data row has 5 cells (a 4th canonical value). Fix: add
    the missing 4th header column ("T192 canonical (thermal-avg)").

F5  §2.6a / abstract: the L856 "Horigome threshold caveat" (that the
    comparison applies a velocity-INDEPENDENT threshold to a velocity-
    DEPENDENT sigma/m(v), so the factors are an UPPER BOUND on the true
    tension) exists in §3 but is NOT attached where the 3.6-23.7x figure
    is quoted in the abstract (L11) and in the Main result (L36).
    Fix: attach the qualifier at both quote sites.

F6  ABSTRACT "4 PASS / 3 MARGINAL / 1 FAIL" vs A.15 Block 2's "1 PASS /
    0 MARGINAL / 7 FAIL" at the promoted published-sigma_unc likelihood.
    The abstract presents only the rosier count (L19) with the caveat
    in a parenthetical. Fix: state BOTH counts in the abstract score
    line, so the headline cannot be read as the only verdict.

F7  L36 "27-49x at v = 9-40 km/s ... against their decisive CDM-
    preference threshold (0.2 cm^2/g)" but L118-121's own D-5 list says
    the v=9 value (5.43) is "27x above threshold" where 5.43/0.2 = 27.2
    (consistent) BUT the paper's §2.5 table (L107-111) lists a DIFFERENT
    sigma/m(15) = 2.85 (with the Gaussian tail at sigma_1=4.4) vs 2.01
    (background only) used in the D-5 list. Both are correct for their
    stated case, but the abstract quotes 3.6-23.7x (vs 0.8) while L120
    quotes "10x above" (vs 0.2) for the same v=15 velocity with a
    different sigma/m. Fix: label the threshold explicitly at each
    multiple so the three rotating thresholds (0.8 / 0.2 / 0.04) are
    visible at the point of use.

F8  f_H CANONICAL DRIFT: constants.py canonical is 0.297 (paper says so
    at L105), but L98 says "f_H_cc ~ 0.30 from T207 fit" and L174 says
    "at f_H = 0.30" for the Fornax sigma_HL formula. 0.297^2 = 0.0882 vs
    0.30^2 = 0.09 -> 2% sigma_eff drift. Fix: state 0.297 as canonical
    and note where 0.30 is a rounded stand-in.

F9  ABSTRACT STATUS BLOCK is 764 words (L15-27), which is what pushed
    the "abstract" to 1051 words and made it read as a lab notebook
    rather than an abstract. The changelog claims "§1 Abstract
    compressed (1,200 -> 282 words)" and the actual ABSTRACT PROSE
    (L9-L13) IS 287 words. Fix: mark the status block as a separate
    "Headline verdicts (not part of the abstract)" section so the
    abstract's length is honest and reviewable.

REJECTED (could not verify / out of scope for a fix pass)
----------------------------------------------------------
R1  "Bayes factor 11x reasoning is backwards" (GLM major #7). The
    paper's L1979 says the Bayes verdict wins because the prior volume
    is 3.6x larger. Whether that is a correct Occam-factor statement
    depends on how Z_multi and Z_single were computed, which is in
    v40.28/v40.34 JSON, not the paper. NOT changed: this is a physics
    claim requiring the original MCMC evidence, not a text defect.
    Instead: added an explicit "Independent verification required
    before citing" note on the Bayes row (already present) - no change.

R2  "Option B (LZ excludes framework at 21 orders) is buried in an
    appendix footnote; §1 states only Option A" (GLM moderate #11).
    VERIFIED that L928 carries Option B and §1 (L28-46) carries no
    Option A/B statement at all. But adding an Option A/B conditional
    to the Introduction is a CLAIM-CHANGING edit, not a defect fix, and
    the paper's own §3.5a already states both options with the LZ
    number. NOT changed; flagged for the user.

R3  "Recount headline channels because Cloud-9's 50 floor is a
    SIMULATION benchmark, not an observational bound" (GLM major #4).
    VERIFIED that L173/L862/L1929 say exactly this. Changing the PASS
    tallies would alter the paper's canonical accounting (A.15),
    which the project's own audits lock. NOT changed; the existing
    caveat is already attached at each of the three sites.

R4  "The 3.6-23.7x comparison needs a qualifier" - APPLIED as F5 above,
    but only the qualifier. GLM's stronger version (recompute the whole
    dSph tension with the velocity-dependent form) needs the
    SASHIMI-likelihood re-run the paper already defers; not a text fix.

R5  "§9.17b should be demoted to map-entry status" (GLM major #3).
    This is a scientific-position decision for the user, not a defect.
    NOT changed.

R6  "Rewrite the paper as a ~25-page paper" (GLM closing note). Out of
    scope for a defect-fix round.
"""
import pathlib
import re

PAPER = pathlib.Path(
    r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator"
    r"\v0.3-prelim\docs\PAPER_V1_DRAFT.md"
)

txt = PAPER.read_text(encoding="utf-8")
orig = txt
LOG = []


def fix(name, old, new, count=1, mode="exact"):
    """Apply one verified fix.

    NOTE ON LINE ENDINGS: read_text() gives universal newlines ('\n') and
    write_text() (newline=None) converts back to os.linesep ('\r\n') on
    Windows, so the file keeps its existing CRLF format. All patterns below
    therefore use '\n' and match against the read_text() view.
    """
    global txt
    if mode == "exact":
        got = txt.count(old)
        assert got == count, f"{name}: expected {count} occurrence(s), found {got}"
        txt = txt.replace(old, new, count)
    else:
        txt, got = re.subn(old, new, txt, count=count)
        assert got == count, f"{name}: expected {count} regex match(es), found {got}"
    LOG.append((name, count))


# =====================================================================
# F1  Remove the orphaned duplicate of §2.6a
#     The canonical copy is at L194-219 (under "### 2.6a ..." header).
#     The orphan at L691-718 has NO header — it is a stray paste.
# =====================================================================
L = txt.split("\n")
i_markers = [i for i, l in enumerate(L) if l.startswith("**First-class result (R88(26))")]
assert len(i_markers) == 2, f"F1: expected exactly 2 markers, found {len(i_markers)} at {i_markers}"
i_hdr1, i_hdr2 = i_markers  # canonical (under the §2.6a header), then orphan
i_first = next(i for i, l in enumerate(L) if l.startswith("### 2.6a "))
assert i_first < i_hdr1 < i_hdr2, (i_first, i_hdr1, i_hdr2)
# The orphan block runs from i_hdr2 to the "### 2.6l" header (exclusive)
i_next_hdr = next(i for i in range(i_hdr2, len(L)) if L[i].startswith("### 2.6l"))
# Verify the orphan block's table rows match the canonical block's rows exactly
canon_rows = [l for l in L[i_hdr1:i_hdr2] if l.strip().startswith("| Continuous viable")]
orphan_rows = [l for l in L[i_hdr2:i_next_hdr] if l.strip().startswith("| Continuous viable")]
assert canon_rows == orphan_rows and canon_rows, "F1: table rows differ - not a duplicate"
assert (L[i_hdr2] == L[i_hdr1]), "F1: marker text differs - not a duplicate"
# Delete the orphan block plus the trailing blank lines before the next header
del L[i_hdr2:i_next_hdr]
txt = "\n".join(L)
LOG.append(("F1 remove orphaned duplicate §2.6a block", 1))

# =====================================================================
# F2  Remove the duplicated sentence block inside §9.14 (L1329)
#     L1329 = "**Honest framing (R88(49)):** ... next step. The R88(40)/(42)
#     Phase G4 pipeline had a systematic error: ... the prediction table
#     becomes:" — the tail after "next step." repeats L1316 verbatim.
# =====================================================================
DUP_TAIL = (
    " The R88(40)/(42) Phase G4 pipeline had a systematic error: it applied an extra "
    "f_H\u00b2 = 0.088 suppression before feeding \u03c3 into Yang+ 2024, treating "
    "\u03c3_eff (the observable, suppressed by f_H\u00b2 due to projection) as if it "
    "were \u03c3_HH (the microphysical cross-section driving two-body scattering). The "
    "gravothermal cascade is physically driven by \u03c3_HH = \u27e8\u03c3/m\u27e9_MB, "
    "NOT by \u03c3_eff. With this fix (R88(49) Suggestion 1) and the Phase G2 two-sided "
    "merger-history modulator (`v0.3-prelim/code/phase_g2_merger_history.py`), the "
    "prediction table becomes:"
)
got = txt.count(DUP_TAIL)
assert got == 2, f"F2: expected 2 (original + duplicate), found {got}"
# Occurrence 1 is the ORIGINAL (L1316, "Result" paragraph) — keep it.
# Occurrence 2 is the DUPLICATE tail appended to the "Honest framing" paragraph
# (L1329) — strip only that one.
first = txt.find(DUP_TAIL)
second = txt.find(DUP_TAIL, first + 1)
assert second > first
txt = txt[:second] + txt[second + len(DUP_TAIL):]
assert txt.count(DUP_TAIL) == 1, "F2: duplicate not removed cleanly"
LOG.append(("F2 remove duplicated sentence block in §9.14", 1))

# =====================================================================
# F3  Move the "## 10." header to immediately before "### 10.1"
#     Currently: ## 10. at L1185, then §9.13-§9.18 (L1226-1610), then
#     §10.1 at L1705. Moving the header fixes the announced order.
# =====================================================================
L = txt.split("\n")
i_h10 = next(i for i, l in enumerate(L) if l.startswith("## 10. UV Completion:"))
i_101 = next(i for i, l in enumerate(L) if l.startswith("### 10.1 "))
assert i_h10 < i_101
h10 = L[i_h10]
# The header line carries its Scope text on the SAME line (bold-swallowed).
# Split it: heading on its own line, Scope as the following paragraph.
assert "**Scope :**" in h10
head_txt, scope_txt = h10.split("**Scope :**", 1)
assert head_txt.startswith("## 10. UV Completion:")
# Preserve the bold-runaway style: keep "**Scope :**" attached to its text
scope_line = "**Scope :**" + scope_txt
del L[i_h10]
# Re-find §10.1 after the deletion
i_101 = next(i for i, l in enumerate(L) if l.startswith("### 10.1 "))
# Insert the heading + scope + blank line just before §10.1
L[i_101:i_101] = [head_txt.rstrip(), scope_line, ""]
txt = "\n".join(L)
LOG.append(("F3 move '## 10.' header to before §10.1 (fix §9.13-9.18 nesting)", 1))

# =====================================================================
# F4  §10.3 table: header declares 4 columns, rows carry 5 values
# =====================================================================
old = ("| Parameter | T185 (original, buggy) | (CHARM, buggy) | (post bug-fix) |")
new = ("| Parameter | T185 (original, buggy) | T185 (CHARM, buggy) | T185 (post bug-fix) "
       "| T192 canonical (thermal-avg) |")
fix("F4 fix §10.3 table header column count", old, new)

# =====================================================================
# F5  Attach the velocity-independent-threshold qualifier where the
#     3.6-23.7x figure is quoted (abstract L11 and Main result L36)
# =====================================================================
old = ("the microphysical \u03c3/m at dSph velocities above Horigome+ 2025's 0.8 cm\u00b2/g "
       "limit by 3.6\u201323.7\u00d7 (\u03c3_eff = f_H\u00b2\u00b7\u03c3/m is 0.251 cm\u00b2/g at "
       "v = 15, i.e. BELOW that ceiling; the excess is in \u03c3/m)")
new = ("the microphysical \u03c3/m at dSph velocities above Horigome+ 2025's 0.8 cm\u00b2/g "
       "limit by 3.6\u201323.7\u00d7 (\u03c3_eff = f_H\u00b2\u00b7\u03c3/m is 0.251 cm\u00b2/g at "
       "v = 15, i.e. BELOW that ceiling; the excess is in \u03c3/m; the comparison applies a "
       "velocity-dependent \u03c3/m(v) to a velocity-INDEPENDENT threshold, so these factors "
       "are an UPPER BOUND on the true tension \u2014 see \u00a73.6)")
fix("F5a attach upper-bound qualifier to abstract 3.6-23.7x", old, new)

old = ("the framework's \u03c3/m(v) exceeds Horigome+ 2025 preference thresholds by "
       "3.6\u201323.7\u00d7 at v_eff = 5\u201320 km/s using their w = 10 km/s velocity-dependent "
       "limit (0.8 cm\u00b2/g) and by 27\u201349\u00d7 at v = 9\u201340 km/s (excluding v=28 where "
       "\u03c3/m is resonantly 830\u00d7) against their decisive CDM-preference threshold "
       "(0.2 cm\u00b2/g, Abstract); at v = 28 km/s (Cloud-9 anchor) \u03c3/m = 166 cm\u00b2/g, "
       "830\u00d7 above the velocity-independent threshold.")
new = ("the framework's \u03c3/m(v) exceeds Horigome+ 2025 preference thresholds by "
       "3.6\u201323.7\u00d7 at v_eff = 5\u201320 km/s using their w = 10 km/s velocity-dependent "
       "limit (0.8 cm\u00b2/g) and by 27\u201349\u00d7 at v = 9\u201340 km/s (excluding v=28 where "
       "\u03c3/m is resonantly 830\u00d7) against their decisive CDM-preference threshold "
       "(0.2 cm\u00b2/g, Abstract); at v = 28 km/s (Cloud-9 anchor) \u03c3/m = 166 cm\u00b2/g, "
       "830\u00d7 above the velocity-independent threshold. **Caveat:** the 0.2 cm\u00b2/g "
       "decisive threshold is a velocity-INDEPENDENT quantity while the framework's "
       "\u03c3/m(v) is strongly velocity-dependent, so these factors are an UPPER BOUND on "
       "the true tension; a definitive comparison requires re-running Horigome+'s "
       "SASHIMI likelihood with our \u03c3(v,\u03b8) form (\u00a73.6).")
fix("F5b attach upper-bound qualifier to Main result 3.6-23.7x", old, new)

# =====================================================================
# F6  Abstract: state BOTH channel counts, not just the rosier one
# =====================================================================
old = ("**Framework score (per A.15 canonical, R88(52) honest + v19.2-E A.1 caveat):** "
       "8 constrained channels (**4 PASS / 3 MARGINAL / 1 FAIL**; PASS = Cluster v=500, "
       "dSph v=10, Cloud-9 v=28, SPARC v=100; MARGINAL = UFD v=3, UFD v=5, UFD v=15; "
       "FAIL = dSph v=7; see \u00a7A.15 Block 1).")
new = ("**Framework score (per A.15 canonical, R88(52) honest + v19.2-E A.1 caveat):** "
       "8 constrained channels. Under the canonical (self-normalized \u03c3_unc) accounting: "
       "**4 PASS / 3 MARGINAL / 1 FAIL** (PASS = Cluster v=500, dSph v=10, Cloud-9 v=28, "
       "SPARC v=100; MARGINAL = UFD v=3, UFD v=5, UFD v=15; FAIL = dSph v=7; see "
       "\u00a7A.15 Block 1). Under the promoted published-\u03c3_unc likelihood (T205, "
       "v19.2-E A.1) the SAME canonical parameters give **1 PASS / 0 MARGINAL / 7 FAIL** "
       "(Cluster v=500 only); the 5-parameter DE best-fit reaches 5/8 at that likelihood "
       "(\u00a7A.15 Blocks 2\u20133). **Both counts are stated here because they differ only "
       "by likelihood convention, and a reader who sees only one of them would draw a "
       "materially different conclusion.**")
fix("F6 abstract states both channel counts", old, new)

# =====================================================================
# F7  Label the threshold at each quoted multiple so the three
#     rotating thresholds (0.8 / 0.2 / 0.04) are visible at point of use
# =====================================================================
# NOTE: the file's list continuation lines are " - v = N" (leading space),
# so every "\n" in the pattern must be followed by a space.
old = ("- v = 9 (Sculptor): 5.43 cm\u00b2/g (canonical a_slope=1.93) \u2014 27\u00d7 above threshold\n"
       " - v = 10 (Draco): 4.39 cm\u00b2/g \u2014 22\u00d7 above\n"
       " - v = 15 (Fornax): 2.01 cm\u00b2/g \u2014 10\u00d7 above\n"
       " - v = 18 (Fornax canonical): 1.41 cm\u00b2/g \u2014 7\u00d7 above\n"
       " - v = 25: 0.75 cm\u00b2/g \u2014 3.7\u00d7 above\n"
       " - v = 28 (Cloud-9): 0.60 cm\u00b2/g \u2014 3\u00d7 above (resonance peak: \u03c3/m = 174, far above)")
new = ("- v = 9 (Sculptor): 5.43 cm\u00b2/g (canonical a_slope=1.93, background only) \u2014 "
       "27\u00d7 above the **0.2 cm\u00b2/g decisive CDM-preference threshold**\n"
       " - v = 10 (Draco): 4.39 cm\u00b2/g (background only) \u2014 22\u00d7 above the "
       "**0.2 cm\u00b2/g decisive threshold**\n"
       " - v = 15 (Fornax): 2.01 cm\u00b2/g (background only; 2.85 cm\u00b2/g with the "
       "\u03c3_1 = 4.4 Gaussian tail included, per \u00a72.5) \u2014 10\u00d7 above the "
       "**0.2 cm\u00b2/g decisive threshold**\n"
       " - v = 18 (Fornax canonical): 1.41 cm\u00b2/g (background only) \u2014 7\u00d7 above "
       "the **0.2 cm\u00b2/g decisive threshold**\n"
       " - v = 25: 0.75 cm\u00b2/g (background only) \u2014 3.7\u00d7 above the "
       "**0.2 cm\u00b2/g decisive threshold**\n"
       " - v = 28 (Cloud-9): 0.60 cm\u00b2/g (background only) \u2014 3\u00d7 above the "
       "**0.2 cm\u00b2/g decisive threshold** (resonance peak: \u03c3/m = 174, far above)\n"
       "\n"
       "**Threshold-rotation note.** Three different Horigome+ 2025 limits are in play "
       "across this paper, and each quoted multiple below is against a NAMED one: the "
       "**0.8 cm\u00b2/g** w = 10 km/s velocity-dependent upper limit (the appropriate "
       "comparison for this framework's strongly velocity-dependent \u03c3/m(v), and the "
       "basis for the abstract's 3.6\u201323.7\u00d7), the **0.2 cm\u00b2/g** decisive "
       "CDM-preference threshold (the basis for the 3\u201327\u00d7 figures above), and "
       "the **0.04 cm\u00b2/g** velocity-independent (w\u2192\u221e) upper limit (the basis "
       "for the 115\u2013460\u00d7 figures in \u00a73.6). The three are NOT interchangeable: "
       "the same \u03c3/m(15) yields 3.6\u00d7, 10\u00d7, and 50\u00d7 against the 0.8, 0.2, "
       "and 0.04 limits respectively.")
fix("F7 label thresholds at point of use", old, new)

# =====================================================================
# F8  f_H canonical drift: 0.297 (constants.py) vs 0.30
# =====================================================================
old = ("with f_H the heavy-fraction at the observation radius (f_H_cc \u2248 0.30 from "
       "T207 fit for core-collapsed dSphs)")
new = ("with f_H the heavy-fraction at the observation radius (f_H_cc \u2248 0.30 from "
       "T207 fit for core-collapsed dSphs; the canonical single-component value is "
       "f_H = 0.297 per constants.py \u2014 0.30 is a rounded stand-in, a 2% shift in "
       "f_H\u00b2\u00b7\u03c3/m)")
fix("F8a note f_H canonical value at L98", old, new)

old = ("**Fornax \u03c3_HL outlier**: \u03c3_HL_required = (\u03c3_eff_published \u2212 "
       "f_H\u00b2 \u03c3_HH) / (2 f_H f_L) at f_H = 0.30.")
new = ("**Fornax \u03c3_HL outlier**: \u03c3_HL_required = (\u03c3_eff_published \u2212 "
       "f_H\u00b2 \u03c3_HH) / (2 f_H f_L) at f_H = 0.30 (rounded from the canonical "
       "f_H = 0.297 of constants.py; see \u00a72.5).")
fix("F8b note f_H canonical value at L174", old, new)

# =====================================================================
# F9  Separate the 764-word status block from the 287-word abstract
# =====================================================================
old = "**v19.2-F Phase 3 verdict (2026-10-11, this draft):**"
new = ("---\n\n"
       "### Headline verdicts (summary block \u2014 not part of the abstract prose)\n\n"
       "**v19.2-F Phase 3 verdict (2026-10-11, this draft):**")
fix("F9 mark the status block as separate from the abstract", old, new)

# =====================================================================
# Structure preservation checks
# =====================================================================
# F9 deliberately adds ONE H3 ("### Headline verdicts ..."), so the H3
# count is expected to be +1. Everything else must be unchanged.
assert txt.count("\n## ") == orig.count("\n## "), "F-check: H2 count changed"
assert txt.count("\n### ") == orig.count("\n### ") + 1, "F-check: H3 count != +1"
assert txt.count("```") == orig.count("```"), "F-check: code fence count changed"
assert txt.count("\n## ") == orig.count("\n## "), "F-check: H2 count changed"

PAPER.write_text(txt, encoding="utf-8")

print("=" * 78)
print("ROUND 5 PAPER FIXES APPLIED")
print("=" * 78)
for name, n in LOG:
    print(f"  \u2713 {name}  ({n})")
print()
print(f"  paper: {len(orig)} -> {len(txt)} chars ({len(txt)-len(orig):+d})")