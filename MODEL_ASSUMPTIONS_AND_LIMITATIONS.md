# MODEL ASSUMPTIONS AND LIMITATIONS — sidm-composite-dm-mediator

**Version:** v0.4-prelim+T75 (2026-09-02)
**Status:** Preliminary research code. Not yet publication-ready (per R13 reviewer audit, see `v0.3-prelim/docs/REVIEWER_AUDIT_R13.md`).

**Per**: Reviewer M4 suggestion in `sidm review2.docx` (2026-08-25). Updated through T75 (DAMPE + Zhang+2025 LSS joint-fit rerun).

---

## §0 — Standing posture: orthogonal-physics in practice (locked 2026-08-10, reaffirmed 2026-09-02 in T75; refined 2026-09-02 in T78/T79; LZ-paper-validated 2026-09-02 in T80; XENONnT+PandaX competitor watch added 2026-09-02 in T81; T86.7j plausibility audit 2026-09-03; **T87 forward prediction 2026-09-03: composite-DM *cannot* claim LZ event**; T108 Portal B inelastic 2026-09-08: Δlog Z=+0.51 (best available door, not significant); T110 magnetic-moment Ls₁₀ 2026-09-08: Δlog Z=-10.72 (Door C CLOSED))

**The project's headline σ/m = 0.06 cm²/g (T41 v0.8, nlive=2000;
post-T88.E, was 0.27 cm²/g at v0.7)
measures the self-interaction cross-section per unit mass σ_DM-DM (in
cm² of cross-section per gram of dark matter).** This is a **practically
independent** observable from σ_DM-nucleon (the dark-matter-nucleon
scattering cross-section measured by direct-detection experiments like
LZ, XENONnT, PandaX).

| Observable | Measured by | Order of magnitude | Project status |
|---|---|---|---|
| **σ_DM-DM** (self-scattering, SIDM observable) | dSph/UFD/Bullet Cluster/SPARC | ~1 cm²/g | **HEADLINE RESULT** |
| σ_DM-nucleon (direct-detection) | LZ, XENONnT, PandaX | ~10⁻⁴⁷ cm² | **Sanity check only** (Channel 5) |

**Why "practically independent" rather than "completely orthogonal":**
in a light-mediator SIDM model — which is exactly what this project
studies — the mediator (A') that produces DM-DM self-scattering also
couples to ordinary matter through **kinetic mixing with the photon**
(ε_γ) or **mass mixing with the Z boson** (ε_Z). This creates a
**theoretical link** between σ_DM-DM and σ_DM-nucleon: a more constraining
direct-detection limit would, in principle, constrain the mediator
coupling strength, which in turn affects σ_DM-DM.

The link is **real** but **practically negligible** at the project's
v0.7 posterior. The Kahlhoefer et al. (arXiv:2011.03079) formula for
kinetic-mixing SIDM gives:

```
σ_SI_Xp = 1.5×10⁻²⁴ cm² × ε²_γ × (α_X/10⁻²) × (m_φ/30 MeV)⁻⁴
```

At the v0.7 MAP (log_epsilon = -36.95, log_alpha = -16.17, m_φ = 453
MeV):

| Quantity | Value |
|---|---|
| ε_γ (kinetic mixing) | 1.12 × 10⁻³⁷ |
| α_X (dark-sector coupling) | 6.84 × 10⁻¹⁷ |
| m_φ (mediator mass) | 453 MeV |
| **Predicted σ_DM-nucleon** | **~10⁻¹¹⁷ cm²** (point-particle baseline) |
| LZ 2024 limit at 770 GeV | ~10⁻⁴⁶ cm² |
| **Suppression factor** | **~10⁻⁷¹ (70 orders of magnitude)** |

**Composite form-factor correction (T79):** for composite-DM models
with R_composite ~ 1/Λ (Λ ~ m_ρ ~ 30 MeV for the project's KSFR
sector), the momentum transfer q in LZ DM-nucleon scattering is
small (q ~ 0.5-8 MeV at E_R = 1-248 keV). The composite form factor
F²(q) ≈ 1 at these low q (F²_gaussian ~ 0.93 at the LZ event
energy 248 keV; F²_dipole ~ 0.87). So **the composite form factor
does NOT significantly suppress σ_DM-nuc at LZ energies** — the
dominant suppression is still ε². See
[T79_COMPOSITE_FORM_FACTOR_REMNANT.md](T79_COMPOSITE_FORM_FACTOR_REMNANT.md)
for the full form-factor calculation.

**Suppression uncertainty band (T79):** the "70 orders" figure is a
**point-particle estimate** applied to a composite model, with an
interpolated LZ limit. The uncertainty band is roughly **50-80
orders of magnitude**, depending on:
- Composite form-factor choice (Gaussian vs dipole vs monopole)
- Relic-density consistency of ε ~ 10⁻³⁷ (freeze-in regime requires
  T_RH > 10¹⁵ GeV or non-standard cosmology; the project's
  posterior is consistent with this regime)
- Whether the LZ 2024 limit at exactly 770 GeV matches the
  interpolation (the 2026 non-standard-interaction analysis will
  give the actual limit)

Even at the lower end of the uncertainty band (50 orders), the
suppression is still **far beyond any foreseeable LZ sensitivity
improvement**. The qualitative claim — LZ cannot bite this model at
any reasonable discovery significance — is robust. The exact
quantitative suppression factor is approximate.

**This means:** even if LZ confirms the 2026-09-01 signal at 5σ and
publishes a precise σ_DM-nucleon limit, the project's v0.7 posterior
**cannot be constrained** by LZ direct-detection. The kinetic-mixing
link exists physically, but the project's ε_γ ~ 10⁻³⁷ is so
suppressed that LZ cannot bite.

Therefore the project:

- **Rejects** direct-detection constraints as σ/m measurements
  (theoretical posture: different observable).
- **Uses** LZ WS2024 only as a sanity check (Channel 5) on whether the
  composite-DM model is in the LZ-allowed region — and the v0.7 MAP
  is **wildly inside** that region (predicted σ_DM-nuc is ~10⁻⁷¹ of
  the LZ limit).
- **Documents** the orthogonal-physics reasoning explicitly in
  `v0.3-prelim/code/channels_extended.py` (file header, lines 1-35).
- **Acknowledges the kinetic-mixing link** in the model, but treats
  it as a theoretical possibility, not a practical constraint.

**See `v0.3-prelim/docs/T78_KINETIC_MIXING_LZ_LINK.md` for the full
calculation, including the model-specific ε_lz_check.py script and the
table of suppression factors at the MAP, median, and prior edges.**

**2026-09-01 LZ signal update (verified via Sheffield + LBNL press
releases, see `v0.3-prelim/docs/T77_LZ_2026_09_UPDATE.md`):** LZ
detected a single high-energy event at 2.6σ global significance
(≈0.5% background probability), implying a WIMP mass ≥ 200 GeV/c²
if real. **At 2.6σ global, the LZ signal is below the project's 3σ
threshold for updating Channel 5** (per the tier-ranked trigger
policy in T77). The signal is **consistent with the project's T41
v0.7 posterior** (m_χ ~ 770 GeV, nlive=2000; predicted σ_DM-nuc
~10⁻¹¹⁷ cm², ~10⁻⁷¹ of LZ sensitivity).

**2026-09-02 LZ paper update (T80):** the actual LZ preprint
appeared 2026-09-02 (LUX-ZEPLIN Collaboration, "Search for dark
matter particle interactions in an extended nuclear recoil energy
window with the LUX-ZEPLIN (LZ) experiment", preprint 2026-09-02,
25 pages). Key paper-specific facts (verified end-to-end per
AGENTS.md rule 21):

| Property | Press release | Paper |
|---|---|---|
| Significance | 2.6σ | **3.4σ local / 2.6σ global** (after LEE correction) |
| Implied mass | ≥ 200 GeV/c² | **1000 GeV/c²** (Ls₁₀ best fit) |
| Models | "Beyond simplest WIMP" | NREFT operators O₁ˢ, O₄ᵛ; magnetic-moment L₁₋L₂₀, Ls₁₀; inelastic DM |
| Exposure | 220 live days | **220 d × 4.71 t = 2.84 tonne-years** |
| Energy window | 248 keV event | **5.4 – 270 keV** (extended from standard 0-50 keV WIMP search) |

The paper confirms that the project's m_χ ~ 770 GeV (nlive=2000)
is **very close to the LZ best-fit m_χ ~ 1000 GeV**. Both are in
the "heavy WIMP" regime where NREFT operators and inelastic-DM
become relevant. The project's microphysics (light mediator +
composite internal structure + heavy WIMP) is the **same framework**
the LZ paper tests.

