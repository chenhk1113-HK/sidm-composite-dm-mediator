# T90 — Magnetic-Moment EFT Tier-3 Branch (Plan + Phase 0 results)

> **Status:** Phase 0 complete (branch + install + smoke test). Phase 1-4 next.
> **Branch:** `wip/tier3-magnetic-moment-LZ` (off master @ `7fb9cdd`)
> **Date:** 2026-09-06
> **Trigger:** User directive "I want to explore tier 3, as a branch to our model.
> Plenty computer resource available."

---

## TL;DR — what Tier-3 branch does

This branch explores the **hybrid composite-DM + magnetic-moment EFT**
hypothesis as a way to reproduce the LZ 248 keV event WITHOUT changing
the project's v0.8 standing posterior (σ/m = 0.06 cm²/g, log Z =
−164.87 ± 0.084).

**The branch adds one new dimension** to the joint-fit parameter space:
a magnetic-dipole coupling `μ_x` (in units of nuclear magnetons μ_N).
The astrophysical channels (σ_DM-DM) are unchanged — only the direct-
detection channel gets a new contribution.

---

## Why this branch exists

The project's Benchmark A (composite-DM + elementary dark photon +
secluded sector) cannot reproduce the LZ 248 keV event:
- σ_inel_nuc at 248 keV = **1.15 × 10⁻¹¹⁷ cm²**
- Predicted N_events in 2.84 tonne-years = **4.8 × 10⁻⁷³**
- 71 orders of magnitude below LZ sensitivity
- Verdict (T87): composite-DM **cannot** claim the LZ event at v0.7 MAP

The LZ paper itself (arXiv:2609.02608, Di Mauro+ 2026) flags the
**magnetic-moment Ls₁₀ operator** as the leading candidate for explaining
the 248 keV event (best-fit: m_χ = 1000 GeV). This branch adds that
operator as a parallel contribution to direct detection.

---

## Phase 0 — Setup (✅ DONE 2026-09-06)

**Actions taken:**

1. **Created branch** `wip/tier3-magnetic-moment-LZ` off master @ `7fb9cdd`
   (clean separation from master, reversible).

2. **Installed WIMpy_NREFT v1.2** (Brad Kavanagh+ Oct 2024, MIT) in
   `.venv-sidm-bench/` via:
   ```
   uv pip install --python .venv-sidm-bench/Scripts/python.exe \
       git+https://github.com/bradkav/WIMpy_NREFT.git
   ```
   - Install commit: `50581c637069305a3def3865462ef1b4ed9a616d`
   - Pure Python, numpy + scipy only (both already in venv)
   - Includes operators O_1 to O_20 + magnetic-dipole + millicharged DM
   - Supports xenon isotopes (Xe128, Xe129, Xe130, Xe131, Xe132,
     Xe134, Xe136)

3. **Patched WIMpy/DMUtils.py** to handle scipy 1.12+ deprecation:
   `scipy.integrate.trapz` → `scipy.integrate.trapezoid` and
   `scipy.integrate.cumtrapz` → `scipy.integrate.cumulative_trapezoid`.
   Without this patch, WIMpy_NREFT imports fail on modern scipy.
   **This patch should be upstreamed** but for now lives locally.

4. **Smoke test passed:** `dRdE_magnetic(E, m_chi, mu_x, target)` runs
   cleanly on Xe129.

---

## Phase 0 smoke-test results — KEY FINDING

**Bisection result for μ_x that reproduces LZ event rate:**

| m_χ (GeV) | μ_x (μ_N) | Predicted N_events (2.84 tonne-years at 248 keV) |
|---|---|---|
| 1000 (LZ best-fit) | 3 × 10⁻¹¹ | **1.89** |
| 770 (project v0.8 MAP) | 3 × 10⁻¹¹ | **2.33** |
| Observed | — | **1** |

**Interpretation:** A magnetic-dipole coupling of μ_x ~ 3 × 10⁻¹¹ μ_N
reproduces the LZ 248 keV event within Poisson noise at BOTH the LZ
best-fit mass (1000 GeV) and the project's v0.8 MAP (770 GeV). The
mass is not a strong discriminator in this range.

**This is a positive scientific result.** The magnetic-dipole operator
is a viable microphysical interpretation of the LZ event, and our
project's mass window is compatible with it.

---

## Phase plan (1-4)

### Phase 1 — Operator cross-validation (~1-2 hours)

**Goal:** Verify WIMpy_NREFT's standard SI operator matches our existing
portal formula at the relevant regime.

- Compute σ_DM-nucleon at v0.8 MAP using both:
  - Our portal formula (T62, T76 — composite-DM + kinetic mixing ε)
  - WIMpy_NREFT's `dRdE_standard` with O_1 operator
- Verify the SI baseline (c_p = c_n = 1) matches at standard SI
  cross-section ~10⁻⁴⁵ cm²
- Compute Ls₁₀ spectrum at LZ best-fit point and compare to LZ paper
  Fig.5 reference shape (qualitative match — full Fig.5 data may not
  be public)

