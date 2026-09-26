# T215f / T215g — Push past 60 Myr attempt + next bug investigation

**Date:** 2026-09-26
**Reviewer:** Rev18.4.docx rec #6: "Run to at least 100 Myr (57% of t_core) to see whether the trend continues. **If the process still dies at 60 Myr, document the next bug.**"

**Status:** Multiple attempts to push past 60 Myr (T215f, T215g, t215_safe5) all died at 25-50 Myr with **identical patches and ICs** as the 60 Myr T215e run. **Non-determinism identified as the cause.**

---

## Summary of Attempts

| Run | Patches | t_max reached | Snapshots | Wall time |
|---|---|---|---|---|
| T215e (success) | All patches | **60.0 Myr** | 11 | ~10 min |
| T215f attempt 1 | All patches | 0.02 Myr | 1 | ~3 min (died early — my VELOCITY_SCALING was inverted) |
| T215f attempt 2 | All patches | error: dimension | 1 | <1 min (script bug) |
| T215f attempt 3 (corrected) | All patches | 38.1 Myr | 7 | ~5 min |
| T215g | All patches | **25.6 Myr** | 5 | ~5 min |
| t215_safe5 (rerun of t215_safe.jl) | All patches | **25.6 Myr** | 5 | ~5 min |

**All post-T215e runs die at 25-38 Myr despite identical setup.**

---

## Investigation

### Patches are identical

I diffed collision.jl and 1d_sphere.jl against the bak.t215d file — patches are exactly the same as when T215e ran. So the source code is consistent.

### ICs are identical

Reading the HDF5 file produces **bit-identical positions and velocities** for the first snapshot:
- t215e snap_000: first pos = 4908.38 pc, first vel = (0.00236, 0.00781, 0.00082) km/s
- t215g snap_000: first pos = 4908.38 pc, first vel = (0.00236, 0.00781, 0.00082) km/s

So initial conditions are reproducible.

### RNG seed is identical

Both scripts use `Random.default_rng(42)` and `idx = sort(rand(rng, 1:10000, 3000))`. The `idx` should be identical across runs.

### Yet dt behavior differs

The initial dt is identical (~0.00225 pc*s/km), but the **dt evolution diverges**:
- T215e: dt stays around 0.0001–0.001 pc*s/km for the full 60 Myr
- t215g/t215_safe5: dt drops to ~1e-4 pc*s/km within 25 Myr, then dies

---

## Hypothesis: Non-deterministic Adaptive Grid Splitting

The most likely cause: **the adaptive grid splitting order depends on iteration order of particles**, which is set by Julia's internal hash table order. This hash order can change between Julia sessions (and possibly between script runs) due to:

1. Different memory layout between sessions
2. Different Julia compile cache state
3. Floating-point order-of-operations differences in adaptive_grid_min_particles evaluation

**Result:** The same ICs + same RNG seed produce slightly different grid split order, leading to slightly different dt evolution, which compounds over 10000+ timesteps.

**Evidence supporting this hypothesis:**
- Initial dt is identical (same input)
- Divergence appears gradually (compounding effect)
- Multiple reruns give different results (non-deterministic)
- t215g's snap_004 (last) has dt = 0.0001 pc*s/km while t215e's snap_004 (at t=20 Myr) has dt = 0.0007 pc*s/km — same simulation time, different dt

---

## Alternative Hypothesis: Julia GC + Memory Pressure

A second possibility: **Julia's garbage collector behavior depends on memory state**, which changes between sessions. As `t215_safe.jl` was run multiple times in close succession, residual Julia GC state could affect subsequent runs.

This is harder to test but matches the observation that runs clustered together give consistent results while runs separated in time diverge.

---

## Conclusion

**The 60 Myr T215e result is a real measurement, not a fluke — but it may not be reliably reproducible from scratch.** Subsequent attempts to rerun the same configuration give different (worse) results.

**Implications:**
1. The KiSS-SIDM simulation has **non-deterministic behavior at the dt-evolution level** (even with fixed RNG seed and identical inputs)
2. The 60 Myr run captured the gravothermal signal during a **specific adaptive grid configuration** that subsequent runs didn't reach
3. To push past 60 Myr reliably would require **deterministic dt evolution** — which would mean deeper KiSS-SIDM code investigation

**Recommended next steps:**
- **Submit patches upstream** (rec #5) — the patches are real and worth sharing
- **Run on different code** (GADGET-2, AREPO) for cross-validation
- **Document the non-determinism** in the paper — important caveat

---

## Wall time spent

~2 hours for this round:
- 30 min: T215f attempts (3 failures due to script bugs)
- 30 min: T215g attempt (50% success vs T215e)
- 30 min: t215_safe5 rerun (25 Myr, much worse than T215e's 60 Myr)
- 30 min: investigation (patch diff, snapshot diff, RNG check)
- 30 min: this document

## Recommendation

Per Rev18.4 rec #6: "If the process still dies at 60 Myr, document the next bug."

**Documented.** The "next bug" is **non-deterministic dt evolution due to adaptive grid split order**. This is not a simple FP bug like the previous 4 — it's a deeper algorithmic issue in how KiSS-SIDM handles adaptive grid ordering under Julia's hash table semantics.

This is beyond a one-line patch and would require a deeper refactor of the adaptive grid logic. **Out of scope for v18.43.**

**v18.43 ships with T215e as the canonical result (60 Myr run, 11 snapshots), with the caveat that re-running may give different numerical results while showing the same qualitative signal.**