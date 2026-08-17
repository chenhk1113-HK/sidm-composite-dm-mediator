# Reviewer Audit R12 — six reviews.docx (2026-08-17)

**Author:** Hermes M3 (assisted by user K Lam)
**Repo:** `sidm-composite-dm-mediator` @ `1bf23d5` (pre-R12)
**Reviewers:** 6 external (mixed; numbered 1–6 in `six reviews.docx`)
**Cycle date:** 2026-08-17
**Status:** Closed (all P0 + P1 fixes shipped, committed, pushed)

---

## 1. Tier rank of the 6 reviewers

| # | Identity / signal | Tier | Verdict |
|---|-------------------|------|---------|
| 1 | Anonymous; framework checklist (Born, VMD, BBN); generic; no project-specific evidence | **C** | Useful as composite-DM rubric; weak as project audit |
| 2 | Anonymous, sophisticated; cites Yang+Tsai, HBM, KiSS-SIDM, DSMC; flags the interpolation issue correctly | **A–** | Best general critique. Three claims verified against code — all correct. |
| 3 | Anonymous, very sophisticated; cites Drobczyk arXiv:2506.22997; methodology framing | **A** | Best engineering/methodology audit |
| 4 | Anonymous; open-science rubric | **B+** | Useful checklist but no project engagement |
| 5 | Anonymous; a summary, not a review | **C+** | Sanity check that README is internally consistent |
| 6 | Anonymized but very specific; cites actual line numbers, makes falsifiable claims | **A** (caveated) | Best **and** worst at the same time. 7 specific findings, 6 verified at cited lines. **Includes a hit on my own recent work (finding #6).** |

**Sum:** R3 + R6 ≫ R2 > R4 > R5 > R1.

## 2. R6's 7 specific findings — all verified at cited lines

### Finding #1 — Velocity-index sign convention: **VERIFIED, CRITICAL**

- `channels_v03.py:32-34`: positive `a` = falling σ/m with v ✅
- `t54_dark_quark_joint_fit.py:91`: returns POSITIVE `a` for falling σ/m ✅
- `t41_mediator_mass_joint_fit.py:97-104`: docstring says `a = -d log(σ/m)/d log(v)` but body at line 103 is `(log(s1) - log(s2)) / (log(50) - log(200))` — **missing the minus sign**. Returned NEGATIVE numbers (−1.08 at m_φ=10 MeV/m_χ=40 GeV/g_chi=0.1) when physics says σ/m is falling.
- **Fixed in P0-B.** Now returns +1.08, matching channels_v03 + t54.

### Finding #2 — `t40_yukawa_sigma_m.py` Born-vs-(1+1/2s) bug: **VERIFIED, CRITICAL**

- Line 21 docstring adds `× (1 + 1/(2s))` as "Roberts+ 2024 correction" — **fictitious**.
- Line 90-100 defines `sigma_T_with_m_low_correction` which applies the bogus factor.
- Line 109 in `sigma_m_cm2_per_g` (public API used by t41/t43/t46) calls the broken function.
- Repro: σ/m at v=0.1 km/s = **1.95×10⁶ cm²/g** (insane).
- **Fixed in P0-A.** Removed `(1+1/(2s))`; σ/m at v=0.1 km/s = **3.48 cm²/g** (Born plateau). σ/m falls smoothly to 8.9×10⁻³ cm²/g at v=1000 km/s.

### Finding #3 — Dark ρ / dark photon conflation: **VERIFIED**

- Doc & code used one "m_φ" with one "ε" without specifying mediator identity.
- **Fixed in P1-A.** Added §9 to `DARK_SECTOR_LAGRANGIAN.md` declaring Benchmark A: composite dark pion + elementary dark photon A' with kinetic mixing ε. The mediator is A', NOT the dark ρ.

### Finding #4 — Vector-mass interpolation formula: **VERIFIED**

- `t53_dark_rho_meson.py:70` `m_ρ = 2 sqrt(m_q Λ + Λ²)` failed its own stated heavy-quark limit (m_q → ∞ → 2 sqrt(m_q Λ), not 2 m_q).
- **Fixed in P1-B.** Replaced with KSFR relation `m_ρ² = 2 g_ρππ² f_π²` (Bando+ 1985) calibrated to give m_ρ = 0.79 GeV at Λ_dark = 0.2 GeV (matches QCD's 770 MeV). Also wired `t53b_lattice_input` as the lattice-informed path.

### Finding #5 — ε·σ/m and α·σ/m² mappings in t39: **VERIFIED, DIMENSIONALLY BROKEN**

- `t39_tier3_epsilon_alpha_joint_fit.py:92`: `σ_DM_nucleon_cm2 = ε × σ_m_0` — units cm²/g, NOT cm².
- Line 99: `σ_v = α × σ_m_at_v²` — units cm⁴/g², NOT cm³/s.
- **Fixed in P1-C.** Added `sigma_SI_from_dark_photon()` and `sigma_v_from_dark_photon()` helpers using the proper dark-photon portal form (Kaplinghat, Tulin, Yu 2014; Berlin+ 2018). 4 regression tests added.

### Finding #6 — `t55_boltzmann_relic.py` is not a Boltzmann solver: **VERIFIED — MY WORK**

- Imported `scipy.integrate.odeint` at line 45; never called it.
- Function body returns hardcoded `1/⟨σv⟩` calibration dressed up as an ODE solver.
- **This was MY commit `cc4dce5` from earlier today (R11 G15 closure).** Honest-name fix: renamed to `t55_wimp_relic_calibration.py`; docstring rewritten to state "this is a calibrated mapping, not a Boltzmann solver"; dead odeint import removed. Pitfall H1 in action (R11 audit reference).

### Finding #7 — Horigome+ 2025 dSph constraint misread: **VERIFIED, MOST CONSEQUENTIAL**

- `channels_v03.py:45-77` built a bimodal-with-dip surrogate (peaks at σ/m ≈ 0.1 AND ≈ 10 cm²/g).
- Actual abstract (verified via `web_extract` of arXiv:2503.13650): "decisively prefers CDM to SIDM when σ/m exceeds ~0.2 cm²/g" — a 95% CL UPPER LIMIT, not a bimodal posterior.
- **Fixed in P0-D.** Replaced with proper upper-limit form (peak at σ/m ≈ 0.05, half-Gaussian up to 0.2 cm²/g, strong penalty above). Propagated to `t28_published_style_dsph.loglike_dsph_published_style` and `sidm_velocity_dependent.loglike_dsph_published` (both now delegate to channels_v03). 8 regression tests added.

## 3. Cross-reviewer consensus

Five-reviewer consensus (R1, R2, R3, R4, R6): the composite sector is a "toy / interpolation", the prior-volume-driven decoupling is mistaken for a detection prediction, and the likelihoods are largely surrogate. Six-reviewer consensus: the headline numbers (σ/m, the 1.3σ tension, the tier-3 ε/α prediction) cannot be taken as physical model predictions in their current form.

**The 1.3σ "composite a ≈ 2.24 vs data 0.94 tension" was largely a sign-flip artifact** (R6 finding #1). After P0-B: Yukawa-derived a ≈ +1.08 at the canonical point, well within data-preferred range.

## 4. Honest new numbers (P1-D snapshot)

At the Benchmark A canonical point (m_χ = 40 GeV, m_A' = 10 MeV, g_χ = 0.1):

| Quantity | Old value (R11) | New value (R12) | Notes |
|----------|----------------|-----------------|-------|
| σ/m at v_ref = 100 km/s | 2.78 cm²/g (with bogus factor) | **1.78 cm²/g** (clean Born) | P0-A |
| velocity index a | −1.08 (sign-flipped) | **+1.08** | P0-B |
| composite dark ρ at Λ_dark=1 GeV (KSFR) | 4.27 GeV (legacy interp) | **3.95 GeV** (KSFR) | P1-B |
| composite dark ρ at Λ_dark=1 GeV (lattice) | n/a | **8.36 GeV** (lattice ratio) | P1-B |
| σ_SI at ε=1e-5 | 1.20e-5 cm²/g (wrong units) | **1.20e-32 cm²** (proper) | P1-C |
| σ_v at α_D=0.01 | 5.88e3 cm³/s (wrong units) | **6.85e-25 cm³/s** (proper) | P1-C |
| dSph log L at σ/m_0=10 cm²/g | 0 (favored!) | **−4.53** (disfavored) | P0-D |

## 5. P0 + P1 closure summary

| Phase | Fix | Files | Tests added |
|-------|-----|-------|-------------|
| P0-A | Remove bogus (1+1/2s) Yukawa factor | t40_yukawa_sigma_m.py | 4 |
| P0-B | Correct velocity-index sign in t41.derived_a | t41_mediator_mass_joint_fit.py | 2 |
| P0-C | Rename t55 to honest "wimp_relic_calibration" + remove dead odeint | t55_boltzmann_relic.py → t55_wimp_relic_calibration.py | 2 |
| P0-D | Replace bimodal-dip dSph surrogate with Horigome+ upper limit | channels_v03.py, t28_published_style_dsph.py, sidm_velocity_dependent.py | 8 (incl. 1 delegated) |
| P1-A | Choose Benchmark A (composite matter + elementary A'); document | docs/DARK_SECTOR_LAGRANGIAN.md §9 | n/a |
| P1-B | Replace t53 dark-ρ interpolation with KSFR + wire t53b lattice | t53_dark_rho_meson.py | 1 (KSFR) + 1 (lattice path) |
| P1-C | Fix t39 dimensional mappings via dark-photon portal form | t39_tier3_epsilon_alpha_joint_fit.py | 4 |
| P1-D | Record honest new anchor numbers | docs/REVIEWER_AUDIT_R12.md (this file) | n/a |

**Total tests added: 22 regression tests; 0 regressions; final pytest run: 354 pass / 4 skip / 3 unrelated pre-existing failures (config drift, KISS-SIDM fit, t37 import).**

## 6. Caveats and what was deferred

- **P2-A (SPARC saturation → hierarchical):** R11 G12 closure added the hierarchical per-galaxy model (`t8_v03_joint_fit.py`), but the joint fit (t39) still uses the saturation score via `t8.delta_log_sparc(sigma_m_0, a) / 1000`. Properly wiring the hierarchical likelihood into t39 is a v0.4+ scope item.
- **P2-B (relic benchmarking vs micrOMEGAs):** Not implemented. The t55 calibration is honest about being a calibration, but doesn't reproduce published Boltzmann-solver outputs to a specified tolerance.
- **P2-C (χ²/DoF + posterior-predictive checks):** Not implemented. The joint-fit outputs report MAP and median but no χ²/DoF.
- **P2-D (re-run joint fit with P0/P1 corrections baked in):** Cached `data/results/t41_mediator_mass_joint_fit.json` still has the pre-P0-B `Yukawa_a_at_MAP = -1.81` (which was really +1.81 in the correct convention). Re-running the joint fit is deferred to a follow-up commit so this PR is testable as-is.

## 7. Self-audit note (rule 12: catch your own mistakes)

Three of R6's seven findings cite lines or functions I either wrote or imported this week:
- Finding #1: t41 sign-flip — I extended t41 across multiple audit rounds.
- Finding #5: t39 dimensional mappings — I extended t39 across multiple fitting rounds.
- Finding #6: t55 "Boltzmann solver" — I shipped it. Commit `cc4dce5`, this morning.

Two structural improvements happened in service of these fixes (testability, not on the original P0 list):
- `tests/conftest.py` ensures pytest picks up both v0.1-prelim and v0.3-prelim code paths.
- Lazy `halo_profiles` / `sparc_loader` imports in `channels_v03.py` and `sidm_velocity_dependent.py`. Previously these were top-level, breaking any test that imported the modules on Windows.

These are recorded for future-me as reviewer-audit class-level lessons (testability is part of scientific plausibility).

## 8. Save-as-skill opportunity

The R12 process demonstrated that **scientific-plausibility defects accumulate in pieces**:
1. The dSph bimodal-dip surrogate existed in three near-identical forms (channels_v03, t28, sidm_velocity_dependent); fixing one without fixing the others leaves the bug.
2. The (1+1/2s) blowup + the missing minus sign + the dimensionally-inconsistent mappings + the misnamed "Boltzmann solver" are independent defects with one common root cause: **the headline numbers were inflated/decorated to support a physical-plausibility narrative** (σ/m ≈ 1 cm²/g from a bimodal that doesn't exist in the paper; a ≈ 2.24 that is sign-flipped; ε ≈ 10⁻⁵⁴ that is dimensionally broken).

For future R13+: every external-review cycle should include (a) a **grep across all module variants** of any function with the same name (H2), and (b) a **dimensional-check pass** of every mapping in the joint fit (universal rule). This would catch the dSph duplication and the t39 dimensions at the same time.

---

**Cycle status:** All P0 + P1 fixes closed 2026-08-17. Project moved from "phenomenological toy" (R11 verdict) toward "phenomenological framework with documented limitations" (R12 verdict).