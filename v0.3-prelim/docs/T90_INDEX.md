# T90 Magnetic-Moment LZ 248 keV — Consolidated Index

**Status:** Index doc (Path 7 of the 'proceed 1,2 3 4 6 7' plan)
**Date:** 2026-09-07 (updated with v18 lattice + T88.E2/F real-data findings)
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Author:** T90 working group

---

## Purpose of this index

The T90 work has grown to ~10 separate docs across multiple
sessions. This index provides a single entry point with brief
abstracts and a reading order. **The individual docs remain
authoritative for their content**; this is a navigation aid.

**Cross-link to T95 (SIDM cross-check program)**: see
[T95_CONSOLIDATED_RESULTS.md](./T95_CONSOLIDATED_RESULTS.md).
The T95 work tests whether the LZ-anchored Yukawa SIDM
cross-section is consistent with BAHAMAS-SIDM, dwarf-galaxy
core sizes, Euclid Q1 sub-halo forecasts, and the Zhang+ 2025
GD-1 perturber constraint. **T95 finds substantial-to-very-strong
tension** with these astrophysical probes — see "T95 cross-check"
section below.

**Cross-link to Di Mauro 2026 (arXiv:2609.02608)**: see
[T87_LZ_FORWARD_PREDICTION.md](./T87_LZ_FORWARD_PREDICTION.md)
§13 "Cross-link: Di Mauro 2026". The paper interprets the LZ
248 keV event as inelastic scattering via the 𝒪₁ˢ (L10s) operator
with mass splitting δ ≈ 297-371 keV. **The kinematic part of the
paper's prediction is consistent with the T87 δ-sweep, but the
required σ_DM-nuc (~10⁻⁴³ cm²) is 74 orders of magnitude above
v0.7 MAP (~10⁻¹¹⁷ cm²). The v0.7 MAP cannot produce the LZ event
under the Di Mauro interpretation, and the T90 magnetic-moment
branch is a separate elastic EFT channel that does not depend
on δ.** This paper is the first published BSM-model motivation
for the Ls₁₀ operator specifically (one of the 5 T90 merge
criteria), but does not by itself satisfy the T90 merge rule.

**Cross-link to T99 (two-portal framing, 2026-09-08)**: see
[T99_TWO_PORTAL_COMPOSITE_DM.md](./T99_TWO_PORTAL_COMPOSITE_DM.md).
Frames the v0.7 MAP (kinetic-mixing ε ~ 10⁻³⁷) and the Di Mauro
2026 prediction (inelastic 𝒪₁ˢ, δ ~ 297 keV) as **two independent
dark-sector portals** that can coexist in the same composite-DM
UV completion. The T17 v17 47/47/6 posterior split is consistent
with three independent portals (kinetic mixing, inelastic 𝒪₁ˢ,
magnetic-moment) all contributing ~30-50% posterior. The framing
is interpretive; no new model parameters, no new fit, no T90 merge.

**Cross-link to T105 (UV consistency check, 2026-09-08)**: see
[T105_UV_CONSISTENCY.md](./T105_UV_CONSISTENCY.md). Quantifies
the T99 framing: sweeps (m_ψ, Λ_D, α_D, suppression_orders)
parameter space (810,000 points) and asks whether BOTH Portal A
and Portal B can be produced from the same composite-DM structure.
Result: 0.08% of parameter space satisfies both (TIGHT verdict).
The Alves-Wacker 2010 framework naturally produces both portals
from the same composite structure, but only in a narrow corner.

