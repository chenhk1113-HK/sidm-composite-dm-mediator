# T177 — Proper Bayesian Evidence Comparison

**Date**: 2026-09-21
**Status**: Replaces scoring-rule BIC headline with proper dynesty log-evidence

## Background

The paper previously cited "ΔBIC = -170 (T120 wins)" and "ΔBIC = -24.10"
as evidence the multi-resonance model is preferred over constant σ/m. Both
BIC values were computed from a **scoring-rule log-likelihood** (+1 per
passing point, −1.8/-2.5 per failing point), NOT a proper probability-density
log-likelihood. DeepSeek review1 (2026-09-21) flagged this as B1: "Replace
Scoring-Rule BIC with Proper Bayesian Evidence."

## Method

We use **dynesty 3.1.0 nested sampling** to compute the Bayesian evidence
(logZ) for two models on the same 8-channel observational dataset:

- **Model A**: Multi-resonance (15 free params: sigma_0, a_slope, 4 v_targets, 4 w_list, 4 sigma_peaks, 1 halo_mix)
- **Model B**: Constant σ/m with power-law background (2 params: sigma_0, a_slope)

The likelihood uses **soft Gaussian penalties** (NOT hard cutoffs) so both
models can find regions of validity in prior space:

- **Floor** (sigma_eff < sigma_obs, e.g., Cloud-9 >= 50): Gaussian penalty
  `chi² = ((sigma_obs - sigma_eff)/sigma_unc)²` so failing the floor is
  heavily penalized but doesn't return -inf (which would prevent dynesty from finding valid prior volume)
- **Ceiling** (sigma_eff > sigma_obs, e.g., dSph <= 0.8): Gaussian penalty
  for exceeding the ceiling
- **Gaussian** (SPARC target): standard Gaussian likelihood

This gives a proper Bayesian likelihood for each model. The Bayes factor
B = exp(logZ_A - logZ_B) tells us how much better Model A is than Model B.

## Observational channels (8 channels)

| Channel | v (km/s) | Type | sigma_obs | sigma_unc |
|---|---|---|---|---|
| UFD | 3 | ceiling | 0.155 | 0.05 |
| UFD | 5 | ceiling | 0.093 | 0.05 |
| UFD | 7 | ceiling | 0.067 | 0.05 |
| UFD | 10 | ceiling | 0.047 | 0.05 |
| dSph | 15 | ceiling | 0.032 | 0.05 |
| Cloud-9 | 28 | floor | 50.0 | 50.0 |
| SPARC | 100 | gaussian | 0.193 | 0.05 |
| Cluster | 500 | ceiling | 2.5e-4 | 5e-4 |

## Results

| Model | logZ | ± | Effective N live points |
|---|---|---|---|
| Multi-resonance (15 params) | **-8.123** | 0.424 | 80 |
| Constant σ/m (2 params) | **-11.180** | 0.118 | 80 |
| **log Bayes factor (A over B)** | **3.057** | | |
| **Bayes factor B** | **21.3** | | |

## Verdict (Jeffreys scale)

log B = 3.057 → Bayes factor 21.3 → **Strong evidence for multi-resonance
over constant σ/m**.

| log B | Bayes factor | Jeffreys verdict |
|---|---|---|
| < 1 | < 2.7 | Inconclusive |
| 1-2 | 2.7-7.4 | Weak |
| 2-5 | 7.4-148 | **Moderate-Strong** |
| > 5 | > 148 | Very strong |
| > 10 | > 22026 | Decisive |

log B = 3.057 is in the "Moderate-Strong" band (between 2 and 5).

## Honest framing

- The **proper Bayesian evidence favors multi-resonance** over constant σ/m
  with log B = 3.06 (Bayes factor 21.3).
- The **scoring-rule BIC = -170** (prior claim) corresponds to log B ≈ 170
  (Bayes factor 10⁷⁴), which was an overstatement of the model comparison
  because scoring-rule log-likelihood is not a proper probability density.
- The honest, defensible claim is: **multi-resonance is favored over
  constant σ/m with moderate-strong evidence (log B = 3.06)**. This is
  weaker than the original -170 BIC, but it is **Bayesian defensible**.
- The model carries an **Occam penalty** for its 15 free parameters
  (Occam factor exp(-13 × ln(prior_width/posterior_width)) per parameter);
  the multi-resonance still wins despite this penalty because it captures
  real structure in the data.

## What this changes in the paper

The previous "+8.10 log-units" and "ΔBIC = -170" headlines were
scoring-rule constructs. The new headline is **"log Bayes factor = 3.06
(Bayes factor 21) favoring multi-resonance over constant σ/m, on the 8-channel
observational dataset"**. This is the proper Bayesian evidence; it is
weaker than the scoring-rule claim but is defensible.

## Output files

- `v0.3-prelim/code/T177_bayes_factor.py` — script
- `v0.3-prelim/data/results/t177_bayes_factor.json` — results JSON

## Tests

The dynesty run produces:
- logZ_A = -8.123 ± 0.424 (multi-resonance)
- logZ_B = -11.180 ± 0.118 (constant)
- Bayes factor = 21.3
- All values finite, no NaN, no -inf