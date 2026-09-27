# T116 — Sequential confirmation of T90-era magnetic-moment value

**Date:** 2026-09-08
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Status:** RUNNING (background process `proc_cca3c441b459`)
**Method:** Sequential (find workable solution, fix it, test against other data)

---

## TL;DR

User follow-up (2026-09-08) to query1.docx methodological point:
**"what about the sequential testing using the original magnetic value of t95?"**

This is the **direct application of the sequential method** to the
T90-era workable magnetic-moment solution:

- **T90-era found:** μ_χ = 6.10×10⁻⁸ μ_N at m_χ = 1000 GeV
  (workable, sequential method)
- **T110 (global) found:** when μ_χ is allowed to float freely, the data
  prefer μ_χ → 0 (Door C CLOSED, Δlog Z = -10.7)
- **T116 (this script):** sequential confirmation at the T90 value

The user is asking: **was the T90 workable finding actually workable?**

---

## What this tests

**T90-era sequential logic:**
1. Tune μ_χ to match LZ observation (got 6.10×10⁻⁸ μ_N)
2. Check it doesn't break v0.7 SIDM fit (assumed yes)
3. Conclude: μ_χ ~ 10⁻⁷ μ_N is a "workable solution"

**T116 tests:**
1. Fix μ_χ = 6.10×10⁻⁸ μ_N (NOT a free parameter)
2. Run v0.7 6D fit with this FIXED μ_χ
3. Check if v0.7 SIDM fit is preserved (sequential check 1)
4. Predict LZ events at this fixed μ_χ value
5. Check if ~1 event predicted (sequential check 2)

**If both sequential checks pass:**
- T90-era workable solution is **actually workable**
- T110's global rejection means: "data don't prefer it, but it doesn't break anything"

**If sequential checks fail:**
- T90-era solution was **not even workable** at the value they found
- More concerning than T110's global rejection

---

## Honest expectation

T110 (global) found that when μ_χ is free, the data prefer μ_χ → 0.
This means the data are not particularly fond of magnetic-moment explanation.

But: **T110 doesn't tell us if the T90 value was workable**. It tells us
that a free μ_χ goes to zero. T110 doesn't preclude that μ_χ = 6.10×10⁻⁸
could be a workable solution.

The sequential test (T116) is what the user is asking for: was the
workable solution actually workable?

---

## T90 value being tested

| Parameter | Value | Source |
|---|---|---|
| μ_χ | 6.10×10⁻⁸ μ_N | `pandax_magnetic_moment_real.py` (T90 era) |
| m_χ | 1000 GeV (1 TeV) | T90 posterior |
| Note | T90 found this matched LZ 248 keV via magnetic-moment EFT | |

---

## What this confirms/denies

**If T116 PASSES both sequential checks:**
- T90 workable solution is genuinely workable
- T110's global rejection is just "data don't prefer this, prefer zero"
- Project position: "Door C was sequentially workable, but globally not preferred"
- Consistent with query1.docx: sequential and global answer different questions

**If T116 FAILS sequential check 1 (v0.7 broken):**
- T90 workable solution breaks v0.7 SIDM
- Means T90 finding was NOT actually workable (it broke something)
- More concerning than T110 alone

**If T116 FAILS sequential check 2 (LZ event):**
- T90 workable solution doesn't actually predict LZ event
- Means T90 value didn't really match LZ
- T110's global rejection makes more sense

---

## Cross-references

- **T90 era (early 2026):** μ_χ = 6.10×10⁻⁸ μ_N found sequentially
- **T110 (2026-09-08):** global fit, μ_χ → 0, Door C CLOSED, Δlog Z = -10.7
- **T115 (2026-09-08):** sequential confirmation of T112 (Portal B), failed
- **T116 (this):** sequential confirmation of T90 (magnetic-moment), running

---

## Files

- `v0.3-prelim/code/t116_sequential_t90_value.py` — main script
- `v0.3-prelim/tests/test_t116_sequential_t90_value.py` — 10 tests
- `v0.3-prelim/outputs/t95/t116_sequential_t90_value.json` — final output
- `v0.3-prelim/docs/T116_SEQUENTIAL_T90_VALUE.md` — this doc

---

## Caveats

1. **Sequential check is a sanity test** — confirms T90 finding was workable.
2. **T90 value (6.10×10⁻⁸ μ_N)** is from `pandax_magnetic_moment_real.py`.
3. **Even if T116 passes**, T110's global rejection still stands — the data
   don't PREFER μ_χ ≠ 0 when μ_χ is free.
4. **The query1.docx methodological point is fully tested by T115 + T116**:
   sequential and global answer different questions; both should be reported.

---

## Provenance

- T116 implementation: 2026-09-08
- Triggered by: user follow-up "what about the sequential testing using the
  original magnetic value of t95"
- Hermes Agent (MiniMax-M3)
- Branch: `wip/tier3-magnetic-moment-LZ`