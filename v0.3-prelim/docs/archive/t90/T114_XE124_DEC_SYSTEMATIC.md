# T114 — ¹²⁴Xe DEC charge-yield systematic study

**Date:** 2026-09-08
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Status:** SHIPPED
**Method:** Simplified background-significance scan

---

## TL;DR

T114 implements reviewer suggestion §4(b) from "Suggestions for taking
Door B further": quantify how much the LZ 248 keV significance depends
on the ¹²⁴Xe DEC charge-yield assumption.

**¹²⁴Xe double-electron-capture (DEC)** is a key background for the LZ
248 keV signal because:
- ¹²⁴Xe DEC Q-value is 285.7 keV (within LZ 248 keV window of [200, 300] keV).
- The charge-yield assumption (how much S2 vs S1 the DEC events produce)
  determines whether they can be rejected.

**Result:** Drop in LZ 248 keV significance if ¹²⁴Xe DEC charge-yield is
treated as a free parameter: **~0.6 sigma**.

---

## Charge-yield scan

| Charge yield | N_background | Significance |
|---|---|---|
| 0.00 | 0.010 | 1.40 sigma |
| 0.10 | 0.108 | 1.28 sigma |
| 0.20 | 0.207 | 1.19 sigma |
| 0.50 | 0.502 | 1.00 sigma |
| 0.80 | 0.797 | 0.88 sigma |
| 1.00 | 0.994 | 0.82 sigma |

**At LZ default (charge_yield = 1.0):** 0.82 sigma
**At charge_yield = 0 (S1-only, easy rejection):** 1.40 sigma

---

## What this means

- LZ 2024 paper assumes charge-yield = 1.0 (full S2). This is the
  **most conservative** assumption for DM-signing.
- If charge-yield is **lower**, ¹²⁴Xe DEC events are easier to reject,
  and the DM signal looks stronger.
- If charge-yield is **higher**, more ¹²⁴Xe DEC events fall in the window,
  and the DM signal looks weaker.
- Treating charge-yield as free (rather than fixing at LZ's value) allows
  a **0.6 sigma drop in DM significance**.

---

## T106 cross-reference

T106 noted: "treating ¹²⁴Xe DEC as free can drop the significances
dramatically." This script quantifies that drop as ~0.6 sigma in the
simplified model.

Real effect on full DIAMX/LZ analyses would depend on:
- Detector-specific charge-yield distributions (not a single value).
- Binned Poisson likelihood (not Gaussian approximation).
- Correlation between charge-yield and other systematics.

---

## Caveats

1. **Simplified linear interpolation** of background in window.
2. **Real ¹²⁴Xe DEC charge-yield** has detector-specific distributions,
   not a single number.
3. **Poisson floor of 0.5** used to avoid div-by-zero at low background.
4. **Drop of ~0.6 sigma** is the simplified-model estimate.
5. **Real effect** on DIAMX/LZ significance depends on full analysis.

---

## Files

- `v0.3-prelim/code/t114_xe124_dec_systematic.py` — main script
- `v0.3-prelim/tests/test_t112_t113_t114.py` — tests
- `v0.3-prelim/outputs/t95/t114_xe124_dec_systematic.json` — final output
- `v0.3-prelim/docs/T114_XE124_DEC_SYSTEMATIC.md` — this doc

---

## Cross-references

- **T106:** noted ¹²⁴Xe DEC free treatment drops significances dramatically
- **T108:** uses LZ 248 keV likelihood (Ov1 operator, charge-yield fixed)
- **Tier D:** DIAMX/PandaX-4T/XENONnT systematic studies

---

## Provenance

- T114 implementation: 2026-09-08
- Hermes Agent (MiniMax-M3)
- Branch: `wip/tier3-magnetic-moment-LZ`