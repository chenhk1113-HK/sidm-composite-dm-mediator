# Layman Summary — T71.8 / T71.8.1 (2026-08-29)

> **For**: Anyone who has heard "dark matter might bump into itself" and wants
> to know what this particular project says about it, without a physics PhD.
> > **Standing version**: `v0.3-prelim+T71.7` (T71.8 and T71.8.1 are doc-only
> > maintenance rounds; they don't change any numbers).
> > **One-line answer**: This is a prototype analysis showing that a moderately
> > self-interacting dark-matter particle is *physically possible* and *not
> > ruled out* by current data — but every specific number in it can shift if
> > you change one of the project's theoretical assumptions. Treat the headline
> > numbers as a *range of plausible values*, not as measured truth.

---

## 1. What this project does — in plain language

Dark matter is the invisible glue that holds galaxies together. The textbook
picture ("cold dark matter") works fine on big scales but struggles with the
detailed inner shape of small galaxies and a few clusters. One popular
upgrade is **self-interacting dark matter** (SIDM): the dark particles can
*bounce off each other* a little, which smooths out galaxy cores the same way
wind flattens a sandcastle.

The project's computer pipeline asks: *if* dark matter is a composite particle
(a bit like a dark version of the proton/pion) that interacts through a very
light "dark photon" which almost never touches normal matter, *what particle
properties fit all the astronomical observations at the same time*? It feeds
in dwarf galaxy kinematics, the Bullet Cluster, galaxy rotation curves, two
underground dark-matter experiments (LZ, Fermi), and a handful of newer
claims, and lets a Bayesian sampler find the sweet spot.

### The headline numbers (v0.5 canonical, KSFR-mask ON)

| What | Where it sits | Plain-English sense |
|---|---|---|
| Self-interaction strength at galaxy speeds | **σ/m₀ ≈ 0.10 cm²/g** | "Moderately bouncy" — same order of magnitude as the published cross-section that fits dwarf cores |
| Velocity dependence | **a ≈ +1.89** (Yukawa-derived) | Bounciness *grows* with relative speed; data prefers +0.94, so we're at 0.95σ tension — **not significant** |
| Dark-matter particle mass | **m_χ ≈ 515 GeV (MAP) / 805 GeV (median)** | Hundreds of times heavier than a proton; comfortably above direct-detection reach |
| Dark-photon mediator mass | **m_φ ≈ 502 MeV (MAP) / 553 MeV (median)** | About half a proton — sub-GeV but not "ultra-light" |
| Kinetic mixing with normal photons | **ε ≈ 4×10⁻³⁵** | Extraordinarily tiny — this mediator barely touches ordinary matter at all |
| Bayesian log evidence | **log Z = −254.24 ± 0.16** | Internal model-quality score; smaller numbers are better-fit, the absolute value isn't directly meaningful to a non-specialist |

The "ε is so tiny" result is the most striking practical claim: it means this
model predicts **essentially zero events** in every existing direct-detection
experiment — many orders of magnitude below LZ's published limits and below
the "neutrino fog" floor. The model is invisible to underground searches.

### What's NEW in T71.8 / T71.8.1 (what shipped after the upload doc was written)

The doc you uploaded (the "Condensed Executive Summary" you sent) describes
the project accurately as of late T71.0. Two things have shifted since:

- **(2, 2) KSFR promoted ESTIMATED → LATTICE** (T71.8, commit `b21ddd8`).
  Arthur et al. 2016 (arXiv:1602.06559) — cross-cited in Bennett Sp(4) 2019
  Figure 17 — gives SU(2) N_f=2 fundamental continuum-chiral R = 8.1 ± 1.2.
  Numerical overlap with the previous 8.0 ± 1.0 ESTIMATED is within 1σ; m_ρ
  shifts 400 → 405 MeV (no downstream impact). The LATTICE/ANALYTICAL/ESTIMATED
  count is now **3 / 2 / 2** (was 2 / 2 / 3). The Sp(4) vs SU(2) confusion
  from the reviewer was explicitly distinguished — they are *different*
  theories (Sp(4) gives R ≈ 5.72, not 8.0). This is a real upgrade, not a
  cosmetic one.
- **Standing-doc tightening for the KiSS-SIDM UFD verdict** (T71.8.1, commit
  `572c69e`). The KiSS-SIDM (Gurian & May 2025) Julia backend was tested
  end-to-end at N=5e4 dwarf scale. It hit the 7200-second wrapper timeout
  with only **2 of 10 snapshots** completed. The wall-time bottleneck is
  *physics* (snapshot cadence slows in UFD regime), not the wrapper. So UFD
  KiSS-SIDM is **structurally out-of-session**: no more 2-hour timeouts;
  this is now a v0.7+ roadmap item requiring architectural change. The
  fix landed in standing docs as `KISS_SIDM_CANONICAL_N=10000` (the
  MW-scale canonical halo, ~5–15 min wall, finishes in single-session)
  plus a new README runbook section and a "⚠️ Known caveats" block at the
  top of `FINDINGS.md`.

---

## 2. What the project explicitly does NOT claim

This is the credibility section. The pipeline is a *prototype*, not a
measurement.

- **No claim that dark matter IS self-interacting.** The output says this
  model is *compatible with* current data. Different SIDM models, and
  collisionless dark matter, are also compatible. This project studies
  one corner.
- **No claim of a discovery.** The Bayesian sampler finds the best-fit
  point inside a prior range; it doesn't *prove* the universe has this
  particle. The headline MAP (m_φ ≈ 502 MeV, σ/m₀ ≈ 0.105, a ≈ +1.89) is
  *one* candidate point in a model that happens to fit the data — it's
  not "the answer."
- **No claim of independent expert review.** The pipeline was built and
  audited by AI systems. AI review has caught real bugs (R12 sign-flip,
  R12 P1-C units mismatch, v0.5 KSFR-floor violation). But AI audit ≠
  human peer review. The disclaimer at the top of `README.md` is honest
  about this.
- **No claim that the relic density is first-principles.** The amount of
  dark matter left over from the Big Bang is computed by a *calibrated
  1/⟨σv⟩ mapping*, not a Boltzmann solver. T71.6 added a real
  single-component s-wave Boltzmann solver (`t59_production_boltzmann.py`)
  that confirmed the WIMP-miracle crossing at (m_χ=50 GeV, g_χ=0.05) — but
  composite-DM relic density via micrOMEGAs-dark is still multi-month scope.
- **No claim that (N_c, N_f) is identified.** Seven different dark-QCD
  gauge-group parameters were tested. The log-Bayes-factor spread across
  all seven is **0.135 ± 0.120** — well below Jeffreys' threshold (1.0)
  and within the sampler's own noise floor. The (3, 3) anchor is *one*
  choice; data cannot pick between them. This is what T71.0 + the
  nlive=2000 scan (T71.3) settled.

---

## 3. The honest scope / cost of being honest

Three quantified caveats that any reader should know before quoting a number.

### 3.1 The headline numbers are MAP, not measured

The numbers in §1 are **maximum-a-posteriori** (MAP) point estimates — the
single best-fit point under the chosen priors. The Bayesian posterior is a
distribution, and the marginal distributions on m_φ, m_χ, σ/m₀ are all
**broad** — typically spanning half an order of magnitude or more on each
axis. Citing only the MAP overstates how precisely the data constrains the
model. Read the posteriors, not the headlines.

### 3.2 The (N_c, N_f) scan shows no data discrimination

| (N_c, N_f) | log BF vs (3,3) anchor | Class | What it means |
|---|---|---|---|
| (2, 2) | +0.113 ± 0.120 | **LATTICE** (T71.8) | Indistinguishable from anchor |
| (2, 3) | +0.127 ± 0.120 | ESTIMATED | Indistinguishable from anchor |
| (3, 2) | +0.061 ± 0.120 | LATTICE | Indistinguishable from anchor |
| **(3, 3)** | **0.000 ± 0.120** | LATTICE | The anchor — chosen for theoretical reasons, not data |
| (3, 4) | +0.099 ± 0.120 | ESTIMATED | Indistinguishable from anchor |
| (4, 3) | −0.135 ± 0.121 | ANALYTICAL | Indistinguishable from anchor |
| (4, 4) | −0.048 ± 0.121 | ANALYTICAL | Indistinguishable from anchor |

**Spread = 0.262 log-units. Sampling noise ≈ 0.120 per pair.** The "best"
alternative is (2, 3) at +0.127, which is *less than one sigma* of
sampling noise. Nothing in the data picks a winner. The (3, 3) anchor is
a *theoretical* choice (QCD-like reference point), not a data-driven one.

### 3.3 The KSFR mask boundary moves the answer

The "KSFR/PCAC validity mask" is a *theoretical* filter that excludes
regions of parameter space where the dark-pion / dark-rho mass formulas
break down. The mask upper bound is currently **9.5** (post-T71.0; was 9.0
pre-T71.0). Quantitative sensitivity studies (T71.6) confirmed that
loosening the mask to 9.8 brings back some lighter-mediator (~tens of
MeV) parameter space that the default mask excludes.

This means the MAP you see depends on a setting that's hand-picked for
theoretical reasons. If a different research group chose a slightly
different mask boundary, the headline numbers would shift. The pipeline is
honest about this; readers should be too.

### 3.4 Pre-R12 vs post-R12 vs v0.5 — the numbers have moved

The v0.5 result is **not** the same as the pre-R12 result. Three independent
bugs were fixed in R12 (P0-A/B/D):
- A sign-flip in `t41.derived_a` (the velocity index sign was inverted)
- A units mismatch in `sigma_SI` (cm²/g returned instead of cm²)
- A bimodal-surrogate dSph likelihood that misread the Horigome+ 2025 paper

Pre-R12 vs v0.5: pre-R12 said "1.3σ Yukawa tension, σ/m₀ ≈ 0.066 cm²/g,
a ≈ −1.810". V0.5 says "0.95σ tension, σ/m₀ ≈ 0.105 cm²/g, a ≈ +1.89".
**The project has rehabilitated its own earlier pessimistic result** —
that's the honest framing, not "the field changed." If you see a "1.3σ
tension" claim quoted from this project, it's stale.

---

## 4. What this changes about the project — decision matrix

| Question | Answer |
|---|---|
| Is σ/m₀ ≈ 0.105 cm²/g still the canonical number? | Yes for v0.5 (KSFR mask ON, nlive=500, ξ free). No as a measured value — it's the MAP under the default priors. |
| Can I cite a (N_c, N_f) from this scan as "preferred by data"? | No. The scan spread is 0.262 log-BF, which is below Jeffreys' threshold (1.0) and within sampling noise. The (3, 3) anchor is a theoretical choice. |
| Is the dark photon at m_φ ≈ 502 MeV detectable? | No. ε ≈ 4×10⁻³⁵ puts σ_SI ~16 orders of magnitude above LZ's published limit at the canonical benchmark — so the model is invisible to direct detection. To probe this model directly would need a non-LZ experiment. |
| Has anything shifted between T71.0 and T71.8? | Yes, in three places: (2,2) KSFR is now LATTICE; KiSS-SIDM UFD is honestly deferred as out-of-session; the README/CHANGELOG/CITATION doc stamps are consistent again. **No** new physics numbers. |
| Should I trust the v0.5 numbers more than the pre-R12 numbers? | Yes. R12 fixed three real bugs that produced wrong physical conclusions. The v0.5 result is the most defensible single-point summary the project has shipped. |
| What would make this analysis publication-quality? | (1) Real published SPARC per-galaxy likelihoods (not a calibrated saturation score); (2) Boltzmann-solver relic density (micrOMEGAs-dark or equivalent); (3) Full hierarchical SPARC selection effects; (4) Independent human domain-expert peer review. None of these are in v0.6 scope. |
| What about the Drobczyk 2025 cross-check? | Confirmed qualitative agreement: independent paper also finds self-interaction can fit cluster data while staying hidden from direct detection. Quantitative discrepancy at cluster scales (factor ~526×) is honest, real, and documented in T71.5 — likely a reflection of different physics assumptions, not a bug. |

---

## 5. Why it matters — in one sentence

> This project shows that a moderately bouncy dark-matter particle, with a
> half-proton-mass dark photon that essentially doesn't touch normal matter,
> is *physically possible* and *not ruled out* by every channel of data
> combined — but every specific number (particle masses, bounciness) is
> provisional, sensitive to the project's chosen theoretical filter, and
> should be quoted alongside its prior settings, its mask boundary, and
> the full posterior distribution rather than as a single measured value.

---

## Appendix A — One-paragraph version (for Slack / informal forwards)

> The project tests whether dark-matter particles might bounce off each other
> (self-interacting dark matter), fits many astronomical datasets at once,
> and finds that yes — a moderately bouncy dark particle with a sub-GeV
> "dark photon" mediator that barely talks to normal matter can fit all
> the data simultaneously. The best-fit numbers say the dark-matter
> particle is ~500 GeV (hundreds of times a proton), the dark photon is
> ~500 MeV (about half a proton), and the "bounciness" σ/m₀ ≈ 0.1 cm²/g.
> The mediator is *so* weakly coupled to normal photons that no existing
> underground detector could see it. **But** every number in this story
> can shift if you change one of the project's hand-picked theoretical
> settings, so the headline should be read as "physically possible, not
> ruled out, not measured" rather than "we found it." Seven different
> candidate dark-matter theories were tested and the data can't tell them
> apart. No human expert has peer-reviewed the work yet.

---

## Appendix B — Citation recipe (for academic citation)

If citing this work, use the `CITATION.cff` metadata:

```
@software lam_sidm_composite_dm_mediator_2026
  author    = {Lam, K.}
  title     = {sidm-composite-dm-mediator}
  version   = {0.3-prelim+T71.7}
  year      = {2026}
  month     = {8}
  url       = {https://github.com/chenhk1113-HK/sidm-composite-dm-mediator}
  license   = {MIT}
```

**Always pair with the underlying physics references** (Pospelov 2008,
Kaplinghat Tulin Yu 2014, Berlin 2018, Bando 1985, Gurian & May 2025,
Horigome 2025, Yang 2026, Di Mauro 2025, Chakraborti 2025) — the CFF
message body lists them all. When quoting a number, also note which
analysis version produced it: `v0.5` (KSFR mask ON, nlive=500) vs
`v0.6 (Nc,Nf)` (scan at nlive=2000, default mask=9.5). The KSFR-mask
boundary and the nlive setting are part of the citation contract — without
them, the number is incomplete.

---

## Change history

| Date | Change | Source |
|---|---|---|
| 2026-08-29 | Initial layman summary at T71.8 / T71.8.1 standing. Synthesises (a) the user-uploaded "Condensed Executive Summary.docx" (verified against on-disk state — central claims accurate, but (2,2) KSFR is now LATTICE not ESTIMATED, KiSS-SIDM UFD is now structurally out-of-session, README/FINDINGS/CITATION stamps are consistent); (b) the v0.5 canonical T41 result (`t41_mediator_mass_joint_fit_v0_5.json`); (c) the nlive=2000 (N_c, N_f) scan summary (`nc_nf_scan_v0_6_nl2000_summary.json`); (d) the existing R12/R13/R14 layman summaries for tone and format consistency. | T71.8 + T71.8.1, this round |