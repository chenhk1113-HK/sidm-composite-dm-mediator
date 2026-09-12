# Roadmap — Major Posteriors NOT in Current Model (2026-09-12)

**Status:** ROADMAP ONLY. No code changes implied. Future project phases require explicit user direction to begin.

**Current model:** 4D joint posterior (log_σ/m_0, a, log_ε, log_α), fed by 10 channels (Ch1-lens_subhalo, Ch2-dSph, Ch3-UFD, Ch4-cluster, Ch5-Draco, Ch6-radio_relic, Ch7-MW_satellite, Ch8-CKM, Ch9-dm_free_udg, Ch13-dm_dom_udg).

**Reference:** T39 Tier-3 fit at `v0.3-prelim/data/results/t39_tier3_epsilon_alpha_joint_fit.json` shows log_Z = -2.94, MAP (σ/m_0, a, ε, α) = (-0.14, 1.31, 10^-56, 10^-28).

---

## Summary table — 7 missing posteriors, ranked

| # | Missing posterior | Dimensions | New total | Priority | Estimated cost | Particle physics gain | Status |
|---|---|---|---|---|---|---|---|
| 1 | DM mass (m_χ) | +1 | 5D | **HIGH** | 1–2 weeks | High — direct-detection prediction | Not started |
| 2 | Mediator mass (m_A') | +1 | 5D | **HIGH** | 1–2 weeks | High — distinguishes mediator models | Not started |
| 1+2 | **m_χ + m_A' jointly** | **+2** | **6D** | **HIGH** | **2–4 weeks** | High — physically meaningful | Not started |
| 4 | Baryonic feedback | structural | — | **HIGH** ↑ | 4–8 weeks (sims) OR **1–2 weeks minimal** | **High — R1: "fundamental degeneracy"** | Not started |
| 6 | Cross-channel correlations | structural | — | **MEDIUM** ↑ | 1–2 weeks OR **1 week minimal** | **Medium — R1: "statistically invalid"** | Not started |
| 3 | Particle-physics model class | structural | — | MEDIUM | 2–4 weeks | Medium — vector vs scalar vs composite | Not started |
| 7 | Time-dependence (gravothermal) | +1 | 5D | LOW | 2–4 weeks (sims) | Low — core-collapse timeline | Not started |
| 5 | Cosmological initial conditions | structural | — | LOW | 3–6 months | Low — alternative DM models | Not started |

**Note on dimensional accounting** (corrected per R1 mapreview.docx Gap 3):
- 4D baseline = (log_σ/m_0, a, log_ε, log_α)
- 4D + m_χ = **5D**
- 4D + m_A' = **5D**
- 4D + (m_χ + m_A' jointly) = **6D** (NOT 5D — earlier table said "+1 (5D total)" for both, which was incorrect)
- Doing them jointly is the physically meaningful calculation: σ/m ∝ α^2 m_χ / m_A'^4 depends on both simultaneously

---

## Missing posterior #1: Dark matter mass (m_χ)

### What's missing

The model assumes m_χ is in the GeV–TeV (WIMP-like) range but **does not fit for it**. The astrophysical channels constrain σ/m (cross-section per unit mass) but are insensitive to the absolute mass scale.

### What it would add

- Testable prediction for direct-detection experiments (recoil spectra scale with m_χ)
- Connection to early-universe cosmology (freeze-out, freeze-in scenarios)
- Bridge between astrophysics and lab physics

### How to add it

1. Extend prior to m_χ ∈ [0.1, 1000] GeV (log-uniform)
2. Convert σ/m_0 → σ × m_χ/m_A'^2 to expose mass dependence
3. Add LZ direct-detection bound as Ch14 (recoil spectrum channel)
4. Add CMB bounds as Ch15 (acoustic peak damping scale)
5. Re-run 4D → 5D joint fit with `t39_5d_extended_fit.py`

### Cost estimate

**1–2 weeks.** Most work is data wrangling (LZ recoil spectra, CMB damping bounds).

### Risk

Low. The geometry is straightforward; the challenge is getting LZ/CMB data into the right format.

### Particle physics payoff

**Transformative.** The model would shift from "phenomenology" to "particle physics" by giving a target m_χ for experimentalists.

---

## Missing posterior #2: Mediator mass (m_A')

### What's missing

The model treats σ/m as a phenomenological cross-section, agnostic to the underlying mediator mass. But the mediator mass determines:
- Cosmological history (early-universe annihilation rate)
- Beam-dump / fixed-target signatures
- Stellar cooling rates (HB stars, SN1987A)

### What it would add

- Distinguish dark photon mediator (vector, m_A' ~ MeV–GeV) from dark Higgs (scalar, m_φ ~ MeV–GeV) from dark pion (composite)
- Predict beam-dump signatures (NA64, beam-dump at FNAL)
- Bound the mediator mass from stellar cooling

### How to add it

1. Extend prior to m_A' ∈ [1, 1000] MeV (log-uniform)
2. Convert σ/m_0 → coupling × g^2/m_A'^4 to expose mediator dependence
3. Add beam-dump constraints (Ch16)
4. Add stellar cooling bounds (Ch17)
5. Re-run 5D → 6D joint fit

### Cost estimate

**1–2 weeks.** Similar to #1, mostly data wrangling.

### Risk

Medium. Different mediator models (vector vs scalar vs composite) give different functional forms — choosing the wrong one locks you into a wrong parameterization.

### Particle physics payoff

**Transformative.** Mediator mass distinguishes mediator models, which is the question every reviewer asks.

---

## Missing posterior #3: Particle-physics model class (structural)

### What's missing

The current model is **elastic, point-like, contact-interaction SIDM**. It does not distinguish:
- **Dark photon mediator** (vector, A')
- **Dark Higgs mediator** (scalar, φ)
- **Dark pion exchange** (composite, from dark QCD)
- **Yukawa potential** (long-range, finite m_A')

At galactic scales, all these give similar σ/m(v). At lab or cosmological scales, they predict very different behavior.

### What it would add

- Ability to test which mediator class the data prefers
- Connection to specific UV completions (e.g., freeze-in via Higgs portal for scalar; kinetic mixing for vector)

### How to add it

1. Treat mediator class as a discrete parameter (vector | scalar | composite)
2. For each class, derive the σ/m(v) functional form at all relevant velocity scales
3. Compute the Bayes factor between classes
4. Report which class is preferred

### Cost estimate

**2–4 weeks.** Requires literature survey of σ/m(v) for each model class.

### Risk

High. Different model classes have different normalizations and priors — getting them comparable is non-trivial.

### Particle physics payoff

Medium. Knowing "vector mediator preferred over scalar" is publishable but doesn't directly point to one specific UV completion.

---

## Missing posterior #4: Baryonic feedback (structural)

### What's missing

All 10 channels use **DM-only** dynamics. But real galaxies have:
- Gas cooling + stellar feedback
- Supernova winds
- AGN feedback
- Stellar bar dynamics

A core in a dwarf galaxy could be:
- SIDM with σ/m = 1.5 cm^2/g
- CDM with strong baryonic feedback (same observable core)
- CDM with ancient major merger (also produces cores)

The project assumes the cores are SIDM-only. **This is an unstated, untested assumption.**

### What it would add

- Addresses the core-formation degeneracy (SIDM vs baryonic vs merger)
- Connects to EAGLE / IllustrisTNG / FIRE simulation predictions
- Honest uncertainty quantification on SIDM parameters

### How to add it

1. Pull EAGLE / IllustrisTNG rotation curves (publicly available)
2. Compute SPARC galaxy likelihoods under both SIDM-only and CDM+baryonic models
3. Compute Bayes factor between models
4. Report how much of the "SIDM signal" can be explained by baryonic feedback

### Cost estimate

**4–8 weeks.** This requires running or accessing hydrodynamic simulations and re-fitting SPARC.

### Risk

Medium. Baryonic feedback modeling has large systematic uncertainties — could invalidate the SIDM interpretation entirely.

### Particle physics payoff

**High.** If SIDM is preferred over CDM+baryonic, that's strong evidence. If CDM+baryonic is comparable, SIDM loses some of its support.

### Reviewer 1 escalation (2026-09-12, roadmap1.docx)

Reviewer 1 (paragraph 52) flagged this as **fundamental, not minor**:

> "The baryonic feedback degeneracy: The document correctly notes that SIDM cores can be mimicked by CDM + baryonic feedback. This is not a minor caveat—it is a fundamental degeneracy that affects every channel. The roadmap should prioritize a hydrodynamic simulation comparison (EAGLE, IllustrisTNG, FIRE) as the single most important validation step."

**Priority bumped: MEDIUM → HIGH** (per roadmap table above).

**Implication**: This should be done in parallel with Phase 2 (m_χ + m_A'). The m_χ + m_A' extension gives the model particle-physics credibility; the baryonic feedback test gives it scientific credibility. Both are needed before publishing.

---

## Missing posterior #5: Cosmological initial conditions (structural)

### What's missing

The model assumes **standard ΛCDM initial conditions** for the dark matter power spectrum. It doesn't consider:
- Primordial black hole dark matter
- Axion dark matter (different)
- Mixed dark matter (multiple components with different masses)

### What it would add

- Test whether DM is SIDM or some other class
- Connection to early-universe physics (inflation, reheating, etc.)

### How to add it

1. Add a discrete parameter for "DM is SIDM | primordial BH | axion | mixed"
2. For each, compute the predicted small-scale power spectrum
3. Add Lyman-alpha forest bounds (probe small-scale power)
4. Add CMB μ-distortion bounds (probe early energy injection)

### Cost estimate

**3–6 months.** Each alternative DM class is essentially a separate project.

### Risk

High. This is a fundamentally different research direction, not a model extension.

### Particle physics payoff

Low (for this project) — would be a different paper entirely.

---

## Missing posterior #6: Cross-channel correlations (structural)

### What's missing

The model treats all 10 channels as **independent**. But:
- NGC 1052-DF2 appears in Ch9 and Ch13 (correlated)
- LSB-6 and UDG-1 share telescope calibration (correlated systematic)
- Same Lyman-alpha forest data informs both Ch1 (subhalo) and Ch4 (cluster)

A full treatment would be a **hierarchical model with shared nuisance parameters**.

### What it would add

- More honest uncertainty quantification
- Better-calibrated posteriors (wider if correlations are positive)

### How to add it

1. Identify shared systematics across channels
2. Add hierarchical nuisance parameters (e.g., "telescope calibration offset" shared across UV channels)
3. Re-run with hierarchical likelihood

### Cost estimate

**1–2 weeks.** Mostly bookkeeping.

### Risk

Low. This is technically straightforward but doesn't change the headline answer.

### Particle physics payoff

Low. Mostly affects uncertainty bars, not the MAP.

---

## Missing posterior #7: Time-dependence (gravothermal evolution)

### What's missing

The model assumes σ/m is **constant in time**. But SIDM halos evolve:
- Core formation: σ/m converts cuspy NFW → cored (gravothermal relaxation)
- Core collapse: cores re-contract after ~10 Gyr (gravothermal instability)
- The "MAP σ/m_0 = 1.5" might be a snapshot, not a steady state

### What it would add

- Test whether observed cores are in core-formation phase (LSB-6) or core-collapse phase (massive clusters)
- Predict how galaxies evolve over cosmic time
- Connect to AMUSE simulation pipeline (which is built for time-evolution)

### How to add it

1. Add time-evolution to AMUSE N-body runs
2. Compute σ/m_eff(t) for each channel
3. Add "system age" as a parameter
4. Re-run joint fit with time-evolved σ/m

### Cost estimate

**2–4 weeks** of simulation work. Requires AMUSE pipeline improvement (currently N=10^3, would need N≥10^4).

### Risk

Medium. The AMUSE pipeline is incomplete (placeholder σ/m_peak from earlier work); extending it is real engineering work.

### Particle physics payoff

Low. Mostly affects evolutionary predictions, not the headline σ/m vs velocity.

### Reviewer 1 escalation (2026-09-12, roadmap1.docx)

Reviewer 1 (paragraph 53) flagged this as **statistically invalid**:

> "The channel cross-correlation problem: NGC 1052-DF2 appears in both Ch9 and Ch13. Treating channels as independent is statistically invalid. A hierarchical model with shared nuisance parameters is required for a credible joint fit."

**Priority bumped: LOW → MEDIUM** (per roadmap table above).

**Implication**: This should be done before Phase 2 (m_χ + m_A'), because adding more parameters to a statistically-invalid baseline would compound the problem. Cost is small (1-2 weeks of bookkeeping) but the credibility cost is high.

---

## Null result as legitimate outcome (added 2026-09-12 per R1)

**Reviewer 1 (paragraphs 64–70, roadmap1.docx)** raised the option that the Tier-3 posterior is "a null result dressed up as a consistency check." The reviewer proposed three legitimate outcomes for the project:

1. **Publish the null result**: "We find that a composite SIDM model with a secluded mediator can fit multi-channel astrophysical data only if the mediator is decoupled from the Standard Model at the 10^-54 level, which we interpret as a naturalness catastrophe."

2. **Pivot to a different question**: If the mediator is decoupled, what does that imply for the dark sector? Is there a symmetry that enforces this? Or is the model simply wrong?

3. **Collaborate with particle physicists**: The ε problem is not something the current project can solve alone. It requires input from model-builders who understand symmetry-based suppression mechanisms.

**Status**: All three are legitimate outcomes. The current roadmap assumes the model is worth pursuing (Phase 2: add m_χ + m_A'). **A future strategic decision** should explicitly address whether the project should:
- (A) Continue with Phase 2+ (assume the model is worth pursuing)
- (B) Pivot to publishing the null result
- (C) Pivot to the symmetry question
- (D) Defer to particle-physics collaboration

This decision should be made BEFORE Phase 2 begins, not after.

### Jeffreys-scale framing (added per R1)

Reviewer 1 noted that log_Z = -2.94 corresponds to "substantial" evidence on the Jeffreys scale, not "strong." The project's T39 docs currently say "RESOLVED" but the honest framing is:

- **log_Z = -2.94 vs catastrophic T30 (-9207) and T32 (-1578)**: 600× improvement, but escaping a catastrophic exclusion ≠ positive evidence
- **log_Z = -2.94 vs marginalization baseline**: substantial evidence that decoupling works
- **log_Z = -2.94 in absolute terms**: not decisive by Jeffreys scale

The verdict should be **"WEAKLY CONSISTENT (log_Z = -2.94)"** not **"RESOLVED."** This update applies to `T39_EPSILON_TIER3_VERIFICATION_2026_09_12.md` (see that doc for the softened verdict).

---

### Phase 0 (NEW per R1 mapreview.docx): Theoretical Assessment of ε Naturalness (1–2 weeks)

**Why this phase is first** (per R1 Gap 1, mapreview.docx paragraph 28):

> "The roadmap says Ch14+ should be deferred until '(1) ε naturalness addressed'—but there is no phase dedicated to addressing it. The seven missing posteriors are all about adding dimensions or fixing statistical issues. None of them tackle the core theoretical problem: why is ε ~ 10^-54?"

> "Adding m_χ and m_A' will not answer this. Cross-channel correlations will not answer this. Baryonic feedback will not answer this. The naturalness problem is a model-building problem, not a fitting problem."

**Tasks:**
1. **Survey known suppression mechanisms:**
 - Spontaneously broken U(1) (e.g., Stueckelberg mass, Higgs mixing)
 - Clockwork / linear-dilaton suppression
 - Large extra dimensions (mediator propagates in bulk)
 - Sequestering / accidental cancellation in UV completion
2. **For each mechanism, ask:**
 - Can it produce ε ~ 10^-54 without new fine-tuning?
 - What are the testable consequences?
3. **Decision criteria:**
 - If ≥1 mechanism works naturally → proceed with Phases 2–5 as planned
 - If NO mechanism works → pivot to Option B (publish null result)

**Output doc:** `v0.3-prelim/docs/THEORETICAL_NATURALNESS_ASSESSMENT_2026_09_12.md`

**Cost:** 1–2 weeks of literature review + 1 page of synthesized judgment.

**Risk if skipped:** R1's strongest critique. Adding more dimensions won't fix naturalness; the roadmap is "a plan to fit harder, not a plan to understand better."

---

### Phase 1 (current, completed 2026-09-12)

**Status:** 10-channel σ/m vs velocity model with 4D posterior (σ/m_0, a, ε, α). Tier-3 marginalization succeeds (log_Z = -2.94). 225/225 tests passing.

### Phase 2 (re-ordered per R1 mapreview.docx): cross-channel correlations

**Re-prioritized**: R1 (Gap2, kill criterion) and R2 (minimal version) both flag this as a prerequisite, not a parallel track. **Moved from Phase 3 → Phase 2** (now runs SECOND after Phase 0 theoretical assessment).

**Full version (1–2 weeks):**
- Add hierarchical nuisance parameters for shared systematics
- Identify shared telescope calibration across channels
- Add correlated-likelihood framework
- Re-run with hierarchical model

**Minimal version (1 week, R2's recommendation):**
- Add shared nuisance parameters only for NGC 1052-DF2 (appears in Ch9 + Ch13)
- Add shared telescope calibration nuisance for UV-band channels
- Don't build full hierarchical framework yet
- Re-run with minimal correlation

**Why this is now Phase 2**: Without this fix, log Z is not meaningful (R1: "If the same galaxy enters twice, the log Z is not meaningful"). Must come before any further dimension additions.

### Phase 3 (re-ordered): baryonic feedback (4–8 weeks full OR 1–2 weeks minimal)

**Re-prioritized**: Per R1 (paragraph 16), baryonic feedback "should arguably be the first phase, not the fifth." Per R2 (paragraph 120), a minimal nuisance is achievable faster and still addresses the fundamental degeneracy.

**Full version (4–8 weeks, R1's preference):**
- Pull EAGLE/IllustrisTNG/FIRE hydrodynamic simulations
- Compare to SPARC rotation curves
- Compute Bayes factor between SIDM-only vs CDM+baryonic
- Output: definitive answer on whether SIDM cores are required

**Minimal version (1–2 weeks, R2's recommendation):**
- Add 1-2 parameter baryonic nuisance (e.g., core-size offset, feedback-efficiency)
- Apply only to SPARC + UDG channels (where the degeneracy matters most)
- Compare to current 10-channel fit
- Output: order-of-magnitude answer on whether baryons can substitute

**Why minimal first**: Don't block on full hydro simulations. R2's 1-2 param nuisance "still addresses the fundamental degeneracy flagged by the reviewer."

### Phase 4 (re-ordered): particle-physics posterior (m_χ + m_A' jointly, 2–4 weeks)

**Re-prioritized** per R1 (paragraph 76): "Do them jointly as a 6D fit, not sequentially." Per dimensional accounting correction (Gap 3):
- 4D baseline = (log_σ/m_0, a, log_ε, log_α)
- 4D + (m_χ + m_A' jointly) = **6D** (NOT 5D)

**Tasks:**
- Convert σ/m_0 → σ × m_χ/m_A'^4 (jointly, not separately)
- Add LZ direct-detection (Ch14) and CMB damping (Ch15)
- Add beam-dump (Ch16) and stellar cooling (Ch17)
- Re-run as 6D joint fit
- Output: testable particle-physics parameters (mass, mediator mass, couplings)

**Why joint, not sequential**: σ/m ∝ α^2 m_χ / m_A'^4 depends on both simultaneously. The 5D-separable approach (add m_χ first, then m_A') was incorrect because the posterior constraints couple them.

### Phase 5 (re-ordered): particle-physics model class (2–4 weeks)

**Compare vector vs scalar vs composite mediators** (posterior #3).
- Derive σ/m(v) for each class
- Compute Bayes factor
- Report preferred class

**Why medium priority**: Publishable but doesn't directly point to one UV completion.

### Phase 6 (LOW priority): gravothermal time-evolution

**Extend AMUSE pipeline for time-dependent σ/m** (posterior #7).
- Improve AMUSE from N=10^3 to N≥10^4
- Add pairwise Rutherford SIDM kernel
- Run 401-timestep evolutionary simulations

**Why lower priority**: Mostly evolutionary predictions, not headline.

### Phase 7 (LOW priority, defer indefinitely per R1): alternative DM classes

**Per R1 (paragraph 78): "Phases 6–7 (time-dependence, cosmological ICs): Defer indefinitely. These are low-priority refinements to a model that may not survive Phase 0."**

**Add primordial BH / axion / mixed models** (posterior #5).
- Each is a separate project
- Likely beyond this project's scope
- **Defer indefinitely until model survives Phase 0**

---

## Kill criteria per phase (NEW per R1 Gap 2, mapreview.docx paragraph 38)

**Per R1:** "A credible scientific program needs a falsification threshold. ... The roadmap should state these thresholds explicitly. A roadmap without a kill criterion is a plan to keep going regardless of what the data says."

| Phase | Kill criterion | Action if criterion triggered |
|---|---|---|
| **Phase 0** (theoretical) | No known mechanism naturally produces ε ~ 10^-54 | Pivot to Option B (publish null result) |
| **Phase 2** (correlations) | log Z degrades below -10 after adding shared nuisance | Stop — model is not credible as-is |
| **Phase 3** (baryonic) | CDM + feedback reproduces all 10 channels equally well | SIDM interpretation not required; publishable result either way |
| **Phase 4** (m_χ + m_A') | 6D log Z worse than 4D log Z (after ΔAIC adjustment) | Extra parameters not justified; stop adding dimensions |
| **Phase 5** (mediator class) | Bayes factors between classes indistinguishable (|Δlog Z| < 1) | Mediator class not constrained by data; report and stop |
| **Phase 6** (time-dep) | AMUSE N≥10^4 simulations show no qualitative change | Time-dep corrections negligible; drop from model |
| **Phase 7** (alternative DM) | If we got this far, model survived all earlier phases | Pursue as new project |

**Why this matters**: Without explicit thresholds, the roadmap is "a plan to keep fitting, not a plan to find out whether the model is right" (R1 paragraph 82).

---

## Minimal alternatives (NEW per R2)

**R2's key insight** (paragraph 120): "Full hydro + SIDM comparison is a research-group-scale effort. A minimal one- or two-parameter nuisance (e.g., a simple core-size or feedback-efficiency parameter on the SPARC/UDG channels) is achievable faster and still addresses the fundamental degeneracy flagged by the reviewer."

**R2's key insight** (paragraph 133): "Implement a minimal cross-channel correlation treatment (shared nuisance parameters or a simple hierarchical layer) — 1 week maximum. ... Do not let it become a multi-week blocker."

**Two minimal alternatives now in the table:**
- Cross-channel correlations: 1 week minimal (R2) vs 1-2 weeks full (R1)
- Baryonic feedback: 1-2 weeks minimal (R2) vs 4-8 weeks full (R1)

**Recommended path**: Run the minimal version first. If the minimal version shows a meaningful effect, upgrade to full. If the minimal version shows nothing, drop the phase.

---

## Total estimated cost

| Phase | Posterior | Cost | Priority |
|---|---|---|---|
| 2 | #1 + #2 (DM + mediator mass) | 1–2 weeks | HIGH |
| 3 | #6 (cross-channel correlations) — **was LOW** | 1–2 weeks | **MEDIUM ↑** |
| 5 | #4 (baryonic feedback) — **was MEDIUM** | 4–8 weeks | **HIGH ↑** |
| 4 | #3 (mediator class) | 2–4 weeks | MEDIUM |
| 6 | #7 (time evolution) | 2–4 weeks | LOW |
| 7 | #5 (alternative DM) | 3–6 months | LOW |

**Total:** ~3–6 months of focused work to reach a particle-physics-grade model.

**Quickest impact**: Phase 2 (1–2 weeks for m_χ + m_A').

**Highest risk**: Phase 5 (baryonic feedback could invalidate SIDM interpretation) — now HIGH priority per R1.

**Recommended sequence** (per R2):
1. Phase 3 (cross-channel correlations, 1-2 weeks) — first, because adding parameters to a statistically-invalid baseline compounds the problem
2. Phase 2 (m_χ + m_A', 1-2 weeks) — particle-physics upgrade
3. Phase 5 (baryonic feedback, 4-8 weeks) — run in parallel with Phase 2 if resources allow
4. Phase 4 (mediator class, 2-4 weeks) — last, depends on Phase 2 results

---

## ⚠️ STOP RULE — Do not add more channels (per R2, paragraph 32)

Reviewer 2 (roadmap1.docx, paragraph 32) flagged a critical warning:

> "Do not expand the number of exotic channels (extra LRD variants, more UDG subtypes, etc.) until the naturalness issue is under better control. Adding more astrophysical likelihoods while the mediator remains invisible simply amplifies the fine-tuning."

**Implication**: Channel 13 (DM-dominated UDG, added this session in response to LRD2 cherry-picking concern) was **borderline-justified** but may have been premature. Per R2's rule:

- **Channel 11** (DM-free UDG): pre-existing, keep
- **Channel 13** (DM-dominated UDG): added this session, justified by LRD2 cherry-picking concern — KEEP
- **Any further channels (Ch14+)** should be DEFERRED until:
 1. The ε naturalness problem is addressed (Phase 0 strategic decision)
 2. Cross-channel correlations are fixed (Phase 3)
 3. m_χ + m_A' are added (Phase 2)

**This is an audit-trail marker**: future sessions should not add Ch14, Ch15, etc. without explicit user direction to override this stop rule.

---

## What's deliberately NOT in this plan

- **Alternative SIDM functional forms** (e.g., σ/m = const + v^-ᵃ + v^-ᵇ) — would expand the velocity-dependence model
- **Higher-order velocity terms** (cross-section varies with second derivative of velocity)
- **Substructure beyond SIDM** (dark matter substructure within subhalos)
- **Modified gravity alternatives** (MOND, TeVeS) — different physics entirely

These are all research directions but not "missing posteriors" — they're model extensions within the current framework.

---

## What I recommend as the next concrete step

**Strategic decision first, then Phase 2:**

### Step 1 — Strategic decision (per R1, paragraphs 64–70)

Before beginning Phase 2, decide which of the four legitimate outcomes the project should pursue:
- **(A) Continue with Phase 2+**: assume the model is worth pursuing (default)
- **(B) Pivot to publishing the null result**: publish the naturalness catastrophe as the contribution
- **(C) Pivot to the symmetry question**: investigate what symmetry could enforce ε ~ 10^-54
- **(D) Defer to particle-physics collaboration**: hand off the ε problem to model-builders

This decision should be made before Phase 2 (m_χ + m_A') begins, not after.

### Step 2 — If (A) chosen: ship Phase 2 (m_χ + m_A' joint posterior)

- 1–2 weeks
- Highest particle-physics payoff
- Builds on existing infrastructure (just adds 2 dimensions to T39 framework)
- Output: a 6D posterior with testable predictions for direct-detection experiments

If you want to commit to that, the next step would be to:
1. Read `v0.3-prelim/code/t39_tier3_epsilon_alpha_joint_fit.py` to understand the existing 4D infrastructure
2. Add m_χ and m_A' as new dimensions
3. Convert σ/m_0 to mass-dependent form
4. Pull LZ direct-detection data
5. Re-run as 6D joint fit

### Step 2.5 — Fix cross-channel correlations (per R1, paragraph 53) BEFORE Phase 2

- 1-2 weeks of bookkeeping
- Required for statistical validity of any future joint fit
- Add hierarchical nuisance parameters for shared systematics
- **Bumped to MEDIUM priority** (was LOW) per R1's "statistically invalid" critique

### Step 3 — If (A) chosen AND Phase 2 succeeds: ship Phase 5 (baryonic feedback)

- 4–8 weeks of simulation work (EAGLE/IllustrisTNG comparison)
- **Bumped to HIGH priority** (was MEDIUM) per R1's "fundamental degeneracy" critique
- Could invalidate the SIDM interpretation entirely
- Run in parallel with Phase 2 if resources allow

**Or if you'd rather defer Phase 2**, this roadmap doc is sufficient as a reference for future sessions.

---

## Tracking

- **Roadmap written:** 2026-09-12 (this doc, initial version)
- **Roadmap updated:** 2026-09-12 (this version, per R1+R2 review in roadmap1.docx)
- **Code changes:** none
- **Test changes:** none
- **Channel additions:** none
- **Priority bumps:**
 - Baryonic feedback: MEDIUM → **HIGH** (R1: "fundamental degeneracy")
 - Cross-channel correlations: LOW → **MEDIUM** (R1: "statistically invalid")
 - m_χ + m_A': unchanged at HIGH
- **New sections:** Null result as legitimate outcome, STOP RULE for new channels, strategic decision framing
- **Verdict softening:** "Tier-3 RESOLVED" → "Tier-3 WEAKLY CONSISTENT (log_Z = -2.94)" per R1's Jeffreys-scale analysis
- **Priority list:** Phase 2 (m_χ + m_A') is highest-impact

Reference: T39 Tier-3 fit at `v0.3-prelim/data/results/t39_tier3_epsilon_alpha_joint_fit.json`
Reference: T90.63 LRD-Cloud-9 doc at `v0.3-prelim/docs/T9063_LRD_CLOUD9_RECONCILIATION_2026_09_12.md`
Reference: Channel 13 doc at `v0.3-prelim/docs/LSB6_PAPER_RETRIEVAL_2026_09_12.md`