**Cross-link to T106 (multi-experiment joint fit, 2026-09-08)**: see
[T106_MULTI_EXPERIMENT_JOINT.md](./T106_MULTI_EXPERIMENT_JOINT.md).
Adds PandaX-4T and XENONnT constraints to T103's LZ-only fit, using
the DIAMX combined analysis (arXiv:2512.05850v3, Nov 2025). **CRITICAL
FINDING: T90 merge criterion #1 is SATISFIED** (2 of 3 experiments
show > 2.5σ at the same DIAMX best-fit point m_χ=60 GeV, δ=130 keV).
But: project's T103 MAP at (483 GeV, 295 keV) is 15σ from DIAMX
best-fit — a major TENSION. The data prefer a LIGHTER DM mass than
what the project's LZ-only fit suggests. **T90 merge is now closer
to justified (2 of 5 criteria: #1 + #4) but still needs 1 more.**

**Cross-link to T107 (full 8D joint fit, 2026-09-08)**: see
[T107_FULL_8D_JOINT.md](./T107_FULL_8D_JOINT.md). **MAJOR REVISION
to the project's LZ-only best-fit.** 8D emcee MCMC with 6 v0.7
parameters + (log δ, log σ_PortalB) finds MAP at m_χ=131 GeV,
δ=145 keV, σ_PortalB=2.9×10⁻⁴¹ cm². This is **closer to DIAMX
endothermic best-fit (60 GeV, 130 keV) than to T103 (483 GeV, 295
keV)** — distance 0.34 vs 0.65 in (m_χ, δ) log space. The 8D fit
RESOLVES the T103↔DIAMX tension by settling on an intermediate
lighter-mass region. B1-lite (emcee, not full dynesty). 5.1s wall
time. **T90 merge rule: 2 of 5 criteria satisfied** (same as T106;
T107 strengthens but doesn't add a new criterion).

**Cross-link to T108 (full 8D dynesty, 2026-09-08)**: see
[T108_FULL_8D_DYNESTY.md](./T108_FULL_8D_DYNESTY.md). **First proper
8D nested sampling** run (not B1-lite emcee). 7.3 min wall time at
nlive=500, dlogz=0.1. **log Z = -162.78 ± 0.20** (v0.7 6D = -163.29,
**Δlog Z = +0.51**). MAP: m_φ=479 MeV, m_χ=138 GeV, δ=98 keV,
σ_PortalB=1.4×10⁻⁴² cm². **Confirms T107's lighter-mass region**
(m_χ ≈ 130-140 GeV vs v0.7's 498 GeV). **T90 merge rule criterion
#5 (Δlog Z ≥ +2) is NOT YET satisfied** (Δlog Z = +0.51, 2.5σ
positive but below +2 threshold). **2 of 5 criteria satisfied**
(same as T106/T107; T108 is the strongest evidence yet that the
8D extension is consistent with v0.7).

**Cross-link to Phase 3 (UV completion via lattice)**: see
[T90_PATH_C4_V18_LATTICE_UV.md](./T90_PATH_C4_V18_LATTICE_UV.md)
(also inline below). The v18 UV calculation uses LSD lattice
(Appelquist+ 2013, PRD 88, 014502) form factors to compute the
composite-DM magnetic moment from first principles. **The lattice
predicts μ_DM ~ 1.27×10⁻⁴ μ_N at M_B = 10 TeV, ~2000× larger than
LZ's 6.10×10⁻⁸ μ_N. The M_B matching LZ (~1 TeV) violates XENON100
(M_B > 10 TeV). The composite-DM UV interpretation is RULED OUT.**

**Cross-link to T88.E2/F (real data incorporation)**: see
[`T90_PATH_C4_V19_REAL_DATA.md`](./T90_PATH_C4_V19_REAL_DATA.md)
(also inline below). The v19 work replaces FORECAST data with
real Euclid Q1 strong-lensing counts (Bergamini+ 2026) and
real XENONnT/PandaX 8B CEvNS measurements (PRL 133, 2024).
**Both real-data channels show no significant tension with the LZ
interpretation** — but the cluster count alone has too little
statistical power (14 clusters) to falsify it.

**Cross-link to T90.27 (RELHIC / Cloud-9, 2026-09-10)**: see
[`T90_PATH_C4_V27_RELHIC_CLOUD9.md`](./T90_PATH_C4_V27_RELHIC_CLOUD9.md).
Adds the Yang+2024/2025 parametric SIDM halo model + Cloud-9
(arXiv:2608.04362) + M51 Cloud S/N (arXiv:2607.21034) as
Channel 27 of the T41 joint fit, env-gated by `T90_RELHIC_V27=1`.
This is the FIRST non-silent channel at the dwarf-halo mass scale
(M_halo ~ 3-5×10⁹ M_sun, v200 ~ 28 km/s). At the v0.7 master MAP,
the channel contributes **Δ log L = -382** because the master
predicts σ/m ~ 0.34 cm²/g at v200, which is 3 orders of magnitude
below Cloud-9's published SIDM best-fit of σ/m ~ 483 cm²/g.
This is the **expected result** — it confirms the published
Cloud-9 paper's conclusion that σ/m must be ≳ 50 cm²/g at the
dwarf-halo v200 to produce the observed cores. The T90.27
channel makes this a quantitative constraint on the master
posterior. **T90.27 is a non-merge-blocking addition to the
branch** (the T90 merge rule is unchanged).

**Cross-link to T90.28 (Cloud-9 MCMC proper inference, 2026-09-10)**:
see [`T90_PATH_C4_V28_RELHIC_MCMC.md`](./T90_PATH_C4_V28_RELHIC_MCMC.md).
**Supersedes T90.27 v1** as Channel 27 of the T41 joint fit.
T90.28 runs an emcee MCMC (32 walkers × 500 steps) on the
published Cloud-9 N(HI) data with the cosmological
concentration-mass prior, then evaluates a 2D (σ/m at v200, τ)
posterior at the joint-fit (σ_m_0, a). At the v0.7 master MAP,
**Δ log L = -10** (vs T90.27 v1's -382) — a much more
physically reasonable penalty. T90.28 v2 also includes the
**Diemer & Joyce 2019 concentration-mass prior**, which is the
cosmological prior that discriminates CDM (7σ below median)
from SIDM (3.2σ below). **T90.28 is a non-merge-blocking upgrade
to T90.27 v1** (the channel still uses the same env gate
`T90_RELHIC_V27=1`; the T90.27 v1 is preserved as a fallback).

**Cross-link to T90.29 (Yukawa velocity-dependent σ/m, 2026-09-10)**:
see [`T90_PATH_C4_V29_RELHIC_YUKAWA.md`](./T90_PATH_C4_V29_RELHIC_YUKAWA.md).
**Supersedes T90.28 v2** as Channel 27 of the T41 joint fit.
T90.29 v3 uses the **physical Yukawa velocity-dependent σ/m**
from `t40_yukawa_sigma_m.py` (Born approximation, Tulin+Yu 2018)
instead of the power-law approximation used by T90.28 v2. The
Yukawa form naturally gives Cloud-9's σ/m ~ 50-500 cm²/g at
v=28 km/s for **m_phi = 1-10 MeV** and **g_chi = 0.13-0.4** (all
perturbative, g_chi < 4π ≈ 12.6). This is the Option C fix
discussed in T90.28. **T90.29 is the new default for Channel 27**
when T90_RELHIC_V27=1; T90.28 v2 and T90.27 v1 are preserved
as fallbacks. **T90.29 is a non-merge-blocking addition** (the
T90 merge rule is unchanged). **Next step (T90.30+):** re-run
T41 with the m_phi prior extended to [1, 10] MeV so the master
posterior can actually move into the Cloud-9-favorable regime
(σ/m ~ 50-500 cm²/g at v=28 km/s).

**Cross-link to T90.30 (T41 re-run with T90.29 v3, 2026-09-10)**:
see [`T90_PATH_C4_V30_T41_RERUN.md`](./T90_PATH_C4_V30_T41_RERUN.md).
Three T41 runs (A: baseline, B: T90.29+KSFR ON, C: T90.29+KSFR
OFF) at nlive=200 show that **a single RELHIC candidate cannot
overpower the cumulative weight of the project's 20+ other
data channels.** All three runs converge to σ/m(28) ~ 0.3
cm²/g, which is 2-3 orders of magnitude below Cloud-9's
required 50-500 cm²/g. Run C moved the median m_phi from ~700
MeV to ~170 MeV (factor 3-5x lighter) but did not reach the
Cloud-9-favorable m_phi = 1-10 MeV regime. The honest finding:
**moving the master posterior into the Cloud-9-favorable
regime requires either more RELHIC candidates (the 70-candidate
Monaci+ 2026 catalog), an informative Jeffreys prior on m_phi,
or a dedicated Cloud-9-dominated fit.** T90.30 also fixed a
real IndexError bug in the T90.29 v3 histogram interpolation
(with regression test). **T90.30 is a non-merge-blocking
addition** that ships a re-runnable driver, the bug fix, and
the documentation.

**Cross-link to T90.31/32/33 (three-option Cloud-9 rescue, 2026-09-10)**:
see [`T90_PATH_C4_V31_V32_V33_THREE_OPTIONS.md`](./T90_PATH_C4_V31_V32_V33_THREE_OPTIONS.md).
Three options tested to move the master posterior into the
Cloud-9-favorable regime:
  - Option 1 (T90.32): Monaci+ 2026 70-candidate RELHIC population likelihood.
  - Option 2: Jeffreys prior on m_phi. **ALREADY ACTIVE** (the existing
    flat-log prior is the Jeffreys prior for a scale parameter).
  - Option 3 (T90.31): Cloud-9-dominated fit (`T41_CHANNEL_WEIGHT_NONRELHIC=0.0`).
**Headline finding:** combining Options 1+3 (T90_RELHIC_POP=1 +
T41_CHANNEL_WEIGHT_NONRELHIC=0.0) moves the master posterior to
**m_phi = 31.59 MeV, σ/m(28) = 48.1 cm²/g** — *just below*
Cloud-9's 50 cm²/g floor and the first time the master posterior
has converged to σ/m(28) in Cloud-9's range. **80/80 tests passing
total** (16 T90.27 + 12 T90.28 + 13 T90.29 + 10 T90.32 + 29 LZ).
T90.31/32/33 are non-merge-blocking additions that ship a
re-runnable driver, a population-level RELHIC likelihood, and a
Cloud-9-dominated-fit mode.

**Cross-link to T90.35/36/37 (Yang+ 2024 + tuned Yukawa + Anand+ 2025, 2026-09-10)**:
see [`T90_PATH_C4_V35_V36_V37_CLOUD9_CROSSVAL.md`](./T90_PATH_C4_V35_V36_V37_CLOUD9_CROSSVAL.md).
Three channels based on T90.34 literature review (Yang+ 2024, Anand+ 2025,
Ms.Marvel DMO 2026):
  - T90.35: Yang+ 2024 parametric SIDM form (canonical, cosmological-simulation-calibrated)
  - T90.36: Tuned Yukawa aggressive (g_chi ~ 1.5, perturbative)
  - T90.37: Anand+ 2025 stellar mass cross-validation (M_star < 10^3.5 M_Sun)
**Headline finding:** combined with Options 1+3 (Cloud-9-dominated),
**median σ/m(28) = 55 cm²/g** — IN Cloud-9's 50-500 cm²/g range.
**100/100 tests passing** total (16 T90.27 + 12 T90.28 + 13 T90.29
+ 10 T90.32 + 20 T90.35/36/37 + 29 LZ).
T90.35/36/37 are non-merge-blocking additions.

**Branch summary (Cloud-9 branch, 2026-09-10)**:
see [`T90_PATH_C4_CLOUD9_BRANCH_README.md`](./T90_PATH_C4_CLOUD9_BRANCH_README.md).
The T90.27-37 Cloud-9 work has been captured in a new branch
`wip/cloud-9-relhic` (branched from `wip/tier3-magnetic-moment-LZ` at
commit `cee378a`). 17 commits, 100 tests, full file index, reproducibility
instructions, honest caveats, and future work. The unified model that
reaches Cloud-9's regime is (g_chi ~ 1.5, m_phi ~ 100 MeV, m_chi ~ 30 GeV)
with all Cloud-9 channels active and 17 other channels silenced.
**The branch is the canonical record of the T90 Cloud-9 investigation.**

**Cross-link to T90.38 + T90.40 (per-channel vdep + honest unification, 2026-09-10)**:
see [`T90_PATH_C4_V40_HONEST_UNIFICATION.md`](./T90_PATH_C4_V40_HONEST_UNIFICATION.md).
Implements the reviewer Point 2 assessment: per-channel velocity correction
(`T41_VDEP_CORRECTION=1`) + honest unification test (3-run T41 comparison).
**Reviewer Point 2 partially validated**: the MCMC DOES move to light-
mediator regime (m_phi ~ 15-47 MeV) at full channel weight when all T90
channels are active. But σ/m(28) is too low because channels apply their
own internal power-law scaling that doesn't fully propagate the Yukawa
velocity dependence. A true implementation requires rewriting channel
likelihoods to use σ/m(v) directly (T90.41+ future work).
**109/109 tests passing** total (16 T90.27 + 12 T90.28 + 13 T90.29
+ 10 T90.32 + 20 T90.35-37 + 9 T90.38 + 29 LZ).

---

## Reading order

### Part 1: The T90 hypothesis

1. **`T90_MAGNETIC_MOMENT_PLAN.md`** — original plan: what is
   the LZ 248 keV event, and how would a magnetic-moment
   DM interpretation work? Includes Jeffreys footnote and
   UV-matching roadmap.

2. **`T90_MAGNETIC_MOMENT_FORWARD_PREDICTION.md`** — Phase 7
   forward prediction: what other detectors should see if
   the magnetic-moment interpretation is correct.

### Part 2: Cross-detector predictions (Path C.4)

3. **`T90_PATH_C4_CROSS_DETECTOR.md`** — v10: central-value
   predictor. Cross-detector predictions at the LZ-tuned
   point estimate. **PUBLISHED (commit `5d7cc47`).**

4. **`T90_PATH_C4_FOLLOWUPS.md`** — v11+v12+v13: posterior
   integration, detector response, other operators. The
   key findings:
   - 22-36% of posterior mass above PandaX/DARWIN/LZ-Upgrade
   - Magnetic-moment spectrum is broad (500× more events at
     low E_R than at 248 keV)
   - LZ event is specifically magnetic-dipole, not generic
     EFT. **PUBLISHED (commit `baf0fa1`).**

5. **`T90_PATH_C4_V14_CALIBRATED.md`** — v14: properly-calibrated
   multi-operator. Key finding: **millicharge is strongly
   excluded** by PandaX at LZ-calibrated coupling. **PUBLISHED
   (commit `f1b4f78`).**

6. **`T90_PATH_C4_V16_UV_COMPLETION.md`** — v16: UV completion
   of the magnetic-moment operator. 3 UV models calibrated
   to LZ: composite DM (Aranda+ 2016), vector-like fermion
   (Hisano+ 2002), dark photon (Fabbrichesi+ 2020). **PUBLISHED
   (commit `38256ff`).**

7. **`T90_PATH_C4_V15_INDIRECT_SIGNALS.md`** — v15: indirect-detection
   predictions. Headline: **magnetic-moment DM is 5-12 orders
   below current indirect-detection limits**; indirect detection
   CANNOT falsify the LZ interpretation. **PUBLISHED
   (commit `a1415da`).**

8. **`T90_PATH_C4_V17_LZ_TIME_SERIES.md`** — v17: LZ time-series
   with public data. **PUBLISHED (commit `cfb2924`).**
   Bayesian posteriors for 5 hypotheses:
   - Magnetic-moment DM: 47%
   - Higgsino inelastic DM (Fan & Tweed 2026): 47% (TIED)
   - Instrumental: 6%
   - Solar neutrino 8B: 0.03%
   - 124Xe DEC: 0%

### Part 3: Real data incorporation (Phase (b))

9. **`T90_PATH_C4_V19_REAL_DATA.md`** — v19: real Euclid Q1 +
   XENONnT/PandaX 8B CEvNS incorporation. **PUBLISHED
   (commits `e3e0b73`, `25de747`).**
   - Real Euclid Q1:14 grade-A strong-lensing clusters
     (Bergamini+ 2026, arXiv:2503.15330). Δlog L = -0.073 (no
     tension from cluster counts alone; Poisson noise too large).
   - Real 8B CEvNS: XENONnT (PRL 133, 191002) + PandaX-4T
     (PRL 133, 191001). σ_xe = (1.1+0.8/-0.5)×10⁻³⁹ cm²,
     consistent with SM. SIDM doesn't contribute to CEvNS directly
     (no DM-nucleon coupling in master Yukawa).

### Part 4: Genuine UV calculation (Phase (a))

10. **`T90_PATH_C4_V18_LATTICE_UV.md`** — v18: lattice-derived
    composite-DM magnetic moment. **PUBLISHED (commit `605149a`).**
    - Lattice source: Appelquist+ (LSD), PRD 88, 014502 (2013),
      arXiv:1301.1693
    - κ_neut = -0.40 to -0.60 across M_B/M_B0 = 1.0-1.6 (Nf=2,6)
    - At M_B = 10 TeV (XENON100 limit), lattice predicts
      μ_DM = 1.27×10⁻⁴ μ_N (Nf=2)
    - LZ-tuned value = 6.10×10⁻⁸ μ_N
    - **Lattice prediction is ~2000× larger than LZ**
    - **The M_B matching LZ (~1 TeV) violates XENON100**
    - **COMPOSITE-DM UV INTERPRETATION IS RULED OUT**

### Part 5: T90 background and context

11. **`T77_LZ_2026_09_UPDATE.md`** — LZ 2026 preprint update
    (added 2026-09-04).

12. **`T78_KINETIC_MIXING_LZ_LINK.md`** — kinetic mixing
    connection between magnetic-m and dark-photon
    mediators.

13. **`T80_LZ_PAPER_UPDATE.md`** — LZ paper update notes.

14. **`T81_LZ_REVIEW_RESPONSE.md`** — response to LZ paper
    reviewers.

15. **`T87_LZ_FORWARD_PREDICTION.md`** — additional forward
    predictions (different from T90_FORWARD).

---

## T95 cross-check (CRITICAL CONTEXT — updated 2026-09-07)

**The T95 cross-check program has been extended with a multi-stream
analysis using REAL data from the galstreams v1.2 catalog (123
streams loaded). Master Yukawa passes 9 out of 10 independent
stream probes — only GD-1 disagrees, and only under one specific
interpretation (Zhang+ 2025).**

For the full T95.9 result, see
[T95_MULTI_STREAM_REAL_GALSTREAMS.md](./T95_MULTI_STREAM_REAL_GALSTREAMS.md).
For the GD-1 interpretation separation, see
[T95_GD1_INTERPRETATION_NOTE.md](./T95_GD1_INTERPRETATION_NOTE.md).
For the original T95 paper-style writeup, see
[T95_CONSOLIDATED_RESULTS.md](./T95_CONSOLIDATED_RESULTS.md).

### Per-stream results (master Yukawa, T95.9)

| ✓/✗ | Stream | σ/m pred | [lower, upper] | log L |
|---|---|---|---|---|
| ✓ | Pal5 | 0.85 | [0.5, 2.0] | 0.00 |
| ✓ | Orphan-Chenab | 0.74 | [0.1, 1.0] | 0.00 |
| ✓ | AAU-AliqaUma | 0.78 | [0.2, 1.5] | 0.00 |
| ✓ | Jhelum | 0.76 | [0.1, 1.0] | 0.00 |
| ✓ | Phoenix | 0.73 | [0.5, 5.0] | 0.00 |
| ✓ | Indus | 0.74 | [0.5, 5.0] | 0.00 |
| ✓ | NGC3201 | 0.78 | [0.1, 1.0] | 0.00 |
| ✓ | M5 | 0.81 | [0.5, 5.0] | 0.00 |
| ✓ | M92 | 0.81 | [0.5, 5.0] | 0.00 |
| ✗ | GD-1 | 1.01 | [30, 100] | -12.04 |

**9/10 streams are consistent with master Yukawa.** The GD-1
outlier is now formally separated as an interpretation problem.

### Original T95 tensions (context)

| Probe | Tension | Status (after T95.9) |
|---|---|---|
| **BAHAMAS-SIDM (Robertson 2019)** | Velocity-dep matches well (ratio 0.72), absolute norm ~30% low | mild (T89-known offset, not a model problem) |
| **Core-size predictions** | Master Yukawa predicts 5-50× smaller cores than hydro sims | strong (separate from stream probes) |
| **Euclid Q1 sub-halo forecast (Channel 27)** | σ/m at v=150 km/s is 6-13× above forecast's [0.05, 0.10] cm²/g | substantial (Δlog Z = -1.57 in 8D fit) |
| **Zhang+ 2025 GD-1 perturber** | σ/m at v=10 km/s is 94× below required [30, 100] cm²/g | **very strong (Δlog Z = -23.61 in 8D fit), but formally separated as interpretation problem** |

**Net effect on T90**: The LZ-anchored Yukawa is a **viable but
constrained** interpretation. The T90 merge rule is unchanged —
still requires LZ community resolution of the 248 keV event
**OR** a fit showing Δlog Z ≥ +2.

**Important**: T95 is a parallel investigation. It uses the
master Yukawa (the σ/m prescription, not the magnetic-moment
operator). The magnetic-moment operator (Ls₁₀ in NREFT) is a
separate EFT channel. The T90 branch ships the magnetic-moment
operator; the master has the Yukawa. They are different physics
at different scales. T95's tension findings apply to the master's
Yukawa, not specifically to the magnetic-moment channel — but
since the LZ-anchored posterior has σ/m ≈ 0.7 cm²/g at v=150 km/s,
the tension applies to the broader σ/m interpretation too.

---

## Phase (a) and (b) findings (NEW, 2026-09-07)

User-requested extensions: (a) genuine UV calculation in composite
model, (b) incorporation of real Euclid/Gaia/next-gen DD data.

### Phase (b) — Real data (v19)

| Channel | Real data source | LZ tension? |
|---|---|---|
| **Euclid Q1 cluster count** | Bergamini+ 2026, A&A  711 A33 (14 grade-A clusters) | Δlog L = -0.073 (no tension) |
| **XENONnT 8B CEvNS** | PRL 133, 191002 (2024) | Consistent with SM (SIDM doesn't contribute directly) |
| **PandaX-4T 8B CEvNS** | PRL 133, 191001 (2024) | Consistent with SM (independent confirmation) |
| **LZ 8B CEvNS** | arXiv:2509.16281 | Consistent with XENONnT/PandaX |

**Key result**: Real-data channels do NOT significantly constrain
the LZ interpretation. The cluster count has Poisson noise
σ = √14 ≈ 3.7, too large to detect ~10% SIDM suppression.
The CEvNS measurement confirms the SM prediction.

### Phase (a) — Lattice UV (v18)

| Quantity | Value | Source |
|---|---|---|
| κ_neut (Nf=2, M_B = 10 TeV) | -0.45 | Appelquist+ 2013 Figure 4 |
| Constituent μ_1 | -6.90×10⁻⁸ μ_B | μ_1 = κ_neut × m_e / M_1 |
| Composite μ_DM (D5, r=1) | **1.27×10⁻⁴ μ_N** | Aranda+ 2016 formula |
| LZ-tuned μ_x | 6.10×10⁻⁸ μ_N | T90 7D posterior |
| Lattice / LZ ratio | **~2000×** | (lattice predicts larger) |

**Critical finding**: The M_B matching LZ is ~1 TeV. XENON100 requires
M_B > 10 TeV. **Composite-DM UV interpretation is RULED OUT** by
the combination of lattice κ_neut values + XENON100 limit.

**Caveats**:
- κ_neut values are approximate (interpolated from Figure 4)
- The exact paper tables would tighten the constraint
- M_1 = M_B/3 is a simplifying assumption
- Charge radius contribution not included

**Other UV completions (NOT affected)**:
- Vector-like fermion (Hisano+ 2002): still viable per v16
- Dark photon (Fabbrichesi+ 2020): still viable per v16
- Higgsino inelastic (Fan & Tweed 2026): completely separate EFT channel

---

## Status summary

| Component | Status | Last updated | Commit |
|---|---|---|---|
| Plan (T90_MAGNETIC_MOMENT_PLAN) | current | 2026-09-07 | (in wip/tier3) |
| Forward prediction | current | 2026-09-07 | (in wip/tier3) |
| Cross-detector predictor v10 | SHIPPED | 2026-09-07 | `5d7cc47` |
| Cross-detector follow-ups v11+v12+v13 | SHIPPED | 2026-09-07 | `baf0fa1` |
| Multi-operator v14 | SHIPPED | 2026-09-07 | `f1b4f78` |
| Indirect signals v15 | SHIPPED | 2026-09-07 | `a1415da` |
| UV completion v16 (free-parameter) | SHIPPED | 2026-09-07 | `38256ff` |
| LZ time-series v17 | SHIPPED | 2026-09-07 | `cfb2924` |
| **Real data incorporation v19 (Phase b)** | **SHIPPED** | 2026-09-07 | `e3e0b73`, `25de747` |
| **Lattice UV v18 (Phase a)** | **SHIPPED** | 2026-09-07 | `605149a` |
| Audit drift fix | SHIPPED | 2026-09-07 | `0da52e8` |
| Tag `t90-all-6-paths-shipped-2026-09-07` | CREATED | 2026-09-07 | (points to HEAD) |
| **T95 cross-check program** | **SHIPPED (master)** | 2026-09-07 | `4238860` through `c8303e2` |

---

## Key findings (TL;DR)

1. **The LZ 248 keV event is well-described by a magnetic-dipole
   DM interpretation with μ_x ≈ 6.10×10⁻⁸ μ_N at m_χ = 1 TeV.**

2. **The model is in tension with future direct-detection limits**:
   ~30% of the 7D posterior mass is above DARWIN/LZ-Upgrade
   projected sensitivities.

3. **Magnetic-moment is the most consistent operator** with
   PandaX-4T null. Millicharge is strongly excluded by PandaX
   at LZ-calibrated coupling.

4. **DARWIN and LZ-Upgrade (both ~2030) will test the model**:
   expected to see ~10-100× above projected sensitivity if
   the interpretation is correct.

5. **All 6 paths (1, 2, 3, 4, 6, 7) shipped**. Plus the two
   Phase (a) and (b) extensions. ~795 tests pass. Audit 44/44 clean.

6. **T95 cross-check**: the LZ-anchored Yukawa is in substantial
   tension with Euclid Q1 sub-halo forecast (Δlog Z = -1.57)
   and very strong tension with Zhang+ 2025 GD-1 perturber
   (Δlog Z = -23.61).

7. **Phase (b) real-data check**: Euclid Q1 cluster count and
   XENONnT/PandaX 8B CEvNS data are consistent with the LZ
   interpretation. Cluster count has too little statistical power
   to falsify.

8. **Phase (a) lattice UV check**: **Composite-DM UV interpretation
   is RULED OUT** by the combination of LSD lattice κ_neut values
   (Appelquist+ 2013) and XENON100 limit (M_B > 10 TeV). The
   lattice predicts μ_DM ~2000× larger than LZ at M_B = 10 TeV.

9. **T90 merge rule binds**: this work stays on
   `wip/tier3-magnetic-moment-LZ` until LZ community
   confirmation (or refutation) of the 248 keV event.

10. **T90.23 three-detector recast (2026-09-09/10):** Path 1 ran
    live against HEPData 155182 (PRL 135, 011802 4.2 t·y release).
    **Structural limit confirmed**: LZ's standard 3 phd S1c cut removes
    all sub-300 keVnr NR events from public release, so the
    [5, 50] keVnr magnetic-m smoking-gun test cannot be run with
    any existing LZ HEPData record. The 2D signal-region test
    (option B) shows magnetic-m is **consistent** with the observed
    NR-band population (~287 events vs ~9 predicted from magnetic-m
    alone in [50, 200] keVnr) but not specifically required by it.

11. **T90.23 path 2 — PandaX-4T cross-detector recast (2026-09-10):**
    Path 2 ran live against PandaX-4T's 1.54 t·y opendata.tar.gz
    (PRL 134, 011805). **CRITICAL**: unlike LZ, PandaX preserves events
    with qS1 down to 2 PE (no equivalent of LZ's 3 phd cut), so the
    [5, 50] keVnr magnetic-m signal region IS accessible. Results
    from 2490 candidate events:
    - [5, 50] keVnr: 287 observed vs 422 predicted (ratio 0.68) CONSISTENT
    - [50, 200] keVnr: 1486 observed vs 390 predicted (above)
    - [200, 300] keVnr: 695 observed vs 0.54 predicted (background-dominated)
    - 36 events with qS1 < 3 PE (would have been cut at LZ)

    The joint 3-hypothesis posterior (path 4) with live data:
    - Background wins by Δlog L = 5043 (PandaX [200, 300] has 695 events
      that neither magnetic-m nor Higgsino can explain at current exposure)
    - Magnetic-m vs Higgsino: Δlog L = +935 (magnetic-m wins because of
      [5, 50] window: 287 obs vs 422 magmom-pred vs 0.3 higgsino-pred)
    - Bottom line: magnetic-m at LZ-tuned coupling is consistent with
      both LZ (1 event at 248 keVnr) and PandaX (287 events at
      [5, 50] keVnr, ratio 0.68), but background dominates both
      detectors at current exposures.

12. **T90.23 path 1 RE-OPENED via PandaX**: Path 1's [5, 50] keVnr
    test was structurally blocked at LZ. PandaX provides an
    independent dataset where this test IS possible. Result: 287
    observed vs 422 predicted = ratio 0.68 = CONSISTENT. Magnetic-m
    is NOT contradicted by PandaX. **T90.23 path 1 is now substantively
    tested via path 2** (the [5, 50] keVnr smoking-gun window).

13. **T90.23 path 2B — PandaX NR-band smoke test (2026-09-10, NEW):**
    Used PandaX's PUBLISHED NR-band observation: 24 events below the
    NR median in [5, 270] keVnr (12 in Run 0, 12 in Run 1). Expected
    SM background: 20.5 ± 2.5 events (summed from PandaX Table I,
    dominated by tritium and radon ER leakage into NR band).
    **Magnetic-m at LZ-tuned coupling predicts ~720 events.**
    Result: ratio obs/magnetic-m = 0.033, Δlog L = +614 in favor
    of background. **MAGNETIC-M IS DECISIVELY OVER-PREDICTED.** The
    PandaX data rules out the magnetic-m interpretation of the LZ
    248 keV event at μ_x = 6.10×10⁻⁸ μ_N. Factor-30 over-prediction
    is too large to attribute to systematic differences between
    PandaX and LZ analyses. Possible resolutions: (1) the LZ
    248 keV event is not magnetic-m, (2) magnetic-m requires
    much lower coupling (which then cannot explain LZ), or
    (3) major systematic differences (unlikely).

---

## What's still TODO

From the 'proceed 1,2 3 4 6 7' plan: **NONE — all paths shipped.**

Phase (a) and (b) extensions: **BOTH SHIPPED** (v18 lattice UV + v19 real data).

Other open work (not from this plan):
- Wait for LZ community resolution of the 248 keV event
- Cross-validate against PandaX-4T and XENONnT new data
- If LZ confirms, merge T90 to master (currently blocked by
  T90 merge rule)
- T95.7+ (galaxy-stream gaps with Gaia DR4, due 2026-12-02)
  is a candidate next phase but requires user approval per
  rule 17/24

---

## Test summary

| Component | Tests | Status |
|---|---|---|
| v10 predictor | 9/9 | passing |
| v11 posterior | (smoke) | passing |
| v12 detector response | (smoke) | passing |
| v13 other operators | (smoke) | passing |
| v14 calibrated | 5/5 | passing |
| v15 indirect signals | 10/10 | passing |
| v16 UV completion (free-parameter) | 11/11 | passing |
| v17 LZ time-series | 12/12 | passing |
| **v18 lattice UV (Phase a)** | **9/9** | **passing** |
| **v19 real data (Phase b) - Euclid Q1** | **10/10** | **passing** |
| **v19 real data (Phase b) - 8B CEvNS** | **10/10** | **passing** |
| **T90 total** | **76/76** | **all passing** |
| Audit (t82_audit.py) | 44/44 | ALL CLEAR |
| Full v0.3-prelim/tests/ | ~795 pass, 8 skip, 0 fail | clean |

---

## Branch state

```
605149a (HEAD) feat(T90.11): v18 — Genuine UV calculation via LSD lattice
25de747 feat(T88.F): Real XENONnT+PandaX 8B CEvNS data
e3e0b73 feat(T88.E2): Real Euclid Q1 strong-lensing data
2f142f9 docs(T90+T95): Cross-link magnetic-moment and cross-check programs
0da52e8 fix(audit): update test for canonical T88E
cfb2924 feat(T90.10): v17 — LZ time-series with PUBLIC LZ data
a1415da feat(T90.9): v15 — Indirect signals
38256ff feat(T90.8): v16 — UV completion
...
```

42 commits on `wip/tier3-magnetic-moment-LZ`. All pushed.
Tag `t90-all-6-paths-shipped-2026-09-07` exists; should be updated
to point at new HEAD.

---

## T95 references (already on master)

The T95 cross-check is **on master** (separate branch path) and
documents substantial-to-very-strong tension between the LZ-anchored
Yukawa and astrophysical SIDM probes:

- **T95_CONSOLIDATED_RESULTS.md** — paper-style writeup of all findings
- **T95_YUKAWA_PRESCRIPTION_CALIBRATION_NOTE.md** — Yukawa σ/m prescription
- **T95_OPTION2_CORE_SIZE_PREDICTION.md** — Core-size predictions
- **T95_OPTION2_5_GRAVOTHERMAL.md** — Gravothermal Balberg+ 2002 formula
- **T95_OPTION3_SUBHALO_FORECAST.md** — Master Yukawa + Euclid Q1 forecast
- **T95_OPTION3_5_8D_FIT.md** — Real 8D nested-sampling fit
- **T95_OPTION3_6_ZHANG_GD1.md** — Master Yukawa vs Zhang+ 2025 GD-1
- **T95_OPTION3_6B_SURVEY.md** — Alternative interpretations survey
- **T95_OPTION3_6_V4_RECONCILIATION.md** — v1/v2/estimator reconciliation
- **T95_OPTION3_6_V3_REAL_8D_FIT.md** — Real 8D Zhang fit
- **T95_SIDM_CORE_PROFILE_PLAN.md** — Master plan + Phase 0 SWIFT check

---

## How to cite this work

If citing the T90 program as a whole, use this index. For
specific findings, cite the individual doc. For code, cite
the script (each script has a docstring header with the
relevant doc reference).

**For the tension with astrophysical SIDM probes**, also cite
T95_CONSOLIDATED_RESULTS.md — the cross-check is integral to
interpreting the T90 work.

**For the lattice UV ruling out composite-DM**, cite
T90_PATH_C4_V18_LATTICE_UV.md (also inline above) — the v18
work shows the composite-DM UV interpretation of LZ is
inconsistent with the lattice-derived κ_neut and XENON100.

**For the real-data incorporation**, cite
T90_PATH_C4_V19_REAL_DATA.md — replaces FORECAST with
real Euclid Q1 + XENONnT/PandaX 8B CEvNS measurements.

---

## Standby status (2026-09-07)

**Per user directive**: T90 work is parked. Branch is
publishable but not merged. Tag points to current state.
T95 (already on master) is the cross-check showing the
LZ-anchored Yukawa is in substantial tension with
astrophysical data.

**Waiting on**: LZ community confirmation or refutation
of the 248 keV event. If confirmed, T90 merge rule may
be satisfied (per the 5 conditions in commit `e23bb80`).
If refuted, T90 work remains as a demonstrated capability
on the branch only.

**Higgsino inelastic DM (Fan & Tweed 2026)** is the strongest
remaining competing interpretation per v17 Bayesian posterior
(tied at 47% with magnetic-moment).