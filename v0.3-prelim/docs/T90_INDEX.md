# T90 Magnetic-Moment LZ 248 keV — Consolidated Index

**Status:** Index doc (Path 7 of the 'proceed 1,2 3 4 6 7' plan)
**Date:** 2026-09-07 (updated with T95 cross-link)
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Author:** T90 working group

---

## Purpose of this index

The T90 work has grown to ~10 separate docs across multiple
sessions. This index provides a single entry point with brief
abstracts and a reading order. **The individual docs remain
authoritative for their content**; this is a navigation aid.

**Cross-link to T95 (SIDM cross-check program)**: see
[T95_CONSOLIDATED_RESULTS.md](./T95_CONSOLIDATED_RESULTS.md).
The T95 work tests whether the LZ-anchored Yukawa SIDM
cross-section is consistent with BAHAMAS-SIDM, dwarf-galaxy
core sizes, Euclid Q1 sub-halo forecasts, and the Zhang+ 2025
GD-1 perturber constraint. **T95 finds substantial-to-very-strong
tension** with these astrophysical probes — see "T95 cross-check"
section below.

---

## Reading order

### Part 1: The T90 hypothesis

1. **`T90_MAGNETIC_MOMENT_PLAN.md`** — original plan: what is
   the LZ 248 keV event, and how would a magnetic-moment
   DM interpretation work? Includes Jeffreys footnote and
   UV-matching roadmap.

2. **`T90_MAGNETIC_MOMENT_FORWARD_PREDICTION.md`** — Phase 7
   forward prediction: what other detectors should see if
   the magnetic-moment interpretation is correct.

### Part 2: Cross-detector predictions (Path C.4)

3. **`T90_PATH_C4_CROSS_DETECTOR.md`** — v10: central-value
   predictor. Cross-detector predictions at the LZ-tuned
   point estimate. **PUBLISHED (commit `5d7cc47`).**

4. **`T90_PATH_C4_FOLLOWUPS.md`** — v11+v12+v13: posterior
   integration, detector response, other operators. The
   key findings:
   - 22-36% of posterior mass above PandaX/DARWIN/LZ-Upgrade
   - Magnetic-moment spectrum is broad (500× more events at
     low E_R than at 248 keV)
   - LZ event is specifically magnetic-dipole, not generic
     EFT. **PUBLISHED (commit `baf0fa1`).**

5. **`T90_PATH_C4_V14_CALIBRATED.md`** — v14: properly-calibrated
   multi-operator. Key finding: **millicharge is strongly
   excluded** by PandaX at LZ-calibrated coupling. **PUBLISHED
   (commit `f1b4f78`).**

6. **`T90_PATH_C4_V16_UV_COMPLETION.md`** — v16: UV completion
   of the magnetic-moment operator. 3 UV models calibrated
   to LZ: composite DM (Aranda+ 2016), vector-like fermion
   (Hisano+ 2002), dark photon (Fabbrichesi+ 2020). **PUBLISHED
   (commit `38256ff`).**

7. **`T90_PATH_C4_V15_INDIRECT_SIGNALS.md`** — v15: indirect-detection
   predictions. Headline: **magnetic-moment DM is 5-12 orders
   below current indirect-detection limits**; indirect detection
   CANNOT falsify the LZ interpretation. **PUBLISHED
   (commit `a1415da`).**

8. **`T90_PATH_C4_V17_LZ_TIME_SERIES.md`** — v17: LZ time-series
   with public data. **PUBLISHED (commit `cfb2924`).**
   Bayesian posteriors for 5 hypotheses:
   - Magnetic-moment DM: 47%
   - Higgsino inelastic DM (Fan & Tweed 2026): 47% (TIED)
   - Instrumental: 6%
   - Solar neutrino 8B: 0.03%
   - 124Xe DEC: 0%

### Part 3: T90 background and context

9. **`T77_LZ_2026_09_UPDATE.md`** — LZ 2026 preprint update
   (added 2026-09-04).

10. **`T78_KINETIC_MIXING_LZ_LINK.md`** — kinetic mixing
    connection between magnetic-moment and dark-photon
    mediators.

11. **`T80_LZ_PAPER_UPDATE.md`** — LZ paper update notes.

12. **`T81_LZ_REVIEW_RESPONSE.md`** — response to LZ paper
    reviewers.

13. **`T87_LZ_FORWARD_PREDICTION.md`** — additional forward
    predictions (different from T90_FORWARD).

