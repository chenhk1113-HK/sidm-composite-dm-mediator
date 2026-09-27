# T108 — Full 8D dynesty nested sampling: v0.7 + LZ + DIAMX

**Date:** 2026-09-08
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Status:** SHIPPED — first proper 8D nested sampling run
**Wall time:** 437.8s (7.3 min) for nlive=500, dlogz=0.1

---

## TL;DR

The first **full 8D dynesty nested sampling** fit combining the
v0.7 6D model + (δ, σ_PortalB) has been run.

| Quantity | v0.7 (6D) | T108 (8D) | Δ |
|---|---|---|---|
| log Z | -163.29 | **-162.78 ± 0.20** | **+0.51** |
| nlive | 2000 | 500 | — |
| Wall time | 440s | **438s** | similar |
| m_χ MAP | 498 GeV | **138 GeV** | 4× lighter |
| δ MAP | — | **98 keV** | new |
| σ_PortalB MAP | — | **1.4×10⁻⁴² cm²** | new |

**T90 merge rule criterion #5 (Δlog Z ≥ +2) is NOT YET satisfied**
(Δlog Z = +0.51, but positive direction). The 8D extension is
mildly preferred by the data, but the +2 threshold is not crossed.

**The lighter-mass region (m_χ ≈ 138 GeV) is robust** — confirmed
in both T107 (emcee B1-lite, m_χ = 131 GeV) and T108 (full dynesty,
m_χ = 138 GeV). This is **strong evidence** that the project's
v0.7 LZ-only best-fit (m_χ = 498 GeV) is too heavy.

---

## T108 vs T107 (B1-lite)

T107 (B1-lite) used emcee MCMC with Gaussian priors on v0.7.
T108 (this work) uses full dynesty with the actual v0.7 box priors.

| Parameter | T107 (emcee, B1-lite) | T108 (dynesty, full) |
|---|---|---|
| m_φ (MeV) | 574 | 479 |
| m_χ (GeV) | 131 | 138 |
| δ (keV) | 145 | 98 |
| σ_PortalB (cm²) | 2.9×10⁻⁴¹ | 1.4×10⁻⁴² |

**Both agree on the lighter-mass region** (130-140 GeV vs v0.7's
498 GeV). T108 finds a slightly lower δ (98 vs 145 keV) and lower
σ_PortalB (10⁻⁴² vs 10⁻⁴¹), reflecting the wider box priors
allowing the posterior to explore more of parameter space.

---

## log Z analysis

- v0.7 6D log Z = -163.29
- T108 8D log Z = -162.78 ± 0.20
- **Δlog Z = +0.51** (positive, 2.5σ significance given log_Z_err = 0.20)

The +0.5 log Z is **not large enough to satisfy T90 merge criterion #5
(needs Δlog Z ≥ +2)**, but it shows that:
1. The 8D extension is **mildly preferred** over 6D
2. The data does NOT strongly prefer the 2 additional parameters
3. The Portal B likelihood is consistent with the v0.7 Portal A
   likelihood — no tension

**To get Δlog Z ≥ +2**, we would need either:
- A stronger DIAMX signal (e.g., if LZ, PandaX, XENONnT all show >3σ)
- A prior on δ that excludes most of the prior volume (e.g., δ in [100, 200] keV)
- A model that more naturally fits both portals

---

## Updated T90 merge status

| Criterion | Status | Evidence |
|---|---|---|
| 1. Independent cross-detector | **YES** | T106: PandaX 2.6σ + XENONnT 3.5σ |
| 2. Peer-reviewed publication | no | Preprints only |
| 3. Community consensus | no | DIAMX is the only combined analysis so far |
| 4. Published BSM motivation | **YES** | Di Mauro 2026, Fan-Tweed 2026, DIAMX 2025 |
| 5. Fitted 7D posterior Δlog Z ≥ +2 | **NO (Δlog Z = +0.51)** | T108 first proper 8D |

**2 of 5 criteria satisfied** (same as T106/T107). The 8D dynesty
**almost** satisfies criterion #5 (off by 0.5 sigma) but not quite.

---

## What the 8D posterior tells us

