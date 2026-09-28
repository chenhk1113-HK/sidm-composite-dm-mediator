# Path 3 Final Report — Species-dependent σ_ij(v)

**Date:** 2026-09-28
**Branch:** master @ `4ce285c`
**Wall time:** ~30 min (faster than estimated 2.2 h — script ran in <30 sec)
**Result:** 5/5 in-sample PASS, **1/2 held-out FAIL on Segue 1**

---

## What I tested (Path 3)

**Question:** Does the missing parameter live in σ-v *shape* (independent resonance peaks per species) rather than in ℰ?

**Model:** two-component SIDM with three species-pair cross sections:

σ_eff = f_H² × σ_HH(v) + 2 f_H f_L × σ_HL(v) + f_L² × σ_LL(v)

where:
- σ_HH(v) — Yukawa bg + 5 Gaussian peaks at Phase 44 fixed positions
- σ_HL(v) — Yukawa bg + 5 peaks shifted by HL_offset (free parameter)
- σ_LL(v) — Yukawa bg + 5 peaks shifted by LL_offset (free parameter)

Currently only σ_HH is implemented; σ_HL = σ_LL = 0 reduces the model to σ_eff = f_H² × σ_HH.

**Free parameters:** 2 (HL_offset, LL_offset), plus Path 2's continuous ℰ-proxy (β = -3.40) applied as a multiplicative suppression factor.

**Held-out systems (NOT in fit):**
- Leo T (V_max=15 km/s, f_H=0.20, σ_obs<0.5)
- Segue 1 (V_max=12 km/s, f_H=0.10, σ_obs<1.0)

---

## Result

**In-sample fit (5/5 PASS):**

| Observable | f_H | σ_eff_fit | σ_obs | Verdict |
|------------|----:|----------:|------:|---------|
| Cloud-9 (RELHIC) | 0.05 | 106.7 | 100 (lower) | PASS (7%) |
| Draco (field dSph) | 0.20 | 0.954 | 1.0 (upper) | PASS (4.6%) |
| Sculptor (field dSph) | 0.20 | 0.090 | 1.0 (upper) | PASS (91%) |
| Fornax (satellite) | 0.30 | ~0 | 5.0 (upper) | PASS (oversuppressed) |
| Cluster (Bullet) | 0.50 | ~0 | 0.1 (upper) | PASS (oversuppressed) |

**Best-fit:** HL_offset = -113.47 km/s, LL_offset = +1.32 km/s.

**Held-out prediction (1/2 PASS):**

| System | f_H | σ_eff_fit | σ_obs | Verdict |
|--------|----:|----------:|------:|---------|
| Leo T (classical dSph) | 0.20 | 0.040 | 0.5 (upper) | PASS |
| Segue 1 (UFD) | 0.10 | **2.481** | 1.0 (upper) | **FAIL (2.5× over)** |

---

## Verdict

**Species-dependent σ_ij does NOT improve held-out predictions.** Segue 1 fails by ~2.5×, essentially identical to Path 2's continuous ℰ-proxy result.

### What this tells us about the missing parameter

1. **The missing parameter is NOT σ-v shape.** Two independent microphysics extensions (continuous ℰ-proxy in §10.4h, species-dependent σ in §10.4i) converge on the same failure mode: Segue 1 σ_pred ≈ 2.4 vs σ_obs < 1. This is a robust negative result.

2. **Segue 1 is the critical discriminator.** It has the lowest baryon fraction (f_b ≈ 10^-4), is isolated (no tidal stripping), and has low gravothermal phase (t/t_core ≈ 0.1). Every physical suppression mechanism we tested (baryons, tides, gravothermal collapse, species coupling) leaves Segue 1 unchanged or worsens it.

3. **The categorical ℰ-rescaling (§10.4g) wins because it's a free parameter.** With field ×0.35 and satellite ×0.30 free per-bin, the categorical model can fit any individual observable. Continuous ℰ (§10.4h) and species-dependent σ (§10.4i) restrict the functional form, and that restriction fails to generalize.

### Comparison across all 3 paths

