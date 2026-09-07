# T90 Magnetic-Moment LZ 248 keV — Consolidated Index

**Status:** Index doc (Path 7 of the 'proceed 1,2 3 4 6 7' plan)
**Date:** 2026-09-07
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Author:** T90 working group

---

## Purpose of this index

The T90 work has grown to ~10 separate docs across multiple
sessions. This index provides a single entry point with brief
abstracts and a reading order. **The individual docs remain
authoritative for their content**; this is a navigation aid.

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

### Part 3: T90 background and context

6. **`T77_LZ_2026_09_UPDATE.md`** — LZ 2026 preprint update
   (added 2026-09-04).

7. **`T78_KINETIC_MIXING_LZ_LINK.md`** — kinetic mixing
   connection between magnetic-moment and dark-photon
   mediators.

8. **`T80_LZ_PAPER_UPDATE.md`** — LZ paper update notes.

9. **`T81_LZ_REVIEW_RESPONSE.md`** — response to LZ paper
   reviewers.

10. **`T87_LZ_FORWARD_PREDICTION.md`** — additional forward
    predictions (different from T90_FORWARD).

---

## Status summary

| Component | Status | Last updated | Commit |
|---|---|---|---|
| Plan (T90_MAGNETIC_MOMENT_PLAN) | current | 2026-09-07 | (in wip/tier3) |
| Forward prediction | current | 2026-09-07 | (in wip/tier3) |
| Cross-detector predictor v10 | SHIPPED | 2026-09-07 | `5d7cc47` |
| Cross-detector follow-ups v11+v12+v13 | SHIPPED | 2026-09-07 | `baf0fa1` |
| Multi-operator v14 | SHIPPED | 2026-09-07 | `f1b4f78` |
| Indirect signals v15 | DRAFT STUB | 2026-09-07 | (in this session) |
| UV completion v16 | DRAFT STUB | 2026-09-07 | (in this session) |
| LZ time-series v17 | DRAFT STUB | 2026-09-07 | (in this session) |
| Repo cleanup (Dockerfile) | SHIPPED | 2026-09-07 | (on wip/cleanup branch) |

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

5. **T90 merge rule binds**: this work stays on
   `wip/tier3-magnetic-moment-LZ` until LZ community
   confirmation (or refutation) of the 248 keV event.

---

## What's still TODO

From the 'proceed 1,2 3 4 6 7' plan:

- **Path 4 (indirect signals)**: DRAFT STUB at
  `v0.3-prelim/code/t90_v15_indirect_signals.py`. Needs the
  Hisano+ 2001 loop calculation for γγ annihilation and
  the Ibe+ 2012 solar-capture formalism.

- **Path 3 (UV completion)**: DRAFT STUB at
  `v0.3-prelim/code/t90_v16_uv_completion.py`. Needs the
  charged-scalar loop formula from Aranda+ 2016.

- **Path 2 (LZ time-series)**: DRAFT STUB at
  `v0.3-prelim/code/t90_v17_lz_time_series.py`. Needs LZ
  data access.

---

## Test summary

| Component | Tests | Status |
|---|---|---|
| v10 predictor | 9/9 | passing |
| v11 posterior | (smoke) | passing |
| v12 detector response | (smoke) | passing |
| v13 other operators | (smoke) | passing |
| v14 calibrated | 5/5 | passing |
| v15-v17 stubs | not yet | TODO |

---

## Branch state

```
f1b4f78 (HEAD) feat(T90.5): v14 — Properly-calibrated multi-operator
baf0fa1 feat(T90.4): v11+v12+v13 — posterior, response, other operators
5d7cc47 feat(T90.4): Path C.4 — Cross-detector predictor
6cc9738 docs(T95): Tidy-up scope audit
...
6cc9738 (start of T95 work on this branch)
```

33 commits on `wip/tier3-magnetic-moment-LZ`. All pushed.
T90 merge rule binds — branch stays off master until LZ
community resolution.

---

## How to cite this work

If citing the T90 program as a whole, use this index. For
specific findings, cite the individual doc. For code, cite
the script (each script has a docstring header with the
relevant doc reference).
