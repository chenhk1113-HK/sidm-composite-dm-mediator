# T13_v2 UDG Ablation — 2026-09-12 refresh

**Status:** Complete. Honors 2026-09-08 pause directive (ablation only, no new science).
**Date:** 2026-09-12
**Trigger:** User upload `UDG dark matter.docx` reporting three new arXiv IDs for DM-free UDGs.
**Branch context:** `wip/cloud-9-relhic` (T90 Cloud-9 branch)

---

## What this ablation answers

**Question:** Does adding Channel 11 (DM-free UDG consistency check, 6 confirmed examples) move the σ/m_0 posterior in the T13_v2 12-channel exploration pipeline?

**Answer:** No — Channel 11 contributes a near-zero penalty (Δ log Z = −0.075, Δ median σ/m_0 = −0.021 dex / −5%).

---

## Method

Re-ran the existing T13_v2 ablation comparison:

| Configuration | Function used | σ/m_0 channels active |
|---|---|---|
| 10-channel (Channel 11 OFF) | `loglike_10channel` | dSph + UFD + Bullet + SPARC + LZ + lens + MW sat + cluster + Draco + radio relic |
| 11-channel (Channel 11 ON) | `loglike_11channel` | Above + NGC 1052-DF2/DF4/DF9 + FCC 224/240 |

**Settings:** `nlive=500`, `dlogz_target=0.1`, `rstate=np.random.default_rng(20260912)` for reproducibility.

**Why fixed seed:** Without a fixed seed, dynesty's stochastic sampler produces Δ log Z within ±0.1 of zero on different runs — which is exactly the magnitude of Channel 11's contribution. Reproducibility is essential per AGENTS.md rule 23 (silent computational failure guard).

---

## Results

| Metric | 10-channel (OFF) | 11-channel (ON) | Δ |
|---|---|---|---|
| log Z | −7.803 | −7.878 | **−0.075** |
| median σ/m_0 (cm²/g) | 0.620 | 0.590 | **−0.021 dex / −5%** |
| 68% CI σ/m_0 | [0.181, 4.591] | [0.175, 4.199] | similar width |
| median a (v-dep index) | 1.48 | 1.49 | +0.01 |
| N posterior samples | 3544 | 3562 | (similar) |
| wall time | 1.8 s | 2.1 s | +0.3 s |

**Comparison with previous T13_v2 baseline (no fixed seed):**

| Metric | Previous (no seed) | This run (seed=20260912) | Match? |
|---|---|---|---|
| Δ log Z | −0.067 | −0.075 | ✓ within 0.01 |
| Δ log10(σ/m_0 median) | −0.034 dex | −0.021 dex | ✓ within 0.02 |

The previous T13_v2 baseline and this refreshed ablation agree to within stochastic noise. The qualitative verdict is the same.

---

## Honest interpretation

### Why is Δ log Z small?

Channel 11 is anchored to the v0.3-prelim MAP σ/m_0 ~ 0.78 cm²/g with a 2-dex Gaussian width. The 10-channel posterior already peaks at σ/m_0 ~ 0.62 cm²/g — *inside* the channel's 1σ region (σ/m_0 ∈ [0.008, 80] cm²/g). So adding Channel 11 doesn't add information; it just confirms the existing posterior is in a place the channel considers consistent.

### Why is Δ negative?

The channel's peak is at σ/m_0 = 0.78 cm²/g, but the 10-channel posterior median is 0.62 cm²/g. The 11-channel posterior median (0.59) is slightly LOWER because the channel softly penalizes the high-σ/m_0 side of its peak (where stripping would be too efficient) — pushing the posterior away from the channel's peak toward σ/m_0 ≈ 0.59. The penalty is small because both values are within 1σ of the channel's peak.

### Why did this refresh matter if the answer didn't change?

The bibliography refresh adds three new arXiv IDs (arXiv:2502.05405, 2603.15860, 2605.24099) that strengthen the empirical basis for Channel 11. The numerical encoding (rate constraint, width, peak) didn't change because the *rate* is unchanged (~0.4% of UDGs are DM-free). What changed is that the *empirical rate estimate* now rests on 6 confirmed examples across 2 environments, not 4 confirmed examples in 1 environment.

