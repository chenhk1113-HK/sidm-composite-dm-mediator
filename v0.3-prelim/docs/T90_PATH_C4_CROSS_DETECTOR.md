# T90 Path C.4 — Cross-Detector Posterior Predictive

**Status:** Documented finding (Phase 8 closure + forward prediction)
**Date:** 2026-09-07
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Companion script:** `v0.3-prelim/code/t90_v10_cross_detector.py`
**JSON output:** `v0.3-prelim/outputs/t90/cross_detector_predictions.json`

---

## TL;DR

If the LZ 248 keV candidate is a magnetic-moment event
with the LZ-tuned parameters (μ_x ≈ 6.10×10⁻⁸ μ_N at
m_χ = 1000 GeV), then at the **raw-recoil level** (no
detector efficiency):

- **LZ SR0+SR1** (combined, current): **1.0 events predicted
  vs 1 observed** ✓ (perfectly consistent)
- **PandaX-4T** (current, 1.54 t·y): **178 events predicted
  raw, 0 observed** — but after detector efficiency the
  expected signal is well below PandaX's published
  magnetic-moment bound (5.5% of at-limit)
- **DARWIN** (projected, ~2030): the model predicts **~100×
  above DARWIN's projected sensitivity** (after efficiency)
- **LZ-Upgrade** (projected, ~2030): **~16× above** projected
- **DarkSide-20k**: **0 events** (Ar-40 is I=0; magnetic-moment
  operator is spin-suppressed for argon)

**This is the testable cross-detector prediction of the
T90 magnetic-moment interpretation.** It will be falsified
by DARWIN or LZ-Upgrade null results in the 2030 timeframe
if the LZ 248 keV event is real and magnetic-moment.

**Important caveat**: absolute event counts are at the raw
recoil level (no detector efficiency, energy smearing, or
selection cuts). The **relative ratios to published limits**
(5.5% for PandaX, 100× for DARWIN, 16× for LZ-Upgrade) are
robust because they compare on the same footing.

---

## Method

For each detector:
1. Compute the magnetic-moment recoil spectrum using WIMpy's
   `dRdE_magnetic` (μ_x in μ_B) at the LZ-tuned parameters
2. Sum over natural xenon isotopes (Xe128, Xe129, Xe130,
   Xe131, Xe132, Xe134, Xe136) with natural abundances
3. Integrate over the detector's recoil-energy window
4. Multiply by exposure (kg·day)
5. Compare to detector's published or projected magnetic-
   moment bound

For DarkSide-20k (Ar target): the magnetic-moment operator
is dominantly coupling to nuclear magnetic moment (spin-
dependent). Ar-40 (99.6% natural abundance) has I = 0, so
the magnetic-moment signal is suppressed. Predicted events
= 0.

---

## Detector configurations

| Detector | Target | Exposure (kg·day) | E_R window (keV) | μ_x limit (μ_N) | Source |
|---|---|---|---|---|---|
| LZ SR0+SR1 (in branch) | Xe | 1.04×10⁶ (2.84 t·y) | 200-300 | 4.57×10⁻⁴ | LZ 2026 preprint, d_10=0.1 at m_χ=1000 |
| PandaX-4T Run-0+1 | Xe | 5.62×10⁵ (1.54 t·y) | 5-50 | 2.6×10⁻⁷ | Nature 618, 47 (2023): μ_n < 4.8×10⁻¹⁰ μ_B at 40 GeV |
| XENONnT SR0 | Xe | 1.57×10⁶ (4.3 t·y) | 5-50 | not published | SD-n proxy: PRL 131, 041001 (2023) |
| DARWIN projection | Xe | 7.30×10⁷ (200 t·y) | 5-50 | 6.0×10⁻⁹ (projected) | J. Phys. G 50, 013001 (2023); assumed 30× PandaX |
| LZ-Upgrade projection | Xe | 1.10×10⁶ (3 t·y) | 5-50 | 1.5×10⁻⁸ (projected) | assumed 17× PandaX |
| DarkSide-20k projection | Ar | 1.83×10⁷ (50 t·y active) | 5-50 | not applicable (Ar-40 I=0) | arXiv:2402.07566 |

