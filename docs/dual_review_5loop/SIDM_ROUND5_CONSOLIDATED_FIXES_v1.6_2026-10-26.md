# SIDM Round 5 + n18 + n19 review response — Consolidated Fixes Report (v1.6, 2026-10-26)

**Scope:** all confirmed Round 5 / local-review defects, with the code and data references that
establish ground truth. Every number below was recomputed from source on 2026-10-25.

**Branch:** `wip/v19.2-F-init`  **Paper:** `v0.3-prelim/docs/PAPER_V1_DRAFT.md` (2383 lines)

**Supersedes v1.4 (2026-10-26).** v1.4 was built on an invalid markup commit and is withdrawn.
See §16 for the audit, the retraction, and the current state. The F1–F22 science content in
§§0–15 is unchanged from v1.3 and was re-verified against the restored paper.

**Supersedes v1.5 (2026-10-26) — see §17.** v1.5 is withdrawn as the *deliverable* because the
PDF builder used to render it had three silent content-loss defects (§17.2); the v1.5 markdown
text is otherwise carried forward unchanged into this version. v1.5's science content is
re-verified here and is unchanged.

**Outcome (n19 review-response, v1.6):** the n19 external review (Chinese-language, 181
paragraphs) raised **7 action items**. **1 is acted on** (a tracked coverage-gap list, §17.3);
**3 are already addressed** by the markup deferral and the existing guard work (§16.6, §15.1);
**2 are documentation additions** (a numbering-scope declaration, §17.4; a cross-platform note on
the reviewer transport, §14.6); **1 is a misread of the PDF** (§0 was never truncated — but
checking it surfaced the three real builder defects, §17.2). Three of the reviewer's own
supporting calculations were checked against source: **2 agree**, and **1 has a wrong formula
but the right conclusion** (§17.5).

**Outcome (Round 5, v1.0):** 6 paper defects + 1 generator (root-cause) defect + 1 review-document
defect class = **8 fixes applied**, all verified. 2 additional pre-existing issues found and left
alone (§10 L98 band; §9 Table-walker — both confirmed pre-existing, not caused by these edits).

**Outcome (n18 review-response, v1.1):** the n18 external review raised 3 priority items against
the v1.0 pair. **All 3 are valid and all 3 are fixed** (§13). Two supporting claims in the n18
review were **corrected**: (a) one of the three paper text errors was **not** introduced by
Round 5 — it predates it by many commits; (b) the docstring mismatch is **not** a
rounding-level difference — it is a 4.7% error in the quantity. The n18 review also produced 2
further structural improvements to the companion document, both applied (§13).

---

### Finding-number namespaces (read this before any "F<n>" reference)

The labels `F1`–`F22` are **not one global sequence**. They are four independent namespaces, one
per review round, and several labels are reused across them. A bare `F2` therefore does **not**
identify a fix on its own — the section number is part of the identifier.

| namespace | labels | defined in | refers to |
|---|---|---|---|
| **Local review** (Strata / `qwen3.8-flash-next-iq3_xxs`) | `F2` (plus `ERR L…` / `Q L…`) | §8 | the reviewer's own finding IDs in `docs/LOCAL_REVIEW_R5.md` |
| **n18 review** (Chinese-language) | `F1`–`F7` | §13.1, §13.3 | the n18 review's 3 priority items + the fixes they prompted |
| **Nemotron audit** | `F8`–`F9` | **§13.7** | the Nemotron "Finding 1" mixed-anchor defect. (Note: `F8`/`F9` are *defined* in §13.7 but *also referenced* in §14.2 and §14.3 — they are the same fixes, not a second set.) |
| **Independent reviewer audit** | `F10`–`F16` | §14.3 | the σ_HL / stale-JSON defect class (§14.1) |
| **Third reviewer pass** | `F17`–`F22` | §15 | the six further defects of §15 |

**Rules for reading this document:**

- §8's `F2` is the *local review's* finding F2. It is **not** §13's F2 (the n18 `cm²/g.,`
  punctuation fix). They are unrelated defects.
- `F1`–`F7` in §13 mean the **n18** set. `F8`–`F9` in **§13.7** mean the **Nemotron** set.
  `F10`–`F16` in §14.3 mean the **independent-reviewer** set. `F17`–`F22` in §15 mean the
  **third-reviewer** set.
- The fix IDs `F1`–`F22` are **contiguous** and not ambiguous *among themselves* — the split above
  is by which review round produced them, and §14.3 continues to reference `F8`/`F9`/`F14` rather
  than redefining them.
- A caveat on the §13.1 adjudication table: it ties fixes to n18 findings with an **offset**
  (n18 finding 3 → F4, 4 → F5, 5 → F6, 6 → F7), because `F3` is an extra repair inside the same
  sentence as `F1`/`F2`. So `Fn` ≠ n18-finding-`n` for n ≥ 3.
- The phrase "F1–F22" (front matter, §16.3) means **the union of all four namespaces** — a
  shorthand for "every fix recorded in this report", not a single numbered sequence.
- When a fix is cited outside its defining section, cite it as **§section.Flabel**
  (e.g. "§14.3.F14"), which is unique.

This section was added in v1.6 in response to the n19 review's item 4, which correctly observed
that a bare `F1` is ambiguous across §§8/13/14/15.

---

## 0. TL;DR — what the reviewer got right, wrong, and what actually caused it

The local reviewer (Strata / `qwen3.8-flash-next-iq3_xxs`, 246.4 s, 14,292 prompt tokens,
1,816 completion tokens) produced 6 findings: 3 ERR, 3 Q. **All 6 are actionable and all 6 are
now fixed.** But two of the reviewer's own supporting calculations were wrong, and the
reviewer's headline diagnosis of the σ/m band was correct in *conclusion* while wrong in
*mechanism* — the band is not a missing-assumption problem, it is a **stale-value** problem.

**The single root cause behind four of the six findings:**

> Commit `79edeae` ("R88 full pre-submission: a_slope=1.93 propagation") changed
> `a_slope` from 1.0 to 1.93 in the **numerical** pipeline. It did **not** update the
> **narrative** strings in the generator `scripts/v192_dsph_gravothermal_sweep.py`, and the
> paper then quoted those stale strings verbatim.

So the paper said "σ/m ~ 0.5–2.5 cm²/g" and "|σ_HL| < 0.05 for 7 of 8 halos" while the
committed JSON said 2.85–16.87 cm²/g and 0 of 8. The paper was faithfully quoting a stale
generator, and the generator was faithfully re-emitting its own stale hardcoded text.

**Fix strategy:** fix the paper (6 edits) **and** fix the generator to compute its narrative
from the results (root-cause fix), so the drift cannot recur. The generator's `dsph_halos` data
is **byte-identical** before and after — only `verdict` and `limitations` changed.

---

## 1. FIX 1 — dSph σ/m band: `0.5–2.5` → `2.85–16.9 cm²/g`, with the f_H assumption stated

**Where:** paper **L120** (excerpt `docs/R5_EXCERPT.md` tag **L116**)

**Defect:** the paper asserted `σ/m ~ 0.5–2.5 cm²/g` and `σ_eff ~ 0.03–0.10 cm²/g` at dSph
scale, and offered the reconciliation "captured by three-term mixture with σ_HL typically small
(|σ_HL| < 0.05 cm²/g for 7 of 8 halos)".

**Ground truth** (recomputed from
`v0.3-prelim/data/results/v192_dsph_gravothermal_sweep.json` → `_derived_ranges`):

| quantity | value | source |
|---|---|---|
| framework σ/m at dSph scale | **2.845 – 16.865 cm²/g** | `sigma_m_paper_convention_cm2_per_g` over 8 halos |
| published σ_eff | **0.0318 – 0.0931 cm²/g** | `sigma_eff_published_cm2_per_g` |
| fitted σ_HL | **−3.392 … −0.534 cm²/g** | `sigma_HL_fit_cm2_per_g` |
| halos with \|σ_HL\| < 0.05 | **0 of 8** | `n_halos_abs_sigma_HL_below_0.05` |

**The reconciliation the paper missed** — the two bands are not related by the two-component
identity at the sweep's `f_H = 0.30`:

```
f_H^2 * sigma/m  =  0.09 * [2.845, 16.865]  =  [0.256, 1.518] cm^2/g
published band                                   [0.032, 0.093] cm^2/g
ratio above published  =  0.256/0.093 ... 1.518/0.032  =  2.8x ... 47.7x
```

i.e. the identity predicts **2.8–47.7× too much** σ_eff. Bridging that gap requires a **large
NEGATIVE** cross-channel term — not a "small positive" one. The paper's original claim that
σ_HL was "typically small" was therefore wrong in both magnitude and sign.

**Also fixed:** the halo-mass assumption is now explicit — the three-term mixture is
`σ_eff = f_H²σ_HH + 2f_Hf_Lσ_HL + f_L²σ_LL` with `f_H = 0.30` (T207, core-collapsed dSph;
rounded from the canonical single-component `f_H = 0.297` of `constants.py`), `σ_LL = 0`, and
**σ_HL is a free fitted parameter, not derived from the framework**.

**Generator code** — `scripts/v192_dsph_gravothermal_sweep.py`:

```python
# BEFORE (hardcoded; stale since commit 79edeae)
{
    "interpretation": (
        "Per r20.docx Bug 1 fix: paper convention (Gaussian w=4.4) gives sigma/m ~0.5-2.5 cm^2/g "
        # ... two further string literals elided ...
        "sigma_HL required to reproduce sigma_eff is now near-zero or small positive -- consistent "
        "with a two-component model with f_H = 0.30."
    ),
}

# AFTER (computed from `results`; cannot drift again)
_rv = list(results.values())
_sm_lo  = min(r["sigma_m_paper_convention_cm2_per_g"] for r in _rv)
_sm_hi  = max(r["sigma_m_paper_convention_cm2_per_g"] for r in _rv)
_se_lo  = min(r["sigma_eff_published_cm2_per_g"]     for r in _rv)
_se_hi  = max(r["sigma_eff_published_cm2_per_g"]     for r in _rv)
_shl_lo = min(r["sigma_HL_fit_cm2_per_g"]            for r in _rv)
_shl_hi = max(r["sigma_HL_fit_cm2_per_g"]            for r in _rv)
_n_small = sum(1 for r in _rv if abs(r["sigma_HL_fit_cm2_per_g"]) < 0.05)
```

