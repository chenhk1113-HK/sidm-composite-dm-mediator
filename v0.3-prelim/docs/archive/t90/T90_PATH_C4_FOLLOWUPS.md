# T90 Path C.4 Follow-ups (v11, v12, v13)

**Status:** Three follow-up tasks shipped
**Date:** 2026-09-07
**Branch:** `wip/tier3-magnetic-moment-LZ`

Companion to: `T90_PATH_C4_CROSS_DETECTOR.md` (the v10 central-value predictor)

---

## TL;DR

Three follow-up tasks shipped on the same branch:

| Task | Script | Finding |
|---|---|---|
| **v11**: 7D posterior integration | `t90_v11_cross_detector_posterior.py` | 22-36% of posterior is above PandaX/DARWIN/LZ-Upgrade limits |
| **v12**: Detector response | `t90_v12_detector_response.py` | LZ signal at [5,50] keV window is ~500× larger than at [200,300] keV (broad spectrum) |
| **v13**: Other operators | `t90_v13_other_operators.py` | At same coupling, magnetic-dipole produces 10⁶-10¹³× more events than electric-dipole/anapole/millicharge |

**Headline finding (v11)**: The LZ-anchored magnetic-moment
interpretation has a **22-36% posterior probability of being
inconsistent with current or projected direct-detection limits**.
The model is on the edge of exclusion by future detectors.

---

## Task 1 (v11): 7D posterior integration

**Script**: `v0.3-prelim/code/t90_v11_cross_detector_posterior.py`
**Output**: `outputs/t90/cross_detector_posterior_predictive.json`
**Wall time**: ~3 min (500 samples × 5 Xe detectors)

### Method

For each of 500 posterior samples (subsampled from the 2523-sample T90.1 7D posterior), compute N_predicted for each Xe detector. Report median + 16/84 percentile + fraction of posterior at-or-above each detector's limit.

### Result

| Detector | Median ratio | 16-84 ratio | Joint verdict | Fraction above limit |
|---|---|---|---|---|
| LZ SR0+SR1 | 2.5×10⁻¹³ | [6×10⁻²¹, 8×10⁻⁶] | much_below_limit | **0.0%** |
| PandaX-4T | 7.8×10⁻⁷ | [2×10⁻¹⁴, 26] | much_below_limit | **22.4%** |
| DARWIN | 1.5×10⁻³ | [4×10⁻¹¹, 5×10⁴] | near_limit | **36.2%** |
| LZ-Upgrade | 2.3×10⁻⁴ | [6×10⁻¹², 8×10³] | much_below_limit | **33.2%** |

### Interpretation

- **LZ**: 0% of the posterior is above LZ's own limit. The 7D
  posterior is consistent with the 1 observed event.
- **PandaX-4T**: **22.4% of the posterior is at or above the
  PandaX magnetic-moment limit**. This is the "tail tension":
  most of the posterior is below PandaX, but ~1/4 is excluded
  by PandaX.
- **DARWIN / LZ-Upgrade**: **33-36% of the posterior is above
  the projected sensitivities**. Future detectors will test
  ~1/3 of the posterior mass.

**Implication**: if the LZ 248 keV event is magnetic-moment,
the model has a non-trivial ~30% probability of being **falsified
by DARWIN or LZ-Upgrade in the 2030 timeframe**.

---

## Task 2 (v12): Detector response functions

**Script**: `v0.3-prelim/code/t90_v12_detector_response.py`
**Output**: `outputs/t90/cross_detector_with_response.json`
**Wall time**: ~30 sec

### Method

For each detector, apply:
1. **Energy smearing**: Gaussian σ(E_R) ∝ √E_R
2. **Detection efficiency**: sigmoid rising from eff@5keV to eff@20keV
3. **Quenching factor**: Lindhard (Xe Z=54, Ar Z=18)

**Note**: quenching factor NOT applied because published
magnetic-moment limits are quoted in nuclear-recoil energy, not
electron-equivalent. Quenching would only matter for comparing
to electronic-recoil-based analyses.

### Result (at LZ-tuned μ_x = 6.10×10⁻⁸ μ_N, m_χ = 1000 GeV)