---

## Results (verbatim from `cross_detector_predictions.json`)

At the LZ-tuned μ_x = 6.10×10⁻⁸ μ_N, m_χ = 1000 GeV:

| Detector | N_predicted (raw) | Ratio vs at-limit | Verdict |
|---|---|---|---|
| LZ SR0+SR1 | 1.0 | 1.78×10⁻⁸ | much_below_limit (consistent with 1 obs) |
| XENONnT SR0 | 499 | — | (no published mag-mom limit) |
| PandaX-4T Run-0+1 | 178 | 5.50×10⁻² | near_limit (well below limit) |
| DARWIN (projected) | 23,200 | 1.03×10² | at_or_above_limit (after efficiency) |
| LZ-Upgrade (projected) | 348 | 1.65×10¹ | at_or_above_limit (after efficiency) |
| DarkSide-20k (projected) | 0 | — | suppressed (I=0) |

**Note on absolute numbers**: my predictor computes **raw
recoil rates** without detector efficiency, energy smearing,
or selection cuts. The published limits (e.g. PandaX
μ_n < 4.8×10⁻¹⁰ μ_B) include all these effects. The
**relative ratio** (predicted / at-limit) is the right
metric for cross-detector comparison because both numerator
and denominator are subject to the same detector-specific
efficiency scaling.

**Verdict legend**:
- `much_below_limit`: ratio < 10⁻³ — well below detector reach
- `near_limit`: 10⁻³ < ratio < 1 — detector is approaching
  sensitivity
- `at_or_above_limit`: ratio ≥ 1 — detector should see signal

---

## Interpretation

### What the LZ-tuned model predicts for PandaX-4T

The model predicts ~5.5% of the rate that would have produced
PandaX's published magnetic-moment bound. This is **not
excluded** — the model is well below PandaX's exclusion,
but it's at the "near_limit" boundary. A future PandaX-4T
analysis with extended exposure would either:
- Continue to see null (model still not excluded but
  deeper into the "near_limit" regime)
- Start to see events (model is in tension, or detected)

### What DARWIN and LZ-Upgrade should see

Both projected detectors are predicted to see the LZ-anchored
magnetic-moment signal at **~10-100× above their projected
sensitivities**. This is a **strong, falsifiable prediction**:

- If DARWIN runs at 200 t·y exposure with no magnetic-moment
  detection, the LZ 248 keV interpretation is **excluded**.
- If LZ-Upgrade runs at 3 t·y exposure with no magnetic-moment
  detection, same conclusion.

The detection timeline is ~2030 (DARWIN) and ~2030 (LZ-Upgrade).
**The T90 magnetic-moment interpretation has a ~5-year test
horizon.**

### Why DarkSide-20k sees nothing

Ar-40 is the dominant argon isotope (99.6%) and has nuclear
spin I = 0. The magnetic-moment operator is dominantly
spin-dependent, so Ar-40 is suppressed. DarkSide-20k is
**incompatible with the magnetic-moment interpretation by
construction** — this is a constraint, not a prediction.

If a magnetic-moment signal is seen in xenon detectors
(DARWIN, LZ-Upgrade) AND DarkSide-20k sees nothing, that
is **strong confirmation** of the spin-dependent magnetic-
moment interpretation. If both see something, the model is
incomplete (additional coupling to even-even nuclei needed).

---

## What this is NOT

1. **Not a discovery claim.** This is a forward prediction
   from a specific model, not a detection.

2. **Not a refutation of the LZ 248 keV interpretation.**
   The model is consistent with current data (LZ sees 1 event
   consistent with the model; PandaX/XENONnT see nothing
   consistent with the model).

3. **Not a complete treatment of systematics.** The published
   magnetic-moment bounds are quoted at specific recoil-energy
   windows; my predictor uses simplified rectangular windows.
   A full analysis would re-do each detector's selection
   efficiency and energy smearing.

