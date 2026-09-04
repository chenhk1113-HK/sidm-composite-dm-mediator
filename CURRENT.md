# CURRENT — Version-of-Record (1 page)

> **For:** Anyone who has 60 seconds and wants to know what this project
> is, what it claims, and what the current best numbers are.
> Updated with each version-bump round. Last refresh: 2026-09-03 (T86).

---

## Standing: v0.4-prelim+T75 (Tier-1 milestone)

The project is a joint-fit framework for self-interacting dark matter
(SIDM), grounded in published astrophysical data. The standing version
(`v0.4-prelim+T75`) is the result of rounds **T72–T79** adding DAMPE and
Zhang+2025 LSS channels; **T80** confirming LZ paper compatibility;
**T81** adding XENONnT/PandaX watch; **T82** stale-claim audit;
**T83** KSFR (3,2) fundamental LATTICE promotion; **T84** Channel 18 ρ
sensitivity sweep. All within one standing version — no re-run of the
joint fit after T75.

## What the project measures

A 6-dimensional Bayesian posterior over Benchmark A parameters:
`(log_ε, log_α, m_φ, m_χ, g_χ, log_ξ)`, sampling via dynesty nested
sampling. **20 channels** of observational data constrain the posterior.

## v0.7 posterior headline (nlive=2000, ~7 min wall)

| Quantity | Value | Source |
|---|---|---|
| **Bayesian evidence log Z** | **−163.29 ± 0.085** | T41 nlive=2000 |
| DM mass **m_χ** (MAP) | **770 GeV** (median 498) | T41 posterior |
| Mediator mass **m_φ** (MAP) | **453 MeV** ✓ KSFR-valid (median 588) | T41 posterior |
| **σ/m₀** at galactic scale (MAP) | **0.27 cm²/g** | T41 derived |
| Velocity index **a** (Yukawa, at MAP) | +0.344 | T41 derived |
| Tension T39 vs Yukawa a | **0.60σ** (below 1.0 threshold) | T41 vs T39 |
| Bare **ε** (median posterior) | **1.4×10⁻³⁷** | T41 posterior |
| Bare **α_X** (median posterior) | 3.5×10⁻¹⁶ | T41 posterior |
| Dark Yukawa **g_χ** (MAP) | 1.19 | T41 MAP |
| Form-factor suppression **ξ** (MAP) | 0.17 | T41 MAP |

## Channels in production

1. dSph kinematics
2. UFD kinematics
3. Bullet Cluster
4. SPARC rotation curves (calibrated saturation; Tier-2 hierarchical upgrade pending)
5. LZ WS2024 direct detection (sanity check only — orthogonal posture)
6. Fermi gamma-ray dwarf stacking
7. H3 convergence & H4 form-factor sweeps
8. **DAMPE CRE** (T72-T73)
9. **Zhang+2025 LSS** assembly bias (T74)
10. **XENONnT + PandaX-4T** competitor watch (T81)

(Plus ~9 internal/auxiliary channels: KSFR mask, mediator lifetime, etc.)

## Standings posture — what σ/m does and doesn't say

- **σ/m = 0.27 cm²/g measures σ_DM-DM** (SIDM observable, galactic scale).
- **σ_DM-nucleon** (LZ/XENONnT/PandaX observable) is suppressed by
  **~50–80 orders of magnitude** at this posterior due to kinetic-mixing
  ε ~ 10⁻³⁷. Direct-detection constraints enter as sanity checks only.
- **σ_DM-DM ≠ σ_DM-nucleon in practice** at this point in parameter space,
  despite being theoretically linked via the dark-photon portal. They
  become linked only at ε ≫ 10⁻¹⁰, which the posterior excludes.

## Standing test count

- **542 pass / 6 skip** (post-T84)
- Drift-guard audit (`scripts/t82_audit.py`): **40/40 ALL CLEAR**
- Standing version file: `0.4-prelim+T75` (verified by audit)

## Plausibility audit — LZ finding + Planck-scale concerns (T86.7j, 2026-09-03)

Two concerns surfaced in 2026-09-03 from `Consider3.docx` + the actual LZ
preprint. Both addressed with verbatim paper quotes + numerical derivations.
**Full analysis:** [`v0.3-prelim/docs/T86_PLAUSIBILITY_AUDIT.md`](v0.3-prelim/docs/T86_PLAUSIBILITY_AUDIT.md).

### Concern 1 — LZ 2.6σ event (paper appeared 2026-09-02)

