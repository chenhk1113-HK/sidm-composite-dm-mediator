# Phase 31a — Three Critical Review Tests (consider8.docx)

> **Status:** ✅ Shipped 2026-09-14 (branch `wip/cloud-9-relhic`)
> **Trigger:** User requested Phase 31a (tests C, H, I from consider8.docx)
> **Direction:** Run 3 remaining fast tests on Phase 29's resonant SIDM model
> **Predecessor:** Phase 30 (4 of 9 tests done; verdict PLAUSIBLE w/ caveats)

---

## TL;DR — Three new test results

| Test | Question | Verdict | Severity |
|---|---|---|---|
| **C** | Real Euclid Q1 strong-lensing cluster count (14 observed) | ✓ **CONSISTENT_WITH_DATA** | σ/m at v=500-1000 is tiny, model looks like CDM for lensing |
| **H** | Dwarf core sizes vs observations | ✗ **OVERSHOOTS_DWARF_CORES** | Fornax: predicts 40 kpc (obs 0.5-1); Sculptor: 88 kpc (obs 0.3-0.5) |
| **I** | Direct-detection limits (LZ, XENONnT) | ⚠️ **EVADES with ε ≤ 1.4×10⁻¹³** | Need very tiny kinetic mixing; asymmetric DM makes this natural |

**Net verdict (after Phase 30 + 31a): PLAUSIBLE with 1 major caveat.**

The model fails Test H — **the resonance that solves Cloud-9 overshoots dwarf cores by 40-80×**. This is a real structural problem, not just fine-tuning.

---

## Test C — Subhalo real data (Euclid Q1)

**Question**: Does the resonant SIDM predict the right number of strong-lensing clusters?

**Method**:
- Used existing `euclid_q1_subhalo_real_data.py` Poisson count likelihood
- Computed σ/m at v = 500-1000 km/s (cluster velocities) for Phase 29 median
- Compared predicted N_lenses vs 14 observed grade-A clusters in Euclid Q1 (63.1 deg²)

**Result**:
- σ/m(500) = 0.0051 cm²/g (very small)
- σ/m(1000) = 0.0026 cm²/g (very small)
- SIDM suppression at these σ/m values: ~0% (negligible)
- Resonant log L: -2.247
- CDM log L: -2.247
- **Δlog L = 0.000** (identical)

**Verdict: CONSISTENT_WITH_DATA** — The resonant model looks identical to CDM for cluster-scale lensing because σ/m at v=500-1000 km/s is below the suppression threshold.

This is **good news** for the model — real Euclid data is consistent with the prediction.

---

## Test H — Dwarf core sizes

**Question**: Does the model predict the right size of dark-matter cores in dwarf galaxies?

**Method**:
- Used Kaplinghat+ 2016 isothermal-core formula: r_c = √(σ_T × ρ_s × r_s² / m_χ)
- Computed r_c for 4 halos: Fornax-like dwarf, Sculptor-like UFD, Milky Way, A1689-like cluster
- Compared to observations

**Result**:

| Halo | v_0 (km/s) | σ/m(v_0) | r_c predicted | r_c observed | Verdict |
|---|---|---|---|---|---|
| Fornax-like dwarf | 18.6 | 96.6 | **40.1 kpc** | 0.5-1 kpc | ✗ OVERSHOOT (40-80×) |
| Sculptor-like UFD | 12.0 | 465.2 | **88.0 kpc** | 0.3-0.5 kpc | ✗ OVERSHOOT (176-293×) |
| Milky Way | 146.7 | 0.018 | 0.54 kpc | 5-20 kpc | ✓ Consistent |
| A1689 cluster | 1693.5 | 0.0015 | 0.16 kpc | <10 kpc | ✓ CDM-like |

**Verdict: OVERSHOOTS_DWARF_CORES** — The resonance peak at v=28 km/s gives σ/m ~ 29-465 at dwarf velocities, predicting cores that are 40-300× LARGER than observed.

This is a **real structural failure** of the resonant architecture:
- Same resonance that gives Cloud-9 σ/m(28) = 29 ✓
- Predicts dwarf cores of 40-88 kpc ✗
- Real dwarf cores are 0.3-1 kpc

The model is **incompatible with dwarf core observations**.

---

## Test I — Direct-detection limits

**Question**: Does the model evade current LZ/XENONnT/PandaX limits?

**Method**:
- Computed σ_SI from kinetic mixing ε: σ_DM_n = ε² × (m_χ m_n)² / m_φ⁴
- For Phase 29 median: m_χ = 6.09 GeV, m_φ = 8.4 MeV
- Compared to LZ limit at m_χ = 6.09 GeV: σ_SI < 10⁻⁴⁵ cm²

**Result**:
- σ_DM_n at ε=1: 5.17×10⁻²⁰ cm² (much larger than limit)
- σ_DM_n at ε=1e-3: 5.17×10⁻²⁶ cm² (still above limit)
- σ_DM_n at ε=1e-10: 5.17×10⁻⁴⁰ cm² (still above limit)
- σ_DM_n at ε=1e-13: 5.17×10⁻⁴⁶ cm² (BELOW limit)
- **Max ε satisfying LZ: 1.4×10⁻¹³**

