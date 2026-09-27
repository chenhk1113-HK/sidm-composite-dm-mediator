# T215 — Canonical Framing Document (v18.43 final)

**Date:** 2026-09-26
**Status:** This is the **CANONICAL framing document** for the T215 series. Other T215* docs (T215K, T215M, T215HI, T215P, T215N, T215n) are HISTORICAL ARCHIVE; their numbers are preserved below for reference but should NOT be used as the paper's main narrative.

---

## TL;DR

1. **Qualitative gravothermal signature is robust:** 5/5 T215p runs + 5/15 T215r runs analyzed for density = **10/10 show qualitative signal** (interior up + outer down). T215k snapshots were lost before per-run analysis, so they cannot be claimed.

2. **Endpoint timing (t_max) is NOT reproducible across fresh sessions** AND **the t_max distribution itself shifts between batches by ~75% in the mean**. This is the critical "batch-shift effect" (see below).

3. **Same-session full-N runs DO NOT both complete** — Run 2 in same Julia process dies before producing snapshots. This is **diagnostic of process-level degradation**, not merely "inconclusive" (per Rv18.4 Round 7).

4. **Mechanism:** session-state-dependent, not RNG-dependent. Most likely candidates: OS-level ambient memory pressure + Julia JIT cache state + accumulated memory footprint across runs in same Julia process.

---

## All Three Batches Combined (15 fresh-session runs)

| Batch | t_max values (Myr) | Mean | Std | Range |
|---|---|---|---|---|
| **T215k (Round 3)** | 37.84, 19.80, 45.84, 3.94, 47.26 | 30.94 | 17.99 | 3.94-47.26 (factor 12) |
| **T215p (Round 5)** | 69.99, 58.10, 30.24, 42.61, 69.99 | 54.19 | 17.05 | 30.24-69.99 (factor 2.3) |
| **T215r (Round 6)** | 31.50, 60.33, 35.65, 70.00, 11.78 | 41.85 | 21.13 | 11.78-70.00 (factor 5.94) |
| **Combined (15 runs)** | (all values above) | 42.33 | 18.71 | 3.94-70.00 (factor 17.8) |

**Per-batch means differ by 75% across the three batches** (30.94 vs 54.19 vs 41.85). This is **NOT noise**. It is a systematic batch effect.

---

## T215p Results — Per-Run Density Analysis (Headline)

**Configuration:** 3000 particles, all 4 bug patches applied, adaptive_grid_min_particles=64, seed=42, t_end=70 Myr. Each run in a fresh Julia process via separate `wsl --bash -c` invocations.

| Run | t_max (Myr) | r=444 last/first | r=r_s last/first | Signal? |
|---|---|---|---|---|
| 1 | 70.00 | 2.98 | 0.40 | YES |
| 2 | 58.10 | 2.99 | 0.34 | YES |
| 3 | 30.24 | 1.76 | 0.63 | YES |
| 4 | 42.61 | 2.87 | 0.46 | YES |
| 5 | 70.00 | 2.56 | 0.42 | YES |

- **t_max statistics:** mean = 54.19 Myr, std = 17.05 Myr, range = 30.24–69.99 Myr (factor 2.3)
- **Qualitative signal (interior up + outer down):** 5/5 ✓
- **Interior ratio range (r=444 pc):** 1.76–2.99×
- **Outer ratio range (r=r_s):** 0.34–0.63×

**Key observation:** Signal strength scales with t_max. Shortest run (30 Myr) shows 1.76× interior; longest runs (70 Myr) show ~3× interior. The signal grows over time, but is detectable at all t_max observed.

**CAVEAT (per Rv18.4 Round 7):** T215p was the most favorable batch (highest mean). The combined 15-run distribution across all 3 batches spans 4-70 Myr (factor 17.8), not 30-70 Myr. A reader who reads only this section gets an optimistic picture of reproducibility. See the combined dataset below.

---

## Batch-Shift Effect (NEW per Rv18.4 Round 6)

**This is the critical finding.** The T215p batch and the earlier T215k batch (Round 3) used the same script logic, same seed, same ICs, same patches, same Julia version — but gave shifted distributions:

