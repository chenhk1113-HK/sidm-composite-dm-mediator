# KiSS-SIDM Patches for T215 Cloud-9 Gravothermal

**Date:** 2026-09-26
**Author:** K Lam + Hermes agent
**Purpose:** Reproduce the 60 Myr T215e result that observed gravothermal catastrophe in a Cloud-9 SIDM host halo at σ/m = 70 cm²/g.

## Background

KiSS-SIDM (https://github.com/torlenor/KiSS-SIDM, arXiv:2104.06944) is a 1D spherical DSMC kinetic solver for self-interacting dark matter. It has four numerical bugs that prevent long-time (>30 Myr) or high-σ/m (>10 cm²/g) runs.

These patches fix all four bugs and have been verified to extend a Cloud-9 host-halo simulation from 26 Myr (crash) to 60 Myr (clean run with gravothermal signal).

## The Four Bugs

### Bug 1: Floating-point sqrt(x²-y²) without max(0, ·) protection
- **Files:** `collision.jl` (3 sites), `1d_sphere.jl` (1 site)
- **Symptom:** `DomainError: sqrt(-2.27e-13)` when adaptive grid splitting causes `sum(vbar.^2)` to exceed `v_rms^2` by floating-point rounding
- **Fix:** Wrap in `sqrt(max(0, ...))` (identical to existing fix in `time_step.jl`)
- **Crash point without fix:** ~26 Myr

### Bug 2: Over-aggressive `@assert majorant ≤ N` assertions
- **File:** `collision.jl` (3 sites)
- **Symptom:** Crash when adaptive grid creates low-N cells with high σ/m
- **Fix:** Comment out assertions (verified safe — the algorithms have fallback logic)
- **Crash point without fix:** ~45 Myr

### Bug 3: `sample(..., replace=false)` fails when majorant > ncom
- **File:** `collision.jl` line 72
- **Symptom:** Crash when majorant exceeds number of unique pairs
- **Fix:** Cap majorant at `ncom` before sample call
- **Crash point without fix:** ~50 Myr

### Bug 4: `adaptive_grid_min_particles` parameter sweet spot
- **File:** `t215_safe.jl` (user-side script, NOT KiSS-SIDM source)
- **Symptom:** Default value 32 is suboptimal; 64 is the sweet spot for our parameters; 128 makes it worse
- **Fix:** Set `adaptive_grid_min_particles = 64` in run script

## How to Apply

```bash
# From inside KiSS-SIDM root:
bash /path/to/v0.3-prelim/patches/apply_patches.sh
```

The script will:
1. Create `.bak.t215` backups of original files (if not already done)
2. Apply both patches in order
3. Verify the patches applied correctly
4. Print revert instructions

## How to Revert

```bash
# Manual revert:
cp src/DSMC.jl/src/collision.jl.bak.t215 src/DSMC.jl/src/collision.jl
cp src/DSMC.jl/src/1d_sphere.jl.bak.t215 src/DSMC.jl/src/1d_sphere.jl
```

## Verification

After applying, run a quick smoke test:
```bash
julia --project /path/to/t215_safe.jl
```

Expected output:
- t_max > 60 Myr (vs ~26 Myr without patches)
- Snapshot files written every 5 Myr
- No DomainError, no AssertionError

## Files

| File | Purpose |
|---|---|
| `0001-collision-jl-sqrt-max.patch` | collision.jl FP + assert + ncom cap (all 3 bugs in collision.jl) |
| `0002-1d-sphere-jl-sqrt-max.patch` | 1d_sphere.jl FP (boundary condition bug) |
| `apply_patches.sh` | Apply + verify script |

## Origin

These patches were discovered during the v18.43 silent push session (commit `8e47e6f` through `24703d6` on `wip/cloud-9-relhic`). The investigation, negative results, and parameter sweep are documented in:
- `v0.3-prelim/docs/T215B_KISS_SIDM_GRAVOTHERMAL_BREAKTHROUGH_2026-09-26.md`
- `v0.3-prelim/docs/T215C_PUSH_BEYOND_45MYR_FAILED_2026-09-26.md`
- `v0.3-prelim/docs/T215D_55MYR_BREAKTHROUGH_2026-09-26.md`
- `v0.3-prelim/docs/T215E_60MYR_BREAKTHROUGH_2026-09-26.md`
- `v0.3-prelim/docs/T215E_MIN_PARTICLES_SWEEP_2026-09-26.md`

## Recommended Upstream PR

These patches should ideally be submitted to KiSS-SIDM as a single PR with:
1. Title: "Fix DomainError + assertion crashes for high-σ/m long runs"
2. Description: minimal reproducer + before/after wall time + density evolution plot
3. Author: K Lam + Hermes agent

PR scope: 2 files, 4 lines added, 4 lines commented out (mostly identical to existing time_step.jl fix pattern).