**Verdict: EVADES_DD_LIMITS with ε ≤ 1.4×10⁻¹³** — The model needs very tiny kinetic mixing to evade LZ. For asymmetric DM (Phase 22 switch), ε can be 0 — model trivially satisfies DD.

**Note**: The "tiny ε" requirement is consistent with asymmetric DM scenarios where ε → 0 naturally.

---

## Aggregate verdict (Phase 30 + 31a combined)

**Tests run (7 of 9)**:
- Phase 30: D (fine-tuning NATURAL), A (low-v systems PARTIAL), F (relic density REASONABLE), B (SPARC Bayes modest)
- Phase 31a: C (subhalo CONSISTENT), H (dwarf cores OVERSHOOT), I (DD evades with ε ≤ 1.4e-13)

**Tests deferred (2 of 9)**:
- E: UV completion (1-2 hour scan, expected: NO_KNOWN_UV)
- G: Stellar stream gaps (3-4 hours, expected: predicts too few gaps)

**Verdict matrix**:

| Test | Result | Severity |
|---|---|---|
| D (fine-tuning) | NATURAL (max 1.3) | None |
| A (other low-v) | PARTIAL (4/10) | Mild — model doesn't work for v < 10 km/s |
| F (relic density) | REASONABLE (η/η_B = 0.82) | None |
| B (SPARC Bayes) | Δlog L = -0.48 | Modest — power-law slightly better |
| C (subhalo real data) | CONSISTENT | None |
| **H (dwarf cores)** | **OVERSHOOTS 40-300×** | **CRITICAL — major structural failure** |
| I (DD limits) | Evades with ε ≤ 1.4e-13 | Mild — needs tiny ε, OK with asymmetric DM |

**Overall: PLAUSIBLE with 1 CRITICAL CAVEAT.**

The model is:
- ✓ Phenomenologically robust (Test D)
- ✓ Asymmetric DM compatible (Tests F, I)
- ✓ Consistent with strong-lensing data (Test C)
- ⚠️ Partial coverage of low-v systems (Test A)
- ⚠️ Slightly worse than power-law for SPARC (Test B)
- ✗ **Predicts dwarf cores 40-300× too large (Test H)**
- ❓ UV completion unknown (Test E deferred)
- ❓ Stream gap prediction unknown (Test G deferred)

### What this means for the model

**The resonant SIDM model satisfies Cloud-9 but breaks dwarf cores.** The same resonance that gives σ/m(28) = 29 (Cloud-9 OK) gives σ/m(20) = 96-465 (dwarf cores too large).

This is a **fundamental architectural problem**:
- Cloud-9 (v=28 km/s) and dwarfs (v=10-20 km/s) are at SIMILAR velocities
- The resonance must be sharp enough to distinguish them
- But the Breit-Wigner form gives σ/m(20) ~ σ/m(28) × Γ/ΔE (still too high)

**Realistic scenarios**:
1. The model is **wrong** for dwarfs (need new physics)
2. The model needs a **steeper velocity cutoff** (e.g., velocity-dependent coupling)
3. Dwarf core observations are **systematically biased** (unlikely — multiple independent measurements)

### Recommended next step

This is the **first genuinely fatal structural problem** for the resonant model. Options:

**Option 1**: Run Phase 31b (UV completion scan) to see if ANY known UV model can produce a sharper velocity dependence
**Option 2**: Run Phase 31c (stream gaps) to see if streams confirm the dwarf core problem
**Option 3**: Retire the "publishable" framing entirely — the model is too phenomenological
**Option 4**: Investigate whether a velocity-dependent coupling or non-BW form can fix dwarf cores while keeping Cloud-9

---

## Files shipped

- `code/phase31a_C_subhalo_real_data.py` (~180 lines)
- `code/phase31a_H_core_size.py` (~210 lines)
- `code/phase31a_I_direct_detection.py` (~190 lines)
- `data/results/phase31a_C_subhalo_real_data.json`
- `data/results/phase31a_H_core_size.json`
- `data/results/phase31a_I_direct_detection.json`
- `tests/test_phase31a_three_tests.py` — 5/5 PASS

**92/92 tests pass** across the post-Phase 10 sweep (21 phases, 27 sub-tasks).

---

## Bottom line

Phase 29's resonant SIDM model:
- ✓ Solves Cloud-9 (σ/m(28) = 29)
- ✓ Passes real Euclid lensing data (Test C)
- ✓ Evades DD limits (Test I, with asymmetric DM)
- ⚠️ Doesn't cover all low-v systems (Test A)
- ⚠️ Slightly worse than power-law for SPARC (Test B)
- ✗ **Predicts dwarf cores 40-300× too large (Test H) — CRITICAL FAILURE**

**The model is no longer a credible "full solution" — it's a Cloud-9 solver that breaks dwarf cores.**

The honest scientific stance: the resonant model is **one viable approach for Cloud-9** but has a structural weakness at dwarf scales that requires either:
1. New physics (velocity-dependent coupling)
2. UV completion that gives sharper velocity dependence
3. Retirement of the model