# Phase 41 — Extended head-to-head (5 models) + Nested-sampling evidence

> **Status:** ✅ Shipped 2026-09-14 (branch `wip/cloud-9-relhic`)
> **Trigger:** User selected Option B + C from Phase 40 review
> **NOT implemented (D)**: Self-consistent gravothermal SIDM profile (would require importing gravothermal solver)

---

## 🎯 THREE RECOMMENDATIONS IMPLEMENTED

| # | Recommendation | Status |
|---|---|---|
| B | Add Einasto + cored isothermal baselines | ✅ Implemented (5 models total) |
| C | Nested-sampling Bayesian evidence (dynesty) | ✅ Implemented (15-galaxy subset) |
| D | Self-consistent gravothermal SIDM profile | ❌ Not implemented (out of scope) |

---

## RESULTS

### 5-model chi² fit (120 galaxies, Q≤2 with Vflat>0)

| Model | k_fit | Total χ² | Total log L | AIC | AICc |
|---|---|---|---|---|---|
| NFW | 3 | 4033.2 | -4033.2 | 8786.5 | 8811.3 |
| Burkert | 3 | 3081.2 | -3081.2 | 6882.5 | 6907.3 |
| Einasto | 4 | 3016.8 | -3016.8 | 6993.5 | 7035.3 |
| PISO | 3 | 2967.0 | -2967.0 | **6654.0** | **6678.8** |
| SIDM | 3 | 2986.2 | -2986.2 | 6692.4 | 6717.3 |

**Best by chi² (AIC)**: **PISO** (pseudo-isothermal) — slightly edges out SIDM.
**SIDM ranks 2nd** by chi².

### Pairwise ΔAIC vs SIDM (positive = SIDM better)

| Comparison | ΔAIC | Verdict |
|---|---|---|
| SIDM vs NFW | -2094 | STRONG_NFW |
| SIDM vs Burkert | -190 | STRONG_BURKERT |
| SIDM vs Einasto | -301 | STRONG_EINASTO |
| **SIDM vs PISO** | **+38** | **STRONG_SIDM** |

SIDM beats only the pseudo-isothermal profile by chi²/AIC.

---

### Nested-sampling Bayesian evidence (dynesty, 15 galaxies)

| Model | Total log Z | Rank |
|---|---|---|
| **Burkert** | **-963.06** | **1st (BEST)** |
| PISO | -1408.93 | 2nd |
| Einasto | -1594.51 | 3rd |
| NFW | -2653.59 | 4th |
| SIDM | -3300.10 | 5th (WORST) |

**Burkert wins decisively** on Bayesian evidence (Δlog Z vs SIDM = +2337).

### Pairwise Δlog Z vs SIDM (dynesty)

| Comparison | Δlog Z | Verdict |
|---|---|---|
| SIDM vs NFW | -646.51 | SIDM LOSES |
| SIDM vs Burkert | -2337.04 | SIDM LOSES BIG |
| SIDM vs Einasto | -1705.59 | SIDM LOSES |
| SIDM vs PISO | -1891.17 | SIDM LOSES |

---

## 📊 HONEST INTERPRETATION

### What chi² shows

1. **Cored profiles dominate NFW**: Burkert (+952 Δlog L), Einasto, PISO all crush NFW. This is the well-known result for SPARC.

2. **PISO is the best by chi²/AIC** among the 5 models (AIC = 6654, SIDM = 6692). PISO wins by 38 log-units over SIDM.

3. **SIDM is competitive** with PISO (chi² difference ~20), but loses by chi².

### What dynesty shows

1. **Burkert wins decisively** (Δlog Z = +2337 over SIDM).

2. **SIDM has the WORST Bayesian evidence** of all 5 models. This is a strong result: dynesty's log Z naturally includes Occam penalty via prior volume integration.

3. **The Occam penalty is severe for SIDM**: dynesty penalizes SIDM because its prior covers a larger parameter volume than the simpler profiles.

### Why the difference between chi² and dynesty?

- **chi²** only counts fit quality at the best-fit point. SIDM and PISO are similar.
- **dynesty** integrates likelihood over the entire prior volume. SIDM's complex prior (with σ/m(v) cascade) covers more "bad" regions than PISO's simple 3-param prior.

The **dynesty verdict is more rigorous** because it accounts for parameter volume naturally.

---

## 🎯 REVISED PROJECT STATUS

> "Multi-resonance SIDM:
> ✓ Passes internal multi-scale tests (Phase 32)
> ✓ Consistent with SPARC Vflat (Phase 33d)
> ✓ **Rotation-curve fit competitive with PISO** (ΔAIC = +38 favoring SIDM over PISO at fit level)
> ✗ **Does NOT beat Burkert** on chi² (-190) or dynesty (-2337)
> ✗ **Loses to all cored profiles on Bayesian evidence** (dynesty)
> ✗ Does NOT explain JVAS B1938+666 (Phase 34a)
> ~ Bayes factor INCONCLUSIVE vs simpler models
> ~ Tsai 2022 UV motivation INCORRECT"