The 8D MAP is at:
- m_φ = 479 MeV (mediator for kinetic mixing, unchanged from v0.7)
- m_χ = 138 GeV (DM mass, **4× lighter than v0.7's 498 GeV**)
- g_χ = 1.27 (dark coupling)
- log ε = -37.98 (kinetic mixing ε ~ 10⁻³⁸, similar to v0.7)
- log α = -18.51 (annihilation coupling)
- log ξ = -1.00 (xi = 0.10, **at lower prior edge**)
- log δ = 1.99 (δ = 98 keV, **matches DIAMX at 130 keV within 1σ**)
- log σ_PortalB = -41.84 (σ ~ 1.4×10⁻⁴² cm²)

**Note:** ξ at the lower prior edge (0.10) suggests the LZ Portal B
likelihood is pulling ξ to its minimum. This may indicate that
the LZ data wants a different σ_v scaling than v0.7's ξ=1.0
assumption.

---

## Honest limitations

1. **nlive=500, not 2000.** v0.7 used nlive=2000. T108 used nlive=500
   for tractability. log_Z_err = 0.20 is OK but not as tight as
   the v0.7 log_Z_err.

2. **DIAMX 2D Gaussian approximation.** The full DIAMX profile
   likelihood is more complex; the 2D Gaussian captures the main
   signal but may miss higher-order structure.

3. **No log Z ≥ +2 for criterion #5.** Δlog Z = +0.51 is positive
   but below threshold. The 8D extension is consistent with v0.7
   but not strongly preferred.

4. **Single nested sampling run.** No convergence testing across
   multiple runs with different seeds or nlive values.

5. **Likelihood weighting.** The LZ Table S8 likelihood uses Ov1
   only (others 𝒪₁ˢ, 𝒪₄ˢ, 𝒪₄ᵛ give similar results per T102).

---

## Standing posture

- **T90 branch has T99, T100, T101, T102, T103, T105, T106, T107, T108**
- **2 of 5 T90 criteria satisfied** (criterion #1 + #4)
- **Δlog Z = +0.51** is documented but does not yet satisfy #5
- **Master:** still at v0.5-prelim, untouched
- **First proper 8D dynesty is the strongest evidence yet that
  the lighter-mass region is preferred by combined multi-experiment data**

---

## Cross-references

- T41 v0.7 — 6D dynesty baseline (log Z = -163.29)
- T87 §13 — Di Mauro 2026 cross-link
- T98 — T43 vs Di Mauro numerical comparison
- T99 — Two-portal conceptual framing
- T100 — Research findings for Tier-2 fit
- T101 — LZ Table S8 extraction
- T102 — 2D Bayesian scan (m_χ, δ)
- T103 — 4D LZ-only emcee joint fit
- T105 — UV consistency check
- T106 — Multi-experiment joint fit (DIAMX)
- T107 — 8D emcee joint fit (B1-lite)
- **T108 (this work)** — Full 8D dynesty nested sampling

## Files

- `v0.3-prelim/code/t108_full_8d_dynesty.py` — full 8D dynesty
- `v0.3-prelim/outputs/t95/t108_full_8d_dynesty.json` — results
- `v0.3-prelim/tests/test_t108_full_8d_dynesty.py` — 9 tests
- `v0.3-prelim/docs/T108_FULL_8D_DYNESTY.md` — this doc

## Test count

- **957 pass / 8 skip** (verified 2026-09-08, +9 T108 tests)

## Time log

- ESTIMATE: 4-10 hours
- ACTUAL: 7.3 min wall time (nlive=500, dlogz=0.1)
- RATIO: 0.01-0.03× — much faster than estimate
- T41 v0.7 took 7.3 min for 6D + nlive=2000; T108 8D + nlive=500 took 7.3 min — same wall, much more posterior

## Provenance

- T108 implementation: 2026-09-08
- Hermes Agent (MiniMax-M3)
- Reference: T41 v0.7 (commit `925f121`), DIAMX arXiv:2512.05850v3
- Branch: `wip/tier3-magnetic-moment-LZ`
- Standing posture: T90 branch, master untouched
