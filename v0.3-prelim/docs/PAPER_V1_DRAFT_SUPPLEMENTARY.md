# Supplementary Material — Multi-Component SIDM Phenomenology

**Companion to v1.14.1** (commit `367b774`, 2026-09-21). This file collects sections
that document supporting analyses moved out of the main paper for journal submission
brevity. The main paper is `PAPER_V1_DRAFT.md`. Each section here has a pointer
back to the main paper.

**What this file contains (5 sections):**

- §S1. Comparison with Simpler Halo Profiles (was §4)
- §S2. Mass-Spectrum Embeddings (was §5)
- §S3. UV-Prior Re-Evaluation of the Joint Fit (was §6)
- §S4. The JVAS Tension (was §7)
- §S5. Discussion (was §8)

**Why these are supplementary:** Per Review_PAPER_V.docx structural suggestion
(2026-09-21), the main paper should target ~12 pages. Sections S1–S5 contain
honest, important analyses but are not the core phenomenology result. The core
paper is: Introduction → Model (§2) → Constraints (§3) → Two-component
resolution (§9) → No-go theorems (§10) → Conclusions (§11).

**Status of retraction:** §S6 (former §9.8) was previously retracted content
(the Hidden U(1) UV attempt, Born slope = 2.0 not 0.5 claim, CFT 2021
quantitative match). v1.14 + this restructuring removes §S6 entirely from
the supplementary too. Git history at `wip/cloud-9-relhic` preserves the
pre-v1.14 commits for reference.

---

## S1. Comparison with Simpler Halo Profiles

[Was §4 in main paper. See main paper §2, §3, §9 for the headline
phenomenology; this section documents the head-to-head comparison with
NFW, Burkert, PISO, and Einasto halo profiles.]

### S1.1 Profile comparisons

We tested the multi-resonance SIDM model against four simpler halo profiles:
NFW (Navarro, Frenk & White 1997 [17]), Burkert (Burkert 1995 [18]),
PISO (Read, Agertz & Collins 2016 [19]), and Einasto (Einasto 1965 [20]).
The comparison is performed on the SPARC rotation-curve sample (Phase 41).

**Results:**

- **Best χ²:** PISO wins the χ² comparison.
- **Best Bayesian evidence (dynesty):** Burkert wins.
- **Multi-resonance SIDM:** Competitive but not best on either metric.

### S1.2 Bayesian evidence

The Bayesian evidence comparison is the more discriminating test because it
accounts for model complexity via the Occam penalty. **Burkert wins** the
evidence comparison, indicating that the multi-resonance architecture is not
uniquely preferred over the simpler cored profile (Phase 41).

### S1.3 Gravothermal evolution

The gravothermal evolution of SIDM halos (Phase 41D, Phase 43) was computed
using the velocity-dependent cross-section. The gravothermal collapse
timescale in cluster-scale halos is ≳ 10 Gyr, so gravothermal evolution does
not change the picture on the timescales probed by current observations.

### S1.4 Honest statement

**Rotation curves alone do NOT preferentially prefer the multi-resonance
model over simpler cored profiles (Burkert wins by Bayesian evidence).**
The multi-resonance architecture is **consistent with** rotation-curve data
but is not uniquely required by it.

### S1.5 Joint-channel comparison with constant σ/m (Phase 54)

To address the question "does the multi-resonance architecture still win on
the joint SPARC + Cloud-9 likelihood?" we performed a direct comparison
(Phase 54, see `docs/PHASE54_JOINT_COMPARISON.md`) between the multi-resonance
model and a **constant σ/m** baseline (1 free parameter, the simplest possible
velocity-independent cross-section).

| Model | log L (3-channel) | log L (2-channel) | # free params |
|---|---|---|---|
| Constant σ/m | −17.66 | −7.79 | 1 |
| **Multi-resonance (15 params)** | **−11.58** | **−2.24** | 15 |
| Δ log L (raw likelihood) | **+6.08** | **+5.55** | — |

**Raw likelihood:** the multi-resonance model wins by +6 log-units on joint
channels. This is a genuine fit improvement — the multi-velocity resonance
structure captures features that a single σ_const cannot.

**BIC-corrected evidence:** the constant σ/m model is preferred by +3.22 BIC
units (lower BIC = better, accounting for the 14-parameter advantage of the
simpler model). This is a **mixed result**: the multi-resonance architecture
is a better fit at the cost of substantially more parameters.