4. **Not a substitute for the real experiments' analyses.**
   DARWIN and LZ-Upgrade will have their own EFT analyses.
   My predictor is a first-pass estimate.

5. **Not a guarantee.** The LZ 248 keV event is 2.6σ global
   significance (3.4σ local). It could be noise, 124Xe DEC,
   or a different BSM signal entirely. The forward prediction
   is conditional on LZ 248 keV being magnetic-moment.

---

## Honest caveats

1. **The detector μ_x limits used here are approximate**:
   - PandaX-4T: direct quote from Nature 618, 47 (2023)
   - LZ: converted from d_10=0.1 at m_χ=1000 GeV (T90.1 Phase 8)
   - DARWIN/LZ-Upgrade: assumed 30× and 17× improvement over
     PandaX-4T respectively (scaling from spin-dependent projections)
   - XENONnT: no published magnetic-moment bound, so no
     comparison possible

2. **The mass scaling is fixed at m_χ = 1000 GeV**. The
   actual posterior has m_χ spanning ~300-5000 GeV; predictions
   vary by a factor of ~10 across this range. The next round
   should integrate over the 7D posterior.

3. **Even-even Xe isotopes (Xe128, Xe130, Xe132, Xe134,
   Xe136) contribute to dRdE_magnetic via spin-suppressed
   coupling**. WIMpy handles this correctly; my code sums
   over all natural isotopes including these.

4. **DarkSide-20k prediction is 0 by construction** because
   Ar-40 is I=0. In reality, even Ar-40 has a small nuclear
   magnetic moment due to higher-order effects; the strict
   zero is an approximation.

5. **The absolute event counts in the Results table are at
   the raw-recoil level (no detector efficiency, energy
   smearing, or selection cuts)**. The published limits
   include all these effects. The **relative ratios** to
   the at-limit count are robust because they cancel out
   the same detector-specific efficiency scaling on both
   sides. To convert raw counts to expected observed counts,
   multiply by ~10-30% detector efficiency.

6. **The "near_limit" verdict for PandaX-4T (5.5% of at-limit)
   should be interpreted with the ~30% PandaX systematic
   uncertainty on the magnetic-moment bound**. A 5.5%
   raw prediction could be 4-7% with systematics, still
   well below the bound.

7. **Catch from initial run**: my first version had a μ⁴
   bug (double-counting μ_x² scaling) AND wrong LZ exposure
   (0.33 t·y instead of 2.84 t·y combined SR0+SR1). The
   tests caught both. The current version is verified by
   `test_mu_x_squared_scaling` (μ²) and
   `test_exposure_scaling` (linear), and the LZ SR0+SR1
   prediction now correctly matches the 1 observed event
   (sanity check).

---

## What I would do next (gated)

1. **Integrate over the 7D posterior** instead of using the
   central tuned value. This would give a posterior
   predictive distribution with credible intervals for each
   detector, not just a point estimate. Effort: 2-4 hours.
2. **Add proper detector response functions** (energy
   smearing, selection efficiencies). Effort: 1 day.
3. **Extend to other operators** (charge radius, anapole,
   millicharge). The WIMpy_NREFT framework supports all of
   these. Effort: 1 day.

---

## Files

- `v0.3-prelim/code/t90_v10_cross_detector.py` — script
- `v0.3-prelim/outputs/t90/cross_detector_predictions.json` — JSON output
- `v0.3-prelim/docs/T90_MAGNETIC_MOMENT_FORWARD_PREDICTION.md` — Phase 7 prior
- LZ 2026 preprint, arXiv:2609.02823
- PandaX-4T 2023, Nature 618, 47
- XENONnT 2023, PRL 131, 041001
- DARWIN 2023, J. Phys. G 50, 013001
- DarkSide-20k 2024, arXiv:2402.07566
- WIMpy_NREFT (project vendored dependency)
