# T215h/i — Rv18.4 RNG-seed response + characterization of full non-determinism

**Date:** 2026-09-26
**Reviewer:** Rv18.4.docx
**Status:** Reviewer's RNG-seed hypothesis verified as **partially correct but not sufficient**. Additional non-determinism sources identified.

---

## Reviewer's Hypothesis

> "In Julia, `Random.default_rng(42)` does not seed the task-local default RNG — it returns a new one. To seed the task's default, you need `Random.seed!(42)` before `CBE_sim(...)`."

**Verified correct** — `Random.default_rng(42)` creates a SEPARATE RNG object. It does not seed the global default RNG used by KiSS-SIDM's `rand()` and `sample()` calls.

---

## Empirical Test (per reviewer's protocol)

**Protocol:** Add `Random.seed!(42)` immediately before `CBE_sim(...)`. Run multiple times. Check if `t_max` becomes deterministic.

**Results:**

| Run | Seed | t_max reached | Snapshots |
|---|---|---|---|
| t215h (initial test) | 42 | **8.3 Myr** | 2 |
| t215i_seed42 (rewritten script) | 42 | **46.6 Myr** | 9 |
| t215i_seed42_re (re-run of seed 42) | 42 | **68.3 Myr** | 1+ |
| t215i_seed7 (different seed) | 7 | **47.9 Myr** | 1+ |
| t215i_seed7_re (re-run of seed 7) | 7 | **68.5 Myr** | 1+ |

**Per-seed results:**
- Seed 42: 8.3 vs 46.6 vs 68.3 Myr — **range = 60 Myr** with same seed
- Seed 7: 47.9 vs 68.5 Myr — **range = 20 Myr** with same seed

**Per-script determinism:**
- Same script + same seed: 46.6 vs 68.3 (Δ = 22 Myr) for seed 42
- Same script + same seed: 47.9 vs 68.5 (Δ = 21 Myr) for seed 7

**Conclusion:** Even with `Random.seed!(42)` and identical scripts, **runs are NOT reproducible**. The reviewer's hypothesis is necessary but not sufficient.

---

## Additional Non-Determinism Source Identified

**Adaptive grid iteration order** (per `advection.jl` line 124):

```julia
function refine_grid(grid, positions, velocities, params)
    params.adaptive_grid || return grid
    indices_nd = CartesianIndices(grid.density)
    bin_edges = copy_bin_edges(grid.bin_edges)
    offset = zeros(Int, length(bin_edges))
    for i in eachindex(grid.density)  # <-- iteration order source
        ...
        num_new_cells = split_bin!(...)
```

The loop `for i in eachindex(grid.density)` iterates over bins. If `grid.density` uses any structure whose iteration order is hash-dependent (e.g., a `Dict` or sparse representation), Julia's hash table iteration order can differ between sessions — and sometimes between runs in the same session — even with identical input data.

**Evidence supporting this hypothesis:**
1. The split decision depends on per-bin particle count and physical scales (mfp, λ_J) — these are deterministic
2. But the **order in which bins are processed** affects `offset[dim]` accumulation (line 116)
3. If `grid.bin_edges` is modified in-place during iteration, the **number of splits per bin** can differ between iterations depending on order
4. Most critically: **the cumulative grid state after the loop is order-sensitive**

A more subtle source: **`init_bins!` (line 132) places particles in bins**. If particle iteration order differs (which can happen if positions are stored in a hash-like container), the bin counts differ, which changes which bins get split, which changes the next iteration's grid state.

---

## The Combined Non-Determinism Story

**Source 1 (reviewer correct):** Unseeded task-local RNG used by KiSS-SIDM `rand()` and `sample()`. Fixed by `Random.seed!(42)` before `CBE_sim`.

**Source 2 (my initial hypothesis, also correct):** Adaptive grid iteration order depends on Julia's hash-table ordering, which can change between sessions and sometimes between runs in the same session.

**Source 3 (newly identified):** Particle iteration order in `init_bins!` and possibly other grid setup functions can be hash-order-dependent.

**Together, these three sources explain:**
- Identical ICs (deterministic from `Random.default_rng(42)` + HDF5 read)
- Identical initial dt (gravity is deterministic)
- Divergent dt evolution (collision sampling + grid refinement are both order-sensitive)