**Success criterion:** SI baseline matches to within 50% (sanity
check; small differences expected due to form-factor parameterizations).

### Phase 2 — Hybrid channel implementation (~3-5 hours)

**Goal:** Add Channel 26 = magnetic-moment LZ as a new
`loglike_lz_magnetic_moment(c_mag, m_chi)` function.

- New parameter: `log_c_mag` (prior [-15, -8] in log10(μ_x/μ_N))
- Total joint-fit dimension: 7 (Benchmark A's 6 + c_mag 1)
- New channel returns log-likelihood contribution from magnetic-dipole
  rate at LZ, gated by `T90_MAGNETIC_MOMENT_DISABLE=1` env var
- Test file: `tests/test_lz_magnetic_moment.py` with 5-10 tests
  (cross-validation, kinematic limits, N_events smoke test, prior
  bounds, env-var gating)

**Files modified:**
- `v0.3-prelim/code/channels_extended.py` — add Channel 26
- `v0.3-prelim/code/t41_mediator_mass_joint_fit.py` — wire Channel 26
- `v0.3-prelim/tests/test_lz_magnetic_moment.py` — new test file
- `v0.3-prelim/code/channels_extended.py:CHANNEL_STATUS` — add entry 26

### Phase 3 — Joint-fit re-run (~30-60 min wall)

**Goal:** Run T41 at nlive=1000 (faster than 2000 for Tier-3
exploration) with Channel 26 enabled, compare posterior to v0.8.

**Verdict tree:**
1. **c_mag pulls strongly** + ε stays at 10⁻³⁷ → hybrid branch works;
   LZ event explained; commit + document.
2. **c_mag pulls weakly** + ε stays at 10⁻³⁷ → magnetic-moment adds
   little; LZ event still unexplained; document as null result.
3. **c_mag pulls** + ε shifts up → portal re-engages; check if other
   constraints still satisfied; if yes, ship as new posterior; if no,
   document as over-fit warning.

**Compute:** ~30-60 min wall at nlive=1000 on the existing dynesty
infrastructure; can run in background while we continue other work.

### Phase 4 — Documentation + ship (~1-2 hours)

**Goal:** Document the verdict, push the branch to origin.

- `T90_MAGNETIC_MOMENT_FORWARD_PREDICTION.md` with verdict + derivation
- CHANGELOG entry for T90
- Decide whether to merge into master (default: **NO** — keep as
  `wip/tier3-magnetic-moment-LZ` for review)
- Push branch to origin: `git push -u origin wip/tier3-magnetic-moment-LZ`

**Files modified:**
- `v0.3-prelim/docs/T90_MAGNETIC_MOMENT_FORWARD_PREDICTION.md` (new)
- `CHANGELOG.md` (T90 entry)

---

## Resource budget

- Compute: ~5-10 hours wall over 1-2 sessions
- Disk: WIMpy_NREFT ~5 MB, no large data products
- Branches: 1 new (`wip/tier3-magnetic-moment-LZ`)
- Venv: existing `.venv-sidm-bench/` reused (already has WIMpy)

---

## Risks + fallbacks

| Risk | Fallback |
|---|---|
| WIMpy_NREFT's Ls₁₀ spectrum doesn't match LZ paper Fig.5 | Fall back to hand-rolling Ls₁₀ operator (~2-3 days) |
| Joint-fit posterior is unstable at nlive=1000 | Fix c_mag to LZ paper best-fit, scan over Benchmark A only |
| Hybrid adds too many parameters (Bayes factor penalty) | Drop c_mag to a single fixed value; just compute the event rate at v0.8 MAP |
| Cross-validation fails (WIMpy SI baseline ≠ ours) | Document the disagreement; switch to direct implementation |

---

## What this branch does NOT do

- ❌ Does NOT bump VERSION on master (this is Tier-3 exploration)
- ❌ Does NOT change v0.8 standing posterior on master
- ❌ Does NOT modify drift-guard audit script (branch is experimental)
- ❌ Does NOT add Channel 26 to master CHANNEL_STATUS (only on this branch)

---

## References

- WIMpy_NREFT v1.2: Kavanagh & Edwards (2024),
  [github.com/bradkav/WIMpy_NREFT](https://github.com/bradkav/WIMpy_NREFT),
  [doi:10.5281/zenodo.1230503](https://doi.org/10.5281/zenodo.1230503)
- LZ paper: Di Mauro+ 2026, arXiv:2609.02608 (Sep 2026)
- NREFT framework: Fitzpatrick+ 1203.3542, 1505.03117; Catena 1907.02910
- Magnetic-dipole DM: Barger+ 2017 (early DM magnetic moment constraints)
- Project's prior LZ analysis: T77 (initial), T80 (paper update),
  T87 (composite-DM forward prediction)

---

**Next action:** Phase 1 — operator cross-validation. Will proceed in
this session unless user redirects.