# V19.2-E D — Machine-generated canonical numbers (ClawsGO B.2)

**Date:** 2026-10-09
**Status:** INTEGRATION LAYER
**Author:** Hermes (per ClawsGO comment #5 B.2)

## What this is

Per ClawsGO comment #5 B.2: "The project already claims `constants.py`
as 'single source of truth' and has a drift-guard audit. Extend it:
channel counts, the trade-off factor, σ_eff values, and the 'N first-
class results' number should be *computed* from one file and injected
into the docs, so a corpus that says four different things about one
quantity becomes impossible. This ends the entire drift class, which
has consumed most of the last six rounds."

This commit adds two scripts:
- `scripts/canonical_numbers.py` — computes all headline numbers from
  `constants.py` + `T205_full_likelihood_published.OBS_PUBLISHED`
- `scripts/drift_guard.py` — reads the canonical JSON and flags any
  deviation in the headline docs

## Canonical numbers (output of `scripts/canonical_numbers.py`)

```
v19.2-D canonical (Phase 44 free fit):
  PASS: 1, MARGINAL: 0, FAIL: 7
  Headline: 1 of 8 channels pass
  Cloud-9 factor below 50: 3.4x
  SPARC factor below 0.19: 42.1x
  dSph v=15 factor above ceiling: 7.8x
  UFD v=3 factor above ceiling: 25.7x

v19.2-E A.2 5-param DE best-fit:
  PASS: 5, MARGINAL: 2, FAIL: 1
  Headline: 5 of 8 channels pass
  Cloud-9 factor below 50: 0.3x
  SPARC factor below 0.19: 82.6x
  dSph v=15 factor above ceiling: 0.7x
  UFD v=3 factor above ceiling: 1.0x

Halo-specific gravothermal prefactors (vs Yang+ 2024 150*C):
  BM2 cluster: 1.82x
  Cosmo-501 dwarf: 2.2x
  Fornax dSph: 18.7x
  Segue 1 UFD: 4.0x
```

## Drift-guard (output of `scripts/drift_guard.py`)

The drift-guard currently checks:
1. **Pass count** in headline docs (PAPER, README, CURRENT, FINDINGS,
   CITATION_AUDIT, TRANSITION) — should match the canonical v19.2-E A.2
   headline of "5 of 8 channels pass"
2. **SPARC factor** — should match the canonical v19.2-E A.2 value
   (82.6x) or the v19.2-D canonical value (42.1x) within 15%
3. **Halo-specific prefactors** (Fornax 18.7x, Segue 1 4.0x, BM2 1.82x,
   Cosmo-501 2.2x) — should match within 20% in gravothermal context
4. **First-class structural findings** count — should match the
   v19.2-D freeze (2)

The drift-guard does **not** check:
- CHANGELOG (historical record by design)
- Per-round working docs (A.1, A.2 stress, A.2 8ch, B, C) for pass count
  (these legitimately report different numbers)
- Channel denominator drift (handled by section A.15 in the paper)
- THEOREM vs Result naming (handled by R88(87) freeze)

## Current drift-guard status

```
$ python scripts/drift_guard.py
Canonical headline: v19.2-E A.2 5-param DE best-fit:
  PASS count: 5
  SPARC factor below 0.19: 82.6x
  First-class structural findings (v19.2-D freeze): 2
  Halo-specific prefactors:
    BM2 cluster: 1.82x
    Cosmo-501 dwarf: 2.2x
    Fornax dSph: 18.7x
    Segue 1 UFD: 4.0x
======================================================================
RESULT: No drift detected. All docs consistent with canonical numbers.
======================================================================
```

The drift-guard **passes** at the current commit. The headline docs
(PAPER, README, CURRENT, FINDINGS, CITATION_AUDIT, TRANSITION) are
all consistent with the canonical v19.2-E A.2 numbers.

## Files

- `scripts/canonical_numbers.py` (13.7 KB)
- `scripts/drift_guard.py` (10.5 KB)
- `v0.3-prelim/data/results/canonical_numbers.json` (output)
- This document (`docs/V19_2_E_D_CANONICAL_NUMBERS.md`)

## Usage

```bash
# 1. Compute canonical numbers from constants.py and OBS_PUBLISHED
python scripts/canonical_numbers.py

# 2. Run drift-guard to check docs for stale numbers
python scripts/drift_guard.py            # reports drift, exits 0
python scripts/drift_guard.py --strict   # reports drift, exits 1 on drift
```

The drift-guard is the integration layer: it makes the "single source
of truth" property **enforced**, not just declared. Future R88 rounds
that change `constants.py` or add new channel constraints should re-run
`canonical_numbers.py` and the drift-guard will flag any docs that
were not updated.

## Honest limitations

1. **The drift-guard heuristics are imperfect.** It uses keyword
   matching to skip retraction/overclaim/historical contexts, but
   some new false-positive patterns may emerge. The current
   implementation has been tested against the existing docs and
   passes cleanly.

2. **The drift-guard only checks a subset of all numbers.** It
   doesn't check σ_peak sensitivity (paper §2.6, §A.14), gravothermal
   t_core values for Fornax, Lei/Wang upper bounds, or other
   paper-specific quantities. Adding more checks is straightforward
   (add a function to `drift_guard.py`) but requires careful
   heuristic tuning to avoid false positives.

3. **The canonical JSON is overwritten on each run.** It is
   effectively build-time output, not a committed artifact. If
   `constants.py` changes, the JSON changes, and the drift-guard
   will flag any docs that don't match the new values.

4. **The drift-guard doesn't check the PAPER's "5/8" headline yet.**
   The paper's headline is in the abstract, which has been updated
   in A.2 to "two first-class structural results" (no pass count
   in the abstract). The drift-guard checks the "5/8 channels pass"
   patterns in the body, which are present in section §9.17a, §A.15,
   etc. — these are consistent with the canonical v19.2-E A.2 result.

## Reference

- ClawsGO comment #5 (2026-10-09), Part B.2
- `scripts/constants.py` (single source of truth for σ_0, a_slope,
  σ_peak, v_target, σ_1, F_H_CANONICAL)
- `v0.3-prelim/code/T205_full_likelihood_published.py` (OBS_PUBLISHED
  with 8 channels and published σ_unc)
- v19.2-E A.1 (real-likelihood promotion, 1/8 result)
- v19.2-E A.2 (5-param DE best-fit, 5/8 result)
- v19.2-E B (per-halo gravothermal calibration, Fornax + Segue 1)
- v19.2-E C (data-only σ/m(v) constraint, 2/4 result)