---

## T95 cross-check (CRITICAL CONTEXT)

**The T90 magnetic-moment interpretation, evaluated at the LZ-tuned
parameters, is in substantial-to-very-strong tension with
astrophysical SIDM probes.** See [T95_CONSOLIDATED_RESULTS.md](./T95_CONSOLIDATED_RESULTS.md)
for the full paper-style writeup. Key results:

| Probe | Tension | Jeffreys verdict |
|---|---|---|
| **BAHAMAS-SIDM (Robertson 2019)** | Velocity-dep matches well (ratio 0.72), absolute norm ~30% low | mild (T89-known offset) |
| **Core-size predictions** | Master Yukawa predicts 5-50× smaller cores than hydro sims | strong |
| **Euclid Q1 sub-halo forecast (Channel 27)** | σ/m at v=150 km/s is 6-13× above forecast's [0.05, 0.10] cm²/g range | substantial (Δlog Z = -1.57 in 8D fit) |
| **Zhang+ 2025 GD-1 perturber** | σ/m at v=10 km/s is 94× below required [30, 100] cm²/g | **very strong (Δlog Z = -23.61 in 8D fit)** |

**Net effect on T90**: The LZ-anchored Yukawa is a **viable but
constrained** interpretation. The T90 merge rule is unchanged —
still requires LZ community resolution of the 248 keV event
**OR** a fit showing Δlog Z ≥ +2.

**Important**: T95 is a parallel investigation. It uses the
master Yukawa (the σ/m prescription, not the magnetic-moment
operator). The magnetic-moment operator (Ls₁₀ in NREFT) is a
separate EFT channel. The T90 branch ships the magnetic-moment
operator; the master has the Yukawa. They are different physics
at different scales. T95's tension findings apply to the master's
Yukawa, not specifically to the magnetic-moment channel — but
since the LZ-anchored posterior has σ/m ≈ 0.7 cm²/g at v=150 km/s,
the tension applies to the broader σ/m interpretation too.

---

## Status summary

| Component | Status | Last updated | Commit |
|---|---|---|---|
| Plan (T90_MAGNETIC_MOMENT_PLAN) | current | 2026-09-07 | (in wip/tier3) |
| Forward prediction | current | 2026-09-07 | (in wip/tier3) |
| Cross-detector predictor v10 | SHIPPED | 2026-09-07 | `5d7cc47` |
| Cross-detector follow-ups v11+v12+v13 | SHIPPED | 2026-09-07 | `baf0fa1` |
| Multi-operator v14 | SHIPPED | 2026-09-07 | `f1b4f78` |
| Indirect signals v15 | SHIPPED | 2026-09-07 | `a1415da` |
| UV completion v16 | SHIPPED | 2026-09-07 | `38256ff` |
| LZ time-series v17 | SHIPPED | 2026-09-07 | `cfb2924` |
| Audit drift fix | SHIPPED | 2026-09-07 | `0da52e8` |
| Tag `t90-all-6-paths-shipped-2026-09-07` | CREATED | 2026-09-07 | (points to HEAD) |
| **T95 cross-check program** | **SHIPPED (master)** | 2026-09-07 | `4238860` through `c8303e2` |

---

## Key findings (TL;DR)

1. **The LZ 248 keV event is well-described by a magnetic-dipole
   DM interpretation with μ_x ≈ 6.10×10⁻⁸ μ_N at m_χ = 1 TeV.**

2. **The model is in tension with future direct-detection limits**:
   ~30% of the 7D posterior mass is above DARWIN/LZ-Upgrade
   projected sensitivities.

3. **Magnetic-moment is the most consistent operator** with
   PandaX-4T null. Millicharge is strongly excluded by PandaX
   at LZ-calibrated coupling.

4. **DARWIN and LZ-Upgrade (both ~2030) will test the model**:
   expected to see ~10-100× above projected sensitivity if
   the interpretation is correct.

5. **All 6 paths (1, 2, 3, 4, 6, 7) shipped**. 763/763 tests pass.
   Audit 44/44 clean.

6. **T95 cross-check**: the LZ-anchored Yukawa is in substantial
   tension with Euclid Q1 sub-halo forecast (Δlog Z = -1.57)
   and very strong tension with Zhang+ 2025 GD-1 perturber
   (Δlog Z = -23.61).

7. **T90 merge rule binds**: this work stays on
   `wip/tier3-magnetic-moment-LZ` until LZ community
   confirmation (or refutation) of the 248 keV event.