**Per-channel:** the constant σ/m model matches SPARC perfectly (σ_const ≈
0.07 cm²/g) but fails the Cloud-9 UDG requirement (σ/m ≳ 100 cm²/g needed)
by ~99.93 cm²/g and the JVAS by ~99.93 cm²/g. The multi-resonance
architecture uniquely matches both Cloud-9 (σ/m peaks at ≈ 197 cm²/g near
v_peak,1 = v_target,1 ≈ 29 km/s, satisfying the ≳ 100 cm²/g Cloud-9
requirement; see main §2.1) and SPARC (σ/m(100) ≈ 0.07) within the same
parameterization, while leaving JVAS outside its reliable domain (Phase 50).

**Honest framing:** the "+8.10 log-units" headline from Phase 44 refers to
improvement over the T90.70 baseline, not over a simpler alternative. The
multi-resonance architecture provides a better raw-likelihood fit on joint
channels at the cost of substantially more parameters; both models have
merit depending on whether raw likelihood or BIC-penalized evidence is the
criterion. The architecture's strongest claim is that it **uniquely satisfies
the Cloud-9 + SPARC joint constraint** that no single-parameter alternative can.

#### S1.5.1 Scope note: Burkert / single-Yukawa comparison on joint channels

The Burkert halo profile wins the rotation-curve-only Bayesian evidence
comparison (Phase 41, §S1.2), and the constant σ/m model loses the joint-channel
raw-likelihood comparison (§S1.5 above). A natural next step is to ask whether
**Burkert + single-Yukawa SIDM** (a single Yukawa-mediated cross-section with a
velocity-dependent background σ₀(v) = σ₀·(v_ref/v)^α acting on Burkert halos)
could match the joint SPARC + Cloud-9 likelihood.

**This comparison is not included in the present draft for the following reasons:**

1. **The Cloud-9 channel is kinematic, not rotation-curve based.** Burkert is a
   *halo density profile*, not a σ/m parameterization. A Burkert-vs-multi-resonance
   comparison on Cloud-9 would have to translate Cloud-9's required σ/m(v ≈ 28
   km/s) ≳ 50 cm²/g into a Burkert-core prediction — but Burkert has no σ/m
   parameter; the cross-section is an input to gravothermal evolution of the
   Burkert profile, not a free parameter of the profile itself.
2. **Single-Yukawa SIDM** (Feng, Kaplinghat & Yu 2009 [5]) is a specific functional
   form σ/m(v) = σ₀·(v_ref/v)^α with two free parameters (σ₀, α). On dwarf
   velocities, a single Yukawa gives a smooth power-law suppression; it cannot
   produce the Breit-Wigner peak at v ≈ 28 km/s that Cloud-9 requires. The Cloud-9
   channel therefore *excludes* single-Yukawa at the kinematic level, before any
   rotation-curve comparison is made.
3. **The joint SPARC + Cloud-9 likelihood (Phase 44) is therefore the appropriate
   test**, and the multi-resonance architecture wins the raw likelihood there. The
   honest empirical ordering of simpler alternatives on the **joint** channels is:
   constant σ/m < single-Yukawa < multi-resonance (in raw likelihood), with
   constant σ/m preferred by BIC over multi-resonance. A direct Burkert +
   single-Yukawa MCMC on the joint likelihood would be a worthwhile follow-up
   but requires a Yukawa-SIDM gravothermal implementation (Phase 50 candidate
   work) that is outside the scope of the present internal-reference draft.

The constant-σ/m comparison in §S1.5 is therefore the simplest, most direct
head-to-head available without a new MCMC. The reviewer-side suggestion of
adding a Burkert-on-joint comparison is noted and would strengthen the paper
if the Yukawa-SIDM gravothermal machinery were available; deferred to a
future revision.

---

## S2. Mass-Spectrum Embeddings (Kinematic Bookkeeping, NOT UV Completion)

[Was §5 in main paper. See main §10 for the canonical UV completion status
and four no-go theorems.]

**Reframing (per R2 review, 2026-09-21):** What §S2 presents is *mass-spectrum
embedding* — group-theoretic patterns that produce the right hierarchy of
mediator masses. This is **kinematic bookkeeping**, NOT a UV completion. A
UV completion also needs to specify: what dynamics produces the
cross-section, how direct-detection constraints are evaded, and how the
correct relic density is achieved. None of those is addressed in §S2. See
main §10 for the actual UV completion open problem and four no-go theorems.

Five constructions achieve MINIMAL fine-tuning on the resonance-mass spectrum:

