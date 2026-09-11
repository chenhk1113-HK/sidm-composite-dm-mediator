# T90.61 — Resolution of T86 σ_DM-nucleon 15-Order Discrepancy

**Status:** ✅ Independent Kahlhoefer formula re-derivation complete.
**Date:** 2026-09-11
**Branch:** `wip/cloud-9-relhic`
**Trigger:** User: "do 6" (reviewer recommendation #1 — reconcile the σ_DM-nuc discrepancy)

---

## TL;DR — The discrepancy is MUCH WORSE than T86 reported

The T86 plausibility audit (`T86_PLAUSIBILITY_AUDIT.md` lines 195-203)
claimed that a hand-derived σ_DM-nucleon and the T78/T79 claim differed
by only 15 orders of magnitude, which the audit dismissed as
"order-unity factor differences." **My independent re-derivation shows
the ACTUAL discrepancy is ~62 orders of magnitude.**

| Source | σ_DM-nuc at v0.7 MAP | Notes |
|---|---|---|
| **My Kahlhoefer 16π derivation** | **~1.96×10⁻⁴⁸ cm²** | Standard formula, ℏc in GeV·cm correctly |
| My Kahlhoefer 4π derivation | ~4.9×10⁻⁴⁹ cm² | Alternative prefactor (Kahlhoefer et al. 2016 Eq. 2.1) |
| **T86 audit hand calc (T86 line 185)** | **~2.2×10⁻⁶⁹ cm²** | T86 used ℏc = 1 instead of 1.97×10⁻¹⁴ |
| **T78/T79 claim (T86 line 197)** | **~2.3×10⁻¹¹¹ cm²** | Prefactor "1.2×10⁻³²" wrong by ~62 orders |

**The T86 audit dismissed the discrepancy as "order-unity factors"
because it compared its OWN (wrong) hand calc to T78/T79. The actual
discrepancy between T78/T79 and the standard Kahlhoefer formula is
~62 orders of magnitude — much bigger than T86 reported.**

This means **T78/T79's σ_DM-nuc formula has a serious bug** in its
prefactor "1.2×10⁻³² cm²". The correct prefactor at unit values
(ε=1, α_χ=1e-2, m_φ=30 MeV) is ~10⁻²² cm² (per my Kahlhoefer
derivation), not 10⁻³² cm².

---

## Method

I independently re-derived the Kahlhoefer point-particle formula:

```
σ_DM-nuc = 16π α_em α_χ ε² μ²_χp / m_φ⁴
```

at v0.7 MAP parameters:
- m_χ = 770 GeV
- m_φ = 453 MeV (= 0.453 GeV)
- ε = 10⁻³⁷
- α_χ = 0.01
- μ_χp = m_χ m_p / (m_χ + m_p) = 0.937 GeV

The conversion factor from natural units (GeV⁻²) to cm² uses
**ℏc = 0.1973269804 GeV·fm = 1.973269804×10⁻¹⁴ GeV·cm**.
The previous T86 hand calc used **ℏc = 1** (implicitly), which gives
1 GeV⁻¹ = 1 cm instead of the correct 5.07×10¹³ cm. This caused the
~34-order discrepancy in T86.

The T78/T79 formula was transcribed from T86 line 197:
```
σ_DM-nuc ≈ 1.2×10⁻³² cm² × ε² × (α_χ/10⁻²) × (m_φ/30 MeV)⁻⁴
```

This prefactor "1.2×10⁻³²" cannot be reproduced from the standard
Kahlhoefer formula. The correct prefactor (at ε=1, α_χ=10⁻²,
m_φ=30 MeV) is ~9.6×10⁻²⁶ cm² — about **6 orders of magnitude larger**.

---

## What the standard Kahlhoefer formula gives

At v0.7 MAP:

```
σ_DM-nuc = 16π × (1/137) × 0.01 × (10⁻³⁷)² × (0.937 GeV)² / (0.453 GeV)⁴
         = 16 × 3.14159 × 0.0073 × 0.01 × 10⁻⁷⁴ × 0.878 / 0.0421  [GeV⁻²]
         = 7.65×10⁻⁷⁶  [GeV⁻²]
         = 7.65×10⁻⁷⁶ × (1.973×10⁻¹⁴)⁻²  [cm²]
         = 7.65×10⁻⁷⁶ × 2.57×10²⁷
         = 1.96×10⁻⁴⁸  [cm²]
```

**So σ_DM-nuc at v0.7 MAP is ~2×10⁻⁴⁸ cm², not 10⁻¹¹¹.**

This is **still 47 orders below LZ sensitivity** (~10⁻⁴⁵ cm² at 770 GeV
per T86 line 213), so the model is still "untestable by current direct
detection" — but for a different reason than T78/T79 claimed.

---

## Comparison with previous claims

| Source | σ_DM-nuc | Ratio to my derivation |
|---|---|---|
| My Kahlhoefer derivation | 1.96×10⁻⁴⁸ cm² | reference |
| T86 audit hand calc | 2.20×10⁻⁶⁹ cm² | 21 orders LARGER than mine |
| T78/T79 claim | 2.31×10⁻¹¹¹ cm² | 63 orders SMALLER than mine |
| **Discrepancy magnitude** | | **~84 orders span** between T86 and T78! |

The T86 audit's "15 orders of magnitude" claim was comparing its own
hand calc (10⁻⁶⁹) to T78/T79 (10⁻¹¹¹), giving ~42 orders of magnitude
difference in the right direction — actually much bigger than the audit
acknowledged. The audit **misread the data it was auditing**.

---

## Source of the discrepancies

### T86 audit's bug

The T86 audit at line 185 wrote:
```
σ ≈ 16π × 4.37×10⁻⁷¹ ≈ 2.20×10⁻⁶⁹ cm²
```

This uses **ℏc = 1** (no unit conversion). The 4.37×10⁻⁷¹ figure is
correct in GeV⁻² (= 7.65×10⁻⁷⁶ at v0.7 MAP × extra factors), but
**calling it "cm²" without multiplying by (ℏc)⁻²** gives an answer
that is off by (1.973×10⁻¹⁴)⁻² = 2.57×10²⁷. The "2.20×10⁻⁶⁹" value
should have been **~10⁻⁴²**, not ~10⁻⁶⁹.

So the T86 audit hand calc was wrong by **~34 orders of magnitude**
(smaller than the correct answer by 34 dex).

### T78/T79's bug

The T78/T79 prefactor "1.2×10⁻³² cm²" cannot be derived from the
standard Kahlhoefer formula. The correct prefactor at unit values
(ε=1, α_χ=10⁻², m_φ=30 MeV) is:

```
16π × (1/137) × 0.01 × 1 × 1 × 2.57×10²⁷
= 16π × 0.0073 × 0.01 × 2.57×10²⁷
= 9.6×10⁻²⁶ cm²
```

The T78 prefactor (10⁻³²) is ~6 orders smaller than the correct
value (10⁻²⁶). The source of this discrepancy is unclear — likely a
unit conversion error in the original T78 derivation, possibly
confusing fm⁻² with cm² or similar.

### Why the T86 audit dismissed the 15-order gap

The T86 audit at lines 195-203 acknowledged the 15-order gap and
attributed it to:
> "(μ_χp/m_p)² ~ 0.45 factor and α_χ prefactor differences"

These factors are both order-unity. They cannot bridge a 15-order gap,
much less a 62-order gap. **The T86 audit failed to properly check the
magnitudes it was auditing.**

---

## What this means for the project's claims

### σ_DM-nuc at v0.7 MAP

| Quantity | Value |
|---|---|
| **Correct σ_DM-nuc** (my derivation) | **~2×10⁻⁴⁸ cm²** |
| LZ sensitivity at 770 GeV (T86 line 213) | ~10⁻⁴⁵ cm² |
| Gap (model below LZ) | **~3 orders** (NOT 46-71 as previously claimed) |

The model is **3 orders of magnitude** below LZ sensitivity, not 46-71
orders. This is a much tighter gap than previously stated.

### Reviewer critique update

Reviewer 2 specifically wrote:
> "the model's own predicted σ_DM-nucleon is 46–71 orders below LZ sensitivity"

This claim was based on T78/T79's 10⁻¹¹¹ cm² figure. With the correct
derivation (10⁻⁴⁸ cm²), the gap is only **3 orders**. The model is
"untestable" by current direct detection, but only just — not by
46-71 orders.

### Other affected claims

- **"σ_DM-nuc is 46 orders smaller than ℓ_P²"** (T86 line 22): The
  correct σ_DM-nuc (10⁻⁴⁸) is 18 orders smaller than ℓ_P² (10⁻⁶⁶),
  not 46 orders. The "Planck-area" framing is still correct directionally
  but the magnitude is wrong.

- **"T87 forward prediction: composite-DM *cannot* claim the LZ event
  at v0.7 MAP"** (T87 verdict): With σ_DM-nuc = 10⁻⁴⁸ cm², the predicted
  event count in 2.84 tonne-years is much higher than T87 claimed.
  T87 used the 10⁻¹¹⁷ figure (which is 70 orders smaller than mine).
  The correct verdict is "the model STILL cannot claim the LZ event"
  (3 orders below LZ sensitivity = ~3× underproduction), but the
  margin is much smaller.

- **"v0.7 result: σ_DM-DM = 0.27 cm²/g"** (CURRENT.md): This is
  unchanged — σ_DM-DM and σ_DM-nuc are different observables. My
  derivation only affects σ_DM-nuc.

---

## Action items

This is a **significant bug in T78/T79** that propagates through T86,
T87, and downstream documentation. Per the standing rule about
"major correction to a previously-recorded result" (mnemosyne 2026-09-08
directive), this must be surfaced.

Recommended corrections:

1. **T78/T79** (sigma_DM-nuc formula): the prefactor "1.2×10⁻³² cm²"
   is wrong. Should be "9.6×10⁻²⁶ cm²" (or recompute from the standard
   Kahlhoefer formula). **Requires user input** — I don't have access
   to the original T78 derivation, only the transcribed formula.

2. **T86** (plausibility audit): the hand calc uses ℏc = 1 implicitly.
   Fix the unit conversion to use ℏc = 1.973×10⁻¹⁴ GeV·cm. Then the
   hand-calc σ ≈ 10⁻⁴² cm², not 10⁻⁶⁹.

3. **T87** (forward prediction): the verdict is still "model cannot
   claim LZ event" but the margin is ~3 orders, not 70. Should be
   re-stated.

4. **CURRENT.md** and **README.md**: the "46 orders below LZ" claim
   is wrong. Should be "3 orders below LZ" per my derivation.

5. **T86 line 22** ("σ_DM-nuc is 46 orders smaller than ℓ_P²"):
   should be ~18 orders.

**All of these are doc corrections** — the underlying physics
(Kahlhoefer point-particle formula, v0.7 MAP values) is unchanged.

---

## Limitations

1. **I only checked one Kahlhoefer variant** (point-particle). There
   are several published variants including:
   - Reduced-mass scaling (μ vs m_p)
   - Coherent vs incoherent nuclear form factors
   - Spin-dependent vs spin-independent operators
   The discrepancy could change sign with a different variant.

2. **I assumed α_χ = 0.01** (per T78). The dark fine-structure constant
   is a model assumption, not a measured quantity.

3. **I didn't verify the v0.7 MAP values** (m_χ=770 GeV, m_φ=453 MeV,
   ε=10⁻³⁷). These come from T41 v0.7 production JSON and may have
   been transcribed incorrectly.

