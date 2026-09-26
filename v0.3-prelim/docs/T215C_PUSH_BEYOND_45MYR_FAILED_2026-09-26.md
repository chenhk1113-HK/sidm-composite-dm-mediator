# T215c — v18.43 pushing past 45 Myr (failed)

**Date:** 2026-09-26 (same day as T215b)
**Status:** Investigation of remaining bottlenecks. **Conclusion: 45 Myr is the practical limit on this host.**

## What I tried

After T215b's 45 Myr success, attempted to push to 100 Myr. Five strategies tried:

### Strategy 1: Remove `majorant ≤ N` assertions
- Hypothesis: assertion was the actual crash point
- Result: **WORSE** — without assertion, sample(..., replace=false) fails when majorant > ncom
- Reached only **3.22 Myr** (76k timesteps)

### Strategy 2: Cap `majorant` at `ncom` (line 72)
- Added `majorant = min(majorant, ncom)` before sample
- Result: **WORSE** — capped at unique pair count, reducing collision efficiency
- Reached only **21 Myr** (37k timesteps)

### Strategy 3: Switch to `replace=true` (line 72)
- Allows sampling beyond ncom (with replacement)
- Result: **MASSIVELY WORSE** — `min(N-1, ncom)` + repeat=true gives excessive collisions, slowing simulation
- Reached only **3.22 Myr**

### Strategy 4: Increase `adaptive_grid_min_particles` from 32 to 64
- Forces more particles per cell (fewer cells)
- Result: **42.84 Myr** — slightly worse than 45 Myr
- Hypothesis: at high σ/m, larger cells mean larger majorant → more time spent on collision sampling

### Strategy 5: Add `dt_init` keyword
- Hypothesis: forcing smaller initial timestep might prevent assertion
- **Failed** — `dt_init` is not a CBEParams field. MethodError.

## Why 45 Myr is the ceiling

The fundamental bottleneck is the **adaptive grid splitting + low-density cell physics**:
- As the system evolves, particles spread out
- Adaptive grid creates cells with varying densities
- Low-density cells with N=2-5 particles + high σ/m → majorant can exceed N
- Without proper handling, this either crashes (assertion) or runs inefficiently (cap)

The real fix would require a deeper refactor of KiSS-SIDM's cell-splitting logic, which is **out of scope** for v18.43.

## What v18.43 ships with

**T215b result: 45 Myr run, 9 snapshots, qualitative confirmation of gravothermal catastrophe.**

The 45 Myr ceiling is **good enough to demonstrate the qualitative physics** — center collapse + outer expansion — but not enough for direct quantitative t_core measurement.

## Wall time spent on (b)

~2 hours for this push attempt:
- 30 min: investigate post-45-Myr crashes
- 30 min: try assertion removal (strategy 1-3)
- 30 min: try adaptive grid parameter (strategy 4)
- 10 min: try dt_init (strategy 5, failed immediately)
- 20 min: documentation

## Files (no new commits, all in /tmp)

- `v0.3-prelim/code/t215c.jl` — script with all attempted modifications
- `/home/lamkuenai/KiSS-SIDM/src/DSMC.jl/src/collision.jl` — restored to T215b state (FP patches only)
- `/home/lamkuenai/KiSS-SIDM/src/DSMC.jl/src/collision.jl.bak.t215*` — backup chain

## Honest verdict

**v18.43 ships as T215b: 45 Myr, qualitative gravothermal validation.**

Pushing further requires either:
1. **KiSS-SIDM upstream fixes** (deeper refactor of cell-splitting logic)
2. **More compute** (cluster-scale, days of wall time)
3. **Different code** (write our own kinetic solver from scratch)

None of these are feasible on this laptop within a session budget. The T215b result is the **maximum signal we can extract on this hardware**.