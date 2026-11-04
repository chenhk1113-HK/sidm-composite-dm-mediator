# High-σ Cloud-9 formation-timing recheck (2026-11-03)

**Trigger:** arXiv:2610.28890 (van den Bosch & Tokayer, accepted MNRAS) calibration caveat adopted 2026-11-03: the LMFP collapse-time family (Yang+ 2024 eq 2.2, used by project reference [43] and `gravothermal_yang2024.py`) underestimates late-time collapse once the core is optically thick. Open item: does this affect the Cloud-9 / M94 RELHIC anchor (sigma ~ 174 cm2/g at 29.4 km/s)?

**Method:** pure recompute with the project's own module (`v0.3-prelim/code/gravothermal_yang2024.py`, functions `collapse_time_SI_gyr`, `collapse_time_calibrated_gyr`, `collapse_time_gyr`, `f_rho_s_over_rho_s0`, `f_rc_over_rs0`, `rho_sidm`, canonical Gaussian sigma form with constants from `scripts/constants.py`: SIGMA_0=0.052, A_SLOPE=1.93, V_REF=100, SIGMA_PEAK=174, V_TARGET=29.4, width=4.4). Optical thickness criterion: mean free path lambda = 1/(rho_core x sigma/m) < r_core, evaluated on the parametric beta=4 profile at r = r_c. Script: `scripts/recheck_cloud9_highsigma_20261103.py` (committed; run with C:/Python314/python.exe). ASCII notation throughout.

## 1. Canonical sigma at Cloud-9 velocities

sigma(15) = 2.85 | sigma(21) = 29.2 | sigma(28) = 166.0 | sigma(29.4) = 174.6 | sigma(36) = 56.9 cm2/g.

Re-baseline note applies: Cloud-9 gas sigma_v = 5.1 km/s is NOT the DM velocity; the NFW DM velocities are V_max ~ 31-36 km/s and DM 1D dispersion ~21 km/s (CLOUD9_REBASELINE.md). Which velocity "counts" changes the applicable sigma by a factor 6 (29 vs 166-174). This recheck brackets all three.

## 2. Collapse-time and optical-thickness results

