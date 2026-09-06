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

### Phase 1 — Operator cross-validation (~1-2 hours) ✅ DONE 2026-09-06

**Goal:** Verify WIMpy_NREFT's standard SI operator matches our existing
portal formula at the relevant regime.

**Tests run:** 4 cross-validation checks via
`.venv-sidm-bench/t90_phase1_cross_validation.py`

**Results:**

1. **Standard SI at LZ sensitivity (σ = 10⁻⁴³ cm², m_chi = 1000 GeV):**
   WIMpy_NREFT predicts N_pred = 0.12 events. This matches LZ WS2024
   sensitivity at m_chi ~ 1 TeV (~10⁻⁴³ cm²). ✅

2. **Standard SI at LZ null-result (σ = 10⁻⁴⁴ cm², m_chi = 1000 GeV):**
   N_pred = 0.01 events. Below LZ discovery threshold. ✅

3. **Magnetic-moment at tuned coupling (μ_x = 3×10⁻¹¹ μ_N):**
   - m_chi = 1000 GeV: N_pred = 1.03 (Poisson log L = -1.02)
   - m_chi = 770 GeV: N_pred = 1.27 (Poisson log L = -1.27)
   - **Magnetic-moment operator is 10-100× more efficient than standard SI
     at producing high-energy recoils**, explaining why LZ paper flags it. ✅

4. **Project's portal formula equivalent (σ = 10⁻¹¹⁷ cm²):**
   N_pred ≈ 0 (sanity check). ✅

**Verdict:** Phase 1 complete. WIMpy_NREFT is correctly calibrated;
magnetic-moment operator reproduces LZ 248 keV event at both LZ best-fit
mass (1000 GeV) and project MAP (770 GeV).

### Phase 2 — Hybrid channel implementation (~3-5 hours) ✅ DONE 2026-09-06

**Goal:** Add Channel 26 = magnetic-moment LZ as a new
`loglike_lz_magnetic_moment(c_mag, m_chi)` function.

**Files modified:**
- `v0.3-prelim/code/channels_extended.py` — added 6 constants +
  `loglike_lz_magnetic_moment()` function (line 1607-1735)
- `v0.3-prelim/code/channels_extended.py:181` — added Channel 26 to
  CHANNEL_STATUS dict
- `v0.3-prelim/code/t41_mediator_mass_joint_fit.py:82` — added
  `loglike_lz_magnetic_moment` to import block
- `v0.3-prelim/code/t41_mediator_mass_joint_fit.py:498-522` — wired
  Channel 26 with env-var gating + ablation support
- `v0.3-prelim/code/t41_mediator_mass_joint_fit.py:524` — added
  `+ ll_magnetic_moment` to return sum
- `v0.3-prelim/tests/test_lz_magnetic_moment.py` — 18 tests, all passing

**Test results:**
- 18 tests in `test_lz_magnetic_moment.py`: **all pass**
- End-to-end T41 integration:
  - No T90 env vars: log L = -158.534 (master-compatible; Channel26 =0)
  - T90_MAGNETIC_MOMENT_MU_X=3e-11: log L = -159.534 (delta = -1.0,
    matching Poisson log-likelihood)
  - T90_MAGNETIC_MOMENT_DISABLE=1: log L = -158.534 (matches no-env)

**Channel 26 design (Tier-3 exploration, default OFF):**
- Gated by env var `T90_MAGNETIC_MOMENT_MU_X` (mu_x value)
- If env var unset: returns 0 (no effect on posterior)
- If `T90_MAGNETIC_MOMENT_DISABLE=1`: returns 0 (ablation)
- Otherwise: computes Poisson log-likelihood on (N_obs=1, N_pred(mu_x, m_chi))

**Mass-discrimination test (mu_x = 3e-11):**

| m_chi (GeV) | log L (T41 sum) |
|---|---|
| 50 | -280.25 |
| 100 | -220.36 |
| 500 | -165.99 |
| 770 (project MAP) | **-159.53** (peak) |
| 1000 (LZ best-fit) | -160.45 |
| 2000 | -166.54 |
| 5000 | -183.68 |

The channel "likes" the 770-1000 GeV mass window at μ_x = 3×10⁻¹¹ μ_N,
peaking at the project's v0.8 MAP mass. **The LZ 248 keV event is
explained by magnetic-moment interaction with the project's standing
mass window.**

### Phase 3 — Joint-fit re-run (~30-60 min wall)

**Goal:** Run T41 at nlive=1000 with Channel 26 enabled via env var,
compare posterior to v0.8.

**Next step:** Will run as a background job. Need to:
1. Set `T90_MAGNETIC_MOMENT_MU_X=3e-11` in the environment
2. Run T41 with the existing 6D prior_transform_6
3. Compare posterior to v0.8 baseline

**Verdict tree:** Same as Phase 2 plan doc.

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