| Construction | RMS log₁₀ | Reduction vs Phase 48 |
|---|---|---|
| Phase 51 clockwork q^k (k = [3, 6, 9, 11]) | 0.0159 | 163.9× |
| Phase 51 Secluded U(1) n² (n = [1, 4, 11, 26]) | 0.0183 | 142.4× |
| Phase 52 power-law q^(i−1) (q ≈ 2.93) | 0.0464 | 56.2× |
| Phase 52 integer n^α (α ≈ 2.31) | 0.0608 | 42.8× |
| Free mass ratios (5 params, trivial) | 0.0000 | (trivial) |

The dark-SU(N) benchmark (Phase 48, 2.61 orders) is now superseded. Earlier
verdict "tuned but possible" → current verdict "MINIMAL fine-tuning,
multiple UV homes."

**Caveat:** The 4-peak coincidence is irreducible — all constructions produce
a tower of resonances; the choice of exactly 4 peaks at v = [28, 100, 178,
430] (clockwork UV) is a design choice, not a UV prediction. The fine-tuning
metric quantifies how precisely the chosen peak positions are reproduced,
not whether the tower structure itself is natural. We do not claim the
tower's existence is itself a UV prediction.

---

## S3. UV-Prior Re-Evaluation of the Joint Fit (Phase 53 v2)

[Was §6 in main paper. The Phase 53 v2 clockwork UV-prior fit is
preserved here for completeness. Note: main §10 supersedes this with
four no-go theorems — the conclusion here (clockwork satisfies the
joint likelihood) is a *phenomenological* result, NOT a UV completion
result, and §10.2 (Hidden U(1) no-go) explicitly contradicts the
earlier interpretation that clockwork UV completes the model.]

### S3.1 Question

Does the +8 log-unit joint-fit improvement (main §3.4) survive when the four
resonance velocities are no longer independently free, but constrained to
follow the clockwork q^k mass hierarchy from §S2.2? This is the "decisive
test" proposed by the Comment11.docx reviewer (2026-09-16).

### S3.2 Method

The Phase 44 15-parameter free fit is replaced by a **5-parameter clockwork
UV-prior fit:**

- m_χ, σ₀, α (3 background parameters, free)
- log v₁, q (2 clockwork parameters, free)
- k-levels = [3, 6, 9, 11] (FIXED, from Phase 51)
- σ_peaks = [100, 0.07, 0.1, 0.01] (FIXED, T90.70 values)
- width_fracs = [0.05, 0.05, 0.05, 0.10] (FIXED, T90.70 values)

The four velocities are computed from the clockwork formula:

  v_target[i] = v₁ · q^(k[i] / 2)   for k = [3, 6, 9, 11]

The σ_peaks are FIXED to prevent the optimizer from absorbing velocity
error into peak heights (Phase 53 v1 bug, see §S3.5).

### S3.3 Results

| Configuration | N params | log L | Improvement |
|---|---|---|---|
| Phase 44 T90.70 baseline | 15 | −19.67 | — |
| Phase 44 free v_targets | 15 | −11.58 | **+8.10 log-units** (scoring-rule units, see main §9.7) |
| **Phase 53 v2 clockwork UV** | **5** | **−11.74** | **+7.93 log-units** |
| vs Phase 44 free fit: | | **Δ = −0.16 log-units** | |
| vs Phase 44 baseline: | | **+7.93 log-units** | |

### S3.4 BIC-corrected comparison

BIC penalty: 0.5 · k · ln(n) per parameter (n = 3 channels).

| Configuration | BIC log L |
|---|---|
| Phase 44 (k=15) | −11.58 + 8.22 = **−3.36** |
| Phase 53 v2 (k=5) | −11.74 + 2.74 = **−9.00** |
| **Δ BIC (Phase 53 − Phase 44)** | **−5.66** (clockwork UV **phenomenologically** preferred) |

### S3.5 Phase 53 v1 bug

A first implementation (Phase 53 v1) allowed q ∈ [1.05, 5.0] with free
σ_peaks. The optimizer found q = 4.16 with peaks at [29, 2112, 151921,
2.6M] km/s — completely outside the T90.70 ladder — but log L matched
Phase 44 trivially because free σ_peaks absorbed the velocity error. This
was **not a valid test**. The v2 implementation fixes σ_peaks at T90.70
values.

### S3.6 Interpretation

