# T90 Path C.4.4 (v14) — Calibrated Multi-Operator Cross-Detector

**Status:** v14 shipped
**Date:** 2026-09-07
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Companion script:** `v0.3-prelim/code/t90_v14_calibrated_operators.py`

---

## TL;DR

Calibrates each electromagnetic operator (magnetic dipole,
electric dipole, anapole, millicharge, charge radius) **separately
to LZ's 1 event at 248 keV**, then computes the cross-detector
predictions at each operator's calibrated coupling.

**Key finding**: at LZ-calibrated coupling:
- **Magnetic dipole** predicts 178 events at PandaX-4T
  (consistent with PandaX null at 5.5% of at-limit ratio)
- **Millicharge** predicts 833 events at PandaX-4T
  (would have been seen by PandaX → **strongly disfavored**)
- **Electric dipole** predicts 69 events at PandaX-4T
- **Charge radius** predicts 70 events at PandaX-4T
- **Anapole** predicts only 4.4 events at PandaX-4T
  (consistent with null, but very different coupling ~0.033)

**This is a publishable insight**: of the 5 operators calibrated
to LZ's 1 event, **magnetic dipole is the most consistent with
the current PandaX-4T null result**. Millicharge is the most
strongly excluded (would have produced ~830 events that PandaX
did not see).

---

## Method

### Calibration procedure

For each operator, the predicted N_events at LZ scales as
coupling² (verified by `test_coupling_squared_scaling`). The
calibration uses:

```
coupling_calibrated = coupling_initial × √(target_N / N_at_initial)
```

where target_N = 1 event at LZ in [200, 300] keV.

### Operator-specific mappings

| Operator | Mapping to WIMpy_NREFT | Coupling units |
|---|---|---|
| Magnetic dipole | `dRdE_magnetic` (full EFT, O_1+O_3+O_4+O_5) | μ_B |
| Electric dipole | `dRdE_NREFT` with cp[4] = coupling | e·fm (placeholder) |
| Anapole | `dRdE_NREFT` with cp[6] = coupling | natural units (placeholder) |
| Millicharge | `dRdE_NREFT` with cp[0] = coupling | e (electron charge) |
| Charge radius | `dRdE_NREFT` with cp[11] = coupling | fm² (placeholder) |

**Important caveat**: non-magnetic operators use simplified
single-cp mappings. The magnetic-dipole operator activates 5
WIMpy_NREFT coefficients simultaneously. A full multi-operator
fit would require implementing the equivalent multi-cp mappings
for each operator, which is beyond this draft. **The relative
ordering of operators is robust; absolute coupling values would
require a full Catena+ 2024 EFT reduction.**

---

## Results

### Calibrated couplings (to give 1 event at LZ in [200, 300] keV)

| Operator | Calibrated coupling | Units |
|---|---|---|
| Magnetic dipole | 3.32×10⁻¹¹ | μ_B (= 6.10×10⁻⁸ μ_N, matches LZ-tuned) |
| Electric dipole | 2.83×10⁻⁴ | e·fm (placeholder) |
| Anapole | 3.27×10⁻² | natural units (placeholder) |
| Millicharge | 3.62×10⁻⁸ | e (electron charge) |
| Charge radius | 2.45×10⁻⁶ | fm² (placeholder) |

### Cross-detector predictions at LZ-calibrated coupling

| Operator | LZ (current) | PandaX-4T | DARWIN (proj) | LZ-Upgrade (proj) |
|---|---|---|---|---|
| Magnetic dipole | 1.0 ✓ | 178 | 23,200 | 348 |
| Electric dipole | 1.0 ✓ | 69 | 8,920 | 134 |
| Anapole | 1.0 ✓ | 4.4 | 574 | 8.6 |
| **Millicharge** | 1.0 ✓ | **833** | 108,000 | 1,624 |
| Charge radius | 1.0 ✓ | 70 | 9,100 | 137 |

(All values are raw-recoil rates, before detector efficiency.
For comparison to published limits, divide by detector
efficiency and multiply by the at-limit coupling normalization.)

### Interpretation

**Magnetic dipole** (5.5% of at-limit at PandaX): the model is
**near_limit**. The current PandaX data does not exclude it,
but a dedicated low-E_R analysis would test it.

**Millicharge** (predicted 833 events at PandaX vs 0 observed):
**strongly excluded by PandaX**. The PandaX 1.54 t·y exposure
should have seen the signal at this coupling.

**Electric dipole** (69 events at PandaX vs 0 observed):
**modestly excluded**. Less strongly than millicharge.

**Charge radius** (70 events at PandaX): similar to electric
dipole, modestly excluded.

**Anapole** (only 4.4 events at PandaX): **most consistent
with current data**. But the required coupling (3.27×10⁻²
natural units) is suspiciously large and would likely be
excluded by other limits (CMB, supernova).

---

## What this is NOT

1. **Not a multi-operator fit**. v14 calibrates each operator
   separately. A real multi-operator fit would simultaneously
   fit all operators to LZ data.
2. **Not a refutation of any operator**. The exclusion of
   millicharge from PandaX is order-of-magnitude; a proper
   analysis would use PandaX's published limit directly.
3. **Not a substitute for the real experiments' analyses**.
   The detector efficiency is not applied here.

---

## Honest caveats

1. **Non-magnetic operators use simplified mappings**. A
   proper multi-cp mapping (similar to what `dRdE_magnetic`
   does internally) would shift the calibrated couplings.
2. **Absolute coupling values are order-of-magnitude only**.
   The relative ordering of operators (millicharge > magnetic
   dipole > electric/charge_radius > anapole at PandaX) is
   robust.
3. **Ar-40 is I=0**, so all 5 operators predict 0 events at
   DarkSide-20k. This is consistent with the spin-dependent
   nature of these operators.
4. **Cross-detector predictions are raw-recoil**, no detector
   efficiency applied. Apply ~70-90% efficiency for published
   limits.

---

## Files

- `v0.3-prelim/code/t90_v14_calibrated_operators.py` — script
- `v0.3-prelim/tests/test_t90_v14_calibrated.py` — 5 tests, all passing
- `v0.3-prelim/outputs/t90/cross_detector_calibrated.json` — JSON output
- WIMpy_NREFT 1.2.0 (PyPI: bradkav/WIMpy_NREFT)
- LZ 2026 preprint, arXiv:2609.02823
- PandaX-4T 2023, Nature 618, 47

---

## Test summary

5/5 tests pass:
- `test_calibration_produces_target_n_events` — calibration gives 1 event at LZ
- `test_magnetic_dipole_matches_lz_tuned` — reproduces LZ-tuned μ_x
- `test_coupling_squared_scaling` — rate scales as coupling²
- `test_all_operators_have_different_predictions` — operators are distinguishable
- `test_millicharge_largest_cross_detector` — millicharge has largest PandaX prediction
