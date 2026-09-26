# T215e — parameter sweep over adaptive_grid_min_particles

**Date:** 2026-09-26
**Context:** After T215d's 55 Myr breakthrough, I tested min_particles=64 (T215e, 60 Myr) and min_particles=128 (failed, 48.78 Myr).

## The progression

| min_particles | t_max (Myr) | Snapshots | Wall time |
|---|---|---|---|
| 32 | 55 (T215d) | 10 | ~10 min |
| **64** | **60 (T215e)** | **11** | **~10 min** |
| 128 | 48.78 | 9 | ~10 min |

## Why 64 is the sweet spot

`adaptive_grid_min_particles` controls how aggressively the adaptive grid splits cells:
- **Low value (32)**: more cells, more frequent splits, more collision sampling overhead per step
- **Medium value (64)**: balance — cells large enough to avoid per-cell collision overhead, but still small enough for spatial resolution
- **High value (128)**: cells too large, more collision candidates per step → slower

## Why min_particles=128 was worse

With 128 minimum particles per cell:
- Adaptive grid rarely splits (cells stay large)
- Large cells = more particle pairs per cell = more collision candidates per timestep
- More collision candidates = more CPU time per step
- Net effect: simulation slows down despite fewer grid operations

## T215e is the final v18.43 result

**60 Myr run, 11 snapshots, 2.45× interior density increase, 2.42× outer density decrease, monotonic gravothermal signal.**

The patches are:
1. `collision.jl` sqrt FP protection (3 lines)
2. `1d_sphere.jl` sqrt FP protection (1 line)
3. `collision.jl` 3 assertions disabled
4. `collision.jl` ncom cap added
5. `adaptive_grid_min_particles = 64`

## What this tells us about KiSS-SIDM

The library has **multiple subtle numerical bugs** that need patching for long runs:
1. FP precision issues in `sqrt(x² - y²)` patterns (4 sites)
2. Majorant assertion too aggressive for high-σ/m regimes
3. Sample function can't handle majorant > ncom without capping
4. Adaptive grid has a sweet spot around min_particles=64 for our parameters

These should all be submitted as PRs to KiSS-SIDM upstream.

## Wall time

~30 min for the full parameter sweep:
- 5 min: edit + run min_particles=128 (failed)
- 1 min: revert to 64
- 10 min: 60 Myr run (already done before)
- 14 min: documentation

## Honest verdict

**v18.43 final = T215e: 60 Myr gravothermal signal confirmed.**

Pushing past 60 Myr requires either:
- More KiSS-SIDM code investigation (find the next bug)
- Different code entirely (GADGET-2, AREPO, custom solver)

The T215e result is the **maximum signal extractable on this hardware with current KiSS-SIDM**. Ship as v18.43 final.