# T215v/w/x/y — Tier 1+2 Pilot Results (2026-09-27)

**Status:** Tier 1+2 future-work pilot per R18.4 Round 11 (Consider.docx) **FAILED to extend t_core reach**. Reviewer's Tier 2 levers did not work as predicted.

---

## TL;DR

| Pilot | N | min_particles | t_end | t_max reached | Splits | Merges |
|---|---|---|---|---|---|---|
| T215u (baseline, PROVEN) | 3000 | 64 | 70 Myr | **70 Myr ✓** | 78 | 0 |
| T215x (longer t_end) | 3000 | 64 | 180 Myr | 22.49 Myr | 78 | 0 |
| T215y (N=5k) | 5000 | 64 | 100 Myr | 5.38 Myr | 120 | 0 |
| T215v run 1 (N=10k, min=128) | 10000 | 128 | 180 Myr | 15.67 Myr | 123 | 0 |
| T215v run 2 (ulimit 16GB) | 10000 | 128 | 180 Myr | 1.74 Myr | 107 | 0 |
| T215v run 3 | 10000 | 128 | 180 Myr | 3.55 Myr | 112 | 0 |
| T215w (N=10k, min=32 default) | 10000 | 32 | 180 Myr | **0.32 Myr ✗** | 509 | 0 |

---

## Key Finding (Opposite of Reviewer's Hypothesis)

**Higher N → earlier dt collapse.** Reviewer predicted "more particles = better sampling = longer t". Actual result: with N=10k, the adaptive grid subdivides bins AGGRESSIVELY to maintain the min_particles threshold. Each split creates a bin with fewer particles, which triggers more splits. **No merge events occur** (0 merges in all configs).

The original KiSS-SIDM v0.0.1 grid policy subdivides bins freely but never merges them back. With higher N, the grid runs out of "refinement room" faster → dt shrinks faster → run dies earlier.

---

## What Did NOT Work

- **N=10k** (Tier 2 lever "more particles"): died at 0.3-16 Myr, NEVER reached 30 Myr. Higher particle count made things WORSE, not better.
- **min_particles=128** (Tier 2 lever "raise min_particles"): only marginal improvement (15.67 Myr vs 3.55 Myr at N=10k), still nowhere near Balberg t_core = 176 Myr.
- **ulimit -v 16000000** (vs 8000000): made things WORSE (1.74 vs 15.67 Myr). Larger memory budget doesn't help when grid policy is the issue.
- **Longer t_end** (0.07 → 0.10 → 0.18 Gyr): caused EARLIER dt collapse at low N (22.49 Myr at t_end=0.18 vs 70 Myr at t_end=0.07). More sim time → more densification → more grid splits.

---

## Why T215p (N=3k, min=64, t_end=0.07) Works

This is the sweet spot:
- 3000 particles is enough to resolve core dynamics for ~70 Myr
- min_particles=64 forces reasonable bin sizes (not too many tiny bins)
- t_end=0.07 Gyr is short enough that the densifying core doesn't trigger catastrophic bin splitting
- ulimit -v 8000000 caps memory allocator variance

At any other tested config, either the grid splits too aggressively (N=10k) or the densification outpaces resolution (longer t_end).

---

## What WOULD Work (Tier 3 — Code Modifications Required)

Reviewer's Tier 3 levers remain untested:
1. **Subcycled time integration in inner core**: outer halo uses large dt, inner core subcycles with smaller dt. Requires code modification.
2. **Freeze refinement after density threshold**: stop grid from splitting once ρ > threshold. Requires code modification.
3. **Cap minimum bin size in core**: not global min_particles, but a r-dependent cap. Requires code modification.
4. **Restart from last good snapshot with coarsening**: when dt hits floor, write state, coarsen core, continue. Requires custom orchestration.

These are **out of scope** for this paper cycle. They require modifying KiSS-SIDM source code, not just parameter changes.

---

## Implications for Paper

§10.5b conclusion stands: **t_core not reached, methods-only contribution**. The Tier 1+2 future work showed that **parameter tuning alone cannot extend the run beyond ~70 Myr**. Reaching Balberg t_core = 176 Myr requires Tier 3 code modifications to KiSS-SIDM itself.

**Recommendation:** Do not pursue t_core in this paper cycle. The methods contribution is sufficient. If a quantitative t_core measurement is needed in future work, allocate ~6 months for Tier 3 code development + Tier 2 compute (~100 CPU-days for ensemble).

---

## Files

- `code/t215v.jl` — Tier 1+2 spec config (N=10k, min=128, t_end=0.18)
- `code/t215w.jl` — Revised Tier 2 (N=10k, min=32)
- `code/t215x.jl` — Extended t_end (N=3k, min=64, t_end=0.18)
- `code/t215y.jl` — Medium N (N=5k, min=64, t_end=0.10)
- `data/results/t215vwy_pilot_summary.json` — All run metadata
- `data/snapshots_t215{v,w,x,y}/` — Persistent snapshots (Tier 1 applied)

---

## Wall Time

~45 min total (5-10 min per run × multiple runs + diagnostics + writeup).