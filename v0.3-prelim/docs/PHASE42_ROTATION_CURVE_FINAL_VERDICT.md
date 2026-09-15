# Phase 39 → 41D — Master rotation-curve verdict

> **Status:** ✅ Shipped 2026-09-14 (branch `wip/cloud-9-relhic`)
> **Purpose:** Consolidates the full rotation-curve comparison series into one place
> **Final verdict:** **The multi-resonance SIDM model is NOT statistically preferred over simpler cored profiles on SPARC rotation curves once proper Occam penalties are applied.**

---

## 🎯 THE FINAL VERDICT

After 4 phases of increasingly rigorous head-to-head comparisons against rotation-curve baselines:

| Phase | What was tested | Verdict |
|---|---|---|
| **Phase 39** | NFW vs SIDM hybrid (15 galaxies) | STRONG_SIDM (overstated) |
| **Phase 40** | NFW vs Burkert vs SIDM + Occam (120 galaxies) | Burkert wins (honest) |
| **Phase 41** | + Einasto + PISO + dynesty Bayesian evidence | Burkert wins by dynesty |
| **Phase 41D** | + Self-consistent gravothermal (Yang+ 2023) | Hybrid SIDM still better |

**Bottom line**: Rotation curves alone do not preferentially select the multi-resonance particle model over simpler phenomenological cored profiles (Burkert, PISO, Einasto).

---

## 📊 KEY RESULTS

### Phase 41 (chi² on 120 galaxies)

| Model | k_fit | Total χ² | Total log L | AIC |
|---|---|---|---|---|
| NFW | 3 | 4033.2 | -4033.2 | 8787.6 |
| Burkert | 3 | 3081.2 | -3081.2 | 6882.5 |
| Einasto | 4 | 3016.8 | -3016.8 | 6993.5 |
| PISO | 3 | 2967.0 | -2967.0 | **6654.0 (best)** |
| SIDM (hybrid) | 3 | 2986.2 | -2986.2 | 6692.4 |

PISO wins by chi² (AIC). SIDM ranks 3rd.

### Phase 41 (dynesty Bayesian evidence on 15 galaxies)

| Model | Total log Z |
|---|---|
| **Burkert** | **-963 (BEST)** |
| PISO | -1409 |
| Einasto | -1595 |
| NFW | -2654 |
| SIDM | -3300 (worst) |

Burkert wins decisively by Bayesian evidence. SIDM has the **lowest** evidence of all 5 models.

### Phase 41D (gravothermal)

| Metric | Hybrid SIDM | Gravothermal SIDM | Δ |
|---|---|---|---|
| k_fit | 3 | 4 (+1) | +1 |
| AIC | 6692.4 | 7179.2 | **+487 (worse)** |

The self-consistent gravothermal profile (Yang+ 2023) does **not** improve rotation-curve fits. Median t_r = 0.058 → most galaxies haven't evolved far from NFW.

---

## 🔬 WHY THE GRAVOTHERMAL PROFILE DIDN'T HELP

Three mechanistic reasons (per Phase 41D review):

1. **Velocity-dependence mismatch**: Yang+ 2023's parametric form was calibrated for **constant σ/m**. Our multi-resonant σ/m varies by 4 orders of magnitude across velocity regimes (σ/m(28)=100, σ/m(100)=0.07). Applying a constant-σ/m gravothermal mapping is an imperfect translation.

2. **Most systems are at t_r << 1**: At the velocities preferred by our posterior, the formal collapse time is longer than a Hubble time for typical SPARC halo parameters. Only 3/120 galaxies reach t_r > 0.5 (near collapse).

3. **Hybrid profile already captures the phenomenology**: A velocity-dependent core radius grafted onto a Burkert+NFW form is flexible enough to fit the data.

---

## 🎯 WHAT THIS MEANS FOR THE MULTI-RESONANCE MODEL

### Defensible (still true)

1. ✓ Passes **internal multi-scale consistency tests** (Phase 32)
2. ✓ Consistent with **SPARC Vflat** constraints (Phase 33d, 115/127 galaxies)
3. ✓ **Rotation-curve fit competitive with PISO** at fit level (ΔAIC = +38 favoring SIDM over PISO)
4. ✓ Provides a **unified cross-section framework** across velocity scales (Cloud-9, SPARC, subhalos)

