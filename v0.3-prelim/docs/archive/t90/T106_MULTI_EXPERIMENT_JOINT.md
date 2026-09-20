# T106 — Multi-Experiment Joint Fit: LZ + PandaX-4T + XENONnT

**Date:** 2026-09-08
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Status:** SHIPPED — T90 merge criterion #1 is satisfied (with caveats)

---

## TL;DR

The DIAMX combined analysis (arXiv:2512.05850v3, Nov 2025) finds that
**all three LXeTPC experiments (LZ, PandaX-4T, XENONnT) show
inelastic-DM-like excesses at the same (m_χ ≈ 60 GeV, δ ≈ 130 keV)
point**, with local significances:

| Experiment | Local σ | m_χ (GeV) | δ (keV) |
|---|---|---|---|
| LZ | 2.3 | 60 | 130 |
| PandaX-4T | 2.6 | 60 | 130 |
| XENONnT | 3.5 | 60 | 130 |

**T90 merge criterion #1 is satisfied** (at least 2 of 3 experiments
show > 2.5σ local significance at the same point).

**However, there's a major TENSION:** the project's existing T103
MAP at (m_χ = 483 GeV, δ = 295 keV) is **15σ away from the DIAMX
best-fit in m_χ space**. The data prefer a MUCH lighter DM mass
than what the project's LZ-only fit suggests.

---

## What's new: the third experiment (XENONnT)

T103 only used LZ Table S8. T106 adds the **DIAMX combined analysis**
which uses public data from LZ, PandaX-4T, AND XENONnT in a unified
framework. This is the first time the project has:

1. Used a **published, peer-style** combined analysis (arXiv preprint)
2. Compared against **3 experiments simultaneously**
3. Had a defensible "independent cross-detector confirmation" claim

---

## Consistency tests

For each major published model point, the distance from the DIAMX
best-fit (60 GeV, 130 keV) in (m_χ, δ) space:

| Point | m_χ (GeV) | δ (keV) | Distance (σ) | Verdict |
|---|---|---|---|---|
| DIAMX best-fit | 60 | 130 | 0.0 | CONSISTENT |
| T103 MAP (project) | 483 | 295 | 15.1 | INCONSISTENT |
| Di Mauro 2026 | 1000 | 297 | 31.8 | INCONSISTENT |
| Fan-Tweed 2026 | 1100 | 350 | 35.4 | INCONSISTENT |

**Pattern:** The DIAMX analysis finds a much LIGHTER DM mass (60 GeV)
than what any TeV-scale interpretation has proposed. This is a
**major revision** to the project's T103 best-fit if the
endothermic interpretation is correct.

---

## T90 merge criterion #1

**Criterion:** At least 2 of 3 experiments (LZ, PandaX-4T, XENONnT)
show local significance > 2.5σ at the same (m_χ, δ) point.

**Status:** **SATISFIED** under DIAMX Case I (DEC charge yields at
nominal 0.88 L-shell, 1.00 M-shell values).

But the criterion is **fragile**:
- Case II (DEC charge yield as free parameter): LZ drops to 0.1σ,
  PandaX to 0.5σ, XENONnT to 1.8σ. Criterion NOT satisfied.
- Case III (DEC free + LZ+PandaX excluded): only XENONnT at 1.1σ.
  Criterion NOT satisfied.

**The systematic uncertainty on ¹²⁴Xe DEC charge yield is the
dominant error budget.** This is a known, named, experimentally
targetable background that will be better measured in upcoming
LZ/PandaX/XENONnT analyses.

---

## Implication for the project

The T103 MAP at (483 GeV, 295 keV) is in TENSION with DIAMX. The
project's LZ-only fit may be biased by the choice of:
- Which NREFT operator to use (project uses 𝒪₁ˢ, 𝒪₁ᵛ, 𝒪₄ˢ, 𝒪₄ᵛ)
- Which LZ bin/spectrum to fit
- How to handle the LZ background model

DIAMX uses a different (more conservative) approach and finds
m_χ = 60 GeV. This is **NOT necessarily a contradiction** — the
project's fit is also valid for the LZ-only data — but it suggests
the TeV-scale interpretation may be over-fit to LZ's specific
spectrum.