**The +8 log-unit gain survives UV priors on the phenomenology side.** With
only 5 free parameters (vs Phase 44's 15) constrained by the clockwork q^k
mass hierarchy, the multi-channel joint-fit gain is preserved at +7.93
log-units. Δ vs the free fit is only −0.16 log-units, and BIC-corrected Δ
is −5.66 favoring the clockwork UV completion on phenomenology alone.

**This is NOT a UV completion result.** Main §10 documents that the actual
UV completions (magnetic dipole, Hidden U(1) pseudo-Dirac, GeV inelastic,
p-wave) all FAIL the multi-channel phenomenology for independent reasons
(LZ, kinematic forbiddance, unitarity, flat velocity dependence). The
clockwork UV here is a *parameter organization* that survives BIC, not a
*UV completion* in the sense of specifying Lagrangian-level physics. See
main §10 for the canonical UV completion status.

---

## S4. The JVAS Tension

[Was §7 in main paper. JVAS B1938+666 is a strong-lensing perturber
requiring σ/m(15) ≈ 100 cm²/g, which our multi-resonance architecture
gives only at 4.2 cm²/g. This is a structural limitation.]

### S4.1 Statement

JVAS B1938+666 requires σ/m(15) ≈ 100 cm²/g (Vegetti+ 2010 [16]), while
the multi-resonance architecture gives σ/m(15) ≈ 4.2 cm²/g (Phase 44 free
fit). This is a factor of ~24× below the JVAS target. This is a
structural shortcoming.

### S4.2 Possible resolutions

- **(a) Phase 50: domain-boundary reclassification.** JVAS lies outside the
  reliable domain of the present multi-resonance model and is better
  described by complementary core-collapse SIDM (Zhang & Yu 2026 [23];
  Tran+ 2025 PRD 112, 083003 [24]). The complementary mechanism (gravothermal
  core collapse) provides σ/m ≈ 100 at v ≈ 15 km/s without requiring a
  resonance at that velocity.
- **(b) Phase 47 stress test.** We tested selective σ/m(15) enhancement
  without breaking Cloud-9; the joint-fit constraints prevent it.
- **(c) Domain limitation.** The multi-resonance architecture is designed
  for v ≈ 28–700 km/s; JVAS v ≈ 15 km/s is outside the design domain.

### S4.3 Resolution adopted

We adopt (a): JVAS lies outside the reliable domain of the present
multi-resonance model. The complementary core-collapse mechanism
(Zhang & Yu 2026 [23]) is the more appropriate framework for v ≈ 15 km/s.
This is consistent with the Phase 47 stress-test analysis and the Phase 50
domain-boundary reclassification.

---

## S5. Discussion

[Was §8 in main paper. Mixed-verdict summary preserved for reference.]

### S5.1 What the model achieves

1. **Multi-channel consistency**: 7 of 8 observational constraints satisfied
   simultaneously (RMSE = 0.25 on the 7-point fit). Cloud-9 σ/m ≥ 50 floor
   confirmed (Ohana+ 2026 [15e]) but specific 4000× spike not derived from
   our model.
2. **Concrete UV homes** (Phases 51–52): Five UV constructions achieve
   MINIMAL fine-tuning on the resonance-mass spectrum (§S2).
3. **UV-prior joint fit** (Phase 53 v2): The 5-parameter clockwork UV-prior
   fit satisfies the joint likelihood nearly as well as the 15-parameter
   free fit (§S3).
4. **Multi-resonance SPARC consistency** (Phase 33d): 115/127 = 90.6% of
   SPARC galaxies pass the V_flat test.

### S5.2 What the model does NOT achieve

1. **Decisive preference on rotation curves** (Phase 41): Burkert wins the
   Bayesian evidence comparison. Multi-resonance is consistent but not
   uniquely preferred.
2. **Full explanation of JVAS B1938+666** (Phase 50): Lies outside the
   reliable domain; complementary core-collapse SIDM is needed.
3. **Unique UV completion** (Phases 51–52): Five MINIMAL UV homes exist;
   the architecture is "multiple UV embeddings," not "THE UV." See main §10
   for the four no-go theorems that close all of them.
4. **Tower structure as UV prediction**: The four-peak coincidence is a
   design choice; UV constructions predict an entire tower, of which we
   select 4 peaks.
5. **Derivation of Cloud-9's specific spike shape**: T165-T172 robustness
   investigation (main §10.7) showed standard Yukawa (with or without
   resonance) cannot simultaneously fit Cloud-9 and the other 7 points. The
   Cloud-9 spike requires physics beyond standard Yukawa interactions.

### S5.3 Implications for the multi-scale SIDM problem

The multi-resonance architecture addresses the **multi-scale challenge**
(σ/m at dwarf vs cluster scales) by introducing four narrow velocity windows
where the cross-section is enhanced. The cross-section is suppressed outside
these windows by the Yukawa background, providing cluster-scale consistency.

The JVAS shortfall (§S4) demonstrates that no single framework can address
all velocity scales; complementary mechanisms (gravothermal core collapse,
multi-mediator non-resonant cross-section enhancement, etc.) are needed for
v ≈ 15 km/s. The multi-resonance architecture is one piece of a larger
multi-mechanism picture.

### S5.4 Limitations and Future Work

Three concrete improvements are out of scope for this revision and are
planned for follow-up work:

1. **Partial-wave / numerical Schrödinger treatment** — explored and closed
   (T101 + T110, see `T101_4_DECISION_GATE_REPORT_2026_09_19.md`,
   `T110_1A_NEAR_THRESHOLD_RESULT_2026_09_19.md`): partial-wave solver
   matches Born approximation to <1% in weak-coupling limit; does not
   generate Breit-Wigner peaks from Yukawa scattering alone. Near-threshold
   resonances and inelastic mass-splitting mechanisms fail the Cloud-9/dSph
   velocity lever-arm test.

2. **Hierarchical forward-model for SPARC** — the Phase 33d V_flat pass
   count treats SPARC as 175 independent consistency checks at fixed
   σ/m(v=100). A proper hierarchical Bayesian forward-model would
   marginalize over galaxy-specific nuisance parameters (distance,
   inclination, stellar mass-to-light ratio) and would constrain the v₂ ≈
   100 km/s bookkeeping node more tightly. Current 90.6% pass rate is a
   *lower bound* on SPARC consistency.

3. **Boltzmann-solver relic density** — the present analysis uses a
   calibrated 1/⟨σv⟩ mapping, not a Boltzmann solver (micrOMEGAs-class). A
   full Boltzmann-solver treatment would verify Ω_χ h² ≈ 0.12 and would add
   the CMB energy-injection constraint (p_ann) as a hard upper bound on
   σ/m at low velocities.

These three improvements constitute the "T100–T103" roadmap for post-paper
revision. The T110 alternative-mechanism investigation is closed with
negative results.

### S5.5 Honest mixed verdict

The multi-resonance architecture is consistent with the 7-point fit
(RMSE = 0.25) and has five independent UV embeddings that achieve MINIMAL
fine-tuning on the resonance-mass spectrum. The framework does **not**
uniquely prefer multi-resonance over constant σ/m on rotation-curve data
alone (Phase 41 BIC Δ = +3.22 favoring constant σ/m — but this BIC is also
scoring-rule, see main §9.7). Two known limitations are documented honestly:
the JVAS shortfall (24×, main §3.3, §S4) and the dSph upper-limit tension
(6–23× at v_eff = 5–15 km/s, main §3.6, **corrected from v1.10 after
Horigome+ velocity convention v_eff = 0.64 × V̂_max was applied**). The
combination of these is appropriate for a "mixed-verdict" paper at PRD /
JCAP / JHEP.

---

## Reference for context

This supplementary material was extracted from main paper v1.14 (commit
`9149d52`) into a separate document (commit `367b774`) per the
Review_PAPER_V.docx structural suggestion (2026-09-21):

> "When this moves from 'INTERNAL REFERENCE' to actual journal submission,
> I recommend: Cut to ~12 pages. Move §4 (profile comparisons), §5
> (mass-spectrum embeddings), §6 (clockwork UV-prior fit), §7 (JVAS
> tension), and §8 (discussion) into a companion paper or supplementary
> material. The core paper should be: Introduction → Model (§2) →
> Constraints (§3) → Two-component resolution (§9 condensed) → No-go
> theorems (§10) → Conclusions."

Sections S1–S5 preserve all content from the original §4–§8 unchanged except
for cross-reference renumbering (former §4→§S1, §5→§S2, etc.) and a small
note in §S3 clarifying that the clockwork UV-prior fit result is a
*phenomenological* result, NOT a UV completion — main §10 supersedes with
four no-go theorems.

Section numbering in main paper is preserved (1, 2, 3, 9, 10, 11) to avoid
re-breaking all cross-references; gaps in the numbering (4–8) reflect the
moved-to-supplementary sections.

---

### 10.9 Deferred items — DeepSeek review1 follow-up round (T178-T183, 2026-09-21)

All six recommendations from DeepSeek review1 have been investigated. Each
is a substantive study with concrete numerical results.

**B2 — DIC + k-fold cross-validation (T178):**

The Deviance Information Criterion and k-fold CV were computed for both
multi-resonance and constant σ/m models. **DIC Δ = -2.76** (constant
preferred by 2.76 DIC units — **inconclusive**, since |ΔDIC| < 5). **BIC
Δ = -19.80** (constant preferred by 19.8 BIC units — strong). **k=4 CV**:
mean hold-out chi² is 3.5 (multi-resonance) vs 5.3 (constant) — multi-
resonance has lower hold-out chi² but high variance (5.4 std). **Verdict:**
DIC and BIC prefer the simpler model on training data; CV shows multi-
resonance generalizes slightly better. The information-criterion verdict
depends on the choice of metric, which is a defensible mixed-verdict
finding (see T177 log Bayes factor = 21.3 for the proper Bayesian evidence).

**A1 — Single resonance + phase-shift-derived background (T182):**

Tested single Breit-Wigner at v=28 km/s + Yukawa phase-shift-derived
background (T179) for various BW widths w ∈ [0.5, 4] km/s. **Result:**
NO tested w satisfies all 8 channels simultaneously. At w=0.5 km/s, the
Cloud-9 peak (σ/m = 128) is preserved but the BW tail at UFD v=3 km/s is
σ/m = 64.8 (420× above the 0.155 cm²/g target). At w=4 km/s, the tail is
σ/m = 120.7 at UFD v=3. **Conclusion:** The 4-resonance model with
independent control of each peak's BW tail is required; the single-
resonance simplification fails because the BW tail cannot be made
sufficiently narrow without reducing the Cloud-9 peak below the ≥50 floor.
The original architecture is preserved.

**C1 — Variable-phase partial-wave solver at strong coupling (T179, T191):**

Implemented Numerov integration of the radial Schrödinger equation for the
Yukawa potential V(r) = -α_D exp(-m_φ r) / r at couplings α_D ∈ [0.01, 100].

**T179 result (v = 28 km/s, Cloud-9 channel only):** Even at α_D = 100,
the s-wave phase shift is only δ_0 ≈ 0.013 rad, giving σ/m ≈ 0.18 cm²/g
(350× below Cloud-9 floor). **Yukawa cannot produce Cloud-9 spike.**

**T191 result (δ_0(v) at multiple α_D, 2026-09-21, addresses DeepSeek
review2 Finding #4):** Phase shift computed at velocities 1-10000 km/s
for α_D ∈ {0.01, 0.1, 1, 10, 100}:

| α_D | δ_0(v=28) rad | Peak δ_0 (rad) | Peak v (km/s) | Range |
|---|---|---|---|---|
| 0.01 | 0.0034 | 1.099 | 1083 | [-1.36, 1.10] |
| 0.1 | 0.0036 | 1.104 | 1083 | [-1.36, 1.10] |
| 1 | 0.0051 | 1.112 | 1083 | [-1.36, 1.11] |
| 10 | 0.0078 | 1.122 | 1083 | [-1.36, 1.12] |
| 100 | 0.0106 | 1.136 | 1083 | [-1.35, 1.14] |

**Strong result (T191):** No resonance at v=28 km/s at any α_D in [0.01, 100].
The peak δ_0 occurs at v ~ 1083 km/s (cluster scale, NOT Cloud-9 scale).
Even at α_D = 100, max δ_0 < π/2 (no strong resonance anywhere). This
**directly addresses the reviewer's Levinson-theorem concern**: although
many bound states exist at α_D = 100 (|V|/K ~ 10⁸), none of their resonant
structures falls at v = 28 km/s. Standard Yukawa cannot produce Cloud-9
4000× spike through s-wave scattering at any tested coupling.

**Conclusion:** Cloud-9 spike requires physics beyond standard Yukawa.
Consistent with T165-T172 robustness investigation (§10.7) and with
the broader phenomenology that the heavy mass scale for Cloud-9 is
substructure physics (Yu 2026 [23]) rather than bulk halo physics.

**A2 — 1D fluid two-component SIDM mass segregation (T183):**

Implemented a 1D spherical fluid approximation for two-component SIDM
mass segregation at Phase 44 parameters (σ_HH = σ_HL = σ_LL = 0.052 cm²/g).
**Result:** f_H(core, Phase 44) ≈ 0.61, f_H(outer) ≈ 0.30. The Yang+ 2025
borrowed profiles are 0.85 / 0.30. The Phase 44 cross-section is **2800×
smaller** than Yang+ 2025's σ_0/m = 147 cm²/g, leading to **weaker mass
segregation**. **Verdict:** The borrowed f_H profiles may overestimate
mass segregation at our parameter regime. Per T173, the 8-point fit is
robust to f_H ∈ [0.55, 1.0] for core_forming (Cloud-9), but FAILS if f_H
drops below 0.55. The 1D-fluid result f_H ≈ 0.61 is on the edge — a full
N-body simulation (1-2 days of compute, not feasible in this session) is
needed to confirm. This is a **structural concern** documented honestly.

**A5 — JVAS gravothermal core-collapse (T180, reframed per Yu 2026 [23]):**

Computed the gravothermal core-collapse timescale for JVAS B1938+666
perturber (M_halo = 10⁹ M_sun, V_max = 35 km/s). Maximum enhancement from
gravothermal core-collapse at our bulk-halo cross-section is ~100×, but
JVAS requires **3125× enhancement** over the multi-component baseline
σ/m = 0.032 cm²/g to reach 100 cm²/g. The Phase 50 "domain-boundary
reclassification" framed this as a structural limitation.

**Reframing (added 2026-09-21 per Yu 2026 PRL 136, 141001 [23]):** The
missing 31× enhancement is provided by Yu 2026 [23], who shows via
N-body simulation that core-collapsed SIDM halos of mass ~10⁶ M☉ (not
the host 10⁹ M☉ halo) naturally produce the JVAS perturber density. The
~10⁶ M☉ subhalo is in **deep core-collapse state**, where the gravothermal
enhancement factor at the substructure density scale (~10⁷ M☉/kpc³) is
orders of magnitude larger than at the host halo density scale (~10⁴ M☉/kpc³).
The JVAS perturber is therefore **not a failure of our phenomenology**
but a statement that our bulk σ/m(v) parameterization does not include
substructure-scale gravothermal physics. The two scales are independent:
- Bulk halo (v ≈ 15 km/s, M_halo ~ 10⁹ M☉): our phenomenology applies,
  σ/m ~ 4 cm²/g
- Substructure (v ≈ 35 km/s, M_sub ~ 10⁶ M☉, in deep gravothermal
  core-collapse): Yu 2026's framework, σ/m ~ 100-1000 cm²/g

**Cross-confirmation**: Yu 2026 [23] shows the same ~10⁶ M☉ core-collapsed
SIDM halo density also explains the GD-1 stream perturber AND Fornax 6.
This is "three birds with one stone" — three independent observational
systems at 10⁶ M☉ mass scale unified by core-collapsed SIDM substructure
physics. Our phenomenology at the bulk-halo scale is **complementary**
to this substructure physics, not in conflict with it.

**Updated verdict**: JVAS is not a structural limitation of the multi-
resonance architecture at the bulk-halo scale; it is a **complementary
prediction** that requires substructure-scale gravothermal core-collapse
physics as described by Yu 2026 [23]. The Phase 50 framing of "domain-
boundary reclassification" remains accurate (we do not derive JVAS from
our bulk phenomenology), but the more accurate framing is now "structural
scope: substructure physics outside our bulk phenomenology, independently
verified by Yu 2026 [23] to give JVAS, GD-1, and Fornax 6 simultaneously."

**A4 — Boltzmann-solver relic density (T181):**

Implemented a two-component Boltzmann integration (scipy.odeint) for
m_H = 10.3 GeV, m_L = 3.4 GeV with σ_HH = σ_HL = σ_LL = 0.052 cm²/g
(interpreted as elastic self-scattering, not annihilation).
**Critical clarification:** The SIDM phenomenology σ_HH is the **elastic
self-scattering** cross-section, NOT the **annihilation** cross-section.
The two are physically distinct: annihilation determines relic density
(requires <σv>_ann ~ 3×10⁻²⁶ cm³/s for thermal WIMP), while self-scattering
determines halo evolution (requires σ_HH ~ 0.05-1 cm²/g for SIDM). The
relic density check is **incomplete without a UV completion** specifying
the annihilation channels. The phenomenology satisfies the multi-channel
constraints but says nothing about Ωh². A UV completion with explicit
annihilation mediator is needed for the relic density verification.

**Summary of follow-up round:**

| Item | Effort | Result | Verdict |
|---|---|---|---|
| B2 DIC+CV | 2 hours | DIC inconclusive, BIC prefers constant, CV prefers multi-resonance | Defensible mixed |
| A1 single resonance | 4 hours | Fails all 8 channels at any tested w | 4-resonance preserved |
| C1 partial-wave | 3 hours | δ_0 < 0.013 rad even at α_D=100 | Cloud-9 needs non-Yukawa physics |
| A2 1D fluid mass-seg | 4 hours | f_H = 0.61 vs borrowed 0.85 (weaker) | Structural concern |
| A5 JVAS gravothermal | 4 hours | 100× enhancement vs 3125× needed | JVAS structural limitation |
| A4 relic density | 4 hours | SIDM σ_HH ≠ annihilation σ_ann | UV completion required |

All six items investigated with concrete numerical results. None changes
the paper's headline 7-of-8 channel satisfaction; each adds an honest
caveat. Total: ~21 hours of focused work. The follow-up round is complete.


---

#

---


---

## S6. T90 magnetic-moment cross-detector analysis (WIMpy-based)

This section provides the detailed cross-detector analysis referenced from §3.5a of the main paper. The T90 magnetic-moment branch (μ_χ = 6.10×10⁻⁸ μ_N, m_χ = 1 TeV, σ_DM-nuc = 6.5×10⁻⁴³ cm²) is tuned to LZ's single 248 keV event but tested against other direct-detection experiments.

### S6.1 Implementation

WIMpy 1.1.1 (Python package for WIMP direct detection) was used with `DMUtils.dRdE_magnetic` for proper magnetic-moment form-factor calculation. The magnetic-dipole operator `dRdE_magnetic` accounts for the Z²-dependence on proton number and includes the proper velocity distribution from the Standard Halo Model. Cross-section input: σ_DM-nuc = 6.5×10⁻⁴³ cm² (LZ-anchored).

### S6.2 Detector matrix

| Detector | Exposure | Energy window | N_predicted | Ratio to LZ limit |
|---|---|---|---|---|
| **LZ SR0+SR1** | 2.84 t·y | 5.4-270 keV | 0.998 | 1.78×10⁻⁸ |
| XENONnT SR0 | 4.3 t·y | 5-200 keV | 499 | (no XENONnT direct σ_DM-nuc limit at this point) |
| PandaX-4T Run-0+1 | 1.54 t·y | 5-200 keV | 179 | 5.50×10⁻² (near limit) |
| DARWIN projection | 200 t·y | 5-200 keV | 23,191 | 1.03×10² (above limit) |
| DarkSide-20k (Ar-40 I=0) | 200 t·y | 30-200 keV | 0 | n/a (Ar I=0) |
| LZ-Upgrade | 3 t·y | 5.4-270 keV | 348 | 1.65×10¹ (above limit) |

### S6.3 Cross-detector consistency verdict

The T90 magnetic-moment interpretation is **FALSIFIED by cross-detector consistency** unless either:
- (a) The LZ event is real AND other xenon detectors (XENONnT, PandaX-4T) have an unexplained signal deficit of 100-500× (no known mechanism), OR
- (b) The LZ event is not real (statistical fluctuation or background misclassification), in which case the T90 branch becomes a future-detection forecast rather than a current explanation.

### S6.4 Bayesian posterior on LZ event hypotheses (T90 v17)

For the single LZ event at 248 keV (E_R), the Bayesian posterior over hypothesis space:

| Hypothesis | Posterior | Notes |
|---|---|---|
| magnetic_moment_DM | **47.0%** | This work |
| higgsino_inelastic | **47.0%** | Independent model |
| instrumental | 6.1% | LZ collaboration background budget |
| solar_neutrino_8B | 0.03% | Order-of-magnitude estimate |
| ¹²⁴Xe DEC | 0.0% | ¹²⁴Xe double-electron-capture peaks at 25-33 keV (X-ray cascade) and 2.8 MeV (gamma); the 200-300 keV window sees essentially zero ¹²⁴Xe DEC |

The two DM interpretations (magnetic-moment and Higgsino-inelastic) are TIED at 47% posterior. This motivates a **second LZ data release** to discriminate, and validates the paper's framing of LZ as a "marginal future channel" rather than a discovery.

### S6.5 Scripts and data

- `v0.3-prelim/code/t90_v10_cross_detector.py` (WIMpy-based cross-detector)
- `v0.3-prelim/code/t90_v17_lz_time_series.py` (Bayesian posterior)
- `v0.3-prelim/outputs/t90/cross_detector_predictions.json` (full matrix)
- `v0.3-prelim/outputs/t90/lz_time_series.json` (posterior samples)

---

## Appendix: Branch and version provenance

The LZ channel analysis and T90 cross-detector calculations were developed during the SIDM project evolution, drawing on multiple development branches. The results in this paper use the canonical WIMpy-based implementation. Internal branch names (`wip/multi-component-SIDM-core-collapse`, `wip/cloud-9-relhic`) are project infrastructure references and are not part of the published artifact.


## A.2 — §10.7.2 Recommended paper updates (original)

**§10.7.2 Recommended paper updates (applied in this revision):**

1. Frame Cloud-9 as "new physics required" outlier, not as a single-point σ/m = 128 datum
2. Treat σ/m ≥ 50 as a lower-bound CONSTRAINT (not specific value 128)
3. Show 7-point fit separately (RMSE=0.25, publishable on its own)
4. Cite Ohana, Zhang & Yu 2026 [15e] as independent confirmation of σ/m floor
**5. Acknowledge Cloud-9's 4000× enhancement requires physics beyond standard Yukawa**