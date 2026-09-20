# Plan — Phase 33: Quantitative fine-tuning + Bayes factor comparison

> **Status:** 📋 Plan ready (2026-09-14)
> **Trigger:** User uploaded t90review.docx (Phase 32 critical review)
> **Predecessor:** Phase 32c — ALL_9_PASS verdict was overstated

---

## Goal

Address the 4 caveats in t90review.docx with concrete quantitative analysis:
1. **Fine-tuning / Occam measure** for 1, 2, 3, 4 resonances (with proper Bayes factors)
2. **Show resonance positions are predicted**, not freely fit
3. **External probes** (independent galaxy samples)
4. **Proper statistical standard** (nested sampling or Laplace approximation)

Most important: **compute the Occam penalty** for the 4-resonance model vs simpler alternatives.

---

## Reviewer's 4 caveats in detail

### Caveat 1: Freedom vs. naturalness

**Reviewer's claim**: "Four resonance locations plus a background slope give substantial freedom. The claim 'NATURAL_MULTI_RESONANCE / no fine-tuning' needs a quantitative fine-tuning or Occam measure against simpler models."

**What we did**: Said "Tsai 2022 multi-resonance is natural" without comparing to simpler models.

**What's needed**: Compute Bayes factor K = P(data | 4-resonance) / P(data | 1-resonance, 2-resonance, no-resonance).

### Caveat 2: Predicted vs. fitted spectrum

**Reviewer's claim**: "In a true dark-QCD construction the resonance positions are fixed by dark quark masses. If the code places resonances near the velocities that previously failed, the model remains closer to a flexible phenomenological fit."

**What we did**: Placed resonances at v = 28, 100, 300, 700 km/s because those are the velocities of the test systems.

**What's needed**: Show that the resonance positions are CONSISTENT with Tsai 2022's level-spacing formula (Eq. 11: Δn ~ C/n). Compute predicted positions from (m_Q, Λ_D, N_c) and check they match.

### Caveat 3: Statistical standard

**Reviewer's claim**: "'Top 1% of 30k samples' is weaker than a full nested-sampling evidence comparison. The Occam penalty for the extra parameters should be shown explicitly."

**What we did**: Used rejection sampling, kept top 1%.

**What's needed**: Use Laplace approximation to compute the Bayesian evidence (log Z) for each model (1, 2, 3, 4 resonances). Show that the 4-resonance model has HIGHER evidence after the Occam penalty.

### Caveat 4: External probes

**Reviewer's claim**: "All nine tests are still internal to the project's chosen likelihoods and wrappers. Independent external checks remain the decisive next step."

**What's needed**: Re-run with at least one external dataset (e.g., real THINGS galaxies, real SPARC sample, real strong-lensing data).

---

## Phase 33a — Bayes factor: 1 vs 2 vs 3 vs 4 resonances (~1-2 hours)

For each model (1, 2, 3, 4 resonances), compute:
- Number of parameters N
- Best-fit log-likelihood L_max
- Volume of high-likelihood region in parameter space (Laplace approximation)
- log evidence = L_max - (N/2) × ln(N_data) + ln(V_prior / V_posterior)

Then compute:
- Δlog Z (4 vs 1), (4 vs 2), (4 vs 3)
- If Δlog Z > 5 (strong evidence), 4-resonance model is justified
- If Δlog Z < 0, simpler model wins (Occam penalty dominates)

### Expected outcomes

| Model | N params | Expected log Z |
|---|---|---|
| 1 resonance + bg | ~5 | highest IF data only needs 1 scale |
| 2 resonances + bg | ~8 | moderate |
| 3 resonances + bg | ~11 | moderate-high |
| 4 resonances + bg | ~14 | highest IF data needs 4 scales |

The data has 4 distinct scales (dwarfs, Cloud-9, SPARC, streams, clusters), so we expect Δlog Z (4 vs 1) > 0.

## Phase 33b — Resonance positions vs Tsai 2022 prediction (~1 hour)

Compute the predicted resonance positions from Tsai 2022 Eq. 11:
- m[Υ(nS)] - m[Υ((n-1)S)] = C × [1/n + O(1/n²)]

Then for our fitted m_chi and known m_phi (mediator):
- Convert n → v_target → check if fitted positions match

If fitted positions fall on the predicted curve → "predicted"
If they don't → "phenomenological"

## Phase 33c — External probe: real THINGS galaxies (~1-2 hours)

Use real rotation curve data from THINGS survey (Walter+ 2008):
- 17 galaxies with HI rotation curves
- Compute sigma/m(v_max) for each
- Compare predicted vs observed for our multi-resonance model

If the model fits THINGS galaxies well → external validation
If not → flag as another caveat

## Phase 33d — Document + verdict update (~30 min)

- Add Phase 33 results to T90_CLOUD9_INDEX and T90_MASTER_REFERENCE
- Update README with honest verdict:
  - Was: "ALL_9_PASS = publication-quality"
  - Now: "Multi-resonance passes internal tests + Bayes factor + external probe"

---

## Expected outcome

**Best case**: All 4 caveats addressed. Verdict upgrade to "QUANTIFIED_PASS" with:
- Bayes factor > 100 for 4-resonance vs simpler models
- Resonance positions match Tsai 2022 prediction
- External probe (THINGS) consistent

**Realistic case**: 2-3 caveats addressed. Verdict "INTERNAL_PASS_WITH_CAVEATS".

**Pessimistic case**: Bayes factor shows simpler model wins → must accept that 4-resonance is overfit.

---

## Sequencing

Phase 33a (Bayes factor) is most important. Run it first.
- If Δlog Z (4 vs 1) > 5 → proceed with 33b, 33c, 33d
- If Δlog Z (4 vs 1) < 0 → verdict downgrade, retire "ALL_9_PASS" claim entirely

---

## Files to create

- `code/phase33a_bayes_factor.py`
- `code/phase33b_tsai_prediction.py`
- `code/phase33c_things_external.py`
- `code/phase33d_verdict_update.py`
- Update docs/T90_MASTER_REFERENCE.md, README.md

---

## Bottom line

The reviewer is right: "ALL_9_PASS" was overstated without quantitative justification. Phase 33 addresses the legitimate concern with concrete numbers (Bayes factor, predicted vs fitted, external probe). The architecture may still be the best model, but the **claim** needs to be backed by the **evidence**.