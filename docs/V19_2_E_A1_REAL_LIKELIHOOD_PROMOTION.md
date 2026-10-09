# V19.2-E A.1 — Real-Likelihood Promotion (Phase 44 v2)

**Date:** 2026-10-09
**Status:** COMPLETED
**Author:** Hermes (per ClawsGO comment #5 B.4)
**Tag:** supersedes v19.2-D Phase 44 v1 hand-set 3-channel likelihood

## What this is

Phase 44 v1 (`phase44_joint_fit.py`) used a 3-channel hand-set Gaussian
likelihood (SPARC, JVAS, Cloud-9) to produce a +8.10 log-unit improvement
over the T90.70 baseline. The pass/fail table at v19.2-D-R88(80) was
**"4 of 7 constrained channels pass"** under this hand-set likelihood.

Phase 44 v2 (`phase44_joint_fit_v2_real_likelihood.py`) replaces the
3-channel hand-set Gaussian with the **8-channel T205 published-σ_unc
likelihood** (Horigome+ 2025, Lelli+ 2016, BLN24/Ohana+ 2026, Randall+
2008 — all with the actual published error budgets).

The pass/fail table is now **measured** from real published error
budgets, not **chosen** by hand.

## Key change: result

| Setup | Channels | PASS | MARGINAL | FAIL | Headline |
|---|---|---|---|---|---|
| Phase 44 v1 (3-channel hand-set Gaussian) | 3 | — | — | — | "+8.10 log-unit improvement" |
| Phase 44 v1 (3-channel) under paper's canonical σ/m(v) at f_H=0.297 | 8 | 1 | 0 | 7 | "1 of 8 channels pass" |
| T205 (8-channel published σ_unc, full dynesty) | 8 | — | — | — | log Z = -14.285, BF = 11.15 |

The canonical Gaussian σ/m(v) (per `scripts/constants.py` Phase 44 free
fit: σ_0=0.052, a_slope=1.93, σ_peak=174, v_target=29.4, σ₁=4.4, f_H=0.297)
gives **1 of 8 channels PASS at the published-σ_unc likelihood**:
- Cluster (v=500) PASS (σ_eff=2.05×10⁻⁴ < ceiling 2.5×10⁻⁴)
- Cloud-9 (v=28) **FAIL** — σ_eff=14.64 < floor 128
- SPARC (v=100) **FAIL** — σ_eff=0.0046 < observation 0.193
- dSph (v=15) **FAIL** — σ_eff=0.251 > ceiling 0.032 (factor 7.8× over)
- UFD v=10 **FAIL** — σ_eff=0.391 > ceiling 0.047 (factor 8.3× over)
- UFD v=7 **FAIL** — σ_eff=0.777 > ceiling 0.067 (factor 11.6× over)
- UFD v=5 **FAIL** — σ_eff=1.488 > ceiling 0.093 (factor 16.0× over)
- UFD v=3 **FAIL** — σ_eff=3.987 > ceiling 0.155 (factor 25.7× over)

The 5 Horigome+ 2025 dSph/UFD ceiling constraints at v=3, 5, 7, 10, 15
are all **catastrophically violated** (factor 8-26× over the published
ceiling). This is the §2.6a Cloud-9 vs dSph no-go, **quantified with
real published σ_unc**.

## What the v1 result was hiding

The Phase 44 v1 3-channel hand-set Gaussian likelihood only included:
1. **SPARC** at v=100, with σ_eff target ~ 0.07 cm²/g (hand-picked)
2. **JVAS** at v=15, with σ/m target ~ 100 cm²/g (hand-picked; observational-interpretation, not measurement)
3. **Cloud-9** at v=28, with σ/m target ~ 100 cm²/g (hand-picked)

It did **NOT** include the 5 Horigome+ 2025 dSph/UFD ceiling
constraints at v=3, 5, 7, 10, 15. These constraints are the
**observational data** that the framework most needs to satisfy, and
the framework fails them by factor 8-26× at the canonical Phase 44
parameter point.

The +8.10 log-unit improvement was real for the 3 channels it
included, but it was hiding the failure of the 5 channels it excluded.

## Why this matters (ClawsGO B.4 verdict)

> "Real likelihood. The SPARC χ² pipeline (phase41/43) and a Horigome
> velocity-dependent likelihood exist. Promote them to the comparison
> statistic and retire the 3-anchor hand-set Gaussian. This is the
> single biggest credibility upgrade — it turns the pass/fail table
> from 'chosen' into 'measured'."

The promotion is done. The result is honest: **1 of 8 channels pass**
at the canonical Phase 44 free fit. This is a much weaker scientific
claim than the v1 "4 of 7 channels pass" framing, but it is the
**correct** claim — it includes the Horigome+ 2025 dSph/UFD ceiling
constraints and the Cloud-9 v=28 floor.

## Method

1. Load `constants.py` Phase 44 free-fit values: σ_0=0.052, a_slope=1.93,
   σ_peak=174, v_target=29.4, σ₁=4.4, f_H=0.297
2. For each of 8 T205 channels (v=3, 5, 7, 10, 15, 28, 100, 500):
   - Compute σ_HH(v) using the canonical Gaussian form
   - Compute σ_eff = f_H² × σ_HH(v) with canonical f_H=0.297
   - Compare σ_eff to σ_obs with published σ_unc
   - PASS / MARGINAL / FAIL per T205 convention (gaussian / ceiling / floor)
3. Save per-channel pass/fail to
   `v0.3-prelim/data/results/phase44_joint_fit_v2_real_likelihood.json`

## Honest limitations

1. **T205's OBS_PUBLISHED splits the Horigome+ 2025 combined sample
   across 5 v bins.** T205 itself flags this as a limitation
   (treating them as independent channels over-counts the effective
   constraint). The 5 dSph/UFD channels are not 5 independent
   observations — they are 5 velocity bins of a single Horigome+ 2025
   analysis. The effective number of constraints is closer to 1, not 5.

2. **The σ_eff = f_H² × σ/m formula uses a single f_H=0.297 across all
   velocities** (per constants.py + paper §2.6). The project does
   NOT have a first-principles f_H derivation at Phase 44 parameters
   (R88(88) caveat). The f_H=0.297 is the Phase G7 phenomenological
   fit, not a Yang+ 2025 SIDM2c prediction. With f_H=1.0 (Phase G9
   flat f_H), the pass/fail table does not change qualitatively — the
   dSph/UFD channels still FAIL because the σ_HH tail at v=3-15 is
   still too large.

3. **T205's v²-space Lorentzian ansatz vs paper's Gaussian form.**
   T205 uses a v²-space Lorentzian Breit-Wigner with 4 resonances and
   15 free parameters; this script uses the paper's canonical Gaussian
   form (single resonance, σ_peak=174, σ₁=4.4). The T205 model A
   full dynesty result (log Z = -14.285) was found by T205's
   parameterization, not the paper's. The paper's Gaussian form is
   what the paper's headline numbers use (σ/m(15)=2.85, σ/m(28)=166).

## What this changes in the paper

Per R88 v19.2-D-FREEZE, the paper's "framework score" was:
- 4 PASS / 3 MARGINAL / 1 MARGINAL-FAIL / 2 unconstrained placeholders / 1 not tested
- Headline: "4 of 7 constrained channels pass" (with caveat that Lei/Wang
  and Sameie+ 2020 are MARGINAL/FAIL by R88(87) tuning statement)

With this v19.2-E A.1 promotion:
- 1 PASS (Cluster only) / 0 MARGINAL / 7 FAIL out of 8 Horigome+ SPARC+Cloud-9+Randall channels
- 1 of 8 channels pass

The 4-of-7 framing included JVAS and the Lei/Wang and Sameie+ channels
which are not in the T205 published-σ_unc set. The 1-of-8 framing
includes only channels with real published σ_unc. The two framings
are answering different questions:
- v1 4-of-7: "How many of the channels we *chose to test* does the
  model pass under hand-set Gaussian widths?"
- v2 1-of-8: "How many of the channels with *real published σ_unc* does
  the model pass?"

The v2 framing is the right one for the headline.

## Next steps (V19.2-E roadmap)

- A.2 (next): re-run Phase 44 free fit with the 8-channel T205
  published-σ_unc likelihood, not the 3-channel hand-set Gaussian.
  Find the best-fit that maximizes the *measured* pass/fail, not
  the *chosen* one. This may give a different best-fit parameter
  point with a better published-σ_unc pass/fail.
- B: per-halo gravothermal calibration (Fornax, Segue 1)
- C: σ/m(v) data-only constraint analysis (MCMC over σ/m at 5-10
  velocity bins using the wired real likelihood)
- D: machine-generated canonical numbers from constants.py + this
  script

## Files

- `v0.3-prelim/code/phase44_joint_fit_v2_real_likelihood.py` — new
  script, 10.3 KB
- `v0.3-prelim/data/results/phase44_joint_fit_v2_real_likelihood.json` —
  output, per-channel pass/fail at canonical Gaussian σ/m(v)
- `v0.3-prelim/data/results/phase44_joint_fit.json` — v1 hand-set result
  (preserved for diff)

## Reference

- ClawsGO comment #5 (2026-10-09), Part B.4
- T205_full_likelihood_published.py — 8-channel published-σ_unc
  likelihood (already exists, was not wired into the headline)
- precompute_sparc_hierarchical.py — 175-galaxy SPARC hierarchical
  per-galaxy likelihood (already exists, not yet wired)
- Paper §2.6 — canonical Gaussian σ/m(v) form
- Paper §A.15 — canonical channel table (R88(82) added)
