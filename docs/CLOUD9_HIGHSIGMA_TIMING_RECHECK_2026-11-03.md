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

## 3. Optical-thickness onset

Within the parametric model, lambda < r_core occurs at **tau* = 1.37 for every sigma tested (7-174)** — the parametric core collapse itself drives the transition; sigma only sets WHEN (in Gyr) tau=1.37 is reached:

- sigma 166-174: t* = 1.7-2.0 Gyr (literal) / 3.0-3.6 Gyr (calibrated)
- sigma 50:       t* = 5.8-6.6 Gyr (literal) / 10.6-12.0 Gyr (calibrated)
- sigma 7:        t* = 42-47 Gyr (literal) / 76-86 Gyr (calibrated) — never reached within any halo lifetime (optically thin for the whole dwarf case).

At the project's tau=1 truncation (deep-collapse endpoint) Cloud-9 is still OPTICALLY THIN at every sigma (lambda 0.54-17.5 kpc vs r_c 0.15-0.20 kpc). So the specific claimed state in `predict_sidm_halo` (which truncates at tau=1 "to avoid extrapolation") is inside the formula's nominal validity edge — but only just.

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

1. **The open item is REAL for the high-sigma Cloud-9 anchor.** At sigma ~ 174 the Cloud-9 halo crosses into the optically thick regime at tau* ~ 1.4 — only ~3 Gyr after formation (z ~ 1), deep inside its ~9.5 Gyr life. Any statement of the form "Cloud-9's observed dense core was produced in t_c = 2-3 Gyr per eq 2.2" extends past tau 1.4 into the regime where van den Bosch & Tokayer show the LMFP family runs too fast. Required formation time is underestimated by an amount this recheck cannot quantify (it needs the SphDSMC-corrected time mapping, not the parametric family).
2. **Margin at sigma = 50 (Zhou+ lower bound):** tau_natural ~ 1.1-1.2 — the halo barely reaches tau* within its lifetime; the low-sigma end of the Cloud-9 band is only mildly affected.
3. **The dwarf-scale anchors (sigma ~ 7) are untouched**: never optically thick within any lifetime (tau_natural < 0.2).
4. **Velocity ambiguity sharpens the anchor question**: if Cloud-9's governing DM velocity is ~21 km/s (1D dispersion), the canonical fit gives only sigma ~ 29 cm2/g for Cloud-9 — 6x below 174 — giving t_c_cal ~ 13-15 Gyr and tau_natural ~ 0.6-0.7: the halo would NOT be deeply collapsed within its life at that velocity. The 174 cm2/g Cloud-9 anchor is self-consistent only if the governing velocity is 28-29 km/s (near V_max), not the 1D dispersion. This scope condition must be stated wherever Cloud-9 174 is quoted.
5. **Repo bugs (sec 4) must be fixed or fenced** before any tau-dependent statement is trusted; together they inflate tau ~4.3x wherever `evolution_time_gyr` feeds it.

## 6. Follow-ups (not yet done)

- Patch `lookback_time_gyr` to the asinh form; fix `evolution_time_gyr` to return `t_L(z_f)`; add tests (t_L(0)=0; paper worked example z=1.55 -> 9.48; tl(1.5116)=9.50; evolution_time_gyr(5e9) ~ 9.5). Test impact is low (no existing test pins the broken values). Then re-check every tau-dependent downstream statement for ~4.3x inflation.
- Quantify the SMFP-slowdown factor by implementing 2610.28890's calibrated time mapping (their NFW (alpha,beta)=(0.5,0.9) family) on the Cloud-9 halo.
- Both feed the Path 3 RELHIC census (TNG) selection logic: RELHIC-likeness criteria must use the corrected timing or be flagged.

## Appendix: raw recompute output (2026-11-03)

Canonical constants and per-arm results as printed by `scripts/recheck_cloud9_highsigma_20261103.py`: sigma(15)=2.85, sigma(21)=29.18, sigma(28)=166.02, sigma(29.4)=174.55, sigma(36)=56.86; Cloud9-legacy rho_s0=3.867e7 Msun/kpc3; Cloud9-rebaseline rho_s0=2.951e7; Fornax-control rho_s0=2.535e7; per-sigma t_c (lit/cal/legacy) and tau* as tabulated above; tau*=1.37 in all arms; tau=1 states optically thin in all arms (lambda/r_c = 0.54/0.15 through 17.5/0.15 kpc). Old module t_evol(M=5e9)=40.66 Gyr (bug, now fixed to 9.38); Fornax-control old 41.53 (now 9.54). z_f(5e9)=1.5116, z_f(1e9)=1.5786. Post-fix verification (2026-11-03): t_L(0)=0.0005, t_L(1.55)=9.4717 (paper: 9.48), evolution_time_gyr(5e9)=9.3799; regression tests tests/test_gravothermal_lookback_fix.py 6/6 PASS.
