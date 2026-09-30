# Phase B (v19.2-B): Ohana+ 3.2σ Reproduction — Layman + Plan

**Date:** 2026-09-30
**Status:** Plan
**Outcome target:** Family of papers — simple v2 + full v3 if time

## Honest framing (per Rule 28 / no-shortcut protocol)

The existing `scripts/ohana2026_cloud9_joint_likelihood.py` (v19.1.5) computes
**c-M tension = 1.04σ** (median of posterior samples), but Ohana+ 2026
[arXiv:2608.04362] quotes **3.2σ below cosmological median** for the SIDM
best-fit. The discrepancy is structural:

1. **Our script uses synthetic data** constructed at the published best-fit
   (M=4.7e9, c=4.0, tau=0.18) — the data is *consistent* with the best-fit
   by construction. The 1.04σ comes from the posterior median drifting toward
   the prior because the synthetic-data likelihood is weak.

2. **Our script computes tension from posterior MEDIAN**; Ohana+ quote
   tension from **best-fit (MAP/MLE)**. The median is pulled by the prior;
   the best-fit is anchored by the likelihood peak.

3. **Our script uses σ_scatter = 0.14 dex** (Diemer+ 2019 default);
   Ohana+ likely use a different σ_scatter value (Duffy+ 2008 = 0.11,
   or possibly mass-dependent scatter from Diemer & Joyce 2019).

To reproduce the published 3.2σ, the script needs ONE OR MORE of:
- (a) Best-fit (MAP) tension instead of posterior-median tension
- (b) σ_scatter sweep to identify which literature value reproduces 3.2σ
- (c) Real N_HI data from BLN24 (full v3 — Phase B "full")

Phase B v2 = (a) + (b). Phase B v3 (if time) = (c).

## Plan A: v19.2-B v2 — "Simple best-fit + σ_scatter sweep" (~30 min)

**Goal:** Reproduce Ohana+'s published 3.2σ tension using:
- Best-fit (minimum chi² sample), not posterior-median
- σ_scatter sweep over literature values
- Report: best-fit c, best-fit σ/m, tension per σ_scatter

**Files modified:**
- `scripts/ohana2026_cloud9_joint_likelihood.py` — add `compute_best_fit_tension()`,
  `sigma_scatter_sweep()`, replace posterior-median tension with best-fit tension
  as the headline number
- `v0.3-prelim/data/results/ohana2026_cloud9_joint_likelihood.json` — bump
  v19.1.5 → v19.2-B.1, add best-fit c, best-fit tension per σ_scatter
- `v0.3-prelim/docs/PAPER_STANDING_NUMBERS.md` — update §5 Ohana+ row

**Verification:**
- `python scripts/ohana2026_cloud9_joint_likelihood.py` runs without error
- For SIDM best-fit (c=4.0, M=4.7e9), tension should be **2.5–3.5σ** for some
  σ_scatter ∈ [0.10, 0.16] — bracketing the published 3.2σ
- 8-layer Round 13 self-check passes

**Stop conditions:**
- If best-fit tension < 1σ for all σ_scatter — synthetic-data limitation
  is structural; flag honestly and proceed to v3 with real data.

## Plan B: v19.2-B v3 — "Full hydrostatic + real BLN24 N_HI" (~2 hours, if time)

**Goal:** Replace synthetic N_HI with published BLN24 column densities
(Cloud-9 has published radial N_HI profile in BLN24 paper / Anand+ 2025
follow-up). Implement:
- BLN17 T(rho) hydrostatic equilibrium (Cloud-9 is gas-pressure-supported)
- Rahmati+ 2013 HI fraction (Cloud-9 is HI-dominated, photoionization matters)
- Real N_HI profile in cm⁻² units from BLN24

**Files modified:**
- Same script, plus side files `cloud9_n_hi_BLN24.py`, `hydrostatic_eq.py`

**Stop conditions:**
- v2 must succeed first; v3 only if v2 shows the synthetic-data gap is
  the dominant discrepancy mechanism.

## What I will NOT do (commitment per Rule 28 / no-shortcut protocol)

- **Will NOT** fabricate a 3.2σ number by tuning σ_scatter outside the
  literature range (0.10–0.16 dex) just to match
- **Will NOT** declare "Ohana+ validated" if the synthetic-data likelihood
  cannot produce 3.2σ even with best-fit + reasonable σ_scatter
- **Will NOT** skip the 8-layer self-check before claiming completion
- **Will NOT** write the paper update before running the script

## Carried-over item: wip/multi-component-SIDM-core-collapse

**Diagnosis (this session):** Local `9c40251` is 10 commits BEHIND remote
(origin: `2363a43` + 4 newer). No divergence requiring Rule 5 approval —
just stale. **Defer to next session** unless user wants me to fast-forward
now (one-line operation: `git merge --ff-only origin/wip/...` after user OK).