# T115 — Sequential confirmation of T112 MAP (Door B')

**Date:** 2026-09-08
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Status:** SHIPPED with HONEST FAILURE finding
**Method:** Sequential (find solution, fix it, test against other data)

---

## TL;DR

User (2026-09-08) raised the methodological point that the **sequential
approach is "the essence"** — find a workable solution first, then test
it against other situations, rather than letting the new parameter flow
freely in a global joint fit.

T115 does the SEQUENTIAL confirmation of T112 MAP. **HONEST RESULT:**
**BOTH sequential checks fail** at T112 MAP. This **weakens Door B'** and
provides important context for the +2.13 global fit result.

---

## Result summary

| Step | Check | Result |
|---|---|---|
| **Step 2** | v0.7 6D fit alone | log Z = -164.78 (vs published -163.29, drift = 1.49) |
| | m_φ preservation (factor < 2) | **PASS** (426 vs 588 MeV) |
| | m_χ preservation (factor < 2) | **PASS** (417 vs 498 GeV) |
| | log Z preservation (drift < 1.0) | **FAIL** (drift = 1.49) |
| **Step 3** | LZ event prediction at T112 MAP | N_pred = 0.0086 (vs ~1 expected) |
| | N_pred in [0.5, 5.0] | **FAIL** (0.0086 << 0.5) |

**Overall verdict:** BOTH SEQUENTIAL CHECKS FAIL — Door B' weakens.

---

## What this means

The user's methodological point was: **find a workable solution first,
then test it against other data**. T115 applied this to T112 MAP:

**Step 2 finding (v0.7 6D drift):**
- When LZ/DIAMX terms are removed from the likelihood, v0.7's fit at
  T112 MAP drifts by 1.49 log Z units (above 1.0 threshold).
- This means the T112 fit was **partially using the LZ/DIAMX terms** to
  pull the v0.7 6D parameters away from their pure-SIDM optimum.
- The drift is borderline (1.49 vs threshold 1.0); not catastrophic.
- Verdict: v0.7 SIDM is **mostly** preserved at T112 MAP but with some drift.

**Step 3 finding (LZ event prediction):**
- At T112 MAP, σ_PortalB = 8.7×10⁻⁴⁷ cm² is **BELOW LZ exclusion limit**.
- LZ exposure of 2.84 tonne-year with this σ predicts **~0.009 events**
  in the [200, 300] keV window.
- LZ observes 1 event.
- This means T112's σ_PortalB is **too small to explain the LZ event**.
- Verdict: T112 MAP does NOT match LZ observation via event count.

---

## Reconciling with T112's global +2.13 result

**Why did T112 get +2.13 then?**

T112's likelihood at MAP has these contributions:
- log L_v0.7 = -163.29 (the SIDM fit, baseline)
- log L_LZ_at_MAP = **+3.55** (significance 2.67σ, but σ is below limit so
  this is "LZ is consistent with this parameter point")
- log L_DIAMX (positive)
- Penalty for 2 extra parameters

**The +2.13 comes from the LZ/DIAMX terms being positive at T112 MAP.**
T112 found that adding (δ, σ_PortalB) as free parameters doesn't hurt
the fit. But it doesn't strongly EXPLAIN the LZ event either — at T112
MAP, σ_PortalB is too small for that.

**In other words:** T112's +2.13 is "the data don't reject the Portal B
extension," not "the data strongly prefer it for explaining LZ."

---

## What T112 actually shows

T112 demonstrates:
- ✅ Composite-DM with Portal B inelastic scattering is **compatible**
  with v0.7 SIDM (sequential check 2a PASSES for m_φ, m_χ).
- ✅ The data **don't reject** the extension (T112 global Δlog Z = +2.13).
- ❌ But the σ_PortalB at MAP is **too small to explain LZ's 248 keV event**
  (sequential check 3 FAILS).

This means: **T112's result is consistent with "the data allows composite-DM
with Portal B" but NOT with "the data demands composite-DM to explain LZ."**

---

## Honest caveats

1. **Sequential check is a sanity test, not a replacement for global fit.**
   The global test (T112, Δlog Z = +2.13) is the primary significance metric.
2. **The drift in v0.7 log Z (1.49) is borderline**, not a hard failure.
   m_φ and m_χ are within factor 2 of published values.
3. **The LZ event rate mismatch (0.009 vs 1)** is more concerning —
   T112 MAP predicts almost no events at current LZ, but LZ sees 1.
4. **T113 forecast for LZ Run 4 (~1000 events)** uses T108 MAP
   (σ = 1.4×10⁻⁴², much higher), not T112 MAP (8.7×10⁻⁴⁷).
   The two MAP points are very different.

---

## What this changes about T90 merge eligibility

**Before T115:** T90 branch eligible (3 of 5 criteria; T112 satisfied +2).

**After T115:** The T112 result needs to be **interpreted differently**:
- T112's +2.13 is real, but it shows "data compatible with Portal B",
  NOT "data strongly prefer Portal B for LZ explanation."
- The user's methodological point is **validated** by T115: sequential
  check is needed for full validation.

**Updated standing posture:**
- T90 branch is still WIP until user explicitly approves merge.
- T112's +2.13 criterion #5 is satisfied, BUT the interpretation is now
  "compatible, not strongly preferred."
- Sequential check (T115) shows: v0.7 mostly preserved, LZ event NOT matched.

**Honest summary:** Door B' is **technically open but weakly motivated**.
T112's +2.13 is the boundary case; T115 reveals it's not a strong claim.

---

## Caveats and methodological notes

1. **The T108 vs T112 difference matters.** T108 MAP had σ = 1.4×10⁻⁴²
   (above LZ limit, predicting many events). T112 MAP has σ = 8.7×10⁻⁴⁷
   (below LZ limit, predicting few events). Different priors → different MAPs.
2. **The user is correct** that the sequential method is "the essence".
   The global test alone is necessary but not sufficient for a claim.
3. **The +2.13 from T112 is technically the threshold for "statistically
   significant" but is right at the boundary.** T115 reveals it's not
   a strong claim about LZ explanation.

---

## Files

- `v0.3-prelim/code/t115_sequential_confirmation.py` — main script
- `v0.3-prelim/tests/test_t115_sequential_confirmation.py` — 11 tests
- `v0.3-prelim/outputs/t95/t115_sequential_confirmation.json` — final output
- `v0.3-prelim/docs/T115_SEQUENTIAL_CONFIRMATION.md` — this doc

---

## Cross-references

- **T112 (Door B', global fit):** Δlog Z = +2.13 (criterion #5 satisfied,
  but T115 reveals interpretation is "compatible, not preferred")
- **T108 (Door B, global fit):** Δlog Z = +0.51
- **T113 (event forecasts):** used T108 MAP, not T112 MAP
- **T114 (Xe-124 systematic):** orthogonal to T115 finding

---

## Standing posture

- **Master:** v0.5-prelim tagged, untouched
- **T90/LZ branch:** T108, T110, T111, T112, T113, T114, T115
- **T90 branch status:** still 2/3 criteria satisfied (the +2.13 is
  satisfied but now interpreted more cautiously)
- **Awaiting user direction on merge**

---

## Provenance

- T115 implementation: 2026-09-08
- Triggered by: user query "query1.docx" on methodological point
- Hermes Agent (MiniMax-M3)
- Branch: `wip/tier3-magnetic-moment-LZ`