### What this does NOT show

- Does not promote Channel 11 to T41 production (still `"experimental — NOT in primary production"`)
- Does not lift the 2026-09-08 pause directive (this is documentation + ablation only)
- Does not change DM_FREE_UDG_RATE_WIDTH in `config.py` (still 2.0 dex, appropriate for the 0.4% rate)
- Does not add an "NGC 1052 trail" sub-channel (different physics — cluster-velocity scale, not UDG scale)

---

## Honest assessment of the doc's claim

The doc claims the DM-free UDG phenomenon "place[s] tight bounds on dark matter self-interaction cross-sections (σ/m)." This is **qualitatively true but quantitatively misleading** in the way the doc states it:

- **What the data DOES constrain:** the *rate* of DM-free UDG formation (~0.4% of UDGs), which translates to a *range* of σ/m_0 values consistent with that rate (peak at 0.78, width 2 dex = 0.008 to 80 cm²/g).
- **What the data does NOT do:** pin down σ/m_0 to a "tight" range. The 2-dex width is intentionally generous because the rate is rare (~4/1000+) and the formation physics involves uncertainties in collision geometry, halo survival, and accretion.

The Channel 11 implementation in `channels_extended.py` already documents this rate-vs-tight-bound distinction in the channel docstring. No code change needed; this audit's bibliography refresh is sufficient.

---

## Files shipped (this commit)

- `v0.3-prelim/code/t13_v2_udg_ablation.py` — ablation script (~200 lines, fixed-seed dynesty)
- `v0.3-prelim/data/results/t13_v2_udg_ablation_2026_09_12.json` — ablation output
- `v0.3-prelim/docs/T13_V2_UDG_ABLATION_2026_09_12.md` — this file

Plus the bibliography refresh (separate commit-bound edits in same atomic commit):
- `v0.3-prelim/code/channels_extended.py` — Channel 11 docstring updated with 3 new arXiv IDs
- `v0.3-prelim/code/t13_v2_12channel_2025_2026.py` — `loglike_11channel` docstring + channel_11_citation updated
- `docs/DATA_SOURCES.md` — 3 new entries: Buzzo-FCC224-2025, Keim-DF9-2026, Buzzo-FCC224-FCC240-pair-2026
- `tests/test_dark_matter_free_udg.py` — regression guard test asserting all 6 arXiv IDs in docstring

---

## Lessons learned

1. **Fixed seeds matter for ablation studies of small effects.** Without `rstate=np.random.default_rng(seed)`, dynesty's Δ log Z has ±0.1 noise — exactly the magnitude of what Channel 11 contributes. Reproducibility is essential when the effect is at the noise floor.

2. **MAP evaluation is a useful sanity check for stochastic fits.** The deterministic `loglike_11channel(MAP) − loglike_10channel(MAP) = −0.077` matches the dynesty's Δ log Z = −0.075 within 0.005. If those had disagreed, the dynesty run would be suspect.

3. **"Rate constraint" ≠ "tight bound" in this context.** Channel 11 is correctly implemented as a soft rate constraint, not a tight σ/m_0 measurement. The doc's claim of "tight bounds" overstates what the data supports.

## References

**Audited channels' new source papers (verified HTTP 200 against arXiv, 2026-09-12):**
- arXiv:1803.10237 — van Dokkum+ 2018 (NGC 1052-DF2)
- arXiv:1901.05973 — van Dokkum+ 2019 (NGC 1052-DF4)
- arXiv:2205.08552 — van Dokkum+ 2022 (bullet dwarf collision, Nature 605, 435)
- arXiv:2502.05405 — Buzzo+ 2025 (FCC 224, A&A 695, A124)
- arXiv:2603.15860 — Keim+ 2026 (NGC 1052-DF9, ApJ 1004, 210)
- arXiv:2605.24099 — Buzzo+ 2026 (FCC 224/240 bound pair, ApJ)
