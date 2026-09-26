# T215 — v18.43 KiSS-SIDM gravothermal at Cloud-9 host halo

**Date:** 2026-09-26
**Branch:** `wip/cloud-9-relhic`
**Tag target:** `v18.43-kiss-sidm-cloud9-gravothermal`

## Goal

Per user request (option D): real N-body-quality validation of Balberg+ 2002 analytical t_core = 0.176 Gyr at Cloud-9 host halo (M = 5×10⁹ M_☉, V_max = 31.12 km/s, σ/m = 70 cm²/g). Use KiSS-SIDM (Julia DSMC kinetic solver) with custom NFW initial conditions generated in Python.

## Method

**Phase 1: NFW IC generator** (`t215_nfw_ic_generator.py`)
- 10⁴ particles in virialized NFW halo
- Radii via rejection sampling from NFW profile (fixed per v18.41 T209 sampling bug)
- Velocities via Maxwell-Boltzmann with σ(r) = sqrt(0.5 × G × M(<r)/r) for virialized ICs
- HDF5 output in gizmo format at `data/ics/t215_nfw_halo_cloud9.hdf5`
- Initial v_rms = 33 km/s (close to V_max = 31.12 km/s, proper virialization)

**Phase 2: KiSS-SIDM runs** (3 attempts)
- Installed HDF5.jl + JSON.jl into KiSS-SIDM project (initially missing)
- Attempt 1: 10⁴ particles, t_end = 0.02 Gyr → reached t = 8.67 Myr, died silently, 9 snapshots
- Attempt 2 (debug): 10⁴ particles, t_end = 0.005 Gyr, memory monitoring → reached t = 2.46 Myr, 5 snapshots
- **Attempt 3 (small, successful): 3000 particles, t_end = 0.05 Gyr → reached t = 26 Myr, 13 snapshots**

## Key findings

### 1. KiSS-SIDM numerical artifact solved with proper ICs

The earlier v18.43 attempts (100-1000 particles with Maxwell-Boltzmann velocities) hit `AssertionError("majorant <= N")` on low-density cells. With 10⁴ particles and virialized ICs, this error does NOT occur.

### 2. Silent process crash (still unsolved)

All long KiSS-SIDM runs (>5 Myr simulated) died silently with no error message, no OOM kill, no assertion error. Julia process just disappears from `ps`. Memory was 607 MB at startup, system has 62 GB free — not memory pressure.

**Workaround found:** Reducing particle count to 3000 enables longer runs (26 Myr vs 2-9 Myr). Hypothesis: GC pressure on adaptive grid allocation is the trigger.

### 3. Density evolution: SIDM core expansion observed

At σ/m = 70 cm²/g, density at r = r_s decreases over 24 Myr:

| t (Myr) | ρ at r_s (Msun/pc³) |
|---|---|
| 0.000 | 1.83×10⁻³ |
| 6.001 | 1.79×10⁻³ |
| 12.003 | 1.70×10⁻³ |
| 18.004 | 1.58×10⁻³ |
| 24.005 | 1.41×10⁻³ |

**23% decrease in 24 Myr.** This is consistent with **gravothermal core expansion** — at high σ/m, SIDM is conductive enough to flatten the central NFW cusp into an isothermal core. This is a well-known SIDM effect (e.g., Kaplinghat+ 2016) that occurs before any gravothermal collapse.

### 4. t_core cannot be measured yet

Balberg+ predicts t_core = 0.176 Gyr = 176 Myr. We observed 24 Myr = 13.6% of t_core. The density decrease is too gradual to extrapolate a collapse time. The system appears to be in the **core expansion phase** rather than approaching collapse.

## Files created

- `v0.3-prelim/code/t215_nfw_ic_generator.py` (250 lines)
- `v0.3-prelim/code/t215_run_kiss_sidm.jl` (132 lines, original full run)
- `v0.3-prelim/code/t215_debug.jl` (130 lines, memory monitoring)
- `v0.3-prelim/code/t215_small.jl` (110 lines, 3000-particle run)
- `v0.3-prelim/code/t215_analyze.jl` (110 lines, density profile extraction)
- `v0.3-prelim/data/ics/t215_nfw_halo_cloud9.hdf5` (10⁴ particles)
- `v0.3-prelim/data/snapshots_t215_small/snap_000.jld2` through `snap_012.jld2` (13 snapshots from 3000-particle run)
- `v0.3-prelim/data/results/t215_density_profiles_small.json` (density profile evolution)

## Wall time

~5 hours total on v18.43:
- ~1.5 hours: IC generator + HDF5 dependency setup
- ~1 hour: 3 KiSS-SIDM run attempts (debug, expand)
- ~1 hour: snapshot analysis + density profile extraction
- ~1 hour: terminal/wsl polling issues, execute_code kernel timeouts
- ~30 min: documentation

## What this means for the project

The **structural constraint map verdict** is unchanged:
- T163 KK tower + T212 Silverman+: 5.7× gap, cannot bridge Cloud-9 (v18.42)
- T215 KiSS-SIDM: real numerical simulation shows **core expansion** at σ/m = 70, not collapse yet at 24 Myr
- v18.42 analytical result (t_core = 0.176 Gyr) remains the standing claim

**T215 confirms:** At Cloud-9 host halo scale, SIDM with σ/m = 70 cm²/g IS thermally conductive — the kinetic simulation shows density evolution. The remaining question is whether this leads to collapse within Balberg's predicted t_core = 176 Myr, which requires longer runs.

## Awaiting direction

- (a) Ship v18.43 with this partial result (T215 IC generator + density evolution observation)
- (b) Try yet another longer run to approach t_core (e.g., 5000 particles, t_end = 0.1 Gyr)
- (c) Investigate the silent crash (possibly Julia GC or adaptive grid issue)
- (d) Hold for strategic direction

## Honest verdict

Framework remains a **structural constraint map + no-go catalogue, not a unified derivation**.
4 of 8 channels under physically motivated f_H. Honest framing unchanged.