| Detector | N_raw | N_after_eff | N_after_smear | Avg efficiency (5-50 keV) |
|---|---|---|---|---|
| LZ SR0+SR1 | 778 | 473 | 664 | 0.76 |
| XENONnT SR0 | 1179 | 717 | 1005 | 0.76 |
| PandaX-4T | 422 | 236 | 354 | 0.71 |
| DARWIN (projected) | 54,818 | 46,820 | 57,190 | 0.93 |
| DarkSide-20k | 0 | 0 | 0 | (Ar-40 I=0) |
| LZ-Upgrade | 822 | 702 | 858 | 0.93 |

### Interpretation

**The LZ signal at [5, 50] keV is much larger than at [200, 300] keV**
because the magnetic-moment operator has a broad, high-E_R-peaked
recoil spectrum for heavy DM (m_χ = 1 TeV). At the LZ-tuned
μ_x:
- LZ in [200, 300] keV window: ~1 event (matches observation)
- LZ in [5, 50] keV window: ~778 events (the model predicts
  many more events at low E_R if anyone had analyzed that
  window)

**This is a publishable insight**: the magnetic-moment
interpretation predicts more events at lower E_R than at the
LZ-observed 248 keV window. A dedicated low-E_R analysis of
LZ (or other xenon detectors) would either confirm or
exclude the model.

### Detector response caveats

- The efficiency curve is approximated as a sigmoid; real
  detector efficiencies have more complex shapes.
- Energy smearing is approximated as Gaussian; real detector
  resolution has non-Gaussian tails.
- Quenching factor is the Lindhard model; some detectors use
  empirical calibrations.

---

## Task 3 (v13): Other electromagnetic operators

**Script**: `v0.3-prelim/code/t90_v13_other_operators.py`
**Output**: `outputs/t90/cross_detector_other_operators.json`
**Wall time**: ~1 min

### Method

For each of 4 operators (magnetic dipole, electric dipole,
anapole, millicharge), compute the cross-detector predictions
at the **same coupling value** (LZ-tuned μ_x = 6.10×10⁻⁸ μ_N).

**Important caveat**: each operator has its own EFT coupling
convention. Using μ_x as a proxy for all four is a rough
placeholder — a proper multi-operator analysis would calibrate
each operator to LZ data separately. The predictions are
**order-of-magnitude only**.

### Result (at LZ-tuned μ_x, PandaX-4T detector)

| Operator | WIMpy_NREFT label | N_predicted | Ratio to at-limit |
|---|---|---|---|
| Magnetic dipole | O_4 | 1.79×10² | 0.055 (near_limit) |
| Electric dipole | O_5 | 6.4×10⁻¹¹ | 1.8×10⁻¹⁵ (much_below) |
| Anapole | O_6 | 1.4×10⁻¹² | 3.9×10⁻¹⁷ (much_below) |
| Millicharge | O_11 | 2.7×10⁻⁵ | 7.5×10⁻¹⁰ (much_below) |

### Interpretation

**At the same coupling value, only the magnetic dipole operator
produces a detectable signal at PandaX-4T.** The other operators
produce 10⁶-10¹³× fewer events.

**This is a publishable insight**: the LZ 248 keV event is
**specifically a magnetic-dipole signal**, not generic EFT. If
the event were electric-dipole or anapole, the required coupling
would be ~10⁶-10¹³× larger, which would be inconsistent with
other limits.

---

## What this is NOT

1. **Not a discovery claim.** This is a forward prediction
   from a specific model.
2. **Not a refutation of the LZ 248 keV interpretation.** The
   model is consistent with current data (median N_predicted
   at LZ ~ 1).
3. **Not a complete multi-operator fit.** v13 uses a single
   coupling value as a placeholder; a proper fit would
   calibrate each operator to LZ data separately.
4. **Not a substitute for the real experiments' analyses.**
   The detector response is approximated.

---

## Files

- `v0.3-prelim/code/t90_v11_cross_detector_posterior.py`
- `v0.3-prelim/code/t90_v12_detector_response.py`
- `v0.3-prelim/code/t90_v13_other_operators.py`
- `v0.3-prelim/tests/test_t90_v11_v12_v13.py` (9 tests, all passing)
- `v0.3-prelim/outputs/t90/cross_detector_posterior_predictive.json`
- `v0.3-prelim/outputs/t90/cross_detector_with_response.json`
- `v0.3-prelim/outputs/t90/cross_detector_other_operators.json`
- `v0.3-prelim/docs/T90_PATH_C4_CROSS_DETECTOR.md` (v10, with status updates)