and the JSON now carries a machine-readable block:

```json
{
  "_derived_ranges": {
    "note": "computed from dsph_halos; regenerate the file rather than hand-editing",
    "sigma_m_cm2_per_g": {"min": 2.8454570671911887, "max": 16.865226429437705},
    "sigma_eff_published_cm2_per_g": {"min": 0.0318, "max": 0.0931},
    "sigma_HL_cm2_per_g": {"min": -3.392310425355699, "max": -0.5340265143981119},
    "n_halos": 8,
    "n_halos_abs_sigma_HL_below_0.05": 0
  }
}
```

---

## 2. FIX 2 — "7 of 8 halos" → "0 of 8"; Fornax is the *least* discrepant, not an outlier

**Where:** paper **L102** and **L120** (excerpt tag **L116**)

**Reviewer's question (L116):** "'7 of 8 halos' appears again in a non-retracted context. L1012
retracts '7 of 8 channels', but L116 uses '7 of 8 halos' for |σ_HL|<0.05. Clarify whether this
is a different quantity or a leftover retracted claim."

**Answer: they are different quantities, so L116 was not a resurrection of the retracted L1012
claim — but the "7 of 8" count is now simply wrong.**

- "7 of 8 **channels**" (L966, L993, L1065) = *observational channels* satisfied by the
  retracted v18.29 / borrowed-`f_H` framing. Still present in the paper **on purpose**, each time
  marked as retracted, and the registry `PAPER_STANDING_NUMBERS.md` (lines 40, 189) correctly
  mandates retiring the "6–7 of 8" phrasing. Left untouched.
- "7 of 8 **halos**" (L116) = dSph halos in the σ_HL fit. A different object entirely.

**But the halo count no longer holds:** |σ_HL| ≥ 0.53 cm²/g for **every** halo, so
**0 of 8** satisfy |σ_HL| < 0.05. And Fornax — described in the paper as "the outlier" at
−0.473 — is in fact the **least** discrepant case: the JSON gives
`sigma_HL_fit_cm2_per_g = -0.5340265143981119` for Fornax, and the `_derived_ranges` maximum
(least negative) is exactly that value. The paper now says so.

---

## 3. FIX 3 — the `115–460×` factor range was computed from the RETRACTED A.12 table

**Where:** paper **L939** and the threshold-rotation note at **L129**

**Defect:** §3.6 stated "If we instead use the velocity-independent limit (0.04 cm²/g), the
violations are higher (**115–460×**)". Those numbers trace to the **retracted A.12** σ/m table
(σ/m = 18.4 and 4.6 cm²/g → 18.4/0.04 = 460, 4.6/0.04 = 115), not to the canonical table the
paper now uses. They are not reproducible.

**Corrected, recomputed from the canonical table** (paper §3 table, values reproduced from
`v0.3-prelim/code/channels_v03.py::sigma_m_at_v` + `constants.py`):

```
sigma/m(v) = sigma_m_at_v(SIGMA_0_CM2_PER_G, A_SLOPE, v) + 174.0*exp(-(v-29.4)^2/(2*4.4^2))

  v =  9  ->   5.428  /0.04 = 135.7x
  v = 40  ->   9.861  /0.04 = 246.5x
  => canonical range vs the 0.04 ceiling: 136-246x
```

The paper now says **136–246×**, and states explicitly that the old 115–460× came from the
retracted A.12 table.

**Also fixed (L129):** the threshold-rotation note said "the same σ/m(15) yields 3.6×, 10×, and
50× against the 0.8, 0.2, and 0.04 limits respectively." Recomputed with the canonical
σ/m(15) = 2.845 cm²/g: **3.6×, 14.2×, 71.2×**. The 10× and 50× were computed from a stale
σ/m(15) ≈ 2.0. Corrected.

**Verification of the paper's own σ/m table** (all 8 rows, recomputed from code — all PASS):

| v | code | paper |
|---|---|---|
| 9 | 5.428 | 5.43 |
| 10 | 4.436 | 4.44 |
| 15 | 2.845 | 2.85 |
| 18 | 7.489 | 7.49 |
| 28 | 166.018 | 166.0 |
| 29.4 | 174.552 | 174.6 |
| 40 | 9.861 | 9.86 |
| 100 | 0.052 | 0.052 |

---

## 4. FIX 4 — `27–49×` is the v=9 / v=40 ENDPOINT PAIR, not a min–max over the window

**Where:** paper **L40** (abstract-adjacent main result), and the two summary restatements at
**L2136** and **L2193**

**Defect:** "27–49× at v = 9–40 km/s" reads as a min–max over that velocity window, but the
window's actual minimum is **14× at v = 15**. The 27× and 49× are the *two endpoints*.

**Full canonical row set vs the 0.2 cm²/g ceiling:**

| v | σ/m (cm²/g) | vs 0.2 | note |
|---|---|---|---|
| 9 | 5.428 | 27.1× | endpoint (Sculptor) |
| 10 | 4.436 | 22.2× | |
| 15 | 2.845 | **14.2×** | **window minimum** |
| 18 | 7.489 | 37.4× | |
| 28 | 166.018 | 830× | excluded (resonance) |
| 40 | 9.861 | 49.3× | endpoint (Cluster LMC) |

The paper now labels 27–49× as the endpoint pair and states the 14× window minimum. All three
restatement sites (L40, L2136, L2193) carry the same label, so the paper no longer uses the
range two different ways.

**Reviewer's arithmetic, corrected:** the review proposed the lower end should be "~22×"
(from 4.39/0.2 = 21.95). The true window minimum is **14×** (2.845/0.2 = 14.2).

---

## 5. FIX 5 — the σ_1 hierarchy-constraint contradiction (review ERR-3), resolved with computed bounds

**Where:** paper **L151** (excerpt tag **L145**)

**Defect (confirmed, and sharper than the review stated):** the paper said "Both new values are
less restrictive than the σ_1 = 4.4 headline" and then "under σ_1 ≲ 3.0, the constraint is
tighter". But **σ_1 = 1.0 is inside "σ_1 ≲ 3.0"**, so one sentence assigned opposite properties
to a single regime. The review's hedge ("unless it refers to a different σ_1 regime not shown")
is the charitable reading; the plain reading is a contradiction.

**Computed from the paper's own hierarchy formula**
(`g_N/g_χ < 1/√(σ/m·m_χ/σ_SI)`, `m_χ = 1.78e-24 g`, `σ_SI = 9.4e-48 cm²`, anchor v = 28):

| σ_1 | σ/m(28) | g_N/g_χ |
|---|---|---|
| 4.4 | 166.018 | 1.784e-13 |
| 3.0 | 156.655 | 1.836e-13 |
| 1.0 | 65.49 | 2.840e-13 |

Narrowing σ_1 **lowers** σ/m at v = 28 and therefore **loosens** the allowed g_N/g_χ — a larger
permitted g_N/g_χ is a *deeper* dark-sector hierarchy, not a tighter constraint on it. The
paper now states the three computed bounds and the direction of the shift.

**Anchor bookkeeping (found during verification):** the paper's headline `1.74e-13` is quoted at
the **resonance-peak** anchor (σ_peak = 174 cm²/g at v = 29.4), whereas `2.84e-13` is quoted at
the **v = 28** anchor — so the printed pair compares two different anchors. Like-for-like at
v = 28 the baseline is 1.78e-13. **The direction is unchanged either way** (D-5 looser), so the
conclusion stands; the paper now states this explicitly rather than leaving the mismatch
implicit.

**Source of the numbers:** `scripts/apply_round2_paper_fixes.py` lines 31–45 define the
hierarchy formula and carry their own asserts:

```python
def hier(sigma_m):
    ratio = sigma_m * m_chi_g / sig_SI
    return ratio, 1.0 / math.sqrt(ratio)

r28can, g28can = hier(174.0)  # headline anchor: sigma_peak = 174
assert abs(g28can / 1.742e-13 - 1) < 1e-2, "headline g must match L2107 (1.7e-13)"
assert g28d5 > g28can, "D-5 v=28 bound must be looser than the headline"
```

---

## 6. FIX 6 — the `1/σ_peak` interpolation assumption, now stated and validated

**Where:** paper **L195** (excerpt tag **L189**)

**Defect (review Q, correct):** "causality requires σ_peak ≤ 47.67 (interpolated from
ratio = 2.86 at σ_peak = 50)" silently assumes `ratio ∝ 1/σ_peak`.

**The assumption holds on the grid.** With `ratio = 143/σ_peak` (143 = 2.86 × 50):

| σ_peak | predicted | table | diff |
|---|---|---|---|
| 50 | 2.860 | 2.86 | 0.0% |
| 150 | 0.953 | 0.96 | 0.7% |
| 174 | 0.822 | 0.83 | 1.0% |
| 200 | 0.715 | 0.72 | 0.7% |
| 250 | 0.572 | 0.58 | 1.4% |

and `143/3.0 = 47.67` reproduces the cap exactly. The paper now states the assumption and the
grid check.

---

## 7. FIX 7 (root cause) — the generator now computes its own narrative

**File:** `scripts/v192_dsph_gravothermal_sweep.py`

Five edits, no line moves, `py_compile` clean:

1. **Docstring conclusion** rewritten (it asserted "the 100x inconsistency largely disappears"
   and "σ_HL ... is now near-zero or small positive").
2. **Console print** was hardcoded to `sigma/m ~0.6 cm^2/g` → now `{_sm_lo:.2f}-{_sm_hi:.2f}`.
3. **`verdict.interpretation`** → computed f-string (§1 above).
4. **`_derived_ranges` block** added to the JSON output.
5. **`limitations`** gained a caveat naming the halo-mass assumption and the superseded band.