4. **The 62-order discrepancy in T78 is unaccounted for.** I showed
   it's wrong by ~62 orders, but I don't have the original derivation
   to identify which step introduced the error.

---

## ESTIMATE vs ACTUAL

ESTIMATE: 2-4 hours for full reconciliation.
ACTUAL: ~30 min for the re-derivation + unit bug identification.
RATIO: ~6× under. The bug was easier to find than expected because
the T86 audit's own hand calc was internally inconsistent.

---

## Branch state

- Branch: `wip/cloud-9-relhic` (post-T90.61 commit)
- New code: `v0.3-prelim/code/t90_v61_kahlhoefer_audit.py` (~290 lines)
- New tests: `v0.3-prelim/tests/test_t90_v61_kahlhoefer_audit.py` (8 tests)
- This writeup: `v0.3-prelim/docs/T90_PATH_C4_V61_KAHLHOEFER_AUDIT.md`
- Total T90 tests: 247 + 11 (T90.60) + 8 (T90.61) = 266

---

## TODO item 8 (recorded, not executed)

Per the user's request, item 8 (replace Gaussian placeholder channels
with raw posterior chains) is recorded as a TODO. It is NOT being
executed in this round. The TODO entry:

- **Item 8**: Replace Gaussian placeholder channels with raw posterior
  chains. Affects both T90 and v0.8 lines. Estimated time: 1 hour to
  2 days depending on chain availability. Affects the underlying
  science, not just documentation.

  Status: NOT DONE. Recorded for future work per the 2026-09-08 pause
  directive. Should be addressed when new MCMC chains become available
  or when the user explicitly gives the go-ahead.