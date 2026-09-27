# Phase 33a — Bayes Factor Comparison: 1 vs 2 vs 3 vs 4 Resonance Models

> **Status:** 📋 Complete (2026-09-14)
> **Trigger:** Reviewer critique in t90review.docx (4 caveats about Phase 32 "ALL_9_PASS" claim)
> **Reference:** Phase 32c (ALL_9_PASS), t90review.docx
> **Verdict:** **INCONCLUSIVE — Δlog Z (4 vs 1) = -0.24** — data does not distinguish the models

---

## TL;DR (reviewer's critique confirmed)

The 4-resonance model fits the data as well as the 1-resonance model with the same number of free parameters (3: m_chi, σ_0_dwarf, a_slope). The Occam penalty does not strongly favor either. **The "ALL_9_PASS" verdict was based on loose target bands** — when observational constraints are tightened (especially SPARC), one of the 4-resonance predictions fails.

---

## Method

For each model with N resonances, run rejection sampling on (m_chi, σ_0_dwarf, a_slope) — the 3 free parameters. Compute:
- L_max = max log-likelihood across samples
- log Z = L_max + log(V_post / V_prior) − (N/2) ln(N_data)

All models have N=3 free parameters (the resonance positions and widths are FIXED in the architecture, not free).

---

## Results

| Model | L_max | log Z | Δlog Z vs 1 |
|---|---|---|---|
| 1-resonance | -0.478 | **-8.23** | 0 (best) |
| 2-resonance | 0.000 | -8.62 | -0.39 |
| 3-resonance | 0.000 | -8.33 | -0.10 |
| 4-resonance | -0.178 | -8.47 | -0.24 |

**Interpretation**:
- 2- and 3-resonance models achieve L=0 (perfect fit to all systems with loose bands)
- 1-resonance achieves L=-0.48 (fails on 1-2 tight constraints)
- 4-resonance achieves L=-0.18 (fails on 1 tight constraint)
- After volume ratio correction, all models are within Δlog Z ~ 0.4 (inconclusive)

---

## Hidden finding: 4-resonance FAILS tight SPARC band

When SPARC target is tightened from [0.03, 0.5] (Phase 32c) to [0.05, 0.15] (observational):

**Phase 32b 4-resonance posterior median**:
- σ/m(100) = 0.29
- SPARC target: [0.05, 0.15]
- **FAIL**

The reason: with σ_0_dwarf=0.29 and a_slope=0.7, the velocity-dependent background contributes σ/m(100) = 0.29. This is ABOVE the tight SPARC target.

The 4-resonance architecture (as published in Phase 32b) **does not satisfy the observational SPARC Bayes factor analysis** (which prefers σ/m(100) ~ 0.069 with tight constraints).

---

## Implications for the verdict

### Phase 32c verdict: ALL_9_PASS (overstated)

Under loose target bands (Phase 32c):
- Segue 1, Fornax, etc.: [0.5, 5] (10× range)
- SPARC: [0.03, 0.5] (16× range)
- Cloud-9: [30, 500] (16× range)

→ All models fit easily, ALL_9_PASS is trivial

### Tightened observational bands (Phase 33a):
- Segue 1, Fornax, etc.: [1.0, 3.0] (3× range, Kaplinghat+ 2020)
- SPARC: [0.05, 0.15] (3× range, SPARC Bayes)
- Cloud-9: [50, 200] (4× range, RELHIC)

→ 4-resonance FAILS SPARC, **not actually 9/9 PASS**

---

## Reviewer's caveats — addressed

### Caveat 1: Freedom vs. naturalness ✓ ADDRESSED

The Bayes factor comparison shows the 4-resonance model has **comparable evidence** to the 1-resonance model. The multi-resonance architecture is not strongly justified by the data.

**Honest statement**: The data does not strongly prefer 4 resonances over 1. The architectural choice is not Occam-justified.

### Caveat 2: Predicted vs. fitted ⚠ PARTIALLY ADDRESSED

In Phase 32c, v_targets were chosen to match the test systems' velocities (28, 100, 300, 700 km/s). These are not predicted by Tsai 2022's level-spacing formula — they were chosen to fit the data.

**Honest statement**: The resonance positions are phenomenological, not predicted.

### Caveat 3: Statistical standard ✓ ADDRESSED

The Phase 33a analysis uses Laplace approximation with proper Occam penalty. The result is **inconclusive** (Δlog Z ~ 0.4) rather than "decisive evidence for 4-resonance".

### Caveat 4: External probes ⏳ NOT YET ADDRESSED

This phase focused on internal Bayes factor comparison. External probes (real THINGS galaxies, real SPARC, real lensing) still need to be done.

---

## Updated verdict

| | Phase 31bc | Phase 32c | **Phase 33a** |
|---|---|---|---|
| Verdict | PARTIALLY_PLAUSIBLE | ALL_9_PASS (loose) | **INCONCLUSIVE** |
| 4-resonance evidence | Not tested | Implicit (claimed) | Δlog Z = -0.24 (no preference) |
| SPARC tight band | n/a | PASS (loose) | **FAIL** |

**Final verdict**: The multi-resonance architecture is **promising but not Occam-justified**. The 1-resonance model fits the data comparably well with fewer concepts.

---

## What this means for publication

If we want to publish the multi-resonance model, we need to:

1. **Show that the 4 resonance positions are PREDICTED** by dark QCD (Tsai 2022 Eq. 11), not chosen to fit data
2. **Demonstrate a discriminating external test** that prefers 4-resonance over 1-resonance
3. **Fix the SPARC issue** (lower σ_0_dwarf or add a 5th resonance at v=100)

Without these, the 4-resonance model is **indistinguishable from a simpler 1-resonance model** given current data.

---

## Honest recommendation

**Retire the "ALL_9_PASS = publication-quality" verdict**.

Replace with:
> "Multi-resonance dark-QCD-inspired SIDM model passes the project's internal tests under loose target bands. Bayes factor comparison with simpler models is inconclusive (Δlog Z = -0.24). External probes and tighter observational constraints are required to distinguish the architectures. The model remains a viable candidate but not a demonstrated unique solution."

This is the reviewer's recommended status, and it is the honest one.

---

## Files shipped

- `code/phase33a_bayes_factor.py` (~340 lines)
- `data/results/phase33a_bayes_factor.json`
- `docs/PHASE33A_BAYES_FACTOR_HONEST_VERDICT_2026_09_14.md`

Tests: pending (will be added in next commit)