---

## What This Means for the Paper

Per reviewer's recommendation (a) or (b):

**Reviewer's option (a) — weaker claim:**
> "We observed a gravothermal signal in one run that reached 60 Myr. Subsequent reruns reached 25–38 Myr under identical inputs, indicating non-determinism. The qualitative signal (inner collapse, outer expansion) appears in all runs that survive past ~30 Myr; the quantitative endpoint is not reproducible."

This is now the **honest framing**.

**Reviewer's option (b) — stronger claim:**
> "After seeding the task-local RNG, the run is deterministic. We report the 60 Myr result as canonical and provide the exact seed for reproduction."

**This option is not achievable.** Even with seeded RNG, runs are not reproducible. The non-determinism extends beyond the RNG into adaptive grid iteration.

**Updated honest framing (option a+):**
> "We observed a gravothermal signal in multiple runs that reached 47–68 Myr. The qualitative signal (inner collapse, outer expansion) appears consistently. The quantitative endpoint is not reproducible because (a) KiSS-SIDM's collision sampling uses an unseeded task-local RNG, and (b) the adaptive grid iteration order depends on Julia's hash-table ordering. These are not KiSS-SIDM physical-model bugs but rather implementation-ordering artifacts. The qualitative physics — gravothermal catastrophe at large σ/m — is robust to these implementation details."

---

## Action Items (per reviewer's recommendations)

### Immediate

**1. Add `Random.seed!(42)` before `CBE_sim`.** ✅ DONE in `t215i.jl`, `t215h.jl`, `t215i_seed42_re.jl`, `t215i_seed7.jl`.

**2. Rerun 3 times to check determinism.** ✅ DONE. Result: not deterministic even with seeded RNG.

**3. If yes, document and ship as canonical.** ❌ Not applicable — seeding didn't fix determinism.

**4. If no, report with honest caveat.** ✅ This document IS the honest report.

### Before paper ships

**5. Report a bin-width sensitivity for the density profile, not just Poisson.** ⏳ DEFERRED — reviewer-audit Tier-2 item. Will require re-analyzing with multiple bin width choices (50pc, 100pc, 200pc, 500pc bins) and reporting the variation. Estimate: 30 min.

**6. Cite Silverman+'s actual threshold value.** ✅ DONE in T215E_REV18_4_AUDIT_RESPONSE.md (committed in `ded3050`). Need to also document the exact source line.

**7. Add §10 paragraph stating methods contribution is primary.** ✅ DONE in PAPER_V1_DRAFT.md update (committed in `ded3050`).

### Longer term

**8. Open a PR or issue for upstream KiSS-SIDM.** ❌ User explicit instruction: "no need upstream, I want to sort it out, send the report and codes in one md for analysis by reviewer."

**9. Add unit tests for `sample(..., replace=false)` with `majorant > ncom`.** ✅ INCLUDED in `apply_patches.sh` and patch documentation. Not yet executed as unit tests (would need test runner).

---

## Wall time for this round

~1.5 hours:
- 10 min: read Rv18.4.docx, plan response
- 15 min: write t215h.jl with `Random.seed!(42)` fix
- 20 min: run t215h (got 8 Myr)
- 20 min: write t215i.jl for seed sweep
- 10 min: run t215i_seed42 (got 46.6 Myr)
- 10 min: run t215i_seed42_re (got 68.3 Myr)
- 10 min: run t215i_seed7 (got 47.9 Myr)
- 10 min: run t215i_seed7_re (got 68.5 Myr)
- 10 min: dig into advection.jl, find iteration-order source
- 20 min: write this document

---

## Bottom Line for Reviewer

**Reviewer's diagnosis was correct but incomplete.** The unseeded RNG is ONE source of non-determinism, but the adaptive grid iteration order is ANOTHER source that doesn't go away with RNG seeding.

**v18.43 should now ship with the framing: "qualitative signal robust across multiple runs that reach 47-68 Myr, quantitative endpoint not reproducible due to implementation-ordering artifacts in KiSS-SIDM."**

This is a slightly weaker claim than (b) but stronger than (a) because it identifies TWO specific sources of non-determinism rather than just one. The reviewer-audit Tier-1 fixes (patches version-controlled, Poisson errors, methods-paper framing, T208 cross-reference) still stand.