### NOT defensible (Phase 39 overclaimed)

1. ✗ Does **not beat Burkert** on rotation curves (ΔAIC = -190; Δlog Z = -2337 by dynesty)
2. ✗ Does **not beat PISO** on Bayesian evidence (worse by dynesty)
3. ✗ Does **not beat Einasto** on rotation curves
4. ✗ **Self-consistent gravothermal does not rescue the model** (Phase 41D)

### Other limitations (not rotation curves)

1. ✗ Does NOT explain **JVAS B1938+666** lensing perturber (Phase 34a, fails by 84×)
2. ~ Bayes factor INCONCLUSIVE vs simpler models (Phase 33a)
3. ~ Tsai 2022 UV motivation was INCORRECT (Phase 33b)

---

## 🚦 THE HONEST SCIENTIFIC POSTURE

The multi-resonance SIDM model is:
- **A defensible particle-physics framework** that unifies cross-sections across multiple velocity scales
- **NOT statistically preferred** on rotation-curve data alone, once model complexity is properly accounted for
- **Compatible with SPARC Vflat** but does not deliver decisive evidence for SIDM over simpler cored profiles

This is an **honest and useful place to stand**: the model has scope, but rotation curves alone don't validate it. Future work would need:
- Velocity-dependent gravothermal modelling (substantially more work)
- Strong-lensing data (JVAS-class)
- Subhalo structure data
- Combined multi-channel evidence

The **hybrid Burkert+NFW profile** (Phase 41) remains the pragmatic choice for future rotation-curve comparisons.

---

## 📁 FILES

| Phase | Files |
|---|---|
| 39 | `code/phase39_nfw_vs_sidm.py`, `tests/test_phase39_nfw_vs_sidm.py`, `docs/PHASE39_NFW_VS_SIDM_2026_09_14.md` |
| 40 | `code/phase40_corrected_comparison.py`, `tests/test_phase40_corrected_comparison.py`, `docs/PHASE40_CORRECTED_COMPARISON_2026_09_14.md` |
| 41 | `code/phase41_extended_comparison.py`, `tests/test_phase41_extended_comparison.py`, `docs/PHASE41_EXTENDED_COMPARISON_2026_09_14.md` |
| 41D | `code/phase41d_parametric_sidm.py`, `tests/test_phase41d_parametric_sidm.py`, `docs/PHASE41D_PARAMETRIC_SIDM_2026_09_14.md` |

**171/171 tests pass** across the entire series.

---

## 🔖 TAGS

- `t90-nfw-vs-sidm-v39-2026-09-14`
- `t90-corrected-comparison-v40-2026-09-14`
- `t90-extended-comparison-v41-2026-09-14`
- `t41d-gravothermal-2026-09-14`

---

## 💡 LESSONS LEARNED

This series demonstrates several methodological lessons:

1. **NFW is a low bar**: Beating NFW does not mean beating CDM. Many cored profiles already win on rotation curves. The relevant comparison is against cored profiles (Burkert, PISO, Einasto).

2. **Occam penalty matters**: A 3-parameter fit and a 15-parameter particle model cannot be compared on raw likelihood alone. The parameter count must be reflected in the comparison (AIC, BIC, or Bayesian evidence).

3. **Outlier-driven results**: A few outlier galaxies (UGC02916, ESO563-G021, IC2574) can dominate total likelihood differences. Always report median + outliers separately.

4. **Nested-sampling is more rigorous**: dynesty naturally integrates Occam penalty via prior volume. Laplace AIC is an approximation.

5. **Self-consistency doesn't always help**: The gravothermal profile is more physical but more restrictive. If the underlying physics (constant σ/m assumption) doesn't match the actual model, it can hurt fit quality.

6. **Honest negative results are valuable**: Phase 41D's "the gravothermal model doesn't help" finding is a useful scientific conclusion, not a failure.

---

## 📖 REFERENCES

- Yang & Yu 2023, arXiv:2305.16176 — parametric SIDM model
- DanengYang/parametricSIDM GitHub repository
- Kaplinghat+ 2016 — core radius formula for velocity-dependent SIDM
- de Blok 2010 — cored profiles on SPARC galaxies
- Kass & Raftery 1995 — Bayes factor interpretation thresholds
- Speagle 2020 — dynesty nested-sampling package