Halo versions: Cloud9-legacy (5e9 Msun, V31.12, r_s 1.4; rho_s0 = 3.87e7 Msun/kpc3), Cloud9-rebaseline (5e9, V36, r_s 1.85; rho_s0 = 2.95e7), Fornax-control (1e9, V18, r_s 1.0; rho_s0 = 2.54e7). Evolution duration used: **9.38 Gyr** for Cloud-9-class halos (z_f = 1.5116 via eq 3.1; t_L = 9.38 Gyr, closed form and numerical integration agreeing to <0.001 Gyr — see sec 4; the module's old 40.66 Gyr was a bug). Fornax: z_f = 1.5786, duration 9.54 Gyr.

| sigma_eff | t_c lit | t_c cal (x1.82) | tau* reached at (cal) | tau_natural = duration/t_c_cal |
|---|---|---|---|---|
| Cloud9, 174 | 1.22-1.39 Gyr | 2.22-2.52 Gyr | 3.0-3.5 Gyr | 3.7-4.2 |
| Cloud9, 166 | 1.28-1.45 | 2.33-2.64 | 3.2-3.6 Gyr | 3.6-4.0 |
| Cloud9, 50  | 4.26-4.82 | 7.74-8.77 | 10.6-12.0 Gyr | 1.1-1.2 |
| Cloud9, 7   | 30.4-34.4 | 55.3-62.7 | 76-86 Gyr (never) | 0.15-0.17 |
| Fornax, 7   | 80.1 | 145.8 | 199.8 Gyr (never) | 0.07 |

The dwarf-scale control (Fornax, sigma ~ 7) stays shallow (tau_natural 0.07) and fully optically thin — the van den Bosch caveat does NOT touch the dwarf-scale results, consistent with the 2026-11-03 Tier-1 adjudication.

**Column validity (2026-11-04):** the `tau* reached at (cal)` column above was computed with `rho_sidm` while it was still inverted (sec 7) and is superseded by sec 3. The `t_c lit`, `t_c cal` and `tau_natural` columns are independent of the density profile and remain valid.

## 3. Optical-thickness onset — CORRECTED 2026-11-04

> **SUPERSEDED (2026-11-04).** The original section 3 stated **tau* = 1.37 in every arm** and that
> "Cloud-9 is still OPTICALLY THIN at tau = 1 (lambda 0.54-17.5 kpc vs r_c 0.15-0.20 kpc)". Both were
> wrong, for two independent reasons: (i) the core densities came from `rho_sidm` while it was
> inverted relative to arXiv:2305.16176 eq. 2.1 (sec 7), which understated rho(r = r_c) by 12.7x
> at the tau = 1 Cloud9-legacy state (5.125e7 instead of 6.511e8 Msun/kpc3) — exactly what made the arm
> look optically thin (lambda/r_c = 3.575 rather than 0.281); and (ii) tau* = 1.37 lies OUTSIDE the range where the eq. 2.3
> fitting functions are physical at all (sec 3b). Re-derived below with the corrected profile.

**3a. Corrected recompute** (`scripts/recheck_cloud9_highsigma_20261103.py`, re-run 2026-11-04 after the eq. 2.1 fix; identical constants; Cloud9-legacy arm, rho_s0 = 3.8666e7 Msun/kpc3, r_s0 = 1.4 kpc, r_c(tau) = r_s0 f_rc(tau)):

| sigma_eff | tau | r_c (kpc) | rho(r_c) Msun/kpc3 | lambda(r_c) kpc | lambda/r_c | rho(0) Msun/kpc3 | lambda(0)/r_c | state |
|---|---|---|---|---|---|---|---|---|
| 174 | 0.01 | 0.3071 | 1.180e8 | 0.2333 | 0.760 | 2.169e8 | 0.413 | THICK |
| 174 | 0.10 | 0.6506 | 3.979e7 | 0.6916 | 1.063 | 1.179e8 | 0.359 | marginal |
| 174 | 0.30 | 0.6541 | 4.115e7 | 0.6687 | 1.022 | 1.293e8 | 0.325 | marginal |
| 174 | 0.50 | 0.5261 | 6.356e7 | 0.4329 | 0.823 | 1.775e8 | 0.295 | THICK |
| 174 | 1.00 | 0.1502 | 6.511e8 | 0.0423 | 0.281 | 1.183e9 | 0.155 | THICK |
| 166 | 1.00 | 0.1502 | 6.511e8 | 0.0443 | 0.295 | 1.183e9 | 0.162 | THICK |
| 50  | 1.00 | 0.1502 | 6.511e8 | 0.1471 | 0.979 | 1.183e9 | 0.539 | marginal/THICK |
| 7   | 1.00 | 0.1502 | 6.511e8 | 1.0505 | 6.99  | 1.183e9 | 3.85  | thin |
| 7 (Fornax) | 1.00 | 0.1073 | 4.27e8 | 1.6021 | 14.93 | — | — | thin |

Reading: **the optical-depth statement is not a single crossing time.** On the `lambda < r_c` criterion the Cloud-9 arm at sigma 166-174 is THICK at tau = 0.01, marginally THIN (ratio 1.02-1.06) in the narrow tau ~ 0.1-0.3 window where f_rc peaks, and THICK again from tau ~ 0.4 onward, reaching lambda/r_c = 0.28 at the tau = 1 truncation. On the stricter central-density criterion (lambda(0)/r_c) it is THICK at every tau > 0 probed (0.16-0.41). At sigma = 7 (dwarf anchors) the halo is thin by a factor 7-15 at tau = 1 and never approaches the transition within any lifetime.

**3b. The eq. 2.3/2.4 fits have a hard validity ceiling near tau ~ 1.3 (NEW, measured 2026-11-04).** The fitting polynomials turn unphysical just past tau = 1.2:

| tau | f_rho_s | f_r_s | f_rc/r_s0 | f_Vmax | f_Rmax |
|---|---|---|---|---|---|
| 1.00 | 7.2202 | 0.4547 | 0.1073 | 1.2097 | 0.4877 |
| 1.20 | 26.5666 | 0.2386 | 0.0350 | 1.1587 | 0.2706 |
| 1.40 | 112.8472 | **-0.0740** | 0.0313 | **-2.9549** | -0.0024 |
| 2.00 | 3683.10 | -1.7893 | 1.0461 | -456.49 | -1.3640 |

`r_s/r_s,0` and `V_max/V_max,0` go NEGATIVE from tau >= 1.4, i.e. the paper's fits are not extrapolable there. Consequences: (a) the original tau* = 1.37 was already outside the physical range, and the script's original scan out to tau = 20 produced meaningless numbers; (b) the repo's producers are safe — `predict_sidm_halo` (gravothermal_yang2024.py:462), `phase39b_sidm_responsive_profile.py:229` and `v19_2_e_b_per_halo_gravothermal.py:217/243` all clamp tau = min(t_evol/t_c, 1.0), and the stored phase39b artifact's tau range is [4.6e-5, 0.200] — inside the fit range. Only this recheck script's diagnostic scan exceeded it.

## 4. NEW FINDING: `lookback_time_gyr` mis-transcribes eq 3.2 (repo bug) — verified three independent ways

`gravothermal_yang2024.py::lookback_time_gyr` implements `13.647 - 11.020 ln(1.58 (1+z)^1.5 sqrt(1 + 2.4965 (1+z)^3))`. This is broken:

- **Check 1 (must vanish at z=0):** returns 1.712 Gyr at z=0; a lookback time is 0 at z=0 by definition. Any formula failing this is wrong.
- **Check 2 (paper's own worked example):** Yang+ 2024 sec 3.1 states z_f ~ 1.55 -> t_L ~ 9.48 Gyr (Cosmo-501). The repo formula gives -31.4 Gyr at z=1.55. The correctly transcribed form `13.647 - 11.020 ln(1.58 (1+z)^-1.5 + sqrt(1 + 2.4965 (1+z)^-3))` (all (1+z) exponents NEGATIVE; SUM not product — i.e. `13.647 - 11.020 asinh(1.58 (1+z)^-1.5)` in log form) gives 9.47 Gyr at z=1.55. Match. (pdftotext of the KB PDF shows 1.5800/2.4965 as stacked fraction fragments with exponents rendered positive — the negative signs and the sum structure are lost in text extraction; the asinh form reproduces the paper's own numbers exactly.)
- **Check 3 (numerical integration):** tl(z) = integral of dz/((1+z) E(z)) with E = sqrt(0.286(1+z)^3 + 0.714), H0 = 70: tl(1.5116) = 9.380 Gyr, tl(1.55) = 9.472 Gyr — matching the corrected closed form to <0.001 Gyr.

Consequences:
- `lookback_time_gyr(1.5116)` currently returns **-27.0 Gyr** (negative "age"); `evolution_time_gyr(5e9)` returns **40.66 Gyr** — longer than the age of the universe. Every tau routed through it is inflated ~4.3x.
- **Second, independent bug:** even with a correct `lookback_time_gyr`, `evolution_time_gyr = 13.647 - t_L(z_f)` uses the wrong quantity. Yang+ 2024's recipe (sec 3.1): "If tL(zf)/tc > 1, truncate the halo's evolution at tc" — the evolution duration entering tau is **t_L(z_f) itself** (lookback = time from formation to today), while 13.647 - t_L is the age of the universe AT formation (4.2 Gyr). Correct Cloud-9 duration 9.38 Gyr; module returned 40.66.
- Affected call sites: `predict_sidm_halo` (gravothermal_yang2024.py line ~405) and `v19_2_e_b_per_halo_gravothermal.py` line ~206. `tests/test_sashimi_parametric.py` uses a DIFFERENT module's `formation_redshift` (sashimi_parametric), so no test currently pins the broken values — a fix is low test-impact.

## 5. Verdict on the recheck question

1. **The open item is REAL for the high-sigma Cloud-9 anchor, and STRONGER than originally stated** (corrected 2026-11-04). With the eq. 2.1 profile fixed, Cloud-9 at sigma 166-174 is optically thick (lambda < r_c) at essentially every tau the model can describe: lambda/r_c = 0.76 at tau = 0.01, 0.28-0.30 at the tau = 1 truncation, and only marginally thin (1.02-1.06) inside the narrow tau ~ 0.1-0.3 window where f_rc(tau) peaks; on the central-density criterion it is thick at every tau > 0 probed. So "Cloud-9's dense core was produced in t_c = 2-3 Gyr per eq 2.2" sits INSIDE the regime where van den Bosch & Tokayer show the LMFP family runs too fast, not merely past a tau* ~ 1.4 crossing. How much the required formation time is underestimated still cannot be quantified here (it needs the SMFP-corrected time mapping, not the parametric family).
2. **Margin at sigma = 50 (Zhou+ lower bound):** genuinely marginal — lambda/r_c = 0.98 at the tau = 1 truncation and 2.6-3.7 thinner at earlier tau, with tau_natural ~ 1.1-1.2. The low-sigma end of the Cloud-9 band is borderline, not clearly inside the SMFP regime.
3. **The dwarf-scale anchors (sigma ~ 7) are untouched**: never optically thick within any lifetime (tau_natural < 0.2).
4. **Velocity ambiguity sharpens the anchor question**: if Cloud-9's governing DM velocity is ~21 km/s (1D dispersion), the canonical fit gives only sigma ~ 29 cm2/g for Cloud-9 — 6x below 174 — giving t_c_cal ~ 13-15 Gyr and tau_natural ~ 0.6-0.7: the halo would NOT be deeply collapsed within its life at that velocity. The 174 cm2/g Cloud-9 anchor is self-consistent only if the governing velocity is 28-29 km/s (near V_max), not the 1D dispersion. This scope condition must be stated wherever Cloud-9 174 is quoted.
5. **Repo bugs (sec 4) were fixed on 2026-11-03** — `lookback_time_gyr` now uses the asinh form and `evolution_time_gyr` returns t_L(z_f); pinned by `tests/test_gravothermal_lookback_fix.py` (6/6 PASS). Any tau-dependent statement written before that date carries tau inflated ~4.3x and has to be re-checked, not just re-read.
6. **New ceiling (sec 3b):** the eq. 2.3/2.4 fitting functions are unphysical from tau >= 1.4 (negative r_s and V_max). tau-dependent statements beyond tau ~ 1.3 are not physical statements at all, whatever the profile.

## 6. Follow-ups (not yet done)

- DONE 2026-11-03: `lookback_time_gyr` patched to the asinh form, `evolution_time_gyr` returns `t_L(z_f)`, and `tests/test_gravothermal_lookback_fix.py` pins t_L(0)=0.0005, t_L(1.55)=9.4717 (paper 9.48), tl(1.5116)=9.50, evolution_time_gyr(5e9)=9.3799. Then re-check every tau-dependent downstream statement for ~4.3x inflation.
- Quantify the SMFP-slowdown factor by implementing 2610.28890's calibrated time mapping (their NFW (alpha,beta)=(0.5,0.9) family) on the Cloud-9 halo. Priority RAISED 2026-11-04: with the corrected profile the Cloud-9 anchor is inside the SMFP regime over the whole tau window, so the parametric t_c for that anchor cannot be quoted at face value until this is done.
- Both feed the Path 3 RELHIC census (TNG) selection logic: RELHIC-likeness criteria must use the corrected timing or be flagged.

## 7. Follow-up (2026-11-04): the density profile this recheck used was itself inverted

This document's original section 3 was produced by a script that evaluated the project's own
`gravothermal_yang2024.rho_sidm`. That function was later found (2026-11-04, [LocalIntegrity-Sweep-2026-11-04]
F10, decision D7) to carry arXiv:2305.16176 eq. 2.1's core factor INVERTED:

- wrong (in the module until 2026-11-04): `rho_s * [(r^b + r_c^b)/(r_s^b + r_c^b)]^(1/b) * (r_s/(r+r_s))^2`
- right (paper eq. 2.1): `rho_s / { [(r/r_s)^b + (r_c/r_s)^b]^(1/b) * (1 + r/r_s)^2 }`, b = 4
- signature of the error: at r_c = 0 the module's ratio to NFW was exactly (r/r_s)^2 — 0.028 at 0.5 kpc,
  1.0 at 3.0 kpc, 100.0 at 30.0 kpc — so density ROSE outward instead of falling, and it never reduced to
  NFW in the r_c -> 0 limit the paper states.

At the Cloud-9 tau = 1 state the inverted form gave rho(r_c) = 5.125e7 Msun/kpc3 instead of 6.511e8
(factor 12.7), mean free path 0.537 kpc instead of 0.042 kpc, and hence the false "optically thin at
tau = 1" verdict. Fixed in `v0.3-prelim/code/gravothermal_yang2024.py`; pinned by
`v0.3-prelim/tests/test_gravothermal_rho_sidm_source_form.py` (8 tests, each compared against a third
implementation typed from the source PDF) and by
`v0.3-prelim/tests/test_phase39b_responsive_profile.py::test_gravothermal_yang2024_rho_sidm_matches_paper_eq_2_1`,
which previously pinned the defect in the reverse direction.

No stored result JSON was produced from the inverted form: the function's only callers were print-only
diagnostics (this recheck script and phase39b's cross-check report), and `predict_sidm_halo` evolves
(rho_s, r_s, r_c, V_max, R_max) without ever evaluating the profile.

## Appendix: raw recompute output (2026-11-03)

Canonical constants and per-arm results as printed by `scripts/recheck_cloud9_highsigma_20261103.py`: sigma(15)=2.85, sigma(21)=29.18, sigma(28)=166.02, sigma(29.4)=174.55, sigma(36)=56.86; Cloud9-legacy rho_s0=3.867e7 Msun/kpc3; Cloud9-rebaseline rho_s0=2.951e7; Fornax-control rho_s0=2.535e7; per-sigma t_c (lit/cal/legacy) as tabulated above. **The original 2026-11-03 printout also gave tau*=1.37 in all arms and optically-thin tau=1 states (lambda/r_c = 0.54/0.15 through 17.5/0.15 kpc); that printout is superseded — it evaluated the inverted rho_sidm and scanned tau out to 20, far past the fit ceiling (sec 3b).** 2026-11-04 re-run (post-fix) gives: Cloud9-legacy 174 -> lambda(r_c)=0.0423 kpc, lambda/r_c=0.281, THICK; 166 -> 0.0443 / 0.295 THICK; 50 -> 0.1471 / 0.979 marginal; 7 -> 1.0505 / 6.99 thin; Cloud9-rebaseline 174 -> 0.0554 / 0.279 THICK, 50 -> 0.1927 / 0.969 marginal, 7 -> 1.3767 / 6.92 thin; Fornax 174 -> 0.0645 / 0.601 THICK, 50 -> 0.2243 / 2.09 thin, 7 -> 1.6021 / 14.93 thin; tau* within the fit range: Cloud9 166-174 thick already at tau=0.01 (0.76-0.80), Fornax 166-174 tau*=0.85-0.87. Old module t_evol(M=5e9)=40.66 Gyr (bug, now fixed to 9.38); Fornax-control old 41.53 (now 9.54). z_f(5e9)=1.5116, z_f(1e9)=1.5786. Post-fix verification (2026-11-03): t_L(0)=0.0005, t_L(1.55)=9.4717 (paper: 9.48), evolution_time_gyr(5e9)=9.3799; regression tests tests/test_gravothermal_lookback_fix.py 6/6 PASS.
