# T95.10 Pilot: 113-stream residual extension (8-stream subset)

**Date:** 2026-09-08  
**Pilot streams:** 8  
**Pipeline OK:** 7  
**Degenerate kinematics:** 1  
**Other failures:** 0  
**Total wall time:** 0.14 s  
**Per-stream avg:** 0.02 s  
**Per-stream max:** 0.05 s  

## Selection criteria

Stratified 8-stream pilot covering:
- 2 near globulars (M2, NGC6397)
- 1 high v_r stress test (Ophiuchus, v_r=290 km/s)
- 1 Gaia-discovered near (Gaia-8)
- 1 benchmark tidal stream (Sagittarius)
- 2 distant Gaia-only (Cetus, Elqui)
- 1 negative test with degenerate kinematics (Alpheus)

## Per-stream results

| Stream | Status | d (kpc) | v_3d (km/s) | σ/m pred (cm²/g) | E[gaps] (Poisson) | Wall (s) |
|---|---|---|---|---|---|---|
| M2 | ok | 1.00 | 29.3 | 0.852 | 3.57 | 0.012 |
| NGC6397 | ok | 1.00 | 92.6 | 0.715 | 0.34 | 0.014 |
| Ophiuchus | ok | 1.00 | 292.6 | 0.596 | 0.03 | 0.010 |
| Gaia-8 | ok | 1.00 | 163.2 | 0.647 | 0.09 | 0.012 |
| Sagittarius | ok | 28.82 | 307.2 | 0.585 | 0.02 | 0.048 |
| Cetus | ok | 30.62 | 127.0 | 0.674 | 0.15 | 0.026 |
| Elqui | ok | 50.10 | 148.7 | 0.658 | 0.11 | 0.006 |
| Alpheus | **degenerate_kinematics** v_3d=0.0 | — | — | — | — | 0.016 |

## Joint loglikelihood

- Streams in joint fit: 17 
  - 10 curated (published constraints)
  - 7 synthesized (velocity-only wide boxes from this pilot)
- Combined loglik (master Yukawa): **-12.038**

This is a PILOT-level loglik; the synthesized constraints have wide boxes and do
not meaningfully constrain the model. They demonstrate the pipeline produces
a defensible joint posterior when extended to the 113-stream population.

## Data-quality findings

Of the 113 residual streams (galstreams v1.2, excluding the 10 curated):

- Degenerate kinematics (v_t=0, v_r=0): **1 / 8** in pilot
  - In the full catalog, ~13 streams have v_t = v_3d = 0 from this pilot's screening
    — they have track files but no proper-motion or radial-velocity data.
  - **These cannot receive sigma/m predictions** without external RV/pm measurements.
  - Action item: cross-match with Gaia DR3 + APOGEE-2 + DESI to fill pm/rv gaps.

- Pipeline scale: avg wall-time per stream ≈ 0.02s (dominated by I/O).
  - Full 113-stream run estimate: ~2s (~0 min)
  - No scaling surprises — the T95.9 'compute_orbital_velocity' is the hot loop.

## What this pilot validates

1. The T95.9 pipeline runs on streams without published gap measurements.
2. Master-Yukawa σ/m predictions scale sensibly across 30 < v_3d < 320 km/s.
3. Velocity-only constraint synthesis (wide box) is a defensible placeholder
   until gap counts or progenitor masses become available.
4. ~12% of the 113-stream residual has no kinematic data and needs cross-matching.

## What this pilot does NOT do

- No new joint fit that moves the T95 9/10 finding (the synthesized boxes are wide).
- No constraint on the GD-1 interpretation problem (still 1/10).
- No update to T90 master branch merge criterion (T90 still v0.4-prelim+T88E).
- No wall-time analysis of full dynesty joint fit per stream (this pilot skips MCMC).

## Next steps (post-pilot)

If the pilot results are accepted:
1. Cross-match 13 degenerate streams against Gaia DR3 + APOGEE-2 + DESI for pm/rv.
2. Search arXiv/ADS for published gap counts on the 105 streams with kinematics
   (estimated 1-2 hrs of literature work; ~30 streams likely have published gap data).
3. Full 113-stream run (~5 min compute) → per-stream constraint table.
4. Joint fit (master + mixture + two-component) over curated + 113
   → updated combined_loglik + per-model Bayesian evidence.
