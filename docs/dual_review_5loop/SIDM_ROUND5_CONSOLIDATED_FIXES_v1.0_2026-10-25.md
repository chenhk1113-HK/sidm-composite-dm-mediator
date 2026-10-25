# SIDM Round 5 — Consolidated Fixes Report (v1.0, 2026-10-25)

**Scope:** all confirmed Round 5 / local-review defects, with the code and data references that
establish ground truth. Every number below was recomputed from source on 2026-10-25.

**Branch:** `wip/v19.2-F-init`  **Paper:** `v0.3-prelim/docs/PAPER_V1_DRAFT.md` (2383 lines)

**Outcome:** 6 paper defects + 1 generator (root-cause) defect + 1 review-document defect class
= **8 fixes applied**, all verified. 2 additional pre-existing issues found and left alone
(§10 L98 band; §9 Table-walker — both confirmed pre-existing, not caused by these edits).

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
"interpretation": (
    "Per r20.docx Bug 1 fix: paper convention (Gaussian w=4.4) gives sigma/m ~0.5-2.5 cm^2/g "
    ...
    "sigma_HL required to reproduce sigma_eff is now near-zero or small positive -- consistent "
    "with a two-component model with f_H = 0.30."
),

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
"_derived_ranges": {
  "sigma_m_cm2_per_g": {"min": 2.8454570671911887, "max": 16.865226429437705},
  "sigma_eff_published_cm2_per_g": {"min": 0.0318, "max": 0.0931},
  "sigma_HL_cm2_per_g": {"min": -3.392310425355699, "max": -0.5340265143981119},
  "n_halos": 8,
  "n_halos_abs_sigma_HL_below_0.05": 0
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
| F2 | ceiling labels on L36 | **OK** — the stray trailing `[Q]` removed; the "9.85" arithmetic flagged |
| ERR L36 | 27–49× unsupported by excerpt | **VALID**, proposed lower end **superseded** (14×, not 22×) |
| ERR L117 | 0.5–2.5 conflicts with 5.43/4.39 | **VALID and worse than stated** — stale band, not a missing assumption; line ref off by one |
| Q L117 | "7 of 8 halos" vs retracted "7 of 8 channels" | **ANSWERED** — different quantities; and the count is 0 of 8 |
| ERR L145 | hierarchy contradiction | **CONFIRMED**, sharper — σ_1 = 1.0 is inside "σ_1 ≲ 3.0" |
| Q L189 | 1/σ_peak assumption unstated | **CORRECT**, assumption validated to ≤1.4% |
| Q L2210 | archival ranges | **ANSWERED** — both reproducible from the canonical table; the stale one was 115–460× |

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
