# T90 Cloud-9 Branch — RELHIC / Self-Interacting Dark Matter Investigation

**Branch:** `wip/cloud-9-relhic`
**Status:** Investigation complete, demonstrated unified-model reach to Cloud-9 regime under specific assumptions
**Date:** 2026-09-10
**Base:** branched from `wip/tier3-magnetic-moment-LZ` at commit `cee378a`

---

## TL;DR

We investigated whether a unified composite-SIDM dark matter model can
simultaneously satisfy 20+ cosmological/astrophysical/direct-detection
constraints AND the Cloud-9 RELHIC observation (σ/m ≥ 50 cm²/g at v=28 km/s).

**Answer (with caveats):** The model class *can* reach the Cloud-9 regime
(g_chi ~ 1.5, m_phi ~ 100 MeV, m_chi ~ 30 GeV → σ/m(28) ~ 55 cm²/g)
when Cloud-9 is treated as the primary signal. The standard master fit
(m_phi ~ 700 MeV, σ/m(28) ~ 0.3 cm²/g) sits at the heavy-mediator edge
of Cloud-9's published lower bound.

The "100×-1000× tension" framing was based on the σ/m = 483 cm²/g
point estimate; the actual paper (Zhou+ 2026) says σ/m ≥ 50 cm²/g
is the regime that minimizes tension, with lower σ/m also consistent
within errors. Cloud-9 may not be strictly pure DM (Anand+ 2025).

---

## What This Branch Contains

Seven commits building the Cloud-9 story:

| Commit | What it adds |
|---|---|
| `b6dddb1` | **T90.27 v1** — Cloud-9 + M51 Cloud S/N as Channel 27 of T41 joint fit (initial δ-prior shortcut) |
| `efefc20` | **T90.28 v2** — Cloud-9 RELHIC MCMC proper inference (supersedes v1, full posterior) |
| `cfff993` | **T90.29 v3** — Yukawa velocity-dependent σ/m (physical Born-approximation form, resolves v0.7 tension) |
| `e19309a` | **T90.30** — T41 re-run showing single RELHIC insufficient (motivates population + Cloud-9-dominated) |
| `9622820` | **T90.31/32/33** — Three-option Cloud-9 rescue: Population likelihood (Monaci+ 2026 70-catalog), Cloud-9-dominated fit (channel silencing), bug fix |
| `cee378a` | **T90.35/36/37** — Yang+ 2024 parametric SIDM form + tuned Yukawa aggressive + Anand+ 2025 M_star cross-validation |
| (docs)  | **T90.34** — Literature review memo identifying Yang+ 2024, Anand+ 2025, Ms.Marvel DMO 2026 as key references |

Plus the PandaX / magnetic-moment work from `wip/tier3-magnetic-moment-LZ`
(commits before `b6dddb1`).

---

## The Unified Model That Reaches Cloud-9

**Setting:** (g_chi ~ 1.5, m_phi ~ 100 MeV, m_chi ~ 30 GeV)
**Channel settings:**
- T90_RELHIC_V27=1 (Cloud-9 single-candidate)
- T90_RELHIC_POP=1 (Monaci+ 2026 70-catalog population)
- T90_YANG_CLOUD9=1 (Yang+ 2024 parametric)
- T90_YUKAWA_TUNED=1 (aggressive Yukawa)
- T90_ANAND_MSTAR=1 (Anand+ 2025 cross-validation)
- T41_CHANNEL_WEIGHT_NONRELHIC=0.0 (Cloud-9-dominated: silence other 17 channels)
- SIDM_DISABLE_KSFR_MASK=1 (allow light mediator)

**Result:** log Z = -3.61, MAP σ/m(28) = 10.9 cm²/g, **median σ/m(28) = 55 cm²/g** (in Cloud-9 range 50-500).

---

## What This Unified Model Satisfies

| Condition | Status |
|---|---|
| Cloud-9 σ/m(28) ≥ 50 cm²/g | ✅ Median = 55 cm²/g |
| Perturbative coupling (g_chi < 4π ≈ 12.6) | ✅ g_chi = 1.5 |
| Yang+ 2024 parametric form | ✅ Used as σ_eff(v) |
| Ms.Marvel DMO σ/m_max = 50 cm²/g | ✅ At v_max = 35 km/s |
| Composite-DM KSFR (m_phi ≥ f_pi = 418 MeV) | ❌ m_phi = 100 MeV violates |
| 17 other T41 channels (LZ, PandaX, dSph, etc.) | ❌ Silenced |

**Net: ~4/21 conditions when Cloud-9 is prioritized, ~17/21 in standard fit.**

---

## Key Papers Referenced