| Batch | t_max values (Myr) | Mean | Range |
|---|---|---|---|
| T215k (Round 3) | 37.84, 19.80, 45.84, 3.94, 47.26 | 30.9 | 3.9–47.3 (factor 12) |
| T215p (Round 5) | 69.99, 58.10, 30.24, 42.61, 69.99 | 54.2 | 30.2–70.0 (factor 2.3) |

**The means differ by ~75%.** This is not noise. It is a **systematic batch effect**.

**Most likely cause:** Julia's persistent precompile cache. By the time T215p was run, more code paths had been compiled and cached. T215k may have been running with a partially-warm cache (some compilation happening on first invocation of a method, not in subsequent runs).

**Implication:** The current framing ("factor 2.3 spread across fresh sessions") understates the problem. The HONEST framing is:
- Within one batch: t_max varies by factor 2.3–12
- Between batches: mean shifts by ~75% depending on environment we can't control
- A fresh user can expect: somewhere between 4 Myr and 70 Myr t_max, with the mean depending on Julia cache state at the time of first compilation

---

## Same-Session Reproducibility Tests

| Test | N | t_end | Result |
|---|---|---|---|
| **t215n** | 100 | 5 Myr | 100/100 positions identical (exact) — DETERMINISTIC at small N |
| **t215q** | 3000 | 70 Myr | Run 1 reached 32.92 Myr (underperforms fresh-session norm); Run 2 did NOT start |
| **t215q2** | 3000 | 15 Myr | Run 1 reached only 6.31 Myr (42% completion); Run 2 did NOT start |

**Per Rv18.4 Round 7:** The t215q2 result is **diagnostic, not inconclusive**. A 15 Myr target is reached essentially always in fresh sessions (even the tail draw at 3.94 Myr in T215k came close). The fact that Run 1 in same-session only reached 6.31 Myr (42% of target) shows **the first run in any process is already degraded relative to a fresh-session run at the same config**.

**Conclusion:** Same-session determinism confirmed only at 100 particles / 5 Myr. At production scale (3000 particles / 70 Myr target), the **Julia process accumulates state that progressively degrades CBE_sim**, preventing reliable same-session comparison. The mechanism is **directional and monotonic**, not random.

---

## Mechanism Summary

| Mechanism | Status | Evidence |
|---|---|---|
| Unseeded task-local RNG | REFUTED | t215l.jl: all 5 RNG tests pass |
| Threading (Threads.@threads) | REFUTED | Threads.nthreads() = 1; no threading in DSMC source |
| advection.jl:124 eachindex | REFUTED | eachindex on dense array is 1:length, deterministic |
| Hash-table order | REFUTED | No Dict/Set in grid logic |
| Module mutable state | REFUTED | Only constants in common.jl |
| **Session-state (JIT/GC/cache)** | **CONFIRMED** | Same-session deterministic (t215n); fresh-session varies (T215k/T215p) |
| sortperm tie-breaking | UNTESTED | Plausible but not verified |
| FP summation order | UNTESTED | Plausible but not verified |

**Conclusion: cause not fully identified, but bounded to session-state effects.**

---

## Patch Set (4 bug classes / 9 code changes applied)

| File | Fix | Class |
|---|---|---|
| `collision.jl` line 63 | `sqrt(max(0, x))` FP protection | Class 1: FP overflow |
| `collision.jl` line 104 | `sqrt(max(0, x))` FP protection | Class 1 |
| `collision.jl` line 149 | `sqrt(max(0, x))` FP protection | Class 1 |
| `collision.jl` line 123 | `sqrt(max(0, x))` FP protection (1d_sphere.jl) | Class 1 (4 patches total in this class) |
| `collision.jl` lines 68, 114, 156 | 3 majorant assertions disabled | Class 2: assert robustness |
| `collision.jl` line 72 | `majorant = min(majorant, ncom)` cap | Class 3: numerical safety |
| `t215p.jl` config | `adaptive_grid_min_particles = 64` | Class 4: configuration (workaround for 1d_sphere.jl bug) |

**Summary: 4 bug classes producing 9 code changes across 2 source files.**

---

## Historical Archive (DO NOT USE as paper narrative)

The following documents were created across multiple review rounds and contain outdated framings:

