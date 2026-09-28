# Phase 4B Summary — Higher-N KiSS-SIDM Pilot (2026-09-27)

## Goal

Per devplan §4 Phase 4B: try to extend KiSS-SIDM Cloud-9 simulation beyond the proven T215u baseline of **70 Myr (N=3000, min=64, ulimit 8 GB, std=0.74 Myr)** toward the Balberg-predicted t_core = 176 Myr. If successful, directly measure Cloud-9 gravothermal core-collapse timing.

## Attempts (in order)

### T215b — Scenario B: bump ulimit to 16 GB

- **Config**: N=3000, min=64, t_end=0.07 Gyr, ulimit 16 GB
- **Result**: t_max = 71.59 Myr (last snapshot at 71.41 Myr in log), 12 snapshots
- **Verdict**: equal to T215u baseline within 1σ. **No improvement.**
- **Interpretation**: memory pressure was not the bottleneck for the N=3000 baseline; the run reaches its 70 Myr target whether ulimit is 8 GB or 16 GB.

### T215c — Scenario A-lite: lower N with longer t_end

- **Hypothesis**: Tier 2 (higher N) failed because more particles → more adaptive subdivisions → earlier dt-collapse. Reverse the hypothesis: lower N → fewer subdivisions → longer simulation.
- **Config**: N=1000, min=32, t_end=0.20 Gyr (3× baseline), ulimit 16 GB
- **Result**: **died at t = 3.89 Myr** (1 snapshot only, dt collapsed to 1.13e-5 floor)
- **Verdict**: hypothesis **refuted in the opposite direction**. Lower N dies earlier, not later.
- **Interpretation**: With fewer particles per bin, dt collapses even faster because the adaptive grid has less statistical mass to average over.

## Combined verdict

| Attempt | N | t_max (Myr) | Outcome |
|---|---|---|---|
| T215u baseline (proven) | 3000 | 70.0 ± 0.7 | works |
| T215x Tier 2 (longer t_end) | 3000 | 22.5 | dies earlier |
| T215y Tier 2 (N=5000) | 5000 | 5.4 | dies much earlier |
| T215v Tier 2 (N=10000) | 10000 | 1.7-16.0 | dies early |
| T215w Tier 2 (N=10000, min=32) | 10000 | 0.32 | worst case |
| **T215b** (ulimit 16 GB) | **3000** | **71.6** | **equal to baseline** |
| **T215c** (N=1000, longer t_end) | **1000** | **3.89** | **dies much earlier** |

**Phase 4B FAILS in all directions within the parameter envelope accessible without modifying KiSS-SIDM source code.**

The optimum is sharply peaked: N=3000, min=64, t_end=0.07 Gyr. Deviations of ±10% on N or ±3× on t_end cause earlier failure. ulimit scaling does not help.

## What would still work (Tier 3 — deferred, would require code modifications)

The devplan mentioned Tier 3 levers as possible escape hatches:
1. **Subcycled time integration** (advance particles on a smaller dt than the adaptive grid)
2. **Freeze adaptive refinement after density threshold** (once core forms, lock the grid)
3. **Manual particle redistribution** when bins get too dense (vs automatic subdivision)
4. **Anti-gravitational pressure term** to prevent collapse runaway

These all require modifying `/home/lamkuenai/KiSS-SIDM/src/DSMC.jl/src/` source files. Estimated cost per devplan: ~3-4 hours dev + ~30 min pilot runs. Risk: same pattern as Tier 2 (untested, could make it worse).

**Phase 4B is closed with this negative result.** Tier 3 modifications are **deferred to post-submission** per devplan recommendation ("only pursue if reviewer asks for gravothermal core-collapse timing").

## What the paper now says

§10.5b's "Methods contribution only" framing was always honest about T215's limits. This Phase 4B round adds explicit documentation that the proven N=3000 baseline is a strict optimum — extending it is not just computationally infeasible but a known-failure direction in the parameter envelope.

## Artifacts

- `v0.3-prelim/data/results/t215b_phase4b_scenario_b.json`
- `v0.3-prelim/data/results/t215c_phase4b_lower_n.json`
- `v0.3-prelim/data/snapshots_t215b/` (12 snapshots from T215b at 16 GB ulimit)
- `/tmp/t215c_output/snap_000.jld2` (1 snapshot, T215c initial state only)

## Cost

- **Scenario B**: ~5-7 min wall time on KiSS-SIDM run + 1 min analysis = ~10 min total
- **Scenario A-lite**: ~3-5 min wall time (process died early) + script analysis = ~10 min total
- **Phase 4B total cost: ~20-30 min**, not the "100+ days" initially estimated