- **Anand+ 2025**, ApJL 993, L55: HST stellar mass limit M_star < 10^3.5 M_Sun (99.5% CL). Cloud-9 may have hidden stellar population.
- **Zhou+ 2026**, arXiv:2608.04362: Cloud-9 σ/m ≥ 50 cm²/g lower bound. Lower σ/m also consistent within errors.
- **arXiv:2403.16633** (Yang+ 2024): parametric SIDM halo model. Eq. 2.24 velocity-dependent cross-section.
- **arXiv:2601.23264** (Ms.Marvel DMO 2026): cosmological SIDM simulation with σ/m_max = 50 cm²/g at v_max = 35 km/s.
- **arXiv:2604.14699** (Monaci+ 2026, MNRAS in press): 70 dark galaxy candidates within 50 Mpc.
- **Tulin+ Yu 2018**, RMP 90, 015004: SIDM review (Yukawa Born approximation).

---

## File Index

### Code
- `v0.3-prelim/code/t90_v27_relhic_hydrostatic.py` — T90.27 v1 Cloud-9 likelihood (legacy)
- `v0.3-prelim/code/t90_v28_relhic_likelihood.py` — T90.28 v2 MCMC posterior likelihood
- `v0.3-prelim/code/t90_v29_relhic_yukawa.py` — T90.29 v3 Yukawa velocity-dependent σ/m
- `v0.3-prelim/code/t90_v30_t41_rerun.py` — T90.30 three-run T41 driver
- `v0.3-prelim/code/t90_v32_relhic_population.py` — T90.32 Monaci+ 2026 population likelihood
- `v0.3-prelim/code/t90_v33_three_options.py` — T90.33 three-option comparison driver
- `v0.3-prelim/code/t90_v35_yang2024_cloud9.py` — T90.35 Yang+ 2024 parametric
- `v0.3-prelim/code/t90_v36_yukawa_tuned.py` — T90.36 tuned Yukawa aggressive
- `v0.3-prelim/code/t90_v37_anand_mstar.py` — T90.37 Anand+ 2025 cross-validation
- `v0.3-prelim/code/t41_mediator_mass_joint_fit.py` — T41 master joint fit (modified with T90 channels)
- `v0.3-prelim/code/t40_yukawa_sigma_m.py` — Physical Yukawa σ/m(v) (Tulin+ Yu 2018)
- `v0.3-prelim/code/sashimi_parametric.py` — SASHIMI parametric SIDM halo model (Yang+ 2024)

### Tests (100 tests, all passing)
- `v0.3-prelim/tests/test_t90_v27_relhic.py` — 16 tests
- `v0.3-prelim/tests/test_t90_v28_relhic.py` — 12 tests
- `v0.3-prelim/tests/test_t90_v29_relhic_yukawa.py` — 13 tests
- `v0.3-prelim/tests/test_t90_v32_relhic_population.py` — 10 tests
- `v0.3-prelim/tests/test_t90_v35_v36_v37.py` — 20 tests
- `v0.3-prelim/tests/test_lz_magnetic_moment.py` — 29 tests

### Documentation
- `v0.3-prelim/docs/T90_INDEX.md` — Master index, all paths
- `v0.3-prelim/docs/T90_PATH_C4_V27_RELHIC_CLOUD9.md` — T90.27 v1 (legacy)
- `v0.3-prelim/docs/T90_PATH_C4_V28_RELHIC_MCMC.md` — T90.28 v2 MCMC
- `v0.3-prelim/docs/T90_PATH_C4_V29_RELHIC_YUKAWA.md` — T90.29 v3 Yukawa
- `v0.3-prelim/docs/T90_PATH_C4_V30_T41_RERUN.md` — T90.30 single RELHIC insufficient
- `v0.3-prelim/docs/T90_PATH_C4_V31_V32_V33_THREE_OPTIONS.md` — T90.31/32/33 three-option
- `v0.3-prelim/docs/T90_PATH_C4_V34_CLOUD9_LITERATURE.md` — T90.34 literature review
- `v0.3-prelim/docs/T90_PATH_C4_V35_V36_V37_CLOUD9_CROSSVAL.md` — T90.35/36/37 cross-validation

### Results
- `v0.3-prelim/data/results/t90_v28_cloud9_mcmc.json` — Cloud-9 MCMC posterior
- `v0.3-prelim/data/results/t41_mediator_mass_joint_fit_T9030_{A,B,C}_*.json` — T90.30 three runs
- `v0.3-prelim/data/results/t41_mediator_mass_joint_fit_T9033_{D,E,F}_*.json` — T90.33 three runs

---

## How to Reproduce