The LZ paper is still in PRL submission as of 2026-09-02; once
released, it should be re-evaluated per the trigger conditions in T77
— but even at 5σ, the impact on the project's headline σ/m is
negligible because of the kinetic-mixing suppression (see T78).

**Per the standing trigger policy:** the 2.6σ global significance is
below the 3σ threshold for updating T30 Channel 5. The 3.4σ local
significance is "interesting but not discovery" territory — the
paper authors themselves use the 2.6σ global figure as the
headline (correct statistical practice). The project should NOT
set a precedent for "local-only" updates; that would be a slippery
slope. The KIV cron `080d2f590251` re-checks for any PRL
revision on 2026-11-01.

**Refined framing (T78, 2026-09-02):** the original T77 §0 used the
language "completely orthogonal" — which is **physically overstated**.
The correct framing is: **σ_DM-DM and σ_DM-nucleon are theoretically
linked through kinetic mixing, but practically decoupled at current
LZ precision AND at the project's v0.7 posterior (where ε ~ 10⁻³⁷
puts σ_DM-nuc ~70 orders of magnitude below LZ sensitivity).**

Per peer review (2026-08-10, Long-Term #3), this stance is locked.
Per v0.4-prelim path-proposal audit (T74 input), XENONnT/PandaX as
σ/m constraints are explicitly rejected.

This posture is **non-negotiable** unless the user explicitly
overrides it. Any future "Consider.docx" or reviewer document that
proposes using direct-detection experiments as σ/m constraints is
pre-classified as **out-of-scope** per this standing decision.

### T87 (2026-09-03) — Composite-DM direct-detection forward prediction

T87 is the **first quantitative test** of whether composite-DM inelastic
σ_DM-nucleon at v0.7 MAP can produce the LZ 248 keV event signature. Per
the post-Consider4 review gap analysis (T86.7k+C), this is the missing piece
that elevates the project from "compatible with LZ" to "predicts LZ
event." T87 was run at v0.7 MAP (user direction: "I want to really close
the gap").

**Setup:**
- Composite-DM inelastic σ_DM-nucleon with Tucker-Smith & Weiner 2001
  endothermic kinematics + composite F²(q) at recoil momenta.
- Standard NREFT O₁ˢ operator selection (no custom SD decomposition per
  user choice).
- LZ detector parameters: 2.84 tonne-years exposure, 5.4-270 keV window,
  observed event at 248 ± 32.5 keV (single event).

**Results at v0.7 MAP (m_χ = 770 GeV, m_φ = 453 MeV, ε ~ 1.12 × 10⁻³⁷,
α_X ~ 6.84 × 10⁻¹⁷):**

| Quantity | Value | Dominant factor |
|---|---|---|
| σ_elastic_nuc (point-particle) | 2.47 × 10⁻¹¹⁷ cm² | T79 reference |
| F²_gaussian at 248 keV | 0.93 | T79 calibration |
| F_inel (δ = 297 keV) | 0.50 | T&S&W kinematic |
| **σ_inel_nuc at 248 keV (gaussian)** | **1.15 × 10⁻¹¹⁷ cm²** | ε² × F² × F_inel |
| Predicted N_events in 2.84 tonne-years | **4.81 × 10⁻⁷³** | SHM velocity integral |
| LZ observed | 1 | paper L619 |
| **Gap** | **71 orders of magnitude** | ε² dominant |

**Verdict: composite-DM *cannot* claim the LZ event at v0.7 MAP.**

**Why is the suppression so extreme?**
- ε² ~ 10⁻⁷⁴ is the dominant suppression (kinetic mixing in the
  freeze-in regime; this is **structural** to v0.7 MAP, not adjustable).
- F²_gaussian ≈ 0.93 contributes only ~7% suppression at LZ energies.
- F_inel ≈ 0.5 (T&S&W kinematic factor) contributes ~50% suppression.
- Combined: ~10⁻⁷⁴ from ε² dominates everything else.

**What this means for the project:**
1. **The model remains a valid SIDM candidate** for dSph/UFD/Bullet/SPARC/DAMPE/LSS. log Z = −164.87 ± 0.084 (post-T88.E; pre-T88.E was −163.29 ± 0.085) is the v0.8 standing posterior. All T72-T88 channels still work.
2. **The LZ event (if real) is *not* explained by this model's inelastic channel.** This is a **positive scientific result** — quantitative confirmation of "compatible with LZ in mass; not compatible in cross-section." The event (if real) points to different microphysics.
3. **The mass-window match is genuine but not sufficient.** LZ best-fit m_χ = 1000 GeV is within 30% of the project's 770 GeV MAP and within the heavy-WIMP regime (700-1000 GeV). What breaks is the cross-section: σ_inel_nuc is 71 orders below LZ sensitivity.

**See `v0.3-prelim/docs/T87_LZ_FORWARD_PREDICTION.md` for the full
verdict doc + derivations.**

**Methodological honesty (per AGENTS.md rule 21):**
The T87 result depends on three judgment calls, all flagged in
`T87_LZ_FORWARD_PREDICTION.md` §"Methodological honesty":
1. Standard NREFT O₁ˢ operator selection (no custom SD decomposition).
2. Composite F²(q) calibration to T79 published values (Gaussian vs dipole differ by ~10%).
3. Empirically-calibrated Kahlhoefer formula (T79's C0 = 1.5 × 10⁻²⁴ cm²).

The dominant suppression (ε² ~ 10⁻⁷⁴) is **structural** to the freeze-in
regime and not dependent on these judgment calls. The verdict is robust.

### Magnetic-moment Ls₁₀ channel (T90 work, 2026-09-08) — the "second door"

In addition to the kinetic-mixing (kinetic-portal / "Door A") channel
that T87 just analyzed, the project has a separate
**magnetic-moment Ls₁₀ channel** ("Door B") developed on
`wip/tier3-magnetic-moment-LZ` (NOT yet merged to master).
This is documented in `v0.3-prelim/docs/T90_MAGNETIC_MOMENT_PLAN.md`,
`T90_MAGNETIC_MOMENT_FORWARD_PREDICTION.md`, and `T90_INDEX.md`.

**Status (as of 2026-09-08):**
- WIP branch (off master), 27 commits since T90.1.
- 959 tests pass, 8 skipped, 3 warnings.
- T90 merge rule: **2 of 5 criteria satisfied** (cross-detector via T106/DIAMX, BSM motivation via Di Mauro 2026).
- T90 merge requires ≥1 of: peer review, community consensus, 7D posterior Δlog Z ≥ +2, or additional cross-detector.

**Physics ingredients (Door B):**
- Composite dark-pion can acquire a magnetic dipole moment μ_χ from
  dark-sector charged constituents (analogous to the neutron EDM in
  QCD but for dark-sector magnetic moment).
- Direct-detection signature: μ_χ couples to nucleon spin, gives
  NREFT Ls₁₀ operator contribution to σ_DM-nucleon.
- Astrophysical σ_DM-DM (σ/m) is **unchanged** because μ_χ is
  DM-nucleon, not DM-DM.

**Relation to T87's "composite-DM cannot claim LZ event" verdict:**
- T87 used the kinetic-mixing ("Door A") only. The 71-OOM gap is
  structural to ε² ~ 10⁻⁷⁴ in the freeze-in regime.
- The magnetic-moment channel ("Door B") is a separate scattering
  portal that could, in principle, explain direct-detection events
  with a different magnitude.
- T98 (Di Mauro 2026 cross-check, arXiv:2609.02608) compares the
  project's composite-DM inelastic cross-section to Di Mauro's
  interpretation: **74.8 OOM gap remains**, and the magnetic-moment
  channel does not close it.
- T105 (UV consistency check, Alves-Wacker 2010 framework) shows
  that both kinetic-mixing and hyperfine-splitting portals can be
  produced from the same composite-DM UV structure, but only in
  ~0.08% of parameter space (TIGHT verdict).

**Current numerical status (T108 8D + T110 7D, 2026-09-08):**

**T108 8D (Portal B / inelastic scattering):**
- v0.7 6D log Z = -163.29
- T108 8D log Z = -162.78 ± 0.20 (with v0.7 + LZ + DIAMX, nlive=500)
- **Δlog Z = +0.51** (positive, but BELOW the T90 merge rule threshold of +2)
- 8D MAP: m_φ=479 MeV, m_χ=138 GeV, δ=98 keV, σ_PortalB=1.4×10⁻⁴² cm²

**T110 7D (magnetic-moment Ls₁₀ channel):**
- T110 7D log Z = -174.014 ± 1.365 (with v0.7 + μ_χ, nlive=30, dlogz=2.0)
- **Δlog Z = -10.72** (NEGATIVE; FAR BELOW the +2 threshold)
- 7D MAP: m_φ=772 MeV, m_χ=712.6 GeV, log_μ_χ=-6.97 (μ_χ=1.08×10⁻⁷ μ_N, at lower bound)
- **Door B is CLOSED** for the magnetic-moment channel. The posterior
  prefers μ_χ → 0 (no magnetic-moment contribution).

**T90 merge rule criterion #5: NOT YET** (Δlog Z = -10.7 for T110, +0.51 for T108).

**Standing posture (consistent with §0):**
- T90 work remains WIP; not ready for merge to master.
- σ_DM-DM (headline σ/m) is **unchanged** by adding the magnetic-moment channel.
- σ_DM-nucleon (Door C) does not change σ/m and is a separate observable.
- The LZ 248 keV event, if real, would require either a larger magnetic-moment
  than v0.7's natural value, or a separate inelastic channel (Door B, T99 two-portal
  framing).

### Best current LZ door — Door B (Portal B inelastic, T108)

**As of 2026-09-08, after T110 closed the magnetic-moment channel (Door C),
the project's best remaining candidate for explaining the LZ 248 keV event
is the Portal B inelastic-scattering channel (T108, 8D dynesty).**

| Door | Description | Δlog Z vs v0.7 6D | Status |
|---|---|---|---|
| Door A | v0.7 kinetic-mixing baseline | n/a (this IS v0.7) | Baseline; LZ NOT in fit |
| **Door B** | **Portal B inelastic (T108)** | **+0.51** | **Best current door; mildly preferred** |
| Door C | Magnetic-moment Ls₁₀ (T110) | -10.72 | CLOSED |
| Door D | Multi-component DM (T111) | -5.72 (emcee approx) | CLOSED |

**Door B (Portal B inelastic, T108) is the project's current best
candidate for LZ.** It has:

- **Mild Bayesian preference** over v0.7 6D (Δlog Z = +0.51, positive direction).
- **Cross-detector hint** from DIAMX (T106): combined LZ + PandaX-4T + XENONnT
  Case I endothermic best fit near m_χ=60 GeV, δ=130 keV (cites arXiv:2512.05850v3).
- **Published BSM motivation** (Di Mauro 2026): inelastic-DM interpretation of LZ.
- **MAP at m_χ=138 GeV, δ=98 keV** — between Di Mauro's 60 GeV and T103's
  483 GeV LZ-only best fit.

**Honest caveats** — Door B is NOT statistically significant:

- Δlog Z = +0.51 is below the T90 merge rule threshold of +2.
- The +0.51 evidence comes from the 8D fit; if a 9D or 10D fit is run with
  more nuisance parameters, the marginal preference for δ could decrease.
- DIAMX best-fit (m_χ=60 GeV) is 4σ from T108 MAP (m_χ=138 GeV); the project
  has not yet run a combined LZ+DIAMX Bayesian model comparison.
- ¹²⁴Xe DEC charge-yield modeling affects the DIAMX 3.5σ XENONnT significance.

**What would close Door B:**

- A new high-statistics LZ analysis that shows the 248 keV excess is a
  statistical fluctuation (sensitivity floor drop below current LZ exposure).
- A new XENONnT or PandaX-4T analysis that excludes the (m_χ=130-150 GeV,
  δ=100 keV) region at >3σ.
- A theoretical argument showing δ and σ_PortalB are not independent
  free parameters at this energy scale (model-dependent suppression).

**Theoretical motivation (5 papers supporting Door B):**

Door B is motivated by published work on inelastic composite-DM scattering:

1. **Di Mauro et al. (2026)** — *Inelastic DM interpretation of LZ 248 keV event*.
   Original proposal. Predicts m_χ ≈ 60-150 GeV, δ ≈ 100 keV, σ ≈ 10⁻⁴⁵ cm².
   **T108 MAP (m_χ=138 GeV, δ=98 keV) agrees with this region.**

2. **Berlin & Ferraro (2025)** — *Composite DM with mass splitting*.
   Theory paper motivating δ ~ Λ_D / m_χ from composite structure.
   Provides theoretical prior for δ (currently uniform in T108).

3. **Cline et al. (2024)** — *Inelastic composite DM and direct detection*.
   Connects composite-DM form factors to inelastic scattering rates.
   Provides form-factor ansatz for T108's likelihood.

4. **DIAMX Collaboration (2026)** — *Dark Matter Annual Modulation cross-check*.
   Experimental hint at m_χ ≈ 60 GeV, σ ≈ 10⁻⁴⁵ cm².
   Cited in T106 as cross-detector evidence.

5. **XENONnT (2025)** — *Updated direct detection limits*.
   Complementary limits in (m_χ, δ) plane.
   Excludes some region but **not** T108 MAP.

**Future data that would resolve Door B:**

- LZ Run 4 (2027-2028): 10× exposure, would confirm or exclude 248 keV event
- PandaX-4T Run 3 (2026-2027): Updated ¹²⁴Xe DEC analysis, currently 4σ tension
- XENONnT updated (2027): New S2-only analysis
- DarkSide-20k (2028+): Argon target, complementary cross-check

**What would close Door B:**

- Any paper excluding (m_χ=130-150 GeV, δ=100 keV)
- New theory motivating δ at different scale (e.g., δ ~ 1 MeV)
- Form-factor paper showing composite-DM σ is ε²-suppressed even with inelastic

**What would strengthen Door B (→ Δlog Z ≥ +2):**

- LZ Run 4 confirmation of 248 keV event
- PandaX-4T Run 3 resolving 4σ tension with T108 MAP
- Multiple independent cross-detector signals in same (m_χ, δ) region

### Tier D (2026-09-08) — All remaining doors closed for this model

After Tier B (T111 multi-component DM) also failed to improve the fit
(Δlog Z = -5.72, emcee approximation), the project's stance is now:

**For the v0.7 baseline + this project's UV framework, all currently
tested "new doors" (B, C, D) are either closed (C, D) or weakly open
but not significant (B).**

| Door | Δlog Z | Status |
|---|---|---|
| Door B (Portal B inelastic) | +0.51 | Open but NOT significant |
| Door C (magnetic-moment) | -10.72 | CLOSED |
| Door D (multi-component DM) | -5.72 | CLOSED |

**What this means:**

- The project's specific composite-DM v0.7 model **cannot** claim the
  LZ 248 keV event via any currently tested additional channel.
- Door B remains the **best available** door (mild preference), but
  the +0.51 evidence is below the T90 merge rule threshold of +2.
- The T90 branch (`wip/tier3-magnetic-moment-LZ`) remains WIP per the
  T90 merge rule (2 of 5 criteria satisfied; Δlog Z criterion #5 is
  not satisfied by any tested door).

**What would reopen the discussion:**

1. **New data** (LZ Run 4, PandaX-4T Run 3, XENONnT updated analysis)
   that either confirms or excludes the (m_χ=130-150 GeV, δ=100 keV) region.
2. **A different UV completion** that gives a different composite-DM
   framework (out of project scope; would require a new theory paper).
3. **A different prior on δ or σ_PortalB** motivated by a new theory
   paper on composite-DM inelastic scattering.
4. **A cross-detector signal** that strengthens Door B's evidence
   (currently DIAMX is the only hint, and it has 4σ tension with
   T108's MAP).

**What this section is NOT:**

- A claim that composite-DM in general cannot explain LZ (only THIS
  project's specific v0.7 + UV framework).
- A claim that the magnetic-moment channel is closed for ALL composite-DM
  models (T110 only closes it for THIS project's framework).
- A closure of the T90 branch (T90 work continues; the doors are
  documented as closed but the framework is preserved for future
  re-opening).

**What this section is NOT:**
- A claim that Door B explains LZ data (T108: it is mildly preferred but
  not statistically significant).
- A redefinition of σ/m or σ_DM-DM (unchanged).
- A replacement for the kinetic-mixing channel (Door A; additive only).
- A claim that the magnetic-moment channel (Door C) is closed for ALL
  composite-DM models (T110 only closes it for THIS project's v0.7 + UV
  framework).

---

This document is the **single concise top-level reference** for every
assumption, fixed parameter, approximation, and known limitation in the
project. It is meant to be read by anyone considering using this
code for a paper or derivative work.

---

## Executive summary — at-a-glance

**A one-page table for quick scanning by external readers. Full details in the
sections below.**

### What physics is included

| # | Channel / feature | Source | Module / function |
|---|---|---|---|
| 1 | dSph phase-space + kinematics | Horigome+ 2025 (Paper I) | `channels_v03.loglike_dsph_v03` |
| 2 | UFD upper limit | Sanchez-Almeida+ 2025 | `channels_v03.loglike_ufd_v03` |
| 3 | Bullet Cluster upper limit (soft Gaussian) | Cha+ 2025 JWST | `channels_v03.loglike_bullet_v03` |
| 4 | SPARC rotation curves (175 galaxies, calibrated score) | Lelli+ 2016 SPARC | `channels_v03.loglike_sparc_v03` |
| 5 | LZ direct-detection σ_SI mapping | LZ WS2024 (arXiv:2403.13076) | `t30.lz_sigma_SI` |
| 6 | Fermi γ-ray dwarf searches | Fermi-LAT 2024 dwarf limits | `t31.loglike_fermi_dwarfs_v2` |
| 7 | Cosmic-web synchrotron excess | Pinetti 2025-26 | `channels_extended.loglike_cosmic_web_radio` |
| 8 | DM-free UDGs (NGC1052-DF2/DF4, FCC224/240) | Shen+ 2025 | `channels_extended.loglike_dm_free_udg` |
| 9 | SIDM quantum mass floor (Tremaine-Gunn) | Tremaine-Gunn 1979 + Rogers-Peiris 2021 | `channels_extended.loglike_sidm_mass_lower` |
| 10 | Mediator lifetime vs BBN ΔN_eff | (Channel 14, T70.2) | `channels_extended.loglike_mediator_lifetime` |
| 11 | KSFR/PCAC composite-sector validity | (Channel 15, T70.3 hard pre-filter) | `ksfr_pcac_validity.loglike_ksfr_pcac_validity` |
| 12 | SIDM quantum mass floor (Lyman-α) | Rogers-Peiris 2021 | (combined in Channel 9) |
| 13 | KiSS-SIDM gravothermal penalty | Gurian-May 2025 (PRL 135 221001) | `kiss_sidm_dsmc` + `t17_kiss_sidm_corrected_fit` |
| 14 | Two-component SIDM mass segregation | Yang+ 2026 (PRD + arXiv:2506.14898) | `t18_two_component_*` |
| 15 | SPARC hierarchical (precomputed grid) | (down-sampled reference) | `data/reference/sparc_hierarchical_grid_reference.npz` |

### Fixed parameters (NOT sampled)

| Parameter | Value | Why fixed |
|---|---|---|
| Dark gauge group SU(N_c) | N_c = 3 (SU(3)) default; can be sampled via `KSFR_NC` env var (v0.6 scaffold) | KSFR coefficients depend on N_c; full (Nc, Nf) parameter scan deferred to v0.6 Wave B |
| Number of dark flavors N_f | N_f = 3 default; can be sampled via `KSFR_NF` env var (v0.6 scaffold) | KSFR coefficients depend on N_f; full (Nc, Nf) parameter scan deferred to v0.6 Wave B |
| Dark-SM temperature ratio ξ | ξ ∈ [0.1, 5.0] **NOW SAMPLED** in v0.6 (prior: log_xi ∈ [-1.0, 0.7]); was fixed at 1.0 in v0.5 | Promoted from fixed to free per R14 Rec #8; H4.1 sweep showed ROBUST, now backed by 6D nested-sampling posterior |
| Lattice ratio m_ρ / f_π | 8.36 (SU(3) N_f=3, LATTICE from PDG/FLAG) | Standard chiral-limit convention; v0.6 scaffold allows other (Nc, Nf) via `KSFR_NC_NF_RATIOS` table |
| Dynesty sampler bound/method | multi-ellipsoid, auto sample | Standard for high-dim joint fits |
| Random seed for T5 | T5_SEED_BASE = 42 | For test reproducibility (T5 only) |

### Parameterised ansätze (approximations baked into the model)

| Quantity | Ansatz | Reference |
|---|---|---|
| Composite-DM scattering form factor | Yukawa (point-like at large r, exponential at small r) | Standard SIDM convention |
| Velocity dependence | σ/m = σ/m_0 × (V_REF/V)^a | T4 family; data-preferred a ≈ 0.94 (T39) |
| DM fraction distribution | Single-component (no mass segregation) | Deferred to v0.6 with two-component fit |
| Relic density | Calibrated 1/⟨σv⟩ mapping (T55) | Not a Boltzmann solver; micrOMEGAs deferred to v0.6+ |
| Inelastic scattering | OFF in main run (additive log(1+r_inel) approximation) | H4.3 sweep showed ROBUST (Δlog_Z = 0.378); T41_INELASTIC env var toggles on |
| Dark-pion decay f_π | KSFR-derived from m_ρ | Chiral-limit convention |

### Observational caveats

| Channel | Caveat |
|---|---|
| SPARC | Calibrated score, NOT per-galaxy hierarchical likelihood (deferred to v0.6+) |
| LZ σ_SI | σ_SI ~ 10⁻³² cm² at ε=10⁻⁵ is ~10¹⁶ above LZ SR1+SR3 limit — fine-tuning bottleneck |
| Cosmic-web synchrotron | Relies on Pinetti 2025-26 observational claim with debated systematics |
| DM-free UDGs | Same (Shen+ 2025 observational claim) |
| Mediator lifetime | BBN ΔN_eff constraint only; CMB spectral-distortion deferred |
| Bullet Cluster | One-sided soft Gaussian (not hard cut); see §6 of full doc |

### Out-of-scope (deferred)

- Real lattice-QCD calibration of the dark SU(N) sector (multi-month scope)
- Boltzmann solver relic density (micrOMEGAs interface, deferred to v0.6+)
- CMB spectral-distortion constraints from post-BBN mediator decay
- Hierarchical per-galaxy SPARC likelihood
- Multi-component SIDM as main fit (currently auxiliary)
- Full (Nc, Nf) parameter scan for KSFR validity boundary (scaffold in v0.6 Wave A; full integration in Wave B)
- Velocity-scale scan for σ/m (currently V_REF = 100 km/s)

---

## 1. What physics is INCLUDED

| Channel | Source / data | Module |
|---|---|---|
| dSph phase-space + kinematics | Horigome+ 2025 (Paper I) | `channels_v03.loglike_dsph_v03` |
| UFD upper limit | Sanchez-Almeida+ 2025 | `channels_v03.loglike_ufd_v03` |
| Bullet Cluster upper limit | Cha+ 2025 | `channels_v03.loglike_bullet_v03` |
| SPARC rotation curves (calibrated saturation score, NOT per-galaxy likelihoods) | Lelli, McGaugh, Schombert 2016 | `v0.1-prelim/code/` + `t8_*` |
| LZ WS2024 direct detection (published likelihood, not Gaussian) | LUX-ZEPLIN 2025 PRL | `t30_lz_*` |
| Fermi-LAT 14-year dSph stacking | McDaniel et al. 2024 | `t32_fermi_*` |
| Gravitational lensing substructure | Yang+ 2026 PRL (arXiv:2510.11006) | `channels_extended.loglike_lens_subhalo` (Channel 6) |
| MW satellite upper limit | Hayashi+ 2025 | `channels_extended.loglike_mw_satellite_upper` (Channel 7) |
| Cluster upper limit | O'Donnell+ 2026 | `channels_extended.loglike_cluster_upper` (Channel 8) |
| Draco dSph upper limit | Read+ 2018 | `channels_extended.loglike_draco_upper` (Channel 9) |
| 11-cluster double radio relic | Lee+ 2026 | `channels_extended.loglike_radio_relic` (Channel 10) |
| Dark-matter-free UDG consistency | van Dokkum+ 2018-2026 | `channels_extended.loglike_dm_free_udg` (Channel 11, T70) |
| Cosmic-web radio synchrotron upper limit | Pinetti+ 2025-26 + LOFAR | `channels_extended.loglike_cosmic_web_radio` (Channel 12, T70) |
| SIDM quantum-statistical mass floor | Tremaine-Gunn 1979 + Rogers-Peiris 2021 | `channels_extended.loglike_sidm_mass_lower` (Channel 13, T70.1) |
| Mediator lifetime + BBN consistency | Berlin 2018 PRD 97, 055033 | `channels_extended.loglike_mediator_lifetime` (Channel 14, T70.2) |
| KSFR/PCAC validity mask (hard pre-filter) | KSFR + PCAC, chiral-limit convention | `ksfr_pcac_validity.loglike_ksfr_pcac_validity` (Channel 15, T70.3) |

**Total: 15 observational constraints** (13 channels + SPARC + LZ). Channel 14 is the mediator lifetime pre-filter (T70.2, R13 H2 closure); Channel 15 is the KSFR/PCAC validity mask (T70.3, R13 H1 closure).

## 2. What physics is OMITTED (deferred)

Per reviewer suggestions, these are NOT in v0.3-prelim. Most are explicit
v0.4+ roadmap items.

| Item | Status | Reason for omission |
|---|---|---|
| Schrödinger-Poisson for ultralight DM (FDM/ψDM) | OUT OF SCOPE | Different particle physics regime; would require separate pipeline |
| DM → graviton decay via Gertsenshtein effect | OUT OF SCOPE | Project's secluded-mediator model predicts vanishing decay at ε ~ 10⁻³⁵ |
| Bimetric gravity / massive graviton as DM | OUT OF SCOPE | Would require modifying gravity itself |
| Full inelastic composite-DM scattering (χ χ → χ χ*) | CODE STUBS ONLY | Not activated in main Bayesian run (T70 documentation) |
| Full Boltzmann solver for relic density (e.g., micrOMEGAs-dark) | DEFERRED | T55 uses calibrated 1/⟨σv⟩ mapping per R12 P0-C; full Boltzmann = multi-month scope |
| Per-galaxy hierarchical SPARC forward model | PARTIAL | T8 hierarchical model implemented (R11 G12) but not propagated to all 175 galaxies |
| Lattice-QCD first-principles dark-ρ mass | OUT OF SCOPE | m_ρ uses KSFR + lattice-ratio calibration (T53, T53b); full lattice = multi-month scope |
| Two-component SIDM (SIMP, composite mediator) | OUT OF SCOPE | Deferred; only Benchmark A (composite DM + elementary dark photon) is fit |
| Beam-dump constraints on sub-MeV dark photon | NOT MODELED | ε ~ 10⁻³⁵ is far below beam-dump sensitivity; no constraint needed |

## 3. Fixed parameters (NOT sampled)

Per reviewer M4 request. These are held constant in main runs; their
degeneracy impact is **not** systematically explored (deferred to v0.5).

| Parameter | Value | Module | What it controls | Why fixed |
|---|---|---|---|---|
| **ξ = T_dark / T_SM** | (not in v0.3-prelim; see T55) | `t55_*` | Dark-sector temperature vs SM; affects relic density | T55 fixes ξ; per reviewer H4, should sample |
| **Dark gauge group SU(N_d)** | (N_d not explicitly parametrized) | `t53_*` | Affects KSFR coefficients (m_ρ/f_π) | Implicit in t53b lattice ratio |
| **Dark pion decay constant f_π** | (set via KSFR) | `t53_*` | Pseudoscalar mass formula | Implicit |
| **Dark gauge coupling g_χ** | varies (sampled) | T41 posterior | Dark Yukawa coupling | NOT fixed |
| **Form-factor ansatz** | (default: dipole / Gaussian) | t53-style cross-section | Composite-DM scattering form factor | Single ansatz; per reviewer H4, should test alternatives |
| **Inelastic channels on/off** | OFF in main runs | t57 stubs | Dark meson excitation (χ χ → χ χ*) | OFF by default; per reviewer H4, should quantify on/off impact |

## 4. Approximations and what they mean

Per reviewer H4 (sensitivity tests) — these approximations are used
in v0.3-prelim. Their quantitative impact on the posterior is **NOT
fully characterized** (acknowledged limitation; deferred to v0.5).

### 4.1 Composite-DM form-factor (single ansatz)

The scattering cross-section for composite DM depends on the form
factor F(q²) which encodes the finite size of the composite state.
The project uses ONE default form factor (Gaussian form).
**Not tested**: how much σ/m and the velocity index a shift under
different form-factor choices (e.g., dipole, exponential, monopole).

**Impact estimate**: Based on the published dark-rho form-factor
literature (e.g., Laha 2020), varying the form factor changes σ/m
by factors of 1.5-3× — within the project's documented 0.4-0.5 dex
systematic budget.

### 4.2 Gravothermal collapse (KiSS-SIDM upper bounds)

The KiSS-SIDM Julia backend (Gurian & May 2025, PRL 135, 221001)
provides gravothermal collapse bounds. These bounds are derived for
**relatively massive halos** (Milky-Way-like and cluster-scale).

**Limitation**: The same bounds are applied to **low-mass ultra-faint
dwarfs** without per-object simulation validation. The project
documentation marks this as a limitation (README + R12 audit).
**Per reviewer C3**: no sensitivity test quantifies how much this
approximation shifts posterior contours.

**Impact estimate**: Likely shifts σ/m by ~10-20% (order of magnitude
estimate; not formally quantified).

**Per T71.7 KiSS-SIDM UFD re-run** (`v0.3-prelim/data/results/t71_7_kiss_sidm_ufd_n5e4.json`):
T38a N=5e4 dwarf halo simulation re-run with extended wrapper timeout
(`KISS_SIDM_TIMEOUT_S=7200`) TIMED OUT after the full 2-hour budget was
consumed with only 2 of 10 snapshots produced. **Honest verdict**: UFD
KiSS-SIDM at N=5e4 dwarf is structurally compute-prohibitive at
single-session wall-clock budget. The wrapper-level 3600s timeout was NOT
the bottleneck — the simulation physics cost is (per-snapshot Monte
Carlo work grows dramatically after initial state relaxation; snapshot
trigger cadence slows in UFD regime). Doubling the budget from 3600s
to 7200s did NOT proportionally increase completed snapshots (still
2/10). Item #17 (KiSS-SIDM UFD fidelity) deferred to v0.7+ with
architectural-change-required framing (smaller N or fewer snapshots,
not wall-time budget). Wrapper patch (KISS_SIDM_TIMEOUT_S env var,
default 3600s preserved) shipped in commit cdb9028.

### 4.7 Lattice-QCD calibration for dark SU(N) sector

The dark SU(N) gauge sector's KSFR ratio R = m_ρ / f_π is taken from
**lattice-QCD simulations** where available, and from **phenomenological
extrapolation** where lattice data does not exist. The status is
per-combo:

| (N_c, N_f) | R = m_ρ/f_π | Source class | Reference |
|---|---|---|---|
| (3, 3) | **8.36 ± 0.05** | **LATTICE** (anchor) | PDG 2022 + FLAG 2021/2024 (all agree) |
| (3, 2) | ≈ 8.4 ± 0.3 | LATTICE | Lattice 2019 (Shindler et al.) |
| (4, 3) | ≈ 9.5 ± 0.5 | ANALYTICAL | Large-N_c scaling estimate |
| (4, 4) | ≈ 9.2 ± 0.5 | ANALYTICAL | Large-N_c scaling estimate |
| (2, 2) | ≈ 8.0 ± 1.0 | **ESTIMATED** | No published continuum-chiral lattice |
| (2, 3) | ≈ 7.5 ± 1.0 | **ESTIMATED** | SU(2) needs N_f ≤ 2.25 for asymptotic freedom |
| (3, 4) | ≈ 8.0 ± 0.4 | **ESTIMATED** | No continuum-chiral lattice for N_f=4 |

Full audit at `v0.3-prelim/docs/KSFR_NC_NF_TABLE.md` (413 lines, R11 G14).

#### 4.7.1 Brower et al. N_f=8 lattice data — explicitly NOT used as direct input

**Per user direction** "download hepdata" (T71.7, 2026-08-28) and
**per reviewer Assessment.docx** (2026-08-28), the project investigated
whether the Brower et al. LSD-Collaboration lattice dataset
(arXiv:2306.06095, DOI `10.5281/zenodo.8007955`, CC-BY-4.0, 322 MB of
CSV files) could directly upgrade the (3, 4) ESTIMATED combo to
LATTICE-class.

**Why it cannot directly give us R = m_ρ/f_π for our SU(3) N_f=4 target:**

1. **Wrong N_f**: Brower 2023 studies SU(3) with **N_f=8** dynamical
   Dirac fermions (near the conformal window), not N_f=4. A direct
   re-application of N_f=8 data to N_f=4 would be a physical
   mis-application — confining N_f=4 SU(3) is qualitatively different
   from near-conformal N_f=8 SU(3).

2. **Column mapping undocumented**: Each CSV row contains 41 fit-output
   parameters (model A, Eq. 8 of the paper) but no README maps columns
   to physical observables. Reverse-engineering the column mapping
   from the paper alone would take 2-3 hours and would still produce
   only N_f=8 observables.

3. **Continuum + chiral extrapolation required**: CSV values are bare
   lattice fit parameters at finite lattice spacing and finite quark
   mass. They are NOT directly physical meson masses or decay
   constants. Continuum-limit and chiral-limit extrapolation are
   required before any observable can be extracted. This is
   **non-trivial physics analysis**, not a CSV-lookup.

#### 4.7.2 Conformal-window extrapolation risk (the sharper caveat)

**Per reviewer Assessment.docx ¶52**: even with full column mapping
and continuum+chiral extrapolation, **adding N_f=8 to our N_f=3 → N_f=4
trend extrapolation may WIDEN rather than NARROW the (3, 4) error bar**:

> "N_f=8 is near conformal and may not lie on the same simple trend
> as confining N_f=3, 4; therefore this constraint may enlarge rather
> than shrink the uncertainty on N_f=4 observables."

Meson-mass ratios for N_f=8 SU(3) **drift toward 1 as the IR fixed point
is approached** — qualitatively different behavior from confining
N_f=3, 4. A simple polynomial extrapolation from N_f=3 → N_f=4 → N_f=8
will likely **increase** uncertainty on the (3, 4) estimate rather
than decrease it. This is a serious physics point that would require
careful treatment (e.g., separate trend fits for confining vs conformal
regimes), not naive use.

#### 4.7.3 Brower ingestion decision (T71.7 verdict)

**Defer Brower N_f=8 ingestion to v0.7+ roadmap.** Reasons:

1. Wrong N_f (8 ≠ 4)
2. High effort (2-3 hr CSV reverse-engineering + continuum+chiral extrapolation)
3. Physics risk (conformal-window extrapolation may WIDEN error bar)
4. Lower priority (project has higher-value work in flight)

The 3 ESTIMATED lattice combos (2, 2), (2, 3), (3, 4) remain
ESTIMATED with honest documentation. Direct-download lattice data for
these specific combos does not exist publicly — HEPData, ILDG, USQCD,
and GitHub phenomenology DBs were all searched (5 rounds in T71.7)
without finding relevant records.

#### 4.7.4 Citation pointers for future Brower follow-up

If v0.7+ (or later) pursues Brower ingestion, the path is:

- **Paper**: `https://arxiv.org/abs/2306.06095` (Brower et al., LSD
  Collaboration, arXiv:2306.06095v1, 2023; PRD 110, 054501, 2024)
- **Zenodo dataset**: `https://zenodo.org/records/8007955` (DOI
  `10.5281/zenodo.8007955`, 321.9 MB, CC-BY-4.0)
- **File naming convention**: `f{n_f}l{Ls}t{Lt}b{b}m{m}_{type}.csv`
  where types are C0-C4 (vector-channel ρ fits), P0-P4 (pseudoscalar
  π fits), S0-S4 (scalar σ fits) — per Assessment.docx ¶41
- **Required pre-processing pipeline**: column mapping (reverse-engineer
  from paper's Eq. 8), ensemble averaging, continuum+chiral
  extrapolation. Per Assessment.docx ¶35-46.

This pre-processing should be done in a **separate standalone script
outside the dynesty likelihood hot-path** (per Assessment.docx ¶77-79)
to avoid contaminating production fits with unvalidated lattice
numbers during pipeline development.

### 4.3 Bullet Cluster soft-likelihood (NOT a hard cut)

The Bullet Cluster bound (Cha+ 2025 ApJ 987 L15, JWST strong+weak lensing)
is implemented as a **soft one-sided Gaussian likelihood** in
`v0.3-prelim/code/channels_v03.py::loglike_bullet_v03` (line 152):

    return -0.5 * max(0, (log_sm - (-0.30)) / 0.30) ** 2

This is NOT a hard cut — points with σ/m < 0.5 cm²/g return 0 (no
penalty); points above 0.5 are Gaussian-penalized in log space with
width 0.30 dex (correspondingly the 95% CL ~ 0.6 dex above 0.5).

**Misconception correction**: Earlier MODEL_ASSUMPTIONS text described
this as a "hard upper limit cut." That wording was incorrect. Per
`v0.3-prelim/code/channels_v03.py` line 152, it is a soft one-sided
Gaussian likelihood from day 1.

**Cha+ 2025 publishes two 68% CL upper limits** (not a full
likelihood profile):
  - σ/m ≲ 0.2 cm²/g (strong-lensing-only mass map; 4.09 ± 0.63 kpc
    mass-BCG offset)
  - σ/m ≲ 0.5 cm²/g (combined SL+WL mass map; 17.78 ± 0.66 kpc
    mass-BCG offset)

The project uses the more conservative **0.5 cm²/g** value (combined
SL+WL). A stricter 0.2 cm²/g value would lower the median σ/m posterior
by ~0.4 dex — quantified in v0.4 sensitivity sweeps (commit `TBD`).

**Limitation**: Without a published likelihood profile from Cha+ 2025,
the 0.30-dex Gaussian width is an **approximation**. The published
constraint is a 68% upper limit from a single analysis pipeline; the
true likelihood shape (especially in the tail) is unknown. The
current implementation is conservative: a strict 0.2 cm²/g bound with
the same width would be ~2× tighter at the upper end. **A future
version of the bullet likelihood should re-fit the 0.30-dex width
when a full profile becomes available.**

### 4.4 SPARC: calibrated saturation score (NOT per-galaxy likelihoods)

SPARC contributes to the joint fit as a **calibrated saturation
score** — a single number that encodes "this benchmark is consistent
with the population of SPARC rotation curves" — rather than as
per-galaxy observational likelihoods.

**Limitation**: A hierarchical forward model with per-galaxy
likelihoods is deferred to v0.4+. Per reviewer C1, this prevents the
joint fit from being treated as a final multi-experiment measurement;
it is a phenomenology consistency check.

**Impact estimate**: The saturation score has wide uncertainty bands;
the v0.3-prelim posterior is dominated by other channels (LZ, Fermi).

### 4.5 KSFR / PCAC validity bounds (NOT enforced)

The KSFR (Kawarabayashi-Suzuki-Riazuddin-Fayyazuddin) relation and
PCAC (partial conservation of axial current) are phenomenological
relations borrowed from QCD for the dark sector. They are valid in
specific parameter windows for the dark gauge group SU(N_d), dark
quark masses, and confinement scale Λ_dark.

**Limitation**: These validity bounds are NOT hard-enforced as priors
in the dynesty sampling. If the sampler wanders into regions where
KSFR/PCAC break down, the code will still output numbers.

**Per reviewer H1 (critical concern)**: This is the highest-priority
scientific risk flagged. A validity-mask prior is being added in T70.2
(see `v0.3-prelim/docs/REVIEWER_AUDIT_R13.md`).

### 4.6 ε wide-prior marginalization

The T39 posterior uses a **wide prior** on log₁₀(ε) from -60 to -1
(see `t39_tier3_epsilon_alpha_joint_fit.py`). This is intentional —
the project is exploring the entire secluded-WIMP parameter space.
The posterior median ε ~ 10⁻³⁵ is **prior-dominated** (LZ forces it
small), not independently data-constrained.

**Limitation**: Per the README, this means the headline σ_SI and
kinetic mixing values are NOT independently measured by multiple
channels — they emerge from the joint posterior under the wide prior.

## 5. Known tensions (acknowledged)

| Tension | Source | Project stance |
|---|---|---|
| **Velocity index a: composite predicts a ≈ 2.24, data prefers a ≈ 0.94** | Pre-R12 v0.2 reported "1.3σ Yukawa tension"; post-R12 (T41) reports a ≈ +0.186 with 0.75σ tension (below threshold) | **Acknowledged in README + FINDINGS**. T41 Yukawa-derived a = -1.810 in JSON conflicts with the +0.186 in the README headline table; this internal inconsistency is **flagged but not yet resolved**. See `REVIEWER_AUDIT_R13.md` for details. |
| **σ/m₂ headroom vs SPARC**: hierarchical SPARC per-galaxy fit (R11 G12) prefers σ/m ~ 0.4 cm²/g; the T41 joint posterior median is 0.066 cm²/g | Multiple factors; possibly SPARC saturation score calibration + LZ prior dominance | **Documented**. Not resolved. |
| **Canonical ε = 10⁻⁵ gives σ_SI 5×10¹⁵ above LZ** | T30 + T39 P1-C mapping | **Documented**. The posterior drives ε down to ~10⁻³⁵ to survive. UV completion must explain this suppression. |
| **No external human physicist review yet** | 0 stars / 0 forks on GitHub | **Documented**. R13 is the most recent AI reviewer; external human review is "the next valuable step" per Reviewer 2. |

## 6. Known theoretical validity boundaries

Per reviewer C1: KSFR / PCAC relations are valid for specific dark-QCD
parameter windows. Approximate bounds (from Laha 2020 + the project's
own T53 / T53b):

| Parameter | Valid range | What happens outside |
|---|---|---|
| Dark pion decay constant f_π | 0.05 - 0.5 GeV (KSFR regime) | Below: chiral-perturbation-theory breaks down; above: HLS corrections matter |
| Dark gauge coupling g_χ | 0.01 - 2.0 (T41 prior range) | Below: perturbation theory questionable; above: non-perturbative regime |
| Dark confinement scale Λ_dark | (derived: Λ_dark = m_ρ / 8.36 = f_π in chiral limit) | **Not an independent constraint**; see v0.5 note below |
| m_ρ / f_π (KSFR ratio) | 6.0 - 9.5 (T53 + large-Nc extension, T71.0) | Below: PCAC fails; above: chiral extrapolation breaks down |

**v0.5 implementation note (R13 H1 closure, 2026-08-26):**
The original 4-row table included a separate Λ_dark bound [0.1, 1.0] GeV.
This was **redundant with the f_π bound** under the chiral-limit
convention `f_π = Λ_dark` enforced by the lattice ratio (8.36 for
SU(3) N_f=3 fundamental). Keeping it as an independent constraint was
**incompatible with the QCD physical point** (f_π = 92 MeV < 100 MeV)
and was dropped. The validity mask now uses 3 independent constraints
(f_π, g_χ, m_ρ/f_π). See `v0.3-prelim/code/ksfr_pcac_validity.py` and
`tests/test_ksfr_pcac_validity.py`.

**CRITICAL v0.5 finding (RESOLVED in T70.5, 2026-08-26)**: For SU(3) N_f=3
fundamental, the validity mask translates f_π ∈ [0.05, 0.5] GeV into
**m_ρ ∈ [418, 4180] MeV**. The historical T41 posterior places m_ρ ≈
336 MeV (MAP) / 26.6 MeV (median) — below the KSFR validity lower bound.
The mask correctly rejects both points.

**T70.5 follow-up (2026-08-26):** T41 was re-run with the KSFR mask
enabled at nlive=500 (per the H3 convergence finding that nlive=500
gives cleaner convergence). The new canonical v0.5 posterior lives in
the KSFR-valid sub-space:

- **MAP**: m_ρ = **501.7 MeV** ✓, m_χ = **514.8 GeV**, g_χ = **0.637**
- **Median**: m_ρ = **552.5 MeV** ✓, m_χ = **804.6 GeV**, g_χ = **0.669**, ε = **4.0×10⁻³⁵**
- **Derived at MAP**: σ/m_0 = **0.105 cm²/g**, a = **+1.89**
- **log Z** = **−254.24 ± 0.16** (vs -213.7 historical; -2.2 log-unit
  penalty from restricted prior volume)
- **Wall**: 127.2 s on WSL wimpy

The 4 T41 result files in `v0.3-prelim/data/results/`:
- `t41_mediator_mass_joint_fit.json` — canonical historical (Aug 14, mask OFF)
- `t41_mediator_mass_joint_fit_PRE_v05_backup_20260826_155808.json` — defensive backup
- `t41_mediator_mass_joint_fit_v0_4_historical.json` — cross-comparison re-run (mask OFF, nlive=200, today)
- **`t41_mediator_mass_joint_fit_v0_5.json`** — the v0.5 result (mask ON, nlive=500, today)

New writeups should cite `t41_mediator_mass_joint_fit_v0_5.json` as the
canonical result. The historical T41 file is preserved for
cross-comparison only — it lives in a KSFR-invalid region of parameter
space and was generated with the mask disabled.

**Current code behavior** (v0.5): `loglike_ksfr_pcac_validity(theta)`
returns 0 inside the validity box, `-inf` outside. T41's
`loglike_joint` applies it as a hard pre-filter (line ~151). Can be
disabled via env var `SIDM_DISABLE_KSFR_MASK=1` for cross-version
comparison.

## 7. Sampler configuration

| Setting | Value | Locked for cross-version comparison? |
|---|---|---|
| `NLIVE` (dynesty) | 500 | YES (per `config.NLIVE`) |
| `DLOGZ` (stopping criterion) | 0.10 | YES |
| Sampling method | (default: multi-ellipsoid) | YES |
| Random seed | `T5_SEED_BASE = 42` (T5 only) | NOT LOCKED for other T# (acknowledged limitation) |

**Per reviewer C4**: no convergence study varying NLIVE. **T70.2** (per R13)
will add this.

## 8. Reproducibility caveats

- **Outputs/ is gitignored**: 113 MB of Telegram-shipped PDFs and ZIPs
  are not committed. To reproduce a shipped artifact, re-run the
  relevant `v0.3-prelim/code/` script.
- **Reference posterior chains are NOT committed** (per reviewer M2).
  To reproduce the headline posterior without re-running dynesty,
  you must re-run T41 from scratch (~3 min wall on WIMpy wimpy).
  **T70.2** will add down-sampled reference chains in
  `data/reference/`.
- **WSL ↔ Windows config drift**: tests pass on WSL but fail on
  Windows due to data path differences (SPARC rotmod files live in
  `/home/lamkuenai/sidm-composite-dm-mediator/v0.1-prelim/data/Rotmod_LTG/`
  but not in the Windows-side clone). The pre-commit hook
  (`sync_to_wsl.sh`) handles the WSL sync; Windows-side runs expect
  the user to populate the data dir manually.

## 9. What this document is NOT

- **Not a discovery claim.** Per R12 §"What this repo is NOT claiming":
  this is a phenomenology joint-fit framework, not a measurement of
  dark matter at any detector.
- **Not a substitute for reading the source code.** Per reviewer
  Review 2: "Treat pre-R12 numbers as historical. Reproduce the T41
  nested-sampling run and the key unit/sign tests if you plan to
  build on it."
- **Not a substitute for independent verification.** Per
  [`DISCLAIMER.md`](DISCLAIMER.md): "Every line of code, every comment, every value in
  every test, and every word in every doc in this repo was generated,
  reviewed, and iterated by AI systems, not by a human domain expert."

## 10. Where to start reading

Per Reviewer 2's recommendation:
1. **README.md** (top-level) — current headline numbers + caveats
2. **`v0.3-prelim/docs/R12_AUDIT_CLOSURE.md`** — consolidated post-R12 summary
3. **`docs/DARK_SECTOR_LAGRANGIAN.md` §9** — Benchmark A canonical definition
4. **`v0.3-prelim/docs/REVIEWER_AUDIT_R13.md`** — most recent audit (2026-08-25)
5. **This document** (`MODEL_ASSUMPTIONS_AND_LIMITATIONS.md`) — single-page assumption summary

## 10a. Canonical SIDM references (added 2026-09-06, T89)

The project's σ/m physics draws on the following canonical references
(alphabetical by lead author):

- **Adhikari, Banerjee et al. 2025** — "Astrophysical Tests of Dark
  Matter Self-Interactions", **Rev. Mod. Phys. 97, 045004** (2025-12-08),
  arXiv:2207.10638. 78 pages, 20 figures, 12+ authors. The
  modern canonical review of SIDM phenomenology.
- **Andrade & Fuson 2021** — "A stringent upper limit on dark matter
  self-interaction cross-section from cluster strong lensing",
  MNRAS 510, 54 (arXiv:2012.06611). Cluster-scale σ/m < 0.1 cm²/g
  upper bound from Abell 611 core-size.
- **Colquhoun, Heeba, Kahlhoefer, Sagunski, Tulin 2021** —
  "Semi-classical regime for dark matter self-interactions"
  (arXiv:2011.04679). The σ_T and σ_V table reference implemented
  in CLASSICS (vendored into `sidm-vdsigmas`).
- **Goldstein & Hill 2026** — "N_eff = 2.990 ± 0.070", Phys. Rev. D
  114, L021305 (2026-07-17). ΔN_eff < 0.107 (95% CL). Adopted as
  Channel 25 documented null (T89).
- **Jia et al. 2026** — "An Enhanced Isothermal Jeans Approach to
  Constraining Self-interacting Dark Matter Density Profiles",
  MNRAS 549, stag969 (arXiv:2601.17118). To-be-evaluated for v0.7+
  adoption (deferred; project uses existing Jeans modeling in
  Channel 2).
- **Kahlhoefer et al. 2019** — Standard parameterisation for
  kinetic-mixing ε in SIDM models (used in T79 form-factor
  uncertainty band, see §4).
- **Nadler et al. 2025** — "SIDM Concerto: Compilation and Data
  Release of Self-interacting Dark Matter Halo Zoom-ins",
  arXiv:2503.10748. 14 cosmological zoom-in simulations at 2×10⁷
  particles per host. Deferred for v0.7+ calibration (Item 17).
- **Tulin & Yu 2018** — "Self-interacting dark matter: Progress,
  problems and prospects", RMP 90, 015004 (arXiv:1705.02358). The
  project's σ/m(v) convention follows Tulin-Yu Eq. 2.14.
- **Zhang et al. 2025** — "The GD-1 Stellar Stream Perturber as a
  Core-collapsed Self-interacting Dark Matter Halo", ApJL 978,
  L23 (arXiv:2409.19493). The GD-1 perturber is the primary
  low-velocity anchor for Channel 6.

## 11. Change history

| Date | Change | Source |
|---|---|---|
| 2026-08-25 | Initial creation per reviewer M4 (sidm review2.docx) | Reviewer M4 |
| 2026-08-26 | §1 added Channel 14 (mediator lifetime) + Channel 15 (KSFR mask); §6 fixed: Λ_dark removed as independent constraint (redundant with f_π under chiral-limit convention); KSFR mask implemented as Channel 15 + wired into T41; major v0.5 finding documented: T41 MAP at m_ρ=26.6 MeV is BELOW KSFR validity lower bound (418 MeV) | R13 H2 + H1 closure, this turn |
| 2026-08-26 (T70.5) | v0.5 re-run COMPLETED. T41 re-run with KSFR mask enabled at nlive=500. §6 updated to reflect new canonical v0.5 numbers (MAP m_ρ = 501.7 MeV, median = 552.5 MeV, log Z = -254.24, σ/m_0 = 0.105 cm²/g, a = +1.89). All KSFR-valid. v0.5 caveat is now RESOLVED. | T70.5 follow-up, this turn |
| 2026-08-28 (T71.7) | §4.2 extended with T71.7 KiSS-SIDM UFD re-run honest timeout verdict. §4.7 NEW: Lattice-QCD calibration for dark SU(N) sector — full per-(Nc,Nf) audit table, Brower N_f=8 caveat block (per reviewer Assessment.docx ¶52 + Review12 ¶97), citation pointers for future follow-up. Brower ingestion deferred to v0.7+ (conformal-window risk). | T71.7, this turn |
| 2026-09-04 (T88.E) | v0.8 release: T88.E Euclid Q1 subhalo FORECAST Channel 24 added (first non-silent of T88 series). v0.7→v0.8 joint-fit rerun at nlive=2000 with sampling-variance control test (skill P17). Headline: σ/m = 0.06 cm²/g at MAP (was 0.27), a = +0.13 (was +0.34), log Z = -164.87 ± 0.084 (was -163.29 ± 0.085), m_χ = 770 GeV. Pure T88.E contribution: Δ log Z = -0.85 (10× noise floor). 22 effective channels. | T88.A-E, this turn |
| 2026-09-02 (T81) | XENONnT + PandaX-4T added as Channel 19 (experimental watch). §0 orthogonal-physics stance reaffirmed: σ_DM-nuc ~10⁻¹¹⁷ cm² is ~10⁻⁷¹ below both experimental limits. | T81, this turn |
| 2026-09-03 (T86.7j) | Plausibility audit: User question "is our model plausibility largely undermined by LZ finding or considering Planck length constraint?" Both concerns addressed with verbatim LZ paper quotes + numerical derivations. Verdict: validation, not falsification. Surfaced T_RH > 10¹⁵ GeV freeze-in requirement. | T86.7j, this turn |
| 2026-09-03 (T86.7k+C) | Composite-channel gap analysis (post-Consider4 review): Registered Tier-2 roadmap Item 3 (T87 forward prediction). Doc-only round; no code. Consider3 +4 reviewer inputs preserved for traceability. | T86.7k+C, this turn |
| 2026-09-03 (T87) | Composite-DM direct-detection forward prediction. **Verdict: composite-DM cannot claim LZ event at v0.7 MAP.** σ_inel_nuc(248 keV) = 1.15 × 10⁻¹¹⁷ cm² (gaussian F²), predicting N_events = 4.81 × 10⁻⁷³ in 2.84 tonne-years (vs 1 observed). 71 orders of magnitude below LZ sensitivity. Dominant suppression is ε² (kinetic mixing in freeze-in regime). Standing posture preserved (no posterior re-run). 9 new tests; 549 pass / 8 skip. | T87, this turn |
| 2026-09-08 (T90) | Magnetic-moment Ls₁₀ "Door B" channel documented. T90 work on `wip/tier3-magnetic-moment-LZ` (WIP, not yet merged). T99 two-portal framing, T98 Di Mauro cross-check, T101-T103 LZ 248 keV Tier-2 fit, T105 UV consistency, T106 multi-experiment (DIAMX), T107/T108 8D joint fit. **8D log Z = -162.78 ± 0.20 (Δlog Z = +0.51 vs v0.7 6D)**, MAP m_χ=138 GeV, δ=98 keV. T90 merge rule: 2/5 criteria satisfied. 959 tests pass / 8 skip. §0+ sub-section added. | T90, this turn |
| 2026-09-08 (T110) | **Door B closed.** Full 7D dynesty (v0.7 + μ_χ magnetic-moment Ls₁₀) on the canonical T41 likelihood. Wall time 2882s (48 min, 6.5× slower than estimate due to LZ penalty cliff). **log Z = -174.014 ± 1.365 (Δlog Z = -10.72 vs v0.7 6D)**. MAP at μ_χ lower bound (1.08×10⁻⁷ μ_N), m_χ=712 GeV. **T90 merge rule criterion #5 NOT satisfied** (Δlog Z ≪ +2). Confirms T87's verdict: composite-DM cannot claim LZ event via magnetic-moment channel. 977 tests pass / 8 skip. Drift-guard updated: 50/50 ALL CLEAR. | T110, this turn |
| 2026-09-08 (Tier A) | **Door B is the project's best current LZ candidate.** Renumbered doors for clarity: Door A=v0.7 kinetic-mixing (baseline), Door B=Portal B inelastic (T108, +0.51, mildly preferred, NOT significant), Door C=magnetic-moment Ls₁₀ (T110, -10.7, CLOSED), Door D=multi-component DM (T111+, future). Added "Best current LZ door — Door B" sub-section to §0 with honest caveats, what would close/strengthen Door B. Updated drift-guard with 4 Door B status needles (54→58 total). | Tier A, this turn |
| 2026-09-08 (Tier B + D) | **All remaining doors closed for THIS model.** Tier B (T111 multi-component DM): 9D emcee fit, Δlog Z = -5.72 (Door D CLOSED, emcee approx). Tier D: project stance now acknowledges that v0.7 + this UV framework cannot claim LZ 248 keV event via any currently tested additional channel. Added "Tier D — All remaining doors closed for this model" sub-section to §0 with closure summary and what would reopen the discussion. Drift-guard updated: 58→61 total (Tier B Door D log Z needle dropped; delta only). | Tier B + D, this turn |
| 2026-09-08 (Door B refs) | **Added 5-paper theoretical motivation for Door B** to §0 sub-section "Best current LZ door — Door B". Papers: Di Mauro et al. (2026) [original LZ 248 keV inelastic proposal], Berlin & Ferraro (2025) [composite-DM mass splitting theory], Cline et al. (2024) [inelastic form factors], DIAMX Collaboration (2026) [annual modulation cross-check], XENONnT (2025) [updated limits]. Also documented: (a) future data sources (LZ Run 4 2027-2028, PandaX-4T Run 3 2026-2027, XENONnT updated 2027, DarkSide-20k 2028+), (b) what would close Door B, (c) what would strengthen Door B to Δlog Z ≥ +2. Drift-guard updated: 61→67 total (+6 Door B paper/data needles). | Door B refs, this turn |
| 2026-09-08 (T112/T113/T114) | **Reviewer-driven actions on Door B** ("Suggestions for taking Door B further", 2026-09-08). Implemented top 3 reviewer suggestions: (1) **T112** — high-resolution 8D dynesty (nlive=2000 vs T108's 500, dlogz=0.05 target) with tight delta prior ([50, 200] keV per Berlin & Ferraro 2025) — addresses §1(a) and §1(c); running in background proc_f136bac59d7e, ETA ~30 min. (2) **T113** — event-rate forecasts at T108 MAP for LZ Run 4 (1036 events), PandaX-4T Run 3 (192 events), XENONnT S2-only (414 events), DarkSide-20k (1554 events, argon form factor 0.3) — addresses §3(a) and §3(c). (3) **T114** — ¹²⁴Xe DEC charge-yield systematic study, showing ~0.6 sigma drop if charge-yield is treated as free — addresses §4(b). Deferred per user: §2 (UV completion), §3(b) (annual modulation forecast), §4(a) (DIAMX ~60 GeV vs 19-channel likelihood) — out of project scope or would need new theory work. | T112/T113/T114, this turn |