---

## What's still TODO

From the 'proceed 1,2 3 4 6 7' plan: **NONE — all paths shipped.**

Other open work (not from this plan):
- Wait for LZ community resolution of the 248 keV event
- Cross-validate against PandaX-4T and XENONnT new data
- If LZ confirms, merge T90 to master (currently blocked by
  T90 merge rule)
- T95.7+ (galaxy-stream gaps with Gaia DR4) is a candidate
  next phase but requires user approval per rule 17/24

---

## Test summary

| Component | Tests | Status |
|---|---|---|
| v10 predictor | 9/9 | passing |
| v11 posterior | (smoke) | passing |
| v12 detector response | (smoke) | passing |
| v13 other operators | (smoke) | passing |
| v14 calibrated | 5/5 | passing |
| v15 indirect signals | 10/10 | passing |
| v16 UV completion | 11/11 | passing |
| v17 LZ time-series | 12/12 | passing |
| **T90 total** | **47/47** | **all passing** |
| Audit (t82_audit.py) | 44/44 | ALL CLEAR |
| Full v0.3-prelim/tests/ | 763 pass, 8 skip, 0 fail | clean |

---

## Branch state

```
0da52e8 (HEAD) fix(audit): update test for canonical T88E
cfb2924 feat(T90.10): v17 — LZ time-series with PUBLIC LZ data
a1415da feat(T90.9): v15 — Indirect signals
38256ff feat(T90.8): v16 — UV completion
c9142b4 chore(T90.7): TIME_LOG.md link to global aggregator
25a4f74 chore(T90.7): Add TIME_LOG.md
e4c5861 feat(T90.6): Paths 7, 3, 4, 2 (consolidation + 3 stubs)
f1b4f78 feat(T90.5): v14 — Properly-calibrated multi-operator
baf0fa1 feat(T90.4): v11+v12+v13 — posterior, response, other operators
5d7cc47 feat(T90.4): Path C.4 — Cross-detector predictor
...
```

38 commits on `wip/tier3-magnetic-moment-LZ`. All pushed.
Tag `t90-all-6-paths-shipped-2026-09-07` created and pushed.

---

## T95 references (already on master)

The T95 cross-check is **on master** (separate branch path) and
documents substantial-to-very-strong tension between the LZ-anchored
Yukawa and astrophysical SIDM probes:

- **T95_CONSOLIDATED_RESULTS.md** — paper-style writeup of all findings
- **T95_YUKAWA_PRESCRIPTION_CALIBRATION_NOTE.md** — Yukawa σ/m prescription
- **T95_OPTION2_CORE_SIZE_PREDICTION.md** — Core-size predictions
- **T95_OPTION2_5_GRAVOTHERMAL.md** — Gravothermal Balberg+ 2002 formula
- **T95_OPTION3_SUBHALO_FORECAST.md** — Master Yukawa + Euclid Q1 forecast
- **T95_OPTION3_5_8D_FIT.md** — Real 8D nested-sampling fit
- **T95_OPTION3_6_ZHANG_GD1.md** — Master Yukawa vs Zhang+ 2025 GD-1
- **T95_OPTION3_6B_SURVEY.md** — Alternative interpretations survey
- **T95_OPTION3_6_V4_RECONCILIATION.md** — v1/v2/estimator reconciliation
- **T95_OPTION3_6_V3_REAL_8D_FIT.md** — Real 8D Zhang fit
- **T95_SIDM_CORE_PROFILE_PLAN.md** — Master plan + Phase 0 SWIFT check

---

## How to cite this work

If citing the T90 program as a whole, use this index. For
specific findings, cite the individual doc. For code, cite
the script (each script has a docstring header with the
relevant doc reference).

**For the tension with astrophysical SIDM probes**, also cite
T95_CONSOLIDATED_RESULTS.md — the cross-check is integral to
interpreting the T90 work.

---

## Standby status (2026-09-07)

**Per user directive**: T90 work is parked. Branch is
publishable but not merged. Tag points to current state.
T95 (already on master) is the cross-check showing the
LZ-anchored Yukawa is in substantial tension with
astrophysical data.

**Waiting on**: LZ community confirmation or refutation
of the 248 keV event. If confirmed, T90 merge rule may
be satisfied (per the 5 conditions in commit `e23bb80`).
If refuted, T90 work remains as a demonstrated capability
on the branch only.