**Recommended next step:** Re-run T103 with a 1D prior on
m_χ ∈ [10, 200] GeV to see if the lighter-mass region is
statistically competitive.

---

## Standing posture

- **T90 merge rule — 2 of 5 criteria now satisfied:**
  1. Independent cross-detector confirmation (PandaX/XENONnT) — **YES, via T106/DIAMX** (was the missing piece)
  2. Peer-reviewed publication — no (preprint only)
  3. Community consensus — no
  4. Published BSM model motivation — Di Mauro 2026 = yes
  5. Fitted 7D posterior Δlog Z ≥ +2 — T43 was log Z = -4.15, no
- **Master unchanged:** T106 lives on `wip/tier3-magnetic-moment-LZ`
- **T90 merge is now closer to justified** but criterion #1 is fragile
  (depends on DEC charge-yield assumption)

---

## Honest limitations

1. **Gaussian likelihood approximation.** T106 uses a simple 2D
   Gaussian for the DIAMX best-fit, not the full profile likelihood
   from the paper. The full DIAMX likelihood would give slightly
   different significances and may shift the best-fit by 1-2σ.

2. **Uncertainties on best-fit are rough.** The 1σ widths in m_χ
   (~30 GeV) and δ (~30 keV) are estimated from the paper's
   benchmark table, not from a full posterior.

3. **DEC charge-yield assumption is the dominant systematic.** The
   3.5σ XENONnT significance is ONLY with DEC at nominal. If DEC
   is treated as a free parameter, significance drops to 1.8σ.

4. **Endothermic vs exothermic.** T106 only tests endothermic
   (δ > 0). The exothermic best-fit (m_χ = 13 GeV, |δ| = 455 keV)
   is a different region not tested here.

5. **The project's 60-GeV prediction is a new claim, not yet
   incorporated into the project's v0.7 MAP.** A revised v0.8 MAP
   would be needed if the lighter mass is correct.

---

## Cross-references

- T87 §13 — Di Mauro 2026 cross-link
- T98 — T43 vs Di Mauro numerical comparison
- T99 — Two-portal conceptual framing
- T100 — Research findings for Tier-2 fit (mentions DIAMX in section 6)
- T101/T102/T103 — LZ 248 keV fits (project's LZ-only analysis)
- T105 — UV consistency check (Portal A + Portal B from composite DM)
- **T106 (this work)** — Multi-experiment joint fit, T90 #1 check

## Reference

- **arXiv:2512.05850v3 (Nov 2025)** — "Dark Matter implications from
  the LZ, PandaX-4T and XENONnT Data" (DIAMX combined analysis)
  - Authors: H. An, F. Guo, J. Liu, H. Ni, C. Xu
  - First combined profile-likelihood fit to 3 LXeTPC experiments
  - Total exposure: 8.8 tonne·year (LZ 4.2 + PandaX 1.54 + XENONnT 3.1)
  - Best-fit (endothermic): m_χ = 60 GeV, δ = 130 keV, 3.5σ (XENONnT)
  - Best-fit (exothermic): m_χ = 13 GeV, |δ| = 455 keV, 3.5σ (XENONnT)

## Files

- `v0.3-prelim/code/t106_multi_experiment_joint.py` — multi-exp fit
- `v0.3-prelim/outputs/t95/t106_multi_experiment_joint.json` — results
- `v0.3-prelim/tests/test_t106_multi_experiment_joint.py` — 9 tests
- `v0.3-prelim/docs/T106_MULTI_EXPERIMENT_JOINT.md` — this doc

## Test count

- **939 pass / 8 skip** (verified 2026-09-08, +9 T106 tests)

## Time log

- ESTIMATE: 2-3 hours
- ACTUAL: ~25 min total
- RATIO: 0.15-0.20× — well under estimate (DIAMX paper has clear
  numbers; no need to derive from scratch)

## Provenance

- T106 conceptual analysis: 2026-09-08
- Hermes Agent (MiniMax-M3)
- Reference: arXiv:2512.05850v3 (DIAMX combined analysis)
- Branch: `wip/tier3-magnetic-moment-LZ`
- Standing posture: T90 branch, master untouched