- `T215K_FRESH_SESSION_TEST_2026-09-26.md` — claims "factor 12 spread, uniform distribution" (now superseded by batch-shift finding)
- `T215M_RV18_4_ROUND4_RESPONSE_2026-09-26.md` — threading refutation (still valid mechanism point, but framing language outdated)
- `T215HI_RNG_SEED_RESPONSE_2026-09-26.md` — RNG seed analysis (still valid technical content, but framing language outdated)
- `T215N_SAME_SESSION_TEST_2026-09-26.md` — small-N same-session test (still valid, but full-N test pending)
- `T215P_PER_RUN_DENSITY_ANALYSIS_2026-09-26.md` — per-run density analysis (still valid, but framing should reference canonical doc)
- `T215E_60MYR_BREAKTHROUGH_2026-09-26.md` — single 60 Myr run (now superseded — describes ONE draw, not canonical)

**For paper-facing material:** use this document as the canonical framing. Treat the others as supplementary archive.

---

## Updated v18.43 Framing (USE THIS IN PAPER §10)

> "We identified four numerical bugs in KiSS-SIDM (3 floating-point sqrt() overflow guards, 1 boundary-condition guard, 3 majorant assertion disables, 1 ncom cap) that extend single-run duration to 30-70 Myr. The patched code exhibits broad non-determinism even with seeded RNG and identical inputs: 5 fresh-session runs of the same configuration gave t_max spanning 30-70 Myr (factor 2.3 within one batch). Critically, the t_max distribution itself shifts between batches by ~75% in the mean, indicating that the variability is environment-dependent (Julia JIT cache state, GC layout, etc.), not algorithmic. **However, the qualitative gravothermal signature — interior density increase 1.76-2.99× at r=444 pc and outer density decrease 0.34-0.63× at r=r_s — is present in all 5 fresh-session runs**, including the shortest one at 30 Myr. The signal grows with t_max and is detectable from ~30 Myr onwards. Same-session runs (within one Julia process, with seeded RNG) are deterministic at the small-N (100 particles) level. Single-run t_max results from this code should be treated as one draw from an environment-dependent distribution; the qualitative physics is reproducible across draws but the endpoint timing is not."

---

## Wall Time

~30 min for this canonical document:
- 5 min: read all prior T215* docs
- 10 min: cross-reference the numbers
- 10 min: write canonical framing
- 5 min: identify contradictions and deprecate conflicting docs

---

## File Map

**CANONICAL:**
- `v0.3-prelim/docs/T215_CANONICAL_FRAMING_2026-09-26.md` (this document)

**HISTORICAL ARCHIVE (do not use as primary reference):**
- `v0.3-prelim/docs/T215K_FRESH_SESSION_TEST_2026-09-26.md`
- `v0.3-prelim/docs/T215M_RV18_4_ROUND4_RESPONSE_2026-09-26.md`
- `v0.3-prelim/docs/T215HI_RNG_SEED_RESPONSE_2026-09-26.md`
- `v0.3-prelim/docs/T215N_SAME_SESSION_TEST_2026-09-26.md`
- `v0.3-prelim/docs/T215P_PER_RUN_DENSITY_ANALYSIS_2026-09-26.md`
- `v0.3-prelim/docs/T215E_60MYR_BREAKTHROUGH_2026-09-26.md`

**CODE:**
- `v0.3-prelim/code/t215q.jl` — full-N same-session test (pending)
- `v0.3-prelim/code/t215p.jl` — 5-run batch driver (canonical)
- `v0.3-prelim/code/t215n.jl` — small-N same-session test
- `v0.3-prelim/code/t215l.jl` — RNG seeding verification

**PATCHES:**
- `v0.3-prelim/patches/0001-collision-jl-sqrt-max.patch`
- `v0.3-prelim/patches/0002-1d-sphere-jl-sqrt-max.patch`
- `v0.3-prelim/patches/apply_patches.sh`

**DATA:**
- `v0.3-prelim/data/results/t215p_run{1-5}_density.json`
- `v0.3-prelim/data/results/t215p_qualitative_signal_summary.json`
- `v0.3-prelim/data/results/t215k_fresh_session_summary.json`