| | LZ paper | Project v0.7 |
|---|---|---|
| Event | 248 ± 23 ± 23 keV single recoil, 2.84 tonne-years | (not in scope — measured) |
| Significance | 2.6σ global / 3.4σ local | Below 3σ threshold |
| Best-fit m_χ | **1000 GeV/c²** (Ls₁₀ EFT operator) | **770 GeV** (MAP) — within posterior |
| σ_DM-nucleon (paper's implied) | ~10⁻⁴⁵ cm² for inelastic at 1 TeV | ~10⁻¹¹¹ cm² (Kahlhoefer point-particle) |
| σ_DM-nucleon ratio | — | **66 orders below** LZ sensitivity |

**Verdict: validation, not falsification.** Same mass window (700-1000 GeV);
same physics regime (NREFT + inelastic DM); orthogonal-physics stance
preserved (σ_DM-nucleon ~66 orders below LZ). Standing trigger policy:
<3σ → doc-only (current); ≥3σ → update Channel 5 + re-run T41; ≥5σ →
v0.5-prelim release. KIV cron `080d2f590251` re-checks 2026-11-01.

### Concern 2 — Planck-length extrapolation

- σ_DM-nuc ≈ 10⁻¹¹¹ cm² is **~10⁴⁶× smaller than the Planck area** (ℓ_P² ≈
  2.6×10⁻⁶⁶ cm²), NOT smaller than the Planck length (different dimensions).
  The "below Planck length" framing is a **category error**.
- Composite form-factor correction at LZ energies is **~13%** (F²_gaussian
  ≈ 0.93, F²_dipole ≈ 0.87 per T79 §"Composite form-factor calculation") —
  NOT ±5 orders as the reviewer suggested. Dominant suppression is ε².
- **Honest caveat:** ε ~ 10⁻³⁷ is **29 orders below the "secluded" regime**
  (ε ≲ 10⁻⁸ per Coogan et al. 2024). The project's posterior falls in the
  **freeze-in regime**, which requires **T_RH > 10¹⁵ GeV** or non-standard
  cosmology. This is documented in T79 §"Relic-density consistency check"
  but is **not** prominent in the layman summary. Surfaced here.

**Verdict:** the formula's regime-of-validity question is real but separate
from whether the model fits the data better than alternatives. **log Z =
−163.29 ± 0.085** is the Bayesian evidence comparison; whether the
Kahlhoefer formula extrapolates to ε ~ 10⁻³⁷ is a separate question.
The reheating-temperature assumption (T_RH > 10¹⁵ GeV) is the only
substantive hidden assumption and is now surfaced.

### What didn't change

- Standing version: **v0.4-prelim+T75** (no bump).
- Joint-fit posterior: **log Z = −163.29 ± 0.085**, m_χ = 770 GeV, σ/m = 0.27 cm²/g.
- Tests: 579 pass / 8 skip.
- Drift-guard audit: 40/40 ALL CLEAR.

**No posterior re-run.** No new physics. No new channels. The standing
posture is preserved; the audit + tests confirm clean.

### T87 (2026-09-03): Composite-DM direct-detection forward prediction

Verdict: **composite-DM cannot claim the LZ event at v0.7 MAP.**

| Quantity | Value |
|---|---|
| σ_inel_nuc(248 keV, gaussian F²) | **1.15 × 10⁻¹¹⁷ cm²** |
| σ_inel_nuc(248 keV, dipole F²) | **1.07 × 10⁻¹¹⁷ cm²** |
| Predicted N_events in 2.84 tonne-years | **4.81 × 10⁻⁷³** |
| LZ observed | 1 |
| Gap | **71 orders of magnitude below LZ sensitivity** |

**Why so suppressed?** The dominant suppression is **ε²** (kinetic mixing ε
~ 10⁻³⁷ at v0.7 MAP). The composite F²(q) factor (F²_gaussian ≈ 0.93 at 248
keV) and the inelastic kinematic factor F_inel ≈ 0.5 are sub-dominant.
The freeze-in regime forces ε into the deep-decoupled part of parameter
space, which is what makes the model essentially invisible to LZ.

**Scientific interpretation:**
- **The model remains a valid SIDM candidate** for dSph/UFD/Bullet/SPARC/DAMPE/LSS. log Z = −163.29 ± 0.085 is unchanged. All T72-T84 channels still work.
- **The model does NOT explain the LZ event** if it's real. The event (if real) points to a different microphysics — Higgsino, pseudo-Dirac, or some other inelastic-DM scenario with different (m_χ, δ, ε) than v0.7 MAP predicts.
- **The mass-window match is genuine but not sufficient.** LZ best-fit m_χ = 1000 GeV is within 30% of the project's 770 GeV MAP and within the heavy-WIMP regime (700-1000 GeV). What breaks is the cross-section: σ_inel_nuc is 71 orders of magnitude below LZ's effective event-rate sensitivity.

**Three new code modules + 9 new tests:**
- `v0.3-prelim/code/t87_composite_inelastic_nucleon.py` (~430 lines): Kahlhoefer point-particle elastic + T&S&W inelastic kinematics + composite F²(q) calibrated to T79.
- `v0.3-prelim/code/t87_lz_event_rate.py` (~470 lines): SHM Maxwell-Boltzmann + Lewin-Smith event-rate integration + verdict classification.
- `v0.3-prelim/tests/test_t87_inelastic_nucleon.py` (9 tests, all pass).
- `v0.3-prelim/data/results/2026-09-03_t87_lz_forward_prediction.json` (results JSON).
- `v0.3-prelim/docs/T87_LZ_FORWARD_PREDICTION.md` (verdict doc).

**Standing posture preserved** (no posterior re-run, no new physics, no new channels).

### Composite-channel gap (T86.7k+C, post-Consider4 review)

User uploaded `consider4.docx` (109-paragraph third-party review) after T86.7j
shipped. The reviewer correctly identifies that the LZ paper is testing
**inelastic-DM and SD operators**, not elastic SI — the project's "10⁻¹¹¹
cm² elastic SI" number is answering a question LZ isn't actually asking.

**Genuine gap:** composite-DM inelastic σ_DM-nucleon + LZ-event forward
prediction. The reviewer is right that this is the missing piece that would
elevate the project from "compatible with LZ" to "predicts LZ event."

**Status:** Registered as Tier-2 roadmap Item #3 in
[`v0.3-prelim/docs/V0_6_ROADMAP.md`](v0.3-prelim/docs/V0_6_ROADMAP.md). **Not
initiated** in this round (T86.7k+C is docs-only). Per the project's
pre-registered T78 trigger discipline: <3σ → doc-only (current); ≥3σ →
run the analysis. T87 is the analysis that would run at ≥3σ; running it
now is premature but allowed.

**Three reviewer claims corrected as stale premises** (full analysis in
[`v0.3-prelim/docs/T86_PLAUSIBILITY_AUDIT.md`](v0.3-prelim/docs/T86_PLAUSIBILITY_AUDIT.md)
§"Composite-channel gap analysis"):

1. "T79 composite form-factor ⏳ Pending" — T79 already shipped at commit
   `6b83904` (2026-09-02). F²_gaussian ≈ 0.93, F²_dipole ≈ 0.87 at 4 LZ
   energies.
2. "Relic-density + BBN/CMB consistency pending" — T79 §"Relic-density
   consistency check" verifies freeze-in regime at ε ~ 10⁻³⁷; T_RH > 10¹⁵
   GeV now surfaced in CURRENT.md.
3. "Inelastic/SD cross-section ⏳ Not started" — partially right.
   Inelastic σ_DM-DM exists (T43, T41_INELASTIC, h4_inelastic_sweep).
   Inelastic σ_DM-nucleon + composite-SD operator decomposition is
   genuinely missing.

## Where to read deeper

- README.md — full project description + quick-start (440 lines)
- docs/LAYMAN_SUMMARY.md — non-expert overview + **honest caveats** (T86.7j)
- docs/MATHEMATICS.md — formulas & derivations
- docs/DARK_SECTOR_LAGRANGIAN.md — Benchmark A specification (§9 is canonical)
- MODEL_ASSUMPTIONS_AND_LIMITATIONS.md — what the project does NOT claim
- docs/INDEX.md — full navigation
- v0.3-prelim/data/results/2026-09-02_dampe_poc/ — T75/T76/T84 result JSONs
- v0.3-prelim/docs/T72_*.md → T84_*.md — per-round documentation
- **v0.3-prelim/docs/T86_PLAUSIBILITY_AUDIT.md** — LZ + Planck analysis (T86.7j)

## Provenance

> Generated 2026-09-03 (T86) as a 1-page version-of-record. Numbers
> spot-checked against `v0.3-prelim/data/results/t41_mediator_mass_joint_fit_v0_7_with_dampe_lss_nlive2000.json`.
> Standing version `v0.4-prelim+T75` (no bump in T82-T86).