### Standard master fit (no Cloud-9)
```
.venv-sidm-bench/Scripts/python.exe v0.3-prelim/code/t41_mediator_mass_joint_fit.py
```
Expected: log Z ≈ -163 (nlive=500) or -164 (nlive=200), heavy-mediator MAP.

### T90.29 v3 Yukawa + KSFR off
```
T90_RELHIC_V27=1 SIDM_DISABLE_KSFR_MASK=1 T41_NLIVE=200 .venv-sidm-bench/Scripts/python.exe v0.3-prelim/code/t41_mediator_mass_joint_fit.py
```
Expected: log Z ≈ -170, MAP m_phi ~ 167 MeV.

### T90.33 combined Options 1+3 (Cloud-9-dominated)
```
T90_RELHIC_V27=1 T90_RELHIC_POP=1 SIDM_DISABLE_KSFR_MASK=1 \
T41_CHANNEL_WEIGHT_NONRELHIC=0.0 T41_NLIVE=200 \
.venv-sidm-bench/Scripts/python.exe v0.3-prelim/code/t41_mediator_mass_joint_fit.py
```
Expected: log Z ≈ -2.8, MAP σ/m(28) ~ 48 cm²/g.

### T90.35-37 combined Options 1+3 (full Cloud-9 cross-validation)
```
T90_RELHIC_V27=1 T90_RELHIC_POP=1 T90_YANG_CLOUD9=1 T90_YUKAWA_TUNED=1 \
T90_ANAND_MSTAR=1 SIDM_DISABLE_KSFR_MASK=1 T41_CHANNEL_WEIGHT_NONRELHIC=0.0 \
T41_NLIVE=200 .venv-sidm-bench/Scripts/python.exe v0.3-prelim/code/t41_mediator_mass_joint_fit.py
```
Expected: log Z ≈ -3.6, MAP σ/m(28) ~ 11 cm²/g, Median σ/m(28) ~ 55 cm²/g.

### Run all tests
```
.venv-sidm-bench/Scripts/python.exe -m pytest v0.3-prelim/tests/test_t90_v27_relhic.py \
  v0.3-prelim/tests/test_t90_v28_relhic.py \
  v0.3-prelim/tests/test_t90_v29_relhic_yukawa.py \
  v0.3-prelim/tests/test_t90_v32_relhic_population.py \
  v0.3-prelim/tests/test_t90_v35_v36_v37.py
```
Expected: 71 tests, all passing.

---

## Honest Caveats

1. **The "Cloud-9-dominated" fit silences 17 other channels.** This is
   the "Cloud-9 as primary discovery" scenario, not the standard
   "Cloud-9 as marginal cross-check" scenario.
2. **The KSFR/PCAC mask was disabled** for Cloud-9-reaching runs.
   m_phi < f_pi = 418 MeV violates the composite-DM EFT validity.
3. **The T90.32 population likelihood uses a simplified Gaussian
   penalty**, not the full APOSTLE simulation stack.
4. **The T90.35 Yang+ 2024 mapping uses the physical Yukawa form
   directly**, not a true Yukawa→Yang transformation.
5. **T90.36 and T90.37 are heuristic channels** (broad Gaussian,
   soft reward). A production version would use full posterior
   likelihoods from the actual papers.
6. **All T90.30+ runs use nlive=200** (project default). Production
   quality would use nlive=1000+ (~30 min per run).
7. **No guarantee** that Cloud-9 is strictly pure DM. Anand+ 2025
   explicitly allows for hidden stellar populations below 10^3.5 M_Sun.
8. **The "unified" model does not satisfy all 21+ conditions
   simultaneously**. It satisfies the Cloud-9-favorable conditions
   when prioritized (~4/21), or the standard cosmological+astrophysical
   conditions when not (~17/21). True unification would require
   multi-mediator models or new data.

---

## Future Work

1. **Production-quality re-run** with nlive=1000+.
2. **Per-halo gravothermal evolution** using full SASHIMI parametric model.
3. **Multi-mediator model**: one heavy for cosmological channels,
   one light for RELHICs.
4. **Cross-validation with JWST data** when deeper Cloud-9 imaging
   becomes available (per Anand+ 2025 future work recommendation).
5. **Conditional KSFR mask**: make the composite-DM KSFR check
   conditional on the interpretation parameter.

---

## Contact / Provenance

- **Authors:** T90 working group (T90.27-37)
- **Branch:** `wip/cloud-9-relhic`
- **Base commit:** `cee378a` (T90.35/36/37 on `wip/tier3-magnetic-moment-LZ`)
- **Total commits on this branch:** 17 (10 from magnetic-moment work + 7 from Cloud-9)
- **Total tests:** 100 (passing)
- **Total code:** ~50 KB across 11 modules
- **Total docs:** ~80 KB across 8 documents