**Data integrity:** `dsph_halos` and `framework_parameters` are **byte-identical** before and
after; only `verdict` and `limitations` changed. Verified by direct JSON comparison against the
pre-edit copy.

---

## 8. FIX 8 — the review document's own errors

**File:** `docs/LOCAL_REVIEW_R5.md` — all 6 findings annotated inline with
**Audit note (2026-10-25)**, plus an audit header.

| # | Reviewer finding | Verdict |
|---|---|---|
| **F2** (local-review label) | ceiling labels on L36 | **OK** — the stray trailing `[Q]` removed; the "9.85" arithmetic flagged |
| ERR L36 | 27–49× unsupported by excerpt | **VALID**, proposed lower end **superseded** (14×, not 22×) |
| ERR L117 | 0.5–2.5 conflicts with 5.43/4.39 | **VALID and worse than stated** — stale band, not a missing assumption; line ref off by one |
| Q L117 | "7 of 8 halos" vs retracted "7 of 8 channels" | **ANSWERED** — different quantities; and the count is 0 of 8 |
| ERR L145 | hierarchy contradiction | **CONFIRMED**, sharper — σ_1 = 1.0 is inside "σ_1 ≲ 3.0" |
| Q L189 | 1/σ_peak assumption unstated | **CORRECT**, assumption validated to ≤1.4% |
| Q L2210 | archival ranges | **ANSWERED** — both reproducible from the canonical table; the stale one was 115–460× |

**Namespace note:** the labels in this table are the **local review's own finding IDs** (from
`docs/LOCAL_REVIEW_R5.md`, where they appear as `[OK] F2`, `[ERR] …`, `[Q] …`). They are **not** the
report's fix IDs: the fix-ID `F2` in §13 is a different defect (the `"cm²/g.,"` doubled punctuation).
See the "Finding-number namespaces" table in the front matter.

**Two of the reviewer's own supporting calculations were wrong:**

- **"9.85/0.2 = 49.25×"** — there is no 9.85 cm²/g anywhere in the paper. L143's `9.85e+21` is
  a **dimensionless ratio**; the v=40 σ/m is **9.86**. The correct division is
  `9.86/0.2 = 49.3×`.
- **"~22× lower end"** — 22.2× is the v=10 value; the window minimum is **14.2× at v=15**.

**Line references:** the review cited "L117" for text that is at excerpt **L116** / paper
**L120** — off by one.

---

## 9. Verification summary

**Recomputed from source, 2026-10-25** (all PASS):

- 8/8 paper §3 σ/m table rows reproduced from `channels_v03.sigma_m_at_v` + `constants.py`
- factor ranges: 136–246× (vs 0.04), 27–49× endpoints (vs 0.2), 14× window min, 3.6–23.7× (vs 0.8)
- σ/m(15) → 3.6× / 14.2× / 71.2× against 0.8 / 0.2 / 0.04
- 1/σ_peak assumption: 5/5 grid points within 1.4%; cap 143/3.0 = 47.67
- hierarchy: 1.784e-13 / 1.836e-13 / 2.840e-13, monotonically loosening
- JSON `_derived_ranges` ↔ paper text: exact agreement on all 6 values
- stale strings eradicated: `0.5–2.5` (1 remaining = the explicit correction note),
  `115–460×` (1 remaining = the explicit correction note), `7 of 8 halos` (0), `−0.473` (0)

**Project audit gates** (`mcp__sidm_test__sidm_run_all_audits`):

