# Plan — Phase 34: Combined response to both papers

> **Status:** 📋 Plan ready (2026-09-14)
> **Trigger:** User uploaded 2 documents:
>   1. **t90review.docx** (Phase 32c critique, 4 caveats)
>   2. **halo1.docx** (arXiv:2603.19362, Klemmer+ 2026 SIDM subhalos)

---

## Both papers in plain English

### Paper 1: t90review.docx (already addressed in Phase 33a-d)

Critique of Phase 32c "ALL_9_PASS" verdict. 4 caveats:
1. **Freedom vs naturalness**: 4 resonances = lots of freedom, need Occam measure
2. **Predicted vs fitted**: v_targets chosen to fit data, not UV-predicted
3. **Statistical standard**: top 1% of 30k samples weaker than full Bayes
4. **Scope of 9 tests**: all internal, need external

**Status after Phase 33**: All 4 addressed (Bayes INCONCLUSIVE, Tsai 2022 FALSIFIED, Laplace approx done, REAL SPARC passes 90.6%).

### Paper 2: halo1.docx (arXiv:2603.19362, Klemmer+ 2026)

SIDM subhalo evolution paper. Key contributions:
1. **SSHI** (scattering-induced subhalo-halo interaction) — previously called "evaporation" or "ram-pressure"
2. **Realistic N-body** with virtual host particles + Eddington inversion
3. **Tests isotropic vs forward-dominated** scattering
4. **Result**: SIDM subhalos have much **greater diversity** in central densities and density slopes than CDM
5. **SSHI can prevent core collapse** if cross section doesn't drop fast enough with velocity
6. **Can explain lensing anomalies** (SDSSJ0946+1006 subhalo)

### What Paper 2 says about our model

Our Phase-32 framework is "precisely a velocity-dependent SIDM model whose σ/m(v) changes across the regimes relevant to subhalos and satellites." The paper provides:
- **Realistic environmental physics** we don't currently include
- **Concrete benchmark for "diversity of cores"** — a key SIDM prediction
- **Angular dependence** test (Breit-Wigner is typically isotropic at low v)
- **Lensing relevance** for our Euclid-subhalo channel

### What Paper 2 doesn't address

- Doesn't publish ready-to-use likelihood for our exact σ/m(v)
- Our v-dependent background (Yukawa) isn't tested against their simulations
- We need to do the mapping ourselves

---

## Combined lessons from BOTH papers

Both papers converge on: **the model is viable but current tests are insufficient**. Paper 1 focuses on statistical rigor, Paper 2 on physical completeness.

| Aspect | Paper 1 | Paper 2 |
|---|---|---|
| **Internal tests** | Insufficient (loose bands, internal only) | Insufficient (missing SSHI/tides) |
| **External probes** | Required (real data) | Required (subhalo observables) |
| **Diversity of predictions** | Not quantified | Key SIDM signature |
| **UV motivation** | Falsified for Tsai 2022 | Could replace with Sp(4), scalar bound states |
| **Statistical standard** | Bayes factor needed | N/A |
| **Subhalo physics** | N/A | SSHI + core collapse needed |

---

## Phase 34 plan

### Phase 34a — σ/m diversity analysis (30 min)

Compute the diversity of σ/m(v) across our Phase 32b posterior, then compare:
- **Variance** of σ/m at fixed v across posterior samples
- **Diversity ratio** (max - min) / median at each test velocity
- Compare to Paper 2's claim that SIDM subhalos have "much larger diversity than CDM"

Expected: Our posterior likely has LOW diversity (narrow), which Paper 2 would interpret as "CDM-like subhalos" — could be a problem for lensing tests.

### Phase 34b — Simplified SSHI calculation (1-2 hours)

Implement a simplified SSHI formula:
- SSHI rate ∝ σ/m(v_orbital) × ρ_host × v_orbital
- For Milky Way-like host, compute typical SSHI-driven mass loss rate
- Compare to Paper 2's prediction: SSHI suppresses core collapse for σ/m(orbital) > ~10 cm²/g

If our σ/m(orbital) ~ 0.1 cm²/g (which it is for SPARC-like), SSHI is negligible → our model is consistent.

### Phase 34c — Combined doc update (15 min)

- Add section to T90_MASTER_REFERENCE combining lessons from BOTH papers
- Update README with combined verdict
- Tag as new "both-papers-addressed" version

---

## Sequencing

Phase 34a is fastest and most informative. Run it first:
- If our σ/m diversity is HIGH → strong SIDM signal, Phase 2 lensing tests could be added
- If our σ/m diversity is LOW → "CDM-like", Paper 2 would predict no lensing anomalies → flag as caveat

Phase 34b is more rigorous but slower.

Phase 34c is bookkeeping.

---

## Bottom line

Both papers point at the same conclusion: **the model works but tests are incomplete**. Paper 1 wants quantitative comparison; Paper 2 wants environmental physics. Together they motivate Phase 34: check our σ/m diversity and SSHI compatibility.

Files to create:
- `code/phase34a_sigma_diversity.py`
- `data/results/phase34a_sigma_diversity.json`
- `code/phase34b_sshi_simple.py` (optional)
- `docs/PHASE34_BOTH_PAPERS_RESPONSE_2026_09_14.md`
- README.md update

Recommend proceeding with Phase 34a (30 min) as the next step.