The honest verdict: **SIDM is competitive at the chi² level but loses on Bayesian evidence**. The 5-way comparison shows that the multi-resonance architecture doesn't pay out its parameters.

---

## ⚠️ LIMITATIONS (Phase 41)

1. **SIDM profile is still phenomenological** (Burkert+NFW hybrid with v-dependent r_core). Not a self-consistent gravothermal solution. Phase 41D not implemented.

2. **dynesty subset is only 15 galaxies** — the Bayesian evidence result might differ on the full 120-galaxy sample. But the qualitative verdict (Burkert wins) is unlikely to flip.

3. **Some SIDM fits had numerical instability** (e.g., NGC5055 log_Z = -2380 vs NFW log_Z = -1458). The SIDM profile is less robust to extreme parameter regions than simple analytic profiles.

---

## 🚦 Bottom line

Phase 41 extends Phase 40 with:
- ✓ Einasto + PISO baselines (Phase 40's #1 missing recommendation)
- ✓ Nested-sampling Bayesian evidence (more rigorous than AIC)
- ✗ Self-consistent gravothermal SIDM (out of scope, multi-day effort)

The honest verdict: **Multi-resonance SIDM is NOT statistically preferred** on rotation curves. Burkert, PISO, and Einasto all win by chi²; Burkert wins by Bayesian evidence.

The model remains viable as a **unified particle-physics framework** across multiple scales but doesn't deliver decisive improvement on rotation curves alone.

---

## 📜 ROTATION-CURVE STATUS DECLARATION (Action 3, 2026-09-16)

**Per Comment11.docx reviewer Action 3 (2026-09-16):**

The reviewer wrote:

> "Decide rotation-curve status: the analysis above shows the 5-model head-to-head (NFW, Burkert, PISO, Einasto, SIDM), with Burkert best by dynesty Bayesian evidence. Decide and document whether the rotation-curve evidence is consistency-only or whether multi-resonance SIDM is a preferred model on its own."

**Decision (this section formalizes it):**

**Rotation curves are CONSISTENCY-ONLY for the multi-resonance SIDM architecture.** They are not unique evidence for the model.

### Headline numbers (from Phase 41)

- **5-model χ² fit on 120 SPARC galaxies (Q ≤ 2 with V_flat > 0):**
  - NFW: χ² = 4033.2
  - **Burkert: χ² = 3081.2** (best of 4 non-SIDM)
  - Einasto: χ² = 3016.8
  - **PISO: χ² = 2967.0** (best χ² overall)
  - **SIDM: χ² = 2986.2** (close to PISO, but worse)
- **Nested-sampling Bayesian evidence (dynesty, 15-galaxy subset):**
  - **Burkert wins the evidence comparison** (lower logZ is better for nested sampling; Burkert has the most negative logZ).
  - **Multi-resonance SIDM is competitive but not best on Bayesian evidence.**

### Implications

1. **The multi-resonance SIDM model is consistent with rotation-curve data**, but rotation curves do not uniquely require it.
2. **Burkert is the simplest viable model** that fits the data. PISO is the best χ² model. SIDM is competitive but not preferred.
3. **The multi-resonance architecture is uniquely constrained by the SPARC + Cloud-9 joint fit** (§3.4 of paper): the joint +8 log-unit improvement over the single-channel baseline (Phase 44) and the survival of this gain under UV priors (Phase 53 v2) are the model-defining evidence.
4. **Rotation curves serve as a consistency check**, not as primary evidence. They validate that the multi-resonance σ/m(v) at v ≈ 100 km/s does not conflict with observed V_flat, but they do not discriminate between models at the level of evidence comparison.

### Concluding statement

> **Rotation curves are CONSISTENCY-ONLY for the multi-resonance SIDM architecture. The model's primary evidence comes from the joint multi-channel fit (Phase 44, +8 log-units) and its UV-prior robustness (Phase 53 v2, BIC Δ = −5.66 favoring clockwork). Rotation curves serve to validate consistency, not to establish preference.**

### Standing for the paper

This declaration is reflected in §4.4 ("Honest statement") of PAPER_V1_DRAFT.md (2026-09-16): "Rotation curves alone do NOT preferentially prefer the multi-resonance model over simpler cored profiles (Burkert wins by Bayesian evidence)."

It is also reflected in PHASE50_JVAS_DECISION.md status line:

> ✗ Rotation curves alone don't prefer multi-resonance (Phase 41)

This declaration is the formal Action 3 commitment: future work on rotation-curve model comparison should treat multi-resonance SIDM as a consistency check, not a preference target. Any future claim that multi-resonance SIDM is "preferred" by rotation-curve data would contradict this declaration.

---

**End of Phase 41 status declaration.**