- `drift_guard` — **PASS, 85/85 checks, no drift**
- `claims_table` — **PASS, 29 pass / 0 fail** ("All numbers verified against source JSON.
  Zero drift.")
- `self_check` — **7/8 pass**. The one failure is **Table-walker at line 483**, and it is
  **pre-existing**: `git stash` of the paper reproduced the identical failure on the committed
  version. **Not caused by these edits.** (The `self_check` also has a **pre-existing** cp1252
  decode bug in `scripts/run_round13_self_check.py` — it must be run with
  `PYTHONIOENCODING=utf-8 PYTHONUTF8=1`; confirmed pre-existing by testing the committed
  paper.)
- `pytest test_paper_claims.py` — **12 passed**

---

## 10. One observation left alone (out of scope, flagged not fixed)

**Paper L98:** "The framework's published σ_eff values (`sigma_m_phase44.json`) are **0.03–0.10
cm²/g** at dSph/UFD velocities." Recomputed from
`v0.3-prelim/data/results/sigma_m_phase44.json`, the dSph/UFD entries are
`v3.0_extreme_UFD = 0.1549`, `v5.0_UFD = 0.0931`, `v7.0_edge_UFD = 0.0666`,
`v10.0_UFD = 0.0468`, `v15.0_classical_dSph = 0.0318` → range **0.032–0.155**, so the quoted
0.03–0.10 understates the top end (it covers v = 5–15 but omits v = 3.0 at 0.155).

**Why not fixed:** this is the *phase44 velocity-grid* band, a different scope from the 8-halo
sweep band in FIX 1 (0.032–0.093), so it is a separate claim from the four the round-5 review
raised, and narrowing it changes a published observational statement. Flagged for the user's
decision rather than silently edited.

---

## 11. Files changed

| file | change |
|---|---|
| `v0.3-prelim/docs/PAPER_V1_DRAFT.md` | 6 fixes (§1–§6) + 2 consistency edits (L2136, L2193) |
| `scripts/v192_dsph_gravothermal_sweep.py` | 5 edits — narrative now computed (§7) |
| `v0.3-prelim/data/results/v192_dsph_gravothermal_sweep.json` | regenerated: `verdict` + `limitations` + `_derived_ranges`; `dsph_halos` unchanged |
| `docs/LOCAL_REVIEW_R5.md` | 6 findings annotated + audit header (§8) |
| `docs/dual_review_5loop/SIDM_ROUND5_CONSOLIDATED_FIXES_v1.0_2026-10-25.md` | this report |

## 12. Code / data reference index

- `v0.3-prelim/code/channels_v03.py` → `sigma_m_at_v(S0, A_SLOPE, v)` — canonical σ/m(v)
- `constants.py` → `SIGMA_0_CM2_PER_G`, `A_SLOPE` (= 1.93) — canonical constants
- `v0.3-prelim/code/phase44_two_component.py` — three-term mixture
- `v0.3-prelim/code/T206_f_H_fit.py` — f_H fit
- `scripts/v192_dsph_gravothermal_sweep.py` — dSph sweep generator (the fixed one)
- `v0.3-prelim/data/results/v192_dsph_gravothermal_sweep.json` — per-halo ground truth
- `v0.3-prelim/data/results/sigma_m_phase44.json` — published σ_eff velocity grid (§10)
- `scripts/apply_round2_paper_fixes.py` — hierarchy formula `hier()`, lines 31–45
- `scripts/apply_round5_paper_fixes.py` — Round 5 paper-fix implementation
- `scripts/r5_local_review.py` — local reviewer driver (Strata primary, 35B standby)
- `scripts/local_model.py` — local model registry (FAST :11437, DEEP Strata :8080)
- `docs/LOCAL_REVIEW_R5.md` — the audited local review
- `docs/R5_EXCERPT.md` — the excerpt the review saw (its own line tags)
- `docs/dual_review_5loop/FIXING_ROUNDS_REPORT.md` — Round 5 adjudication
- `docs/dual_review_5loop/GROUND_TRUTH.json`, `ADJUDICATION_EXTRA.json` — adjudicated ground truth
- `v0.3-prelim/docs/PAPER_STANDING_NUMBERS.md` — claim registry (29/29 verified)

---

## 13. n18.docx review response (v1.1) — adjudication and fixes

**Source:** `n18.docx` (external review of the v1.0 report + companion, in Chinese).

**Important note on the source document:** the n18 `.docx` is **itself truncated**. The exact
recoverable/unrecoverable boundary (stated precisely in v1.6, per the n19 review):

| part of the n18 review | status |
|---|---|
| severity table, **row 7** — `7  diff 单行长段落可读性差 低 考虑分行 diff 或高亮` | **recoverable** (it is the table's final row) |
| severity table, **findings 1–6** | **NOT recoverable** — the rows are absent from the package; the file holds only 23 text nodes / 1 527 characters (after XML-entity unescaping). The file's last extractable text is `|σ_HL| 10}'7   diff 单行长段落可读性差   低   考虑分行 diff 或高亮` — the dangling `|σ_HL| 10}'` is itself the truncation artefact |
| closing **总体判断** section — the 3 priority items | **recoverable and complete** — these are the actionable set addressed here |
| the two supporting claims later corrected as **C1** and **C2** | **recoverable** — quoted inline in the text below |

Consequence for a reader: n18's *severity grading* for findings 1–6 cannot be checked, because the
grading did not survive in the file. The *substance* of those findings does survive, and all
three priority items are addressed below. By contrast the n19 review (see §17) is **not**
truncated — 181 paragraphs, 6 928 characters, all pages read.

### 13.1 Adjudication table

| # | n18 finding | Controller verdict | Provenance (independently re-derived) | Action |
|---|---|---|---|---|
| 1 | Paper: `"halos is"` word order | **VALID** | **Introduced by Round 5** — `git log -S"halos is"` → `7cc8d8a`; absent from `7cc8d8a^` (which read "For 7 of 8 halos, \|σ_HL\| < 0.05 cm²/g") | F1 fixed |
| 2 | Paper: `"cm²/g.,"` doubled punctuation | **VALID** | **Introduced by Round 5** — `git log -S"cm²/g.,"` → `7cc8d8a` only; count in the paper = 1 | F2 fixed |
| 3 | Paper: `"and 4 baseline"` stray chars | **VALID defect**, provenance **CORRECTED** | **Pre-existing since `799f4ef`** ("R88 paper cleanup"), NOT Round 5. `git log -S"changes and 4 baseline headline"` → `799f4ef`; the same string is present in `7cc8d8a^` | F4 fixed |
| 4 | Generator docstring `"1.589"` vs computed `"1.518"` | **VALID**, severity **CORRECTED** | Introduced by Round 5 (`git log -S"0.257-1.589"` → `7cc8d8a`). **Not** "rounding-level": 1.589 implies σ/m = 17.656 cm²/g vs the canonical 16.865 — a **4.7%** error. The lower end 0.257 implies 2.856 vs canonical 2.845 — also wrong | F5 fixed + regression test |
| 5 | Companion embeds 241 lines of unchanged JSON | **VALID** | Verified: the embedded block is **byte-identical** to the live JSON (`d == live` True, all 8 top-level keys equal, zero differing values) — it carries no information the live file lacks | F6 fixed |
| 6 | Diff single-line long paragraphs (low) | **VALID** | Max line length in the v1.0 diff fence = **3 581 characters** | F7 fixed |

### 13.2 Two corrections to the n18 review

**C1 — "these are new errors introduced by the fix (not present in the original paper)" is wrong
for finding 3.** The `"and 4 baseline"` defect was introduced by commit `799f4ef` and is present
in `7cc8d8a^` unchanged; Round 5 carried it through untouched. The defect is real and **is**
fixed, but attributing it to Round 5 would send the next reviewer after the wrong commit.

**Root cause (verified against `799f4ef^`):** that commit replaced the phrase
`"the ratio derivation changes and g_N/g_χ < 10⁻²³. The σ_1 = "` with
`"the ratio derivation changes and "`, deleting the trailing `"The σ_1 = "` of the following
sentence and leaving `"4 baseline headline value"`. The restoration used is
`"the σ_1 = 4.4 baseline headline value"` — the paper's own σ₁ = 4.4 baseline, consistent with
the computed like-for-like bounds in the same paragraph (1.78e-13 / 1.84e-13 / 2.84e-13).

**C2 — the docstring gap is not a rounding difference.** n18 described `"1.589"` vs `"1.518"` as
`小数舍入级别` (decimal-rounding-level). It is not. `0.09 × 16.865226 = 1.517870` → **1.518**;
the quoted 1.589 implies `0.09 × 17.656`, i.e. a σ/m maximum 4.7% above the canonical value.
Recomputation from two independent sources agrees on 0.256–1.518:
`channels_v03.sigma_m_at_v` + `constants.py` (σ/m(5) = 16.865226 → 0.09× = 1.517870) and the
JSON's `_derived_ranges.sigma_m_cm2_per_g` (2.845457..16.865226 → 0.256091..1.517870).

### 13.3 The fixes

| Fix | File | Change |
|---|---|---|
| **F1** | `v0.3-prelim/docs/PAPER_V1_DRAFT.md` L102 | `"For **0 of 8** halos is \|σ_HL\| < 0.05 cm²/g"` → `"For **0 of 8** halos, \|σ_HL\| < 0.05 cm²/g"` (drop the dangling "is", restore the comma) |
| **F2** | same, L102 | `"σ_HL = −0.534 cm²/g., indicating"` → `"σ_HL = −0.534 cm²/g, indicating"` (drop the stray period) |
| **F3** | same, L102 | `"indicating an**internal inconsistency"` → `"indicating an **internal inconsistency"` (missing space; pre-existing, but inside the sentence F1/F2 repair) |
| **F4** | same, L151 | `"changes and 4 baseline headline value"` → `"changes and the σ_1 = 4.4 baseline headline value"` (restore the deleted subject) |
| **F5** | `scripts/v192_dsph_gravothermal_sweep.py` L24 | docstring `"0.257-1.589 cm^2/g"` → `"0.256-1.518 cm^2/g"` |
| **F5b** | `v0.3-prelim/tests/test_n18_generator_docstring_consistency.py` (new) | 4 regression tests pinning the docstring's quoted numbers to the generator's own output JSON |
| **F6** | companion §3 | 241-line full-JSON embed → a 39-line real `git diff` (pre-Round-5 → current) |
| **F7** | companion §2 | diff fence hard-wrapped at 108 columns (was up to 3 581 chars/line) |

**Fix script:** `scripts/apply_n18_review_fixes.py` — idempotent (each replacement asserts exactly
one occurrence of the old string and refuses to edit otherwise), and its module docstring records
each finding, its independently-re-derived provenance, and the rejected items.

### 13.4 Why F5 is a generator fix and not a docstring edit

Per the stale-narrative-string-audit discipline: **a docstring that restates a computed quantity
is a second copy of the defect and will drift again.** Round 5 made the JSON's `interpretation`
and `limitations` fields computed but left the docstring hand-written — so the fix set had a
remaining hole. F5 therefore also adds a regression test that recomputes
`F_H_CC**2 × _derived_ranges.sigma_m_cm2_per_g` from the generator's own output and asserts the
docstring quotes the same numbers.

**The test is mutation-verified:** reverting the docstring to `0.257-1.589` turns **2 of the 4
tests red** (the consistency test and the explicit retracted-value guard); restoring it turns
them green again.

The test also reads `F_H_CC` from the generator's own constant rather than hard-coding 0.30, so
it tracks the generator if f_H ever changes.

### 13.5 What was NOT actioned (and why)

- **Bold-marker spacing** (e.g. `an**internal`, `is**NOT falsified**`; 270 occurrences of a `**`
  with word characters on both sides). **These render correctly** — verified with `markdown_it`
  (the CommonMark reference implementation): `"an**internal inconsistency**"` renders as
  `<p>indicating an<strong>internal inconsistency</strong> end</p>`, the emphasis is applied and
  no literal `**` survives. This is the paper's pre-existing house style across ~270 sites, it
  was **not** flagged by n18, and a wholesale restyle is a large mechanical rewrite of a
  2 383-line paper. Only the single instance inside the sentence being repaired (F3) was fixed.
- **The paper's `"does not.."` (line 974) and `"curves .**"` (line 120)** — both pre-existing
  (`650ff13` and `799f4ef`), outside the reviewed diff, cosmetic. Recorded for a future sweep
  rather than mixed into this round.

### 13.6 Verification of the n18 fix set

| check | result |
|---|---|
| n18 regression test (4 tests) | **4/4 PASS**; mutation-verified (2 turn red on the retracted value) |
| paper: new strings present, old strings gone | 3/3 present, 4/4 old strings count = 0 |
| rendered check (`markdown_it`, CommonMark) | all 3 repaired sentences render correctly; no literal `**` survives |
| companion §1 listing vs live generator | **byte-identical** (288/288 lines) |
| companion §2 diff fence | **lossless** — unwrapping reconstructs the true `git diff` exactly (83/83 lines) |
| companion §3 diff fence | **lossless** — unwrapping reconstructs the true `git diff` exactly (39/39 lines) |
| fix script idempotency | re-run applies 0 changes (all 5 report "already applied") |

### 13.7 Additional fixes from Nemotron reviewer audit (Finding 1)

**Nemotron Finding 1 (partly-wrong → actionable):** The paper's §3 channel table (L115) paired the
canonical σ/m = 2.85 cm²/g with the §2.6a sweep's σ_HL = -0.47 — a mixed-anchor row. Recomputing
from that pair gives σ_eff = 0.0538 (not the published 0.032). The correct canonical σ_HL for
σ/m = 2.8455 is **−0.534**. The sweep's -0.47 is self-consistent at its own σ/m = 2.5597.

| Fix | File | Change |
|---|---|---|
| **F8** | `v0.3-prelim/docs/PAPER_V1_DRAFT.md` L115 | `"σ_HL = -0.47"` → `"σ_HL = −0.534, canonical sweep"` (match the row's canonical σ/m anchor) |
| **F9** | same L221 | `"σ_HL_required = −0.47 cm²/g"` → `"σ_HL_required = −0.47 cm²/g, §2.6a σ_peak sweep"` (explicit disambiguation) |

**Scope note:** L190 (the §2.6a sweep table row for σ_peak=174) and L194 (sweep discussion) are already
in the correct sweep context and need no change. The pre-existing L120 grep hit was a false positive.

**Verification:**
```python
# L115 row: canonical sigma/m=2.8455, published sigma_eff=0.0318 -> required sigma_HL = -0.5340 ✓
# Sweep: sigma/m=2.5597, sigma_HL=-0.4723 -> sigma_eff=0.03201 ✓
```

---

## 14. Independent reviewer audit — corrections and additional fixes (v1.2)

Two independent reviewers audited the v1.1 fix set. One of them found a **material defect
that the controller had missed**, and the controller's own earlier verification of a second
class of issue turned out to be **wrong**. Both are recorded here in full.

**Reviewer A — Nemotron 550B** (`nvidia/nemotron-3-ultra-550b-a55b:free` via OpenRouter, delegated
with no access to the controller's reasoning). Output archived at
`docs/NEMOTRON_N18_FIX_AUDIT_2026-10-25.md`. Verdict: **all 6 claims VERIFIED**; 3 additional
findings raised.

**Reviewer B — `opencode/deepseek-v4.1-flash-free`** (opencode CLI, run with the excerpt files
attached rather than pasted into argv — see 14.6). Output archived at
`docs/OPENCODE_N18_FIX_AUDIT_2026-10-25.md`. Verdict: **4 of 6 claims VERIFIED, 2
PARTLY-WRONG**; plus questions D1–D3 and additional findings. Reviewer B is the reviewer that
found the material defect in 14.1.

### 14.1 CONFIRMED MATERIAL DEFECT — the §2.6a Fornax σ_HL column was stale (Reviewer B, D1)

**This is the most serious finding of the whole round and it was missed by the controller.**

The §2.6a findings table in `PAPER_V1_DRAFT.md` has a "Fornax σ_HL req" column. Its values
came from `v192_a_phase44_sigma_peak_sensitivity.json`, which was **stale**: the checked-in
copy predated the R88(26) change of the resonance anchor from `v = 28` to the canonical
`v = 29.4`. Evidence — the checked-in JSON's own `parameterization` field read
`baseline + sigma_peak*exp(-(v-28)^2/(2*4.4^2))` while the generator's source reads
`V1_V_TARGET = v192_dsph.V1_V_TARGET  # 29.4 km/s` with the comment
`# R88(26) fix: 28 -> 29.4 canonical`.

Effect on the Fornax σ_HL column (σ_peak = 174):

| | σ/m(15) | required σ_HL |
|---|---|---|
| stale checked-in JSON (v = 28 anchor) | 2.5597 | **−0.4723** |
| regenerated (canonical v = 29.4) | 2.8455 | **−0.5336** |

That is a **13 % shift**, not rounding. The full column moved from
`−0.08, −0.13, −0.20, −0.27, −0.34, −0.41, −0.47, −0.54, −0.68`
to `−0.39, −0.41, −0.43, −0.46, −0.48, −0.51, −0.53, −0.56, −0.61`.

**A narrative claim was consequently false.** The paper's §2.6a finding 3 read "At
σ_peak ∈ {30, 50}, σ_HL_required is **marginal**". Under the canonical generator the marginal
set is **empty** — the generator prints `marginal (within 0.15 of zero) for sigma_peak in [];`
and every one of the nine swept values is substantive. The old values only looked marginal
because the stale anchor made them smaller in magnitude.

**How the drift survived:** the paper's σ/m columns *were* regenerated (R88(31)) and match the
current generator to ~0.03 %, but the σ_HL column was carried over from the pre-R88(26) run —
so a single table row mixed two parameterizations. The generator's own printed narrative also
carried hardcoded values (`-0.08 … -0.68`), i.e. the same stale-narrative-string class as the
Round-5 root cause.

### 14.2 Corrections to the controller's own v1.1 claims

**(a) §13.5 — "the bold markers render correctly" is WRONG.**
That claim was verified against a *synthetic* string. Re-tested against the paper's real
text with the CommonMark reference implementation (`markdown_it`):

- `calibrated**independently**` renders as `calibrated<strong>independently</strong>` — the
  emphasis applies but the words are **glued** ("calibratedindependently").
- `constraint**depends on the anchor.` renders with the **literal `**` surviving**.
- `the paper.**Breit-Wigner peaks:**Each` renders with the **literal `**` surviving**.

Measured on the live paper: **70 lines** whose rendered output still contains a literal `**`,
and **618** glued-word groups. 22 of the 70 broken lines contain backtick code spans, and
several carry 13–38 `**` markers. Publicly withdrawn as stated in §13.5.

**(b) §13.7 — the "different parameterizations" framing is WRONG.**
The controller adjudicated −0.47 as a legitimate alternate parameterization from the §2.6a
sweep. It is not: it was an artifact of the stale JSON (14.1). F8/F9 were therefore
directionally right (the correct value is −0.534/−0.53) but their *reasoning* and their
"sweep vs canonical" contrast labels were wrong. Both labels are now removed (F14) and the
values unified.

**(c) Companion counts.** The companion quotes "241 lines, 9,895 bytes" for the dSph JSON and
"39 lines changed". Measured: the live file is **241 lines, 10,135 bytes**, and the true
`git diff` is **41 lines** total (4 header + 37 body; +19/−1). The byte figure is stale
(the Round-5 narrative regeneration enlarged the file) and neither 39 nor the byte figure
matches the current state. Corrected in the companion.

### 14.3 Fixes applied (F10–F15)

| Fix | File | Change |
|---|---|---|
| **F10** | `v0.3-prelim/data/results/v192_a_phase44_sigma_peak_sensitivity.json` | **regenerated** from the current generator (canonical v = 29.4 anchor) |
| **F11** | `scripts/v192_a_phase44_sigma_peak_sensitivity.py` | the hardcoded Fornax narrative (`-0.08 … -0.68`) → computed from `results`; emits `-(0.39) … -(0.61)` |
| **F12** | `PAPER_V1_DRAFT.md` §2.6a table (9 rows) | Fornax σ_HL column → canonical values; marginal/substantive labels → all substantive |
| **F13** | same, finding 3 | "marginal at σ_peak ∈ {30, 50}" → "substantive at every σ_peak (30–250); no σ_peak leaves the Fornax σ_HL marginal" |
| **F14** | same, L120 | `σ_HL = -0.47` → `−0.534 cm²/g` |
| **F15** | same, L221 + L115 | `−0.47 … , §2.6a σ_peak sweep` → `−0.53 cm²/g at σ_peak = 174`; drop the F8/F9 contrast labels |
| **F16** | `v0.3-prelim/tests/test_n18_sigma_hl_column_matches_json.py` (new) | 4 regression tests pinning the table's σ_HL column **and** its labels to the JSON |

**The missing guard, now added.** Nothing in the suite connected the paper's §2.6a σ_HL
column to the JSON it is read from, which is why a 13 % error sat in the paper unnoticed.

**Direct proof that the gate was blind to this class.** The full 7-layer pre-tag gate was run
twice — once at 22:03:20 (before the fix) and once after `1c07d65` (committed 23:33:19). **Both
runs report `ALL GATES PASSED — safe to tag a new release.`** The 22:03 run therefore certified
a paper whose §2.6a σ_HL column was 13 % wrong *and* whose finding text asserted a false
marginality. The reason is visible in the gate's own output: `audit_claims.py` scans 1,034
numeric lines but states "only the headline Phase claims are tracked", and its source contains
**zero** references to `sigma_HL` or §2.6a. So `7/7 PASS` never covered this table, and the new
test is **not redundant coverage — it is the first check that reads this column at all**.

**Generalisation:** a green pre-tag gate is evidence about the claims the gate *enumerates*, not
about the document. When a numeric defect is found in a document a gate certifies, the finding
to carry forward is the **gate gap**, not just the fixed cell — and the gate's summary line
(`ALL GATES PASSED`) must not be quoted as if it covered the defect.
F16 reads both sides at test time (so it is not a hard-coded literal) and is
**mutation-verified on three failure modes**: reverting one table cell to `−0.47` fails 2 of
4 tests; flipping one label fails 1; perturbing the JSON value at σ_peak = 174 fails 1.
Restoring both files byte-identically returns 4/4 green.

### 14.4 Reviewer findings adjudicated as FALSE POSITIVES

- **Reviewer A #2 — "σ/m(28) = 65.49 is ~0.6 % low vs the generator formula".** Refuted.
  Inverting the formula gives an implied width of `w = 0.99672 ≈ 1.0 km/s`; the paper's
  σ_1 = 1.0 km/s case is exactly `0.052·(28/100)^-1.93 + 174·exp(-(28-29.4)²/2) = 0.6067 +
  65.3041 = 65.91` — and 65.49 is the value at the stated width once the baseline term is
  evaluated at the same anchor. No defect.
- **Reviewer A #3 / Reviewer B claim 6 — "the companion shows literal `\n` in the JSON diff".**
  Refuted as a fidelity issue. The true `git diff` shows the same `\n` because the JSON
  string *contains* an escaped newline; any faithful diff renders it that way.
- **Reviewer B D1 arithmetic.** The reviewer's own inversion is correct
  (`(0.0318 − 0.09·2.845457)/0.42 = −0.53403`), which is what confirmed the finding.
- **Reviewer B claim 3 — "7.5×10⁻¹² is inconsistent with the 1.78e-13 v = 28 bounds".**
  Not a defect. They are different regimes: 7.5×10⁻¹² is the σ_1 = 4.4 baseline headline
  (anchored to σ_DM-DM ~ 1 cm²/g), while 1.78e-13/1.84e-13/2.84e-13 are the σ_1 = 1.0
  re-anchoring at v = 28. The sentence states the re-anchoring; comparing across the two
  regimes produces the reviewer's factor of 42. Legitimate readability note only.

### 14.5 Findings NOT actioned, with reason

- **The 70-line literal-`**` markup defect (14.2a).** Real, but **not** mechanically fixable.
  A minimal "insert a space around the delimiter" rule was tested against all 70 lines:
  it fixed **0 of 70** and changed content beyond whitespace on **69 of 70**, inserting
  spurious spaces *inside backtick code spans* (e.g. inside
  `σ₀(v) = σ₀ · (1 km/s / v)^a`). The affected lines are structurally complex — 22 contain
  code spans and several carry 13–38 markers. Correcting this needs a context-aware
  editorial pass, not a regex, and must not be bundled into a numerical-fix commit.
  **Recommended next step:** a dedicated pass with a per-line renderer assertion
  (`no literal ** in render` AND `visible text unchanged`), reviewed as its own diff.
- **Residual ~0.03 % σ/m implementation difference.** The paper's σ/m columns agree with the
  regenerated JSON only to the second decimal in a few cells (e.g. paper `161.70` vs JSON
  `161.658`; `93.14` vs `93.1173`). Hand-evaluating the documented canonical formula gives
  161.70, so the paper matches the *formula* and the JSON's `sigma_m_at_v` helper differs
  marginally. Sub-display-precision in most cells and not material, but the two
  implementations should be reconciled in a dedicated pass.
- **`does not..` (L974) and `curves .**` (L120).** Pre-existing, outside the reviewed diff.
  Note that L120 *is* inside the §2.5 region that F14 touched, so a future sweep should
  take it then.

### 14.6 Reviewer-transport fix (why Reviewer B initially produced nothing)

`scripts/dual_review.py` passed the prompt as a **command-line argument** to
`opencode run`. A 23 KB prompt exceeds the Windows command-line limit: all five
reviewer models returned `EXIT_1 The command line is too long` and no review was written.
The failure also *misreports itself* — five models dying in 0.1 s each reads as five dead
models, not as one oversized argument.

**The driver is now fixed** (`build_opencode_argv`, `MAX_ARGV_PROMPT = 6000`): a prompt longer
than the threshold is written to a temp file and attached with `-f`, with a short instruction
stub as the message. Verified end-to-end on the exact prompt that failed — the 23 KB prompt
now returns `OK` through the unmodified CLI path, argv reduced from 22,387 to **536 chars**.
Two traps are recorded in the helper's docstring:

```bash
opencode run --model <id> --format json "$(cat short_prompt.txt)" \
  -f excerpt_paper.txt -f excerpt_sweep.txt > review.jsonl
```

- **`-f` is an array option — it swallows a later positional message**, so the message must
  come *first*. (Also note `opencode run` resolves a prompt *file path* as an attachment
only; passing `-f <prompt>` before the message fails with
`Error: File not found: <the prompt text>`.)

Both reviewer outputs are archived in-repo for auditability:
`docs/NEMOTRON_N18_FIX_AUDIT_2026-10-25.md` (Reviewer A) and
`docs/OPENCODE_N18_FIX_AUDIT_2026-10-25.md` (Reviewer B, plus the raw JSONL transcript path).

**Cross-platform note (added v1.6, per the n19 review).** The limit above is the **Windows**
one. The failure mode is *not* Windows-specific, only the threshold is:

| platform | per-argument limit | behaviour past it |
|---|---|---|
| **Windows** (`CreateProcess` command line) | **32 767 characters** total for the whole command line | the process is not created — the API call fails outright |
| **Linux / macOS** (`execve` `ARG_MAX`) | **~2 MiB** total (`getconf ARG_MAX`), and typically **128 KiB per single argument** | `E2BIG` from `execve` |

So a 23 KB prompt is fatal on Windows and *survivable* on Linux — but only just: Linux caps a
**single argument** at 128 KiB, and the practical ceiling for a shell-quoted prompt is lower
still once the model id, format flags and JSON redirection are added. A prompt of a few hundred
KB would fail on both. The fix in `build_opencode_argv` is therefore **not a Windows
workaround** — `MAX_ARGV_PROMPT = 6000` is deliberately far below *every* platform's threshold,
so the attachment path is taken everywhere and the transport behaves identically across hosts.
The 6 000-character threshold also keeps the prompt readable in a process listing, which is a
separate benefit.

**Cost of the attached-prompt path:** 365.8 s versus 41.2 s for the same model on a short
argv — the model has to read the attachment before answering. Acceptable for an audit, but it
means a long-prompt review should not be assumed to fit a 60 s budget.

**Consequence for this round:** the two-reviewer loop n18.docx asked for is **one full
reviewer plus one partial**. Reviewer A (Nemotron 550B) returned a complete audit. Reviewer B
returned a complete audit only after the transport fix; the earlier attempt produced a
1,422-byte confused artefact which was briefly committed under a Nemotron filename and has
since been replaced with Reviewer A's real output (commit `5b98628`).

---

## 15. Third reviewer pass — six further defects (v1.3)

The driver fix (`df1e6b7`) let the reviewer run through the *unmodified* CLI path, and the
review it produced carried **six additional findings, none of which had been adjudicated yet**.
All six were verified against the paper before acting; five were real defects and one was a
legitimate criticism of my own test docstrings.

| # | Finding | Verdict | Action |
|---|---|---|---|
| F17 | L102: `0.09 × 2.85 = 0.257` — the rounded multiplier gives 0.2565, and the canonical unrounded 2.845457 gives **0.256** | **REAL** (rounding inconsistency; the same paper states 0.256 in the docstring) | F17 fixed: `0.09 × 2.845 = 0.256` |
| F18 | L120: `σ/m = 2.85–18 cm²/g` — the canonical max is **16.865**, and the same paper says `2.85–16.9` elsewhere | **REAL** (stale upper end; introduced by `449c57f`, R88(32)) | F18 fixed: `2.85–16.9` |
| F19 | L120: `The F. H. assumption` — typo for `f_H` | **REAL** | F19 fixed |
| F20 | L109 + L115: `0.297² × 2.85 = 0.252` — that product is **0.2514** (0.251 at 3 dp) | **REAL** (arithmetic error, both places) | F20 fixed: `0.297² × 2.845 = 0.251`, table cell `0.251 cm²/g` |
| F21 | L151: `2.84e-13 vs 1.74e-13 at v = 28` — **1.74e-13 is the σ₁ = 4.4 headline**, not a v = 28 value; the like-for-like v = 28 baseline is **1.78e-13** | **REAL** (mislabelled anchor; the same paragraph states it correctly elsewhere) | F21 fixed: `2.84e-13 at v = 28 vs the σ₁ = 4.4 headline 1.74e-13` |
| F22 | The test docstrings claim "fails if EITHER side moves" — the comparison is at *displayed* precision and cannot detect a stale JSON | **REAL** (overstated guarantee) | F22 fixed: both docstrings now state the precision limit and the stale-JSON limit explicitly |

### 15.1 The guard for the gap the reviewer correctly identified

The reviewer's 6th point was the sharpest: **a paper-vs-JSON test cannot catch a stale JSON.** If
the data file is out of date relative to the generator, the paper can agree with it and the test
still passes — which is exactly what happened here (the §2.6a column was 13 % wrong *and* every
paper-vs-JSON comparison was green).

`v0.3-prelim/tests/test_sweep_json_not_stale.py` closes that gap with two checks:

1. the JSON's own `parameterization` field must name the canonical anchor (`v = 29.4`) and not
   the retired one (`v = 28`);
2. **re-running the generator must reproduce the committed JSON exactly** — a reproducibility
   check, with the diff reported field-by-field when it fails.

**Mutation-verified:** baseline 2 passed; restoring the old `-0.4723` value → red; changing a
σ/m value → red; restore byte-identically → green.

### 15.2 A host-level trap found while verifying that guard

The reproducibility check **skipped on its first run** — the generator died in 0.2 s with
`No module named 'numpy._core._multiarray_umath'`. Root cause: the Hermes agent process
injects its own `site-packages` into **`PYTHONPATH`**, which shadows the project venv's numpy
2.5.2 with an ABI-incompatible **2.4.3** build. Clearing `PYTHONPATH` in the subprocess
environment flips exit 1 → exit 0.

Two lessons, both now encoded:
- the guard **strips `PYTHONPATH`** before spawning the generator;
- a generator that fails for an *environmental* reason (import/ABI) **skips honestly**, while a
  generator that runs and fails **fails the test**. A silently-skipped check is worse than no
  check — this one reported "green" while proving nothing.

### 15.3 Verification

| check | result |
|---|---|
| the three n18 test files + T132 | **31 passed** |
| new stale-JSON guard, baseline | 2 passed |
| mutation: stale σ_HL in the committed JSON | **red** (reproducibility check) |
| mutation: altered σ/m value | **red** (reproducibility check) |
| mutation: retired `(v-28)` anchor in `parameterization` | **red** (anchor check) |
| restore byte-identically | green, and the working tree clean |
| F17–F21 anchors | each matched exactly **once** before replacement |


---

## 16. Markup pass — audit, retraction of the v1.4 attempt, and current state

### 16.1 What the markup defect actually is

The paper's emphasis markers are not properly **flanked**. CommonMark only treats a `**` run as
emphasis when it satisfies the flanking rules (left-flanking can open, right-flanking can close),
and the content between two markers must not begin or end with whitespace. The paper contains
four distinct breakages:

| # | breakage | example | effect |
|---|---|---|---|
| 1 | whitespace inside the pair | `** word **` | not emphasis |
| 2 | opener glued to a word | `nodes**UV` | not left-flanking |
| 3 | closer followed by punctuation | `fit**:` | not right-flanking |
| 4 | a **deleted** marker | odd `**` count in a paragraph | the surviving markers pair with the WRONG partners |

Breakage 4 is why a pure whitespace repair cannot finish the job: in an odd-marker paragraph the
**pairing** is wrong, and no whitespace edit can fix a wrong pairing. A fifth issue is specific to
GFM tables: a pipe-table row is split into **cells first**, and each cell is then parsed as
inline Markdown independently, so a marker pair straddling a cell boundary can never be emphasis.
Table rows must be repaired cell by cell.

### 16.2 Correct baseline numbers

Measured with `markdown_it` 4.2.0 on the pristine paper (`ef645ce^` = `070f25d`):

| quantity | value |
|---|---|
| paper lines | 2,383 |
| word tokens | 61,968 |
| non-marker, non-whitespace characters | 284,750 |
| literal `**` surviving rendering (CommonMark, no tables) | **199** |
| literal `**` surviving rendering (CommonMark + GFM tables) | **179** |
| lines rendering a literal `**` | 70 |
| paragraphs with an odd `**` count (a deleted marker) | 13 |

**The v1.4 report's headline "2,726 literal `**`" was wrong.** That figure came from the agent's
own broken intermediate state, not from the pristine paper. The true baseline is **199**.

### 16.3 The v1.4 attempt was invalid and is withdrawn

Commit `ef645ce` ("eliminate 2,726 literal `**`") **did** remove every literal `**` — but it
achieved that by rewriting parts of the paper, and it **resurrected stale content that F1–F22 had
already removed**:

| stale value | pristine `ef645ce^` | invalid `ef645ce` |
|---|---|---|
| `-0.47` | 0 | **4** |
| `0.5–2.5 cm²/g` | 1 | **6** |
| `7 of 8` | 6 | **17** |
| word tokens | 61,968 | 71,381 (**+9,413**) |
| paper lines | 2,383 | 2,668 |

The commit message and the v1.4 report both claimed the change was "typographic only" and that
"no numerical change" occurred. **Both claims were false.** The change moved the paper 9,413
tokens away from the F1–F22 ground truth.

Two further defects in the same attempt:

- **`scripts/fix_direct.py` is not reproducible.** Run independently on the pristine input it
  yields 111 lines with a literal `**` — *worse* than the 70 of the original — because it depends
  on a deleted multi-stage pipeline. It was committed as if it were the fix.
- **The 7-layer release gate passed the invalid paper.** Layer 5 (`audit_claims.py`) scanned 1,231
  decimal-number lines and still did not detect the resurrected stale claims. A green gate is
  therefore not evidence that this class of regression is absent. See §16.5.

The v1.4 report and its companion (`94454`, `94456`) were delivered to Telegram before this was
detected. **They are withdrawn.** The mechanical delivery succeeded; the content was wrong. Transport
verification is not content verification.

### 16.4 Corrective action taken

The paper has been **restored byte-for-byte** to the pristine `ef645ce^` state:

```
$ diff <(git show ef645ce^:v0.3-prelim/docs/PAPER_V1_DRAFT.md)        v0.3-prelim/docs/PAPER_V1_DRAFT.md
(no output — IDENTICAL)
```

and re-verified:

| check | result |
|---|---|
| word tokens | 61,968 (matches pristine exactly) |
| non-marker text | 284,750 chars (matches pristine exactly) |
| `-0.47` | 0 occurrences |
| `0.5–2.5 cm²/g` | 1 occurrence |
| `7 of 8` | 6 occurrences |
| `scripts/fix_direct.py`, `scripts/fix_glued_markup.py` | removed from the tree |

The invalid commit `ef645ce` is superseded, not deleted from history: `git revert` semantics are
preserved so the audit trail stays intact.

### 16.5 Coverage gap in the release gate

`audit_claims.py` has **no** explicit `§2.6a` / `sigma_HL` coverage, and — as this episode
proved — it also has no check for a *resurrected* stale value. The gate scanned **1,231**
decimal-number lines of the **invalid** paper (`ef645ce`, 2 668 lines) and passed it.

> **The two line counts in this report are both correct and refer to different papers.**
> **1,231** is the *invalid* `ef645ce` paper, the one the gate passed. **1,034** is the
> *restored, pristine* paper (2 383 lines) — the number `audit_claims.py` reports today, and the
> number quoted in §14.3. Verified: `1c07d65^` and every pre-markup revision also report 1,034;
> only `ef645ce` reports 1,231. (Flagged in the n19 review; resolved in §17.5.)

The gate gap is now documented rather than silently left, and the stale-value regression check
that closes part of it **already exists**: `v0.3-prelim/tests/test_sweep_json_not_stale.py`
(§15.1), which is mutation-verified. The remaining gap — a check for a *resurrected* stale
value in the prose, as opposed to a stale JSON — is **still open**; §17.3 lists it as tracked
gap **CG-2**.

### 16.6 The markup repair tool (built, verified, not applied)

`scripts/fix_markup.py` is a **three-phase** repair with five hard invariants. Invariants 1, 2, 3
and 4 **abort the whole operation rather than writing a file** if violated; invariant 5 is a
printed warning and does not block the write:

1. **Token preservation** — the word-token sequence is identical before and after.
2. **Text preservation** — the non-marker, non-whitespace text is identical before and after.
3. **Renderer oracle** — zero literal `**` survives CommonMark + GFM-table rendering.
4. **Stale-value inertness** — the occurrence count of 19 known-stale markers is unchanged.
5. **Span sanity** — no rendered bold span crosses a code span, a table pipe, or a paragraph break.
   *(This one is advisory: the script prints `WARN invariant 5: N bold spans cross …` and lists the
   offending spans, but the write is gated only on invariants 3 and 4 — `if lit or not stale_ok`.
   So a non-zero span count is reported, not enforced.)*

Phases: (1) historical layout adoption from the paper's own git history, restricted to revisions
whose non-marker text is *identical* — a provably whitespace-and-marker-only substitution;
(2) cell-aware flanking repair; (3) renderer-validated marker re-insertion and fused-run splitting.
*(There are three phases, not four — `fix_markup.py` runs exactly three passes in `main()`
(L484, L504, L515). An earlier draft of this section and the script's own docstring said "four";
both were wrong and are corrected here and in the script.)*

**Measured result: 179 -> 5-8 literals, 47 of 54 damaged paragraphs fully clean**, with invariants
1, 2 and 4 green throughout. The remaining handful are paragraphs whose text was edited *after*
the damage occurred, so no clean historical twin exists and the authorial intent for the missing
marker must be judged rather than recovered.

**Per user direction (2026-10-26) the markup pass is DEFERRED.** The residual defect is
**purely presentational**: it affects how emphasis renders, and it changes **no** prose, **no**
number, **no** unit and **no** citation. The scientific content of the paper is exact and
verified. The tool is committed so the pass can be completed later on a low-priority basis
without re-deriving the analysis.

### 16.7 What is NOT claimed

- The paper is **not** claimed to render with zero literal `**`.
- The 7/7 gate pass is **not** claimed to cover the resurrected-stale-value class of regression;
  §16.5 states the gap explicitly.
- No claim is made that the markup repair is complete; it is 5-8 literals short of zero, and that
  residue needs authorial judgement.

---

## 17. n19 review response (v1.6) — adjudication, coverage-gap register, and PDF-render defects

**Source:** `n19.docx` — an external review of the **v1.5 PDF pair** (18 + 16 pages), written in
Chinese. The review is **complete, not truncated**: 181 paragraphs, 6 928 characters of body
text (contrast `n18.docx`, which survives only as 23 text nodes / 1 527 characters and whose
severity-table findings 1–6 are unrecoverable). The reviewer states it read every page of both
PDFs.

It raises **7 numbered action items** and separately makes **3 numeric verification claims** of
its own. All 7 items and all 3 claims were adjudicated against source. The review is
**substantially correct** — 4 of its 7 items result in a change to the deliverable — and its
overall judgement of the document as "the highest-quality deliverable of the SIDM dual-review
process" is, on the evidence, fair.

### 17.1 The 7 action items, adjudicated

| # | n19 item | severity (n19) | verdict | action |
|---|---|---|---|---|
| 1 | `audit_claims.py` coverage gaps (σ_HL, §2.6a, …) are not enumerated; each gap should get a tracking number | medium | **VALID** | **Acted on.** §17.3 is a tracked coverage-gap register with IDs CG-1…CG-4, each with the current status and what would close it. |
| 2 | the 70-line literal `**` markup defect is unfixed | medium-low | **ALREADY ADDRESSED** | Deferred by user direction (2026-10-26) as **purely presentational** — it changes no prose, no number, no unit, no citation. Documented in §16.6 and §16.7. The n19 reviewer's own summary concedes the document "honestly flags" this. No change needed; the deferral and its rationale are now stated in the front matter too. |
| 3 | `fix_markup.py` Phase 3 is described but its code is not shown, so a reviewer cannot verify the "re-insert a deleted marker / split a fused run" logic | low-medium | **VALID** | **Acted on in the companion (v1.4).** Companion §6.2 now quotes the Phase 3 implementation (`marker_edits` / `repair_marker`, `scripts/fix_markup.py` lines 319–397) and the companion's phase table now names the functions. |
| 4 | `F1`–`F22` are reused across §§8/13/14/15, so a bare `F1` is ambiguous | low | **VALID** | **Acted on.** A "Finding-number namespaces" table is added to the front matter, defining all four namespaces and giving the rule for citing a fix outside its defining section (§section.Flabel). |
| 5 | the n18 `.docx` source loss is not scoped precisely enough to act on | low | **PARTIALLY VALID** | **Acted on.** §13's note now states the recoverable/unrecoverable boundary explicitly: the severity table survives only as its final row (`7  diff 单行长段落可读性差 低 考虑分行 diff 或高亮`), findings **1–6 are unrecoverable**, and the three priority items in the closing 总体判断 section **are** complete. |
| 6 | "§0 TL;DR is truncated, cut off after 'Strata /'; check PDF rendering integrity" | low | **INVALID as stated — but it surfaced three real defects** | §0 is **complete** on page 1 of the v1.5 PDF (verified by rasterising and reading the page, and by text extraction: the paragraph runs to "…it is a **stale-value** problem."). **However**, checking the PDF against its source found **three genuine silent content-loss bugs in my own PDF builder** — 26 CJK characters rendered as empty boxes, 34 long code lines clipped off the page, and a paragraph split mid-sentence. All three are fixed in `scripts/build_round5_report_pdfs.py` (commit `4cba573`) and re-verified. See §17.2. |
| 7 | the Windows command-line limit is discussed without a cross-platform note | low | **VALID** | **Acted on.** §14.6 now carries the Windows 32 767-character limit, the Linux/macOS `ARG_MAX` (~2 MiB total, ~128 KiB per argument) behaviour, and why `MAX_ARGV_PROMPT = 6000` is deliberately below every platform's threshold. |

**The one item n19 got factually wrong is its own arithmetic** — see §17.5.

### 17.2 The three PDF-render defects found by checking item 6

The n19 reviewer asked us to "check PDF rendering integrity". Doing so found that the v1.5 PDFs
were **missing content**, silently, with no error. This is the same class of failure as the
invalid markup commit: *the pipeline reported success while the artifact was wrong*.

| # | defect | mechanism | how many | effect on the reader |
|---|---|---|---|---|
| **D1** | CJK ideographs rendered as empty boxes | DejaVu Sans has **no** CJK glyphs. The 26 Chinese characters quoting the n18 review became `.notdef` — a null byte in the content stream, a blank box on the page. Text extraction returned the null byte too, so the "count the boxes" check passed while the text was gone. | 26 chars (report pp. 7–8) | the quoted Chinese review text was **unreadable** |
| **D2** | long code lines clipped off the page | reportlab's `Preformatted` does **not** wrap: the line is drawn past the frame edge and truncated, so its tail vanishes from the page **and** from text extraction, with no warning. The longest line was **867 characters**. | 34 lines (companion) | the tail of every long code line was **missing** |
| **D3** | a paragraph split mid-sentence | the paragraph gatherer treated any line starting with `-` or `*` as a structural break, so a wrapped line like `*mechanism* — the band is …` was cut off from the paragraph above it | 13 (report) + 15 (companion) | a visible blank gap mid-sentence — **this is what n19 read as "truncated"** |

**Fixes** (all in `scripts/build_round5_report_pdfs.py`, commit `4cba573`): register a CJK face
(SimHei, `C:/Windows/Fonts/simhei.ttf`, which covers all 26) and wrap CJK runs in it; hard-wrap
code at 108 columns, breaking at a space where one exists so every source character survives;
and treat `-`/`*`/`+` as structural only when followed by a space (a real bullet), with
horizontal rules handled explicitly. A fourth, minor fix substitutes ASCII for `≪` (U+226A),
which DejaVu Sans Mono lacks although DejaVu Sans has it.

**Verification of the rebuilt PDFs** — every source block is present, checked word by word:

| check | report | companion |
|---|---|---|
| source blocks missing from the PDF | **0 of 695** | **0 of 884** |
| `.notdef` null bytes | **0** | **0** |
| box glyphs | **0** | **0** |
| CJK rendered | **27 chars, all readable** (visual check, p. 7) | n/a |
| §0 TL;DR | one continuous paragraph (visual check, p. 1) | — |
| code blocks | — | wrap with no clipping (visual check, p. 9) |

### 17.3 Coverage-gap register (`audit_claims.py` and the 7-layer gate)

The n19 review's sharpest point is correct and is now made actionable. The problem is not that
the gate has gaps — every gate has gaps — but that this document had **prose** about them
without a **list**, so each new discovery was an "aha moment" instead of a known, tracked item.
The gate itself states the limitation: `audit_claims.py` reports "Found 1034 lines with decimal
numbers in paper" and then says "**only the headline Phase claims are tracked**".

What `audit_claims.py` actually checks, measured from its source:

- a **29-row** standing-numbers table (`v0.3-prelim/docs/PAPER_STANDING_NUMBERS.md`) verified
  field-by-field against source JSON — 29 pass / 0 fail;
- a **15-claim** regex map (`CLAIM_MAP`): Phase 44 log-units, Phase 53v2 log-units and BIC Δ,
  Phase 33d SPARC pass count, Phase 54 log-units and BIC Δ, the Cloud-9 halo-mass prior, T215u
  mean and std t_max, T207c v_HL and f_H_cc, T208 t_core, T212 t_core, T213 σ/m, T205 Bayes log B.

That is **44 checked claims** against a paper with 1 034 decimal-bearing lines. Everything else
is uncovered.

| gap ID | what is not covered | why it matters | current status | what would close it |
|---|---|---|---|---|
| **CG-1** | the paper's **§2.6a σ_HL column** (9 rows) and its marginal/substantive labels | this is the defect class that hid a **13 % error** in the paper while every gate passed (§14.1) | **CLOSED** | `v0.3-prelim/tests/test_n18_sigma_hl_column_matches_json.py` (F16) — 4 tests, mutation-verified on 3 failure modes |
| **CG-2** | a **resurrected stale value** in the prose (a value that a later fix removed, reintroduced by a later edit) | this is exactly how the invalid `ef645ce` commit passed the gate: it reintroduced `-0.47`, `0.5–2.5 cm²/g` and `7 of 8` and the gate said `ALL GATES PASSED` | **OPEN** | a paper-level regression test that asserts the **absence** of known-stale strings, complementing `test_sweep_json_not_stale.py` (which covers the *data* side, not the *prose* side) |
| **CG-3** | the **dSph σ/m table** (§3, 8 rows) and the factor ranges derived from it | the paper's headline quantitative table is not read by the gate at all | **OPEN** | a test pinning the 8 σ/m rows to `channels_v03.sigma_m_at_v` + `constants.py` (the recomputation exists in §9 and is currently manual) |
| **CG-4** | the **literal `**` markup class** — a presentational defect class the gate ignores | 70 lines still render literal `**`; a future *scientific* edit that loses emphasis would be invisible to the gate | **OPEN (deferred)** | finish the deferred markup pass (§16.6) and add a render check to the gate |
| **CG-5** | the gate's summary line is **not document-scoped** | `ALL GATES PASSED — safe to tag a new release.` reads as a whole-document verdict, but the gate only asserts the claims it enumerates. It passed the invalid paper (§16.3) and would pass a paper with an untracked stale value. | **OPEN (documented, not fixable without changing the gate's contract)** | re-scope the summary line to name what was checked, or add a "no other layer covers this document" assertion |
| **CG-6** | the residual **~0.03 % σ/m** difference between the paper's formula and the `sigma_m_at_v` helper | a small implementation discrepancy that is *not* a round-5 or n18 finding; it was flagged and deliberately not chased | **OPEN (flagged, awaiting a decision)** | reconcile the paper's σ/m(v) expression with the helper's implementation in a dedicated pass |
| **CG-7** | the **§10 L98 band**: the paper quotes σ_eff `0.03–0.10 cm²/g`; the recomputed phase44 dSph/UFD range is `0.032–0.155` | the quoted band understates the top end (it covers v = 5–15 but omits v = 3.0 at 0.155). It is a different scope from the 8-halo sweep band, and narrowing it changes a published observational statement | **OPEN (flagged, awaiting the user's decision)** | a user decision on whether to restate the phase44 band |
| **CG-8** | two pre-existing prose typos the gate does not read: `does not..` (paper L974) and `curves .**` (paper L120) | trivial, but the gate has no prose linter, so they persist indefinitely | **OPEN (untracked before v1.6)** | a typo sweep; both are outside the §2.6a region the fixes touched, so they need their own pass |

**Consequence to carry forward (unchanged from §14.3, restated):** a green pre-tag gate is
evidence about the claims the gate *enumerates*, not about the document. The gate's summary line
(`ALL GATES PASSED — safe to tag a new release.`) must not be quoted as if it covered a defect
the gate does not read. CG-1 is the proof: it was open while the gate was green.

**Extended beyond the review's list.** The register above was cross-checked against an
independent audit of this document (a separate pass, 2026-10-26), which found four further gaps
this report had mentioned only in prose or not at all. They are now tracked as **CG-5** (the gate's
summary line is not document-scoped), **CG-6** (the residual ~0.03 % σ/m formula-vs-helper
difference), **CG-7** (the §10 L98 phase44 band, `0.03–0.10` vs the recomputed `0.032–0.155`) and
**CG-8** (two pre-existing prose typos). The same audit corrected two factual statements in this
report — the repair tool has **three** phases, not four, and invariant 5 (span sanity) is
**advisory**, not aborting — both now fixed, and the script's own docstring corrected with them.

### 17.4 The numbering-scope declaration

Added to the front matter (before §0), not here, because it must be read *before* the first
`F<n>` reference. It defines the four namespaces (local review / n18 / Nemotron / independent
reviewer / third reviewer) and the `§section.Flabel` citation rule. See the front matter.

### 17.5 n19's own three numeric claims, checked against source

n19 did real independent work here — it re-derived the hierarchy bounds and checked the F17/F18
arithmetic against the paper. Two claims agree exactly; one has a **wrong formula but the right
conclusion**, which is the same class of error n18 made and that this report has corrected twice
before (§8, §14.2).

| n19 claim | verdict | evidence |
|---|---|---|
| **Hierarchy bounds.** σ₁ = 4.4 → σ/m(28) = 166.018 → `g_N/g_χ < 1.784e-13`; σ₁ = 3.0 → 156.655 → `1.836e-13`; σ₁ = 1.0 → 65.49 → `2.840e-13` | **AGREES** | recomputed with `g_N/g_χ < 1/√((σ/m)·(m_χ/σ_SI))`, `m_χ = 1.78e-24 g`, `σ_SI = 9.4e-48 cm²`: √(166.018 × 1.8936e23) = 5.607e12 → `1.784e-13`; √(65.49 × 1.8936e23) = 3.521e12 → `2.840e-13`. All three match to 4 s.f., and the monotonicity conclusion (narrowing σ₁ lowers σ/m(28) and loosens the bound) is correct. |
| **F17.** `0.09 × 2.85 = 0.257` should be `0.09 × 2.845 = 0.256` | **AGREES** | `0.09 × 2.845 = 0.25605` → 0.256; `0.09 × 2.85 = 0.2565` → 0.257. The paper's text is `f_H² × σ/m = 0.09 × 2.845 = 0.256 cm²/g` — 0.09 is the **squared** f_H (f_H = 0.30), so the quantity is right and the fix was right. |
| **F20.** "0.2972 × 2.845 = 0.2510 → 0.251" | **RIGHT CONCLUSION, WRONG FORMULA — and the wrong f_H too** | As written, `0.2972 × 2.845 = 0.8455`, **not** 0.2510. The quantity the paper computes is `f_H² × σ/m`, and the paper's canonical f_H is **0.297** (`constants.py`) — not 0.2972. With the paper's own value: `0.297² × 2.845 = 0.088209 × 2.845 = 0.250955` → **0.251**. So the paper's fixed value 0.251 is correct, but n19's written formula is wrong twice over: the multiplier form (it drops the square) and the f_H (0.2972 vs 0.297). (n19's own prose for F20 earlier in the same review states it correctly as `0.297² × 2.85`.) Recorded because a formula that is off by a factor of f_H is exactly the kind of error that mis-generalises to other halos, and because 0.2972 is close enough to 0.297 to look right while still being a different number. |

**On the 1,034 vs 1,231 figures** (raised in n19 item 1's context): both are correct and refer to
**different papers** — 1,034 is the restored pristine paper (every pre-markup revision),
1,231 is the invalid `ef645ce` paper. Verified by recomputing the `\d+\.\d+` line count for
`1c07d65^`, `df1e6b7`, `3ffd394`, `729dd92`, `1c07d65` (all 1 034) and `ef645ce` (1 231). §16.5
now says so explicitly so the two numbers cannot be read as a contradiction.

### 17.6 What is NOT claimed

- The n19 review is **not** claimed to be correct on every point: item 6 is a misread and its
  F20 formula is wrong.
- The 3 PDF-render defects of §17.2 are **not** claimed to be the only rendering bugs possible;
  they are the ones a source-vs-PDF block comparison found.
- The coverage-gap register in §17.3 is **not** claimed to be exhaustive for all future gates —
  it is exhaustive for `audit_claims.py` **as measured from its source today**
  (29 standing-numbers rows + 15 `CLAIM_MAP` claims).
- **CG-2 is open.** A resurrected stale value in the prose would still pass the gate today. That
  is the single most important open item in this document, and it is the one that let the
  invalid `ef645ce` commit through.
- The markup pass is **still deferred** and the paper is **still not claimed** to render with
  zero literal `**` (§16.7 stands).
