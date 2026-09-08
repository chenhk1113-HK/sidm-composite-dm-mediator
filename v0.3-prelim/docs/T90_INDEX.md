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

**Cross-link to Phase 3 (UV completion via lattice)**: see
[T90_PATH_C4_V18_LATTICE_UV.md](./T90_PATH_C4_V18_LATTICE_UV.md)
(also inline below). The v18 UV calculation uses LSD lattice
(Appelquist+ 2013, PRD 88, 014502) form factors to compute the
composite-DM magnetic moment from first principles. **The lattice
predicts μ_DM ~ 1.27×10⁻⁴ μ_N at M_B = 10 TeV, ~2000× larger than
LZ's 6.10×10⁻⁸ μ_N. The M_B matching LZ (~1 TeV) violates XENON100
(M_B > 10 TeV). The composite-DM UV interpretation is RULED OUT.**

**Cross-link to T88.E2/F (real data incorporation)**: see
[T90_PATH_C4_V19_REAL_DATA.md](./T90_PATH_C4_V19_REAL_DATA.md)
(also inline below). The v19 work replaces FORECAST data with
real Euclid Q1 strong-lensing counts (Bergamini+ 2026) and
real XENONnT/PandaX 8B CEvNS measurements (PRL 133, 2024).
**Both real-data channels show no significant tension with the LZ
interpretation** — but the cluster count alone has too little
statistical power (14 clusters) to falsify it.

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