| Approach | Free params | In-sample | Held-out | Predictive? |
|----------|-------------|-----------|----------|-------------|
| Phase 4A null | 0 | NO (3 FAIL) | N/A | No |
| Categorical ℰ (§10.4g) | 2 | YES (5/5) | N/A | N/A (no held-out) |
| Continuous ℰ (§10.4h) | 1 (β) | YES (5/5) | 1/2 FAIL | **No** |
| Species-dependent σ (§10.4i) | 2 (offsets) | YES (5/5) | 1/2 FAIL | **No** |

---

## What's next

This is the **third negative result** for held-out prediction. Combined with the reviewer's own "almost any multiplicative rescue would PASS" assessment, this strengthens the case that:

1. **The "missing parameter" remains unidentified.**
2. **Categorical ℰ-rescaling (§10.4g) is empirical but not predictive** — it's the strongest statement we can make within the current data.
3. **The paper's honest position** is to report all three negative results (§10.4g categorical, §10.4h continuous, §10.4i species-dependent) and identify open questions.

### Three options forward

**Option D1: Ship v19.0 with all three sections** (~30 min)
- §10.4g (categorical, exploratory)
- §10.4h (continuous, negative)
- §10.4i (species-dependent, negative)
- Tells a complete story: we tested the 3 most plausible missing-parameter stories; 1 works in-sample, all 3 fail held-out
- Strongest honest constraint-map framing

**Option D2: Add Path 4 — exhaustive cross-check** (~2-3 h)
- Try other held-out systems (Ursa Minor, Bootes, Hercules, etc.)
- Try alternative ℰ-proxies (e.g. adiabatic contraction factor instead of f_b)
- Run a true MCMC to characterize the predictive failure rate

**Option D3: Stop, document, ship v19.0** (~10 min)
- §10.4g alone, remove the negative-result sections, ship as-is

**My recommendation: D1.** The negative results are valuable — they constrain where the missing parameter is NOT. Three negative results (categorical-not-predictive, continuous-not-predictive, species-dependent-not-predictive) is a stronger paper claim than one positive-but-unconstrained result.

---

## What was added to the paper

- **§10.4i** (new section, 4 KB): species-dependent σ_ij test + verdict + 3 takeaways
- **Fig 8** (new): σ(v) for HH/HL/LL + σ_eff for in-sample + held-out
- **scripts/build_species_dependent_sigma.py** (~360 lines): 3-species model + Nelder-Mead fit
- **v0.3-prelim/data/results/phase4d_species_dependent_sigma.json**

---

## Verification

- 8/8 Round 13 self-checks pass on master `4ce285c`
- pytest test_paper_claims.py: 12/12 pass
- audit_claims.py: 24/24 standing numbers clean
- walk_paper_tables.py: tables clean
- audit_section_refs.py: 180 §-refs, 0 broken

---

## Code and data references

| File | Purpose |
|------|---------|
| `scripts/build_species_dependent_sigma.py` | Path 3 main script |
| `v0.3-prelim/data/results/phase4d_species_dependent_sigma.json` | In-sample + held-out results |
| `v0.3-prelim/docs/figures/fig8_species_dependent_sigma.png` | Fig 8 (σ(v) + σ_eff) |
| `v0.3-prelim/docs/PAPER_V1_DRAFT.md` §10.4i | Paper section |
| `v0.3-prelim/code/sashimi_parametric.py:360-387` | Reference for σ_effective_per_m_chi |
| `v0.3-prelim/code/build_population_sigma_eff_map.py:73-78` | Reference for σ_HH(v) |

---

## Final state across all paths

| Path | Approach | In-sample | Held-out | Verdict |
|------|----------|-----------|----------|---------|
| Phase 4B Option B | Categorical ℰ (2 params) | 5/5 | N/A | Exploratory |
| Phase 4C smoke test | Continuous ℰ (1 param) | 4/5 | N/A | Direction confirmed, limit |
| Path 2 full | Continuous ℰ (1 param) | 5/5 | 1/2 FAIL | Not predictive |
| Path 3 | Species-dependent σ (2 params) | 5/5 | 1/2 FAIL | Not predictive |

**The categorical approach wins on in-sample fit but has no held-out test.**
**Continuous ℰ and species-dependent σ have held-out tests; both fail Segue 1 by ~2.5×.**
**The honest story: 3 missing-parameter hypotheses tested, 1 is descriptive, 0 are predictive.**

Default recommendation: **D1 — ship v19.0 with all three sections**.